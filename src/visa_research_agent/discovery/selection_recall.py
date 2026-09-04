"""Grading what a selector *chose to read* against ground truth no selector helped build.

Every number in DECISIONS entries 84 to 86 was graded against a set the two arms constructed
between them: a page counted as filling a role only if some arm had fetched it and the adjudicator
had credited it, so a page neither arm read could never enter the oracle at all. Both selectors were
scored on a denominator they made together, and entry 86's +41 points rests on it. That is the
weakness entry 86 named and could not fix from its own data.

`oracle/selection_oracle.yaml` fixes it: for ten corridors, the page that answers each role, named
by hand from each corridor's whole contention set rather than from what anybody fetched. This module
reads that file, replays the shipped ranking from recorded scores, and reports both numbers — the
independent one and entries 85-86's joint one — so the size of the bias is on the record.

**Role recall, not roles filled, and not pages hit.** Entry 81 measured "roles filled" swinging +/-2
on identical input, and entries 79 to 81 are three consecutive entries that were wrong because they
leaned on it; it grades the adjudicator, not the selector. Pages hit — entry 86's metric — has a
subtler fault: one page often answers five roles, so an arm that finds the single page answering all
of the United Arab Emirates scores 1 against a five-page denominator elsewhere. The question a
selection change is actually about is *did this arm choose to read something that answers this
question*, so that is what `role_recall` counts, and a role several pages answer is one target.

Nothing here fetches, searches, or calls a model. Given a directory of recall logs and the fixture
it is arithmetic, which is why it can be a test.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import Field

from visa_research_agent.discovery.contention import Contention
from visa_research_agent.discovery.models import ROLE_ORDER, CandidatePage, PageLink, RoleScores
from visa_research_agent.discovery.resolver import DEFAULT_SHORTLIST_SIZE, shortlist
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.research.errors import VisaResearchError

DEFAULT_ORACLE_PATH = Path("oracle/selection_oracle.yaml")

# How a curated page was read, which bounds how much the row is worth. `text` is the page's own
# stored body. `title_only` is its address and label, where the index holds no body and the address
# leaves no room — Sweden's "List of third countries whose nationals must be in possession of
# visas". `mirror` is the same document read at a second address the index does hold, which is the
# only way the United States corridor could be judged at all: travel.state.gov stores nothing and
# publishes its whole /content/travel/en/ tree under adoption.state.gov as well.
SEEN_KINDS = ("text", "title_only", "mirror")

# Which set a curator read to build a row. `pool` is the 6% `_choose_what_to_read` shows the model
# and is the default, because it is what the first twenty rows were built from. `whole_corpus` means
# the anchor scorer's filter was off, so the row can name a page the selector is never shown — which
# is the only way a fixture can grade the gate rather than agree with it. See `curated_from`.
CURATION_SETS = ("pool", "whole_corpus")


class OracleError(VisaResearchError):
    """The fixture could not be read, or does not say what it claims to."""


class OraclePage(StrictModel):
    """One page a human judged to answer one role, and the sentence that decided it."""

    url: str = Field(min_length=1)
    seen: str
    why: str = Field(min_length=1)
    """Quoted or named from the page. Kept because a truth set nobody can check is not one: the
    next session has to be able to disagree with a specific row rather than with the file."""


class CorridorOracle(StrictModel):
    """What should have been read for one corridor, and what could not be established."""

    corridor: str = Field(min_length=1)
    contention: int = Field(ge=0)
    """How many candidates scored above zero — the set the curation read through."""

    text_held: int = Field(ge=0)
    """How many of those the page-text index held a body for. The ceiling on the whole row: a role
    can only be answered by a page somebody could read, and France sits at 21 of 206."""

    answers: dict[str, list[OraclePage]] = Field(default_factory=dict)
    tools: dict[str, str] = Field(default_factory=dict)
    """A role whose answer an official questionnaire works out instead of a page stating it. Naming
    one never fills the role (entries 59 and 60), so these are graded on their own line."""

    not_applicable: dict[str, str] = Field(default_factory=dict)
    """A role that does not arise for this traveller, with why — never one nobody could answer.

    Singapore is the case it was added for (TODO item 39). A Filipino needs no visa, so there is no
    application: no checklist to bring, no route to take, no fee to pay and nothing to process. All
    four were recorded `unanswered`, and the row read two of six — **a corridor that resolved
    correctly, scored as a thin one.** That is entry 93's defect a second time: the metric counting
    a complete outcome as a gap.

    Kept apart from `unanswered` because the two mean opposite things about the store. `unanswered`
    is a recall problem somebody could fix by crawling deeper or reading better. This is a fact
    about the world, and a bigger corpus would not touch it.

    **It may only be claimed where the corridor's own `visa_decision` is answered by a page saying
    no.** A role is not "not applicable" because nobody found it — that is `unanswered`, and the
    distinction is the whole point.
    """

    unanswered: dict[str, str] = Field(default_factory=dict)
    curated_from: str = "pool"
    """Which set the curator read to build this row — `pool` or `whole_corpus`.

    **The fixture's own bias, recorded on the row rather than in a comment nobody joins to the
    numbers.** The first twenty rows were curated from every candidate scoring above zero, which is
    the same 6% `_choose_what_to_read` shows the selector — so they can say whether the selector
    picked well *within* the gate and can say nothing at all about the gate, and 88 of 88 of their
    answering pages being in the pool is a tautology (entry 123). A row marked `whole_corpus` was
    curated with that filter off, from `Contention.unpooled` ranked by `PageTextStore.rank`, so its
    answers may legitimately fall outside the pool and `pool_audit` can count them.

    Never infer it. A row written before this field existed is a `pool` row, which is what the
    default says, and silently promoting one would manufacture the evidence item 31 needs.
    """

    unverifiable: list[str] = Field(default_factory=list)
    """Candidates that plausibly answer a role and hold no stored text. Neither credited nor
    dismissed: an arm that reads one is reported separately rather than scored either way."""

    excluded: list[dict[str, str]] = Field(default_factory=list)
    note: str = ""
    joint: list[str] = Field(default_factory=list)
    """The pages entries 85 and 86 graded against, kept so their bias stays measurable."""

    @property
    def slug(self) -> str:
        return self.corridor.split("/")[0]

    def answering_urls(self, role: str) -> set[str]:
        return {page.url for page in self.answers.get(role, [])}


class SelectionOracle(StrictModel):
    corridors: list[CorridorOracle] = Field(min_length=1)

    def for_corridor(self, key: str) -> CorridorOracle | None:
        return next((c for c in self.corridors if c.corridor == key), None)


def load_oracle(path: Path = DEFAULT_ORACLE_PATH) -> SelectionOracle:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise OracleError(f"the selection oracle could not be read: {exc}") from exc
    if not isinstance(raw, dict):
        raise OracleError(f"{path} does not contain a mapping")
    oracle = SelectionOracle.model_validate(raw)
    for corridor in oracle.corridors:
        for role, pages in corridor.answers.items():
            if role not in ROLE_ORDER:
                raise OracleError(f"{corridor.corridor} names an unknown role {role!r}")
            for page in pages:
                if page.seen not in SEEN_KINDS:
                    raise OracleError(
                        f"{corridor.corridor} {role} {page.url} was seen {page.seen!r}, "
                        f"which is not one of {', '.join(SEEN_KINDS)}"
                    )
        overlap = set(corridor.answers) & set(corridor.unanswered)
        if overlap:
            raise OracleError(
                f"{corridor.corridor} both answers and does not answer {', '.join(sorted(overlap))}"
            )
        if corridor.curated_from not in CURATION_SETS:
            raise OracleError(
                f"{corridor.corridor} was curated from {corridor.curated_from!r}, which is not one "
                f"of {', '.join(CURATION_SETS)}"
            )
        for role in corridor.not_applicable:
            if role not in ROLE_ORDER:
                raise OracleError(f"{corridor.corridor} names an unknown role {role!r}")
        clash = set(corridor.not_applicable) & (set(corridor.answers) | set(corridor.unanswered))
        if clash:
            raise OracleError(
                f"{corridor.corridor} calls {', '.join(sorted(clash))} not applicable and also "
                "answers it or records it unanswered"
            )
        # The guard that keeps `not_applicable` from becoming a place to hide a recall failure.
        # A role only fails to arise because the decision says it does not, so a row claiming it
        # without a stated decision is claiming something it cannot know.
        if corridor.not_applicable and "visa_decision" not in corridor.answers:
            raise OracleError(
                f"{corridor.corridor} calls a role not applicable without a page answering "
                "visa_decision; only a stated decision can say a role does not arise"
            )
    return oracle


@dataclass(frozen=True)
class PoolAudit:
    """Whether the pages a curator named are ones the selector is ever shown.

    This is the measurement `selection-recall` structurally could not make. Its arms replay what a
    run *chose* out of the pool, so a page the gate excluded is invisible to every arm at once and
    scores as though no selector could have found it — which is true, and is the finding, and was
    being reported as ordinary recall.

    `outside` is the number that matters, and a non-zero one is a confirmed instance of an answer
    inside the discarded 94%. `absent` is kept apart from it deliberately: a page the corpus does
    not hold at all is item 35's gap, not this one's, and adding the two would merge the two ends of
    the bottleneck that entry 88 spent a session separating.
    """

    corridor: str
    curated_from: str
    pooled: tuple[str, ...]
    outside: tuple[str, ...]
    absent: tuple[str, ...]

    @property
    def answers(self) -> int:
        return len(self.pooled) + len(self.outside) + len(self.absent)


def pool_audit(corridor: CorridorOracle, contention: Contention) -> PoolAudit:
    """Split one row's answering pages by whether the anchor scorer admits them."""

    pooled = {candidate.link.url for candidate in contention.candidates}
    unpooled = {candidate.link.url for candidate in contention.unpooled}
    inside: list[str] = []
    outside: list[str] = []
    absent: list[str] = []
    for role in ROLE_ORDER:
        for page in corridor.answers.get(role, []):
            if page.url in pooled:
                inside.append(page.url)
            elif page.url in unpooled:
                outside.append(page.url)
            else:
                absent.append(page.url)
    return PoolAudit(
        corridor=corridor.corridor,
        curated_from=corridor.curated_from,
        pooled=tuple(inside),
        outside=tuple(outside),
        absent=tuple(absent),
    )


@dataclass(frozen=True)
class Arm:
    """One selector's picks for one corridor, and how many pages that cost."""

    name: str
    picks: tuple[str, ...]


@dataclass
class ArmScore:
    """One arm's totals across the corridors graded."""

    name: str
    roles_hit: int = 0
    roles_total: int = 0
    pages_read: int = 0
    tools_hit: int = 0
    tools_total: int = 0
    joint_hit: int = 0
    joint_total: int = 0
    unverifiable_read: int = 0

    # Role recall split by whether the anchor scorer admits the role's answer at all. Every arm
    # picks out of `pool`, so a role answered only outside it cannot be filled by any of them, and
    # rolling the two together reports a gate failure as a selector failure. TODO item 31.
    pooled_hit: int = 0
    pooled_total: int = 0
    outside_hit: int = 0
    outside_total: int = 0
    absent_total: int = 0
    """Roles whose only answers are not in the corpus at all — item 35's gap, never item 31's.

    Held out of both numerators and both denominators rather than counted as a miss. A page nobody
    crawled says nothing about the admission gate in either direction, and the two ends of that
    bottleneck are what entry 88 spent a session separating."""

    @property
    def role_recall(self) -> float:
        return self.roles_hit / self.roles_total if self.roles_total else 0.0

    @property
    def pooled_recall(self) -> float:
        return self.pooled_hit / self.pooled_total if self.pooled_total else 0.0

    @property
    def outside_recall(self) -> float:
        return self.outside_hit / self.outside_total if self.outside_total else 0.0

    @property
    def joint_recall(self) -> float:
        return self.joint_hit / self.joint_total if self.joint_total else 0.0


@dataclass
class CorridorScore:
    corridor: str
    picks: int
    roles_hit: int
    roles_total: int
    joint_hit: int
    joint_total: int


@dataclass
class Grading:
    """Every arm's score, plus the per-corridor rows for the arm named first."""

    arms: list[ArmScore]
    rows: dict[str, list[CorridorScore]]
    graded: list[str]
    skipped: list[str]
    unattributed: list[str] = field(default_factory=list)
    """Corridors whose log exists and does not say which selector fetched its pages.

    Reported apart from `skipped` because the two need different actions: a skipped corridor has
    never been run, while one of these has a log that simply predates `RecallRecord.selector`. Both
    are fixed by running the corridor; only the second would otherwise look like a working
    measurement (entry 91)."""


def role_reach(corridor: CorridorOracle, role: str, contention: Contention | None) -> str | None:
    """Where a role's answers live relative to the admission gate: pooled, outside, or absent.

    A role counts as **pooled** when any of its answering pages is in the pool, because one is all
    an arm needs. It is **outside** only when every answer it has was excluded by the gate — that is
    the role no selector can fill however well it chooses. **absent** is the same test against the
    corpus, and it is reported separately rather than as a miss: an address nobody crawled says
    nothing about the gate in either direction (item 35, not item 31).

    Returns None when the role is unanswered, or when there is no contention set to judge against —
    a corridor whose country has no corpus is not evidence that its answers were excluded.
    """

    pages = corridor.answers.get(role)
    if not pages or contention is None:
        return None
    pooled = {candidate.link.url for candidate in contention.candidates}
    unpooled = {candidate.link.url for candidate in contention.unpooled}
    urls = {page.url for page in pages}
    if urls & pooled:
        return "pooled"
    if urls & unpooled:
        return "outside"
    return "absent"


def grade(
    oracle: SelectionOracle,
    arms_by_corridor: Mapping[str, Sequence[Arm]],
    *,
    unattributed: Sequence[str] = (),
    contentions: Mapping[str, Contention] | None = None,
) -> Grading:
    """Score each arm on role recall, tools found, and entries 85-86's joint page set.

    With `contentions` the role numbers are additionally split by `role_reach`, which is the only
    way to tell a selector that chose badly from a gate that never offered the choice.
    """

    totals: dict[str, ArmScore] = {}
    rows: dict[str, list[CorridorScore]] = {}
    graded: list[str] = []
    skipped: list[str] = []
    for corridor in oracle.corridors:
        arms = arms_by_corridor.get(corridor.corridor)
        if not arms:
            skipped.append(corridor.corridor)
            continue
        graded.append(corridor.corridor)
        joint = set(corridor.joint)
        for arm in arms:
            score = totals.setdefault(arm.name, ArmScore(name=arm.name))
            picked = set(arm.picks)
            hit = sum(
                1
                for role in ROLE_ORDER
                if corridor.answers.get(role) and picked & corridor.answering_urls(role)
            )
            score.roles_hit += hit
            score.roles_total += len(corridor.answers)
            contention = (contentions or {}).get(corridor.corridor)
            for role in ROLE_ORDER:
                reach = role_reach(corridor, role, contention)
                if reach is None:
                    continue
                found = bool(picked & corridor.answering_urls(role))
                if reach == "pooled":
                    score.pooled_total += 1
                    score.pooled_hit += found
                elif reach == "outside":
                    score.outside_total += 1
                    score.outside_hit += found
                else:
                    score.absent_total += 1
            score.pages_read += len(arm.picks)
            score.tools_hit += sum(1 for url in corridor.tools.values() if url in picked)
            score.tools_total += len(corridor.tools)
            score.joint_hit += len(joint & picked)
            score.joint_total += len(joint)
            score.unverifiable_read += len(set(corridor.unverifiable) & picked)
            rows.setdefault(arm.name, []).append(
                CorridorScore(
                    corridor=corridor.corridor,
                    picks=len(arm.picks),
                    roles_hit=hit,
                    roles_total=len(corridor.answers),
                    joint_hit=len(joint & picked),
                    joint_total=len(joint),
                )
            )
    return Grading(
        arms=list(totals.values()),
        rows=rows,
        graded=graded,
        skipped=[key for key in skipped if key not in set(unattributed)],
        unattributed=list(unattributed),
    )


# --- reading the arms back out of recall logs ------------------------------------------------


def candidates_of(record: dict[str, object]) -> list[CandidatePage]:
    """Rebuild the candidate set the run ranked, from the scores it recorded.

    Only `link_scores` is restored, and that is exact rather than approximate: the recall log stores
    link scores, and `combined` returns the link score untouched when no body or text scores are
    attached — which is the shipped configuration everywhere, because the numeric text lift is off
    below `DEFAULT_TEXT_COVERAGE_BAR` and no country clears it.
    """

    rows = record.get("candidates")
    if not isinstance(rows, list):
        raise OracleError("a recall log has no candidates to replay")
    rebuilt: list[CandidatePage] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        rebuilt.append(
            CandidatePage(
                link=PageLink(url=str(row["url"]), depth=int(row.get("depth", 0))),
                link_scores=RoleScores(scores=dict(row.get("scores", {}))),
                title=str(row["title"]) if row.get("title") else None,
                found_by=str(row.get("found_by", "crawl")),  # type: ignore[arg-type]
            )
        )
    return rebuilt


def model_picks(record: dict[str, object]) -> tuple[str, ...]:
    """What the run actually read — **only when the run says a model chose it.**

    A log's fetched URLs are what the selector picked, and until entry 91 nothing in the file said
    *which* selector. That was harmless only by accident: the ten corridors in the oracle all had
    logs from the model runs behind entries 85 to 87. Adding a second traveller brought in six logs
    written before entry 85 turned the model selector on, and grading them here put the heuristic
    into the arm labelled `model` and compared it against itself — moving a published figure by six
    points with nothing in the output to say so.

    So an unattributable log yields no picks, and the caller counts it rather than guessing. That is
    `RecallRecord.cause`'s rule applied to a second field: a record written before the field existed
    is reported as unrecorded, never inferred.
    """

    if record.get("selector") != "model":
        return ()
    rows = record.get("candidates")
    if not isinstance(rows, list):
        return ()
    return tuple(str(row["url"]) for row in rows if isinstance(row, dict) and row.get("fetched"))


def read_recall_logs(directory: Path) -> dict[str, dict[str, object]]:
    """Every recall log in a directory, newest kept, keyed by corridor."""

    logs: dict[str, dict[str, object]] = {}
    for path in sorted(directory.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(record, dict) and isinstance(record.get("corridor_key"), str):
            logs[str(record["corridor_key"])] = record
    return logs


MATCHED = "heuristic, matched budget"
FULL = "heuristic, shipped budget"
MODEL = "model"


def unattributed_logs(oracle: SelectionOracle, logs: dict[str, dict[str, object]]) -> list[str]:
    """Oracle corridors whose log exists and cannot say which selector chose what it read."""

    return [
        corridor.corridor
        for corridor in oracle.corridors
        if corridor.corridor in logs and logs[corridor.corridor].get("selector") != "model"
    ]


def arms_from_logs(
    oracle: SelectionOracle,
    logs: dict[str, dict[str, object]],
    *,
    full_size: int = DEFAULT_SHORTLIST_SIZE,
) -> dict[str, list[Arm]]:
    """Three arms per corridor: the model's own picks, and the ranking at two budgets.

    **The matched budget is the model's pick count for *that corridor*.** That is what entry 86
    means by "the same 112 picks": ten per-corridor budgets summed, not one number split ten ways.
    Entry 85 got a headline wrong by a factor of six because it let two things vary at once — who
    chooses and how many they choose — so holding the second fixed is the whole point of this arm.

    One recall log per corridor is enough for all three, and that is a measured fact rather than an
    assumption: the corpus makes candidate generation deterministic, so the heuristic and model runs
    behind entries 85 and 86 produced identical candidate sets, and replaying the ranking from
    either log gives the same 13 of 29.

    Pins and crawl failures are both empty here, as they were in entry 86. Both omissions can only
    help the heuristic, which is the right direction for a comparison it loses.
    """

    by_corridor: dict[str, list[Arm]] = {}
    for corridor in oracle.corridors:
        record = logs.get(corridor.corridor)
        if record is None:
            continue
        chosen = model_picks(record)
        if not chosen:
            # Either nothing was fetched or the log cannot say which selector fetched it. Both are
            # "no arm can be replayed here", and neither is graded silently — `Grading.skipped`
            # carries them to the report.
            continue
        candidates = candidates_of(record)
        by_corridor[corridor.corridor] = [
            Arm(
                name=MATCHED,
                picks=tuple(c.link.url for c in shortlist(candidates, size=len(chosen))),
            ),
            Arm(name=MODEL, picks=chosen),
            Arm(
                name=FULL,
                picks=tuple(c.link.url for c in shortlist(candidates, size=full_size)),
            ),
        ]
    return by_corridor
