"""Honouring each host's published crawl policy, and reporting what that cost.

The point of these tests is not that `robots.txt` is parsed — `urllib` does that. It is that a page
left unread because of a policy is **recorded as that**, with a reason that is true of what was
actually observed, and that it never quietly becomes "nothing was found". See DECISIONS entry 36.
"""

import socket
from pathlib import Path

import httpx
import pytest
from discovery_site import (
    AUTHORITY,
    INDEX,
    MISSION,
    MISSION_INDEX,
    destination,
    handler,
    site_pages,
)
from test_discovery_resolver import build_resolver, corridor
from test_live_sources import Clock, build_fetcher
from test_live_sources import destination as live_destination

from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.research.robots import (
    RobotsCache,
    RobotsVerdict,
    origin_of,
    user_agent_token,
)

# The user agent this project actually sends, so the matching is tested against the real string
# rather than a convenient one.
REAL_USER_AGENT = "VisaResearchAgent/0.1 (personal visa research; contact repository owner)"

SOURCE_URL = "https://immigration.gov.example/visa/india"


def robots_transport(policy: str, *, status: int = 200) -> httpx.MockTransport:
    """Serve one policy for every host, and a short page for everything else."""

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(status, text=policy, headers={"Content-Type": "text/plain"})
        return httpx.Response(
            200,
            text="<html><body><h1>Visa</h1></body></html>",
            headers={"Content-Type": "text/html"},
        )

    return httpx.MockTransport(respond)


def test_the_product_token_is_taken_out_of_the_full_header() -> None:
    """`robots.txt` records name a product token, never a whole User-Agent header."""

    assert user_agent_token(REAL_USER_AGENT) == "VisaResearchAgent"
    assert user_agent_token("bare-agent") == "bare-agent"


def test_a_policy_is_keyed_by_origin_not_by_hostname() -> None:
    """Scheme and port each get their own policy: publishing for one says nothing about
    the other."""

    assert origin_of("https://a.gov.example/visa/index.html?x=1#y") == "https://a.gov.example"
    assert origin_of("https://a.gov.example:8443/visa") == "https://a.gov.example:8443"
    assert origin_of("https://a.gov.example/x") != origin_of("http://a.gov.example/x")


@pytest.mark.anyio
async def test_a_disallow_for_this_client_is_obeyed() -> None:
    policy = "User-agent: VisaResearchAgent\nDisallow: /visa/\n"
    cache = RobotsCache(user_agent=REAL_USER_AGENT)
    transport = robots_transport(policy)

    async with httpx.AsyncClient(transport=transport) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.DISALLOWED
        assert await cache.verdict(client, f"https://{AUTHORITY}/news") is RobotsVerdict.ALLOWED


@pytest.mark.anyio
async def test_a_disallow_aimed_at_another_client_does_not_apply() -> None:
    """Coverage is not given away to a rule that was never about us."""

    policy = "User-agent: SomeOtherBot\nDisallow: /\n"
    cache = RobotsCache(user_agent=REAL_USER_AGENT)

    async with httpx.AsyncClient(transport=robots_transport(policy)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.ALLOWED


@pytest.mark.anyio
async def test_a_wildcard_disallow_applies_to_this_client_too() -> None:
    cache = RobotsCache(user_agent=REAL_USER_AGENT)

    async with httpx.AsyncClient(transport=robots_transport("User-agent: *\nDisallow: /visa")) as (
        client
    ):
        assert await cache.verdict(client, INDEX) is RobotsVerdict.DISALLOWED


@pytest.mark.anyio
async def test_no_published_policy_restricts_nothing() -> None:
    """A `404` is the ordinary case, and it must not fail closed or nothing would ever be read."""

    cache = RobotsCache(user_agent=REAL_USER_AGENT)

    async with httpx.AsyncClient(transport=robots_transport("", status=404)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.ALLOWED


@pytest.mark.anyio
async def test_a_protected_policy_file_is_not_a_closed_site() -> None:
    """RFC 9309 §2.3.1.3. A `403` on the file says the file is protected, not that we are barred."""

    cache = RobotsCache(user_agent=REAL_USER_AGENT)

    async with httpx.AsyncClient(transport=robots_transport("", status=403)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.ALLOWED


@pytest.mark.anyio
async def test_a_policy_that_could_not_be_read_is_unreadable_not_disallowed() -> None:
    """The two must stay apart: only one of them is a claim about what the authority permits."""

    cache = RobotsCache(user_agent=REAL_USER_AGENT)

    async with httpx.AsyncClient(transport=robots_transport("", status=503)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.UNREADABLE


@pytest.mark.anyio
async def test_an_unreachable_host_raises_rather_than_inventing_a_policy() -> None:
    """The guard against a false reason. Swallowing this made every dead host report as
    "its robots.txt does not permit this client", which was not observed and is not true."""

    def failing(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("the authority is unreachable")

    cache = RobotsCache(user_agent=REAL_USER_AGENT)
    async with httpx.AsyncClient(transport=httpx.MockTransport(failing)) as client:
        with pytest.raises(httpx.HTTPError):
            await cache.verdict(client, INDEX)


@pytest.mark.anyio
async def test_one_policy_is_read_per_origin_however_many_pages_are_checked() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text="User-agent: *\nAllow: /\n")

    cache = RobotsCache(user_agent=REAL_USER_AGENT)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        for path in ("/a", "/b", "/c"):
            await cache.verdict(client, f"https://{AUTHORITY}{path}")
        await cache.verdict(client, f"https://{MISSION}/a")

    assert [str(request.url) for request in requests] == [
        f"https://{AUTHORITY}/robots.txt",
        f"https://{MISSION}/robots.txt",
    ]


@pytest.mark.anyio
async def test_the_crawl_records_a_skipped_page_rather_than_passing_over_it() -> None:
    """A page nobody asked for must never read as a page that did not exist."""

    requests: list[httpx.Request] = []
    transport = httpx.MockTransport(
        handler(requests, robots={AUTHORITY: "User-agent: *\nDisallow: /visa/\n"})  # type: ignore[arg-type]
    )
    fetcher = CrawlFetcher(transport=transport, host_delay_seconds=0.0)

    async with httpx.AsyncClient(transport=transport) as client:
        assert await fetcher.fetch_html(client, INDEX, destination()) is None

    assert fetcher.outcomes[INDEX] == "disallowed"
    assert fetcher.disallowed_urls() == {INDEX}
    assert "does not permit" in fetcher.failures[INDEX]
    assert requests == [], "a disallowed page must not be requested at all"


@pytest.mark.anyio
async def test_a_crawl_skip_is_never_a_refusal_a_corridor_can_be_built_on() -> None:
    """A `403` was observed on the page; a `Disallow` covers a page nobody asked for. Only the
    first may resolve a corridor, or the narrow exception in entry 32 stops being narrow."""

    requests: list[httpx.Request] = []
    transport = httpx.MockTransport(
        handler(requests, robots={AUTHORITY: "User-agent: *\nDisallow: /\n"})  # type: ignore[arg-type]
    )
    fetcher = CrawlFetcher(transport=transport, host_delay_seconds=0.0)

    async with httpx.AsyncClient(transport=transport) as client:
        await fetcher.fetch_html(client, INDEX, destination())

    assert fetcher.disallowed_urls() == {INDEX}
    assert fetcher.blocked_urls() == set()
    assert fetcher.persistent_refusals() == set()


@pytest.mark.anyio
async def test_an_unreadable_policy_stops_the_crawl_but_says_so_honestly() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(500, text="broken")
        return httpx.Response(200, text=site_pages()[INDEX])

    fetcher = CrawlFetcher(transport=httpx.MockTransport(respond), host_delay_seconds=0.0)
    async with httpx.AsyncClient(transport=fetcher.transport) as client:
        assert await fetcher.fetch_html(client, INDEX, destination()) is None

    assert fetcher.outcomes[INDEX] == "disallowed"
    assert "could not be read" in fetcher.failures[INDEX]
    assert "does not permit" not in fetcher.failures[INDEX]


@pytest.mark.anyio
async def test_a_dead_host_is_still_reported_as_unreachable() -> None:
    """Reading the policy first must not change the diagnosis of a host that is simply gone."""

    dead = f"https://gone.{AUTHORITY}/visa/index.html"

    def failing(request: httpx.Request) -> httpx.Response:
        error = httpx.ConnectError("[Errno 8] nodename nor servname provided, or not known")
        error.__cause__ = socket.gaierror(8, "nodename nor servname provided")
        raise error

    fetcher = CrawlFetcher(transport=httpx.MockTransport(failing), host_delay_seconds=0.0)
    async with httpx.AsyncClient(transport=fetcher.transport) as client:
        assert await fetcher.fetch_html(client, dead, destination()) is None

    assert fetcher.outcomes[dead] == "unreachable"
    assert fetcher.disallowed_urls() == set()


@pytest.mark.anyio
async def test_a_redirect_onto_a_disallowed_path_is_refused_after_the_fact() -> None:
    """The request cannot be taken back, but its result can be, and that is the honest half."""

    landing = f"https://{AUTHORITY}/private/visa.html"

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /private/\n")
        if request.url.path == "/private/visa.html":
            return httpx.Response(200, text=site_pages()[INDEX])
        return httpx.Response(302, headers={"Location": landing})

    fetcher = CrawlFetcher(transport=httpx.MockTransport(respond), host_delay_seconds=0.0)
    async with httpx.AsyncClient(transport=fetcher.transport, follow_redirects=True) as client:
        assert await fetcher.fetch_html(client, INDEX, destination()) is None

    assert fetcher.outcomes[INDEX] == "disallowed"
    assert "redirected" in fetcher.failures[INDEX]


@pytest.mark.anyio
async def test_retrieval_reports_a_disallowed_source_as_a_gap_and_never_requests_it(
    tmp_path: Path,
) -> None:
    requests: list[httpx.Request] = []
    clock = Clock()

    def unused(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><body>never reached</body></html>")

    fetcher = build_fetcher(
        tmp_path, clock, unused, requests, robots="User-agent: *\nDisallow: /visa\n"
    )
    report = await fetcher.fetch(live_destination())

    assert not report.fetched
    assert [failure.outcome for failure in report.failures] == ["disallowed"]
    assert "does not permit" in report.failures[0].detail
    assert requests == [], "a disallowed source must not be requested at all"


@pytest.mark.anyio
async def test_evidence_still_inside_its_ttl_is_served_without_asking_again(
    tmp_path: Path,
) -> None:
    """`robots.txt` governs fetching. Text already held and still current is not a fetch, so a
    policy published since it was read does not retrospectively forbid reading what we have."""

    requests: list[httpx.Request] = []
    clock = Clock()
    body = "Indian passport holders require an entry visa. " * 40

    def serving(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text=f"<html><body><main><p>{body}</p></main></body></html>",
            headers={"Content-Type": "text/html"},
        )

    open_fetcher = build_fetcher(tmp_path, clock, serving, requests)
    first = await open_fetcher.fetch(live_destination())
    assert first.fetched, f"the first fetch should succeed: {first.failures}"

    closed_fetcher = build_fetcher(
        tmp_path, clock, serving, requests, robots="User-agent: *\nDisallow: /\n"
    )
    clock.advance(1)
    second = await closed_fetcher.fetch(live_destination())

    assert [item.source.source_id for item in second.fetched] == ["tl_visa_documents"]
    assert not second.failures


@pytest.mark.anyio
async def test_a_corridor_says_out_loud_that_a_policy_kept_it_out(tmp_path: Path) -> None:
    """The whole point of the outcome. A reader must be able to tell "we were not allowed to look"
    from "we looked and there was nothing", because only one of them is about the authority."""

    requests: list[httpx.Request] = []
    resolver, _ = build_resolver(
        tmp_path,
        requests,
        [INDEX, MISSION_INDEX],
        robots={AUTHORITY: "User-agent: *\nDisallow: /visa/\n"},
    )

    resolved = await resolver.resolve(destination(), corridor())

    assert any("robots.txt" in note for note in resolved.notes), resolved.notes
    assert not any(request.url.host == AUTHORITY for request in requests)
    # Reported, and nothing more. A page nobody asked for cannot be the page that held the answer.
    assert resolved.inaccessible_urls == []
    assert resolved.decision_blocking_urls == []


@pytest.mark.anyio
async def test_a_policy_is_read_again_once_it_expires() -> None:
    """The fetchers holding one of these live as long as the server process, so a cache with no
    expiry would obey a policy read at boot until someone restarted it — including a `Disallow`
    the site had since withdrawn."""

    served = ["User-agent: *\nDisallow: /visa\n", "User-agent: *\nAllow: /\n"]

    reads: list[str] = []

    def responder(request: httpx.Request) -> httpx.Response:
        body = served[min(len(reads), len(served) - 1)]
        reads.append(str(request.url))
        return httpx.Response(200, text=body)

    now = [0.0]
    cache = RobotsCache(user_agent=REAL_USER_AGENT, ttl_seconds=3600.0, clock=lambda: now[0])
    async with httpx.AsyncClient(transport=httpx.MockTransport(responder)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.DISALLOWED
        now[0] += 60.0
        assert await cache.verdict(client, INDEX) is RobotsVerdict.DISALLOWED
        assert len(reads) == 1, "inside the TTL the policy is not asked for again"
        now[0] += 3600.0
        assert await cache.verdict(client, INDEX) is RobotsVerdict.ALLOWED

    assert len(reads) == 2
