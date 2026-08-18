"""Resolving a destination nobody configured, without a person in the loop.

Until now a human approved every domain before anything was fetched. That gate is removed here,
and what replaces it is **not** trust in search — it is the rule the human was actually applying.
Reviewing six bootstraps, every accept and every reject reduced to one question: *is this domain
the destination country's own government?* Those are the two properties `bootstrap.py` already
computes, and the rule reproduces all 22 recorded human decisions with no disagreements.

**Where that rule runs changed on 2026-08-18 (DECISIONS entry 34).** It used to run inside every
cold request, cached per *corridor*, so a country's trusted set was re-derived from that day's
search rankings for every new nationality — entry 22's United States coin flip was this, diagnosed
at the time as ranking. The rule is unchanged and `auto_trusted_domains` below is still the whole of
it; what moved is *when*. It is now run offline for all 198 countries, read once by a person, and
committed as `authority_domains.yaml`. This service reads that file. Nothing here searches for a
domain any more, so two requests for the same country cannot disagree about whose government it is.

What the rule keeps out is the point of it. France's bootstrap surfaced `axa-schengen.com`, a
commercial travel insurer; Vietnam's ranked `usembassy.gov` first, which is a real government
describing the rules for *Americans*; Brazil's offered VFS, an appointed provider that by design
cannot pass domain trust. None of those is under the destination's own government, and none is
admitted.

The rule says which domains *may* be used. It does not say how many should be, and that turned out
to matter: it was calibrated against countries whose government is small enough that its own
top-level domain names only a handful of domains. A large government's whole namespace passes the
same rule, and the cost lands on everything downstream — three searches per trusted domain, a crawl
budget divided by the hosts seeded, ten places in the shortlist. So the set is also capped, and
ordered by the authority hint the hostname carries, before anything is fetched.

Everything downstream is unchanged. Approved domains still pass `is_bare_public_suffix`, pages are
still fetched only from them, redirects and renders are still re-checked, and a corridor that
cannot fill a load-bearing role is still refused rather than filled in.
"""

from collections.abc import Callable
from datetime import UTC, datetime

from visa_research_agent.discovery.bootstrap import BootstrapReport, DomainProposal
from visa_research_agent.discovery.corridor_store import FileCorridorStore
from visa_research_agent.discovery.lexicon import (
    Country,
    CountryRegistry,
    Denylist,
    get_country_registry,
    get_denylist,
)
from visa_research_agent.discovery.models import Corridor, ResolvedCorridor
from visa_research_agent.discovery.registry import AuthorityRegistry, get_authority_registry
from visa_research_agent.discovery.resolver import CorridorResolver
from visa_research_agent.discovery.search import SearchProvider
from visa_research_agent.domain.models import DestinationConfig, StrictModel
from visa_research_agent.research.errors import VisaResearchError


class AutomaticDiscoveryError(VisaResearchError):
    """Raised when a destination cannot be resolved automatically, with a reason to show."""


# How many of a destination's own domains one bootstrap may put into use. A bound on the
# consequence rather than a test for any particular cause: whatever makes a trusted set wide, the
# cost is the same. Three searches are run per trusted domain, the crawl's per-host budget is the
# page budget divided by the number of hosts seeded, and the shortlist has ten places — so a wide
# set spends more, reads less of each site, and makes the right page compete with more noise.
#
# Five is calibration against the corridors run so far, not a derived number: the ones that resolve
# accepted one, two and four domains, and the United States accepted eight. It is deliberately
# above every accept in the audit behind DECISIONS entry 19, so no recorded decision changes.
MAXIMUM_AUTO_TRUSTED_DOMAINS = 5


def is_own_government(proposal: DomainProposal) -> bool:
    """The rule that replaces the human approval gate."""

    return proposal.is_own_government


def _trust_priority(proposal: DomainProposal) -> tuple[int, int, str]:
    """Order own-government domains by how likely they are to be a visa authority.

    This ranks *within* a set every member of which has already passed domain trust; it is not part
    of deciding whether a domain is official. `suggested_kind` is read from the hostname alone —
    `emb`, `consul`, `immi`, `mofa` — the same class of evidence as `looks_governmental` and the
    same inference `derive_authority` makes when naming an authority. Nothing about how a page reads
    or where search ranked it enters here, so two runs over the same proposals order them the same.

    Among domains with no hint and equal corroboration the order is alphabetical, which is
    arbitrary but stable: a hostname carries no further signal about whether that part of a
    government issues visas.
    """

    return (0 if proposal.suggested_kind else 1, -proposal.corroboration, proposal.domain)


def auto_trusted_domains(
    report: BootstrapReport,
    *,
    maximum_trusted: int = MAXIMUM_AUTO_TRUSTED_DOMAINS,
) -> tuple[list[str], dict[str, str]]:
    """Split a bootstrap into what may be trusted without a person, and what may not.

    The withheld list is returned rather than dropped: a corridor that then resolves nothing should
    be able to say which plausible-looking domains it declined to trust, and why. It carries what
    bootstrap rejected outright as well, so everything declined leaves one trace in one place.

    **Each reason has to be true, because this list is the only mitigation there is.** Known problem
    2 tells a reviewer to read it and look for domains declined that should not have been. Until
    2026-08-18 a domain under the destination's own top-level domain carrying no governmental
    marker fell through to "not a government domain for this destination" — which said something
    false about Italy's `esteri.it`, in wording identical to what a commercial visa agency got, so
    the one safeguard misled instead of warning. That case now says what is true: this rule cannot
    confirm it. See DECISIONS entry 33.
    """

    accepted: list[str] = []
    withheld: dict[str, str] = dict(report.rejected)
    destination = report.destination_name

    for proposal in sorted(report.proposals, key=_trust_priority):
        if not proposal.is_own_government:
            if proposal.looks_governmental:
                withheld[proposal.domain] = (
                    "governmental, but not under this destination's own government, so it "
                    "describes another country's rules"
                )
            elif proposal.belongs_to_destination:
                # Not "not a government domain": nothing here establishes that, and for 19 of 51
                # countries measured this is where the real immigration authority lands. The honest
                # statement is about the limit of the rule rather than about the domain.
                withheld[proposal.domain] = (
                    f"under {destination}'s own top-level domain, but its hostname carries no "
                    "marker this rule recognises as governmental, so it could not be confirmed as "
                    "an authority. It may be a real one: some governments use no such marker, and "
                    "for those the domain has to be named in reviewed data instead"
                )
            else:
                withheld[proposal.domain] = (
                    "neither governmental nor under this destination's own top-level domain"
                )
        elif len(accepted) < maximum_trusted:
            accepted.append(proposal.domain)
        else:
            # This one is the destination's own government. Saying so is the point: whoever reads
            # this must not be told it belongs to another country, which is a different problem
            # with a different fix.
            withheld[proposal.domain] = (
                "this destination's own government, but not among the "
                f"{maximum_trusted} best-evidenced visa authorities found, so it was not read"
            )
    return accepted, withheld


def unconfirmable_authorities(report: BootstrapReport) -> list[str]:
    """Domains under the destination's own top-level domain that carry no governmental marker.

    These are the candidates the trust rule can neither accept nor honestly dismiss, and naming them
    is what turns *"no domain belonging to Germany's own government could be identified"* — which is
    false, and the wrong place to go looking — into a description of the actual gap. Measured
    2026-08-18: 19 of 51 countries have their real immigration or foreign ministry here, because no
    `gov.de`, `gov.nl` or `gov.se` convention exists for one to be found under.

    Deliberately **not** a route to trusting any of them. The rule refuses "looks like an
    authority", and this only reports what it refused. See DECISIONS entry 33.
    """

    return sorted(
        proposal.domain
        for proposal in report.proposals
        if proposal.belongs_to_destination and not proposal.looks_governmental
    )


class DiscoveredDestination(StrictModel):
    """A destination assembled entirely by machine, and the corridor that produced it."""

    config: DestinationConfig
    resolved: ResolvedCorridor
    trusted_domains: list[str]
    withheld_domains: dict[str, str]
    from_cache: bool = False


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AutomaticDestinationService:
    """Turn a country name and a corridor into a destination the plan pipeline can use."""

    def __init__(
        self,
        provider: SearchProvider,
        build_resolver: Callable[[], CorridorResolver],
        store: FileCorridorStore,
        *,
        countries: CountryRegistry | None = None,
        denylist: Denylist | None = None,
        authorities: AuthorityRegistry | None = None,
        maximum_age_hours: float = 24.0 * 21,
        now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self.provider = provider
        # A factory, not an instance: a resolver holds per-run state (render budgets, crawl
        # failures), so reusing one across requests would leak one corridor's limits into the next.
        self.build_resolver = build_resolver
        self.store = store
        self.countries = countries or get_country_registry()
        self.denylist = denylist or get_denylist()
        # Read once at construction. Which domains belong to a government is not a per-request
        # question, and making it one is exactly what entry 34 moved out of this path.
        self.authorities = authorities or get_authority_registry()
        self.maximum_age_hours = maximum_age_hours
        self.now = now

    def country_named(self, name: str) -> Country | None:
        """Find a country however it was referred to: by name, synonym, or destination slug.

        The interface sends a slug, the registry stores display names, and a person may type
        either. All three have to land on the same country or a destination becomes unresearchable
        purely because of how it was spelled.
        """

        wanted = name.strip().lower()
        by_slug = self.countries.by_slug(wanted)
        if by_slug is not None:
            return by_slug
        return next(
            (
                country
                for country in self.countries.countries
                if country.name.lower() == wanted
                or wanted in {synonym.lower() for synonym in country.synonyms}
            ),
            None,
        )

    async def destination_for(self, name: str, corridor: Corridor) -> DiscoveredDestination:
        """Resolve a destination from nothing, or refuse with a reason a traveller can read."""

        country = self.country_named(name)
        if country is None:
            raise AutomaticDiscoveryError(
                f"{name} is not a country this agent knows how to research. Its own government "
                "domains cannot be told apart from other countries' pages about it."
            )

        cached = self.store.load(corridor)
        if cached is not None and cached.age_hours(self.now()) < self.maximum_age_hours:
            base = self._base_config(country, corridor, cached.trusted_domains)
            return DiscoveredDestination(
                config=cached.resolved.to_destination_config(base),
                resolved=cached.resolved,
                trusted_domains=cached.trusted_domains,
                withheld_domains=cached.withheld_domains,
                from_cache=True,
            )

        entry = self.authorities.get(country.code)
        if entry is None:
            # Not a refusal about the country — a refusal about this deployment. Searching for the
            # domains here instead would reintroduce the per-request variance entry 34 removed, and
            # would do it silently, on exactly the countries nobody had reviewed.
            raise AutomaticDiscoveryError(
                f"{country.name} is not in the reviewed authority registry, so there is no "
                "confirmed government domain to research it from. Nothing was fetched. Regenerate "
                "the registry with `visa-discover registry` and review the entry."
            )

        trusted = list(entry.trusted)
        withheld = {
            domain: (
                f"under {country.name}'s own top-level domain, but its hostname carries no marker "
                "this rule recognises as governmental, so it could not be confirmed as an "
                "authority. It may be a real one: some governments use no such marker, and for "
                "those the domain has to be named in reviewed data instead"
            )
            for domain in entry.unconfirmable
        }
        if not trusted:
            # Name the candidates the rule could not confirm. Without this the message says no
            # government domain was *identified*, which for Germany or Italy is simply untrue and
            # sends whoever reads it to look at search or ranking rather than at the trust rule.
            detail = ""
            if entry.unconfirmable:
                detail = (
                    f" Candidates under {country.name}'s own top-level domain were found — "
                    f"{', '.join(entry.unconfirmable)} — but none of their hostnames carries a "
                    "marker this agent recognises as governmental, so none could be confirmed as "
                    "an authority. Some governments use no such marker; for those the domain has "
                    "to be named in reviewed data."
                )
            raise AutomaticDiscoveryError(
                f"No domain belonging to {country.name}'s own government could be confirmed, so "
                f"there was nothing safe to read. Nothing was fetched.{detail}"
            )

        base = self._base_config(country, corridor, trusted)
        resolved = await self.build_resolver().resolve(base, corridor)
        if not resolved.is_usable:
            missing = ", ".join(role.replace("_", " ") for role in resolved.unresolved_roles)
            raise AutomaticDiscoveryError(
                f"{country.name}'s official sources were searched, but no page could be confirmed "
                f"as the {missing}. Nothing was substituted in its place."
            )

        self.store.store(corridor, resolved, trusted, withheld, self.now())
        return DiscoveredDestination(
            config=resolved.to_destination_config(base),
            resolved=resolved,
            trusted_domains=trusted,
            withheld_domains=withheld,
        )

    def _base_config(
        self, country: Country, corridor: Corridor, trusted: list[str]
    ) -> DestinationConfig:
        return DestinationConfig(
            slug=corridor.destination_slug,
            display_name=country.name,
            route_type="national",
            implementation_status="available",
            trusted_domains=trusted,
        )
