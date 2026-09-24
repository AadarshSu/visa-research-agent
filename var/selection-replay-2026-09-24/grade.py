"""Grade replayed selections against the oracle: role recall per run, and per-role stability.

usage: grade.py FILE.jsonl [--detail] [--roles]
"""

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.discovery.models import ROLE_ORDER
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.selection_recall import load_oracle

ROOT = Path("/Users/aadarsh/Documents/Visa Research Agent")
oracle = {row.corridor: row for row in load_oracle(ROOT / "oracle/selection_oracle.yaml").corridors}


def key_of(name):
    slug, nat, res = name.rsplit("_", 2)
    return f"{slug}/{nat}/{res}/tourism"


ALIAS = "--alias" in sys.argv


TEXT = {"new": ROOT / "var/pagetext", "old": ROOT / "var/_backup_before_pilot_2026-09-25/pagetext"}
CODES = {}
_text_cache = {}


def text_of(arm, name, urls):
    if name not in CODES:
        CODES[name] = get_country_registry().by_slug(name.rsplit("_", 2)[0]).code
    key = (arm, name)
    cache = _text_cache.setdefault(key, {})
    missing = [u for u in urls if u not in cache]
    if missing:
        got = PageTextStore(TEXT[arm]).text_for_selection(CODES[name], missing)
        for u in missing:
            cache[u] = got.get(u)
    return {u: cache[u] for u in urls}


def redirect_target(url):
    parts = urlsplit(url)
    if "update_language" not in parts.path:
        return None
    target = parse_qs(parts.query).get("redirect", [None])[0]
    return f"{parts.scheme}://{parts.netloc}{target}" if target else None


def credited(arm, name, picked, answers):
    """Picks that are an answering page: the address itself, or (with --alias) the same stored
    text at another address, or a language switch redirecting to it."""
    if picked & answers:
        return True
    if not ALIAS:
        return False
    for u in picked:
        t = redirect_target(u)
        if t and (
            t in answers
            or t.replace("://www.", "://") in {a.replace("://www.", "://") for a in answers}
        ):
            return True
    texts = text_of(arm, name, list(picked | answers))
    answer_texts = {texts[a] for a in answers if texts.get(a)}
    return any(texts.get(u) in answer_texts for u in picked if texts.get(u))


rows = [json.loads(line) for f in sys.argv[1:] if f.endswith(".jsonl") for line in open(f)]
rows = [r for r in rows if not r.get("failed")]
detail = "--detail" in sys.argv
by_arm = defaultdict(list)
for r in rows:
    by_arm[(r["arm"], r["variant"])].append(r)

for (arm, variant), rs in sorted(by_arm.items()):
    hits = defaultdict(lambda: defaultdict(list))  # corridor -> role -> [bool per run]
    per_run = defaultdict(int)
    corridors = sorted({r["corridor"] for r in rs})
    total_roles = 0
    for name in corridors:
        row = oracle[key_of(name)]
        total_roles += len(row.answers)
    for r in rs:
        row = oracle[key_of(r["corridor"])]
        picked = set(r["picks"])
        for role in ROLE_ORDER:
            if row.answers.get(role):
                found = credited(r["arm"], r["corridor"], picked, row.answering_urls(role))
                hits[r["corridor"]][role].append(found)
    runs = defaultdict(int)
    for r in rs:
        runs[r["corridor"]] += 1
    n = min(runs.values())
    # expected roles found per run = sum over corridor-roles of hit rate
    expected = sum(sum(v) / len(v) for c in hits.values() for v in c.values())
    always = sum(1 for c in hits.values() for v in c.values() if all(v))
    never = sum(1 for c in hits.values() for v in c.values() if not any(v))
    some = sum(1 for c in hits.values() for v in c.values() if any(v) and not all(v))
    # per-run totals where every corridor has run i
    totals = []
    for i in range(n):
        t = 0
        for name in corridors:
            rr = [x for x in rs if x["corridor"] == name and x["run"] == i]
            if not rr:
                break
            row = oracle[key_of(name)]
            picked = set(rr[0]["picks"])
            t += sum(
                1
                for role in ROLE_ORDER
                if row.answers.get(role)
                and credited(rr[0]["arm"], name, picked, row.answering_urls(role))
            )
        else:
            totals.append(t)
    CORE = ("visa_decision", "document_checklist")
    core = sum(sum(v) / len(v) for c in hits.values() for role, v in c.items() if role in CORE)
    core_total = sum(1 for c in hits.values() for role in c if role in CORE)
    picks = statistics.mean(len(r["picks"]) for r in rs)
    tokens = [r["input_tokens"] for r in rs if r["input_tokens"]]
    secs = statistics.mean(r["seconds"] for r in rs)
    mean_input = statistics.mean(tokens) / 1000 if tokens else 0
    print(
        f"{arm:4} {variant:22} corridors {len(corridors):2} runs/corr {n}"
        f"  roles/run {expected:5.1f} of {total_roles}"
        f"  core {core:4.1f}/{core_total} other {expected - core:4.1f}/{total_roles - core_total}"
        f"  per-run totals {totals}  always {always} sometimes {some} never {never}"
        f"  picks {picks:4.1f}  input {mean_input:5.1f}k  {secs:4.1f}s"
    )
    if detail:
        for name in corridors:
            cells = []
            for role in ROLE_ORDER:
                v = hits[name].get(role)
                if v is None:
                    continue
                cells.append(f"{role[:10]}:{sum(v)}/{len(v)}")
            pool = rs[[x["corridor"] for x in rs].index(name)].get("pool")
            print(f"     {name:28} pool {pool:4}  " + "  ".join(cells))
