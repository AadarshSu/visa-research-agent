"""TODO item 78: does the stored-text score see the oracle's processing-time answers? No network.

For every captured oracle corridor, each page the oracle says answers `processing_times`: what the
shipped `score_body` gives it for that role, the phrase that earned it, and — where it earned
nothing — every passage naming a number of days or weeks, to read for the words it does use.

usage: times.py
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "item77-2026-09-30")]

import rescore  # noqa: E402

from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

common = rescore.common
DURATION = re.compile(r"(?i)\b\d+\s+(calendar |working |business )?(days|weeks|months)\b")


def main() -> None:
    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    seen: set[str] = set()
    scored = unscored = 0
    for name in common.names():
        slug, nat, res = name.rsplit("_", 2)
        row = oracle.get(f"{slug}/{nat}/{res}/tourism")
        answers = row.answering_urls("processing_times") if row else set()
        if not answers:
            continue
        data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
        texts = rescore.bodies(data["code"], answers)
        cap, _ = rescore.load(name, "SRC", texts)
        print(f"\n## {name}")
        for url in sorted(answers):
            if url not in texts:
                print(f"  no stored text   {url}")
                continue
            score = cap["scores"].get(url)
            value = score.score_for("processing_times") if score else 0.0
            why = (score.signals.get("processing_times") or [""])[0] if score else ""
            print(f"  {value:6.1f} {why:40} {url}")
            scored += value > 0
            unscored += value <= 0
            if value <= 0 and url not in seen:
                body = texts[url][0]
                for match in list(DURATION.finditer(body))[:6]:
                    s, e = max(0, match.start() - 110), match.end() + 60
                    print("        «", " ".join(body[s:e].split()), "»")
            seen.add(url)
    print(f"\nanswer pages with stored text: {scored} scored for the role, {unscored} did not")


if __name__ == "__main__":
    main()
