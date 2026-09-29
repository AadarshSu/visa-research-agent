"""Oracle refresh, 2026-09-29 (DECISIONS entry 239): what to read, and the passage to read it by.

Per corridor and role, candidates are the top 8 by each of three selector-independent rankings of
the captured pool — link, stored-text keywords, embedding similarity — plus every page any recorded
replay run picked (so every compared arm is fully judged). A (page, role) pair is kept for reading
only when its stored text holds a passage of the role's kind; the passage is printed with its
neighbourhood. Pages the oracle already names for the role are skipped. No network, no model.

usage: candidates.py > review.txt    (from the repository root)
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "embed-replay-2026-09-28"))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.selection_recall import load_oracle, same_pages  # noqa: E402

K = 8
MIRRORS: list = []
RUNS = [
    "var/embed-replay-2026-09-28/stage2.jsonl",
    "var/embed-replay-2026-09-28/excerpt.jsonl",
    "var/selection-replay-2026-09-24/results.jsonl",
]
SIGNAL = {
    "visa_decision": (
        r"(do(es)? not (need|require) a visa|visa[- ]free|visa exemption"
        r"|exempt(ed)? from (the )?visa|require[sd]? a visa|need a visa|visa (is )?required"
        r"|visa on arrival|visa waiver)"
    ),
    "document_checklist": (
        r"(passport[^.]{0,200}(photo|photograph|bank statement|itinerary|insurance)"
        r"|(photo|photograph|bank statement|itinerary|insurance)[^.]{0,200}passport"
        r"|supporting documents|required documents|documents? (required|you (will )?need))"
    ),
    "application_route": r"(apply (online|in person|at|through|via)|application cent(re|er)"
    r"|submit (your|the) application|VFS|TLScontact|BLS|book an appointment|eVISA|e-visa)",
    "fees": r"((£|€|\$|USD|EUR|CAD|SGD|AED|PHP|JPY|INR|SEK)\s?\d|\d+\s?(euros?|yen|dirhams?)"
    r"|visa fee|application fee|processing fee)",
    "processing_times": r"(processing time|within \d+ (working |calendar |business )?days"
    r"|\d+ (working |calendar |business )?(days|weeks)[^.]{0,80}(process|decision|decide)"
    r"|(process|decision|decide)[^.]{0,80}\d+ (working |calendar |business )?(days|weeks))",
    "general_entry": r"(passport[^.]{0,120}valid[^.]{0,80}(months|beyond|after)"
    r"|90 days (in|within) (any|a) 180|border (control|check|guard)|immigration (check|control"
    r"|inspection)|entry (conditions|requirements)|landing permission|return ticket"
    r"|onward (ticket|travel))",
}


def passages(body: str, role: str, limit: int = 3) -> list[str]:
    out, last = [], -10_000
    for m in re.finditer(SIGNAL[role], body, re.IGNORECASE):
        if m.start() - last < 500:
            continue
        last = m.start()
        s, e = max(0, m.start() - 220), min(len(body), m.end() + 260)
        out.append(" ".join(body[s:e].split()))
        if len(out) == limit:
            break
    return out


def main() -> None:
    oracle = load_oracle(common.ORACLE)
    global MIRRORS
    MIRRORS = oracle.mirrors
    picks = defaultdict(set)
    for f in RUNS:
        for line in open(f):
            r = json.loads(line)
            if r.get("arm", "new") == "new":
                picks[r["corridor"]] |= set(r["picks"])
    con = common.connect()
    total = 0
    for name in common.names():
        cap = common.load(name)
        slug, nat, res = name.rsplit("_", 2)
        row = oracle.for_corridor(f"{slug}/{nat}/{res}/tourism")
        rks = [
            common.link_ranking(cap),
            common.text_ranking(cap),
            common.embed_ranking(cap, "neutral", con),
        ]
        held = {r: len(v) for r, v in row.answers.items()}
        print(f"\n######## {name}  (answers held: {held}; unanswered: {sorted(row.unanswered)})")
        for role in ROLE_ORDER:
            cands = set(picks[name])
            for rk in rks:
                cands |= set(rk[role][:K])
            answers = row.answering_urls(role)
            cands = sorted(u for u in cands if cap["held"].get(u) and u not in answers)
            # The grader already credits the same page at another address (`same_pages`), so a
            # candidate identical to an answer needs no reading, and identical candidates are read
            # once, under the first address, with the others listed beside it.
            groups = same_pages(
                set(cands) | answers, {u: t for u, t in cap["held"].items() if t}, MIRRORS
            )
            seen, shown = set(), []
            for u in cands:
                if u in seen or groups[u] & answers:
                    continue
                twins = sorted(groups[u] - {u})
                seen |= groups[u]
                p = passages(cap["held"][u], role)
                if p:
                    shown.append((u + (f"  (= {', '.join(twins)})" if twins else ""), p))
            if not shown:
                continue
            print(f"\n=== {name} {role}  ({len(shown)})")
            for u, ps in shown:
                total += 1
                print(f"- {u}")
                for p in ps:
                    print(f"    « {p} »")
    print(f"\n{total} pairs to read", file=sys.stderr)


main()
