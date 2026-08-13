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
    source_mode: Literal["fixtures", "live"] = "fixtures"
    extraction_mode: Literal["fixture", "openai"] = "fixture"
    cache_directory: Path = Path("var/cache")
    maximum_fixture_characters: int = 50_000
    maximum_model_input_characters: int = 80_000
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None
    openai_request_timeout_seconds: float = 60.0
    openai_max_output_tokens: int = 6_000
    openai_reasoning_effort: Literal["none", "low", "medium", "high", "xhigh", "max"] = "low"


settings = Settings()
