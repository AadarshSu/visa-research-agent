"""FastAPI dependency factories for independently testable business services."""

from functools import lru_cache

from visa_research_agent.config.settings import settings
from visa_research_agent.research.fixtures import FixtureSourceFetcher, FixtureVisaPlanExtractor
from visa_research_agent.research.service import VisaPlanService


@lru_cache(maxsize=1)
def get_visa_plan_service() -> VisaPlanService:
    if settings.source_mode != "fixtures":
        raise RuntimeError("Live research mode has not been implemented")
    return VisaPlanService(FixtureSourceFetcher(), FixtureVisaPlanExtractor())
