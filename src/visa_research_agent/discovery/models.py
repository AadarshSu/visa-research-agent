"""Strict models for the discovery pipeline.

The important one is `ResolvedCorridor`: it is machine-produced, so its conversion back into a
`DestinationConfig` deliberately re-runs that model's validators. A corridor whose URLs drifted off
the approved domains cannot be turned into something the retriever would fetch.
"""

from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator, model_validator

from visa_research_agent.domain.models import (
    COUNTRY_CODE_PATTERN,
    ConfiguredSource,
    DestinationConfig,
    GuidanceTopic,
    SourceKind,
    SourcePass,
    StrictModel,
    TravelPurpose,
)
from visa_research_agent.domain.trust import host_of

# Built from the domain's `GuidanceTopic` rather than restated, so a role a page can fill and a
# topic a plan can offer a tool for can never drift apart. `irrelevant` is discovery's alone: it
# is a verdict about a page, not a question a traveller has.
DiscoveryRole = Literal[GuidanceTopic, "irrelevant"]
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

# Why one run ended the way it did, as a value rather than a sentence.
#
# `RecallRecord.outcome` has always carried this in prose, and prose cannot be counted. Worse, two
# of these read *identically* there: a corridor refused because nothing stated the visa decision and
# a corridor resolved by handing over the questionnaire that states it both write "resolved, with no
# visa_decision". Those have opposite meanings for a traveller and opposite fixes for us, and the
# twenty-corridor logs on disk cannot be told apart at all — which is what this exists to end.
#
# Deliberately **not** every reason a traveller can go unanswered. The two largest are decided
# before a resolver is constructed — a country with no row in `authority_domains.yaml`, and a row
# whose domains the trust rule cannot confirm — so no run happens and no record is written. Those
# are counted from committed data instead (`visa-discover audit`), and conflating the two sources
# would let a reachability failure hide inside a recall failure.
RefusalCause = Literal[
    "resolved",
    "resolved_decision_blocked",
    "resolved_decision_tool",
    "decision_not_found",
    "no_candidates",
    "adjudication_failed",
    "run_raised",
]

# Display and output order, so proposals diff cleanly between runs.
ROLE_ORDER: tuple[DiscoveryRole, ...] = (
    "visa_decision",
    "document_checklist",
    "application_route",
    "fees",
    "processing_times",
    "general_entry",
)


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
    found_by: Literal["search", "crawl", "corpus"] = "crawl"
    """Which stage produced this candidate.

    `corpus` is not cosmetic: measuring whether the crawl still earns its place meant reading 25
    shortlisted URLs against a 3,216-entry store by hand (DECISIONS entry 48). Recorded here, the
    recall log answers it for free the next time the question comes up.
    """

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


class ResolvedTool(StrictModel):
    """One official questionnaire, and the question it settles."""

    role: GuidanceTopic
    url: str = Field(min_length=1)


class ResolvedCorridor(StrictModel):
    """The sources discovery selected for one corridor, plus what it could not resolve."""

    schema_version: Literal[1] = 1
    corridor: Corridor
    resolved_at: datetime
    sources: list[ResolvedSource] = Field(default_factory=list)
    unresolved_roles: list[DiscoveryRole] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    ran_without_search: bool = False
    """True when the search provider was unavailable and the stored corpus answered alone.

    A **typed** field rather than a sentence in `notes`, for DECISIONS entry 36's reason: what acts
    on a fact must read a recorded outcome, never parse the prose describing it, or rewording a
    message silently changes behaviour. What acts on it is the corridor store, which must not keep
    a narrower resolution for three weeks and serve it as an ordinary one.

    A corridor may only run this way when a corpus exists to run from. With no corpus there is
    nothing to fall back to and the refusal stands — a `402` must never read as "this country has
    no pages" (entry 74).
    """

    inaccessible_domains: list[str] = Field(default_factory=list)
    """Domains that refused automated retrieval.

    Carried separately from `notes` because it supports a different statement. These authorities
    did not fail and are not wrong; this program was not permitted to read them, so their guidance
    could not be independently verified here. Nothing may be inferred in their place.
    """

    inaccessible_urls: list[str] = Field(default_factory=list)
    """The exact pages whose refusal was settled, so a plan can hand over a link, not a domain.

    A page, not a host, because that is the scope of what was observed: this URL refused this
    client. It is still not evidence about what the page says.

    **Only persistent refusals** — `401` and `403` — reach this list. A `429` is a rate limit, and
    telling a traveller an authority would not permit us to read a page is not something a momentary
    limit supports. Such a refusal is still reported, in `inaccessible_domains` and in the notes;
    it is simply not handed over as guidance nobody was allowed to read. See DECISIONS entry 32.
    """

    decision_blocking_urls: list[str] = Field(default_factory=list)
    """The refusals that plausibly held the visa decision, and the only ones that may resolve this.

    Carried apart from `inaccessible_urls` because the two answer different questions. Every
    refusal is worth *reporting*; only a refusal of a page that could have answered the question
    licenses saying the decision is unverifiable rather than unfound.

    Without this the exception swallows the rule. A `403` on a footer link would qualify, and WAF
    refusals on incidental pages are ordinary at scale — so corridors whose decision was simply
    **not found**, which must refuse, would drift into presenting as authority-blocked, which
    resolves. That is the refusal discipline leaking, and it is the failure this field exists to
    prevent. See DECISIONS entry 32.
    """

    interactive_tools: list["ResolvedTool"] = Field(default_factory=list)
    """Pages that were read and found to *ask* a question rather than answer it.

    The third outcome. A source is "a page answered it", `decision_blocking_urls` is "an authority
    would not let us look", and this is "we looked, and the authority publishes the answer only
    inside a questionnaire". Before it existed, a `visa_decision` in that state fell into *not
    found* and refused the corridor, discarding a checklist, a route, processing times and fees
    that had all been resolved correctly — every United Kingdom corridor, in the twenty-corridor
    measurement (entry 58).

    **Every role, not only the decision** (entry 60). An authority that puts its checklist or its
    entry requirements behind a questionnaire has published that guidance, and a plan that said
    nothing would be withholding the one thing the traveller could act on. Only a `visa_decision`
    tool changes whether the corridor resolves, because only that role is load-bearing; the rest add
    a link to a plan that already stands.

    Kept apart from `decision_blocking_urls` because the two support different sentences and one of
    them would become false: nothing refused us here. It is also the stronger claim of the two,
    which is why it does not need entry 32's second gate — the model is judging a page whose text
    it was actually given, so "this page defers the answer to a form" is checkable in a way "this
    page nobody read might have held the answer" is not.

    Entry 32's *lesson* still binds, though: *not found* and *behind a tool* must not blur. So this
    is filled only by the adjudicator, on a page it read, and only for a role no source filled.
    """

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
        """True when every load-bearing role was filled, or the gap is one an authority imposed.

        A corridor that simply could not find its visa decision is still refused: a substitute page
        would be worse than nothing.

        There are two exceptions and they share a shape. When an authority under the destination's
        *own* government refused this program, or when it publishes the answer only inside an
        interactive tool, the honest position is not silence — it is naming the page and saying why
        it did not answer, which is something the traveller can act on by opening it themselves.
        That needs a plan to exist to say it in, so the corridor resolves and
        `decision_is_unverified` carries the reason. Readable sources are still required in both:
        with nothing at all to cite there is no plan, only a link.

        For a refusal, three things have to hold, and each keeps the exception from swallowing the
        rule: it must be **settled** rather than a rate limit, it must be of a page that could
        plausibly have **held the decision**, and something readable must remain to cite. For a
        tool, the page must have been **read** and judged to defer the answer, which is the same
        discipline reached by a shorter route — the text was in hand.
        """

        filled = {role for source in self.sources for role in source.roles}
        if all(role in filled for role in LOAD_BEARING_ROLES):
            return True
        handed_over = bool(self.decision_blocking_urls or self.decision_tool_urls)
        return handed_over and bool(self.sources)

    @property
    def decision_tool_urls(self) -> list[str]:
        """Only the tools that settle the visa decision. The other topics resolve nothing."""

        return [tool.url for tool in self.interactive_tools if tool.role == "visa_decision"]

    @property
    def decision_is_unverified(self) -> bool:
        """True when nothing confirmed the visa decision and a named page is why.

        Deliberately not "and something somewhere was blocked". A decision that was merely not
        found must still refuse, so the blocked page has to be one that could have answered the
        question — which is what `decision_blocking_urls` records — or the page has to have been
        read and found to ask the question rather than answer it, which is `decision_tool_urls`.
        """

        filled = {role for source in self.sources for role in source.roles}
        if "visa_decision" in filled:
            return False
        return bool(self.decision_blocking_urls or self.decision_tool_urls)

    @property
    def outcome_cause(self) -> RefusalCause:
        """Why this corridor ended as it did, as a value something can count.

        This is the distinction `RecallRecord.outcome` cannot express. A corridor that refused
        because nothing stated the visa decision and a corridor that resolved by handing over the
        questionnaire stating it both write "resolved, with no visa_decision" there, and every
        United Kingdom run in the twenty-corridor logs is the second wearing the first's words.

        `resolved` means the load-bearing roles were filled outright. It says nothing about
        `document_checklist`, which is reported by `unresolved_roles` and counted separately — a
        corridor missing only its checklist resolved, and calling that a failure would re-open the
        question DECISIONS entry 14 settled.

        **Two refusals are invisible from the result alone**: a run that found no candidates and a
        run whose adjudication failed both produce a corridor with no sources. Those are recorded
        where they happen, by `ResolutionTrace.refusal_cause`, and the recall log prefers it. Left
        to this property a sourceless corridor reads as `decision_not_found`, which is what a
        corridor that fetched pages and filled nothing is — the accurate answer in every case the
        two overrides do not already claim.

        Blocked is checked before tool, so a corridor holding both is counted as blocked. That is
        the narrower fact of the two: an authority refused us, which is a thing that happened to a
        request, where a questionnaire is a judgement about a page we read.
        """

        filled = {role for source in self.sources for role in source.roles}
        if all(role in filled for role in LOAD_BEARING_ROLES):
            return "resolved"
        if self.sources and self.decision_blocking_urls:
            return "resolved_decision_blocked"
        if self.sources and self.decision_tool_urls:
            return "resolved_decision_tool"
        return "decision_not_found"

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
        # Named so the plan can point at them. Deliberately not sources: there is no content behind
        # them, and a source with empty content is exactly what must never be citable as evidence.
        payload["unreadable_authorities"] = [
            {
                "url": url,
                "authority": f"{destination.display_name} authority ({host_of(url)})",
                "detail": (
                    "refused automated retrieval, so its guidance could not be independently "
                    "verified here"
                ),
            }
            for url in self.inaccessible_urls
        ]
        # Read, not refused, so it is neither a source nor an unreadable authority. It is a page
        # the traveller can finish themselves, and the detail says exactly that — never a guess at
        # what answering it would produce. A tool is offered only where no source filled its role:
        # once a page answers the question, a questionnaire is a longer route to the same place.
        # A tool is offered only where no source filled its role: once a page answers the question,
        # a questionnaire is a longer route to the same place.
        #
        # **Not deduplicated by URL, though it was for an hour on 2026-08-24 and that was wrong.**
        # France's `uk.diplomatie.gouv.fr/en/applying-for-a-visa` settles three questions —
        # whether a visa is needed, which documents, and the fee — and collapsing it to one hid the
        # checklist tool from the documents panel, which is exactly where a reader looking for
        # documents goes. The same page under two questions is two answers, not one link twice.
        # Where it *would* read as repetition — the catch-all panel carrying fees, times and
        # entry conditions together — the interface skips a URL it has already shown.
        filled = {role for source in self.sources for role in source.roles}
        tools = [
            tool
            for role in ROLE_ORDER
            for tool in self.interactive_tools
            if tool.role == role and tool.role not in filled
        ]
        payload["official_tools"] = [
            {
                "topic": tool.role,
                "url": tool.url,
                "authority": f"{destination.display_name} authority ({host_of(tool.url)})",
                "detail": (
                    "answers this by asking questions rather than stating it, so the answer could "
                    "not be read from the page"
                ),
            }
            for tool in tools
        ]
        payload["decision_is_unverified"] = self.decision_is_unverified
        return DestinationConfig.model_validate(payload)
