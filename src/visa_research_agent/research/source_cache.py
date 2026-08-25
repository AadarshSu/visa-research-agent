"""Filesystem cache holding retrieved official-source text and its provenance."""

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator

from visa_research_agent.domain.models import (
    MAXIMUM_HTTP_STATUS,
    MINIMUM_HTTP_STATUS,
    StrictModel,
)
from visa_research_agent.research.errors import LiveSourceError


class CachedSource(StrictModel):
    """One retrieval, kept with the validators needed to revalidate it cheaply later."""

    schema_version: Literal[1] = 1
    url: str = Field(min_length=1)
    final_url: str = Field(min_length=1)
    fetched_at: datetime
    content: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    http_status: int = Field(ge=MINIMUM_HTTP_STATUS, le=MAXIMUM_HTTP_STATUS)
    etag: str | None = None
    last_modified: str | None = None

    @field_validator("fetched_at")
    @classmethod
    def validate_fetched_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("fetched_at must include a timezone")
        return value

    def age_hours(self, now: datetime) -> float:
        """Hours between the recorded retrieval and `now`, never negative."""

        return max((now - self.fetched_at).total_seconds() / 3600, 0.0)


class FileSourceCache:
    """Store one JSON document per source URL under a local cache directory."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def _path(self, url: str) -> Path:
        return self.directory / f"{sha256(url.encode()).hexdigest()}.json"

    def load(self, url: str) -> CachedSource | None:
        """Return the cached retrieval for a URL, treating unreadable entries as a miss."""

        path = self._path(url)
        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise LiveSourceError("The source cache could not be read") from exc

        try:
            entry = CachedSource.model_validate_json(raw)
        except ValidationError:
            return None
        # A digest collision or a hand-edited file must never be served as another URL.
        return entry if entry.url == url else None

    def store(self, entry: CachedSource) -> None:
        """Write an entry atomically so an interrupted run cannot leave partial evidence."""

        path = self._path(entry.url)
        temporary_path = path.with_name(f"{path.name}.tmp")
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(entry.model_dump_json(), encoding="utf-8")
            temporary_path.replace(path)
        except OSError as exc:
            raise LiveSourceError("The source cache could not be written") from exc
