"""Domain trust: which hosts count as official, enforced when configuration loads."""

import pytest
from pydantic import AnyHttpUrl, ValidationError

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.discovery.bootstrap import GOVERNMENT_NAMESPACE_LABELS
from visa_research_agent.domain.models import (
    AppointedProvider,
    ConfiguredSource,
    DestinationConfig,
    UnreadableAuthority,
)
from visa_research_agent.domain.trust import (
    SUFFIX_MARKER_LABELS,
    host_is_within,
    host_of,
    is_bare_public_suffix,
    registrable_domain,
)


def source(source_id: str, url: str, kind: str = "immigration_authority") -> ConfiguredSource:
    return ConfiguredSource.model_validate(
        {
            "source_id": source_id,
            "title": "A page",
            "url": url,
            "authority": "An authority",
            "kind": kind,
        }
    )


def build(**overrides: object) -> DestinationConfig:
    base: dict[str, object] = {
        "slug": "testland",
        "display_name": "Testland",
        "route_type": "national",
        "application_document_source_ids": ["tl_docs"],
        "trusted_domains": ["immigration.gov.example"],
        "sources": [source("tl_docs", "https://immigration.gov.example/visa")],
    }
    base.update(overrides)
    return DestinationConfig.model_validate(base)


def test_host_of_extracts_the_lowercase_hostname() -> None:
    assert host_of("https://WWW.ICA.GOV.SG/visa?a=1") == "www.ica.gov.sg"
    assert host_of("not a url") == ""


def test_subdomains_match_but_lookalikes_do_not() -> None:
    trusted = ["mfa.gov.sg"]

    assert host_is_within("mfa.gov.sg", trusted)
    assert host_is_within("london.mfa.gov.sg", trusted)
    # The dot boundary is what stops a lookalike domain from passing.
    assert not host_is_within("notmfa.gov.sg", trusted)
    assert not host_is_within("mfa.gov.sg.evil.example", trusted)


def test_bare_public_suffixes_are_recognised() -> None:
    for suffix in ("gov.sg", "gov.uk", "go.jp", "gouv.fr", "co.uk", "com", "gov"):
        assert is_bare_public_suffix(suffix), suffix
    for registrable in ("ica.gov.sg", "mfa.gov.sg", "service.gov.uk", "usa.gov"):
        assert not is_bare_public_suffix(registrable), registrable


def test_a_bare_public_suffix_cannot_be_trusted() -> None:
    with pytest.raises(ValidationError, match="public suffix"):
        build(
            trusted_domains=["gov.example", "gov.sg"],
            sources=[source("tl_docs", "https://anything.gov.sg/visa")],
        )


def test_a_source_outside_the_trusted_domains_is_rejected() -> None:
    with pytest.raises(ValidationError, match="not on a trusted domain"):
        build(sources=[source("tl_docs", "https://visa-tips-blog.example/singapore")])


def test_a_destination_with_sources_must_declare_its_trusted_domains() -> None:
    with pytest.raises(ValidationError, match="must declare its trusted domains"):
        build(trusted_domains=[])


def test_a_planned_destination_without_sources_needs_no_trusted_domains() -> None:
    planned = DestinationConfig(slug="later", display_name="Later", route_type="national")

    assert planned.sources == []
    assert planned.trusted_domains == []


def test_an_appointed_provider_is_trusted_only_via_a_named_official_source() -> None:
    config = build(
        appointed_providers=[AppointedProvider(domain="provider.example", appointed_by="tl_docs")],
        sources=[
            source("tl_docs", "https://immigration.gov.example/visa"),
            source("tl_apply", "https://provider.example/apply", "official_application_provider"),
        ],
    )

    # The provider is not a government domain, so it passes only through its appointment.
    assert config.trusts_host("provider.example")
    assert not host_is_within("provider.example", config.trusted_domains)


def test_an_appointed_provider_must_name_a_real_appointing_source() -> None:
    with pytest.raises(ValidationError, match="unknown appointing source"):
        build(
            appointed_providers=[
                AppointedProvider(domain="provider.example", appointed_by="nonexistent")
            ]
        )


def test_load_bearing_sources_default_to_the_document_checklist() -> None:
    assert build().load_bearing_source_ids == ["tl_docs"]


def test_declared_required_sources_add_to_the_checklist_rather_than_replacing_it() -> None:
    """Naming a required source must not quietly drop the document checklist.

    This was a fallback (`required_source_ids or application_document_source_ids`), so declaring
    any required source discarded the checklist requirement entirely — a destination could list a
    checklist and still produce a plan without it.
    """

    config = build(
        required_source_ids=["tl_decision"],
        application_document_source_ids=["tl_docs"],
        sources=[
            source("tl_docs", "https://immigration.gov.example/visa"),
            source("tl_decision", "https://immigration.gov.example/need-a-visa"),
        ],
    )

    assert config.load_bearing_source_ids == ["tl_docs", "tl_decision"]


def test_required_sources_must_exist() -> None:
    with pytest.raises(ValidationError, match="required sources contain unknown IDs"):
        build(required_source_ids=["nonexistent"])


def test_the_committed_singapore_configuration_satisfies_its_own_trust_rules() -> None:
    singapore = load_destination_registry().get("singapore")
    assert singapore is not None

    # Loading already enforces this, but state it explicitly: every hand-picked URL is trusted.
    for configured in singapore.sources:
        assert singapore.trusts_host(host_of(str(configured.url))), configured.source_id
    assert singapore.load_bearing_source_ids == [
        "sg_ica_india_visa_details",
        "sg_ica_visa_requirement_overview",
    ]
    assert not singapore.trusts_host("visa-advice-blog.example")
    assert not singapore.trusts_host(host_of(str(AnyHttpUrl("https://ica.gov.sg.evil.example/x"))))


def test_a_page_offered_as_guidance_must_still_be_on_an_approved_domain() -> None:
    """An unreadable authority is shown to a traveller as this destination's own guidance, so it
    is held to the same rule as evidence — and it is the case that needs the rule most, because
    nobody read the page, so the domain is the only thing vouching for it."""

    with pytest.raises(ValidationError, match="not on an approved domain"):
        DestinationConfig(
            slug="france",
            display_name="France",
            route_type="national",
            implementation_status="available",
            trusted_domains=["diplomatie.gouv.fr"],
            decision_is_unverified=True,
            unreadable_authorities=[
                UnreadableAuthority(
                    url="https://visa-agency.example/france",  # type: ignore[arg-type]
                    authority="Not France",
                    detail="refused automated retrieval",
                )
            ],
        )


def test_every_government_namespace_is_also_too_broad_to_trust_whole() -> None:
    """The containment between two hand-maintained lists that answer different questions.

    `GOVERNMENT_NAMESPACE_LABELS` asks "is this a government namespace?"; `SUFFIX_MARKER_LABELS`
    asks "is it too broad to trust whole?". A label in the first and missing from the second is a
    hole rather than an omission, and it is invisible from either file on its own.

    Found by adding `gv` on 2026-08-25. `registrable_domain("bmeia.gv.at")` returned **`gv.at`**,
    so trusting Austria's foreign ministry would have trusted every Austrian public body under the
    same namespace — the thing refusing `gov.br` whole exists to prevent, reintroduced through the
    other list. Neither file's own tests could see it.
    """

    missing = set(GOVERNMENT_NAMESPACE_LABELS) - SUFFIX_MARKER_LABELS
    assert not missing, (
        f"{sorted(missing)} name a government namespace but are not treated as a public suffix, so "
        "a domain inside one reduces to the namespace and trusting an authority trusts everything "
        "beneath it — add them to SUFFIX_MARKER_LABELS"
    )


def test_an_authority_inside_a_government_namespace_keeps_its_own_identity() -> None:
    """The behaviour the containment above buys, checked rather than inferred from the lists."""

    for authority, namespace in (
        ("bmeia.gv.at", "gv.at"),
        ("ica.gov.sg", "gov.sg"),
        ("mofa.go.jp", "go.jp"),
    ):
        assert registrable_domain(authority) == authority, (
            f"{authority} reduced past itself, so trusting it would trust all of {namespace}"
        )
        assert is_bare_public_suffix(namespace), namespace


def test_a_named_government_domain_is_trusted_with_everything_beneath_it() -> None:
    """The other shape, and why it is the safer one.

    `canada.ca` and `admin.ch` are single domains a government holds, not namespaces its bodies
    register under, so a subdomain can only exist if that government made it. Reducing to the domain
    is correct here and would be wrong for `gv.at`.
    """

    assert registrable_domain("ircc.canada.ca") == "canada.ca"
    assert not is_bare_public_suffix("canada.ca")
