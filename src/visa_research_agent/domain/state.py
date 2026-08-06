"""Typed state contract for the future LangGraph workflow."""

from typing import TypedDict

from visa_research_agent.domain.models import (
    ConfiguredSource,
    FetchedSource,
    TravellerProfile,
    VisaPlan,
)


class VisaResearchState(TypedDict):
    """State passed between bounded research workflow nodes."""

    destination: str
    traveller_profile: TravellerProfile
    configured_sources: list[ConfiguredSource]
    fetched_sources: list[FetchedSource]
    extracted_result: VisaPlan | None
    missing_fields: list[str]
    conflicts: list[str]
    research_attempts: int
    final_result: VisaPlan | None
