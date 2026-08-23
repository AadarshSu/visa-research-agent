"""Following links within approved domains to pinpoint the exact page.

Search usually lands on a section index rather than the document itself. Japan's tourism checklist
is one link from the embassy visa index, labelled "Tourism", at a URL that says nothing. Crawling
that last hop is what turns a good search result into the right page.

The crawl cannot leave the approved domains: every URL passes `is_crawlable` before a request is
made, and the final host is checked again after redirects.
"""

import asyncio
import heapq
import socket
import time
from collections.abc import Awaitable, Callable

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

from visa_research_agent.discovery.models import CandidatePage, PageLink, RoleScores
from visa_research_agent.discovery.urls import (
    canonicalise_url,
    is_crawlable,
    is_pdf_url,
    strip_invisible,
)
from visa_research_agent.domain.models import (
    BLOCKING_STATUS_CODES,
    PERSISTENT_REFUSAL_STATUS_CODES,
    DestinationConfig,
    FailureOutcome,
)
from visa_research_agent.domain.trust import host_of
from visa_research_agent.research.rendering import PageRenderer
from visa_research_agent.research.robots import RobotsCache, RobotsVerdict
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


def host_does_not_resolve(error: httpx.HTTPError) -> bool:
    """True when the failure was the hostname itself not resolving.

    Tested by exception type rather than by reading the message: the errno and wording differ
    between platforms — macOS says `[Errno 8] nodename nor servname provided`, Linux says
    `[Errno -2] Name or service not known` — while `socket.gaierror` is the same everywhere.

    This is the one failure that is a fact about a **host** rather than about one request, which is
    why it is worth telling apart. Every other kind says only that this URL, this time, did not
    work.
    """

    seen = 0
    cause: BaseException | None = error
    while cause is not None and seen < 8:
        if isinstance(cause, socket.gaierror):
            return True
        cause = cause.__cause__ or cause.__context__
        seen += 1
    return False


def _robots_reason(verdict: RobotsVerdict, detail: str) -> str:
    """Why a crawl policy stopped a page, in words that are true of *that* verdict.

    Two sentences rather than one because a host that said no and a host whose policy could not be
    read are different facts, and only the first is a statement about what the authority permits.
    Every reason this project reports has to be true of what was actually observed.

    The unreadable case names what came back, because "could not be read" alone points a reader at
    a crawl policy when the fact in front of them may be a host serving `502` to everything —
    measured on `avas.mfa.gov.cn` and `cova.mfa.gov.cn`, 2026-08-18.
    """

    if verdict is RobotsVerdict.DISALLOWED:
        return "its robots.txt does not permit this client to fetch it"
    return f"its robots.txt {detail}, so whether this client may fetch it is unknown"


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
        # Stripped before the join, not after: `httpx.URL.join` parses the target itself and
        # raises on an invisible character in the hostname, so normalising downstream is too late.
        target = strip_invisible(href.strip())
        if target.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        try:
            absolute = canonicalise_url(httpx.URL(base_url).join(target).__str__())
        except (httpx.InvalidURL, UnicodeError, ValueError):
            # A link that cannot be parsed is not a link. It must never be fatal: this runs over
            # every anchor on every page of a live government site, and one malformed `href` used
            # to end the whole corridor with a traceback — observed on Thailand's immigration site,
            # which links a hostname containing a zero-width space.
            continue
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
        clock: Callable[[], float] = time.monotonic,
        robots: RobotsCache | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.maximum_bytes = maximum_bytes
        self.user_agent = user_agent
        self.renderer = renderer
        self.minimum_links = minimum_links
        # Discovery's own allowance. It visits far more pages than retrieval, so without a
        # separate count it would spend the whole browser budget before evidence was ever read.
        #
        # A spent count may live on the instance here, where retrieval's may not, and the reason is
        # lifetime rather than style: `AutomaticDestinationService` holds a resolver *factory*, so
        # one of these is built per corridor and shares its allowance across that corridor's many
        # `fetch_html` calls — which is the intent. `LiveSourceFetcher` is reached through an
        # `lru_cache(maxsize=1)` instead and outlives every run, so its allowance is a per-call
        # `RenderBudget`. If this fetcher ever becomes long-lived, this counter has the same defect.
        self.maximum_renders = maximum_renders
        self.renders = 0
        self.transport = transport
        self.sleep = sleep
        self.host_delay_seconds = host_delay_seconds
        self.clock = clock
        # Each host's own crawl policy, read once and obeyed. Built here rather than injected so
        # there is no configuration in which the crawl runs without it; the parameter exists so a
        # test can seed one, not so it can be switched off.
        self.robots = robots or RobotsCache(user_agent=user_agent)
        # When each host may next be asked for a page. The politeness delay is owed *to a host*;
        # applied globally it made every site wait behind every other, which is latency rather
        # than courtesy.
        self.next_request_at: dict[str, float] = {}
        self.requested: list[str] = []
        # Why a page could not be read. Reporting "nothing scored well enough" when the real
        # cause was an unreachable site would hide the actual problem from the reader.
        self.failures: dict[str, str] = {}
        # The same facts as `failures`, in a form nothing has to read prose to use. Whether an
        # authority refused us decides both what a traveller is told and whether a fetch place is
        # worth spending, and neither should depend on a sentence someone may reword.
        self.outcomes: dict[str, FailureOutcome] = {}
        # Hosts whose name does not resolve. Held per host rather than per URL because that is the
        # scope of the fact: no path under this name can be read, so none is worth a fetch place.
        self.unresolvable_hosts: set[str] = set()
        # Where each request actually landed. Relative links must resolve against that, not
        # against the URL that was asked for, or a redirected page's links all point nowhere.
        self.final_urls: dict[str, str] = {}
        # Which status a refusal came back with. `outcomes` says a page was refused, which is what
        # reporting needs; this says whether waiting could change that, which is what deciding
        # needs. A rate limit and "you may not read this" are not the same fact.
        self.refusal_statuses: dict[str, int] = {}

    def _record_failure(
        self, url: str, outcome: FailureOutcome, reason: str, *, status: int | None = None
    ) -> None:
        """Record why a page could not be read, once, in every form something needs it.

        The sentence is for whoever reads the run; the outcome is for whatever has to act on it.
        Kept together so the two can never describe different things.
        """

        self.failures[url] = reason
        self.outcomes[url] = outcome
        if status is not None:
            self.refusal_statuses[url] = status

    def blocked_urls(self) -> set[str]:
        """URLs an authority refused this client.

        Asking again is pointless — same client, same URL, same answer — and spending a fetch place
        on one costs a page that could have been read. It is **not** a fact about the host: another
        path on the same site may be served normally, so nothing here is skipped by domain.
        Reporting is unaffected: `inaccessible_domains` is derived from these records, not from
        whether the page was later fetched.
        """

        return {url for url, outcome in self.outcomes.items() if outcome == "blocked"}

    def disallowed_urls(self) -> set[str]:
        """URLs a host's own `robots.txt` told this client not to fetch.

        Held apart from `blocked_urls` on purpose. Both mean "we were not permitted", but only a
        refusal *observed on the page itself* may resolve a corridor (DECISIONS entries 32 and 36).
        A `Disallow` covers a path nobody asked for, so it is reported and nothing more — treating
        it as evidence that the answer was behind that page would be guessing about a page we chose
        not to request.
        """

        return {url for url, outcome in self.outcomes.items() if outcome == "disallowed"}

    def persistent_refusals(self) -> set[str]:
        """Refusals that waiting would not change, so the only ones a plan may be built around.

        A `429` is a rate limit: it is still a refusal, still reported, and still not retried — but
        it does not support telling a traveller that an authority would not let this program read a
        page, because next week it might. Only `401` and `403` do. See DECISIONS entry 32; the
        distinction is the same one entry 27 drew when it excluded a `502`.

        A refusal recorded without a status is excluded, which fails toward refusing rather than
        toward claiming an authority blocked us.
        """

        return {
            url
            for url in self.blocked_urls()
            if self.refusal_statuses.get(url, 0) in PERSISTENT_REFUSAL_STATUS_CODES
        }

    async def _wait_for_host(self, host: str) -> None:
        """Space this host's requests, without holding up any other host.

        The next slot is claimed before sleeping rather than after, so two requests to the same
        host queue behind each other instead of both reading the same last-request time and going
        at once. A host asked for the first time waits not at all.
        """

        if not self.host_delay_seconds:
            return
        now = self.clock()
        earliest = self.next_request_at.get(host, now)
        self.next_request_at[host] = max(now, earliest) + self.host_delay_seconds
        if earliest > now:
            await self.sleep(earliest - now)

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
            # The host's own crawl policy, read before anything is asked of it. A `Disallow` is not
            # a block to route around: it is the authority stating what it permits, and obeying it
            # is the posture DECISIONS entry 35 settled on. Recorded rather than silently skipped,
            # so a page left unread can never present as a page that did not exist.
            #
            # Inside the try because a host that cannot be reached for its policy cannot be reached
            # for its pages either, and the handler below is where that is already described
            # correctly — including telling a name that does not resolve from a request that failed.
            verdict = await self.robots.verdict(client, url)
            if verdict is not RobotsVerdict.ALLOWED:
                detail = self.robots.unreadable_detail(url)
                self._record_failure(url, "disallowed", _robots_reason(verdict, detail))
                return None
            await self._wait_for_host(host_of(url))
            response = await client.get(url)
        except httpx.HTTPError as exc:
            reason = str(exc).strip()
            if "CERTIFICATE_VERIFY_FAILED" in reason:
                reason = "its TLS certificate could not be verified"
            elif not reason:
                # Several httpx errors carry no message, and "because " reads as a broken sentence.
                reason = f"the request failed ({type(exc).__name__})"
            self._record_failure(url, "unreachable", reason[:120])
            if host_does_not_resolve(exc):
                self.unresolvable_hosts.add(host_of(url))
            return None

        # Redirects are followed, so the landing host must be re-checked exactly as retrieval does.
        final_url = str(response.url)
        if not destination.trusts_host(host_of(final_url)):
            self._record_failure(url, "untrusted", "it redirected off the approved domains")
            return None
        # And re-checked against the landing host's policy, for the same reason: the request that
        # was permitted is not the one that was answered. The fetch cannot be taken back, but its
        # result can be refused, which is the honest half that is still available here.
        if final_url != url:
            try:
                landing = await self.robots.verdict(client, final_url)
            except httpx.HTTPError:
                # The landing host would not serve its policy, so we cannot say we were permitted.
                landing = RobotsVerdict.UNREADABLE
            if landing is not RobotsVerdict.ALLOWED:
                self._record_failure(
                    url,
                    "disallowed",
                    "it redirected to a page "
                    + _robots_reason(landing, self.robots.unreadable_detail(final_url)),
                )
                return None
        if response.status_code in BLOCKING_STATUS_CODES:
            # The authority is refusing this client, which says nothing about whether its guidance
            # is correct. Recorded in its own words so a refusal cannot read as "nothing found".
            #
            # Same gap as the retrieval path (entry 41): a `403` carrying `cf-mitigated: challenge`
            # is a browser check rather than a refusal, and this branch returns before
            # `_render_if_empty` below, so the renderer never sees it. Behind France's challenge at
            # least one "blocked" URL turned out to be a plain 404. TODO item 5.
            self._record_failure(
                url,
                "blocked",
                f"it refused automated retrieval (HTTP {response.status_code}), so its guidance "
                "could not be independently verified here",
                status=response.status_code,
            )
            return None
        if response.status_code != httpx.codes.OK:
            self._record_failure(url, "unusable", f"it answered HTTP {response.status_code}")
            return None
        if len(response.content) > self.maximum_bytes:
            self._record_failure(url, "unusable", "it is larger than the size limit")
            return None
        if "html" not in response.headers.get("content-type", "text/html").lower():
            self._record_failure(url, "unusable", "it is not an HTML page")
            return None
        # An empty body is not a separate failure from a shell that renders to nothing: it is the
        # same page, one step further along. So it goes to the renderer too, and only becomes a
        # failure once rendering has had its turn.
        self.final_urls[url] = final_url
        html = await self._render_if_empty(response.text, url, destination)
        if html is not None and not html.strip():
            self._record_failure(url, "unusable", "it returned no content")
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
            self._record_failure(
                url, "untrusted", "rendering it navigated off the approved domains"
            )
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
        maximum_concurrent_hosts: int = 4,
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
        # One request per host at a time, several hosts at once. A corridor usually spans two to
        # four sites, and walking them one page at a time meant each site's politeness delay was
        # also paid by every other site.
        self.maximum_concurrent_hosts = maximum_concurrent_hosts
        self.rejected: dict[str, str] = {}
        # A page's own <title> is only knowable once it is fetched, so it is recorded here
        # rather than guessed from the link that pointed at it.
        self.titles: dict[str, str] = {}

    async def crawl(
        self,
        destination: DestinationConfig,
        seeds: list[str],
    ) -> list[CandidatePage]:
        """Return every candidate reached, scored on its link evidence alone.

        Takes no corridor, and used to. It was never read here — everything corridor-specific
        reaches this class through the injected `score_link`, which closes over the traveller. The
        parameter was dropped on 2026-08-22 when the corpus crawl (entry 44) needed to walk a
        country's sites with no traveller at all, and passing a fabricated corridor to satisfy an
        argument nothing used would have made a corridor-independent job look corridor-shaped.
        """

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
        # A list so the frontier's tie-breaking sequence keeps counting across pages that are now
        # expanded in a separate method. Without it two equally scored links compare PageLink
        # objects, which raises.
        counters = [counter]

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
                wave = self._next_wave(frontier, visited, per_host, host_budget)
                if not wave:
                    break
                for _depth, url, _link in wave:
                    visited.add(url)
                    per_host[host_of(url)] = per_host.get(host_of(url), 0) + 1

                pages = await asyncio.gather(
                    *(
                        self.fetcher.fetch_html(client, url, destination)
                        for _depth, url, _link in wave
                    )
                )

                # Results are handled in the order the frontier gave them, never the order they
                # came back in. What a corridor resolves to depends on the order candidates are
                # seen, and that must not depend on which site answered first.
                for (depth, url, _link), html in zip(wave, pages, strict=True):
                    if html is None:
                        continue
                    self._expand(
                        url, html, depth, destination, candidates, visited, frontier, counters
                    )

        return list(candidates.values())

    def _next_wave(
        self,
        frontier: list[tuple[float, int, str, int, PageLink]],
        visited: set[str],
        per_host: dict[str, int],
        host_budget: int,
    ) -> list[tuple[int, str, PageLink]]:
        """The next few pages to fetch together: the best links, one per host.

        One page per host keeps each site's spacing intact — the delay is what makes this polite,
        and it is only owed per host. Entries for a host already in the wave go back to the
        frontier rather than being dropped, so nothing is lost by being second in its queue.
        """

        remaining = self.maximum_pages - len(visited)
        wanted = min(self.maximum_concurrent_hosts, max(0, remaining))
        wave: list[tuple[int, str, PageLink]] = []
        hosts: set[str] = set()
        deferred: list[tuple[float, int, str, int, PageLink]] = []

        while frontier and len(wave) < wanted:
            entry = heapq.heappop(frontier)
            _, depth, url, _sequence, link = entry
            if url in visited:
                continue
            host = host_of(url)
            # Over its share of the budget: dropped rather than deferred, exactly as before, or a
            # large portal would keep its links circulating forever.
            if per_host.get(host, 0) >= host_budget:
                continue
            if host in hosts:
                deferred.append(entry)
                continue
            hosts.add(host)
            wave.append((depth, url, link))

        for entry in deferred:
            heapq.heappush(frontier, entry)
        return wave

    def _expand(
        self,
        url: str,
        html: str,
        depth: int,
        destination: DestinationConfig,
        candidates: dict[str, CandidatePage],
        visited: set[str],
        frontier: list[tuple[float, int, str, int, PageLink]],
        counters: list[int],
    ) -> None:
        """Record what a fetched page said, and queue the links worth following."""

        page_title = page_title_of(html)
        if page_title:
            self.titles[url] = page_title

        if depth >= self.maximum_depth:
            return

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
                counters[0] += 1
                heapq.heappush(frontier, (-best, depth + 1, child.url, counters[0], child))
