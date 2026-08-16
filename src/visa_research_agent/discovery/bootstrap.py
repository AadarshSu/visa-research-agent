"""Proposing the official domains for a country that has never been configured.

This is the only place where search results are not already bounded by an approved domain, so it
is the only place where search genuinely adds risk. Everything here exists to keep that risk in
front of a human rather than behind one:

  * a denylist removes commercial visa agencies before anyone reads the list;
  * a domain must be corroborated by more than one query, so a single lucky ranking is not enough;
  * bare public suffixes are rejected outright, because trusting `gov.sg` would trust every site
    beneath it;
  * government-shaped domains are ranked higher but never admitted automatically.

Nothing here approves anything. It produces a short, evidenced list for a person to accept.
"""

import re
from urllib.parse import urlsplit

from pydantic import Field

from visa_research_agent.discovery.lexicon import Denylist
from visa_research_agent.discovery.models import SearchResult
from visa_research_agent.discovery.search import SearchProvider, bootstrap_queries
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.domain.trust import host_of, is_bare_public_suffix

# Hostname shapes that governments use. A strong hint, never a decision: legitimate authorities sit
# outside these patterns and spam imitates them.
GOVERNMENT_PATTERNS = (
    re.compile(r"(^|\.)gov(\.[a-z]{2,})?$"),
    re.compile(r"(^|\.)go\.[a-z]{2}$"),
    re.compile(r"(^|\.)gouv\.[a-z]{2}$"),
    re.compile(r"(^|\.)gob\.[a-z]{2}$"),
    re.compile(r"(^|\.)govt\.[a-z]{2}$"),
    re.compile(r"(^|\.)gc\.ca$"),
    re.compile(r"(^|\.)admin\.ch$"),
    re.compile(r"(^|\.)europa\.eu$"),
)

# Words in a hostname that suggest which kind of authority it is. Shown to the reviewer as a hint.
KIND_HINTS: tuple[tuple[str, str], ...] = (
    ("immi", "immigration_authority"),
    ("immigration", "immigration_authority"),
    ("ica", "immigration_authority"),
    ("emb", "embassy_or_high_commission"),
    ("embassy", "embassy_or_high_commission"),
    ("consul", "embassy_or_high_commission"),
    ("mofa", "foreign_ministry"),
    ("mfa", "foreign_ministry"),
    ("foreign", "foreign_ministry"),
)

MINIMUM_CORROBORATING_QUERIES = 2
# A governmental domain under the destination's own top-level domain is such a strong signal that
# one query is enough. Vietnam's own foreign ministry was otherwise discarded for appearing once.
MINIMUM_CORROBORATING_QUERIES_FOR_OWN_GOVERNMENT = 1


def registrable_domain(host: str) -> str:
    """Reduce a hostname to the domain worth trusting.

    Keeps three labels for multi-part public suffixes (`ica.gov.sg`) and two otherwise
    (`example.com`), which matches how `trusted_domains` entries are written by hand.
    """

    labels = host.lower().strip(".").split(".")
    if len(labels) <= 2:
        return ".".join(labels)
    candidate_two = ".".join(labels[-2:])
    # If the last two labels are themselves a suffix, the registrable domain needs a third.
    if is_bare_public_suffix(candidate_two):
        return ".".join(labels[-3:])
    return candidate_two


class DomainProposal(StrictModel):
    """One candidate authority domain, with the evidence that produced it."""

    domain: str = Field(min_length=1)
    looks_governmental: bool
    belongs_to_destination: bool = False
    """True when the domain sits under the destination country's own top-level domain."""

    suggested_kind: str | None = None
    queries: list[str] = Field(default_factory=list)
    example_urls: list[str] = Field(default_factory=list)
    titles: list[str] = Field(default_factory=list)

    @property
    def corroboration(self) -> int:
        return len(set(self.queries))


class BootstrapReport(StrictModel):
    """What bootstrap found, and what it threw away and why."""

    destination_name: str
    proposals: list[DomainProposal] = Field(default_factory=list)
    rejected: dict[str, str] = Field(default_factory=dict)
    queries_run: list[str] = Field(default_factory=list)


def looks_governmental(domain: str) -> bool:
    return any(pattern.search(domain) for pattern in GOVERNMENT_PATTERNS)


def belongs_to_destination(domain: str, destination_tlds: list[str]) -> bool:
    """True when a domain sits under one of the destination country's own top-level domains.

    This is what separates Vietnam's immigration department from the US embassy in Vietnam. Both
    are real governments and both look governmental; only one sets Vietnam's entry rules.
    """

    lowered = domain.lower().strip(".")
    return any(lowered == tld or lowered.endswith(f".{tld}") for tld in destination_tlds)


def suggest_kind(domain: str) -> str | None:
    for token, kind in KIND_HINTS:
        if token in domain:
            return kind
    return None


def propose_domains(
    destination_name: str,
    results_by_query: dict[str, list[SearchResult]],
    denylist: Denylist,
    destination_tlds: list[str] | None = None,
) -> BootstrapReport:
    """Turn raw search results into a short reviewable list of candidate authority domains."""

    grouped: dict[str, DomainProposal] = {}
    rejected: dict[str, str] = {}

    for query, results in results_by_query.items():
        for result in results:
            host = host_of(result.url)
            if not host:
                continue
            domain = registrable_domain(host)
            if domain in rejected:
                continue

            if denylist.blocks(host):
                rejected[domain] = "on the denylist of agencies and non-authoritative sites"
                grouped.pop(domain, None)
                continue
            if is_bare_public_suffix(domain):
                rejected[domain] = "a public suffix, which would trust every site beneath it"
                grouped.pop(domain, None)
                continue

            proposal = grouped.get(domain)
            if proposal is None:
                proposal = DomainProposal(
                    domain=domain,
                    looks_governmental=looks_governmental(domain),
                    belongs_to_destination=belongs_to_destination(domain, destination_tlds or []),
                    suggested_kind=suggest_kind(domain),
                )
                grouped[domain] = proposal
            proposal.queries.append(query)
            if len(proposal.example_urls) < 3:
                proposal.example_urls.append(result.url)
            if result.title and len(proposal.titles) < 3:
                proposal.titles.append(result.title)

    proposals: list[DomainProposal] = []
    for domain, proposal in grouped.items():
        own_government = proposal.belongs_to_destination and proposal.looks_governmental
        needed = (
            MINIMUM_CORROBORATING_QUERIES_FOR_OWN_GOVERNMENT
            if own_government
            else MINIMUM_CORROBORATING_QUERIES
        )
        if proposal.corroboration < needed:
            rejected[domain] = (
                f"appeared in only {proposal.corroboration} of the queries; at least "
                f"{needed} are needed"
            )
            continue
        proposals.append(proposal)

    # The destination's own government first. Another country's government may still be worth
    # seeing, but it must never head the list: it describes its own citizens' rules, not this
    # destination's.
    proposals.sort(
        key=lambda p: (
            not (p.belongs_to_destination and p.looks_governmental),
            not p.belongs_to_destination,
            not p.looks_governmental,
            -p.corroboration,
            p.domain,
        )
    )
    return BootstrapReport(
        destination_name=destination_name,
        proposals=proposals,
        rejected=rejected,
        queries_run=list(results_by_query),
    )


async def bootstrap_destination(
    destination_name: str,
    provider: SearchProvider,
    denylist: Denylist,
    *,
    destination_tlds: list[str] | None = None,
    results_per_query: int = 10,
) -> BootstrapReport:
    """Search for a country's official authorities and return candidates for human approval."""

    results_by_query: dict[str, list[SearchResult]] = {}
    for query in bootstrap_queries(destination_name):
        results_by_query[query] = await provider.search(query, count=results_per_query)
    return propose_domains(destination_name, results_by_query, denylist, destination_tlds)


def entry_point_for(proposal: DomainProposal) -> str | None:
    """The most visa-relevant URL seen for a domain, used as a crawl seed once approved."""

    ranked = sorted(
        proposal.example_urls,
        key=lambda url: (0 if "visa" in urlsplit(url).path.lower() else 1, len(url)),
    )
    return ranked[0] if ranked else None
