"""Strict models for the discovery pipeline.

The important one is `ResolvedCorridor`: it is machine-produced, so its conversion back into a
`DestinationConfig` deliberately re-runs that model's validators. A corridor whose URLs drifted off
the approved domains cannot be turned into something the retriever would fetch.
"""

from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator, model_validator

from visa_research_agent.domain.models import (
    ConfiguredSource,
    DestinationConfig,
    SourceKind,
    SourcePass,
    StrictModel,
)

DiscoveryRole = Literal[
    "visa_decision",
    "document_checklist",
    "application_route",
    "fees",
    "processing_times",
    "general_entry",
    "irrelevant",
]
TravelPurpose = Literal["tourism", "business", "study", "transit"]
DecidedBy = Literal["heuristic", "model"]

# The roles a corridor cannot be considered resolved without. Everything else is useful context.
#
# `document_checklist` is deliberately **not** here. Some authorities publish no checklist at all:
# Vietnam states its e-visa requirements as upload fields inside the application form, so there is
# no page to find, and refusing the corridor forever would be refusing reality.
#
# This is safe only because the absence is carried through rather than papered over. A plan built
# without a document source may not contain document requirements — `VisaPlan` enforces that — and
# must say so in its unresolved questions. The model is never left to infer a checklist from a page
# that is not one. Removing that enforcement re-creates the wrong-checklist failure this project
# exists to prevent; see DECISIONS.md entry 14.
LOAD_BEARING_ROLES: tuple[DiscoveryRole, ...] = ("visa_decision",)

# Roles whose absence must be named in the result even when it no longer refuses the corridor.
# A missing checklist stops being fatal, but it must never become invisible: it changes what the
# traveller can be told, so it is reported and moves the command's exit code from 0 to 1.
REPORTED_ROLES: tuple[DiscoveryRole, ...] = (*LOAD_BEARING_ROLES, "document_checklist")

# Display and output order, so proposals diff cleanly between runs.
ROLE_ORDER: tuple[DiscoveryRole, ...] = (
    "visa_decision",
    "document_checklist",
    "application_route",
    "fees",
    "processing_times",
    "general_entry",
)

COUNTRY_CODE_PATTERN = r"^[A-Z]{2}$"


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value


class Corridor(StrictModel):
    """One traveller's route: who they are, where from, where to, and why.

    The correct pages depend on all four, which is why a destination alone cannot identify them.
    """

    destination_slug: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    passport_nationality: str = Field(pattern=COUNTRY_CODE_PATTERN)
    applying_from: str = Field(pattern=COUNTRY_CODE_PATTERN)
    purpose: TravelPurpose = "tourism"

    @property
    def key(self) -> str:
        """A stable identifier for caching, e.g. "japan/IN/GB/tourism"."""

        return (
            f"{self.destination_slug}/{self.passport_nationality}/"
            f"{self.applying_from}/{self.purpose}"
        )


class SearchResult(StrictModel):
    """One result from the search provider, before any trust decision has been made."""

    url: str = Field(min_length=1)
    title: str = ""
    snippet: str = ""
    query: str = Field(min_length=1)
    rank: int = Field(ge=0)


class PageLink(StrictModel):
    """A link found while crawling, kept with the text that led to it.

    The anchor text is often the only signal a page has: Japan's tourism checklist sits at
    "index_000070.html" and is identifiable solely by being labelled "Temporary Visitor Visa".
    """

    url: str = Field(min_length=1)
    text: str = Field(default="", max_length=300)
    heading: str = Field(default="", max_length=300)
    depth: int = Field(ge=0)
    discovered_from: str = Field(default="", max_length=2000)


class RoleScores(StrictModel):
    """Scores per role, with the reasons that produced them so a decision can be explained."""

    scores: dict[str, float] = Field(default_factory=dict)
    signals: dict[str, list[str]] = Field(default_factory=dict)

    def score_for(self, role: DiscoveryRole) -> float:
        return self.scores.get(role, 0.0)

    def best(self) -> tuple[DiscoveryRole, float]:
        """The highest-scoring role, resolving ties by the fixed role order for determinism."""

        best_role: DiscoveryRole = "irrelevant"
        best_score = 0.0
        for role in ROLE_ORDER:
            score = self.scores.get(role, 0.0)
            if score > best_score:
                best_role, best_score = role, score
        return best_role, best_score

    def runner_up(self, winning: DiscoveryRole) -> float:
        others = [score for role, score in self.scores.items() if role != winning]
        return max(others) if others else 0.0


class CandidatePage(StrictModel):
    """A page under consideration, with everything known about it so far."""

    link: PageLink
    link_scores: RoleScores = Field(default_factory=RoleScores)
    body_scores: RoleScores | None = None
    title: str | None = None
    content_hash: str | None = None
    found_by: Literal["search", "crawl"] = "crawl"

    def combined(self, role: DiscoveryRole) -> float:
        """Blend link and body evidence, weighting the page's own text more heavily."""

        link_score = self.link_scores.score_for(role)
        if self.body_scores is None:
            return link_score
        return 0.4 * link_score + 0.6 * self.body_scores.score_for(role)


class ResolvedSource(StrictModel):
    """A page discovery selected, with the role it fills and why."""

    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    title: str = Field(min_length=1)
    url: AnyHttpUrl
    authority: str = Field(min_length=1)
    kind: SourceKind
    research_pass: SourcePass = "primary"
    roles: list[DiscoveryRole] = Field(min_length=1)
    """Every role this page fills. One page often serves several: Singapore's per-nationality
    page both establishes whether a visa is needed and lists the documents to bring, and its
    hand-written configuration names it for both."""

    score: float
    decided_by: DecidedBy = "heuristic"
    signals: list[str] = Field(default_factory=list)

    def to_configured_source(self) -> ConfiguredSource:
        """Drop the discovery-only fields, leaving what the registry understands."""

        return ConfiguredSource(
            source_id=self.source_id,
            title=self.title,
            url=self.url,
            authority=self.authority,
            kind=self.kind,
            research_pass=self.research_pass,
        )


class ResolvedCorridor(StrictModel):
    """The sources discovery selected for one corridor, plus what it could not resolve."""

    schema_version: Literal[1] = 1
    corridor: Corridor
    resolved_at: datetime
    sources: list[ResolvedSource] = Field(default_factory=list)
    unresolved_roles: list[DiscoveryRole] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)
    model_calls: int = 0
    pages_fetched: int = 0

    _validate_resolved_at = field_validator("resolved_at")(_require_aware)

    @model_validator(mode="after")
    def validate_unique_source_ids(self) -> "ResolvedCorridor":
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("a resolved corridor cannot list the same source twice")
        return self

    @property
    def is_usable(self) -> bool:
        """True when every load-bearing role was filled.

        A corridor missing its checklist is refused rather than served, because a plan without one
        cannot be produced and a substitute page would be worse than nothing.
        """

        filled = {role for source in self.sources for role in source.roles}
        return all(role in filled for role in LOAD_BEARING_ROLES)

    def source_ids_for(self, role: DiscoveryRole) -> list[str]:
        return [source.source_id for source in self.sources if role in source.roles]

    def age_hours(self, now: datetime) -> float:
        return max((now - self.resolved_at).total_seconds() / 3600, 0.0)

    def to_destination_config(self, destination: DestinationConfig) -> DestinationConfig:
        """Fold discovered sources into a destination, re-running every trust rule.

        Validation is deliberately not bypassed: this is the point at which a machine-chosen page
        must prove it still sits on a human-approved domain.
        """

        checklist_ids = self.source_ids_for("document_checklist")
        required_ids = checklist_ids + [
            source_id
            for source_id in self.source_ids_for("visa_decision")
            if source_id not in checklist_ids
        ]
        payload = destination.model_dump(mode="json")
        payload["sources"] = [
            source.to_configured_source().model_dump(mode="json") for source in self.sources
        ]
        payload["application_document_source_ids"] = checklist_ids
        payload["required_source_ids"] = required_ids
        # Keep only the appointed providers whose authorising page is still present. A provider
        # whose appointing source is gone is no longer authorised, and saying otherwise would
        # invent permission that no official page grants.
        source_ids = {source.source_id for source in self.sources}
        payload["appointed_providers"] = [
            provider
            for provider in payload.get("appointed_providers", [])
            if provider.get("appointed_by") in source_ids
        ]
        return DestinationConfig.model_validate(payload)
