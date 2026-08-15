"""Search as a candidate generator, and the safeguards on proposing a new authority domain."""

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
    bootstrap_queries,
    corridor_queries,
    resolve_corridor_countries,
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
    corridor = Corridor(
        destination_slug="japan", passport_nationality="IN", applying_from="GB"
    )
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
