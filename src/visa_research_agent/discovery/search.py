"""Finding candidate pages with a search engine.

Search decides only what is *considered*. Nothing it returns becomes evidence until it passes the
domain trust rules, so a highly-ranked commercial visa agency is discarded rather than judged.

Queries are built from templates and the corridor alone. They are never written by a model and
never derived from fetched page content, so a page cannot influence what is searched for next.
"""

import asyncio
from typing import Protocol

import httpx

from visa_research_agent.discovery.lexicon import Country, CountryRegistry
from visa_research_agent.discovery.models import Corridor, SearchResult
from visa_research_agent.domain.models import DestinationConfig
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.errors import VisaResearchError


class SearchError(VisaResearchError):
    """Raised when the search provider cannot be reached or is misconfigured."""


class SearchProvider(Protocol):
    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        """Return ranked results for one query."""
        ...


# How many search queries may be in flight at once. Queries are independent, so running them one
# after another spent a second of latency per query for no reason — twelve of them was eleven
# seconds of a corridor. Kept modest rather than unbounded: a search API is someone else's rate
# limit, and a burst that trips it turns a resolvable corridor into a refusal.
DEFAULT_SEARCH_CONCURRENCY = 4


async def search_all(
    provider: SearchProvider,
    queries: list[str],
    *,
    count: int,
    concurrency: int = DEFAULT_SEARCH_CONCURRENCY,
) -> dict[str, list[SearchResult]]:
    """Run several queries at once, returning their results keyed by query in the order asked.

    The ordering matters beyond tidiness: what a corridor resolves to depends on the order results
    are considered, so it must not depend on which query happened to answer first.

    A failing query still raises, exactly as it did when these ran one at a time. Tolerating one
    would be a separate decision about whether a partly-searched corridor is safe to serve.
    """

    limit = asyncio.Semaphore(max(1, concurrency))

    async def run(query: str) -> list[SearchResult]:
        async with limit:
            return await provider.search(query, count=count)

    completed = await asyncio.gather(*(run(query) for query in queries))
    return dict(zip(queries, completed, strict=True))


def bootstrap_queries(destination_name: str) -> list[str]:
    """Queries for finding a country's official authorities.

    Deliberately several and deliberately overlapping: a domain must appear in more than one before
    it is proposed, which is what removes sites that rank for a single lucky phrase.
    """

    return [
        f"{destination_name} visa official government",
        f"{destination_name} embassy visa application",
        f"{destination_name} immigration authority official",
        f"{destination_name} ministry of foreign affairs visa",
    ]


def corridor_queries(
    corridor: Corridor,
    destination: DestinationConfig,
    nationality: Country,
    residence: Country,
) -> list[str]:
    """Queries for finding the pages one traveller needs, constrained to approved domains.

    Every query carries a `site:` restriction, so the search engine is asked only about domains a
    human already approved. Results are checked again afterwards; the restriction is a courtesy to
    the engine, not the safety mechanism.
    """

    name = destination.display_name
    queries: list[str] = []
    for domain in destination.trusted_domains:
        queries.extend(
            [
                f"site:{domain} {name} visa requirements {nationality.name}",
                f"site:{domain} {corridor.purpose} visa documents required",
                f"site:{domain} visa application {residence.name}",
            ]
        )
    return queries


def usable_results(
    results: list[SearchResult],
    destination: DestinationConfig,
) -> list[SearchResult]:
    """Keep only results on an approved domain.

    This is the gate that makes search safe to use: spam is dropped here, before anything is
    fetched, so an unofficial page is never read let alone quoted.
    """

    return [result for result in results if destination.trusts_host(host_of(result.url))]


class BraveSearchProvider:
    """Search through the Brave Search API.

    Chosen for an independent index and a plain REST interface. The provider is behind a protocol
    so swapping vendors, or running entirely offline in tests, needs no change elsewhere.
    """

    endpoint = "https://api.search.brave.com/res/v1/web/search"

    def __init__(
        self,
        api_key: str,
        *,
        timeout_seconds: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key.strip():
            raise SearchError("A search API key is required for discovery")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
        try:
            async with httpx.AsyncClient(
                transport=self.transport,
                timeout=self.timeout_seconds,
                headers=headers,
            ) as client:
                response = await client.get(self.endpoint, params={"q": query, "count": count})
                if response.status_code != httpx.codes.OK:
                    raise SearchError(f"The search provider answered HTTP {response.status_code}")
                payload = response.json()
        except httpx.HTTPError as exc:
            raise SearchError(f"The search request failed ({exc})") from exc
        except ValueError as exc:
            raise SearchError("The search provider returned a malformed response") from exc

        web = payload.get("web") or {}
        entries = web.get("results") or []
        results: list[SearchResult] = []
        for rank, entry in enumerate(entries):
            url = (entry or {}).get("url")
            if not isinstance(url, str) or not url:
                continue
            results.append(
                SearchResult(
                    url=url,
                    title=str(entry.get("title") or ""),
                    snippet=str(entry.get("description") or ""),
                    query=query,
                    rank=rank,
                )
            )
        return results


def resolve_corridor_countries(
    corridor: Corridor, registry: CountryRegistry
) -> tuple[Country, Country]:
    """Look up the corridor's nationality and residence, refusing unknown codes."""

    return registry.require(corridor.passport_nationality), registry.require(corridor.applying_from)
