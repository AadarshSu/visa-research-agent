"""Application-facing visa plan service, independent of HTTP routing."""

from collections.abc import Callable

from visa_research_agent.domain.models import DestinationConfig, TravellerProfile, VisaPlan
from visa_research_agent.research.interfaces import SourceFetcher, VisaPlanExtractor


class VisaPlanService:
    """Run the current bounded retrieval and extraction pipeline."""

    def __init__(self, source_fetcher: SourceFetcher, extractor: VisaPlanExtractor) -> None:
        self.source_fetcher = source_fetcher
        self.extractor = extractor

    async def generate(
        self,
        destination: DestinationConfig,
        traveller_profile: TravellerProfile,
        *,
        on_stage: Callable[[str], None] | None = None,
    ) -> VisaPlan:
        """Build the plan. `on_stage` hears `retrieve` and then `write` as each starts.

        It is told which stage has started and nothing else: no part of a plan reaches a traveller
        before the whole plan has been validated (TODO item 57, DECISIONS entry 6).
        """

        if on_stage is not None:
            on_stage("retrieve")
        report = await self.source_fetcher.fetch(destination)
        if on_stage is not None:
            on_stage("write")
        return await self.extractor.extract(destination, traveller_profile, report)
