"""Item 76 (entry 244): what the boosted arm picked where it lost a role today's arm answered.

For each (corridor, role) given, the oracle's answers, how often today's arm picked one, and every
page the boosted arm picked in 3+ of 5 runs, with a passage its stored text holds for the pattern.
The pattern only finds passages to read; whether one answers is judged by hand. No network.

usage: EMBED_CAPTURES=var/search-boost-2026-09-29/cap/new losses.py
"""

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "embed-replay-2026-09-28"))

import common  # noqa: E402

from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

LOSSES = [
    ("czechia_IN_GB", "visa_decision", r"(India|exempt from the visa requirement|require a visa)"),
    ("france_IN_GB", "processing_times", r"(processing time|\d+ (calendar |working )?days)"),
    ("france_PH_PH", "processing_times", r"(processing time|\d+ (calendar |working )?days)"),
]


def main() -> None:
    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    runs = collections.defaultdict(list)
    for line in (HERE / "stage2.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        runs[(record["corridor"], record["variant"])].append(record["picks"])
    for name, role, pattern in LOSSES:
        cap = common.load(name)
        slug, nat, res = name.rsplit("_", 2)
        answers = oracle[f"{slug}/{nat}/{res}/tourism"].answering_urls(role)
        boosted = collections.Counter(
            u for picks in runs[(name, "search_boost_c40")] for u in set(picks)
        )
        today = collections.Counter(
            u for picks in runs[(name, "fusion120_blind40")] for u in set(picks)
        )
        print(f"\n## {name} {role}")
        for u in sorted(answers):
            print(f"  oracle {u}  today picked {today[u]}/5")
        for u, count in boosted.most_common():
            if count < 3:
                continue
            body = cap["held"].get(u) or ""
            match = re.search(pattern, body, re.IGNORECASE)
            print(f"  boosted {count}/5 {'passage' if match else '       '} {u[:110]}")
            if match:
                s, e = max(0, match.start() - 160), match.end() + 160
                print("      «", " ".join(body[s:e].split()), "»")


if __name__ == "__main__":
    main()
