"""TODO item 70, step 2: re-run the 14 corridors that read their authority and credited no decision.

Each run takes the path `POST /visa-plans` takes — `refuse_impossible_corridors`, then
`resolve_destination`, then `VisaPlanService.generate` — called in-process, one at a time (Personas
answered four concurrent calls with ten minutes of `504`s, OFSELF_FEEDBACK 8.22). Every run gets
empty corridor, plan-draft and recall folders of its own, so nothing is reused between runs and each
run's recall log survives the next. The evidence cache is shared, as it is in production.

Two things are kept that the route throws away:
- the reason a plan call refused (the route answers only "could not be generated safely");
- the role-adjudication packet and the model's answer, so step 4 can replay the roles call alone.

Run from the repository root, in the owner's own terminal (headless Chromium cannot start from
Claude Code's sandboxed shell):

    .venv/bin/python .claude/worktrees/angry-satoshi-3ff8bd/var/item70-2026-09-24/run.py

Resumable: a run whose `result.json` exists is skipped. `RUNS` and `CORRIDORS` can be narrowed with
arguments: `run.py 3 italy/BD/AE malta/BD/SA`.
"""

import asyncio
import json
import os
import sys
import time
import traceback
from pathlib import Path

from fastapi import HTTPException

from visa_research_agent.api.dependencies import (
    build_automatic_destinations,
    build_visa_plan_service,
)
from visa_research_agent.api.routes import refuse_impossible_corridors, resolve_destination
from visa_research_agent.api.schemas import TravellerRequest
from visa_research_agent.config.loader import get_runtime_policy
from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.resolver import CorridorResolver
from visa_research_agent.research import openai_extraction
from visa_research_agent.research.openai_extraction import LangChainStructuredPlanGenerator
from visa_research_agent.research.personas import PersonasCandidateSelector, PersonasPlanGenerator

HERE = Path(__file__).resolve().parent
# A second arm writes elsewhere: `ITEM70_OUT=fixed PYTHONPATH=<worktree>/src run.py …` runs the
# worktree's code against the same stores, so a fix is compared with the rounds above.
OUT = HERE / os.environ.get("ITEM70_OUT", "runs")

CORRIDORS = [
    "croatia/BD/AE",
    "malta/BD/AE",
    "malta/BD/SA",
    "italy/BD/AE",
    "poland/BD/AE",
    "belgium/BD/AE",
    "belgium/BD/SA",
    "slovenia/BD/AE",
    "india/BD/SA",
    "egypt/BD/SA",
    "mexico/IN/GB",
    "saudi-arabia/IN/GB",
    "united-arab-emirates/IN/GB",
    "netherlands/PH/PH",
]

# Where the packet of the run in progress is written. The resolver is built inside the service,
# so the capture hooks the method rather than the object.
CURRENT: dict[str, Path] = {}
_original = CorridorResolver._adjudicate_with_one_retry


async def _capturing(self, packet, notes):  # type: ignore[no-untyped-def]
    adjudication, attempts = await _original(self, packet, notes)
    run_dir = CURRENT.get("run")
    if run_dir is not None:
        (run_dir / "roles_packet.txt").write_text(packet, encoding="utf-8")
        (run_dir / "roles_answer.json").write_text(
            adjudication.model_dump_json(indent=2), encoding="utf-8"
        )
    return adjudication, attempts


CorridorResolver._adjudicate_with_one_retry = _capturing  # type: ignore[method-assign]


def _capture_drafts(cls):  # type: ignore[no-untyped-def]
    """Keep the plan call's raw draft: on a refusal the route keeps nothing (entry 197)."""

    original = cls.generate

    async def generate(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        draft = await original(self, *args, **kwargs)
        run_dir = CURRENT.get("run")
        if run_dir is not None:
            dump = getattr(draft, "model_dump_json", None)
            (run_dir / "plan_draft.json").write_text(
                dump(indent=2) if dump else json.dumps(draft, indent=2, default=str),
                encoding="utf-8",
            )
        return draft

    cls.generate = generate


_capture_drafts(PersonasPlanGenerator)
_capture_drafts(LangChainStructuredPlanGenerator)


def _capture_selection(cls):  # type: ignore[no-untyped-def]
    """Keep the selection call's packet and answer, so a miss can be replayed on a fixed pool."""

    original = cls.select

    async def select(self, system_prompt, packet, **kwargs):  # type: ignore[no-untyped-def]
        answer = await original(self, system_prompt, packet, **kwargs)
        run_dir = CURRENT.get("run")
        if run_dir is not None:
            (run_dir / "select_packet.txt").write_text(packet, encoding="utf-8")
            (run_dir / "select_answer.json").write_text(
                answer.model_dump_json(indent=2), encoding="utf-8"
            )
        return answer

    cls.select = select


_capture_selection(PersonasCandidateSelector)


_build_research_packet = openai_extraction.build_research_packet


def _capturing_research_packet(*args, **kwargs):  # type: ignore[no-untyped-def]
    """Keep the plan call's input, which a refusal for size never sends and so never records."""

    packet = _build_research_packet(*args, **kwargs)
    run_dir = CURRENT.get("run")
    if run_dir is not None:
        (run_dir / "plan_packet.json").write_text(packet, encoding="utf-8")
    return packet


openai_extraction.build_research_packet = _capturing_research_packet


async def run_once(key: str, number: int) -> None:
    slug, nationality, residence = key.split("/")
    run_dir = OUT / key.replace("/", "_") / str(number)
    if (run_dir / "result.json").exists():
        return
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in ("corridors", "plans", "recall"):
        (run_dir / name).mkdir(exist_ok=True)
    settings.corridor_directory = run_dir / "corridors"
    settings.plan_directory = run_dir / "plans"
    settings.recall_log_directory = run_dir / "recall"
    CURRENT["run"] = run_dir

    policy = get_runtime_policy()
    automatic = build_automatic_destinations(policy)
    service = build_visa_plan_service(policy)
    traveller = TravellerRequest(
        passport_nationality=nationality, country_of_residence=residence
    ).to_profile()

    started = time.monotonic()
    result: dict[str, object] = {"corridor": key, "run": number}
    try:
        refuse_impossible_corridors(slug, traveller)
        destination = await resolve_destination(slug, traveller, automatic)
        result["research"] = "resolved"
        try:
            plan = await service.generate(destination, traveller)
            result["plan"] = "answered"
            result["visa_required"] = plan.visa_required
            result["status"] = str(getattr(plan, "status", ""))
            (run_dir / "plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        except Exception as exc:  # the route turns these into a bare 503; keep the reason
            result["plan"] = "refused"
            result["plan_error"] = f"{type(exc).__name__}: {exc}"
            causes = []
            cause = exc.__cause__
            while cause is not None:
                causes.append(f"{type(cause).__name__}: {cause}"[:4000])
                cause = cause.__cause__
            if causes:
                result["plan_error_causes"] = causes
            reasons = getattr(exc, "reasons", None)
            if reasons:
                result["plan_reasons"] = list(reasons)
    except HTTPException as exc:
        result["research"] = "refused"
        result["detail"] = exc.detail
    except Exception as exc:
        result["research"] = "raised"
        result["detail"] = f"{type(exc).__name__}: {exc}"
        (run_dir / "traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
    finally:
        CURRENT.pop("run", None)
    result["seconds"] = round(time.monotonic() - started, 1)
    (run_dir / "result.json").write_text(
        json.dumps(result, indent=2, default=str), encoding="utf-8"
    )
    summary = result.get("visa_required", result.get("detail", ""))
    print(
        f"{key} run {number}: research {result['research']}, plan {result.get('plan', '-')}, "
        f"{str(summary)[:120]} ({result['seconds']}s)",
        flush=True,
    )


async def main() -> None:
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    # A corridor folds what it read back into the corpus, so an arm running unshipped code points
    # at a copy rather than changing the store the baseline reads.
    if os.environ.get("ITEM70_CORPUS"):
        settings.corpus_directory = Path(os.environ["ITEM70_CORPUS"])
    corridors = sys.argv[2:] or CORRIDORS
    # Round by round rather than corridor by corridor, so a run cut short leaves every corridor
    # with a first run before any has a third.
    for number in range(1, runs + 1):
        for key in corridors:
            await run_once(key, number)
    print("done", flush=True)


asyncio.run(main())
