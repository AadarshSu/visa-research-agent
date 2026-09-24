"""Replay the selection call alone on a captured packet, as shipped and with anchored excerpts.

usage (repo root): replay_select.py OUT.jsonl RUNS VARIANTS CODE PACKET TARGET[,TARGET...]

VARIANTS is a comma list of `baseline` (the packet as captured) and `anchored<N>` (each excerpt is
the same head plus up to N characters of windows around the traveller's own country words, added
only where the page names them past the head). CODE is the destination's page-text code. TARGET is
a URL fragment whose pick is being counted. Calls go through Personas, one at a time.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.adjudication import _anchor_pattern, anchored_excerpt
from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.discovery.models import Corridor
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.search import resolve_corridor_countries
from visa_research_agent.discovery.selection import load_selection_prompt
from visa_research_agent.research.personas import (
    PersonasCandidateSelector,
    personas_client_from_settings,
)


def anchored(packet: dict, code: str, extra: int) -> dict:
    t = packet["traveller"]
    corridor = Corridor(
        destination_slug=t["destination"],
        passport_nationality=t["passport_nationality"],
        applying_from=t["applying_from"],
        purpose=t["purpose"],
    )
    nationality, residence = resolve_corridor_countries(corridor, get_country_registry())
    anchors = sorted({*nationality.text_tokens, *residence.text_tokens})
    pattern = _anchor_pattern(tuple(anchors))
    held = PageTextStore(settings.page_text_directory).text_for_selection(
        code, [c["url"] for c in packet["candidates"]]
    )
    out = json.loads(json.dumps(packet))
    for c in out["candidates"]:
        head = c.get("stored_excerpt")
        text = held.get(c["url"])
        if head is None or not text or pattern is None:
            continue
        if not pattern.search(text, len(head)):
            continue
        c["stored_excerpt"] = anchored_excerpt(
            text,
            anchors,
            budget=len(head) + extra,
            head_characters=len(head),
            window_characters=extra // 2,
        )
    return out


async def main() -> None:
    out, runs = Path(sys.argv[1]), int(sys.argv[2])
    variants, code, packet_path = sys.argv[3].split(","), sys.argv[4], Path(sys.argv[5])
    targets = sys.argv[6].split(",")
    base = json.loads(packet_path.read_text(encoding="utf-8"))
    selector = PersonasCandidateSelector(personas_client_from_settings())
    prompt = load_selection_prompt()
    for variant in variants:
        packet = base if variant == "baseline" else anchored(base, code, int(variant[8:]))
        text = json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
        by_id = {c["source_id"]: c["url"] for c in packet["candidates"]}
        for run in range(1, runs + 1):
            started = time.monotonic()
            row = {"packet": str(packet_path), "variant": variant, "run": run, "chars": len(text)}
            try:
                picked = [by_id.get(i, i) for i in (await selector.select(prompt, text)).source_ids]
                row["picked"] = picked
                row["hit"] = any(t in u for u in picked for t in targets)
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"[:300]
            row["seconds"] = round(time.monotonic() - started, 1)
            with out.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(
                f"{variant} run {run}: hit={row.get('hit', row.get('error'))} "
                f"({row['chars']} chars, {row['seconds']}s)",
                flush=True,
            )


asyncio.run(main())
