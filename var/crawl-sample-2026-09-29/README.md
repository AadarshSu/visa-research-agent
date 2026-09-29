# Crawl sample, 2026-09-29 (TODO item 75, DECISIONS entry 240)

Among the links a corpus build recorded and never opened because they scored nothing, would
embeddings pick the ones that hold guidance? Austria, Japan and Turkey; 100 addresses ranked by
embedding and 100 at random from each.

1. `prepare.py AT JP TR` embeds each unopened zero-scoring link's text, heading and address with
   Voyage and writes both samples to `samples.json`. Opens nothing.
2. `fetch.py AT JP TR` opens them through the build's own crawler at depth 0 into `pagetext/` here
   (never committed), recording outcomes in `fetched.json`. Run it from the owner's Terminal panel.
   It never asks for an address twice.
3. `grade.py blind` writes `blind.jsonl`, the pages read, shuffled with the sample hidden;
   `labels.json` holds this session's label for each id; `grade.py report` joins them (`report.log`).

The labels are one reader's, blind, and not the owner's checking (entry 68).
