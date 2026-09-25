# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

**How to read this file.** **Now** is what to pick up, in the order written; **Next up** follows it;
**Later** is real but not urgent; **Done** keeps finished work because what building it found is usually
why the item after it exists; **Smaller things** are one-paragraph defects with no owner yet.

## The five goals — the owner, 2026-09-23 (entry 182)

**Unordered, as the owner gave them.** Until the owner orders them, entry 148's order is the
tie-break: correctness, then optimisation, then expansion. Each row says where the goal stands and
points at the items that do the work. The detail lives in the items, not here.

| goal | where it stands | items | waits on |
| --- | --- | --- | --- |
| **Model calls paid through Ofself Personas**, on their OpenAI key | **Done 2026-09-24 (entry 188), and the route from now on — the owner.** All three calls go through Personas on Ofself's account; graded against the direct route's baselines. One Japan inference is a *Smaller thing* | 62 (done) | — |
| **~30s a corridor, with information on screen while it runs** | A fresh request is ~55s: ~25s research, ~29s plan (entry 171); the graded runs of 2026-09-25 took 35–70s. Fast mode everywhere projects ~39s. A repeat within 24h skips the plan call, not timed live | **57** (on screen, Now), **58** (research); **65** and **60** blocked | Ofself: a Fast tier setting (60) and a GPT-6 deployment (65) |
| **Hosted at a URL** | Runs on one laptop. Ofself signs users in but does not host. `POST /visa-plans` needs an Ofself sign-in since 2026-09-24 (entry 191); the stores are still local files | **7**, **20** (and 55's sign-in) | choosing a host; the refusal-storing decision in item 7 |
| **Most corridors accurate and useful** | Nothing in the repo measures *right*, only *answered* (known problem 26). **Item 70 done 2026-09-25 (entries 198–202):** of 14 corridors that read their authority and refused, 11 now answer from an official page. That took eight fixes, rule 8g, and the EU tier for Schengen members (entry 201). **The full rebuild is done and graded (2026-09-25, entries 203 and 204); next is item 63's broad answer rate, sized by the owner** | **63** | the owner's own checking (entry 68) |
| **55 → 100+ countries** | 55 have a registry row and a rebuilt store; 143 have no row. The page offers all 198 (known problem 23). Schengen's EU half of item 2 is done (entry 201); governments with no hostname marker remain | **64**, **2** | nothing external — search credit only |

**Offline cost is not the constraint — the owner, 2026-09-23 (entry 184).** Build time and a higher
one-time cost are acceptable for anything that makes each live request better. Prefer an offline
fix to a per-request one.

**What is left half-done** — the loose ends a cold session trips on — is listed once, in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) under *Where it stands*.

**The goal this list serves — the owner, 2026-09-07 (entry 147).** **The objective is providing the
right information. Latency and cost are the constraint it fits inside, not the goal.** A country is
built offline — corpus plus page-text index — and a corridor answers from that store; **search does
not have to leave the request path, provided it can be justified as giving reliable information at a
cost that is not high.** On cost and time it passes: **search is about $0.054 of a $0.31 corridor,
roughly 18% of the money and 8% of the seconds; the model calls are $0.251, measured live** (entries
159 and 171). On reliability nothing here can answer it — see entry 147, and
known problem 26. The older measurement below still stands on its own terms: of 382 pages read by runs that postdate their country's corpus, **59 were not in the
corpus and all 59 came from search — 17 of them covering a role nothing else in the run covered**.
So the corpus is not yet a superset, not even where it is large: Bulgaria has 7,098 entries and
still gets its visa decision from a search-only PDF. Read entries 159 and 160 before proposing to switch search
off for anything.

**Item 51 was measured on 2026-09-15, and search stays on every corridor (entry 159).** The owner
asked for search to run only where the corpus could not answer. Two shapes were tried and neither
pays:
- **Searching after the corpus leaves a role open** projects −3% money and **+4% seconds**, because
  7 of 15 corridors would do the whole pass twice. It also never searches where the corpus filled a
  role with a general page and search had the traveller's own embassy page (Japan `PH/PH`, UK
  `PH/PH`).
- **Deciding per query from what the corpus holds** loses 5–6 of the 8 search-only pages that
  answered.

**Then the purpose query was measured, and it stays (entry 160), which closes item 51.**
- **It finds pages no other query finds.** Of the 45 pages it was first to return, 28 are still
  returned by it alone.
- **It changes answers.** Without it, in both runs:
  - Japan `IN/GB`'s checklist from the London embassy became a questionnaire, and its decision moved
    to a general ministry page;
  - Norway `IN/IN`'s January 2024 checklist was replaced by an older file.

**Item 48 was worked the same day (entry 161).**
- **Root seeding was probed and rejected:** 0 of 9 target pages were reached from their roots.
- **The real gap was a build discarding its own search seeds.** That is fixed, and Norway, Thailand
  and Japan were rebuilt with it.
- **A matched test found Thailand `IN/GB` resolving in 4 of 4 runs where it had refused in 4 of 4**,
  for about 9% more a corridor.

**The owner then chose not to wait for the new key, and all 53 corpora were rebuilt the same day**,
which closed item 48. Preparing and running it fixed three more defects: a failed search query no
longer costs a build (entry 162), a `www.` host and its bare host share one crawl budget (entry 163),
and a malformed redirect no longer ends a build or a corridor (entry 176).

**Re-ordered 2026-09-14 by the owner's rule for the hybrid (entry 148).** **The corpus holds what
every traveller shares; live search fetches what this traveller needs, and stays the minority.** So
the Now section leads with **correctness** — item 52 first, a defect found in the same survey and
done the same day (entry 149), then item 53, which building it found and which was also done that
day (entry 150), then 17 — counted and closed that day too (entry 151) — then 8, read that day as
well (entry 152), then 9 — re-scoped and closed that day (entries 153, 154) — then 54 (done that day, entry 155) and 21 (closed that day, entries 156 and 157) — and
**optimisation** follows it: 31 (done that day, entry 158), then the new item 51 (5 of a corridor's 15
live queries carry no traveller detail — closed 2026-09-15 with all three kept, entries 159 and 160),
then 48. **Item 49 stops where it is**, and 35 and 47 move
to Later: all three exist to make the store cover every traveller and residence offline, which the
rule hands to request-time search. **Expansion** — item 2's rule question, the 143 countries with
no registry row, deployment — comes after both.

**Item 49's seeding half shipped on 2026-09-06, its premise was wrong, and the rebuild that priced
it failed its own bar.** The item proposed a **search query** for the ministry's index of its own
missions; **44 of the 53 corpora already record one and 34 never opened it**, so this was allocation
rather than discovery (entry 137). The seed shipped, Australia was rebuilt, and **the family went
from 1 member recorded to 166 while `uae.embassy.gov.au` stayed at 0** (entry 138). The corpus can
now point at the post and still does not walk to it, for two measured reasons: `www.dfat.gov.au`
times out on 22 of 25 opens, and every member scores 0.0 so the queue's order is the order the links
sit on the page — both alphabetical heads, and `united-arab-emirates` is in the tail. **That, not
another rebuild, is what item 49 has left.**

**Item 50 is done (entry 135), 2026-09-05.** Item 50's own premise was wrong and
checking it made the defect worse — the shortlist shares **five** renders, not twelve — so one
client-rendered host could take the whole allowance, and a page nobody rendered was reporting itself
as a page with nothing to read. Both fixed; the **total** deliberately stays at five until a sweep
reads the new reasons.

**Items 49 and 50 were new on 2026-09-04 (entry 132).** A 27-country sweep for
`BD/AE` — a traveller nobody tuned for — filled **142 of 162 roles, 88%**, with **75% of what it read
served from the corpus**, and found two defects breadth alone could reach: the corpus holds **no
mission for the country the traveller applies from** (Australia 1,599 pages on `embassy.gov.au`, 0 on
`uae.embassy.gov.au`), and **one client-rendered host can spend a corridor's whole render budget**
where the crawl has capped that since entry 92.

**Item 48 was the lead, 2026-09-02 (entries 129, 130).** The corpus's gaps were
categorised and the largest cause turned out not to be a gap at all — 12 of 30 role-cells nothing
answers are an **official tool** holding the answer, which the product has resolved since entry 63.
Of what remains, the cheapest lead is that **1,148 of 2,222 hosts (51.7%) have pages in the corpus
and their root was never visited**. Item 48 is the experiment that decides whether seeding those
roots helps, and it exists rather than a patch because Thailand showed item 35 is **two** problems —
entering a site in the wrong place, and spending the budget on the wrong part of it once inside —
and root seeding could make the second worse.

**Item 1 was promoted to the top on 2026-09-02 (entry 124), finished the same day, and then cut
back the same day (entry 126).** A page about the country the traveller applies from now earns
`residence_weight` on the four roles the post governs, and **nothing is taken off** the page about
their passport country. It shipped as a *swap* — the passport bonus withdrawn and the residence
bonus put in its place — and that half was withdrawn after measurement: over 53 corpora it removed
**25 pages from the selector's pool and added none**, and it cost New Zealand's only Indian visitor
checklist 40 points for a traveller in Britain, where New Zealand publishes no British one for it
to lose to.

**The finding that came out of asking why a URL scorer is deciding this at all is bigger than the
item.** `_choose_what_to_read` pools on `best_combined() > 0` and hands the pool to the model
**unsorted**, with the scores withheld on purpose. So the scorer's ordering is consumed by nothing
in the shipped path — it reaches a corridor as a **boolean**. Item 1 in its final shape admits
**35 pages of 186,596**, and three of the four families it was built for already hold the answer in
their own stored text. **Item 31 is re-scoped around that and is the top item.**

Entry 124's "21 of 53 corpora, 5,901 pages" was the whole per-country dimension; the *application*
families inside it are **4 corpora and 944 pages** (CA, NL, RO, HR). Finding them needed a
different instrument, and that is item 47's real premise — `country_family_keys` reads the URL, so
it sees neither Canada's `?country=IN` nor Romania's `MAREA-BRITANIE.PDF`.

**The first re-prioritisation of 2026-09-02 (entry 123).**
The model selector is shown **6% of the corpus** — 4,450 of 71,798 candidates over 24 runs — because
`_choose_what_to_read` pools only what the anchor heuristic scores above zero. Liechtenstein offers
**2 of 7,482**. That makes **item 31 the top item, re-scoped** from "improve the ordering of the 6%"
to "can stored text put a candidate into the pool at all", and it puts a co-cause under every country
whose failure has been attributed to a challenge. The arm comparison of entries 84–87 is
**unaffected** — both selectors filter on `> 0`, so they raced over the same 6% — but the absolute
recall figures have a denominator curated under the same bound.

Four claims in this file were stale and are corrected in place: item 2's remaining corpus experiment
is **already answered** (all 53 corpora carry their current domains), item 5's "the interface tells a
challenged authority it does not permit automated retrieval" has been **false since entry 75**, item
7's "the CLI cannot reach a registry destination" was fixed by entry 45, and item 7's deployment
blocker has dissolved. Item 9 moved up to Now; item 46 moved to Later.

**Where the list stood, 2026-09-01.** **Item 44 is done** (entry 118). Six corridors were re-run
over the countries whose ranking text had been a bot-check page: **Norway and Indonesia now fill all
six roles** and Thailand names its own checker for the decision, while the Philippines' missing
checklist turns out to be a **visa-free** corridor where no checklist arises. Three written-down
diagnoses were corrected, and one of them became entry 119: the United States loses four
`uk.usembassy.gov` pages — the post an Indian applicant in Britain actually uses — because that host
answers its own `/robots.txt` with 659 KB of HTML. **The United States corridor also flips between
two runs of identical code with no search in it**, which is new and belongs to item 17.

**Where the list stood, 2026-08-30.** **53 of the 55 reachable countries now have a corpus and a
page-text index** (item 41, entry 116) — only Brazil and Uruguay do not, at one authority domain
each. That closed items 30 and 18 with it. The three items that used to gate everything were
finished earlier and confirmed by live runs: **item 22** (the corpus replaces the crawl, entries
49–53), **item 23** (the vocabulary could not recognise a page that *states* the visa answer, entry
56) and **item 3** (the twenty-corridor measurement, entry 58, which passed marginally).

**Building the 43 found three code defects that no amount of depth would have** — a public-suffix
domain that made Bulgaria fail at construction (entry 113), one PDF's NUL bytes discarding China's
whole crawl (entry 114), and a shallow-crawl warning that gave the same advice to two opposite
failures (entry 115). A fourth came out of item 42: `is_challenge` truncated the body at 20,000
characters, so **414 stored bodies across nine countries were a bot-check page rather than the
authority's** (entry 117). That is the fourth, fifth, sixth and seventh defect found by breadth
rather than by depth, which is the standing argument for running countries nobody has run.

**Selector work now has ground truth it did not build** (item 34, entry 87). The measurement harness
that produced entries 84–86 was grading both arms on a set they made between them; the independent
version is committed at `oracle/selection_oracle.yaml` and says entry 86's +41 points is **+30**. The
direction held. Two things it hands to the items below: thirteen of sixty roles have no readable
answer at all, and the fixture is still one nationality and one residence.

**And the corpus does not generalise across travellers** (entry 88). A build reads 3–15% of what it
records, and the page answering a *specific* traveller sits one hop below something it recorded and
never opened — the Netherlands held 219 `apply-{country}` pages and **five** tourism checklists. That
is fixed and proved on one country (item 35), and it exposed a wider limit that is not the crawler's:
for most residences the Netherlands publishes its checklist on **VFS Global**, which the trust rule
refuses — now named to the traveller rather than withheld (item 36, entry 89).

**And the oracle now has a second traveller** (entry 91). Twenty corridors, `IN/GB/tourism` and
`PH/PH/tourism` over the same ten countries. Both read 100% *held* and the denominators are the
finding: the same stores answer **47 of 60 roles for one traveller and 41 of 60 for the other**.
Building it exposed a defect in the grader, fixed under item 38 (entries 97–98).

**The gate is built and it is now the promotion rule for stage 3** (item 37, entry 90).
`visa-discover coverage` reports two halves that are never added: the 47 of 47 known answers, which
is one traveller and stays as a regression check, and the per-traveller family, which is the
dimension that varies. Six of the ten corpora have no per-traveller dimension at all, Singapore and
the United Kingdom are *bounded by the authority* — a pass — and **only the Netherlands is
`incomplete`**, with three complete families never opened. Two things it corrected on the way: a
gateway cannot be told from a leaf by counting children, and the United Kingdom has a per-traveller
family where entry 88 counted none.

**Search has credit again, and the three things that were gating stage 3 are fixed and confirmed
live**: pacing and `402` classification (entry 74), the post mis-pick (entry 72, six of seven
regression corridors correct), and the challenge (entry 75, Cyprus and India recovered — 41 - 9 - 2 =
**34 of 41 now answer**). **Stage 3 is clear to run.**

**But do not expect it to add coverage** (entry 76). Measured first: search supplies 30–67% of the
pages a corridor actually reads even in the ten best corpus countries, and none of the seven remaining
refusals can be fixed by a crawl, because every one of them fails at *retrieval* — the corpus builder
hits the same wall. Stage 3 buys latency, passport-stability and outage tolerance. **The next coverage
win is search recall, which nobody has measured** — see entries 159 and 160 and known problem 13.

**Item 5's challenge half is done** (entry 75): `challenged` is its own outcome, detected from headers
**and body**, answered by the renderer under our own user agent, and `render_mode` is now `on_demand`.
**Cyprus resolves.** Greece's genuine refusal is untouched. Two residuals worth knowing: Slovakia
challenges every page and spends its render budget before reaching the decision, and Lithuania's
challenge fingerprints past the user agent — recorded as `challenged`, and not worked around.

**Item 30 is finished, all three stages.** All 41 never-run destinations ran on 2026-08-25 — 103
corridors — and every one resolved or refused for a verified reason; 32 of 41 answered at least one
passport. The sweep also found two defects no five-country corridor could (entry 71) and closed
known problem 27 with a measurement. Stage 3, the 43 corpora, was built on 2026-08-30 (entry 116).
**Batch 2 is therefore unblocked and deliberately not started** — see the *Done* row for what that
does and does not license.

**The session of 2026-08-24/25 asked what the rigor costs and answered it** (entries 63–66). Short
version: **the rigor is cheap and the backlog is expensive, and it has been easy to mistake the second
for the first.** Of 198 countries, 157 are refused before a page is fetched and every one of those is a
registry job nobody has run. A one-off control arm — plain web search, no trust model — was ~5× faster
and answered more, and cited **0 of 8 hosts that would pass the trust rule**. Read entry 64 before
arguing to relax anything; it cuts both ways.

**Item 2 follows item 30, and its cheap half is done.** It was `soon` for weeks as a coverage complaint;
entries 63 and 64 measured what that complaint is made of and it is almost entirely this item.
**Entry 65 did the corrections half on 2026-08-25** — three missing markers, coverage 39 → 41
researchable, and the "row with nothing confirmable" bucket emptied.

**The measurement is done too (entry 66), and it settled the design question.** Of the 16 governments
with no marker: a TLS certificate names the organisation for **9**, RDAP for 1 (dropped), and **7 have
nothing machine-readable**. So the rest is reviewed rows, not automation — but the review is nine
certificate confirmations and seven pieces of research, one time.

**Batch 1 is *reachable*, which is not the same as done — entry 68.** The EU and EEA went 41 → 53
researchable, and that is stage 1 of three. That rule — no further country until batch 1 clears
reachable, resolves and fast — **has now been satisfied** (item 30, 2026-08-30), so batch 2 is
unblocked. Liechtenstein is the reminder that "clears" is not "answers": it has a 7,456-page corpus
and fills no role, because `llv.li` challenges every request (entry 117).

**Batch 1 is every reachable country** — 53 when this was written, **55 since 2026-08-29** when
Iceland and Liechtenstein gained their first domains (entry 110). Not the fourteen: those were
catching up to the rest, and counting the rest the same way found the real gap. **41 of the 53 had
never had a corridor run against them**, which is not the same as failing. Iceland and Liechtenstein
have now had one each (entry 116): Iceland fills five roles and names its visa checker for the
sixth, Liechtenstein fills none, which item 42 traced to a challenge our renderer cannot answer. **53 of the 55 now have a corpus and a text index**
(entry 116); only BR and UY do not. **Accuracy is verified by the project owner
outside this repository** and is deliberately not a stage; do not build a correctness grader here
without asking.

The method for a country the rule cannot confirm is settled and cheap: ask Wikidata about the *domain* —
`haswbstatement:P856=https://<domain>/` — and check `P17` against the country. It recovered 6 of the 8
refusals in batch 1 and guesses no names. TLS certificates managed only 2 of 8 here against entry 66's
9 of 16, because that measured each country's known-correct domain while this measures whatever search
found.

**The rest of the sweep no longer waits behind item 30, which is done.** 143 countries have no row at all — 4 searches each.
Two things to know before spending it: **fix the search rate limiter first** (see *Smaller things* — a
capped plan answers `402`, which reads as *out of credit* rather than *too fast*), and **the sweep does
not build the corpus.** The corpus is a separate, far larger job and is a speed
optimisation rather than a prerequisite; a country without one crawls in the request path exactly as it
does today. The rule is also refusing correct authorities *inside* countries it accepts — a one-off
control arm cited `india.diplo.de`, Germany's own mission, declined for want of a marker.

**Then item 17, now that 24, 25 and 26 are settled.** Items 24 and 25 took the United Kingdom from
refusing every corridor to resolving all four: a page that *asks* a question is named for the role it
settles (entries 59–60), and the shortlist reserves five per role rather than three so the answering
page actually reaches the model (entry 61). Item 26 was then measured and **closed without a code
change** — four candidate fixes, four disproofs, and a residual cost of 0.27 shortlist places per
corridor (entry 62).

**For context, and it is what those items grew out of:** item 3 measured the largest coverage limit
there is and it was not the one this file had been assuming — every United Kingdom corridor refused
*after* finding the checklist, the route, the times and per-nationality fees, because the decision
lives inside a wizard. Item 24 gave a corridor the words to say so, entry 60 widened it to every role,
and item 25 got the answering page into the shortlist it was falling five-deep out of. Items 17, 18 and
19 are the corpus work item 22 grew out of, and 19 closed on 2026-09-15 — the crawl went, and search stays (entries 159
and 173).

Status: `next` · `soon` · `blocked` · `later` — the label on each heading matches the section it sits in, so the two
can never disagree. **Blocked** holds an item with a dependency it cannot clear itself; each says what it waits on.

**Every open item has a number, and numbering is append-only** so that the cross-references in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) stay valid. The numbers are names, not an order: **the section
decides the order**, and a gap in the sequence means an item was finished or dropped. Finished items
keep no number — a number is a handle for pointing at work still to be done — and *Smaller things* are
one-paragraph defects rather than items.

| | | |
| --- | --- | --- |
| **Now** | 63. Make most corridors return accurate and useful information | `next` |
|  | 57. Stream the plan to the screen as it is written | `next` |
|  | 64. Expand from 55 countries to 100+ — ask the owner before a batch | `next` |
| **Next up** | 61. Decide what a corridor may spend answering a challenge | `soon` |
|  | 2. Amend the trust rule for governments with no marker, and for Schengen | `soon` |
|  | 4. Decide the client-side retrieval question | `soon` |
|  | 7. Put it somewhere others can open it aka deployment | `soon` |
|  | 20. Make the stores substrate-swappable and durable | `soon` |
|  | 55. Take the traveller from Ofself's shared identity, through one adapter | `soon` |
|  | 59. Guard the 272K-token price threshold | `soon` |
|  | 58. What is left of model-call cost and research latency | `soon` |
| **Blocked** | 60. Decide where Fast mode goes — on Ofself adding a tier setting | `blocked` |
|  | 65. Test GPT-6 Sol against GPT-5.6 Terra — on Ofself deploying GPT-6, or OpenAI credit | `blocked` |
|  | 67. Test ranking by embeddings of stored page text — on OpenAI credit | `blocked` |
| **Later** | 69. Read scanned PDFs — for ranking first, and as evidence only after a decision | `later` |
|  | 49. The family is walked at 25 members a build and has 169 — stopped by entry 148 | `later` |
|  | 35. Finish the Netherlands, then roll the family reservation across the other nine | `later` |
|  | 47. Find out how much of the world the family detector cannot see | `later` |
|  | 46. Decide what to do about a refusal served as `HTTP 200` | `later` |
|  | 27. Decide whether a hosted scraping service may be used, and only for corpus discovery | `later` |
|  | 10. Try sitemaps before crawling | `later` |
|  | 11. Decide whether a host that has refused every request should be skipped | `later` |
|  | 12. Watch where the two deciders disagree | `later` |
|  | 13. Revisit conflict detection, with claim scope | `later` |
|  | 14. Detect drift in configured sources | `later` |

---

## Background

The direction was set by an outside review on 2026-08-18, agreed with in full and recorded as
[DECISIONS.md](DECISIONS.md) entries 29–35, plus 36–42 which came out of building them. **Read those
before picking anything up here.** In one line: the posture, not the principle, is what was costing
coverage (entry 35). Everything from that review is implemented or explicitly answered except two
parts of entry 35 — asking authorities for access, and the client-side retrieval question, which
nobody has argued yet (item 4).

**One habit matters more than the list.** Repeatedly, a constraint has turned out not to be where the
documentation said it was — the corrections table in [CORRECTIONS.md](CORRECTIONS.md) has over two hundred and fifty rows and every
one cost a session. **Prefer running a corridor to reading a code path**, and when an item below
proposes a fix, measure the proposal before implementing it. Several items here were written from a
careful reading and were wrong.

---

## Now — pick these up in this order

**Surveyed 2026-09-25, after the full rebuild.** The rebuild sequence that stood here is finished
(Done), and so is item 68. Items 65 and 67 were listed next and cannot run — 65 waits on Ofself
deploying GPT-6, 67 on OpenAI credit — so both moved to **Blocked**. What is left follows entry 148's
order: correctness (63), then the owner's on-screen goal (57), then expansion (64, which asks the
owner first). Hosting and Ofself (7, 20, 55) are independent and fine to run alongside.

### 63. Make most corridors return accurate and useful information — `next`, **added 2026-09-23 (entry 182); moved to Now 2026-09-24 as step 3 of the rebuild sequence**

**Why it matters.** It is the owner's goal and the objective entry 147 set: right information first.

**The bound on it.** Correctness is checked by the owner, outside this repository (entry 68). **Do
not build a truth set, a correctness grader or an accuracy metric here without asking.** What this
item may do on its own is measure what corridors *answer*, and report it with known problem 26's
caveat.

**Where it stands.**
- **The last broad measurement is 2026-08-24's twenty corridors** (entry 58). 75% confirmed the
  decision and 50% yielded a checklist, a marginal pass. That sample was five destinations, each
  replicated four times.
- **All 55 stores were rebuilt by 2026-09-25 (entries 193, 203, 204).** Graded on the oracle
  corridors' stores and item 70's corridors: every oracle answer held, and item 70's corridors
  answer as before or better, except Egypt's roles-call variance. About 30 of the rebuilt countries
  have had no corridor run.
- **Since then, the plan has changed in ways that show up in its answers.** The decision and every
  requirement now carry a checked quote (entry 156), a missing checklist is worded as what was found
  (entry 153), and absence from a visa-required list counts as "no visa" (entry 172, checked on
  Singapore only).

**Next step — a broad answer rate on the rebuilt stores, sized by the owner.** The owner dropped the
pilot's before-and-after comparison (a rebuilt store should answer on its own merits), so this is
one arm. Corridor runs cost search only on Personas, about $0.05 each.
- **Choose the corridors by destination, as entry 58 advised,** among the rebuilt countries no
  corridor has touched. Agree the number with the owner first, because the owner checks them.
- **Run each at least twice** (entry 144), through `var/item70-2026-09-24/run.py`, which keeps the
  packets a refusal needs traced.
- **Report decision and checklist rates beside entry 58's**, and put the plans in front of the owner.

### 57. Stream the plan to the screen as it is written — `next`, **a UX improvement, added 2026-09-15; moved to Now 2026-09-25**

**Why it matters.** A fresh request takes about 55s and a repeat about 24s (entry 171) — a repeat within
24 hours now reuses its plan instead (entry 178) — and the
traveller sees nothing until the whole plan arrives. More than half of a fresh request, and nearly
all of a repeat, is the model writing the plan. Streaming would not shorten any of that, but text
could appear seconds after the plan call starts rather than when it ends. **Item 56 took about 1.5s off the plan call (entry 175); this makes the rest feel shorter.**

**What stands in the way — to be designed, not assumed.**
- **The plan is validated as a whole before anyone sees it:** `VisaPlan`'s validators,
  `QuoteChecker`, the rule that a null decision is never `verified`, and the entry-plan shape
  (entries 95, 150 and 156). A half-written plan has passed none of them. Nothing streamed may show
  a claim the finished plan could still drop or refuse — the visa decision above all.
- **One safe shape streams progress rather than content**: which stage the request has reached —
  searching, choosing pages, reading them, writing the plan. Another streams only the parts that are
  already final. Which parts qualify is the design question.
- **The call uses strict structured output** (`with_structured_output`, `json_schema`). Streaming
  partial JSON through LangChain and FastAPI to `static/app.js` is a real change at both ends.
- **A refusal can arrive after text has started to appear**, and the interface would need an honest
  way to take it back.

**Measured, 2026-09-16 (entry 177).** The plan call's first visible token arrives 7–15s in today and
4–7s on Fast mode, so streaming would put text on the screen that early.

**The owner's goal settles half of this (entry 182):** about 30 seconds, *with information on
screen while it runs*. So at least the progress shape is wanted, whatever else is decided.

**Open for whoever picks it up:** whether streaming progress alone is enough, and whether any plan
content can be shown before validation without breaking entry 6's rule against unverified claims that
would alarm a traveller if wrong.

### 64. Expand from 55 countries to 100+ — `next`, **added 2026-09-23 (entry 182); moved to Now 2026-09-25 — ask the owner before a batch**

**Why it matters.** It is the owner's goal. The page offers 198 destinations and refuses 143 of them
(known problem 23).

**What adding a country takes — the three stages of entry 68.**
0. **Ask the owner first**: which countries, and how many (*Order*, below).
1. **Reachable:** a row in `config/authority_domains.yaml`, from `visa-discover registry`. Where the
   rule cannot confirm a domain, ask Wikidata about the domain and review it by hand (entries 67,
   110 and 111). Item 2 covers the governments with no marker, and the rule itself never bends.
2. **Resolves:** a corpus and page-text index from `visa-discover corpus --country XX`. Then run
   corridors and read every refusal's reason, as stage 2 of batch 1 did (entry 70).
3. **Fast:** the corridor answers from the store without crawling.

**What it costs, as arithmetic, not measured.**
- **The registry sweep:** about 4 searches a country, so the remaining 143 countries come to about
  $3 of search.
- **Corpus builds:** 42–56 queries a country in the 2026-09-25 rebuild, about 22 minutes a country
  two at a time (PROJECT_HANDOFF). Fifty more countries is about **$12** and roughly ten hours.
- **No model cost to build.** Corridor runs for stage 2 go through Personas and cost search only,
  about $0.05 each.

**Order.** Entry 148 puts expansion after correctness and optimisation. The owner listed the five
goals unordered, so ask before starting a large batch. Pick countries by traveller volume, as batch
1 did (entry 67).

## Next up

### 61. Decide what a corridor may spend answering a challenge — `done` for the script question (entries 201, 202); the render budget below is still open, **added 2026-09-16 (entry 179)**

**Why it matters.** Half the challenges met today cannot be answered, and France's corridor stops
reading its own portal after five pages.
- **12 of 24 sampled challenges stayed a challenge**: Norway, Liechtenstein, Finland, Indonesia,
  Thailand, Lithuania, the Philippines and `ezov.mzv.sk`. In every one, the only request the render
  gate aborted was `challenges.cloudflare.com`. None of the 12 answered asked for it.
- **France's two latest corridors left 14 of 17 challenged pages unrendered**, because the run's five
  renders were spent. The challenge itself is answered in about five seconds.

**Closed 2026-09-25.** EUR-Lex pages may reach AWS's challenge-token host (entry 201). Cloudflare's
host was approved and measured, and not shipped (entry 202): with it allowed, 6 of 7 Cloudflare
pages still refused our headless browser as a bot, and passing would mean disguising the client.

**Two decisions, both the owner's.**
1. **May a challenge render load Cloudflare's own challenge script?** Entry 13 says a render trusts
   nothing new, because script running in the page decides what the evidence says. The exception
   would be that one host, only while answering a challenge, never on a thin-page render.
   - **Whether it works is not measured, on purpose**: trying it is the change.
   - **An interactive check — a checkbox or a puzzle — is a CAPTCHA** and stays out of bounds whatever
     is decided here.
2. **Should a corridor's five renders grow, or be kept for pages a challenge guards?** An answered
   challenge costs 4–13s and a failing one the full 20s. Priced in seconds only: nothing yet shows the
   extra pages change an answer.

**Before either ships**, run France `BD/AE` and a Liechtenstein corridor several times in each arm,
with the cache warm in both (entry 136), and count roles rather than pages.

### 2. Amend the trust rule for governments with no marker, and for Schengen — `soon`; **the Schengen half done 2026-09-25 (entry 201)**, and Germany is the worked example

**Schengen done 2026-09-25 (entry 201): the EU may answer a member's visa decision.** The
consolidated regulation on EUR-Lex and the ETIAS page, read from a shared EU store; Croatia `BD/AE`
answers from it. What is left here is the other half — governments with no hostname marker.

**Six more domains landed for five countries on 2026-08-29 (entry 110), and `audit` now reads
`row, no confirmable domain: 0`** — Iceland and Liechtenstein were refused outright and are now
reachable, taking researchable from 53 to **55**. The transferable lesson is about *method*:
`unconfirmable` is what a search turned up, **not** a shortlist of the authority's real domains, and
promoting from it would have trusted three wrong domains while missing three right ones. Ask Wikidata
for the **organisation**, then read its `P856`/`P17`. `iom.sk` was examined and **rejected** — it is
the International Organization for Migration, not Slovakia's government.

**Twelve more landed the same day on the owner's judgement (entry 111), and no country is thin any
more.** Bulgaria, Denmark, Iceland, Liechtenstein, Lithuania, Luxembourg, Norway and Slovakia all
carry two to four domains now. Five were read from the page's own title; six are marked "Judgement"
and "Owner's call" in the file because the site is behind a challenge or renders client-side. **The
standard `reviewed` now carries is "a person decided, and the file says what they had"** — read entry
111 before adding more, and keep marking the tier.

**Brazil and Uruguay still carry one domain, correctly.** `liveinuruguay.uy` is a relocation
promotion and `gub.uy` already covers the government. **`iom.sk` stays refused** — it is the
International Organization for Migration, which passes the own-TLD half and fails the governmental
one, and it is left in `unconfirmable` so the next reviewer meets it.

**~~Untested: whether any of the nine gains what Germany gained.~~ Answered 2026-09-02, and the
answer is no.** Every one of the 53 corpora was checked against the registry it was built from:
**all 53 already carry their current domains**, and the only gaps anywhere are `uaelegislation.gov.ae`
and `geds-sage.gc.ca` — a legislation site and a staff directory, on two countries that already
resolve. Bulgaria, Denmark, Iceland, Liechtenstein, Lithuania, Luxembourg, Norway and Slovakia were
**built on 08-29/08-30 with their new domains already trusted**, and they still fill little. So the
Germany-shaped win does not repeat here and there is no build to run; the causes are the challenges
and stated `Disallow`s already named, plus the pool gate — which entry 158 widened, and in one run Liechtenstein's pool went from 2
to 21 and the corridor still refused on its challenge. **What is left of this item is the rule question, not the coverage one** — Schengen and
`europa.eu`, and the rule refusing correct authorities inside countries it accepts.

**Germany is done and it worked (entries 107, 108).** `diplo.de` is now `reviewed` — the warrant is
that the already-trusted `auswaertiges-amt.de` prints "Website http://www.washington.diplo.de" under
"Consulate General of the Federal Republic of Germany", which is entry 89's two-part test satisfied
from stored text, after TLS failed to confirm it. Rebuilt: **1,565 entries on one host → 5,712 across
87**, `germany/PH/PH` now fills **6 of 6** and `germany/IN/GB` 5 of 6. Both `document_checklist`
slots closed; one `general_entry` remains. **The rest of this item — the other fifteen countries with
no governmental marker — is untouched and is still the work.** What Germany shows is the size of the
prize per country.

**The original case, kept because it is the worked example (entry 106).** Germany's corpus
is **1,565 entries and every one is `www.auswaertiges-amt.de`** — not a single mission page — because
`authority_domains.yaml` lists **`diplo.de` as `unconfirmable`**: under Germany's own top-level domain,
no governmental hostname marker, so never fetched. The Federal Foreign Office defers to its missions
in its own words — *"you should consult the requirements well in advance… to find out about the
documentation which has to be submitted"* — so `document_checklist` and `general_entry` are open for
both travellers and no crawl of the ministry can close them.

`diplo.de` is the Foreign Office's own mission network (`uk.diplo.de`, `manila.diplo.de`), so the
evidence for reviewing it is the evidence that already justified `auswaertiges-amt.de`. Adding it is
the `reviewed` escape hatch entries 33 and 34 designed. **It is a trust decision** — this file says
editing `trusted` by hand is one — so it wants a DECISIONS entry naming the evidence, not a quiet
edit. Expect it to close 4 of the 9 remaining open slots.

**Why this is now first.** Measured 2026-08-24, entries 63 and 64. Of 198 countries offered, 157 are
refused before a page is fetched and **every one of them has no registry row at all** — unfinished
data, not rigor. And the rule does not only refuse whole countries: a one-off control arm — open-web search
with no trust model, run on three corridors and then deleted (entry 64) — cited `india.diplo.de`,
which **is** Germany's own diplomatic mission giving guidance to exactly that traveller, and the rule
declines it because `diplo.de` carries no governmental marker. That is this item, with a measured cost
rather than a description.

**First, what `looks_governmental` actually is**, because its name misdescribes it and that makes the
whole rule read as flimsier than it is. Probed against adversarial hostnames 2026-08-18:

```
visa-gov.com  gov-uk.com  govuk.com  mygov.in  e-gov.in  thegov.uk
gov.sg.evil.example   immigration.gov.in.attacker.net   esteri.it.visa-help.com
    -> every one rejected
fakegov.gov   help.gov.co   visa.gov.tk   -> accepted
```

The regex only matches a marker at a **label boundary anchored to the end**, so it cannot be spoofed by
putting "gov" in a name — `gov.ica.sg` and `go.mofa.jp` are both rejected. What the three accepted ones
have in common is that they genuinely sit under `.gov`, `gov.co`, `gov.tk`: **namespaces whose registry
restricts who may register.** You cannot buy `foo.gov.sg`. So the check is not "reads as official" — it is
"sits inside a registry-controlled government namespace", which is a real, unforgeable property and
exactly the kind of thing this project's trust model wants.

**So judge it by the right standard:**

| As a test of | Verdict |
| --- | --- |
| *this IS official* (sufficient) | **Sound.** Registry-backed, zero false positives in the probe above. |
| *only these are official* (necessary) | **Wrong, measured 19 of 51 — 16 after entry 65.** Where a country has no government namespace there is no signal to find, so no regex can ever fix the rest. |
| *this is a **visa** authority* | **Does not try.** `nasa.gov` and `recreation.gov` pass as US own-government. Bounded by the cap and corroboration bar (entry 22), not by this rule. |

That is why the fix is to **add other sufficient conditions, never to loosen this one** — and why
renaming `looks_governmental` to something like `in_government_namespace` is worth doing while here.

**The tension this item must resolve, and currently ducks.** "A reviewed authority domain" was written
without saying *how the reviewer knows*, and hand-reviewing 198 countries is the manual curation the
production goal exists to remove. Four mechanisms could supply officialness without per-country
judgement, and the cheap measurement comes first:

1. **The government's own published domain list.** Where a country publishes one, that is the
   destination's own government asserting which domains are its own — this project's trust model applied
   recursively, no human taste involved. Strongest where it exists; coverage patchy.
2. ~~**Registry (RDAP/WHOIS) organisation data.**~~ **Dropped, measured 1 of 16 (entry 66).** It adds
   nothing TLS did not already give, and the failure is worse than the GDPR redaction predicted here:
   **13 of the 16 ccTLDs answer no RDAP at all.** Norway's response names only the *registrar*, which
   says nothing about who owns the domain — do not count that as a hit if this is ever revisited.
3. **TLS certificate organisation.** **Measured 9 of 16 (entry 66) — the one that works, and it is not
   automatic.** OV/EV certificates carry a CA-validated `O=`, and eight of the nine name the authority
   outright (`Auswärtiges Amt`, `Migrationsverket`, `Ministerstvo vnitra`). The ninth, Hungary, names
   `NISZ Zrt.`, a state IT operator rather than an authority — so this yields a **name, not a verdict**,
   and one judgement in nine has to come out *no*. Confirmed: it needs a TLS handshake before trust is
   decided.
4. **Cross-vouching from an already-trusted domain.** For the ten countries that *do* have a marked
   domain, `interno.gov.it` naming `esteri.it` as the foreign ministry is the government vouching for its
   own domain — the existing `appointed_by` idea generalised. **The hole:** governments link to
   contractors, partners and news, so "linked from a trusted domain" is far too weak, and
   `ARCHITECTURE.md` says appointing a provider is human judgement never automated. This is a decision to
   argue, not a patch to apply.

**~~Do the measurement first~~ — done 2026-08-25, entry 66, and it answers the question against the
production goal.** Coverage of the 16: TLS 9, RDAP 1, **neither 7** (BE, CL, DK, GR, IE, NO, RU — all
serving DV certificates that name nobody). Mechanism (1), a government's own published domain list, is
**still unmeasured** and is not generically probeable; it matters only for those seven, so that
follow-up is bounded to seven countries rather than sixteen.

**So: reviewed data is the honest answer, and the review is small.** Automating it away is not
available — seven have nothing machine-readable, and the nine that do still need a person to say
whether the named organisation is the government. What changed is the *shape* of that work: for nine
countries a reviewer reads a CA-validated organisation name and confirms it in seconds, and the
certificate is exactly the independent evidence `CountryAuthorities.reviewed` demands. Seven are
research. Both are one-time.

**Then the two problems the measurement was for:**

- **16 of 51 governments have no governmental marker in their hostname** (19 before entry 65). The
  amendment is an authority domain named in the entry 34 registry — **never a wider regex**, and now
  with the evidence for each row coming from its TLS certificate where one names an organisation. Adding `.de`, `.nl`, `.it` as markers would trust every commercial site in
  those countries, and `belongs_to_destination` cannot narrow it, because for exactly these countries the
  own-TLD test is the only other signal there is. `tests/test_trust_coverage.py` asserts that trap
  directly: it checks a German visa agency is indistinguishable from the ministry on the only half that
  would remain.
- **Schengen is a definition problem, not a bug.** For short-stay visas the decision genuinely lives at
  EU level as much as nationally, and `europa.eu` passes `looks_governmental` but can never pass
  `belongs_to_destination` for any member state. "The destination's own government" is the wrong trust
  unit for a supranational regime. A reviewed supranational-domain list per member is the fix, and it
  amends the rule as stated in entry 19 and in `CLAUDE.md`, so **record a decision rather than
  patching.**

**~~Do first, separately~~ — done 2026-08-25, entry 65.** `gv`, `gub` and `canada.ca` are added, the
registry rebuilt for AT and UY, and coverage went **39 → 41 researchable** with the "row, no confirmable
domain" bucket now empty. Two things that came out of it and are worth knowing before touching this
again: a marker added to `GOVERNMENT_NAMESPACE_LABELS` **must** also be in `trust.SUFFIX_MARKER_LABELS`
or trusting one authority trusts its whole government (a test now asserts it), and **a rule change
reaches nobody until the affected rows are rebuilt** — the registry is committed data.

### 4. Decide the client-side retrieval question — `soon`

**Why:** DECISIONS entry 35 raises it and deliberately does **not** approve it. The traveller's own
browser can open `france-visas.gouv.fr`; a human reading a public page is not this program circumventing
a refusal. Whether the agent may then read what their session received is genuinely near entry 18's
boundary.

**Do:** write the decision either way before writing any code. It needs its own entry because it moves
page content through the client, which needs a trust argument of its own — the domain rule still has to
hold, and content arriving via a browser has not passed the checkpoints that content arriving via
`LiveSourceFetcher` has.

**Careful:** nothing here licenses spoofing or retrying. **Amended 2026-08-19:** it no longer reads
"or pointing this program's renderer at a refusal, entry 18 is unchanged" — entry 41 measured France's
`403` as a Cloudflare *challenge* rather than a refusal and allows the renderer to answer it under our
own user agent, which is item 5. That narrows this item rather than settling it: the client-side
question is about content arriving through *someone else's* session, and none of entry 41 speaks to
that.

### 7. Put it somewhere others can open it aka deployment — `soon`

**Why:** it runs on one laptop with a `.env`. The goal is a URL to share. Keep this simple — a host,
some environment variables, done. No pipelines, no orchestration; CI already runs the checks.

**Its stated blocker has dissolved, 2026-09-02.** This used to be held behind item 2, "because
deploying before item 2 ships a product whose two highest-volume corridors return no checklist" —
Germany now fills all six roles for `IN/GB` (entry 108) and item 2's coverage half is answered above.
What still holds it is item 20 and a number nobody has: **a full cold `POST /visa-plans` has never
been timed** (known problem 5).

**Timing, measured 2026-08-24:** the **corridor phase** is a median of **27.4s** over 40 live runs, all
corpus-routed. Plan extraction sits on top and the two have never been timed together, so the number a
deployment plan actually needs — full cold `POST /visa-plans` — is still unknown. The stale note that
follows is kept for the reasoning, not the figures.

**The timing needs re-measuring before this is planned.** The **34.1s** figure (19.4s corridor + 14.7s
plan, `united-states/IN/IN/tourism`, both caches cleared) was taken before the domain registry and no
longer holds: the corridor phase alone measures **39–45s** now, because `corridor_queries` runs three
searches per trusted domain and the registry gives a country up to five where `destinations.yaml` gave
two. A full cold request has not been re-timed. The lever is the per-domain query count or the domain
cap, **not** the shortlist — that was measured separately and costs nothing (entry 40).

`var/cache/`, `var/corridors/` **and `var/recall/`** are local directories, so a disposable filesystem
makes **every** request cold. That is item 20, which this item should be planned with rather than after.

1. **Precompute and ship corridors.** A warm corridor is 0.0s. Resolve popular ones locally, keep the
   JSON, point `FileCorridorStore` at it. The deployed app answers instantly for anything precomputed
   and refuses politely for the rest.
   **This works from `visa-discover corridor` now** — corrected 2026-09-02. This used to say the
   command could not reach a registry destination; entry 45 fixed that and the note never moved. Ten
   registry destinations were run from it on 2026-09-01 (Austria, Morocco, Mexico, Romania, Saudi
   Arabia, the Philippines, Lithuania, Norway, Thailand, Indonesia), none of which is in
   `destinations.yaml`.
2. **Prefer a host that keeps a disk and a long-running process.** The stores persist and warm requests
   stay warm. If a disposable host is preferred, all three are small classes behind a `load`/`store`
   pair — except `FileRecallLog`, which is `write`/`read` and, being a diagnostic nothing depends on,
   need not survive at all.
3. **Set three secrets:** `OPENAI_API_KEY`, `OPENAI_MODEL`, `SEARCH_API_KEY`.
4. **Keep `render_mode: never`** unless the host can carry Chromium (~150MB plus system libraries).
   Vietnam will refuse without it, which is correct rather than broken.
5. **Put a key or a rate limit on `POST /visa-plans`.** **Done as a key, 2026-09-24 (entry 191):**
   a plan needs an Ofself session, `REQUIRE_SIGN_IN` defaults on, and required-but-unconfigured
   refuses every plan. On the host, set the three sign-in secrets, `PARADIGM_REDIRECT_URI` (and
   register it on the app) and `SESSION_COOKIE_SECURE=true`. There is still no rate limit per user;
   while the app is in incubator mode, who may sign in is the allowlist.

**Ofself provides sign-in, not a host — as far as its documentation shows (2026-09-17, entry 180).**
Paradigm stores the user's data and handles OAuth. The app registers its own redirect URI,
webhook URL and plugin endpoint, all served by the developer, and `paradigm-cli` 0.5.0 has no
deploy command. So this item still needs a host of its own; ask Ofself before choosing one. What
Paradigm does change is step 5: an app in **incubator** mode can be authorised only by an
allowlist, which makes a private deployment possible without a public URL anyone can spend.

**Do not** deploy with `source_mode: fixtures`: it only knows Singapore, and would look like a working
product that answers exactly one corridor.

**Decide how the corridor store treats a corridor that resolves on some runs and not others — before
deploying (entry 151, the owner's call on 2026-09-14).** A refusal is never stored and a resolution
is kept three weeks, so behind a public URL every refused request is retried by the next traveller
until one run resolves, and that run is served to everyone. Keep it, store refusals for a short
window, or require two agreeing runs before storing. Nothing is at risk while nothing is deployed,
which is why it waits here. **The same store freezes what was refused and what was said about it**:
the web app served `united-states/IN/GB` from a corridor stored 16 days earlier that never named the
London embassy a fresh resolution names (entry 152).

**Say it on the page:** this shows official guidance with citations and promises nothing about
correctness or currency. That framing is what makes the product safe to publish, so it belongs in the
interface rather than only in these files.

### 20. Make the stores substrate-swappable and durable — `soon`

**Why:** `var/cache/`, `var/corridors/` and `var/recall/` are local directories, so **a disposable host
makes every request cold** — up to fifteen searches, twenty-five fetches, two model calls, though
since entry 191 only for a signed-in user. Item 7 already notes this; entry 44 makes it structural,
because a corpus that does not survive a restart is not a corpus. Both existing stores are small classes with `load`/`store`,
so the seam is already there.

**Do:** put the corpus, the source snapshots and the corridor resolutions behind their existing
protocols and add a networked implementation. Add the refresh job at the same time — a weekly conditional
`GET` over every stored URL, which is cheap because most answer `304`, and which is where a `404` or an
off-domain redirect is caught and the country flagged.

**Three things that are right today and are easy to lose in a migration:**

1. **A row records when the evidence was retrieved, never when the row was written.** `_serve_stale`
   keeps the original `fetched_at`; a `304` moves it, because a validator match proves currency. A schema
   that collapses `retrieved_at` and `row_written_at` starts lying about how current its guidance is
   (entry 4).
2. **The stale ceiling still refuses.** Past `source_maximum_stale_hours` a stored page is refused rather
   than served, whatever the store.
3. **A hash change marks a source and never auto-swaps a role-bearing one** — item 14.

**Careful:** `content_hash` is already computed over the *cleaned* text, so drift detection is less noisy
than item 14 assumes. Do not add a second hash over raw bytes; it would fire on every nav timestamp.

### 55. Take the traveller from Ofself's shared identity, through one adapter — `soon`

**Why — the owner, 2026-09-15.** This project is to become one app in **Ofself**, a platform whose
apps all share one identity data structure per person. Each app reads it, and each app updates it
as the person uses that app. Ofself will give this project **a subset of that structure, through a
schema for the details this project needs**. "Hosted" here means a member of that ecosystem; it
says nothing yet about where the server runs, which is still item 7.

Today the traveller is typed into a form on every request. Inside Ofself it should come from the
shared identity, and the field names and format are Ofself's to define, not ours. The aim is that
integrating it means **one new module mapping their schema onto ours**, not edits spread across the
API, extraction and the page.

**How a traveller is wired today, checked against the code 2026-09-15.** Most of the seam already
exists, which is why this is sized small:
- **The edge is `TravellerRequest`** (`api/schemas.py`). It turns whatever a person wrote into ISO
  codes and refuses a country with no reference data (entry 20), then `to_profile()` builds the
  domain model.
- **`TravellerProfile`** (`domain/models.py`) is what the rest of the program depends on: passport
  nationality, passport type, country of residence, purpose, and three optional residence details.
  It is imported by `api/routes.py` and by `research/` — `service.py`, `interfaces.py`,
  `openai_extraction.py`, `fixtures.py`.
- **Discovery never sees the profile.** `corridor_for` (`api/routes.py`) reduces it to a `Corridor`
  of destination, passport, country applied from and purpose. That is all search, the corpus,
  selection and adjudication read, and corridor store keys hold codes only.
- **Three places assumed the one input path; one is now a seam.** `create_visa_plan` asks an
  injected `TravellerSource` (`api/traveller.py`) instead of reading `request.traveller`, and only
  the request-body source falls back to the default traveller. Still assuming the form: the page
  pre-selects from `DEFAULT_TRAVELLER_PROFILE` (`api/routes.py`), and `app.js` posts the form's fields.

**Do:**
1. ~~**Make where the profile comes from an injected dependency.**~~ **Done 2026-09-17.**
   `TravellerSource` has one method, `traveller_for(request)`, and `get_traveller_source` in
   `api/dependencies.py` returns `RequestBodyTravellerSource`. The default-traveller fallback moved
   into that source, out of the route, so an Ofself source cannot inherit it.
2. ~~**Move `normalise_country` out of `api/schemas.py`.**~~ **Done 2026-09-17**, to
   `api/countries.py`. It did not accept an **alpha-3** code — `IND`, `GBR`, `NGA` and `PHL` were
   refused, and `USA` passed only as a synonym — and step 3 added them.
3. **Write the adapter as one module.** **Built 2026-09-17, and run against Paradigm the same day.**
   - **`api/ofself.py`:** `OfselfIdentity.passport_nationalities(user_id)` reads
     `GET /api/v1/nodes?schema_id=work-authorization` with `X-API-Key` and `X-User-ID`, through the
     project's own `httpx` client and `transport=` seam, and returns `PassportNationalities`: every
     citizenship as alpha-2 in recorded order (the traveller picks one, rule 3), what named no known
     country (never guessed), and a count of encrypted values (never read). Empty means ask (rule 4).
   - **Errors:** the five authorisation codes and the legacy one raise `OfselfAuthorizationLost`,
     from either documented envelope; a refused API key, any other refusal, a transport failure or a
     malformed body raise `OfselfUnavailable`, so a broken answer is never mistaken for an empty one.
   - **Alpha-3:** `countries.yaml` gained `alpha3` for all 198 countries, from Wikidata's P297/P298 —
     exactly one each, all distinct, none equal to another country's name or synonym — and
     `normalise_country` accepts it. A test checks all 198.
   - **Settings:** `PARADIGM_API_KEY`, `PARADIGM_BASE_URL`, `PARADIGM_TIMEOUT_SECONDS`.
   - **How the page uses it — the owner, 2026-09-17:** one citizenship fills the passport field in,
     editable and with no confirmation step; none leaves it empty, as today; **two or more are
     offered with none chosen**, so the traveller taps the one this trip is on. A dual national's
     visa answer depends on the passport, and the record cannot say which one a trip uses.
   - **Run live, 2026-09-17,** against sandbox user `66a3241b-5130-4ca9-9ce7-baaa69f84745`
     (`paradigm app test-users list`), given a `work-authorization` record of `["IND", "GB"]` plus
     `notes`, `source` and `work_authorized_in`. The adapter returned `IN, GB`; a user who never
     authorised the app raised `OfselfAuthorizationLost` with `EP_NOT_FOUND`; a made-up key raised
     `OfselfUnavailable` naming `INVALID_API_KEY`.
   - **Two ways the live API differs from the developer guide.** `GET /nodes` answers `"total":
     null`, never a count, so the adapter pages until a page comes back short; the guide's version
     would have stopped after one page. `POST /nodes` returns the node at the top level, not under
     `"node"`.
   - **Unconfirmed: whether `fields: [citizenships]` narrows a real grant.** The sandbox user also got
     `notes`, `source` and `work_authorized_in` back, but a sandbox user has full access, so that
     proves nothing about a real authorisation. It needs one real OAuth grant to check. The adapter
     reads only `citizenships` and keeps nothing, either way.
   - **Not done:** nothing calls it yet — that needs sign-in, to know whose identity to read.
4. **Sign in with Ofself.** **Built 2026-09-17, and one real sign-in completed the same day.** `api/signin.py`.
   - **The flow was read from Ofself's authorize page itself,** since the guide shows it only through
     private SDK helpers. `/oauth/login` sends the browser to
     `app.ofself.ai/authorize?client_id=…&redirect_uri=…`. After approval the page redirects with
     `code=success` (a literal), `client_id`, `user_id`, `username` and a single-use `sid_code`.
   - **Only `POST /api/v1/auth/session/exchange` names the user**, called with the app's key and
     `{"code": sid_code}`; found by probing with a dummy code, which answered `INVALID_CODE`.
     `/oauth/callback` never believes the query's `user_id`: it refuses a missing `sid_code`, another
     `client_id`, anything but `code=success`, a browser that never started sign-in, and a `user_id`
     that disagrees with the exchange.
   - **The session** is one signed cookie holding the Ofself user id and nothing else — HMAC-SHA256
     with `SESSION_SECRET`, a purpose stamp so the pending cookie cannot pass as a session, and a
     12-hour expiry. No new dependency. `GET /oauth/session` says who is signed in; `POST
     /oauth/logout` forgets it here and leaves the grant on Ofself alone.
   - **Off until configured:** `PARADIGM_CLIENT_ID`, `PARADIGM_API_KEY` and `SESSION_SECRET`. But
     since entry 191 a plan **requires** it unless `REQUIRE_SIGN_IN=false`, so unconfigured means
     no plans rather than anonymous plans.
     `.claude/launch.json` has `visa-research-agent-signin` on port 8000, the registered redirect.
   - **The real sign-in, 2026-09-17.** The owner authorised the app under Full Access and was signed
     in as `43b82f83-66c4-449b-a9ce-eb1f690c433b`. Two earlier callbacks, from a browser that had not
     visited `/oauth/login`, were refused as they should be. The exchange answered in one of the two
     accepted shapes with no warning, but which one was not recorded; tightening to it is optional,
     since both are checked as UUIDs.
   - **The real grant narrows as asked.** `/my-permissions` for that user reports effective access
     of exactly `nodes:read` on `work-authorization`, field `citizenships`, and reading every node
     returns none — the owner's `profile` is out of reach. **Whether a read returns only that field
     is still unseen:** the owner's account holds no `work-authorization` record. The grant **expires
     2026-10-17**, thirty days on, after which the app gets `EP_EXPIRED` (step 5).
   - **The page uses it, 2026-09-18.** Signed out, the header offers "Sign in with Ofself" and the
     form keeps its default traveller; with sign-in unconfigured, nothing mentions Ofself. Signed
     in, the passport and applying-from fields start empty and required — never the default
     (rule 4) — and `GET /oauth/passport` fills the passport in: one citizenship is selected with a
     note that it came from Ofself, several are offered as buttons with none chosen, none leaves it
     to the traveller, and unrecognised or encrypted values are named. A lost grant (`403`,
     `reconnect: true`) shows a "Reconnect with Ofself" link. Seen in the browser for the sandbox
     user's `IND, GB` at desktop and phone width; the phone layout, two columns that cut country
     names to a few letters even before this, is now one. **Not yet seen on the owner's own account**,
     which holds no `work-authorization` record. `POST /visa-plans` still takes the traveller from
     the body as confirmed on the page, and does not check the grant — that is step 5.
   - **`sid_code` was in the access log.** Uvicorn logs the whole callback address, and a callback
     refused before its exchange leaves its code unredeemed. `RedactSessionCodes` now replaces it
     with `[redacted]` on uvicorn's access logger; confirmed in the live log.
   - **Cannot be closed from this side:** the authorize page echoes no `state`, so a callback cannot
     be tied to the login that began it. The pending cookie refuses a browser that never started.
5. **Check authorisation twice per request:** before reading the node, and again before returning a
   plan, because a plan takes about 55s and access can be withdrawn while it is written. Handle
   `EP_NOT_FOUND`, `EP_REVOKED`, `EP_PAUSED`, `EP_EXPIRED` and the legacy `NO_AUTHORIZATION` — the
   guide names both vocabularies — and none of them may fall back to `DEFAULT_TRAVELLER_PROFILE`.
   **Ofself's review of sign-in, 2026-09-24, on what happens when a grant is revoked:**
   - **A lost grant now ends the session — fixed the same day.** `/oauth/traveller` answered `403`
     with `reconnect` and left the session cookie in place, so the browser still looked signed in.
     It now deletes the cookie with the same `403`, and a test checks the browser is signed out.
   - **Revoking doesn't log anyone out, because the session is ours.** Sign-in exchanges the
     `sid_code` for a user id and keeps its own 12-hour cookie, discarding the session id Ofself
     returns. Holding that id would let a revocation end the session here; what the exchange
     returns has still not been recorded (item 55, step 4), so read it on the next real sign-in.
   - **Ofself fires `session.revoked` to a webhook, and none is registered.** Receiving it needs a
     public address, so it waits on item 7's host; `localhost` cannot receive it.
6. **Stop keeping model drafts past their reuse window.** `FilePlanStore` reuses a draft for 24 hours
   (entry 178) and never deletes it, and a draft is written from the whole `TravellerProfile`, so a
   city or a residence status can sit on disk indefinitely. Harmless for one developer; not for
   real users.

**Settled with the owner on 2026-09-17 — entry 180, which has the reasoning.** The Ofself design lives
in [CRUX.md](CRUX.md), which `paradigm crux validate` passes; this item is the work and does not
restate it.
- **The platform is Paradigm**, Ofself's developer platform. The app authenticates with `X-API-Key`
  plus the `X-User-ID` that OAuth returns. Its data request (DLR) is a YAML block in `CRUX.md` §11.
- **The DLR is `nodes:read` on `work-authorization` and nothing else.** Its `citizenships` stands in
  for passport nationality until the owner's planned visa schema exists. The registry holds no
  schema for a passport, a residence or a residence permit.
- **Asked on the page, not requested:** country of residence (`place` would bring every address the
  person holds), destination and purpose (`trip` cannot be narrowed to future trips), residence
  status and permit expiry (no schema). The form does not ask the last two today either.
- **Nothing is written back, and `fact` nodes are never read as evidence.**

**Six travel schemas appeared in the registry on 2026-09-21, and they change what this item can
ask for.** All public, all v1: `travel-plan`, `travel-document`, `travel-requirement`,
`travel-stay`, `travel-obligation`, `travel-zone`. Evaluated the day they appeared. **The owner then decided to request
ahead (entry 181), and `CRUX.md`'s DLR now asks for fields from five of them plus `place`**; it
passes `crux validate` with six schemas resolved. **It went live the same day** — see the bullet
below. Publishing was the owner's, because `crux sync` refuses a non-interactive shell:
`paradigm crux sync`, then `paradigm commit`, then `paradigm dlr preview` to see the consent card.
`paradigm commit` then asks `--ep-action cancel` (revoke every existing grant) or `continue` (keep
them; the new fields fail until each user re-authorises) — `continue` was recommended. Then the
owner re-authorises by signing in again, and runs `paradigm crux push`, which
marks the review stale; a fresh `crux review` is billable (feedback 5.7).

**Built 2026-09-21, the owner: "use these schemas now."** `OfselfIdentity.traveller_defaults` in
`api/ofself.py` reads `travel-document`, `travel-plan` and — only when a plan needs a candidate
resolved — `place`, beside `citizenships`; `GET /oauth/traveller` replaces `/oauth/passport`; and
the signed-in form starts from it. Passports come with their expiry and whether it was read off the
passport or typed in; a passport whose code is not ordinary is named and not offered; another
person's document is counted and not offered; a residence permit fills "applying from"; an open
plan's candidates are offered as destinations, filling purpose where the plan's is one this app
researches. Twelve new offline tests. Checked in the browser against a fake Ofself serving invented
records, at desktop and phone width — **not against live data**, which needs the DLR published
first, and then records in a real account. **Nothing a plan says changed**: `TravellerProfile`, the
request and the model packet are untouched, and entry 181 says why the rest is held back.
- **The DLR is live and the owner has re-authorised, 2026-09-21.** `paradigm commit --ep-action
  continue` published it (spec version 5), and after the owner signed in again `effective_access`
  held all six schemas with exactly the requested fields — no document number, scans or names. The
  grant's expiry did not move: still **2026-10-17** (feedback 9.8).
- **Next:** put real `travel-document` and `travel-plan` records in the owner's account — it holds
  none in any of the six schemas — and see the form fill from them. That is the first time the live
  node shapes are seen.
- **One statement above the form, the owner's call the same day.** Whether Ofself filled anything,
  nothing, or could not be reached is said once above the form rather than in each field; a
  field's own note is only for what that field was filled with, or what it withheld.
- **Destination and purpose now start empty for a signed-in traveller**, as passport and residence
  already did — the first entry in each list had been passing as a choice.

The evaluation below is what the field list was built from.
- **Read `travel-document`, narrowed to fields — the one clear win.** It answers the three gaps
  entry 180 recorded as having no schema: the passport as a document with `document_code`
  (`P`/`PD`/`PS`), so rule 2's refusal of a non-ordinary passport becomes possible instead of
  hard-coding `ordinary`; `expires_at` and `issued_at`, without which passport-validity and the
  Schengen ten-year condition cannot be checked at all; and `kind: residence_permit` with `grants`,
  which is residence status and permit expiry — decisive for Brazil and China, and named as missing
  in CRUX §11. Its `field_provenance` rule is this project's own doctrine in Ofself's words, and it
  agrees with rule 3: what is read is a default the traveller confirms.
  **Ask for a narrow field list and never the whole node.** `number` and `photo_ids` are a passport
  number and scans; `surname`, `given_names`, `date_of_birth`, `place_of_birth` and `sex` decide no
  guidance. Rule 1 is why this matters: `build_research_packet` sends the profile whole to OpenAI.
- **`travel-plan` answers entry 180's objection to `trip`.** It is *"a journey someone is
  considering but has not committed to"*, so reading it does not drag in every past trip the way
  `trip` would. It also carries `travellers` and several `candidates`, which this app has no shape
  for — one corridor is one traveller and one destination. Worth reading as a default to confirm,
  not as a corridor.
- **Never read `travel-requirement` as evidence.** It is the decision table entry 44 refused to
  build, held in a store every app can write. A row's `source_url` has passed none of entry 2's
  domain rules, and its `read_at` can be older than `source_maximum_stale_hours` allows this app to
  serve. The same argument as `fact` nodes, and it needs its own line in CRUX §13.
- **Writing is where the platform pulls hardest, and the answer is still no.** `travel-requirement`
  is the graph write that would lift readiness past 2 (feedback 5.6), and its `outcome` field is
  required — so any row this app wrote would carry a model-derived verdict, which is exactly entry
  44's refusal. `travel-obligation` is the one write that would not: it records what *happened*, and
  states outright that *"the eligibility verdict is derived and never stored."* But this app books
  and submits nothing, so it has no history to record. **Either way, a decision entry first.**
- **`travel-stay` is a capability this app does not have** — entry and exit legs, for rolling
  allowances like 90 days in any 180. If it is ever read, the schema's own caveat is binding and is
  entry 6 restated: a total built from self-declared stays may raise a question and may never state
  days remaining.
- **`travel-zone` is not requested**, because a roster in the graph is another app's assertion.
  *Corrected the same day:* this said zone membership was "committed reference data here
  already". It is not — only the few configured destinations carry `route_type: schengen_member`.
  Planned workflow D needs a roster from somewhere, and that is its own question (entry 181).

**Open, for the owner to ask Ofself:**
- **Does any Ofself app record a trip before it happens?** If one does, `trip` is worth adding before
  launch. Widening a DLR later costs every existing user a re-authorisation, which costs nothing
  while there are no users.
- **Does Ofself host apps?** Nothing in the guide or `paradigm-cli` 0.5.0 says so. See item 7.

**Registered on 2026-09-17** as "Visa Research Desk" (app id `ed21d312-1c8a-487e-9de3-38ed61abb013`),
in incubator mode, visible to selected users only, with `http://localhost:8000/oauth/callback` as its
one redirect URI — Paradigm accepted `http://localhost`. The API key is in `.paradigm/secrets.toml`;
it was moved into `.env` as `PARADIGM_API_KEY`, where every other secret lives, on 2026-09-17.
- **Registering needs a file only `paradigm init` writes.** `app push` registers from
  `.paradigm/pending.toml`, and `init` would also have installed Paradigm's SDK into `.venv` and
  overwritten `CRUX.md`, so the file was written by hand with the same three keys.
- **The DLR is published separately, and only by the owner.** `app push` registers with an empty
  DLR — it does not read `CRUX.md` — and `crux sync` refuses a non-interactive shell so that the
  developer, not an assistant, confirms what users will consent to. Then `paradigm commit` applies
  the staged change and `paradigm dlr preview` shows the consent card.
- **The CRUX is published as of 2026-09-21**, `spec_version` 3, with the owner's go-ahead. The
  record stores `format: md`, all sixteen sections (10,027 characters) and the DLR block; the DLR
  itself is unchanged. `paradigm crux review` — Paradigm's own model reading the CRUX — then
  **passed all five of its criteria**, taking the app to **13 of 16 checks**: every permission
  justified by a workflow, the inference and its confirmer named, the schema choices justified, the
  identity thesis a real claim, and the workflows complete jobs. The three that fail are all
  traffic: two are usage counts a private incubator app cannot have, and the third is the write-back
  below. **Readiness is 2 of 5, "Wired", and reaching 3 requires having written to the graph** — which
  entry 44 and this item's sixth rule forbid. That is a ceiling to accept deliberately rather than
  design around; it is feedback 5.6, and worth raising with Ofself alongside the questions below.
  The paragraph that follows is kept for how the state was found.
- **The CRUX document was unpublished until then, found the same day.** `crux sync` publishes only
  the DLR; `crux push` stores the design doc on the registration. Only the first was ever run, so
  `paradigm app show` reports `crux: null`, the portal says the app has no CRUX, and
  `paradigm readiness` refuses to score it — it reads the CRUX, and calls the feature table the only
  evidence for what the platform cannot observe. The file is fine: `crux check` reports all sixteen
  sections filled and `crux validate` passes, resolving the one schema. **To publish:**
  `paradigm crux push -m "<summary>"`, which bumps `spec_version` to 3. **No `--app-id` is needed**
  — corrected 2026-09-21 by reading `appref.py`: the binding is `app_id` in
  `.paradigm/secrets.toml`, written at registration, and `pending.toml` was only ever the input to
  `app push`. **The markdown path is not the loss it sounds:** `crux push` prefers a JSON answers
  block in a `CRUX.html`, but with only a `CRUX.md` it sends `{format: "md", sections: {…}, dlr:
  {…}}`, every filled section's full text included, so the *"best-effort extraction"* drops no
  prose. Nothing in `paradigm-cli` 0.5.0 writes a `CRUX.html`, so there was never one to have.
  Whether a spec bump pauses the owner's live grant is untested, though it changes no DLR and the
  only grants are the owner's and the sandbox user's.

**What the platform itself got wrong or left unsaid is in [OFSELF_FEEDBACK.md](OFSELF_FEEDBACK.md)**, for
Ofself's developers; the traps below are the ones that shape this item's work.

**Two more traps in `paradigm-cli` 0.5.0.**
- **Its own materials disagree about where the DLR goes.** `crux init` scaffolds a sixteen-section
  `CRUX.md` that says it has no DLR section, while `crux validate` fails without a `dlr.requests`
  block and the bundled skill says to use §9.
- **It writes secrets to `.paradigm/secrets.toml`,** which `.gitignore` now excludes. The skill it
  writes to `.claude/skills/` and the `API_REFERENCE.md` that `paradigm init` adds are generic
  Paradigm material and are not committed.

**Six things an adapter must not lose, each easy to lose by mapping fields one to one:**
1. **Read only the fields that select guidance, and drop anything else that arrives.** *Changed
   2026-09-21 by entry 181:* the DLR now **asks** ahead for fields a future plan could use, and this
   rule moved from the request to the adapter. The shared identity will hold a name, a date of
   birth, a passport number, an address. `build_research_packet`
   (`research/openai_extraction.py:108`) sends `traveller_profile.model_dump()` to OpenAI **whole**,
   so any field added to `TravellerProfile` goes to a third party on every plan. A field granted for
   a planned workflow is not read until that workflow is built; the adapter drops what the plan does
   not use, and `TravellerProfile` is not widened to hold it. Keep `StrictModel`'s
   `extra="forbid"`, which stops a stray field at construction. **What is never requested at all**
   is entry 181's first bound: anything only an application form could use.
2. **A passport type the program cannot research is refused, never coerced.** `to_profile()`
   hard-codes `passport_type="ordinary"`, which is safe only because the form has no type field. A
   shared identity recording a diplomatic or official passport must be refused at the adapter, as
   `test_a_diplomatic_passport_cannot_be_requested` refuses it at the schema, or it is answered with
   the ordinary-passport rules (entry 20).
3. **A traveller with more than one passport chooses which; the adapter never picks.** Dual
   nationality is one of the two questions entry 59 found a corridor does not carry, and a silent
   pick changes the answer. Residence is the same, and more so in a shared structure: another Ofself
   app may have written it from how the person used that app, which is not the person telling this
   one where they apply from. **Show what Ofself holds as a default the traveller confirms**, never
   as the corridor.
4. **A traveller whose identity lacks a deciding field is asked, never given the default.**
   `create_visa_plan` falls back to `DEFAULT_TRAVELLER_PROFILE`, an Indian passport resident in
   Edinburgh, when no traveller is described. That suits the anonymous form. Inside Ofself it would
   answer someone else's corridor for them without saying so.
5. **After the adapter a country is an ISO alpha-2 code**, whether Ofself stores alpha-3, a name or
   its own enum. It is normalised once, at the edge.
6. **Nothing is written back to the shared identity without a decision entry first.** Ofself apps
   update the structure as it is used, so this one will be expected to. What the pipeline
   *concludes* — a visa decision, a checklist, a route — must never go there: a plan is a rendering,
   never a stored fact (entry 44), and a wrong "needs a visa" sitting in a store every other app
   reads, with no citation and no age, is the alarming-wrong-answer class entry 6 forbids. The most
   that could be argued for is what the traveller *stated* here, such as which passport they chose,
   and that argument has not been made.

**Plan it with item 7.** Ofself's login now answers item 7's fifth step: `POST /visa-plans` needs a
signed-in session (entry 191).

### 59. Guard the 272K-token price threshold — `soon`, **split from item 19 on 2026-09-15 (entry 173)**

**Why it matters.** OpenAI bills a request with more than 272K input tokens at 2× input and 1.5×
output for the *whole* request — the `gpt-5.6-terra` model page, read 2026-09-15 (entry 167).
- **Canada's selection packet is already ~92K tokens** after entry 170, and was 149K before it.
- **Nothing caps a selection packet as a whole.** `DEFAULT_SELECTION_CHARACTERS` bounds the excerpt
  text, but every candidate still brings its address and labels, and each excerpt keeps at least 200
  characters. A pool that grows — entry 158's admission, write-back, a rebuild — grows the packet.
- **By arithmetic, the other calls stay below it.** The roles packet is at most 20 pages of 20,000
  characters on the model path, roughly 100K tokens, but up to 35 pages on the heuristic path. The plan
  packet is capped at 80,000 characters (`maximum_model_input_characters`).

**Open — measure before deciding.**
- **How close any country comes.** Rebuild each corpus's largest pool offline with `contention_for`
  and count tokens, as entry 164 did, allowing for search's extra candidates.
- **What a guard should do when a packet would cross.** Shorter excerpts are what `excerpt_budget`
  already does as a pool widens. A hard cap on candidates is what entries 123 and 158 argue against,
  because the pool is the recall gate. Or refuse with a note. Silently dropping candidates is not an
  option (`selection.py`'s module docstring).
- **Whether to warn near the threshold.** `var/usage/` already records every call's `input_tokens`.

### 58. What is left of model-call cost and research latency — `soon`, **split from item 19 on 2026-09-15 (entry 173)**

**The owner's target, 2026-09-23 (entry 182): about 30 seconds, with information on screen while
it runs.** Fast mode on every call projects to ~39s, so the rest has to come from the research
latency below, or be made to feel shorter through item 57.

**Where it stands.** A fresh corridor that resolves costs **$0.251 in model calls**, plus about $0.054 of
search, and takes about **55s**: ~25s of research and ~29s of writing the plan (entry 171). The plan
call's wait is item 57; the 272K price threshold is item 59. The instrumentation is on: every
model call goes to `var/usage/model-calls-YYYY-MM-DD.jsonl`, and every stage's seconds to the recall
log's `phase_seconds`.

**Cost, biggest first — none of it decided.**
- ~~**Shrink what selection reads.**~~ **Done 2026-09-24 (entry 195):** the selector sees the fusion
  top 120 plus 40 pages with no stored text, at about 42% less selection input.
- **A cheaper model for selection only.** Selection is ~63% of the model bill, and `gpt-5.6-luna` is
  listed at a tenth of `gpt-5.6-terra`'s price a token, which could take a corridor from about $0.25 to
  about $0.11. It changes what picks the pages, so it needs grading and the owner's decision. Entry
  170's selection-only A/B is the method, about $1.70 for ten corridors. A failed selection falls
  back to the heuristic ranking, which is allowed: entry 31 governs the decider, not the selector.
  Role adjudication and the plan call stay on the stronger model.
- **Trim the roles call's packet**, as entry 170 trimmed selection's. Its JSON is still indented.
  Roles is ~19% of the bill, so the saving is a few percent, and it changes what the adjudicator
  reads, so it is graded.
- **A refusal is not stored** (entry 151), so each repeat of a refusing corridor pays ~29s and
  $0.11–0.19 again. Storing one briefly is a freshness question as much as a cost one.
- **Entry 146's reusable country-stable packet waits for traffic.** OpenAI's cache lives 30 minutes,
  a write costs 1.25×, and pools overlap 79–99% across travellers (entry 164).

**Fast mode was measured on every call (entry 177)** — plan −43%, selection −23%, roles −13%, at
twice the price. Where it goes is item 60.

**Research latency, ~25s — none of it decided.** Means over five fresh corridors (entry 171): roles
8.2s, selection 6.6s, search 3.5s, the crawl stage 3.2s, fetch 2.7s. Fetch was measured on a warm page
cache, and Canada still took 12s.
- **Overlap search with the fetches** rather than blocking on it before anything else. Proposed under
  item 19 and never built.
- **Find out what `fetch` is made of** — renders, serial waiting, one failing host — before touching
  it. Entry 139 asked that of the crawl fetcher; nobody has asked it of `LiveSourceFetcher`.
- **Grade any latency change on several runs, and price it in dollars too.** Model-call seconds swing
  40% between identical runs (entry 144), and latency and cost pull opposite ways (entry 145).

**Carried over from item 19, not about cost.**
- **Should `visa-discover corridor` write back to the corpus?** Only the web path does (entry 173).
  It is not free: `--runs` withholds pins so one run cannot contaminate the next, and write-back
  mutates the store in exactly that way.
- **Eviction is designed and unbuilt**, so the corpus only grows.
- **A dead pin must never silently degrade.** If a pinned page 404s and its role cannot be refilled,
  the corridor refuses, as it would have without the pin.

**Do not re-propose** conditional search (entries 159 and 160) or refusing on a miss (entry 173).

---

## Blocked

### 65. Test GPT-6 Sol against GPT-5.6 Terra on answers, time and cost — `blocked` on Ofself deploying GPT-6, or on OpenAI credit, **added 2026-09-23; blocked 2026-09-25**

**On the Personas route (entry 188) this tests what Ofself's account offers, and needs no OpenAI
credit.** The model is set on each call's agent (`llm_model`), and every reply's model is checked
against `OPENAI_MODEL`, so a model the account lacks fails loudly rather than being swapped. **Step 0
is one probe: does Personas serve `gpt-6-sol` at all?** Its price there is Ofself's, not the list
price below, and Ofself reports no cached tokens, so the cost column compares token counts only.

**Step 0 result, 2026-09-25: Personas does not serve it.** A one-call probe on a separate agent
(`visa-probe-<model>`, so the production agents' stored model was untouched) answered on
`gpt-5.6-terra` in 2.5s and failed for `gpt-6-sol` and `gpt-6-luna` with Azure's
`DeploymentNotFound` — Ofself serves models through Azure deployments, and has none for GPT-6
(OFSELF_FEEDBACK 8.21). **So this item waits on Ofself deploying GPT-6 Sol, or on OpenAI credit for
the direct route.** Ask Ofself which models the account serves. Until then, the rebuild sequence
goes on with Terra, and item 65 is re-run before step 3's baseline only if Sol arrives first.

**It must also settle entry 188's open Japan question.** One of six Personas runs answered Japan
`IN/GB` "visa required" from MOFA's list of who does *not* need a visa, the inference rule 8e and
entry 174 rule out. Run a dozen Japan calls on the same packet for each model and count it.

**Why it matters.** OpenAI released GPT-6 Sol on 2026-09-22 at Terra's input price and a lower
output price: $2.00 input, $0.20 cached, $2.50 cache write and **$10.00 output** per million tokens,
against Terra's $12.00. It is the tier above Terra, and the first published scores put it ahead:
- **Artificial Analysis:** 48 against Terra's 34.
- **BenchLM overall:** 82.2 against 72.8.
- **Individual tests are mixed**, and none of them resembles this project's task. It is ahead on
  OSWorld 2.0 (60.5% against 50.2%) and behind on DeepSWE (68.8% against 69.6%) and HealthBench
  Hard (30.1% against 32.7%).

Those figures do not answer the question for this project, for three reasons:
- **Sol's 48 was scored at `max` reasoning effort, and every call here runs at `low`.** At `max`,
  Artificial Analysis measured about 107s to the first token.
- **Nothing is published yet for Sol on the qualities this project depends on:** instruction
  following, long-document reading and hallucination.
- **A model change has broken a decision before.** In entry 177, `gpt-5.6-luna` wrote Japan a
  "no visa required" plan.

**What it could buy.** If it is at least as good, it would be a quality upgrade at slightly lower
cost. Repricing 2026-09-15's logged calls puts the saving at about **2–3% a fresh corridor**
(~$0.251 → ~$0.245). The plan call gets about 11% cheaper, and selection and roles barely move
because they are almost all input. How Sol's speed compares to Terra's is unknown. With Fast mode out
of reach on Personas (item 60), this is the only model-side lever left for speed as well as quality.

**How to run it — all three calls are one setting.** `OPENAI_MODEL` in `.env` drives selection,
roles, blocked-page judgement and the plan call alike (`config/settings.py`), and
`openai_reasoning_effort` stays `low` in both arms.
1. **First, record the model name in each usage record.** `ModelCallRecord`
   (`research/model_usage.py`) holds no model today, so a Sol call and a Terra call in
   `var/usage/` cannot be told apart or priced separately. This is a small code change with a
   test.
2. **Clear `var/cache/`, `var/corridors/` and `var/plans/` before each arm, or before neither.**
   Otherwise one arm runs on reused corridors and drafts (entries 136 and 178).
3. **Run several times per arm.** Model seconds swing about 40% between identical runs (entry 144),
   and one run per arm cannot separate the models. Three per corridor per arm is the least.
4. **Corridors:**
   - **Japan `IN/GB` and Singapore `PH/PH`.** Any change to the plan call must pass these (entry 174),
     and rule 8e's "no visa" bounds live only in the prompt.
   - **Entry 170's ten graded corridors**, for selection, whose method is the selection A/B.
5. **Record, per arm:**
   - **Answers:** each corridor's visa decision (required / not required / open), whether it
     resolved or refused, and roles filled. Put any decision that differs from Terra's in front of
     the owner.
   - **Time:** `phase_seconds` and each call's seconds from the recall log, plus the whole request.
   - **Cost:** tokens per call priced at each model's rates, including cache writes (entry 167). Sol
     may reason more or less than Terra at `low`, so its output tokens must be measured, not assumed.

**The bound on grading it.** Correctness is the owner's to judge (entry 68). This item compares what
the two models *answer* and flags every disagreement; it does not build a grader. **Any
disagreement on a visa decision blocks the switch** until the owner has read both plans. Where
Terra was open and Sol commits, that counts as a disagreement, and it is the worst direction.

**Cost of the test itself:** search only on the Personas route, about $0.05 a corridor.

**If Sol wins:** changing `OPENAI_MODEL` is one line of `.env`, and the Personas agents are
re-created with it. Record the result as a decision
entry and update the headline cost and time figures in CLAUDE.md, the handoff and TODO, which all
quote Terra's.

### 67. Test ranking by embeddings of stored page text — `blocked` on OpenAI credit, **added 2026-09-23 (entries 183, 184)**

**Blocked, checked 2026-09-25.** It needs an embeddings model, and the Personas route (entry 188)
offers chat calls only, so it waits on an OpenAI top-up or another embeddings source the owner
approves.

**Why it matters.** Entry 183 found that what separates the model selector from the heuristics is
**judgement, not information**:
- **Same inputs, different results.** Both see stored text where it exists and a ~29-character link
  where it does not, and the model finds 83% of answers against the heuristics' 53–60%.
- **Even on pages read in full, the keyword decider was confidently wrong on 34%.**

The keyword scorer matches listed phrases. Embeddings match meaning, so they may rank better:
- other wordings, such as "supporting documents", "what to bring" and other languages;
- a page that *is* a checklist over one that mentions one.

**What embeddings cannot do.**
- **They cannot help a page with no stored text.** Embedding a 29-character link adds nothing. That
  gap is closed by reading more pages at build time (entry 184).
- **They may not separate near-identical pages for different travellers**, such as a London and a
  New Delhi checklist. That is the part expected to stay the model's.

**Build — offline, once, then per rebuild.**
1. **Embed every stored body** in `var/pagetext/` (~43,000 when last counted, more since the 2026-09-15
   rebuild) with `text-embedding-3-small` or `-large`. At $0.02/M tokens for small, that is about
   $1 once. Entry 184 allows more if a larger model ranks better. Chunk long pages rather than
   truncating them, keeping the best-matching chunk's score per page.
2. **Store the vectors beside the text index.** They are ranking input and **never evidence**, as the
   text itself is (entries 78 and 83), and nothing may read a sentence back out of them. Vectors of
   stored text are a derivative of stored text and carry its age.

**Measure — offline, with the harness entry 183 used.**
- **Per corridor and role, embed a short query** such as "document checklist for a tourist visa,
  Indian passport, applying in the United Kingdom". The query embeddings are the only per-request
  cost, and they are tiny. Pages without text fall back to their link rank, as fusion does.
- **Grade it two ways against `oracle/selection_oracle.yaml`:**
  - **As a selector** at the model's own per-corridor page count. The bar is the model's **83%**, and
    anything short of it is entry 86's finding again.
  - **As the selector's cut** (entry 195). Does it rank the pages the model picks above
    `fusion_order`'s top 120, at a smaller cut? `var/selection-replay-2026-09-24/` grades a new
    ordering on fixed pools, five runs each; also try it fused with link rank.
- **Check it on the 81 non-oracle model runs**, by the model's picks kept, as entry 183 did.
- **Record the time per request** of the query embeddings and the similarity ranking. It should be
  well under a second. Anything more is a finding.

**Then decide.**
- **As a filter,** it replaces `fusion_order` in `shown_to_selector` if it beats 80.0 of 90 there.
- **As a selector,** it would have to reach the model's recall before a live test is worth running.
- **Either way it is recall change**, graded live over several runs (entry 144) before shipping.

### 60. Decide where Fast mode goes — `blocked`, **added 2026-09-16 (entry 177); blocked 2026-09-24 on Ofself adding a tier setting**

**Decide it after item 65.** Fast mode was measured on Terra, and its price and gain depend on
the model it runs on.

**And it is out of reach on the Personas route, the route from 2026-09-24 (entry 188).** Fast mode
is OpenAI's `service_tier`, and Personas' `llm_config` has no such field and refuses unknown ones.
Turning it on needs Ofself to add a tier setting, or this project back on the OpenAI route with its
own credit.

**Why it matters.** It is the one latency lever measured that is both large and safe.
- **The plan call is 39–48% faster** on Fast mode, with no decision changed: Japan open, Germany
  "visa required" and Singapore "no visa" in every call.
- **Selection is 23% faster and roles 13%**, because selection's seconds are mostly fixed.
- **It costs twice the standard price** of whatever it is turned on for.

**The choice — the owner's.**

| option | fresh request | repeat | model cost, fresh | model cost, repeat |
| --- | --- | --- | --- | --- |
| today | ~55s | ~24s | $0.251 | ~$0.035 |
| Fast mode on the plan call | ~42s | ~14s | ~$0.30 | ~$0.07 |
| Fast mode on every call | ~39s | ~14s | ~$0.50 | ~$0.07 |

Projected from entry 171's split, not timed end to end. Since entry 178 a repeat inside the
24-hour reuse window makes no plan call at all, so Fast mode's gain is for fresh requests and for
repeats after the window.

**If it ships.**
- **Make the tier reviewable policy, per call** — a setting beside `openai_reasoning_effort`, never a
  hidden default, so each call's tier can be chosen on its own.
- **Record the tier each call was served** in `var/usage/`. OpenAI downgrades to the standard tier
  when traffic grows past its ramp limit and says so only in `service_tier`.
- **Time real requests afterwards, several each**, on fresh and repeated corridors, before quoting the
  new seconds. The table above is arithmetic.

**Do not take the cheaper shortcuts instead.** Reasoning `none` answered Japan "visa required" where
no page states it, 3 of 3, and `gpt-5.6-luna` wrote Japan a "no visa required" plan (entry 177).


---

## Later

### 69. Read scanned PDFs — for ranking first, and as evidence only after a decision — `later`, **added 2026-09-25**

**Why it matters.** The rebuild sequence's step 2 checked the PDFs whose text could not be read
before the rebuild. None holds an oracle answer, so this waits. But **196 score for a role on their
link alone**, and they are guidance nobody can currently use, in the corpus or in a live corridor:
- **95 of 1,001 with an empty text layer (scanned)** — Thailand's visa-fee tables (updated 15 July
  2024) and its 60-day visa-exemption notice, Czechia's consular fees for August 2026, a South
  African visa-exemption notice, Swiss fee sheets, Norwegian checklists for other residences.
- **101 of 215 that could not be parsed** — mostly IRCC's document checklists (IMM 5484 and its
  siblings). These are dynamic Adobe forms that show a "please wait" shell to any other reader, so
  text recognition would not help them either. They need a different reading, or stay named.

**Two uses, with very different risk:**
- **Ranking — low risk.** Text recognition at corpus-build time puts a scanned page's words into
  `var/pagetext`, which ranks and never speaks (entry 78). A misread word costs a ranking.
- **Evidence — needs a decision entry first.** A live corridor would quote recognised text to a
  traveller. A misread digit in a fee table is a wrong fee with a citation. `QuoteChecker` would
  compare the quote against the recognised text, so it cannot catch a recognition error. Argue it
  against entries 5 and 156 before any code.

**First step:** count how often a corridor's selection or shortlist includes one of the 95. That
says whether this is a real gap for travellers or a store curiosity. It is offline, over
`var/recall`.

### 49. The family is walked at 25 members a build and has 169 — decide if that is enough — `later`, **stopped 2026-09-14 (entry 148)**

> **Stopped here on 2026-09-14 by the owner's rule (entry 148).** The corpus holds what every
> traveller shares; the post for the country a traveller applies from is traveller-specific, and
> live search fetches it at request time. The seed (entry 137) and the family ordering and host
> back-off (entry 139) shipped and stay. **The budget question below does not need answering** —
> walking all 169 members is the exhaustive per-residence coverage the rule hands to search. Kept
> for its measurements, and in case a sweep ever shows search failing to supply a post.

**The corpus does not hold the destination's post in the country the traveller applies from, and a
27-country sweep found it eight times (entry 132).** Australia holds **1,599** pages on
`embassy.gov.au` and **0** on `uae.embassy.gov.au`; China holds 3,523 on `china-embassy.gov.cn` plus
2,280 on `china-consulate.gov.cn` and **0** on `ae.china-embassy.gov.cn` or
`dubai.china-consulate.gov.cn`. Search supplied those pages on every corridor that needed them.
Measured from a second residence (entry 133): **24 of 27 corpora hold no post for either**, and
Australia holds 35 pages on its Riyadh post against 0 on its Dubai one — same authority, same host
pattern, so the crawl never went there rather than being unable to.

**~~The data half~~ — done 2026-09-05, entry 134.** `countries.yaml` gave 184 of 198 countries only
their ISO code; it now carries name forms for all and curated cities for 115, 293 labels to 723.
Labels let a corridor *recognise* a post it is shown; they do not put one in the corpus.

**~~The seeding half~~ — done 2026-09-06, entry 137, and the item's premise was wrong.** This item
proposed finding the missing posts with a **search query** for the ministry's index of its own
missions. It did not need one. **44 of the 53 corpora already record such an index, and 34 never
opened it** — Australia's `www.dfat.gov.au/…/our-embassies-and-consulates-overseas` sits at depth 1
with status `unknown`, and opening it by hand yields **194** per-country mission pages, of which
the corpus holds **one**, the United Arab Emirates member linking straight to
`uae.embassy.gov.au`. The family gate groups **70** of the 194, in two families of 45 and 25, and
the UAE embassy page is inside the 45; the other 124 name their country mid-address and form no
family — the same blind spot item 47 exists for, one level up. So this was **allocation, not discovery** — item
48's distinction, inside this item.

> **And allocation alone could not have fixed it, which is what settled the shape.** That chain is
> three hops and `maximum_depth` is 3, so from depth 1 the post's guidance pages land at depth 4 and
> are never recorded at all. Reserving budget for the index where it lies — entry 88's answer to a
> page that never wins the frontier — would buy a home page and nothing on it. **A seed is depth 0,
> and depth 0 is what buys the three hops.** `mission_index_seeds` promotes up to eight recorded
> addresses per build, unopened first; `CORPUS_FAMILY_PATTERN` was widened to admit the mission
> family, which it had been refusing because `…/australian-embassy-{}` carries no visa word.
>
> **Do not add `{residence}` to `corpus_queries`.** The bar in its own docstring
> (`discovery/corpus_build.py`) is not "does a traveller dimension appear" but "is the dimension
> covered **exhaustively**" — which is why purpose is swept in four passes. Residence fails that as a
> *query* dimension and passes it as a *seed* one: one index yields every post and favours nobody.

### What is left, and the first step of it has been run

**Step 1 was run twice, and the second run fixed both of the first run's causes (entries 138 and
139).** The corpus holds **4,008** entries on **86** hosts, the family is genuinely being walked —
50 members attempted against 25, 12 read against 3, six new mission hosts entering *through the
directory* rather than through search — and **`uae.embassy.gov.au` is still 0 pages**, because
`www.dfat.gov.au` is given up on after six unanswered requests before the sweep reaches the U's.

**Step 1 as it stood after the first build (entry 138).** `visa-discover corpus --country AU`, on
2026-09-06: the corpus went 2,874 → 3,563 entries and **the family went from 1 member recorded to
166**, which is the defect entry 137 diagnosed, closed. **`uae.embassy.gov.au` is still 0 pages.**

Two measured causes, and the seed is neither of them:

- **`www.dfat.gov.au` timed out on 22 of the 25 members opened** — plain `ReadTimeout` inside 20s,
  not a challenge or a block, under sustained crawling at a 0.5s host delay. Three came back
  readable.
- **Which 25 is document order.** Every member scores 0.0, so the reserved queue falls through to
  the frontier sequence, which is the order the links sit on the page: `australian-embassy-argentina`
  through `…-hungary`, and `australian-high-commission-bangladesh` through `…-new-zealand`. Both
  alphabetical heads. **A single-host family whose budget is smaller than its membership never
  reaches its tail**, and `united-arab-emirates` is in the tail.

**And do not read the rebuild's ten new hosts as this change working** — `philippines` at 107 pages,
`bangladesh` 66, `chile` 41, `peru` 34, `fiji` 25. `discovered_from` says every one arrived from its
own search seed or a sibling that did; **exactly one page on one host came from a mission page**. It
is search variance, and it also means `var/corpus/AU.json` is now confounded as a before/after for
this change.

1. **~~Order the queue and cap a failing host~~ — done 2026-09-07, entry 139.** Family members
   attempted went **25 → 50** and read **3 → 12**, and **6 of 11** new mission hosts entered
   *through the directory* where entry 138's build managed 0 of 10. A corpus may order on what it
   lacks — never opened, then tried and failed, then read — and may never order on a traveller,
   which is entry 44 and is why the residence signal is not the answer here.
2. **The open question is now a budget one, and it needs an argument before code.** The family has
   **169** members and a build walks about **25**, because one host's share of one build's page
   budget is smaller than one family. So the sweep completes in six or seven builds. Three ways out,
   none measured:
   - **Let it sweep.** It works, it is free, and it needs nothing built. Six builds is six nights of
     a scheduled job and 420 search queries.
   - **Give a family its own host allowance.** `_next_wave` refuses to exempt a family from the host
     budget *on purpose* — "a family lives on one host by construction, so exempting it would hand
     that host the whole crawl through the side door" — so this reopens a decision made
     deliberately, and has to argue against that sentence rather than around it.
   - **Seed the members directly**, as `mission_index_seeds` seeds the index. A seed is depth 0 and
     escapes the family queue entirely, but 169 seeds against a 1,200-page budget is entry 101's
     failure: the whole allowance spent fetching seeds.
3. **Do not rebuild the other 51 yet.** A build is roughly 15 minutes and 70 search queries. China
   is still a named expected miss: its index forwards with `window.location.href` rather than a link.
4. **Then re-run the `BD/AE` and `BD/SA` sweeps** and compare. Three things will otherwise waste it:
   - **Australia's row is already confounded** — ten of its hosts arrived by search variance in the
     first rebuild, not by any change here.
   - **Copy `var/recall` aside first.** A recall log is keyed on its corridor, so a re-run
     overwrites it (entry 118) and the baseline is gone.
   - **Do not clear `var/cache` for one arm only.** Entry 136 lost a whole measurement that way: a
     cold arm against a warm baseline read as a two-point regression the code had nothing to do
     with, because `blocked` went 1 → 15 and `challenged` 15 → 27.

**What success looks like**, unchanged and stated before the run so it cannot be moved afterwards:
the corpora hold a post for the residence in more than the 3-of-27 and 2-of-27 they hold now, and
the corridors that currently buy those pages from search read them from the store instead.
`australia/BD/AE` and `china/BD/AE` are the two clearest cases — both currently take their UAE-post
pages from search while holding the *Saudi* post of the same authority.

**Two things this deliberately does not cover.** A **cold** build gets no mission seed, because
there is no previous corpus to read one from; the search-query form is still the right answer there
and nobody has measured whether such a query returns the index. And **nine of the 53** record no
index this recognises — it is a keyword gate and it misses.

**Why:** entries 132, 133 and 137. It compounds with entry 126 — the residence signal scores a page
for being about where they apply from, and here that page is not in the corpus to be scored.

### 35. Finish the Netherlands, then roll the family reservation across the other nine — `later`, **parked 2026-09-14 (entry 148)**

> **Parked 2026-09-14 (entry 148).** The family reservation exists to make the store cover the
> per-traveller dimension offline, which the owner's rule hands to request-time search. Root seeding
> — the traveller-neutral half of this item — lives on as item 48.

> **And it has a concrete, cheap first move as of entry 130: seed every trusted host's root.**
> Across all 53 corpora, **1,148 of 2,222 hosts (51.7%) have pages and their root was never visited
> at all** — only 20 roots were seeds. 294 of those hold twenty pages or more: Spain's
> `www.interior.gob.es` at 1,930, Finland's `um.fi` at 1,736, Greece's `portal.immigration.gov.gr`
> at 428, Bulgaria's `mfa.bg` at 399. A build seeds from search results, and a search result is a
> **page, not a site**, so a host enters the corpus wherever the engine pointed and whether the
> crawl ever reaches its front door is left to the link graph below that point.
>
> Thailand is the worked example. The corpus holds three `tdac.immigration.go.th` pages, all
> children of one search seed at `/manual/en/`, and the arrival-card form itself is linked from
> none of them — so search supplies it on every run. **Measure before building**, per this file's
> own rule: it is not known whether a root yields links a deep seed does not (one host is not
> evidence), nor what it costs, since entry 82 found surplus budget flows to the *largest* host and
> roots on the frontier could feed the same appetite.
>
> **A second Thai finding, separate and not fixed by roots.** 2,617 of its 2,662
> `immigration.go.th` pages are **provincial office** sites — Uthai Thani alone holds 492 against
> the national site's 41 and TDAC's 3. They are WordPress installations whose category and archive
> pages present an effectively unbounded link graph.
>
> **Sized on 2026-09-02 (entry 129), and it is smaller than it looks.** Of the 30 role-cells the
> corpus cannot answer, **12 are an official tool holding the answer** — not a gap at all, and
> resolved by the product since entry 63 — 4 are pages nobody may read, and 2 are Germany declining
> to name a document. **Twelve cells are the whole of what a deeper crawl could address**, and a
> curator has read the candidates for each and found nothing. Meanwhile the 25 load-bearing pages
> search supplies are all on hosts the corpus already crawls but never recorded, concentrated in
> Lithuania (12, behind a `Disallow`), the UK fee form (3) and Bulgarian PDFs (3). **So this item's
> value is in the countries with a form-gated or PDF-deep space, not in the ten it was written
> for.**

**The rebuild was run on 2026-08-29 and its acceptance test could never have passed.** 42 queries,
162 seeds, 2,965 pages crawled — **27 new entries, verdict unchanged**. `build_corpus` seeds from
search results only and merges the existing corpus in afterwards, so a rebuild re-walks the same
ground: **an address a build recorded and left unfetched stays unfetched however often you re-run
it.** Entry 88's 3–15% is structural, not a budget symptom. Entry 101.

**Two of the three things this item asked for turn out to be already true, and the gate was hiding
it.** `opened` counted a member that *fathered a recorded link*, so a member fetched from a page
that links nowhere read as never fetched. Corrected to `read = max(opened, text_held)`, the Dutch
families are **schengen 100%** (was 39%), `entry-visa` 94%, `consular-fees` 99%. The 113-page gap
the old column showed was entry 89's VFS Global ceiling being reported as a crawl gap.

**What is genuinely left, and it is small:**

- `airport-transit-visa/apply-{}` at **52% read** — in scope, serves the `transit` purpose.
- `mvv-long-stay/apply-{}` at **1%** — long-stay, so arguably not this product's business.
- Three families at **0%** that should never have counted: `passport-id-card/abroad/apply-{}`
  (Dutch citizens renewing a passport), `caribbean-visa/short-stay/apply-{}` (Aruba/Curaçao —
  outside Schengen, so *wrong* for a `netherlands` corridor), and `making-appointment/{}` (booking,
  permanently out of scope). All three pass `CORPUS_FAMILY_PATTERN` because it keyword-matches the
  address on `apply|visa|appointment`.

**Step 1 is done (entry 102).** `CORPUS_FAMILY_PATTERN` now requires a visa-domain word rather
than any government word: `apply`, `appointment` and `fees` are gone, because they admitted Dutch
passport renewals and appointment booking. Measured over all ten corpora first — it drops exactly
those two families and keeps every other family in every country. It also stops the crawl reserving
budget for them. The `incomplete` advice line, which entry 101 showed was false, is fixed too.

**And the gap this item was aimed at turned out not to be the biggest one (entry 103).** Reading
`unresolved_roles` counts a tool-settled role as unresolved; against the oracle, the genuinely-open
roles are **`general_entry` 7, `document_checklist` 3, `processing_times` 3** of 120 slots. The three
roles with the fewest lexicon terms are exactly the three that score **zero** candidates in some
countries, and they hold 11 of the 16. `general_entry` is now widened — Japan 0 → 2 candidates, the
UK 10 → 23 — with every other role's top page unchanged.

**`fees` and `processing_times` are now done too (entry 104)**: corridors scoring zero for those two
fall **14 → 10**, Sweden's timings go 0 → 15 topped by the right page, and the Netherlands' fees are
topped by `consular-fees/india` at 112.8. `payment` was tried and rejected — it promoted a checkout
page over the fee schedule.

**Two vocabulary follow-ups, both small and both needing their own measurement:** `customs` (weight 8
in `general_entry`) still pulls Canada's vehicle-import page and was left in a thirteen-term change
where it could not be attributed; and Germany scores **zero for all three widened roles**, which is
now firmly a discovery gap rather than a scoring one — its pages are in the text index by cache
backfill and not in its corpus. That belonged to item 30, now closed; Germany has since been rebuilt across 87 hosts (entries 107–108).

**Step 2 is what remains of *this* item: seed the crawl from the corpus's unfetched addresses**, the only thing
that can ever open them. Entry 101 rejected doing it blind — 600 depth-0 seeds against today's 162
is a real change to crawl shape. **And measure first**: an attempt to establish whether unfetched
recorded pages hold checklists anywhere outside the Netherlands failed, because URL-pattern counting
cannot tell a checklist from a Bastille Day PDF. Without that measurement step 2 is a crawl-shape
change justified by one country whose ceiling is a contractor.

**The other nine are unchanged and mostly no-ops** — six read *no per-traveller dimension*, and SG
and GB are *bounded by the authority*, which is a pass. Verified after the measurement change: no
other country's verdict moved.

**Do not raise the share to reach further.** Unchanged and now doubly true: the last build opened
661 pages against a 1,200 budget and 290 on `netherlandsworldwide.nl` against a 400 per-host cap, so
nothing was capping it.

### 47. Find out how much of the world the family detector cannot see — `later`, **parked 2026-09-14 (entry 148)**

> **Parked 2026-09-14 (entry 148).** Both things resting on the family detector — `coverage` half
> two and the crawl's family reservation — serve per-traveller coverage of the store, which the
> owner's rule hands to request-time search.

**Romania holds a 58-member per-residence checklist family and `coverage` reports it as having
none** (entry 121). `eviza.mae.ro/media/3252/MAREA-BRITANIE.PDF` is the page that filled
`document_checklist` for a UK-resident applicant, and its siblings are `AFGANISTAN`,
`ARABIA-SAUDITA`, `BANGLADESH` — named in **Romanian**. `country_family_keys` matches English
country slugs and returns `[]` for every one.

> **The premise narrowed on 2026-09-02 (entry 124), and the fix looks smaller than this item
> assumed.** Romania's family is *not* invisible for being in Romanian: its anchor text is English
> ("United Kingdom"), and `wrong_country` reads it correctly to reject the other 55. What missed it
> is that `country_family_keys` matches the **URL only** — so `coverage` cannot see a family the
> live scorer can, which makes this a **metric** defect rather than a recall one. **Try matching the
> anchor text before building any translation table.** A language-agnostic sweep of all 53 corpora
> then found the residual blind spot is overwhelmingly **English aliases and dependent
> territories** — `czech-republic`, `ivory-coast`, `cape-verde`, `east-timor`, `kosovo`,
> `cook-islands`, `anguilla`, `curacao`, `hongkong` — not translations. That is a bounded alias
> fixture of a few dozen rows, not 198 names in every authority language.

> **Narrowed again on 2026-09-02 (entry 126), which built the anchor-text instrument this item
> suggests trying first.** Grouping on the anchor text and masking whatever part of the address
> varies with it finds the four per-residence *application* families the corpora hold — Canada 538
> pages, the Netherlands 332, Romania 65, Croatia 12. `country_family_keys` sees **two** of them:
> it misses Canada's `?country=IN`, a two-letter code below its three-character floor, and
> Romania's Romanian-named PDF. So the anchor-text instrument works, it is written down in entry
> 126, and it is worth an hour to fold into `country_family_keys` — but note **the two-character
> floor is a second blind spot the language story never predicted**, and lowering it is not free:
> `FAMILY_TOKEN_MINIMUM` is 3 because two-letter tokens collide with everything.

**Two things rest on that function**, so the blind spot is not cosmetic: `coverage` half two, whose
verdict is computed from families alone (entry 90), and the crawl's family reservation, which is
entry 88's whole answer to a corpus that opens 3–15% of what it records. A country publishing in
its own language gets neither.

**Measure before building anything, and note the obvious probe does not work.** A language-agnostic
sweep for runs of sibling URLs sharing every path segment but the last found 16 corpora with a run
of 20 or more — and **missed Romania's own family**, because its members sit under different
numeric parents (`/media/3120/`, `/media/3126/`) rather than a shared one. So that probe undercounts
and its zero means nothing. Something that groups on the *last segment's* shape, independent of the
parent, is what would actually count this.

**Then decide what to do, and do not assume it is a translation table.** 198 country names in every
authority language is a large fixture with a maintenance cost, and entry 70 already found that
demonyms bought 22 shortlist places all of which were noise. A cheaper candidate: a family is a run
of siblings differing only in one token, whatever that token means — which needs no country list at
all and is what the failed probe was reaching for.

**What this does not change.** Entry 120's rule stands: the oracle grows one country at a time. If
this measurement shows several countries have families nobody could see, that lowers the number of
genuinely `ungraded` countries rather than raising the number needing curation.

### 46. Decide what to do about a refusal served as `HTTP 200` — `later`, **demoted 2026-09-02**

**Morocco's authority declines the request and answers `200`** (entry 121). All four candidates in
`morocco/IN/GB` came back as `unusable`, *"too little readable text to trust"*; fetched directly
under our own user agent they are 244 bytes of *"Request Rejected. The requested URL was rejected.
Please consult with your administrator. Your support ID is: …"* — an F5 BIG-IP block. `unusable`
says we read the page and it held nothing. The truth is that we were not permitted to check, which
is entry 18's distinction and the one this project treats as load-bearing.

**It is a diagnosis defect and not a safety one, which is why it is an item rather than a fix.**
All 43,153 indexed bodies were scanned and **0** hold that sentence: at 140 visible characters it is
below `minimum_source_characters`, so the thinness guard already stops it becoming a source. Entry
117's failure — an interstitial stored and citable — cannot happen here, and only because
Cloudflare's is ~1,370 characters and this is not. **That is a size accident, not a design, and it
is the reason to look rather than to leave it.**

**Why reclassifying is a decision.** `blocked` feeds `inaccessible_urls` and entry 32's
`decision_blocking_urls`, so a body-marker test would change **what resolves a corridor** —
a Moroccan corridor could start reading `resolved_decision_blocked`. Entry 57's bounds and entry
32's narrowness both apply, and entry 109 is the warning next door: it establishes a block from what
the page **states**, never from a vendor's scaffolding. F5's sentence is the page stating it, which
is the good case; the risk is the next vendor whose sentence is less clear.

**Do:** count first. How many pages across the 53 corpora answer `200` with a body under
`minimum_source_characters` that names a refusal, and on how many hosts. If it is Morocco alone the
honest fix may be a truer `unusable` reason rather than a new outcome.

### 27. Decide whether a hosted scraping service may be used, and only for corpus discovery — `later`

**Why:** asked directly on 2026-08-24 (Firecrawl). Worth writing down because the answer is *mostly
already decided* by rules this project treats as inviolable, and the one open part is narrow.

**Retrieval through such a service is refused by existing rules, not by a new one.** Firecrawl's own
front page sells "Proxies, anti-bot, JavaScript rendering". That is the thing
[CLAUDE.md](CLAUDE.md) forbids outright: a refusal must never be worked around, and a service whose
selling point is bypassing bot detection makes that unauditable even if the feature is never
deliberately switched on. Three further rules land on the same answer:

- **The posture is honest client** (entry 35). The project announces `VisaResearchAgent/0.1`, and
  entry 41's argument for answering France's Cloudflare challenge — "our own renderer, under our own
  user agent, misrepresents nothing to anybody" — depends entirely on the client being ours. Through a
  third party the authority sees their infrastructure, not ours, and that argument evaporates.
- **`robots.txt` is read and obeyed by us** (entry 36). Delegating that to a vendor's policy is
  delegating a rule this project does not delegate.
- **Never disable TLS verification** (entry 12). The chain is verified here, with intermediates
  bundled and each checked to a trusted root, because an attacker impersonating an immigration
  authority could dictate what documents a traveller brings. A third-party fetch cannot be attested.

Provenance is a fourth: entry 4 requires a stored row to record when the **evidence** was retrieved,
and a vendor cache layer muddies that. And `/extract` — LLM extraction inside the vendor — would be a
second unaudited model deciding what a page says.

**What is genuinely open, and only this:** `/map`, for **offline corpus discovery**. Enumerating which
URLs a government site has is not retrieval, not evidence, and not in the request path — it is the same
role search already plays under entry 11, *a candidate generator that may never widen trust*. Pages
would still have to be fetched by our own client to become evidence, and every domain rule still
applies. It would speed corpus builds, which cost search quota.

**Do first, because it may make the question moot:** [item 10](#10-try-sitemaps-before-crawling--later),
which is the same idea with no third party, no cost and no new trust surface — read `sitemap.xml`,
which `robots.txt` already points at, before crawling.

### 10. Try sitemaps before crawling — `later`

**Why:** within already-approved domains, `sitemap.xml` gives the full URL inventory for scoring without
the politeness-heavy two-hop crawl. And the crawl has a known hole: its 40-page budget is spent entirely
at depth 0 (see *Smaller things*), so depth-2 discovery — where Japan's checklist was found — never
happens for a multi-domain destination.

**Do:** check first whether the seven verified corridors' chosen pages appear in their domains'
sitemaps. If most do, the crawl becomes a fallback rather than the primary mechanism. Cheap to check,
and worth checking before optimising the crawl further.

### 11. Decide whether a host that has refused every request should be skipped — `later`

**Why:** entry 24 recovered three of the US corridor's five wasted fetch places. **Two remain**, both
`travel.state.gov`, and they remain because neither URL was ever crawled — one is a PDF, which the crawl
skips by design. The per-URL rule cannot help, and every other `travel.state.gov` request has been
refused.

**The question, a judgement rather than a lookup:** may a host that has refused *every* request and
served *none* be treated as blocked for URLs never tried? It recovers two places out of **twenty-five**
(entry 40 — this line said "ten" until 2026-08-22, which overstated the gain by more than double), and it
is inductive, which is why it was not simply done.

**Do:** count requests and refusals per host; consider it only where refusals are high and served is
zero. Then measure whether the two recovered places change what the corridor resolves. If not, leave the
rule out — an inductive skip that buys nothing is not worth its risk. Item 5 may make this moot: a
`Disallow` is a stated policy covering paths never tried, which is the honest version of this inference.

**Careful:** a `403` on one path is genuinely not evidence about another — real sites put WAF rules on
some paths and serve the rest. A host-level skip can silently lose a readable page, and losing evidence
costs a refusal. The block must still be reported as `blocked` (entry 18), and nothing here may become a
retry.

**And do item 5 before this — 2026-08-19.** France looked like the strongest case for a host-level skip:
eight `france-visas.gouv.fr` paths refused in one run while eight more took shortlist places and refused
too, so 15 of 25 places were read. Measured, the right answer was not to skip the host but to answer its
challenge — and behind the challenge at least one of those "blocked" URLs was a plain **404**, which a
host-level skip would have permanently hidden rather than revealed. A skip is inductive; reading is not.

**Also still overstated:** `pages_fetched` is the shortlist length rather than the number of pages that
were readable, so it now reports up to 25 read when fewer are usable.

### 12. Watch where the two deciders disagree — `later`

**Why:** `decided_by` says which decider chose, and the heuristic's score is kept beside the model's
choice. That divergence is free evidence about both, and nobody is reading it.

**Do:** on a corridor run, note every role where the model chose a page the heuristic did not rank first.
A pattern is either a lexicon gap worth closing or a model error worth prompting against. Four corridors
currently disagree on `general_entry` and `visa_decision` most.

**Careful:** do not tune the lexicon to agree with the model. The heuristic's job is to build a good
shortlist, not to reproduce the model's judgement. It is no longer the fallback (entry 31), so
its remaining jobs are the shortlist and the offline baseline.

### 13. Revisit conflict detection, with claim scope — `later`

**Why:** entry 30 deletes the unverified `conflicts` field. That removes an alarming unchecked signal; it
does not answer the underlying question, which is real — official sources do disagree.

**Do:** record the population each claim applies to, and compare only same-scope claims — the exact gap
that killed the previous attempt. Leave the visa decision out of comparison; it already has stronger
guards. Restrict to quantitative rules (validity periods, stay lengths, processing times) where a wrong
flag costs a caveat rather than alarm. Full post-mortem in [DECISIONS.md](DECISIONS.md) entry 6 — read it
before starting.

### 14. Detect drift in configured sources — `later`

**Why:** every source already stores a content hash, so a changed government page is detectable and
currently ignored.

**Corrected 2026-08-21:** the premise below — that government pages change whitespace constantly — is
weaker than it reads. `content_hash` is `sha256` over the **cleaned** text
(`live_sources.py:451`), taken after `clean_source_html` has stripped `script`, `nav`, `header`, `footer`
and `aside`, so most incidental churn is already gone before the hash is taken. What survives is dated
"last reviewed" lines and rotating banners. Do not add a second hash over raw bytes; it would fire on
every nav timestamp. See entry 44 and item 20, which makes this the corpus-rot check.

**Do:** on a hash change, mark the source rather than refusing — government pages change whitespace
constantly. **Never** auto-rediscover and swap a role-bearing source: that is the wrong-checklist failure
with the human removed. A persistent failure over several runs is the honest trigger to propose a
replacement.

---

## Done

Kept because what building something found is usually why the item after it exists. The reasoning is
in the DECISIONS entry; this is the one-line index.

| Was | Done | Entry | What building it found |
| --- | --- | --- | --- |
| — The full rebuild: the pilot, then every other store | 09-25 | 193, 203, 204 | **All 55 rebuilt and graded.** The pilot's loss was the selector's, not the store's (item 66). The 44's reports showed the archived-year veto still dropping filed guidance in three forms, then a fourth; widened, and ZA, CY, HR and Brazil rebuilt. The stores hold every oracle answer; item 70's corridors answer as before or better; Brazil's refusal is its `robots.txt` |
| 68. Read more of what a build records, and choose what to open with more context | 09-25 | 185–187, 189, 192, 200 | **The cause was the host split, not the ordering**: Japan's visa host was cut at 25 pages with 149 scored links dropped. A scored link may now read past its share (Japan 0 → 12 of 20 oracle pages), and a link is scored with the text around it (11 → 15). In the real stores since the full rebuild. Version B (a model ordering the frontier) stays declined; opening zero-scoring links only near a seed was not adopted (entry 200) |
| 70. Find why a corridor that read its authority's pages still has no visa decision | 09-25 | 198–202 | **The lead was wrong: the roles call was right on every packet it refused**, so nothing in the prompt needed fixing. Re-run three times each and traced, 11 of the 14 now answer "visa required" from an official page, through eight fixes, all measured before shipping: a plan refusing itself over a page it could not read (UAE), a residence-permit veto dropping the Dutch checker, a year veto dropping every pre-2025 upload (Malta, rebuilt), the lexicon missing "required to hold a visa" (Belgium — a PDF-only depth rule shipped first and was withdrawn as unjustified), the selector seeing only a page's head (Slovenia), an 80k plan-input guard (India), an uncited step link (Germany), and rule 8g — a visa on arrival is a visa (UAE). **The EU now answers a Schengen member's visa decision** from EUR-Lex (entry 201): Croatia and Poland, refused and null, answered 6 of 6. Cloudflare's challenge proved unanswerable without disguising the client (202). Mexico (an image) and Saudi Arabia (unreadable) still refuse |
| 66. Keep the selector's picks as good as its pools grow | 09-24 | 194, 195 | **The pilot's 75 → 68 was half noise, a month-old baseline and one address**; replaying only the selection call, five runs a corridor, the real loss was −2.8 of 90, all in secondary roles, while decision + checklist rose 23.2 → 25.0. **A shorter list, not more text, fixed it**: the whole pool 76.6, an 800k text budget 73.3, the fusion top 120 82.4, top 120 + 40 pages with no stored text 80.0 at 42% less input. **The owner shipped top 120 + 40 blind without the live A/B** and dropped the rule that no candidate is dropped — the blind 40 are where the model found the traveller's own posts, which the oracle cannot credit. `selection-recall` gained a same-page column, because the oracle names one address per page |
| 62. Pay for model calls through Ofself Personas | 09-24 | 188 | **Blocked on Ofself, then documented overnight**: Personas' live guide grew a model-only call, `capabilities: []` — one plain call, nothing added to the prompt (the `debug` request event showed only our two messages), with strict JSON schema and reasoning effort in `llm_config`. **`llm_config.model` is ignored without the app's own key**, so each call's agent holds the model and every reply's model is checked. `research/personas.py` implements the three existing interfaces; `model_route: personas` switches all of them. **Graded without an OpenAI arm**: selection 41 of 48 oracle roles against entry 170's direct 39 of 48, nine of ten corridors unresolved exactly as before; 14 plan calls with no refusal and no wrong "no visa", Germany and Singapore as baseline, Japan "visa required" once in six — a *Smaller thing*. Lost: prompt caching, Fast mode, cached and reasoning token counts. **The owner made it the route from now on** |
| 5. Answer the challenge, honour every `robots.txt`, and get a checklist out of France | 09-16 | 75, 92, 93, 109, 179 | **Steps 1–4 were built on 08-25 (entry 75), and the item still called them undone**, as did four other files. France's checklist is behind the Visa Wizard — named, never driven (92, 93). Step 5, measured: **12 of 24 challenges answered, and the 12 that were not all needed `challenges.cloudflare.com`**, which the render gate aborts. France's corridors lose 14 of 17 challenged pages to the five-render total, not to the challenge. The `robots.txt` count: **401 of 3,471 origins serve a web page there**, holding 4,687 read pages and 171 corridor reads; one is a real policy labelled `text/html`, already obeyed, so the verdict stays. Both spending decisions are item 61 |
| 48. Test root seeding before building it, and separate discovery from allocation | 09-15 | 161–163, 176 | **Root seeding was probed and rejected**: 0 of 9 target pages reached from eight hosts' roots. **The gap was a build discarding its own search seeds**, kept only if another page linked to them; fixed, and a matched test found Thailand `IN/GB` resolving in 4 of 4 runs where it had refused in 4 of 4, for ~9% more a corridor. Before rebuilding, a failed search query stopped costing a build (162) and a `www.`/bare host pair became one budget share (163). **All 53 corpora rebuilt the same day**: 190,491 → 237,283 entries, 7,289 seeds kept, no failed queries, ~2,590 queries (~$13) over ~10 hours two at a time. China crashed on a redirect to an address that is not a URL (176); fixed and rebuilt. Equal budget shares for unequal hosts moved to *Smaller things* |
| — Reuse a plan written for the same inputs | 09-16 | 178 | **The owner's decision, amending entry 44.** The model's draft is kept, never the plan, keyed on everything the model is shown — prompt, packet with every page's text and retrieval time, schema, model settings — for up to `plan_reuse_hours` (24, never past the page TTL). Every request still checks quotes, validates and grades on its own retrieval, and a refusal is never kept. The risk it takes: a bad draw reaches every identical request for up to a day, as a good one does. 15 tests, and identical keys on two real consecutive requests for three corridors. **Not timed live: the OpenAI account ran out of credits** — re-run Japan `IN/GB` twice once it is topped up |
| 56. Make the written plan shorter | 09-15 | 174, 175 | **Short source ids were declined**: 2 refused plans and 2 wrong "no visa required" answers for Japan in 48 calls, none in 48 without them. **The owner shipped trims 2 and 3** — one quote of at most 150 characters, and a few words of why an unconditional document applies — and not trim 4. The visible plan fell 5–13% but billed output only about 150 tokens, because hidden reasoning did not shrink with it: about 1.5s of a ~25s call, too little for measured seconds to show. Japan's decision stayed open and Singapore's "no visa" held in every call. Rule 8e's bounds live only in the prompt, so any change to this call re-runs both first |
| 19. Get a corridor under ten seconds; search may stay | 09-15 | 140–146, 159–173 | **Closed, not reached: ten seconds was set against the research stage alone.** A fresh request measures ~55s end to end, ~29s of it writing a plan that is never stored. Delivered: search pace 19.0s → 2.6s at identical spend; every corridor's seconds and every model call's tokens, cache writes and retries recorded; search kept on every corridor, measured twice; model calls $0.394 → $0.251 a fresh corridor, after finding every call was writing its whole prompt to a cache billed at 1.25×. Refusing on a miss dropped. What is left is items 58 and 59; the plan's wait is 56 and 57 |
| 51. Make live search ask only for what is specific to this traveller | 09-15 | 159, 160 | **Nothing was built, and both results are measured.** The owner's corpus-first version was tried two ways (entry 159). Searching only after the corpus leaves a role open projects −3% money and +4% seconds, and misses the traveller's own embassy pages. Deciding per query from what the corpus holds loses 5–6 of 8 answering pages. **The purpose query was marked traveller-neutral and is not** (entry 160): it alone returns 28 of the 45 pages it was first to find, and in matched runs dropping it cost Japan `IN/GB` its London-embassy checklist and moved Norway `IN/IN` to an older checklist, the same way in both runs. It would have saved $0.030 a corridor. All three queries stay |
| 31. The anchor scorer gates 94% of the corpus: measure it, scope a fix, test it | 09-14 | 123, 125–128, 158 | **The 94% held four fixture answers nothing in the pool could replace**, and every rule tried recovered them, so cost and safety chose. Admitting every page whose stored text scores cost +68% input and was mostly chaff; a cap the size of the pool displaced 1,813 pooled pages with no text and five the fixture names. **Shipped: the five best per role on stored text, added, nothing removed** — each recovered answer ranks second for its role, +16% selection input over 53 corpora, and no second scoring pass, because step 3b already scored every candidate and threw the scores away. Czechia's UK checklist filled live; Liechtenstein's pool went 2 → 21 and its challenge still refused |
| 21. Fill the three provenance gaps | 09-14 | 156, 157 | **A claim now carries the sentence behind it**: the decision and every requirement get quotes the model writes and the application keeps only where the retrieved text holds them — 35 of 35 in a probe before building, 45 of 45 live after. A match proves the words exist, not that they fit the claim. **Every cited source carries its page's content hash and why discovery chose it**, attached when the plan is built because the retrieval cache is shared between corridors. Steps and `where_to_apply` still carry no quote |
| 54. Say which refused page mattered, once per authority | 09-14 | 155 | **14 of 142** answered runs name refused pages and **9** name three or more, up to eight across four sites (Malta). Each named refusal now carries whether the refused-page judgement picked it as able to hold the decision — set from `decision_blocking_urls` by the application, never the model — and the caveats say one sentence per authority, those pages first, every link kept. The model is told the same and asked not to repeat every address |
| 9. Tell "no checklist exists" apart from "we failed to find it" | 09-14 | 153, 154 | **Re-scoped: nobody can show a checklist does not exist.** The product was asserting it — the prompt, the documents panel and the delegate box — and now says what was found among the pages read; the per-country declaration is withdrawn. Of 60 resolved corridors without a checklist, 7 met likely pages they could not open, and a plan now names those with their links, set by the application and never the model. Item 17's Canada finding, a 64.0 checklist page fetched and declined three times, is recorded in entry 153's 48 rather than solved |
| 8. Confirm a blocked authority actually reads usefully | 09-14 | 152 | It reads as **we could not check**, not *no visa needed*, and the first step hands over the decision page. Two defects: one caveat sentence per refused page at equal weight, with the judged decision pages indistinguishable (item 54); and the web app served a corridor stored 16 days earlier that never named the London embassy a fresh run names, because corridor notes never reach a plan (item 7's storing decision). Whether the links open was left to a person — this session may not read a refused page |
| 17. Decide what a corridor that flips between runs should do | 09-14 | 43, 44, 118, 151 | Recall-side flips were answered by the corpus (entry 44). The US flip was counted: **0 in 3** back-to-back runs, and entry 118's flip was a run that filled no role, not the refused-page judgement. Its premise that a repeat spends no search was false. The counting found an unchosen retry: a refusal is never stored, so the next request retries it until one resolves, and that run is kept three weeks — deferred by the owner to item 7 |
| 53. A plan whose visa decision is null can still be graded `verified` | 09-14 | 150 | The docstring stated the rule and the code held it for one cause: only a block or a questionnaire downgraded a null decision, so a model's own null from cleanly read pages was graded `verified` — seen on `japan/IN/GB`. Now graded on the decision itself and refused by `VisaPlan`, with both tests shown failing on the unfixed code first. The interface needed nothing |
| 52. Stop hand-configured destinations answering every traveller from one traveller's pages | 09-14 | 149 | **The item's own claim was wrong.** Nobody was handed London's checklist: the model declined another traveller's list and a guard turned that into a 503 *"could not be generated safely"*, for a Filipino asking about Japan and a Nigerian asking about Singapore. Through the automatic path both are `verified` from their own post. The cost is Japan for `IN/GB`, whose pinned checklist fills in **1 of 3** automatic runs — the page fetched every time, the adjudicator naming the eVISA questionnaire instead. Every SG and JP corridor run from the command had measured a path the web app did not serve. Found item 53 |
| 1. Score a page for being about where the traveller applies from | 09-02 | 126 | **The scorer's ordering is consumed by nothing** — the pool goes to the model unsorted with scores withheld, so `score_link` reaches a corridor as a *boolean*. Shipped as a swap and cut back to adding only: the withdrawal removed **25 pages from the pool and added none**. Admits 35 of 186,596, and 3 of its 4 families already held the answer in stored text — which is the argument for item 31. Also: `_describes_country` could not read `united-kingdom` in a path, so every multi-word country was invisible unless the anchor said it |
| 50. Cap renders per host on the request path | 09-05 | 135, 136 | The item's own number was wrong and checking it made the defect worse: the shortlist shares **5** renders, not 12 — `MAXIMUM_CRAWL_RENDERS` is the *crawl's*. Two faults: one host could take all five, and a page nobody rendered reported itself as a page with nothing to read, which is why nobody had measured it. Three consecutive empty renders and a host is dropped, as `CHALLENGE_FAILURES_PER_HOST` does on the crawl; **the total stays at five**. A sweep then read the new reasons (136) and could price nothing — the cache was cleared for the after-arm only — and showed the cap does **not** recover Australia's roles: it stops a host starving *others* |
| 45. Re-run the five countries last measured before their corpus existed | 09-01 | 121, 122 | **Romania fills 5 of 6** off `eviza.mae.ro`, Austria 2 — both were predictions this item said would stand. Morocco refuses with an `HTTP 200` reported as `unusable` (item 46), and Romania's 58 Romanian-named checklist PDFs are invisible to the family detector (item 47) |
| 43. Give the new 43 something the coverage gate can grade | 09-01 | 120 | **42 of 53 countries were deferring to an empty half** and read as passes. Fixed with an `ungraded` verdict. The oracle is **not** growing to 53: 17 of the 42 resolve every passport tried, and of the 9 that resolve none, 6 have a named cause outside the store |
| 44. Re-measure the countries whose ranking text was a bot-check page | 09-01 | 118, 119 | NO and ID now fill **6 of 6**, TH names its checker. The Philippines' missing checklist is a **visa-free** corridor, Lithuania's ceiling is the challenge and not its `Disallow`, and the US gaps split — `travel.state.gov` blocked, `uk.usembassy.gov` never requested. The US corridor **flips** between two runs of identical code |
| 42. Why Liechtenstein's 7,456 pages yield two candidates | 08-30 | 117 | **Not Liechtenstein's fault.** `is_challenge` read `body[:20_000]`; Cloudflare's marker sits at 24,915 of 29,336, so an unanswered challenge was stored as the page. 414 rows across nine countries, including Lithuania's visa page and `egov.uscis.gov/processing-times` |
| 41. Build the corpora for the 43 remaining countries | 08-30 | 116 | 10 → **53 corpora** in ~13 hours. Three code defects only breadth could find (113, 114, 115). Nine corridors all answered from the store; the gate cannot grade any of the 43 |
| 30. Perfect batch 1 before adding a further country | 08-30 | 116 | All three stages met: 55 reachable, all run and refusing for named reasons (08-25), and 53 corpus-routed. **BR and UY are the two without a corpus**, at one authority domain each. Batch 2 is now unblocked and deliberately not started |
| 18. Build the offline corpus job, run it on more destinations | 08-30 | 44, 116 | Built as `visa-discover corpus` and now run on 53 countries. What it found is that a build *records* far more than it *reads* — 3–15% (entry 88) — which is why item 35 exists |
| 40. Let curation fetch one page the index does not hold | 08-28 | 99 | **Dropped.** France scores 100% at 7% text coverage; all seven misses had text the model had read, so the premise was wrong |
| 39a. Have a model actually produce the visa-free plan | 08-28 | 98 | A sixth blocker: extraction read a correct **empty** checklist as a failed model call |
| 39. Build the visa-free plan as an entry plan | 08-28 | 96 | The floor it needed was **no floor** — three visa-free corridors state 3, ~5 and ~7 duties. Forcing `where_to_apply` to null would have deleted the UK ETA |
| 38. Re-run the twenty oracle corridors | 08-28 | 97, 98 | `selector` recorded which selector was *configured*, not which ran — a credit outage put the heuristic in the model's arm |
| 37. Build the gate that says whether a corpus is good enough | 08-28 | 90 | A gateway cannot be told from a leaf by counting children, and the UK has a per-traveller family entry 88 counted as none |
| 36. What to do about guidance on a commercial contractor | 08-28 | 89 | Named, never read, never believed. 44 of 236 contractor links are "track your application"; only 30 are documents |
| 34. Build an oracle neither selector helped make | 08-27 | 87 | ICA publishes one page at three addresses, so "a page proven to fill a role" was never one page. Entry 86's +41 is **+30** |
| 33. Measure the model candidate selector | 08-27 | 85 | Turned on. It reads half as many pages and finds more; a country with no stored text falls back and says so |
| 32. Raise the corpus page budget / fix the budget split | 08-27 | 82 | **Closed, no change shipped.** The UK's fee host was never budget-limited — it published a *form*, and a surplus goes to the largest host |
| — Count why a traveller goes unanswered | 08-24 | 63 | `RecallRecord.unreadable` had been filled from the crawl alone and went **silently empty** when the crawl left. First two corridors: 0 of 15 lost pages were `blocked` |
| 26. The nationality bonus rewards naming a country | 08-24 | 62 | **Closed with no code change.** Four fixes, four disproofs — including one implemented and reverted when the suite caught it. Cost of leaving it: 0.27 shortlist places |
| 25. Get the answering page into the shortlist | 08-24 | 61 | The reservation was three per role and the answer was 5th. Five per role, budget 35 — **the UK went 0/8 → 4/4**. Depth and budget only work together |
| 24. Say "the answer is behind a tool we cannot drive" | 08-24 | 59, 60 | Widened the same day: a questionnaire is an answer **for every role**, not a blockade. Also declines URL-construction, with measurements |
| 3. Measure the top 20 corridors against a bar set in advance | 08-24 | 58 | It passes, marginally — and the sample is five destinations replicated four times, not twenty corridors. Found the wizard, not blocks, as the largest limit |
| 23. Give `visa_decision` its floor back | 08-24 | 56 | **The proposal was wrong.** Removing the guard would score 12–58% of a country's pages for the decision; the real defect was the vocabulary not recognising an answer |
| 15. Re-run the six verified corridors | 08-23 | 55 | Reporting held; **qualification** broke. Removing the crawl cost the blocked-authority exception, which nothing was testing |
| 22. Route the request path through the corpus, drop the crawl | 08-23 | 49–53 | 2–5× faster, crawl at 0.0s — and the slowness was never scoring, it was `wrong_country`, 33× |
| — Find out whether Canada's page was ranked out or never found | 08-21 | 43 | Never found. "Ranked out" and "never found" had looked identical, so every run now writes a recall log |
| — Stop the adjudicator's excerpt cutting the answer off | 08-21 | 42 | A flat 6,000-character head made truncation the decider, and which travellers got an answer depended on the alphabet |
| — Move "who to believe" out of the request path | 08-18 | 34, 38 | Reviewing the generated registry found what running it could not; twelve countries needed a human override |
| — Read and honour `robots.txt` | 08-18 | 36 | The stdlib parser was inert, and only a live probe showed it. A skipped page is its own outcome, never "nothing found" |
| — Commit the 51-country trust-rule test | 08-18 | 33 | The gap is the **governmental** half, not the TLD half — the opposite of what these files had said for a week |
| — Narrow what a block may hand over | 08-18 | 32 | A `403` on a footer link could make a decision "unverifiable"; the refusal discipline was leaking |
| — Delete three things | 08-18 | 29, 30 | LangGraph declined outright; `conflicts` deleted by entry 6's own rule |
| — Make a failed adjudication refuse | 08-18 | 31 | Falling back to the heuristic turns an outage into a confident wrong answer — amends entry 16 |
| — Stop `withheld_domains` telling a reviewer something false | 08-18 | 33 | Italy's real foreign ministry was declined with the same words a commercial agency got |
| — Find out why a corridor refuses on a domain it can now read | 08-18 | 39 | The rule was not the only thing wrong |

## Smaller things

**`coverage` reports the EU store as a country nobody has built.** It lists every file in
`var/corpus/`, the registry does not know `EU` (entry 201), and the report says "no corpus at all
for EU — a job nobody has run", which is false. Skip a union's store the way the two corpus tests
now do (entry 204).

**Egypt `BD/SA` credits its decision 1 run in 3 on a byte-identical roles packet (entry 204).** The
portal's disclaimer says a visa is required before entry; the model refuses when it notices
Bangladesh is off the e-Visa list. Whether rule 8g or the roles prompt should settle that is a
prompt question — measure it with `replay_roles.py` on the captured packet before changing anything.

**`canonicalise_url` drops a trailing slash before a query string, and some servers care.** Found on
EUR-Lex (entry 201): `…/TXT/HTML/?uri=…` is the regulation, `…/TXT/HTML?uri=…` is "Page Not Found".
Every crawled link goes through it, so a store may hold addresses that 404 where the page linked
works. Unmeasured: count stored addresses with a query whose path had a slash (the raw `href` is not
kept, so this needs a crawl), and change it only with a rebuild, since it changes stored addresses.

**A failed model call is told to the traveller as a missing page.** When both role-adjudication
attempts fail (`adjudication_failed`), the refusal reads *"no page could be confirmed as the visa
decision, document checklist"* — true, and it hides that a model call failed. Seen on 2026-09-24
when Personas answered HTTP 500 for two minutes (entry 198). Say that the check could not be run and
that trying again may answer.

**A per-host fair share treats unequal hosts equally.** Moved here from item 48, closed
2026-09-15; unmeasured, and it changes what a build spends, so it needs its own rebuild. Thailand opened 1,041 pages across 63
hosts and the top hosts each got **41 or 42** — Uthai Thani province, population ~330,000, took the
same share as the national immigration service. 31 of those 63 hosts are provincial offices, so
Thailand's national guidance was diluted 31-fold: **44 pages for `www.immigration.go.th`, 3 for
TDAC, 2,615 recorded for the provinces.** The provincial sites are WordPress installations whose
category and archive pages present an effectively unbounded link graph. **The crawler is not being
greedy; it is being fair between things that are not equal.**

**A `TypeError` from the model call reports itself as bad model output.** Both providers wrap
`ainvoke` in `except (ValidationError, ValueError, TypeError)` and raise *"The model returned invalid
structured output"*. `with_structured_output(strict=True)` parses inside `ainvoke`, so catching
`ValidationError` there is right — but a `TypeError` from the *call* (a wrong keyword, a bad
argument) is not the model returning anything, and it is reported as though it were. Found on
2026-09-07 when adding `config={"callbacks": ...}` to both calls: a test fake whose `ainvoke` refused
the new keyword failed with a sentence about model output. The fix is to separate the invoke from the
parse, and it is not done here because it changes error handling on the path that decides what a
traveller is told, which deserves its own change rather than a footnote to a costing exercise.

**Sweden's ranking is unexplained, and entry 126 did not explain it.** Carried over from item 1,
which was otherwise finished on 2026-09-02. Sweden reads `migrationsverket.se`, fills
`general_entry`, and neither widening the shortlist window nor correcting its domain moved the visa
decision or the checklist. Its `visiting-sweden-for-up-to-90-days-entry-visa` page slipped from
104th to 111th for `application_route` at an **unchanged** score of 5.6, passed by seven
`british-citizens` pages that gained 40 — so the page was never scoring on anything, which is a
symptom rather than a regression, and at 104 deep it is outside any selection budget either way. It
has never been traced the way the Netherlands was, and it should be before anything is changed on
its account.


**Cyprus names `mip.gov.cy`, which does not resolve; `www.mip.gov.cy` does.** Found 2026-08-30,
entry 116. Cyprus's corpus is 612 of 620 entries on `www.gov.cy`, and its Ministry of Interior — the
department that actually issues Cypriot visas — contributed five. The build reported `mip.gov.cy` as
`unreachable [Errno 8] nodename nor servname provided`, while `www.mip.gov.cy` was reached and gave
those five entries, so trust already covers the subdomain and only the seeding of the bare host
failed. Whether naming the `www` host in `authority_domains.yaml` would actually seed more is
**unmeasured** — seeds come from search results rather than from the domain list — so measure before
editing. This is the same shape as entry 113's fix but not the same defect: nothing fails closed
here, it is coverage.

**Ireland reports one dead host two different ways.** Found 2026-08-30. `inis.gov.ie` is the
decommissioned predecessor of `irishimmigration.ie`, which carries 2,080 of Ireland's 2,107 entries.
The corpus build recorded it as `disallowed — its robots.txt is larger than the size limit for a
crawl policy`; a direct fetch under the project's own TLS context gets `CERTIFICATE_VERIFY_FAILED`.
Both are honest about what that client saw and neither costs an answer, so this is cosmetic — but
two incompatible reasons for one host is the kind of thing that wastes a session later.


**Germany fills `document_checklist` for two travellers and not for a third.** Found 2026-08-29,
entry 112. `uk.diplo.de/…/what-documents-do-i-need-for-a-c-visa` answers it for `IN/GB` and a Manila
page answers it for `PH/PH`, but `germany/NG/NG` leaves it unidentified even though
`nigeria.diplo.de` is in the corpus and answers that corridor's `visa_decision`. So the mission is
reachable and the checklist page under it either is not held or is not being selected — the two have
different fixes and nobody has looked yet. It is the cleanest per-traveller gap the third-traveller
run surfaced.


**`travel.state.gov` stores nothing, and rebuilding with the render budget did not change that.**
Entries 106 and 108. **Tested 2026-08-29**: the US corpus predated the render fix, so it was rebuilt
with the same 400-render budget that took France's portal 12 → 104 readable and Sweden's
`government.se` 0 → 863. `travel.state.gov` still holds **zero** stored pages — 76 entries, 73 never
opened, 3 unreadable after `CHALLENGE_FAILURES_PER_HOST` gave up. **The challenge is not answerable
by our renderer**, which makes the United States' five open slots a ceiling rather than a backlog.
Entry 18 forbids working around it. The only readable route is the partial `adoption.state.gov`
mirror (entry 87), and leaning on a mirror deliberately would be its own decision. Original
diagnosis follows.

**How it was found.** Entry 106. The corpus holds **70** of its pages — 67 never opened, 3 marked *"it asked this client to
prove it is a browser (HTTP 403), and that challenge could not be answered here"* — and the text index
holds **zero** from it, against 24 from the `adoption.state.gov` mirror that entry 87 found publishes
the same tree. All five remaining US role gaps are this one cause. Entry 92 counted the US at 19
unanswered challenges and predicted little from fixing it, on the grounds that `egov.uscis.gov` and
`ceac.state.gov` are application portals — **it was looking at the wrong host.** Entry 41 permits
answering a challenge, so trying is allowed; whether the renderer can answer this one is untested and
`CHALLENGE_FAILURES_PER_HOST` gives up after three. A US corpus rebuild is the experiment, and the
honest prior is that it may simply not be answerable.


**A delegated checklist counts as `open` in the coverage metric, and the plan already hands the
traveller its link.** Raised by the project owner 2026-08-29. `coverage` half one reports four
columns — answered by a page, settled by an official tool, does not arise, open — and a role the
authority contracted out falls into `open`, even though `delegated_services` puts the URL in front
of the traveller exactly as `official_tools` does. **This is entry 93's defect one instance later**:
that entry gave tools their own column because "the product has called it resolved since entry 63;
only the metric disagreed", and the same sentence is true of delegates since entry 89. A fifth
column, counted apart and never added into `held` — a company's page is not citable and
`validate_absent_checklist` still forbids a requirement behind one. It would change the Netherlands
most, which holds 236 delegations.


**~~Singapore's hand-written configuration is India-specific~~ — promoted to item 52 on
2026-09-14 and done the same day (entry 149).** Japan had the same shape, and the web app served
both from those pages rather than from discovery.

**`www.ph.emb-japan.go.jp` answers 404, twice.** Seen on both `japan/PH/PH` runs on 2026-08-28, so
it is a stable fact about that host rather than a transient. Japan's Manila embassy is exactly where
a Filipino traveller's guidance would be, and `japan/PH/PH` still scores 5/5 without it. Worth a
check that the address in the corpus is stale rather than the host being gone.


**25 recall logs carry no cause, and only a re-run fills them in.** Entry 63 added
`RecallRecord.cause`, and the logs from the twenty-corridor measurement predate it. They cannot be
repaired by reading their `outcome` line — a corridor that refused for want of a visa decision and one
that resolved by handing over the questionnaire stating it wrote the same sentence, which is the
conflation the field exists to end. `visa-discover audit` reports them as unrecorded rather than
bucketing them. Re-running those corridors is quota, not work — fold it into the next measurement
that needs live runs rather than spending the quota on its own.

**A sweep has no way to notice that every corridor is failing for the same non-country reason.**
Found 2026-08-25, entry 70. The OpenAI account ran out of credit mid-way through stage 2 and the next
sixteen corridors each searched their domains, crawled, built a shortlist, then refused with
`role adjudication failed on all 2 attempts`. **The resolver was right** — entry 31 forbids the
heuristic standing in — but sixteen corridors' worth of search quota went on runs that could not have
answered, and the run set now holds eight countries that look measured and are not. The fix belongs to
whatever drives a sweep, not to the resolver: stop after N consecutive `adjudication_failed`, and say
which provider said what. Related: `429 credit_balance_exhausted` and a genuine model-side blip are
indistinguishable in the note the corridor prints, which is the same conflation the `402` item below
describes for search.

**All three search defects recorded here are fixed — DECISIONS entry 74, 2026-08-25.** The provider
now paces itself at 1.3s from one lock and one clock, so `search_all`'s concurrency cannot outrun it;
a `402` is classified from `error.meta.current_spend` against `usage_limit` into `SearchQuotaExhausted`
or `SearchThrottled` rather than reported as one thing; and a search outage falls back to the stored
corpus where one exists, recorded on a typed `ran_without_search` field, said plainly in the notes,
and **never stored for reuse**. With no corpus the refusal still stands, because *we could not look*
must never become *there is nothing to find*.

Confirmed live against a genuinely capped account: all ten corpus countries resolved or handed over a
tool where every one of them previously raised. Canada answered in 31.7s from 2,450 stored pages.

**What is still open here**: search remains required for the 43 countries with no corpus, and taking
it out of the request path *by design* was item 19's question, and it is settled: search stays on
every corridor (entries 159 and 173).

**Settled in part, 2026-08-24 — DECISIONS entry 57 moved the meaning question to the model, and left
the ranking with the heuristic.** What follows is the evidence that produced that split, kept because
the ranking half is still open.
Measured across the six corridors: of the **18** distinct pages the model chose, **5 ranked outside the
25 places** by heuristic score — 27th, 31st, 35th, 57th and **101st** — and **every one was admitted by
the top-3-per-role reservation**, not by its rank. So the ranking is not what finds the answers; the
structural reservations and the generous window are (which is also what entry 40 measured when 10 → 25
places bought more than every scoring rule in the file).

What that does **not** license is deleting the heuristic. It is a *recall gate*, and something has to
cut 2,455 candidates down to what a model can read — reading them all is thousands of fetches and
~1.9M tokens per corridor. The honest framing is that it has two jobs and does them very differently:

| job | how it does | note |
| --- | --- | --- |
| reject obvious non-guidance | well | archived paths, site furniture, wrong audience, wrong country — cheap and deterministic |
| **rank what survives** | **poorly** | 5 of 18 answers outside the window; reservations rescue them |
| **judge what a page means** | **badly, and it should not be doing this** | `_decision_blocking` asks "could this page have held the decision?" by keyword, on a page **nobody read** — and that is what item 23 had to patch |

**The third row is now done** (entry 57): a blocked page has a URL and an anchor text and nothing
else, so asking a model about *that* is a small call over metadata rather than a page read, and it
measurably discriminates where keywords could not — France now qualifies its UK and India pages and
rejects its FAQ and application form.

**The second row is still open, and the arguments against changing it are strong.** Entry 31 makes
every model call another way for a corridor to refuse; entries 44–53 spent four sessions making the
candidate set *deterministic*, and a model in front of the shortlist would reintroduce variance
exactly where it was removed; and something must still cut ~2,455 candidates to what a model can read.
Entry 40's answer — a wider window rather than a better ranker — has never been retested since the
corpus made the pool six times larger. **Try 25 → 40 places and measure before trying anything
cleverer.**

**The corpus crawl's page budget is tuned to Canada and does not generalise.** `DEFAULT_CORPUS_PAGES`
is 1,200, chosen because Canada produced 203 seeds and a 200-page budget meant the crawl never left
them. Measured 2026-08-23 across six countries, three still fired `depth_is_exercised`: Japan 272
seeds → 9% beyond depth 1, France 176 → 6%, Singapore 295 → 3%. The budget should be derived from the
seed count rather than fixed — the flag already reports the failure, so the data to calibrate it is
being printed and ignored.

**~~A corpus build loses everything to one failed search query~~ — fixed 2026-09-15, DECISIONS entry
162.** A build now goes on without a failed query and names it in its output. An account out of
credit, or every query failing, still stops the build. Corridors are unchanged.

**`CorpusEntry` holds one `link_text`/`heading` per URL, and pages are linked from many sections.**
Sweden's visa-decision page is stored under the heading *"I will be studying in Sweden for less than
three months"*, which is off-scope vocabulary for a tourism corridor, because that is the section the
offline crawl happened to follow. So the store can attach one traveller's context to a page every
traveller needs. Keeping the best-scoring anchor, or several, would fix it; entry 55.


- **A footer link inherits the heading of whatever came above it.** `extract_links` assigns each link the
  last heading it has seen, and footer links sit below everything, so France's legal notice was scored
  against a news article's heading about visa requirements (entry 26). The boilerplate veto handles the
  pages this was observed on; the inheritance itself is still wrong and will quietly inflate any other
  footer link. Telling a footer from markup is the hard part, so this is recorded rather than fixed.
- **A plan can leak an internal field name into traveller-facing text.** The US plan's first unresolved
  question reads "no official application-document checklist was published in the configured
  `application_document_source_ids`" — the model repeating a key from the research packet. A prompt matter
  rather than a code one.
- **A reserved shortlist place guarantees a domain, not a page.** Entry 22's floor reserves each domain's
  best *link-scored* candidate, so the US mission's reserved place went to
  `in.usembassy.gov/scheduling-immigrant-visas-appointments` — right post, wrong visa class — rather than
  `/visas/`. The fix is in mission scoring, not the floor: `mission_affinity`'s bonus applies only to
  `document_checklist` and `application_route`, and only when those roles already scored.
- **`_mission_domains` returns `[]` for every automatically discovered destination.** It reads
  `destination.sources`, and `AutomaticDestinationService._base_config` builds a `DestinationConfig` with
  none — so the `on_mission_host` bonus never fires in the request path at all. Broader than known problem
  13, which describes only Brazil's path-based case. Mission detection survives there solely through
  `mission_affinity`'s host-label check.
- **The corridor's 40-page crawl budget is spent entirely at depth 0.** Seeds enter the frontier at
  priority `-1000.0`, so every seed is popped before any child, and twelve corridor queries at eight
  results each produce well over 40 unique seeds. Depth-1 links still become candidates without being
  fetched, so the loss is depth-2 discovery — which is where Japan's checklist was found. A per-domain
  **seed** cap would restore it without lowering `maximum_pages`, which must not be lowered. See also item 10,
  the sitemaps one, which may be the better answer.
  **And item 18 (entry 44) makes this moot for a populated country**, because an offline job has no
  latency budget to spend — Canada's answering page was reachable at depth 1, and the ones still lost are
  deeper. Fix the seed cap anyway and fix it *separately*: it still governs every country the corpus has
  not reached, and doing both as one change would hide which of them bought the recall.
- **Nothing validates `countries.yaml` against a `tlds` entry that widens trust.** Adding `gov` to a
  country's `tlds` would change what is trusted with no review of the rule itself. Bounded now by the cap
  and the corroboration bar (entry 22), but the data is still where a mistake would not be caught. `tests/test_trust_coverage.py`
  is the natural place to add a guard.
- **Missions named by city are still unrecognised** — Singapore's `london.mfa.gov.sg`. Folded into the
  ranking work: path-based mission detection has to solve the same problem, since the residence country is
  not always a host label. Add city names to `countries.yaml` beside `host_labels`.
- **Cache invalidation on rule changes.** After changing what counts as usable, cached entries still serve
  the old result until the TTL expires. This cost real debugging time — a fix appeared not to work until
  `var/cache/` was cleared. Consider keying entries by a rules version.
- **`is_bare_public_suffix` is a heuristic**, not a real public suffix list. It correctly rejects `gov.sg`,
  `gov.uk`, `go.jp`, `gouv.fr` and `co.uk` while allowing `usa.gov` and `service.gov.uk`, but review it as
  countries are added — and note it will need `gv` and `gub` per item 2.
- **Singapore's VFS page is a 403, not a JavaScript problem.** It was recorded as client-rendered; it is
  bot-blocked at the HTTP layer, so rendering never applies (the render only runs after a `200` whose text
  was thin).
- **`xuatnhapcanh.gov.vn/en` answers `200` with `location: http://localhost:4000/vi`** and an empty body: a
  misconfigured Next.js i18n redirect. Browsers ignore `Location` on a `200`, so rendering does not fix it
  either. The site root works. Possibly worth reporting to the authority; nothing to fix here.
- **The eVisa "Go here" link for Japan** points at an information page that is itself a PDF shell, so
  clicking it downloads a PDF rather than opening the application portal. The plan's own unresolved
  questions flag this, so it is visible rather than silently wrong.
- **Rendering has earned zero live corridors.** It is off in committed config, contained behind a protocol,
  and Vietnam still refuses with it on (for non-rendering reasons). Keep it, but build nothing downstream
  on it until a corridor actually needs it. **If it is ever measured, do it on code from 2026-08-18 or
  later:** before then the render allowances were process-lifetime rather than per-run, so a long-running
  server stopped rendering after 17 pages and reported the pages it skipped as unreadable (entry 37). Any
  earlier measurement of rendering's value would have been reading that, not reading rendering.
