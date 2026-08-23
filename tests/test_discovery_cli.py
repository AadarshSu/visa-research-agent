"""The discovery commands: their exit codes and the config they emit."""

import io
from datetime import UTC, datetime

import pytest
import yaml

from visa_research_agent.discovery.cli import (
    build_parser,
    corridor_destination,
    print_corridor,
    print_variance,
    run_corridor,
)
from visa_research_agent.discovery.models import (
    Corridor,
    ResolvedCorridor,
    ResolvedSource,
)
from visa_research_agent.discovery.proposal import render_corridor_yaml
from visa_research_agent.discovery.recall_log import CandidateVariance, VarianceReport

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

    print_corridor(
        resolved(unresolved_roles=["document_checklist"], notes=["nothing scored"]), stream
    )
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


def test_a_configured_destination_with_domains_is_used_as_written() -> None:
    """Japan has hand-written sources, so the registry must not displace them."""

    destination = corridor_destination("japan", corridor(), io.StringIO())

    assert destination is not None
    assert destination.sources, "the configured destination's own sources were lost"


def test_a_destination_with_no_configured_domains_falls_back_to_the_registry() -> None:
    """The gap this closed: `united-states` has no trusted_domains in destinations.yaml.

    It used to exit 3 saying "run bootstrap first" while the API resolved the same corridor
    perfectly well from `authority_domains.yaml`, so every live check of a registry corridor had to
    be run from a throwaway script.
    """

    wanted = Corridor(
        destination_slug="united-states",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )

    destination = corridor_destination("united-states", wanted, io.StringIO())

    assert destination is not None
    assert "state.gov" in destination.trusted_domains
    assert not destination.sources, "the registry supplies domains, never pages"


def test_a_country_outside_the_registry_is_refused_with_the_same_words_as_the_api() -> None:
    """Austria has a registry row with no confirmable domain, so it refuses — correctly (entry 39).

    The message has to be the registry's own, not a second one written for the command: a country
    the CLI cannot research and a country the API cannot research are one fact.
    """

    wanted = Corridor(
        destination_slug="austria",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )
    stream = io.StringIO()

    assert corridor_destination("austria", wanted, stream) is None
    message = stream.getvalue()
    assert "No domain belonging to Austria's own government could be confirmed" in message
    assert "Nothing was fetched" in message


@pytest.mark.anyio
async def test_repeated_runs_report_what_varied_between_them() -> None:
    """TODO item 17's counting: the command has to say which page moved, not just the outcomes."""

    args = build_parser().parse_args(
        [
            "corridor",
            "--destination",
            "japan",
            "--nationality",
            "IN",
            "--from",
            "GB",
            "--runs",
            "2",
        ]
    )
    stream = io.StringIO()
    calls = 0

    async def never_the_same(
        destination: object, wanted: object, policy: object
    ) -> ResolvedCorridor:
        nonlocal calls
        calls += 1
        return resolved()

    assert await run_corridor(args, stream, resolve=never_the_same) == 0
    assert calls == 2, "each run must actually resolve; a store would defeat the measurement"
    report = stream.getvalue()
    assert "2 runs: resolved, resolved" in report
    assert "run 1:" in report and "run 2:" in report
    # The fake resolver writes no recall record, so the candidate comparison has nothing to
    # compare. It must say so rather than report two runs as agreeing about nothing.
    assert "only 0 of 2 runs left a recall record" in report


def test_no_variance_is_not_reported_as_variance() -> None:
    """The first version said "the variance is real" when nothing had varied at all.

    Exactly the falsehood entries 33 and 36 removed elsewhere: a reason has to be true of what was
    seen. Canada's three runs on 2026-08-22 produced an identical candidate set, and the report
    described that as real variance that failed to reach the decider.
    """

    stream = io.StringIO()
    print_variance(
        VarianceReport(runs=3, records_read=3, outcomes=["resolved"] * 3, stable=471, unstable=[]),
        stream,
    )
    written = stream.getvalue()

    assert "exactly the same candidate set" in written
    assert "variance is real" not in written
    # And it must not let a reader mistake stable recall for a deterministic pipeline.
    assert "known problem 10" in written


def test_a_page_only_some_runs_read_is_named() -> None:
    stream = io.StringIO()
    answering = "https://www.canada.ca/entry-requirements-country.html"
    print_variance(
        VarianceReport(
            runs=2,
            records_read=2,
            outcomes=["resolved", "refused"],
            stable=400,
            unstable=[
                CandidateVariance(
                    url=answering,
                    runs_seen=[1],
                    runs_shortlisted=[1],
                    runs_fetched=[1],
                    best_score=53.4,
                )
            ],
        ),
        stream,
    )
    written = stream.getvalue()

    assert "the corridor flipped" in written
    assert answering in written
    assert "read in runs 1" in written
