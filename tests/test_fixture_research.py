import pytest

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.config.traveller import TRAVELLER_PROFILE
from visa_research_agent.domain.models import DestinationConfig
from visa_research_agent.research.errors import FixtureDataError
from visa_research_agent.research.fixtures import FixtureSourceFetcher, FixtureVisaPlanExtractor
from visa_research_agent.research.service import VisaPlanService


def singapore_config() -> DestinationConfig:
    singapore = load_destination_registry().get("singapore")
    assert singapore is not None
    return singapore


@pytest.mark.anyio
async def test_fixture_fetcher_loads_primary_sources_without_network() -> None:
    fetched_sources = await FixtureSourceFetcher().fetch(singapore_config())

    assert len(fetched_sources) == 5
    assert all(source.from_cache for source in fetched_sources)
    assert all(len(source.content_hash) == 64 for source in fetched_sources)
    assert {source.source.source_id for source in fetched_sources} == {
        "sg_ica_visa_requirement_overview",
        "sg_ica_india_visa_details",
        "sg_mfa_check_visa",
        "sg_mfa_london_visa_information",
        "sg_ica_entry_requirements",
    }


@pytest.mark.anyio
async def test_fixture_fetcher_enforces_content_size_limit() -> None:
    with pytest.raises(FixtureDataError, match="size limit"):
        await FixtureSourceFetcher(maximum_characters=10).fetch(singapore_config())


@pytest.mark.anyio
async def test_fixture_service_generates_deterministic_validated_plan() -> None:
    service = VisaPlanService(FixtureSourceFetcher(), FixtureVisaPlanExtractor())

    first_plan = await service.generate(singapore_config(), TRAVELLER_PROFILE)
    second_plan = await service.generate(singapore_config(), TRAVELLER_PROFILE)

    assert first_plan == second_plan
    assert first_plan.visa_required is True
    assert first_plan.where_to_apply is not None
    assert first_plan.where_to_apply.location == "66 Wilson Street, London EC2A 2BT"
    assert first_plan.requirements
    assert all(
        "sg_ica_india_visa_details" in requirement.source_ids
        for requirement in first_plan.requirements
    )
    assert any(step.link_target == "application_route" for step in first_plan.application_steps)
    assert any("30 days" in step.timing for step in first_plan.application_steps)
    assert any("three working days" in step.action for step in first_plan.application_steps)
    assert all(step.source_ids for step in first_plan.application_steps)
    assert len(first_plan.unresolved_questions) == 5
    assert len(first_plan.conflicts) == 1
    assert {
        source_id for requirement in first_plan.requirements for source_id in requirement.source_ids
    } <= {source.source_id for source in first_plan.sources}
