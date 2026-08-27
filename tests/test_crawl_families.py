"""Per-traveller families: one page published once per country, and the budget to open them.

The Netherlands publishes 219 pages at `…/schengen-visa/apply-{country}` and opening any one of them
yields that country's checklist for every purpose plus its consular fee page. Measured on the
corpus built 2026-08-27, **two of the 219 were ever opened**, so for 193 of 198 residences the store
held no tourism checklist at all — not as a candidate, not as anything.

The cause is a scoring failure, not a depth or budget one. A member's anchor text is a bare country
name, so every one of them scores 8.0 while the index listing them scores 17.6 and the leaf each one
leads to would score 25.0. Raising their score does not reach them either: 764 unopened Dutch pages
already score above the index. Reserved budget does.

Everything here is offline against a fake site.
"""

import re

import httpx
import pytest
from discovery_site import destination

from visa_research_agent.discovery.corpus_build import CORPUS_FAMILY_PATTERN
from visa_research_agent.discovery.crawl import CrawlFetcher, LinkCrawler
from visa_research_agent.discovery.models import PageLink, RoleScores
from visa_research_agent.discovery.urls import country_family_keys

AUTHORITY = "authority.gov.example"
COUNTRIES = [
    "india",
    "germany",
    "france",
    "brazil",
    "japan",
    "kenya",
    "mexico",
    "norway",
    "poland",
    "sweden",
]
SLUGS = frozenset(COUNTRIES)

INDEX = f"https://{AUTHORITY}/visa/apply"
LOUD = [f"https://{AUTHORITY}/visa/news-{n}" for n in range(40)]


def apply_page(country: str) -> str:
    return f"https://{AUTHORITY}/visa/apply-{country}"


def checklist(country: str) -> str:
    return f"https://{AUTHORITY}/visa/checklist/{country}"


def fee_page(country: str) -> str:
    """A second family, on the same page, whose anchors score higher than the first's."""

    return f"https://{AUTHORITY}/visa/fees/{country}"


def site() -> dict[str, str]:
    """An index linking ten country siblings and forty better-scoring distractions.

    The distractions are the point: without them the family would be opened anyway and the test
    would pass for the wrong reason.
    """

    pages = {
        INDEX: "".join(
            [f'<a href="{apply_page(c)}">{c.title()}</a>' for c in COUNTRIES]
            + [f'<a href="{fee_page(c)}">{c.title()}</a>' for c in COUNTRIES]
            + [f'<a href="{url}">visa requirements document checklist</a>' for url in LOUD]
        )
    }
    for country in COUNTRIES:
        pages[apply_page(country)] = f'<a href="{checklist(country)}">{country.title()}</a>'
    for country in COUNTRIES:
        pages[fee_page(country)] = "<p>the fee is 90 euros</p>"
    for url in LOUD:
        pages[url] = "<p>nothing here</p>"
    for country in COUNTRIES:
        pages[checklist(country)] = "<p>bring a passport and a photograph</p>"
    return pages


def handler(requests: list[str]) -> object:
    pages = site()

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="not found")
        url = str(request.url).rstrip("/")
        requests.append(url)
        if url in pages:
            return httpx.Response(
                200, text=pages[url], headers={"Content-Type": "text/html; charset=utf-8"}
            )
        return httpx.Response(404, text="not found")

    return respond


def score(link: PageLink) -> RoleScores:
    """Anchor-driven, exactly as the real scorer is: a bare country name says nothing.

    This is the whole mechanism reproduced in four lines. A family member's only description is the
    country it is about, so it scores at the floor however important the page behind it is.
    """

    words = f"{link.text} {link.url}".lower()
    if "checklist" in words or "requirements" in words:
        return RoleScores(scores={"document_checklist": 25.0})
    if link.url.rstrip("/") == INDEX:
        return RoleScores(scores={"application_route": 17.6})
    # The Netherlands' real numbers: a fee page's anchor scores 12.0 and an apply page's 8.0, and
    # only the apply page leads anywhere. A reserved queue ordered by score reads 131 of the first
    # and none of the second.
    if "/fees/" in words:
        return RoleScores(scores={"fees": 12.0})
    return RoleScores(scores={"application_route": 8.0})


async def sleep_none(_seconds: float) -> None:
    return None


def build(requests: list[str], **kwargs: object) -> LinkCrawler:
    fetcher = CrawlFetcher(
        transport=httpx.MockTransport(handler(requests)),  # type: ignore[arg-type]
        sleep=sleep_none,
        host_delay_seconds=0.0,
    )
    return LinkCrawler(
        fetcher,
        score,
        maximum_depth=3,
        maximum_pages=20,
        maximum_pages_per_host=20,
        expansion_threshold=0.0,
        **kwargs,  # type: ignore[arg-type]
    )


def target() -> object:
    config = destination()
    return config.model_copy(update={"trusted_domains": [AUTHORITY]})


@pytest.mark.anyio
async def test_a_family_is_unreachable_without_a_reserved_share() -> None:
    """The failure this exists to fix, reproduced: the family loses to better-scoring noise.

    This is the request path's configuration and it is the correct one there — a corridor has one
    traveller, so opening nine other countries' pages is nine wasted fetches.
    """

    requests: list[str] = []
    crawler = build(requests, family_slugs=SLUGS, family_share=0.0)

    await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    opened = set(requests)
    assert not opened & {apply_page(c) for c in COUNTRIES}
    assert not opened & {checklist(c) for c in COUNTRIES}


@pytest.mark.anyio
async def test_a_reserved_share_opens_the_family_and_reaches_the_leaf_below_it() -> None:
    """The claim, stated so it can fail: opening a member is what makes its leaf exist at all.

    The leaves are the assertion rather than the members, because a member nobody opens is still a
    usable candidate — it has an address. Its child does not exist in any form until someone reads
    the page that links to it.
    """

    requests: list[str] = []
    crawler = build(requests, family_slugs=SLUGS, family_share=0.5)

    candidates = await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    opened = set(requests)
    assert opened & {apply_page(c) for c in COUNTRIES}, "no family member was opened"
    found = {candidate.link.url for candidate in candidates}
    assert found & {checklist(c) for c in COUNTRIES}, "no leaf below the family was reached"


@pytest.mark.anyio
async def test_the_reserved_share_leaves_room_for_the_ordinary_crawl() -> None:
    """Half of each wave, not all of it: starving the rest trades one blind spot for another."""

    requests: list[str] = []
    crawler = build(requests, family_slugs=SLUGS, family_share=0.5)

    await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    assert set(requests) & set(LOUD), "the ordinary frontier was starved by the family"


@pytest.mark.anyio
async def test_a_short_run_of_country_links_is_not_a_family() -> None:
    """Below the minimum it is a region menu or a footer, and reserving budget for it is waste."""

    requests: list[str] = []
    crawler = build(
        requests, family_slugs=SLUGS, family_share=0.5, family_minimum=len(COUNTRIES) + 1
    )

    await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    assert not set(requests) & {apply_page(c) for c in COUNTRIES}


@pytest.mark.anyio
async def test_detection_is_off_when_no_country_slugs_are_supplied() -> None:
    """The request path passes none, so nothing about its behaviour can change."""

    requests: list[str] = []
    crawler = build(requests, family_share=0.5)

    await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    assert not set(requests) & {apply_page(c) for c in COUNTRIES}


def test_a_country_is_recognised_wherever_the_address_carries_it() -> None:
    """Whole segment, tail of a segment, and query value — the three shapes authorities use."""

    slugs = frozenset({"india", "united-kingdom"})

    assert country_family_keys("https://x.gov/consular-fees/india", slugs) == [
        "https://x.gov/consular-fees/{}"
    ]
    assert country_family_keys("https://x.gov/visa/apply-united-kingdom", slugs) == [
        "https://x.gov/visa/apply-{}"
    ]
    assert country_family_keys("https://x.gov/y?country=india&lang=en", slugs) == [
        "https://x.gov/y?country={}&lang=en"
    ]


def test_two_addresses_differing_only_by_country_share_a_key() -> None:
    slugs = frozenset({"india", "germany"})

    assert set(country_family_keys("https://x.gov/a/apply-india", slugs)) & set(
        country_family_keys("https://x.gov/a/apply-germany", slugs)
    )


def test_an_address_with_no_country_has_no_family() -> None:
    slugs = frozenset({"india"})

    assert country_family_keys("https://x.gov/visa/apply", slugs) == []
    assert country_family_keys("https://x.gov/visa/apply-india", frozenset()) == []


def test_the_scan_does_not_stop_at_the_first_thing_that_looks_like_a_token() -> None:
    """`/apply-united-kingdom` has to be tried as `united-kingdom` too.

    A consuming scan sees `apply-united-kingdom`, finds it is not a country, and moves past the
    whole thing — which undercounted the Netherlands' 219-member family to zero the first time this
    was measured, and would have made the whole finding invisible.
    """

    assert country_family_keys(
        "https://x.gov/schengen-visa/apply-united-kingdom", frozenset({"united-kingdom"})
    ) == ["https://x.gov/schengen-visa/apply-{}"]


def test_a_destination_named_in_its_own_addresses_still_forms_a_family() -> None:
    """The bug that made the first real rebuild read zero gateway pages.

    `netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-india` carries **two** country
    tokens, and blanking only the first gives every one of the 219 members a different key — so no
    family forms, no budget is reserved, and the crawl behaves exactly as it did before. A country
    named in its own URLs is the ordinary case rather than a Dutch quirk, so every key is returned
    and the caller keeps whichever one groups.
    """

    slugs = frozenset({"netherlands", "india", "germany"})
    india = country_family_keys(
        "https://x.nl/visa-the-netherlands/schengen-visa/apply-india", slugs
    )
    germany = country_family_keys(
        "https://x.nl/visa-the-netherlands/schengen-visa/apply-germany", slugs
    )

    assert len(india) == 2, india
    assert set(india) & set(germany) == {"https://x.nl/visa-the-netherlands/schengen-visa/apply-{}"}


@pytest.mark.anyio
async def test_a_higher_scoring_family_cannot_take_the_whole_reservation() -> None:
    """The failure the first build of this actually shipped, frozen so it cannot come back.

    Reserved budget in one score-ordered pool is not a reservation: measured against the real
    Netherlands on 2026-08-27 it read 131 `consular-fees/{country}` pages and **zero**
    `apply-{country}` pages, because a fee anchor scores 12.0 and an apply anchor 8.0. Only the
    apply page is a gateway, and nothing tells them apart before one is opened — so every family
    gets its turn instead.
    """

    requests: list[str] = []
    crawler = build(requests, family_slugs=SLUGS, family_share=0.5)

    await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    opened = set(requests)
    assert opened & {fee_page(c) for c in COUNTRIES}, "the higher-scoring family was not read"
    assert opened & {apply_page(c) for c in COUNTRIES}, "the lower-scoring family was starved"


@pytest.mark.anyio
async def test_a_family_that_is_not_visa_guidance_gets_no_reserved_budget() -> None:
    """The regression this gate exists to prevent, on the other nine countries.

    Canada's largest country family is `travel.gc.ca/destinations/{}` at 176 members and Japan's are
    country-relations pages at 141, and neither is guidance for a traveller applying for anything.
    Members cannot be told apart by score — scoring at the floor is the defect being fixed — so the
    shared address decides.
    """

    requests: list[str] = []
    crawler = build(
        requests,
        family_slugs=SLUGS,
        family_share=0.5,
        family_pattern=re.compile(r"nothing-matches-this"),
    )

    await crawler.crawl(target(), [INDEX])  # type: ignore[arg-type]

    assert not set(requests) & {apply_page(c) for c in COUNTRIES}


def test_the_shipped_pattern_keeps_the_dutch_family_and_drops_the_canadian_one() -> None:
    """Real keys from the two corpora, so the pattern is checked against what it must sort."""

    keep = "https://www.netherlandsworldwide.nl/visa-the-netherlands/schengen-visa/apply-{}"
    also_keep = "https://www.netherlandsworldwide.nl/consular-fees/{}"
    drop = "https://travel.gc.ca/destinations/{}"
    also_drop = "https://www.mofa.go.jp/region/europe/{}/index.html"

    assert CORPUS_FAMILY_PATTERN.search(keep)
    assert CORPUS_FAMILY_PATTERN.search(also_keep)
    assert not CORPUS_FAMILY_PATTERN.search(drop)
    assert not CORPUS_FAMILY_PATTERN.search(also_drop)
