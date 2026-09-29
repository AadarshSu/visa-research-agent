# Embedding replay, 2026-09-28 (TODO item 67, DECISIONS entry 235)

Does embedding rank earn a place in `fusion_order`, beside link rank and stored-text rank? Runs over
the candidate sets `../selection-replay-2026-09-24/capture.py` saved in `cap/new/`, which must be on
this machine. Embeddings are ranking input only; nothing here changes what a plan may say.

1. `embed.py --dry-run` counts what would be embedded: pages, chunks, an approximate token range.
   No network.
2. `embed.py` embeds each pooled page's stored text (4,000-character chunks, 500 overlap) and each
   role query with `voyage-4-large` at 1024 dimensions, into `vectors.sqlite` (not committed).
   Resumable: a re-run embeds only what is missing. Needs `VOYAGE_API_KEY`.
3. `rank.py [--detail]` — no network, no model. For each arm, fuses and cuts the pool as
   `fusion120_blind40` does, and counts the oracle roles whose answering page survives the cut, split
   by English, other-language and no stored text; also the best answering page's position. Arms:
   link+text (today), embed only, link+embed, link+text+embed, each with a traveller-neutral query
   and one naming the passport and residence.
4. `replay_embed.py OUT.jsonl --variants fusion120_blind40,emb_... --runs 5 --concurrency 1` — the
   selector itself, through Personas, via the 2026-09-24 replay unchanged. Grade with
   `../selection-replay-2026-09-24/grade.py OUT.jsonl --alias`. Re-run `fusion120_blind40` beside
   the embedding arm rather than comparing with the recorded 80.0: `var/pagetext` has been rebuilt
   since then.

5. `sweep.py` — no network, no model: the same arms at smaller cuts (top 20–120 plus 40 blind).

Under ~3 roles of difference is no result (item 67).

**Run 2026-09-29 (DECISIONS entry 236):** `embed.log`, `rank.log`, `sweep.log`, and stage 2's
`stage2.jsonl`, `stage2.log`, `stage2_grade.log` beside this file. An `emb_…_c<N>` variant shows the
top N instead of 120, plus the 40 blind.
Voyage needs a payment method on the account for a usable rate limit; the free tokens still apply,
but not to its Batch API.

**Excerpt experiment (entry 238):** `excerpt_replay.py embed`, then `excerpt_replay.py excerpt.jsonl
--variants excerpt_today,excerpt_embed --runs 5 --concurrency 1`; graded in `excerpt_grade.log`, read in
`excerpt_substitutes.log` (`substitutes.py excerpt.jsonl excerpt_embed excerpt_today`).
