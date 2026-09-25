"""A page about this trip's visa that a run could not read is named for the traveller, never read.

DECISIONS entry 219, the owner's decision. Home Affairs' "Visitor visa (subclass 600) Tourist
stream (apply outside Australia)" is chosen by every Australia run and its CDN refuses our browser,
so the traveller was never pointed at the page with the Apply button on it.
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from visa_research_agent.config.loader import load_destination_registry
from visa_research_agent.discovery.lexicon import get_lexicon
from visa_research_agent.discovery.models import (
    CandidatePage,
    Corridor,
    PageLink,
    ResolvedCorridor,
    RoleScores,
)
from visa_research_agent.discovery.resolver import (
    says_it_is_this_trips_visa_page,
    unread_visa_pages,
)
from visa_research_agent.domain.models import DestinationConfig, FailureOutcome, SourceFailure
from visa_research_agent.research.openai_extraction import download_label

TOURIST = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/tourist-stream-overseas"
BUSINESS = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/business-visitor-stream"
FEES = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/fees-and-charges/current-visa-pricing"

CORRIDOR = Corridor(
    destination_slug="australia", passport_nationality="IN", applying_from="IN", purpose="tourism"
)


def failure(url: str, outcome: FailureOutcome = "unusable") -> SourceFailure:
    return SourceFailure(
        source_id="australi_immi_page",
        title="Visitor visa (subclass 600)",
        authority="Australia authority (immi.homeaffairs.gov.au)",
        outcome=outcome,
        detail="the page returned too little readable text to trust",
        attempted_url=url,  # type: ignore[arg-type]
    )


def candidate(url: str, title: str, route_score: float = 51.2) -> CandidatePage:
    return CandidatePage(
        link=PageLink(url=url, text=title, depth=0),
        link_scores=RoleScores(scores={"application_route": route_score}),
        title=title,
    )


CANDIDATES = {
    TOURIST: candidate(TOURIST, "Visitor visa (subclass 600) Tourist stream (apply outside ..."),
    BUSINESS: candidate(BUSINESS, "Visitor Visa – Business Stream", 60.0),
    FEES: candidate(FEES, "Visa pricing table"),
}


@pytest.mark.parametrize(
    ("text", "named"),
    [
        ("Visitor visa (subclass 600) Tourist stream (apply outside Australia)", True),
        ("Visitor visa (Tourist stream)(subclass 600)", True),
        ("C-3-9 (Tourist visa)", True),
        # Another purpose, or an audience a tourist is not.
        ("Visitor Visa – Business Stream", False),
        ("Work and Holiday visa (subclass 462)", False),
        ("Working Holiday visa (subclass 417)", False),
        ("Student visa (subclass 500)", False),
        # Names no visa, or no purpose.
        ("Tourist information", False),
        ("Visa pricing table", False),
    ],
)
def test_only_a_page_whose_own_words_say_it_is_this_trips_visa_is_named(
    text: str, named: bool
) -> None:
    page = CandidatePage(
        link=PageLink(url=TOURIST, text=text, depth=0),
        link_scores=RoleScores(scores={"application_route": 20.0}),
    )

    assert says_it_is_this_trips_visa_page(page, CORRIDOR, get_lexicon()) is named


def test_the_tourist_stream_page_the_run_could_not_read_is_named() -> None:
    named = unread_visa_pages(
        [failure(FEES), failure(BUSINESS), failure(TOURIST)],
        CANDIDATES,
        read=[],
        already_named=[],
        corridor=CORRIDOR,
        lexicon=get_lexicon(),
    )

    assert [str(page.attempted_url) for page in named] == [TOURIST]
    assert named[0].detail == "the page returned too little readable text to trust"


@pytest.mark.parametrize(
    ("failures", "already_named"),
    [
        # Landed off the approved domains: not an address to send a traveller to.
        ([failure(TOURIST, "untrusted")], []),
        # Never a candidate at all.
        ([failure("https://immi.homeaffairs.gov.au/unknown")], []),
        # Already named, as a checklist.
        ([failure(TOURIST)], [TOURIST]),
    ],
)
def test_a_visa_page_is_named_only_once_and_only_for_a_reason_that_licenses_it(
    failures: list[SourceFailure], already_named: list[str]
) -> None:
    assert (
        unread_visa_pages(
            failures,
            CANDIDATES,
            read=[],
            already_named=already_named,
            corridor=CORRIDOR,
            lexicon=get_lexicon(),
        )
        == []
    )


def test_nothing_is_named_once_a_page_the_run_read_is_this_trips_visa_page() -> None:
    """Australia's first run with Home Affairs readable read its Tourist stream page and named two
    listing pages beside it as "possible pages for your visa"."""

    listing = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600"
    candidates = {**CANDIDATES, listing: candidate(listing, "Visitor visa (subclass 600)")}

    assert (
        unread_visa_pages(
            [failure(listing)],
            candidates,
            read=[TOURIST],
            already_named=[],
            corridor=CORRIDOR,
            lexicon=get_lexicon(),
        )
        == []
    )


def test_the_pages_reach_the_destination_a_plan_is_built_from() -> None:
    resolved = ResolvedCorridor(
        corridor=CORRIDOR,
        resolved_at=datetime(2026, 9, 26, 9, 0, tzinfo=UTC),
        unread_visa_pages=[failure(TOURIST)],
    )
    base = DestinationConfig(
        slug="australia",
        display_name="Australia",
        route_type="national",
        implementation_status="available",
        trusted_domains=["homeaffairs.gov.au"],
    )

    config = resolved.to_destination_config(base)

    assert [str(page.attempted_url) for page in config.unread_visa_pages] == [TOURIST]


def test_a_destination_refuses_an_unread_visa_page_off_its_approved_domains() -> None:
    singapore = load_destination_registry().get("singapore")
    assert singapore is not None
    payload = singapore.model_dump(mode="json")
    payload["unread_visa_pages"] = [
        failure("https://australia-visa-help.example.com/tourist-visa").model_dump(mode="json")
    ]

    with pytest.raises(ValidationError, match="not on an approved domain"):
        DestinationConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("url", "title", "label"),
    [
        # South Korea's: the address says nothing, the government's own label says PDF.
        (
            "https://overseas.mofa.go.kr/in-mumbai-en/brd/m_1978/down.do?seq=717617",
            "Korean Visa checklist(w.e.f. 24.08.2026).pdf",
            ", a PDF download we could not open",
        ),
        (
            "https://www.eda.admin.ch/files/Checklist_Tourist-EN.pdf",
            "Tourist",
            ", a PDF download we could not open",
        ),
        (
            "https://example.gov/forms/checklist.docx",
            "Checklist",
            ", a document download we could not open",
        ),
        ("https://www.ica.gov.sg/visa/documents-required", "Documents required", ""),
    ],
)
def test_a_named_page_that_is_a_file_says_it_is_a_download_nobody_opened(
    url: str, title: str, label: str
) -> None:
    """Entry 219, the owner: a checklist we could not open may be named, labelled as such."""

    page = SourceFailure(
        source_id="page",
        title=title,
        authority="authority",
        outcome="unusable",
        detail="could not be read",
        attempted_url=url,  # type: ignore[arg-type]
    )

    assert download_label(page) == label
