from pathlib import Path

import pytest
from pydantic import ValidationError

from visa_research_agent.config.loader import load_destination_registry


def test_registry_contains_the_four_mvp_destinations() -> None:
    registry = load_destination_registry()

    assert [destination.slug for destination in registry.destinations] == [
        "singapore",
        "japan",
        "united-states",
        "france",
    ]


def test_france_has_a_country_specific_schengen_route() -> None:
    france = load_destination_registry().get("france")

    assert france is not None
    assert france.route_type == "schengen_member"
    assert france.schengen_member == "France"


def test_registry_rejects_duplicate_destination_slugs(tmp_path: Path) -> None:
    duplicate_config = tmp_path / "destinations.yaml"
    duplicate_config.write_text(
        """
schema_version: 1
destinations:
  - slug: japan
    display_name: Japan
    route_type: national
  - slug: japan
    display_name: Japan again
    route_type: national
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="destination slugs must be unique"):
        load_destination_registry(duplicate_config)
