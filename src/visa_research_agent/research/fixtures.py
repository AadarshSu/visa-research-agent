"""Offline fixture source loading and deterministic structured extraction."""

from datetime import datetime
from hashlib import sha256
from importlib.resources import files
from typing import Any, Literal

import yaml
from pydantic import Field, model_validator

from visa_research_agent.config.settings import settings
from visa_research_agent.domain.models import (
    ApplicationLocation,
    DestinationConfig,
    FetchedSource,
    RetrievalReport,
    SourceReference,
    StrictModel,
    TravellerProfile,
    VisaPlan,
    VisaPlanDraft,
)
from visa_research_agent.research.errors import FixtureDataError
from visa_research_agent.research.outcomes import require_load_bearing_sources, resolve_plan_status


class FixtureSourceEntry(StrictModel):
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    fixture_file: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*\.txt$")
    supporting_excerpt: str = Field(min_length=1, max_length=300)


class FixtureManifest(StrictModel):
    schema_version: Literal[1]
    destination: str
    captured_at: datetime
    sources: list[FixtureSourceEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_manifest(self) -> "FixtureManifest":
        if self.captured_at.tzinfo is None or self.captured_at.utcoffset() is None:
            raise ValueError("captured_at must include a timezone")
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("fixture source IDs must be unique")
        return self


def _fixture_directory(destination_slug: str) -> Any:
    return files("visa_research_agent.fixtures").joinpath(destination_slug)


def _load_yaml(resource: Any) -> Any:
    try:
        return yaml.safe_load(resource.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, yaml.YAMLError) as exc:
        raise FixtureDataError(f"Unable to load fixture data: {resource.name}") from exc


class FixtureSourceFetcher:
    """Load source snapshots from package data without using the network."""

    def __init__(self, maximum_characters: int | None = None) -> None:
        self.maximum_characters = maximum_characters or settings.maximum_fixture_characters

    async def fetch(self, destination: DestinationConfig) -> RetrievalReport:
        fixture_directory = _fixture_directory(destination.slug)
        manifest = FixtureManifest.model_validate(
            _load_yaml(fixture_directory.joinpath("manifest.yaml"))
        )
        if manifest.destination != destination.slug:
            raise FixtureDataError("Fixture destination does not match configured destination")

        configured_sources = {
            source.source_id: source
            for source in destination.sources
            if source.research_pass == "primary"
        }
        fixture_entries = {source.source_id: source for source in manifest.sources}
        if configured_sources.keys() != fixture_entries.keys():
            raise FixtureDataError("Fixture sources do not match configured primary sources")

        fetched_sources: list[FetchedSource] = []
        for source_id, configured_source in configured_sources.items():
            entry = fixture_entries[source_id]
            try:
                content = fixture_directory.joinpath(entry.fixture_file).read_text(encoding="utf-8")
            except (FileNotFoundError, OSError) as exc:
                raise FixtureDataError(f"Fixture content is missing for {source_id}") from exc

            cleaned_content = content.strip()
            if not cleaned_content:
                raise FixtureDataError(f"Fixture content is empty for {source_id}")
            if len(cleaned_content) > self.maximum_characters:
                raise FixtureDataError(f"Fixture content exceeds the size limit for {source_id}")

            source_reference = SourceReference(
                source_id=configured_source.source_id,
                title=configured_source.title,
                url=configured_source.url,
                authority=configured_source.authority,
                retrieved_at=manifest.captured_at,
                supporting_excerpt=entry.supporting_excerpt,
            )
            fetched_sources.append(
                FetchedSource(
                    source=source_reference,
                    content=cleaned_content,
                    content_hash=sha256(cleaned_content.encode()).hexdigest(),
                    from_cache=True,
                )
            )
        # Offline snapshots are complete by construction, so a fixture run never reports gaps.
        return RetrievalReport(fetched=fetched_sources, failures=[])


class FixtureVisaPlanExtractor:
    """Deterministic fake model that returns validated, evidence-linked fixture output."""

    async def extract(
        self,
        destination: DestinationConfig,
        traveller_profile: TravellerProfile,
        report: RetrievalReport,
    ) -> VisaPlan:
        if traveller_profile.passport_nationality != "IN":
            raise FixtureDataError("The Singapore fixture only supports the fixed Indian profile")
        if traveller_profile.travel_purpose != "tourism":
            raise FixtureDataError("The Singapore fixture only supports tourism")
        fetched_sources = report.fetched
        if not fetched_sources:
            raise FixtureDataError("Structured extraction requires at least one source")
        require_load_bearing_sources(destination, report)

        fixture_directory = _fixture_directory(destination.slug)
        template = VisaPlanDraft.model_validate(_load_yaml(fixture_directory.joinpath("plan.yaml")))
        if template.destination != destination.display_name:
            raise FixtureDataError("Fixture plan destination does not match configuration")

        application_source_ids = set(destination.application_document_source_ids)
        if not application_source_ids:
            raise FixtureDataError("No application document sources are configured")
        if any(
            not application_source_ids.intersection(requirement.source_ids)
            for requirement in template.requirements
        ):
            raise FixtureDataError("Fixture checklist contains a non-application document source")

        references = [fetched_source.source for fetched_source in fetched_sources]
        last_checked = max(reference.retrieved_at for reference in references)
        where_to_apply = (
            ApplicationLocation.model_validate(template.where_to_apply.model_dump())
            if template.where_to_apply is not None
            else None
        )
        return VisaPlan(
            destination=template.destination,
            visa_required=template.visa_required,
            visa_type=template.visa_type,
            explanation=template.explanation,
            decision_source_ids=template.decision_source_ids,
            where_to_apply=where_to_apply,
            requirements=template.requirements,
            application_document_source_ids=destination.application_document_source_ids,
            application_steps=template.application_steps,
            sources=references,
            unresolved_questions=template.unresolved_questions,
            conflicts=template.conflicts,
            last_checked=last_checked,
            status=resolve_plan_status(report),
            unavailable_sources=report.failures,
        )
