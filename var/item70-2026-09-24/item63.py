"""TODO item 63: decision and checklist rates over the ten-destination round (DECISIONS entry 205).

usage, from the repository root: .venv/bin/python var/item70-2026-09-24/item63.py [OUT]
Reads OUT/*/*/result.json and plan.json (default: item63/ beside this file), one line per run, then
entry 58's two rates: a decision confirmed in both runs, and a checklist found in both runs.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / (sys.argv[1] if len(sys.argv) > 1 else "item63")


def describe(run_dir: Path) -> dict[str, object]:
    result = json.loads((run_dir / "result.json").read_text())
    row: dict[str, object] = {"research": result["research"], "plan": result.get("plan", "-")}
    plan_path = run_dir / "plan.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        row.update(
            decision=plan["visa_required"],
            status=plan["status"],
            checklist=bool(plan["application_document_source_ids"]) and bool(plan["requirements"]),
            requirements=len(plan["requirements"]),
            decision_tool=any(t.get("topic") == "visa_decision" for t in plan["official_tools"]),
            checklist_tool=any(
                t.get("topic") == "document_checklist" for t in plan["official_tools"]
            ),
            delegated=len(plan["delegated_services"]),
        )
    recall = next((run_dir / "recall").glob("*.json"), None)
    if recall is not None:
        row["unresolved"] = json.loads(recall.read_text()).get("unresolved_roles", [])
    row["seconds"] = result.get("seconds")
    return row


by_corridor: dict[str, list[dict[str, object]]] = defaultdict(list)
for result_path in sorted(OUT.glob("*/*/result.json")):
    by_corridor[result_path.parent.parent.name].append(describe(result_path.parent))

confirmed = checklists = 0
for corridor, rows in sorted(by_corridor.items()):
    print(corridor)
    for row in rows:
        print("   ", row)
    if len(rows) >= 2 and all(r.get("decision") is not None for r in rows):
        confirmed += 1
    if len(rows) >= 2 and all(r.get("checklist") for r in rows):
        checklists += 1
total = len(by_corridor)
print(f"\ndecision confirmed, every run: {confirmed}/{total}")
print(f"checklist found, every run:   {checklists}/{total}")
