"""Building a country's corpus: what it keeps that a corridor would drop.

Offline throughout, against the fake two-host government site. The rules worth pinning are the ones
that distinguish this from `resolver.py`, because a later "simplification" toward sharing that code
would break exactly them. See DECISIONS entry 44.
"""

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from discovery_site import (
    ARCHIVED,
    AUTHORITY,
    DETAIL_CHINA,
    DETAIL_INDIA,
    FULL_CHECKLIST,
    INDEX,
    MISSION,
    MISSION_INDEX,
    OFF_DOMAIN,
    handler,
)

from visa_research_agent.discovery.corpus import CountryCorpus
from visa_research_agent.discovery.corpus_build import (
    all_corpus_queries,
    build_country_corpus,
)
from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.lexicon import Country
from visa_research_agent.discovery.models import SearchResult
from visa_research_agent.discovery.page_text import PageTextStore

NOW = datetime(2026, 8, 22, 9, 0, tzinfo=UTC)
TRUSTED = ["immigration.gov.example", "uk.embassy.gov.example"]


def country() -> Country:
    return Country(
        code="XX",
        name="Example",
        tlds=[".example"],
        synonyms=[],
        demonyms=[],
        host_labels=["xx"],
        mission_labels=["xx"],
    )


class FakeSearch:
    """Returns fixed results for every query, and records what was asked."""

    def __init__(self, urls: list[str]) -> None:
        self.urls = urls
        self.queries: list[str] = []

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        self.queries.append(query)
        return [
            SearchResult(url=url, title="", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls)
        ]


async def sleep_none(_: float) -> None:
    return None


def fetcher(requests: list[httpx.Request]) -> CrawlFetcher:
    return CrawlFetcher(
        transport=httpx.MockTransport(handler(requests)),  # type: ignore[arg-type]
        host_delay_seconds=0.0,
        sleep=sleep_none,
    )


async def build(
    urls: list[str], *, existing: CountryCorpus | None = None, pages: int = 60
) -> tuple[CountryCorpus, list[httpx.Request]]:
    requests: list[httpx.Request] = []
    corpus, _report = await build_country_corpus(
        country(),
        TRUSTED,
        FakeSearch(urls),
        fetcher(requests),
        existing=existing,
        now=NOW,
        maximum_pages=pages,
    )
    return corpus, requests


def test_the_queries_name_no_nationality_or_residence() -> None:
    """198-valued dimensions stay out: a corpus built for one nationality is not a corpus."""

    queries = all_corpus_queries("Canada", ["canada.ca"])

    assert all(query.startswith("site:canada.ca ") for query in queries)
    for word in ("india", "indian", "british", "united kingdom", "resident"):
        assert not any(word in query.lower() for query in queries), word


def test_every_purpose_is_swept() -> None:
    """The measured gap, and why purpose is not treated like nationality.

    `.../visit-canada/supporting-documents` reached the live corridor run as a seed from
    `site:canada.ca tourism visa documents required`, and the corpus — which asked only
    `visa application documents required` — never saw it. Purpose has four values, so the dimension
    is swept exhaustively rather than dropped, and the corpus stays corridor-independent because it
    then holds every purpose's pages rather than one traveller's.
    """

    queries = all_corpus_queries("Canada", ["canada.ca"])

    for purpose in ("tourism", "business", "study", "transit"):
        assert any(purpose in query for query in queries), purpose
    # The exact phrasing the corridor uses, or the sweep would miss what it is meant to cover.
    assert "site:canada.ca tourism visa documents required" in queries


def test_the_query_list_is_stable_and_free_of_duplicates() -> None:
    """The corpus removes variance; it must not introduce a new source of it."""

    first = all_corpus_queries("Canada", ["canada.ca", "travel.gc.ca"])
    second = all_corpus_queries("Canada", ["canada.ca", "travel.gc.ca"])

    assert first == second
    assert len(first) == len(set(first))


@pytest.mark.anyio
async def test_a_build_records_the_pages_it_reached_with_how_it_got_there() -> None:
    corpus, _ = await build([INDEX])

    assert corpus.country_code == "XX"
    assert corpus.entries, "the crawl reached nothing"
    india = corpus.find("detail/india")
    assert india, "a page two hops in was not recorded"
    assert india[0].depth >= 1
    assert india[0].discovered_from, "how a page was reached is what a later crawl follows"


@pytest.mark.anyio
async def test_pages_about_other_countries_are_kept() -> None:
    """The sharpest difference from `resolver.py`, and it is deliberate.

    A corridor vetoes a page about another country, correctly — for *that* traveller it is noise.
    The corpus serves every corridor, so China's page is exactly what a later China corridor needs,
    and dropping it here would build a store that can only answer corridors it was not built for.
    """

    corpus, _ = await build([INDEX])

    assert corpus.find("detail/india"), "the India page should be held"
    assert corpus.find("detail/china"), "the China page must not be vetoed out of a corpus"


@pytest.mark.anyio
async def test_archived_paths_are_still_refused() -> None:
    """Not guidance for anybody, so unlike wrong-country it stays a rejection."""

    corpus, _ = await build([INDEX])

    assert not corpus.find("/2019/"), ARCHIVED


@pytest.mark.anyio
async def test_nothing_off_the_trusted_domains_is_ever_requested() -> None:
    corpus, requests = await build([INDEX, OFF_DOMAIN])

    assert all("cheap-visas" not in str(request.url) for request in requests)
    assert not corpus.find("cheap-visas")


@pytest.mark.anyio
async def test_a_second_build_adds_without_removing() -> None:
    """The whole point of the store, exercised end to end rather than only on the merge."""

    first, _ = await build([INDEX])
    held = {entry.url for entry in first.entries}
    assert held

    # A later crawl that only ever sees the mission host must not lose the authority's pages.
    second, _ = await build([MISSION_INDEX], existing=first)

    assert held.issubset({entry.url for entry in second.entries})
    assert len(second.entries) >= len(first.entries)


@pytest.mark.anyio
async def test_the_trusted_domains_are_refreshed_but_entries_are_not_filtered() -> None:
    """Trust is applied when the corpus is read, so a build records the set it used and no more."""

    first, _ = await build([INDEX])
    narrowed = first.model_copy(update={"trusted_domains": ["immigration.gov.example"]})

    allowed = narrowed.entries_within(["immigration.gov.example"])

    assert all(AUTHORITY in entry.url for entry in allowed)
    assert len(narrowed.entries) >= len(allowed), "narrowing must not delete what was found"


@pytest.mark.anyio
async def test_a_build_reports_what_it_did() -> None:
    requests: list[httpx.Request] = []
    _corpus, report = await build_country_corpus(
        country(),
        TRUSTED,
        FakeSearch([INDEX]),
        fetcher(requests),
        existing=None,
        now=NOW,
        maximum_pages=60,
    )

    assert report.country_code == "XX"
    assert report.queries == len(all_corpus_queries("Example", TRUSTED))
    assert report.seeds >= 1
    assert report.added == report.total, "a first build adds everything it found"


@pytest.mark.anyio
async def test_the_corpus_stores_no_scores() -> None:
    """Scoring is corridor-dependent, so freezing it would freeze the half that must stay live."""

    corpus, _ = await build([INDEX])

    assert corpus.entries
    assert not any(hasattr(entry, "score") for entry in corpus.entries)
    # What it does keep is what a later corridor needs to score the page for itself.
    entry = next(item for item in corpus.entries if item.url == DETAIL_INDIA or item.link_text)
    link = entry.to_link()
    assert link.url == entry.url
    assert isinstance(link.text, str)


@pytest.mark.anyio
async def test_china_and_india_pages_both_survive_a_rebuild() -> None:
    first, _ = await build([INDEX])
    second, _ = await build([INDEX], existing=first)

    urls = {entry.url for entry in second.entries}
    assert DETAIL_INDIA in urls
    assert DETAIL_CHINA in urls
    assert second.find("detail/india")[0].times_seen == 2


@pytest.mark.anyio
async def test_a_host_that_gives_the_build_nothing_is_named() -> None:
    """The gap that was invisible, and stayed invisible because nothing could see it.

    A seed never becomes a corpus entry — only the links found *on* a fetched page do — so a seeded
    host whose own fetch fails leaves no entry, no `unreadable` count and no trace of any kind.
    Japan's London embassy went missing through a transient `403` during a build, and the corpus has
    lacked the whole host ever since while live search returns it and a live corridor reads a
    document checklist from it. DECISIONS entry 77.
    """

    requests: list[httpx.Request] = []
    site = handler(requests)

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.host == MISSION and request.url.path != "/robots.txt":
            return httpx.Response(403, text="Access Denied")
        response: httpx.Response = site(request)  # type: ignore[operator]
        return response

    _corpus, report = await build_country_corpus(
        country(),
        TRUSTED,
        FakeSearch([INDEX, MISSION_INDEX]),
        CrawlFetcher(
            transport=httpx.MockTransport(handle),
            host_delay_seconds=0.0,
            sleep=sleep_none,
        ),
        existing=None,
        now=NOW,
        maximum_pages=60,
    )

    assert report.total, "the readable host still produced a corpus"
    assert MISSION in report.lost_hosts
    assert report.lost_host_outcomes[MISSION] == "blocked"
    # The typed outcome is what a count may rest on; the sentence is only ever repeated.
    assert "403" in report.lost_hosts[MISSION]
    # A host the build did read is not "lost", however many of its individual pages failed.
    assert AUTHORITY not in report.lost_hosts


@pytest.mark.anyio
async def test_a_build_keeps_the_text_of_the_pages_it_read(tmp_path: Path) -> None:
    """Two stores written from one crawl, and the text costs no extra request.

    The corpus answers *which pages exist*; the index answers *what they say*. The assertion that
    matters is the last one: no page was fetched twice to fill the second store.
    """

    requests: list[httpx.Request] = []
    index = PageTextStore(tmp_path)

    _corpus, report = await build_country_corpus(
        country(),
        TRUSTED,
        FakeSearch([INDEX, FULL_CHECKLIST]),
        fetcher(requests),
        existing=None,
        now=NOW,
        maximum_pages=60,
        page_text=index,
    )

    assert report.indexed_text > 0
    assert index.count("XX") == report.indexed_text
    fetched = [str(request.url) for request in requests if "robots.txt" not in str(request.url)]
    assert len(fetched) == len(set(fetched))


@pytest.mark.anyio
async def test_a_build_given_no_index_writes_none(tmp_path: Path) -> None:
    """The corpus must still be buildable alone, and nothing may be created on the side."""

    _corpus, report = await build_country_corpus(
        country(),
        TRUSTED,
        FakeSearch([INDEX]),
        fetcher([]),
        existing=None,
        now=NOW,
        maximum_pages=60,
    )

    assert report.indexed_text == 0
    assert list(tmp_path.iterdir()) == []
