"""Letting a model choose among already-trusted pages, without letting it choose anything else.

No test here calls an LLM. The adjudicator is a protocol precisely so a fake can be injected, in
the same way `StructuredPlanGenerator` is faked for extraction.

The assertions that matter are the containment ones: the model picks from a list the application
built, and anything else it says is discarded rather than believed. It cannot introduce a page,
cannot reach a domain nobody approved, and its refusal is honoured rather than filled in.
"""

from typing import TypedDict

import pytest
from discovery_site import DETAIL_INDIA, MISSION_CHECKLIST, destination, handler

from visa_research_agent.discovery.adjudication import (
    EXCERPT_GAP_MARKER,
    AdjudicationError,
    DecisionTool,
    RoleAdjudication,
    RoleChoice,
    anchored_excerpt,
    build_candidate_packet,
    load_adjudication_prompt,
    validated_choices,
    validated_decision_tool,
)
from visa_research_agent.discovery.models import CandidatePage, Corridor, PageLink
from visa_research_agent.discovery.resolver import (
    AdjudicationRefusal,
    CorridorResolver,
    FetchedShortlist,
)

pytestmark = pytest.mark.anyio


def corridor() -> Corridor:
    return Corridor(
        destination_slug="testland",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def candidate(url: str, title: str = "") -> CandidatePage:
    return CandidatePage(
        link=PageLink(url=url, text=title, heading="", depth=0, discovered_from="seed"),
        title=title,
        found_by="crawl",
    )


def shortlist() -> FetchedShortlist:
    by_id = {
        "tl_india": candidate(DETAIL_INDIA, "Visa Requirements for Indian Travel Documents"),
        "tl_checklist": candidate(MISSION_CHECKLIST, "Items required"),
    }
    return FetchedShortlist(
        candidates=list(by_id.values()),
        by_id=by_id,
        contents={"tl_india": "You will need a visa.", "tl_checklist": "Bring a passport."},
    )


class PacketBudget(TypedDict):
    excerpt_characters: int
    excerpt_head_characters: int
    excerpt_window_characters: int
    anchor_terms: tuple[str, ...]


def packet_budget(
    *,
    excerpt_characters: int = 6_000,
    head_characters: int | None = None,
    anchor_terms: tuple[str, ...] = (),
) -> PacketBudget:
    """The excerpt arguments, so a test that is not about excerpting need not restate them.

    The head defaults to the whole budget, which is the flat head-of-page slice this replaced.
    """

    return PacketBudget(
        excerpt_characters=excerpt_characters,
        excerpt_head_characters=(
            excerpt_characters if head_characters is None else head_characters
        ),
        excerpt_window_characters=3_000,
        anchor_terms=anchor_terms,
    )


class FakeAdjudicator:
    """Answers with whatever the test wants, including things it should not be allowed to say."""

    def __init__(self, adjudication: RoleAdjudication | Exception) -> None:
        self.adjudication = adjudication
        self.calls: list[str] = []

    async def adjudicate(self, system_prompt: str, packet: str) -> RoleAdjudication:
        self.calls.append(packet)
        if isinstance(self.adjudication, Exception):
            raise self.adjudication
        return self.adjudication


class FlakyAdjudicator:
    """Fails a set number of times and then answers — the transient failure a retry is for."""

    def __init__(self, *, failures: int, adjudication: RoleAdjudication) -> None:
        self.remaining_failures = failures
        self.adjudication = adjudication
        self.calls: list[str] = []

    async def adjudicate(self, system_prompt: str, packet: str) -> RoleAdjudication:
        self.calls.append(packet)
        if self.remaining_failures:
            self.remaining_failures -= 1
            raise AdjudicationError("the request timed out")
        return self.adjudication


def resolver_with(adjudicator: object | None) -> CorridorResolver:
    return CorridorResolver(None, None, None, adjudicator=adjudicator)  # type: ignore[arg-type]


# --- containment ----------------------------------------------------------------------------


def test_a_page_the_model_invented_is_discarded() -> None:
    """The application decides what is real. This is the whole safety story of the change.

    A model that could name a page nobody fetched would be a way to introduce a source that never
    passed domain trust, which is the one thing this project cannot allow.
    """

    adjudication = RoleAdjudication(
        choices=[
            RoleChoice(
                role="document_checklist",
                source_id="tl_helpful_agency",
                reason="It looked comprehensive.",
            )
        ]
    )

    kept, discarded = validated_choices(adjudication, shortlist().by_id)

    assert kept == {}
    assert any("tl_helpful_agency" in reason for reason in discarded)


def test_a_real_choice_is_kept_with_its_reason() -> None:
    adjudication = RoleAdjudication(
        choices=[
            RoleChoice(
                role="document_checklist",
                source_id="tl_checklist",
                reason="It names a passport and a photograph.",
            )
        ]
    )

    kept, discarded = validated_choices(adjudication, shortlist().by_id)

    assert kept["document_checklist"] == ("tl_checklist", "It names a passport and a photograph.")
    assert discarded == []


def test_answering_the_same_role_twice_keeps_only_the_first() -> None:
    adjudication = RoleAdjudication(
        choices=[
            RoleChoice(role="visa_decision", source_id="tl_india", reason="States a visa is due."),
            RoleChoice(role="visa_decision", source_id="tl_checklist", reason="Also mentions it."),
        ]
    )

    kept, discarded = validated_choices(adjudication, shortlist().by_id)

    assert kept["visa_decision"][0] == "tl_india"
    assert any("more than once" in reason for reason in discarded)


# --- refusing -------------------------------------------------------------------------------


async def test_a_refusal_is_honoured_rather_than_filled_in() -> None:
    """A null choice must leave the role unresolved, never fall back to a plausible page."""

    adjudicator = FakeAdjudicator(
        RoleAdjudication(
            choices=[
                RoleChoice(role="visa_decision", source_id="tl_india", reason="States it plainly."),
                RoleChoice(
                    role="document_checklist",
                    source_id=None,
                    reason="No candidate names any document to bring.",
                ),
            ]
        )
    )
    notes: list[str] = []

    sources, unresolved, calls, _ = await resolver_with(adjudicator)._decide_roles(
        destination(), corridor(), shortlist(), notes
    )

    assert calls == 1
    assert "document_checklist" in unresolved
    assert [role for source in sources for role in source.roles] == ["visa_decision"]
    assert any("document checklist" in note for note in notes)


async def test_a_chosen_page_is_recorded_as_decided_by_the_model() -> None:
    adjudicator = FakeAdjudicator(
        RoleAdjudication(
            choices=[
                RoleChoice(
                    role="document_checklist",
                    source_id="tl_checklist",
                    reason="It lists the items to bring.",
                )
            ]
        )
    )

    sources, _, _, _ = await resolver_with(adjudicator)._decide_roles(
        destination(), corridor(), shortlist(), []
    )

    assert [source.decided_by for source in sources] == ["model"]
    assert "lists the items" in sources[0].signals[0]


# --- degrading ------------------------------------------------------------------------------


async def test_a_momentary_failure_is_retried_rather_than_costing_the_corridor() -> None:
    """The failures worth surviving are the transient ones: a timeout, a rate limit, one bad
    response. Retrying a model provider is not what entry 18 forbids — that is about an authority
    refusing to be read."""

    adjudicator = FlakyAdjudicator(
        failures=1,
        adjudication=RoleAdjudication(
            choices=[
                RoleChoice(
                    role="document_checklist",
                    source_id="tl_checklist",
                    reason="It lists the items to bring.",
                )
            ]
        ),
    )
    notes: list[str] = []

    sources, _, calls, _ = await resolver_with(adjudicator)._decide_roles(
        destination(), corridor(), shortlist(), notes
    )

    assert calls == 2
    assert any("retrying once" in note for note in notes)
    assert [source.decided_by for source in sources] == ["model"]


async def test_a_call_that_keeps_failing_refuses_instead_of_using_the_heuristic() -> None:
    """Entry 16 chose to fall back here, calling it "degrade to a worse answer, never to none".
    Entry 31 reverses it: the heuristic is the decider entry 15 caught naming Brazil's Riyadh page
    as a document checklist at exit 0, so falling back turns an outage into a confident wrong answer
    that only `decided_by` would reveal. Every other layer of this project refuses instead."""

    adjudicator = FakeAdjudicator(AdjudicationError("the request failed"))
    notes: list[str] = []

    with pytest.raises(AdjudicationRefusal) as raised:
        await resolver_with(adjudicator)._decide_roles(
            destination(), corridor(), shortlist(), notes
        )

    # The count is carried so a refusal still reports what it cost.
    assert raised.value.attempts == 2
    assert len(adjudicator.calls) == 2
    assert "failed on all 2 attempts" in str(raised.value)
    assert not any("heuristic ranking was used" in note for note in notes)


async def test_without_an_adjudicator_nothing_changes_and_no_call_is_made() -> None:
    sources, _, calls, _ = await resolver_with(None)._decide_roles(
        destination(), corridor(), shortlist(), []
    )

    assert calls == 0
    assert all(source.decided_by == "heuristic" for source in sources)


# --- the packet -----------------------------------------------------------------------------


def test_page_text_reaches_the_model_behind_a_named_untrusted_boundary() -> None:
    packet = build_candidate_packet(
        corridor(), shortlist().by_id, shortlist().contents, **packet_budget()
    )

    assert '"untrusted_content"' in packet
    assert "Bring a passport." in packet


def test_each_candidate_is_truncated_to_the_excerpt_budget() -> None:
    fetched = shortlist()
    fetched.contents["tl_india"] = "x" * 50_000

    packet = build_candidate_packet(
        corridor(), fetched.by_id, fetched.contents, **packet_budget(excerpt_characters=100)
    )

    assert "x" * 100 in packet
    assert "x" * 101 not in packet


def test_the_heuristic_ranking_is_withheld_so_it_cannot_anchor_the_answer() -> None:
    """Passing scores would re-import the ranking that got Brazil wrong."""

    packet = build_candidate_packet(
        corridor(), shortlist().by_id, shortlist().contents, **packet_budget()
    )

    for leaked in ("score", "link_scores", "body_scores", "combined"):
        assert leaked not in packet


def test_the_prompt_tells_the_model_that_refusing_is_correct() -> None:
    prompt = load_adjudication_prompt().lower()

    assert "refus" in prompt
    assert "never invent" in prompt
    assert "untrusted_content" in prompt


def test_the_prompt_explains_the_mark_that_stands_for_omitted_text() -> None:
    """The marker is only honest if the model is told what it means, so the two are tied here."""

    assert EXCERPT_GAP_MARKER.strip() in load_adjudication_prompt()


def test_the_fake_site_handler_is_never_contacted_during_adjudication() -> None:
    # Adjudication reads only what was already fetched; it must make no request of its own.
    requests: list[object] = []
    handler(requests)  # type: ignore[arg-type]

    build_candidate_packet(corridor(), shortlist().by_id, shortlist().contents, **packet_budget())

    assert requests == []


# --- the excerpt ----------------------------------------------------------------------------
#
# The excerpt is a recall gate, not a formatting detail: a page whose answer falls outside it is a
# page nothing downstream can recover. These tests are written from the corridor that proved it —
# `canada/GB/GB/tourism`, where the sentence answering a British traveller sat at offset 8,947 of a
# 16,465-character page and a flat 6,000-character slice refused the corridor.


COUNTRY_LIST_PAGE = (
    "What you need to enter Canada\n"
    + "Preamble about citizenship and how you are travelling.\n" * 40
    + "Travellers who need a visa\n"
    # Long enough that the mention falls past the default budget as well as past the head: the
    # resolver test below would otherwise pass on a page a flat slice would also have caught.
    + "".join(f"Country number {number}\n" for number in range(1_400))
    + "If you are travelling by air\n"
    + "You need an eTA and a valid passport to board your flight. You do not need a visitor visa.\n"
    + "eTA-required countries or territories\nAndorra\nAustralia\nBritish citizen\nBrunei\n"
    # Long enough after the mention that the whole page cannot fit the default budget: the test
    # below would otherwise pass by the page being short, not by the excerpt being anchored.
    + "".join(f"Later country {number}\n" for number in range(1_200))
)
ANSWER = "You need an eTA and a valid passport"


def excerpt(
    text: str,
    anchors: tuple[str, ...] = (),
    *,
    budget: int = 20_000,
    head_characters: int = 6_000,
    window_characters: int = 3_000,
) -> str:
    """The production numbers unless a test is about one of them."""

    return anchored_excerpt(
        text,
        anchors,
        budget=budget,
        head_characters=head_characters,
        window_characters=window_characters,
    )


def test_a_page_that_fits_the_budget_is_shown_whole_and_unmarked() -> None:
    assert excerpt("Short page.") == "Short page."
    assert EXCERPT_GAP_MARKER not in excerpt("Short page.")


def test_the_traveller_is_found_where_the_alphabet_put_them() -> None:
    """The defect itself: at 6,000 flat this page answers Indians and refuses British citizens."""

    assert ANSWER not in COUNTRY_LIST_PAGE[:6_000]

    kept = excerpt(COUNTRY_LIST_PAGE, ("british", "united kingdom"), budget=9_000)

    assert "British citizen" in kept
    assert ANSWER in kept


def test_the_window_is_centred_so_the_sentence_before_the_mention_survives() -> None:
    """Canada answers the question just before naming the traveller, not just after it."""

    forward_only = COUNTRY_LIST_PAGE.index("British citizen")

    kept = excerpt(COUNTRY_LIST_PAGE, ("british",), budget=9_000, window_characters=600)

    assert ANSWER in kept
    assert COUNTRY_LIST_PAGE.index(ANSWER) < forward_only


def test_what_was_left_out_is_marked_so_a_cut_page_cannot_read_as_a_finished_one() -> None:
    kept = excerpt(COUNTRY_LIST_PAGE, ("british",), budget=9_000)

    assert kept.startswith("What you need to enter Canada")
    assert kept.count(EXCERPT_GAP_MARKER) >= 1
    assert kept.endswith(EXCERPT_GAP_MARKER)


def test_a_page_that_never_names_the_traveller_is_read_further_into_not_less_of() -> None:
    """Leftover budget continues from the head, so this is never worse than a flat slice."""

    kept = excerpt(COUNTRY_LIST_PAGE, ("nowhere-in-this-page",), budget=9_000)

    assert COUNTRY_LIST_PAGE[:9_000] in kept
    assert EXCERPT_GAP_MARKER not in kept[:9_000]


def test_no_candidate_exceeds_its_budget_however_often_it_names_the_traveller() -> None:
    page = "".join(f"British citizen {number}\n" for number in range(5_000))

    kept = excerpt(page, ("british",), budget=9_000)

    assert len(kept.replace(EXCERPT_GAP_MARKER, "")) == 9_000


def test_a_two_letter_country_anchors_only_where_it_is_the_country() -> None:
    """ "us" is a pronoun. Case-insensitively it anchored 34 windows in one Canadian guide."""

    page = "Head.\n" + "Tell us about your trip. " * 500 + "US citizens need no visa.\n"

    kept = excerpt(page, ("us", "usa", "united states"), budget=600, head_characters=100)

    assert "US citizens need no visa." in kept


def test_a_country_word_does_not_anchor_inside_a_longer_word() -> None:
    page = "Head.\n" + "Ukraine. " * 500 + "UK passport holders need an eTA.\n"

    kept = excerpt(page, ("uk", "british"), budget=600, head_characters=100)

    assert "UK passport holders need an eTA." in kept


def test_the_packet_anchors_on_the_words_it_is_given() -> None:
    fetched = shortlist()
    fetched.contents["tl_india"] = COUNTRY_LIST_PAGE

    anchored = build_candidate_packet(
        corridor(),
        fetched.by_id,
        fetched.contents,
        **packet_budget(excerpt_characters=9_000, head_characters=6_000, anchor_terms=("british",)),
    )
    flat = build_candidate_packet(
        corridor(), fetched.by_id, fetched.contents, **packet_budget(excerpt_characters=9_000)
    )

    assert "British citizen" in anchored
    assert "British citizen" not in flat


async def test_the_resolver_anchors_on_the_travellers_own_countries() -> None:
    """IN/GB: the packet must follow the passport and the post, not a fixed offset."""

    fetched = shortlist()
    fetched.contents["tl_india"] = COUNTRY_LIST_PAGE
    adjudicator = FakeAdjudicator(RoleAdjudication(choices=[]))

    await resolver_with(adjudicator)._decide_roles(destination(), corridor(), fetched, [])

    assert "British citizen" in adjudicator.calls[0]


# --- the decision behind a tool -------------------------------------------------------------


def test_a_tool_the_model_invented_is_discarded_like_any_other_id() -> None:
    """Same containment as `validated_choices`. A traveller is being sent to this URL, so it has to
    be a page the application fetched, not one the model produced."""

    kept, discarded = validated_decision_tool(
        RoleAdjudication(
            choices=[],
            decision_tool=DecisionTool(
                source_id="tl_checker",
                reason="A step-by-step checker that asks the reader their nationality.",
            ),
        ),
        shortlist().by_id,
    )

    assert kept is None
    assert any("not a candidate" in reason for reason in discarded)


async def test_a_page_that_asks_the_decision_resolves_the_corridor_instead_of_losing_it() -> None:
    """The United Kingdom outcome from entry 58: the checklist was found and then thrown away with
    the rest of the plan, because `visa_decision` was unfilled and nothing could say why."""

    adjudicator = FakeAdjudicator(
        RoleAdjudication(
            choices=[
                RoleChoice(
                    role="visa_decision",
                    source_id=None,
                    reason="No candidate states whether this traveller needs a visa.",
                ),
                RoleChoice(
                    role="document_checklist",
                    source_id="tl_checklist",
                    reason="It lists the items to bring.",
                ),
            ],
            decision_tool=DecisionTool(
                source_id="tl_india",
                reason="It asks nationality and purpose, then says whether a visa is needed.",
            ),
        )
    )
    notes: list[str] = []

    sources, unresolved, _, tool = await resolver_with(adjudicator)._decide_roles(
        destination(), corridor(), shortlist(), notes
    )

    assert tool == DETAIL_INDIA
    assert "visa_decision" in unresolved
    assert [role for source in sources for role in source.roles] == ["document_checklist"]
    assert any("decides the visa question interactively" in note for note in notes)


async def test_the_heuristic_path_never_names_a_tool() -> None:
    """Whether a page is a questionnaire is a question about meaning, and entry 57 is what keyword
    matching meaning cost. With no adjudicator the corridor refuses exactly as it did before."""

    _, _, calls, tool = await resolver_with(None)._decide_roles(
        destination(), corridor(), shortlist(), []
    )

    assert calls == 0
    assert tool is None


def test_the_prompt_keeps_not_found_and_behind_a_tool_apart() -> None:
    """Entry 32's lesson, applied to a new exception: if "could not find it" can present as "an
    official tool holds it", every failed corridor drifts into looking tool-limited."""

    prompt = load_adjudication_prompt()

    assert "decision_tool" in prompt
    assert "not among the candidates" in prompt
    assert "not a way to soften a refusal" in prompt
