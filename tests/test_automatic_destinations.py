"""Resolving a destination nobody configured, with no human approving a domain.

No test here reaches the network or a model. The search provider and the resolver are both
injected, exactly as elsewhere.

The load-bearing assertions are about what the machine refuses to trust. Removing the human gate
only stays safe because the rule that replaces it is the one the human was applying: a domain is
used only when it is the destination country's **own** government. France's real bootstrap
surfaced a commercial travel insurer, and Vietnam's ranked the US embassy first.
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from visa_research_agent.discovery.automatic import (
    MAXIMUM_AUTO_TRUSTED_DOMAINS,
    AutomaticDestinationService,
    AutomaticDiscoveryError,
    auto_trusted_domains,
    is_own_government,
)
from visa_research_agent.discovery.bootstrap import (
    BootstrapReport,
    DomainProposal,
    suggest_kind,
)
from visa_research_agent.discovery.corridor_store import FileCorridorStore
from visa_research_agent.discovery.models import (
    Corridor,
    ResolvedCorridor,
    ResolvedSource,
    SearchResult,
)

pytestmark = pytest.mark.anyio

NOW = datetime(2026, 8, 16, 9, 0, tzinfo=UTC)


def proposal(domain: str, *, governmental: bool, own: bool) -> DomainProposal:
    return DomainProposal(
        domain=domain,
        looks_governmental=governmental,
        belongs_to_destination=own,
        queries=["q1", "q2"],
    )


def corridor(slug: str = "france") -> Corridor:
    return Corridor(
        destination_slug=slug,
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def resolved(slug: str = "france") -> ResolvedCorridor:
    return ResolvedCorridor(
        corridor=corridor(slug),
        resolved_at=NOW,
        sources=[
            ResolvedSource(
                source_id="fr_visa_decision",
                title="Applying for a visa",
                url="https://france-visas.gouv.fr/en/applying",  # type: ignore[arg-type]
                authority="France Visas",
                kind="foreign_ministry",
                roles=["visa_decision", "document_checklist"],
                score=60.0,
                decided_by="model",
            )
        ],
    )


class StubProvider:
    """Returns one fixed set of results, whatever is asked."""

    def __init__(self, urls: list[str]) -> None:
        self.urls = urls
        self.queries: list[str] = []

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        self.queries.append(query)
        return [
            SearchResult(url=url, title="", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls)
        ]


class StubResolver:
    """Stands in for the corridor resolver, recording the config it was handed."""

    def __init__(self, outcome: ResolvedCorridor) -> None:
        self.outcome = outcome
        self.trusted_seen: list[list[str]] = []

    async def resolve(self, destination: object, traveller: Corridor) -> ResolvedCorridor:
        self.trusted_seen.append(list(getattr(destination, "trusted_domains", [])))
        return self.outcome


def build_service(
    tmp_path: Path,
    provider: StubProvider,
    resolver: StubResolver,
    *,
    now: datetime = NOW,
) -> AutomaticDestinationService:
    return AutomaticDestinationService(
        provider,
        lambda: resolver,  # type: ignore[arg-type,return-value]
        FileCorridorStore(tmp_path / "corridors"),
        now=lambda: now,
    )


# --- the rule that replaces the human gate ---------------------------------------------------


def test_only_the_destinations_own_government_is_trusted() -> None:
    assert is_own_government(proposal("diplomatie.gouv.fr", governmental=True, own=True))
    # A real government, describing its own citizens' rules rather than this destination's.
    assert not is_own_government(proposal("usembassy.gov", governmental=True, own=False))
    # Under the country's TLD, but a commercial insurer. France's real bootstrap surfaced this.
    assert not is_own_government(proposal("axa-schengen.com", governmental=False, own=False))
    # An appointed provider cannot pass domain trust by design.
    assert not is_own_government(proposal("vfsglobal.com", governmental=False, own=False))


def test_what_is_withheld_is_reported_with_a_reason() -> None:
    report = BootstrapReport(
        destination_name="France",
        proposals=[
            proposal("diplomatie.gouv.fr", governmental=True, own=True),
            proposal("europa.eu", governmental=True, own=False),
            proposal("axa-schengen.com", governmental=False, own=False),
        ],
    )

    accepted, withheld = auto_trusted_domains(report)

    assert accepted == ["diplomatie.gouv.fr"]
    assert "another country's rules" in withheld["europa.eu"]
    assert "not a government domain" in withheld["axa-schengen.com"]


def test_what_bootstrap_rejected_outright_is_reported_too() -> None:
    """Everything declined leaves one trace in one place.

    A domain dropped for too little corroboration was previously visible only in the bootstrap
    report, which the request path never prints, so a corridor could not say it had seen it.
    """

    report = BootstrapReport(
        destination_name="Wonderland",
        proposals=[proposal("mfa.gov.wl", governmental=True, own=True)],
        rejected={"agency.example": "on the denylist of agencies and non-authoritative sites"},
    )

    accepted, withheld = auto_trusted_domains(report)

    assert accepted == ["mfa.gov.wl"]
    assert "denylist" in withheld["agency.example"]


# --- how many of its own government's domains one bootstrap may put into use ------------------


def own_government(domain: str, *, corroboration: int = 1) -> DomainProposal:
    return DomainProposal(
        domain=domain,
        looks_governmental=True,
        belongs_to_destination=True,
        matched_tlds=["gov"],
        suggested_kind=suggest_kind(domain),
        queries=[f"q{index}" for index in range(corroboration)],
    )


def test_only_the_best_evidenced_own_government_domains_are_put_to_use() -> None:
    """A government large enough to have many domains passes the rule with all of them.

    Every domain here is genuinely this destination's own government, so nothing is being called
    unofficial. They are competing for a crawl budget and ten fetch places, and an authority whose
    hostname says it serves travellers should not lose them to one that says nothing.
    """

    report = BootstrapReport(
        destination_name="Wonderland",
        proposals=[
            own_government("statedept.gov", corroboration=4),
            own_government("portal.gov", corroboration=4),
            own_government("homeland.gov", corroboration=3),
            own_government("wlembassy.gov", corroboration=2),
            own_government("interior.gov"),
            own_government("registry.gov"),
            own_government("enforcement.gov"),
            own_government("services.gov"),
        ],
    )

    accepted, withheld = auto_trusted_domains(report)

    assert len(accepted) == MAXIMUM_AUTO_TRUSTED_DOMAINS
    # The mission network is the one page in this list that serves a traveller abroad, and it is
    # the least corroborated of the four that matter. Its hostname is what keeps it in.
    assert accepted[0] == "wlembassy.gov"
    assert set(accepted) >= {"wlembassy.gov", "statedept.gov", "portal.gov", "homeland.gov"}
    assert set(withheld) and set(withheld).isdisjoint(accepted)


def test_a_domain_left_out_is_not_described_as_another_countrys() -> None:
    """The reason has to be true. These are this destination's own government, and saying otherwise
    would send whoever reads `withheld_domains` after a different problem entirely."""

    report = BootstrapReport(
        destination_name="Wonderland",
        proposals=[own_government(f"agency{index}.gov", corroboration=2) for index in range(7)],
    )

    _, withheld = auto_trusted_domains(report)

    reasons = " ".join(withheld.values())
    assert "another country" not in reasons
    assert "not a government domain" not in reasons
    assert "own government" in reasons


def test_the_cap_does_not_reach_an_ordinary_corridor() -> None:
    """Brazil put one domain to use, France two, China four. None of them changes."""

    report = BootstrapReport(
        destination_name="China",
        proposals=[
            proposal("china-embassy.gov.cn", governmental=True, own=True),
            proposal("china-consulate.gov.cn", governmental=True, own=True),
            proposal("mfa.gov.cn", governmental=True, own=True),
            proposal("nia.gov.cn", governmental=True, own=True),
        ],
    )

    accepted, withheld = auto_trusted_domains(report)

    assert len(accepted) == 4
    assert withheld == {}


def test_which_domains_are_used_does_not_depend_on_the_order_search_returned_them() -> None:
    """The failure this fixes was a coin flip, so the same evidence must give the same set."""

    proposals = [
        own_government("statedept.gov", corroboration=4),
        own_government("portal.gov", corroboration=4),
        own_government("homeland.gov", corroboration=3),
        own_government("wlembassy.gov", corroboration=2),
        own_government("interior.gov"),
        own_government("registry.gov"),
    ]

    forwards, _ = auto_trusted_domains(
        BootstrapReport(destination_name="Wonderland", proposals=list(proposals))
    )
    backwards, _ = auto_trusted_domains(
        BootstrapReport(destination_name="Wonderland", proposals=list(reversed(proposals)))
    )

    assert forwards == backwards


# --- resolving a destination from nothing ----------------------------------------------------


async def test_a_destination_nobody_configured_is_researched(tmp_path: Path) -> None:
    provider = StubProvider(["https://france-visas.gouv.fr/en/applying"])
    resolver = StubResolver(resolved())

    discovered = await build_service(tmp_path, provider, resolver).destination_for(
        "France", corridor()
    )

    assert discovered.trusted_domains == ["france-visas.gouv.fr"]
    assert [str(source.url) for source in discovered.config.sources] == [
        "https://france-visas.gouv.fr/en/applying"
    ]
    # The config must be usable by the ordinary pipeline, with its trust rules re-run.
    assert discovered.config.application_document_source_ids == ["fr_visa_decision"]


async def test_nothing_is_fetched_when_no_own_government_domain_is_found(
    tmp_path: Path,
) -> None:
    """The refusal that keeps the gate's removal honest.

    Search returned only a commercial agency and another country's government. There is nothing
    safe to read, so nothing is read — rather than falling back to the best available.
    """

    provider = StubProvider(["https://axa-schengen.com/visa", "https://travel.state.gov/france"])
    resolver = StubResolver(resolved())

    with pytest.raises(AutomaticDiscoveryError, match="own government"):
        await build_service(tmp_path, provider, resolver).destination_for("France", corridor())

    assert resolver.trusted_seen == [], "nothing may be crawled without an approved domain"


async def test_an_unknown_country_is_refused_rather_than_searched(tmp_path: Path) -> None:
    provider = StubProvider(["https://example.gov.zz/visa"])
    resolver = StubResolver(resolved())

    with pytest.raises(AutomaticDiscoveryError, match="not a country"):
        await build_service(tmp_path, provider, resolver).destination_for(
            "Atlantis", corridor("atlantis")
        )

    assert provider.queries == [], "an unknown country must not even be searched"


async def test_a_corridor_missing_a_load_bearing_role_is_refused(tmp_path: Path) -> None:
    provider = StubProvider(["https://france-visas.gouv.fr/en/applying"])
    empty = ResolvedCorridor(
        corridor=corridor(), resolved_at=NOW, sources=[], unresolved_roles=["visa_decision"]
    )

    with pytest.raises(AutomaticDiscoveryError, match="visa decision"):
        await build_service(tmp_path, provider, StubResolver(empty)).destination_for(
            "France", corridor()
        )


async def test_only_approved_domains_reach_the_resolver(tmp_path: Path) -> None:
    provider = StubProvider(
        [
            "https://france-visas.gouv.fr/en/applying",
            "https://axa-schengen.com/visa",
            "https://travel.state.gov/france",
        ]
    )
    resolver = StubResolver(resolved())

    await build_service(tmp_path, provider, resolver).destination_for("France", corridor())

    assert resolver.trusted_seen == [["france-visas.gouv.fr"]]


# --- caching ---------------------------------------------------------------------------------


async def test_a_second_request_reuses_the_stored_corridor(tmp_path: Path) -> None:
    provider = StubProvider(["https://france-visas.gouv.fr/en/applying"])
    resolver = StubResolver(resolved())
    service = build_service(tmp_path, provider, resolver)

    await service.destination_for("France", corridor())
    again = await service.destination_for("France", corridor())

    assert again.from_cache
    assert len(resolver.trusted_seen) == 1, "a cached corridor must not be re-crawled"


async def test_a_corridor_past_its_age_is_resolved_again(tmp_path: Path) -> None:
    provider = StubProvider(["https://france-visas.gouv.fr/en/applying"])
    resolver = StubResolver(resolved())

    await build_service(tmp_path, provider, resolver).destination_for("France", corridor())
    later = build_service(tmp_path, provider, resolver, now=NOW + timedelta(days=30))
    again = await later.destination_for("France", corridor())

    assert not again.from_cache
    assert len(resolver.trusted_seen) == 2


async def test_a_stored_corridor_is_keyed_by_the_whole_corridor(tmp_path: Path) -> None:
    """Nationality and purpose change the answer, so they must change the key."""

    provider = StubProvider(["https://france-visas.gouv.fr/en/applying"])
    resolver = StubResolver(resolved())
    service = build_service(tmp_path, provider, resolver)

    await service.destination_for("France", corridor())
    other = corridor().model_copy(update={"passport_nationality": "CN"})
    await service.destination_for("France", other)

    assert len(resolver.trusted_seen) == 2
