"""Resolving a whole corridor: search, crawl, fetch, assign roles, or refuse."""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from discovery_site import (
    ARCHIVED,
    DETAIL_CHINA,
    DETAIL_INDIA,
    EXEMPTIONS,
    INDEX,
    MISSION_INDEX,
    MISSION_SPOUSE,
    OFF_DOMAIN,
    destination,
    handler,
)

from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.models import (
    CandidatePage,
    Corridor,
    PageLink,
    RoleScores,
    SearchResult,
)
from visa_research_agent.discovery.resolver import (
    CorridorResolver,
    build_source_id,
    clean_title,
    derive_authority,
)
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.source_cache import FileSourceCache

RESOLVED_AT = datetime(2026, 8, 15, 9, 0, tzinfo=UTC)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="testland",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


class StubSearchProvider:
    """Returns the same ranked URLs for every query, including deliberate spam."""

    def __init__(self, urls: list[str]) -> None:
        self.urls = urls
        self.queries: list[str] = []

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        self.queries.append(query)
        return [
            SearchResult(url=url, title="", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls[:count])
        ]


async def sleep_none(_: float) -> None:
    return None


def build_resolver(
    tmp_path: Path,
    requests: list[httpx.Request],
    search_urls: list[str],
) -> tuple[CorridorResolver, StubSearchProvider]:
    transport = httpx.MockTransport(handler(requests))  # type: ignore[arg-type]
    provider = StubSearchProvider(search_urls)
    crawl_fetcher = CrawlFetcher(transport=transport, sleep=sleep_none, host_delay_seconds=0.0)
    live_fetcher = LiveSourceFetcher(
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
    )
    resolver = CorridorResolver(
        provider,
        crawl_fetcher,
        live_fetcher,
        minimum_role_score=10.0,
        now=lambda: RESOLVED_AT,
    )
    return resolver, provider


def test_source_ids_are_derived_from_the_url_so_they_are_stable() -> None:
    taken: set[str] = set()

    first = build_source_id("testland", DETAIL_INDIA, taken)
    second = build_source_id("testland", DETAIL_INDIA, set())

    assert first == second, "the same page must keep the same id between runs"
    assert first.startswith("testland_")
    assert "india" in first


def test_colliding_source_ids_are_disambiguated() -> None:
    taken: set[str] = set()

    first = build_source_id("testland", "https://immigration.gov.example/a/index.html", taken)
    second = build_source_id("testland", "https://immigration.gov.example/b/index.html", taken)

    assert first != second


def test_a_title_loses_the_site_name_authorities_append() -> None:
    assert clean_title("Visa: Temporary Visitor Visa | Embassy of Japan", "x") == (
        "Visa: Temporary Visitor Visa"
    )
    assert clean_title(None, "fallback") == "fallback"


def test_an_authority_is_named_from_the_host() -> None:
    authority, kind = derive_authority(MISSION_INDEX, destination())

    assert "mission" in authority.lower()
    assert kind == "embassy_or_high_commission"


@pytest.mark.anyio
async def test_a_corridor_resolves_to_the_right_pages(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    resolver, provider = build_resolver(tmp_path, requests, [INDEX, MISSION_INDEX])

    resolved = await resolver.resolve(destination(), corridor())

    assert provider.queries, "search should have been consulted"
    assert resolved.is_usable, f"unresolved: {resolved.unresolved_roles} notes={resolved.notes}"

    by_role = {role: source for source in resolved.sources for role in source.roles}
    assert "visa_decision" in by_role
    assert "document_checklist" in by_role

    # Either genuine decision page is acceptable: the exemptions list establishes the rule and the
    # per-nationality page confirms it. Japan's hand-curated config uses the exemptions page and
    # Singapore's uses the per-nationality one, so both are right answers.
    assert str(by_role["visa_decision"].url) in {EXEMPTIONS, DETAIL_INDIA}
    # What must never happen is a page about a different nationality being chosen.
    assert all(str(source.url) != DETAIL_CHINA for source in resolved.sources)
    assert by_role["visa_decision"].signals, "a selection must record why it was made"


@pytest.mark.anyio
async def test_resolution_never_touches_a_host_outside_the_approved_domains(
    tmp_path: Path,
) -> None:
    """Search returns spam; none of it may ever be requested."""

    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(
        tmp_path, requests, [OFF_DOMAIN, "https://ivisa.com/testland", INDEX]
    )

    await resolver.resolve(destination(), corridor())

    assert requests
    for request in requests:
        assert destination().trusts_host(host_of(str(request.url))), request.url


@pytest.mark.anyio
async def test_a_page_for_another_nationality_is_never_selected(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(tmp_path, requests, [DETAIL_CHINA, INDEX])

    resolved = await resolver.resolve(destination(), corridor())

    assert all(str(source.url) != DETAIL_CHINA for source in resolved.sources)


@pytest.mark.anyio
async def test_an_archived_page_is_never_selected(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(tmp_path, requests, [ARCHIVED, INDEX])

    resolved = await resolver.resolve(destination(), corridor())

    assert all(str(source.url) != ARCHIVED for source in resolved.sources)


@pytest.mark.anyio
async def test_a_wrong_audience_page_does_not_become_the_checklist(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(tmp_path, requests, [MISSION_SPOUSE, MISSION_INDEX, INDEX])

    resolved = await resolver.resolve(destination(), corridor())

    checklist = [s for s in resolved.sources if "document_checklist" in s.roles]
    assert all(str(source.url) != MISSION_SPOUSE for source in checklist)


@pytest.mark.anyio
async def test_a_corridor_with_nothing_usable_is_refused_rather_than_guessed(
    tmp_path: Path,
) -> None:
    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(tmp_path, requests, [OFF_DOMAIN])

    resolved = await resolver.resolve(destination(), corridor())

    assert not resolved.is_usable
    assert resolved.sources == []
    assert set(resolved.unresolved_roles) >= {"visa_decision", "document_checklist"}
    assert resolved.notes, "a refusal must explain itself"


@pytest.mark.anyio
async def test_a_resolved_corridor_converts_into_a_loadable_destination(tmp_path: Path) -> None:
    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(tmp_path, requests, [INDEX, MISSION_INDEX])

    resolved = await resolver.resolve(destination(), corridor())
    config = resolved.to_destination_config(destination())

    assert config.application_document_source_ids
    assert config.load_bearing_source_ids
    # Everything downstream now treats this exactly like hand-written configuration.
    assert all(config.trusts_host(host_of(str(source.url))) for source in config.sources)


@pytest.mark.anyio
async def test_resolution_costs_no_model_calls(tmp_path: Path) -> None:
    """The cost guarantee: the heuristics decide, so a corridor is free to resolve."""

    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(tmp_path, requests, [INDEX, MISSION_INDEX])

    resolved = await resolver.resolve(destination(), corridor())

    assert resolved.model_calls == 0


def test_the_shortlist_budget_is_filled_rather_than_left_part_used(tmp_path: Path) -> None:
    """Taking only the top few per role left most of the fetch budget unspent.

    Vietnam used six of ten places while every readable `evisa.gov.vn` page sat just outside the
    per-role cut, so the one site that needed rendering was never read at all.
    """

    resolver, _ = build_resolver(tmp_path, [], [])
    candidates = [
        CandidatePage(
            link=PageLink(
                url=f"https://immigration.gov.example/visa/p{index}",
                text="Visa documents required",
                heading="",
                depth=1,
                discovered_from="seed",
            ),
            link_scores=RoleScores(scores={"document_checklist": 50.0 - index}),
            found_by="crawl",
        )
        for index in range(12)
    ]

    shortlist = resolver._shortlist(candidates)

    assert len(shortlist) == resolver.shortlist_size
    # Still best-first: filling spare places must not promote a weak page over a strong one.
    assert shortlist[0].link.url.endswith("p0")


def test_a_candidate_no_role_wants_is_not_worth_fetching(tmp_path: Path) -> None:
    resolver, _ = build_resolver(tmp_path, [], [])
    candidates = [
        CandidatePage(
            link=PageLink(
                url=f"https://immigration.gov.example/visa/p{index}",
                text="",
                heading="",
                depth=1,
                discovered_from="seed",
            ),
            link_scores=RoleScores(scores={}),
            found_by="crawl",
        )
        for index in range(12)
    ]

    assert resolver._shortlist(candidates) == []
