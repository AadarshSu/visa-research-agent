# Item 75, test 1: destinations whose visa pages are mostly not in English (DECISIONS entry 241)

Malaysia, Indonesia and Uruguay, each for an Indian applying from Britain and a Filipino applying
from the Philippines. Set `EMBED_CAPTURES=var/embed-test1-2026-09-29/cap/new` for every step after
the capture; the 2026-09-28 embedding scripts and the 2026-09-24 replay read it.

1. `capture.py cap malaysia/IN/GB …` — each corridor's candidates, today's stores only (40
   searches, no model; from the owner's Terminal panel). `cap/` is not committed.
2. `../embed-replay-2026-09-28/embed.py` — the pools' vectors (1.13M Voyage tokens).
3. `candidates.py > review.txt`, regrouped into `r_<destination>.txt` — what was read to curate,
   with passage tests in English, Malay, Indonesian and Spanish. Not committed.
4. `rows.py --append` — the six rows, judged by hand, appended to `oracle/selection_oracle.yaml`.
5. `../embed-replay-2026-09-28/rank.py --detail` (`rank.log`, `rank_results.json`) and `sweep.py`
   (`sweep.log`) — stage 1, no model.
6. `../embed-replay-2026-09-28/replay_embed.py stage2.jsonl --variants
   fusion120_blind40,emb_link_embed_neutral_c40 --runs 5 --concurrency 1`, graded with
   `../selection-replay-2026-09-24/grade.py --alias --detail` (`stage2_grade.log`) — the selector,
   through Personas.
7. `admit.py embed|review|rank` — do embeddings find answers the pool rule keeps out? The unpooled
   pages' vectors (2.62M tokens); `admitted.yaml` holds the pages judged to answer, `admit_rank.log`
   where each ranks.
