"""Keeping a resolved corridor on disk so a request does not re-search the web.

Resolving a corridor costs a crawl, twenty-five fetches and a model call, plus up to fifteen
searches — three per trusted domain. (It cost a bootstrap too until entry 38 moved that to a
committed registry, and ten fetches until entry 40 widened the shortlist.) That is fine as a
deliberate command and far too much for every request, so the result is cached.

A resolved corridor is **not** evidence and has a different lifetime from it. The evidence cache in
`research/source_cache.py` measures freshness in hours, because a government page can change any
day. Which *pages* answer a corridor changes on the timescale of site redesigns, so this measures
weeks. Both still expire: a corridor is re-resolved eventually, and its pages are re-fetched under
their own, much shorter, TTL every time a plan is produced.

Deliberately a file store rather than an `lru_cache`. A process-lifetime memo would serve a corridor
resolved weeks ago for as long as the server stayed up, with no way to notice.
"""

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Literal

from pydantic import Field, ValidationError, field_validator

from visa_research_agent.discovery.models import Corridor, ResolvedCorridor
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.research.errors import VisaResearchError


class CorridorStoreError(VisaResearchError):
    """Raised when the corridor store cannot be read or written safely."""


class StoredCorridor(StrictModel):
    """One resolved corridor, with the domains that were trusted to produce it."""

    schema_version: Literal[1] = 1
    resolved: ResolvedCorridor
    trusted_domains: list[str] = Field(default_factory=list)
    withheld_domains: dict[str, str] = Field(default_factory=dict)
    stored_at: datetime

    @field_validator("stored_at")
    @classmethod
    def validate_stored_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("stored_at must include a timezone")
        return value

    def age_hours(self, now: datetime) -> float:
        """Hours since this corridor was resolved, never negative."""

        return max((now - self.stored_at).total_seconds() / 3600, 0.0)


class FileCorridorStore:
    """One JSON document per corridor, written atomically."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _path(self, corridor: Corridor) -> Path:
        return self.directory / f"{sha256(corridor.key.encode()).hexdigest()}.json"

    def load(self, corridor: Corridor) -> StoredCorridor | None:
        """Return a stored corridor, treating anything unreadable or outdated as a miss."""

        try:
            raw = self._path(corridor).read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise CorridorStoreError("The corridor store could not be read") from exc

        try:
            return StoredCorridor.model_validate_json(raw)
        except ValidationError:
            # A store written by an older schema is a miss, not a crash: re-resolving is always
            # safe, and serving something whose shape is no longer understood is not.
            return None

    def store(
        self,
        corridor: Corridor,
        resolved: ResolvedCorridor,
        trusted_domains: list[str],
        withheld_domains: dict[str, str],
        now: datetime,
    ) -> StoredCorridor:
        entry = StoredCorridor(
            resolved=resolved,
            trusted_domains=trusted_domains,
            withheld_domains=withheld_domains,
            stored_at=now,
        )
        path = self._path(corridor)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Written to a neighbouring temporary file and moved, so a crash mid-write cannot
            # leave a half-written corridor that later reads as valid.
            with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                json.dump(entry.model_dump(mode="json"), handle, ensure_ascii=False)
                temporary = Path(handle.name)
            temporary.replace(path)
        except OSError as exc:
            raise CorridorStoreError("The corridor store could not be written") from exc
        return entry
