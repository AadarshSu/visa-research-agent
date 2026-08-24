"""Counting why travellers go unanswered, in the two places the reasons actually live.

The project could say how often it succeeded — 75% of corridors confirmed a visa decision, 50%
yielded a checklist (DECISIONS entry 58) — and could not say, in any countable form, *why the rest
did not*. Those failures have completely different fixes and completely different bearing on the
trust rules: a country with no row in `authority_domains.yaml` is unfinished data, an authority
answering `403` is a permanent cost of the posture in entry 18, and a page nobody could rank is a
recall problem. Reported as one number they argue for whatever the reader already believed.

**Two sources, deliberately not merged.** Reachability is decided before a resolver is ever built,
so a country refused for want of a registry row leaves no recall log at all — it is computed here
from committed data, where it is exact and needs no runs. Recall causes come from the logs of runs
that did happen. Adding them would produce a denominator that means nothing, and would let the
larger failure hide inside the smaller one.

Nothing here reads a sentence to decide anything. `RecallRecord.cause` and `unreadable_outcomes`
are typed for exactly this, and a record written before they existed is reported as unrecorded
rather than guessed at — see `RecallRecord.cause` for why the old logs cannot be repaired.
"""

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from visa_research_agent.discovery.lexicon import CountryRegistry
from visa_research_agent.discovery.recall_log import RecallRecord
from visa_research_agent.discovery.registry import AuthorityRegistry

# The order buckets are reported in: resolved outcomes first, then refusals, worst last. Fixed so
# two audits diff cleanly, and named here rather than sorted alphabetically because "adjudication
# failed" sorting above "resolved" would put the rarest thing at the top of every report.
CAUSE_ORDER: tuple[str, ...] = (
    "resolved",
    "resolved_decision_blocked",
    "resolved_decision_tool",
    "decision_not_found",
    "no_candidates",
    "adjudication_failed",
    "run_raised",
)

CAUSE_LABELS: dict[str, str] = {
    "resolved": "resolved outright",
    "resolved_decision_blocked": "resolved, decision handed over as a blocked page",
    "resolved_decision_tool": "resolved, decision handed over as a questionnaire",
    "decision_not_found": "refused, nothing stated the visa decision",
    "no_candidates": "refused, no candidate pages at all",
    "adjudication_failed": "refused, the model call failed",
    "run_raised": "the run raised before it finished",
}

# What each bucket costs, and whether the posture is what costs it. This is the column the audit
# exists to produce: without it "we refused" is one number that argues for whatever the reader
# already thought. `partly` is honest about the one genuinely mixed case — a country whose own
# government publishes no confirmable domain is the trust rule's real price, while a country nobody
# has run `visa-discover registry` against yet is not.
POSTURE_COST: dict[str, str] = {
    "no_row": "no — unfinished data",
    "row_without_domain": "partly — the trust rule's real cost",
    "resolved": "—",
    "resolved_decision_blocked": "yes — an authority refused us",
    # Not a cost of the posture at all, and it reads like one until it is said out loud. The
    # authority publishes the answer only inside a questionnaire; no rule of ours put it there, and
    # no relaxation would get it out. This is the outcome entries 59 and 60 exist to name.
    "resolved_decision_tool": "no — the authority publishes it only as a tool",
    "decision_not_found": "no — recall or scoring",
    "no_candidates": "no — recall",
    "adjudication_failed": "no — model availability",
    "run_raised": "no — a defect",
    "blocked": "yes — an authority refused us",
    "disallowed": "yes — a stated crawl policy, obeyed",
    "unreachable": "no — the site failed",
    "unusable": "no — the page held nothing readable",
    "untrusted": "yes — it left the trusted domains",
}


@dataclass(frozen=True)
class Reachability:
    """How much of the world can be researched at all, from committed data alone.

    Exact rather than sampled: every number here is a count of rows in
    `config/authority_domains.yaml` against the country registry, so it needs no network, no model
    and no runs, and it cannot drift from what a request would actually do — `domains` is the same
    property the resolver reads.
    """

    countries: int
    researchable: list[str] = field(default_factory=list)
    row_without_domain: list[str] = field(default_factory=list)
    """A row exists and offers nothing fetchable. The trust rule looked and could not confirm."""

    no_row: list[str] = field(default_factory=list)
    """No row at all. Nobody has run the registry job here; the rule has not been applied yet."""

    unconfirmable_candidates: dict[str, int] = field(default_factory=dict)
    """Per country with no usable domain, how many candidates the rule declined.

    The difference between "nothing was found" and "things were found and none could be confirmed",
    which is what tells a reviewer whether there is anything here to promote by hand.
    """

    @property
    def refused(self) -> int:
        return len(self.row_without_domain) + len(self.no_row)


@dataclass(frozen=True)
class RecallAudit:
    """What the runs on disk did, bucketed by cause."""

    records: int
    causes: Counter[str] = field(default_factory=Counter)
    """Keyed by `RefusalCause`, plus `not recorded` for logs written before the field existed."""

    unresolved_roles: Counter[str] = field(default_factory=Counter)
    unreadable: Counter[str] = field(default_factory=Counter)
    """Keyed by `FailureOutcome`, counted per URL across every run."""

    unreadable_hosts: Counter[str] = field(default_factory=Counter)
    corridors: dict[str, str] = field(default_factory=dict)
    """Corridor key to cause, so a reader can go from a bucket to the run that produced it."""

    @property
    def unrecorded(self) -> int:
        return self.causes.get("not recorded", 0)


def reachability(registry: AuthorityRegistry, countries: CountryRegistry) -> Reachability:
    """Split every country the interface offers into what can be researched and what cannot.

    The denominator is the country registry rather than the authority file, because the gap between
    them is the finding: known problem 23 is that the interface offers every country and can
    research the ones with a usable row.
    """

    researchable: list[str] = []
    row_without_domain: list[str] = []
    no_row: list[str] = []
    unconfirmable: dict[str, int] = {}
    for country in countries.countries:
        row = registry.get(country.code)
        if row is None:
            no_row.append(country.code)
            continue
        if row.domains:
            researchable.append(country.code)
            continue
        row_without_domain.append(country.code)
        if row.unconfirmable:
            unconfirmable[country.code] = len(row.unconfirmable)
    return Reachability(
        countries=len(countries.countries),
        researchable=sorted(researchable),
        row_without_domain=sorted(row_without_domain),
        no_row=sorted(no_row),
        unconfirmable_candidates=dict(sorted(unconfirmable.items())),
    )


def audit_records(records: Sequence[RecallRecord]) -> RecallAudit:
    """Bucket a set of runs, counting nothing it was not told in a typed field."""

    causes: Counter[str] = Counter()
    roles: Counter[str] = Counter()
    unreadable: Counter[str] = Counter()
    hosts: Counter[str] = Counter()
    corridors: dict[str, str] = {}
    for record in records:
        cause = record.cause or "not recorded"
        causes[cause] += 1
        corridors[record.corridor_key] = cause
        for role in record.unresolved_roles:
            roles[role] += 1
        for url, outcome in record.unreadable_outcomes.items():
            unreadable[outcome] += 1
            hosts[_host_of(url)] += 1
    return RecallAudit(
        records=len(records),
        causes=causes,
        unresolved_roles=roles,
        unreadable=unreadable,
        unreadable_hosts=hosts,
        corridors=dict(sorted(corridors.items())),
    )


def read_records(directory: Path) -> list[RecallRecord]:
    """Every recall log in a directory, newest run first.

    A file that will not parse raises rather than being skipped. This is a diagnostic reading other
    diagnostics, and quietly dropping a run would understate exactly the bucket someone is counting.
    """

    records = [
        RecallRecord.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
    ]
    return sorted(records, key=lambda record: record.recorded_at, reverse=True)


def _host_of(url: str) -> str:
    """The host, without importing the trust module for a label in a report."""

    remainder = url.split("://", 1)[-1]
    return remainder.split("/", 1)[0].split("@")[-1].split(":")[0].lower()


def counted(counter: Counter[str], order: Iterable[str]) -> list[tuple[str, int]]:
    """The named buckets in a fixed order, then anything else by count. Empty buckets are kept.

    A bucket at zero is a fact — "nothing refused us in these runs" is the finding entry 58's
    blocked column would have hidden — so it is printed rather than omitted.
    """

    named = list(order)
    rows = [(key, counter.get(key, 0)) for key in named]
    rest = sorted(
        ((key, value) for key, value in counter.items() if key not in named),
        key=lambda item: (-item[1], item[0]),
    )
    return rows + rest
