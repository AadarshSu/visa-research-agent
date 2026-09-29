"""Item 75 test 1 (entry 241): do embeddings find answers the pool rule keeps out?

A candidate enters the pool when its link scores, or when its stored text is among the best few per
role by keywords (`admitted_on_text`). The Malay version of Malaysia's visa list states the answer
and was kept out: its link scores -26 and its text scores only on the English word "eVisa". This
asks how often that happens, and whether embeddings would have let such a page in.

`admit.py embed` embeds the unpooled pages' stored text (Voyage). `admit.py review` prints, per
corridor and role, the top `K` unpooled pages by embedding similarity and the top `K` by keyword
text score, with their passages, for judging by hand. `admit.py rank` reports, for the pages judged
to answer (`admitted.yaml`), where each ranks among the unpooled by each signal. No model.

usage: EMBED_CAPTURES=var/embed-test1-2026-09-29/cap/new admit.py embed|review|rank
"""

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "embed-replay-2026-09-28"), str(HERE)]

import common  # noqa: E402
import grow  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402

K = 10


def rankings(name: str, connection) -> tuple[dict, dict, dict]:
    """(bodies, embedding ranking, keyword ranking) of the unpooled pages with stored text."""

    cap = common.load(name)
    bodies = grow.outside(name, cap)
    sims = grow.similarities(cap, bodies, "neutral", connection)
    scores = cap["scores"]
    embedded = {r: sorted(bodies, key=lambda u, r=r: (-sims[r][u], u)) for r in ROLE_ORDER}
    keyword = {
        r: sorted(
            (u for u in bodies if u in scores and scores[u].score_for(r) > 0),
            key=lambda u, r=r: (-scores[u].score_for(r), u),
        )
        for r in ROLE_ORDER
    }
    return bodies, embedded, keyword


def review() -> None:
    from candidates import passages

    connection = common.connect()
    for name in common.names():
        bodies, embedded, keyword = rankings(name, connection)
        print(f"\n######## {name}: {len(bodies)} unpooled pages with text")
        for role in ROLE_ORDER:
            shown = list(dict.fromkeys(embedded[role][:K] + keyword[role][:K]))
            print(f"\n=== {name} {role}")
            for u in shown:
                tag = f"emb {embedded[role].index(u) + 1}" + (
                    f", kw {keyword[role].index(u) + 1}" if u in keyword[role] else ""
                )
                print(f"- {u}  [{tag}]")
                for p in passages(bodies[u], role, limit=2):
                    print(f"    « {p[:380]} »")


def rank() -> None:
    judged = yaml.safe_load((HERE / "admitted.yaml").read_text(encoding="utf-8"))
    connection = common.connect()
    for name in common.names():
        rows = judged.get(name) or {}
        if not rows:
            continue
        bodies, embedded, keyword = rankings(name, connection)
        for role, urls in rows.items():
            for u in urls:
                e = embedded[role].index(u) + 1
                k = keyword[role].index(u) + 1 if u in keyword[role] else None
                print(
                    f"{name:18} {role:18} emb {e:4}  keyword {k or '—':>4}  of {len(bodies)}  {u}"
                )


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "embed":
        grow.embed()
    else:
        {"review": review, "rank": rank}[command]()
