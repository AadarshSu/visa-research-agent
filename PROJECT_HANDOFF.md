# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It answers three questions and nothing else: where
the project stands, what to do next, and what is known to be broken. The chat is not the source of
truth; these files are.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-25 — update this line when you touch the handoff |
| **Tests** | 499 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean. The suite is blocked from the network — `tests/conftest.py`, entry 45 |

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
corrections table in [CLAUDE.md](CLAUDE.md) has twenty-three rows; three of them are *this file's* known
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
| **Reachable destinations** | **53 of 198** — *reachable*, which is stage 1 of three and not the same as working (entry 68). The binding limit is `config/authority_domains.yaml`, which holds **55 rows**; a country with no row is refused, never bootstrapped live (entry 38). Only Iceland and Liechtenstein carry nothing confirmable. `visa-discover audit` prints the split. |
| **Countries with an offline page corpus** | **10** — AE, CA, DE, FR, GB, JP, NL, SE, SG, US; 16,375 pages. These are served without crawling. The other **43** crawl in the request path, which is the ordinary path for a country nobody has built — a corpus is a speed optimisation, never a prerequisite. |
| **Verified working** | **All 53 have now been run; 10 have a corpus.** Stage 2 cleared on 2026-08-25 (entry 70): 103 corridors over the 41 never-run destinations, every one resolving or refusing for a verified reason. **34 of the 41 answer at least one passport** — Cyprus and India were recovered by the renderer on the same day (entry 75), India with all six roles. **Seven refuse every passport** with a diagnosis checked against what was seen: DK, LT, MA, MX, RO, SA, SK. **No corpus will fix those seven** (entry 76) — every one fails at *retrieval*, and a corpus crawl meets the identical wall. Item 30's remaining work is stage 3, the 43 corpora. |
| **Corridor phase** | median **27.4s**, range 8.8–48.3s, over 40 live runs, all corpus-routed, none crawling. |
| **Full request** | `POST /visa-plans` measured at 33–43s on three corridors, each a corridor resolve *and* extraction, with the page cache warm. A fully cold request is still untimed. |
| **Runtime mode** | `source_mode: live`, `extraction_mode: openai`, `render_mode: on_demand`, `discovery_decider: model`, `destination_mode: automatic` |

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

**Item 30 leads: perfect batch 1 before adding a single further country.** The registry grows in
batches, and **a batch is done in three stages** (entry 68): *reachable* → *resolves* → *fast*.

**Both providers have credit again**, and the three things that were blocking stage 3 are fixed and
confirmed live: search pacing and `402` classification (entry 74), the post-over-nationality
mis-pick (entry 72), and the challenge (entry 75). **Stage 3 is clear to run.**

**Cyprus resolves and Greece still refuses** (entry 75). A challenge is now its own outcome,
detected from headers **and body** because Azure declares it only in the body, and answered by the
renderer under our own user agent — which took `render_mode` to `on_demand`. Cyprus went from refusing
every passport to answering on its all-nationality list; Slovakia gets a checklist but spends its
render budget before the decision; Greece's Akamai refusal is untouched and still reported as a
refusal; Lithuania's challenge fingerprints past the user agent and stays `challenged`, which is
neither a refusal nor a pass.

**The ten countries with a corpus keep working through a search outage** (entry 74). A search outage now falls back
to the stored corpus where one exists, says so in the plan's notes with the provider's own figures, and
is deliberately **not** kept for reuse; with no corpus the refusal still stands. Confirmed live on the
outage itself: all ten resolved or handed over a tool where every one of them previously died with
`Search is unavailable`. The provider also paces itself now, and a `402` is classified into a spend cap
or a throttle instead of being reported as one thing.

**What stage 3 buys, measured before paying for it** (entry 76): latency, recall stability across
passports, and outage tolerance — **not coverage**. 34 of 41 already answer with no corpus at all, and
search still supplies **30–67% of the pages a corridor actually reads** even in the ten best-built
corpus countries. Corpus-only is not equivalent to a normal run either: on the real outage one of the
ten (Netherlands) refused outright and four lost their checklist.

**Stage 2 is done, and stage 3 is what remains of item 30.** All 41 never-run destinations ran on
2026-08-25 — 103 corridors, two or three passports each, with `--from` deliberately different from
`--nationality` — and every one resolved or refused for a reason verified against what was seen. 54
resolved outright, 4 handed over a blocked page, 4 handed over a questionnaire, 41 refused; **0 raised
and 0 model failures** in the run set. Entry 70 is the record. What is left is **43 corpora, ~1,792
searches**, and the search rate limiter should be fixed first.

**Two things entry 69 expected came out backwards, and both change what a future batch tests.**
Authorities largely publish **per diplomatic post**, keyed by where the traveller applies from rather
than by their passport — a fourth shape entry 69's table does not have, which closes nationality and
**opens residence**. Entry 69's "real risk", a page per nationality, was not the shape of a single one
of the 41. And **known problem 27 is measured and the demonym bonus buys nothing**: 0.18 shortlist
places per corridor over 122 corridors, none of the 22 filling a role. Do not write 184 demonym lists.

**The sweep also found two defects that no five-country corridor could** (entry 71): a Saudi host
answering `HTTP 990` crashed both its corridors against a `le=599` bound, and Morocco's foreign
ministry omits a TLS intermediate. Both fixed, the first with a regression test.

**Batch 1 bounds destinations, never nationalities** (entry 69): whatever passport a traveller holds,
a batch-1 destination must answer them. A registry row was never evidence that a country works, and
that had gone uncounted 41 rows deep.

**Accuracy is verified by the project owner, outside this repository, and is deliberately not a
stage.** Do not build a truth set, a correctness grader or an accuracy metric here without asking
(entry 68). What follows and must not be lost: `is_usable` and `RefusalCause.resolved` mean *an
official page stated a decision*, never *the decision is right* — so every figure quoted about this
project, entry 58's 75% included, measures whether it **answered**. Known problem 26.

**Item 2 is the trust rule and the rest of the sweep, and it waits behind item 30.** Its cheap half
landed on 2026-08-25 (entry 65): three missing markers — `gv`, `gub`, `canada.ca` — plus batch 1 took
reachable destinations 39 → 53. It also found a hole worth knowing about: `GOVERNMENT_NAMESPACE_LABELS`
and `trust.SUFFIX_MARKER_LABELS` are two hand-maintained lists that must move together, or trusting one
authority trusts its whole government. A test now asserts it.

**The sweep itself** — 143 countries with no row at all — is unfinished data rather than rigor, and it
is explicitly gated behind item 30. Entries 63–68; `visa-discover audit` prints the split.

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
the backlog is expensive, and it has been easy to mistake the second for the first. The dimension
neither arm graded is **correctness** — if a naive arm is right ~90% of the time the question becomes
"accurate but unattributable versus accurate and attributable", which is harder than the one entry 64
answers. That comparison sits with the project owner, who verifies correctness outside this repository
(entry 68); three corridors is a pointer, not a rate, and the arm would have to be rebuilt to go
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

2. **The trust rule refuses a third of the countries measured, and the failing half is the governmental one.**
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
   after it answered).

   **The fix path is measured (entry 66).** Of the 16, a TLS certificate names the organisation for
   **9** — eight of them the authority outright — RDAP for **1**, and **7 have nothing machine-readable
   at all** (BE, CL, DK, GR, IE, NO, RU). So this is reviewed rows rather than automation, and the
   review is nine certificate confirmations plus seven pieces of research, once. Entries 33, 65, 66;
   TODO item 2.

   **The quieter failure was confirmed on Estonia and is fixed.** Estonia was trusted on
   `e-resident.gov.ee` and refused both its corridors with the e-Residency help centre as the only
   readable page — bootstrap succeeding against a trusted set that could not hold the answer, exactly
   as entry 67 warned. `vm.ee` (Q6867006) and `mae.ro` (Q15628977) are now reviewed rows, and
   **Estonia resolves all three passports on `vm.ee`**. Romania still refuses, but on a different and
   truer diagnosis: `mae.ro`'s hosts are now reached and every one of their `robots.txt` answers `503`.
   Entry 70.

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

   **Narrowed and half fixed, 2026-08-25** (entry 72). A post named in a **host label** —
   `india.embassy.gov.au` — was never concluded to be *another* post, only ever "own" or nothing, so
   it competed as a neutral ministry page. That is fixed, and `fees` and `processing_times` joined the
   roles a foreign post loses points for, after `brazil/US/US` was measured taking Brazil's
   **Edinburgh** fee page. `visa_decision` and `general_entry` are deliberately excluded — a visa rule
   is the same at every consulate, and demoting the only page that states it would refuse corridors to
   buy nothing.

   **Still open: a post named as a bare path segment.** `gov.si/assets/predstavnistva/new-delhi/…` is
   the common information sheet for applicants *in India*, served to someone in London, and
   `mission_in_path` misses it because it requires a `consulado-edimburgo` shape. Measured at 4,178
   flips and three role pages, two of them corrections — not enough to ship on. **And the fix is only
   verified at unit level**: the search account capped out immediately afterwards.

10. **The model decider is non-deterministic, and it is now the only variance left.** Isolated for the
   first time on 2026-08-23 (entry 53): with the candidate count and shortlist identical across runs,
   one run filled `processing_times` and two did not. Confirmed as the residual by entry 58 — 19 of 20
   corridors reproduced exactly, the exception being adjudication with recall held fixed. It means a
   corridor can be `is_usable` with a role unfilled for a purely model-side reason, indistinguishable
   from item 8. It also reaches which *tools* get named (entry 60).

11. **Bot-blocked official portals are a real limit, but not the largest one** — measured, the wizard
   was, and that is now handled (entries 58–61). **Counted rather than assumed since entry 63**:
   `visa-discover audit` buckets every unreadable page by typed outcome. Across the 132 runs on disk,
   **102 are `disallowed`** — Austria's 23, Denmark's mission hosts and Romania's, whose `robots.txt`
   answers `520` and `503` so nothing was requested — and **80 are `blocked`**, led by `www.mfa.gr`,
   `www.gov.cy`, `mzv.sk` and `urm.lt`. **An outright `403` has now cost corridors**, which the
   previous two readings of this number said it had not — Lithuania and Slovakia lose their *entire*
   trusted set to one, and Cyprus all three of its domains.

   **But most of those `403`s are challenges, not refusals, and this entry said the opposite for
   half a day** (entry 73). Azure declares a challenge in the response **body**, so a header-only
   test finds Cloudflare and misses Azure: `www.gov.cy` is an *Azure WAF JS Challenge* and
   `www.mzv.sk` a Cloudflare one whose `robots.txt` answers `200` and **permits us**. Both are read
   successfully by our own renderer under our own user agent — 71,000 and 377,000 characters. `urm.lt`
   is a challenge our renderer cannot answer honestly, which is a third outcome and not a refusal.
   Only **Greece's `www.mfa.gr`** — Akamai, *"You don't have permission"*, no JS — is a real refusal.
   Cyprus's `www.mip.gov.cy` is separate again: a certificate that expired 2026-08-02, refused rather
   than bypassed.
   Both Cyprus corridors refuse, name the blocked hosts, and correctly do not claim
   `resolved_decision_blocked` — nothing was read, and entry 32 requires a source. Verified
   independently with `curl`; entry 70. **Greece's `www.mfa.gr` answers a plain `403` too**, verified
   the same way, though Greece resolves anyway for an Indian passport. **Malta and Thailand produced
   the first four `resolved_decision_blocked` corridors ever recorded** — entries 27, 32 and 57 firing
   on a real corridor for the first time since August.
   Working around a block stays forbidden. What
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

23. **The interface offers 198 destinations and can reach 53.** `researchable_destinations()` lists
   every country with `status="available"`, but 143 have no row in `authority_domains.yaml` and are
   refused with a `503`. The refusal is honest; the *offer* is not. Fix by marking unbuilt countries or
   by building the registry out (item 2) — not by loosening the refusal. **Countable now rather than
   asserted**: `visa-discover audit` prints the split, and attributes it — every one of the 143 is a
   job nobody has run, not the trust rule (entries 63, 65, 67). **And 53 overstates it**: reachable is
   stage 1 of four, and only 9 destinations have ever been shown to answer a traveller (entry 68).

24. **A corpus build stops at its seeds, and that is the defect stage 3 would freeze.**
   **Rewritten 2026-08-26 after three wrong diagnoses, entry 77.** What this entry used to say —
   Japan's corpus holds 29 mission hosts and not the London embassy, "where five of its six roles came
   from" — is **stale and was misleading**. Measured: search *does* seed
   `www.uk.emb-japan.go.jp`; it is absent because that host answers a genuine Akamai `403`, the same
   signature as Greece's `www.mfa.gr`, so nothing can fetch it. And Japan does not need it — its
   latest run filled all six roles from `mofa.go.jp` alone, from the corpus, with search down.

   **The real defect, from rebuilding Japan:** 70 queries produced **276 seeds across ~50 hosts**,
   and at `DEFAULT_CORPUS_PAGES` of 1,200 that is `1200 // 50` = **24 pages per host**. The job's own
   check fails — *"only 7% of what it found lies beyond depth 1 — this crawl fetched its seeds and
   stopped, which is the request path's behaviour, not this job's"* — against a `MINIMUM_DEEP_SHARE`
   of 10%. A corpus in that state is a list of search results with one hop. **Size `--pages` per
   country from the seed-host count before building 43 of them**; the constant was already raised once
   (200 → 1,200) after Canada showed the same symptom.

   **What is settled (entry 76):** search supplies **30–67% of the shortlist a corridor actually
   reads** in the ten corpus countries, and on a real outage corpus-only left the Netherlands refusing
   outright and four others without a checklist. A corpus keeps a country working; it does not keep it
   working as well.
   Measured against the pages that actually filled roles on the crawl path: Singapore 6/6, United States
   3/3, Sweden 3/4, France 2/3, Netherlands 1/2, **Japan 1/6** — Japan's corpus holds 29 mission hosts
   and not the London embassy, where five of its six roles came from. It resolved anyway **because
   search still runs**, which is the strongest argument against dropping search (entry 48). The safety
   net is thinner than it was: the crawl used to compensate for poor corpus recall, badly and
   nondeterministically, and now does not. **Nothing counts how often the corpus was the only source and
   came up short**, though `found_by="corpus"` in the recall log would make it countable.

26. **Every number this project quotes about itself measures whether it *answered*, not whether the
   answer was *right*.** `ResolvedCorridor.is_usable` and `RefusalCause.resolved` both mean an official
   page **stated** a decision. Entry 58's 75% is a rate of answering, and a pipeline replying "visa
   required" for every nationality would score full marks on it.

   **This is a caveat on reading the numbers, not work queued here.** Correctness is verified by the
   project owner outside this repository, deliberately (entry 68) — so do not build a truth set, a
   correctness grader or an accuracy metric without asking. Listed because quoting 75% without this
   sentence overstates what was measured.

27. **184 of 198 nationalities have no demonym, and the nationality bonus runs on them.**
   `Country.text_tokens` is `name + synonyms + demonyms` and feeds `_describes_country`, which awards
   the nationality bonus in `score_link`. Only the fourteen hand-curated countries carry demonyms.
   Probed: a page titled "Visa requirements for Kenyan nationals" at `/visa-for-kenyan-nationals`
   awards **no** bonus to a Kenyan traveller; the identical page does for an Indian one, because
   matching is anchored to word and segment boundaries and `kenya` does not match `kenyan`. Stemming
   would not fix it — the Philippines' demonym is *Filipino*, the Netherlands' is *Dutch*.

   **Measured 2026-08-25, and the cost is nothing** (entry 70). Over 122 recorded corridors, candidates
   matched on a demonym and *not* on the country's name took **0.18 shortlist places per corridor**,
   and **not one of the twenty-two filled a role** — they are approved-insurer lists, a Work Holiday
   notice, an embassy press release about staffing, and four `indianvisaonline.gov.in` pages in a
   corridor whose destination is India. So the demonym half of the bonus is a fetch spent on noise,
   which is entry 62's conclusion about the whole bonus reached from the other side.
   **Do not write 184 demonym lists on a recall argument.** Kept here as a description of the
   mechanism, not as queued work. Method limit: the URL half of the match is exact, the text half
   approximate (entry 62's fidelity note), so twelve is a lower bound — which makes the noise finding
   stronger, not weaker. Entries 69, 70; TODO item 30.

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
