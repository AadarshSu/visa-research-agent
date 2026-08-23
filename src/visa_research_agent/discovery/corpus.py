"""A country's official page corpus: what pages exist, kept between runs.

DECISIONS entry 44. Discovery re-derives a country's candidate pages from search on every request,
so recall is re-rolled every time — entry 43 measured `canada/GB/GB/tourism` finding the page that
answers it fifteenth of 470 on one run and not at all an hour earlier. This is the store that stops
that being re-rolled: **which pages exist** does not vary by corridor, only which one answers a
given traveller does.

Three things about the shape, each of which is the thing that would otherwise be got wrong.

**It stores pages, never answers, and never scores.** A score is corridor-dependent — it weighs the
traveller's own nationality and the post serving where they live — so storing one would freeze
exactly the half of the question that must stay live. What is stored is what a crawl can know
without a traveller: the URL, what linked to it and with what words, and whether it could be read.
Scoring happens per request, from this, as it does today.

**It is additive and is never pruned by a bad run.** A URL that answered once stays even when a
later crawl misses it. That is the whole point: the failure being designed away is a page that one
run finds and the next does not. The cost is the opposite risk — a withdrawn page lingering — which
is bounded by the evidence TTL, since nothing here is evidence and every entry is re-fetched through
`LiveSourceFetcher` under its own freshness rules before it can be read.

**It is depended on, unlike the recall log.** `recall_log.py` holds nearly the same rows and is a
diagnostic: nothing reads it back, and a failed write is swallowed. This is the opposite contract —
it is the candidate source for a later run, so a failed write has to be visible. Same rows, opposite
guarantees, deliberately two files (entry 44).
"""

import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal

from pydantic import Field, ValidationError, field_validator

from visa_research_agent.discovery.models import PageLink
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.domain.trust import host_is_within, host_of
from visa_research_agent.research.errors import VisaResearchError


class CorpusError(VisaResearchError):
    """Raised when a corpus cannot be read or written safely."""


# How far a page has got, which is also its retention tier. Ordered: a status never moves down.
#
#   proven      filled a role in a resolved corridor. The strongest thing the corpus can say, and
#               the one tier that is never evicted — this page has actually answered somebody.
#   readable    fetched and read at least once.
#   unknown     discovered, never fetched. Most of the corpus, and most of it is noise: measured
#               2026-08-22, 723 of Canada's 1,071 entries scored zero on role vocabulary.
#   unreadable  a fetch failed. Recorded rather than acted on: unreadable once is not withdrawn, and
#               dropping it would be the pruning this store exists to avoid.
EntryStatus = Literal["proven", "readable", "unreadable", "unknown"]

# Higher wins when two sightings of the same page disagree. A page that has answered a corridor does
# not stop having answered it because a later crawl merely saw it, or failed to fetch it once.
_STATUS_RANK: dict[str, int] = {"unknown": 0, "unreadable": 1, "readable": 2, "proven": 3}


class CorpusEntry(StrictModel):
    """One page of a country's official corpus, and how it was found."""

    url: str = Field(min_length=1)
    title: str = ""
    link_text: str = Field(default="", max_length=300)
    """The words that linked to it. Often the only thing identifying a page: Japan's tourism
    checklist sits at `index_000070.html` and is knowable solely as "Temporary Visitor Visa"."""

    heading: str = Field(default="", max_length=300)
    depth: int = Field(default=0, ge=0)
    discovered_from: str = Field(default="", max_length=2000)
    first_seen: datetime
    last_seen: datetime
    times_seen: int = Field(default=1, ge=1)
    status: EntryStatus = "unknown"
    detail: str = ""
    """Why it was unreadable, in words true of what was seen. Empty otherwise."""

    _validate_first = field_validator("first_seen")(
        lambda value: _require_aware(value, "first_seen")
    )
    _validate_last = field_validator("last_seen")(lambda value: _require_aware(value, "last_seen"))

    def to_link(self) -> PageLink:
        """The candidate a later corridor scores, exactly as the crawl would have handed it over."""

        return PageLink(
            url=self.url,
            text=self.link_text,
            heading=self.heading,
            depth=self.depth,
            discovered_from=self.discovered_from,
        )


def canonical_key(url: str) -> str:
    """An equivalence key for "is this the same page", ignoring host and scheme aliasing.

    **Not** a replacement for the URL, which is what gets fetched and must stay exactly as found.
    This is only for comparison: does the corpus already hold this page, and is a pinned page
    present?

    Measured 2026-08-22 on Canada: 3,130 stored URLs collapse to 2,996 pages. `visas.asp` alone is
    held four times — `cic.gc.ca`, `www.cic.gc.ca` and `ircc.canada.ca`, over both schemes. Without
    this, a superset check reports pages missing that are sitting right there under another host,
    and a pin can fail to match the page it names.

    Deliberately conservative: it folds scheme, case and a leading `www.`, and nothing else. Query
    strings stay, because `answer.asp?qnum=416` and `?qnum=1453` are different pages; trailing
    slashes stay, because some authorities serve different content for them.
    """

    lowered = url.strip().lower()
    for prefix in ("https://", "http://"):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix) :]
            break
    if lowered.startswith("www."):
        lowered = lowered[4:]
    return lowered


def _require_aware(value: datetime, field: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return value


class CountryCorpus(StrictModel):
    """Every official page found for one country, with the domains it was gathered from."""

    schema_version: Literal[1] = 1
    country_code: str = Field(pattern=r"^[A-Z]{2}$")
    country_name: str = Field(min_length=1)
    trusted_domains: list[str] = Field(default_factory=list)
    """The domains in force when this was gathered, recorded so a reader can see what a later
    narrowing of the registry would exclude. **Not** what authorises a read: that is checked again
    against the live registry every time, because this file is older than the rule."""

    built_at: datetime
    entries: list[CorpusEntry] = Field(default_factory=list)

    _validate_built_at = field_validator("built_at")(
        lambda value: _require_aware(value, "built_at")
    )

    def entries_within(self, trusted: Iterable[str]) -> list[CorpusEntry]:
        """The entries still sitting on a currently trusted domain.

        Applied at read time rather than at write time on purpose. A corpus outlives the registry
        row that produced it, so a domain a person later removes from `authority_domains.yaml` must
        stop being read **without** anyone having to remember to rebuild every corpus. The stored
        `trusted_domains` says what was true then; this says what is allowed now.
        """

        domains = list(trusted)
        return [entry for entry in self.entries if host_is_within(host_of(entry.url), domains)]

    def find(self, fragment: str) -> list[CorpusEntry]:
        return [entry for entry in self.entries if fragment in entry.url]

    def holds(self, url: str) -> bool:
        """True when this page is held, under any host or scheme alias. See `canonical_key`."""

        wanted = canonical_key(url)
        return any(canonical_key(entry.url) == wanted for entry in self.entries)


def merge(
    corpus: CountryCorpus,
    found: Iterable[CorpusEntry],
    *,
    now: datetime,
) -> CountryCorpus:
    """Fold a fresh crawl into a corpus, adding and updating but **never removing**.

    The one rule this function exists to enforce. A crawl that finds fewer pages than last time is
    the ordinary case — search moves, a section is reorganised, a host times out — and treating it
    as a deletion would rebuild the exact failure the corpus is for: a page that one run has and the
    next does not.

    `first_seen` is preserved and `times_seen` accumulates, so a page found by every crawl can be
    told from one seen once a month ago. Nothing here judges either; the counts are for a person
    reading the file and for the refresh job.
    """

    by_url = {entry.url: entry.model_copy(deep=True) for entry in corpus.entries}
    for entry in found:
        existing = by_url.get(entry.url)
        if existing is None:
            by_url[entry.url] = entry.model_copy(deep=True)
            continue
        existing.last_seen = now
        existing.times_seen += 1
        # Prefer the shallower route: a page reached at depth 1 this time is more cheaply reachable
        # than the depth-2 path recorded before, and the shortest known way in is what a later crawl
        # should follow.
        if entry.depth < existing.depth:
            existing.depth = entry.depth
            existing.discovered_from = entry.discovered_from
        if entry.title and not existing.title:
            existing.title = entry.title
        if entry.link_text and not existing.link_text:
            existing.link_text = entry.link_text
        if entry.heading and not existing.heading:
            existing.heading = entry.heading
        # Status only ever moves up. A later readable result clears an earlier failure; a later
        # failure does not erase a page that has been read, still less one that has answered a
        # corridor. Without the ranking a single 502 could demote a proven page to unreadable and
        # the retention tier would drop with it.
        if _STATUS_RANK[entry.status] > _STATUS_RANK[existing.status]:
            existing.status = entry.status
            existing.detail = "" if entry.status in ("readable", "proven") else entry.detail
        elif entry.status == "unreadable" and existing.status == "unreadable":
            existing.detail = entry.detail

    return corpus.model_copy(
        update={
            "built_at": now,
            "entries": sorted(by_url.values(), key=lambda item: item.url),
        }
    )


class FileCorpusStore:
    """One JSON document per country, written atomically.

    A file per country rather than one file for the world, because a corpus is built and refreshed
    per country and two builds running at once must not fight over the same file. A networked store
    would sit behind this same pair of methods; see TODO item 20.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def path_for(self, code: str) -> Path:
        return self.directory / f"{code.upper()}.json"

    def load(self, code: str) -> CountryCorpus | None:
        """Return a country's corpus, or None when there is none.

        A file that cannot be parsed **raises** rather than reading as an absence. That is the
        opposite of `corridor_store.py`, deliberately: a corridor that cannot be read is safely
        re-resolved, but a corpus that cannot be read is the candidate source, and silently treating
        it as "this country has no pages" would turn a corrupt file into a refusal that looks like a
        country nobody has built yet.
        """

        try:
            raw = self.path_for(code).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise CorpusError(f"The corpus for {code} could not be read") from exc
        try:
            return CountryCorpus.model_validate_json(raw)
        except ValidationError as exc:
            raise CorpusError(
                f"The corpus for {code} is not readable in this schema. It is the candidate source "
                "for every corridor into that country, so it is not treated as an absence: fix or "
                "remove the file deliberately."
            ) from exc

    def store(self, corpus: CountryCorpus) -> None:
        path = self.path_for(corpus.country_code)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                json.dump(corpus.model_dump(mode="json"), handle, ensure_ascii=False, indent=2)
                temporary = Path(handle.name)
            temporary.replace(path)
        except OSError as exc:
            # Not swallowed, unlike the recall log's. This one is depended on: a build that silently
            # wrote nothing would look like a country whose crawl found nothing.
            raise CorpusError(f"The corpus for {corpus.country_code} could not be written") from exc

    def countries(self) -> list[str]:
        """Which countries have a corpus, for the refresh job and for reporting coverage."""

        try:
            return sorted(path.stem for path in self.directory.glob("*.json"))
        except OSError:
            return []
