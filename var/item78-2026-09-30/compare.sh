#!/bin/bash
# TODO item 78: both arms, round by round, the arm that goes first alternating — the evidence cache
# is shared and cleared for neither (entry 136), so whichever runs second reads warmer.
# usage, from the repository root: var/item78-2026-09-30/compare.sh RUNS corridor...
set -u
here=var/item78-2026-09-30
runs=$1; shift
for arm in today boost60; do
  [ -d "$here/corpus-$arm" ] || cp -R var/corpus "$here/corpus-$arm"
done
for n in $(seq 1 "$runs"); do
  if [ $((n % 2)) -eq 1 ]; then order="today boost60"; else order="boost60 today"; fi
  for arm in $order; do
    echo "== round $n, $arm"
    ITEM78_ARM=$arm .venv/bin/python "$here/arm.py" "$n" "$@"
  done
done
echo "all done"
