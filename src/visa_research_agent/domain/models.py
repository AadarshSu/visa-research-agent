"""Strict domain models shared by the API and future research workflow."""

from datetime import date, datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

RouteType = Literal["national", "schengen_member"]
ImplementationStatus = Literal["planned", "available"]
SourceMode = Literal["fixtures", "live"]
ExtractionMode = Literal["fixture", "openai"]
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
    application_document_source_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_route(self) -> "DestinationConfig":
        if self.route_type == "schengen_member" and not self.schengen_member:
            raise ValueError("a Schengen member route must identify its member country")
        if self.route_type == "national" and self.schengen_member is not None:
            raise ValueError("a national route cannot set schengen_member")

        source_ids = {source.source_id for source in self.sources}
        if len(self.application_document_source_ids) != len(
            set(self.application_document_source_ids)
        ):
            raise ValueError("application document source IDs must be unique")

        unknown_source_ids = set(self.application_document_source_ids).difference(source_ids)
        if unknown_source_ids:
            unknown = ", ".join(sorted(unknown_source_ids))
            raise ValueError(f"application document sources contain unknown IDs: {unknown}")
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


class RuntimePolicy(StrictModel):
    """Version-controlled policy for what the agent may contact and how old evidence may be.

    These choices are reviewable rather than environment-local: they decide whether government
    websites are contacted, whether a paid model is called, and when stale guidance is refused.
    """

    schema_version: Literal[1]
    source_mode: SourceMode
    extraction_mode: ExtractionMode
    source_cache_ttl_hours: float = Field(gt=0)
    source_maximum_stale_hours: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_freshness_window(self) -> "RuntimePolicy":
        if self.source_maximum_stale_hours < self.source_cache_ttl_hours:
            raise ValueError("the stale ceiling cannot be shorter than the cache TTL")
        return self


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
    is_stale: bool = False
    """True when a refresh failed and cached evidence was served past its freshness window."""


class VisaRequirement(StrictModel):
    """One evidence-backed document requirement."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    reason_it_applies: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)


class ApplicationLocation(StrictModel):
    """Where and how the traveller should apply."""

    authority: str = Field(min_length=1)
    application_method: str = Field(min_length=1)
    location: str | None = None
    application_url: AnyHttpUrl
    source_ids: list[str] = Field(min_length=1)


class ApplicationLocationDraft(StrictModel):
    """Model-facing application details before the URL is validated by the app."""

    authority: str = Field(min_length=1)
    application_method: str = Field(min_length=1)
    location: str | None
    application_url: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)


class ApplicationStep(StrictModel):
    """One evidence-backed action in the traveller's ordered application timeline."""

    title: str = Field(min_length=3, max_length=80)
    action: str = Field(min_length=3, max_length=320)
    timing: str = Field(min_length=3, max_length=160)
    source_ids: list[str] = Field(min_length=1)
    link_target: Literal["application_route", "source", "none"]
    link_source_id: str | None

    @model_validator(mode="after")
    def validate_link_target(self) -> "ApplicationStep":
        if self.link_target == "source":
            if self.link_source_id is None:
                raise ValueError("a source step link requires link_source_id")
            if self.link_source_id not in self.source_ids:
                raise ValueError("link_source_id must also appear in source_ids")
        elif self.link_source_id is not None:
            raise ValueError("link_source_id is only valid for a source step link")
        return self


class VisaPlanDraft(StrictModel):
    """Structured extraction result before trusted source metadata is attached."""

    destination: str = Field(min_length=1)
    visa_required: bool | None
    visa_type: str | None
    explanation: str = Field(min_length=1)
    decision_source_ids: list[str] = Field(min_length=1)
    where_to_apply: ApplicationLocationDraft | None
    requirements: list[VisaRequirement]
    application_steps: list[ApplicationStep] = Field(min_length=4, max_length=8)
    unresolved_questions: list[str]
    conflicts: list[str]


class VisaPlan(StrictModel):
    """Final source-backed output returned by the workflow and API."""

    destination: str = Field(min_length=1)
    visa_required: bool | None
    visa_type: str | None
    explanation: str = Field(min_length=1)
    decision_source_ids: list[str] = Field(min_length=1)
    where_to_apply: ApplicationLocation | None
    requirements: list[VisaRequirement]
    application_document_source_ids: list[str] = Field(min_length=1)
    application_steps: list[ApplicationStep] = Field(min_length=4, max_length=8)
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

        cited_source_ids = set(self.decision_source_ids)
        cited_source_ids.update(
            source_id for requirement in self.requirements for source_id in requirement.source_ids
        )
        cited_source_ids.update(self.application_document_source_ids)
        cited_source_ids.update(
            source_id for step in self.application_steps for source_id in step.source_ids
        )
        if self.where_to_apply is not None:
            cited_source_ids.update(self.where_to_apply.source_ids)

        if self.where_to_apply is None and any(
            step.link_target == "application_route" for step in self.application_steps
        ):
            raise ValueError("application-route step links require an application location")

        unknown_ids = cited_source_ids.difference(source_ids)
        if unknown_ids:
            unknown = ", ".join(sorted(unknown_ids))
            raise ValueError(f"visa plan cites unknown source IDs: {unknown}")
        return self
