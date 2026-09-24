"""Replay the plan call alone on a captured plan input, as entry 197 did for rule 8f.

usage (repo root): replay_plan.py OUT.jsonl RUNS PROMPT PACKET [PACKET ...]

`PROMPT` is `baseline` (the committed `extract_visa_plan.txt`) or a path to a prompt file; a
PACKET is a `plan_packet.json` that `run.py` captured. Calls go through Personas one at a time and
append one JSON line each with the draft's decision, its decision sources and explanation. The
draft is not validated or graded here: this answers only what the model decides.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

from visa_research_agent.research.openai_extraction import load_extraction_prompt
from visa_research_agent.research.personas import (
    PersonasPlanGenerator,
    personas_client_from_settings,
)


async def main() -> None:
    out, runs, variant = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    prompt = load_extraction_prompt() if variant == "baseline" else Path(variant).read_text()
    generator = PersonasPlanGenerator(personas_client_from_settings())
    for packet_path in map(Path, sys.argv[4:]):
        packet = packet_path.read_text(encoding="utf-8")
        for run in range(1, runs + 1):
            started = time.monotonic()
            row: dict[str, object] = {"packet": str(packet_path), "variant": variant, "run": run}
            try:
                draft = await generator.generate(prompt, packet)
                row.update(
                    visa_required=draft.visa_required,
                    decision_source_ids=draft.decision_source_ids,
                    explanation=draft.explanation,
                    unresolved=draft.unresolved_questions[:3],
                )
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"[:300]
            row["seconds"] = round(time.monotonic() - started, 1)
            with out.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(
                f"{packet_path.parent.parent.name}/{packet_path.parent.name} {Path(variant).name} "
                f"run {run}: {row.get('visa_required', row.get('error'))} ({row['seconds']}s)",
                flush=True,
            )


asyncio.run(main())
