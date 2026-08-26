"""Turning a corridor into a set of official sources, or refusing to.

The order is deliberate: search to arrive, crawl to pinpoint, then fetch the shortlist through the
ordinary retrieval path so that discovered pages are subject to exactly the same trust, PDF and
freshness rules as hand-configured ones.

If a load-bearing role cannot be filled confidently the corridor is refused. A plausible substitute
for a document checklist is worse than no answer, because the traveller would be told to bring the
wrong papers with full confidence.

A missing checklist is the one exception, and it is not a relaxation of that rule. Some authorities
publish no checklist anywhere — Vietnam states its e-visa requirements as upload fields inside the
application form — so the corridor resolves and the absence is reported instead. What must never
happen is a checklist appearing without a source behind it, which `VisaPlan` refuses structurally.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from urllib.parse import urlsplit

from pydantic import Field

from visa_research_agent.discovery.adjudication import (
    MAXIMUM_BLOCKED_JUDGED,
    AdjudicationError,
    AdjudicationQuotaExhausted,
    RoleAdjudication,
    RoleAdjudicator,
    build_blocked_packet,
    build_candidate_packet,
    load_adjudication_prompt,
    load_blocked_prompt,
    validated_blocked_choices,
    validated_choices,
    validated_tools,
)
from visa_research_agent.discovery.corpus import CountryCorpus, canonical_key
from visa_research_agent.discovery.crawl import (
    DEFAULT_CRAWL_PAGES,
    CrawlFetcher,
    LinkCrawler,
)
from visa_research_agent.discovery.lexicon import (
    Country,
    CountryRegistry,
    Lexicon,
    get_country_registry,
    get_lexicon,
)
from visa_research_agent.discovery.models import (
    REPORTED_ROLES,
    ROLE_ORDER,
    CandidatePage,
    Corridor,
    DiscoveryRole,
    PageLink,
    RefusalCause,
    ResolvedCorridor,
    ResolvedSource,
    ResolvedTool,
    RoleScores,
)
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.recall_log import (
    RecallLog,
    RecallRecord,
    considered,
)
from visa_research_agent.discovery.scoring import (
    foreign_post_labels,
    is_archived,
    is_boilerplate,
    rank_for_role,
    score_body,
    score_link,
    wrong_audience,
    wrong_country,
)
from visa_research_agent.discovery.search import (
    SearchError,
    SearchProvider,
    corridor_queries,
    resolve_corridor_countries,
    search_all,
    usable_results,
)
from visa_research_agent.discovery.urls import (
    canonicalise_url,
    is_crawlable,
    published_date_in_path,
)
from visa_research_agent.domain.models import (
    PERSISTENT_REFUSAL_STATUS_CODES,
    ConfiguredSource,
    DestinationConfig,
    FailureOutcome,
    SourceFailure,
    SourceKind,
    StrictModel,
)
from visa_research_agent.domain.trust import host_is_within, host_of, registrable_domain
from visa_research_agent.research.live_sources import LiveSourceFetcher

DEFAULT_TEXT_COVERAGE_BAR = 0.5
"""What share of a corridor's candidates must have stored text before it may rank them.

A majority, and a statement rather than a tuned number — see `_text_scoring_is_fair`. Exposed as a
constructor argument only so the rule can be tested and measured against, never so a caller can
lower it to get more pages through.
"""

MINIMUM_ROLE_SCORE = 20.0
# How many pages the adjudicator gets to choose from. **This is a recall budget, not a precision
# one**, and reading it the other way is what kept it at ten for so long.
#
# The heuristic scorer does not decide anything: it decides what the model is allowed to see. So a
# page it ranks out of this window is one nothing downstream can recover, while a page it ranks in
# wrongly costs only an excerpt. The two errors are not symmetric, and the budget should reflect
# that.
#
# Measured 2026-08-18, changing only this number, live, on registry domains:
#
#   Canada       10 → refuses, no visa decision.  25 → every role filled.
#   Japan        10 → no visa decision.           25 → every role filled, same checklist.
#   Netherlands  10 → no checklist.               25 → checklist found.
#   Sweden       10 → two roles unfilled.         25 → unchanged; it fails for another reason.
#
# Two corridors that refused now resolve completely, and nothing regressed. **It bought more than
# any scoring rule in `scoring.py` does**, which is the finding, not the number.
#
# It is close to free. Fetching is concurrent, so the cost scales with batches rather than pages:
# Japan's corridor took 44.5s at ten and 39.3s at twenty-five, Canada's 45.2s and 41.7s — within
# noise both times, with no systematic penalty either way. Adjudication input roughly doubles, to
# about 19k tokens, which is small for one call.
#
# **Raised from 25 to 35 on 2026-08-24, together with the per-role depth below** (entry 61). The two
# move together and neither works alone: at depth 5 the reservation wants 30 places, so leaving the
# budget at 25 pushes the deepest reservations straight back out at truncation — measured, that
# dropped three previously-shortlisted pages per corridor and made the whole thing non-monotone,
# with depth 6 admitting *fewer* answers than depth 5. At 35 the truncation barely fires: replayed
# over 26 recorded corridors, **not one page that is shortlisted today is dropped.**
DEFAULT_SHORTLIST_SIZE = 35
# How many candidates each role reserves before the budget is filled best-first.
#
# **Three until 2026-08-24, and three was the reason the United Kingdom had no plan.** The page that
# decides a UK visa, `gov.uk/check-uk-visa`, scores 30.4 for `visa_decision` in every corridor —
# identically, because it names no country, which is what a page that *asks* your nationality does.
# What moves is the pages around it: for Nigeria and the Philippines it is 3rd for its role and got
# in; for India a ballot scheme on two paths and for China `ads-visa` and a translated-guidance page
# take the places, and at 5th it did not. Every one of those outranks it on `nationality:+40`, the
# scorer's largest term, awarded for a substring of the URL (TODO item 26).
#
# Five is the measured threshold rather than a guess, and the whole grid is in entry 61: depth 4
# admits nothing new, depth 5 admits the checker in all four UK corridors, and depths above it buy
# nothing until the budget grows to match. It is deliberately not a fix to the *scoring* — entries
# 56 and 57 both establish that "what does this page mean" is not a keyword question, and there is
# no honest keyword ranking an 804-character landing page above one that discusses visas at length.
DEFAULT_SHORTLIST_ROLE_DEPTH = 5
# Places held for each trusted domain before the rest are filled best-first. One is enough for what
# this protects against — an authority being shut out of the fetch entirely — and cheap: with the
# trusted set capped, the reserved places cannot crowd out the fill they exist to balance.
DEFAULT_SHORTLIST_DOMAIN_FLOOR = 1
# How much of each candidate the adjudicator is shown, per candidate rather than per packet. This
# is a **second recall gate** behind the shortlist, and entry 40's asymmetry applies to it
# unchanged: text the model never sees is text nothing downstream can recover.
#
# At 6,000, a flat head-of-page slice, it decided corridors on its own. `canada/GB/GB/tourism`
# ranked the right page first, fetched it, and refused: the sentence naming a "British citizen" as
# eTA-required sits at offset 8,947 of 16,465, because the page lists visa-required countries
# alphabetically and starts the eTA list only at 8,517. India at 5,325 was answered and every
# visa-exempt nationality was not, so whether a corridor resolved depended on where the traveller's
# nationality fell in an alphabet — and nothing in the output said so. See entry 42.
#
# Three numbers now, because widening alone scales badly across 25 candidates: the budget is the
# head plus a window centred on each later mention of the traveller's own country, and leftover
# budget reads straight on from the head.
#
# Measured 2026-08-21 over the 27 cached canada.ca/gc.ca pages in `var/cache`, page text across the
# packet goes from 84,704 characters to 153,862 (~+17k tokens for one call). **Almost all of that
# is the raise, not the anchoring**: a flat 20,000 costs 153,852 on the same pages, because 19 of
# the 27 are shorter than the head and only 2 exceed the budget at all. Anchoring is not what makes
# this affordable — it is what stops the raise from being another fixed offset. It changes nothing
# for a page under the budget and everything for one over it: on the 50,000-character visitor-visa
# PDF a US traveller's windows land at 19,452 and 24,449, and the second is text a flat 20,000
# cuts.
DEFAULT_EXCERPT_CHARACTERS = 20_000
# The head is kept whole because it carries the title, the "on this page" list and what the page is
# for. It is the old flat budget, so no page is now shown less of its head than before.
DEFAULT_EXCERPT_HEAD_CHARACTERS = 6_000
# Centred on the mention, not started at it: Canada's answering sentence — "You need an eTA … you
# don't need a visitor visa" — sits about 250 characters *before* the "British citizen" that
# anchors it, and a forward-only window would have cut exactly the sentence being looked for.
DEFAULT_EXCERPT_WINDOW_CHARACTERS = 3_000

# How many times the role adjudication may be asked before the corridor is refused. Two, so a
# momentary failure — a timeout, a rate limit, one malformed response — does not cost a corridor,
# while a real outage refuses instead of falling back to the heuristic. Retrying a *model provider*
# is not what DECISIONS entry 18 forbids; that is about an authority refusing to be read.
ADJUDICATION_ATTEMPTS = 2


class AdjudicationRefusal(AdjudicationError):
    """Every adjudication attempt failed, so the corridor is refused rather than guessed at.

    Distinct from `AdjudicationError` so the retry loop can catch the ordinary failure without
    catching its own decision to give up, and so a caller can tell "this call failed" from "this
    corridor has no answer". Carries the attempt count because those calls were paid for.
    """

    def __init__(self, attempts: int, reason: str) -> None:
        super().__init__(f"role adjudication failed on all {attempts} attempts ({reason})")
        self.attempts = attempts


class FetchedShortlist(StrictModel):
    """The shortlisted pages that could actually be read, and the text they yielded.

    The ids and text are carried rather than discarded because adjudication needs to name pages
    back to the application, and the application must be able to check that what came back was a
    page it actually fetched.
    """

    candidates: list[CandidatePage] = Field(default_factory=list)
    by_id: dict[str, CandidatePage] = Field(default_factory=dict)
    contents: dict[str, str] = Field(default_factory=dict)
    failures: list[SourceFailure] = Field(default_factory=list)
    """Why the rest could not be read, carried out rather than dropped.

    This used to be discarded here, and the crawl was covering for it: every refusal a corridor
    reported came from `CrawlFetcher`, so a page refused at *retrieval* time reached
    `inaccessible_domains`, `inaccessible_urls` and the notes only if the crawl had happened to
    meet the same refusal first. With the crawl gone for a destination that has a corpus, this is
    the only place a refusal is observed at all — and a corridor that stops saying an authority
    refused it is the reporting discipline of DECISIONS entry 18 lost to a speed change.
    """


@dataclass
class ResolutionTrace:
    """What one run considered, filled in as it goes.

    A mutable scratch object rather than a return value, because the runs worth reading are the
    ones that end early: a corridor that refuses at "no candidate pages were found" still has
    queries and seeds worth seeing, and it never reaches a return that could carry them.
    """

    queries: list[str] = field(default_factory=list)
    seeds: list[str] = field(default_factory=list)
    candidates: dict[str, CandidatePage] = field(default_factory=dict)
    shortlisted: set[str] = field(default_factory=set)
    fetched: set[str] = field(default_factory=set)
    crawl_failures: dict[str, str] = field(default_factory=dict)
    fetch_failures: list[SourceFailure] = field(default_factory=list)
    """What reading the shortlist could not read, kept typed rather than flattened to a sentence.

    The crawl's failures were the only ones recorded until 2026-08-24, and once the crawl left the
    request path (entry 51) that meant none were. The shortlist fetch is the only stage that meets a
    refusal now.
    """

    refusal_cause: RefusalCause | None = None
    """Set only where a refusal is decided, for the two `ResolvedCorridor` cannot show.

    A run that found no candidates and a run whose adjudication failed both return a corridor with
    no sources, so `outcome_cause` cannot separate them from the result. Everything else is derived
    there rather than set here, because a value recorded twice drifts.
    """


def _slugify(value: str, *, maximum: int = 24) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return cleaned[:maximum].strip("_")


def build_source_id(destination_slug: str, url: str, taken: set[str]) -> str:
    """A stable identifier derived from the URL alone.

    Deriving it from the URL rather than the rank or role means the same page keeps the same id
    between runs, so two proposals can be compared.
    """

    prefix = _slugify(destination_slug, maximum=8) or "dst"
    host = host_of(url)
    host_label = _slugify(host.split(".")[0] if host else "src", maximum=16)
    segments = [segment for segment in urlsplit(url).path.split("/") if segment]
    stem = _slugify(segments[-1].rsplit(".", 1)[0], maximum=24) if segments else "index"
    if not stem or stem.isdigit():
        stem = _slugify(segments[-2], maximum=24) if len(segments) > 1 else "page"

    base = "_".join(part for part in (prefix, host_label, stem) if part)[:48].strip("_")
    if not base or not base[0].isalnum():
        base = f"src_{base}".strip("_")

    candidate = base
    suffix = 2
    while candidate in taken:
        candidate = f"{base[:44]}_{suffix}"
        suffix += 1
    taken.add(candidate)
    return candidate


def derive_authority(url: str, destination: DestinationConfig) -> tuple[str, SourceKind]:
    """Name the authority behind a URL, preferring what a human already wrote down."""

    host = host_of(url)
    for configured in destination.sources:
        if host_of(str(configured.url)) == host:
            return configured.authority, configured.kind
    for configured in destination.sources:
        if host_is_within(host, [host_of(str(configured.url))]):
            return configured.authority, configured.kind

    # An approved domain with no configured page yet: describe it plainly rather than guess.
    lowered = host.lower()
    if "emb" in lowered or "consul" in lowered:
        return f"{destination.display_name} mission ({host})", "embassy_or_high_commission"
    if "immi" in lowered or "ica" in lowered:
        return f"{destination.display_name} immigration authority", "immigration_authority"
    return f"{destination.display_name} authority ({host})", "foreign_ministry"


def _with_published_date(url: str, signals: list[str]) -> list[str]:
    """Prefix what the URL says about publication, so a reviewer sees it without digging."""

    published = published_date_in_path(url)
    return [f"published in path: {published}", *signals] if published else signals


def clean_title(raw: str | None, fallback: str) -> str:
    """Tidy a page title, dropping the trailing site name authorities append."""

    if not raw or not raw.strip():
        return fallback
    title = " ".join(raw.split())
    for separator in ("|", "—", " - "):
        if separator in title:
            head = title.split(separator)[0].strip()
            if len(head) >= 8:
                title = head
                break
    return title[:90] or fallback


class CorridorResolver:
    """Find the official sources one traveller needs."""

    def __init__(
        self,
        provider: SearchProvider,
        crawl_fetcher: CrawlFetcher,
        live_fetcher: LiveSourceFetcher,
        *,
        lexicon: Lexicon | None = None,
        countries: CountryRegistry | None = None,
        shortlist_size: int = DEFAULT_SHORTLIST_SIZE,
        shortlist_role_depth: int = DEFAULT_SHORTLIST_ROLE_DEPTH,
        shortlist_domain_floor: int = DEFAULT_SHORTLIST_DOMAIN_FLOOR,
        minimum_role_score: float = MINIMUM_ROLE_SCORE,
        results_per_query: int = 8,
        adjudicator: RoleAdjudicator | None = None,
        excerpt_characters: int = DEFAULT_EXCERPT_CHARACTERS,
        excerpt_head_characters: int = DEFAULT_EXCERPT_HEAD_CHARACTERS,
        excerpt_window_characters: int = DEFAULT_EXCERPT_WINDOW_CHARACTERS,
        recall_log: RecallLog | None = None,
        corpus: CountryCorpus | None = None,
        page_text: PageTextStore | None = None,
        text_scoring_coverage_bar: float = DEFAULT_TEXT_COVERAGE_BAR,
        pinned: list[str] | None = None,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.provider = provider
        self.crawl_fetcher = crawl_fetcher
        self.live_fetcher = live_fetcher
        self.lexicon = lexicon or get_lexicon()
        self.countries = countries or get_country_registry()
        self.shortlist_size = shortlist_size
        self.shortlist_role_depth = shortlist_role_depth
        self.shortlist_domain_floor = shortlist_domain_floor
        self.minimum_role_score = minimum_role_score
        self.results_per_query = results_per_query
        # Optional on purpose. Without one the resolver behaves exactly as it did before
        # adjudication existed, which keeps the deterministic path as a regression baseline.
        self.adjudicator = adjudicator
        self.excerpt_characters = excerpt_characters
        self.excerpt_head_characters = excerpt_head_characters
        self.excerpt_window_characters = excerpt_window_characters
        # Optional, and nothing reads it back. A corridor behaves identically without one; what is
        # lost is the ability to answer "was that page ranked out, or never found" afterwards.
        self.recall_log = recall_log
        # The country's known pages, seeded alongside search rather than instead of it. Optional, so
        # a resolver built without one behaves exactly as it did before the corpus existed.
        self.corpus = corpus
        # The body text of pages already fetched, read before the shortlist so a candidate can be
        # ranked by what its page says rather than only by the link pointing at it. Optional, and a
        # country with no index behaves exactly as it did before one existed (entry 78).
        self.page_text = page_text
        self.text_scoring_coverage_bar = text_scoring_coverage_bar
        # URLs that already filled a role for this corridor. They keep their shortlist places
        # whatever the ranking says; see `_shortlist`.
        self.pinned = list(pinned or [])
        # What this run considered, kept so the caller can fold it back into the corpus. A resolver
        # is built per corridor, so this is per-run state rather than something outliving a run —
        # the mistake entry 37 records about render budgets.
        self.discovered: list[PageLink] = []
        self.trace = ResolutionTrace()
        self.now = now

    async def resolve(self, destination: DestinationConfig, corridor: Corridor) -> ResolvedCorridor:
        """Resolve the corridor, and write down what it considered on the way.

        The trace is filled as the run proceeds rather than rebuilt at the end, so a corridor that
        refuses early still records how far it got — which is the run most worth reading.
        """

        trace = ResolutionTrace()
        # Kept on the resolver so a caller can read what this run considered without re-reading the
        # recall log, which is overwritten per corridor and deliberately depended on by nothing.
        # Safe as per-run state because a resolver is built per corridor; the mistake entry 37
        # records is counting a *budget* on an object that outlives the run, not recording one.
        self.trace = trace
        resolved: ResolvedCorridor | None = None
        try:
            resolved = await self._resolve(destination, corridor, trace)
            return resolved
        finally:
            self._write_recall_log(corridor, trace, resolved)

    async def _resolve(
        self, destination: DestinationConfig, corridor: Corridor, trace: "ResolutionTrace"
    ) -> ResolvedCorridor:
        nationality, residence = resolve_corridor_countries(corridor, self.countries)
        destination_code = self._destination_code(destination)
        notes: list[str] = []
        mission_domains = self._mission_domains(destination, residence)
        # Computed once per corridor rather than per link: it walks every country in the registry,
        # and the answer depends only on the corridor's two endpoints.
        other_posts = foreign_post_labels(self.countries, destination_code, residence)

        def score(link: PageLink) -> RoleScores:
            return score_link(
                link,
                corridor,
                self.lexicon,
                nationality,
                residence,
                mission_domains=mission_domains,
                other_posts=other_posts,
            )

        def reject(link: PageLink) -> str | None:
            if is_archived(link.url, self.lexicon):
                return "the path marks it as archived or superseded"
            if is_boilerplate(link.url, self.lexicon):
                return "the path marks it as site furniture rather than guidance"
            audience = wrong_audience(link, corridor, self.lexicon)
            if audience is not None:
                return f"the page is for {audience} holders, not this traveller"
            other = wrong_country(link, corridor, self.countries, destination_code)
            if other is not None:
                return f"the page is about {other}, which is not part of this corridor"
            return None

        # 1. Search to arrive.
        queries = corridor_queries(corridor, destination, nationality, residence)
        trace.queries = queries
        seeds: list[str] = []
        search_candidates: dict[str, CandidatePage] = {}
        # Every query at once, but the results walked in the order the queries were asked. Which
        # page a corridor resolves to depends on the order candidates arrive, so it must not depend
        # on which query the engine answered first.
        # A search outage does not have to end the corridor when the country's pages are already
        # on disk — but it must never be invisible, and it must never happen where there is nothing
        # to fall back to. DECISIONS entry 74.
        searched_without_error = True
        try:
            found = await search_all(self.provider, queries, count=self.results_per_query)
        except SearchError as exc:
            if not self._corpus_links(destination):
                # Nothing stored for this destination, so search was the only recall there was.
                # Falling through here would turn "we could not look" into "there is nothing".
                raise
            searched_without_error = False
            found = {query: [] for query in queries}
            notes.append(
                f"search was unavailable ({exc}), so this corridor was answered from "
                f"{destination.display_name}'s stored page corpus alone. Nothing was substituted "
                "for the pages search would have added, and this result is not kept for reuse."
            )
        for query in queries:
            results = usable_results(found[query], destination)
            for result in results:
                url = canonicalise_url(result.url)
                if not is_crawlable(url, destination):
                    continue
                # Truncated exactly as the crawler truncates anchor text. A search engine will
                # return a title far longer than any link on a page — China's ministry returned a
                # 300-plus character speech headline — and an over-long one raised rather than
                # being trimmed, taking the whole corridor down.
                link = PageLink(
                    url=url,
                    text=result.title[:300],
                    heading="",
                    depth=0,
                    discovered_from=query,
                )
                if reject(link) is not None:
                    continue
                if url not in search_candidates:
                    search_candidates[url] = CandidatePage(
                        link=link, link_scores=score(link), title=result.title, found_by="search"
                    )
                if url not in seeds:
                    seeds.append(url)

        trace.seeds = seeds
        if not seeds and searched_without_error:
            # Guarded, because with search unavailable this sentence would be false of what was
            # seen: nothing was returned because nothing was asked. The note above already says so,
            # and two notes describing one event as two different failures is how a reader ends up
            # believing the corpus came up empty. Entries 33 and 36.
            notes.append("search returned nothing on an approved domain for this corridor")

        # 2. The country's known pages, which is what decides whether a crawl is worth running.
        #
        # Union with search rather than replacement: the corpus is not a superset of what a live run
        # finds — measured 2026-08-22, five of twenty-four pages a Canada run fetched were absent
        # from a 3,130-entry corpus, and one stayed absent when the exact query that had surfaced it
        # was re-run. Search is nondeterministic at the source, so no offline sweep can guarantee
        # the superset; the union is what closes the gap in both directions.
        #
        # Trust is applied here, at read time, against the domains in force now rather than those
        # in force when the corpus was built.
        corpus_links = self._corpus_links(destination)
        held = {canonical_key(link.url) for link, _ in corpus_links}
        candidates: dict[str, CandidatePage] = dict(search_candidates)
        from_corpus = 0
        for entry, title in corpus_links:
            if reject(entry) is not None:
                continue
            from_corpus += 1
            stored = CandidatePage(
                link=entry,
                link_scores=score(entry),
                # The corpus crawl recorded the page's own <title>; without this it would be
                # re-derived from the link text, which is what a crawl has to fall back on and
                # a store does not.
                title=title or None,
                found_by="corpus",
            )
            # **Best evidence about a page wins, exactly as it does for the crawl below** — this was
            # a `setdefault`, and it cost a live corridor its answer on 2026-08-23.
            #
            # Search and the corpus describe the same URL from different evidence. Search knows only
            # the engine's title; the corpus knows the anchor text and section heading an offline
            # crawl harvested from the page that links to it, and `link_text_weight` is why that is
            # worth far more. Measured on `canada/GB/GB/tourism`:
            # `entry-requirements-country.html` scores **63.4** from the corpus — "Entry
            # requirements by country or territory" under "Check if you need a visa or eTA" — and
            # **32.0** from
            # search's "What you need to enter Canada - Canada.ca". Seeded first, the search
            # candidate could not be displaced, and 32.0 missed the shortlist while 63.4 would have
            # been the second-best `visa_decision` candidate in it. The corridor refused.
            #
            # It was latent until entry 51 because the crawl re-found such pages with their real
            # anchor text and the loop below *does* compare scores, so the crawl was quietly
            # repairing what this line broke.
            existing = candidates.get(entry.url)
            if existing is None or stored.link_scores.best()[1] > existing.link_scores.best()[1]:
                candidates[entry.url] = stored

        # 3. Crawl to pinpoint — only when the corpus has not already out-covered it.
        crawled: list[CandidatePage] = []
        page_titles: dict[str, str] = {}
        if self._crawl_is_worth_running(from_corpus):
            crawler = LinkCrawler(self.crawl_fetcher, score, reject=reject)
            crawled = await crawler.crawl(destination, seeds)
            page_titles = crawler.titles
        else:
            notes.append(
                f"the crawl was skipped: {destination.display_name}'s stored page corpus already "
                f"offers {from_corpus} pages on currently trusted domains, more than a crawl could "
                "visit"
            )

        # Name the domains that could not be read at all. Without this a refusal reads as "nothing
        # scored well enough" when the real cause was an unreachable or client-rendered site, which
        # tells the reader to look in a completely different place.
        # A host's own crawl policy is reported separately, and always. Only the first failure per
        # host survives the loop below, so a `Disallow` folded into it could be masked by an
        # unrelated 404 elsewhere on the same site — and "we chose not to ask" is precisely the
        # fact that must never go missing, because it is the one a reader cannot infer from an
        # empty result. See DECISIONS entry 36.
        disallowed = self.crawl_fetcher.disallowed_urls()
        unreadable: dict[str, str] = {}
        for url, reason in self.crawl_fetcher.failures.items():
            if url in disallowed:
                continue
            unreadable.setdefault(host_of(url), reason)
        for host, reason in sorted(unreadable.items()):
            notes.append(f"{host} could not be read because {reason}")
        # Worded from the reason recorded per URL, never asserted. Written as "publishes a
        # robots.txt that does not permit this client", it claimed a policy nobody had read: China's
        # `avas.mfa.gov.cn` and `cova.mfa.gov.cn` answer `502` to every path including their own
        # policy, and the note called that a refusal. One note per host and distinct reason, so a
        # host with both kinds reports both rather than whichever came first.
        skipped: set[tuple[str, str]] = {
            (host_of(url), self.crawl_fetcher.failures[url]) for url in disallowed
        }
        for host, reason in sorted(skipped):
            notes.append(f"{host}: pages discovery reached were not fetched because {reason}")
        # An authority refusing this client is a different fact from a site being broken, and the
        # difference matters to a reader: one means "we were not allowed to check", not "no
        # guidance exists". Read from the recorded outcome rather than by matching the sentence,
        # so rewording a message cannot silently empty this list.
        # Domains cover every refusal including a rate limit, because reporting must not lose one.
        # The URL list is narrower: only a settled refusal may be handed to a traveller as a page
        # nobody was permitted to read, since a 429 might serve fine next week (entry 32).
        # **With no crawl these are empty, and the shortlist fetch is where refusals are seen** —
        # `_report_retrieval_refusals`, entry 49. Both are merged after the fetch.
        crawl_inaccessible = {host_of(url) for url in self.crawl_fetcher.blocked_urls()}
        crawl_refused = set(self.crawl_fetcher.persistent_refusals())

        for candidate in crawled:
            existing = candidates.get(candidate.link.url)
            if existing is None or candidate.link_scores.best()[1] > existing.link_scores.best()[1]:
                candidates[candidate.link.url] = candidate
        for url, candidate in candidates.items():
            if not candidate.title:
                candidate.title = page_titles.get(url) or candidate.link.text or None

        trace.candidates = candidates
        trace.crawl_failures = dict(self.crawl_fetcher.failures)
        # Only what *this run* found, never what the corpus already held: the caller folds this back
        # in, and a page arriving from the corpus has nothing to add to it.
        self.discovered = [
            candidate.link
            for url, candidate in candidates.items()
            if canonical_key(url) not in held
        ]
        if not candidates:
            trace.refusal_cause = "no_candidates"
            return self._refused(corridor, queries, notes, "no candidate pages were found")

        # 3b. Score whatever the text index already holds, before anything is ranked.
        #
        # **Order is the point.** `score_body` has always existed and has always run at step 5, on
        # pages that were already fetched — after the gate it should be part of. A page the anchor
        # scorer filed under the wrong role was never shortlisted, never fetched, and so never had
        # its text read at all. Measured on Japan: the page that fills `document_checklist` for
        # `japan/IN/GB` scores 22.0 as `visa_decision` from its anchor and is not a candidate for
        # the right role at any shortlist depth. Entry 78.
        scored_from_text = self._score_from_text(destination, corridor, nationality, candidates)
        if scored_from_text:
            notes.append(
                f"{scored_from_text} candidates were ranked on the text of the page as well as the "
                "link to it, from the stored page-text index"
            )

        # 4. Fetch the shortlist through the ordinary retrieval path.
        shortlist = self._shortlist(list(candidates.values()))
        trace.shortlisted = {candidate.link.url for candidate in shortlist}
        fetched = await self._fetch_bodies(destination, shortlist, corridor, nationality)
        trace.fetched = {candidate.link.url for candidate in fetched.candidates}
        # Refusals met while reading the shortlist, folded in beside the crawl's. Both are
        # observations from this run; neither is complete on its own, and with no crawl the fetch
        # is the only one there is.
        # Kept on the trace as well as reported, because the recall log is the only place a refusal
        # can be counted across runs and it had been recording the crawl's alone.
        trace.fetch_failures = list(fetched.failures)
        fetch_inaccessible, fetch_refused = self._report_retrieval_refusals(fetched.failures, notes)
        inaccessible = sorted(crawl_inaccessible | fetch_inaccessible)
        refused = sorted(crawl_refused | fetch_refused)

        # 5. Assign roles from the combined evidence.
        try:
            sources, unresolved, model_calls, tools = await self._decide_roles(
                destination, corridor, fetched, notes
            )
        except AdjudicationRefusal as exc:
            # Refuse rather than fall back to the heuristic. Degrading to the decider that named
            # Brazil's Riyadh page as a document checklist is not the conservative option — see
            # DECISIONS entry 31, which amends entry 16.
            trace.refusal_cause = "adjudication_failed"
            return self._refused(corridor, queries, notes, str(exc), model_calls=exc.attempts)

        # Which refused pages, if any, could have held the decision. Asked only when the decision is
        # actually missing and something was actually refused: `decision_blocking_urls` is read by
        # `is_usable` and `decision_is_unverified`, and both are inert once `visa_decision` is
        # filled. So the ordinary corridor makes no extra call at all. DECISIONS entry 57.
        decision_found = any("visa_decision" in source.roles for source in sources)
        # A tool is what to say when nothing stated the answer. Once a page did, it is at best a
        # second route to something already established, and offering it would tell the traveller to
        # go and work out what the plan already says. Applied per role, so a checklist found on a
        # page suppresses only the checklist tool.
        filled = {role for source in sources for role in source.roles}
        for tool in tools:
            if tool.role in filled:
                notes.append(
                    f"a {tool.role} tool was named at {tool.url} but a page answers it, "
                    "so it was not carried"
                )
        tools = [tool for tool in tools if tool.role not in filled]
        if decision_found or not refused:
            blocking = []
        elif self.adjudicator is None:
            # The deterministic path keeps the keyword test, exactly as `_decide_roles` does. This
            # is a configured mode, not entry 31's forbidden fallback from a failed call.
            blocking = self._decision_blocking(refused, candidates)
        else:
            blocking, blocked_calls = await self._decision_blocking_judged(
                corridor, refused, candidates, notes
            )
            model_calls += blocked_calls

        return ResolvedCorridor(
            corridor=corridor,
            resolved_at=self.now(),
            sources=sources,
            unresolved_roles=unresolved,
            notes=notes,
            inaccessible_domains=inaccessible,
            inaccessible_urls=refused,
            decision_blocking_urls=blocking,
            interactive_tools=tools,
            queries=queries,
            pages_fetched=len(shortlist),
            model_calls=model_calls,
            ran_without_search=not searched_without_error,
        )

    def _text_scoring_is_fair(self, scored: int, candidates: int) -> bool:
        """Whether the index covers enough of *this* candidate set to rank it.

        **A signal only some candidates carry cannot order them against each other**, and measured
        2026-08-26 that is not a theoretical worry — it cost `japan/IN/GB` two roles. The index held
        text for 115 of 860 candidates, spread by whatever hosts the crawl happened to reach: 90% of
        `evisa.mofa.go.jp`, 5% of `www.mofa.go.jp`, and **0% of `www.uk.emb-japan.go.jp`, the post
        that actually serves a traveller applying from Britain.** Every one of the eleven pages the
        lift added to the shortlist had index text; the eleven it displaced included the UK post's
        own fee and checklist pages. Corpus-only, three runs each way: with the lift Japan filled
        four roles every time and never `document_checklist` or `fees`; without it, four to six and
        always both.

        `combined` already refuses to let stored text *lower* a score. That protects the score and
        not the place — a shortlist is finite, so lifting some candidates displaces others, and the
        ones that cannot be lifted are the ones nobody crawled rather than the ones nobody needs.

        The bar is a majority, and it is a statement rather than a tuned number: below half,
        presence in the index predicts rank better than anything the page says, which is ranking by
        crawl coverage. Above it the minority is the exception rather than the rule. It is not a
        threshold to nudge — the fix for a country under it is to cover it ([TODO.md](TODO.md) item
        32), not to lower this.
        """

        return candidates > 0 and scored >= candidates * self.text_scoring_coverage_bar

    def _score_from_text(
        self,
        destination: DestinationConfig,
        corridor: Corridor,
        nationality: Country,
        candidates: dict[str, CandidatePage],
    ) -> int:
        """Attach `text_scores` to every candidate whose page text the index holds.

        Returns how many were scored, for the corridor's notes — a traveller-facing count of how
        much of this ranking rested on reading pages rather than reading links.

        **Every candidate is offered, not a promising subset.** Narrowing first would put the link
        scorer back in front of the text scorer, which is the defect this exists to remove, and the
        same one `MAXIMUM_SCORED_MATCHES` records being made inside `rank` itself.
        """

        if self.page_text is None:
            return 0
        code = self._destination_code(destination)
        if code is None:
            return 0
        scored = self.page_text.score_held(
            code,
            candidates.keys(),
            corridor=corridor,
            nationality=nationality,
            lexicon=self.lexicon,
        )
        if not self._text_scoring_is_fair(len(scored), len(candidates)):
            return 0
        for url, scores in scored.items():
            candidate = candidates.get(url)
            if candidate is not None:
                candidate.text_scores = scores
        return len(scored)

    def _corpus_links(self, destination: DestinationConfig) -> list[tuple[PageLink, str]]:
        """The country's known pages and their titles, filtered by the domains trusted *now*.

        Read-time filtering is the point: a corpus outlives the registry row that produced it, so a
        domain a person later removes stops being offered without anyone rebuilding every corpus,
        and without deleting what was found.

        The title comes along because it is a thing the store knows and a crawl has to fetch a page
        to learn. Without it a corpus-sourced candidate falls back to its link text, which is the
        crawl's fallback rather than the store's.
        """

        if self.corpus is None:
            return []
        return [
            (entry.to_link(), entry.title)
            for entry in self.corpus.entries_within(destination.trusted_domains)
        ]

    def _crawl_is_worth_running(self, from_corpus: int) -> bool:
        """Whether walking the site adds anything the corpus has not already got.

        **Measured, and the answer for a built country is no** (DECISIONS entry 48): of the 25 pages
        that reached one Canada corridor's shortlist, 14 came from the crawl and **all 14 were
        already in the corpus**. The crawl contributed no unique shortlisted page while spending 62%
        of a 54-second corridor re-deriving a link graph the offline job had already mapped.

        The bound is derived rather than calibrated, which is why it is this and not a tuned number.
        A crawl visits at most `LinkCrawler.maximum_pages` pages — 40 — so a corpus already offering
        more candidate pages than that, on domains trusted right now, cannot be out-covered by one.
        Below it the corpus is not a map and the crawl is still the best thing available, which is
        the conditional entry 48 requires: **a country nobody has built must behave exactly as it
        does today.**

        What this deliberately does *not* claim is that the corpus is a superset. It is not
        (entry 47), which is why search still runs and why the write-back still folds what a live
        run found back in.
        """

        return from_corpus <= DEFAULT_CRAWL_PAGES

    def _report_retrieval_refusals(
        self, failures: list[SourceFailure], notes: list[str]
    ) -> tuple[set[str], set[str]]:
        """Report what reading the shortlist found out, in the shapes the crawl already reports in.

        Returns the hosts that refused this client and the URLs whose refusal was **settled**, so
        the caller can merge them with the crawl's. The notes are appended here because they read
        the same as the crawl's and a reader should not be able to tell which stage saw a refusal —
        only that one was seen.

        **This is the constraint DECISIONS entry 48 names, and it was already half-broken.**
        `_fetch_bodies` discarded `report.failures` entirely, so a page refused at retrieval time
        contributed nothing to `inaccessible_domains`, `inaccessible_urls` or the notes. The crawl
        covered for it by meeting the same refusals first. Remove the crawl and the cover goes with
        it, so this has to exist before that can happen.

        Every failure is noted, not only refusals. A shortlisted page that could not be read at all
        is the difference between "nothing scored well enough" and "the site would not give us the
        page", and that is precisely what a reader cannot infer from an empty result.

        `outcome` and `http_status` are read; `detail` is only ever repeated. Deciding from the
        sentence is what entry 36 forbids, because rewording a message would then silently empty a
        list something depends on.
        """

        blocked_hosts: set[str] = set()
        settled: set[str] = set()
        seen: set[tuple[str, str]] = set()
        for failure in sorted(failures, key=lambda item: str(item.attempted_url)):
            url = str(failure.attempted_url)
            host = host_of(url)
            if failure.outcome == "blocked":
                blocked_hosts.add(host)
                # Only a settled refusal may be handed to a traveller as a page nobody was
                # permitted to read. A `429` might serve fine next week, and a refusal recorded
                # with no status is excluded, which fails toward *not* claiming we were blocked.
                # DECISIONS entry 32, the same rule `CrawlFetcher.persistent_refusals` applies.
                if failure.http_status in PERSISTENT_REFUSAL_STATUS_CODES:
                    settled.add(url)
            if (host, failure.detail) in seen:
                continue
            seen.add((host, failure.detail))
            if failure.outcome == "disallowed":
                note = f"{host}: pages discovery reached were not fetched because {failure.detail}"
            else:
                note = f"{host} could not be read because {failure.detail}"
            if note not in notes:
                notes.append(note)
        return blocked_hosts, settled

    def _decision_blocking(
        self, refused: list[str], candidates: dict[str, CandidatePage]
    ) -> list[str]:
        """Which refusals plausibly cost us the visa decision, rather than merely happening.

        A block only licenses saying the decision could not be verified if the page that refused
        could have answered the question. Otherwise the exception in `ResolvedCorridor.is_usable`
        stops being narrow: a `403` on a legal notice would resolve a corridor whose decision was
        simply never found, and WAF refusals on incidental pages are ordinary at scale.

        Credibility is read from the score the page already earned for `visa_decision` as a link.
        Anything above zero counts, and that is deliberately a low bar rather than a tuned one: the
        scorer has already **vetoed** site furniture, archived paths and wrong-audience pages
        outright, so a positive score means real visa-decision signal was seen rather than that a
        threshold was cleared. Nothing here is a judgement about what the page *says* — nobody read
        it, and nobody may.

        **Known limit, and it fails toward refusing.** Only pages the pipeline scored can be judged,
        and the crawl discards a page it could not fetch, so a refusal met for the first time at
        crawl depth is not in `candidates` and cannot qualify. In practice an authority's own visa
        portal is what search returns first — `france-visas.gouv.fr` is exactly that — so the case
        this exists for is covered. A corridor losing its answer this way refuses, which is the safe
        direction and the one this project prefers.
        """

        blocking: list[str] = []
        for url in refused:
            candidate = candidates.get(url)
            if candidate is not None and candidate.link_scores.score_for("visa_decision") > 0:
                blocking.append(url)
        return blocking

    async def _decision_blocking_judged(
        self,
        corridor: Corridor,
        refused: list[str],
        candidates: dict[str, CandidatePage],
        notes: list[str],
    ) -> tuple[list[str], int]:
        """Ask which refused pages could have held the decision, instead of keyword-matching them.

        The one place the heuristic was deciding what a page *means* rather than whether it was
        worth reading — and it was doing it on a page **nobody read**. DECISIONS entry 57; entry 56
        is what it cost, when Sweden's country list scored `visa_decision` 0.0 and an authority
        refusing the decision page could not make the decision unverifiable.

        **Fails closed.** Two attempts, then an empty list, which refuses the corridor exactly as
        nothing qualifying would. A model outage can never *create* a blocked-authority plan; it can
        only cost one, which is why it retries at all (entry 31's reasoning).
        """

        judged = {
            source_id: candidates[url]
            for source_id, url in (
                (build_source_id(corridor.destination_slug, url, set()), url)
                for url in sorted(refused)[:MAXIMUM_BLOCKED_JUDGED]
            )
            if url in candidates
        }
        if not judged or self.adjudicator is None:
            return [], 0

        by_id = {source_id: candidate.link.url for source_id, candidate in judged.items()}
        packet = build_blocked_packet(corridor, judged)
        prompt = load_blocked_prompt()
        calls = 0
        for attempt in range(1, ADJUDICATION_ATTEMPTS + 1):
            calls += 1
            try:
                adjudication = await self.adjudicator.adjudicate(prompt, packet)
            except AdjudicationError as exc:
                if attempt < ADJUDICATION_ATTEMPTS:
                    notes.append(f"judging the refused pages failed ({exc}); retrying once")
                    continue
                # Not a fallback to the heuristic: this reports nothing rather than substituting a
                # decider whose keyword answer is the one entry 57 removed.
                notes.append(
                    f"the refused pages could not be judged after {ADJUDICATION_ATTEMPTS} "
                    "attempts, so none is treated as having held the visa decision"
                )
                return [], calls
            kept, discarded = validated_blocked_choices(adjudication, judged)
            for reason in discarded:
                notes.append(reason)
            return sorted(by_id[source_id] for source_id in kept), calls
        return [], calls

    def _mission_domains(self, destination: DestinationConfig, residence: object) -> list[str]:
        """Hosts that look like the post serving the traveller's residence.

        Missions sit on a per-country label of the umbrella domain, so a UK applicant is served by
        uk.emb-japan.go.jp. The label rarely matches the ISO code, which is why it comes from data.
        """

        labels = getattr(residence, "host_labels", [])
        found: list[str] = []
        for configured in destination.sources:
            host = host_of(str(configured.url))
            # Drop a leading "www." before reading the country label, or every host looks like
            # "www" and the mission is never recognised.
            bare = host[4:] if host.startswith("www.") else host
            first = bare.split(".")[0]
            if first and any(first == label for label in labels):
                found.append(bare)
        return found

    def _destination_code(self, destination: DestinationConfig) -> str | None:
        country = next(
            (
                country
                for country in self.countries.countries
                if country.name.lower() == destination.display_name.lower()
            ),
            None,
        )
        return country.code if country else None

    def _shortlist(self, candidates: list[CandidatePage]) -> list[CandidatePage]:
        """The best few candidates per role, so only a handful of pages are ever fetched.

        Per-role first, so no role is crowded out by another's strong results, then the budget is
        filled with the next best overall. Filling it matters: taking three per role left four of
        Vietnam's ten places empty while every readable `evisa.gov.vn` page sat just outside the
        per-role cut, so the site that needed rendering most was never read.

        Then each domain's own best page is reserved a place, because the places are what decide
        what is read at all: an authority whose pages all fall below another's is never fetched, so
        it can never fill a role, so the corridor refuses with the answer sitting one place outside
        the cut. That is how a United States corridor refused while the mission serving the
        traveller went unread and eight federal domains competed for ten places.

        Pages the crawl already proved unreadable are dropped before any of that. A place spent on
        one buys nothing, and the United States was spending half of them that way.

        **Pinned pages take their places first, before any of the ranking runs.** A page that has
        already filled a role for *this* corridor should never have to win the ranking again — and
        it would increasingly have to, because seeding from the corpus grows the pool a great deal
        (Canada: 471 crawled candidates against roughly 3,000 held). Entry 40's asymmetry says a
        page ranked out is unrecoverable, so a larger pool means more pages lost to it. Pinning
        keeps the corpus from making the scorer *more* load-bearing rather than less.
        """

        candidates = self._readable_only(candidates)
        chosen: dict[str, CandidatePage] = {}
        pinned_urls: set[str] = set()
        if self.pinned:
            wanted = {canonical_key(url) for url in self.pinned}
            for candidate in candidates:
                if canonical_key(candidate.link.url) in wanted:
                    chosen.setdefault(candidate.link.url, candidate)
                    pinned_urls.add(candidate.link.url)
        for role in ROLE_ORDER:
            for candidate, _ in rank_for_role(candidates, role)[: self.shortlist_role_depth]:
                chosen.setdefault(candidate.link.url, candidate)

        by_score = sorted(candidates, key=lambda c: (-c.best_combined()[1], c.link.url))
        for candidate in by_score:
            if len(chosen) >= self.shortlist_size:
                break
            # Only pages that scored for something. A candidate no role wants is not worth a fetch.
            if candidate.best_combined()[1] > 0:
                chosen.setdefault(candidate.link.url, candidate)

        # Reserved from every candidate rather than from those already chosen: a domain's best page
        # can be fourth for its role, which is exactly where the per-role cut leaves it.
        reserved = self._reserved_per_domain(by_score)
        for candidate in reserved:
            chosen.setdefault(candidate.link.url, candidate)

        ordered = sorted(chosen.values(), key=lambda c: (-c.best_combined()[1], c.link.url))
        if len(ordered) <= self.shortlist_size:
            return ordered

        # The truncation is where crowding out happens, so this is where both protections have to be
        # honoured. Anything held back earlier would simply be cut here instead.
        #
        # **Pins go first, and until 2026-08-23 they were not honoured here at all.** Entry 47 says
        # a page that already filled a role for this corridor "keeps its shortlist place regardless
        # of ranking", and it kept it only as far as `chosen`: `ordered` sorts by score and the tail
        # was cut without consulting `pinned_urls`, so a low-scoring pin was dropped — exactly
        # the pin that matters, since a high-scoring one never needed pinning. Measured on Canada,
        # `cbsa-asfc.gc.ca/travel-voyage/td-dv-eng.html` is `proven`, scores **0.0** on role
        # vocabulary, and was cut here with the pin naming it.
        reserved_urls = {candidate.link.url for candidate in reserved}
        # Pinned before reserved, and score order preserved inside each group because the sort is
        # stable: if the two protections together overflow the budget, a page that has answered this
        # corridor outranks a domain that merely has not been read yet.
        kept = sorted(
            (
                candidate
                for candidate in ordered
                if candidate.link.url in pinned_urls or candidate.link.url in reserved_urls
            ),
            key=lambda c: c.link.url not in pinned_urls,
        )
        del kept[self.shortlist_size :]
        held = {candidate.link.url for candidate in kept}
        for candidate in ordered:
            if len(kept) >= self.shortlist_size:
                break
            if candidate.link.url not in held:
                kept.append(candidate)
        return sorted(kept, key=lambda c: (-c.best_combined()[1], c.link.url))

    def _readable_only(self, candidates: list[CandidatePage]) -> list[CandidatePage]:
        """Drop candidates the crawl already found it could not read.

        Only two kinds are dropped, and only because each is a fact already established rather than
        a guess about what a fetch would do:

        * a host whose **name does not resolve** — no path under it can be read;
        * a URL an authority **refused this client** — asking again is a retry, which is exactly
          what must not be done, and it would answer the same way.

        Everything else stays. A page that was too large, was not HTML, or answered `502` is left in
        on purpose: retrieval is not the crawler. It reads PDFs, renders, and carries different
        limits, so a page the crawl could not use may still be readable evidence — and dropping
        those would trade a real answer for a tidier count.

        **With no crawl this does nothing, and the corpus's own `status` deliberately does not stand
        in for it** — which is what [TODO.md](TODO.md) item 22 proposed. Two reasons, and the second
        is the one that matters. First, there is nothing to stand in with: `corpus_build` writes
        `unreadable` or `unknown` and never `readable`, so Canada's 3,216 entries hold five
        unreadable and no readable ones. Second, this is a *fetch-budget* optimisation whose input
        today is an observation from **this run**. A stored refusal is an observation from another
        day, and skipping a page on one means the refusal is never seen live — so it can never reach
        `decision_blocking_urls`, and a France-shaped corridor, whose only settled `403` is on the
        page holding the decision, would stop resolving altogether (entries 27 and 32). The cost of
        not skipping is at most a few of twenty-five fetch places, on a step measured at 1.1s.
        """

        blocked = self.crawl_fetcher.blocked_urls()
        unresolvable = self.crawl_fetcher.unresolvable_hosts
        return [
            candidate
            for candidate in candidates
            if candidate.link.url not in blocked and host_of(candidate.link.url) not in unresolvable
        ]

    def _reserved_per_domain(self, by_score: list[CandidatePage]) -> list[CandidatePage]:
        """Each trusted domain's best-scoring pages, up to the floor.

        Keyed on the registrable domain rather than the host, which is the unit trust is granted in.
        A mission network gives every post its own subdomain, so a per-host floor would let one
        authority reserve every place and recreate the crowding this exists to prevent. That is a
        deliberate difference from the crawl's per-host budget, which is about not hammering one
        site rather than about one site starving another.

        A page no role scored for is still not worth fetching, so the floor cannot admit one.
        """

        reserved: list[CandidatePage] = []
        per_domain: dict[str, int] = {}
        for candidate in by_score:
            if candidate.best_combined()[1] <= 0:
                continue
            domain = registrable_domain(host_of(candidate.link.url))
            if per_domain.get(domain, 0) >= self.shortlist_domain_floor:
                continue
            per_domain[domain] = per_domain.get(domain, 0) + 1
            reserved.append(candidate)
        return reserved

    async def _fetch_bodies(
        self,
        destination: DestinationConfig,
        shortlist: list[CandidatePage],
        corridor: Corridor,
        nationality: object,
    ) -> "FetchedShortlist":
        """Read each shortlisted page and score its own text.

        The throwaway config is the point: building it re-runs `validate_route`, so a candidate
        that somehow left the approved domains cannot even be constructed, let alone requested.
        """

        shortlist = [
            candidate
            for candidate in shortlist
            if host_is_within(host_of(candidate.link.url), destination.trusted_domains)
        ]
        if not shortlist:
            return FetchedShortlist()

        taken: set[str] = set()
        probe_sources: list[ConfiguredSource] = []
        by_id: dict[str, CandidatePage] = {}
        for candidate in shortlist:
            source_id = build_source_id(destination.slug, candidate.link.url, taken)
            authority, kind = derive_authority(candidate.link.url, destination)
            by_id[source_id] = candidate
            probe_sources.append(
                ConfiguredSource.model_validate(
                    {
                        "source_id": source_id,
                        "title": clean_title(candidate.title, candidate.link.url),
                        "url": candidate.link.url,
                        "authority": authority,
                        "kind": kind,
                        "research_pass": "primary",
                    }
                )
            )

        payload = destination.model_dump(mode="json")
        payload["sources"] = [source.model_dump(mode="json") for source in probe_sources]
        payload["application_document_source_ids"] = []
        payload["required_source_ids"] = []
        # An appointed provider is authorised by a named official page. Those pages are not in this
        # throwaway config, so the authorisation does not hold here and the provider is dropped
        # rather than assumed. Candidates were already restricted to trusted domains above.
        payload["appointed_providers"] = []
        probe = DestinationConfig.model_validate(payload)

        report = await self.live_fetcher.fetch(probe)
        contents: dict[str, str] = {}
        for item in report.fetched:
            contents[item.source.source_id] = item.content
            fetched_candidate = by_id.get(item.source.source_id)
            if fetched_candidate is None:
                continue
            fetched_candidate.body_scores = score_body(
                item.content,
                item.source.title,
                corridor,
                self.lexicon,
                self.countries.require(corridor.passport_nationality),
                url=fetched_candidate.link.url,
            )
            fetched_candidate.content_hash = item.content_hash
        # Only pages that were actually readable can be proposed.
        readable = [source_id for source_id in contents if source_id in by_id]
        return FetchedShortlist(
            candidates=[by_id[source_id] for source_id in readable],
            by_id={source_id: by_id[source_id] for source_id in readable},
            contents=contents,
            failures=list(report.failures),
        )

    async def _decide_roles(
        self,
        destination: DestinationConfig,
        corridor: Corridor,
        fetched: "FetchedShortlist",
        notes: list[str],
    ) -> tuple[list[ResolvedSource], list[DiscoveryRole], int, list[ResolvedTool]]:
        """Choose the page for each role, by judgement when an adjudicator is configured.

        The fourth return is the interactive tools the model read and judged to hold a role's
        answer behind their questions. They are **only** ever produced here, on the path where the
        model was handed page text — the heuristic never produces one, because "is this page a
        questionnaire" is a question about meaning, and entry 57 is what keyword-matching meaning
        cost the last time. No adjudicator therefore means no tool, which is the deterministic
        baseline behaving exactly as it did before.

        The heuristic is not replaced. It produced the shortlist these candidates come from, and it
        is the answer when no adjudicator is configured — which keeps the deterministic path as the
        offline regression baseline.

        **What it is no longer is the fallback when a model call fails.** That read as the
        conservative choice and was the opposite: the heuristic is the decider entry 15 caught
        giving *confident wrong answers* — Brazil's Riyadh page named as the document checklist, at
        exit 0, with nothing in the output hinting the checklist came from a mission on another
        continent. So falling back turned a transient outage into exactly that, in production,
        visible only to someone who read `decided_by`. The call is retried once and then the
        corridor is refused, which every other layer of this project would do. Retrying is safe
        here because a model provider is not an authority refusing us — entry 18 does not apply.
        See entry 31.
        """

        if self.adjudicator is None or not fetched.candidates:
            sources, unresolved = self._assign_roles(destination, fetched.candidates, notes)
            return sources, unresolved, 0, []

        # The traveller's own country words, so a long page is cut around them rather than at a
        # fixed offset. Nationality and residence only: the destination is named on every page it
        # publishes, so anchoring on it would anchor on nothing.
        nationality, residence = resolve_corridor_countries(corridor, self.countries)
        packet = build_candidate_packet(
            corridor,
            fetched.by_id,
            fetched.contents,
            excerpt_characters=self.excerpt_characters,
            excerpt_head_characters=self.excerpt_head_characters,
            excerpt_window_characters=self.excerpt_window_characters,
            anchor_terms=sorted({*nationality.text_tokens, *residence.text_tokens}),
        )
        adjudication, model_calls = await self._adjudicate_with_one_retry(packet, notes)

        chosen, discarded = validated_choices(adjudication, fetched.by_id)
        notes.extend(discarded)
        named, tool_discarded = validated_tools(adjudication, fetched.by_id)
        notes.extend(tool_discarded)
        sources, unresolved = self._sources_from_choices(destination, fetched, chosen, notes)
        tools: list[ResolvedTool] = []
        for role in ROLE_ORDER:
            tool = named.get(role)
            if tool is None or role == "irrelevant":
                continue
            source_id, reason = tool
            url = fetched.by_id[source_id].link.url
            tools.append(ResolvedTool(role=role, url=url))
            notes.append(f"{url} answers {role} interactively: {reason}")
        return sources, unresolved, model_calls, tools

    async def _adjudicate_with_one_retry(
        self, packet: str, notes: list[str]
    ) -> tuple[RoleAdjudication, int]:
        """One retry, then let the failure through so the corridor refuses.

        A single retry, not a policy: the failures worth surviving are momentary ones — a timeout,
        a rate limit, one malformed response — and if the second attempt fails too, refusing is the
        honest answer rather than reaching for a decider known to be wrong with confidence. The
        attempt count is returned either way, because a refusal that cost two calls still cost
        them.

        **An empty account is not a momentary failure and is not retried.** The sentence above says
        what a retry is for, and "the account has no credit" is the one cause that fails that test
        outright: the second call cannot succeed, and it is billed the same as the first. This is
        entry 74's point about a `402` reaching the place where the retry decision is made — the
        classification is worth nothing if every caller retries anyway.
        """

        attempts = 0
        last: AdjudicationError | None = None
        while attempts < ADJUDICATION_ATTEMPTS:
            attempts += 1
            try:
                return await self.adjudicator.adjudicate(  # type: ignore[union-attr]
                    load_adjudication_prompt(), packet
                ), attempts
            except AdjudicationQuotaExhausted as exc:
                raise AdjudicationRefusal(attempts, str(exc)) from exc
            except AdjudicationError as exc:
                last = exc
                if attempts < ADJUDICATION_ATTEMPTS:
                    notes.append(f"role adjudication failed ({exc}); retrying once")
        raise AdjudicationRefusal(attempts, str(last))

    def _sources_from_choices(
        self,
        destination: DestinationConfig,
        fetched: "FetchedShortlist",
        chosen: dict[DiscoveryRole, tuple[str, str]],
        notes: list[str],
    ) -> tuple[list[ResolvedSource], list[DiscoveryRole]]:
        """Turn validated model choices into sources, honouring every refusal."""

        by_url: dict[str, tuple[CandidatePage, list[DiscoveryRole], list[str]]] = {}
        unresolved: list[DiscoveryRole] = []

        for role in ROLE_ORDER:
            decision = chosen.get(role)
            if decision is None:
                if role in REPORTED_ROLES:
                    unresolved.append(role)
                    notes.append(f"no candidate was judged to be the {role.replace('_', ' ')}")
                continue
            source_id, reason = decision
            candidate = fetched.by_id[source_id]
            url = candidate.link.url
            if url in by_url:
                _, roles, reasons = by_url[url]
                roles.append(role)
                reasons.append(f"{role}: {reason}")
            else:
                by_url[url] = (candidate, [role], [f"{role}: {reason}"])

        taken: set[str] = set()
        sources: list[ResolvedSource] = []
        for candidate, roles, reasons in sorted(
            by_url.values(), key=lambda item: (ROLE_ORDER.index(item[1][0]), item[0].link.url)
        ):
            authority, kind = derive_authority(candidate.link.url, destination)
            sources.append(
                ResolvedSource(
                    source_id=build_source_id(destination.slug, candidate.link.url, taken),
                    title=clean_title(candidate.title, candidate.link.url),
                    url=candidate.link.url,  # type: ignore[arg-type]
                    authority=authority,
                    kind=kind,
                    roles=roles,
                    # The heuristic score is still recorded, so a reviewer can see where the two
                    # deciders disagreed rather than only what the model concluded.
                    score=round(max(candidate.combined(role) for role in roles), 1),
                    decided_by="model",
                    signals=_with_published_date(
                        candidate.link.url, [reason[:160] for reason in reasons][:6]
                    ),
                )
            )
        return sources, unresolved

    def _assign_roles(
        self,
        destination: DestinationConfig,
        candidates: list[CandidatePage],
        notes: list[str],
    ) -> tuple[list[ResolvedSource], list[DiscoveryRole]]:
        """Pick the best page for each role independently.

        Roles are not exclusive. One page can be both the page that says a visa is needed and the
        page listing the documents, which is exactly how Singapore's per-nationality page is
        configured by hand, so forcing one role per page loses the right answer.
        """

        best_by_url: dict[str, tuple[CandidatePage, list[DiscoveryRole], float]] = {}
        unresolved: list[DiscoveryRole] = []

        for role in ROLE_ORDER:
            ranked = [
                (candidate, score)
                for candidate, score in rank_for_role(candidates, role)
                if score >= self.minimum_role_score
            ]
            if not ranked:
                # Reported, not only load-bearing: a missing checklist no longer refuses the
                # corridor, but leaving it unsaid would hide it from whoever reviews the result.
                if role in REPORTED_ROLES:
                    unresolved.append(role)
                    notes.append(f"no page scored high enough to be the {role.replace('_', ' ')}")
                continue

            candidate, score = ranked[0]
            url = candidate.link.url
            if url in best_by_url:
                existing_candidate, roles, best_score = best_by_url[url]
                roles.append(role)
                best_by_url[url] = (existing_candidate, roles, max(best_score, score))
            else:
                best_by_url[url] = (candidate, [role], score)

        taken: set[str] = set()
        sources: list[ResolvedSource] = []
        # Order by the most important role each page fills, so proposals read top-down.
        for candidate, roles, score in sorted(
            best_by_url.values(), key=lambda item: (ROLE_ORDER.index(item[1][0]), item[0].link.url)
        ):
            authority, kind = derive_authority(candidate.link.url, destination)
            signals: list[str] = []
            for role in roles:
                signals.extend(candidate.link_scores.signals.get(role, []))
            sources.append(
                ResolvedSource(
                    source_id=build_source_id(destination.slug, candidate.link.url, taken),
                    title=clean_title(candidate.title, candidate.link.url),
                    url=candidate.link.url,  # type: ignore[arg-type]
                    authority=authority,
                    kind=kind,
                    roles=roles,
                    score=round(score, 1),
                    decided_by="heuristic",
                    signals=list(dict.fromkeys(signals))[:6],
                )
            )
        return sources, unresolved

    def _write_recall_log(
        self,
        corridor: Corridor,
        trace: "ResolutionTrace",
        resolved: ResolvedCorridor | None,
    ) -> None:
        """Write the run down, and never let doing so cost the corridor an answer.

        An `OSError` here is swallowed deliberately: this is a diagnostic nothing reads back, so
        failing a resolution because a log file could not be written would trade an answer for a
        note about an answer. The failure is not silent in practice — the file is simply not there
        when someone goes looking, which is exactly what happened.
        """

        if self.recall_log is None:
            return
        outcome = "resolved"
        if resolved is None:
            outcome = "the run raised before it finished"
        elif not resolved.sources:
            outcome = resolved.notes[-1] if resolved.notes else "refused"
        elif resolved.unresolved_roles:
            unfilled = ", ".join(resolved.unresolved_roles)
            outcome = f"resolved, with no {unfilled}"
        # The sentence above and the value below say the same thing to different readers, and only
        # one of them can be counted. Where a refusal recorded its own cause that wins, because the
        # result cannot show it; everything else is derived from the result so the two cannot drift.
        cause: RefusalCause = "run_raised"
        if resolved is not None:
            cause = trace.refusal_cause or resolved.outcome_cause
        # Both stages, and the crawl's first so a page the fetch also met keeps the earlier reason.
        unreadable = dict(trace.crawl_failures)
        outcomes: dict[str, FailureOutcome] = {}
        for failure in trace.fetch_failures:
            url = str(failure.attempted_url)
            unreadable.setdefault(url, failure.detail)
            outcomes[url] = failure.outcome
        try:
            self.recall_log.write(
                RecallRecord(
                    corridor_key=corridor.key,
                    recorded_at=self.now(),
                    outcome=outcome,
                    cause=cause,
                    unresolved_roles=list(resolved.unresolved_roles) if resolved else [],
                    queries=trace.queries,
                    seeds=trace.seeds,
                    candidates=considered(
                        trace.candidates,
                        shortlisted=trace.shortlisted,
                        fetched=trace.fetched,
                    ),
                    unreadable=unreadable,
                    unreadable_outcomes=outcomes,
                )
            )
        except OSError:
            return

    def _refused(
        self,
        corridor: Corridor,
        queries: list[str],
        notes: list[str],
        reason: str,
        *,
        model_calls: int = 0,
    ) -> ResolvedCorridor:
        """A corridor that produced no sources, with why, and what it cost getting there.

        `model_calls` is reported even though nothing was resolved: a refusal after two failed calls
        still spent money, and a cost that only appears on success is a cost nobody notices.
        """

        return ResolvedCorridor(
            corridor=corridor,
            resolved_at=self.now(),
            sources=[],
            unresolved_roles=list(REPORTED_ROLES),
            notes=[*notes, reason],
            queries=queries,
            model_calls=model_calls,
        )
