"""TODO item 70, step 4: replay the role-adjudication call alone on a captured packet.

usage: replay_roles.py OUT.jsonl RUNS PROMPT_VARIANT PACKET [PACKET ...]

`PROMPT_VARIANT` is `baseline` (the committed `adjudicate_roles.txt`) or a path to a prompt file.
A packet is a `runs/<corridor>/<n>/roles_packet.txt` captured by `run.py`, or a variant of one.
Calls go through Personas, one at a time (OFSELF_FEEDBACK 8.22). Appends one JSON line per call
with what the model said about `visa_decision`, so a variant is graded on several runs of one
fixed input with nothing upstream moving. Run from the repository root so `.env` loads.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from visa_research_agent.config.loader import get_runtime_policy
from visa_research_agent.discovery.adjudication import load_adjudication_prompt
from visa_research_agent.discovery.cli import build_role_adjudicator


async def main() -> None:
    out = Path(sys.argv[1])
    runs = int(sys.argv[2])
    variant = sys.argv[3]
    packets = [Path(p) for p in sys.argv[4:]]
    prompt = load_adjudication_prompt() if variant == "baseline" else Path(variant).read_text()
    adjudicator = build_role_adjudicator(get_runtime_policy())
    assert adjudicator is not None
    for packet_path in packets:
        packet = packet_path.read_text(encoding="utf-8")
        for run in range(1, runs + 1):
            started = time.monotonic()
            row: dict[str, object] = {
                "packet": str(packet_path),
                "variant": variant,
                "run": run,
            }
            try:
                answer = await adjudicator.adjudicate(prompt, packet)
                # ROLE=<role> records another role's choice (entry 223); the decision by default.
                role = os.environ.get("ROLE", "visa_decision")
                decision = [c for c in answer.choices if c.role == role]
                row["decision"] = decision[0].source_id if decision else None
                row["reason"] = decision[0].reason if decision else ""
                row["tools"] = [t.source_id for t in answer.tools if t.role == role]
            except Exception as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"[:300]
            row["seconds"] = round(time.monotonic() - started, 1)
            with out.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(
                f"{packet_path.parent.parent.name}/{packet_path.parent.name} {variant} run {run}: "
                f"{row.get('decision', row.get('error'))} ({row['seconds']}s)",
                flush=True,
            )


asyncio.run(main())
