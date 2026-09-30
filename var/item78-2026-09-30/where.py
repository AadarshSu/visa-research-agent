"""TODO item 78: where one page sits in the order the selector's list is cut from. No network.

For each captured corridor named, with item 77's stored-text scores (`rescore.load(…, "V4")`): the
page's place in today's fusion and the boosted one, its rank per role in each ranking, and the
smallest `shown` at which `shown_to_selector` offers it.

usage: EMBED_CAPTURES=var/search-boost-2026-09-29/cap/new where.py URL_SUFFIX corridor_name...
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "item77-2026-09-30")]

import rescore  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.selection import fusion_order, shown_to_selector  # noqa: E402

common = rescore.common


def main() -> None:
    suffix, names = sys.argv[1], sys.argv[2:]
    for name in names:
        data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
        texts = rescore.bodies(data["code"], {row["link"]["url"] for row in data["candidates"]})
        cap, _ = rescore.load(name, "V4", texts)
        pool, scores = cap["pool"], cap["scores"]
        page = next(c for c in pool if c.link.url.endswith(suffix))
        url = page.link.url
        searched = [c for c in pool if c.searched]
        print(f"\n## {name}: {url}")
        print(
            f"  pool {len(pool)}, search returned {len(searched)} of them; this page searched="
            f"{page.searched}, stored text={'yes' if url in cap['held'] else 'no'}"
        )
        for role in ROLE_ORDER:
            link = sorted(
                (c for c in pool if c.link_scores.score_for(role) > 0),
                key=lambda c, r=role: (-c.link_scores.score_for(r), c.link.url),
            )
            text = sorted(
                (
                    c
                    for c in pool
                    if c.link.url in scores and scores[c.link.url].score_for(role) > 0
                ),
                key=lambda c, r=role: (-scores[c.link.url].score_for(r), c.link.url),
            )
            place = lambda ranking, page=page: next(  # noqa: E731
                (f"{i} of {len(ranking)}" for i, c in enumerate(ranking, 1) if c is page),
                "unranked",
            )
            print(f"  {role:20} link {place(link):>12}   text {place(text):>12}")
        for boost in (False, True):
            order = fusion_order(pool, scores, boost_searched=boost)
            position = order.index(page) + 1
            ahead = sum(1 for c in order[: position - 1] if c.searched)
            first = next(
                shown
                for shown in range(1, len(pool) + 1)
                if page
                in shown_to_selector(
                    pool, scores, cap["held"].__contains__, shown=shown, boost_searched=boost
                )[0]
            )
            print(
                f"  {'boosted' if boost else 'today  '}: position {position} of {len(order)}"
                f" ({ahead} search-returned pages ahead of it); first shown at a cut of {first}"
            )


if __name__ == "__main__":
    main()
