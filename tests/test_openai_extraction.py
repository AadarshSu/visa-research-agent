import json
from datetime import UTC, date, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.discovery.adjudication import UsageRecorder
from visa_research_agent.discovery.recall_log import ModelCall
from visa_research_agent.domain.models import (
    DestinationConfig,
    SupportingQuote,
    VisaPlan,
    VisaPlanDraft,
)
from visa_research_agent.research.errors import (
    InsufficientEvidenceError,
    LLMExtractionError,
)
from visa_research_agent.research.fixtures import FixtureSourceFetcher
from visa_research_agent.research.model_usage import FileModelUsageLog, ModelCallRecord
from visa_research_agent.research.openai_extraction import (
    OpenAIVisaPlanExtractor,
    load_extraction_prompt,
)


def singapore_config() -> DestinationConfig:
    singapore = load_destination_registry().get("singapore")
    assert singapore is not None
    return singapore


def load_golden_draft() -> VisaPlanDraft:
    resource = files("visa_research_agent.fixtures.singapore").joinpath("plan.yaml")
    raw_plan: Any = yaml.safe_load(resource.read_text(encoding="utf-8"))
    return VisaPlanDraft.model_validate(raw_plan)


def test_model_output_schema_avoids_unsupported_format_keywords() -> None:
    schema = json.dumps(VisaPlanDraft.model_json_schema())

    assert '"format"' not in schema
    assert '"category"' not in schema
    assert '"requirement_id"' not in schema


class FakeStructuredPlanGenerator:
    def __init__(self, result: VisaPlanDraft, *, billed: dict[str, int] | None = None) -> None:
        self.result = result
        self.billed = billed or {}
        self.calls = 0
        self.system_prompt: str | None = None
        self.research_packet: str | None = None

    async def generate(
        self, system_prompt: str, research_packet: str, *, usage: UsageRecorder | None = None
    ) -> VisaPlanDraft:
        self.calls += 1
        self.system_prompt = system_prompt
        self.research_packet = research_packet
        # What the LangChain callback would have filled in from the provider's usage report.
        if usage is not None:
            for field, value in self.billed.items():
                setattr(usage, field, value)
        return self.result


@pytest.mark.anyio
async def test_openai_extractor_uses_one_bounded_structured_call() -> None:
    generator = FakeStructuredPlanGenerator(load_golden_draft())
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    plan = await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert generator.calls == 1
    assert generator.system_prompt is not None
    assert "untrusted evidence" in generator.system_prompt
    assert "outside knowledge" in generator.system_prompt
    assert "travel-readiness items" in generator.system_prompt
    assert "genuinely actionable timeline" in generator.system_prompt
    assert "Never claim that an account" in generator.system_prompt
    assert generator.research_packet is not None
    packet = json.loads(generator.research_packet)
    assert packet["traveller_profile"]["passport_nationality"] == "India (IN)"
    assert packet["destination"]["application_document_source_ids"] == ["sg_ica_india_visa_details"]
    assert len(packet["sources"]) == 5
    assert plan.visa_required is True
    assert plan.decision_source_ids == [
        "sg_ica_visa_requirement_overview",
        "sg_ica_india_visa_details",
    ]
    assert plan.where_to_apply is not None
    assert plan.where_to_apply.source_ids == ["sg_mfa_london_visa_information"]
    assert any(step.link_target == "application_route" for step in plan.application_steps)
    assert all(step.timing for step in plan.application_steps)
    assert plan.requirements
    assert all(
        "sg_ica_india_visa_details" in requirement.source_ids for requirement in plan.requirements
    )
    assert plan.application_document_source_ids == ["sg_ica_india_visa_details"]


@pytest.mark.anyio
async def test_openai_extractor_rejects_an_invented_source_id() -> None:
    draft = load_golden_draft()
    invalid_draft = draft.model_copy(update={"decision_source_ids": ["invented_source"]})
    generator = FakeStructuredPlanGenerator(invalid_draft)
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    with pytest.raises(LLMExtractionError, match="source and schema validation"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)


@pytest.mark.anyio
async def test_openai_extractor_omits_documents_from_general_entry_sources() -> None:
    draft = load_golden_draft()
    entry_requirement = draft.requirements[0].model_copy(
        update={"name": "SG Arrival Card", "source_ids": ["sg_ica_entry_requirements"]}
    )
    expanded_draft = draft.model_copy(
        update={"requirements": [*draft.requirements, entry_requirement]}
    )
    generator = FakeStructuredPlanGenerator(expanded_draft)
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    plan = await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert "SG Arrival Card" not in {requirement.name for requirement in plan.requirements}


@pytest.mark.anyio
async def test_openai_extractor_requires_a_designated_application_document_source() -> None:
    golden_draft = load_golden_draft()
    draft = golden_draft.model_copy(
        update={
            "requirements": [
                requirement.model_copy(update={"source_ids": ["sg_ica_entry_requirements"]})
                for requirement in golden_draft.requirements
            ]
        }
    )
    generator = FakeStructuredPlanGenerator(draft)
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    with pytest.raises(LLMExtractionError, match="no source-backed application documents"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)


@pytest.mark.anyio
async def test_a_stated_no_visa_survives_a_destination_that_designates_a_checklist() -> None:
    """The sixth thing in the way of the entry shape, and it was not a validator (entry 98).

    Singapore designates `sg_ica_india_visa_details` as its checklist for *every* traveller, so a
    corridor whose answer is "no visa required" reaches a guard that reads an empty requirements
    list as a model that ignored the checklist. For an application that is exactly right; here
    there is no application, so there are no application documents, and the empty list is the
    answer rather than a failure.

    The plan must also stop designating the source it no longer draws on, or the interface
    announces a checklist with nothing under it.
    """

    golden_draft = load_golden_draft()
    draft = golden_draft.model_copy(
        update={
            "visa_required": False,
            "visa_type": None,
            "where_to_apply": None,
            "requirements": [],
            "unresolved_questions": [],
            # Only steps that link to a page, never to a route: with no `where_to_apply` a
            # route-linked step is refused by `validate_requirement_sources`, which entry 95 named
            # as the guard that looks like an obstacle and is not.
            "application_steps": [
                step
                for step in golden_draft.application_steps
                if step.link_target != "application_route"
            ][:3],
        }
    )
    generator = FakeStructuredPlanGenerator(draft)
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    plan = await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert plan.visa_required is False
    assert plan.requirements == []
    assert plan.application_document_source_ids == [], (
        "a plan with no application must not designate a checklist it does not draw on"
    )
    assert len(plan.application_steps) == 3, "the entry list is as long as the sources state"
    assert plan.status == "verified", "a stated decision on cleanly read pages is verified"


@pytest.mark.anyio
async def test_a_visa_that_is_required_still_needs_its_designated_checklist() -> None:
    """The guard above narrowed and not removed: only a stated *no* may return nothing."""

    golden_draft = load_golden_draft()
    draft = golden_draft.model_copy(
        update={"requirements": [], "unresolved_questions": ["What documents are needed?"]}
    )
    generator = FakeStructuredPlanGenerator(draft)
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000)

    with pytest.raises(LLMExtractionError, match="no source-backed application documents"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)


@pytest.mark.anyio
async def test_openai_extractor_stops_before_call_when_input_is_too_large() -> None:
    generator = FakeStructuredPlanGenerator(load_golden_draft())
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=10)

    with pytest.raises(LLMExtractionError, match="input exceeds"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert generator.calls == 0


# --- What the plan-writing call cost (DECISIONS entries 164 and 165) ---------------------------

RECORDED_AT = datetime(2026, 9, 15, 23, 59, tzinfo=UTC)


class RaisingPlanGenerator:
    async def generate(
        self, system_prompt: str, research_packet: str, *, usage: UsageRecorder | None = None
    ) -> VisaPlanDraft:
        raise RuntimeError("the provider timed out")


class UnwritableUsageLog:
    def write(self, record: ModelCallRecord) -> None:
        raise OSError("read-only file system")


@pytest.mark.anyio
async def test_the_plan_call_records_what_the_provider_billed_including_cache_writes(
    tmp_path: Path,
) -> None:
    """The plan call runs on every web request, stored corridors included, and nothing recorded
    what it cost — and OpenAI bills a cache write at 1.25×, which nothing read either
    (entry 164)."""

    generator = FakeStructuredPlanGenerator(
        load_golden_draft(),
        billed={
            "input_tokens": 6_200,
            "output_tokens": 2_100,
            "cached_input_tokens": 2_048,
            "cache_write_input_tokens": 3_900,
            "reasoning_output_tokens": 700,
        },
    )
    clock = iter([10.0, 16.5])
    log = FileModelUsageLog(tmp_path)
    extractor = OpenAIVisaPlanExtractor(
        generator,
        maximum_input_characters=80_000,
        usage_log=log,
        now=lambda: RECORDED_AT,
        monotonic=lambda: next(clock),
    )
    destination = singapore_config()
    report = await FixtureSourceFetcher().fetch(destination)

    await extractor.extract(destination, DEFAULT_TRAVELLER_PROFILE, report)

    profile = DEFAULT_TRAVELLER_PROFILE
    assert generator.research_packet is not None
    assert log.read(RECORDED_AT.date()) == [
        ModelCallRecord(
            corridor_key=(
                f"{destination.slug}/{profile.passport_nationality}/"
                f"{profile.country_of_residence}/{profile.travel_purpose}"
            ),
            recorded_at=RECORDED_AT,
            call=ModelCall(
                call="plan",
                prompt_characters=len(load_extraction_prompt()),
                packet_characters=len(generator.research_packet),
                seconds=6.5,
                input_tokens=6_200,
                output_tokens=2_100,
                cached_input_tokens=2_048,
                cache_write_input_tokens=3_900,
                reasoning_output_tokens=700,
            ),
        )
    ]


@pytest.mark.anyio
async def test_a_failed_plan_call_is_recorded_and_the_plan_still_refuses(tmp_path: Path) -> None:
    """A slow failure is a cost like any other, which is the rule the other two calls follow."""

    log = FileModelUsageLog(tmp_path)
    extractor = OpenAIVisaPlanExtractor(
        RaisingPlanGenerator(),
        maximum_input_characters=80_000,
        usage_log=log,
        now=lambda: RECORDED_AT,
    )
    report = await FixtureSourceFetcher().fetch(singapore_config())

    with pytest.raises(LLMExtractionError, match="generator failed"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, report)

    [record] = log.read(RECORDED_AT.date())
    assert record.call.failed is True
    assert record.call.input_tokens is None, "a provider that said nothing is not a free call"


@pytest.mark.anyio
async def test_a_plan_refused_before_the_call_records_no_call(tmp_path: Path) -> None:
    log = FileModelUsageLog(tmp_path)
    extractor = OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(load_golden_draft()),
        maximum_input_characters=10,
        usage_log=log,
        now=lambda: RECORDED_AT,
    )
    report = await FixtureSourceFetcher().fetch(singapore_config())

    with pytest.raises(LLMExtractionError, match="input exceeds"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, report)

    assert log.read(RECORDED_AT.date()) == []


@pytest.mark.anyio
async def test_an_unwritable_usage_log_never_costs_the_traveller_their_plan() -> None:
    extractor = OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(load_golden_draft()),
        maximum_input_characters=80_000,
        usage_log=UnwritableUsageLog(),
    )
    report = await FixtureSourceFetcher().fetch(singapore_config())

    plan = await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, report)

    assert plan.destination == singapore_config().display_name


def test_the_usage_log_appends_a_line_per_call_and_starts_a_file_per_day(tmp_path: Path) -> None:
    """Appended, where the recall log overwrites: a day's spend is a sum, not the latest run."""

    log = FileModelUsageLog(tmp_path)
    first = ModelCallRecord(
        corridor_key="japan/IN/GB/tourism",
        recorded_at=datetime(2026, 9, 15, 9, 0, tzinfo=UTC),
        call=ModelCall(call="plan", prompt_characters=1, packet_characters=2, seconds=0.5),
    )
    same_corridor_again = first.model_copy(
        update={"recorded_at": datetime(2026, 9, 15, 9, 5, tzinfo=UTC)}
    )
    next_day = first.model_copy(update={"recorded_at": datetime(2026, 9, 16, 0, 1, tzinfo=UTC)})

    for record in (first, same_corridor_again, next_day):
        log.write(record)

    assert log.read(date(2026, 9, 15)) == [first, same_corridor_again]
    assert log.read(date(2026, 9, 16)) == [next_day]


def checklist_less(destination: DestinationConfig) -> DestinationConfig:
    """The same destination with no page designated as its document checklist.

    What discovery produces whenever no page could be confirmed as the checklist — a country that
    publishes none, one we failed to find, or one behind a block we are not permitted to read — and
    nothing in the pipeline can tell those apart. `required_source_ids` still names the decision
    source, so the plan is not resting on nothing.
    """

    payload = destination.model_dump(mode="json")
    payload["application_document_source_ids"] = []
    payload["required_source_ids"] = ["sg_ica_visa_requirement_overview"]
    return DestinationConfig.model_validate(payload)


UNREAD_CHECKLIST = "https://www.ica.gov.sg/enter-transit-depart/entering-singapore/documents"


def with_unread_checklist(destination: DestinationConfig) -> DestinationConfig:
    """Discovery met a likely checklist page for this corridor and could not read it."""

    payload = destination.model_dump(mode="json")
    payload["unread_checklist_pages"] = [
        {
            "source_id": "singapore_www_documents",
            "title": "Documents required",
            "authority": "Singapore authority (www.ica.gov.sg)",
            "outcome": "challenged",
            "detail": "asked this client to prove it is a browser, and that could not be answered",
            "attempted_url": UNREAD_CHECKLIST,
        }
    ]
    return DestinationConfig.model_validate(payload)


@pytest.mark.anyio
async def test_a_plan_with_no_checklist_names_the_likely_page_it_could_not_read() -> None:
    """Item 9. The traveller can open a page this program could not, so the plan hands it over."""

    draft = load_golden_draft().model_copy(
        update={
            "requirements": [],
            "unresolved_questions": ["No official document checklist was found."],
        }
    )
    destination = with_unread_checklist(checklist_less(singapore_config()))
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(draft), maximum_input_characters=80_000
    ).extract(destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    named = [
        source for source in plan.unavailable_sources if source.source_id.startswith("checklist")
    ]
    assert [str(source.attempted_url) for source in named] == [UNREAD_CHECKLIST]
    assert named[0].title.startswith("Possible document checklist"), "nobody read it"
    assert plan.requirements == [], "naming a page never permits listing what it might say"
    assert plan.status == "partial"


@pytest.mark.anyio
async def test_no_checklist_page_is_named_where_no_application_arises() -> None:
    """A stated "no visa" has no checklist to be missing, so there is nothing to point at."""

    golden_draft = load_golden_draft()
    draft = golden_draft.model_copy(
        update={
            "visa_required": False,
            "visa_type": None,
            "where_to_apply": None,
            "requirements": [],
            "unresolved_questions": [],
            "application_steps": [
                step
                for step in golden_draft.application_steps
                if step.link_target != "application_route"
            ][:3],
        }
    )
    destination = with_unread_checklist(checklist_less(singapore_config()))
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(draft), maximum_input_characters=80_000
    ).extract(destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert plan.unavailable_sources == []
    assert plan.status == "verified"


@pytest.mark.anyio
async def test_a_corridor_with_no_checklist_source_still_produces_a_plan() -> None:
    """DECISIONS entry 14 stopped a missing checklist refusing the corridor, and built
    `validate_absent_checklist` to make the resulting plan safe. The extractor refused first, so
    that validator could never run and the decision reached no traveller.

    Found on `united-states/IN/IN/tourism`: discovery resolved, and the request still answered
    "the visa plan could not be generated safely" because the canonical checklist is a 403.
    """

    golden_draft = load_golden_draft()
    draft = golden_draft.model_copy(
        update={
            "requirements": [],
            "unresolved_questions": ["The official document checklist could not be retrieved."],
        }
    )
    generator = FakeStructuredPlanGenerator(draft)
    destination = checklist_less(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert plan.application_document_source_ids == []
    assert plan.requirements == []
    # The gap has to be stated. Without this the plan reads as though nothing were missing.
    assert plan.unresolved_questions
    # And it must not wear the badge of a complete one, however cleanly the rest was read.
    assert plan.status == "partial"


@pytest.mark.anyio
async def test_documents_are_never_kept_when_no_checklist_source_backs_them() -> None:
    """The failure mode that must stay closed: a checklist assembled from pages that are not one.

    The model is asked not to, but a request is not a guarantee — entry 6 was deleted over exactly
    this — so anything it offers here is dropped rather than published.
    """

    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={"unresolved_questions": ["The document checklist could not be retrieved."]}
        )
    )
    destination = checklist_less(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert plan.requirements == []


@pytest.mark.anyio
async def test_a_declared_checklist_that_was_not_retrieved_still_refuses() -> None:
    """Undeclared and unretrieved are different: one is the world, the other is a broken run.

    Relaxing the first must not relax the second. A destination that names its checklist page is
    saying the plan depends on it, so a run that could not read it has no plan to offer — and it is
    refused before the model call rather than after.
    """

    generator = FakeStructuredPlanGenerator(load_golden_draft())
    destination = singapore_config()
    assert destination.application_document_source_ids == ["sg_ica_india_visa_details"]
    complete = await FixtureSourceFetcher().fetch(destination)
    without_checklist = complete.model_copy(
        update={
            "fetched": [
                item
                for item in complete.fetched
                if item.source.source_id != "sg_ica_india_visa_details"
            ]
        }
    )

    with pytest.raises(InsufficientEvidenceError):
        await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
            destination, DEFAULT_TRAVELLER_PROFILE, without_checklist
        )

    assert generator.calls == 0


def decision_unverified(destination: DestinationConfig) -> DestinationConfig:
    """A destination whose visa decision is published only where we are not allowed to read it."""

    payload = destination.model_dump(mode="json")
    payload["application_document_source_ids"] = []
    payload["required_source_ids"] = []
    payload["decision_is_unverified"] = True
    # The readable half of this fixture is Singapore's, because that is what has snapshots; the
    # blocked half is France's real one. Approving the domain is required — a page offered to a
    # traveller as official guidance must sit on an approved domain like any other.
    payload["trusted_domains"] = [*payload["trusted_domains"], "france-visas.gouv.fr"]
    payload["unreadable_authorities"] = [
        {
            "url": "https://france-visas.gouv.fr/en/web/france-visas",
            "authority": "France authority (france-visas.gouv.fr)",
            "detail": (
                "refused automated retrieval, so its guidance could not be independently "
                "verified here"
            ),
        }
    ]
    return DestinationConfig.model_validate(payload)


@pytest.mark.anyio
async def test_a_plan_names_the_authority_it_was_not_allowed_to_read() -> None:
    """The point of producing a plan at all in this case: the traveller gets the URL and can open it
    themselves, which turns "no verified plan" into a next step."""

    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={
                "requirements": [],
                "visa_required": True,
                "unresolved_questions": ["The visa decision could not be verified."],
            }
        )
    )
    destination = decision_unverified(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    blocked = [source for source in plan.unavailable_sources if source.outcome == "blocked"]
    assert [str(source.attempted_url) for source in blocked] == [
        "https://france-visas.gouv.fr/en/web/france-visas"
    ]
    assert "france-visas.gouv.fr" in blocked[0].authority


@pytest.mark.anyio
async def test_an_unverified_decision_is_never_reported_as_a_decision() -> None:
    """Enforced rather than requested. The model was asked for null and said True here; a wrong yes
    or no about whether someone needs a visa is the most damaging thing this can say, so the
    application overrides it instead of trusting the prompt."""

    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={
                "requirements": [],
                "visa_required": True,
                "unresolved_questions": ["The visa decision could not be verified."],
            }
        )
    )
    destination = decision_unverified(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert plan.visa_required is None
    # And it can never wear the badge of a checked answer.
    assert plan.status == "partial"


@pytest.mark.anyio
async def test_a_decision_the_model_could_not_confirm_is_never_verified() -> None:
    """Item 53. The guard above fires only when a block or a questionnaire stood in for a decision.

    A model can return null on its own, from pages that were all read cleanly — `japan/IN/GB` did,
    *"route and need for a visa not fully established"* — and that plan was graded `verified`.
    Whatever the reason nobody confirmed it, the traveller is being told the one thing they most
    need is unknown, and "Evidence verified" cannot sit beside that.
    """

    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={
                "visa_required": None,
                "unresolved_questions": ["The sources do not establish whether a visa is needed."],
            }
        )
    )
    destination = singapore_config()
    assert not destination.decision_is_unverified, "this is the case no block or tool explains"
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert plan.visa_required is None
    assert plan.status == "partial"


@pytest.mark.anyio
async def test_a_verified_plan_cannot_be_built_around_an_open_decision() -> None:
    """The same rule held by the plan itself, so no other path to a `VisaPlan` can skip it."""

    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    plan = await OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(load_golden_draft()), maximum_input_characters=80_000
    ).extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)
    assert plan.status == "verified"

    with pytest.raises(ValidationError, match="visa decision"):
        VisaPlan.model_validate({**plan.model_dump(), "visa_required": None})


@pytest.mark.anyio
async def test_the_model_is_told_where_the_guidance_lives_but_never_quoted_it() -> None:
    """It is named, not read. A page this program could not open cannot be evidence of anything it
    says, so the packet carries the URL and the authority and no content at all."""

    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={"requirements": [], "unresolved_questions": ["Could not be verified."]}
        )
    )
    destination = decision_unverified(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert generator.research_packet is not None
    packet = json.loads(generator.research_packet)
    assert packet["destination"]["decision_is_unverified"] is True
    named = packet["destination"]["unreadable_authorities"]
    assert named[0]["url"] == "https://france-visas.gouv.fr/en/web/france-visas"
    assert "untrusted_content" not in named[0]


@pytest.mark.anyio
async def test_the_refused_page_that_may_hold_the_decision_is_marked_for_the_traveller() -> None:
    """Item 54. A US plan named nine refused pages at equal weight; the judged ones now say so.

    Both reach the plan, because every refusal is still reported (entry 32): the mark decides what
    leads, never what is shown.
    """

    payload = decision_unverified(singapore_config()).model_dump(mode="json")
    fees = "https://france-visas.gouv.fr/en/web/france-visas/fees"
    payload["unreadable_authorities"] = [
        {**payload["unreadable_authorities"][0], "may_hold_decision": True},
        {**payload["unreadable_authorities"][0], "url": fees},
    ]
    destination = DestinationConfig.model_validate(payload)
    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={"requirements": [], "unresolved_questions": ["Could not be verified."]}
        )
    )
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    refused = {
        str(source.attempted_url): source.may_hold_decision
        for source in plan.unavailable_sources
        if source.outcome == "blocked"
    }
    assert refused == {"https://france-visas.gouv.fr/en/web/france-visas": True, fees: False}
    assert generator.research_packet is not None
    named = json.loads(generator.research_packet)["destination"]["unreadable_authorities"]
    assert [entry["may_hold_decision"] for entry in named] == [True, False]


@pytest.mark.anyio
async def test_a_quote_the_page_does_not_hold_never_reaches_the_plan() -> None:
    """Item 21. The model writes quotes; only the ones found in the retrieved text are shown.

    An invented or drifted quote attributed to a government page is worse than no quote, so it is
    dropped and the claim stands on its citation alone, as it did before quotes existed.
    """

    golden = load_golden_draft()
    first = golden.requirements[0]
    invented = SupportingQuote(
        source_id="sg_ica_india_visa_details",
        text="Applicants must show six months of bank statements.",
    )
    wrong_decision = SupportingQuote(
        source_id="sg_ica_india_visa_details",
        text="Indian nationals may enter Singapore without a visa.",
    )
    draft = golden.model_copy(
        update={
            "decision_quotes": [wrong_decision, *golden.decision_quotes],
            "requirements": [
                first.model_copy(
                    update={"supporting_quotes": [invented, *first.supporting_quotes]}
                ),
                *golden.requirements[1:],
            ],
        }
    )
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())

    plan = await OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(draft), maximum_input_characters=80_000
    ).extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert plan.decision_quotes == golden.decision_quotes
    assert plan.requirements[0].supporting_quotes == first.supporting_quotes
    # The golden plan's own quotes are real, so every one of them survives the same check.
    assert all(requirement.supporting_quotes for requirement in plan.requirements)


@pytest.mark.anyio
async def test_a_plan_refuses_a_quote_from_a_page_its_claim_does_not_cite() -> None:
    """A true sentence from another page is still a misattribution."""

    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    plan = await OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(load_golden_draft()), maximum_input_characters=80_000
    ).extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)
    payload = plan.model_dump(mode="json")
    payload["decision_quotes"] = [
        {
            "source_id": "sg_mfa_check_visa",
            "text": "MFA identifies ICA as the authority for visa matters.",
        }
    ]

    with pytest.raises(ValidationError, match="decision quote must come from a source"):
        VisaPlan.model_validate(payload)


@pytest.mark.anyio
async def test_a_plan_ties_each_source_to_the_text_it_was_read_from_and_why_it_was_chosen() -> None:
    """Item 21, parts 2 and 3. A plan could name a page and not the version of it, and why the page
    was picked for a role stopped at the resolved corridor.

    Attached when the plan is built, from this run's retrieval and this destination's sources —
    never from the retrieval cache, which is shared between corridors that chose a page differently.
    """

    payload = singapore_config().model_dump(mode="json")
    for source in payload["sources"]:
        if source["source_id"] == "sg_ica_india_visa_details":
            source["selection"] = {
                "roles": ["visa_decision", "document_checklist"],
                "decided_by": "model",
                "score": 113.0,
                "signals": ["url:india+40"],
            }
    destination = DestinationConfig.model_validate(payload)
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(
        FakeStructuredPlanGenerator(load_golden_draft()), maximum_input_characters=80_000
    ).extract(destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    hashes = {item.source.source_id: item.content_hash for item in fetched_sources.fetched}
    assert {source.source_id: source.content_hash for source in plan.sources} == hashes
    chosen = {source.source_id: source.selection for source in plan.sources}
    selection = chosen["sg_ica_india_visa_details"]
    assert selection is not None and selection.decided_by == "model"
    # A hand-written source was chosen by a person, and says nothing rather than inventing a score.
    assert chosen["sg_ica_visa_requirement_overview"] is None


def test_the_model_is_told_to_point_at_the_page_that_may_hold_the_decision() -> None:
    prompt = load_extraction_prompt()

    assert "may_hold_decision" in prompt
    assert "do not list every refused address" in prompt


def decision_behind_a_tool(destination: DestinationConfig) -> DestinationConfig:
    """A destination whose visa decision is published only inside an official questionnaire.

    The same unverified decision as `decision_unverified`, reached the other way: nothing refused
    us, the page was read, and it asks rather than answers.
    """

    payload = destination.model_dump(mode="json")
    payload["application_document_source_ids"] = []
    payload["required_source_ids"] = []
    payload["decision_is_unverified"] = True
    payload["trusted_domains"] = [*payload["trusted_domains"], "www.gov.uk"]
    payload["official_tools"] = [
        {
            "topic": "visa_decision",
            "url": "https://www.gov.uk/check-uk-visa",
            "authority": "United Kingdom authority (www.gov.uk)",
            "detail": (
                "decides this by asking questions rather than stating an answer, so the decision "
                "could not be read from the page"
            ),
        }
    ]
    return DestinationConfig.model_validate(payload)


@pytest.mark.anyio
async def test_a_questionnaire_reaches_the_plan_as_a_next_step_not_as_a_failed_source() -> None:
    """It was fetched and read successfully, so reporting it under unavailable evidence would be
    false about what happened. It is the one thing the traveller can act on, and it goes with the
    decision rather than with the caveats."""

    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={
                "requirements": [],
                "visa_required": True,
                "unresolved_questions": ["Answer the official checker to get the decision."],
            }
        )
    )
    destination = decision_behind_a_tool(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    plan = await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert [str(tool.url) for tool in plan.official_tools] == ["https://www.gov.uk/check-uk-visa"]
    # Overridden, exactly as for a block: the model said True and no page said anything.
    assert plan.visa_required is None
    assert plan.status == "partial"
    assert not any(failure.outcome == "blocked" for failure in plan.unavailable_sources), (
        "nothing refused us; saying so would be false"
    )


@pytest.mark.anyio
async def test_the_model_is_told_where_the_question_is_settled_never_what_it_settles_to() -> None:
    generator = FakeStructuredPlanGenerator(
        load_golden_draft().model_copy(
            update={"requirements": [], "unresolved_questions": ["Answer the checker."]}
        )
    )
    destination = decision_behind_a_tool(singapore_config())
    fetched_sources = await FixtureSourceFetcher().fetch(destination)

    await OpenAIVisaPlanExtractor(generator, maximum_input_characters=80_000).extract(
        destination, DEFAULT_TRAVELLER_PROFILE, fetched_sources
    )

    assert generator.research_packet is not None
    packet = json.loads(generator.research_packet)
    named = packet["destination"]["official_tools"]
    assert named[0]["url"] == "https://www.gov.uk/check-uk-visa"
    assert "untrusted_content" not in named[0]


def test_a_missing_checklist_is_never_turned_into_a_claim_that_none_exists() -> None:
    """Item 9. An empty checklist source says what a run found and read, never what an authority
    publishes: the same plan arises when a checklist exists and could not be found or read.

    Rule 8a used to tell the model the authority "publishes no document checklist" and to write that
    none "was published", which is a claim about the world nothing in the pipeline can establish.
    """

    prompt = load_extraction_prompt()

    assert "publishes no document checklist" not in prompt
    assert "saying no official checklist was published" not in prompt
    assert "Never say or imply that the authority publishes no" in prompt
    assert "found among the pages that could be read" in prompt


def test_absence_from_a_visa_required_list_is_an_answer_only_within_its_bounds() -> None:
    """The owner's rule (entry 172): Singapore lists who needs a visa and never names the rest, and
    the plan call answered a Filipino passport "no visa" or "undecided" by chance. The rule settles
    it, and each bound is what keeps a silence from becoming a confident wrong "no"."""

    prompt = load_extraction_prompt()

    assert "Absence from the authority's visa-required list states no visa is needed." in prompt
    assert "The whole list must be in the source text." in prompt
    assert "every footnote, exception" in prompt
    assert "It applies only to a list of who NEEDS a visa." in prompt
    assert "rule 5 governs and visa_required is" in prompt
    assert "The one silence that is an answer" in prompt, "rule 4 must not contradict it"


def test_the_extraction_prompt_separates_a_block_from_a_questionnaire() -> None:
    """Two reasons a decision can be unverified, and they need different sentences: one page was
    withheld, the other was read and asks questions."""

    prompt = load_extraction_prompt()

    assert "official_tools" in prompt
    assert "read successfully" in prompt
    assert "a question is not evidence" in prompt
    # A checklist tool must never read as permission to list a checklist.
    assert "does NOT permit a checklist" in prompt
