"""Entry 203: what a re-run under the widened filing-date rule recorded that the store lacked.

usage, from the repository root: .venv/bin/python var/item70-2026-09-24/veto/measure.py ZA CY HR
Compares var/corpus/<CC>.json with the copy taken just before the re-run, <CC>.before.json here.
"""

import json
import sys
from pathlib import Path

from visa_research_agent.discovery.urls import filed_date_in_path

HERE = Path(__file__).resolve().parent


def filed_before_2025(url: str) -> bool:
    filed = filed_date_in_path(url)
    return filed is not None and int(filed[1][:4]) <= 2024


for code in sys.argv[1:]:
    before_entries = json.loads((HERE / f"{code}.before.json").read_text())["entries"]
    before = {entry["url"] for entry in before_entries}
    after = json.loads(Path(f"var/corpus/{code}.json").read_text())["entries"]
    new = [entry for entry in after if entry["url"] not in before]
    filed = [entry for entry in after if filed_before_2025(entry["url"])]
    filed_new = [entry for entry in filed if entry["url"] not in before]
    print(
        f"{code}: {len(before)} -> {len(after)}, {len(new)} new; {len(filed)} held with a filing "
        f"date up to 2024, {len(filed_new)} of them new"
    )
    for entry in filed:
        if "visa" in entry["url"].lower():
            state = "new" if entry["url"] not in before else "had"
            print("   ", state, entry["status"], entry["url"])
