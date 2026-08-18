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
* **5xx or an oversized file** — the server is answering, and the policy it holds could not be
  read, so whether we are permitted is **unknown**. The standard says to assume we are not, which
  is the direction every other unknown in this project fails in.

**A network failure is deliberately not one of those, and it raises rather than deciding.** It is
not a fact about a crawl policy — it is a fact about the host, and the caller already has machinery
that says so correctly, including telling a name that does not resolve from a request that merely
failed. Swallowing it here would have made every dead host report as *"its robots.txt does not
permit this client"*, which is a **false reason**, and a false reason is the failure mode this
project treats as worse than no answer at all.

Parsing is `urllib.robotparser` rather than a hand-written matcher: it is stdlib, it is far better
tested than anything that would be written here, and a bug in it costs coverage rather than
inventing permission. Its one known shortfall — `Allow` and `Disallow` are matched in file order
rather than by longest match — also errs toward fetching less.
"""

import asyncio
import time
from collections.abc import Callable
from enum import Enum
from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx

# Google refuses to parse past 500 KiB and so does everyone else. A file larger than this is not a
# crawl policy, and guessing at the part that fit would be inventing permission.
MAXIMUM_ROBOTS_BYTES = 512_000

ROBOTS_TIMEOUT_SECONDS = 10.0

# How long a policy may be reused before it is read again. A day is what large crawlers use, and it
# is short enough that a site changing its mind is honoured within a day rather than whenever a
# process happens to restart. This is load-bearing rather than tuning: `get_visa_plan_service` is an
# `lru_cache(maxsize=1)`, so the fetcher holding this cache lives as long as the server does, and
# without an expiry a policy read once at boot would be obeyed forever.
ROBOTS_TTL_SECONDS = 24 * 60 * 60


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
        self._policies: dict[str, tuple[float, RobotFileParser | _Policy]] = {}
        # One fetch per origin even when a wave of pages on that host is checked at once. The lock
        # is held across the fetch, so the second caller waits for the first's answer rather than
        # asking again for the same file.
        self._locks: dict[str, asyncio.Lock] = {}
        # Which policies were actually read, for tests and for anyone reading a run.
        self.fetched: list[str] = []

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
        if policy.can_fetch(self.agent_token, url):
            return RobotsVerdict.ALLOWED
        return RobotsVerdict.DISALLOWED

    async def _load(self, client: httpx.AsyncClient, origin: str) -> RobotFileParser | _Policy:
        """Fetch and parse one origin's `robots.txt`, or decide what its absence means."""

        url = f"{origin}/robots.txt"
        self.fetched.append(url)
        # Not caught. A transport failure here belongs to the caller's account of the host, not to
        # this one's account of a policy — see the module docstring.
        response = await client.get(
            url, headers={"Accept": "text/plain"}, timeout=self.timeout_seconds
        )

        if response.is_server_error:
            return _Policy.CLOSED
        if not response.is_success:
            # Any other non-2xx means no policy is being served here. Redirects are followed by the
            # caller's client, so one reaching this branch has already exhausted its hops.
            return _Policy.OPEN
        if len(response.content) > self.maximum_bytes:
            return _Policy.CLOSED

        parser = RobotFileParser()
        parser.parse(response.text.splitlines())
        return parser
