"""Reading pages whose text only exists after their scripts have run.

Some authorities publish an application shell and fetch the guidance client-side. Vietnam's e-visa
portal returns 39 readable characters; its immigration department returns translation keys rather
than sentences. Neither is an empty requirement list, and neither can be reached by fetching harder.

Rendering is the narrow remedy, and it is deliberately hemmed in:

  * it runs **only** when an ordinary fetch has already failed to produce readable text, so the
    pages that work today are never slowed down or exposed to a browser;
  * it widens nothing. Every request the page makes, document or subresource, is aborted unless its
    host is already trusted for this destination, so no byte from an unapproved domain can
    influence what is read;
  * the landing URL is re-checked after rendering exactly as retrieval re-checks after a redirect.

The renderer is a protocol so tests can inject a fake one. Only the opt-in manual check ever starts
a real browser; see `tests/test_rendering.py`.
"""

from types import TracebackType
from typing import TYPE_CHECKING, Protocol

from visa_research_agent.config.settings import settings
from visa_research_agent.domain.models import DestinationConfig, RuntimePolicy, StrictModel
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.errors import VisaResearchError

if TYPE_CHECKING:  # pragma: no cover - imported for typing only, never at runtime.
    from playwright.async_api import Browser, Playwright, Route


class RenderConfigurationError(VisaResearchError):
    """Raised when rendering is selected as policy but cannot be provided safely."""


class RenderedPage(StrictModel):
    """The HTML a page settled on once its scripts had run."""

    final_url: str
    html: str
    blocked_hosts: list[str] = []
    """Hosts whose requests were refused, so a thin result can say what was withheld."""


class PageRenderer(Protocol):
    async def render(self, url: str, destination: DestinationConfig) -> RenderedPage | None:
        """Return the settled HTML for one URL, or None when it could not be rendered."""
        ...


def is_render_request_allowed(url: str, destination: DestinationConfig) -> bool:
    """True when a page may fetch this URL while rendering.

    This is the trust rule, unchanged and applied to every request the browser makes rather than
    only to navigations. A third-party script is not evidence, but it decides what the evidence
    says, so allowing one would widen trust by the back door.
    """

    host = host_of(url)
    if not host:
        # about:blank, data: and blob: URLs have no host and never reach the network.
        return url.startswith(("about:", "data:", "blob:"))
    return destination.trusts_host(host)


class PlaywrightPageRenderer:
    """Render pages in a headless Chromium, one browser per run.

    The browser is started on first use rather than at construction, so selecting the policy costs
    nothing on a run where every page turns out to be readable.
    """

    def __init__(
        self,
        *,
        user_agent: str,
        timeout_seconds: float = 20.0,
        settle_milliseconds: int = 2_500,
        maximum_renders: int = 40,
    ) -> None:
        try:
            import playwright.async_api  # noqa: F401
        except ImportError as exc:  # pragma: no cover - depends on the install, not the logic.
            raise RenderConfigurationError(
                "rendering is enabled but Playwright is not installed. Install the optional "
                'extra with `pip install -e ".[render]"` and then `playwright install chromium`, '
                "or set render_mode: never in config/runtime.yaml"
            ) from exc

        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.settle_milliseconds = settle_milliseconds
        # A last-resort ceiling on one browser's lifetime, not the working budget. Each caller
        # holds its own smaller allowance, because a single shared count let the crawl spend
        # everything before retrieval — the phase that actually produces evidence — got a turn.
        self.maximum_renders = maximum_renders
        self.renders = 0
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None

    async def __aenter__(self) -> "PlaywrightPageRenderer":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def _ensure_browser(self) -> "Browser":
        if self._browser is None:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
        return self._browser

    async def render(self, url: str, destination: DestinationConfig) -> RenderedPage | None:
        from playwright.async_api import Error as PlaywrightError

        if self.renders >= self.maximum_renders:
            return None
        if not is_render_request_allowed(url, destination):
            # Belt and braces: callers check first, but a renderer that could be handed an
            # arbitrary URL is one refactor away from being a trust hole.
            return None

        self.renders += 1
        browser = await self._ensure_browser()
        context = await browser.new_context(
            user_agent=self.user_agent,
            locale="en-GB",
            accept_downloads=False,
        )
        blocked: dict[str, None] = {}

        async def gate(route: "Route") -> None:
            target = route.request.url
            if is_render_request_allowed(target, destination):
                await route.continue_()
                return
            blocked.setdefault(host_of(target) or target[:60], None)
            await route.abort()

        try:
            await context.route("**/*", gate)
            # Dialogs are left unhandled deliberately: Playwright dismisses them automatically
            # when nothing is listening, and a modal nobody answers would block the load forever.
            page = await context.new_page()
            timeout_ms = self.timeout_seconds * 1_000
            try:
                await page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
                try:
                    await page.wait_for_load_state("networkidle", timeout=timeout_ms)
                except PlaywrightError:
                    # A page that polls never goes idle. Its content is usually already in
                    # place, so take what settled rather than discarding the whole render.
                    pass
                await page.wait_for_timeout(self.settle_milliseconds)
                html = await page.content()
                final_url = page.url
            except PlaywrightError:
                return None
        finally:
            await context.close()

        return RenderedPage(final_url=final_url, html=html, blocked_hosts=sorted(blocked))


def build_page_renderer(policy: RuntimePolicy) -> PageRenderer | None:
    """Build the renderer the policy asks for, or none when it asks for none.

    Constructing it raises when the optional extra is missing rather than quietly carrying on
    without rendering. `render_mode` is a committed, reviewed line, so a machine that cannot
    honour it should say so rather than silently produce different answers from the same config.
    """

    if policy.render_mode == "never":
        return None
    return PlaywrightPageRenderer(
        user_agent=settings.source_user_agent,
        timeout_seconds=settings.render_timeout_seconds,
        settle_milliseconds=settings.render_settle_milliseconds,
        maximum_renders=settings.maximum_source_renders + settings.maximum_crawl_renders,
    )
