import json
from importlib.resources import files
from typing import Any

import pytest
import yaml

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.domain.models import DestinationConfig, VisaPlanDraft
from visa_research_agent.research.errors import LLMExtractionError
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
