"""One row per run: outcome, decision, status, checklist, the pages the decision rests on."""

import glob
import json
import os
import sys

rows = []
for res in sorted(glob.glob(sys.argv[1] + "/*/*/result.json")):
    d = os.path.dirname(res)
    r = json.load(open(res))
    row = {"corridor": r["corridor"], "research": r["research"], "seconds": r["seconds"]}
    if os.path.exists(d + "/plan.json"):
        p = json.load(open(d + "/plan.json"))
        by_id = {s["source_id"]: s for s in p["sources"]}
        row.update(
            visa_required=p["visa_required"],
            status=p["status"],
            visa_type=p["visa_type"],
            decision_condition=p.get("decision_condition"),
            explanation=p.get("explanation"),
            decision=[by_id[i]["url"] for i in p["decision_source_ids"] if i in by_id],
            checklist=[by_id[i]["url"] for i in p["application_document_source_ids"] if i in by_id],
            tools=[t.get("url") for t in p.get("official_tools") or []],
            steps=[s["title"] for s in p["application_steps"]],
            where=(p["where_to_apply"] or {}).get("application_url"),
            questions=p["unresolved_questions"],
        )
    else:
        row["detail"] = (
            (r.get("detail") or {}).get("message")
            if isinstance(r.get("detail"), dict)
            else r.get("detail")
        )
    rows.append(row)
json.dump(rows, open(sys.argv[2], "w"), indent=1)
for x in rows:
    decision = str(x.get("visa_required", "-"))
    checklist = len(x.get("checklist", []))
    print(f"{x['corridor']:32} {x['research']:9} {decision:6} {x.get('status', '-'):9} {checklist}")
