"""Domain trust: which hosts count as official, enforced when configuration loads."""

import pytest
from pydantic import AnyHttpUrl, ValidationError

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.domain.models import (
    AppointedProvider,
    ConfiguredSource,
    DestinationConfig,
)
from visa_research_agent.domain.trust import host_is_within, host_of, is_bare_public_suffix


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
