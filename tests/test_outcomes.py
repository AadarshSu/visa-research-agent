"""How incomplete evidence is graded, and when a run is refused outright."""

from importlib.resources import files
from typing import Any

import pytest
import yaml
from pydantic import AnyHttpUrl

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.domain.models import (
    DestinationConfig,
    FailureOutcome,
    RetrievalReport,
    SourceFailure,
    VisaPlanDraft,
)
from visa_research_agent.research.errors import InsufficientEvidenceError
from visa_research_agent.research.fixtures import FixtureSourceFetcher, FixtureVisaPlanExtractor
from visa_research_agent.research.openai_extraction import OpenAIVisaPlanExtractor
from visa_research_agent.research.outcomes import resolve_plan_status

OPTIONAL_SOURCE = "sg_mfa_check_visa"
REQUIRED_SOURCE = "sg_ica_india_visa_details"


def singapore_config() -> DestinationConfig:
    singapore = load_destination_registry().get("singapore")
    assert singapore is not None
    return singapore


def load_golden_draft() -> VisaPlanDraft:
    resource = files("visa_research_agent.fixtures.singapore").joinpath("plan.yaml")
    raw_plan: Any = yaml.safe_load(resource.read_text(encoding="utf-8"))
    return VisaPlanDraft.model_validate(raw_plan)


class FakeStructuredPlanGenerator:
    def __init__(self, result: VisaPlanDraft) -> None:
        self.result = result
        self.calls = 0

    async def generate(self, system_prompt: str, research_packet: str) -> VisaPlanDraft:
        self.calls += 1
        return self.result


async def singapore_report() -> RetrievalReport:
    return await FixtureSourceFetcher().fetch(singapore_config())


def drop_source(
    report: RetrievalReport,
    source_id: str,
    outcome: FailureOutcome = "unreachable",
) -> RetrievalReport:
    """Rebuild a report as though one source had failed to retrieve."""

    dropped = next(item for item in report.fetched if item.source.source_id == source_id)
    return RetrievalReport(
        fetched=[item for item in report.fetched if item.source.source_id != source_id],
        failures=[
            SourceFailure(
                source_id=source_id,
                title=dropped.source.title,
                authority=dropped.source.authority,
                outcome=outcome,
                detail="the authority did not respond",
                attempted_url=dropped.source.url,
            )
        ],
    )


def mark_stale(report: RetrievalReport, source_id: str) -> RetrievalReport:
    """Rebuild a report as though one source had been served from stale cache."""

    return RetrievalReport(
        fetched=[
            item.model_copy(update={"source": item.source.model_copy(update={"is_stale": True})})
            if item.source.source_id == source_id
            else item
            for item in report.fetched
        ],
        failures=list(report.failures),
    )


def draft_without(draft: VisaPlanDraft, source_id: str) -> VisaPlanDraft:
    """Mirror what a model would return when a source was never in its evidence packet."""

    data = draft.model_dump()
    data["decision_source_ids"] = [i for i in data["decision_source_ids"] if i != source_id]
    for requirement in data["requirements"]:
        requirement["source_ids"] = [i for i in requirement["source_ids"] if i != source_id]
    for step in data["application_steps"]:
        step["source_ids"] = [i for i in step["source_ids"] if i != source_id]
    if data["where_to_apply"] is not None:
        data["where_to_apply"]["source_ids"] = [
            i for i in data["where_to_apply"]["source_ids"] if i != source_id
        ]
    return VisaPlanDraft.model_validate(data)


def test_complete_current_evidence_is_verified() -> None:
    assert resolve_plan_status(RetrievalReport()) == "verified"


@pytest.mark.anyio
async def test_any_failure_downgrades_the_run_to_partial() -> None:
    report = drop_source(await singapore_report(), OPTIONAL_SOURCE)

    assert resolve_plan_status(report) == "partial"


@pytest.mark.anyio
async def test_stale_evidence_downgrades_the_run_to_partial() -> None:
    report = mark_stale(await singapore_report(), OPTIONAL_SOURCE)

    assert resolve_plan_status(report) == "partial"


@pytest.mark.anyio
async def test_missing_required_source_refuses_before_spending_a_model_call() -> None:
    report = drop_source(await singapore_report(), REQUIRED_SOURCE)
    generator = FakeStructuredPlanGenerator(load_golden_draft())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    with pytest.raises(InsufficientEvidenceError) as raised:
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, report)

    assert generator.calls == 0, "a doomed run must not reach the model"
    assert raised.value.reasons
    assert "did not respond" in raised.value.reasons[0]
    assert [failure.source_id for failure in raised.value.failures] == [REQUIRED_SOURCE]


@pytest.mark.anyio
async def test_missing_optional_source_still_produces_a_plan_marked_partial() -> None:
    report = drop_source(await singapore_report(), OPTIONAL_SOURCE)
    generator = FakeStructuredPlanGenerator(draft_without(load_golden_draft(), OPTIONAL_SOURCE))
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    plan = await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, report)

    assert generator.calls == 1
    assert plan.status == "partial"
    assert [failure.source_id for failure in plan.unavailable_sources] == [OPTIONAL_SOURCE]
    assert plan.requirements, "a partial plan must still carry usable guidance"


@pytest.mark.anyio
async def test_stale_evidence_produces_a_partial_plan_on_the_offline_path() -> None:
    report = mark_stale(await singapore_report(), OPTIONAL_SOURCE)

    plan = await FixtureVisaPlanExtractor().extract(
        singapore_config(), DEFAULT_TRAVELLER_PROFILE, report
    )

    assert plan.status == "partial"
    assert not plan.unavailable_sources
    assert any(source.is_stale for source in plan.sources)


@pytest.mark.anyio
async def test_refusal_when_the_run_produced_no_usable_evidence_at_all() -> None:
    empty = RetrievalReport(
        failures=[
            SourceFailure(
                source_id=REQUIRED_SOURCE,
                title="Visa Requirements for Indian Travel Documents",
                authority="Singapore Immigration & Checkpoints Authority",
                outcome="untrusted",
                detail="the request was redirected off the approved authority domains",
                attempted_url=AnyHttpUrl("https://www.ica.gov.sg/visa"),
            )
        ]
    )
    extractor = OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(load_golden_draft()), maximum_input_characters=80_000
    )

    with pytest.raises(Exception, match="at least one source"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, empty)


def test_a_stated_no_is_verified_without_a_checklist_source() -> None:
    """The missing checklist that is not missing.

    Entry 14 grades a checklist-less plan `partial` because a traveller would expect a complete plan
    to rest on one. A visa-free traveller expects no such thing: there is no application, so there
    are no application documents. Grading it `partial` for ever would call its evidence incomplete
    when every page it rests on was read cleanly (DECISIONS entries 94, 95)."""

    assert (
        resolve_plan_status(RetrievalReport(), has_checklist_source=False, no_visa_required=True)
        == "verified"
    )


def test_an_unverified_decision_outranks_a_no_that_nobody_stated() -> None:
    """The exception rests entirely on a page having said no, so a caller that passed both flags is
    refused the label rather than trusted. Extraction cannot produce this pair — it forces the
    decision to null whenever it is unverified — and the ordering here is what makes that a belt
    rather than the only strap."""

    assert (
        resolve_plan_status(
            RetrievalReport(),
            has_checklist_source=False,
            decision_is_unverified=True,
            no_visa_required=True,
        )
        == "partial"
    )


def test_a_missing_checklist_is_still_partial_where_a_visa_is_needed() -> None:
    assert resolve_plan_status(RetrievalReport(), has_checklist_source=False) == "partial"
