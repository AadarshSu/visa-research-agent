from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from visa_research_agent.domain.models import (
    ApplicationStep,
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
            conflicts=[],
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
                "conflicts": [],
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
                "conflicts": [],
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
        "conflicts": [],
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
