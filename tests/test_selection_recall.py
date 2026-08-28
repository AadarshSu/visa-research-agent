"""Grading a selector against ground truth it did not help build.

Every test here is arithmetic on two files, which is the point of the module: entries 84 to 86 could
only be re-run by spending search and model quota, so their numbers were never checked twice. These
are the checks that can run for nothing, and the first one guards the fixture itself — a truth set
nobody validates rots into a truth set nobody believes.
"""

import io
import json
from pathlib import Path

import pytest

from visa_research_agent.discovery.cli import main, print_selection_recall
from visa_research_agent.discovery.models import ROLE_ORDER
from visa_research_agent.discovery.selection_recall import (
    DEFAULT_ORACLE_PATH,
    Arm,
    OracleError,
    arms_from_logs,
    candidates_of,
    grade,
    load_oracle,
    model_picks,
    read_recall_logs,
    unattributed_logs,
)

REPOSITORY = Path(__file__).resolve().parent.parent


def write_oracle(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


ONE_CORRIDOR = """
corridors:
  - corridor: japan/IN/GB/tourism
    contention: 4
    text_held: 3
    answers:
      visa_decision:
        - url: https://a.go.jp/decision
          seen: text
          why: it says so
      fees:
        - url: https://a.go.jp/decision
          seen: text
          why: it also says so
        - url: https://b.go.jp/fees
          seen: text
          why: a second page answering the same question
    tools:
      processing_times: https://a.go.jp/calculator
    unanswered:
      document_checklist: nothing names a document
    unverifiable:
      - https://c.go.jp/unread
    joint:
      - https://a.go.jp/decision
"""


def test_the_committed_oracle_loads_and_says_what_it_claims() -> None:
    """The fixture in the repository is valid, and every role it names is a real one.

    This is the test that earns its place: `load_oracle` refuses an unknown role, an unknown `seen`
    value and a role that is both answered and unanswered, so an edit that breaks the fixture fails
    here rather than silently changing a published number.
    """

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)

    assert len(oracle.corridors) == 20
    travellers = {"/".join(c.corridor.split("/")[1:]) for c in oracle.corridors}
    # Two curated travellers over the same ten countries. The second is what makes any number from
    # this fixture a statement about more than one profile — known problem 29, entry 91.
    assert travellers == {"IN/GB/tourism", "PH/PH/tourism"}
    assert len({c.corridor for c in oracle.corridors}) == 20
    for corridor in oracle.corridors:
        assert corridor.text_held <= corridor.contention
        for role in [*corridor.answers, *corridor.tools, *corridor.unanswered]:
            assert role in ROLE_ORDER
        for pages in corridor.answers.values():
            assert pages, "a role with no page is unanswered, not answered"


def test_every_curated_page_carries_the_sentence_that_decided_it() -> None:
    """No bare URLs. A truth set the next session cannot argue with row by row is not one."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)

    for corridor in oracle.corridors:
        for role, pages in corridor.answers.items():
            for page in pages:
                assert len(page.why) > 20, f"{corridor.corridor} {role} {page.url}"


def test_a_role_cannot_be_both_not_applicable_and_answered(tmp_path: Path) -> None:
    path = write_oracle(
        tmp_path / "oracle.yaml",
        ONE_CORRIDOR + "    not_applicable:\n      fees: there is no application\n",
    )

    with pytest.raises(OracleError, match="not applicable and also"):
        load_oracle(path)


def test_a_role_may_not_be_called_not_applicable_without_a_stated_decision(tmp_path: Path) -> None:
    """The guard that keeps `not_applicable` from becoming somewhere to hide a recall failure.

    A question only fails to arise because the decision says so, so a row claiming it without a page
    answering `visa_decision` is claiming something it cannot know — and would turn "we could not
    find the checklist" into "there is no checklist", which is the worst direction to be wrong in.
    """

    body = ONE_CORRIDOR.replace("      visa_decision:\n", "      general_entry:\n", 1)
    path = write_oracle(
        tmp_path / "oracle.yaml",
        body + "    not_applicable:\n      application_route: there is no application\n",
    )

    with pytest.raises(OracleError, match="without a page answering visa_decision"):
        load_oracle(path)


def test_a_role_the_oracle_says_is_unanswered_may_not_also_be_answered(tmp_path: Path) -> None:
    path = write_oracle(
        tmp_path / "oracle.yaml",
        ONE_CORRIDOR.replace(
            "      document_checklist: nothing names a document", "      fees: nothing states one"
        ),
    )

    with pytest.raises(OracleError, match="both answers and does not answer fees"):
        load_oracle(path)


def test_an_unknown_role_is_refused_rather_than_ignored(tmp_path: Path) -> None:
    path = write_oracle(
        tmp_path / "oracle.yaml", ONE_CORRIDOR.replace("      fees:", "      cost_of_visa:")
    )

    with pytest.raises(OracleError, match="unknown role"):
        load_oracle(path)


def test_a_page_read_in_some_way_nobody_recorded_is_refused(tmp_path: Path) -> None:
    """`seen` bounds how much a row is worth, so a value nothing defines cannot be waved through."""

    path = write_oracle(
        tmp_path / "oracle.yaml",
        ONE_CORRIDOR.replace(
            "seen: text\n          why: it says so", "seen: guessed\n          why: it says so"
        ),
    )

    with pytest.raises(OracleError, match="which is not one of"):
        load_oracle(path)


def test_a_role_several_pages_answer_is_one_target(tmp_path: Path) -> None:
    """The metric asks whether the arm chose to read *something* that answers the question.

    Entry 86 counted pages, so an arm that found one page answering five roles scored one against a
    five-page denominator somewhere else. Reading either fees page is the same outcome for a
    traveller, and reading both is not twice as good.
    """

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    key = "japan/IN/GB/tourism"

    one = grade(oracle, {key: [Arm("one", ("https://b.go.jp/fees",))]})
    both = grade(
        oracle,
        {key: [Arm("both", ("https://b.go.jp/fees", "https://a.go.jp/decision"))]},
    )

    assert (one.arms[0].roles_hit, one.arms[0].roles_total) == (1, 2)
    assert (both.arms[0].roles_hit, both.arms[0].roles_total) == (2, 2)


def test_one_page_answering_several_roles_is_credited_with_all_of_them() -> None:
    """The United Arab Emirates is one page answering six roles; the metric has to see six."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    uae = oracle.for_corridor("united-arab-emirates/IN/GB/tourism")
    assert uae is not None
    everything = "https://www.gdrfad.gov.ae/en/services/727c91b1-52eb-11ea-0320-0050569629e8"

    scored = grade(oracle, {uae.corridor: [Arm("one page", (everything,))]})

    assert scored.arms[0].roles_hit == 6


def test_naming_a_tool_is_counted_apart_from_answering_the_role(tmp_path: Path) -> None:
    """Entries 59 and 60: a questionnaire is named, never counted as the answer."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))

    scored = grade(
        oracle, {"japan/IN/GB/tourism": [Arm("tool only", ("https://a.go.jp/calculator",))]}
    )

    assert scored.arms[0].tools_hit == 1
    assert scored.arms[0].roles_hit == 0


def test_a_page_nobody_could_judge_is_neither_credited_nor_held_against(tmp_path: Path) -> None:
    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))

    scored = grade(oracle, {"japan/IN/GB/tourism": [Arm("unread", ("https://c.go.jp/unread",))]})

    assert scored.arms[0].unverifiable_read == 1
    assert scored.arms[0].roles_hit == 0
    assert scored.arms[0].roles_total == 2


def test_a_corridor_with_no_recall_log_is_reported_rather_than_scored_as_zero(
    tmp_path: Path,
) -> None:
    """A missing run is not a failed run, and a denominator that silently absorbs one lies."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))

    scored = grade(oracle, {})

    assert scored.graded == []
    assert scored.skipped == ["japan/IN/GB/tourism"]
    assert scored.arms == []


def recall_log(
    directory: Path, *, key: str, rows: list[dict[str, object]], selector: str | None = "model"
) -> None:
    """A recall log. `selector` defaults to "model" because that is what these arms replay;
    pass None for a log written before `RecallRecord.selector` existed."""

    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{abs(hash(key))}.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "corridor_key": key,
                "selector": selector,
                "candidates": rows,
            }
        ),
        encoding="utf-8",
    )


def candidate(url: str, score: float, *, fetched: bool = False) -> dict[str, object]:
    return {
        "url": url,
        "title": "",
        "found_by": "corpus",
        "depth": 1,
        "discovered_from": "",
        "best_role": "fees",
        "best_score": score,
        "scores": {"fees": score},
        "shortlisted": fetched,
        "fetched": fetched,
    }


def test_a_log_that_cannot_name_its_selector_is_not_graded_as_the_model(tmp_path: Path) -> None:
    """The defect entry 91 found by widening the oracle. A run's fetched URLs are read as the
    model's picks, and until `RecallRecord.selector` existed nothing said which selector fetched
    them — so a heuristic run was scored in the arm named `model` and compared against itself. It
    went unnoticed while every oracle corridor with a log happened to be a model run."""

    rows = [
        candidate("https://a.go.jp/decision", 90.0, fetched=True),
        candidate("https://b.go.jp/fees", 80.0),
    ]
    recall_log(tmp_path, key="japan/IN/GB/tourism", rows=rows, selector=None)
    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    logs = read_recall_logs(tmp_path)

    assert arms_from_logs(oracle, logs) == {}
    assert unattributed_logs(oracle, logs) == ["japan/IN/GB/tourism"]

    scored = grade(oracle, {}, unattributed=unattributed_logs(oracle, logs))
    assert scored.graded == []
    assert scored.unattributed == ["japan/IN/GB/tourism"]
    # Not also in `skipped`: the two need different reading. A skipped corridor was never run; this
    # one was run and the file cannot say by what.
    assert scored.skipped == []


def test_a_heuristic_run_is_refused_as_firmly_as_an_unrecorded_one(tmp_path: Path) -> None:
    recall_log(
        tmp_path,
        key="japan/IN/GB/tourism",
        rows=[candidate("https://a.go.jp/decision", 90.0, fetched=True)],
        selector="heuristic",
    )
    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    assert arms_from_logs(oracle, read_recall_logs(tmp_path)) == {}


def test_the_ranking_is_replayed_at_the_budget_the_model_actually_spent(tmp_path: Path) -> None:
    """Entry 85's mistake, prevented: the two arms must differ in one thing, not two.

    The model reads two pages here, so the heuristic gets two — not the shipped thirty-five, which
    is what made entry 85's headline wrong by a factor of six.
    """

    recall_log(
        tmp_path,
        key="japan/IN/GB/tourism",
        rows=[
            candidate("https://a.go.jp/decision", 90.0),
            candidate("https://b.go.jp/fees", 80.0),
            candidate("https://d.go.jp/loud", 95.0, fetched=True),
            candidate("https://e.go.jp/louder", 99.0, fetched=True),
        ],
    )
    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))

    arms = arms_from_logs(oracle, read_recall_logs(tmp_path))

    by_name = {arm.name: arm for arm in arms["japan/IN/GB/tourism"]}
    assert len(by_name["model"].picks) == 2
    assert len(by_name["heuristic, matched budget"].picks) == 2
    assert len(by_name["heuristic, shipped budget"].picks) == 4


def test_the_scores_a_run_recorded_are_what_the_replay_ranks_on(tmp_path: Path) -> None:
    """The replay is exact rather than approximate, and this is the reason it can be.

    A recall log stores link scores, and `CandidatePage.combined` returns the link score untouched
    when no body or text scores are attached — which is the shipped configuration everywhere,
    because the numeric text lift is off below the coverage bar and no country clears it.
    """

    rows = [candidate("https://a.go.jp/decision", 90.0), candidate("https://b.go.jp/fees", 12.5)]

    rebuilt = candidates_of({"candidates": rows})

    assert [c.best_combined() for c in rebuilt] == [("fees", 90.0), ("fees", 12.5)]


def test_a_log_from_a_heuristic_run_yields_no_model_arm(tmp_path: Path) -> None:
    """`fetched` is what the model chose. A log with none of it cannot be graded as a model arm."""

    rows = [candidate("https://a.go.jp/decision", 90.0)]
    recall_log(tmp_path, key="japan/IN/GB/tourism", rows=rows)
    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))

    assert model_picks({"candidates": rows}) == ()
    assert arms_from_logs(oracle, read_recall_logs(tmp_path)) == {}


def test_both_columns_are_printed_so_the_bias_is_visible(tmp_path: Path) -> None:
    """The independent number beside the joint one. That comparison is the point of the file."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    scored = grade(oracle, {"japan/IN/GB/tourism": [Arm("model", ("https://a.go.jp/decision",))]})
    stream = io.StringIO()

    print_selection_recall(scored, stream)
    written = stream.getvalue()

    assert "2/2" in written and "1/1" in written
    assert "neither selector helped build" in written
    assert "both arms did help build" in written


def test_the_command_refuses_rather_than_grading_nothing(tmp_path: Path) -> None:
    stream = io.StringIO()

    code = main(
        [
            "selection-recall",
            "--oracle",
            str(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR)),
            "--recall",
            str(tmp_path / "missing"),
        ]
    )

    assert code == 1
    assert stream.getvalue() == ""
