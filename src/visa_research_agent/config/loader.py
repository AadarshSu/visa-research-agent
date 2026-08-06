"""Load and validate version-controlled destination configuration."""

from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from visa_research_agent.domain.models import DestinationRegistry


def load_destination_registry(path: Path | None = None) -> DestinationRegistry:
    """Load a destination registry from disk and validate its complete structure."""

    config_path = path or Path(
        str(files("visa_research_agent.config").joinpath("destinations.yaml"))
    )
    with config_path.open(encoding="utf-8") as config_file:
        raw_config: Any = yaml.safe_load(config_file)
    return DestinationRegistry.model_validate(raw_config)


@lru_cache(maxsize=1)
def get_destination_registry() -> DestinationRegistry:
    """Return the immutable-in-practice application registry once per process."""

    return load_destination_registry()
