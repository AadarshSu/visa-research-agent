"""Live official-source retrieval with hash-and-TTL caching.

Retrieval is deliberately narrow: it visits only URLs already approved in the destination
registry, and it prefers refusing a source to serving evidence that may no longer be current.
"""

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime
from hashlib import sha256

import httpx
from bs4 import BeautifulSoup

from visa_research_agent.domain.models import (
    ConfiguredSource,
    DestinationConfig,
    FetchedSource,
    SourceReference,
)
from visa_research_agent.research.errors import LiveSourceError
from visa_research_agent.research.source_cache import CachedSource, FileSourceCache

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
        self.transport = transport
        self.now = now

    async def fetch(self, destination: DestinationConfig) -> list[FetchedSource]:
        """Retrieve every configured primary source, or fail the run."""

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
            headers={
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-GB,en;q=0.9",
            },
        ) as client:

            async def fetch_one(configured_source: ConfiguredSource) -> FetchedSource:
                async with limit:
                    return await self._fetch_source(client, configured_source)

            return list(
                await asyncio.gather(
                    *(fetch_one(source) for source in configured_sources),
                )
            )

    async def _fetch_source(
        self,
        client: httpx.AsyncClient,
        configured_source: ConfiguredSource,
    ) -> FetchedSource:
        url = str(configured_source.url)
        now = self.now()
        cached = self.cache.load(url)

        if cached is not None and cached.age_hours(now) < self.ttl_hours:
            return self._build(configured_source, cached, from_cache=True, is_stale=False)

        try:
            response = await self._request(client, url, cached)
        except httpx.HTTPError as exc:
            return self._serve_stale(configured_source, cached, now, f"the request failed ({exc})")

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
            )

        content = clean_source_html(response.text, maximum_characters=self.maximum_characters)
        # A near-empty result means a client-rendered or blocked page, not an empty requirement
        # list, so it must never reach extraction as though it were evidence.
        if len(content) < self.minimum_characters:
            return self._serve_stale(
                configured_source,
                cached,
                now,
                "the page returned too little readable text to trust",
            )

        entry = CachedSource(
            url=url,
            final_url=str(response.url),
            fetched_at=now,
            content=content,
            content_hash=sha256(content.encode()).hexdigest(),
            http_status=response.status_code,
            etag=response.headers.get("etag"),
            last_modified=response.headers.get("last-modified"),
        )
        self.cache.store(entry)
        return self._build(configured_source, entry, from_cache=False, is_stale=False)

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
    ) -> FetchedSource:
        """Fall back to cached evidence, but only while it is still inside the stale ceiling."""

        if cached is None:
            raise LiveSourceError(
                f"Could not retrieve {configured_source.source_id} because {reason}",
            )

        age_hours = cached.age_hours(now)
        if age_hours > self.maximum_stale_hours:
            raise LiveSourceError(
                f"Cached evidence for {configured_source.source_id} is {age_hours:.0f} hours old "
                f"and could not be refreshed because {reason}",
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
            ),
            content=entry.content,
            content_hash=entry.content_hash,
            from_cache=from_cache,
            is_stale=is_stale,
        )
