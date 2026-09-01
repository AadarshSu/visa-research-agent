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
    RobotsRules,
    RobotsVerdict,
    origin_of,
    parse_rules,
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
async def test_a_web_page_served_at_robots_is_not_called_an_outsized_policy() -> None:
    """The reason has to be true of what was seen. Measured 2026-09-01: every host that had ever
    tripped the size cap — the `uk`, `ng` and `ph` `usembassy.gov` posts, `rai.malaysia.gov.my`,
    `malaysiavisa.imi.gov.my` — answered `200 text/html` with a web page and no directive in it,
    while the corridor told the traveller their embassy publishes an outsized crawl policy. The
    verdict is unchanged; only the sentence is."""

    page = "<!DOCTYPE html><html><body>Technical Difficulties</body></html>" + "x" * 600_000

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=page, headers={"Content-Type": "text/html"})

    cache = RobotsCache(user_agent=REAL_USER_AGENT)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.UNREADABLE

    reason = cache.unreadable[origin_of(INDEX)]
    assert reason == "answered with a web page rather than a crawl policy"
    assert "does not permit" not in reason


@pytest.mark.anyio
async def test_a_page_served_as_the_wrong_type_is_still_recognised_as_a_page() -> None:
    """A host misconfigured enough to serve markup here has no claim on its `Content-Type` being
    believed either, so the markup itself decides."""

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="\n  <html><body>oops</body></html>" + "x" * 600_000,
            headers={"Content-Type": "application/octet-stream"},
        )

    cache = RobotsCache(user_agent=REAL_USER_AGENT)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.UNREADABLE

    assert cache.unreadable[origin_of(INDEX)] == (
        "answered with a web page rather than a crawl policy"
    )


@pytest.mark.anyio
async def test_a_genuinely_outsized_policy_keeps_its_own_reason() -> None:
    """The other branch is still reachable and still true when it fires: a policy too large to
    parse is a different fact from no policy at all, and guessing at the part that fit would be
    inventing permission either way."""

    policy = "User-agent: *\n" + "".join(f"Disallow: /p{n}\n" for n in range(60_000))

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=policy, headers={"Content-Type": "text/plain"})

    cache = RobotsCache(user_agent=REAL_USER_AGENT)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        assert await cache.verdict(client, INDEX) is RobotsVerdict.UNREADABLE

    assert cache.unreadable[origin_of(INDEX)] == (
        "is larger than the size limit for a crawl policy"
    )


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
    # It names what actually came back. "Could not be read" alone points a reader at a crawl policy
    # when the fact in front of them may be a host serving 500 to every path — which is exactly
    # what `avas.mfa.gov.cn` and `cova.mfa.gov.cn` were doing when this was measured.
    assert "answered HTTP 500" in fetcher.failures[INDEX]
    assert "is unknown" in fetcher.failures[INDEX]
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

    skip_notes = [note for note in resolved.notes if "robots.txt" in note]
    assert skip_notes, resolved.notes
    # The note repeats the reason recorded for the page, rather than asserting one. Written as a
    # fixed sentence it claimed a published refusal for hosts that had merely answered `502` to
    # their own policy — see the China corridor in DECISIONS entry 36.
    assert "does not permit this client to fetch it" in skip_notes[0]
    assert AUTHORITY in skip_notes[0]
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


# --- Pattern matching (RFC 9309 §2.2.2-2.2.3) -------------------------------------------------
#
# These are the tests that made the stdlib parser untenable. `urllib.robotparser` matches with
# `startswith` and supports neither `*` nor `$`, so every one of the wildcard cases below silently
# passed as "allowed" — a parser bug that makes this client fetch *more* than the site permits,
# which is the one direction this module must never fail in.


def rules(text: str, agent: str = "VisaResearchAgent") -> RobotsRules:
    return parse_rules(text, agent)


def test_a_wildcard_matches_any_run_of_characters() -> None:
    """`www.gov.uk` publishes nothing but wildcard rules, so without this it publishes nothing."""

    policy = rules("User-agent: *\nDisallow: /en/*/search.html\n")

    assert not policy.allows("https://a.example/en/anything/search.html")
    assert not policy.allows("https://a.example/en/a/b/c/search.html")
    assert policy.allows("https://a.example/en/anything/visa.html")


def test_a_trailing_dollar_anchors_the_end_of_the_path() -> None:
    policy = rules("User-agent: *\nDisallow: /*/print$\n")

    assert not policy.allows("https://a.example/standard-visitor/print")
    assert policy.allows("https://a.example/standard-visitor/printable-guide")


def test_the_query_string_is_part_of_what_a_rule_matches() -> None:
    """`Disallow: /search/all*` exists to catch `/search/all?keywords=…`; dropping the query
    would let through exactly the URL the rule was written for."""

    policy = rules("User-agent: *\nDisallow: /search/all*\n")

    assert not policy.allows("https://a.example/search/all?keywords=visa")


def test_a_dot_in_a_path_is_literal_and_not_a_regex_wildcard() -> None:
    """Real rules name real files — `imm0143e.pdf`. Reading `.` as "any character" would forbid
    neighbouring paths the site never mentioned."""

    policy = rules("User-agent: *\nDisallow: /forms/imm0143e.pdf\n")

    assert not policy.allows("https://a.example/forms/imm0143e.pdf")
    assert policy.allows("https://a.example/forms/imm0143expdf")


def test_the_longest_matching_pattern_governs() -> None:
    """Otherwise file order decides, and a broad `Disallow` at the top of a file would bury the
    narrow `Allow` beneath it that the site wrote to carve out an exception."""

    policy = rules("User-agent: *\nDisallow: /guidance/\nAllow: /guidance/visas/\n")

    assert not policy.allows("https://a.example/guidance/tax.html")
    assert policy.allows("https://a.example/guidance/visas/visitor.html")


def test_allow_wins_a_tie_against_disallow() -> None:
    policy = rules("User-agent: *\nDisallow: /visa\nAllow: /visa\n")

    assert policy.allows("https://a.example/visa")


def test_an_empty_disallow_forbids_nothing() -> None:
    """The long-standing way to write "no restrictions". Read as a pattern it is the empty prefix,
    which matches every path and would close the whole site."""

    policy = rules("User-agent: *\nDisallow:\n")

    assert policy.allows("https://a.example/anything")


def test_a_rule_line_ends_the_group_so_the_next_agent_starts_a_new_one() -> None:
    """Without this, rules written for one client leak onto every client named before it."""

    policy = rules(
        "User-agent: SomeOtherBot\nDisallow: /\n\nUser-agent: VisaResearchAgent\nDisallow: /admin\n"
    )

    assert policy.allows("https://a.example/visa")
    assert not policy.allows("https://a.example/admin")


def test_a_group_is_selected_by_an_exact_token_never_a_substring() -> None:
    """`urllib` uses a substring test, under which a record aimed at another crawler whose name
    happens to sit inside ours would silently impose rules written for someone else."""

    policy = rules("User-agent: Visa\nDisallow: /\nUser-agent: *\nAllow: /\n")

    assert policy.allows("https://a.example/visa"), "the `Visa` record is not about this client"


def test_a_named_group_is_preferred_over_the_wildcard_one() -> None:
    policy = rules(
        "User-agent: *\nDisallow: /\nUser-agent: VisaResearchAgent\nAllow: /\nDisallow: /admin\n"
    )

    assert policy.allows("https://a.example/visa")
    assert not policy.allows("https://a.example/admin")


def test_comments_and_blank_lines_are_ignored() -> None:
    policy = rules("# a note\nUser-agent: *   # trailing\n\nDisallow: /admin # why\n")

    assert not policy.allows("https://a.example/admin")
    assert policy.allows("https://a.example/visa")


def test_the_real_gov_uk_policy_is_obeyed() -> None:
    """Captured from `www.gov.uk/robots.txt` on 2026-08-18. Every rule in it is a wildcard, so
    under the stdlib parser this whole policy was inert."""

    policy = rules(
        "User-agent: *\n"
        "Disallow: /*/print$\n"
        "Disallow: /search/all*\n"
        "Sitemap: https://www.gov.uk/sitemap.xml\n"
        "User-agent: deepcrawl\n"
        "Disallow: /\n"
    )

    assert policy.allows("https://www.gov.uk/standard-visitor")
    assert not policy.allows("https://www.gov.uk/standard-visitor/print")
    assert not policy.allows("https://www.gov.uk/search/all?keywords=visa")


def test_the_real_canada_policy_keeps_the_guidance_and_withholds_the_forms() -> None:
    """Captured from `www.canada.ca/robots.txt` on 2026-08-18, and the clearest measured cost of
    this change: the visitor-visa guidance stays readable, the IRCC application forms do not."""

    policy = rules(
        "User-agent: *\n"
        "Disallow: /en/*/search.html\n"
        "Disallow: /en/service-canada/\n"
        "Disallow: /en/immigration-refugees-citizenship/services/reference-include/\n"
        "Disallow: /content/dam/ircc/documents/pdf/english/kits/forms/imm0143e.pdf\n"
    )

    canada = "https://www.canada.ca"
    assert policy.allows(f"{canada}/en/immigration-refugees-citizenship/services/visit-canada.html")
    assert not policy.allows(
        f"{canada}/content/dam/ircc/documents/pdf/english/kits/forms/imm0143e.pdf"
    )
    assert not policy.allows(f"{canada}/en/service-canada/some-page.html")
