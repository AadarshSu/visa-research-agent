"""TODO item 78: how many stored pages score for `processing_times`, per captured corridor, and
how many of them are in the pool. Run before and after a lexicon change to see what it lets in.

usage: noise.py
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent / "item77-2026-09-30")]

import rescore  # noqa: E402

common = rescore.common


def main() -> None:
    total = pooled = pools = 0
    for name in common.names():
        data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
        texts = rescore.bodies(data["code"], {row["link"]["url"] for row in data["candidates"]})
        cap, _ = rescore.load(name, "SRC", texts)
        scoring = {u for u, s in cap["scores"].items() if s.score_for("processing_times") > 0}
        in_pool = {c.link.url for c in cap["pool"]}
        total += len(scoring)
        pooled += len(scoring & in_pool)
        pools += len(in_pool)
        print(
            f"{name:28} stored {len(texts):5}  score the role {len(scoring):4}"
            f"  of them pooled {len(scoring & in_pool):4}  pool {len(in_pool):4}"
        )
    print(f"total: {total} stored pages score the role, {pooled} pooled; pools sum to {pools}")


if __name__ == "__main__":
    main()
