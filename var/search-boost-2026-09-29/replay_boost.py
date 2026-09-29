"""TODO item 76: the selector itself, over the search-boosted cut, through Personas (entry 244).

Registers `search_boost_c<N>` — today's link + text fusion with the pages live search returned as a
third ranking (`boost.search_ranking`), cut to the top N plus the 40 best-linked pages with no
stored text — into the 2026-09-24 replay's variants, then runs that replay unchanged. Compare with
its `fusion120_blind40`, today's shipped cut. Point `EMBED_CAPTURES` at the captures to replay.

usage: EMBED_CAPTURES=var/search-boost-2026-09-29/cap/new replay_boost.py OUT.jsonl
       --variants fusion120_blind40,search_boost_c40,search_boost_c60 --runs 5 --concurrency 1
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPLAY = HERE.parent / "selection-replay-2026-09-24"
sys.path[:0] = [str(HERE.parent / "embed-replay-2026-09-28"), str(REPLAY), str(HERE)]

import boost  # noqa: E402
import common  # noqa: E402
import variants  # noqa: E402


def boosted(top: int):
    def variant(cap):
        rankings = [common.link_ranking(cap), common.text_ranking(cap), boost.search_ranking(cap)]
        pool = common.shown(cap, common.fused_order(cap, rankings), top)
        packet, by_id, info = variants.shipped(cap, pool=pool)
        info["withheld"] = len(cap["pool"]) - len(pool)
        return packet, by_id, info

    return variant


for top in (20, 30, 40, 60, 80):
    variants.VARIANTS[f"search_boost_c{top}"] = boosted(top)

sys.argv[0] = str(REPLAY / "replay.py")
runpy.run_path(str(REPLAY / "replay.py"), run_name="__main__")
