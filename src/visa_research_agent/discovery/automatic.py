"""Resolving a destination nobody configured, without a person in the loop.

Until now a human approved every domain before anything was fetched. That gate is removed here,
and what replaces it is **not** trust in search — it is the rule the human was actually applying.
Reviewing six bootstraps, every accept and every reject reduced to one question: *is this domain
the destination country's own government?* Those are the two properties `bootstrap.py` already
computes, and the rule reproduces all 22 recorded human decisions with no disagreements.

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

from visa_research_agent.discovery.bootstrap import (
    BootstrapReport,
    DomainProposal,
    bootstrap_destination,
)
from visa_research_agent.discovery.corridor_store import FileCorridorStore
from visa_research_agent.discovery.lexicon import (
    Country,
    CountryRegistry,
    Denylist,
    get_country_registry,
    get_denylist,
)
from visa_research_agent.discovery.models import Corridor, ResolvedCorridor
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
    """

    accepted: list[str] = []
    withheld: dict[str, str] = dict(report.rejected)

    for proposal in sorted(report.proposals, key=_trust_priority):
        if not proposal.is_own_government:
            if proposal.looks_governmental:
                withheld[proposal.domain] = (
                    "governmental, but not under this destination's own government, so it "
                    "describes another country's rules"
                )
            else:
                withheld[proposal.domain] = "not a government domain for this destination"
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

        report = await bootstrap_destination(
            country.name, self.provider, self.denylist, destination_tlds=country.tlds
        )
        trusted, withheld = auto_trusted_domains(report)
        if not trusted:
            raise AutomaticDiscoveryError(
                f"No domain belonging to {country.name}'s own government could be identified, so "
                "there was nothing safe to read. Nothing was fetched."
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
