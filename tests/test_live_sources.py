from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
from pydantic import AnyHttpUrl

from visa_research_agent.api.dependencies import build_source_fetcher
from visa_research_agent.config.loader import load_runtime_policy
from visa_research_agent.domain.models import (
    AppointedProvider,
    ConfiguredSource,
    DestinationConfig,
    FetchedSource,
    RuntimePolicy,
    SourceFailure,
    SourceMode,
)
from visa_research_agent.research.errors import LiveSourceError
from visa_research_agent.research.fixtures import FixtureSourceFetcher
from visa_research_agent.research.live_sources import LiveSourceFetcher, clean_source_html
from visa_research_agent.research.source_cache import CachedSource, FileSourceCache

SOURCE_URL = "https://immigration.gov.example/visa/india"
PAGE_BODY = "Indian passport holders require an entry visa. " * 40
LATER_BODY = "Indian passport holders now require an electronic visa. " * 40


def page(body: str) -> str:
    return (
        "<html><head><title>Visa</title><style>.a{color:red}</style></head>"
        "<body><nav>Home About Contact</nav><header>Ministry</header>"
        f"<main><p>{body}</p></main>"
        "<footer>Copyright</footer><script>track()</script></body></html>"
    )


def destination() -> DestinationConfig:
    return DestinationConfig(
        slug="testland",
        display_name="Testland",
        route_type="national",
        implementation_status="available",
        application_document_source_ids=["tl_visa_documents"],
        trusted_domains=["immigration.gov.example"],
        appointed_providers=[
            AppointedProvider(domain="provider.example", appointed_by="tl_visa_documents")
        ],
        sources=[
            ConfiguredSource(
                source_id="tl_visa_documents",
                title="Testland Visa Documents",
                url=AnyHttpUrl(SOURCE_URL),
                authority="Testland Immigration Authority",
                kind="immigration_authority",
                research_pass="primary",
            ),
            ConfiguredSource(
                source_id="tl_provider",
                title="Appointed Provider",
                url=AnyHttpUrl("https://provider.example/testland"),
                authority="Appointed provider",
                kind="official_application_provider",
                research_pass="follow_up",
            ),
        ],
    )


class Clock:
    """A controllable replacement for wall-clock time so TTL behaviour is deterministic."""

    def __init__(self) -> None:
        self.moment = datetime(2026, 8, 13, 9, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.moment

    def advance(self, hours: float) -> None:
        self.moment += timedelta(hours=hours)


def build_fetcher(
    tmp_path: Path,
    clock: Clock,
    handler: Callable[[httpx.Request], httpx.Response],
    requests: list[httpx.Request],
    *,
    ttl_hours: float = 24.0,
    maximum_stale_hours: float = 168.0,
    minimum_characters: int = 400,
) -> LiveSourceFetcher:
    def recording_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)

    return LiveSourceFetcher(
        FileSourceCache(tmp_path / "cache"),
        ttl_hours=ttl_hours,
        maximum_stale_hours=maximum_stale_hours,
        timeout_seconds=5.0,
        concurrency=2,
        maximum_characters=50_000,
        minimum_characters=minimum_characters,
        user_agent="test-agent",
        transport=httpx.MockTransport(recording_handler),
        now=clock,
    )


async def fetch_usable(fetcher: LiveSourceFetcher) -> list[FetchedSource]:
    """Retrieve and assert nothing was reported as a gap, for the happy-path tests."""

    report = await fetcher.fetch(destination())
    assert not report.failures, f"unexpected gaps: {report.failures}"
    return report.fetched


async def fetch_failure(fetcher: LiveSourceFetcher) -> SourceFailure:
    """Retrieve and return the single reported gap, for the degraded-path tests."""

    report = await fetcher.fetch(destination())
    assert not report.fetched
    assert len(report.failures) == 1
    return report.failures[0]


def test_clean_source_html_drops_chrome_and_blank_lines() -> None:
    cleaned = clean_source_html(page("Requirement text."), maximum_characters=50_000)

    assert "Requirement text." in cleaned
    for chrome in ("Home About Contact", "Ministry", "Copyright", "track()", "color:red"):
        assert chrome not in cleaned
    assert "\n\n" not in cleaned


def test_clean_source_html_truncates_to_the_character_budget() -> None:
    cleaned = clean_source_html(page(PAGE_BODY), maximum_characters=120)

    assert len(cleaned) <= 120


@pytest.mark.anyio
async def test_first_fetch_retrieves_live_text_and_records_real_provenance(
    tmp_path: Path,
) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []
    fetcher = build_fetcher(
        tmp_path, clock, lambda _: httpx.Response(200, text=page(PAGE_BODY)), requests
    )

    fetched = await fetch_usable(fetcher)

    # Only the primary source is retrieved; the follow-up provider is left alone.
    assert len(requests) == 1
    assert len(fetched) == 1
    assert fetched[0].source.source_id == "tl_visa_documents"
    assert fetched[0].from_cache is False
    assert fetched[0].source.is_stale is False
    assert fetched[0].source.retrieved_at == clock.moment
    assert "Indian passport holders require an entry visa." in fetched[0].content
    assert len(fetched[0].content_hash) == 64


@pytest.mark.anyio
async def test_second_fetch_inside_the_ttl_uses_cache_and_keeps_the_original_timestamp(
    tmp_path: Path,
) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []
    fetcher = build_fetcher(
        tmp_path, clock, lambda _: httpx.Response(200, text=page(PAGE_BODY)), requests
    )

    first = await fetch_usable(fetcher)
    first_retrieved_at = first[0].source.retrieved_at
    clock.advance(5)
    second = await fetch_usable(fetcher)

    assert len(requests) == 1, "a fetch inside the TTL must not hit the network again"
    assert second[0].from_cache is True
    assert second[0].source.is_stale is False
    # The honesty rule: cached evidence reports when it was really retrieved, not now.
    assert second[0].source.retrieved_at == first_retrieved_at
    assert second[0].source.retrieved_at != clock.moment


@pytest.mark.anyio
async def test_revalidation_past_the_ttl_sends_validators_and_accepts_not_modified(
    tmp_path: Path,
) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.headers.get("If-None-Match") == 'W/"v1"':
            return httpx.Response(304)
        return httpx.Response(200, text=page(PAGE_BODY), headers={"ETag": 'W/"v1"'})

    fetcher = build_fetcher(tmp_path, clock, handler, requests)

    await fetch_usable(fetcher)
    clock.advance(30)
    revalidated = await fetch_usable(fetcher)

    assert len(requests) == 2
    assert requests[1].headers["If-None-Match"] == 'W/"v1"'
    assert revalidated[0].from_cache is True
    assert revalidated[0].source.is_stale is False
    # A validator match confirms currency, so the clock advances to the moment of that check.
    assert revalidated[0].source.retrieved_at == clock.moment


@pytest.mark.anyio
async def test_changed_page_past_the_ttl_replaces_content_and_hash(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []
    bodies = [PAGE_BODY, LATER_BODY]

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=page(bodies[min(len(requests) - 1, 1)]))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)

    first = await fetch_usable(fetcher)
    clock.advance(30)
    second = await fetch_usable(fetcher)

    assert first[0].content_hash != second[0].content_hash
    assert "electronic visa" in second[0].content
    assert second[0].from_cache is False
    assert second[0].source.retrieved_at == clock.moment


@pytest.mark.anyio
async def test_failed_refresh_serves_cache_flagged_stale_with_its_true_age(
    tmp_path: Path,
) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(_: httpx.Request) -> httpx.Response:
        if len(requests) > 1:
            raise httpx.ConnectError("the authority is unreachable")
        return httpx.Response(200, text=page(PAGE_BODY))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)

    first = await fetch_usable(fetcher)
    clock.advance(48)
    degraded = await fetch_usable(fetcher)

    assert degraded[0].source.is_stale is True
    assert degraded[0].from_cache is True
    assert degraded[0].source.retrieved_at == first[0].source.retrieved_at


@pytest.mark.anyio
async def test_cached_evidence_past_the_stale_ceiling_is_reported_not_served(
    tmp_path: Path,
) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(_: httpx.Request) -> httpx.Response:
        if len(requests) > 1:
            raise httpx.ConnectError("the authority is unreachable")
        return httpx.Response(200, text=page(PAGE_BODY))

    fetcher = build_fetcher(tmp_path, clock, handler, requests, maximum_stale_hours=72.0)

    await fetch_usable(fetcher)
    clock.advance(200)
    failure = await fetch_failure(fetcher)

    assert failure.outcome == "unreachable"
    assert "past the 72 hour limit" in failure.detail


@pytest.mark.anyio
async def test_unreachable_source_with_no_cache_is_reported_as_a_gap(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("the authority is unreachable")

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    failure = await fetch_failure(fetcher)

    assert failure.outcome == "unreachable"
    assert failure.source_id == "tl_visa_documents"


@pytest.mark.anyio
async def test_client_rendered_shell_is_reported_unusable_not_treated_as_evidence(
    tmp_path: Path,
) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []
    shell = '<html><body><div id="root"></div><script>render()</script></body></html>'
    fetcher = build_fetcher(tmp_path, clock, lambda _: httpx.Response(200, text=shell), requests)

    failure = await fetch_failure(fetcher)

    assert failure.outcome == "unusable"
    assert "too little readable text" in failure.detail


@pytest.mark.anyio
async def test_error_status_without_cached_evidence_is_reported_as_a_gap(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []
    fetcher = build_fetcher(tmp_path, clock, lambda _: httpx.Response(503), requests)

    failure = await fetch_failure(fetcher)

    assert failure.outcome == "unreachable"
    assert "HTTP 503" in failure.detail


@pytest.mark.anyio
async def test_redirect_off_the_trusted_domains_is_refused_as_untrusted(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        # The approved URL redirects away to a domain the destination never approved, which then
        # serves perfectly plausible visa text. Content quality must not rescue it.
        if request.url.host == "immigration.gov.example":
            return httpx.Response(302, headers={"Location": "https://cheap-visas.example/testland"})
        return httpx.Response(200, text=page(PAGE_BODY))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    failure = await fetch_failure(fetcher)

    assert failure.outcome == "untrusted"
    assert failure.final_url is not None
    assert failure.final_url.host == "cheap-visas.example"
    assert "cheap-visas.example" in failure.detail
    # The redirect really was followed; the refusal is about trust, not a failed request.
    assert len(requests) == 2


@pytest.mark.anyio
async def test_destination_without_primary_sources_is_refused(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []
    fetcher = build_fetcher(tmp_path, clock, lambda _: httpx.Response(200), requests)

    with pytest.raises(LiveSourceError, match="No primary sources"):
        await fetcher.fetch(
            DestinationConfig(slug="empty", display_name="Empty", route_type="national")
        )


def test_cache_rejects_an_entry_stored_under_a_mismatched_url(tmp_path: Path) -> None:
    cache = FileSourceCache(tmp_path / "cache")
    cache.store(
        CachedSource(
            url="https://other.gov.example/page",
            final_url="https://other.gov.example/page",
            fetched_at=datetime(2026, 8, 13, 9, 0, tzinfo=UTC),
            content="text",
            content_hash="a" * 64,
            http_status=200,
        )
    )

    assert cache.load("https://other.gov.example/page") is not None
    assert cache.load(SOURCE_URL) is None


def test_cache_treats_a_corrupt_entry_as_a_miss(tmp_path: Path) -> None:
    cache = FileSourceCache(tmp_path / "cache")
    cache.store(
        CachedSource(
            url=SOURCE_URL,
            final_url=SOURCE_URL,
            fetched_at=datetime(2026, 8, 13, 9, 0, tzinfo=UTC),
            content="text",
            content_hash="a" * 64,
            http_status=200,
        )
    )
    (path,) = (tmp_path / "cache").glob("*.json")
    path.write_text("{not json", encoding="utf-8")

    assert cache.load(SOURCE_URL) is None


def test_cached_source_requires_a_timezone_aware_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        CachedSource(
            url=SOURCE_URL,
            final_url=SOURCE_URL,
            fetched_at=datetime(2026, 8, 13, 9, 0),
            content="text",
            content_hash="a" * 64,
            http_status=200,
        )


def policy(source_mode: SourceMode) -> RuntimePolicy:
    return RuntimePolicy(
        schema_version=1,
        source_mode=source_mode,
        extraction_mode="fixture",
        source_cache_ttl_hours=24.0,
        source_maximum_stale_hours=168.0,
    )


def test_source_mode_selects_the_matching_fetcher() -> None:
    assert isinstance(build_source_fetcher(policy("fixtures")), FixtureSourceFetcher)
    assert isinstance(build_source_fetcher(policy("live")), LiveSourceFetcher)


def test_committed_runtime_policy_loads_and_is_valid() -> None:
    loaded = load_runtime_policy()

    assert loaded.source_mode in ("fixtures", "live")
    assert loaded.extraction_mode in ("fixture", "openai")
    assert loaded.source_maximum_stale_hours >= loaded.source_cache_ttl_hours


def test_runtime_policy_rejects_a_stale_ceiling_below_the_ttl() -> None:
    with pytest.raises(ValueError, match="stale ceiling"):
        RuntimePolicy(
            schema_version=1,
            source_mode="live",
            extraction_mode="fixture",
            source_cache_ttl_hours=48.0,
            source_maximum_stale_hours=24.0,
        )


def test_stale_ceiling_shorter_than_the_ttl_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(LiveSourceError, match="stale ceiling"):
        LiveSourceFetcher(
            FileSourceCache(tmp_path / "cache"),
            ttl_hours=48.0,
            maximum_stale_hours=24.0,
            timeout_seconds=5.0,
            concurrency=1,
            maximum_characters=50_000,
            minimum_characters=400,
            user_agent="test-agent",
        )
