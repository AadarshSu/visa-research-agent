"""The discovery commands: their exit codes and the config they emit."""

import io
from datetime import UTC, datetime

import pytest
import yaml

from visa_research_agent.discovery.cli import build_parser, print_corridor, run_corridor
from visa_research_agent.discovery.models import (
    Corridor,
    ResolvedCorridor,
    ResolvedSource,
)
from visa_research_agent.discovery.proposal import render_corridor_yaml

RESOLVED_AT = datetime(2026, 8, 15, 9, 0, tzinfo=UTC)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="japan",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def source(source_id: str, url: str, role: str, score: float = 88.0) -> ResolvedSource:
    return ResolvedSource.model_validate(
        {
            "source_id": source_id,
            "title": "A page",
            "url": url,
            "authority": "An authority",
            "kind": "foreign_ministry",
            "roles": [role],
            "score": score,
            "signals": ["url:visa requirements+25"],
        }
    )


def resolved(**overrides: object) -> ResolvedCorridor:
    payload: dict[str, object] = {
        "corridor": corridor(),
        "resolved_at": RESOLVED_AT,
        "sources": [
            source("jp_decision", "https://www.mofa.go.jp/novisa", "visa_decision"),
            source(
                "jp_checklist",
                "https://www.uk.emb-japan.go.jp/sightseeing",
                "document_checklist",
            ),
        ],
        "pages_fetched": 6,
    }
    payload.update(overrides)
    return ResolvedCorridor.model_validate(payload)


def test_the_parser_accepts_the_documented_corridor_command() -> None:
    args = build_parser().parse_args(
        ["corridor", "--destination", "japan", "--nationality", "IN", "--from", "GB"]
    )

    assert args.command == "corridor"
    assert args.nationality == "IN"
    assert getattr(args, "from") == "GB"
    assert args.purpose == "tourism"


def test_an_unsupported_purpose_is_rejected_by_the_parser() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "corridor",
                "--destination",
                "japan",
                "--nationality",
                "IN",
                "--from",
                "GB",
                "--purpose",
                "smuggling",
            ]
        )


def test_the_printed_report_explains_each_choice() -> None:
    stream = io.StringIO()

    print_corridor(resolved(), stream)
    output = stream.getvalue()

    assert "japan/IN/GB/tourism" in output
    assert "document_checklist" in output
    assert "why:" in output, "a reader must be able to see why a page was chosen"


def test_the_printed_report_names_what_could_not_be_found() -> None:
    stream = io.StringIO()

    print_corridor(resolved(unresolved_roles=["document_checklist"], notes=["nothing scored"]),
                   stream)
    output = stream.getvalue()

    assert "could not be identified" in output
    assert "note: nothing scored" in output


def test_the_emitted_yaml_matches_the_shape_of_hand_written_config() -> None:
    rendered = render_corridor_yaml(resolved())
    body = yaml.safe_load(rendered)

    assert body["application_document_source_ids"] == ["jp_checklist"]
    assert body["required_source_ids"] == ["jp_checklist", "jp_decision"]
    assert {entry["source_id"] for entry in body["sources"]} == {"jp_decision", "jp_checklist"}
    for entry in body["sources"]:
        assert set(entry) == {
            "source_id",
            "title",
            "url",
            "authority",
            "kind",
            "research_pass",
        }


def test_the_emitted_yaml_records_the_reasoning_as_comments() -> None:
    rendered = render_corridor_yaml(
        resolved(unresolved_roles=["application_route"], notes=["mission not found"])
    )

    assert "# Discovered for corridor japan/IN/GB/tourism" in rendered
    assert "UNRESOLVED: application_route" in rendered
    assert "note: mission not found" in rendered


@pytest.mark.anyio
async def test_an_unknown_destination_is_a_configuration_error() -> None:
    args = build_parser().parse_args(
        ["corridor", "--destination", "atlantis", "--nationality", "IN", "--from", "GB"]
    )

    assert await run_corridor(args, io.StringIO()) == 3


@pytest.mark.anyio
async def test_a_destination_without_approved_domains_is_refused_with_guidance() -> None:
    args = build_parser().parse_args(
        ["corridor", "--destination", "france", "--nationality", "IN", "--from", "GB"]
    )
    stream = io.StringIO()

    # France is configured but has no trusted domains yet, so discovery has nowhere safe to look.
    assert await run_corridor(args, stream) == 3
    assert "bootstrap" in stream.getvalue()
