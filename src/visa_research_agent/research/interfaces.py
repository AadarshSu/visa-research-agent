"""Interfaces that keep fixture and future live implementations interchangeable."""

from typing import Protocol

from visa_research_agent.domain.models import (
    DestinationConfig,
    FetchedSource,
    TravellerProfile,
    VisaPlan,
    VisaPlanDraft,
)


class SourceFetcher(Protocol):
    async def fetch(self, destination: DestinationConfig) -> list[FetchedSource]:
        """Retrieve the configured evidence for one destination."""
        ...


class VisaPlanExtractor(Protocol):
    async def extract(
        self,
        destination: DestinationConfig,
        traveller_profile: TravellerProfile,
        fetched_sources: list[FetchedSource],
    ) -> VisaPlan:
        """Transform bounded evidence into a validated visa plan."""
        ...


class StructuredPlanGenerator(Protocol):
    async def generate(self, system_prompt: str, research_packet: str) -> VisaPlanDraft:
        """Make one structured model call over an already bounded research packet."""
        ...
