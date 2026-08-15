"""Discovery's data layer: corridors, URL rules, and the vocabulary loaded from config."""

from datetime import UTC, datetime

import pytest
from pydantic import AnyHttpUrl, ValidationError

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.discovery.lexicon import (
    get_country_registry,
    get_denylist,
    get_lexicon,
)
from visa_research_agent.discovery.models import (
    Corridor,
    ResolvedCorridor,
    ResolvedSource,
)
from visa_research_agent.discovery.urls import (
    canonicalise_url,
    is_crawlable,
    is_pdf_url,
    path_segments,
)
from visa_research_agent.domain.models import DestinationConfig

RESOLVED_AT = datetime(2026, 8, 15, 9, 0, tzinfo=UTC)


def japan() -> DestinationConfig:
    destination = load_destination_registry().get("japan")
    assert destination is not None
    return destination


def corridor() -> Corridor:
    return Corridor(
        destination_slug="japan",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def source(source_id: str, url: str, role: str) -> ResolvedSource:
    return ResolvedSource.model_validate(
        {
            "source_id": source_id,
            "title": "A page",
            "url": url,
            "authority": "An authority",
            "kind": "foreign_ministry",
            "roles": [role],
            "score": 90.0,
        }
    )


def test_a_corridor_has_a_stable_cache_key() -> None:
    assert corridor().key == "japan/IN/GB/tourism"


def test_case_tracking_and_parameter_order_do_not_split_one_page_into_many() -> None:
    variants = [
        "https://WWW.MOFA.GO.JP/visa/?utm_source=x&b=2&a=1",
        "https://www.mofa.go.jp/visa?a=1&b=2",
        "https://www.mofa.go.jp/visa/?b=2&a=1&fbclid=y",
    ]

    assert len({canonicalise_url(variant) for variant in variants}) == 1


def test_fragments_are_dropped_but_real_query_strings_are_kept() -> None:
    assert canonicalise_url("https://www.mofa.go.jp/visa/#section") == "https://www.mofa.go.jp/visa"
    # A query string can select a different page, so it must survive.
    assert canonicalise_url("https://www.mofa.go.jp/visa?id=7") != canonicalise_url(
        "https://www.mofa.go.jp/visa"
    )


def test_pdf_urls_are_recognised_and_are_not_skipped() -> None:
    pdf = "https://www.uk.emb-japan.go.jp/files/100355579.pdf"

    assert is_pdf_url(pdf)
    # Authorities publish checklists as PDFs, so a PDF must remain fetchable.
    assert is_crawlable(pdf, japan())


def test_path_segments_are_whole_segments() -> None:
    segments = path_segments("https://www.ica.gov.sg/enter/visa_requirements/india?x=1")

    assert segments == ["enter", "visa_requirements", "india"]


def test_a_url_off_the_approved_domains_is_never_crawlable() -> None:
    assert not is_crawlable("https://cheap-visas.example/japan", japan())
    # A lookalike host must fail too, on the dot boundary.
    assert not is_crawlable("https://notmofa.go.jp/visa", japan())
    assert is_crawlable("https://www.mofa.go.jp/visa", japan())


def test_site_furniture_and_binaries_are_skipped() -> None:
    for path in ("/search/results", "/privacy", "/en/login", "/assets/logo.png", "/style.css"):
        assert not is_crawlable(f"https://www.mofa.go.jp{path}", japan()), path


def test_the_committed_vocabulary_loads_and_covers_the_roles_we_rely_on() -> None:
    lexicon = get_lexicon()

    for role in ("visa_decision", "document_checklist", "application_route"):
        assert lexicon.roles[role].terms, role
    assert "tourism" in lexicon.purposes


def test_a_travellers_own_purpose_is_not_penalised_as_off_scope() -> None:
    lexicon = get_lexicon()

    # "study" is off-scope for a tourist, but must not be for a student.
    assert "student" in lexicon.off_scope_terms_for("tourism")
    assert "student" not in lexicon.off_scope_terms_for("study")


def test_the_denylist_blocks_agencies_and_their_subdomains() -> None:
    denylist = get_denylist()

    assert denylist.blocks("ivisa.com")
    assert denylist.blocks("uk.ivisa.com")
    assert denylist.blocks("en.wikipedia.org")
    assert not denylist.blocks("mofa.go.jp")


def test_countries_carry_the_host_labels_that_iso_codes_do_not() -> None:
    registry = get_country_registry()

    united_kingdom = registry.require("GB")
    # The mission subdomain is uk., not gb. — that mismatch has to be data.
    assert "uk" in united_kingdom.host_labels
    assert "indian" in registry.require("IN").text_tokens


def test_an_unknown_country_is_refused_rather_than_guessed() -> None:
    with pytest.raises(ValueError, match="not in countries.yaml"):
        get_country_registry().require("ZZ")


def test_a_corridor_is_usable_only_with_both_load_bearing_roles() -> None:
    decision = source("jp_a", "https://www.mofa.go.jp/a", "visa_decision")
    checklist = source("jp_b", "https://www.uk.emb-japan.go.jp/b", "document_checklist")

    assert not ResolvedCorridor(
        corridor=corridor(), resolved_at=RESOLVED_AT, sources=[decision]
    ).is_usable
    assert ResolvedCorridor(
        corridor=corridor(), resolved_at=RESOLVED_AT, sources=[decision, checklist]
    ).is_usable


def test_a_resolved_corridor_becomes_a_destination_with_the_roles_mapped() -> None:
    resolved = ResolvedCorridor(
        corridor=corridor(),
        resolved_at=RESOLVED_AT,
        sources=[
            source("jp_decision", "https://www.mofa.go.jp/novisa", "visa_decision"),
            source(
                "jp_checklist",
                "https://www.uk.emb-japan.go.jp/sightseeing",
                "document_checklist",
            ),
            source("jp_fees", "https://www.uk.emb-japan.go.jp/fees", "fees"),
        ],
    )

    config = resolved.to_destination_config(japan())

    assert config.application_document_source_ids == ["jp_checklist"]
    assert config.load_bearing_source_ids == ["jp_checklist", "jp_decision"]
    assert len(config.sources) == 3


def test_a_corridor_whose_url_left_the_approved_domains_cannot_become_a_destination() -> None:
    """The safety property: machine-chosen pages are re-checked against human-approved trust."""

    tampered = ResolvedCorridor(
        corridor=corridor(),
        resolved_at=RESOLVED_AT,
        sources=[
            source("jp_decision", "https://www.mofa.go.jp/novisa", "visa_decision"),
            source("jp_bad", "https://cheap-visas.example/japan", "document_checklist"),
        ],
    )

    with pytest.raises(ValidationError, match="not on a trusted domain"):
        tampered.to_destination_config(japan())


def test_a_corridor_cannot_list_the_same_source_twice() -> None:
    with pytest.raises(ValidationError, match="same source twice"):
        ResolvedCorridor(
            corridor=corridor(),
            resolved_at=RESOLVED_AT,
            sources=[
                source("jp_a", "https://www.mofa.go.jp/a", "visa_decision"),
                source("jp_a", "https://www.mofa.go.jp/b", "document_checklist"),
            ],
        )


def test_resolved_at_must_be_timezone_aware() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        ResolvedCorridor(corridor=corridor(), resolved_at=datetime(2026, 8, 15, 9, 0))


def test_a_source_converts_to_the_registry_shape_without_discovery_fields() -> None:
    configured = source("jp_a", "https://www.mofa.go.jp/a", "visa_decision").to_configured_source()

    assert configured.source_id == "jp_a"
    assert configured.url == AnyHttpUrl("https://www.mofa.go.jp/a")
    assert configured.research_pass == "primary"
