from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from visa_research_agent.domain.models import (
    ApplicationStep,
    InteractiveTool,
    SourceReference,
    VisaPlan,
    VisaRequirement,
)


def application_steps(source_id: str = "official-source") -> list[ApplicationStep]:
    return [
        ApplicationStep(
            title=title,
            action=action,
            timing=timing,
            source_ids=[source_id],
            link_target="source",
            link_source_id=source_id,
        )
        for title, action, timing in [
            ("Prepare documents", "Prepare the documents.", "Before booking."),
            ("Book appointment", "Book the appointment.", "Before travel."),
            ("Attend centre", "Attend the visa centre.", "At the booked time."),
            ("Submit application", "Submit the application.", "At the appointment."),
        ]
    ]


def test_source_reference_requires_a_timezone() -> None:
    with pytest.raises(ValidationError, match="timestamp must include a timezone"):
        SourceReference.model_validate(
            {
                "source_id": "official-source",
                "title": "Official source",
                "url": "https://example.gov/visas",
                "authority": "Example authority",
                "retrieved_at": datetime(2026, 8, 5),
            }
        )


def test_requirement_rejects_an_unsupported_category() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        VisaRequirement.model_validate(
            {
                "name": "Passport",
                "category": "sometimes",
                "description": "A passport is requested.",
                "reason_it_applies": "The traveller uses an ordinary passport.",
                "source_ids": ["official-source"],
            }
        )


def test_visa_plan_rejects_unknown_requirement_source_ids() -> None:
    checked_at = datetime(2026, 8, 5, tzinfo=UTC)

    with pytest.raises(ValidationError, match="unknown source IDs"):
        VisaPlan(
            destination="Singapore",
            visa_required=True,
            visa_type="Entry visa",
            explanation="The cited source states that a visa is required.",
            decision_source_ids=["official-source"],
            where_to_apply=None,
            requirements=[
                VisaRequirement(
                    name="Passport",
                    description="A passport is requested.",
                    reason_it_applies="The traveller uses an ordinary passport.",
                    source_ids=["missing-source"],
                )
            ],
            application_document_source_ids=["official-source"],
            application_steps=application_steps(),
            sources=[
                SourceReference.model_validate(
                    {
                        "source_id": "official-source",
                        "title": "Official source",
                        "url": "https://example.gov/visas",
                        "authority": "Example authority",
                        "retrieved_at": checked_at,
                    }
                )
            ],
            unresolved_questions=[],
            last_checked=checked_at,
            status="verified",
        )


def test_application_steps_are_structured_and_bounded() -> None:
    steps = [step.model_dump() for step in application_steps()]
    steps[0]["action"] = "A" * 321

    with pytest.raises(ValidationError):
        VisaPlan.model_validate(
            {
                "destination": "Singapore",
                "visa_required": True,
                "visa_type": "Entry visa",
                "explanation": "The cited source states that a visa is required.",
                "decision_source_ids": ["official-source"],
                "where_to_apply": None,
                "requirements": [],
                "application_document_source_ids": ["official-source"],
                "application_steps": steps,
                "sources": [
                    {
                        "source_id": "official-source",
                        "title": "Official source",
                        "url": "https://example.gov/visas",
                        "authority": "Example authority",
                        "retrieved_at": datetime(2026, 8, 5, tzinfo=UTC),
                    }
                ],
                "unresolved_questions": [],
                "last_checked": datetime(2026, 8, 5, tzinfo=UTC),
            }
        )


def test_source_step_link_must_be_cited_by_the_step() -> None:
    steps = [step.model_dump() for step in application_steps()]
    steps[0]["link_source_id"] = "uncited-source"

    with pytest.raises(ValidationError, match="must also appear in source_ids"):
        VisaPlan.model_validate(
            {
                "destination": "Singapore",
                "visa_required": True,
                "visa_type": "Entry visa",
                "explanation": "The cited source states that a visa is required.",
                "decision_source_ids": ["official-source"],
                "where_to_apply": None,
                "requirements": [],
                "application_document_source_ids": ["official-source"],
                "application_steps": steps,
                "sources": [
                    {
                        "source_id": "official-source",
                        "title": "Official source",
                        "url": "https://example.gov/visas",
                        "authority": "Example authority",
                        "retrieved_at": datetime(2026, 8, 5, tzinfo=UTC),
                    }
                ],
                "unresolved_questions": [],
                "last_checked": datetime(2026, 8, 5, tzinfo=UTC),
            }
        )


def checklistless_plan(**overrides: object) -> dict[str, object]:
    """A plan for an authority that publishes no document checklist at all."""

    checked_at = datetime(2026, 8, 5, tzinfo=UTC)
    body: dict[str, object] = {
        "destination": "Vietnam",
        "visa_required": True,
        "visa_type": "E-visa",
        "explanation": "The cited source states that a visa is required.",
        "decision_source_ids": ["official-source"],
        "where_to_apply": None,
        "requirements": [],
        "application_document_source_ids": [],
        "application_steps": [step.model_dump() for step in application_steps()],
        "sources": [
            {
                "source_id": "official-source",
                "title": "Official source",
                "url": "https://example.gov/visas",
                "authority": "Example authority",
                "retrieved_at": checked_at,
            }
        ],
        "unresolved_questions": ["No official document checklist is published for this route."],
        "last_checked": checked_at,
        "status": "verified",
    }
    body.update(overrides)
    return body


def test_a_plan_may_have_no_document_checklist_when_it_says_so() -> None:
    """Some authorities publish none, so the plan states the gap rather than being refused."""

    plan = VisaPlan.model_validate(checklistless_plan())

    assert plan.application_document_source_ids == []
    assert plan.requirements == []


def test_a_plan_with_no_document_source_cannot_list_requirements() -> None:
    """The guard that makes a checklist-less corridor safe to serve.

    With no designated document source there is nothing a requirement could honestly cite, so
    listing one means it was inferred from an eligibility rule or an application form read as
    though it were guidance. Refused structurally rather than asked for in the prompt.
    """

    with pytest.raises(ValidationError, match="cannot list document requirements"):
        VisaPlan.model_validate(
            checklistless_plan(
                requirements=[
                    {
                        "name": "Passport",
                        "description": "A passport is requested.",
                        "reason_it_applies": "Inferred from the eligibility page.",
                        "source_ids": ["official-source"],
                    }
                ]
            )
        )


def test_a_plan_with_no_document_source_must_say_what_is_missing() -> None:
    # Silence would read as "this authority requires no documents", which is far worse.
    with pytest.raises(ValidationError, match="must record what could not be answered"):
        VisaPlan.model_validate(checklistless_plan(unresolved_questions=[]))


def test_a_step_title_that_stopped_mid_clause_is_tidied() -> None:
    """A model given eighty characters wrote to the limit and stopped mid-sentence — "…if the wizard
    says a visa," — which reads as a truncated interface. The title is a label, so trimming the
    trailing punctuation invents nothing; the substance was always in the action."""

    step = ApplicationStep.model_validate(
        {
            "title": "Create an account and complete the online application,",
            "action": "Create an account on the official portal and complete the form.",
            "timing": "After confirming a visa is needed",
            "source_ids": ["a_source"],
            "link_target": "none",
            "link_source_id": None,
        }
    )

    assert step.title == "Create an account and complete the online application"


def test_a_step_title_has_room_for_a_label_and_no_more() -> None:
    """Seventy characters is a label. A sentence belongs in the action, which has room for one."""

    with pytest.raises(ValidationError):
        ApplicationStep.model_validate(
            {
                "title": "Create an account and complete the online application if the wizard "
                "says a visa is needed for this trip",
                "action": "Create an account on the official portal.",
                "timing": "After confirming a visa is needed",
                "source_ids": ["a_source"],
                "link_target": "none",
                "link_source_id": None,
            }
        )


# --- a decision an official tool holds ---------------------------------------------------------


def plan_payload(**overrides: object) -> dict[str, object]:
    checked_at = datetime(2026, 8, 5, tzinfo=UTC)
    payload: dict[str, object] = {
        "destination": "United Kingdom",
        "visa_required": None,
        "visa_type": None,
        "explanation": "The Home Office decides this through its own official checker.",
        "decision_source_ids": ["official-source"],
        "where_to_apply": None,
        "requirements": [],
        "application_document_source_ids": [],
        "application_steps": [step.model_dump() for step in application_steps()],
        "sources": [
            {
                "source_id": "official-source",
                "title": "Official source",
                "url": "https://example.gov/visas",
                "authority": "Example authority",
                "retrieved_at": checked_at,
            }
        ],
        "unresolved_questions": ["Answer the official checker to get the decision."],
        "last_checked": checked_at,
        "status": "partial",
        "official_tools": [
            {
                "topic": "visa_decision",
                "url": "https://www.gov.uk/check-uk-visa",
                "authority": "United Kingdom authority (www.gov.uk)",
                "detail": "decides this by asking questions rather than stating an answer",
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_a_plan_may_name_the_tool_that_holds_the_decision_it_could_not_state() -> None:
    plan = VisaPlan.model_validate(plan_payload())

    assert plan.visa_required is None
    assert [str(tool.url) for tool in plan.decision_tools] == ["https://www.gov.uk/check-uk-visa"]


def test_naming_the_tool_and_answering_it_are_mutually_exclusive() -> None:
    """A tool is named because no page stated the decision. Stating one anyway means it came from
    somewhere else — most likely the questionnaire's own prompts, which is reading an answer out of
    a question."""

    with pytest.raises(ValidationError, match="cannot also state whether a visa is required"):
        VisaPlan.model_validate(plan_payload(visa_required=True))


def test_a_plan_resting_on_an_unanswered_questionnaire_is_never_verified() -> None:
    """The decision is the one thing a traveller most needs right, and nobody read it off a page."""

    with pytest.raises(ValidationError, match="nobody read off a page"):
        VisaPlan.model_validate(plan_payload(status="verified"))


def test_a_decision_tool_carries_no_claim_about_what_it_would_answer() -> None:
    """Only where the decision is settled, never what it settles to."""

    tool = InteractiveTool.model_validate(
        {
            "topic": "visa_decision",
            "url": "https://www.gov.uk/check-uk-visa",
            "authority": "United Kingdom authority (www.gov.uk)",
            "detail": "decides this by asking questions rather than stating an answer",
        }
    )

    assert set(tool.model_dump()) == {"topic", "url", "authority", "detail"}


def test_a_checklist_tool_may_never_sit_beside_a_designated_checklist_source() -> None:
    """A tool is named because no page listed the documents. Designating a source anyway means the
    list came from somewhere that is not a checklist, which is the failure this project exists to
    prevent — `validate_absent_checklist` blocks it from the other side."""

    payload = plan_payload(
        official_tools=[
            {
                "topic": "document_checklist",
                "url": "https://www.gov.uk/check-uk-visa",
                "authority": "United Kingdom authority (www.gov.uk)",
                "detail": "lists the documents by asking questions",
            }
        ],
        application_document_source_ids=["official-source"],
    )

    with pytest.raises(ValidationError, match="cannot also designate a checklist source"):
        VisaPlan.model_validate(payload)


def test_a_tool_for_another_topic_leaves_the_visa_decision_alone() -> None:
    """Only `visa_decision` is load-bearing. A questionnaire holding the fees adds a link to a plan
    that stands on its own, and must not force the decision to unknown."""

    plan = VisaPlan.model_validate(
        plan_payload(
            visa_required=True,
            visa_type="Standard Visitor visa",
            status="partial",
            official_tools=[
                {
                    "topic": "fees",
                    "url": "https://www.gov.uk/check-uk-visa",
                    "authority": "United Kingdom authority (www.gov.uk)",
                    "detail": "works out the fee by asking questions",
                }
            ],
        )
    )

    assert plan.visa_required is True
    assert plan.decision_tools == []
