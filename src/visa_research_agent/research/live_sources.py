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

from visa_research_agent.domain.models import (
    BLOCKING_STATUS_CODES,
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
from visa_research_agent.research.rendering import PageRenderer
from visa_research_agent.research.robots import RobotsCache, RobotsVerdict
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


# A line that is one unspaced token of dotted or camel-cased words: "home.banner-huong-dan",
# "lienKet", "vanBanQuyPhamPhapLuat". Real guidance is written in sentences with spaces.
PLACEHOLDER_KEY = re.compile(r"^[a-z][a-z0-9]*(?:[.\-_][a-z0-9\-]+)+$|^[a-z]+(?:[A-Z][a-z0-9]*)+$")

MINIMUM_PLACEHOLDER_LINES = 4
PLACEHOLDER_SHARE = 0.5


def looks_untranslated(text: str) -> bool:
    """True when a page's text is translation keys rather than words a traveller could read.

    Vietnam's immigration department returns 402 characters of `home.banner-huong-dan-viet-nam`
    and `lienKet`, fetching the actual strings client-side. That clears the readable-text floor,
    so without this check a page of placeholders would reach extraction as though it were
    guidance — the wrong-checklist failure the floor exists to prevent.

    Deliberately conservative: it needs a handful of such lines and a majority share, because the
    cost of a false positive is refusing a source that was perfectly good.
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < MINIMUM_PLACEHOLDER_LINES:
        return False
    keys = sum(1 for line in lines if PLACEHOLDER_KEY.match(line))
    if keys < MINIMUM_PLACEHOLDER_LINES:
        return False
    return keys / len(lines) >= PLACEHOLDER_SHARE


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
    # Deliberately broad, and the breadth is the point: this parses arbitrary bytes served by an
    # arbitrary authority, and its contract is **total** — every input either yields text or is
    # reported as unreadable. A narrow tuple is what it was, and a real PDF walked through the gap:
    # Sweden's corpus-routed shortlist held an AES-encrypted PDF, whose `DependencyError` extends
    # `Exception` directly rather than `PdfReadError` or even `PyPdfError`, so it escaped and
    # **took the whole corridor down** (2026-08-23, entry 54). Losing one source to an unreadable
    # PDF is ordinary; losing a traveller's answer to one is not, and no narrower tuple can be
    # trusted to have enumerated every way a third-party parser fails on hostile input.
    except Exception as exc:
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


def _robots_reason(verdict: RobotsVerdict, detail: str) -> str:
    """Why a crawl policy stopped a source, in words that are true of *that* verdict.

    A host that said no and a host whose policy could not be read are different facts, and only the
    first is a statement about what the authority permits. Both end the same way — the source is
    missing and the plan says so — but a reason this project reports has to be true of what was
    actually observed.
    """

    if verdict is RobotsVerdict.DISALLOWED:
        return (
            "the authority's robots.txt does not permit this client to retrieve it, so its "
            "guidance could not be independently verified here"
        )
    return (
        f"the authority's robots.txt {detail}, so whether this client may retrieve the page is "
        "unknown and it was not requested"
    )


class RenderBudget:
    """How many pages one run may render, spent by that run and nobody else.

    It exists as a value rather than as a counter on the fetcher because the fetcher outlives the
    run. `get_visa_plan_service` is an `lru_cache(maxsize=1)`, so one `LiveSourceFetcher` serves
    every request the server ever answers; a spent count held there is a process-lifetime budget
    however its docstring describes it, and after the first few requests that needed a browser
    every client-rendered page degrades to "too little readable text" for as long as the server
    stays up. Held per call, the allowance is what it always claimed to be, and two requests in
    flight together cannot spend each other's.
    """

    def __init__(self, maximum: int) -> None:
        self.maximum = maximum
        self.spent = 0

    def claim(self) -> bool:
        """Take one render if the run can still afford it."""

        if self.spent >= self.maximum:
            return False
        self.spent += 1
        return True


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
        renderer: PageRenderer | None = None,
        maximum_renders: int = 5,
        transport: httpx.AsyncBaseTransport | None = None,
        now: Callable[[], datetime] = _utc_now,
        robots: RobotsCache | None = None,
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
        # Optional on purpose. Without a renderer this class behaves exactly as it did before
        # rendering existed, which is what keeps the offline and fixture paths unchanged.
        self.renderer = renderer
        # Retrieval's own allowance, held separately from discovery's. Sharing one count let the
        # crawl spend it all before the shortlist — the pages that become evidence — was read.
        # The *limit* lives here because it is configuration; what a run has spent does not, and
        # a `RenderBudget` is built per `fetch` instead. See that class for why.
        self.maximum_renders = maximum_renders
        self.transport = transport
        self.now = now
        # Each host's own crawl policy. Built here rather than injected so retrieval cannot be
        # configured to run without it; the parameter is a seam for tests, not a switch.
        self.robots = robots or RobotsCache(user_agent=user_agent)

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
        # One allowance per call, spent only by the sources this call reads.
        budget = RenderBudget(self.maximum_renders)
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
                    return await self._fetch_source(client, destination, configured_source, budget)

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
        budget: RenderBudget,
    ) -> FetchedSource | SourceFailure:
        url = str(configured_source.url)
        now = self.now()
        cached = self.cache.load(url)

        if cached is not None and cached.age_hours(now) < self.ttl_hours:
            return self._build(configured_source, cached, from_cache=True, is_stale=False)

        try:
            # Checked here rather than above the cache, because `robots.txt` governs *fetching*.
            # Text already held and still current was fetched under whatever policy applied then,
            # and re-reading it makes no request. Past the TTL a request is needed, so the policy
            # decides. Inside the try because a host that will not serve its policy is a host this
            # already knows how to report, and it is not a claim about what that host permits.
            verdict = await self.robots.verdict(client, url)
            if verdict is not RobotsVerdict.ALLOWED:
                return self._serve_stale(
                    configured_source,
                    cached,
                    now,
                    _robots_reason(verdict, self.robots.unreadable_detail(url)),
                    "disallowed",
                )
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

        if response.status_code in BLOCKING_STATUS_CODES:
            # Not a fault, and not evidence that the guidance is wrong or absent: the authority is
            # refusing this client. Say exactly that, and let the source be missing.
            #
            # But first establish that it *is* a refusal, which this does not yet do (entry 41).
            # A `403` carrying `cf-mitigated: challenge` is Cloudflare asking whether we are a
            # browser; `france-visas.gouv.fr` answers that for every path including `/robots.txt`.
            # Note this branch returns **before** the render branch below, so a challenged page
            # never reaches the renderer that would answer it — `render_mode: on_demand` today
            # changes nothing for France. TODO item 5.
            return self._serve_stale(
                configured_source,
                cached,
                now,
                (
                    f"the authority refused automated retrieval (HTTP {response.status_code}), so "
                    "its guidance could not be independently verified here"
                ),
                "blocked",
                status=response.status_code,
            )

        if response.status_code != httpx.codes.OK:
            return self._serve_stale(
                configured_source,
                cached,
                now,
                f"the source answered HTTP {response.status_code}",
                "unreachable",
                status=response.status_code,
            )

        try:
            content, document = await self._read_document(client, destination, response)
            final_url = str(document.url)
            # A page that gave up nothing readable may still be a real page whose text only
            # exists once its scripts have run. Rendering is tried here and nowhere else, so
            # the pages that already work never meet a browser.
            if self._thin_reason(content) is not None and not looks_like_pdf(document):
                rendered = await self._render(destination, final_url, budget)
                if rendered is not None:
                    content, final_url = rendered
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
        thin_reason = self._thin_reason(content)
        if thin_reason is not None:
            return self._serve_stale(configured_source, cached, now, thin_reason, "unusable")

        entry = CachedSource(
            url=url,
            final_url=final_url,
            fetched_at=now,
            content=content,
            content_hash=sha256(content.encode()).hexdigest(),
            http_status=response.status_code,
            etag=response.headers.get("etag"),
            last_modified=response.headers.get("last-modified"),
        )
        self.cache.store(entry)
        return self._build(configured_source, entry, from_cache=False, is_stale=False)

    def _thin_reason(self, content: str) -> str | None:
        """Why this text cannot be trusted as guidance, or None when it can.

        Both cases produce prose that a traveller could be shown, because this reason is what a
        refusal ends up saying.
        """

        if len(content) < self.minimum_characters:
            return "the page returned too little readable text to trust"
        if looks_untranslated(content):
            return "the page returned translation placeholders rather than readable guidance"
        return None

    async def _render(
        self, destination: DestinationConfig, url: str, budget: RenderBudget
    ) -> tuple[str, str] | None:
        """Re-read a page through the renderer, returning its text and where it landed.

        Raises `_ContentProblem` when the rendered page ends up off the approved domains, which is
        the same answer retrieval gives to a redirect that leaves them.
        """

        if self.renderer is None or not budget.claim():
            return None
        rendered = await self.renderer.render(url, destination)
        if rendered is None:
            return None

        # Rendering runs scripts, and a script can navigate. The landing host gets exactly the
        # check a redirect gets, because that is what this is.
        final_host = host_of(rendered.final_url)
        if not destination.trusts_host(final_host):
            raise _ContentProblem(
                "untrusted",
                f"rendering the page navigated to {final_host}, which is not an approved "
                f"authority domain for {destination.display_name}",
                rendered.final_url,
            )
        content = clean_source_html(rendered.html, maximum_characters=self.maximum_characters)
        return content, rendered.final_url

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
                    extract_pdf_text(response.content, maximum_characters=self.maximum_characters),
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

        # The forward is a request of its own, so it answers to the target's policy of its own.
        forward_verdict = await self.robots.verdict(client, target)
        if forward_verdict is not RobotsVerdict.ALLOWED:
            raise _ContentProblem(
                "disallowed",
                "the page forwards to a document, and "
                + _robots_reason(forward_verdict, self.robots.unreadable_detail(target)),
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
        *,
        status: int | None = None,
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
                # Passed on rather than left in the sentence: whether a refusal is settled decides
                # what a traveller may be told, and that must not depend on prose. See
                # `SourceFailure.http_status`.
                http_status=status,
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
