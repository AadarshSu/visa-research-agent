"""Choosing what to read by asking a model: what it may return, and what it may never carry.

Offline throughout. The test that matters is `test_a_selection_cannot_carry_a_word_of_stored_text`:
it is the barrier that lets `page_text.text_for_selection` exist at all (DECISIONS entry 83).
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from visa_research_agent.discovery.models import CandidatePage, Corridor, PageLink, RoleScores
from visa_research_agent.discovery.page_text import PageTextStore, StoredPage
from visa_research_agent.discovery.selection import (
    MAXIMUM_EXCERPT_CHARACTERS,
    MINIMUM_EXCERPT_CHARACTERS,
    Selection,
    admitted_on_text,
    build_selection_packet,
    excerpt_budget,
    load_selection_prompt,
    validated_selection,
)

NOW = datetime(2026, 8, 26, 9, 0, tzinfo=UTC)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="japan", passport_nationality="IN", applying_from="GB", purpose="tourism"
    )


def candidate(url: str, text: str = "") -> CandidatePage:
    return CandidatePage(
        link=PageLink(url=url, text=text, heading="", depth=1, discovered_from="seed")
    )


def test_a_selection_cannot_carry_a_word_of_stored_text() -> None:
    """The barrier that permits `text_for_selection` to exist.

    Entry 78 forbade an accessor for stored bodies because a sentence written from one would be
    guidance served outside `source_maximum_stale_hours`. Entry 83 moved that barrier rather than
    removing it: bodies may be read, and the response type has nowhere to put prose. This test is
    the barrier. If it fails, the reason entry 78 gave has come back.
    """

    assert set(Selection.model_fields) == {"source_ids"}
    field = Selection.model_fields["source_ids"]
    assert field.annotation == list[str]


def test_a_candidate_with_no_stored_text_is_marked_rather_than_dropped() -> None:
    """Entry 80's failure, stated so a model can avoid it.

    A scalar cannot say "nothing is known about this page" — absent text scores zero and zero
    competes. The packet says it in words instead, and the candidate is still offered.
    """

    candidates = {
        "known": candidate("https://a.gov.example/known.html"),
        "unknown": candidate("https://a.gov.example/unknown.html"),
    }
    packet = build_selection_packet(corridor(), candidates, {"known": "Checklist for tourism..."})

    assert "no_stored_text" in packet
    assert "unknown.html" in packet, "a candidate nothing is known about is still offered"
    assert "stored_excerpt" in packet


def test_a_wide_field_shortens_excerpts_rather_than_dropping_candidates() -> None:
    """Dropping the 300th candidate would rebuild the recall gate this call exists to remove."""

    assert excerpt_budget(10, total=400_000) == MAXIMUM_EXCERPT_CHARACTERS
    assert excerpt_budget(705, total=400_000) < MAXIMUM_EXCERPT_CHARACTERS
    assert excerpt_budget(100_000, total=400_000) == MINIMUM_EXCERPT_CHARACTERS
    assert excerpt_budget(0, total=400_000) == MAXIMUM_EXCERPT_CHARACTERS


def test_the_packet_withholds_the_heuristic_scores() -> None:
    """`build_candidate_packet` withholds them for the same reason: passing them would anchor the
    model to the ranking this call exists to replace."""

    picked = candidate("https://a.gov.example/x.html")
    picked.link_scores.scores["visa_decision"] = 91.5

    packet = build_selection_packet(corridor(), {"x": picked}, {})

    assert "91.5" not in packet
    assert "link_scores" not in packet


def test_an_invented_id_is_discarded_and_named() -> None:
    candidates = {"real": candidate("https://a.gov.example/real.html")}

    kept, notes = validated_selection(
        Selection(source_ids=["real", "invented", "real"]), candidates
    )

    assert kept == ["real"], "duplicates collapse and unknown ids are dropped"
    assert any("invented" in note for note in notes)


def test_the_prompt_forbids_writing_anything_a_traveller_reads() -> None:
    """The type makes prose impossible; the prompt has to say why, or the model tries anyway."""

    prompt = load_selection_prompt()

    assert "no_stored_text" in prompt, "the model must be told what an absence means"
    assert "out of date" in prompt


def test_stored_text_is_returned_only_for_pages_the_index_holds(tmp_path: Path) -> None:
    store = PageTextStore(tmp_path)
    store.write("JP", [StoredPage(url="https://a.gov.example/a", fetched_at=NOW, body="x" * 400)])

    held = store.text_for_selection("JP", ["https://a.gov.example/a", "https://a.gov.example/b"])

    assert list(held) == ["https://a.gov.example/a"]
    assert store.text_for_selection("XX", ["https://a.gov.example/a"]) == {}


@pytest.mark.parametrize("count", [1, 72, 705])
def test_every_candidate_reaches_the_packet(count: int) -> None:
    candidates = {f"id{i}": candidate(f"https://a.gov.example/{i}.html") for i in range(count)}

    packet = build_selection_packet(corridor(), candidates, {})

    for i in range(count):
        assert f'"id{i}"' in packet


# --- what stored text may put back into the pool, TODO item 31 ---------------------------------


def text_scores(**by_role: float) -> RoleScores:
    return RoleScores(scores=dict(by_role))


def test_a_page_the_link_scored_zero_is_admitted_on_its_own_text() -> None:
    """Entry 127's case as arithmetic. Czechia's list of supporting documents for applicants in the
    United Kingdom scored zero on its link for every role, so the selector was never shown it, while
    its own text names the documents."""

    page = candidate("https://a.gov.example/uk.pdf")

    admitted = admitted_on_text([page], {page.link.url: text_scores(document_checklist=85.0)})

    assert admitted == [page]


def test_a_page_with_no_stored_text_or_nothing_scoring_in_it_stays_out() -> None:
    """An unread page has nothing to be judged on, and admitting it anyway is the unbounded widening
    the per-role bound exists to prevent. A page whose text scores zero or below — Liechtenstein's
    Casino Ordinance, a title naming the wrong purpose — is chaff and stays out with it."""

    unread = candidate("https://a.gov.example/unread.html")
    empty = candidate("https://a.gov.example/casino-ordinance.html")
    off_scope = candidate("https://a.gov.example/student-visa.html")

    admitted = admitted_on_text(
        [unread, empty, off_scope],
        {empty.link.url: RoleScores(), off_scope.link.url: text_scores(fees=-5.0)},
    )

    assert admitted == []


def test_each_role_admits_its_bound_best_first_with_ties_broken_by_address() -> None:
    pages = [candidate(f"https://a.gov.example/{i}.html") for i in range(8)]
    scored = {page.link.url: text_scores(fees=float(10 + i % 3)) for i, page in enumerate(pages)}

    admitted = admitted_on_text(pages, scored, per_role=3)

    assert [page.link.url for page in admitted] == [
        "https://a.gov.example/2.html",
        "https://a.gov.example/5.html",
        "https://a.gov.example/1.html",
    ]


def test_a_page_two_roles_want_is_admitted_once_and_each_role_still_gets_its_share() -> None:
    both = candidate("https://a.gov.example/both.html")
    fees = candidate("https://a.gov.example/fees.html")
    times = candidate("https://a.gov.example/times.html")
    scored = {
        both.link.url: text_scores(fees=50.0, processing_times=50.0),
        fees.link.url: text_scores(fees=40.0),
        times.link.url: text_scores(processing_times=40.0),
    }

    admitted = admitted_on_text([both, fees, times], scored, per_role=2)

    assert len(admitted) == 3
    assert {page.link.url for page in admitted} == {both.link.url, fees.link.url, times.link.url}


def test_only_a_page_outside_the_pool_can_be_admitted() -> None:
    """The resolver hands over the stored-text scores of *every* candidate, pooled ones included,
    because step 3b computed them all. Admission must never re-add or re-order the pool itself."""

    pooled = candidate("https://a.gov.example/pooled.html")
    outside = candidate("https://a.gov.example/outside.html")
    scored = {
        pooled.link.url: text_scores(document_checklist=99.0),
        outside.link.url: text_scores(document_checklist=30.0),
    }

    assert admitted_on_text([outside], scored) == [outside]
