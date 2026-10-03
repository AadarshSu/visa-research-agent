"""Corridors for purposes other than tourism: business, study and transit.

Item 63's runner (`var/item70-2026-09-24/run.py`) with the purpose added to the key:
`slug/NAT/RES/purpose`. Everything it captures is the same — the roles packet and answer, the
selection packet and answer, the plan packet and draft — so a miss can be replayed with that
folder's `replay_*.py`. Every run gets empty corridor, plan and recall folders; the evidence
cache is shared, as in production.

Run from the repository root, in the owner's own terminal:

    .venv/bin/python var/purposes-2026-10-03/run.py 1 germany/IN/GB/business ...
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
OUT = HERE / os.environ.get("PURPOSE_OUT", "runs")

# Item 63's ten, IN/IN, whose tourism answers the owner has graded; the two reference corridors;
# and US passports studying in Schengen, where the EU tier knows only short stays.
TEN = [
    "australia",
    "china",
    "new-zealand",
    "south-africa",
    "south-korea",
    "spain",
    "switzerland",
    "thailand",
    "turkey",
    "vietnam",
]
CORRIDORS = (
    [f"{slug}/IN/IN/{purpose}" for purpose in ("business", "study", "transit") for slug in TEN]
    + [
        f"{slug}/IN/GB/{purpose}"
        for purpose in ("business", "study", "transit")
        for slug in ("germany", "japan")
    ]
    + ["france/US/US/study", "germany/US/US/study", "spain/US/US/study"]
)

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
    slug, nationality, residence, purpose = key.split("/")
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
        passport_nationality=nationality,
        country_of_residence=residence,
        travel_purpose=purpose,
    ).to_profile()

    started = time.monotonic()
    result: dict[str, object] = {"corridor": key, "run": number, "purpose": purpose}
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
