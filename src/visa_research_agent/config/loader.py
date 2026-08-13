"""Load and validate version-controlled destination configuration."""

from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from visa_research_agent.domain.models import DestinationRegistry, RuntimePolicy


def _config_path(filename: str, path: Path | None) -> Path:
    return path or Path(str(files("visa_research_agent.config").joinpath(filename)))


def load_destination_registry(path: Path | None = None) -> DestinationRegistry:
    """Load a destination registry from disk and validate its complete structure."""

    config_path = _config_path("destinations.yaml", path)
    with config_path.open(encoding="utf-8") as config_file:
        raw_config: Any = yaml.safe_load(config_file)
    return DestinationRegistry.model_validate(raw_config)


def load_runtime_policy(path: Path | None = None) -> RuntimePolicy:
    """Load the reviewable runtime policy from disk and validate it."""

    config_path = _config_path("runtime.yaml", path)
    with config_path.open(encoding="utf-8") as config_file:
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
