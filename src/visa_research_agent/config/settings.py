"""Environment-backed runtime settings."""

from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings read from environment variables or a local `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Visa Research Agent"
    cache_directory: Path = Path("var/cache")
    maximum_fixture_characters: int = 50_000

    # Live retrieval tuning only. Which sources are contacted, which extractor runs, and when
    # stale evidence is refused are reviewable policy and live in `config/runtime.yaml`.
    source_fetch_timeout_seconds: float = 20.0
    source_fetch_concurrency: int = 4
    maximum_source_characters: int = 50_000
    minimum_source_characters: int = 400
    maximum_source_bytes: int = 12_000_000
    source_user_agent: str = (
        "VisaResearchAgent/0.1 (personal visa research; contact repository owner)"
    )

    maximum_model_input_characters: int = 80_000
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None
    openai_request_timeout_seconds: float = 60.0
    openai_max_output_tokens: int = 6_000
    openai_reasoning_effort: Literal["none", "low", "medium", "high", "xhigh", "max"] = "low"


settings = Settings()
