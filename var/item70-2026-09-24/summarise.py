"""TODO item 70, step 3: what each run did, and what the adjudicator said about the decision.

usage: summarise.py [--reasons] [corridor-fragment ...]
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs"


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    reasons = "--reasons" in sys.argv
    by_corridor: dict[str, list[dict]] = defaultdict(list)
    for result_path in sorted(RUNS.glob("*/*/result.json")):
        result = json.loads(result_path.read_text())
        if args and not any(a in result["corridor"] for a in args):
            continue
        recall = next((result_path.parent / "recall").glob("*.json"), None)
        record = json.loads(recall.read_text()) if recall else {}
        result["_record"] = record
        by_corridor[result["corridor"]].append(result)
    for corridor, results in by_corridor.items():
        line = []
        for r in sorted(results, key=lambda r: r["run"]):
            if r["research"] != "resolved":
                line.append("refused")
            elif r.get("plan") == "answered":
                vr = r.get("visa_required")
                word = "required" if vr else "no visa" if vr is False else "null"
                line.append(f"{word}/{r.get('status', '')}")
            else:
                line.append("plan-refused")
        print(f"{corridor:32} {' | '.join(line)}")
        if not reasons:
            continue
        for r in sorted(results, key=lambda r: r["run"]):
            record = r["_record"]
            fetched = [c["url"] for c in record.get("candidates", []) if c.get("fetched")]
            print(f"  run {r['run']}: {record.get('cause')} — fetched {len(fetched)}")
            for v in record.get("role_verdicts", []):
                if v["role"] == "visa_decision":
                    print(f"    [{v['kind']}] {v.get('source_id')} {v.get('url')}")
                    print(f"      {v['reason']}")
            if r.get("plan_error"):
                print(f"    plan: {r['plan_error'][:300]}")


main()
