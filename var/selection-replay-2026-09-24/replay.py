"""Replay only the selection call over captured candidate sets, several times each.

The pool, source ids and packet are built exactly as `CorridorResolver._choose_what_to_read`
builds them; a variant may change what the packet holds. Results append to OUT (JSONL), and a
(arm, variant, corridor, run) already there is skipped, so it resumes.

usage: replay.py OUT --arms new,old --variants baseline --runs 3 [--only japan_IN_GB,...]
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

import variants

from visa_research_agent.discovery.adjudication import UsageRecorder
from visa_research_agent.discovery.models import CandidatePage, Corridor, RoleScores
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.selection import (
    SelectionError,
    admitted_on_text,
    load_selection_prompt,
    validated_selection,
)
from visa_research_agent.research.personas import (
    PersonasCandidateSelector,
    personas_client_from_settings,
)

ROOT = Path("/Users/aadarsh/Documents/Visa Research Agent")
SCRATCH = Path(__file__).parent
TEXT = {
    "new": ROOT / "var/pagetext",
    "old": ROOT / "var/_backup_before_pilot_2026-09-25/pagetext",
}


def load_capture(arm: str, name: str) -> dict:
    data = json.loads((SCRATCH / "cap" / arm / f"{name}.json").read_text(encoding="utf-8"))
    candidates = {}
    for row in data["candidates"]:
        c = CandidatePage.model_validate(row)
        candidates[c.link.url] = c
    scores = {u: RoleScores.model_validate(s) for u, s in data["stored_scores"].items()}
    corridor = Corridor.model_validate(data["corridor"])
    admitted = admitted_on_text(
        [c for c in candidates.values() if c.best_combined()[1] <= 0], scores
    )
    pool = [c for c in candidates.values() if c.best_combined()[1] > 0] + admitted
    held = PageTextStore(TEXT[arm]).text_for_selection(data["code"], [c.link.url for c in pool])
    return {
        "corridor": corridor,
        "slug": data["destination_slug"],
        "pool": pool,
        "held": held,
        "scores": scores,
        "admitted": admitted,
    }


def already(out: Path) -> set[tuple]:
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            if not r.get("failed"):
                done.add((r["arm"], r["variant"], r["corridor"], r["run"]))
    return done


STREAK = [0]


async def one(selector, prompt, job, out, lock, sem):
    arm, variant, name, run, packet, by_id, info = job
    async with sem:
        if STREAK[0] >= 3:
            return
        usage = UsageRecorder()
        started = time.monotonic()
        failed = None
        picks = []
        try:
            selection = await selector.select(prompt, packet, usage=usage)
            chosen, _ = validated_selection(selection, by_id)
            picks = [by_id[s].link.url for s in chosen]
        except SelectionError as exc:
            failed = str(exc)[:300]
        STREAK[0] = STREAK[0] + 1 if failed else 0
        if STREAK[0] == 3:
            print("three consecutive failures: stopping", flush=True)
        row = {
            "arm": arm,
            "variant": variant,
            "corridor": name,
            "run": run,
            "picks": picks,
            "seconds": round(time.monotonic() - started, 3),
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "packet_characters": len(packet),
            "failed": failed,
            **info,
        }
        async with lock:
            with out.open("a") as f:
                f.write(json.dumps(row) + "\n")
        print(
            f"{arm} {variant} {name} #{run}: {len(picks)} picks {row['seconds']}s "
            f"{row['input_tokens']} in {'FAILED ' + failed if failed else ''}",
            flush=True,
        )


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--arms", default="new")
    p.add_argument("--variants", default="baseline")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--only", default="")
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--dry", action="store_true")
    a = p.parse_args()
    out = Path(a.out)
    done = already(out)
    prompt = load_selection_prompt()
    jobs = []
    names = sorted(x.stem for x in (SCRATCH / "cap" / "new").glob("*.json"))
    if a.only:
        names = [n for n in names if n in a.only.split(",")]
    for arm in a.arms.split(","):
        for name in names:
            cap = load_capture(arm, name)
            for variant in a.variants.split(","):
                packet, by_id, info = variants.VARIANTS[variant](cap)
                for run in range(a.runs):
                    if (arm, variant, name, run) not in done:
                        jobs.append((arm, variant, name, run, packet, by_id, info))
    print(f"{len(jobs)} calls to make", flush=True)
    if a.dry:
        for j in jobs[:: a.runs]:
            print(j[0], j[1], j[2], len(j[4]), j[6])
        return
    selector = PersonasCandidateSelector(personas_client_from_settings())
    lock, sem = asyncio.Lock(), asyncio.Semaphore(a.concurrency)
    await asyncio.gather(*(one(selector, prompt, j, out, lock, sem) for j in jobs))


asyncio.run(main())
