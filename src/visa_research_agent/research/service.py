"""Application-facing visa plan service, independent of HTTP routing."""

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
    ) -> VisaPlan:
        fetched_sources = await self.source_fetcher.fetch(destination)
        return await self.extractor.extract(destination, traveller_profile, fetched_sources)
