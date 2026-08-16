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


def is_own_government(proposal: DomainProposal) -> bool:
    """The rule that replaces the human approval gate.

    Both halves are load-bearing. `looks_governmental` alone admits any country's government —
    the US embassy's page about Vietnam. `belongs_to_destination` alone admits any site under the
    country's TLD, including its commercial ones.
    """

    return proposal.looks_governmental and proposal.belongs_to_destination


def auto_trusted_domains(report: BootstrapReport) -> tuple[list[str], dict[str, str]]:
    """Split a bootstrap into what may be trusted without a person, and what may not.

    The withheld list is returned rather than dropped: a corridor that then resolves nothing should
    be able to say which plausible-looking domains it declined to trust, and why.
    """

    accepted: list[str] = []
    withheld: dict[str, str] = {}

    for proposal in report.proposals:
        if is_own_government(proposal):
            accepted.append(proposal.domain)
        elif proposal.looks_governmental:
            withheld[proposal.domain] = (
                "governmental, but not under this destination's own government, so it describes "
                "another country's rules"
            )
        else:
            withheld[proposal.domain] = "not a government domain for this destination"
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
        wanted = name.strip().lower()
        return next(
            (
                country
                for country in self.countries.countries
                if country.name.lower() == wanted or wanted in {s.lower() for s in country.synonyms}
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
