"""TODO item 78: whole corridors, live, with the selector shown today's list or the boosted 60 + 40.

Runs `var/item70-2026-09-24/run.py` unchanged — the path `POST /visa-plans` takes — with one thing
set from `ITEM78_ARM`:

- `today`: 120 + 40, link + text fusion (what ships);
- `boost60`: 60 + 40, with the pages live search returned fused as a third ranking
  (`selection_boost_searched`, entries 243–245).

Each arm writes under `var/item78-2026-09-30/<arm>/`, keeps its own model-usage log there, and reads
its own copy of the corpus (`corpus-<arm>/`, made by `compare.sh`), because a corridor folds what it
read back into the corpus and neither arm may change what the other, or production, reads.

Run from the repository root in the owner's terminal: `ITEM78_ARM=boost60 arm.py 3 germany/IN/GB …`
"""

import os
import runpy
import sys
from pathlib import Path

from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.resolver import CorridorResolver

HERE = Path(__file__).resolve().parent
ARM = os.environ["ITEM78_ARM"]
ARMS = {"today": (120, False), "boost60": (60, True)}
shown, boost = ARMS[ARM]

os.environ["ITEM70_OUT"] = str(HERE / ARM)
os.environ["ITEM70_CORPUS"] = str(HERE / f"corpus-{ARM}")
settings.model_usage_directory = HERE / ARM / "usage"

_init = CorridorResolver.__init__


def _arm_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
    _init(self, *args, **kwargs)
    self.selection_shown = shown
    self.selection_boost_searched = boost


CorridorResolver.__init__ = _arm_init  # type: ignore[method-assign]

RUN = HERE.parent / "item70-2026-09-24" / "run.py"
sys.argv[0] = str(RUN)
runpy.run_path(str(RUN), run_name="__main__")
