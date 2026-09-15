"""What the plan-writing call cost, one line per call and one file per day.

**Why this exists (DECISIONS entries 164 and 165).** Selection and role adjudication are recorded in
a corridor's recall log, which a resolution writes. The call that writes the plan is not part of a
resolution: it runs on every web request, after a fresh resolution or after one served from the
three-week corridor store, where it is the whole of the model bill. So it never reached a recall
log, and `visa-discover corridor`, which every corridor cost in this project was measured with,
never makes it at all.

**Appended, where the recall log overwrites.** A recall log answers "what did the last run of this
corridor do", so the newest run replaces it. This answers "what did the plan calls cost", which is a
sum — a corridor served twenty times is twenty calls — and the figure it exists to be checked
against, the provider's own bill, is kept per day. So: one JSON line per call, one file per UTC day.

**A diagnostic, like the recall log.** Nothing reads it back at runtime and no decision depends on
it, so a write that fails is dropped rather than allowed to cost a traveller their plan.
"""

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field, field_validator

from visa_research_agent.discovery.recall_log import ModelCall
from visa_research_agent.domain.models import StrictModel


class PlanCallRecord(StrictModel):
    """One plan-writing call: which corridor it was for, when, and what the provider billed."""

    schema_version: Literal[1] = 1
    corridor_key: str = Field(min_length=1)
    recorded_at: datetime
    call: ModelCall

    @field_validator("recorded_at")
    @classmethod
    def validate_recorded_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("recorded_at must include a timezone")
        return value


class ModelUsageLog(Protocol):
    def write(self, record: PlanCallRecord) -> None:
        """Keep one call's record beside the others made the same day."""
        ...


class FileModelUsageLog:
    """`plan-calls-YYYY-MM-DD.jsonl`, one per UTC day, with a line appended per call.

    Each record is one write of one line to a file opened for appending, so two requests finishing
    together add two lines rather than one overwriting the other.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def path_for(self, day: date) -> Path:
        return self.directory / f"plan-calls-{day.isoformat()}.jsonl"

    def write(self, record: PlanCallRecord) -> None:
        path = self.path_for(record.recorded_at.astimezone(UTC).date())
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record.model_dump(mode="json"), ensure_ascii=False) + "\n"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def read(self, day: date) -> list[PlanCallRecord]:
        """Every call recorded on one UTC day, in the order it was written."""

        try:
            lines = self.path_for(day).read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return []
        return [PlanCallRecord.model_validate_json(line) for line in lines if line.strip()]
