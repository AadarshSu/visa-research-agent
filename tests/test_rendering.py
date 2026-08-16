"""Reading pages whose text only appears once their scripts have run.

No test here starts a browser. Rendering sits behind the `PageRenderer` protocol precisely so a
fake can be injected, in the same way `httpx.MockTransport` stands in for the network elsewhere.
The one test that does drive real Chromium is skipped unless `VISA_RENDER_MANUAL=1` is set.
"""

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

    async def render(self, url: str, destination: DestinationConfig) -> RenderedPage | None:
        self.calls.append(url)
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
    """

    renderer = FakeRenderer(shell("<p>Loading</p>"))
    fetcher = build_fetcher(tmp_path, shell(), renderer)
    fetcher.maximum_renders = 1

    await fetcher.fetch(destination())
    await fetcher.fetch(destination())

    assert renderer.calls == [SOURCE_URL], "the second fetch must not render again"


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


def test_the_committed_policy_does_not_start_a_browser_by_default() -> None:
    from visa_research_agent.config.loader import load_runtime_policy

    assert load_runtime_policy().render_mode == "never"


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
