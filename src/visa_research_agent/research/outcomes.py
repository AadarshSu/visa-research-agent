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


def resolve_plan_status(report: RetrievalReport) -> PlanStatus:
    """Grade a run: verified only when every source was retrieved and is current."""

    if report.failures:
        return "partial"
    if any(item.source.is_stale for item in report.fetched):
        return "partial"
    return "verified"
