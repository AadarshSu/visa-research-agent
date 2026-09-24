# Selection replay, 2026-09-24 (DECISIONS entry 194)

Replays **only the selection call** over each oracle corridor's candidate set, so a packet change is
graded on several runs of a fixed pool with no search, fetch or adjudication in the way.

1. `capture.py cap/` — runs each corridor up to `_choose_what_to_read` and saves its candidates,
   once over `var/corpus`+`var/pagetext` (`new`) and once over the pre-pilot backup (`old`), with
   search memoized so both arms see the same results. About 15 searches a corridor; no model call.
   `cap/` is ~130 MB and is not committed.
2. `replay.py results.jsonl --arms new --variants baseline,fusion120 --runs 5` — rebuilds the pool
   and packet exactly as the resolver does (checked: `packet_characters` matched the pilot's logs
   byte for byte) and calls the selector through Personas. Resumable. Run it from the repository
   root so `.env` loads, and **one call at a time**: four concurrent calls were followed by ten
   minutes of `504`s (OFSELF_FEEDBACK 8.22).
3. `grade.py results.jsonl --alias [--detail]` — role recall per run against the oracle; `--alias`
   credits the same page at another address, as `selection-recall` now does.

`variants.py` holds what the model is shown: `baseline` is today's packet; `fusion<K>` is entry
183's ranking cut to K; `fusion120_blind40` adds the 40 best no-text candidates by link score.
