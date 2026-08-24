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
# Where a destination's sources come from.
#   configured — only destinations hand-written in destinations.yaml can produce a plan.
#   automatic  — an unconfigured destination is resolved by discovery at request time, trusting
#                only domains belonging to that country's own government.
DestinationMode = Literal["configured", "automatic"]
# Why a source produced no usable evidence. These are kept apart because they need different
# remedies and, more importantly, they support different statements to a traveller.
#
# `blocked` is the subtle one. A site refusing automated clients is not saying its guidance is
# wrong or missing — it is saying this program may not read it. The only honest claim is then
# "we could not independently retrieve and verify this here", which is a much narrower statement
# than "unreachable" and must never be softened into an inference from some other page.
#
# `disallowed` is the same fact arrived at without a request: the host published a crawl policy
# that excludes this client, and it was obeyed (DECISIONS entry 36). Kept apart from `blocked`
# because the two license different things. A `403` was observed on the page itself; a `Disallow`
# is a rule about a path we never asked for, so it may be reported but must never resolve a
# corridor the way a settled refusal can.
#
# MISSING, decided as DECISIONS entry 41 and not yet built: `challenged`. `blocked` currently claims
# every `403` is an authority refusing us, and for `france-visas.gouv.fr` that is false — it answers
# `cf-mitigated: challenge`, a Cloudflare interstitial saying "enable JavaScript and cookies to
# continue", and answers it for `/robots.txt` too, so the authority stated nothing at all. That is a
# capability test rather than a refusal, a real browser under our own user agent answers it, and it
# must sit outside `blocked_urls()` and `persistent_refusals()` exactly as `disallowed` does. Until
# then France's failures are reported in words that are not true of what was seen. See TODO item 5.
FailureOutcome = Literal["untrusted", "unreachable", "unusable", "blocked", "disallowed"]

# Statuses an authority returns to refuse an automated client rather than to report a fault.
BLOCKING_STATUS_CODES = frozenset({401, 403, 429})

# The subset whose refusal is **settled** rather than momentary, and so the only ones a page may be
# handed to a traveller on. `401` and `403` say "you may not read this", and waiting changes
# nothing. `429` says "not right now" — it is a rate limit, and the honest advice there is to try
# again later, exactly as DECISIONS entry 27 reasons about a `502`. Both are still reported as
# `blocked`, because entry 18 requires a refusal never to read as "nothing found"; the distinction
# governs only what may resolve a corridor or be named as guidance nobody was allowed to read.
PERSISTENT_REFUSAL_STATUS_CODES = frozenset({401, 403})
PlanStatus = Literal["verified", "partial"]
SourceKind = Literal[
    "immigration_authority",
    "foreign_ministry",
    "embassy_or_high_commission",
    "official_application_provider",
]
SourcePass = Literal["primary", "follow_up"]

# Why someone is travelling. Shared with discovery, which scores pages against it, so the two can
# never drift apart into a corridor nobody can research.
TravelPurpose = Literal["tourism", "business", "study", "transit"]

# ISO 3166-1 alpha-2. Countries are held as codes rather than names because a name has many
# spellings and a code has one, and every corridor, cache key and lexicon lookup is keyed by code.
COUNTRY_CODE_PATTERN = r"^[A-Z]{2}$"


class StrictModel(BaseModel):
    """Base model that rejects unexpected data instead of silently discarding it."""

    model_config = ConfigDict(extra="forbid")


def _require_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return value


class TravellerProfile(StrictModel):
    """Who is travelling, in the terms that change which official pages apply.

    Only four things actually select the guidance: the passport, where the traveller applies from,
    why they are going, and — where they are not a citizen of the country they live in — what
    permission they hold there. Everything else is optional, because asking for detail a plan does
    not use is asking for personal data with no purpose.
    """

    passport_nationality: str = Field(pattern=COUNTRY_CODE_PATTERN)
    passport_type: Literal["ordinary"]
    """Ordinary only, deliberately. Diplomatic and official passport pages are a hard veto in
    discovery's scoring, so a plan for one of those travellers could not be researched and must
    not be silently approximated with the ordinary-passport rules."""

    country_of_residence: str = Field(pattern=COUNTRY_CODE_PATTERN)
    travel_purpose: TravelPurpose = "tourism"

    city_of_residence: str | None = None
    residence_status: str | None = None
    """The permission a traveller holds where they live, when they are not a citizen of it — a UK
    Graduate visa, a US green card. Frequently decisive: Brazil and China both require proof of
    regular status from a non-citizen resident. None when they are a citizen, or did not say."""

    residence_permission_expiry: date | None = None


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


class UnreadableAuthority(StrictModel):
    """One of the destination's own authorities that would not let this program read it.

    Carried so a plan can name it and hand the traveller the URL, which is a next step they can act
    on: they can open it in their own browser. It is **never evidence**. Nothing here says what the
    page contains — only that it exists, whose it is, and that we were not permitted to read it from
    here. That is the one claim a block licenses (DECISIONS entry 18), and it is the whole reason
    this is a separate type from `ConfiguredSource` rather than a source with empty content.
    """

    url: AnyHttpUrl
    authority: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    """A safe summary of what happened. Never carries retrieved page text."""


class InteractiveDecisionTool(StrictModel):
    """An official page that *determines* the visa decision instead of *stating* it.

    `gov.uk/check-uk-visa` is why this exists. It is served willingly, fetched cleanly and read in
    full, and it does not answer the question: it is a questionnaire that computes an answer from
    replies this program does not have. Measured over twenty corridors, that cost every United
    Kingdom corridor its entire plan — the checklist, the route, the times and the per-nationality
    fees were all found, and all discarded, because `visa_decision` was unfilled (DECISIONS entry
    58).

    So it is deliberately **not** an `UnreadableAuthority`: nothing refused us, and saying so would
    be false. It is equally **not** a `ConfiguredSource` for the decision: the page states no
    decision, so citing it as evidence of one would be inventing an answer out of a form. What it
    is, is a next step the traveller can take and this program cannot — they can answer the
    questions themselves — which is the same thing entry 27 offers for a refused page, and for the
    same reason.

    Driving the questionnaire is not the alternative. That is an application flow, permanently out
    of scope in CLAUDE.md, and it would mean supplying traveller answers nobody gave us.
    """

    url: AnyHttpUrl
    authority: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    """A safe summary of why the page did not answer. Never a guess at what answering would say."""


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

    unreadable_authorities: list[UnreadableAuthority] = Field(default_factory=list)
    """The destination's own authorities that refused this program, for the plan to point at."""

    decision_tools: list[InteractiveDecisionTool] = Field(default_factory=list)
    """Official questionnaires that decide the question, for the plan to hand over."""

    decision_is_unverified: bool = False
    """True when no page could be confirmed as saying whether a visa is needed, *and* the reason is
    one the traveller can act on rather than simply that nothing was found.

    There are two such reasons and they are different facts. An authority refused automated
    retrieval, so the page exists and we were not permitted to read it — `unreadable_authorities`.
    Or the authority publishes the answer only inside an interactive tool, which was read and asks
    questions rather than stating anything — `decision_tools`. Both leave the traveller one page to
    open; neither licenses an inference about what it would say.

    It is what lets a plan be produced at all in either case, so it must never be set without an
    entry in one of those two lists — otherwise "we could not read it" and "the answer is behind a
    form" would both cover for "we did not find it", which needs a different remedy and must still
    refuse."""

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

        if self.decision_is_unverified and not (self.unreadable_authorities or self.decision_tools):
            raise ValueError(
                "an unverified visa decision must name the authority that could not be read, or "
                "the official tool that decides it"
            )

        # These are presented to a traveller as this destination's own guidance, so they are held to
        # the same rule as evidence: officialness is a property of the domain. A page we could not
        # read is exactly the case where nothing else could vouch for it.
        for authority in self.unreadable_authorities:
            if not self.trusts_host(host_of(str(authority.url))):
                raise ValueError(
                    f"unreadable authority {authority.url} is not on an approved domain"
                )

        # The same rule, for the same reason. A tool's page *was* read, but nothing in its text is
        # what makes it official — entry 2 — and a traveller is being sent there to get the answer
        # this plan could not state, which is the last place to start trusting prose.
        for tool in self.decision_tools:
            if not self.trusts_host(host_of(str(tool.url))):
                raise ValueError(f"decision tool {tool.url} is not on an approved domain")

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
    destination_mode: DestinationMode = "configured"
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

    http_status: int | None = Field(default=None, ge=100, le=599)
    """The status the authority answered with, when there was one.

    `outcome` says a page was refused; this says whether waiting could change that. A `429` is a
    rate limit and a `403` is a settled refusal, and only the second supports telling a traveller
    that an authority would not permit this program to read a page — the distinction DECISIONS
    entry 32 draws, and `PERSISTENT_REFUSAL_STATUS_CODES` is what reads it.

    Carried structurally rather than left in `detail`, because entry 36's rule applies here too:
    what acts on a refusal must read a recorded outcome, never parse the sentence describing it, or
    rewording a message silently empties the list something else depends on. `CrawlFetcher` has
    kept the same fact in `refusal_statuses` since entry 32; this is the retrieval path catching up.

    None when no response was received at all — a DNS failure, a timeout, a `robots.txt`
    `Disallow` — which fails toward *not* claiming an authority refused us.
    """


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

    title: str = Field(min_length=3, max_length=70)
    """A short label. The step's substance belongs in `action`, not here."""
    action: str = Field(min_length=3, max_length=320)
    timing: str = Field(min_length=3, max_length=160)
    source_ids: list[str] = Field(min_length=1)
    link_target: Literal["application_route", "source", "none"]
    link_source_id: str | None

    @field_validator("title")
    @classmethod
    def tidy_title(cls, value: str) -> str:
        """Drop punctuation that means a sentence was still going.

        A model given 80 characters wrote to the limit and stopped mid-clause — "…if the wizard says
        a visa," — which reads as a truncation bug in the interface. The length is now tighter and
        the prompt asks for a label, but the trailing comma is trimmed here as well: a heading is
        derived text rather than a claim, so tidying it invents nothing.
        """

        return value.strip().rstrip(",;:").strip() or value.strip()

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
    """Also where a disagreement between official sources goes.

    There was a `conflicts` field beside this one, and it was deleted rather than improved. Entry 6
    built a *deterministic* conflict detector, found a real discrepancy with it, and deleted it
    anyway, because nothing recorded who a claim applied to: a page listing visa-free nationalities
    and a nationality-specific page requiring a visa compared as a contradiction. The lesson it
    recorded — a feature whose wrong answers are alarming needs a near-zero false-positive rate or
    it should not ship — condemns unverified model prose more strongly than the checked version it
    replaced. So a disagreement is reported here, as something we could not resolve, which is what
    it honestly is. See DECISIONS entry 30, and entry 6 before rebuilding it.
    """

    last_checked: datetime
    status: PlanStatus
    unavailable_sources: list[SourceFailure] = Field(default_factory=list)

    decision_tools: list[InteractiveDecisionTool] = Field(default_factory=list)
    """Official questionnaires that hold the decision this plan could not state.

    Deliberately not folded into `unavailable_sources`: these pages were read, and reporting them
    as evidence that could not be used would be false about what happened. They are set by the
    application from the resolved corridor, never by the model, so the URL handed to a traveller is
    one an authority published rather than one that was generated.
    """

    _validate_last_checked = field_validator("last_checked")(_require_aware_datetime)

    @model_validator(mode="after")
    def validate_status_matches_evidence(self) -> "VisaPlan":
        """A verified plan must have complete, current evidence behind every source."""

        if self.status == "verified":
            if self.unavailable_sources:
                raise ValueError("a verified plan cannot report unavailable sources")
            if any(source.is_stale for source in self.sources):
                raise ValueError("a verified plan cannot rest on stale evidence")
            if self.decision_tools:
                raise ValueError("a verified plan cannot rest on a decision nobody read off a page")
        return self

    @model_validator(mode="after")
    def validate_decision_tool_leaves_decision_open(self) -> "VisaPlan":
        """Naming the questionnaire and answering it are mutually exclusive.

        A tool is named precisely because no page stated the decision. Stating one anyway would
        mean it came from somewhere else — the questionnaire's own prompts, most likely, which is
        reading an answer out of a question. Enforced here rather than asked for in the prompt,
        for the same reason `decision_is_unverified` is: a model asked for null returned `true`.
        """

        if self.decision_tools and self.visa_required is not None:
            raise ValueError(
                "a plan naming an interactive decision tool cannot also state whether a visa is "
                "required"
            )
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
