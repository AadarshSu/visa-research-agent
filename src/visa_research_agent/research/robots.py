"""Reading and honouring each host's stated crawl policy.

Nothing in this project fetched `robots.txt` until now, while it computed a per-host politeness
delay for the same hosts. That was inconsistent on its own terms: the delay is a guess at what a
site can tolerate, and `robots.txt` is the site saying it. DECISIONS entry 35 settled the posture
this belongs to — **honest client, not anonymous client**. A `Disallow` is an authority's stated
policy, so it is obeyed even where walking past it would have found the answer.

This is deliberately not a way around DECISIONS entry 18 and it is not softened by it either. Entry
18 forbids *deception*; this file is the opposite obligation, and it costs coverage rather than
buying it. A page skipped here is recorded as its own outcome so it can never read as "nothing was
found".

Status handling follows RFC 9309 §2.3.1, which is the same reasoning this project already applies
to an HTTP refusal:

* **2xx** — a policy was published, so parse it and obey it.
* **4xx** — no policy was published, so nothing restricts this client. This includes `401` and
  `403`: those say the *file* is protected, which is not the site declaring itself closed.
  Measured 2026-08-19 and worth keeping: `france-visas.gouv.fr` answers its own `robots.txt` with a
  Cloudflare challenge, so there is genuinely no policy there to honour — which is what entry 41
  concludes about the `403` on its pages too. Absence of a rule is not permission to deceive; it is
  the absence of a rule.
* **5xx or an oversized file** — the server is answering, and the policy it holds could not be
  read, so whether we are permitted is **unknown**. The standard says to assume we are not, which
  is the direction every other unknown in this project fails in.

**A network failure is deliberately not one of those, and it raises rather than deciding.** It is
not a fact about a crawl policy — it is a fact about the host, and the caller already has machinery
that says so correctly, including telling a name that does not resolve from a request that merely
failed. Swallowing it here would have made every dead host report as *"its robots.txt does not
permit this client"*, which is a **false reason**, and a false reason is the failure mode this
project treats as worse than no answer at all.

**Matching is written here, and `urllib.robotparser` is deliberately not used.** Reaching for stdlib
was the first instinct and it was wrong, found by running it against real authorities rather than by
reading it: `urllib`'s matcher is `filename.startswith(rule.path)`, with **no support for `*` or `$`
at all**. Every rule `www.gov.uk` publishes is a wildcard, so a stdlib client obeys none of them,
and `www.canada.ca` has fourteen more it would silently walk past. A parser shortfall that quietly
makes this fetch **more** is the one kind this file cannot tolerate — the point is to fetch less.

So the matching below implements RFC 9309 §2.2.2–2.2.3 directly: `*` matches any run of characters,
a trailing `$` anchors to the end of the path, the **longest** matching pattern wins, and `Allow`
beats `Disallow` at equal length. Group selection is an exact product-token match, falling back to
`*` — deliberately not `urllib`'s substring test, under which a record aimed at `Visa-Bot` would
capture `VisaResearchAgent`.
"""

import asyncio
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlsplit, urlunsplit

import httpx

# Google refuses to parse past 500 KiB and so does everyone else. A file larger than this is not a
# crawl policy, and guessing at the part that fit would be inventing permission.
MAXIMUM_ROBOTS_BYTES = 512_000

# What the oversize responses actually were, measured 2026-09-01. Every one of the five reachable
# hosts that had ever tripped the cap — `rai.malaysia.gov.my`, `malaysiavisa.imi.gov.my` and the
# `ng`, `ph` and `uk` `usembassy.gov` posts — answered `200 text/html` with a web page: a
# single-page-app catch-all or a "Technical Difficulties" notice, 659 KB to 944 KB of markup with
# not one directive in it. Not one was a large crawl policy. The verdict is unchanged and stays
# CLOSED, because a policy that could not be read leaves permission unknown; what was wrong is the
# **reason**, which told a reader the authority publishes an outsized policy. A false reason is the
# failure this project treats as worse than no answer, so the two are now named apart. Recognised
# from the declared type or the markup itself, since a host serving a page here is already
# misconfigured and its `Content-Type` cannot be relied on either.
HTML_MARKERS = ("<!doctype html", "<html")

ROBOTS_TIMEOUT_SECONDS = 10.0

# How long a policy may be reused before it is read again. A day is what large crawlers use, and it
# is short enough that a site changing its mind is honoured within a day rather than whenever a
# process happens to restart. This is load-bearing rather than tuning: `get_visa_plan_service` is an
# `lru_cache(maxsize=1)`, so the fetcher holding this cache lives as long as the server does, and
# without an expiry a policy read once at boot would be obeyed forever.
ROBOTS_TTL_SECONDS = 24 * 60 * 60


@dataclass(frozen=True)
class _Rule:
    """One `Allow:` or `Disallow:` line, compiled to something that can be matched."""

    allow: bool
    pattern: str
    expression: re.Pattern[str]

    def matches(self, path: str) -> bool:
        return self.expression.match(path) is not None


def _compile(pattern: str) -> re.Pattern[str]:
    """Turn a robots path pattern into a regular expression.

    RFC 9309 §2.2.3 gives the pattern language exactly two special characters: `*` for any run of
    characters and a trailing `$` anchoring the end of the path. Everything else is literal, so it
    is escaped — `.` and `?` appear in real rules (`imm0143e.pdf`, query strings) and must not be
    read as regex syntax.
    """

    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    expression = ".*".join(re.escape(part) for part in body.split("*"))
    return re.compile(expression + ("$" if anchored else ""))


def _path_of(url: str) -> str:
    """What a rule is matched against: the path, with its query when it has one.

    A `?` and what follows it are part of the path a rule may name — `Disallow: /search/all*`
    exists to catch `/search/all?keywords=…`, and dropping the query would let exactly that
    through.
    """

    parts = urlsplit(url)
    path = parts.path or "/"
    return f"{path}?{parts.query}" if parts.query else path


class RobotsRules:
    """The rules from one `robots.txt` that apply to one product token.

    Holds only the selected group. Which group that is depends on our own name, and is decided once
    at parse time rather than on every URL.
    """

    def __init__(self, rules: list[_Rule]) -> None:
        # Longest pattern first, and `Allow` ahead of `Disallow` where the lengths tie. That is
        # RFC 9309 §2.2.2's precedence, so the first match in this order is the one that governs
        # and the search can stop there.
        self.rules = sorted(rules, key=lambda rule: (-len(rule.pattern), not rule.allow))

    def allows(self, url: str) -> bool:
        path = _path_of(url)
        for rule in self.rules:
            if rule.matches(path):
                return rule.allow
        # Nothing addressed this path, so nothing forbids it.
        return True


def parse_rules(text: str, agent_token: str) -> RobotsRules:
    """Read a `robots.txt` and keep only the group that speaks to us.

    Group selection is an **exact** token match, case-insensitively, falling back to `*`. It is
    deliberately not a substring test: `urllib` uses one, and under it a record naming `Visa-Bot`
    or `Research` would silently capture this client and impose rules written for someone else.
    """

    wanted = agent_token.lower()
    groups: dict[str, list[_Rule]] = {}
    current: list[str] = []
    # A `User-agent:` line following a rule begins a new group rather than extending the last one.
    # Without this, `UA: a` / `Disallow: /x` / `UA: b` / `Disallow: /y` gives `a` both rules.
    accepting_agents = True

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()

        if field == "user-agent":
            if not accepting_agents:
                current = []
                accepting_agents = True
            current.append(value.lower())
            groups.setdefault(value.lower(), [])
        elif field in ("allow", "disallow") and current:
            accepting_agents = False
            # An empty `Disallow:` is the long-standing way to say "nothing is forbidden". Read as
            # a pattern it would be an empty prefix, which matches every path and forbids the whole
            # site — the opposite of what was written.
            if not value:
                continue
            rule = _Rule(allow=field == "allow", pattern=value, expression=_compile(value))
            for agent in current:
                groups[agent].append(rule)

    return RobotsRules(groups.get(wanted, groups.get("*", [])))


class RobotsVerdict(Enum):
    """Whether one URL may be fetched, and — when it may not — why not.

    Three values rather than a boolean because the two refusals support different sentences, and
    the sentence is what a reader ends up being told. "The host said no" and "the host has a policy
    we could not read" are both grounds not to fetch; only one of them is a claim about what the
    host permits.
    """

    ALLOWED = "allowed"
    """Either no policy was published, or the published policy permits this client."""

    DISALLOWED = "disallowed"
    """A policy was read, and it excludes this client from this path."""

    UNREADABLE = "unreadable"
    """A policy is being served and could not be read, so permission is unknown."""


class _Policy(Enum):
    """What a host's `robots.txt` came to when it did not parse into rules."""

    OPEN = "open"
    """No policy was published, so nothing here restricts this client."""

    CLOSED = "closed"
    """A policy could not be read, so whether this client is permitted is unknown."""


def origin_of(url: str) -> str:
    """The scheme-and-authority a `robots.txt` governs.

    Keyed on the origin rather than the hostname because that is the file's actual scope: port and
    scheme each get their own policy, and a host serving different sites on two ports has not said
    anything about the second by publishing for the first.
    """

    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def user_agent_token(user_agent: str) -> str:
    """The product token a `User-agent:` line names, taken from the full header value.

    `robots.txt` records match a product token, not a header. `VisaResearchAgent/0.1 (personal visa
    research; contact repository owner)` is matched by a record naming `VisaResearchAgent`, and
    splitting here rather than relying on the parser doing it internally keeps that visible.
    """

    return user_agent.split("/")[0].strip() or "*"


def _oversize_reason(response: httpx.Response) -> str:
    """Why an over-cap response could not be read as a policy, said truly.

    Both answers leave permission unknown and both close the host, so nothing here decides what is
    fetched. What it decides is what a traveller and an audit are told, and the rule in
    [CLAUDE.md](CLAUDE.md) is that the reason must be true of what was **seen**: a host answering
    `/robots.txt` with a "Technical Difficulties" page has published no policy at all, and calling
    that an outsized one invents a fact about the authority. Measured over every host that had ever
    tripped the cap, the outsized-policy branch has never once been the true one — see
    `HTML_MARKERS`.
    """

    declared = response.headers.get("content-type", "").split(";")[0].strip().lower()
    body = response.content[:1024].lstrip().lower()
    is_page = declared == "text/html" or body.startswith(tuple(m.encode() for m in HTML_MARKERS))
    if is_page:
        return "answered with a web page rather than a crawl policy"
    return "is larger than the size limit for a crawl policy"


class RobotsCache:
    """Each origin's crawl policy, fetched once and re-read when it expires.

    Expiry matters more than it looks. The fetchers holding one of these are built behind
    `lru_cache(maxsize=1)`, so they live as long as the server process — a cache with no TTL would
    keep obeying a policy read at boot until someone restarted the thing, including a `Disallow`
    the site had since withdrawn and a permission it had since revoked.
    """

    def __init__(
        self,
        *,
        user_agent: str,
        timeout_seconds: float = ROBOTS_TIMEOUT_SECONDS,
        maximum_bytes: int = MAXIMUM_ROBOTS_BYTES,
        ttl_seconds: float = ROBOTS_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.agent_token = user_agent_token(user_agent)
        self.timeout_seconds = timeout_seconds
        self.maximum_bytes = maximum_bytes
        self.ttl_seconds = ttl_seconds
        self.clock = clock
        # Origin to the policy and the moment it was read.
        self._policies: dict[str, tuple[float, RobotsRules | _Policy]] = {}
        # Why an origin's policy could not be read, in the words of what was observed. Carried so a
        # caller can say "its robots.txt answered HTTP 502" rather than the true but unhelpful
        # "its robots.txt could not be read" — which sends a reader to look at a crawl policy when
        # the fact in front of them is a dead gateway serving 502 to every path on the host.
        self.unreadable: dict[str, str] = {}
        # One fetch per origin even when a wave of pages on that host is checked at once. The lock
        # is held across the fetch, so the second caller waits for the first's answer rather than
        # asking again for the same file.
        self._locks: dict[str, asyncio.Lock] = {}
        # Which policies were actually read, for tests and for anyone reading a run.
        self.fetched: list[str] = []

    def unreadable_detail(self, url: str) -> str:
        """What was actually seen when this origin's policy could not be read.

        A phrase rather than a sentence, so each caller can word the consequence in its own terms.
        """

        return self.unreadable.get(origin_of(url), "could not be read")

    async def verdict(self, client: httpx.AsyncClient, url: str) -> RobotsVerdict:
        """Whether this host's published policy permits this client to fetch this URL.

        Raises `httpx.HTTPError` when the policy itself could not be requested. That is on purpose:
        the caller is already the place that knows how to describe a host it could not reach, and
        an unreachable host is not a crawl policy.

        Deliberately outside the crawl's per-host politeness delay. That delay spaces a host's
        *crawl* requests, and it only ever bites on the second one — its own rule is that a host
        asked for the first time waits not at all. A `robots.txt` fetch is always the first request
        to an origin and there is one per run, so routing it through the delay would not space
        anything; it would only make first contact with every host cost the delay, to read the file
        the host publishes so that clients read it before crawling.
        """

        origin = origin_of(url)
        lock = self._locks.setdefault(origin, asyncio.Lock())
        async with lock:
            entry = self._policies.get(origin)
            if entry is None or self.clock() - entry[0] >= self.ttl_seconds:
                policy = await self._load(client, origin)
                self._policies[origin] = (self.clock(), policy)
            else:
                policy = entry[1]

        if policy is _Policy.OPEN:
            return RobotsVerdict.ALLOWED
        if policy is _Policy.CLOSED:
            return RobotsVerdict.UNREADABLE
        if policy.allows(url):
            return RobotsVerdict.ALLOWED
        return RobotsVerdict.DISALLOWED

    async def _load(self, client: httpx.AsyncClient, origin: str) -> RobotsRules | _Policy:
        """Fetch and parse one origin's `robots.txt`, or decide what its absence means."""

        url = f"{origin}/robots.txt"
        self.fetched.append(url)
        # Not caught. A transport failure here belongs to the caller's account of the host, not to
        # this one's account of a policy — see the module docstring.
        response = await client.get(
            url, headers={"Accept": "text/plain"}, timeout=self.timeout_seconds
        )

        if response.is_server_error:
            self.unreadable[origin] = f"answered HTTP {response.status_code}"
            return _Policy.CLOSED
        if not response.is_success:
            # Any other non-2xx means no policy is being served here. Redirects are followed by the
            # caller's client, so one reaching this branch has already exhausted its hops.
            return _Policy.OPEN
        if len(response.content) > self.maximum_bytes:
            self.unreadable[origin] = _oversize_reason(response)
            return _Policy.CLOSED

        return parse_rules(response.text, self.agent_token)
