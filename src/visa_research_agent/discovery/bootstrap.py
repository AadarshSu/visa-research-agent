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
from visa_research_agent.discovery.search import (
    SearchProvider,
    bootstrap_queries,
    search_all,
)
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.domain.trust import (
    host_of,
    is_bare_public_suffix,
    registrable_domain,
)

# Re-exported: reducing a host to the domain worth trusting is a trust rule and lives beside the
# others, but it was named here first and is imported from here by callers and tests.
__all__ = [
    "BootstrapReport",
    "DomainProposal",
    "belongs_to_destination",
    "bootstrap_destination",
    "entry_point_for",
    "looks_governmental",
    "matched_destination_tlds",
    "propose_domains",
    "registrable_domain",
    "suggest_kind",
]

# Hostname shapes that governments use. A strong hint, never a decision: legitimate authorities sit
# outside these patterns and spam imitates them.
#
# Two shapes, and they carry different risk.
#
# Second-level labels that name a **government namespace** under a country code — `gov.sg`, `go.jp`,
# `gv.at`. What makes these worth trusting is not that they read as official but that the registry
# restricts who may register beneath them: you cannot buy `foo.gv.at`. That is the unforgeable
# property entry 2 is really asking for, and it is why matching is anchored to a label boundary at
# the end — `visa-gov.com` and `gov-uk.com` do not match, and `tests/test_trust.py` holds that.
#
# **Every label here must also be in `trust.SUFFIX_MARKER_LABELS`**, or a domain inside the
# namespace reduces to the namespace itself and trusting one authority trusts that whole
# government. `tests/test_trust.py` asserts the containment; the note on that list records what
# adding `gv` uncovered.
GOVERNMENT_NAMESPACE_LABELS = ("gov", "go", "gouv", "gob", "gv", "gub", "govt")

# Single domains that are a government's own, rather than a namespace anyone in that government may
# register under. The safer of the two shapes — a subdomain can only be created by whoever holds the
# domain — and the only way to recognise a government that marks its hostnames not at all.
NAMED_GOVERNMENT_DOMAINS = ("gc.ca", "canada.ca", "admin.ch", "europa.eu")

# `gv`, `gub` and `canada.ca` were added 2026-08-25, and they are **corrections inside this rule
# rather than relaxations of it** — the distinction CLAUDE.md draws, and why they need no decision
# entry. Austria's ministry is `bmeia.gv.at` and Uruguay's government is `gub.uy`: both are the same
# idea as `gov`, spelled the way their own registry spells it, and neither was on the list. Canada's
# immigration content had moved from the already-named `gc.ca` to `canada.ca` and the rule did not
# follow, which is why entry 33 recorded Canada as a government that passes the rule while its
# guidance sat where the trusted set could not reach.
#
# The namespace patterns are as general as `go`/`gob`/`gouv`/`govt` already were: they admit
# `gv.<any ccTLD>`, and a country selling that namespace openly would be a hole here exactly as it
# would be there. Nothing is *decided* by this list — a match still has to be paired with
# `belongs_to_destination` — so the exposure is bounded by the same second half as the rest.
GOVERNMENT_PATTERNS = (
    # `gov` is the general case and is also its own top-level domain, so it allows a bare `.gov`
    # and a suffix of any length: `nasa.gov` and `ica.gov.sg` both match.
    re.compile(r"(^|\.)gov(\.[a-z]{2,})?$"),
    *(
        re.compile(rf"(^|\.){label}\.[a-z]{{2}}$")
        for label in GOVERNMENT_NAMESPACE_LABELS
        if label != "gov"
    ),
    *(re.compile(rf"(^|\.){re.escape(domain)}$") for domain in NAMED_GOVERNMENT_DOMAINS),
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
#
# It is only that strong when the two halves are *independent* signals, which is what
# `DomainProposal.ownership_is_independent` decides. Where they are not, appearing once means only
# "one of this government's many domains happened to rank once", and the ordinary bar applies.
MINIMUM_CORROBORATING_QUERIES_FOR_OWN_GOVERNMENT = 1


class DomainProposal(StrictModel):
    """One candidate authority domain, with the evidence that produced it."""

    domain: str = Field(min_length=1)
    looks_governmental: bool
    belongs_to_destination: bool = False
    """True when the domain sits under the destination country's own top-level domain."""

    matched_tlds: list[str] = Field(default_factory=list)
    """Which of the destination's own top-level domains this domain was found to sit under."""

    suggested_kind: str | None = None
    queries: list[str] = Field(default_factory=list)
    example_urls: list[str] = Field(default_factory=list)
    titles: list[str] = Field(default_factory=list)

    @property
    def corroboration(self) -> int:
        return len(set(self.queries))

    @property
    def is_own_government(self) -> bool:
        """The destination country's own government: governmental **and** under its own domain.

        Both halves are load-bearing. `looks_governmental` alone admits any country's government —
        the US embassy's page about Vietnam. `belongs_to_destination` alone admits any site under
        the country's top-level domain, including its commercial ones.
        """

        return self.looks_governmental and self.belongs_to_destination

    @property
    def ownership_is_independent(self) -> bool:
        """True when belonging to the destination says something `looks_governmental` did not.

        For almost every country the two halves ask different questions: `gouv.fr` is governmental,
        `.fr` is France's. But a country whose own top-level domain *is* the generic governmental
        marker — `gov` — collapses them into one question, and the whole of that government's
        namespace is admitted rather than its visa authorities. The test is which top-level domain
        actually matched, so it is a property of the data in `countries.yaml` and never of a
        particular country.
        """

        return any(not looks_governmental(tld) for tld in self.matched_tlds)


class BootstrapReport(StrictModel):
    """What bootstrap found, and what it threw away and why."""

    destination_name: str
    proposals: list[DomainProposal] = Field(default_factory=list)
    rejected: dict[str, str] = Field(default_factory=dict)
    queries_run: list[str] = Field(default_factory=list)


def looks_governmental(domain: str) -> bool:
    return any(pattern.search(domain) for pattern in GOVERNMENT_PATTERNS)


def matched_destination_tlds(domain: str, destination_tlds: list[str]) -> list[str]:
    """Which of the destination country's own top-level domains a domain sits under.

    Which one matched is kept rather than only whether one did, because a match on a plain country
    code and a match on `gov` are not equally informative. See
    `DomainProposal.ownership_is_independent`.
    """

    lowered = domain.lower().strip(".")
    return [
        tld for tld in destination_tlds if lowered == tld or lowered.endswith(f".{tld.strip('.')}")
    ]


def belongs_to_destination(domain: str, destination_tlds: list[str]) -> bool:
    """True when a domain sits under one of the destination country's own top-level domains.

    This is what separates Vietnam's immigration department from the US embassy in Vietnam. Both
    are real governments and both look governmental; only one sets Vietnam's entry rules.
    """

    return bool(matched_destination_tlds(domain, destination_tlds))


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
                matched = matched_destination_tlds(domain, destination_tlds or [])
                proposal = DomainProposal(
                    domain=domain,
                    looks_governmental=looks_governmental(domain),
                    belongs_to_destination=bool(matched),
                    matched_tlds=matched,
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
        # The relaxed bar is earned by the two halves of the own-government rule being two
        # separate signals. Where the destination's own top-level domain is itself the
        # governmental marker they are one, so a single appearance is not evidence that this
        # domain, out of that government's whole namespace, is a visa authority.
        relaxed = proposal.is_own_government and proposal.ownership_is_independent
        needed = (
            MINIMUM_CORROBORATING_QUERIES_FOR_OWN_GOVERNMENT
            if relaxed
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
            not p.is_own_government,
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

    results_by_query = await search_all(
        provider, bootstrap_queries(destination_name), count=results_per_query
    )
    return propose_domains(destination_name, results_by_query, denylist, destination_tlds)


def entry_point_for(proposal: DomainProposal) -> str | None:
    """The most visa-relevant URL seen for a domain, used as a crawl seed once approved."""

    ranked = sorted(
        proposal.example_urls,
        key=lambda url: (0 if "visa" in urlsplit(url).path.lower() else 1, len(url)),
    )
    return ranked[0] if ranked else None
