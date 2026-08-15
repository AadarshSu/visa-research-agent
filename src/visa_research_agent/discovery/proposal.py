"""Rendering a resolved corridor as configuration a person can review and paste.

The output is deliberately in the same shape as the hand-written entries in `destinations.yaml`,
so a reviewer compares like with like, and so approving it is a copy rather than a translation.
"""

import yaml

from visa_research_agent.discovery.models import ResolvedCorridor


def render_corridor_yaml(resolved: ResolvedCorridor) -> str:
    """A destination fragment for the corridor, with the reasoning kept as comments."""

    sources = [
        {
            "source_id": source.source_id,
            "title": source.title,
            "url": str(source.url),
            "authority": source.authority,
            "kind": source.kind,
            "research_pass": source.research_pass,
        }
        for source in resolved.sources
    ]
    body = {
        "application_document_source_ids": resolved.source_ids_for("document_checklist"),
        "required_source_ids": (
            resolved.source_ids_for("document_checklist")
            + resolved.source_ids_for("visa_decision")
        ),
        "sources": sources,
    }

    header = [
        f"# Discovered for corridor {resolved.corridor.key}",
        f"# Resolved at {resolved.resolved_at.isoformat()}",
        f"# {resolved.pages_fetched} pages read, {resolved.model_calls} model calls",
    ]
    for source in resolved.sources:
        roles = ", ".join(source.roles)
        header.append(f"#   {source.source_id}: {roles} (score {source.score:g})")
    for role in resolved.unresolved_roles:
        header.append(f"#   UNRESOLVED: {role}")
    for note in resolved.notes:
        header.append(f"#   note: {note}")

    dumped = yaml.safe_dump(body, sort_keys=False, allow_unicode=True, width=100)
    return "\n".join(header) + "\n" + dumped
