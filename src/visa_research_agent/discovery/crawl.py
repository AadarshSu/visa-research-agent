"""Following links within approved domains to pinpoint the exact page.

Search usually lands on a section index rather than the document itself. Japan's tourism checklist
is one link from the embassy visa index, labelled "Tourism", at a URL that says nothing. Crawling
that last hop is what turns a good search result into the right page.

The crawl cannot leave the approved domains: every URL passes `is_crawlable` before a request is
made, and the final host is checked again after redirects.
"""

import asyncio
import heapq
from collections.abc import Awaitable, Callable

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

from visa_research_agent.discovery.models import CandidatePage, Corridor, PageLink, RoleScores
from visa_research_agent.discovery.urls import canonicalise_url, is_crawlable, is_pdf_url
from visa_research_agent.domain.models import BLOCKING_STATUS_CODES, DestinationConfig
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.rendering import PageRenderer
from visa_research_agent.research.tls import build_ssl_context

HEADING_TAGS = ("h1", "h2", "h3")

# Below this many links a page has told the crawler nothing, which is what a client-rendered
# shell looks like from here. The readable-character floor retrieval uses is the wrong test:
# crawling wants anchors, and a page can be rich in prose yet lead nowhere.
#
# Kept low on purpose. The failure being solved is the shell that yields *no* links; a page with
# a few real ones has already said something, and rendering it would spend a render budget that
# the genuinely empty pages need.
MINIMUM_CRAWL_LINKS = 3

# How many pages one crawl may render. A site that is unreadable throughout would otherwise
# render every page it visits, and each render costs seconds rather than milliseconds.
MAXIMUM_CRAWL_RENDERS = 12


def page_title_of(html: str) -> str:
    """The page's own title, preferring the first heading over the browser tab text."""

    soup = BeautifulSoup(html, "html.parser")
    for tag_name in ("h1", "title"):
        tag = soup.find(tag_name)
        if isinstance(tag, Tag):
            text = tag.get_text(" ", strip=True)
            if text:
                return text[:200]
    return ""


def extract_links(html: str, base_url: str, *, maximum_links: int = 400) -> list[PageLink]:
    """Collect the links on a page, keeping the text and heading that give each its meaning.

    This deliberately does not use `clean_source_html`: that strips navigation and returns plain
    text, which destroys the anchors this needs. Do not "simplify" it to share that function.
    """

    soup = BeautifulSoup(html, "html.parser")
    heading = ""
    links: list[PageLink] = []
    seen: set[str] = set()

    for element in soup.find_all([*HEADING_TAGS, "a"]):
        if not isinstance(element, Tag):
            continue
        if element.name in HEADING_TAGS:
            heading = element.get_text(" ", strip=True)[:300]
            continue

        href = element.get("href")
        if not isinstance(href, str) or not href.strip():
            continue
        target = href.strip()
        if target.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        absolute = canonicalise_url(httpx.URL(base_url).join(target).__str__())
        if absolute in seen:
            continue
        seen.add(absolute)
        links.append(
            PageLink(
                url=absolute,
                text=element.get_text(" ", strip=True)[:300],
                heading=heading,
                depth=0,
                discovered_from=base_url[:2000],
            )
        )
        if len(links) >= maximum_links:
            break
    return links


class CrawlFetcher:
    """Fetch raw page text for link extraction, bounded by trust and size.

    Separate from the retrieval fetcher on purpose: that one reduces pages to cleaned evidence text
    and is the audited path for anything a traveller sees. This one only reads structure.
    """

    def __init__(
        self,
        *,
        timeout_seconds: float = 20.0,
        maximum_bytes: int = 4_000_000,
        user_agent: str = "VisaResearchAgent/0.1 (source discovery)",
        renderer: PageRenderer | None = None,
        minimum_links: int = MINIMUM_CRAWL_LINKS,
        maximum_renders: int = MAXIMUM_CRAWL_RENDERS,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        host_delay_seconds: float = 0.5,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.maximum_bytes = maximum_bytes
        self.user_agent = user_agent
        self.renderer = renderer
        self.minimum_links = minimum_links
        # Discovery's own allowance. It visits far more pages than retrieval, so without a
        # separate count it would spend the whole browser budget before evidence was ever read.
        self.maximum_renders = maximum_renders
        self.renders = 0
        self.transport = transport
        self.sleep = sleep
        self.host_delay_seconds = host_delay_seconds
        self.requested: list[str] = []
        # Why a page could not be read. Reporting "nothing scored well enough" when the real
        # cause was an unreachable site would hide the actual problem from the reader.
        self.failures: dict[str, str] = {}
        # Where each request actually landed. Relative links must resolve against that, not
        # against the URL that was asked for, or a redirected page's links all point nowhere.
        self.final_urls: dict[str, str] = {}

    async def fetch_html(
        self,
        client: httpx.AsyncClient,
        url: str,
        destination: DestinationConfig,
    ) -> str | None:
        """Return a page's raw HTML, or None when it cannot or should not be read."""

        if not is_crawlable(url, destination) or is_pdf_url(url):
            return None

        self.requested.append(url)
        try:
            if self.host_delay_seconds:
                await self.sleep(self.host_delay_seconds)
            response = await client.get(url)
        except httpx.HTTPError as exc:
            reason = str(exc).strip()
            if "CERTIFICATE_VERIFY_FAILED" in reason:
                reason = "its TLS certificate could not be verified"
            elif not reason:
                # Several httpx errors carry no message, and "because " reads as a broken sentence.
                reason = f"the request failed ({type(exc).__name__})"
            self.failures[url] = reason[:120]
            return None

        # Redirects are followed, so the landing host must be re-checked exactly as retrieval does.
        if not destination.trusts_host(host_of(str(response.url))):
            self.failures[url] = "it redirected off the approved domains"
            return None
        if response.status_code in BLOCKING_STATUS_CODES:
            # The authority is refusing this client, which says nothing about whether its guidance
            # is correct. Recorded in its own words so a refusal cannot read as "nothing found".
            self.failures[url] = (
                f"it refused automated retrieval (HTTP {response.status_code}), so its guidance "
                "could not be independently verified here"
            )
            return None
        if response.status_code != httpx.codes.OK:
            self.failures[url] = f"it answered HTTP {response.status_code}"
            return None
        if len(response.content) > self.maximum_bytes:
            self.failures[url] = "it is larger than the size limit"
            return None
        if "html" not in response.headers.get("content-type", "text/html").lower():
            self.failures[url] = "it is not an HTML page"
            return None
        # An empty body is not a separate failure from a shell that renders to nothing: it is the
        # same page, one step further along. So it goes to the renderer too, and only becomes a
        # failure once rendering has had its turn.
        self.final_urls[url] = str(response.url)
        html = await self._render_if_empty(response.text, url, destination)
        if html is not None and not html.strip():
            self.failures[url] = "it returned no content"
            return None
        return html

    async def _render_if_empty(
        self, html: str, url: str, destination: DestinationConfig
    ) -> str | None:
        """Re-read a page in a browser when it offered the crawler no links to follow.

        Only when it offered none worth having: rendering is slow, so a page that already leads
        somewhere is returned as it arrived.
        """

        base = self.final_urls.get(url, url)
        found = len(extract_links(html, base))
        if self.renderer is None or found >= self.minimum_links:
            return html
        if self.renders >= self.maximum_renders:
            return html

        self.renders += 1
        rendered = await self.renderer.render(base, destination)
        if rendered is None:
            # Nothing better is available, so the thin page still stands as what was found.
            return html

        # Scripts can navigate, so where rendering ended up gets the same check a redirect gets.
        if not destination.trusts_host(host_of(rendered.final_url)):
            self.failures[url] = "rendering it navigated off the approved domains"
            return None
        if len(extract_links(rendered.html, rendered.final_url)) <= found:
            return html

        self.final_urls[url] = rendered.final_url
        return rendered.html


class LinkCrawler:
    """Walk outward from seed pages, best-first, staying inside the approved domains."""

    def __init__(
        self,
        fetcher: CrawlFetcher,
        score_link: Callable[[PageLink], RoleScores],
        *,
        reject: Callable[[PageLink], str | None] | None = None,
        maximum_depth: int = 2,
        maximum_pages: int = 40,
        maximum_pages_per_host: int = 20,
        expansion_threshold: float = 10.0,
    ) -> None:
        self.fetcher = fetcher
        self.score_link = score_link
        # Rejection is a policy decision, so it is injected rather than hard-coded here. An
        # archived checklist that still reads plausibly must never become a candidate at all,
        # because a high score would otherwise carry it straight to the top.
        self.reject = reject or (lambda _: None)
        self.maximum_depth = maximum_depth
        self.maximum_pages = maximum_pages
        self.maximum_pages_per_host = maximum_pages_per_host
        self.expansion_threshold = expansion_threshold
        self.rejected: dict[str, str] = {}
        # A page's own <title> is only knowable once it is fetched, so it is recorded here
        # rather than guessed from the link that pointed at it.
        self.titles: dict[str, str] = {}

    async def crawl(
        self,
        destination: DestinationConfig,
        corridor: Corridor,
        seeds: list[str],
    ) -> list[CandidatePage]:
        """Return every candidate reached, scored on its link evidence alone."""

        candidates: dict[str, CandidatePage] = {}
        visited: set[str] = set()
        per_host: dict[str, int] = {}
        # (-score, depth, url, sequence) keeps the frontier deterministic and spends budget on
        # the best links. The sequence number is load-bearing: without it two equally scored
        # links tie all the way down and heapq tries to compare PageLink objects, which raises.
        frontier: list[tuple[float, int, str, int, PageLink]] = []
        counter = 0

        seed_links: list[PageLink] = []
        for seed in seeds:
            canonical = canonicalise_url(seed)
            if not is_crawlable(canonical, destination):
                continue
            link = PageLink(url=canonical, text="", heading="", depth=0, discovered_from="seed")
            seed_links.append(link)
            counter += 1
            heapq.heappush(frontier, (-1000.0, 0, canonical, counter, link))

        # Share the budget between the hosts that were seeded. Without this a large portal starves
        # every other site: a ministry index links to hundreds of pages, so it would consume the
        # whole allowance before the mission that actually serves this traveller is ever reached.
        seed_hosts = {host_of(link.url) for link in seed_links}
        host_budget = self.maximum_pages_per_host
        if len(seed_hosts) > 1:
            host_budget = min(host_budget, max(4, self.maximum_pages // len(seed_hosts)))

        async with httpx.AsyncClient(
            transport=self.fetcher.transport,
            timeout=self.fetcher.timeout_seconds,
            follow_redirects=True,
            verify=build_ssl_context(),
            headers={
                "User-Agent": self.fetcher.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-GB,en;q=0.9",
            },
        ) as client:
            while frontier and len(visited) < self.maximum_pages:
                _, depth, url, _sequence, link = heapq.heappop(frontier)
                if url in visited:
                    continue
                host = host_of(url)
                if per_host.get(host, 0) >= host_budget:
                    continue
                visited.add(url)
                per_host[host] = per_host.get(host, 0) + 1

                html = await self.fetcher.fetch_html(client, url, destination)
                if html is None:
                    continue

                page_title = page_title_of(html)
                if page_title:
                    self.titles[url] = page_title

                if depth >= self.maximum_depth:
                    continue

                # Resolve relative links against where the request landed, not where it was
                # aimed. They differ after a redirect, and again after a render.
                base = self.fetcher.final_urls.get(url, url)
                for found in extract_links(html, base):
                    if found.url in visited or not is_crawlable(found.url, destination):
                        continue
                    child = found.model_copy(update={"depth": depth + 1})

                    reason = self.reject(child)
                    if reason is not None:
                        self.rejected[child.url] = reason
                        continue

                    scores = self.score_link(child)
                    _, best = scores.best()

                    existing = candidates.get(child.url)
                    if existing is None or best > existing.link_scores.best()[1]:
                        candidates[child.url] = CandidatePage(
                            link=child, link_scores=scores, found_by="crawl"
                        )

                    # Only follow links that look like they lead somewhere relevant, and never
                    # follow a PDF: it is a destination, not a signpost.
                    if best >= self.expansion_threshold and not is_pdf_url(child.url):
                        counter += 1
                        heapq.heappush(frontier, (-best, depth + 1, child.url, counter, child))

        return list(candidates.values())
