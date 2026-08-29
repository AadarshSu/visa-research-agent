"""Reading pages whose text only appears once their scripts have run.

No test here starts a browser. Rendering sits behind the `PageRenderer` protocol precisely so a
fake can be injected, in the same way `httpx.MockTransport` stands in for the network elsewhere.
The one test that does drive real Chromium is skipped unless `VISA_RENDER_MANUAL=1` is set.
"""

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from discovery_site import AUTHORITY, DETAIL_INDIA, SPA_PORTAL, handler, spa_rendered
from discovery_site import destination as crawl_destination
from pydantic import AnyHttpUrl

from visa_research_agent.discovery.crawl import CrawlFetcher, extract_links
from visa_research_agent.domain.models import (
    ConfiguredSource,
    DestinationConfig,
    FetchedSource,
    RuntimePolicy,
    SourceFailure,
    is_challenge,
)
from visa_research_agent.research.live_sources import LiveSourceFetcher, looks_untranslated
from visa_research_agent.research.rendering import (
    RenderedPage,
    build_page_renderer,
    is_render_request_allowed,
)
from visa_research_agent.research.source_cache import FileSourceCache

pytestmark = pytest.mark.anyio

SOURCE_URL = "https://immigration.gov.example/visa/india"
GUIDANCE = "Indian passport holders require an entry visa for tourism. " * 30

# Exactly the shape Vietnam's immigration department returns: translation keys, not sentences,
# with the strings themselves fetched client-side. Over the 400-character floor, and useless.
PLACEHOLDER_TEXT = "\n".join(
    [
        "home.banner-huong-dan-viet-nam",
        "home.banner-huong-dan-nuoc-ngoai",
        "lienKet",
        "Link website",
        "cacDonViTrucThuoc",
        "vanBanQuyPhamPhapLuat",
        "xemToanBo",
        "thuTucHanhChinh",
        "home.tin-tuc-su-kien",
        "home.thong-bao-moi",
        "hoiDapPhapLuat",
        "home.lien-he-gop-y",
        "danhSachVanBan",
        "home.footer-dia-chi",
        "bieuMauToKhai",
        "home.header-tim-kiem",
        "home.gioi-thieu-chung",
        "coCauToChuc",
        "home.van-ban-dieu-hanh",
        "thongTinTuyenTruyen",
        "home.dich-vu-cong-truc-tuyen",
        "duLieuMoTaChung",
        "home.cau-hoi-thuong-gap",
        "lichTiepCongDan",
    ]
)


def shell(body: str = '<div id="app"></div>') -> str:
    return (
        f"<html><head><title>Visa</title></head><body>{body}<script>boot()</script></body></html>"
    )


def page(text: str) -> str:
    return f"<html><head><title>Visa</title></head><body><main><p>{text}</p></main></body></html>"


def destination_with_sources(count: int) -> DestinationConfig:
    """The same destination with `count` primary sources, all of them shells needing a render."""

    return DestinationConfig(
        slug="testland",
        display_name="Testland",
        route_type="national",
        implementation_status="available",
        trusted_domains=["immigration.gov.example"],
        sources=[
            ConfiguredSource(
                source_id=f"tl_visa_documents_{index}",
                title=f"Testland Visa Documents {index}",
                url=AnyHttpUrl(f"{SOURCE_URL}/{index}"),
                authority="Testland Immigration Authority",
                kind="immigration_authority",
                research_pass="primary",
            )
            for index in range(count)
        ],
    )


def destination() -> DestinationConfig:
    return DestinationConfig(
        slug="testland",
        display_name="Testland",
        route_type="national",
        implementation_status="available",
        trusted_domains=["immigration.gov.example"],
        sources=[
            ConfiguredSource(
                source_id="tl_visa_documents",
                title="Testland Visa Documents",
                url=AnyHttpUrl(SOURCE_URL),
                authority="Testland Immigration Authority",
                kind="immigration_authority",
                research_pass="primary",
            )
        ],
    )


class FakeRenderer:
    """Stands in for a browser, recording what it was asked to render."""

    def __init__(self, html: str | None, *, final_url: str = SOURCE_URL) -> None:
        self.html = html
        self.final_url = final_url
        self.calls: list[str] = []
        self.settles: list[int | None] = []

    async def render(
        self,
        url: str,
        destination: DestinationConfig,
        *,
        settle_milliseconds: int | None = None,
        awaiting_challenge: bool = False,
    ) -> RenderedPage | None:
        self.calls.append(url)
        self.settles.append(settle_milliseconds)
        if self.html is None:
            return None
        return RenderedPage(final_url=self.final_url, html=self.html)


def build_fetcher(
    tmp_path: Path,
    body: str,
    renderer: FakeRenderer | None = None,
    *,
    content_type: str = "text/html; charset=utf-8",
) -> LiveSourceFetcher:
    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=body, headers={"Content-Type": content_type})

    return LiveSourceFetcher(
        FileSourceCache(tmp_path / "cache"),
        ttl_hours=24.0,
        maximum_stale_hours=168.0,
        timeout_seconds=5.0,
        concurrency=2,
        maximum_characters=50_000,
        minimum_characters=400,
        user_agent="test-agent",
        renderer=renderer,
        transport=httpx.MockTransport(respond),
        now=lambda: datetime(2026, 8, 15, 9, 0, tzinfo=UTC),
    )


async def only_result(fetcher: LiveSourceFetcher) -> FetchedSource | SourceFailure:
    report = await fetcher.fetch(destination())
    results: list[FetchedSource | SourceFailure] = [*report.fetched, *report.failures]
    assert len(results) == 1
    return results[0]


# --- the trust rule, which rendering must not move -----------------------------------------


def test_a_page_may_fetch_from_its_own_approved_domain() -> None:
    assert is_render_request_allowed(SOURCE_URL, destination())
    assert is_render_request_allowed("https://immigration.gov.example/app.js", destination())


def test_a_page_may_not_fetch_a_script_from_anywhere_else() -> None:
    # The point of checking subresources: a third-party script is not evidence, but it decides
    # what the evidence says.
    assert not is_render_request_allowed("https://cdn.example/bundle.js", destination())
    assert not is_render_request_allowed("https://cheap-visas.example/apply", destination())


def test_hostless_urls_the_browser_uses_internally_are_allowed() -> None:
    for url in ("about:blank", "data:text/html,<p>x</p>", "blob:https://x/1"):
        assert is_render_request_allowed(url, destination())


def test_an_unrecognisable_url_is_refused_rather_than_waved_through() -> None:
    assert not is_render_request_allowed("chrome-extension://abc/inject.js", destination())


# --- translation placeholders --------------------------------------------------------------


def test_translation_keys_are_recognised_as_unreadable() -> None:
    assert looks_untranslated(PLACEHOLDER_TEXT)


def test_ordinary_guidance_is_not_mistaken_for_placeholders() -> None:
    assert not looks_untranslated(GUIDANCE)


def test_a_short_page_of_headings_is_not_mistaken_for_placeholders() -> None:
    # Real pages carry a few unspaced tokens — a filename, a code. A handful must not be enough.
    assert not looks_untranslated("Visa\nDocuments required\npassport.pdf\nApply in person")


# --- retrieval -----------------------------------------------------------------------------


async def test_a_readable_page_is_never_rendered(tmp_path: Path) -> None:
    renderer = FakeRenderer(page(GUIDANCE))
    result = await only_result(build_fetcher(tmp_path, page(GUIDANCE), renderer))

    assert isinstance(result, FetchedSource)
    assert renderer.calls == [], "rendering must cost nothing on pages that already work"


async def test_a_client_rendered_page_becomes_usable_once_rendered(tmp_path: Path) -> None:
    renderer = FakeRenderer(page(GUIDANCE))
    result = await only_result(build_fetcher(tmp_path, shell(), renderer))

    assert isinstance(result, FetchedSource)
    assert "Indian passport holders require an entry visa" in result.content
    assert renderer.calls == [SOURCE_URL]


async def test_placeholder_text_triggers_rendering(tmp_path: Path) -> None:
    body = page(PLACEHOLDER_TEXT.replace("\n", "</p><p>"))
    renderer = FakeRenderer(page(GUIDANCE))
    result = await only_result(build_fetcher(tmp_path, body, renderer))

    assert isinstance(result, FetchedSource)
    assert renderer.calls == [SOURCE_URL], "clearing the floor is not the same as being readable"


async def test_a_page_that_is_still_thin_after_rendering_stays_unusable(tmp_path: Path) -> None:
    renderer = FakeRenderer(shell("<p>Loading</p>"))
    result = await only_result(build_fetcher(tmp_path, shell(), renderer))

    assert isinstance(result, SourceFailure)
    assert result.outcome == "unusable"
    assert "too little readable text" in result.detail


async def test_placeholders_are_refused_when_rendering_cannot_rescue_them(
    tmp_path: Path,
) -> None:
    body = page(PLACEHOLDER_TEXT.replace("\n", "</p><p>"))
    result = await only_result(build_fetcher(tmp_path, body, FakeRenderer(None)))

    assert isinstance(result, SourceFailure)
    assert result.outcome == "unusable"
    assert "translation placeholders" in result.detail


async def test_rendering_that_navigates_off_the_approved_domains_is_untrusted(
    tmp_path: Path,
) -> None:
    renderer = FakeRenderer(page(GUIDANCE), final_url="https://cheap-visas.example/apply")
    result = await only_result(build_fetcher(tmp_path, shell(), renderer))

    assert isinstance(result, SourceFailure)
    assert result.outcome == "untrusted"
    assert "cheap-visas.example" in result.detail
    # The content the renderer produced must not survive the refusal in any form.
    assert "Indian passport holders" not in result.detail


async def test_a_pdf_is_never_handed_to_the_renderer(tmp_path: Path) -> None:
    renderer = FakeRenderer(page(GUIDANCE))
    fetcher = build_fetcher(tmp_path, "%PDF-1.4 broken", renderer, content_type="application/pdf")
    result = await only_result(fetcher)

    assert isinstance(result, SourceFailure)
    assert renderer.calls == []


async def test_without_a_renderer_behaviour_is_exactly_what_it_was(tmp_path: Path) -> None:
    result = await only_result(build_fetcher(tmp_path, shell(), renderer=None))

    assert isinstance(result, SourceFailure)
    assert result.outcome == "unusable"


async def test_retrieval_stops_rendering_once_its_own_allowance_is_spent(
    tmp_path: Path,
) -> None:
    """Retrieval's budget is its own, not one it shares with discovery's crawl.

    A shared count let a crawl spend everything before the shortlist — the pages that actually
    become evidence — was read, so a working renderer produced no evidence at all.

    Spent *within* one run, which is the scope the allowance claims: three shells, two renders.
    """

    renderer = FakeRenderer(shell("<p>Loading</p>"))
    fetcher = build_fetcher(tmp_path, shell(), renderer)
    fetcher.maximum_renders = 2

    await fetcher.fetch(destination_with_sources(3))

    assert len(renderer.calls) == 2, "the third source must not render"


async def test_each_fetch_gets_the_whole_render_allowance_again(tmp_path: Path) -> None:
    """The allowance is per run, and one `LiveSourceFetcher` serves every run the server answers.

    `get_visa_plan_service` is an `lru_cache(maxsize=1)`, so before this the count was spent once
    and never given back: after the first few requests needing a browser, every client-rendered
    page came back "too little readable text to trust" for the life of the process — a reason that
    was not true of what was seen, because the page had not been read. See DECISIONS entry 37.
    """

    renderer = FakeRenderer(shell("<p>Loading</p>"))
    fetcher = build_fetcher(tmp_path, shell(), renderer)
    fetcher.maximum_renders = 1

    for _ in range(4):
        await fetcher.fetch(destination())

    assert len(renderer.calls) == 4, "every fetch must start with a fresh allowance"


async def test_two_runs_in_flight_together_cannot_spend_each_other_s_allowance(
    tmp_path: Path,
) -> None:
    """Concurrency is why the budget is a value passed down rather than a counter reset on entry.

    Resetting `self.renders` at the top of `fetch` would look equivalent, but two requests
    overlapping — the normal case for a server — would each clear the other's count, so a run
    could render well past its limit. Two concurrent runs of two sources each must render exactly
    four times, never more.
    """

    renderer = FakeRenderer(shell("<p>Loading</p>"))
    fetcher = build_fetcher(tmp_path, shell(), renderer)
    fetcher.maximum_renders = 2

    await asyncio.gather(
        fetcher.fetch(destination_with_sources(3)),
        fetcher.fetch(destination_with_sources(3)),
    )

    assert len(renderer.calls) == 4


# --- discovery's crawl ---------------------------------------------------------------------


async def sleep_none(_: float) -> None:
    return None


def build_crawl_fetcher(renderer: FakeRenderer | None) -> CrawlFetcher:
    return CrawlFetcher(
        transport=httpx.MockTransport(handler([])),  # type: ignore[arg-type]
        sleep=sleep_none,
        host_delay_seconds=0.0,
        renderer=renderer,
    )


async def crawl_html(fetcher: CrawlFetcher, url: str) -> str | None:
    async with httpx.AsyncClient(transport=fetcher.transport, follow_redirects=True) as client:
        return await fetcher.fetch_html(client, url, crawl_destination())


async def test_a_shell_with_no_links_is_rendered_for_the_crawler() -> None:
    renderer = FakeRenderer(spa_rendered(), final_url=SPA_PORTAL)
    html = await crawl_html(build_crawl_fetcher(renderer), SPA_PORTAL)

    assert html is not None
    assert renderer.calls == [SPA_PORTAL]
    found = {link.url for link in extract_links(html, SPA_PORTAL)}
    assert DETAIL_INDIA in found, "the crawler learns nothing from a shell until it is rendered"


async def test_a_page_that_already_has_links_is_not_rendered() -> None:
    renderer = FakeRenderer(spa_rendered())
    html = await crawl_html(build_crawl_fetcher(renderer), f"https://{AUTHORITY}/visa/index.html")

    assert html is not None
    assert renderer.calls == []


async def test_crawl_rendering_that_leaves_the_approved_domains_drops_the_page() -> None:
    renderer = FakeRenderer(spa_rendered(), final_url="https://cheap-visas.example/apply")
    fetcher = build_crawl_fetcher(renderer)
    html = await crawl_html(fetcher, SPA_PORTAL)

    assert html is None
    assert "off the approved domains" in fetcher.failures[SPA_PORTAL]


async def test_the_crawl_stops_rendering_once_its_own_allowance_is_spent() -> None:
    renderer = FakeRenderer(spa_rendered(), final_url=SPA_PORTAL)
    fetcher = build_crawl_fetcher(renderer)
    fetcher.maximum_renders = 1

    await crawl_html(fetcher, SPA_PORTAL)
    await crawl_html(fetcher, SPA_PORTAL)

    assert renderer.calls == [SPA_PORTAL]


async def test_a_shell_is_kept_as_found_when_there_is_no_renderer() -> None:
    fetcher = build_crawl_fetcher(None)
    html = await crawl_html(fetcher, SPA_PORTAL)

    # Unreadable, but not a failure: the crawler simply finds nothing to follow, exactly as before.
    assert html is not None
    assert extract_links(html, SPA_PORTAL) == []
    assert SPA_PORTAL not in fetcher.failures


async def test_links_resolve_against_where_the_request_landed() -> None:
    """A redirected page's relative links must not resolve against the URL that was asked for."""

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/visa":
            return httpx.Response(301, headers={"Location": f"https://{AUTHORITY}/en/visa/"})
        return httpx.Response(
            200,
            text='<html><body><h1>Visa</h1><a href="india.html">India</a>'
            '<a href="china.html">China</a><a href="/a">A</a><a href="/b">B</a>'
            '<a href="/c">C</a></body></html>',
            headers={"Content-Type": "text/html"},
        )

    fetcher = CrawlFetcher(
        transport=httpx.MockTransport(respond), sleep=sleep_none, host_delay_seconds=0.0
    )
    requested = f"https://{AUTHORITY}/visa"
    html = await crawl_html(fetcher, requested)

    assert html is not None
    assert fetcher.final_urls[requested] == f"https://{AUTHORITY}/en/visa/"
    found = {link.url for link in extract_links(html, fetcher.final_urls[requested])}
    assert f"https://{AUTHORITY}/en/visa/india.html" in found


# --- policy --------------------------------------------------------------------------------


def policy(render_mode: str) -> RuntimePolicy:
    return RuntimePolicy.model_validate(
        {
            "schema_version": 1,
            "source_mode": "live",
            "extraction_mode": "fixture",
            "render_mode": render_mode,
            "source_cache_ttl_hours": 24.0,
            "source_maximum_stale_hours": 168.0,
        }
    )


def test_no_renderer_is_built_when_the_policy_says_never() -> None:
    assert build_page_renderer(policy("never")) is None


def test_the_committed_policy_renders_on_demand_and_that_is_deliberate() -> None:
    """The committed policy is a decision, so it is pinned in both directions.

    It was `never` until 2026-08-25, when answering a **challenge** became the reason to start a
    browser: a challenge is a capability test rather than a refusal, and Cyprus and Slovakia lose
    their entire trusted sets to one. DECISIONS entries 41, 73 and 75.

    `on_demand` still never renders a page that already works, and it is never pointed at a genuine
    refusal — that distinction lives in `is_challenge`, not here.
    """

    from visa_research_agent.config.loader import load_runtime_policy

    assert load_runtime_policy().render_mode == "on_demand"


# --- the one check that needs a real browser -----------------------------------------------


@pytest.mark.manual
@pytest.mark.skipif(
    os.environ.get("VISA_RENDER_MANUAL") != "1",
    reason="starts a real browser and reaches the network; run deliberately",
)
async def test_a_real_browser_runs_the_scripts_on_a_page() -> None:
    """Proves the Playwright renderer works end to end, without leaving the machine.

    Deliberately local: this must never depend on a government site being up, and the trust rules
    it has to honour are covered by the fake-renderer tests above.
    """

    from visa_research_agent.research.rendering import PlaywrightPageRenderer

    document = (
        "data:text/html,<html><body><div id='app'></div>"
        "<script>document.getElementById('app').textContent='Rendered guidance';</script>"
        "</body></html>"
    )
    config = DestinationConfig(
        slug="local",
        display_name="Local",
        route_type="national",
        implementation_status="available",
    )
    renderer = PlaywrightPageRenderer(user_agent="test-agent", settle_milliseconds=200)
    try:
        rendered = await renderer.render(document, config)
    finally:
        await renderer.aclose()

    assert rendered is not None
    assert "Rendered guidance" in rendered.html


# --- an authority that refuses automated retrieval -------------------------------------------


async def test_a_refused_request_is_blocked_rather_than_unreachable(tmp_path: Path) -> None:
    """A `403` is the authority declining this client, not a fault and not missing guidance.

    The distinction is the whole point: "unreachable" invites a reader to conclude the site is
    broken, and neither outcome may ever be softened into an inference from some other page.
    """

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Checking if the site connection is secure")

    fetcher = build_fetcher(tmp_path, "")
    fetcher.transport = httpx.MockTransport(respond)
    result = await only_result(fetcher)

    assert isinstance(result, SourceFailure)
    assert result.outcome == "blocked"
    assert "refused automated retrieval" in result.detail
    assert "could not be independently verified here" in result.detail


async def test_a_blocked_page_is_never_rendered_to_get_around_the_block(tmp_path: Path) -> None:
    """Rendering must not become the way past a refusal.

    A headless browser would very likely pass these checks. Pointing it at them would make the
    architecture "if they block us, defeat the block", which this project deliberately refuses.
    """

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Access denied")

    renderer = FakeRenderer(page(GUIDANCE))
    fetcher = build_fetcher(tmp_path, "", renderer)
    fetcher.transport = httpx.MockTransport(respond)
    result = await only_result(fetcher)

    assert isinstance(result, SourceFailure)
    assert result.outcome == "blocked"
    assert renderer.calls == [], "a refusal must not be worked around with a browser"


async def test_a_crawl_records_a_refusal_in_its_own_words() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="Too many requests")

    fetcher = CrawlFetcher(
        transport=httpx.MockTransport(respond), sleep=sleep_none, host_delay_seconds=0.0
    )
    url = f"https://{AUTHORITY}/visa/index.html"
    html = await crawl_html(fetcher, url)

    assert html is None
    assert "refused automated retrieval" in fetcher.failures[url]


# --- telling a challenge apart from a refusal ------------------------------------------------


AZURE_CHALLENGE = (
    '<!doctype html><html><head><meta charset="utf-8"/>'
    '<meta name="description" content="Azure WAF JS Challenge"/><title>Azure WAF</title>'
)
CLOUDFLARE_CHALLENGE = (
    '<!DOCTYPE html><html lang="en-US"><head><title>One moment please</title>'
    '<script>window._cf_chl_opt={cvId:"3",cType:"managed"};</script>'
    '<script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1"></script>'
)
CLOUDFLARE_BLOCK = (
    '<!DOCTYPE html><html lang="en-US"><head><title>Attention Required! | Cloudflare</title>'
    '<script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1"></script></head>'
    "<body><h1>Sorry, you have been blocked</h1><h2>You are unable to access travel.state.gov</h2>"
    "<p>This website is using a security service to protect itself from online attacks.</p>"
)
"""What `travel.state.gov` really answers, taken from the page on 2026-08-29 (entry 109).

It shares `cdn-cgi/challenge-platform` with a genuine Cloudflare challenge and shares **nothing
else**: no `cf-mitigated` header, no `_cf_chl_opt`, no invitation to enable JavaScript, and no
script to run. It states that the client is blocked, which is the authority saying something.
"""

AKAMAI_REFUSAL = (
    "<HTML><HEAD> <TITLE>Access Denied</TITLE> </HEAD><BODY> <H1>Access Denied</H1> "
    'You don&#39;t have permission to access "http://www.mfa.gr/" on this server.'
)


def test_cloudflares_block_page_is_a_refusal_not_a_challenge() -> None:
    """The defect entry 109 found, as one assertion.

    `cdn-cgi/challenge-platform` was a challenge marker, and it appears on Cloudflare's **block**
    page as well as its challenge page. So `travel.state.gov` — "Sorry, you have been blocked" — was
    read as a capability test, the renderer was pointed at a page an authority had refused (which
    DECISIONS entry 18 forbids outright), and the corpus recorded the false reason "it asked this
    client to prove it is a browser".

    The block page still carries that marker here on purpose: the guard has to hold *because* the
    page says it blocked us, not because the marker went away.
    """

    assert not is_challenge(403, {}, CLOUDFLARE_BLOCK)
    assert not is_challenge(403, {"cf-mitigated": "challenge"}, CLOUDFLARE_BLOCK), (
        "a stated block outranks any header claiming otherwise"
    )
    assert is_challenge(403, {}, CLOUDFLARE_CHALLENGE), "a real challenge is still answered"


def test_cloudflare_declares_a_challenge_in_a_header() -> None:
    assert is_challenge(403, {"cf-mitigated": "challenge"}, "")


def test_azure_declares_a_challenge_only_in_the_body() -> None:
    """The half a header-only test misses, which is how Cyprus was called a refusal for half a day.

    `www.gov.cy` answers `403` from Azure Front Door and sets no `cf-mitigated` header at all.
    DECISIONS entry 73.
    """

    assert is_challenge(403, {}, AZURE_CHALLENGE)
    assert is_challenge(403, {}, CLOUDFLARE_CHALLENGE)


def test_a_genuine_refusal_is_not_read_as_a_challenge() -> None:
    """The line this must not cross.

    Greece's `www.mfa.gr` answers an Akamai "Access Denied" with no script to run and no question
    asked. It is an authority saying no, it stays `blocked`, and the renderer is never pointed at
    it — widening the markers until this matched would turn DECISIONS entry 18 into its opposite.
    """

    assert not is_challenge(403, {}, AKAMAI_REFUSAL)
    assert not is_challenge(403, {}, "")
    assert not is_challenge(429, {"cf-mitigated": "challenge"}, "")


def test_a_successful_page_is_never_a_challenge_however_it_reads() -> None:
    """A page may discuss Cloudflare, or embed its script, and still be the guidance itself."""

    assert not is_challenge(200, {"cf-mitigated": "challenge"}, CLOUDFLARE_CHALLENGE)
    assert not is_challenge(404, {}, AZURE_CHALLENGE)
