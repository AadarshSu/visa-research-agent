"""Interfaces that keep fixture and future live implementations interchangeable."""

from typing import Protocol

from visa_research_agent.domain.models import (
    DestinationConfig,
    RetrievalReport,
    TravellerProfile,
    VisaPlan,
    VisaPlanDraft,
)


class SourceFetcher(Protocol):
    async def fetch(self, destination: DestinationConfig) -> RetrievalReport:
        """Retrieve the configured evidence for one destination, reporting any gaps."""
        ...


class VisaPlanExtractor(Protocol):
    async def extract(
        self,
        destination: DestinationConfig,
        traveller_profile: TravellerProfile,
        report: RetrievalReport,
    ) -> VisaPlan:
        """Transform bounded evidence into a validated visa plan."""
        ...


class StructuredPlanGenerator(Protocol):
    async def generate(self, system_prompt: str, research_packet: str) -> VisaPlanDraft:
        """Make one structured model call over an already bounded research packet."""
        ...
