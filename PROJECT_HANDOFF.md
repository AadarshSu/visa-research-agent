# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It answers three questions and nothing else: where
the project stands, what to do next, and what is known to be broken. The chat is not the source of
truth; these files are.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-24 — update this line when you touch the handoff |
| **Tests** | 486 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean. The suite is blocked from the network — `tests/conftest.py`, entry 45 |

---

## Where each thing is written down

This file grew to a thousand lines by absorbing all four of the others. It is deliberately short now,
and each kind of question has one home:

| Question | File |
| --- | --- |
| Where are we, what is next, what is broken | **this file** |
| What is the ordered queue of work, and why each item matters | [TODO.md](TODO.md) |
| Why is it built this way, what was tried and rejected | [DECISIONS.md](DECISIONS.md) — **start at its index** |
| How is it built — trust model, pipeline, retrieval, discovery | [ARCHITECTURE.md](ARCHITECTURE.md) |
| What are the rules I must not break | [CLAUDE.md](CLAUDE.md) — loaded automatically |
| How do I contribute, and how do I debug a corridor | [AGENTS.md](AGENTS.md) |
| What is this project, for someone who has never seen it | [README.md](README.md) |

**Do not restate a fact from one of those here.** Every time this file has summarised DECISIONS or
TODO, the summary and the original have drifted, and the drift is what has wasted the most time. The
corrections table in [CLAUDE.md](CLAUDE.md) has thirteen rows; three of them are *this file's* known
problems being confidently wrong, and the rest are TODO items proposing a fix that measurement then
disproved. Link instead of copying.

---

## Where it stands

**The goal:** produce visa application plans where every claim is grounded in an official government
source, and the traveller is told plainly when something could not be verified. Permanently out of
scope: submitting applications, booking appointments, filling forms, driving an authority's
questionnaire, or claiming approval is guaranteed.

**It works end to end, and it has been measured against a bar committed in advance** (entry 35). Over
twenty high-volume corridors run twice each on 2026-08-24: **75% confirm the visa decision** (bar
≥70%) and **50% yield a document checklist** (bar ≥50%). It passes — by one corridor on the first
number and by nothing at all on the second, so quote it as a marginal pass. Entry 58.

**Read the sample structure before quoting that.** Nationality changed the outcome once in twenty;
destination decided the rest. So the sample is **five destinations replicated four times**, not twenty
independent corridors, and 75% is "three and three-quarters of five". A future bar should sample
destinations.

### What is built

| | |
| --- | --- |
| **Researchable destinations** | **41 of 198.** The binding limit is `config/authority_domains.yaml`, which holds 41 rows; a country with no row is refused, never bootstrapped live (entry 38). Every row now carries a usable domain. `visa-discover audit` prints the split. |
| **Countries with an offline page corpus** | **10** — AE, CA, DE, FR, GB, JP, NL, SE, SG, US; 16,298 pages. These are served without crawling. The other 29 crawl in the request path. |
| **Corridor phase** | median **27.4s**, range 8.8–48.3s, over 40 live runs, all corpus-routed, none crawling. |
| **Full request** | `POST /visa-plans` measured at 33–43s on three corridors, each a corridor resolve *and* extraction, with the page cache warm. A fully cold request is still untimed. |
| **Runtime mode** | `source_mode: live`, `extraction_mode: openai`, `render_mode: never`, `discovery_decider: model`, `destination_mode: automatic` |

**The largest coverage limit is the interactive tool, not bot-blocking** — that was measured and it
inverted the assumption this file had carried for weeks (entry 58). A page that is *read* and judged
to **ask** a question rather than answer it is now a third outcome beside *found* and *blocked*: it is
named for whatever role it settles and the plan offers it beside that question (entries 59 and 60).
Getting those pages in front of the model needed the shortlist to reserve five candidates per role
rather than three, which took **the United Kingdom from 0 of 8 corridor runs resolving to 4 of 4**
(entry 61).

**Discovery runs in the request path** for a destination nobody configured: the country's own
government domains are read from committed data, the corridor resolved, the plan built from what was
found. No human approves anything per request. Seven destinations are also hand-configured in
`destinations.yaml`; everything else uses the automatic path.

---

## What to do next

**[TODO.md](TODO.md) is the queue — go there.** Its index table is generated from its own headings, so
it cannot drift; this file deliberately does not copy it.

**Item 2 leads, and its cheap half landed on 2026-08-25 (entry 65).** Three markers the rule was
missing — `gv`, `gub`, `canada.ca` — took coverage from **39 to 41 researchable** and emptied the "row
with nothing confirmable" bucket. It also found a hole worth knowing about: `GOVERNMENT_NAMESPACE_LABELS`
and `trust.SUFFIX_MARKER_LABELS` are two hand-maintained lists that must move together, or trusting one
authority trusts its whole government. A test now asserts it.

**What is left of item 2 is the measurement, then the sweep.** All 157 remaining refusals are countries
nobody has run `visa-discover registry` for — unfinished data, not rigor. Before spending that quota,
run the coverage check the item asks for: of the 16 governments with no hostname marker, how many are
reachable via a published government domain list, RDAP registrant data, or a TLS certificate
organisation? That decides whether the rest automates or is 16 reviewed rows. Entries 63, 64 and 65;
`visa-discover audit` prints the split.

**Read entry 64 before arguing about relaxing anything, because it cuts both ways.** A one-off control
arm — open-web search, no trust model, one model call — was built, run on three corridors and then
deleted; the entry is the record. It was ~5× faster, answered a country we refuse outright, and
produced a document checklist for Germany where this project produces none. It also cited **0 of 8
hosts that would pass the trust rule** — the United Kingdom's top 8 held no `gov.uk` page at all — and
answered `visa_required: false` for Kenya beside `visa_name: "Electronic Travel Authorization"` in the
same breath. **And the trust rule was wrong about one of the eight**: `india.diplo.de` is Germany's own
mission, declined because `diplo.de` carries no governmental marker, which is known problem 2 with a
cost attached.

**The conclusion those two entries support, stated so it can be argued with:** the rigor is cheap and
the backlog is expensive, and it has been easy to mistake the second for the first. The dimension never
graded is correctness against a truth set — if a naive arm is right ~90% of the time the question
becomes "accurate but unattributable versus accurate and attributable", which is harder than the one
entry 64 answers. Three corridors is a pointer, not a rate, and the arm would have to be rebuilt to go
further.

One thing worth knowing before choosing: item 7 is **deployment**, which entry 58 unblocked by
answering the product question.

---

## Known problems

**Numbering is append-only** — `CLAUDE.md`, `ARCHITECTURE.md`, `TODO.md` and two comments in the code
reference these numbers. Everything listed is **live**. Retired numbers are listed at the end rather
than kept as struck-through entries, which is what made this section unreadable.

Each entry says what is true now. *How* it was learned is in the DECISIONS entry it names — do not
re-add the amendment history here.

2. **The trust rule refuses a fifth of the world, and the failing half is the governmental one.**
   Measured offline: `is_own_government` failed for **19 of 51** countries, **16 since 2026-08-25**
   (entry 65 added the markers Austria, Uruguay and Canada actually use), every one of them on
   `looks_governmental` rather than the own-TLD test. Most of Schengen is unreachable, and Schengen is
   additionally a definition problem — `europa.eu` can never pass `belongs_to_destination` for a member
   state. **Two distinct failures, and the second is worse:** seven countries (BE, DE, DK, FI, NL, NO,
   SE) have no marked domain and refuse safely; **nine (CL, CZ, GR, HU, IE, IT, PT, RO, RU) do have
   one**, so bootstrap *succeeds* against a trusted set that cannot contain the guidance, and nothing
   reports it. Canada used to be the sharpest case of the second kind and is fixed (entry 65). The fix
   is reviewed data, never a wider regex. Frozen in `tests/test_trust_coverage.py`. **And it refuses
   correct authorities *inside* countries it accepts, not only whole countries**: a one-off control
   arm's Germany run cited `india.diplo.de`, Germany's own mission giving guidance to exactly that
   traveller, and the rule declines it for want of a marker (entry 64; the arm itself was deleted
   after it answered). Entry 33; TODO item 2.

5. **The full cold request has never been timed.** Every figure quoted is the corridor phase; plan
   extraction sits on top. The remaining lever is **search**, roughly 3s per corridor at three queries
   per trusted domain — TODO item 19. Warm is instant, and the local `var/` stores are what make it warm.

6. **The trust rule's audit was survivorship, and the cap is uncalibrated.** The rule reproduces all 22
   recorded human decisions, but every country in that audit was one `looks_governmental` already
   handled — which is item 2. Its output is now committed and reviewable rather than re-derived per
   request (entries 38, 39), and twelve countries needed a `reviewed` override. Two things remain
   unreported: whether an accepted domain set plausibly holds a visa authority at all, and the **cap** —
   at most five of a destination's own domains are used (entry 22), so a country whose guidance spans
   six or more loses one, and `withheld_domains` is the only warning. Five is calibrated against
   corridors run, not derived.

7. **Nobody has read a blocked-authority plan as a traveller would.** The mechanism is confirmed live
   on real corridors (entries 55–57): the decision is stated unknown and the page handed over as a URL.
   What is unverified is the *wording* — whether "Uncertain" reads as *we could not check* rather than
   *no visa needed*. Do not fix the mechanism before reading a real plan. TODO item 8.

8. **Nothing distinguishes "this country publishes no checklist" from "we failed to find it."** Both
   produce an empty checklist, and since a missing one no longer refuses the corridor, a find-or-read
   failure now yields a plan with a visibly empty list. The plan says so — `VisaPlan` enforces it — but
   not *which* case it is. Now attached to Germany and the United States, 0/8 checklists each, rather
   than to a hypothetical. **And a third answer is on the table for Germany**: `visa-discover audit`
   records seven pages on `www.auswaertiges-amt.de` fetched and holding too little readable text to
   trust, which is neither of the two cases this problem names. Entry 14, entry 63; TODO item 9.

9. **The heuristic scorer mis-ranks, and it is a recall gate rather than a decider.** The conclusion to
   draw is *widen the gate*, not *improve the ranking* — entry 40, and entry 61 is the same lesson
   again. It still matters, because it builds the shortlist the model chooses from, and it rests on
   English vocabulary and per-country city labels, so it will keep degrading on new countries and
   languages. It remains the offline regression baseline. A sharply defined residual: for an Indian
   national applying from Great Britain the scorer rates `checklist-schengen-visa-tourism/india`
   **113.0** against **73.0** for `/united-kingdom`, when for a consular checklist the **post** governs;
   the adjudicator discards the wrong-post page, so the corridor throws away a checklist it fetched.
   TODO item 1.

10. **The model decider is non-deterministic, and it is now the only variance left.** Isolated for the
   first time on 2026-08-23 (entry 53): with the candidate count and shortlist identical across runs,
   one run filled `processing_times` and two did not. Confirmed as the residual by entry 58 — 19 of 20
   corridors reproduced exactly, the exception being adjudication with recall held fixed. It means a
   corridor can be `is_usable` with a role unfilled for a purely model-side reason, indistinguishable
   from item 8. It also reaches which *tools* get named (entry 60).

11. **Bot-blocked official portals are a real limit, but not the largest one** — measured, the wizard
   was, and that is now handled (entries 58–61). Three blocked portals found: `france-visas.gouv.fr`,
   `www.france-visas.gouv.fr` and Singapore's VFS page. **Narrower again as of entry 63, on two
   corridors:** of 15 pages that could not be read, 0 were `blocked` — 13 held no readable text and 2
   were unreachable. Two corridors is not a rate; it is a pointer at where the losses actually are. Working around a block stays forbidden. What
   entry 35 corrects is the conclusion: the loss is permanent *given an anonymous client*, and that
   posture was never itself decided. `robots.txt` is now read and obeyed (entry 36) and buys nothing
   here — those hosts answer `403` to their own `robots.txt`. **And France's `403` is not a refusal at
   all**: it carries `cf-mitigated: challenge`, so no policy was ever stated, and our own renderer reads
   the page under our own user agent. Decided as entry 41, **not implemented** — TODO item 5 — and the
   interface still tells travellers a challenged authority "does not permit automated retrieval", which
   is untrue of what was seen.

12. **Discovered pages have no staleness check.** A publication date is read from the path and
   *reported* to the adjudicator, deliberately not a veto — two of China's correct picks carry dated
   paths and one is from 2013. Content-hash drift detection covers configured sources only.

13. **Scoring is English-only.** A destination publishing solely in its own language scores near zero
   and refuses. Rendering `xuatnhapcanh.gov.vn` yields 9,327 characters of Vietnamese, which scores
   nothing.

14. **`xuatnhapcanh.gov.vn/en` is broken server-side** — it answers `200` with a
   `location: http://localhost:4000/vi` header and an empty body. Browsers ignore `Location` on a
   `200`, so **rendering does not fix this one**; it renders to 0 characters. The site root works.

15. **An authority's own outdated microsite is undetectable** — right domain, live, linked, text-rich,
   so every check passes.

16. **Mission detection only works when a mission has its own subdomain.** `_mission_domains` returns
   `[]` for a consolidated portal — Brazil puts every mission on `www.gov.br` with the post in the
   *path*, so Riyadh and Atlanta outrank Edinburgh for a UK applicant. **Broader than it reads:** it
   reads `destination.sources`, and the automatic path builds a config with none, so it returns `[]` for
   **every** discovered destination. Mission detection survives there only through `mission_affinity`'s
   host-label check.

17. **The retrieval cache is not re-validated against changed rules.** After changing what counts as
   usable, cached entries serve the old result until their TTL expires. Clear `var/cache/` when testing
   a retrieval change, or a fix will appear not to work.

19. **The candidate set can vary between runs, and the answer varies with it.** The original
   observation: `canada/GB/GB/tourism` run cold twice within an hour, same domains, same queries, same
   code — one refused because the answering page was not among its candidates, one resolved with that
   page ranked 15th of 470. **Largely answered by the corpus** (entries 44–53) and by entry 58: across
   40 runs, 19 of 20 corridors gave identical outcomes, and the candidate set is stable in practice
   because most of it comes from a file. It stays open for the gap it never closed — those runs were
   minutes apart, and the original divergence was two days apart. Every run writes
   `var/recall/<corridor>.json` so it is diagnosable (entry 43). TODO item 17.

20. **A live plan cites a URL with no supporting quote.** `SourceReference.supporting_excerpt` is
   written only by `FixtureSourceFetcher`; on the live path it is always `None`. *"Why did you say an
   Indian passport holder needs this visa?"* is answerable as *which page*, never *which sentence*.
   **Careful when fixing:** a model-produced excerpt must be checked against the retrieved text, because
   an unverified quote attributed to a government page is worse than no quote. TODO item 21.

21. **A plan cannot be tied to the text it was read from.** `content_hash` is on `FetchedSource`;
   `SourceReference` has no hash field, so nothing in a `VisaPlan` identifies the version of the page
   behind a claim. TODO item 21.

22. **Why a page was chosen for a role never leaves discovery.** `decided_by`, `score` and `signals`
   live in `ResolvedCorridor` and appear nowhere in the API response. TODO item 21.

23. **The interface offers 198 destinations and can research 39.** `researchable_destinations()` lists
   every country with `status="available"`, but 157 have no row in `authority_domains.yaml` and are
   refused with a `503`. The refusal is honest; the *offer* is not. Fix by marking unbuilt countries or
   by building the registry out (item 2) — not by loosening the refusal. **Countable now rather than
   asserted**: `visa-discover audit` prints the split, and attributes it — every one of the 157 is a
   job nobody has run, not the trust rule (entries 63 and 65).

24. **A thin corpus has no crawl behind it, and coverage varies enormously between countries.**
   Measured against the pages that actually filled roles on the crawl path: Singapore 6/6, United States
   3/3, Sweden 3/4, France 2/3, Netherlands 1/2, **Japan 1/6** — Japan's corpus holds 29 mission hosts
   and not the London embassy, where five of its six roles came from. It resolved anyway **because
   search still runs**, which is the strongest argument against dropping search (entry 48). The safety
   net is thinner than it was: the crawl used to compensate for poor corpus recall, badly and
   nondeterministically, and now does not. **Nothing counts how often the corpus was the only source and
   came up short**, though `found_by="corpus"` in the recall log would make it countable.

**Retired numbers**, kept so the numbering keeps its meaning: **1** (the unmeasured-product question —
entry 58), **3** ("who to believe" decided per request — entries 34, 38), **4** (the blocked-source
plan never run live — entries 56, 57), **18** (the excerpt silently deciding corridors — entry 42),
**25** (entry 27's exception not firing on the corpus path — entries 56, 57). Also removed as fixed: a
block resolving a corridor it had nothing to do with (entry 32), the unverified `conflicts` field
(entry 30), and a failed model call substituting the heuristic (entry 31).

---

## Working agreements

- **Update this file at the end of a session** — *Where it stands*, *What to do next*, *Known
  problems*. A stale handoff is worse than none, because it is believed.
- **Keep it short.** If something belongs in TODO, DECISIONS or ARCHITECTURE, put it there and link.
- **Record decisions in [DECISIONS.md](DECISIONS.md) as they are made**, with the reasoning and what
  was rejected, and add the entry to its index.
- Do not record a problem as fixed unless it is fixed, or a result as verified unless it was run.
- Before handing off: `ruff check .`, `ruff format --check .`, `mypy`, `pytest`.
- Contributor rules, safety boundaries and how to debug a corridor are in [AGENTS.md](AGENTS.md).
