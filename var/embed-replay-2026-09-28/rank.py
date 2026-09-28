"""Stage 1 of item 67: which arm's cut keeps the oracle's answers? No network, no model.

For each oracle corridor and arm, the pool is fused and cut exactly as the shipped
`fusion120_blind40` cut is, and an oracle role counts as reachable when an answering page (or the
same stored text at another address, as `grade.py --alias` credits) survives the cut. Also reports
where the best answering page sits in the fused order, which moves before the cut count does.

usage: rank.py [--detail]    (writes rank_results.json beside this file)
"""

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402
from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

CORE = ("visa_decision", "document_checklist")


def arms(cap, connection) -> dict[str, list]:
    link, text = common.link_ranking(cap), common.text_ranking(cap)
    out = {"link+text (today)": [link, text]}
    for mode in common.QUERY_MODES:
        embedded = common.embed_ranking(cap, mode, connection)
        if embedded is None:
            continue
        out[f"embed only [{mode}]"] = [embedded]
        out[f"link+embed [{mode}]"] = [link, embedded]
        out[f"link+text+embed [{mode}]"] = [link, text, embedded]
    return out


def main() -> None:
    detail = "--detail" in sys.argv
    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    connection = common.connect()
    totals = defaultdict(lambda: defaultdict(float))
    positions = defaultdict(list)
    report = []
    missing_vectors = []
    for name in common.names():
        slug, nat, res = name.rsplit("_", 2)
        row = oracle.get(f"{slug}/{nat}/{res}/tourism")
        if row is None:
            continue
        cap = common.load(name)
        answer_urls = {u for role in ROLE_ORDER for u in row.answering_urls(role)}
        texts = dict(cap["held"])
        texts.update(
            PageTextStore(common.PAGETEXT).text_for_selection(
                cap["code"], answer_urls - texts.keys()
            )
        )
        corridor_arms = arms(cap, connection)
        if len(corridor_arms) == 1:
            missing_vectors.append(name)
        for arm, rankings in corridor_arms.items():
            order = common.fused_order(cap, rankings)
            cut = {c.link.url for c in common.shown(cap, order)}
            for role in ROLE_ORDER:
                answers = row.answering_urls(role)
                if not answers:
                    continue
                bodies = [texts.get(a) for a in answers]
                kind = (
                    "no stored text"
                    if not any(bodies)
                    else "English text"
                    if any(b and common.is_english(b) for b in bodies)
                    else "other-language text"
                )
                found = common.credited(texts, cut, answers)
                rank = next(
                    (
                        i
                        for i, c in enumerate(order, start=1)
                        if common.credited(texts, {c.link.url}, answers)
                    ),
                    None,
                )
                totals[arm]["roles"] += 1
                totals[arm]["found"] += found
                totals[arm][f"roles:{kind}"] += 1
                totals[arm][f"found:{kind}"] += found
                if role in CORE:
                    totals[arm]["core"] += 1
                    totals[arm]["core found"] += found
                positions[arm].append(rank if rank is not None else len(order) + 1)
                report.append(
                    {
                        "corridor": name,
                        "arm": arm,
                        "role": role,
                        "kind": kind,
                        "reachable": found,
                        "best_answer_position": rank,
                        "pool": len(order),
                    }
                )
    if missing_vectors:
        print(f"no vectors for {len(missing_vectors)} corridors (run embed.py):", missing_vectors)
    kinds = ("English text", "other-language text", "no stored text")
    print(f"{'arm':30} {'reachable':>12} {'core':>8} {'median pos':>11}   " + "   ".join(kinds))
    for arm, t in totals.items():
        split = "   ".join(f"{int(t[f'found:{k}'])}/{int(t[f'roles:{k}'])}" for k in kinds)
        print(
            f"{arm:30} {int(t['found']):>5}/{int(t['roles']):<6} "
            f"{int(t['core found']):>3}/{int(t['core']):<4} "
            f"{statistics.median(positions[arm]):>11.0f}   {split}"
        )
    if detail:
        by_key = defaultdict(dict)
        for r in report:
            by_key[(r["corridor"], r["role"])][r["arm"]] = r["best_answer_position"]
        print("\nbest answering page's position, per corridor and role:")
        for (corridor, role), per_arm in sorted(by_key.items()):
            cells = "  ".join(f"{arm.split(' [')[0][:18]}:{pos}" for arm, pos in per_arm.items())
            print(f"  {corridor:26} {role:18} {cells}")
    out = Path(__file__).resolve().parent / "rank_results.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(f"\nper-role rows written to {out}")


main()
