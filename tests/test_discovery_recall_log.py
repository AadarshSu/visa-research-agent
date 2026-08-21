"""Writing down what a corridor considered, so a miss can be told from a mis-ranking.

Every test here is offline. The point of the file under test is a question asked *after* a run is
over — "was that page ranked out, or never found?" — so these run a whole corridor against the fake
site and then ask the record.
"""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from discovery_site import (
    DETAIL_INDIA,
    INDEX,
    MISSION_INDEX,
    OFF_DOMAIN,
    destination,
    handler,
)

from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.models import Corridor
from visa_research_agent.discovery.recall_log import (
    FileRecallLog,
    RecallRecord,
)
from visa_research_agent.discovery.resolver import CorridorResolver
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.source_cache import FileSourceCache

pytestmark = pytest.mark.anyio

RESOLVED_AT = datetime(2026, 8, 21, 9, 0, tzinfo=UTC)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="testland",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


class StubSearchProvider:
    def __init__(self, urls: list[str]) -> None:
        self.urls = urls

    async def search(self, query: str, *, count: int) -> list[object]:
        from visa_research_agent.discovery.models import SearchResult

        return [
            SearchResult(url=url, title="", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls[:count])
        ]


class RecordingLog:
    """Keeps every record in memory, so a test can see the run that was overwritten."""

    def __init__(self) -> None:
        self.records: list[RecallRecord] = []

    def write(self, record: RecallRecord) -> None:
        self.records.append(record)


class UnwritableLog:
    def write(self, record: RecallRecord) -> None:
        raise OSError("the disk is full")


async def sleep_none(_: float) -> None:
    return None


def build_resolver(
    tmp_path: Path,
    search_urls: list[str],
    recall_log: object | None,
) -> CorridorResolver:
    transport = httpx.MockTransport(handler([]))  # type: ignore[arg-type]
    return CorridorResolver(
        StubSearchProvider(search_urls),  # type: ignore[arg-type]
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
        recall_log=recall_log,  # type: ignore[arg-type]
        now=lambda: RESOLVED_AT,
    )


async def test_a_resolved_run_records_every_candidate_with_its_score(tmp_path: Path) -> None:
    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)

    resolved = await resolver.resolve(destination(), corridor())

    assert resolved.is_usable
    record = log.records[-1]
    assert record.corridor_key == "testland/IN/GB/tourism"
    assert record.outcome == "resolved"
    assert record.queries, "the queries are half of why a page was never found"
    assert len(record.candidates) > len(record.shortlisted)
    assert all(row.best_score >= 0 for row in record.candidates)
    assert [row.best_score for row in record.candidates] == sorted(
        (row.best_score for row in record.candidates), reverse=True
    ), "recorded in the order the shortlist was cut in"


async def test_the_record_answers_which_kind_of_miss_it_was(tmp_path: Path) -> None:
    """The whole reason the file exists: never seen and seen-but-not-used must look different."""

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)

    await resolver.resolve(destination(), corridor())
    record = log.records[-1]

    seen = record.find("/detail/india.html")
    assert seen, "this page is on the fake site and must be recorded as considered"
    assert seen[0].url == DETAIL_INDIA
    assert record.find("entry-requirements-country") == [], (
        "a page nobody ever discovered must come back empty, not with a zero score"
    )


async def test_a_refused_run_is_recorded_too(tmp_path: Path) -> None:
    """The runs worth reading are the ones that failed, so a refusal must not skip the log."""

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [OFF_DOMAIN], log)

    resolved = await resolver.resolve(destination(), corridor())

    assert not resolved.is_usable
    record = log.records[-1]
    assert record.outcome != "resolved"
    assert record.outcome in resolved.notes


async def test_shortlisted_and_fetched_are_recorded_apart(tmp_path: Path) -> None:
    """A shortlisted page that could not be read is a third answer, lost if the two are merged."""

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)

    await resolver.resolve(destination(), corridor())
    record = log.records[-1]

    assert all(row.shortlisted for row in record.candidates if row.fetched)
    assert any(not row.shortlisted for row in record.candidates)


async def test_a_log_that_cannot_be_written_never_costs_the_corridor_its_answer(
    tmp_path: Path,
) -> None:
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], UnwritableLog())

    resolved = await resolver.resolve(destination(), corridor())

    assert resolved.is_usable


async def test_without_a_log_a_corridor_behaves_exactly_as_before(tmp_path: Path) -> None:
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], None)

    resolved = await resolver.resolve(destination(), corridor())

    assert resolved.is_usable


async def test_the_file_log_round_trips_and_keeps_only_the_newest_run(tmp_path: Path) -> None:
    log = FileRecallLog(tmp_path / "recall")
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)

    await resolver.resolve(destination(), corridor())
    first = log.read(corridor())
    await resolver.resolve(destination(), corridor())
    second = log.read(corridor())

    assert first is not None and second is not None
    assert first.corridor_key == second.corridor_key
    assert len(list((tmp_path / "recall").glob("*.json"))) == 1


def test_a_record_read_back_from_disk_is_the_one_written(tmp_path: Path) -> None:
    log = FileRecallLog(tmp_path / "recall")
    record = RecallRecord(
        corridor_key="canada/GB/GB/tourism",
        recorded_at=RESOLVED_AT,
        outcome="no candidate shows the result for a GB passport holder",
        queries=["canada visa british citizen"],
    )

    log.write(record)

    assert (
        log.read(Corridor(destination_slug="canada", passport_nationality="GB", applying_from="GB"))
        == record
    )
