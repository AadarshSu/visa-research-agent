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
    cache_directory: Path = Path("var/cache")
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None


settings = Settings()
