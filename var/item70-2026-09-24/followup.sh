#!/bin/zsh
# TODO item 70: after the three baseline rounds.
# 1. Redo the baseline runs that Personas broke (HTTP 500 on 2026-09-24 14:02–14:04 UTC) — they
#    measured an outage, not the research. `run.py` skips any run whose result.json exists.
# 2. Run the worktree's fixes against a copy of the corpus, three times on each corridor they
#    target, so the fold-back cannot change the store the baseline reads.
# Run from the repository root, in the owner's terminal.
set -e
HERE="${0:A:h}"
WORKTREE="${HERE:h:h}"
SCRATCH="$1"
for run in belgium_BD_SA/2 india_BD_SA/2 egypt_BD_SA/2 slovenia_BD_AE/2 mexico_IN_GB/2; do
  rm -f "$HERE/runs/$run/result.json"
done
.venv/bin/python "$HERE/run.py" 3

rm -rf "$SCRATCH/corpus-fixed"
cp -R var/corpus "$SCRATCH/corpus-fixed"
ITEM70_OUT=fixed ITEM70_CORPUS="$SCRATCH/corpus-fixed" PYTHONPATH="$WORKTREE/src" \
  .venv/bin/python "$HERE/run.py" 3 \
  netherlands/PH/PH malta/BD/AE malta/BD/SA united-arab-emirates/IN/GB
