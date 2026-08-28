"""Load and validate version-controlled destination configuration."""

from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from visa_research_agent.domain.models import (
    DestinationRegistry,
    RuntimePolicy,
    ServiceProviderRegistry,
)


def config_path(filename: str, path: Path | None = None) -> Path:
    """Resolve a packaged config file, or the caller's override when one is given."""

    return path or Path(str(files("visa_research_agent.config").joinpath(filename)))


def load_destination_registry(path: Path | None = None) -> DestinationRegistry:
    """Load a destination registry from disk and validate its complete structure."""

    resolved = config_path("destinations.yaml", path)
    with resolved.open(encoding="utf-8") as config_file:
        raw_config: Any = yaml.safe_load(config_file)
    return DestinationRegistry.model_validate(raw_config)


def load_runtime_policy(path: Path | None = None) -> RuntimePolicy:
    """Load the reviewable runtime policy from disk and validate it."""

    resolved = config_path("runtime.yaml", path)
    with resolved.open(encoding="utf-8") as config_file:
        raw_config: Any = yaml.safe_load(config_file)
    return RuntimePolicy.model_validate(raw_config)


@lru_cache(maxsize=1)
def get_destination_registry() -> DestinationRegistry:
    """Return the immutable-in-practice application registry once per process."""

    return load_destination_registry()


@lru_cache(maxsize=1)
def get_runtime_policy() -> RuntimePolicy:
    """Return the runtime policy once per process."""

    return load_runtime_policy()


def load_service_providers(path: Path | None = None) -> ServiceProviderRegistry:
    """Load the reviewed list of companies a government may delegate its guidance to.

    Committed data rather than a live judgement, for the same reason `authority_domains.yaml` is
    (entry 38): the alternative is deciding at crawl time, from a page's own markup, who a traveller
    may be pointed at — and the page's markup is untrusted content.
    """

    resolved = config_path("service_providers.yaml", path)
    with resolved.open(encoding="utf-8") as config_file:
        raw_config: Any = yaml.safe_load(config_file)
    return ServiceProviderRegistry.model_validate(raw_config)


@lru_cache(maxsize=1)
def get_service_providers() -> ServiceProviderRegistry:
    """Return the reviewed delegate list once per process."""

    return load_service_providers()
