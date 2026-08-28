"""Building a country's page corpus offline, with no traveller and no latency budget.

DECISIONS entry 44. The request path crawls under a stopwatch: forty pages, two hops, and a seed
frontier that in practice spends the whole allowance at depth 0. That is a compromise a sixty-second
request forces, not a judgement about how deep the answers are — Canada's answering page sits at
depth 1, and the ones still being lost are deeper. This job has no such bound, and that is the whole
of why it is expected to beat the request path rather than merely cache it.

Three things it does differently from `resolver.py`, each deliberate.

**No traveller.** Queries name the destination and nothing else, and links are scored with
`score_role_vocabulary` — the corridor-independent half. A corpus guided by one nationality's
vocabulary would be a corpus quietly built for that nationality.

**It keeps pages about other countries.** `resolver.py` vetoes those, correctly: for one corridor a
page about Brazil is noise. For a *corpus* it is the opposite — Canada's per-nationality pages are
exactly what a later India or Nigeria corridor needs, and vetoing them here would build a store that
can only answer the corridors nobody has a page for. Archived paths and site furniture are still
rejected, because those are not guidance for anybody.

**It never deletes.** The merge in `corpus.py` is additive; this job only ever hands it what it
found. A crawl that finds less than last time is ordinary, and treating that as a withdrawal would
rebuild the exact failure the corpus exists to prevent.
"""

import re
from collections import Counter
from collections.abc import Callable
from datetime import datetime
from typing import get_args

import httpx
from pydantic import Field

from visa_research_agent.config.loader import get_service_providers
from visa_research_agent.discovery.corpus import CorpusEntry, CountryCorpus, merge
from visa_research_agent.discovery.crawl import (
    DEFAULT_KEPT_TEXT_CHARACTERS,
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
from visa_research_agent.discovery.models import CandidatePage, PageLink, RoleScores
from visa_research_agent.discovery.page_text import PageTextStore, StoredPage
from visa_research_agent.discovery.scoring import is_archived, is_boilerplate, score_role_vocabulary
from visa_research_agent.discovery.search import SearchProvider, search_all, usable_results
from visa_research_agent.discovery.urls import canonicalise_url, is_crawlable, is_pdf_url
from visa_research_agent.domain.models import (
    DestinationConfig,
    FailureOutcome,
    ServiceProviderRegistry,
    StrictModel,
    TravelPurpose,
)
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.tls import build_ssl_context

# Far above the request path's forty, and **it has to exceed the seed count or the crawl never
# crawls**. Measured 2026-08-22: Canada produced 203 seeds against a 200-page budget, so the whole
# allowance went on fetching seeds — 1,032 of 1,071 entries sat at depth 1 and only 39 deeper. The
# offline job's entire advantage over the request path is that it can go deeper, and at 200 it was
# not going anywhere. `depth_is_exercised` below exists so that failure is visible rather than
# inferred from a distribution nobody prints.
DEFAULT_CORPUS_PAGES = 1_200
# Three hops rather than two. Japan's checklist was found at depth 2 and the request path cannot
# reliably reach it; anything the corpus is *for* lives at least that far in.
DEFAULT_CORPUS_DEPTH = 3
# Per host, so one large ministry portal cannot spend the whole allowance before a mission site is
# reached. Same reasoning as the crawl's own budget, with more room.
DEFAULT_CORPUS_PAGES_PER_HOST = 400
# Below this share of pages beyond depth 1, the crawl did not really crawl: it fetched its seeds and
# stopped. Not a failure — the entries are still real — but it must be reported, because a build
# that quietly behaves like the request path has not done the thing it exists to do.
MINIMUM_DEEP_SHARE = 0.10
# The request path follows a link only when its anchor scores at least 10, because a sixty-second
# corridor cannot afford to read a page that probably says nothing. **This job has no such bound and
# the threshold was costing it most of the country.** Measured on Japan 2026-08-26: 2,834 of 3,103
# corpus entries — 91% — score below 10 from their anchor, so they were discovered and never read,
# and their text could never enter the index. The gate that decides what gets *read* was the same
# anchor scorer that cannot read, which is the defect one level up from the one the index fixes.
#
# Zero rather than a smaller number: the page budget and the per-host budget already bound the
# crawl, and the frontier is best-first, so the high-scoring links are still fetched *first*. This
# only decides what fills the remaining budget — noise, or nothing at all.
CORPUS_EXPANSION_THRESHOLD = 0.0
# PDFs are never followed by a crawl — `_expand` will not queue one, correctly, because a PDF holds
# no links worth walking. But authorities publish checklists as PDFs, which is what the lexicon's
# `pdf_checklist_bonus` exists for, and 26% of Japan's corpus is PDFs. So they are read in a second
# pass, for their text only, best-scoring first.
DEFAULT_CORPUS_PDFS = 400

# How many pages an offline build may render, against the request path's twelve.
#
# **The renderer was always passed to this job; the budget was the bug** (entry 92). Measured on the
# France corpus of 2026-08-28: 64 pages on `france-visas.gouv.fr` answered a Cloudflare challenge,
# twelve renders were available to answer them, and the rest were recorded "that challenge could not
# be answered here" — a sentence that is true of this crawl and false of the authority. France came
# out of that build with **18 readable candidates of 201**, the worst text coverage in the selection
# fixture, and the item that queued this work said the build did not render at all. It does.
#
# Entry 41 is what makes raising it legitimate rather than a relaxation: a challenge states no
# policy, so answering one by running the page's own scripts **under our own user agent** deceives
# nobody. A refusal is still a refusal — a bare `403`, a `401`, a `429` — and is never rendered
# past.
#
# Bounded on two sides, because the cost is time rather than quota: this ceiling, and
# `CHALLENGE_FAILURES_PER_HOST`, which stops a host we genuinely cannot answer from spending the
# whole budget proving it. A corridor keeps twelve because a traveller is waiting for it.
DEFAULT_CORPUS_RENDERS = 400
# **Zero, which means the even split stays — the mechanism below is built, tested and off.**
#
# Item 32 said the United Kingdom's fee tables stopped at 15 of ~198 nationalities because an even
# per-host share starved the host holding them, where Canada's equivalent `?country=XX` pages
# reached 213 on the same code. `HostBudget` was built to fix exactly that, and a rebuild at
# `--pages 3000` disproved the premise: `visa-fees.homeoffice.gov.uk` went **91 pages to 113, and
# 15 nationalities to 20**. It was never budget-limited.
#
# What it is limited by, measured: **zero** of its 86 pages were reached from a *different*
# nationality's page. The country selector is a form, so the space has no links to walk and a crawl
# only ever holds the nationalities search happened to seed. Canada's 425 pages came from a page
# that lists every country as a link — the difference is what the authority published, not what the
# crawler was allowed to spend. That is entry 59's wall, one layer down.
#
# And removing the cap cost something: the surplus goes to whichever host offers the most links,
# which for the United Kingdom is `www.gov.uk` — the whole government website. Its corpus went 922
# entries to 4,530 with **4,252 of them on gov.uk**, most about anything but visas.
#
# Raise this only with a measurement behind it. The floor half is the part worth revisiting: it
# guarantees a small mission host its pages, which is known problem 24's failure, and it is only
# the surplus half that inflated the corpus.
DEFAULT_CORPUS_HOST_FLOOR = 0

# How much of an offline build may be spent opening per-traveller families — one page published once
# per country, `…/apply-{country}`. It is reserved rather than competed for, because the members
# cannot win a competition: their anchor text is a bare country name, so `score_role_vocabulary`
# gives every one of the Netherlands' 219 the same **8.0** while the index listing them scores 17.6
# and the checklist each one leads to would score 25.0. Entry 78's defect, in a new place.
#
# **This is not entry 82's proposal and must not be read as one.** That closed "raise the total"
# and "split the total unevenly between hosts", and measurement closed both. This changes neither
# the total nor the split: it changes what the budget is spent on, within one host.
#
# Measured before it was built: lifting the family's *score* to its index's 17.6 is not enough,
# because 764 unopened Dutch pages already score above that. Reservation is the only thing that
# reaches them.
#
# **Zero on the request path, and that is not an oversight.** A corridor has one traveller; opening
# 218 other countries' pages is the definition of a wasted fetch. Only this job serves everybody.
DEFAULT_CORPUS_FAMILY_SHARE = 0.4

# Which per-traveller families the share is spent on, matched against the family's shared address.
# A gate is needed because the members cannot be told apart by score — scoring at the floor is the
# defect being fixed — and because the largest country family on several sites is not guidance at
# all. Measured over the ten corpora: Canada's biggest is `travel.gc.ca/destinations/{}` at 176
# members and Japan's are `mofa.go.jp/region/{area}/{}` at 141, and reserving budget for those would
# spend 40% of a build on travel advisories. With this gate, six of the ten countries have no
# qualifying family and the reservation is inert for them, which is the intended outcome.
CORPUS_FAMILY_PATTERN = re.compile(
    r"visa|permit|entry|checklist|consular|appointment|apply|immigrat|fees", re.IGNORECASE
)


def corpus_queries(
    country_name: str, domain: str, *, purpose: TravelPurpose | None = None
) -> list[str]:
    """What to ask about a country's visa pages when you do not know who is travelling.

    No nationality and no residence — those are 198-valued, and putting them here would tilt the
    corpus toward whoever it was built for.

    **Purpose is different, and treating it like the others cost the corpus a real page.** Measured
    2026-08-22: `.../visit-canada/supporting-documents` was fetched by a live corridor run and was
    absent from a 1,071-entry corpus. It had entered the corridor run as a search seed from
    `site:canada.ca tourism visa documents required` — `corridor_queries`' purpose template. The
    corpus asked `visa application documents required`, with no purpose word, and never saw it.

    So purpose is swept rather than omitted. There are **four** purposes against 198 nationalities,
    so covering the dimension exhaustively costs four passes and leaves the corpus still
    corridor-independent: a corpus containing every purpose's pages favours no traveller, where a
    corpus containing one purpose's would.

    Each is `site:`-restricted, exactly as `corridor_queries` is, so the engine is asked only about
    a domain the registry already confirmed — and the results are filtered again afterwards, because
    the restriction is a courtesy to the engine and not the safety mechanism.
    """

    if purpose is not None:
        # Deliberately the same phrasings `corridor_queries` uses, so the corpus sees what a
        # corridor would see. Divergent wording would reopen the gap this sweep exists to close.
        return [
            f"site:{domain} {purpose} visa documents required",
            f"site:{domain} {country_name} {purpose} visa requirements",
        ]
    return [
        f"site:{domain} {country_name} visa requirements",
        f"site:{domain} {country_name} who needs a visa",
        f"site:{domain} visa application documents required",
        f"site:{domain} visa types and fees",
        f"site:{domain} visa processing times",
        f"site:{domain} visa exempt countries",
    ]


def all_corpus_queries(country_name: str, domains: list[str]) -> list[str]:
    """Every query one build runs: the neutral pass, then one pass per purpose.

    Order is fixed and duplicates are dropped, so two builds of the same country ask the same things
    in the same order — the corpus is meant to remove variance, not add a new source of it.
    """

    queries: list[str] = []
    for domain in domains:
        queries.extend(corpus_queries(country_name, domain))
    for purpose in get_args(TravelPurpose):
        for domain in domains:
            queries.extend(corpus_queries(country_name, domain, purpose=purpose))
    return list(dict.fromkeys(queries))


class CorpusBuild(StrictModel):
    """What one build of a country's corpus did, for a person reading the command's output."""

    country_code: str
    queries: int = 0
    seeds: int = 0
    crawled: int = 0
    found: int = 0
    """Entries this crawl produced, before the merge."""

    added: int = 0
    """Entries the corpus did not already hold."""

    total: int = 0
    """Entries the corpus holds afterwards, which is never fewer than before."""

    unreadable: int = 0
    delegated: int = 0
    """How many places this country's own pages sent the traveller that we may name but not read."""
    by_depth: dict[int, int] = Field(default_factory=dict)
    """How far this crawl reached. A means rather than the point: the corpus exists so a live
    corridor does not re-fetch for 50+ seconds, and *which pages exist* does not vary by traveller
    (DECISIONS entry 44). Depth matters only where the pages a corridor needs lie deeper."""

    lost_hosts: dict[str, str] = Field(default_factory=dict)
    """Hosts that failed and contributed **nothing**, with the reason, worst kind of gap first.

    A seed never becomes a corpus entry — only the links found *on* a fetched page do — so a seeded
    host whose own fetch fails leaves no trace whatever: not an entry, not an `unreadable` count,
    nothing. Japan's London embassy went missing exactly that way, through a transient Akamai `403`
    during a build, and the corpus has lacked the host ever since while live search returns it and
    the live path reads a document checklist from it (DECISIONS entry 77).

    A corpus is additive and rebuilt rarely, so a hole opened by a moment's failure stays open. This
    is the field that makes it visible; retrying these on the next build is not yet built.
    """

    pdfs_read: int = 0
    """PDFs read in the second pass, for their text only. Counted apart from `crawled` because they
    were never crawled: `_expand` will not follow a PDF, so these are fetched deliberately."""

    indexed_text: int = 0
    """Pages whose readable text was kept, for the text index (`discovery/page_text.py`).

    Counted apart from `crawled` because the two differ and the difference is the interesting part:
    a page can be fetched and still contribute no text — too short to rank, or a render that came
    back empty. It is also **not** comparable to `found`, which counts discovered links rather than
    pages read. Zero here with a non-zero `crawled` means the build was asked to keep nothing."""

    lost_host_outcomes: dict[str, FailureOutcome] = Field(default_factory=dict)
    """The same hosts keyed to the typed outcome, so a count never rests on parsing prose.

    DECISIONS entry 36's rule: `lost_hosts` carries what a person reads, this carries what may be
    counted, and rewording a message must never change what an audit reports."""

    @property
    def deep_share(self) -> float:
        """The share of this crawl's entries found beyond depth 1."""

        found = sum(self.by_depth.values())
        if not found:
            return 0.0
        return sum(count for depth, count in self.by_depth.items() if depth > 1) / found

    @property
    def depth_is_exercised(self) -> bool:
        """False when the crawl fetched its seeds and effectively stopped.

        Reported rather than raised: the entries are real either way. But a build that behaves like
        the request path has not done the one thing it exists to do, and on 2026-08-22 that was true
        and invisible — 1,032 of Canada's 1,071 entries sat at depth 1 and nothing said so.
        """

        return self.deep_share >= MINIMUM_DEEP_SHARE


def _reject(link: PageLink, lexicon: Lexicon) -> str | None:
    """What cannot be visa guidance for anybody.

    Only two, and both are corridor-independent facts about the page rather than about the reader.
    `wrong_audience` and `wrong_country` are deliberately **not** applied: a page about Brazil is
    noise for one corridor and the answer for another, and the corpus serves every corridor.
    """

    if is_archived(link.url, lexicon):
        return "the path marks it as archived or superseded"
    if is_boilerplate(link.url, lexicon):
        return "the path marks it as site furniture rather than guidance"
    return None


def _entry(
    candidate: CandidatePage,
    titles: dict[str, str],
    failures: dict[str, str],
    now: datetime,
    read: set[str] = frozenset(),  # type: ignore[assignment]
) -> CorpusEntry:
    """One corpus entry, and **whether the crawl actually opened the page**.

    `read` was added by entry 92 after a measurement nobody had made: this function wrote only
    `unreadable` or `unknown`, so `readable` was a documented retention tier that no build ever
    assigned. Two things followed, and the second is the one that matters.

    `merge` moves a status up and never down, and `unknown` ranks *below* `unreadable`. So a page
    that failed in one build and was read in the next kept the old failure and its sentence for
    ever. Twelve France entries said "it asked this client to prove it is a browser... and that
    challenge could not be answered here" while the page-text index held their bodies — a reason
    that is not true of what was seen, which is the one thing this project's failure text may never
    be.
    """

    url = candidate.link.url
    reason = failures.get(url)
    return CorpusEntry(
        url=url,
        title=titles.get(url) or candidate.title or "",
        link_text=candidate.link.text,
        heading=candidate.link.heading,
        depth=candidate.link.depth,
        discovered_from=candidate.link.discovered_from,
        first_seen=now,
        last_seen=now,
        status="unreadable" if reason else ("readable" if url in read else "unknown"),
        detail=reason or "",
    )


def _lost_hosts(
    entries: list[CorpusEntry], crawl_fetcher: CrawlFetcher
) -> tuple[dict[str, str], dict[str, FailureOutcome]]:
    """Hosts this build failed on and got *nothing* from, which is the gap nobody could see.

    A host with some pages read and some failed is not lost — the corpus holds it and a later build
    can deepen it. A host that contributed no entry at all is a hole, and because a corpus only ever
    grows, it is a permanent one until someone rebuilds and the same host happens to answer.
    """

    covered = {host_of(entry.url) for entry in entries}
    reasons: dict[str, str] = {}
    outcomes: dict[str, FailureOutcome] = {}
    for url, reason in crawl_fetcher.failures.items():
        host = host_of(url)
        if host in covered:
            continue
        reasons.setdefault(host, reason)
        outcome = crawl_fetcher.outcomes.get(url)
        if outcome is not None:
            outcomes.setdefault(host, outcome)
    return reasons, outcomes


async def _read_pdfs(
    crawled: list[CandidatePage],
    destination: DestinationConfig,
    crawl_fetcher: CrawlFetcher,
    keep: Callable[[str, str, str], None],
    *,
    maximum_pdfs: int,
) -> int:
    """Read the PDFs a crawl found, for their text alone, best-scoring first.

    A second pass rather than part of the crawl, because a PDF is a destination and the crawl walks
    signposts — queuing one on the frontier would mean fetching it to look for links it cannot have.
    Ordered by the anchor score anyway: the budget is finite and a PDF whose link said "Checklist"
    is worth more than one whose link said "Form 12", even though the anchor is exactly the signal
    this whole exercise distrusts. It is what there is *before* the text is in hand.

    No title: a PDF has no `<title>`, and inventing one from the anchor would put the crawl's guess
    where `score_body` reads a page's own claim about itself.
    """

    ordered = sorted(
        (page for page in crawled if is_pdf_url(page.link.url)),
        key=lambda page: -page.link_scores.best()[1],
    )[:maximum_pdfs]
    if not ordered:
        return 0

    read = 0
    async with httpx.AsyncClient(
        transport=crawl_fetcher.transport,
        timeout=crawl_fetcher.timeout_seconds,
        follow_redirects=True,
        verify=build_ssl_context(),
        headers={
            "User-Agent": crawl_fetcher.user_agent,
            "Accept": "application/pdf",
        },
    ) as client:
        for page in ordered:
            text = await crawl_fetcher.fetch_pdf_text(
                client,
                page.link.url,
                destination,
                maximum_characters=DEFAULT_KEPT_TEXT_CHARACTERS,
            )
            if text:
                keep(page.link.url, "", text)
                read += 1
    return read


async def build_country_corpus(
    country: Country,
    trusted: list[str],
    provider: SearchProvider,
    crawl_fetcher: CrawlFetcher,
    *,
    existing: CountryCorpus | None,
    now: datetime,
    lexicon: Lexicon | None = None,
    registry: CountryRegistry | None = None,
    providers: ServiceProviderRegistry | None = None,
    maximum_pages: int = DEFAULT_CORPUS_PAGES,
    maximum_depth: int = DEFAULT_CORPUS_DEPTH,
    maximum_pages_per_host: int = DEFAULT_CORPUS_PAGES_PER_HOST,
    host_floor: int = DEFAULT_CORPUS_HOST_FLOOR,
    results_per_query: int = 10,
    page_text: PageTextStore | None = None,
    maximum_pdfs: int = DEFAULT_CORPUS_PDFS,
    family_share: float = DEFAULT_CORPUS_FAMILY_SHARE,
) -> tuple[CountryCorpus, CorpusBuild]:
    """Search, crawl and fold the result into the country's corpus, adding but never removing.

    With `page_text`, the readable text of every page the crawl reads is kept as well, and this is
    the only place that ever costs nothing extra to do: the bytes are already in hand, already
    parsed for links, and were previously dropped on the floor at `crawl._expand`. No additional
    fetch, no additional search, no additional politeness delay.

    Two stores, written together and deliberately not merged. The corpus answers *which pages
    exist* and is read whole on every request; the index answers *what they say* and is queried
    without being loaded. Putting the text in the corpus file would take Japan's from 1.4MB to
    roughly 35MB and spend about a second of pydantic validation per corridor.
    """

    words = lexicon or get_lexicon()
    # Every country's slug, so a run of sibling links that differ only by which country they
    # are about can be recognised as one page published per traveller.
    every_country = registry or get_country_registry()
    destination = DestinationConfig(
        slug=country.slug,
        display_name=country.name,
        route_type="national",
        implementation_status="available",
        trusted_domains=trusted,
    )

    queries = all_corpus_queries(country.name, trusted)
    found = await search_all(provider, queries, count=results_per_query)

    seeds: list[str] = []
    for query in queries:
        for result in usable_results(found[query], destination):
            url = canonicalise_url(result.url)
            if not is_crawlable(url, destination):
                continue
            if url not in seeds:
                seeds.append(url)

    def score(link: PageLink) -> RoleScores:
        return score_role_vocabulary(link, words)

    # Buffered rather than written page by page: one transaction at the end of a crawl, against
    # thousands mid-crawl. The cost is that a build killed halfway keeps no text, which is the
    # corpus file's own behaviour and the same remedy — run it again.
    kept: list[StoredPage] = []

    def keep(url: str, title: str, text: str) -> None:
        if text:
            kept.append(StoredPage(url=url, fetched_at=now, body=text, title=title))

    crawler = LinkCrawler(
        crawl_fetcher,
        score,
        reject=lambda link: _reject(link, words),
        maximum_depth=maximum_depth,
        maximum_pages=maximum_pages,
        maximum_pages_per_host=maximum_pages_per_host,
        host_floor=host_floor,
        expansion_threshold=CORPUS_EXPANSION_THRESHOLD,
        on_page=keep if page_text is not None else None,
        family_slugs=frozenset(other.slug for other in every_country.countries),
        family_share=family_share,
        family_pattern=CORPUS_FAMILY_PATTERN,
        provider_domains=(providers or get_service_providers()).domains,
    )
    crawled = await crawler.crawl(destination, seeds)
    pdfs_read = 0
    if page_text is not None:
        pdfs_read = await _read_pdfs(
            crawled, destination, crawl_fetcher, keep, maximum_pdfs=maximum_pdfs
        )
    indexed_text = page_text.write(country.code, kept) if page_text is not None else 0

    entries = [
        _entry(candidate, crawler.titles, crawl_fetcher.failures, now, crawler.read)
        for candidate in crawled
    ]
    before = existing or CountryCorpus(
        country_code=country.code,
        country_name=country.name,
        trusted_domains=trusted,
        built_at=now,
        entries=[],
    )
    lost_reasons, lost_outcomes = _lost_hosts(entries, crawl_fetcher)
    known = {entry.url for entry in before.entries}
    # The domains are refreshed to what the registry says now, so the file records the set actually
    # used. The entries are not filtered by it: `entries_within` applies trust when the corpus is
    # *read*, which is what lets a later narrowing take effect without deleting what was found.
    after = merge(
        before.model_copy(update={"trusted_domains": trusted}),
        entries,
        now=now,
        delegations=crawler.delegations.values(),
    )
    return after, CorpusBuild(
        country_code=country.code,
        queries=len(queries),
        seeds=len(seeds),
        crawled=len(crawled),
        found=len(entries),
        added=sum(1 for entry in entries if entry.url not in known),
        total=len(after.entries),
        unreadable=sum(1 for entry in entries if entry.status == "unreadable"),
        delegated=len(after.delegations),
        by_depth=Counter(entry.depth for entry in entries),
        lost_hosts=lost_reasons,
        lost_host_outcomes=lost_outcomes,
        indexed_text=indexed_text,
        pdfs_read=pdfs_read,
    )


BuildReporter = Callable[[CorpusBuild], None]
