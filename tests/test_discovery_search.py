"""Search as a candidate generator, and the safeguards on proposing a new authority domain."""

import asyncio

import httpx
import pytest

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.discovery.bootstrap import (
    bootstrap_destination,
    entry_point_for,
    looks_governmental,
    propose_domains,
    registrable_domain,
)
from visa_research_agent.discovery.lexicon import get_country_registry, get_denylist
from visa_research_agent.discovery.models import Corridor, SearchResult
from visa_research_agent.discovery.search import (
    BraveSearchProvider,
    SearchError,
    SearchQuotaExhausted,
    SearchThrottled,
    bootstrap_queries,
    corridor_queries,
    resolve_corridor_countries,
    search_all,
    usable_results,
)
from visa_research_agent.domain.models import DestinationConfig


def japan() -> DestinationConfig:
    destination = load_destination_registry().get("japan")
    assert destination is not None
    return destination


def result(url: str, query: str, title: str = "A page", rank: int = 0) -> SearchResult:
    return SearchResult(url=url, title=title, query=query, rank=rank)


class FakeSearchProvider:
    """Returns canned results per query, and records what it was asked."""

    def __init__(self, responses: dict[str, list[SearchResult]]) -> None:
        self.responses = responses
        self.queries: list[str] = []

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        self.queries.append(query)
        return self.responses.get(query, [])


def test_registrable_domain_keeps_the_label_that_matters() -> None:
    assert registrable_domain("www.ica.gov.sg") == "ica.gov.sg"
    assert registrable_domain("uk.emb-japan.go.jp") == "emb-japan.go.jp"
    assert registrable_domain("www.example.com") == "example.com"


def test_government_shapes_are_recognised_without_being_decisive() -> None:
    assert looks_governmental("ica.gov.sg")
    assert looks_governmental("mofa.go.jp")
    assert looks_governmental("travel.gc.ca")
    assert not looks_governmental("ivisa.com")


def test_corridor_queries_are_restricted_to_approved_domains() -> None:
    registry = get_country_registry()
    corridor = Corridor(destination_slug="japan", passport_nationality="IN", applying_from="GB")
    nationality, residence = resolve_corridor_countries(corridor, registry)

    queries = corridor_queries(corridor, japan(), nationality, residence)

    assert queries, "a destination with trusted domains must produce queries"
    for query in queries:
        assert query.startswith("site:"), query
    assert any("mofa.go.jp" in query for query in queries)
    assert any("India" in query for query in queries)


def test_results_off_the_approved_domains_are_dropped_before_anything_is_fetched() -> None:
    results = [
        result("https://www.mofa.go.jp/visa", "q"),
        result("https://ivisa.com/japan-visa", "q"),
        result("https://notmofa.go.jp/visa", "q"),
    ]

    kept = usable_results(results, japan())

    assert [item.url for item in kept] == ["https://www.mofa.go.jp/visa"]


def test_a_domain_seen_in_only_one_query_is_not_proposed() -> None:
    report = propose_domains(
        "Japan",
        {
            "q1": [result("https://www.mofa.go.jp/visa", "q1")],
            "q2": [result("https://other.go.jp/x", "q2")],
        },
        get_denylist(),
    )

    assert report.proposals == []
    assert "only 1 of the queries" in report.rejected["mofa.go.jp"]


def test_a_corroborated_government_domain_is_proposed_with_its_evidence() -> None:
    report = propose_domains(
        "Japan",
        {
            "q1": [result("https://www.mofa.go.jp/visa", "q1", "Visa | MOFA")],
            "q2": [result("https://www.mofa.go.jp/j_info/visit/visa/", "q2", "Visa index")],
        },
        get_denylist(),
    )

    assert [proposal.domain for proposal in report.proposals] == ["mofa.go.jp"]
    proposal = report.proposals[0]
    assert proposal.looks_governmental
    assert proposal.suggested_kind == "foreign_ministry"
    assert proposal.corroboration == 2
    assert proposal.example_urls


def test_a_commercial_visa_agency_is_removed_before_a_human_sees_it() -> None:
    report = propose_domains(
        "Japan",
        {
            "q1": [
                result("https://ivisa.com/japan", "q1"),
                result("https://www.mofa.go.jp/a", "q1"),
            ],
            "q2": [
                result("https://ivisa.com/japan/apply", "q2"),
                result("https://www.mofa.go.jp/b", "q2"),
            ],
        },
        get_denylist(),
    )

    assert [proposal.domain for proposal in report.proposals] == ["mofa.go.jp"]
    assert "denylist" in report.rejected["ivisa.com"]


def test_a_bare_public_suffix_can_never_be_proposed() -> None:
    report = propose_domains(
        "Singapore",
        {
            "q1": [result("https://gov.sg/visa", "q1")],
            "q2": [result("https://gov.sg/apply", "q2")],
        },
        get_denylist(),
    )

    assert report.proposals == []
    assert "public suffix" in report.rejected["gov.sg"]


def test_government_domains_are_ranked_above_other_corroborated_ones() -> None:
    report = propose_domains(
        "Japan",
        {
            "q1": [
                result("https://japan-guide.example/visa", "q1"),
                result("https://www.mofa.go.jp/a", "q1"),
            ],
            "q2": [
                result("https://japan-guide.example/apply", "q2"),
                result("https://www.mofa.go.jp/b", "q2"),
            ],
        },
        get_denylist(),
    )

    # The non-government site still appears for review; it is ranked below, never auto-admitted.
    assert [proposal.domain for proposal in report.proposals] == [
        "mofa.go.jp",
        "japan-guide.example",
    ]


def test_the_entry_point_prefers_a_visa_path() -> None:
    report = propose_domains(
        "Japan",
        {
            "q1": [result("https://www.mofa.go.jp/", "q1")],
            "q2": [result("https://www.mofa.go.jp/j_info/visit/visa/index.html", "q2")],
        },
        get_denylist(),
    )

    assert entry_point_for(report.proposals[0]) == (
        "https://www.mofa.go.jp/j_info/visit/visa/index.html"
    )


@pytest.mark.anyio
async def test_bootstrap_runs_every_query_and_returns_proposals() -> None:
    queries = bootstrap_queries("Japan")
    provider = FakeSearchProvider(
        {query: [result("https://www.mofa.go.jp/visa", query)] for query in queries}
    )

    report = await bootstrap_destination("Japan", provider, get_denylist())

    assert provider.queries == queries
    assert [proposal.domain for proposal in report.proposals] == ["mofa.go.jp"]


@pytest.mark.anyio
async def test_the_search_provider_parses_results_and_reports_failures() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Subscription-Token"] == "test-key"
        return httpx.Response(
            200,
            json={
                "web": {
                    "results": [
                        {"url": "https://www.mofa.go.jp/visa", "title": "Visa", "description": "d"},
                        {"title": "no url here"},
                    ]
                }
            },
        )

    provider = BraveSearchProvider("test-key", transport=httpx.MockTransport(handler))
    results = await provider.search("japan visa", count=5)

    assert [item.url for item in results] == ["https://www.mofa.go.jp/visa"]
    assert results[0].query == "japan visa"


@pytest.mark.anyio
async def test_a_failing_search_provider_raises_a_domain_error() -> None:
    provider = BraveSearchProvider(
        "test-key", transport=httpx.MockTransport(lambda _: httpx.Response(429))
    )

    with pytest.raises(SearchError, match="HTTP 429"):
        await provider.search("japan visa", count=5)


def test_a_missing_api_key_is_refused_at_construction() -> None:
    with pytest.raises(SearchError, match="search API key"):
        BraveSearchProvider("   ")


def test_another_countrys_government_never_outranks_the_destinations_own() -> None:
    """Found on the first real Vietnam run: the US embassy in Vietnam ranked above Vietnam's own
    immigration department, because any country's .gov satisfies "looks governmental"."""

    report = propose_domains(
        "Vietnam",
        {
            "q1": [
                result("https://vn.usembassy.gov/vietnamese-visas/", "q1"),
                result("https://immigration.gov.vn/", "q1"),
            ],
            "q2": [
                result("https://travel.state.gov/vietnam", "q2"),
                result("https://vn.usembassy.gov/entry-exit/", "q2"),
                result("https://immigration.gov.vn/apply", "q2"),
            ],
        },
        get_denylist(),
        ["vn"],
    )

    assert report.proposals[0].domain == "immigration.gov.vn"
    assert report.proposals[0].belongs_to_destination
    # The foreign government pages still appear for review, flagged, but never first.
    assert not report.proposals[1].belongs_to_destination


def test_the_destinations_own_government_needs_only_one_corroborating_query() -> None:
    """Vietnam's own foreign ministry was discarded for appearing in a single query."""

    report = propose_domains(
        "Vietnam",
        {"q1": [result("https://mofa.gov.vn/visa", "q1")]},
        get_denylist(),
        ["vn"],
    )

    assert [proposal.domain for proposal in report.proposals] == ["mofa.gov.vn"]


def test_a_foreign_government_domain_still_needs_full_corroboration() -> None:
    report = propose_domains(
        "Vietnam",
        {"q1": [result("https://travel.state.gov/vietnam", "q1")]},
        get_denylist(),
        ["vn"],
    )

    assert report.proposals == []
    assert "at least 2" in report.rejected["state.gov"]


def test_a_country_whose_own_domain_is_the_governmental_marker_gets_no_relaxed_bar() -> None:
    """The relaxed bar is earned by two separate signals, and here there is only one.

    Written against a fictional country rather than the one that exposed this, because the defect
    is the shape of the rule: a top-level domain that is itself the generic governmental marker
    makes "governmental" and "under its own domain" the same question, and admits that
    government's whole namespace rather than its visa authorities.
    """

    report = propose_domains(
        "Wonderland",
        {"q1": [result("https://interior.gov/international", "q1")]},
        get_denylist(),
        ["wl", "gov"],
    )

    assert report.proposals == []
    assert "at least 2" in report.rejected["interior.gov"]


def test_the_same_country_still_admits_a_corroborated_own_domain() -> None:
    """Narrowing the bar must not close the door: two queries is the ordinary bar, not a veto."""

    report = propose_domains(
        "Wonderland",
        {
            "q1": [result("https://wlembassy.gov/visas/", "q1")],
            "q2": [result("https://wlembassy.gov/visas/tourist", "q2")],
        },
        get_denylist(),
        ["wl", "gov"],
    )

    assert [proposal.domain for proposal in report.proposals] == ["wlembassy.gov"]
    assert report.proposals[0].is_own_government


def test_ownership_under_a_plain_country_code_remains_a_second_signal() -> None:
    """Only the top-level domain that actually matched decides this, not the country's whole list.

    A country holding both a plain code and a governmental one must keep the relaxed bar for
    domains under the plain code, or one entry in `countries.yaml` would quietly raise the bar for
    every domain of that country.
    """

    report = propose_domains(
        "Wonderland",
        {"q1": [result("https://immigration.go.wl/apply", "q1")]},
        get_denylist(),
        ["wl", "gov"],
    )

    assert [proposal.domain for proposal in report.proposals] == ["immigration.go.wl"]
    proposal = report.proposals[0]
    assert proposal.matched_tlds == ["wl"]
    assert proposal.ownership_is_independent


def test_a_multipart_governmental_suffix_is_recognised_as_the_marker() -> None:
    report = propose_domains(
        "Wonderland",
        {"q1": [result("https://interior.gov.wl/international", "q1")]},
        get_denylist(),
        ["wl", "gov.wl"],
    )

    # Matched under both, but `wl` is a plain code, so ownership still says something extra.
    assert [proposal.domain for proposal in report.proposals] == ["interior.gov.wl"]
    assert report.proposals[0].matched_tlds == ["wl", "gov.wl"]
    # And the bare suffix itself can never be proposed, whatever the country lists.
    assert registrable_domain("interior.gov.wl") == "interior.gov.wl"


def test_registrable_domain_is_still_importable_from_bootstrap() -> None:
    """It moved to `domain.trust` beside the other hostname rules; callers here are unchanged."""

    assert registrable_domain("in.usembassy.gov") == "usembassy.gov"
    assert registrable_domain("www.ica.gov.sg") == "ica.gov.sg"


@pytest.mark.anyio
async def test_queries_run_together_but_are_read_in_the_order_they_were_asked() -> None:
    """Which page a corridor resolves to depends on the order candidates are considered, so it must
    not depend on which query the engine happened to answer first. The slowest query here is the
    first one asked, so a dict built from completion order would come out reversed."""

    class SlowFirst:
        async def search(self, query: str, *, count: int) -> list[SearchResult]:
            await asyncio.sleep(0.02 if query == "first" else 0.0)
            return [result(f"https://example.gov/{query}", query)]

    found = await search_all(SlowFirst(), ["first", "second", "third"], count=5)

    assert list(found) == ["first", "second", "third"]
    assert found["first"][0].url == "https://example.gov/first"


@pytest.mark.anyio
async def test_a_failing_query_still_fails_the_run() -> None:
    """Unchanged from when these ran one at a time. Whether a partly-searched corridor is safe to
    serve is a separate decision, and it has not been made."""

    class OneBadQuery:
        async def search(self, query: str, *, count: int) -> list[SearchResult]:
            if query == "bad":
                raise SearchError("the search provider answered HTTP 429")
            return []

    with pytest.raises(SearchError):
        await search_all(OneBadQuery(), ["good", "bad"], count=5)


@pytest.mark.anyio
async def test_no_more_queries_are_in_flight_than_the_limit_allows() -> None:
    """A search API is someone else's rate limit, and a burst that trips it turns a resolvable
    corridor into a refusal."""

    in_flight = 0
    highest = 0

    class Counting:
        async def search(self, query: str, *, count: int) -> list[SearchResult]:
            nonlocal in_flight, highest
            in_flight += 1
            highest = max(highest, in_flight)
            try:
                await asyncio.sleep(0.01)
                return []
            finally:
                in_flight -= 1

    await search_all(Counting(), [f"q{index}" for index in range(12)], count=5, concurrency=4)

    assert highest == 4


# --- telling a spend cap apart from a query sent too soon ------------------------------------


EXHAUSTED = {
    "type": "ErrorResponse",
    "error": {
        "id": "df56ac42",
        "status": 402,
        "detail": "Usage limit exceeded.",
        "meta": {"plan": "Search", "current_spend": 25.01, "usage_limit": 25.0},
    },
}


@pytest.mark.anyio
async def test_a_spend_cap_is_reported_as_an_exhausted_account() -> None:
    """Brave answers `402` for both causes, and only the body separates them.

    Reported as one thing, it cost a session an hour of believing the account was empty while
    single queries answered fine — so the difference is a type, not a sentence. DECISIONS entry 74.
    """

    provider = BraveSearchProvider(
        "test-key",
        transport=httpx.MockTransport(lambda _: httpx.Response(402, json=EXHAUSTED)),
        minimum_interval_seconds=0.0,
    )

    with pytest.raises(SearchQuotaExhausted) as raised:
        await provider.search("anything", count=5)

    assert "25.01" in str(raised.value)
    assert isinstance(raised.value, SearchError)


@pytest.mark.anyio
async def test_a_402_with_no_spend_figures_is_reported_as_a_throttle() -> None:
    provider = BraveSearchProvider(
        "test-key",
        transport=httpx.MockTransport(lambda _: httpx.Response(402, json={"error": {}})),
        minimum_interval_seconds=0.0,
    )

    with pytest.raises(SearchThrottled) as raised:
        await provider.search("anything", count=5)

    assert "rate limit" in str(raised.value)
    assert not isinstance(raised.value, SearchQuotaExhausted)


@pytest.mark.anyio
async def test_queries_are_paced_even_when_several_are_asked_at_once() -> None:
    """The pace is the provider's, not the caller's.

    `search_all` runs four queries at a time, so a limiter that lived per-call would let four
    leave together and trip exactly the cap it exists to respect.
    """

    slept: list[float] = []
    clock = [0.0]

    async def sleep(seconds: float) -> None:
        slept.append(seconds)
        clock[0] += seconds

    provider = BraveSearchProvider(
        "test-key",
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"web": {"results": []}})),
        minimum_interval_seconds=1.3,
        sleep=sleep,
        now=lambda: clock[0],
    )

    await search_all(provider, ["a", "b", "c"], count=5, concurrency=4)

    assert slept == pytest.approx([1.3, 1.3])
