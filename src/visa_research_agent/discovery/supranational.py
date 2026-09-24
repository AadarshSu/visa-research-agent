"""Authorities above a country that may answer part of its question (DECISIONS entry 201).

The European Union answers the visa decision for the 29 Schengen states: who needs a short-stay visa
is EU law, the same for every member, and several members publish nothing more than "part of the EU
acquis". The trust rule — governmental and under the destination's own top-level domain — refuses
the one authority that states it, so this is a second tier beside it, in committed data, narrower in
two ways: only for the listed members, and only for the listed roles.

**Nothing here widens a country's own list.** The union's domains travel on `DestinationConfig` as
`supranational_domains`, beside `trusted_domains`, so every check that reads a trusted domain reads
these too and nothing can mistake one for the country's own government.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

import httpx
import yaml
from bs4 import BeautifulSoup
from pydantic import Field, model_validator

from visa_research_agent.discovery.corpus import CorpusEntry, CountryCorpus, FileCorpusStore
from visa_research_agent.discovery.crawl import CrawlFetcher, page_title_of
from visa_research_agent.discovery.models import PageLink
from visa_research_agent.discovery.page_text import PageTextStore, StoredPage
from visa_research_agent.domain.models import DestinationConfig, StrictModel
from visa_research_agent.domain.trust import is_bare_public_suffix
from visa_research_agent.research.live_sources import clean_source_html
from visa_research_agent.research.tls import build_ssl_context

MAXIMUM_UNION_PAGE_CHARACTERS = 400_000
MINIMUM_UNION_PAGE_CHARACTERS = 1_000
"""The consolidated regulation is ~57,000 characters with its annexes; room for it to grow."""


class UnionSource(StrictModel):
    """A page the offline refresh reads for the union."""

    url: str = Field(min_length=1)
    follow_newest: str | None = None
    """A pattern for dated links on this page, its group the date; the refresh reads the newest such
    link, exactly as the page gives it. The regulation's consolidated versions carry their date in
    the address, and a committed address would go stale at the next amendment."""


class Union(StrictModel):
    """One supranational authority and what it may answer for whom."""

    code: str = Field(pattern=r"^[A-Z]{2}$")
    name: str = Field(min_length=1)
    members: list[str] = Field(min_length=1)
    roles: list[str] = Field(min_length=1)
    reviewed: dict[str, str] = Field(min_length=1)
    """Each domain with the evidence for it — the same contract as `authority_domains.yaml`."""
    challenge_script_hosts: dict[str, list[str]] = Field(default_factory=dict)
    sources: list[UnionSource] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_every_domain_is_evidenced_and_narrow(self) -> "Union":
        for domain, evidence in self.reviewed.items():
            if not evidence.strip():
                raise ValueError(f"{self.code}: {domain} needs the evidence for it")
            if is_bare_public_suffix(domain):
                raise ValueError(f"{self.code}: {domain} is a public suffix")
        unknown = set(self.challenge_script_hosts) - set(self.reviewed)
        if unknown:
            raise ValueError(
                f"{self.code}: challenge hosts are listed for pages of unreviewed hosts: "
                + ", ".join(sorted(unknown))
            )
        for source in self.sources:
            if source.follow_newest is not None:
                re.compile(source.follow_newest)
        return self


class SupranationalRegistry(StrictModel):
    unions: list[Union] = Field(default_factory=list)

    def for_member(self, code: str) -> Union | None:
        """The union that may answer for this country, if any. At most one: a country in two would
        need a rule for which of them speaks, and there is no such country here."""

        matches = [union for union in self.unions if code in union.members]
        if len(matches) > 1:
            raise ValueError(f"{code} is a member of more than one union")
        return matches[0] if matches else None

    def by_code(self, code: str) -> Union | None:
        return next((union for union in self.unions if union.code == code), None)


def load_supranational_registry(path: Path | None = None) -> SupranationalRegistry:
    text = (
        path.read_text(encoding="utf-8")
        if path is not None
        else files("visa_research_agent.config")
        .joinpath("supranational_authorities.yaml")
        .read_text(encoding="utf-8")
    )
    return SupranationalRegistry.model_validate(yaml.safe_load(text))


@lru_cache(maxsize=1)
def get_supranational_registry() -> SupranationalRegistry:
    return load_supranational_registry()


def with_union(config: DestinationConfig, country_code: str) -> DestinationConfig:
    """The destination with its union attached where it has one, unchanged where it does not."""

    union = get_supranational_registry().for_member(country_code)
    if union is None:
        return config
    return config.model_copy(
        update={
            "supranational_authority": union.name,
            "supranational_domains": list(union.reviewed),
            "supranational_roles": list(union.roles),
            "challenge_script_hosts": {
                host: list(hosts) for host, hosts in union.challenge_script_hosts.items()
            },
        }
    )


def union_destination(union: Union) -> DestinationConfig:
    """A destination whose only trusted domains are the union's, for reading its own pages."""

    return DestinationConfig(
        slug=union.name.lower().replace(" ", "-"),
        display_name=union.name,
        route_type="national",
        implementation_status="available",
        trusted_domains=list(union.reviewed),
        challenge_script_hosts={
            host: list(hosts) for host, hosts in union.challenge_script_hosts.items()
        },
    )


def newest_dated_link(html: str, base_url: str, pattern: str) -> str | None:
    """The newest link on a page matching `pattern`, by the date its group captures.

    The address is the page's own — read out of its markup by our code, never assembled — so what a
    corridor later reads is exactly what the authority links as its newest version."""

    compiled = re.compile(pattern)
    dated: dict[str, str] = {}
    # The raw `href`, joined to the page and otherwise untouched. `canonicalise_url` drops a
    # trailing slash before a query, and EUR-Lex answers `…/TXT/HTML?uri=` with "Page Not Found"
    # where `…/TXT/HTML/?uri=` is the text (entry 201).
    for element in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = element.get("href")
        if not isinstance(href, str):
            continue
        try:
            url = str(httpx.URL(base_url).join(href.strip()))
        except (httpx.InvalidURL, ValueError):
            continue
        match = compiled.search(url)
        if match is not None:
            dated.setdefault(match.group(1), url)
    return dated[max(dated)] if dated else None


@dataclass
class RefreshReport:
    union: str
    stored: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)


async def refresh_union_store(
    union: Union,
    fetcher: CrawlFetcher,
    corpora: FileCorpusStore,
    page_text: PageTextStore,
    *,
    now: datetime,
) -> RefreshReport:
    """Read the union's listed pages and keep their addresses and text as its shared store.

    Offline and small: no search, only the pages `supranational_authorities.yaml` lists, and the
    newest version a listed page links to. Everything is read through `CrawlFetcher`, so trust,
    robots.txt and the challenge rules apply exactly as they do to any build. **The address a
    corridor reads is one our code took from an approved page's links** — the newest consolidation
    EUR-Lex itself links — never one written into a file that would go stale.

    A page that cannot be read is reported and left out rather than kept from an earlier refresh,
    because an older consolidation served as current is the wrong answer this store exists to avoid.
    """

    destination = union_destination(union)
    report = RefreshReport(union=union.code)
    entries: list[CorpusEntry] = []
    pages: list[StoredPage] = []
    async with httpx.AsyncClient(
        transport=fetcher.transport,
        timeout=fetcher.timeout_seconds,
        follow_redirects=True,
        verify=build_ssl_context(),
        headers={
            "User-Agent": fetcher.user_agent,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-GB,en;q=0.9",
        },
    ) as client:
        for source in union.sources:
            target = source.url
            if source.follow_newest is not None:
                listing = await fetcher.fetch_html(client, source.url, destination)
                newest = (
                    newest_dated_link(listing, source.url, source.follow_newest)
                    if listing
                    else None
                )
                if newest is None:
                    report.failed[source.url] = (
                        "no dated link to follow was found on it"
                        if listing
                        else fetcher.failures.get(source.url, "it could not be read")
                    )
                    continue
                target = newest
            html = await fetcher.fetch_html(client, target, destination)
            text = (
                clean_source_html(html, maximum_characters=MAXIMUM_UNION_PAGE_CHARACTERS)
                if html
                else ""
            )
            if len(text.strip()) < MINIMUM_UNION_PAGE_CHARACTERS:
                # Too short to be what was asked for — EUR-Lex's "Page Not Found" is 388 characters.
                report.failed[target] = fetcher.failures.get(
                    target, f"it returned {len(text.strip())} characters, too little to trust"
                )
                continue
            title = page_title_of(html or "") or union.name
            entries.append(
                CorpusEntry(
                    url=target,
                    title=title,
                    link_text=title[:300],
                    discovered_from=source.url,
                    first_seen=now,
                    last_seen=now,
                    status="readable",
                )
            )
            pages.append(StoredPage(url=target, fetched_at=now, body=text, title=title))
            report.stored.append(target)

    if entries:
        corpora.store(
            CountryCorpus(
                country_code=union.code,
                country_name=union.name,
                trusted_domains=list(union.reviewed),
                built_at=now,
                entries=entries,
            )
        )
        page_text.write(union.code, pages)
    return report


def union_pages(union: Union | None, corpora: FileCorpusStore | None) -> list[tuple[PageLink, str]]:
    """The pages a member corridor reads on every run, from the union's shared store."""

    if union is None or corpora is None:
        return []
    corpus = corpora.load(union.code)
    if corpus is None:
        return []
    return [(entry.to_link(), entry.title) for entry in corpus.entries_within(union.reviewed)]


def union_of(destination: DestinationConfig) -> Union | None:
    """The union a destination carries, if any — the one `with_union` attached."""

    if not destination.supranational_domains:
        return None
    return next(
        (
            union
            for union in get_supranational_registry().unions
            if list(union.reviewed) == destination.supranational_domains
        ),
        None,
    )
