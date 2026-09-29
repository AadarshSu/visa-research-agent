"""Item 75, test 2: does the embedding-ordered shortlist hold up as pools grow? No model.

A captured candidate set already holds the country's whole corpus; the pool is the part that
scores on its link or is admitted on stored text. This grows each oracle corridor's pool by adding
stored pages the pool rule turned away — a random sample, several seeds, at several sizes up to
every one of them — and re-cuts it as `sweep.py` does. The added pages carry their real (zero)
link scores and their captured stored-text scores, so they compete on the second signal only:
keywords in today's order, embeddings in the new one. The link ranking both arms share is
unchanged, and so are the 40 blind (the added pages all have text).

usage: grow.py embed     (Voyage: embeds the added pages' chunks into vectors.sqlite)
       grow.py rank      (no network: writes grow_results.json and prints the tables)
"""

import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402
from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

HERE = Path(__file__).resolve().parent
GROWTH = (0.0, 0.5, 1.0, 2.0, None)  # pages added, as a multiple of the pool; None = all of them
SEEDS = (1, 2, 3)
CUTS = (40, 80, 120)


def outside(name: str, cap: dict) -> dict[str, str]:
    """Stored text of every candidate with a stored-text score that is not in the pool."""

    data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
    pool = {c.link.url for c in cap["pool"]}
    wanted = [u for u in data["stored_scores"] if u not in pool]
    return PageTextStore(common.PAGETEXT).text_for_selection(cap["code"], wanted)


def all_candidates(name: str) -> dict:
    from visa_research_agent.discovery.models import CandidatePage

    data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
    return {row["link"]["url"]: CandidatePage.model_validate(row) for row in data["candidates"]}


def embed() -> None:
    import embed as embedder

    documents: dict[str, str] = {}
    for name in common.names():
        cap = common.load(name)
        for body in outside(name, cap).values():
            for piece in common.chunks(body):
                documents[common.text_hash(piece)] = piece
        print(f"{name}: {len(documents)} chunks so far", flush=True)
    used = embedder.run(documents, "document", 32)
    print(f"done: {used:,} tokens")


def similarities(cap: dict, bodies: dict[str, str], mode: str, connection) -> dict[str, dict]:
    """Per role, each page's best-chunk similarity to that role's query."""

    queries = {r: common.text_hash(common.query_text(cap["corridor"], r, mode)) for r in ROLE_ORDER}
    qv = common.vectors_for(connection, queries.values(), "query")
    page_chunks = {u: [common.text_hash(t) for t in common.chunks(b)] for u, b in bodies.items()}
    cv = common.vectors_for(connection, [h for hs in page_chunks.values() for h in hs], "document")
    missing = sum(1 for hs in page_chunks.values() if not any(h in cv for h in hs))
    if missing:
        sys.exit(f"{cap['name']}: {missing} pages have no vectors; run grow.py embed")

    def unit(v):
        n = sum(x * x for x in v) ** 0.5 or 1.0
        return [x / n for x in v]

    cv = {h: unit(v) for h, v in cv.items()}
    out = {}
    for role, qh in queries.items():
        q = unit(qv[qh])
        out[role] = {
            u: max(sum(a * b for a, b in zip(q, cv[h], strict=True)) for h in hs if h in cv)
            for u, hs in page_chunks.items()
        }
    return out


def rank() -> None:
    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    connection = common.connect()
    rows = []
    for name in common.names():
        slug, nat, res = name.rsplit("_", 2)
        row = oracle.get(f"{slug}/{nat}/{res}/tourism")
        if row is None:
            continue
        base = common.load(name)
        extra_bodies = outside(name, base)
        candidates = all_candidates(name)
        answers_all = {u for role in ROLE_ORDER for u in row.answering_urls(role)}
        texts = dict(base["held"]) | extra_bodies
        texts.update(
            PageTextStore(common.PAGETEXT).text_for_selection(
                base["code"], answers_all - texts.keys()
            )
        )
        every_body = dict(base["held"]) | extra_bodies
        sims = {m: similarities(base, every_body, m, connection) for m in common.QUERY_MODES}
        extra_urls = sorted(extra_bodies)
        print(f"{name}: pool {len(base['pool'])}, outside with text {len(extra_urls)}", flush=True)
        for growth in GROWTH:
            for seed in SEEDS if growth not in (0.0, None) else (0,):
                if growth is None:
                    added = extra_urls
                else:
                    size = min(len(extra_urls), round(growth * len(base["pool"])))
                    added = random.Random(f"{name}/{seed}").sample(extra_urls, size)
                cap = dict(base)
                cap["pool"] = base["pool"] + [candidates[u] for u in added]
                cap["held"] = dict(base["held"]) | {u: extra_bodies[u] for u in added}
                link, text = common.link_ranking(cap), common.text_ranking(cap)
                embedded = {
                    m: {
                        r: sorted(cap["held"], key=lambda u, r=r, m=m: (-sims[m][r][u], u))
                        for r in ROLE_ORDER
                    }
                    for m in common.QUERY_MODES
                }
                arms = {
                    "link+text (today)": [link, text],
                    "link+embed [neutral]": [link, embedded["neutral"]],
                    "link+embed [traveller]": [link, embedded["traveller"]],
                    "link+text+embed [neutral]": [link, text, embedded["neutral"]],
                }
                for arm, rankings in arms.items():
                    order = common.fused_order(cap, rankings)
                    kept = {}
                    for cut in CUTS:
                        shown = {c.link.url for c in common.shown(cap, order, cut)}
                        kept[cut] = shown
                    for role in ROLE_ORDER:
                        answers = row.answering_urls(role)
                        if not answers:
                            continue
                        position = next(
                            (
                                i
                                for i, c in enumerate(order, start=1)
                                if common.credited(texts, {c.link.url}, answers)
                            ),
                            len(order) + 1,
                        )
                        rows.append(
                            {
                                "corridor": name,
                                "growth": "all" if growth is None else growth,
                                "seed": seed,
                                "pool": len(cap["pool"]),
                                "arm": arm,
                                "role": role,
                                "position": position,
                                **{
                                    f"kept_{cut}": common.credited(texts, kept[cut], answers)
                                    for cut in CUTS
                                },
                            }
                        )
    (HERE / "grow_results.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    report(rows)


def report(rows: list[dict]) -> None:
    arms = list(dict.fromkeys(r["arm"] for r in rows))
    levels = list(dict.fromkeys(r["growth"] for r in rows))
    by = defaultdict(list)
    for r in rows:
        by[(r["arm"], r["growth"])].append(r)
    pools = defaultdict(list)
    for r in rows:
        if r["arm"] == arms[0] and r["role"] == "visa_decision":
            pools[r["growth"]].append(r["pool"])
    roles = len([r for r in by[(arms[0], 0.0)]])
    print(f"\nroles kept, of {roles}, mean over seeds; top N plus 40 blind")
    for cut in CUTS:
        print(f"\n  cut {cut}:")
        print(
            f"  {'arm':28}"
            + "".join(f"{('+' + str(g) + 'x') if g != 'all' else 'all':>10}" for g in levels)
        )
        print(
            f"  {'median pool':28}"
            + "".join(f"{statistics.median(pools[g]):>10.0f}" for g in levels)
        )
        for arm in arms:
            cells = []
            for g in levels:
                group = by[(arm, g)]
                seeds = len({r["seed"] for r in group})
                cells.append(f"{sum(r[f'kept_{cut}'] for r in group) / seeds:>10.1f}")
            print(f"  {arm:28}" + "".join(cells))
    print("\nbest answer's position: median, and roles with it past 120 (mean over seeds)")
    for arm in arms:
        cells = []
        for g in levels:
            group = by[(arm, g)]
            seeds = len({r["seed"] for r in group})
            past = sum(r["position"] > 120 for r in group) / seeds
            cells.append(f"{statistics.median(r['position'] for r in group):>5.0f}/{past:<4.1f}")
        print(f"  {arm:28}" + "".join(f"{c:>10}" for c in cells))


if __name__ == "__main__":
    {"embed": embed, "rank": rank}[sys.argv[1]]()
