"""Counting why travellers go unanswered, and keeping the counts from lying about each other.

Every test here is offline. The thing under test exists because the project could say how often it
succeeded and could not say, in any countable form, why the rest failed — and the two failures that
matter most read identically in the prose the recall log had been keeping.
"""

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from discovery_site import AUTHORITY, INDEX, MISSION_INDEX, OFF_DOMAIN, destination, handler

from visa_research_agent.discovery.audit import (
    CAUSE_ORDER,
    POSTURE_COST,
    audit_records,
    counted,
    reachability,
    read_records,
)
from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.discovery.models import (
    Corridor,
    ResolvedCorridor,
    ResolvedSource,
    ResolvedTool,
)
from visa_research_agent.discovery.recall_log import FileRecallLog, RecallRecord
from visa_research_agent.discovery.registry import AuthorityRegistry, CountryAuthorities
from visa_research_agent.discovery.resolver import CorridorResolver
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.source_cache import FileSourceCache

pytestmark = pytest.mark.anyio

RESOLVED_AT = datetime(2026, 8, 24, 9, 0, tzinfo=UTC)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="testland",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def a_source(*roles: str) -> ResolvedSource:
    return ResolvedSource(
        source_id="testland_gov_index",
        title="Visa information",
        url="https://immigration.gov.example/visa/index.html",  # type: ignore[arg-type]
        authority="Testland immigration",
        kind="immigration_authority",
        roles=list(roles),  # type: ignore[arg-type]
        score=80.0,
    )


def resolved_with(**fields: object) -> ResolvedCorridor:
    return ResolvedCorridor(corridor=corridor(), resolved_at=RESOLVED_AT, **fields)  # type: ignore[arg-type]


def a_record(cause: str | None, **fields: object) -> RecallRecord:
    return RecallRecord(
        corridor_key=f"testland/IN/GB/{cause or 'legacy'}",
        recorded_at=RESOLVED_AT,
        outcome="resolved, with no visa_decision",
        cause=cause,  # type: ignore[arg-type]
        **fields,  # type: ignore[arg-type]
    )


# --- the distinction the whole thing exists for --------------------------------------------------


def test_a_refused_decision_and_a_handed_over_tool_are_different_causes() -> None:
    """The conflation this was built to end.

    Both of these write "resolved, with no visa_decision" into `outcome`, and one of them refuses
    the traveller while the other hands them the questionnaire that answers their question. Every
    United Kingdom run in the twenty-corridor logs is the second wearing the first's words.
    """

    not_found = resolved_with(sources=[a_source("document_checklist")])
    behind_a_tool = resolved_with(
        sources=[a_source("document_checklist")],
        interactive_tools=[ResolvedTool(role="visa_decision", url="https://gov.example/check")],
    )

    assert not_found.outcome_cause == "decision_not_found"
    assert behind_a_tool.outcome_cause == "resolved_decision_tool"
    assert not not_found.is_usable
    assert behind_a_tool.is_usable
    assert not_found.unresolved_roles == behind_a_tool.unresolved_roles, (
        "the two are indistinguishable on every field the log used to keep — which is the point"
    )


def test_a_blocked_decision_is_counted_apart_from_a_tool() -> None:
    """Different sentences to a traveller, and only one of them is a cost of the posture."""

    blocked = resolved_with(
        sources=[a_source("document_checklist")],
        decision_blocking_urls=["https://gov.example/check"],
    )

    assert blocked.outcome_cause == "resolved_decision_blocked"
    assert POSTURE_COST["resolved_decision_blocked"].startswith("yes")
    assert POSTURE_COST["resolved_decision_tool"].startswith("no")


def test_a_corridor_holding_both_counts_as_blocked() -> None:
    """The narrower fact wins: a refusal happened to a request, a tool is a judgement on a page."""

    both = resolved_with(
        sources=[a_source("document_checklist")],
        decision_blocking_urls=["https://gov.example/refused"],
        interactive_tools=[ResolvedTool(role="visa_decision", url="https://gov.example/check")],
    )

    assert both.outcome_cause == "resolved_decision_blocked"


def test_a_corridor_missing_only_its_checklist_resolved() -> None:
    """Entry 14's decision, held as a value. A missing checklist is reported, never a refusal."""

    resolved = resolved_with(
        sources=[a_source("visa_decision")],
        unresolved_roles=["document_checklist"],
    )

    assert resolved.outcome_cause == "resolved"
    assert resolved.is_usable


def test_every_cause_has_a_label_and_a_verdict() -> None:
    """A bucket nobody can read is a bucket nobody counts, and a blank verdict reads as 'no'."""

    for cause in CAUSE_ORDER:
        assert POSTURE_COST.get(cause), f"{cause} has no verdict on whether the posture cost it"


# --- what the resolver actually records ----------------------------------------------------------


async def sleep_none(_: float) -> None:
    return None


def build_resolver(
    tmp_path: Path,
    search_urls: list[str],
    recall_log: object | None,
) -> CorridorResolver:
    transport = httpx.MockTransport(handler([]))  # type: ignore[arg-type]
    return CorridorResolver(
        _StubSearch(search_urls),  # type: ignore[arg-type]
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


class _StubSearch:
    def __init__(self, urls: list[str]) -> None:
        self.urls = urls

    async def search(self, query: str, *, count: int) -> list[object]:
        from visa_research_agent.discovery.models import SearchResult

        return [
            SearchResult(url=url, title="", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls[:count])
        ]


class RecordingLog:
    def __init__(self) -> None:
        self.records: list[RecallRecord] = []

    def write(self, record: RecallRecord) -> None:
        self.records.append(record)


async def test_a_refusal_records_which_refusal_it_was(tmp_path: Path) -> None:
    log = RecordingLog()
    resolver = build_resolver(tmp_path, [OFF_DOMAIN], log)

    resolved = await resolver.resolve(destination(), corridor())

    assert not resolved.is_usable
    assert log.records[-1].cause == "no_candidates", (
        "a run that found nothing must not be counted as one that found pages and ranked them out"
    )


async def test_a_resolved_run_records_its_cause_and_its_unfilled_roles(tmp_path: Path) -> None:
    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)

    resolved = await resolver.resolve(destination(), corridor())

    record = log.records[-1]
    assert resolved.is_usable
    assert record.cause == "resolved"
    assert record.unresolved_roles == resolved.unresolved_roles


async def test_a_failure_met_reading_the_shortlist_reaches_the_recall_log(tmp_path: Path) -> None:
    """The regression this audit found by being run.

    `unreadable` was filled from the crawl's failures alone. That was complete only while the crawl
    ran, and the crawl left the request path (entry 51), so all 27 logs from the twenty-corridor
    measurement record nothing unreadable — on runs whose own `ResolvedCorridor` named three
    authorities that had refused us. A count taken from those logs would have reported the posture
    costing nothing, which is the opposite of what happened.

    The failure exercised here is the shortlist fetch's, whatever its outcome. Which outcome it is
    matters to what may be *said* (entries 32 and 36) and is checked where those live; what matters
    here is that the fetch stage reaches the log at all, because until now only the crawl did.
    """

    log = RecordingLog()
    resolver = build_resolver(tmp_path, [INDEX, MISSION_INDEX], log)

    await resolver.resolve(destination(), corridor())

    record = log.records[-1]
    assert record.unreadable_outcomes, "a shortlisted page that failed must be countable afterwards"
    fetched_stage = [url for url in record.unreadable_outcomes if AUTHORITY not in url]
    assert fetched_stage, "the mission page the shortlist could not read is the one at issue"
    assert set(record.unreadable_outcomes) <= set(record.unreadable), (
        "the typed outcome and the readable detail must describe the same URLs"
    )


# --- reachability, which no run can report -------------------------------------------------------


def a_registry(*rows: CountryAuthorities) -> AuthorityRegistry:
    return AuthorityRegistry(schema_version=1, generated_at=RESOLVED_AT, countries=list(rows))


def test_reachability_separates_a_country_with_no_row_from_one_with_no_domain() -> None:
    """Two refusals with different fixes: one needs the registry job run, one needs a reviewer."""

    countries = get_country_registry()
    registry = a_registry(
        CountryAuthorities(code="JP", name="Japan", trusted=["mofa.go.jp"]),
        CountryAuthorities(code="AT", name="Austria", unconfirmable=["bmeia.gv.at"]),
    )

    report = reachability(registry, countries)

    assert report.countries == len(countries.countries)
    assert report.researchable == ["JP"]
    assert report.row_without_domain == ["AT"]
    assert "DE" in report.no_row
    assert report.refused == report.countries - 1
    assert report.unconfirmable_candidates == {"AT": 1}, (
        "a country with declined candidates has something to promote; one with none has not"
    )


def test_reachability_matches_what_the_resolver_would_actually_be_given() -> None:
    """Read through `domains`, the same property the request path reads, so the two cannot drift."""

    countries = get_country_registry()
    reviewed_only = CountryAuthorities(
        code="DE",
        name="Germany",
        reviewed={"auswaertiges-amt.de": "the federal foreign office"},
    )

    report = reachability(a_registry(reviewed_only), countries)

    assert reviewed_only.domains, "a reviewed domain is fetchable and must count as researchable"
    assert report.researchable == ["DE"]


# --- aggregating a set of runs -------------------------------------------------------------------


def test_a_record_with_no_cause_is_reported_as_unrecorded_not_guessed() -> None:
    """Inferring the cause from the outcome sentence is the habit that produced two wrong entries.

    The legacy record here carries the exact prose a tool-resolved corridor and a refused one both
    write. There is no honest bucket for it, so it gets counted as having none.
    """

    report = audit_records([a_record(None), a_record("resolved")])

    assert report.records == 2
    assert report.unrecorded == 1
    assert report.causes["resolved"] == 1
    assert "decision_not_found" not in report.causes


def test_unreadable_pages_are_counted_by_typed_outcome_and_by_host() -> None:
    record = a_record(
        "resolved",
        unreadable={"https://a.gov.example/x": "403", "https://b.gov.example/y": "robots"},
        unreadable_outcomes={
            "https://a.gov.example/x": "blocked",
            "https://b.gov.example/y": "disallowed",
        },
    )

    report = audit_records([record])

    assert report.unreadable == Counter({"blocked": 1, "disallowed": 1})
    assert report.unreadable_hosts == Counter({"a.gov.example": 1, "b.gov.example": 1})


def test_counted_keeps_empty_buckets() -> None:
    """A bucket at zero is a finding. "Nothing refused us" is exactly what a reader needs to see."""

    rows = counted(Counter({"resolved": 3}), CAUSE_ORDER)

    assert [name for name, _ in rows] == list(CAUSE_ORDER)
    assert dict(rows)["no_candidates"] == 0


def test_counted_keeps_an_unexpected_bucket_rather_than_dropping_it() -> None:
    rows = counted(Counter({"resolved": 1, "not recorded": 9}), CAUSE_ORDER)

    assert rows[-1] == ("not recorded", 9)


def test_read_records_raises_on_a_file_it_cannot_parse(tmp_path: Path) -> None:
    """Skipping a broken log would understate the very bucket someone is counting."""

    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(ValueError):
        read_records(tmp_path)


def test_read_records_reads_what_the_log_wrote(tmp_path: Path) -> None:
    log = FileRecallLog(tmp_path)
    log.write(a_record("resolved"))

    records = read_records(tmp_path)

    assert [record.cause for record in records] == ["resolved"]
