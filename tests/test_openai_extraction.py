import json
from importlib.resources import files
from typing import Any

import pytest
import yaml

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.domain.models import DestinationConfig, VisaPlanDraft
from visa_research_agent.research.errors import (
    InsufficientEvidenceError,
    LLMExtractionError,
)
from visa_research_agent.research.fixtures import FixtureSourceFetcher
from visa_research_agent.research.openai_extraction import OpenAIVisaPlanExtractor


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
    def __init__(self, result: VisaPlanDraft) -> None:
        self.result = result
        self.calls = 0
        self.system_prompt: str | None = None
        self.research_packet: str | None = None

    async def generate(self, system_prompt: str, research_packet: str) -> VisaPlanDraft:
        self.calls += 1
        self.system_prompt = system_prompt
        self.research_packet = research_packet
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
async def test_openai_extractor_stops_before_call_when_input_is_too_large() -> None:
    generator = FakeStructuredPlanGenerator(load_golden_draft())
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())
    extractor = OpenAIVisaPlanExtractor(generator, maximum_input_characters=10)

    with pytest.raises(LLMExtractionError, match="input exceeds"):
        await extractor.extract(singapore_config(), DEFAULT_TRAVELLER_PROFILE, fetched_sources)

    assert generator.calls == 0


def checklist_less(destination: DestinationConfig) -> DestinationConfig:
    """The same destination with no page designated as its document checklist.

    What discovery produces when a country publishes no checklist, or publishes one behind a block
    we are not permitted to read. `required_source_ids` still names the decision source, so the plan
    is not resting on nothing.
    """

    payload = destination.model_dump(mode="json")
    payload["application_document_source_ids"] = []
    payload["required_source_ids"] = ["sg_ica_visa_requirement_overview"]
    return DestinationConfig.model_validate(payload)


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
