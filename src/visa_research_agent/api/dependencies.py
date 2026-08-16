"""FastAPI dependency factories for independently testable business services."""

from functools import lru_cache

from visa_research_agent.config.loader import get_runtime_policy
from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.automatic import AutomaticDestinationService
from visa_research_agent.discovery.corridor_store import FileCorridorStore
from visa_research_agent.domain.models import RuntimePolicy
from visa_research_agent.research.errors import LLMConfigurationError
from visa_research_agent.research.fixtures import FixtureSourceFetcher, FixtureVisaPlanExtractor
from visa_research_agent.research.interfaces import SourceFetcher
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.openai_extraction import (
    LangChainStructuredPlanGenerator,
    OpenAIVisaPlanExtractor,
)
from visa_research_agent.research.rendering import build_page_renderer
from visa_research_agent.research.service import VisaPlanService
from visa_research_agent.research.source_cache import FileSourceCache


def build_source_fetcher(policy: RuntimePolicy) -> SourceFetcher:
    """Select offline fixture evidence or live retrieval from the reviewed runtime policy."""

    if policy.source_mode == "fixtures":
        return FixtureSourceFetcher()

    return LiveSourceFetcher(
        FileSourceCache(settings.cache_directory),
        ttl_hours=policy.source_cache_ttl_hours,
        maximum_stale_hours=policy.source_maximum_stale_hours,
        timeout_seconds=settings.source_fetch_timeout_seconds,
        concurrency=settings.source_fetch_concurrency,
        maximum_characters=settings.maximum_source_characters,
        minimum_characters=settings.minimum_source_characters,
        user_agent=settings.source_user_agent,
        maximum_bytes=settings.maximum_source_bytes,
        renderer=build_page_renderer(policy),
        maximum_renders=settings.maximum_source_renders,
    )


def build_visa_plan_service(policy: RuntimePolicy) -> VisaPlanService:
    """Assemble the retrieval and extraction pipeline described by the runtime policy."""

    source_fetcher = build_source_fetcher(policy)
    if policy.extraction_mode == "fixture":
        return VisaPlanService(source_fetcher, FixtureVisaPlanExtractor())

    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value().strip():
        raise LLMConfigurationError("OPENAI_API_KEY is required for OpenAI extraction")
    if settings.openai_model is None or not settings.openai_model.strip():
        raise LLMConfigurationError("OPENAI_MODEL is required for OpenAI extraction")

    generator = LangChainStructuredPlanGenerator(
        api_key=settings.openai_api_key.get_secret_value(),
        model_name=settings.openai_model,
        request_timeout_seconds=settings.openai_request_timeout_seconds,
        max_output_tokens=settings.openai_max_output_tokens,
        reasoning_effort=settings.openai_reasoning_effort,
    )
    extractor = OpenAIVisaPlanExtractor(
        generator,
        maximum_input_characters=settings.maximum_model_input_characters,
    )
    return VisaPlanService(source_fetcher, extractor)


def build_automatic_destinations(policy: RuntimePolicy) -> AutomaticDestinationService | None:
    """Build request-time discovery when the policy asks for it, or none when it does not."""

    if policy.destination_mode == "configured":
        return None

    # Imported here: the CLI owns how a resolver is assembled, and importing it at module scope
    # would make the API depend on the command line rather than the other way round.
    from visa_research_agent.discovery.cli import (
        build_resolver,
        build_role_adjudicator,
        build_search_provider,
    )
    from visa_research_agent.research.rendering import build_page_renderer

    renderer = build_page_renderer(policy)
    adjudicator = build_role_adjudicator(policy)
    return AutomaticDestinationService(
        build_search_provider(),
        lambda: build_resolver(renderer, adjudicator),
        FileCorridorStore(settings.corridor_directory),
        maximum_age_hours=settings.corridor_maximum_age_hours,
    )


@lru_cache(maxsize=1)
def get_visa_plan_service() -> VisaPlanService:
    return build_visa_plan_service(get_runtime_policy())


@lru_cache(maxsize=1)
def get_automatic_destinations() -> AutomaticDestinationService | None:
    """The service itself is cached; **resolved corridors are not.**

    Caching the service is safe because it holds no corridor state. Corridors expire, so they live
    in a file store with an age check rather than in a process-lifetime memo that could serve a
    weeks-old answer for as long as the server stays up.
    """

    return build_automatic_destinations(get_runtime_policy())
