"""TODO item 77 (entry 245): the selector over V4's stored-text scores with the search boost.

Registers `v4_boost_c<N>` into the 2026-09-24 replay: the pool rebuilt from V4's scores
(`rescore.load`), fused as link + text + search (entry 244's boost), cut to the top N plus the 40
best-linked pages without text, and packed by the replay's own `shipped` — so only the order and the
pool differ from its `fusion120_blind40`. Pages' text comes from `text_for_selection`, as the replay
reads it.

usage: EMBED_CAPTURES=var/search-boost-2026-09-29/cap/new replay_v4.py OUT.jsonl
       --variants v4_boost_c60 --runs 5 --concurrency 1
"""

import json
import runpy
import sys
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPLAY = HERE.parent / "selection-replay-2026-09-24"
sys.path[:0] = [str(HERE), str(REPLAY)]

import rescore  # noqa: E402
import variants  # noqa: E402

from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402

common, boost = rescore.common, rescore.boost


@cache
def v4_capture(name: str) -> dict:
    data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
    texts = rescore.bodies(data["code"], {row["link"]["url"] for row in data["candidates"]})
    cap, _ = rescore.load(name, "V4", texts)
    return cap


def v4_boost(top: int):
    def variant(cap):
        corridor = cap["corridor"]
        name = f"{cap['slug']}_{corridor.passport_nationality}_{corridor.applying_from}"
        v4 = v4_capture(name)
        rankings = [common.link_ranking(v4), common.text_ranking(v4), boost.search_ranking(v4)]
        pool = common.shown(v4, common.fused_order(v4, rankings), top)
        held = PageTextStore(common.PAGETEXT).text_for_selection(
            v4["code"], [c.link.url for c in pool]
        )
        packet, by_id, info = variants.shipped(dict(cap, held=held), pool=pool)
        info["withheld"] = len(v4["pool"]) - len(pool)
        return packet, by_id, info

    return variant


def v4_today(top: int):
    """V4's scores in today's link + text fusion, no boost — what shipping item 77 alone changes."""

    def variant(cap):
        corridor = cap["corridor"]
        name = f"{cap['slug']}_{corridor.passport_nationality}_{corridor.applying_from}"
        v4 = v4_capture(name)
        order = common.fused_order(v4, [common.link_ranking(v4), common.text_ranking(v4)])
        pool = common.shown(v4, order, top)
        held = PageTextStore(common.PAGETEXT).text_for_selection(
            v4["code"], [c.link.url for c in pool]
        )
        packet, by_id, info = variants.shipped(dict(cap, held=held), pool=pool)
        info["withheld"] = len(v4["pool"]) - len(pool)
        return packet, by_id, info

    return variant


for top in (40, 60, 80):
    variants.VARIANTS[f"v4_boost_c{top}"] = v4_boost(top)
variants.VARIANTS["v4_c120"] = v4_today(120)

sys.argv[0] = str(REPLAY / "replay.py")
runpy.run_path(str(REPLAY / "replay.py"), run_name="__main__")
