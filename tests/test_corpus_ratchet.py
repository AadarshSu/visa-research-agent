"""The ratchet: a corridor may gain candidates between runs, and must never lose them.

The property being pinned is not "the same candidate set every run" — that would freeze recall — but
**monotonic**: run two sees everything run one saw, plus whatever else turned up. Two mechanisms
carry it, and each is tested here against the case that motivated it:

  * the **corpus** supplies pages a later search forgot (Canada, 2026-08-21);
  * a **pin** keeps a page that already filled a role, so it never has to win the ranking again.

Offline throughout. See DECISIONS entry 44.
"""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from discovery_site import DETAIL_INDIA, INDEX, MISSION_CHECKLIST, destination, handler

from visa_research_agent.discovery.corpus import CorpusEntry, CountryCorpus
from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.models import (
    CandidatePage,
    Corridor,
    PageLink,
    RoleScores,
    SearchResult,
)
from visa_research_agent.discovery.resolver import DEFAULT_SHORTLIST_SIZE, CorridorResolver
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.source_cache import FileSourceCache

RESOLVED_AT = datetime(2026, 8, 22, 9, 0, tzinfo=UTC)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="japan",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


class StubSearch:
    """Returns exactly what it is told to, so "search forgot a page" is expressible."""

    def __init__(self, urls: list[str]) -> None:
        self.urls = urls

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        return [
            SearchResult(url=url, title="", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls)
        ]


async def sleep_none(_: float) -> None:
    return None


def corpus_of(*urls: str) -> CountryCorpus:
    return CountryCorpus(
        country_code="JP",
        country_name="Japan",
        trusted_domains=destination().trusted_domains,
        built_at=RESOLVED_AT,
        entries=[
            CorpusEntry(url=url, first_seen=RESOLVED_AT, last_seen=RESOLVED_AT) for url in urls
        ],
    )


def build(
    tmp_path: Path,
    search_urls: list[str],
    *,
    corpus: CountryCorpus | None = None,
    pinned: list[str] | None = None,
) -> CorridorResolver:
    transport = httpx.MockTransport(handler([]))  # type: ignore[arg-type]
    return CorridorResolver(
        StubSearch(search_urls),
        CrawlFetcher(transport=transport, sleep=sleep_none, host_delay_seconds=0.0),
        LiveSourceFetcher(
            FileSourceCache(tmp_path / "cache"),
            ttl_hours=24.0,
            maximum_stale_hours=168.0,
            timeout_seconds=5.0,
            concurrency=2,
            maximum_characters=50_000,
            minimum_characters=40,
            user_agent="test-agent",
            transport=transport,
            now=lambda: RESOLVED_AT,
        ),
        minimum_role_score=10.0,
        corpus=corpus,
        pinned=pinned,
        now=lambda: RESOLVED_AT,
    )


@pytest.mark.anyio
async def test_the_corpus_supplies_a_page_search_no_longer_returns(tmp_path: Path) -> None:
    """The Canada failure, in miniature.

    Search returns nothing useful; the page that answers the corridor is in the corpus; the corridor
    still considers it. Without this the run is at the mercy of what search felt like returning.
    """

    without = build(tmp_path, [])
    resolved_without = await without.resolve(destination(), corridor())

    with_corpus = build(tmp_path, [], corpus=corpus_of(INDEX, DETAIL_INDIA, MISSION_CHECKLIST))
    resolved_with = await with_corpus.resolve(destination(), corridor())

    assert not resolved_without.sources, "search returned nothing, so there was nothing to resolve"
    assert resolved_with.sources, "the corpus should have supplied candidates search did not"


@pytest.mark.anyio
async def test_a_pinned_page_keeps_its_shortlist_place(tmp_path: Path) -> None:
    """A page that already answered this corridor must not have to win the ranking again.

    Seeding from the corpus grows the candidate pool a great deal, and entry 40's asymmetry says a
    page ranked out is unrecoverable — so a bigger pool costs recall unless what already worked is
    held in place.
    """

    resolver = build(
        tmp_path,
        [INDEX],
        corpus=corpus_of(MISSION_CHECKLIST),
        pinned=[MISSION_CHECKLIST],
    )

    await resolver.resolve(destination(), corridor())

    shortlisted = set(resolver.trace.shortlisted)
    assert MISSION_CHECKLIST in shortlisted


@pytest.mark.anyio
async def test_a_pin_matches_the_page_under_a_host_alias(tmp_path: Path) -> None:
    """Pins are compared by `canonical_key`, or a `www.` would silently break the ratchet."""

    aliased = MISSION_CHECKLIST.replace("https://", "https://www.")
    resolver = build(tmp_path, [INDEX], corpus=corpus_of(MISSION_CHECKLIST), pinned=[aliased])

    await resolver.resolve(destination(), corridor())

    assert MISSION_CHECKLIST in set(resolver.trace.shortlisted)


@pytest.mark.anyio
async def test_only_pages_this_run_found_are_offered_for_write_back(tmp_path: Path) -> None:
    """What the corpus already holds has nothing to add to it, so it is not written back."""

    resolver = build(tmp_path, [INDEX], corpus=corpus_of(INDEX))

    await resolver.resolve(destination(), corridor())

    discovered = {link.url for link in resolver.discovered}
    assert INDEX not in discovered, "a page that came from the corpus is not a discovery"
    assert discovered, "the crawl found pages beyond the seed, and those are worth keeping"


@pytest.mark.anyio
async def test_the_candidate_set_never_shrinks_between_runs(tmp_path: Path) -> None:
    """The property the whole design exists for, stated directly."""

    first = build(tmp_path, [INDEX])
    await first.resolve(destination(), corridor())
    considered_first = set(first.trace.candidates)
    assert considered_first, "the first run considered nothing, so the test proves nothing"

    # The second run's search has forgotten everything — the Canada failure at its worst — but its
    # corpus holds what the first run discovered, which is exactly what write-back produces.
    second = build(tmp_path, [], corpus=corpus_of(*(link.url for link in first.discovered)))
    await second.resolve(destination(), corridor())
    considered_second = set(second.trace.candidates)

    lost = considered_first - considered_second
    assert not lost, f"a total search failure still lost {len(lost)} candidates: {sorted(lost)[:3]}"


@pytest.mark.anyio
async def test_a_corpus_page_on_a_de_trusted_domain_is_never_offered(tmp_path: Path) -> None:
    """Trust is re-checked when the corpus is read, because the file outlives the registry row."""

    off_domain = "https://cheap-visas.example/apply-now"
    resolver = build(tmp_path, [INDEX], corpus=corpus_of(INDEX, off_domain))

    await resolver.resolve(destination(), corridor())

    assert all("cheap-visas" not in url for url in resolver.trace.shortlisted)


def scored_page(url: str, score: float) -> CandidatePage:
    return CandidatePage(
        link=PageLink(url=url, text="", heading="", depth=0, discovered_from="seed"),
        link_scores=RoleScores(
            scores={"document_checklist": score}, signals={"document_checklist": ["test"]}
        )
        if score
        else RoleScores(),
    )


@pytest.mark.anyio
async def test_a_pin_survives_the_shortlist_truncation(tmp_path: Path) -> None:
    """The half of entry 47's pin that was never actually implemented.

    `_shortlist` put pinned pages into `chosen` and then cut the tail by score without consulting
    them, so **a low-scoring pin was dropped** — which is the only pin that matters, since a page
    that wins the ranking never needed pinning. Measured on Canada's real corpus:
    `cbsa-asfc.gc.ca/travel-voyage/td-dv-eng.html` is `status="proven"`, scores **0.0** on role
    vocabulary, and was cut here with a pin naming it.

    The candidates below are spread one per domain so the per-domain floor alone fills the budget,
    which is what the truncation then has to arbitrate between.
    """

    pinned = "https://pinned.gov.example/answered-once.html"
    resolver = build(tmp_path, [], pinned=[pinned])
    candidates = [
        scored_page(pinned, 0.0),
        *(scored_page(f"https://d{n}.gov.example/page.html", 100.0 - n) for n in range(40)),
    ]

    shortlist = resolver._shortlist(candidates)

    assert len(shortlist) == DEFAULT_SHORTLIST_SIZE
    assert pinned in {candidate.link.url for candidate in shortlist}, (
        "a page that already answered this corridor must not have to win the ranking again"
    )
