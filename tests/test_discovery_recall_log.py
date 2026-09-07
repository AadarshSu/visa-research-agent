"""Writing down what a corridor considered, so a miss can be told from a mis-ranking.

Every test here is offline. The point of the file under test is a question asked *after* a run is
over — "was that page ranked out, or never found?" — so these run a whole corridor against the fake
site and then ask the record.
"""

import json
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
from visa_research_agent.discovery.page_text import PageTextStore, StoredPage
from visa_research_agent.discovery.recall_log import (
    ConsideredCandidate,
    FileRecallLog,
    ModelCall,
    RecallRecord,
    compare_runs,
)
from visa_research_agent.discovery.resolver import CorridorResolver, ResolutionTrace
from visa_research_agent.discovery.selection import Selection, SelectionQuotaExhausted
from visa_research_agent.domain.models import DestinationConfig
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


def record(outcome: str, candidates: list[tuple[str, bool, bool]]) -> RecallRecord:
    """One run's record, written as (url, shortlisted, fetched) so a case reads in one line."""

    return RecallRecord(
        corridor_key="canada/GB/GB/tourism",
        recorded_at=datetime(2026, 8, 22, 9, 0, tzinfo=UTC),
        outcome=outcome,
        candidates=[
            ConsideredCandidate(
                url=url,
                depth=0,
                best_score=50.0,
                shortlisted=shortlisted,
                fetched=fetched,
            )
            for url, shortlisted, fetched in candidates
        ],
    )


def test_a_page_one_run_read_and_another_never_saw_is_reported_first() -> None:
    """The Canada case: same corridor, same code, and one run simply never got the page.

    Ordering is the assertion, not a nicety. A person reading this is asking "what could that have
    cost me", so a candidate that reached the decider in one run and was absent in another has to
    come above the noise of pages that flickered without ever being read.
    """

    answering = "https://www.canada.ca/entry-requirements-country.html"
    noise = "https://www.canada.ca/newsroom.html"
    report = compare_runs(
        ["resolved", "refused"],
        [
            record("resolved", [(answering, True, True), (noise, False, False)]),
            record("refused", []),
        ],
    )

    assert report.flipped
    assert report.resolved_runs == 1
    assert [item.url for item in report.unstable][0] == answering
    assert report.unstable[0].reached_the_model
    assert report.unstable[0].runs_fetched == [1]


def test_runs_that_agree_are_not_reported_as_variance() -> None:
    same = [("https://www.canada.ca/a.html", True, True)]
    report = compare_runs(["resolved", "resolved"], [record("resolved", same)] * 2)

    assert not report.flipped
    assert report.stable == 1
    assert report.unstable == []


def test_the_run_count_comes_from_the_runs_not_from_the_records() -> None:
    """A recall-log write may fail silently (entry 43), and that must not erase a run.

    Written because the first version of this counted `len(records)`, so two runs where one failed
    to leave a record described themselves as one run — a diagnostic quietly understating how much
    evidence it had, which is the exact failure this file exists to prevent.
    """

    report = compare_runs(
        ["resolved", "refused"],
        [record("resolved", [("https://www.canada.ca/a.html", True, True)])],
    )

    assert report.runs == 2
    assert report.records_read == 1
    assert not report.comparison_is_complete
    assert report.flipped, "the outcomes still differ even though only one record survived"


# --- which selector actually chose, which is not which one was configured -----------------------


class FailingSelector:
    """A configured model selector whose call cannot succeed.

    This is the shape of what happened on 2026-08-28: the OpenAI account ran out of credit part-way
    through the twenty oracle corridors, so `SelectionQuotaExhausted` came back for the last seven
    and the heuristic ranking chose instead — honestly, and by design (entry 83).
    """

    def __init__(self) -> None:
        self.calls = 0

    async def select(self, system_prompt: str, packet: str) -> Selection:
        self.calls += 1
        raise SelectionQuotaExhausted("The OpenAI account is out of credit")


class PickingSelector:
    """A selector that names the first candidate it is offered, by reading the packet's ids."""

    def __init__(self) -> None:
        self.calls = 0

    async def select(self, system_prompt: str, packet: str) -> Selection:
        self.calls += 1
        entries = json.loads(packet)["candidates"]
        return Selection(source_ids=[entries[0]["source_id"]])


def indexed_destination() -> DestinationConfig:
    """The fake site under a real country's display name, so a page-text index can be found.

    `_destination_code` matches the display name against the country registry, so the ordinary
    "testland" fixture can never reach the selector at all — its index is looked up under a code
    that does not exist.
    """

    return destination().model_copy(update={"display_name": "Japan"})


def text_store(tmp_path: Path, urls: list[str]) -> PageTextStore:
    store = PageTextStore(tmp_path / "pagetext")
    store.write(
        "JP",
        [
            StoredPage(
                url=url,
                fetched_at=RESOLVED_AT,
                body="Visa requirements for Indian nationals applying from the United Kingdom. "
                * 20,
            )
            for url in urls
        ],
    )
    return store


async def test_a_configured_selector_that_never_chose_is_not_recorded_as_the_model(
    tmp_path: Path,
) -> None:
    """The defect, as one assertion.

    `selector` was derived at the write as `"model" if self.selector is not None else "heuristic"`,
    which records the *configuration*. A destination whose text index holds nothing never reaches
    the model at all — the heuristic ranks, exactly as it would with no selector configured — and
    calling that a model run puts the heuristic's own picks inside the model's arm when
    `selection-recall` replays them. Entries 91 and 97.
    """

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)
    selector = FailingSelector()
    resolver.selector = selector

    await resolver.resolve(destination(), corridor())

    assert log.records, "a run must be recorded"
    assert log.records[-1].selector == "heuristic"
    assert selector.calls == 0, "no index, so the model was never even asked"


async def test_a_failed_selection_records_the_arm_that_actually_ranked(tmp_path: Path) -> None:
    """The credit-exhaustion path: the model was asked, could not answer, and did not choose."""

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)
    selector = FailingSelector()
    resolver.selector = selector
    resolver.page_text = text_store(tmp_path, [INDEX, MISSION_INDEX, DETAIL_INDIA])

    resolved = await resolver.resolve(indexed_destination(), corridor())

    assert selector.calls == 1, "the model was asked"
    assert log.records[-1].selector == "heuristic", "and it did not choose"
    assert any("candidate selection failed" in note for note in resolved.notes)


async def test_a_selection_that_chose_is_recorded_as_the_model(tmp_path: Path) -> None:
    """The positive control, so the fix is not just 'always heuristic'."""

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)
    selector = PickingSelector()
    resolver.selector = selector
    resolver.page_text = text_store(tmp_path, [INDEX, MISSION_INDEX, DETAIL_INDIA])

    await resolver.resolve(indexed_destination(), corridor())

    assert selector.calls == 1
    assert log.records[-1].selector == "model"


# --- Where a corridor's seconds went (DECISIONS entry 142) -----------------------------------


def test_a_phase_records_what_it_spent_and_the_clock_is_injected() -> None:
    """Asserted without spending the seconds, which is why the clock is a seam."""

    ticks = iter([0.0, 2.5, 2.5, 9.0])
    trace = ResolutionTrace(clock=lambda: next(ticks))

    trace.begin("search")
    trace.begin("fetch")
    trace.end()

    assert trace.phase_seconds == {"search": 2.5, "fetch": 6.5}


def test_a_phase_entered_twice_accumulates() -> None:
    """A second visit replacing the first would under-report the slow runs worth reading."""

    ticks = iter([0.0, 1.0, 10.0, 13.0])
    trace = ResolutionTrace(clock=lambda: next(ticks))

    trace.begin("fetch")
    trace.end()
    trace.begin("fetch")
    trace.end()

    assert trace.phase_seconds == {"fetch": 4.0}


def test_closing_twice_is_safe_and_records_once() -> None:
    """`end` runs in a `finally` on every exit path, including ones that already closed."""

    ticks = iter([0.0, 3.0])
    trace = ResolutionTrace(clock=lambda: next(ticks))

    trace.begin("adjudicate")
    trace.end()
    trace.end()

    assert trace.phase_seconds == {"adjudicate": 3.0}


def test_a_run_that_never_started_a_phase_records_none() -> None:
    """An empty map means unrecorded, never a run that spent nothing — the field is graded that
    way because every log written before 2026-09-07 has one."""

    trace = ResolutionTrace(clock=lambda: 0.0)
    trace.end()

    assert trace.phase_seconds == {}


def test_the_record_carries_the_phases_and_an_older_log_reads_as_unrecorded(
    tmp_path: Path,
) -> None:
    """The field is optional, so a log written before it existed still loads."""

    log = FileRecallLog(tmp_path)
    corridor = Corridor(
        destination_slug="australia",
        passport_nationality="BD",
        applying_from="AE",
        purpose="tourism",
    )
    log.write(
        RecallRecord(
            corridor_key=corridor.key,
            recorded_at=datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
            outcome="resolved",
            phase_seconds={"search": 2.6, "fetch": 18.4},
        )
    )

    read = log.read(corridor)
    assert read is not None
    assert read.phase_seconds == {"search": 2.6, "fetch": 18.4}
    assert (
        RecallRecord(
            corridor_key=corridor.key,
            recorded_at=datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
            outcome="resolved",
        ).phase_seconds
        == {}
    )


# --- What a model call was given, and what it cost (DECISIONS entry 144) ---------------------


@pytest.mark.anyio
async def test_a_model_call_records_its_input_size_and_what_it_cost(tmp_path: Path) -> None:
    """The 4× adjudication spread of entry 143 had no handle because nothing recorded the input."""

    clock = [0.0]
    resolver = CorridorResolver(
        StubSearchProvider([]),  # type: ignore[arg-type]
        CrawlFetcher(host_delay_seconds=0.0),
        LiveSourceFetcher(
            FileSourceCache(tmp_path),
            ttl_hours=24.0,
            maximum_stale_hours=168.0,
            timeout_seconds=5.0,
            concurrency=2,
            maximum_characters=20_000,
            minimum_characters=10,
            user_agent="VisaResearchAgent/test",
        ),
        monotonic=lambda: clock[0],
    )

    async with resolver._timed_model_call("select", "PROMPT", "PACKET-LONGER"):
        clock[0] += 4.0

    assert resolver.model_call_timings == [
        ModelCall(
            call="select",
            prompt_characters=6,
            packet_characters=13,
            seconds=4.0,
            failed=False,
        )
    ]


@pytest.mark.anyio
async def test_a_failed_model_call_is_timed_and_kept(tmp_path: Path) -> None:
    """A slow failure costs the corridor exactly as much as a slow success, and a retry loop that
    dropped them would under-report the runs worth reading."""

    clock = [0.0]
    resolver = CorridorResolver(
        StubSearchProvider([]),  # type: ignore[arg-type]
        CrawlFetcher(host_delay_seconds=0.0),
        LiveSourceFetcher(
            FileSourceCache(tmp_path),
            ttl_hours=24.0,
            maximum_stale_hours=168.0,
            timeout_seconds=5.0,
            concurrency=2,
            maximum_characters=20_000,
            minimum_characters=10,
            user_agent="VisaResearchAgent/test",
        ),
        monotonic=lambda: clock[0],
    )

    with pytest.raises(SelectionQuotaExhausted):
        async with resolver._timed_model_call("roles", "P", "K"):
            clock[0] += 9.0
            raise SelectionQuotaExhausted("no credit")

    assert len(resolver.model_call_timings) == 1
    assert resolver.model_call_timings[0].failed is True
    assert resolver.model_call_timings[0].seconds == 9.0


def test_the_record_keeps_model_calls_and_an_older_log_reads_as_unrecorded(
    tmp_path: Path,
) -> None:
    """Empty means the log predates the field, not a run that made no calls — which is a real
    state a corridor reaches when it refuses before selection."""

    log = FileRecallLog(tmp_path)
    corridor = Corridor(
        destination_slug="japan",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )
    log.write(
        RecallRecord(
            corridor_key=corridor.key,
            recorded_at=datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
            outcome="resolved",
            model_calls=[
                ModelCall(
                    call="roles", prompt_characters=100, packet_characters=48000, seconds=22.9
                )
            ],
        )
    )

    read = log.read(corridor)
    assert read is not None
    assert read.model_calls[0].packet_characters == 48000
    assert read.model_calls[0].seconds == 22.9
    assert (
        RecallRecord(
            corridor_key=corridor.key,
            recorded_at=datetime(2026, 9, 7, 12, 0, tzinfo=UTC),
            outcome="resolved",
        ).model_calls
        == []
    )
