"""Shared rules for refusing a run and for grading how complete its evidence was.

Both the offline fixture path and the live path use these so the two modes can never disagree
about what counts as sufficient evidence.
"""

from visa_research_agent.domain.models import (
    DestinationConfig,
    FetchedSource,
    PlanStatus,
    RetrievalReport,
    SourceReference,
)
from visa_research_agent.research.errors import InsufficientEvidenceError


def plan_references(
    destination: DestinationConfig, fetched_sources: list[FetchedSource]
) -> list[SourceReference]:
    """The sources a plan cites, each tied to the text it was read from and to why it was chosen.

    TODO item 21, parts 2 and 3. Done here, when the plan is built, rather than where a page is
    retrieved: the retrieval cache is shared between corridors, and a page one corridor chose for
    its checklist may be another's fee table. The hash is this run's; the choice is this
    destination's.
    """

    selections = {source.source_id: source.selection for source in destination.sources}
    return [
        fetched.source.model_copy(
            update={
                "content_hash": fetched.content_hash,
                "selection": selections.get(fetched.source.source_id),
            }
        )
        for fetched in fetched_sources
    ]


def describe_failures(report: RetrievalReport) -> list[str]:
    """One readable sentence per gap, safe to show a traveller."""

    return [
        f"{failure.title} ({failure.authority}) could not be used: {failure.detail}"
        for failure in report.failures
    ]


def require_load_bearing_sources(
    destination: DestinationConfig,
    report: RetrievalReport,
) -> None:
    """Refuse before extraction when a source the plan cannot stand without is missing.

    Checking first means a doomed run never reaches a paid model call.
    """

    required = destination.load_bearing_source_ids
    if not required:
        # Nothing load-bearing is normally a broken configuration. It is not when the reason is on
        # the record: either an authority under this destination's own government refused us, or it
        # publishes the decision only inside a questionnaire, so there was nothing to confirm the
        # decision *with*. The plan then says which of the two happened and names the page, which
        # is a next step the traveller can take, rather than nothing at all.
        if destination.decision_is_unverified:
            return
        raise InsufficientEvidenceError(
            f"{destination.display_name} declares no load-bearing sources",
            reasons=["The destination configuration is incomplete."],
        )

    available = {item.source.source_id for item in report.fetched}
    missing = [source_id for source_id in required if source_id not in available]
    if missing:
        lookup = {failure.source_id: failure for failure in report.failures}
        reasons = [
            describe_failures(RetrievalReport(failures=[lookup[source_id]]))[0]
            if source_id in lookup
            else f"The required source {source_id} was not retrieved."
            for source_id in missing
        ]
        raise InsufficientEvidenceError(
            f"Required evidence for {destination.display_name} is unavailable",
            reasons=reasons,
            failures=report.failures,
        )


def resolve_plan_status(
    report: RetrievalReport,
    *,
    has_checklist_source: bool = True,
    decision_is_unverified: bool = False,
    no_visa_required: bool = False,
    names_unread_pages: bool = False,
) -> PlanStatus:
    """Grade a run: verified only when every source was retrieved and is current.

    A plan with no page designated as its document checklist is **never** verified, however cleanly
    its other sources were read. It is missing evidence a traveller would expect a complete plan to
    rest on — whether because the authority publishes none or because we were not allowed to read
    it — and "verified" beside an empty document list is the one label that would make that
    invisible. It stays honest without refusing, which is what DECISIONS entry 14 chose.

    **Unless a page stated that this traveller needs no visa.** Then there is no application, so
    there are no application documents, and the missing checklist is not missing — the question
    does not arise (DECISIONS entries 94 and 95). Entry 14's reason is that a traveller would
    expect a complete plan to rest on a checklist, and a visa-free traveller expects no such thing.
    Grading such a plan `partial` for ever would say its evidence was incomplete when every page it
    rests on was read cleanly, which is the same defect entry 93 fixed in the coverage metric.

    The exception is safe only because `no_visa_required` means a page *said so*: extraction passes
    the decision it is about to put on the plan, which is `None` rather than `False` whenever
    `decision_is_unverified`. A blocked page and a questionnaire both stay `partial`, and the clause
    below is checked first so a caller that got both wrong still refuses the label.

    A plan whose visa decision could not be confirmed is never verified either, for the same reason
    and more strongly: it is the one thing a traveller most needs to be right. **"Could not be
    confirmed" means a null decision for any reason** — until 2026-09-14 extraction passed only the
    case where a block or a questionnaire stood in for it, so a model leaving the decision open from
    cleanly read pages was graded verified (TODO item 53). `VisaPlan` now refuses that combination.
    """

    if decision_is_unverified:
        return "partial"
    if not has_checklist_source and not no_visa_required:
        return "partial"
    # Pages the plan names and nobody read — an authority page that refused discovery, or a
    # possible checklist nobody opened — are unavailable evidence exactly as a failed fetch is, and
    # `VisaPlan` refuses "verified" beside them. Grading only this run's fetch made the two
    # disagree: `united-arab-emirates/IN/GB` read every page it cited, discovery had met two
    # refusals on `gdrfad.gov.ae`, and the plan was graded verified and then refused as invalid,
    # so the traveller got a 503 instead of a partial plan (TODO item 70).
    if report.failures or names_unread_pages:
        return "partial"
    if any(item.source.is_stale for item in report.fetched):
        return "partial"
    return "verified"
