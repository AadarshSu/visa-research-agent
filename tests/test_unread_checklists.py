"""Likely checklist pages a run could not read are named for the traveller, never read.

TODO item 9, second part. Nobody can show a checklist does not exist (DECISIONS entry 153), but a
run can show it met a page that looked like one and could not open it — and the traveller can.
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
    says_it_is_this_trips_checklist,
    unread_checklist_pages,
)
from visa_research_agent.domain.models import DestinationConfig, FailureOutcome, SourceFailure

CHECKLIST = "https://www.ica.gov.sg/visa/documents-required"
PRESS = "https://www.ica.gov.sg/news/press-release"
UNSCORED = "https://www.ica.gov.sg/about-us"


def failure(url: str, outcome: FailureOutcome = "challenged") -> SourceFailure:
    return SourceFailure(
        source_id="singapore_www_page",
        title="Documents required",
        authority="Singapore authority (www.ica.gov.sg)",
        outcome=outcome,
        detail="asked this client to prove it is a browser, and that could not be answered here",
        attempted_url=url,  # type: ignore[arg-type]
    )


def candidate(url: str, checklist_score: float) -> CandidatePage:
    scores = {"document_checklist": checklist_score} if checklist_score else {}
    return CandidatePage(
        link=PageLink(url=url, text="Documents required", depth=0),
        link_scores=RoleScores(scores=scores),
    )


CORRIDOR = Corridor(
    destination_slug="singapore", passport_nationality="IN", applying_from="GB", purpose="tourism"
)

CANDIDATES = {
    CHECKLIST: candidate(CHECKLIST, 46.0),
    PRESS: candidate(PRESS, 0.0),
    UNSCORED: candidate(UNSCORED, 0.0),
}


def test_a_likely_checklist_page_the_run_could_not_read_is_named() -> None:
    named = unread_checklist_pages(
        [failure(CHECKLIST)],
        CANDIDATES,
        checklist_filled=False,
        already_named=[],
        corridor=CORRIDOR,
        lexicon=get_lexicon(),
    )

    assert [str(page.attempted_url) for page in named] == [CHECKLIST]
    assert named[0].outcome == "challenged", "the reason is what this run saw, carried whole"


def test_a_refused_checklist_is_named_as_a_checklist_too() -> None:
    """Entry 213. Switzerland's India embassy answered `403` for its "Checklist for Schengen Visa:
    Tourist". The refusal is reported in the evidence banner; the traveller looking for documents
    looks in the documents panel, so the page is named there as well — never read."""

    named = unread_checklist_pages(
        [failure(CHECKLIST, "blocked")],
        CANDIDATES,
        checklist_filled=False,
        already_named=[],
        corridor=CORRIDOR,
        lexicon=get_lexicon(),
    )

    assert [str(page.attempted_url) for page in named] == [CHECKLIST]
    assert named[0].outcome == "blocked"


def test_nothing_is_named_once_a_page_filled_the_checklist() -> None:
    """A plan with its checklist has nothing to point past."""

    assert (
        unread_checklist_pages(
            [failure(CHECKLIST)],
            CANDIDATES,
            checklist_filled=True,
            already_named=[],
            corridor=CORRIDOR,
            lexicon=get_lexicon(),
        )
        == []
    )


@pytest.mark.parametrize(
    ("failures", "already_named"),
    [
        # Landed off the approved domains: not an address to send a traveller to.
        ([failure(CHECKLIST, "untrusted")], []),
        # Unreadable, but nothing about its link made it a likely checklist.
        ([failure(PRESS)], []),
        # Never a candidate at all.
        ([failure("https://www.ica.gov.sg/unknown")], []),
        # Something else in the plan already names this address.
        ([failure(CHECKLIST)], [CHECKLIST]),
    ],
)
def test_a_page_is_named_only_once_and_only_for_a_reason_that_licenses_it(
    failures: list[SourceFailure], already_named: list[str]
) -> None:
    assert (
        unread_checklist_pages(
            failures,
            CANDIDATES,
            checklist_filled=False,
            already_named=already_named,
            corridor=CORRIDOR,
            lexicon=get_lexicon(),
        )
        == []
    )


def test_a_page_is_named_once_however_many_times_it_failed() -> None:
    named = unread_checklist_pages(
        [failure(CHECKLIST), failure(CHECKLIST, "unreachable")],
        CANDIDATES,
        checklist_filled=False,
        already_named=[],
        corridor=CORRIDOR,
        lexicon=get_lexicon(),
    )

    assert len(named) == 1


def test_the_pages_reach_the_destination_a_plan_is_built_from() -> None:
    """A stored corridor becomes a destination through the validators, and so do these pages."""

    resolved = ResolvedCorridor(
        corridor=Corridor(
            destination_slug="singapore",
            passport_nationality="IN",
            applying_from="GB",
            purpose="tourism",
        ),
        resolved_at=datetime(2026, 9, 14, 9, 0, tzinfo=UTC),
        unread_checklist_pages=[failure(CHECKLIST)],
    )
    base = DestinationConfig(
        slug="singapore",
        display_name="Singapore",
        route_type="national",
        implementation_status="available",
        trusted_domains=["ica.gov.sg"],
    )

    config = resolved.to_destination_config(base)

    assert [str(page.attempted_url) for page in config.unread_checklist_pages] == [CHECKLIST]


def test_a_destination_refuses_an_unread_checklist_page_off_its_approved_domains() -> None:
    """Offered to a traveller as the destination's own page, so held to entry 2's domain rule."""

    singapore = load_destination_registry().get("singapore")
    assert singapore is not None
    payload = singapore.model_dump(mode="json")
    payload["unread_checklist_pages"] = [
        failure("https://singapore-visa-help.example.com/checklist").model_dump(mode="json")
    ]

    with pytest.raises(ValidationError, match="not on an approved domain"):
        DestinationConfig.model_validate(payload)


@pytest.mark.parametrize(
    ("text", "heading", "named"),
    [
        # Switzerland's and South Korea's, which say so.
        ("Checklist for Schengen Visa: Tourist", "", True),
        ("Korean Visa checklist(w.e.f. 24.08.2026).pdf", "", True),
        # A purpose label under a checklists heading.
        ("Tourist", "Checklists", True),
        # Australia's, named on a link score alone before entry 213.
        ("Evidence of the financial status and funding for visit", "", False),
        ("Visitor visa (subclass 600) Tourist stream", "", False),
        # A heading alone: every form under it would qualify.
        ("Visa application form", "Visa application documents", False),
        # Another purpose's checklist.
        ("Checklist for Schengen business visa", "", False),
    ],
)
def test_only_a_page_whose_own_words_say_it_is_this_trips_checklist_is_named(
    text: str, heading: str, named: bool
) -> None:
    """Entry 213, the owner: name an unread page only where the surrounding context makes us
    confident it leads to the relevant checklist."""

    page = CandidatePage(
        link=PageLink(url=CHECKLIST, text=text, heading=heading, depth=1),
        link_scores=RoleScores(scores={"document_checklist": 20.0}),
    )

    assert says_it_is_this_trips_checklist(page, CORRIDOR, get_lexicon()) is named
