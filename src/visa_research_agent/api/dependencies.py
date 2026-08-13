"""FastAPI dependency factories for independently testable business services."""

from functools import lru_cache

from visa_research_agent.config.settings import settings
from visa_research_agent.research.errors import LLMConfigurationError
from visa_research_agent.research.fixtures import FixtureSourceFetcher, FixtureVisaPlanExtractor
from visa_research_agent.research.openai_extraction import (
    LangChainStructuredPlanGenerator,
    OpenAIVisaPlanExtractor,
)
from visa_research_agent.research.service import VisaPlanService


@lru_cache(maxsize=1)
def get_visa_plan_service() -> VisaPlanService:
    if settings.source_mode != "fixtures":
        raise RuntimeError("Live research mode has not been implemented")

    source_fetcher = FixtureSourceFetcher()
    if settings.extraction_mode == "fixture":
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
