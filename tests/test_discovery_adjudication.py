"""Letting a model choose among already-trusted pages, without letting it choose anything else.

No test here calls an LLM. The adjudicator is a protocol precisely so a fake can be injected, in
the same way `StructuredPlanGenerator` is faked for extraction.

The assertions that matter are the containment ones: the model picks from a list the application
built, and anything else it says is discarded rather than believed. It cannot introduce a page,
cannot reach a domain nobody approved, and its refusal is honoured rather than filled in.
"""

import pytest
from discovery_site import DETAIL_INDIA, MISSION_CHECKLIST, destination, handler

from visa_research_agent.discovery.adjudication import (
    AdjudicationError,
    RoleAdjudication,
    RoleChoice,
    build_candidate_packet,
    load_adjudication_prompt,
    validated_choices,
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

    sources, unresolved, calls = await resolver_with(adjudicator)._decide_roles(
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

    sources, _, _ = await resolver_with(adjudicator)._decide_roles(
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

    sources, _, calls = await resolver_with(adjudicator)._decide_roles(
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
    sources, _, calls = await resolver_with(None)._decide_roles(
        destination(), corridor(), shortlist(), []
    )

    assert calls == 0
    assert all(source.decided_by == "heuristic" for source in sources)


# --- the packet -----------------------------------------------------------------------------


def test_page_text_reaches_the_model_behind_a_named_untrusted_boundary() -> None:
    packet = build_candidate_packet(
        corridor(), shortlist().by_id, shortlist().contents, excerpt_characters=6_000
    )

    assert '"untrusted_content"' in packet
    assert "Bring a passport." in packet


def test_each_candidate_is_truncated_to_the_excerpt_budget() -> None:
    fetched = shortlist()
    fetched.contents["tl_india"] = "x" * 50_000

    packet = build_candidate_packet(
        corridor(), fetched.by_id, fetched.contents, excerpt_characters=100
    )

    assert "x" * 100 in packet
    assert "x" * 101 not in packet


def test_the_heuristic_ranking_is_withheld_so_it_cannot_anchor_the_answer() -> None:
    """Passing scores would re-import the ranking that got Brazil wrong."""

    packet = build_candidate_packet(
        corridor(), shortlist().by_id, shortlist().contents, excerpt_characters=6_000
    )

    for leaked in ("score", "link_scores", "body_scores", "combined"):
        assert leaked not in packet


def test_the_prompt_tells_the_model_that_refusing_is_correct() -> None:
    prompt = load_adjudication_prompt().lower()

    assert "refus" in prompt
    assert "never invent" in prompt
    assert "untrusted_content" in prompt


def test_the_fake_site_handler_is_never_contacted_during_adjudication() -> None:
    # Adjudication reads only what was already fetched; it must make no request of its own.
    requests: list[object] = []
    handler(requests)  # type: ignore[arg-type]

    build_candidate_packet(
        corridor(), shortlist().by_id, shortlist().contents, excerpt_characters=6_000
    )

    assert requests == []
