"""Crawling within approved domains, and scoring what is found."""

import asyncio
import socket
from typing import Any

import httpcore
import httpx
import pytest
from discovery_site import (
    ARCHIVED,
    AUTHORITY,
    DETAIL_CHINA,
    DETAIL_INDIA,
    INDEX,
    MISSION,
    MISSION_INDEX,
    MISSION_OPAQUE,
    MISSION_SPOUSE,
    OFF_DOMAIN,
    destination,
    handler,
)

from visa_research_agent.discovery.crawl import (
    CrawlFetcher,
    LinkCrawler,
    extract_links,
    host_does_not_resolve,
)
from visa_research_agent.discovery.lexicon import get_country_registry, get_lexicon
from visa_research_agent.discovery.models import Corridor, PageLink, RoleScores
from visa_research_agent.discovery.scoring import (
    is_archived,
    rank_for_role,
    score_body,
    score_link,
    wrong_audience,
    wrong_country,
)
from visa_research_agent.domain.trust import host_of


def corridor(nationality: str = "IN", purpose: str = "tourism") -> Corridor:
    return Corridor.model_validate(
        {
            "destination_slug": "testland",
            "passport_nationality": nationality,
            "applying_from": "GB",
            "purpose": purpose,
        }
    )


def link_for(url: str, text: str = "", depth: int = 1) -> PageLink:
    return PageLink(url=url, text=text, heading="", depth=depth, discovered_from="seed")


def scores_for(
    url: str, text: str = "", *, nationality: str = "IN", purpose: str = "tourism", depth: int = 1
) -> RoleScores:
    registry = get_country_registry()
    return score_link(
        link_for(url, text, depth),
        corridor(nationality, purpose),
        get_lexicon(),
        registry.require(nationality),
        registry.require("GB"),
    )


async def sleep_none(_: float) -> None:
    return None


def build_crawler(requests: list[httpx.Request], **kwargs: Any) -> LinkCrawler:
    registry = get_country_registry()
    lexicon = get_lexicon()
    traveller = corridor()

    def score(link: PageLink) -> RoleScores:
        return score_link(link, traveller, lexicon, registry.require("IN"), registry.require("GB"))

    fetcher = CrawlFetcher(
        transport=httpx.MockTransport(handler(requests)),  # type: ignore[arg-type]
        sleep=sleep_none,
        host_delay_seconds=0.0,
    )
    return LinkCrawler(fetcher, score, **kwargs)


def test_link_extraction_keeps_the_text_that_gives_a_url_meaning() -> None:
    html = (
        "<html><body><h2>Visa</h2>"
        '<a href="/visa/index_000070.html">Temporary Visitor Visa</a>'
        '<a href="mailto:x@y.z">Email</a><a href="#top">Top</a>'
        "</body></html>"
    )

    links = extract_links(html, f"https://{MISSION}/visa/")

    assert [item.url for item in links] == [f"https://{MISSION}/visa/index_000070.html"]
    assert links[0].text == "Temporary Visitor Visa"
    assert links[0].heading == "Visa"


def test_anchor_text_identifies_a_page_whose_url_says_nothing() -> None:
    """Japan's real checklist parent is `index_000070.html`; only its label identifies it."""

    labelled = scores_for(MISSION_OPAQUE, "Temporary Visitor Visa")
    unlabelled = scores_for(MISSION_OPAQUE, "")

    # Both are eligible because the URL mentions visas, but only the labelled one is identifiable
    # as the visa category a tourist needs.
    assert labelled.best()[0] == "application_route"
    assert labelled.best()[1] > unlabelled.best()[1] + 20


def test_a_nationality_specific_page_beats_the_general_one_for_that_traveller() -> None:
    specific = scores_for(DETAIL_INDIA, "India").score_for("visa_decision")
    general = scores_for(f"https://{AUTHORITY}/visa/index.html", "Visa").score_for("visa_decision")

    assert specific > general


def test_the_same_page_scores_lower_for_a_traveller_it_is_not_about() -> None:
    for_indian = scores_for(DETAIL_INDIA, "India", nationality="IN").score_for("visa_decision")
    for_american = scores_for(DETAIL_INDIA, "India", nationality="US").score_for("visa_decision")

    assert for_indian > for_american


def test_a_wrong_audience_page_is_pushed_below_the_right_one() -> None:
    spouse = scores_for(MISSION_SPOUSE, "Spouse Visa Documents Required")
    tourism = scores_for(
        "https://uk.embassy.gov.example/visa/tourism-documents-required.html",
        "Tourism: Documents Required",
    )

    assert tourism.score_for("document_checklist") > spouse.score_for("document_checklist")
    # The spouse page carries the off-scope penalty despite matching the checklist vocabulary.
    assert any("off-scope" in signal for signal in spouse.signals["document_checklist"])


def test_a_page_about_another_country_is_named_for_rejection() -> None:
    registry = get_country_registry()

    assert wrong_country(link_for(DETAIL_CHINA, "China"), corridor(), registry, "SG") == "China"
    assert wrong_country(link_for(DETAIL_INDIA, "India"), corridor(), registry, "SG") is None


def test_an_archived_path_is_recognised() -> None:
    lexicon = get_lexicon()

    assert is_archived(f"https://{AUTHORITY}/visa/2019/tourist-checklist.html", lexicon)
    assert is_archived(f"https://{AUTHORITY}/archive/visa.html", lexicon)
    assert not is_archived(DETAIL_INDIA, lexicon)


def test_a_pdf_is_extra_evidence_for_a_checklist_only() -> None:
    pdf = scores_for("https://uk.embassy.gov.example/files/documents-required.pdf", "Documents")
    html = scores_for("https://uk.embassy.gov.example/documents-required.html", "Documents")

    assert pdf.score_for("document_checklist") > html.score_for("document_checklist")


def test_depth_is_penalised_so_shallow_pages_win_ties() -> None:
    shallow = scores_for(DETAIL_INDIA, "India", depth=1).score_for("visa_decision")
    deep = scores_for(DETAIL_INDIA, "India", depth=3).score_for("visa_decision")

    assert shallow > deep


def test_body_text_confirms_what_a_link_suggested() -> None:
    registry = get_country_registry()
    scores = score_body(
        "Nationals of India require a visa for tourism visits of up to 90 days.",
        "Visa Requirements for Indian Travel Documents",
        corridor(),
        get_lexicon(),
        registry.require("IN"),
    )

    assert scores.score_for("visa_decision") > 0


def test_a_wrong_audience_title_penalises_the_page_body() -> None:
    registry = get_country_registry()
    common = ("Documents required for the application.", corridor(), get_lexicon())

    tourism = score_body(common[0], "Tourism checklist", *common[1:], registry.require("IN"))
    spouse = score_body(common[0], "Spouse visa checklist", *common[1:], registry.require("IN"))

    assert tourism.score_for("document_checklist") > spouse.score_for("document_checklist")


@pytest.mark.anyio
async def test_the_crawl_never_requests_a_host_outside_the_approved_domains() -> None:
    """The core safety property of discovery."""

    requests: list[httpx.Request] = []
    crawler = build_crawler(requests)

    candidates = await crawler.crawl(destination(), [INDEX])

    assert requests, "the crawl should have fetched something"
    for request in requests:
        assert destination().trusts_host(host_of(str(request.url))), request.url
    assert all(OFF_DOMAIN != str(request.url) for request in requests)
    # The off-domain link is seen on the page but never becomes a candidate.
    assert all(candidate.link.url != OFF_DOMAIN for candidate in candidates)


@pytest.mark.anyio
async def test_the_crawl_reaches_a_page_two_hops_from_the_entry_point() -> None:
    requests: list[httpx.Request] = []
    crawler = build_crawler(requests)

    candidates = await crawler.crawl(destination(), [INDEX])
    found = {candidate.link.url for candidate in candidates}

    assert DETAIL_INDIA in found, "the per-nationality page is two hops from the index"


@pytest.mark.anyio
async def test_the_crawl_honours_its_page_budget() -> None:
    requests: list[httpx.Request] = []
    crawler = build_crawler(requests, maximum_pages=2)

    await crawler.crawl(destination(), [INDEX])

    assert len(requests) <= 2


@pytest.mark.anyio
async def test_the_crawl_is_deterministic_across_runs() -> None:
    first_requests: list[httpx.Request] = []
    second_requests: list[httpx.Request] = []

    first = await build_crawler(first_requests).crawl(destination(), [INDEX])
    second = await build_crawler(second_requests).crawl(destination(), [INDEX])

    assert sorted(c.link.url for c in first) == sorted(c.link.url for c in second)
    assert [str(r.url) for r in first_requests] == [str(r.url) for r in second_requests]


@pytest.mark.anyio
async def test_an_archived_page_never_becomes_a_candidate() -> None:
    """Without this, the 2019 checklist wins on the word "checklist" alone."""

    requests: list[httpx.Request] = []
    lexicon = get_lexicon()

    def reject(link: PageLink) -> str | None:
        return "archived" if is_archived(link.url, lexicon) else None

    crawler = build_crawler(requests, reject=reject)
    candidates = await crawler.crawl(destination(), [INDEX])

    assert all(candidate.link.url != ARCHIVED for candidate in candidates)
    assert ARCHIVED in crawler.rejected
    # And the archived page would otherwise have ranked top for the checklist role.
    unfiltered = await build_crawler([]).crawl(destination(), [INDEX])
    assert rank_for_role(unfiltered, "document_checklist")[0][0].link.url == ARCHIVED


@pytest.mark.anyio
async def test_a_wrong_audience_sibling_is_ranked_below_the_right_page() -> None:
    requests: list[httpx.Request] = []
    crawler = build_crawler(requests)

    candidates = await crawler.crawl(destination(), [MISSION_INDEX])
    by_url = {candidate.link.url: candidate for candidate in candidates}

    assert MISSION_SPOUSE in by_url and MISSION_OPAQUE in by_url
    assert (
        by_url[MISSION_OPAQUE].link_scores.best()[1]
        > (by_url[MISSION_SPOUSE].link_scores.best()[1])
    )


def test_a_diplomatic_passport_page_is_vetoed_not_merely_penalised() -> None:
    """Found on Japan's real site: the diplomatic exemption list names many nationalities, so a
    nationality match made it outscore the correct page. No score may outweigh a wrong audience."""

    lexicon = get_lexicon()
    diplomatic = link_for(
        "https://www.mofa.go.jp/ca/fna/page22e_000692.html",
        "Visa Exemptions for Diplomatic and Official Passport Holders",
    )

    assert wrong_audience(diplomatic, corridor(), lexicon) == "diplomatic"
    assert wrong_audience(link_for(DETAIL_INDIA, "India"), corridor(), lexicon) is None


def test_a_students_own_pages_are_not_vetoed_for_a_study_corridor() -> None:
    lexicon = get_lexicon()
    student = link_for("https://immigration.gov.example/visa/student.html", "Student Visa")

    assert wrong_audience(student, corridor(purpose="study"), lexicon) is None


def test_a_comprehensive_nationality_page_is_not_penalised_for_breadth() -> None:
    """Singapore's per-nationality page genuinely covers decision, documents, fee and timing.
    Dampening it for breadth handed the checklist role to a narrower, wrong page."""

    registry = get_country_registry()
    broad = (
        "Visa requirements for India. Documents required: passport, photograph. "
        "Visa fee applies. Processing time is three working days. Entering Singapore."
    )
    with_nationality = score_body(
        broad, "India Visa Requirements", corridor(), get_lexicon(), registry.require("IN")
    )
    without_nationality = score_body(
        broad.replace("India", "applicants"),
        "Visa Requirements",
        corridor(),
        get_lexicon(),
        registry.require("IN"),
    )

    assert with_nationality.score_for("document_checklist") > (
        without_nationality.score_for("document_checklist")
    )


def test_a_dns_failure_is_recognised_by_type_not_by_message() -> None:
    """The errno and wording differ between platforms — macOS `[Errno 8] nodename nor servname
    provided`, Linux `[Errno -2] Name or service not known` — so the message is the wrong thing to
    match on. `socket.gaierror` is the same everywhere, and httpx wraps it two layers deep."""

    resolution = httpx.ConnectError("[Errno 8] nodename nor servname provided, or not known")
    resolution.__cause__ = httpcore.ConnectError()
    resolution.__cause__.__cause__ = socket.gaierror(8, "nodename nor servname provided")

    assert host_does_not_resolve(resolution)
    # A refused connection or a timeout is about this attempt, not about the name.
    assert not host_does_not_resolve(httpx.ConnectError("[Errno 61] Connection refused"))
    assert not host_does_not_resolve(httpx.ReadTimeout("timed out"))


@pytest.mark.anyio
async def test_a_host_that_does_not_resolve_is_recorded_once_for_the_whole_host() -> None:
    """Every other failure is about one request; this one is about the name, so it is held per host
    and every path beneath it can be skipped without asking."""

    dead = f"https://gone.{AUTHORITY}/visa/index.html"

    def failing(request: httpx.Request) -> httpx.Response:
        error = httpx.ConnectError("[Errno 8] nodename nor servname provided, or not known")
        error.__cause__ = socket.gaierror(8, "nodename nor servname provided")
        raise error

    fetcher = CrawlFetcher(transport=httpx.MockTransport(failing), host_delay_seconds=0.0)
    async with httpx.AsyncClient(transport=fetcher.transport) as client:
        assert await fetcher.fetch_html(client, dead, destination()) is None

    assert fetcher.unresolvable_hosts == {host_of(dead)}
    assert fetcher.outcomes[dead] == "unreachable"
    # The sentence a reader sees is kept alongside the outcome, not replaced by it.
    assert "nodename" in fetcher.failures[dead]


@pytest.mark.anyio
async def test_a_refusal_is_recorded_as_blocked_rather_than_as_a_broken_page() -> None:
    """`inaccessible_domains` is derived from this, so it must not depend on the wording."""

    refused = f"https://{AUTHORITY}/visa/blocked.html"

    def refusing(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Access denied")

    fetcher = CrawlFetcher(transport=httpx.MockTransport(refusing), host_delay_seconds=0.0)
    async with httpx.AsyncClient(transport=fetcher.transport) as client:
        assert await fetcher.fetch_html(client, refused, destination()) is None

    assert fetcher.outcomes[refused] == "blocked"
    assert fetcher.blocked_urls() == {refused}
    assert not fetcher.unresolvable_hosts


@pytest.mark.anyio
async def test_the_politeness_delay_is_owed_to_a_host_not_to_the_whole_crawl() -> None:
    """It was applied before every request whatever host it was for, so forty pages cost twenty
    seconds of waiting and a second site queued behind the first for no reason. Each host still
    gets its spacing, which is what the delay is actually for."""

    slept: list[float] = []
    clock = [0.0]

    async def sleep(seconds: float) -> None:
        slept.append(seconds)
        clock[0] += seconds

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><body></body></html>")

    fetcher = CrawlFetcher(
        transport=httpx.MockTransport(respond),
        sleep=sleep,
        clock=lambda: clock[0],
        host_delay_seconds=0.5,
    )
    async with httpx.AsyncClient(transport=fetcher.transport) as client:
        await fetcher.fetch_html(client, f"https://{AUTHORITY}/a", destination())
        # A different host owes nothing: it has not been asked for anything yet.
        await fetcher.fetch_html(client, f"https://{MISSION}/a", destination())
        assert slept == []
        # The same host again does wait, and only for its own remaining spacing.
        await fetcher.fetch_html(client, f"https://{AUTHORITY}/b", destination())

    assert slept == [0.5]


@pytest.mark.anyio
async def test_different_hosts_are_crawled_at_the_same_time() -> None:
    """The frontier was walked one page at a time, so a corridor spanning several sites paid each
    site's latency in turn. One request per host at a time, several hosts at once."""

    in_flight = 0
    highest = 0

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, highest
        return httpx.Response(200, text="<html><body></body></html>")

    async def fetch_html(client: Any, url: str, destination: Any) -> str:
        nonlocal in_flight, highest
        in_flight += 1
        highest = max(highest, in_flight)
        try:
            await asyncio.sleep(0)
            return "<html><body></body></html>"
        finally:
            in_flight -= 1

    fetcher = CrawlFetcher(transport=httpx.MockTransport(respond), host_delay_seconds=0.0)
    fetcher.fetch_html = fetch_html  # type: ignore[method-assign]
    crawler = LinkCrawler(fetcher, lambda link: RoleScores(scores={}))

    await crawler.crawl(
        destination(),
        [f"https://{AUTHORITY}/a", f"https://{MISSION}/a"],
    )

    assert highest == 2


@pytest.mark.anyio
async def test_two_pages_on_one_host_are_not_fetched_at_the_same_time() -> None:
    """Concurrency across hosts must not become concurrency within one. The second page waits for
    the next wave, which is what keeps each site's spacing honest."""

    in_flight = 0
    highest = 0
    read: list[str] = []

    async def fetch_html(client: Any, url: str, destination: Any) -> str:
        nonlocal in_flight, highest
        in_flight += 1
        highest = max(highest, in_flight)
        read.append(url)
        try:
            await asyncio.sleep(0)
            return "<html><body></body></html>"
        finally:
            in_flight -= 1

    fetcher = CrawlFetcher(host_delay_seconds=0.0)
    fetcher.fetch_html = fetch_html  # type: ignore[method-assign]
    crawler = LinkCrawler(fetcher, lambda link: RoleScores(scores={}))
    seeds = [f"https://{AUTHORITY}/a", f"https://{AUTHORITY}/b", f"https://{AUTHORITY}/c"]

    await crawler.crawl(destination(), seeds)

    assert highest == 1
    # Deferring is not dropping: a page that waited for a later wave is still read.
    assert sorted(read) == sorted(seeds)


def test_a_link_with_an_invisible_character_in_its_host_still_resolves() -> None:
    """Found live: Thailand's immigration site links `tdac.immigration.go.th` with a zero-width
    space inside the hostname. It is an editor artefact, invisible, and meaningless in a URL, so
    removing it recovers a real government page. Trust is unaffected — the approved-domain check
    runs on the result."""

    html = '<a href="https://tdac.immigration.go.th​/arrival-card">Arrival card</a>'

    links = extract_links(html, "https://immigration.go.th/")

    assert [link.url for link in links] == ["https://tdac.immigration.go.th/arrival-card"]


def test_a_link_that_cannot_be_parsed_is_skipped_rather_than_fatal() -> None:
    """One malformed `href` used to end the whole corridor with a traceback. This runs over every
    anchor on every page of a live government site, so it has to tolerate what it finds — and a
    link that cannot be parsed is not a link."""

    html = (
        '<a href="https://good.gov.example/visa">Visa</a>'
        '<a href="https://exa​mp le broken^host/x">Broken</a>'
        '<a href="https://other.gov.example/apply">Apply</a>'
    )

    links = extract_links(html, "https://good.gov.example/")

    assert "https://good.gov.example/visa" in [link.url for link in links]
    assert "https://other.gov.example/apply" in [link.url for link in links]


@pytest.mark.anyio
async def test_a_crawl_hands_over_the_text_of_every_page_it_reads() -> None:
    """The bytes were always there; before 2026-08-26 they went out of scope at `_expand`.

    A page's own text is the only thing that can identify it when its anchor cannot — which is the
    usual case, not the exception, since a crawl records a page from the words of the link pointing
    at it. Nothing is fetched twice to get this.
    """

    kept: dict[str, tuple[str, str]] = {}
    crawler = build_crawler(
        [],
        maximum_depth=1,
        on_page=lambda url, title, text: kept.__setitem__(url, (title, text)),
    )

    await crawler.crawl(destination(), [MISSION_SPOUSE])

    title, text = kept[MISSION_SPOUSE]
    assert title == "Spouse visa"
    assert "documents required for a spouse visa" in text.lower()


@pytest.mark.anyio
async def test_a_crawl_told_to_keep_nothing_keeps_nothing() -> None:
    """The request path passes no reader and must be untouched by any of this."""

    crawler = build_crawler([], maximum_depth=1)

    await crawler.crawl(destination(), [MISSION_SPOUSE])

    assert crawler.on_page is None
