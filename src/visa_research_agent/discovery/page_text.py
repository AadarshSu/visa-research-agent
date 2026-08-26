"""The body text of pages already fetched, indexed so a page can be found by what it says.

The corpus (entry 44) records that a page **exists** and what linked to it. It does not record what
the page *says*: `crawl._expand` reads the HTML, keeps the title and the links, and lets the body go
out of scope. So a corridor ranks three thousand pages on a median of 29 characters — an anchor, a
heading, and whatever words happen to be in the URL — while a search engine ranks the same pages on
their full text. That asymmetry, not crawl depth, is why a corpus-only run loses the page it holds.

The case that decided this. `mofa.go.jp/files/000121327.pdf` fills `document_checklist` for
`japan/IN/GB`. Everything the corpus knows about it is `link_text="Single Entry Visas (PDF)"`,
`heading="Application Procedures for"`, and a URL of pure digits — from which it scores 22.0 as
`visa_decision`, the wrong role. Its first two hundred characters read *"Checklist for Single-Entry
Short-Term Stay Visa, for all nationalities except China, Russia... Purpose of Visit... Tourism...
Documents to be submitted"*. The anchor is not junk; it is a good short label that names the page's
subject and cannot name the roles it fills or the populations it covers.

**Ranking only. This is never evidence, and the type system is what says so.**

Nothing here returns a body. `rank` returns URLs and scores; there is no public accessor for
stored text, and there is deliberately no `snippet()` for debugging, for the same reason
`build_blocked_packet` has no parameter through which page text could be passed (entry 57). Text
stored here is older than the freshness rules that govern what a traveller may be told, so a quote
taken from it would be guidance served outside `source_maximum_stale_hours` with nothing to say how
old it was. A page this index ranks is still fetched through `LiveSourceFetcher` before a word of it
reaches a plan. The worst a stale row can do is win a shortlist place for a page that has since
changed — a wasted fetch, never a wrong answer.

**The vocabulary is the lexicon's, not a second one.** Role phrases, purpose terms and country names
all come from `discovery_lexicon.yaml` and `countries.yaml`, so this cannot drift away from
`score_link`. Entry 56 is what a second vocabulary costs.
"""

import re
import sqlite3
from collections.abc import Callable, Iterable, Iterator
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path

from pydantic import Field, ValidationError

from visa_research_agent.discovery.lexicon import Country, Lexicon, RoleTerms
from visa_research_agent.discovery.models import Corridor, RoleScores
from visa_research_agent.discovery.scoring import score_body
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.errors import VisaResearchError
from visa_research_agent.research.source_cache import CachedSource

SCHEMA_VERSION = 1

# FTS5 reads a bare hyphen as a column filter and a bare quote as a phrase delimiter, so a phrase
# goes in double-quoted and everything that is not a letter, digit or space is dropped first.
# "short-term stay" becomes the phrase [short term stay], which is what it should match anyway.
_PHRASE_NOISE = re.compile(r"[^\w ]+")

# Below this many characters a page has nothing to rank: a redirect stub, a nav-only shell, a PDF
# whose text layer did not extract. `unusable` already refuses these as evidence; indexing them
# would only put empty documents into the denominator BM25 divides by.
MINIMUM_INDEXABLE_CHARS = 200

# A safety bound on how many bodies one query may score, not a relevance cut. It is deliberately
# **not** a multiple of the caller's `limit`.
#
# It was, and that was the same defect this module exists to fix, made a third time: BM25 was
# ordering the matches and only the top `limit * 8` were handed to `score_body`, so a cheap ranker
# was gating the good one. Measured on Japan 2026-08-26, the page that fills `document_checklist`
# for japan/IN/GB sits at BM25 position **116 of 122** — it is a 15,000-character document that
# says "checklist" once, which is what BM25 punishes and what `names_documents` rewards. Asking for
# six results silently narrowed recall to 48 and dropped it.
#
# So every page matching the role vocabulary is scored. That set is small — 122 of 684 indexed
# pages for Japan's widest role — because the MATCH is already the filter.
MAXIMUM_SCORED_MATCHES = 2_000

# How many URLs one `IN (...)` may name. SQLite's default parameter ceiling is far higher on
# modern builds and was 999 on older ones; chunking costs nothing and does not depend on which.
_URLS_PER_QUERY = 500


class PageTextError(VisaResearchError):
    """Raised when the page-text index cannot be read or written safely."""


class StoredPage(StrictModel):
    """One page on its way *into* the index. Write-side only — nothing reads a body back out."""

    url: str = Field(min_length=1)
    fetched_at: datetime
    body: str = Field(min_length=1)
    title: str = ""
    """The page's own `<title>` or first heading, where the source of the text knew one.

    Carried because `score_body` reads the traveller's nationality from the title and URL rather
    than from the body, deliberately — a page naming India once inside a table of exceptions is not
    a page written for Indians. A backfill from the retrieval cache has no title to give, so those
    rows score without that signal; a corpus build does, and passes it."""


class TextMatch(StrictModel):
    """A page the index ranked, identified and scored. Carries no text, by design."""

    url: str
    score: float
    bm25: float
    signals: list[str] = Field(default_factory=list)
    """Why it scored what it did, in the same shape `RoleScores.signals` uses."""


def _phrase(term: str) -> str:
    cleaned = _PHRASE_NOISE.sub(" ", term.lower()).strip()
    return f'"{cleaned}"' if cleaned else ""


def _match_query(terms: Iterable[str]) -> str:
    """An FTS5 MATCH expression that is true when any of these phrases appears."""

    phrases = [phrase for phrase in (_phrase(term) for term in terms) if phrase]
    return " OR ".join(dict.fromkeys(phrases))


class PageTextStore:
    """One SQLite database per country, mirroring `FileCorpusStore`'s one file per country.

    Per country rather than one database for all of them so a country can be rebuilt, inspected or
    thrown away on its own, and so a corrupt file costs one destination rather than every one.

    Not held in the corpus JSON, which is the point of it being here at all: that file is read whole
    and validated through pydantic on every request — 51ms for Japan's 1.4MB today — and text would
    take it to roughly 35MB, so the same load path would spend about a second parsing JSON per
    corridor on a pipeline whose whole justification is latency. SQLite answers a MATCH without
    loading the file.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def path_for(self, code: str) -> Path:
        return self.directory / f"{code.upper()}.sqlite3"

    def has(self, code: str) -> bool:
        return self.path_for(code).exists()

    @contextmanager
    def _connect(self, code: str, *, create: bool) -> Iterator[sqlite3.Connection]:
        path = self.path_for(code)
        if not create and not path.exists():
            raise PageTextError(f"There is no page-text index for {code.upper()}")
        if create:
            path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with closing(sqlite3.connect(path)) as connection:
                if create:
                    _create_schema(connection)
                yield connection
        except sqlite3.Error as exc:
            raise PageTextError(
                f"The page-text index for {code.upper()} could not be used"
            ) from exc

    def write(self, code: str, pages: Iterable[StoredPage]) -> int:
        """Add or replace pages, returning how many were indexed.

        Replace rather than merge: unlike the corpus, where a later crawl seeing fewer pages must
        never read as a deletion, a newer body of the *same* URL is simply better. Nothing is
        removed for being absent from this batch, so the index is still additive across builds.
        """

        indexed = 0
        with self._connect(code, create=True) as connection:
            for page in pages:
                if len(page.body) < MINIMUM_INDEXABLE_CHARS:
                    continue
                connection.execute("DELETE FROM page_text WHERE url = ?", (page.url,))
                connection.execute(
                    "INSERT INTO page_text (url, body) VALUES (?, ?)", (page.url, page.body)
                )
                connection.execute(
                    "INSERT INTO pages (url, fetched_at, chars, title) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(url) DO UPDATE SET fetched_at = excluded.fetched_at, "
                    "chars = excluded.chars, title = excluded.title",
                    (page.url, page.fetched_at.isoformat(), len(page.body), page.title),
                )
                indexed += 1
            connection.commit()
        return indexed

    def count(self, code: str) -> int:
        with self._connect(code, create=False) as connection:
            row = connection.execute("SELECT count(*) FROM pages").fetchone()
        return int(row[0])

    def countries(self) -> list[str]:
        try:
            return sorted(path.stem for path in self.directory.glob("*.sqlite3"))
        except OSError:
            return []

    def rank(
        self,
        code: str,
        *,
        role: str,
        corridor: Corridor,
        nationality: Country,
        lexicon: Lexicon,
        limit: int = 25,
    ) -> list[TextMatch]:
        """The pages whose own text best answers one role for this traveller.

        Two stages, and the split is the whole design. **FTS5 does recall**: it narrows thousands of
        pages to the few whose text contains the role's vocabulary at all, which is the thing anchor
        text cannot do, because the words that identify a checklist are inside the checklist and not
        in the link to it. **`score_body` does precision**, unchanged and uncopied.

        Reusing `score_body` rather than scoring here is not tidiness, it is the finding. That
        function is already the project's rule for judging a page by its text — strongest phrase per
        role rather than the sum of synonyms, distinct document nouns, nationality read from the
        title and URL and deliberately *not* from the body. Today it runs at `resolver.py:1113`, on
        pages that have already been fetched, which is **after the gate it should be part of**: a
        page that anchor text ranked out is never fetched, so its text is never scored. An index of
        text already fetched is what lets the same judgement run *before* the shortlist instead of
        after it.

        The first version of this method scored the text itself and got it backwards within an hour,
        which is why the reuse is stated this strongly. It gave a page 40 points for naming the
        traveller's nationality anywhere in its body — and the comment above
        `written_for_nationality` records that exact mistake made and measured once already:
        Japan's ministry-wide
        checklist names India once, inside a table of nationality exceptions, and that alone
        made it beat the UK post's own tourism checklist. `score_body` reads nationality from the
        title and URL for that reason. A second scorer would have had to relearn it.
        """

        terms = [term.phrase for term in lexicon.roles.get(role, RoleTerms()).terms]
        query = _match_query(terms)
        if not query:
            return []

        # Every match is scored, and the ordering here only decides which are dropped if a country
        # ever exceeds the safety bound. BM25 must not choose what `score_body` gets to see: it
        # knows nothing about the document nouns that separate a checklist from a page about
        # checklists, and it ranks a long document that names the role once near the bottom.
        with self._connect(code, create=False) as connection:
            rows = connection.execute(
                "SELECT page_text.url, page_text.body, bm25(page_text), "
                "coalesce(pages.title, '') FROM page_text "
                "LEFT JOIN pages ON pages.url = page_text.url "
                "WHERE page_text MATCH ? ORDER BY bm25(page_text) LIMIT ?",
                (query, MAXIMUM_SCORED_MATCHES),
            ).fetchall()

        matches: list[TextMatch] = []
        for url, body, raw, title in rows:
            # The body is read, scored and dropped inside this loop. It is never returned, never
            # stored on `TextMatch`, and never reaches a caller: see this module's docstring for why
            # that boundary is not negotiable.
            scores = score_body(str(body), str(title), corridor, lexicon, nationality, url=str(url))
            role_score = scores.scores.get(role)
            if role_score is None:
                continue
            matches.append(
                TextMatch(
                    url=str(url),
                    score=role_score,
                    # bm25() is negative and more negative is better; flipped so bigger wins, as
                    # everywhere else a score is compared in this codebase. Reported rather than
                    # added: it is what selected the candidate, not what ranked it.
                    bm25=-float(raw),
                    signals=list(scores.signals.get(role, [])),
                )
            )

        matches.sort(key=lambda match: (-match.score, match.url))
        return matches[:limit]

    def text_for_selection(self, code: str, urls: Iterable[str]) -> dict[str, str]:
        """The stored text of these pages, **for choosing what to fetch and for nothing else.**

        This is an amendment to the rule at the top of this module, made deliberately and recorded
        in DECISIONS entry 83 rather than slipped in. That rule said there is no accessor for a body
        and named `snippet()` as the thing not to add. The reason was never that reading stored text
        is wrong — `rank` reads it — it was that a **sentence written from it must never reach a
        traveller**, because stored text is older than `source_maximum_stale_hours` and carries
        nothing to say how old it is.

        `discovery/selection.py` reads bodies and returns `Selection`, which holds source ids and
        has no field for prose. So the chain is body → packet → model → ids, and no word of stored
        text can leave it. That property lives in `Selection`, not here, which is why this method is
        named for its single caller: a second caller wanting text for any other purpose is the
        change this docstring exists to make someone argue for.

        **It is still not evidence.** A page chosen here is fetched through `LiveSourceFetcher`
        before a word of it is quoted, exactly as before.
        """

        wanted = list(dict.fromkeys(urls))
        if not wanted or not self.has(code):
            return {}
        held: dict[str, str] = {}
        with self._connect(code, create=False) as connection:
            for start in range(0, len(wanted), _URLS_PER_QUERY):
                chunk = wanted[start : start + _URLS_PER_QUERY]
                placeholders = ",".join("?" * len(chunk))
                rows = connection.execute(
                    f"SELECT url, body FROM page_text WHERE url IN ({placeholders})",  # noqa: S608
                    chunk,
                ).fetchall()
                held.update({str(url): str(body) for url, body in rows})
        return held

    def score_held(
        self,
        code: str,
        urls: Iterable[str],
        *,
        corridor: Corridor,
        nationality: Country,
        lexicon: Lexicon,
    ) -> dict[str, RoleScores]:
        """Score, by their own text, whichever of these candidates the index holds.

        The shortlist's counterpart to `rank`. `rank` asks the index *which pages answer this role*
        and is how a person interrogates it; this asks *what do these particular pages say*, which
        is what a corridor needs — the candidate set is already assembled and the question is only
        how to order it.

        One `score_body` per page rather than one query per role: that call returns every role at
        once, so six roles cost one pass over the text instead of six.

        Silent on a country with no index, deliberately, unlike `count` and `rank`. Those are asked
        *about* the index and an absence is the answer; this is asked in the middle of resolving a
        corridor, where no index means exactly what it meant before there were any — rank on the
        link alone.
        """

        wanted = list(dict.fromkeys(urls))
        if not wanted or not self.has(code):
            return {}

        scored: dict[str, RoleScores] = {}
        with self._connect(code, create=False) as connection:
            for start in range(0, len(wanted), _URLS_PER_QUERY):
                chunk = wanted[start : start + _URLS_PER_QUERY]
                placeholders = ",".join("?" * len(chunk))
                rows = connection.execute(
                    f"SELECT page_text.url, page_text.body, coalesce(pages.title, '') "  # noqa: S608
                    f"FROM page_text LEFT JOIN pages ON pages.url = page_text.url "
                    f"WHERE page_text.url IN ({placeholders})",
                    chunk,
                ).fetchall()
                for url, body, title in rows:
                    scored[str(url)] = score_body(
                        str(body), str(title), corridor, lexicon, nationality, url=str(url)
                    )
        return scored


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            fetched_at TEXT NOT NULL,
            chars INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT ''
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS page_text USING fts5(url UNINDEXED, body);
        """
    )
    # An index written before titles were carried is upgraded rather than refused: the text in it
    # is still good, and a rebuild costs a crawl. Every row added before this simply has no title,
    # which is the same position a cache backfill is in.
    columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(pages)")}
    if "title" not in columns:
        connection.execute("ALTER TABLE pages ADD COLUMN title TEXT NOT NULL DEFAULT ''")
    connection.execute(
        "INSERT INTO meta (key, value) VALUES ('schema_version', ?) ON CONFLICT(key) DO NOTHING",
        (str(SCHEMA_VERSION),),
    )


class BackfillReport(StrictModel):
    """What a backfill saw, per country, so an empty index can be told from an empty cache."""

    indexed: dict[str, int] = Field(default_factory=dict)
    skipped_short: int = 0
    skipped_unmapped: int = 0
    """Cached pages on no country's trusted domains. Never guessed at: a page whose authority
    cannot be named is exactly what the trust rules exist to keep out of a candidate set."""

    unreadable: int = 0

    @property
    def total(self) -> int:
        return sum(self.indexed.values())


def backfill_from_cache(
    store: PageTextStore,
    cache_directory: Path,
    *,
    country_of_host: Callable[[str], str | None],
) -> BackfillReport:
    """Index every body the retrieval cache already holds, costing no fetch and no search.

    The cheap half of the argument for storing text at all. A corridor already fetches around thirty
    pages and `FileSourceCache` already keeps each one's text — so the pages that most matter, the
    ones a real corridor actually read, can be indexed with no crawl. A rebuild is then something to
    justify with a measurement rather than a prerequisite for taking one.

    The cache is keyed by URL and knows nothing about countries, so the mapping is the caller's:
    `country_of_host` is the same trust registry a corridor reads, applied now rather than when the
    page was cached, exactly as `entries_within` applies it to the corpus.
    """

    report = BackfillReport()
    pending: dict[str, list[StoredPage]] = {}
    for path in sorted(cache_directory.glob("*.json")):
        try:
            entry = CachedSource.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError):
            report.unreadable += 1
            continue
        code = country_of_host(host_of(entry.url))
        if code is None:
            report.skipped_unmapped += 1
            continue
        if len(entry.content) < MINIMUM_INDEXABLE_CHARS:
            report.skipped_short += 1
            continue
        pending.setdefault(code, []).append(
            StoredPage(url=entry.url, fetched_at=entry.fetched_at, body=entry.content)
        )

    for code, pages in sorted(pending.items()):
        report.indexed[code] = store.write(code, pages)
    return report
