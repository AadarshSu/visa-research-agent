"""Stage 2 of item 67: the selector itself, over each embedding arm's cut, through Personas.

Registers one variant per embedding arm into the 2026-09-24 replay's `variants.VARIANTS`, then
runs that replay unchanged, so pool, source ids and packet are built exactly as before. Takes the
same arguments as `replay.py`; grade the output with that directory's `grade.py --alias`.

    emb_<arms>_<mode>, e.g. emb_link_text_embed_traveller, emb_link_embed_neutral, emb_embed_neutral

usage: replay_embed.py OUT.jsonl --variants fusion120_blind40,emb_link_text_embed_neutral --runs 5
       --concurrency 1
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPLAY = HERE.parent / "selection-replay-2026-09-24"
sys.path[:0] = [str(HERE), str(REPLAY)]

import common  # noqa: E402
import variants  # noqa: E402

_connection = common.connect()


def embedding_variant(parts: tuple[str, ...], mode: str):
    def variant(cap):
        name = (
            f"{cap['slug']}_{cap['corridor'].passport_nationality}_{cap['corridor'].applying_from}"
        )
        cap = dict(cap, name=name)
        rankings = []
        if "link" in parts:
            rankings.append(common.link_ranking(cap))
        if "text" in parts:
            rankings.append(common.text_ranking(cap))
        embedded = common.embed_ranking(cap, mode, _connection)
        if embedded is None:
            raise SystemExit(f"no vectors for {name}: run embed.py first")
        rankings.append(embedded)
        pool = common.shown(cap, common.fused_order(cap, rankings))
        packet, by_id, info = variants.shipped(cap, pool=pool)
        info["withheld"] = len(cap["pool"]) - len(pool)
        return packet, by_id, info

    return variant


for parts in (("embed",), ("link", "embed"), ("link", "text", "embed")):
    for mode in common.QUERY_MODES:
        key = "emb_" + "_".join(parts) + "_" + mode
        variants.VARIANTS[key] = embedding_variant(parts, mode)

sys.argv[0] = str(REPLAY / "replay.py")
runpy.run_path(str(REPLAY / "replay.py"), run_name="__main__")
