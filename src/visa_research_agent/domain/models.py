"""Strict domain models shared by the API and future research workflow."""

from datetime import date, datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator

from visa_research_agent.domain.trust import host_is_within, host_of, is_bare_public_suffix

RouteType = Literal["national", "schengen_member"]
ImplementationStatus = Literal["planned", "available"]
SourceMode = Literal["fixtures", "live"]
ExtractionMode = Literal["fixture", "openai"]
# Whether a real browser may be started for pages that return nothing readable. Kept as policy
# rather than tuning because it changes how government sites are contacted.
RenderMode = Literal["never", "on_demand"]
# Which decider assigns roles during discovery. `heuristic` is deterministic, free and offline;
# `model` asks one bounded question over pages already fetched and trusted.
DiscoveryDecider = Literal["heuristic", "model"]
# Why a source produced no usable evidence. Unreachable and unusable are kept apart because they
# need different remedies: one is a transient site problem, the other needs a different retriever.
FailureOutcome = Literal["untrusted", "unreachable", "unusable"]
PlanStatus = Literal["verified", "partial"]
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


class AppointedProvider(StrictModel):
    """A non-government domain authorised by a named official page.

    Appointed providers cannot pass domain trust by design, so their authority comes only from an
    official source that names them for this destination.
    """

    domain: str = Field(min_length=1)
    appointed_by: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")


class DestinationConfig(StrictModel):
    """Country-specific research configuration."""

    slug: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    display_name: str = Field(min_length=1)
    route_type: RouteType
    schengen_member: str | None = None
    implementation_status: ImplementationStatus = "planned"
    sources: list[ConfiguredSource] = Field(default_factory=list)
    application_document_source_ids: list[str] = Field(default_factory=list)
    trusted_domains: list[str] = Field(default_factory=list)
    appointed_providers: list[AppointedProvider] = Field(default_factory=list)
    required_source_ids: list[str] = Field(default_factory=list)

    @property
    def load_bearing_source_ids(self) -> list[str]:
        """Sources the plan cannot be produced without: the checklist, plus anything else required.

        A union, not a fallback. This used to be `required_source_ids or
        application_document_source_ids`, so naming any required source silently discarded the
        checklist requirement — a destination could declare a checklist and still produce a plan
        without it. Order is preserved so the reported reason names the checklist first.
        """

        combined = [*self.application_document_source_ids, *self.required_source_ids]
        return list(dict.fromkeys(combined))

    def trusts_host(self, host: str) -> bool:
        """True when a host is an approved authority domain or an appointed provider domain."""

        return host_is_within(host, self.trusted_domains) or host_is_within(
            host, [provider.domain for provider in self.appointed_providers]
        )

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

        unknown_required_ids = set(self.required_source_ids).difference(source_ids)
        if unknown_required_ids:
            unknown = ", ".join(sorted(unknown_required_ids))
            raise ValueError(f"required sources contain unknown IDs: {unknown}")

        for domain in self.trusted_domains:
            if is_bare_public_suffix(domain):
                raise ValueError(
                    f"trusted domain {domain} is a public suffix and would trust every site "
                    "beneath it"
                )

        for provider in self.appointed_providers:
            if provider.appointed_by not in source_ids:
                raise ValueError(
                    f"appointed provider {provider.domain} names an unknown appointing source: "
                    f"{provider.appointed_by}"
                )

        # Every hand-configured URL must already satisfy the destination's own trust rules, so a
        # mistake in review fails at load time rather than during a research run.
        if self.sources and not self.trusted_domains:
            raise ValueError("a destination with sources must declare its trusted domains")
        untrusted = sorted(
            {
                str(source.url)
                for source in self.sources
                if not self.trusts_host(host_of(str(source.url)))
            }
        )
        if untrusted:
            listed = ", ".join(untrusted)
            raise ValueError(f"configured sources are not on a trusted domain: {listed}")
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
    render_mode: RenderMode = "never"
    discovery_decider: DiscoveryDecider = "heuristic"
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
    is_stale: bool = False
    """True when a refresh failed and cached text was served past its freshness window."""

    _validate_retrieved_at = field_validator("retrieved_at")(_require_aware_datetime)


class FetchedSource(StrictModel):
    """Cleaned source material and retrieval metadata passed to extraction."""

    source: SourceReference
    content: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    from_cache: bool = False


class SourceFailure(StrictModel):
    """A configured source that produced no usable evidence, and why."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    title: str = Field(min_length=1)
    authority: str = Field(min_length=1)
    outcome: FailureOutcome
    detail: str = Field(min_length=1)
    """A safe summary of the cause. Never carries retrieved page text."""

    attempted_url: AnyHttpUrl
    final_url: AnyHttpUrl | None = None
    """Where the request actually landed, recorded when a redirect left the trusted domains."""


class RetrievalReport(StrictModel):
    """Everything one retrieval pass produced: usable evidence and explained gaps."""

    fetched: list[FetchedSource] = Field(default_factory=list)
    failures: list[SourceFailure] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_source_ids(self) -> "RetrievalReport":
        source_ids = [item.source.source_id for item in self.fetched] + [
            failure.source_id for failure in self.failures
        ]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("a retrieval report cannot report the same source twice")
        return self


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
    application_document_source_ids: list[str]
    """May be empty: some authorities publish no checklist. See `validate_absent_checklist`."""
    application_steps: list[ApplicationStep] = Field(min_length=4, max_length=8)
    sources: list[SourceReference]
    unresolved_questions: list[str]
    conflicts: list[str]
    last_checked: datetime
    status: PlanStatus
    unavailable_sources: list[SourceFailure] = Field(default_factory=list)

    _validate_last_checked = field_validator("last_checked")(_require_aware_datetime)

    @model_validator(mode="after")
    def validate_status_matches_evidence(self) -> "VisaPlan":
        """A verified plan must have complete, current evidence behind every source."""

        if self.status == "verified":
            if self.unavailable_sources:
                raise ValueError("a verified plan cannot report unavailable sources")
            if any(source.is_stale for source in self.sources):
                raise ValueError("a verified plan cannot rest on stale evidence")
        return self

    @model_validator(mode="after")
    def validate_absent_checklist(self) -> "VisaPlan":
        """With no document source, a plan may state the gap but never fill it.

        This is the guard that makes a checklist-less corridor safe to serve. Without a designated
        document source there is nothing a requirement could honestly cite, so listing one means it
        was inferred from a page that is not a checklist — an eligibility rule or an application
        form read as though it were guidance. That is the single most damaging output this project
        can produce, so it is refused structurally rather than asked for politely in the prompt.
        """

        if self.application_document_source_ids:
            return self
        if self.requirements:
            raise ValueError(
                "a plan with no document checklist source cannot list document requirements"
            )
        if not self.unresolved_questions:
            raise ValueError(
                "a plan with no document checklist source must record what could not be answered"
            )
        return self

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
