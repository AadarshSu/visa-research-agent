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

from collections import Counter
from collections.abc import Callable
from datetime import datetime
from typing import get_args

from pydantic import Field

from visa_research_agent.discovery.corpus import CorpusEntry, CountryCorpus, merge
from visa_research_agent.discovery.crawl import CrawlFetcher, LinkCrawler
from visa_research_agent.discovery.lexicon import Country, Lexicon, get_lexicon
from visa_research_agent.discovery.models import CandidatePage, PageLink, RoleScores
from visa_research_agent.discovery.scoring import is_archived, is_boilerplate, score_role_vocabulary
from visa_research_agent.discovery.search import SearchProvider, search_all, usable_results
from visa_research_agent.discovery.urls import canonicalise_url, is_crawlable
from visa_research_agent.domain.models import DestinationConfig, StrictModel, TravelPurpose

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
    by_depth: dict[int, int] = Field(default_factory=dict)
    """How far this crawl actually reached, which is the job's whole reason for existing."""

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
) -> CorpusEntry:
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
        status="unreadable" if reason else "unknown",
        detail=reason or "",
    )


async def build_country_corpus(
    country: Country,
    trusted: list[str],
    provider: SearchProvider,
    crawl_fetcher: CrawlFetcher,
    *,
    existing: CountryCorpus | None,
    now: datetime,
    lexicon: Lexicon | None = None,
    maximum_pages: int = DEFAULT_CORPUS_PAGES,
    maximum_depth: int = DEFAULT_CORPUS_DEPTH,
    maximum_pages_per_host: int = DEFAULT_CORPUS_PAGES_PER_HOST,
    results_per_query: int = 10,
) -> tuple[CountryCorpus, CorpusBuild]:
    """Search, crawl and fold the result into the country's corpus, adding but never removing."""

    words = lexicon or get_lexicon()
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

    crawler = LinkCrawler(
        crawl_fetcher,
        score,
        reject=lambda link: _reject(link, words),
        maximum_depth=maximum_depth,
        maximum_pages=maximum_pages,
        maximum_pages_per_host=maximum_pages_per_host,
    )
    crawled = await crawler.crawl(destination, seeds)

    entries = [
        _entry(candidate, crawler.titles, crawl_fetcher.failures, now) for candidate in crawled
    ]
    before = existing or CountryCorpus(
        country_code=country.code,
        country_name=country.name,
        trusted_domains=trusted,
        built_at=now,
        entries=[],
    )
    known = {entry.url for entry in before.entries}
    # The domains are refreshed to what the registry says now, so the file records the set actually
    # used. The entries are not filtered by it: `entries_within` applies trust when the corpus is
    # *read*, which is what lets a later narrowing take effect without deleting what was found.
    after = merge(before.model_copy(update={"trusted_domains": trusted}), entries, now=now)
    return after, CorpusBuild(
        country_code=country.code,
        queries=len(queries),
        seeds=len(seeds),
        crawled=len(crawled),
        found=len(entries),
        added=sum(1 for entry in entries if entry.url not in known),
        total=len(after.entries),
        unreadable=sum(1 for entry in entries if entry.status == "unreadable"),
        by_depth=Counter(entry.depth for entry in entries),
    )


BuildReporter = Callable[[CorpusBuild], None]
