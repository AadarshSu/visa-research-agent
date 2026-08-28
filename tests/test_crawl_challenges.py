"""Answering a browser challenge during a crawl, and knowing when to stop trying.

DECISIONS entry 41 settled the principle: a challenge states no policy, so answering one by running
the page's own scripts **under our own user agent** misrepresents nothing. Entry 75 built it and
entry 92 found that the offline corpus build had the renderer all along and twelve renders to
spend — France met 64 challenges with twelve, and the rest were recorded as unanswerable when they
were merely unafforded.

Raising the budget alone would have traded that for a worse failure, so the second half of these
tests is the per-host give-up: a host whose challenge we genuinely cannot answer must cost three
renders, not four hundred.

Offline throughout, against a fake site and a fake renderer.
"""

import httpx
import pytest
from discovery_site import destination

from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.domain.models import DestinationConfig
from visa_research_agent.research.rendering import RenderedPage

AUTHORITY = "immigration.gov.example"
CHALLENGE = (
    '<!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title>'
    '<script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1"></script>'
)
GUARDED = (
    "<html><body><h1>Visa requirements</h1><p>The guidance behind the challenge.</p></body></html>"
)


class CountingRenderer:
    """A browser that answers the challenge, or never does, and counts how often it was asked."""

    def __init__(self, html: str | None) -> None:
        self.html = html
        self.calls: list[str] = []

    async def render(
        self,
        url: str,
        destination: DestinationConfig,
        *,
        settle_milliseconds: int | None = None,
        awaiting_challenge: bool = False,
    ) -> RenderedPage | None:
        self.calls.append(url)
        return None if self.html is None else RenderedPage(final_url=url, html=self.html)


async def sleep_none(_: float) -> None:
    return None


def challenging_site(*, status: int = 403, body: str = CHALLENGE) -> httpx.MockTransport:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /\n")
        return httpx.Response(
            status, text=body, headers={"Content-Type": "text/html; charset=utf-8"}
        )

    return httpx.MockTransport(respond)


def fetcher(
    renderer: CountingRenderer | None,
    *,
    transport: httpx.MockTransport,
    maximum_renders: int = 400,
    failures_per_host: int = 3,
) -> CrawlFetcher:
    return CrawlFetcher(
        transport=transport,
        sleep=sleep_none,
        host_delay_seconds=0.0,
        renderer=renderer,
        maximum_renders=maximum_renders,
        challenge_failures_per_host=failures_per_host,
        challenge_settle_milliseconds=1,
    )


async def read(crawl: CrawlFetcher, url: str) -> str | None:
    """One page through the crawl fetcher, with the client it expects."""

    async with httpx.AsyncClient(transport=crawl.transport) as client:
        return await crawl.fetch_html(client, url, destination())


@pytest.mark.anyio
async def test_a_challenge_is_answered_and_the_guarded_page_comes_back() -> None:
    """Entry 41's decision, exercised through the crawl rather than the request path."""

    renderer = CountingRenderer(GUARDED)
    crawl = fetcher(renderer, transport=challenging_site())
    html = await read(crawl, f"https://{AUTHORITY}/visa")

    assert html is not None
    assert "The guidance behind the challenge" in html
    assert renderer.calls == [f"https://{AUTHORITY}/visa"]


@pytest.mark.anyio
async def test_a_host_that_never_answers_costs_three_renders_not_the_whole_budget() -> None:
    """The failure raising the budget would otherwise have bought. `urm.lt` fingerprints past our
    user agent (entry 75), so every render against it fails at up to the full settle — at 400
    renders that is hours of a build spent proving the same thing four hundred times."""

    renderer = CountingRenderer(None)
    crawl = fetcher(renderer, transport=challenging_site())
    for page in range(10):
        assert await read(crawl, f"https://{AUTHORITY}/page-{page}") is None

    assert len(renderer.calls) == 3


@pytest.mark.anyio
async def test_a_render_that_returns_the_challenge_again_counts_as_a_failure() -> None:
    """The renderer answering with the interstitial is the ordinary way a challenge fails — the
    poll in `_wait_out_challenge` returns whatever the page last held when its deadline passes. If
    that counted as a success the give-up would never fire and the page would read as fetched."""

    renderer = CountingRenderer(CHALLENGE)
    crawl = fetcher(renderer, transport=challenging_site())
    for page in range(10):
        await read(crawl, f"https://{AUTHORITY}/page-{page}")

    assert len(renderer.calls) == 3


@pytest.mark.anyio
async def test_one_page_that_answers_clears_the_host() -> None:
    """Three consecutive failures is a property of the host; three scattered ones is a slow site.
    A site that mostly passes must never be written off, so a success resets the count."""

    class Flaky(CountingRenderer):
        async def render(
            self,
            url: str,
            destination: DestinationConfig,
            *,
            settle_milliseconds: int | None = None,
            awaiting_challenge: bool = False,
        ) -> RenderedPage | None:
            self.calls.append(url)
            # Fails twice, answers, then fails again — never three in a row.
            failed = len(self.calls) % 3
            return None if failed else RenderedPage(final_url=url, html=GUARDED)

    renderer = Flaky(GUARDED)
    crawl = fetcher(renderer, transport=challenging_site())
    for page in range(9):
        await read(crawl, f"https://{AUTHORITY}/page-{page}")

    assert len(renderer.calls) == 9


@pytest.mark.anyio
async def test_a_genuine_refusal_is_never_rendered_past() -> None:
    """The line entry 41 draws and this change does not move. Akamai's `403` states a decision, so
    there is nothing to answer and the renderer must not be asked."""

    refusal = (
        "<HTML><HEAD> <TITLE>Access Denied</TITLE> </HEAD><BODY> <H1>Access Denied</H1> "
        'You don&#39;t have permission to access "/" on this server.'
    )
    renderer = CountingRenderer(GUARDED)
    crawl = fetcher(renderer, transport=challenging_site(body=refusal))

    assert await read(crawl, f"https://{AUTHORITY}/visa") is None
    assert renderer.calls == []


@pytest.mark.anyio
async def test_a_rate_limit_is_never_rendered_past_either() -> None:
    """A `429` is transient and "try again later" is the honest advice (entry 32). Rendering past it
    would be the retry the rules forbid, wearing a browser."""

    renderer = CountingRenderer(GUARDED)
    crawl = fetcher(renderer, transport=challenging_site(status=429))

    assert await read(crawl, f"https://{AUTHORITY}/visa") is None
    assert renderer.calls == []


@pytest.mark.anyio
async def test_the_render_budget_still_bounds_the_whole_crawl() -> None:
    """The per-host give-up is a second bound, not a replacement: a country with many challenging
    hosts must still stop somewhere."""

    renderer = CountingRenderer(None)
    crawl = fetcher(renderer, transport=challenging_site(), maximum_renders=2)
    for page in range(10):
        await read(crawl, f"https://{AUTHORITY}/page-{page}")

    assert len(renderer.calls) == 2
