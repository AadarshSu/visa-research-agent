# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It answers three questions and nothing else: where
the project stands, what to do next, and what is known to be broken. The chat is not the source of
truth; these files are.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-09-02 — update this line when you touch the handoff |
| **Tests** | 678 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean. The suite is blocked from the network — `tests/conftest.py`, entry 45 |

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
corrections table in [CLAUDE.md](CLAUDE.md) has a hundred and twenty rows; three of them are *this file's* known
problems being confidently wrong, and the rest are TODO items proposing a fix that measurement then
disproved. Link instead of copying.

---

## Where it stands

**The goal:** produce visa application plans where every claim is grounded in an official government
source, and the traveller is told plainly when something could not be verified. Permanently out of
scope: submitting applications, booking appointments, filling forms, driving an authority's
questionnaire, or claiming approval is guaranteed.

**The goal for the work in front of us, stated 2026-08-26.** A country is built **offline** — its
corpus and its page-text index — and a corridor answers from that store. **Live search is acceptable
where it is genuinely unavoidable; it is not acceptable as the ordinary source of recall.** The corpus
has to be useful, and useful means a number: how often a corridor finds what it needs without
searching. [TODO.md](TODO.md) **item 19** is that goal as a work item. **Item 34 is done** (entry
87): selector work now has ground truth it did not build, so a measurement of item 19 can be
believed.

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
| **Reachable destinations** | **55 of 198** — *reachable*, which is stage 1 of three and not the same as working (entry 68). The binding limit is `config/authority_domains.yaml`, which holds **55 rows**; a country with no row is refused, never bootstrapped live (entry 38). **Every row now carries a confirmable domain** — Iceland and Liechtenstein were the last two and were fixed on 2026-08-29 (entry 110), so `audit` reads `row, no confirmable domain: 0`. `visa-discover audit` prints the split. |
| **Countries with an offline page corpus** | **53 of the 55 reachable** — the ten of entry 85 plus the 43 built on 2026-08-30 (entry 116, ~13 hours). Only **BR and UY** have none, at one authority domain each. Median around 2,900 entries; Iceland 8,263 and Luxembourg 8,231 largest, **Egypt 45 and Lithuania 139 smallest — every thin one for a cause outside this program** (an expired certificate, a stated `Disallow`, unanswerable challenges, off-domain redirects), none of them a crawler setting. **A build opens 3–15% of what it records** (entry 88), and the page answering a specific traveller is usually one hop below something it recorded and never opened. The Netherlands is the only one rebuilt with a reserved share for per-traveller families; item 35. **Read a host count against the country's domain count, never alone** — Croatia and Slovenia came back on two hosts each and are healthy, having exactly two configured domains; Germany's symptom was one host against five (entry 116).
| **Verified working** | **All 55 reachable have a row; 53 have a corpus** (entry 116). Stage 2 cleared on 2026-08-25 (entry 70): 103 corridors over the 41 never-run destinations, every one resolving or refusing for a verified reason; **34 of the 41 answer at least one passport**. **A traveller nobody tuned for scores 87% on the original ten** (entry 112). **Nine corridors were run over the new stores on 2026-08-30 and all nine answered from the store without crawling** — Portugal filled six roles, Iceland and China five, Ireland four plus a named tool, Bulgaria two, Slovakia two, and **Liechtenstein and Lithuania none**. Three served a Nigerian traveller that country's own pages: China's Nigeria embassy, Portugal's and Slovakia's Abuja embassies. **The old claim that DK, LT and SK refuse every passport is now partly disproved** — with corpora Denmark fills four roles and Slovakia two; only Lithuania still fills none, behind a `robots.txt` `Disallow` that must not be worked around.
| **Corridor phase** | median **27.4s**, range 8.8–48.3s, over 40 live runs, all corpus-routed, none crawling. |
| **Full request** | `POST /visa-plans` measured at 33–43s on three corridors, each a corridor resolve *and* extraction, with the page cache warm. A fully cold request is still untimed. |
| **Page-text index** | **53 countries**, and **414 rows across nine of them held a bot-check page instead of the authority's** until 2026-08-30 (entry 117) — `is_challenge` read only the first 20,000 characters and Cloudflare's marker sits past it, so an unanswered challenge was stored as the page. Purged with `pagetext --purge-interstitials`; 0 remain of 43,153. **Measurements of PH, LT, NO, TH, ID, LI, US, SK and FI taken before that date no longer describe them — item 44.** Formerly: — one file per country in `var/pagetext/`, the 43 of entry 116 written by their builds. Formerly 1 built and 11 backfilled: — `var/pagetext/`, one SQLite/FTS5 file each. Japan holds 684 pages of body text (94 PDFs) after a rebuild; the other ten are cache backfills of 1–38 pages. **Read at step 3b of `_resolve`, before the shortlist — and currently inert, on purpose** (entry 80). The A/B was taken and **it could not answer the question**: six runs of identical code give 4, 4, 4, 4, 5 and 6 roles, so role count cannot see a ranking change on one corridor (entry 81, which withdraws entry 80's regression). What is established is that the role-filling pages are shortlisted and fetched in every arm — the lift is recall-neutral, nothing shows it helps, and it stays off. Entries 78–81. |
| **Runtime mode** | `source_mode: live`, `extraction_mode: openai`, `render_mode: on_demand`, `discovery_decider: model`, `discovery_selector: model`, `destination_mode: automatic` |
| **Model candidate selection** | **Built and on** (entries 83–87). `discovery_selector: model` reads stored page text for every candidate in contention and picks ~7 to fetch, against the heuristic's 35. **On by default since entry 85.** All ten corpus countries now have a text index (~420 searches, ~3 hours of crawling). Graded against **`oracle/selection_oracle.yaml`, ground truth neither selector helped build** (entry 87): **100% role recall against the heuristic's 70% at matched budget**, and 91% when the heuristic is allowed its shipped 35 places and 3.1× the fetches. On the jointly-built oracle entries 85–86 used, the same three arms read 86%, 45% and 79% — so **entry 86's +41 points is +30**, and its +7 against the shipped heuristic is +9. The direction held; the numbers moved. It costs a second model call per corridor; one line in `runtime.yaml` reverts it. Still one run per corridor, one corridor per country, all `IN/GB`. |
| **Selection ground truth** | **`oracle/selection_oracle.yaml`, committed — twenty corridors over two travellers, plus one curated from outside the pool** (entries 87, 91, 127). The twenty-first row, `czechia/IN/GB/tourism`, is marked `curated_from: whole_corpus` and is the only one that can name a page the recall gate removes; it answers two roles of six and leaves four `unanswered` on purpose. `IN/GB/tourism` and `PH/PH/tourism` across the same ten countries, named by hand from each corridor's whole contention set. Both read **100% held**; the denominators are the finding — the same stores answer **47 of 60 roles for one traveller and 41 of 60 for the other**. A row for a corridor nobody has run is curated offline with `visa-discover contention`. No network, no model. |
| **Corpus sufficiency** | **`visa-discover coverage`, committed** (entries 90, 93, 120) — the promotion rule for stage 3. Two halves, never added. Half one reports three columns per traveller — answered **by a page**, settled **by an official tool**, open — and never merges the first two: **IN/GB 47 + 7 = 54/60 actionable, PH/PH 41 + 5 = 46/60**. Half two is every per-traveller family the store holds, from which the verdict is computed alone. Today: six countries *no per-traveller dimension*, SG and GB *bounded by the authority* (a pass), **NL `incomplete`**. Offline, no model, no search. **It says when it cannot grade, since 2026-09-01** — a country with no per-traveller family and no oracle row reads **`ungraded`**, and the report names the set once at the end. **42 of the 53 built countries are ungraded**; the six oracle countries with no family still read *no per-traveller dimension*, which is a legitimate deferral, and Portugal is graded from its family despite being outside the oracle. Formerly all 43 read *no per-traveller dimension*, which was vacuous rather than a pass (entries 116, 120). |

**The largest coverage limit is the interactive tool, not bot-blocking** — that was measured and it
inverted the assumption this file had carried for weeks (entry 58). A page that is *read* and judged
to **ask** a question rather than answer it is now a third outcome beside *found* and *blocked*: it is
named for whatever role it settles and the plan offers it beside that question (entries 59 and 60).
Getting those pages in front of the model needed the shortlist to reserve five candidates per role
rather than three, which took **the United Kingdom from 0 of 8 corridor runs resolving to 4 of 4**
(entry 61).

**The corpus stored the link and threw away the page, and that was the ranking limit** (entry 78).
`crawl._expand` read each page's HTML, kept the title and links, and let the body go out of scope, so
**93% of Japan's corpus entries have no title and the median description is 29 characters** against a
median body of 3,602. The page that fills `document_checklist` for `japan/IN/GB` was in the corpus all
along and scored 22.0 as **`visa_decision`** — the wrong role, unrecoverable at any shortlist depth.
Body text is now kept in a separate index that **ranks and never speaks**, and two request-path gates
that were deciding what a corpus build ever read — a score threshold 91% of links never cleared, and
PDFs never being followed — are lifted for the offline job.

**Can a corpus serve a corridor without live search? Site-level recall is already solved** (entry
82). Across 30 corridors into the ten corpus countries, 18 had **zero** misses, and of the 67 pages
missed in total **none were on a host the corpus lacks**. What remains is page-level and has two
causes: ordinary deep pages the budget did not reach, and spaces behind a **form** — the UK publishes
its per-nationality fee tables through a country selector with no links between nationalities, so a
crawl holds only what search seeded, at any budget. Canada's equivalent reached 213 values because
Canada published a page listing every country as a link. That second cause is the questionnaire
outcome (entries 59 and 60) appearing as a corpus gap, and the honest response is the same one.

**Discovery runs in the request path** for a destination nobody configured: the country's own
government domains are read from committed data, the corridor resolved, the plan built from what was
found. No human approves anything per request. Seven destinations are also hand-configured in
`destinations.yaml`; everything else uses the automatic path.

---

## What to do next

**[TODO.md](TODO.md) is the queue — go there.** This file deliberately does not copy it. What
follows is only the state a cold session needs to read the queue.

**Its index table is hand-maintained, and it does drift** — this line used to claim the table was
generated from the headings and therefore could not, which was false. On 2026-08-30 the table listed
its items in a different order from the bodies below it, and **eleven finished items were still
sitting in the `Now` section** with their full bodies. Both were corrected by hand. Nothing enforces
either property, so check them when you touch the file: the table must match the body order, and a
finished item moves to the `Done` index as one line, its reasoning left in DECISIONS.

**Start at item 31: the anchor scorer gates 94% of the corpus out of the selector's sight.** The
queue was re-prioritised on 2026-09-02 and the Now order is **31, 19, 17, 47, 35, 9, 2, 5**. Item 1
sat at the top of it for part of that day and is **done** (entry 126).

**Item 31's first deliverable is built and it changed the item's premise (entry 127).** Its own
question 2 — *is the gate bad, or is the 94% chaff?* — could not be asked, because the oracle was
curated from inside the gate. `contention --outside-pool`, `curated_from:` on each row and a **pool
audit** in `selection-recall` now make it askable, and the first row curated that way answers it:
Czechia's `mzv.gov.cz/…/4835385_2943205_UK_EN.PDF`, the EC decision *"establishing the list of
supporting documents to be submitted by applicants for short stay visas in the United Kingdom"* —
this traveller exactly — scores **0.0 for every role** and the selector is never shown it, while the
pool's best `document_checklist` candidate there is an Entry/Exit System page. **"The 94% is chaff
and the item closes" is ruled out.**

**And the frequency is now measured, on the owner's reframing (entry 128).** The question is not
whether the discarded 94% holds a relevant page but whether it answers a role the pool **cannot** —
a corridor filling six roles from the pool loses nothing to the gate. Over 126 (corridor, role)
cells: 87 answered from the pool, 31 unanswered by anything, 4 not applicable, **3 answered only
outside the pool**, 1 absent from the corpus. **So of the 35 roles the pool cannot answer, 3 are
recoverable — 8.6%, in 2 of 21 corridors, and 19 corridors lose nothing at all.** Quote that 19 only
with its caveat: nineteen of those rows were curated *from* the pool, and of the two curated against
the whole corpus **both** lose something. The gap is closed by triage — all 38 open cells were
listed and the plausible ones read — which is real but weaker than a curated row.

**Why item 31 sits ahead of the project's own goal (entry 125).** The selector's pool admits **49% of search results and 5.5% of corpus pages** — a 9× gap, because search returns pages whose URL and title already match visa vocabulary, which is what the anchor scorer scores. Item 19 asks whether search can leave the request path while measuring the corpus through a filter biased nine to one against it, so its "17 load-bearing search-only pages" is an upper bound on search's necessity. Item 31 tightens it.

**Item 1 was measured, promoted, finished and then cut back, all on 2026-09-02 (entries 124 and
126).** `score_link` rewarded a page for being about the traveller's **passport** country and had no
equivalent for the country they apply from — Canada's `?country=GB` page scored **-8.0** for
`application_route`, outside the pool, while its `?country=IN` sibling scored **32.0**. A page about
the residence now earns `residence_weight` on the four roles the post governs, and **nothing is
taken off** the passport page. It shipped as a *swap*; that half was withdrawn after measurement,
having removed **25 pages from the selector's pool and added none** and cost New Zealand's only
Indian visitor checklist 40 points for a traveller in Britain, where New Zealand publishes no
British one to lose to. Over all 53 corpora the final shape admits **35 pages of 186,596** and
removes none. The dimension turned out to be **4 corpora and 944 pages** (CA 538, NL 332, RO 65, HR
12), not entry 124's 21 corpora and 5,901 pages: that number counted every per-country page, and
most are embassy contacts and travel advice where zero is correct.

**The finding that came out of it is bigger than the item, and it re-scopes item 31.**
`_choose_what_to_read` pools on `best_combined() > 0` and hands the pool to the model **unsorted**,
with the scores withheld on purpose — so the scorer's ordering is consumed by nothing on the shipped
path, and `score_link` reaches a corridor as a **boolean**. Every rank measurement in entries
124–126 was grading something no corridor reads. Three of the four families item 1 was built for
already hold the answer in their own stored text — the Netherlands' UK apply page opens *"Applying
for a Schengen visa for the Netherlands in the United Kingdom"* and the index has held those 8,594
characters all along. **A weighting change is not a way past a boolean gate**, which is item 31.
Two defects were also found on the way: `_describes_country` could not read `united-kingdom` in a
path segment, so every multi-word country name was invisible unless the anchor text said it; and
Canada's `?country=GB&lob=visit`, the page a *tourism* corridor actually wants, scores 0.0 because
`score_link` returns early on an empty vocabulary — it is inside the 94% and it is not chaff.

**The earlier measurement of the same day (entry 123), which item 31 still rests on.** `_choose_what_to_read` pools only candidates the anchor
heuristic scores above zero, so **the model selector is shown 6% of the corpus** — 4,450 of 71,798
candidates over the 24 runs postdating 2026-08-30. Liechtenstein offers **2 of 7,482**, Bulgaria 8 of
6,847. Entry 81 measured this against the *shortlist*; entry 85 replaced the shortlist with the
selector and the new gate inherited the filter, which nobody wrote down.

**What it does and does not invalidate.** Entries 84–87's model-versus-heuristic comparison
**stands** — both arms filter on `> 0`, so they raced over the same 6%. What is narrower than it
reads is the absolute figures: `oracle/selection_oracle.yaml` was curated "from every candidate that
scored above zero", so "100% role recall" and `coverage`'s "47 of 47 answerable" share that
denominator. **The fixture cannot detect the filter it shares** — 88 of 88 oracle-named answering
pages are in the pool, which is a tautology rather than reassurance — so whether the discarded 94%
holds a single answer is **unmeasured**, and measuring it needs rows curated from the whole
candidate set. Item 31 carries the method.

**Four stale claims were corrected in TODO on the same pass:** item 2's remaining corpus experiment
is already answered (all 53 corpora carry their current domains), item 5's false
challenged-authority sentence has not shipped since entry 75, item 7's "the CLI cannot reach a
registry destination" was fixed by entry 45, and item 7's deployment blocker has dissolved.

Items 43, 44 and 45 are done; see below.

**What changed on 2026-09-01, in seven results (entries 118 to 122):**

- **Romania resolves and fills 5 of 6 roles** (item 45, entry 121), off `eviza.mae.ro` — including
  a per-residence checklist PDF. Austria fills two. Both were countries this project had recorded
  as never resolving any passport, and both predictions that the verdict would stand were wrong;
  their baselines were crawl-path runs taken before their corpora existed.
- **Morocco refuses with an `HTTP 200`** and is reported as `unusable` — *"too little readable text
  to trust"* — when the body is an F5 *"Request Rejected"* page. **0 of 43,153 indexed bodies hold
  one**, so the thinness guard already stops it becoming a source and this is a diagnosis defect,
  not a safety one. Reclassifying it would change what resolves a corridor: item 46.
- **The per-traveller family detector is English-only** (entry 121). Romania holds **58**
  per-residence checklist PDFs named in Romanian and `country_family_keys` returns `[]` for every
  one, so `coverage` reports it as having no per-traveller dimension. `coverage` half two and the
  crawl's family reservation both rest on that function. How general it is, is **not** measured —
  item 47.

**What changed earlier on 2026-09-01, in four results (entries 118, 119 and 120):**

- **The coverage gate was reading 42 passes nobody had earned** (item 43, entry 120). A country
  with no per-traveller family verdicted `no per-traveller dimension`, whose own sentence says the
  known-answer half settles it — and for anything outside the ten-country oracle that half held
  nothing. A fifth verdict, **`ungraded`**, now says so, and the report names the set once at the
  end. Half one's *content* still never votes; only its absence can withhold a verdict.
- **The oracle is not growing to 53, and that was measured** (entry 120). 17 of the 42 ungraded
  countries already resolve **every** passport tried, so a hand-curated row would buy a 100% on a
  half that does not enter the verdict. Of the 9 that resolve none, 6 have a named cause outside
  the store; only **LI, MA and SA** are genuinely ambiguous. The rule is now: grow the oracle one
  country at a time, after a corridor run has failed to settle the question — **`ungraded` is not a
  backlog of 42 curation jobs.**

- **Item 44 is closed and three of its six corridors improved.** Norway and Indonesia now fill
  **all six roles** — Norway off an India-specific checklist PDF, Indonesia off a VoA list page
  scoring **1.6** — and Thailand names its own e-Visa checker for the decision. Not attributable to
  the purge: five of the six had no corpus when their baseline was taken, so what these runs measure
  is the corpus arriving with the purge folded into it.
- **Three written-down diagnoses were wrong.** The Philippines' missing checklist is a **visa-free**
  corridor where none arises; Lithuania's corridor ceiling is the challenge and a dead host, not the
  `robots.txt` `Disallow` that limits its corpus; and *"all five United States gaps are
  `travel.state.gov`"* is disproved — three pages are that block, **four are `uk.usembassy.gov` and
  were never requested**. `egov.uscis.gov/processing-times`, item 44's own hypothesis, is in neither
  the US corpus nor its index.
- **`uk.usembassy.gov` answers its own `/robots.txt` with `200 text/html` and 659,508 bytes of a
  "Technical Difficulties" page**, and the corridor told the traveller their embassy publishes an
  outsized crawl policy. Every host that has ever tripped the size cap does the same thing; none was
  a large policy. Fixed as entry 119 — the verdict is unchanged, the sentence is not.

**What changed on 2026-08-30, in four results:**

- **53 of the 55 reachable countries now have a corpus and a page-text index** (item 41, entry 116),
  up from ten. Only Brazil and Uruguay do not, at one authority domain each. That closed items 30
  and 18 with it, and **batch 2 is now unblocked and deliberately not started**.
- **Breadth found four defects that depth could not** — `gov.bg` was a public suffix and made
  Bulgaria fail at *construction* (113); one PDF's NUL bytes discarded China's whole 18-minute crawl
  (114); the shallow-crawl warning gave the same advice to two opposite failures (115); and
  `is_challenge` truncated the body at 20,000 characters while Cloudflare's marker sat at 24,915,
  so unanswered challenges were stored as guidance and **retrieval could cite one** (117).
- **Item 19 is measured rather than argued, and the answer is "not yet".** Of 382 pages read by runs
  that postdate their country's corpus, **59 were not in the corpus and all 59 came from search — 17
  of them covering a role nothing else in that run covered**, including the page Bulgaria's visa
  decision comes from and the UK's form-gated fee table. Neither obvious shortcut works: a corpus is
  not a superset even where it is large. See item 19 for the method and what it does not measure.
- **The write-back only runs on the API path.** `automatic.py:414` is its one call site, so
  `visa-discover corridor` folds nothing back (`cli.py:744`). Bulgaria has `proven` entries: **0**.
  Whether the CLI should write back is an open decision, because it would mutate the store between
  `--runs` iterations, which is exactly what that flag exists to measure against.

**Earlier context that still holds, from 2026-08-29:** a traveller nobody tuned for scores **87%**
(entry 112); the trust config no longer starves a build — Germany went from 1,565 entries on one
host to 5,712 across 87 when `diplo.de` was reviewed (entries 107, 110, 111); a block is told from a
challenge (entry 109); and the role vocabulary is no longer the limit (entries 103–105).

**The open ledger on the ten built countries is six role slots** — one `general_entry` in Germany and
five in the United States behind a block that cannot be answered and never will be. Four more, in
Singapore, correctly do not arise.

**The selector question is closed** (entry 106, the owner's call). The model wins — 92% against the
matched heuristic's 47%, most recently 90% against 59% — and the twenty corridors are no longer
re-run to refresh that figure. `visa-discover selection-recall` remains as an offline regression
check; read entries 87, 100 and 106 before quoting it, because it measures agreement with pages a
person named and its known errors run against the model.

**Two things a new session should not rediscover the hard way.** A corpus rebuild re-walks its search
seeds, so it **cannot** open an address a previous build recorded and skipped — 2,965 pages crawled
bought 27 entries on the Netherlands (entry 101). And `visa-discover coverage` measures the store,
while `selection-recall` measures the corridor; a low score in one says nothing about the other, in
either direction (entries 99, 100).


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
   again. **It matters more than that wording suggested and the mechanism has moved**: it no longer
   builds the shortlist the model chooses from, it builds the **pool the model is allowed to see at
   all**, and measured over 24 runs that pool is **6% of the candidate set** — Liechtenstein 2 of
   7,482 (entry 123). Whether the discarded 94% contains answers is unmeasured and
   `selection-recall` cannot say, because its ground truth was curated from the pool. TODO item 31
   owns that; it rests on English vocabulary and per-country city labels, so it will keep degrading
   on new countries and languages. It remains the offline regression baseline. A sharply defined residual: for an Indian
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

   **And it reaches whether the corridor resolves at all, which is new (entry 118).**
   `united-states/IN/GB/tourism`, twice within seven minutes, corpus-routed so no search was
   involved: run 1 refused `decision_not_found`, run 2 resolved `resolved_decision_blocked`. The
   same three `travel.state.gov` URLs were refused in both and all three were in `candidates`, so
   `_decision_blocking_judged` answered the same question about the same pages both ways. Every
   earlier observation of this problem was about which roles fill; this one is the load-bearing
   decision. It fails safe — a lost plan, never an invented one — and it is now the counting item 17
   asks for, at no search cost.

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
   **Largely answered 2026-08-26 by entry 78 — read that first, then this for what remains.** The
   build no longer stops at its seeds: `expansion_threshold` was a *request-path* compromise that
   **91% of Japan's entries never cleared**, so the crawl fetched its seeds because almost nothing else
   was eligible. Dropped for the offline job, the same `--pages 1500` took depth beyond 1 from **4% to
   ~50%**. And the two "different misses" below are one thing, diagnosed wrong: `visaonline.html` was
   **already in the corpus**, at depth 1. `found_by` records which *description* of a URL won a score
   comparison, not which store held it — so "3 of 5 from the corpus" measured description quality.
   Of 35 shortlisted candidates only **6** were genuinely absent from the corpus. What is left of this
   problem is the last paragraph: a host lost to a transient failure. That is still unfixed.

   **Rewritten 2026-08-26 after three wrong diagnoses, entry 77.** What this entry used to say —
   Japan's corpus holds 29 mission hosts and not the London embassy, "where five of its six roles came
   from" — is **stale and was misleading**. Measured: search *does* seed
   `www.uk.emb-japan.go.jp`; it is absent because that host answers a genuine Akamai `403`, the same
   signature as Greece's `www.mfa.gr`, so nothing can fetch it. And Japan does not need it — its
   latest run filled all six roles from `mofa.go.jp` alone, from the corpus, with search down.

   **The corpus is a latency cache, so the test is its hit rate on role-filling pages** — not depth.
   Both paths are meant to find the right page; the corpus exists because a live corridor took 50+
   seconds and *which pages exist* does not vary per traveller (entry 44). Measured on `japan/IN/GB`
   with search up, right after a rebuild: **3 of 5 role pages came from the corpus.** The checklist and
   the application route came from live search.

   **Two different misses, two different fixes.** `mofa.go.jp/.../visaonline.html` sits on a host the
   corpus holds 200+ pages of — a page the crawl never reached, and a larger `--pages` addresses it
   (`host_budget` is `maximum_pages // seed_hosts`, so 1,200 over ~50 hosts is 24 pages each; the
   constant was already raised once, 200 → 1,200, after Canada showed the same symptom).
   `www.uk.emb-japan.go.jp` is missing **entirely** — it answered a transient `403` during the build,
   which was counted as one of "3 unreadable" and named nowhere, so the corpus silently lacks the host
   and will keep lacking it. **A corpus build that loses a host to a transient failure never
   notices.** That one is unfixed and is the more serious.

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

29. **The selection fixture has two travellers and one purpose.** `oracle/selection_oracle.yaml` is
   now twenty corridors — `IN/GB/tourism` and `PH/PH/tourism` over the same ten countries (entry
   91) — so the nationality-and-residence half of this is answered, and the answer is large: the
   same stores answer **47 of 60 roles for one traveller and 41 of 60 for the other**. Read the
   `held` column with care: it is a finding for `IN/GB`, curated from the page-text index, and
   near-circular for `PH/PH`, curated from the corpus itself. What is left
   is **purpose**: every one of the twenty rows is `tourism`, and the roles most likely to move are
   `document_checklist` and `application_route`. Note also that the `PH/PH` rows have **no selector
   grade yet** — that needs item 38's runs.

30. **The fixture cannot name an answer nobody could read.** Thirteen of its sixty roles are recorded
   `unanswered`, and twelve candidates are recorded `unverifiable` — plausible answers with no stored
   text. Both are honest, and both mean the denominator is a floor rather than the truth: France sits
   at 21 readable candidates of 206 because its portal answers a Cloudflare challenge, so an arm that
   picks the right France page gets no credit for it. A recall number computed on it is therefore
   "recall over what is legible", and item 5 moves the bound rather than the metric.


31. **A corpus serves the travellers whose pages an authority publishes, and no more.** Entry 88
   fixed the crawl-side half — a per-traveller family now gets reserved budget, so the Netherlands
   went from 5 tourism checklists to 14 — and in doing so measured the half that cannot be fixed
   here: **of 185 Dutch `apply-{country}` pages read, 113 link nothing and 58 link only language
   forks**, because for most residences the checklist is published on `vfsglobal.com`. Nigeria is
   handled by Belgium's TLScontact. The guidance is official and current and sits on a domain the
   trust rule refuses, correctly. This is entry 82's form and entry 59's questionnaire in a third
   shape, and the widest of the three. **The answering half is now built** (entry 89): such a page
   is *named* to the traveller with the government page that appointed it, never read and never
   cited, so `netherlands/PK/PK` now hands over the checklist link it previously withheld. What
   remains uncounted is the other nine countries, and nothing verifies a delegate's URL still
   resolves.

32. **The Netherlands is unfinished and nine corpora have never been rebuilt at all.** Entry 88
   proved the reservation on the Netherlands and did not finish it: `visa-discover coverage` reads
   `incomplete` there, with the schengen gateway at 71 of 184 opened and three complete families
   never opened. The reservation is inert where there is no qualifying family — CA, JP and GB have
   zero **that a crawl can see**, though the United Kingdom does have one across the store (entry
   90). **Singapore was checked on 2026-08-28 and is not a second Netherlands**: its
   per-nationality page is a leaf rather than a gateway, and ICA's own index yields 6 children
   rather than 198, so the missing 164 nationalities are behind a selector — entry 82's wall. A
   rebuild there buys stored text for the selector (5 of 34 have any today), not coverage. TODO
   item 35.

33. **The 47 of 47 is one traveller, and there is now a second one beside it.** Entry 91 curated
   `PH/PH/tourism` across the same ten countries: **41 of 60 roles answerable against 47 of 60**,
   both at 100% held. So the gate is no longer blind to the traveller, and two profiles is still
   two. Every row is `tourism` — known problem 29. What follows is the original entry. Against
   `oracle/selection_oracle.yaml` every answerable role's page is already in the corpus, and that
   oracle is `IN/GB/tourism` for all ten countries. The Netherlands' three answers were held before
   entry 88's rebuild and after it, so it cannot see the thing entry 88 fixed. **Do not quote the
   100% as evidence a corpus is ready.** The gate that measures the dimension which varies is built
   (`visa-discover coverage`, entry 90) and computes its verdict from the family half **alone**, so
   nothing in the tooling can make that mistake — but a person reading the first half of its output
   still can. What stays open is the oracle itself: widening it past one nationality and one
   residence is known problem 29.

34. **A recall log older than 2026-08-28 cannot say which selector wrote it, so it is not graded.**
   `RecallRecord.selector` was added by entry 91 after the grader was found reading a heuristic
   run's fetches as the model's picks. Every log on disk predates it, so `visa-discover
   selection-recall` currently grades **nothing** and says so; entry 87's numbers stand as recorded
   and are not reproducible from disk. Fixed by running the corridors again — TODO item 38 — not by
   loosening the check, which would restore exactly the mislabelling it was added to stop.

35. **The corpus-coverage gate can only see families the corpus recorded.** `visa-discover
   coverage` reads the store, so a country whose crawl never reached a per-traveller family reports
   *no per-traveller dimension* — indistinguishable, in the output, from a country that genuinely
   publishes its guidance centrally. The verdicts resting on the thinnest stores are the ones to
   doubt: **Germany at 1,565 entries and the United Kingdom at 922**, against Canada's 9,655. A
   rebuild could turn either over. Entry 90 chose the conservative reading deliberately — the gate
   says what the store contains, never what the authority publishes — and the fix is to rebuild the
   thin corpora, not to soften the verdict.

36. **A correct "no visa required" scores as a thin corridor.** Singapore's `PH/PH` row leaves
   `document_checklist`, `application_route` and `fees` unanswered *because* the answer is no visa —
   there is no application, so there is nothing for those roles to name. Every metric here counts
   them as gaps, which understates a corridor that answered completely. TODO item 39; the fix has to
   key on a decision a source **stated**, never on a tool or an unverified one, because a wrong "no
   visa" that suppresses five questions leaves the traveller nothing to notice the error with.

37. **The oracle's `unverifiable` rows are a limit of the curation tool, not of the corpus.**
   `visa-discover contention` is offline, so a candidate the page-text index holds no body for
   cannot be judged — Sweden's decision list, the Netherlands' Philippine checklist. The product
   would simply fetch those pages. So the fixture understates what is answerable, which is known
   problem 30 read from the other side. TODO item 40.

38. **A corpus entry's failure reason could never be cleared, and twelve were false.** `_entry`
   wrote only `unreadable` or `unknown`, so `readable` was a documented retention tier no build ever
   assigned — and because `merge` only moves a status up, with `unknown` below `unreadable`, a page
   that failed once kept the old sentence for ever. Twelve France entries claimed a browser
   challenge "could not be answered here" while the index held their text. **Fixed** in entry 92:
   the crawler records what it opened. The stale reasons clear on each country's next build, so any
   corpus not rebuilt since 2026-08-28 still carries them — FR and SE are clean, the other eight are
   not.

**Retired numbers**, kept so the numbering keeps its meaning: **1** (the unmeasured-product question —
entry 58), **3** ("who to believe" decided per request — entries 34, 38), **4** (the blocked-source
plan never run live — entries 56, 57), **18** (the excerpt silently deciding corridors — entry 42),
**25** (entry 27's exception not firing on the corpus path — entries 56, 57), **28** (selection graded
against an oracle the arms built — entry 87 replaces it with a curated one). Also removed as fixed: a
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
