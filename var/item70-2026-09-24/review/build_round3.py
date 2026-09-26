"""The owner's third look at the corridors judged wrong or unsure in item 63's second round.

usage, from the repository root:
    .venv/bin/python var/item70-2026-09-24/review/build_round3.py > data3.json
Australia, South Korea and Spain: the second round's runs (`item63-round2/`) beside the latest two,
on the code and stores of 2026-09-26 (`item63-rebuilt-2026-09-26/`, entries 215-223), with the
owner's verdict on the second round shown on each card. Same shape as `build_review_data.py`.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ROUND_ONE = HERE / "item63-round2"
ROUND_TWO = HERE / "item63-rebuilt-2026-09-26"

DESTINATIONS = [
    ("australia", "Australia"),
    ("south-korea", "South Korea"),
    ("spain", "Spain"),
]

# The owner's verdicts on the second round (entry 216), shortened.
EARLIER_VERDICTS = {
    "australia": "Wrong: the Tourist stream (subclass 600) page should be reached and linked.",
    "south-korea": "Unsure: an uninspected PDF download; state the visa type (C-3-9); the visa "
    "application centre.",
    "spain": "Unsure: the embassy's Schengen visa page gives a document checklist.",
}


def read(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def outline(run_dir: Path) -> dict:
    """The short form, for the earlier round: what it decided and whether it had a checklist."""

    result = read(run_dir / "result.json") or {}
    plan = read(run_dir / "plan.json")
    if plan is None:
        return {"answered": False, "reason": str(result.get("detail", ""))[:200]}
    return {
        "answered": True,
        "decision": plan["visa_required"],
        "checklist": bool(plan["application_document_source_ids"] or plan["requirements"]),
        "status": plan["status"],
    }


def detail(run_dir: Path) -> dict:
    """What one plan told the traveller, with the official page behind each part."""

    result = read(run_dir / "result.json") or {}
    plan = read(run_dir / "plan.json")
    out: dict = {"seconds": result.get("seconds")}
    if plan is None:
        detail_text = result.get("detail") or result.get("plan_error") or "no plan was produced"
        if isinstance(detail_text, dict):
            detail_text = detail_text.get("message", str(detail_text))
        out.update(answered=False, reason=str(detail_text))
        return out
    sources = {source["source_id"]: source for source in plan["sources"]}

    def page(source_id: str) -> dict | None:
        source = sources.get(source_id)
        if source is None:
            return None
        return {
            "title": source["title"],
            "url": source["url"],
            "authority": source["authority"],
            "retrieved": source["retrieved_at"][:10],
            "stale": source["is_stale"],
        }

    where = plan.get("where_to_apply")
    out.update(
        answered=True,
        decision=plan["visa_required"],
        visa_type=plan["visa_type"],
        status=plan["status"],
        explanation=plan["explanation"],
        decision_pages=[p for p in map(page, plan["decision_source_ids"]) if p],
        decision_quotes=[
            {"text": quote["text"], "page": page(quote["source_id"])}
            for quote in plan["decision_quotes"]
        ],
        checklists=[p for p in map(page, plan["application_document_source_ids"]) if p],
        unread_checklists=[
            {
                "title": failure["title"],
                "url": failure["attempted_url"],
                "why": failure["detail"],
            }
            for failure in plan["unavailable_sources"]
            if failure["source_id"].startswith("checklist_unread_")
        ],
        unread_visa_pages=[
            {
                "title": failure["title"],
                "url": failure["attempted_url"],
                "why": failure["detail"],
            }
            for failure in plan["unavailable_sources"]
            if failure["source_id"].startswith("visa_page_unread_")
        ],
        refused=[
            {"title": failure["title"], "url": failure["attempted_url"], "why": failure["detail"]}
            for failure in plan["unavailable_sources"]
            if not failure["source_id"].startswith(("checklist_unread_", "visa_page_unread_"))
        ],
        where_to_apply=(
            {
                "authority": where["authority"],
                "method": where["application_method"],
                "url": where["application_url"],
            }
            if where
            else None
        ),
        steps=[
            {
                "title": step["title"],
                "action": step["action"],
                "timing": step.get("timing"),
                "url": (
                    (where or {}).get("application_url")
                    if step.get("link_target") == "application_route"
                    else (sources.get(step.get("link_source_id") or "") or {}).get("url")
                ),
            }
            for step in plan["application_steps"]
        ],
        questions=plan["unresolved_questions"],
        tools=[{"topic": tool["topic"], "url": tool["url"]} for tool in plan["official_tools"]],
        all_pages=[p for p in map(page, sources) if p],
    )
    return out


rows = []
for slug, name in DESTINATIONS:
    key = f"{slug}_IN_IN"
    rows.append(
        {
            "slug": slug,
            "name": name,
            "earlier_verdict": EARLIER_VERDICTS[slug],
            "before": [outline(ROUND_ONE / key / str(n)) for n in (1, 2)],
            "after": [detail(ROUND_TWO / key / str(n)) for n in (1, 2)],
        }
    )
json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
