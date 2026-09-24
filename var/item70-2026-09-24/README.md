# Item 70 re-runs, 2026-09-24 (DECISIONS entry 198)

The 14 corridors that read their authority's pages and credited no visa decision, re-run three
times each and traced to the first link that broke. Every script runs from the repository root, in
the owner's terminal: headless Chromium cannot start from Claude Code's sandboxed shell.

- `run.py [RUNS] [slug/NAT/RES ...]` — the path `POST /visa-plans` takes, in-process, one run at a
  time, each with empty corridor, plan and recall folders. Keeps what the route discards: the roles
  packet and answer, the plan draft, and why a plan call refused. Resumable. `ITEM70_OUT=fixed
  ITEM70_CORPUS=<copy> PYTHONPATH=<worktree>/src` runs unshipped code against a copy of the corpus,
  because a corridor folds what it read back into the store.
- `followup.sh SCRATCH` — redid the five runs a Personas outage broke, then ran the fixed arm.
- `summarise.py [--reasons] [fragment ...]` — each corridor's outcomes, and what the adjudicator
  said about `visa_decision` in each run.
- `replay_roles.py OUT RUNS PROMPT PACKET ...` — replays the roles call alone on a captured packet.
  Written for step 4 and not run: no survivor broke at the roles call.
- `rebuild.sh CC ...` — step 5: backs a country's corpus and text index up to
  `var/_backup_before_item70_2026-09-24/`, then rebuilds it. Resumable. `rebuild/` holds the logs.
- `trace.md` — the working notes, per corridor. `run.log` — every run's one-line outcome.

`runs/` (the baseline, 42 runs), `fixed/` (the fixed arm, 12 runs) and `rebuilt/` (Malta after its
rebuild, 6 runs) hold the raw outputs and are not committed: about 75 MB, and the packets are
government page text.
