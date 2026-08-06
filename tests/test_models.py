from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from visa_research_agent.domain.models import SourceReference, VisaPlan, VisaRequirement


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


def test_requirement_category_is_validated() -> None:
    with pytest.raises(ValidationError):
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
            where_to_apply=None,
            requirements=[
                VisaRequirement(
                    name="Passport",
                    category="mandatory",
                    description="A passport is requested.",
                    reason_it_applies="The traveller uses an ordinary passport.",
                    source_ids=["missing-source"],
                )
            ],
            application_steps=[],
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
        )
