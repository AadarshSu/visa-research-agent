"""Shared rules for refusing a run and for grading how complete its evidence was.

Both the offline fixture path and the live path use these so the two modes can never disagree
about what counts as sufficient evidence.
"""

from visa_research_agent.domain.models import (
    DestinationConfig,
    PlanStatus,
    RetrievalReport,
)
from visa_research_agent.research.errors import InsufficientEvidenceError


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
) -> PlanStatus:
    """Grade a run: verified only when every source was retrieved and is current.

    A plan with no page designated as its document checklist is **never** verified, however cleanly
    its other sources were read. It is missing evidence a traveller would expect a complete plan to
    rest on — whether because the authority publishes none or because we were not allowed to read
    it — and "verified" beside an empty document list is the one label that would make that
    invisible. It stays honest without refusing, which is what DECISIONS entry 14 chose.

    A plan whose visa decision could not be confirmed is never verified either, for the same reason
    and more strongly: it is the one thing a traveller most needs to be right.
    """

    if not has_checklist_source or decision_is_unverified:
        return "partial"
    if report.failures:
        return "partial"
    if any(item.source.is_stale for item in report.fetched):
        return "partial"
    return "verified"
