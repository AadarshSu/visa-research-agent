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
from visa_research_agent.discovery.contention import Contention
from visa_research_agent.discovery.models import ROLE_ORDER, CandidatePage, Corridor, PageLink
from visa_research_agent.discovery.selection_recall import (
    DEFAULT_ORACLE_PATH,
    Arm,
    OracleError,
    arms_from_logs,
    candidates_of,
    grade,
    load_oracle,
    model_picks,
    pool_audit,
    read_recall_logs,
    role_reach,
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

    assert len(oracle.corridors) == 21
    travellers = {"/".join(c.corridor.split("/")[1:]) for c in oracle.corridors}
    # Two curated travellers over the same ten countries, plus Czechia for the Indian one — the
    # eleventh country and the only row curated from outside the pool (entry 127). The second
    # traveller is what makes any number from this fixture a statement about more than one profile:
    # known problem 29, entry 91.
    assert travellers == {"IN/GB/tourism", "PH/PH/tourism"}
    assert len({c.corridor for c in oracle.corridors}) == 21
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


# --- the pool audit: grading the gate rather than the selector, TODO item 31 --------------------


def audit_contention(pooled: list[str], unpooled: list[str]) -> Contention:
    """A `Contention` holding only what `pool_audit` reads off it."""

    def page(url: str) -> CandidatePage:
        return CandidatePage(link=PageLink(url=url, depth=1, discovered_from="seed"))

    return Contention(
        corridor=Corridor(destination_slug="japan", passport_nationality="IN", applying_from="GB"),
        candidates=tuple(page(url) for url in pooled),
        unpooled=tuple(page(url) for url in unpooled),
        rejected=0,
        text_held=0,
    )


def test_an_answering_page_the_selector_is_never_shown_is_counted_apart(tmp_path: Path) -> None:
    """The measurement `selection-recall`'s arms structurally cannot make.

    Every arm replays what a run *chose out of the pool*, so a page the anchor scorer excluded is
    invisible to all of them at once and scores as though no selector could have found it. That is
    true, and it is the finding, and it was reading as ordinary recall.
    """

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    audit = pool_audit(
        oracle.corridors[0],
        audit_contention(["https://a.go.jp/decision"], ["https://b.go.jp/fees"]),
    )

    assert audit.pooled == ("https://a.go.jp/decision", "https://a.go.jp/decision")
    assert audit.outside == ("https://b.go.jp/fees",)
    assert audit.absent == ()


def test_a_page_the_corpus_does_not_hold_is_not_counted_as_one_the_gate_removed(
    tmp_path: Path,
) -> None:
    """`absent` and `outside` are the two ends of a bottleneck entry 88 spent a session separating:
    a page nobody crawled is item 35's gap, and a page crawled and scored to zero is item 31's.
    Adding them would merge the two and make either unfixable from the number."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    audit = pool_audit(oracle.corridors[0], audit_contention(["https://a.go.jp/decision"], []))

    assert audit.outside == ()
    assert audit.absent == ("https://b.go.jp/fees",)


def test_a_row_says_which_set_it_was_curated_from_and_defaults_to_the_pool(
    tmp_path: Path,
) -> None:
    """Never inferred. A row written before the field existed was curated inside the gate, and
    silently promoting one to `whole_corpus` would manufacture the evidence item 31 is waiting
    for."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    assert oracle.corridors[0].curated_from == "pool"

    widened = ONE_CORRIDOR.replace(
        "    contention: 4", "    curated_from: whole_corpus\n    contention: 4"
    )
    assert (
        load_oracle(write_oracle(tmp_path / "wide.yaml", widened)).corridors[0].curated_from
        == "whole_corpus"
    )


def test_a_row_curated_from_a_set_nobody_defined_is_refused(tmp_path: Path) -> None:
    """The same discipline `seen:` follows: an unrecognised value is a typo or a new idea, and
    either way reading it as the default would quietly mislabel the row's bias."""

    body = ONE_CORRIDOR.replace(
        "    contention: 4", "    curated_from: everything\n    contention: 4"
    )
    with pytest.raises(OracleError, match="curated from 'everything'"):
        load_oracle(write_oracle(tmp_path / "oracle.yaml", body))


def test_the_fixture_can_now_name_a_page_the_selector_is_never_shown() -> None:
    """Pins the honest reading of the shipped fixture, and the reading changed on 2026-09-02.

    The first twenty rows were curated from candidates scoring above zero — the same filter
    `_choose_what_to_read` applies — so a zero in the pool audit against them is a tautology, not a
    result (entry 123). `czechia/IN/GB/tourism` is the first row curated with that filter off, and
    its `document_checklist` answer is the EC supporting-documents list for applicants **in the
    United Kingdom**, which scores zero for every role and is never shown to the selector. That is
    the confirmed instance TODO item 31 was waiting for (entry 127).

    Asserted as "at least one", not "exactly one": a second such row is progress and must not fail
    a test. What must not happen is the count going back to zero, which would mean the fixture had
    silently returned to agreeing with the gate by construction.
    """

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    widened = [row for row in oracle.corridors if row.curated_from == "whole_corpus"]

    assert widened, "the fixture can no longer name a page outside the pool"
    czechia = oracle.for_corridor("czechia/IN/GB/tourism")
    assert czechia is not None and czechia.curated_from == "whole_corpus"
    assert czechia.answering_urls("document_checklist") == {
        "https://mzv.gov.cz/public/d3/71/2a/4835385_2943205_UK_EN.PDF"
    }


def test_a_role_is_pooled_when_any_one_of_its_answers_is(tmp_path: Path) -> None:
    """One pooled answer is all an arm needs, so the role is not a gate failure.

    `fees` in this fixture has two answering pages. With either of them in the pool the selector had
    something to find, and counting the role as excluded because its *other* answer was not would
    inflate the gate's cost with roles the gate never cost anything."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    row = oracle.corridors[0]

    both = audit_contention(["https://a.go.jp/decision"], ["https://b.go.jp/fees"])
    assert role_reach(row, "fees", both) == "pooled"

    neither = audit_contention([], ["https://a.go.jp/decision", "https://b.go.jp/fees"])
    assert role_reach(row, "fees", neither) == "outside"


def test_a_role_with_no_answer_and_a_corridor_with_no_corpus_both_reach_nothing(
    tmp_path: Path,
) -> None:
    """Two different silences, and neither may be counted against the gate.

    An unanswered role has nothing to classify. A corridor whose country has no corpus has nothing
    to classify it *against* — and reading that as "the answer was excluded" would let a missing
    store manufacture evidence for item 31."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    row = oracle.corridors[0]

    assert role_reach(row, "document_checklist", audit_contention(["x"], ["y"])) is None
    assert role_reach(row, "fees", None) is None


def test_a_role_answered_only_outside_the_pool_is_scored_apart_from_the_selector(
    tmp_path: Path,
) -> None:
    """The number entry 128 exists to produce: an arm cannot be charged for a page it was never
    shown. Both roles here are answered, one from the pool and one only outside it, and an arm that
    picks the pooled one scores 1/1 on the column it could act on rather than 1/2 overall."""

    oracle = load_oracle(write_oracle(tmp_path / "oracle.yaml", ONE_CORRIDOR))
    contention = audit_contention(["https://a.go.jp/decision"], ["https://b.go.jp/fees"])
    grading = grade(
        oracle,
        {"japan/IN/GB/tourism": [Arm(name="one", picks=("https://a.go.jp/decision",))]},
        contentions={"japan/IN/GB/tourism": contention},
    )
    arm = grading.arms[0]

    assert (arm.pooled_hit, arm.pooled_total) == (2, 2)
    assert (arm.outside_hit, arm.outside_total) == (0, 0)
