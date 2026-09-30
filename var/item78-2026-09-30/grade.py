"""TODO item 78: read both arms of the live comparison. No network, no model.

Per corridor and arm, over its runs: what the plan said (`visa_required`, status), how many of the
six roles the adjudicator filled and with which page, the selection call's input and seconds, and
the whole request's seconds. Then the totals, and every role whose chosen page differs between the
arms — the differences are for reading; nothing here judges which page is right (entry 68).

usage: grade.py
"""

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ("today", "boost60")
ROLES = (
    "visa_decision",
    "document_checklist",
    "application_route",
    "fees",
    "processing_times",
    "general_entry",
)


def runs(arm: str):
    for result in sorted((HERE / arm).glob("*/*/result.json")):
        record = json.loads(result.read_text(encoding="utf-8"))
        logs = list((result.parent / "recall").glob("*.json"))
        record["recall"] = json.loads(logs[0].read_text(encoding="utf-8")) if logs else None
        yield record


def main() -> None:
    table: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for arm in ARMS:
        for record in runs(arm):
            table[record["corridor"]][arm].append(record)

    totals: dict[str, Counter] = {arm: Counter() for arm in ARMS}
    numbers: dict[str, dict[str, list[float]]] = {arm: defaultdict(list) for arm in ARMS}
    picks: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    for corridor, by_arm in sorted(table.items()):
        print(f"\n## {corridor}")
        for arm in ARMS:
            for record in by_arm.get(arm, []):
                recall = record["recall"]
                filled = []
                select_in = select_s = None
                if recall:
                    for verdict in recall.get("role_verdicts", []):
                        picks[(corridor, verdict["role"], arm)][verdict.get("url")] += 1
                        if verdict.get("url"):
                            filled.append(verdict["role"])
                    for call in recall.get("model_calls", []):
                        if call["call"] == "select":
                            select_in, select_s = call["input_tokens"], call["seconds"]
                            numbers[arm]["select input"].append(select_in)
                            numbers[arm]["select seconds"].append(select_s)
                        numbers[arm][f"{call['call']} input"].append(call["input_tokens"]) if call[
                            "call"
                        ] != "select" else None
                totals[arm]["runs"] += 1
                totals[arm]["roles filled"] += len(filled)
                totals[arm]["decision filled"] += "visa_decision" in filled
                totals[arm]["checklist filled"] += "document_checklist" in filled
                totals[arm]["plan answered"] += record.get("plan") == "answered"
                totals[arm]["verified"] += record.get("status", "").endswith("verified") and not (
                    record.get("status", "").endswith("unverified")
                )
                totals[arm]["decision stated"] += record.get("visa_required") is not None
                numbers[arm]["request seconds"].append(record["seconds"])
                print(
                    f"  {arm:8} run {record['run']}: {record['research']}/{record.get('plan', '-')}"
                    f" visa_required={record.get('visa_required')} {record.get('status', '')}"
                    f" roles {len(filled)}/6 select {select_in} tok {select_s}s"
                    f" total {record['seconds']}s"
                    + (
                        f" | {str(record.get('detail') or record.get('plan_error'))[:140]}"
                        if record.get("plan") != "answered"
                        else ""
                    )
                )

    print("\n## totals")
    for arm in ARMS:
        print(f"  {arm:8} " + ", ".join(f"{k} {v}" for k, v in totals[arm].items()))
        for name, values in numbers[arm].items():
            print(
                f"           {name}: mean {statistics.mean(values):,.1f}"
                f" median {statistics.median(values):,.1f} (n={len(values)})"
            )

    print("\n## roles whose chosen page differs between the arms")
    for corridor in sorted(table):
        for role in ROLES:
            a, b = picks[(corridor, role, "today")], picks[(corridor, role, "boost60")]
            if set(a) != set(b):
                print(f"  {corridor} {role}")
                for arm, counter in (("today", a), ("boost60", b)):
                    for url, count in counter.most_common():
                        print(f"    {arm:8} {count}x {url}")


if __name__ == "__main__":
    main()
