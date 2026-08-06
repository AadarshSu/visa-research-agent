"""Strict domain models shared by the API and future research workflow."""

from datetime import date, datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

RequirementCategory = Literal["mandatory", "conditional", "recommended"]
RouteType = Literal["national", "schengen_member"]
ImplementationStatus = Literal["planned", "available"]
SourceKind = Literal[
    "immigration_authority",
    "foreign_ministry",
    "embassy_or_high_commission",
    "official_application_provider",
]
SourcePass = Literal["primary", "follow_up"]


class StrictModel(BaseModel):
    """Base model that rejects unexpected data instead of silently discarding it."""

    model_config = ConfigDict(extra="forbid")


def _require_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value


class TravellerProfile(StrictModel):
    """The deliberately fixed, non-sensitive traveller details used by the MVP."""

    passport_nationality: str = Field(min_length=1)
    passport_type: Literal["ordinary"]
    country_of_residence: str = Field(min_length=1)
    city_of_residence: str = Field(min_length=1)
    uk_immigration_status: str = Field(min_length=1)
    uk_permission_expiry: date
    travel_purpose: Literal["tourism"]


class ConfiguredSource(StrictModel):
    """An approved official starting point for one destination."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    title: str = Field(min_length=1)
    url: AnyHttpUrl
    authority: str = Field(min_length=1)
    kind: SourceKind
    research_pass: SourcePass = "primary"


class DestinationConfig(StrictModel):
    """Country-specific research configuration."""

    slug: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    display_name: str = Field(min_length=1)
    route_type: RouteType
    schengen_member: str | None = None
    implementation_status: ImplementationStatus = "planned"
    sources: list[ConfiguredSource] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_route(self) -> "DestinationConfig":
        if self.route_type == "schengen_member" and not self.schengen_member:
            raise ValueError("a Schengen member route must identify its member country")
        if self.route_type == "national" and self.schengen_member is not None:
            raise ValueError("a national route cannot set schengen_member")
        return self


class DestinationRegistry(StrictModel):
    """Validated top-level destination configuration file."""

    schema_version: Literal[1]
    destinations: list[DestinationConfig] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_identifiers(self) -> "DestinationRegistry":
        slugs = [destination.slug for destination in self.destinations]
        if len(slugs) != len(set(slugs)):
            raise ValueError("destination slugs must be unique")

        source_ids = [
            source.source_id for destination in self.destinations for source in destination.sources
        ]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source IDs must be unique across the registry")
        return self

    def get(self, slug: str) -> DestinationConfig | None:
        normalized_slug = slug.strip().lower()
        return next(
            (
                destination
                for destination in self.destinations
                if destination.slug == normalized_slug
            ),
            None,
        )


class SourceReference(StrictModel):
    """A source actually consulted during a research run."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    title: str = Field(min_length=1)
    url: AnyHttpUrl
    authority: str = Field(min_length=1)
    retrieved_at: datetime
    supporting_excerpt: str | None = None

    _validate_retrieved_at = field_validator("retrieved_at")(_require_aware_datetime)


class FetchedSource(StrictModel):
    """Cleaned source material and retrieval metadata passed to extraction."""

    source: SourceReference
    content: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    from_cache: bool = False


class VisaRequirement(StrictModel):
    """One evidence-backed document requirement."""

    name: str = Field(min_length=1)
    category: RequirementCategory
    description: str = Field(min_length=1)
    reason_it_applies: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)


class ApplicationLocation(StrictModel):
    """Where and how the traveller should apply."""

    authority: str = Field(min_length=1)
    application_method: str = Field(min_length=1)
    location: str | None = None
    application_url: AnyHttpUrl


class VisaPlan(StrictModel):
    """Final source-backed output returned by the workflow and API."""

    destination: str = Field(min_length=1)
    visa_required: bool | None
    visa_type: str | None
    explanation: str = Field(min_length=1)
    where_to_apply: ApplicationLocation | None
    requirements: list[VisaRequirement]
    application_steps: list[str]
    sources: list[SourceReference]
    unresolved_questions: list[str]
    conflicts: list[str]
    last_checked: datetime

    _validate_last_checked = field_validator("last_checked")(_require_aware_datetime)

    @model_validator(mode="after")
    def validate_requirement_sources(self) -> "VisaPlan":
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source IDs in a visa plan must be unique")

        unknown_ids = {
            source_id
            for requirement in self.requirements
            for source_id in requirement.source_ids
            if source_id not in source_ids
        }
        if unknown_ids:
            unknown = ", ".join(sorted(unknown_ids))
            raise ValueError(f"requirements cite unknown source IDs: {unknown}")
        return self
