"""Interfaces that keep fixture and future live implementations interchangeable."""

from typing import TYPE_CHECKING, Protocol

from visa_research_agent.domain.models import (
    DestinationConfig,
    RetrievalReport,
    TravellerProfile,
    VisaPlan,
    VisaPlanDraft,
)

if TYPE_CHECKING:
    from visa_research_agent.discovery.adjudication import UsageRecorder


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
    async def generate(
        self, system_prompt: str, research_packet: str, *, usage: "UsageRecorder | None" = None
    ) -> VisaPlanDraft:
        """Make one structured model call over an already bounded research packet.

        `usage`, where given, is told what the provider billed for this call. It is handed in rather
        than read back off the generator afterwards, because one generator serves every concurrent
        web request and a field on it could be overwritten by another call before this one read it.
        """
        ...
