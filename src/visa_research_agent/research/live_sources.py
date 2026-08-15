"""Live official-source retrieval with hash-and-TTL caching.

Retrieval is deliberately narrow: it visits only URLs already approved in the destination
registry, and it prefers refusing a source to serving evidence that may no longer be current.
"""

import asyncio
import re
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256
from io import BytesIO
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag
from pydantic import AnyHttpUrl
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from visa_research_agent.domain.models import (
    ConfiguredSource,
    DestinationConfig,
    FailureOutcome,
    FetchedSource,
    RetrievalReport,
    SourceFailure,
    SourceReference,
)
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.errors import LiveSourceError
from visa_research_agent.research.source_cache import CachedSource, FileSourceCache
from visa_research_agent.research.tls import build_ssl_context

# Government pages carry heavy navigation furniture that would otherwise dominate the
# evidence and dilute the text the extractor reasons over.
STRIPPED_TAGS = (
    "script",
    "style",
    "noscript",
    "template",
    "svg",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "iframe",
    "button",
)


def clean_source_html(html: str, *, maximum_characters: int) -> str:
    """Reduce a page to bounded readable text, dropping chrome and blank lines."""

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(STRIPPED_TAGS):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    cleaned = "\n".join(line for line in lines if line)
    return cleaned[:maximum_characters].strip()


# Authorities often publish a checklist as a PDF behind a tiny HTML page that forwards to it.
# Following that forward is necessary to reach the real guidance, but each hop must still be
# checked for trust, so this is kept deliberately shallow.
MAXIMUM_FORWARD_HOPS = 2


def _collapse_whitespace(text: str) -> str:
    lines = (line.strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line)


def extract_pdf_text(data: bytes, *, maximum_characters: int) -> str:
    """Pull readable text out of a PDF, stopping once the character budget is met."""

    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("the PDF is encrypted")
        collected: list[str] = []
        length = 0
        for page in reader.pages:
            page_text = page.extract_text() or ""
            collected.append(page_text)
            length += len(page_text)
            if length >= maximum_characters:
                break
    except (PdfReadError, ValueError, OSError, KeyError) as exc:
        raise ValueError("the PDF could not be read") from exc

    return _collapse_whitespace("\n".join(collected))[:maximum_characters].strip()


def find_forward_target(html: str, base_url: str) -> str | None:
    """Return the absolute URL a meta-refresh page forwards to, if it is one."""

    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("meta", attrs={"http-equiv": re.compile(r"^\s*refresh\s*$", re.IGNORECASE)})
    if not isinstance(tag, Tag):
        return None
    content = tag.get("content")
    if not isinstance(content, str):
        return None
    match = re.search(r"url\s*=\s*['\"]?([^'\";]+)", content, re.IGNORECASE)
    if match is None:
        return None
    target = match.group(1).strip()
    return urljoin(base_url, target) if target else None


# Content types that are data for a program, not guidance for a person. Discovery can surface an
# API endpoint that returns several hundred characters of JSON, which would otherwise clear the
# readable-text floor and be quoted as though it were official advice.
MACHINE_CONTENT_TYPES = ("application/json", "application/xml", "text/csv", "text/xml")


def looks_machine_readable(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return any(marker in content_type for marker in MACHINE_CONTENT_TYPES)


def looks_like_pdf(response: httpx.Response) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    if "application/pdf" in content_type:
        return True
    # Some authorities serve PDFs with a generic content type, so fall back to the path.
    return response.url.path.lower().endswith(".pdf")


class _ContentProblem(Exception):
    """Raised when a retrieved document cannot become trustworthy evidence."""

    def __init__(self, outcome: FailureOutcome, reason: str, final_url: str | None = None) -> None:
        super().__init__(reason)
        self.outcome = outcome
        self.reason = reason
        self.final_url = final_url


def _utc_now() -> datetime:
    return datetime.now(UTC)


class LiveSourceFetcher:
    """Fetch registry-approved official pages, reusing cached text while it stays current."""

    def __init__(
        self,
        cache: FileSourceCache,
        *,
        ttl_hours: float,
        maximum_stale_hours: float,
        timeout_seconds: float,
        concurrency: int,
        maximum_characters: int,
        minimum_characters: int,
        user_agent: str,
        maximum_bytes: int = 12_000_000,
        transport: httpx.AsyncBaseTransport | None = None,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        if concurrency < 1:
            raise LiveSourceError("Live retrieval requires a concurrency of at least one")
        if maximum_stale_hours < ttl_hours:
            raise LiveSourceError("The stale ceiling cannot be shorter than the cache TTL")

        self.cache = cache
        self.ttl_hours = ttl_hours
        self.maximum_stale_hours = maximum_stale_hours
        self.timeout_seconds = timeout_seconds
        self.concurrency = concurrency
        self.maximum_characters = maximum_characters
        self.minimum_characters = minimum_characters
        self.user_agent = user_agent
        self.maximum_bytes = maximum_bytes
        self.transport = transport
        self.now = now

    async def fetch(self, destination: DestinationConfig) -> RetrievalReport:
        """Retrieve every configured primary source, reporting any that could not be used."""

        configured_sources = [
            source for source in destination.sources if source.research_pass == "primary"
        ]
        if not configured_sources:
            raise LiveSourceError(
                f"No primary sources are configured for {destination.slug}",
            )

        limit = asyncio.Semaphore(self.concurrency)
        async with httpx.AsyncClient(
            transport=self.transport,
            timeout=self.timeout_seconds,
            follow_redirects=True,
            # Verification stays on; the context only completes chains servers fail to send.
            verify=build_ssl_context(),
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/pdf",
                "Accept-Language": "en-GB,en;q=0.9",
            },
        ) as client:

            async def fetch_one(
                configured_source: ConfiguredSource,
            ) -> FetchedSource | SourceFailure:
                async with limit:
                    return await self._fetch_source(client, destination, configured_source)

            results = await asyncio.gather(
                *(fetch_one(source) for source in configured_sources),
            )

        # One unusable source no longer ends the run; it is reported as an explained gap and the
        # decision about whether the plan can still stand is made downstream.
        return RetrievalReport(
            fetched=[item for item in results if isinstance(item, FetchedSource)],
            failures=[item for item in results if isinstance(item, SourceFailure)],
        )

    async def _fetch_source(
        self,
        client: httpx.AsyncClient,
        destination: DestinationConfig,
        configured_source: ConfiguredSource,
    ) -> FetchedSource | SourceFailure:
        url = str(configured_source.url)
        now = self.now()
        cached = self.cache.load(url)

        if cached is not None and cached.age_hours(now) < self.ttl_hours:
            return self._build(configured_source, cached, from_cache=True, is_stale=False)

        try:
            response = await self._request(client, url, cached)
        except httpx.HTTPError as exc:
            return self._serve_stale(
                configured_source, cached, now, f"the request failed ({exc})", "unreachable"
            )

        # Follow where the request actually landed. A page that redirects off the approved
        # authority domains is refused outright rather than quoted as official guidance.
        final_host = host_of(str(response.url))
        if not destination.trusts_host(final_host):
            return SourceFailure(
                source_id=configured_source.source_id,
                title=configured_source.title,
                authority=configured_source.authority,
                outcome="untrusted",
                detail=(
                    f"the request was redirected to {final_host}, which is not an approved "
                    f"authority domain for {destination.display_name}"
                ),
                attempted_url=configured_source.url,
                final_url=AnyHttpUrl(str(response.url)),
            )

        # A validator match proves the cached text is still current, so only the clock moves.
        if response.status_code == httpx.codes.NOT_MODIFIED and cached is not None:
            revalidated = cached.model_copy(update={"fetched_at": now})
            self.cache.store(revalidated)
            return self._build(configured_source, revalidated, from_cache=True, is_stale=False)

        if response.status_code != httpx.codes.OK:
            return self._serve_stale(
                configured_source,
                cached,
                now,
                f"the source answered HTTP {response.status_code}",
                "unreachable",
            )

        try:
            content, document = await self._read_document(client, destination, response)
        except _ContentProblem as problem:
            if problem.outcome == "untrusted":
                return SourceFailure(
                    source_id=configured_source.source_id,
                    title=configured_source.title,
                    authority=configured_source.authority,
                    outcome="untrusted",
                    detail=problem.reason,
                    attempted_url=configured_source.url,
                    final_url=AnyHttpUrl(problem.final_url) if problem.final_url else None,
                )
            return self._serve_stale(
                configured_source, cached, now, problem.reason, problem.outcome
            )
        except httpx.HTTPError as exc:
            return self._serve_stale(
                configured_source,
                cached,
                now,
                f"the forwarded document could not be retrieved ({exc})",
                "unreachable",
            )

        # A near-empty result means a client-rendered or blocked page, not an empty requirement
        # list, so it must never reach extraction as though it were evidence.
        if len(content) < self.minimum_characters:
            return self._serve_stale(
                configured_source,
                cached,
                now,
                "the page returned too little readable text to trust",
                "unusable",
            )

        entry = CachedSource(
            url=url,
            final_url=str(document.url),
            fetched_at=now,
            content=content,
            content_hash=sha256(content.encode()).hexdigest(),
            http_status=response.status_code,
            etag=response.headers.get("etag"),
            last_modified=response.headers.get("last-modified"),
        )
        self.cache.store(entry)
        return self._build(configured_source, entry, from_cache=False, is_stale=False)

    async def _read_document(
        self,
        client: httpx.AsyncClient,
        destination: DestinationConfig,
        response: httpx.Response,
        hops: int = 0,
    ) -> tuple[str, httpx.Response]:
        """Reduce a response to bounded text, following a forward to a PDF where one exists.

        Returns the text and the response it actually came from, so provenance records the
        document that was read rather than the page that pointed at it.
        """

        if len(response.content) > self.maximum_bytes:
            raise _ContentProblem("unusable", "the document exceeds the configured size limit")

        if looks_machine_readable(response):
            raise _ContentProblem(
                "unusable", "it returns data for a program rather than readable guidance"
            )

        if looks_like_pdf(response):
            try:
                return (
                    extract_pdf_text(
                        response.content, maximum_characters=self.maximum_characters
                    ),
                    response,
                )
            except ValueError as exc:
                raise _ContentProblem("unusable", str(exc)) from exc

        html = response.text
        target = find_forward_target(html, str(response.url))
        if target is None:
            return clean_source_html(html, maximum_characters=self.maximum_characters), response
        if hops >= MAXIMUM_FORWARD_HOPS:
            raise _ContentProblem("unusable", "the page forwards through too many redirects")

        # A forward is a redirect by another name, so it gets the same trust check.
        target_host = host_of(target)
        if not destination.trusts_host(target_host):
            raise _ContentProblem(
                "untrusted",
                f"the page forwards to {target_host}, which is not an approved authority domain "
                f"for {destination.display_name}",
                target,
            )

        forwarded = await client.get(target)
        if forwarded.status_code != httpx.codes.OK:
            raise _ContentProblem(
                "unreachable",
                f"the forwarded document answered HTTP {forwarded.status_code}",
            )
        final_host = host_of(str(forwarded.url))
        if not destination.trusts_host(final_host):
            raise _ContentProblem(
                "untrusted",
                f"the forwarded document resolved to {final_host}, which is not an approved "
                f"authority domain for {destination.display_name}",
                str(forwarded.url),
            )
        return await self._read_document(client, destination, forwarded, hops + 1)

    async def _request(
        self,
        client: httpx.AsyncClient,
        url: str,
        cached: CachedSource | None,
    ) -> httpx.Response:
        headers: dict[str, str] = {}
        if cached is not None:
            if cached.etag:
                headers["If-None-Match"] = cached.etag
            if cached.last_modified:
                headers["If-Modified-Since"] = cached.last_modified
        return await client.get(url, headers=headers)

    def _serve_stale(
        self,
        configured_source: ConfiguredSource,
        cached: CachedSource | None,
        now: datetime,
        reason: str,
        outcome: FailureOutcome,
    ) -> FetchedSource | SourceFailure:
        """Fall back to cached evidence, but only while it is still inside the stale ceiling."""

        def failure(detail: str) -> SourceFailure:
            return SourceFailure(
                source_id=configured_source.source_id,
                title=configured_source.title,
                authority=configured_source.authority,
                outcome=outcome,
                detail=detail,
                attempted_url=configured_source.url,
            )

        if cached is None:
            return failure(reason)

        age_hours = cached.age_hours(now)
        if age_hours > self.maximum_stale_hours:
            return failure(
                f"{reason}, and the cached copy is {age_hours:.0f} hours old, past the "
                f"{self.maximum_stale_hours:.0f} hour limit for serving stale guidance"
            )
        return self._build(configured_source, cached, from_cache=True, is_stale=True)

    def _build(
        self,
        configured_source: ConfiguredSource,
        entry: CachedSource,
        *,
        from_cache: bool,
        is_stale: bool,
    ) -> FetchedSource:
        return FetchedSource(
            source=SourceReference(
                source_id=configured_source.source_id,
                title=configured_source.title,
                url=configured_source.url,
                authority=configured_source.authority,
                # The recorded retrieval time, never the request time, so cached evidence
                # cannot present itself as freshly checked.
                retrieved_at=entry.fetched_at,
                is_stale=is_stale,
            ),
            content=entry.content,
            content_hash=entry.content_hash,
            from_cache=from_cache,
        )
