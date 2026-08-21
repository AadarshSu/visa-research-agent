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
    corridor_directory: Path = Path("var/corridors")
    # What each corridor considered, for diagnosing a refusal afterwards. One file per corridor,
    # overwritten by the newest run, read by nobody: deleting the directory costs a question, never
    # an answer.
    recall_log_directory: Path = Path("var/recall")
    # Three weeks. A corridor is not evidence: which pages answer it changes when a site is
    # redesigned, not when its guidance is edited. The pages themselves are re-fetched under the
    # much shorter evidence TTL every time a plan is produced.
    corridor_maximum_age_hours: float = 24.0 * 21
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

    # Rendering tuning only. Whether rendering happens at all is policy and lives in
    # `config/runtime.yaml`, because it changes how government sites are contacted.
    render_timeout_seconds: float = 20.0
    render_settle_milliseconds: int = 2_500
    # Separate allowances: discovery visits many more pages than retrieval, and a single shared
    # count let the crawl spend it all before the pages that become evidence were read.
    maximum_source_renders: int = 5
    maximum_crawl_renders: int = 12

    # Source discovery. The search key is a secret; the rest is machine-local tuning. Whether
    # discovery may run at all is not a setting: it is a separate command, run deliberately.
    search_api_key: SecretStr | None = None
    search_timeout_seconds: float = 15.0
    discovery_host_delay_seconds: float = 0.5

    maximum_model_input_characters: int = 80_000
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None
    openai_request_timeout_seconds: float = 60.0
    openai_max_output_tokens: int = 6_000
    openai_reasoning_effort: Literal["none", "low", "medium", "high", "xhigh", "max"] = "low"


settings = Settings()
