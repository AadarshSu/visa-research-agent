"""Item 67, entry 236: were stage 2's lost roles lost, or found on a page the oracle never lists?

The oracle was curated 2026-08-27 to 09-04, before every store was rebuilt on 09-25, and credits
only the pages it names. For each role one arm answered in fewer runs than the other, this prints
the oracle's answers with the sentence that decided each, then every page the losing arm picked in
3+ runs instead whose stored text matches a crude pattern for that role, with the matching passage.
Then the same for roles both arms missed equally, restricted to pages only one arm picked.
The patterns only find passages to read; the reading is a person's. No network, no model.

usage: substitutes.py    (run from the repository root, after stage 2)
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.selection_recall import load_oracle

PAT = {
    "fees": r"(£\s?\d|€\s?\d|\$\s?\d|USD\s?\d|PHP\s?\d|AED\s?\d|\d+\s?yen|visa fee)",
    "processing_times": (
        r"(processing time|takes? (up to )?\d+ (working |calendar )?(days|weeks)"
        r"|within \d+ (working )?days|\d+ hours?\)?)"
    ),
    "general_entry": (
        r"(passport[^.]{0,80}(valid for|validity|at least \d+ months)"
        r"|90 days (in|within) (any|a) 180|at the border|border control"
        r"|entry (conditions|requirements))"
    ),
    "application_route": (
        r"(apply (online|at|through|in person)|application centre|VFS|TLS|eVISA"
        r"|submit[^.]{0,60}(embassy|consulate|centre|online))"
    ),
    "document_checklist": (
        r"(supporting documents|documents (required|to (submit|bring|provide))"
        r"|bank statement|travel insurance)"
    ),
    "visa_decision": (
        r"(visa (is )?(not )?required|visa[- ]free|visa waiver|do not need a visa|need a visa)"
    ),
}


def show(arm, other, picks, texts, answers, role):
    for u, n in picks[arm].most_common():
        if n < 3 or (other and u in picks[other]) or common.credited(texts, {u}, answers):
            continue
        body = texts.get(u) or ""
        m = re.search(PAT[role], body, re.IGNORECASE)
        if m:
            s = max(0, m.start() - 110)
            print(f"  {arm} {n}/5 {u}\n     «{' '.join(body[s : m.end() + 130].split())}»")


raw = {c["corridor"]: c for c in yaml.safe_load(common.ORACLE.read_text())["corridors"]}
oracle = {r.corridor: r for r in load_oracle(common.ORACLE).corridors}
rows = [json.loads(line) for line in (common.HERE / "stage2.jsonl").open()]
runs = defaultdict(lambda: defaultdict(list))
for r in rows:
    runs[r["corridor"]][r["variant"]].append(set(r["picks"]))
V = {"emb": "emb_link_embed_neutral_c40", "today": "fusion120_blind40"}
for name in common.names():
    slug, nat, res = name.rsplit("_", 2)
    row = oracle[f"{slug}/{nat}/{res}/tourism"]
    cap = common.load(name)
    picks = {k: Counter(u for p in runs[name][v] for u in p) for k, v in V.items()}
    texts = cap["held"] | PageTextStore(common.PAGETEXT).text_for_selection(
        cap["code"], list(picks["emb"] | picks["today"])
    )
    for role in ROLE_ORDER:
        a = row.answering_urls(role)
        if not a:
            continue
        sc = {k: sum(common.credited(texts, p, a) for p in runs[name][v]) for k, v in V.items()}
        if sc["emb"] == sc["today"] == 5:
            continue
        if sc["emb"] != sc["today"]:
            loser = min(sc, key=sc.get)
            print(f"\n=== {name} {role}: embeddings {sc['emb']}/5, today {sc['today']}/5")
            for ans in raw[f"{slug}/{nat}/{res}/tourism"]["answers"][role]:
                why = " ".join(str(ans.get("why", "")).split())[:220]
                print(f"  oracle {ans['url']}\n     why: {why}")
            show(loser, None, picks, texts, a, role)
        else:
            print(f"\n=== {name} {role}: both {sc['emb']}/5")
            show("emb", "today", picks, texts, a, role)
            show("today", "emb", picks, texts, a, role)
