# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

**How to read this file.** **Now** is what to pick up, in the order written; **Next up** follows it;
**Later** is real but not urgent; **Done** keeps finished work because what building it found is usually
why the item after it exists; **Smaller things** are one-paragraph defects with no owner yet.

**The goal this list serves.** A country is built offline — corpus plus page-text index — and a
corridor answers from that store. Live search is acceptable where genuinely unavoidable, not as the
ordinary source of recall. **Item 19 is that goal as a work item**; items 30 and 33 fed it, item 34
is done (entry 87), and entry 82 measured how close it already is: 18 of 30 corridors had zero corpus
misses, and none of the 67 misses were on a host the corpus lacks.

**Where the list stands, 2026-08-27.** The three items that used to gate everything are finished and
confirmed by live runs — **item 22** (the corpus replaces the crawl, entries 49–53), **item 23** (the
vocabulary could not recognise a page that *states* the visa answer, entry 56) and **item 3** (the
twenty-corridor measurement, entry 58, which passed marginally).

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
finding: the same stores answer **47 of 60 roles for one traveller and 36 of 60 for the other**.
Building it exposed a defect in the grader — see item 38, which is now the first thing to do.

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
win is search recall, which nobody has measured** — see item 19 and known problem 13.

**Item 5's challenge half is done** (entry 75): `challenged` is its own outcome, detected from headers
**and body**, answered by the renderer under our own user agent, and `render_mode` is now `on_demand`.
**Cyprus resolves.** Greece's genuine refusal is untouched. Two residuals worth knowing: Slovakia
challenges every page and spends its render budget before reaching the decision, and Lithuania's
challenge fingerprints past the user agent — recorded as `challenged`, and not worked around.

**Item 30's stage 2 is finished, and stage 3 is what is left of it.** All 41 never-run destinations
ran on 2026-08-25 — 103 corridors — and every one resolved or refused for a verified reason; 32 of 41
answered at least one passport. The sweep also found two defects no five-country corridor could
(entry 71) and closed known problem 27 with a measurement. **What remains under item 30 is building
43 corpora**, which is the expensive stage: ~1,792 searches. Fix the search rate limiter first — see
*Smaller things*.

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
researchable, and that is stage 1 of three. **Item 30 is now first, and no further country is added
until batch 1 clears all three stages**: reachable, resolves, fast.

**Batch 1 is all 53 reachable countries**, not the fourteen — those were catching up to the rest, and
counting the rest the same way found the real gap: **41 of the 53 have never had a corridor run against
them**, which is not the same as failing. 43 have no corpus. **Accuracy is verified by the project owner
outside this repository** and is deliberately not a stage; do not build a correctness grader here
without asking.

The method for a country the rule cannot confirm is settled and cheap: ask Wikidata about the *domain* —
`haswbstatement:P856=https://<domain>/` — and check `P17` against the country. It recovered 6 of the 8
refusals in batch 1 and guesses no names. TLS certificates managed only 2 of 8 here against entry 66's
9 of 16, because that measured each country's known-correct domain while this measures whatever search
found.

**The rest of the sweep waits behind item 30.** 143 countries have no row at all — 4 searches each.
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
19 are the corpus work item 22 grew out of, and 19 is now half done — the crawl has gone, search has
not.

Status: `next` · `soon` · `later` — the label on each heading matches the section it sits in, so the two
can never disagree. There is no **Blocked** section at the moment; give one its own section again if an
item acquires a dependency it cannot clear itself.

**Every open item has a number, and numbering is append-only** so that the cross-references in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) stay valid. The numbers are names, not an order: **the section
decides the order**, and a gap in the sequence means an item was finished or dropped. Finished items
keep no number — a number is a handle for pointing at work still to be done — and *Smaller things* are
one-paragraph defects rather than items.

| | | |
| --- | --- | --- |
| **Now** | 38. Re-run the twenty oracle corridors so a selector can be graded again | `next` |
|  | 39. Stop asking five more questions once the answer is "no visa required" | `next` |
|  | 40. Let curation fetch one page the index does not hold | `next` |
|  | 5b. Answer France's challenge in the corpus build, not only the request path | `next` |
|  | 35. Finish the Netherlands, then roll the family reservation across the other nine | `next` |
|  | 30. Perfect batch 1 before adding a single further country | `next` |
|  | 2. Amend the trust rule for governments with no marker, and for Schengen | `next` |
|  | 17. Decide what a corridor that flips between runs should do | `next` |
|  | 18. Build the offline corpus job, and run it on more destinations | `next` |
|  | 19. Take search out of the request path too | `next` |
|  | 5. Answer the challenge, honour every `robots.txt`, and get a checklist out of France | `next` |
|  | 1. Fix the post-over-nationality weighting, and find out why Sweden does not move | `next` |
| **Next up** | 4. Decide the client-side retrieval question | `soon` |
|  | 7. Put it somewhere others can open it aka deployment | `soon` |
|  | 8. Confirm a blocked authority actually reads usefully | `soon` |
|  | 9. Tell "no checklist exists" apart from "we failed to find it" | `soon` |
|  | 20. Make the stores substrate-swappable and durable | `soon` |
|  | 21. Fill the three provenance gaps | `soon` |
| **Later** | 27. Decide whether a hosted scraping service may be used, and only for corpus discovery | `later` |
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
documentation said it was — the corrections table in [CLAUDE.md](CLAUDE.md) has seventy-six rows and every
one cost a session. **Prefer running a corridor to reading a code path**, and when an item below
proposes a fix, measure the proposal before implementing it. Several items here were written from a
careful reading and were wrong.

---

## Now — pick these up in this order

### 37. ~~Build the gate that says whether a country's corpus is good enough~~ — `done, entry 90`

**Done 2026-08-28.** `visa-discover coverage` is committed and tested: offline, no model, no search,
reading only `var/corpus/`, `var/pagetext/` and the committed oracle. Two halves, printed apart and
never added, and **the verdict is computed from half two alone** so the 100% cannot outvote it.

- **Half one, the regression check:** 47 of 47 answerable roles already in the corpus. Frozen by a
  test. It compares on `canonical_key` — the first run read 46 of 47 and the miss was
  `www.gdrfad.gov.ae` against `gdrfad.gov.ae`, the same page.
- **Half two, the point:** every per-traveller family the corpus holds, with members held, members
  opened, gateway or leaf, how many the text index can read, and whether any single page lists
  enough siblings for the crawl's reservation to see it.

**One verdict per country, and two of the three this item predicted came out as written.** Six of
the ten read *no per-traveller dimension* (AE, CA, DE, FR, SE, US; JP too). Singapore reads *bounded
by the authority* at 32 of 198, which is a **pass** — the missing 166 are behind a selector.

**The Netherlands reads `incomplete`, not `covered`.** Its largest gateway family is 71 of 184
opened, and three complete families have never been opened at all: `making-appointment/{}` at 188
held, `caribbean-visa/short-stay/apply-{}` at 185, `passport-id-card/abroad/apply-{}` at 184. Entry
88 proved the mechanism on one country and did not finish the country — that is item 35, now with a
number on it.

**And the United Kingdom has a per-traveller family, where entry 88 counted none.** Corpus-wide the
counts are **NL 13, SG 2, GB 1** against entry 88's NL 9, SG 1, GB 0 — because `_queue` groups the
links found on *one page* and this groups across the store. Per-page grouping reproduces entry 88's
counts exactly. The extra British family is `visa-fees.homeoffice.gov.uk/y?previous-answer={}`, entry
82's fee wall showing up as a family for the first time, 14 of 198 held and none opened. Each family
is marked `listed` or `spread` for which grouping sees it.

**Use it as the promotion rule for stage 3** (entry 68): a country is not stage 3 until this command
reports *no per-traveller dimension*, *covered*, or *bounded by the authority*. `incomplete` means
rebuild first. Exit code 1 on `incomplete` or a missing known answer, so it can gate a script.

**What it deliberately does not answer.** Whether the *corridor* then finds what the store holds —
that is `visa-discover selection-recall`, entry 87, and merging the two would hide which half
failed. A complete, under-opened family that no page lists is printed as `spread` and pushes the
verdict neither way; no such family exists in the ten corpora, so the case is documented rather than
machined for.


### 34. ~~Build an oracle that neither selector helped make~~ — `done, entry 87`

**Done 2026-08-27.** `oracle/selection_oracle.yaml` names, by hand, the page answering each role for
the ten corpus corridors, built from each corridor's whole contention set rather than from what
either arm fetched. `visa-discover selection-recall` grades any directory of recall logs against it
and prints entries 85–86's joint oracle beside it, so the bias is a number on every run rather than
a sentence in an entry.

**Entry 86's +41 points is +30**, and the direction held. Against the heuristic at its shipped 35
places the margin is **+9 where the joint oracle said +7** — the bias ran both ways. The recommended
option (2) was the right one for a reason neither option statement gave: a fetch-everything oracle
would have inherited the alias bug that turned out to be the joint oracle's sharpest fault, because
it would still have been a set of URLs somebody fetched.

**What it left open, in the order it matters.**

- **Thirteen of the sixty roles have no answer anyone could read**, and that is where the remaining
  coverage lives — France's four behind the Visa Wizard (item 5), the Netherlands' UK consular fee
  page holding no text, the United States' Visa Waiver country list not extracting.
- **Still one nationality and one residence, `IN/GB`, across all ten.** That is now the largest
  untested dimension in the whole harness, and item 48's nationality question is the same question.
- **The heuristic at 35 places reaches 91% against the model's 100%**, so the shipped comparison is
  a cost argument — 3.1× the fetches — at least as much as a recall one. Any future selector work
  should quote both.


### 38. Re-run the twenty oracle corridors so a selector can be graded again — `next`, **start here**

**Why:** entry 91 widened the oracle to a second traveller and, in doing so, found that
`arms_from_logs` could not tell a model run from a heuristic one — a run's fetched URLs are read as
*the model's picks* and nothing in `RecallRecord` said which selector fetched them. Six of the new
traveller's logs predate entry 85, so grading them put the heuristic into the arm labelled `model`
and moved the printed figure from 100% to 92% with nothing saying why.

`RecallRecord.selector` now records it and an unattributable log is **not graded**, which is
`cause`'s rule from entry 63 applied to a second field. **The cost is that `selection-recall` grades
nothing today.** Entry 87's numbers stand as recorded and are not currently reproducible from disk.

**Do:** run the ten `IN/GB` corridors and the ten `PH/PH` ones with `discovery_selector: model`, then
`visa-discover selection-recall`. Two things come out of it and only the first is a repeat:

- entry 87's 100% / 91% / 70%, reproduced from logs that say who chose;
- **the first selector number for a second traveller**, which nothing has ever measured. Expect it to
  be worse: the `PH/PH` half of the fixture answers 36 of 60 roles against 47 of 60, so there is less
  to find and the pages that answer are thinner.

Twenty corridors of search and model quota. Cheap, and it is the only thing standing between the
widened oracle and a number.

**Careful:** clear nothing. `var/corpus/` and `var/pagetext/` are stores; `var/recall/` is where the
output lands and the old logs are harmless now that they are refused rather than mis-graded.


### 39. Stop asking five more questions once the answer is "no visa required" — `next`

**Why:** Singapore's `PH/PH` row records `document_checklist`, `application_route` and `fees` as
unanswered, and every one of them is unanswered **because the corridor resolved correctly**. A
Filipino needs no visa for Singapore, so there is no application to bring documents to, no route to
take and no fee to pay. Asking anyway turns a complete, correct answer into a 2-of-6 result in every
metric this project has — entry 58's checklist rate included, and known problem 26 already warns that
those numbers measure *answering* rather than being right.

**What a complete answer looks like when the decision is "no visa":** the decision, the official page
that states it, and whatever entry conditions do still bind — Singapore's SG Arrival Card, an onward
ticket, a passport validity rule. That is `visa_decision` and `general_entry`, and the other four
roles are **not applicable** rather than missing.

**Do:** give a role a third outcome beside filled and unfilled — *not applicable, because the visa
decision is no*. It has to be derived from the adjudicated decision rather than guessed, and it must
never fire when `visa_decision` is unverified or handed over as a tool: "we could not confirm whether
you need a visa" can never suppress the checklist. Then teach the corridor's own reporting, the
interface's empty-checklist panel (which already names three reasons — entry 89) and
`visa-discover coverage` to count those roles apart from the ones nobody could answer.

**Careful, and this is the whole risk:** a wrong "no visa required" that then suppresses five
questions is worse than a wrong one that leaves them visible, because the traveller has nothing left
to notice the error with. So this may only key on a `visa_decision` that is *stated by a source* —
never on a tool, never on a blocked page, never on `decision_is_unverified`.

**Also update the oracle**, whose Singapore rows currently record those three as `unanswered` with a
reason. They want a fourth key — `not_applicable` — or the fixture will keep scoring a correct
corridor as a thin one.


### 40. Let curation fetch one page the index does not hold — `next`

**Why:** entry 91. Sweden's `visa_decision` is on `government.se` with no stored text, and the
Netherlands' Philippine tourism checklist is named from its address alone. Both are recorded
`unverifiable` or `title_only`, and **the product would simply fetch them** — the index is a ranking
store, not the limit on what can be read. So the oracle understates what is answerable, which is
known problem 30 read from the other side: it is a limit of the *curation tool*, not of the corpus.

**Do:** an opt-in on `visa-discover contention` that fetches **one named candidate** through
`LiveSourceFetcher` — so domain trust, `robots.txt`, the TLS rules and the freshness ceiling all
apply exactly as they do in a corridor — and prints it for the curator. Offline stays the default,
because the set a row is curated against has to be reproducible next month.

**Careful:** this is a curation aid and must not become a second retrieval path. It reads one URL a
person typed, never a set; it never writes to the corpus or the index; and a page it fetches is still
fetched again by the product before a word of it reaches a traveller.


### 5b. Answer France's challenge in the *corpus build*, not only the request path — `next`

**Why:** entry 91 measured France at **18 readable candidates of 201**, which is the worst text
coverage in the fixture and the reason France answers one role for either traveller. Entry 41 settled
the principle — a Cloudflare challenge is not a refusal, it states no policy, and answering it by
running the page's own JavaScript in our own renderer **under our own user agent** misrepresents
nothing — and entry 75 built it, taking `render_mode` to `on_demand` and recovering Cyprus.

**What was missed is that the corpus build does not do it.** The request path renders a challenged
page; the offline crawl that fills `var/corpus/` and `var/pagetext/` does not, so France's portal is
recorded as pages with no text and every later measurement inherits the gap.

**This is not a relaxation of anything** and must not be written as one. Spoofing a user agent,
retrying past a rate limit and rendering past a **refusal** all stay forbidden; `www.mfa.gr`'s Akamai
`403` and `urm.lt`'s unanswerable challenge are untouched. The line is entry 41's: did the authority
state anything.

**Do:** give the corpus crawler the renderer on the same terms the request path has it, with a
budget, and rebuild France. Then re-run `visa-discover coverage --country FR` and re-curate France's
two oracle rows, which are currently the fixture's weakest.


### 35. Finish the Netherlands, then roll the family reservation across the other nine — `next`

**The gate now says what to do, which it could not when this item was written** (item 37, entry 90).
`visa-discover coverage` reads:

```
NL  incomplete                  9 listed families, largest gateway 71/184 opened
SG  bounded by the authority    32/198 held, behind a selector — a pass, nothing to do
GB  bounded by the authority    14/198 held, the fee wizard — a pass, nothing to do
AE CA DE FR JP SE US            no per-traveller dimension — no-ops, confirmed rather than assumed
```

**So the first job is the Netherlands, not the other nine.** Entry 88 proved the mechanism and did
not finish the country: three *complete* families have never been opened at all —
`making-appointment/{}` at 188 held, `caribbean-visa/short-stay/apply-{}` at 185,
`passport-id-card/abroad/apply-{}` at 184 — and the schengen gateway sits at 39% opened. Whether the
three unopened ones are gateways or leaves is **unknown until one is opened**, which is the honest
state and the reason the verdict is `incomplete` rather than `covered`.

Rerun `visa-discover coverage --country NL` after the rebuild; the verdict is the acceptance test.

**Then the other nine, and the gate has already made six of them no-ops.** Rebuild and diff the
qualifying families, which is free to check offline before spending a crawl.

**Why:** entry 88. A corpus crawl reads 3–15% of what it records, and the page that answers a
*specific* traveller is almost always one hop below something it recorded and never opened. Proved
and fixed on the Netherlands: gateway pages read went 0 → 185, tourism checklists held 5 → 14, and
`netherlands/PH/PH` — a profile the store could not serve at all — now fills four of six roles from
the corpus with the crawl skipped.

**Nine countries are untested, and the gate makes most of them no-ops.** Families the *reservation*
can see — the crawler groups links found on one page — are **NL 9, SG 1, and zero for CA, JP and GB**
(AE, DE, FR, SE, US likewise). So the work is small. Counted across the whole store instead the
totals are NL 13, SG 2, GB 1, and the difference is a finding rather than a discrepancy: entry 90.

**Singapore is not the Netherlands, and this was checked rather than assumed (2026-08-28).** An
earlier draft of this item said to do it first because its per-nationality page fills five roles.
That was the wrong reason:

- Singapore's `visa-detail-page/{country}` is a **leaf**, not a gateway. Opening the 34 held yields
  two children in total, against the Dutch gateway's six apiece — and an unopened URL is already a
  usable candidate, so the 34 already work.
- Its coverage gap is a **form wall**, not a budget one. `ica.gov.sg/.../visa_requirements` yields
  **6 children, not 198**; the 34 held all came from mission pages (33 New Delhi, 1 Chennai). That
  is entry 82's UK fee table, and no reservation reaches the other 164.
- What a rebuild *would* buy is narrower and real: **only 4 of the 32 that group have stored text**
  (the gate's own count; two of the 34 carry country names the registry has no slug for), and stored
  text is what the model selector reads. It improves selection for other nationalities, not
  coverage. Worth doing, worth not overselling.
- **The thing that might actually help is invisible to this mechanism.** Sixteen mission
  `visa-information` pages are in the store and **none has ever been opened**. They sit on sixteen
  hosts and carry no country token, so they never group into a family. Whether any lists
  nationalities the way New Delhi's does is untested — London's, which has been read, does not.

So: rebuild the eight remaining countries and diff the qualifying families, which is free to check
offline before spending a crawl. Expect selection gains, not coverage, anywhere the authority
publishes its list behind a selector.

**Do not raise the share to reach further.** The Dutch ceiling is not the budget: of 185 gateway
pages read, 113 link nothing and 58 link only language forks, because for most residences the
Netherlands publishes its checklist on **VFS Global**. See item 36.


### 36. ~~Decide what to do about guidance published on a commercial contractor~~ — `done, entry 89`

**Done 2026-08-28.** Decided and built: named, never read, never believed. Trusting or crawling a
contractor was declined for reasons in entry 89; `config/service_providers.yaml` holds the reviewed
list, and the warrant is two independent things — an approved government page linked it **and** the
domain is on that list.

Proved on `netherlands/PK/PK`: `document_checklist` stays unfilled, so no requirement may be listed,
and the traveller is handed
`visa.vfsglobal.com/one-pager/netherlands/pakistan/english` with the government page that appointed
it. That corridor previously said nothing about documents at all.

**What it left open**, smallest first:

- **Nobody checks whether a delegate's URL still resolves.** A dead contractor link would be named
  as confidently as a live one. It is a link rather than a claim, which is why it did not block, but
  it is the obvious next defect. A `HEAD` against a page we may not read is arguably fine; argue it.
- **Only the Netherlands has recording on**, because only it has been rebuilt (item 35). The other
  nine hold no delegations and the feature is inert for them.
- **The interface wording is a design judgement, not a measurement.** Amber rather than the tools'
  green, the limit stated beside the link, and the empty-checklist panel now names which of three
  reasons applies. Nobody has watched a traveller read it.


### 30. Perfect batch 1 before adding a single further country — `next`

**Why:** entry 68. A batch is done at **three** stages, and having a registry row is only the first.
Adding breadth on top of untested depth turns a registry of 198 rows into 198 unverified claims.

**Batch 1 is every reachable country — all 53.** The fourteen entry 67 added were catching up to the
ones already in the registry, and counting those the same way is what found the real gap: **41 of the
53 have never had a single corridor run against them.** A row was never evidence that a country works.

| | stage | today |
| --- | --- | --- |
| 1 | Reachable — a confirmed authority domain | **53** |
| 2 | Resolves — a decision, or a refusal for a *correct* named reason | **53 of 53 — cleared 2026-08-25** |
| 3 | Fast — corpus-routed rather than crawling | **10 of 53** |

**Stage 2 is done. Stage 3 is the whole of what remains.** All 41 never-run destinations were run on
2026-08-25 — 103 corridors, two or three passports each, `--from` deliberately different from
`--nationality` — and every one either resolved or refused for a reason verified against what was
seen. Entry 70 has the table, the shapes and the nine that refuse every passport.

| | |
| --- | --- |
| resolved outright | 54 |
| decision handed over as a blocked page | 4 |
| decision handed over as a questionnaire | 4 |
| refused, nothing stated the visa decision | 41 |
| the run raised, or the model call failed | **0** |

- **Answered at least one passport (32):** AU, BE, BG, BR, CH, CN, CZ, EE, EG, ES, FI, GR, HR, HU, ID,
  IE, IT, KR, LU, LV, MT, MY, NZ, PH, PL, PT, SI, TH, TR, UY, VN, ZA
- **Refused every passport (7, down from 9):** DK, LT, MA, MX, RO, SA, SK. **Cyprus and India were
  recovered** the same day by the renderer (entry 75), India with all six roles. These seven pass
  stage 2 and are **not** the same as working — and **no corpus will fix them** (entry 76): every one
  fails at *retrieval*, so a corpus crawl meets the identical wall. Morocco was the one that looked
  like it needed `render_mode: on_demand`; it has it now and still returns too little readable text.
- **Corpus-routed (10):** AE, CA, DE, FR, GB, JP, NL, SE, SG, US. Everything else crawls.

**Accuracy is not a stage** — whether a decision is *correct* is verified by the project owner outside
this repository (entry 68). Do not build a truth set, a correctness grader or an accuracy metric here
without asking.

### Stage 2: run the 41, and **for every nationality**

**Batch 1 bounds the destination list, not nationality** (entry 69). Whatever passport a traveller
holds, a batch-1 destination must answer them. 53 × 198 is 10,494 corridors, so this is a question
about *mechanism*, not sample size.

**Classify each destination by how its authority publishes**, because that decides whether nationality
is a recall problem at all:

| shape | nationality risk |
| --- | --- |
| one page naming every nationality (a Schengen annex table) | **none** — find it once and the dimension is closed |
| a page per nationality (Canada's) | **the real risk** — recall must find the right one of ~200 |
| a questionnaire (`gov.uk/check-uk-visa`) | **none** — the tool is handed over whole and serves every passport |

So: two or three nationalities per destination to establish the shape, then **a handful of deliberately
awkward passports against the per-nationality destinations only** — chosen for demonyms that do not
resemble the country name.

**The known defect this was testing for is now measured, and the answer is "nothing"** (entry 70).
Over 59 recorded corridors, candidates matched on a demonym and *not* on the country's name took
**0.20 shortlist places per corridor**, and **not one of the twelve filled a role** — they are
approved-insurer lists, a Work Holiday notice and an embassy press release. **Do not write 184 demonym
lists on a recall argument.** Known problem 27 stays open only as a description; the cost attached to it
is now zero answers and ~0.2 wasted fetches.

**What the 41 found, and what it changes about the stages after this one** (entry 70):

- **There is a fourth shape: per diplomatic post**, keyed by where the traveller applies from rather
  than by their passport — `dirco.gov.za/uk`, `gov.pl/web/unitedkingdom`, `conslondra.esteri.it`. That
  closes nationality and **opens residence**, which is the same size. Nothing is queued for it yet, and
  it is the honest successor to the question entry 69 asked.
- **Three destinations pick the post by *nationality* instead**, which is the wrong page wherever the
  post governs: for an Indian passport resident in Great Britain, Australia, Brazil and Slovenia all
  answered from their New Delhi post. Known problem 9's residual on three new countries — **item 1**.
- **A page per nationality — entry 69's "the real risk" — was not the shape of a single one of the 41.**
  The awkward-passport runs it prescribed were never worth running; there was nothing to run them
  against.
- **The real nationality risk is search recall.** Belgium refused `IN/IN` and resolved `US/US` on the
  *same page*, which was never a candidate in the losing run — `corridor_queries` puts the
  nationality's name literally into one of three templates. Czechia's equivalent page came from the
  **crawl** and answered all three passports identically. So a one-page-names-all destination closes
  nationality only when the page is reached by crawl or corpus — which is a reason for stage 3 that
  entry 68's latency argument did not have.

What the codebase is answerable for is **resolve or refuse, and refuse for a reason true of what was
seen** — entries 33, 36 and 63. `visa-discover audit` buckets a run set by cause, so read it there
rather than by eye. Expect the causes to spread: some will be wrong-domain (below), some wizard-only
(entries 59–60), some `robots.txt`-blocked as Austria is.

**The two to watch are done, and they came out differently.** Reviewed rows are committed for `vm.ee`
(Wikidata Q6867006) and `mae.ro` (Q15628977), both confirmed by entry 67's exact-statement method.
**Estonia now resolves all three passports on `vm.ee`**, six of six roles for `IN/GB`. **Romania still
refuses**, but the row did its job: `mae.ro` and its missions are now reached, and the reason moved
from "the trusted set cannot hold the answer" to "every one of their `robots.txt` answers `503`, so
nothing was requested". Only the second is a fact about Romania.

**And they cost less to confirm than entry 67 implies**: the P856 statements are `http://www.vm.ee` and
`http://www.mae.ro`, with no trailing slash, so a lookup that tries only `https://<domain>/` finds
nothing and the domain reads as unconfirmable when it is not.

**Iceland and Liechtenstein are stage-1 failures and may stay that way.** `government.is`, `island.is`
and `llv.li` all sit under their own top-level domain and carry no governmental marker; no Wikidata
entity claims any as an official website, and all three serve DV certificates naming nobody. Nothing
was found, so nothing is asserted. Reopening them means finding evidence, not loosening a rule.

### Stage 3: corpora for the 43, and deliberately after stage 2

Entry 55 measured corpus-routing at **2.1×–5.2×** faster (Singapore 56.1s → 10.8s). 43 of the 53 have
no corpus, so they crawl on every request.

**This is the expensive stage by an order of magnitude: ~1,792 searches and up to 51,600 page fetches**
for the 43, against 4 searches for a registry row. Two reasons it comes second. A corpus built for a
country whose corridors do not resolve has unknown value — known problem 24 records how badly coverage
varies, Japan's holding 1 of its 6 role pages. And stage 2 tells us which countries are worth 42
searches each and which are refusing for a reason no corpus can fix.

**The search rate limiter this stage was waiting on is done** (entry 74): the provider paces itself at
1.3s and a `402` now says which kind it is. 1,792 searches still need a cap that allows them.

**Judge a corpus by its hit rate on role-filling pages, not by depth** (entry 77). The corpus is a
latency cache — both paths are supposed to find the right page, and the corpus exists so the live one
does not re-fetch for 50+ seconds. Measured on `japan/IN/GB` right after a rebuild: **3 of 5 role
pages came from the corpus**; the checklist and the route came from live search.

> **That 3-of-5 does not mean what it was read to mean (entry 78).** `found_by` records which
> *description* of a URL won a score comparison in `resolver.py`, not which store held the page —
> search and the corpus describe the same URL from different evidence and the higher score wins. Both
> pages attributed to search were **in the corpus already**: `visaonline.html` at depth 1, and the
> checklist PDF. Of 35 shortlisted candidates on that run, only **6** were genuinely absent from the
> corpus, three of them on post hosts. The corpus's problem was never that it lacked the page.

So before building 43, fix the two things that cause a miss:

1. ~~**Pages the crawl never reached on a host the corpus does hold.**~~ **Tried and it does not
   work.** Japan rebuilt at `--pages 5000`: entries 1,977 → 3,029, hosts 50 → 68, depth beyond 1
   from 7% to 36% — and the corpus hit rate on role pages went **3/5 to 2/4**. A bigger budget buys
   volume and depth, not the pages a corridor needs. Do **not** size stage 3 on this.
2. **Hosts lost at build time. Half built** — the build now **names** every host it got nothing from,
   with the typed outcome beside the reason, and Japan's rebuild named five. What it still cannot
   catch is a host that was never *seeded*: London was absent from the rebuild and absent from the
   lost list, because search's seed set varies between runs (known problem 19). Retrying named hosts
   on the next build is still unbuilt.

3. ~~**The structural one:** pages only a corridor-specific query surfaces can never be stored, and
   the document checklist is one.~~ **Wrong, and measured wrong (entry 78).** The checklist page
   `mofa.go.jp/files/000121327.pdf` **was in the corpus all along**. It could not be *found* there: the
   corpus stored `link_text="Single Entry Visas (PDF)"` and threw the body away, and from that anchor
   it scores 22.0 as **`visa_decision`** — the wrong role entirely, so no shortlist depth recovers it.
   From its own text it is the answer. `corpus_queries` staying traveller-free is still right and still
   entry 44's rule; it was not what lost the checklists.

4. **What actually lost them, now fixed** (entry 78): the body was discarded at `crawl._expand`, and
   two request-path gates decided what a corpus build ever read — `expansion_threshold = 10.0`, which
   **91% of Japan's entries never cleared**, and PDFs never being followed, which is **26%** of them.
   `discovery/page_text.py` keeps the text; the offline job drops the threshold and reads PDFs in a
   second pass. Japan rebuilt on the same budget: depth beyond 1 from 4% to ~50%, index 209 → 684
   pages, 17 → 94 PDFs.

Then build **one** country, run a corridor against it, and check how many role pages came back
`found_by="corpus"` before paying for the other 42.

### Done when

All 53 resolve, or refuse for a correct named reason, **for any nationality** — **done, 2026-08-25** —
and all 53 are corpus-routed, which is stage 3 and untouched. **Then** batch 2.

### 31. Rank a candidate by what the page says, not only by the link to it — `built, gated off, blocked on item 32`

> **Superseded by entry 81 — the regression below is withdrawn.** Six runs of identical code give
> 4, 4, 4, 4, 5 and 6 roles, so every A/B here sat inside the metric's noise. The pages that fill
> roles are shortlisted and fetched in every arm, making the lift recall-neutral; nothing shows it
> helps, so it stays off as the conservative default. **The next step is a measurement with no
> adjudicator in it: grade the shortlist, not the plan.**
>
> **And there is now a country where it could be tested.** The UK rebuild (entry 82) left a 1,598-page
> text index, and over a real corridor **85% of the candidates in contention have text** — against
> 13% for Japan. If entry 81 is right that the bar's denominator should be candidates that can
> actually be shortlisted rather than all of them, the United Kingdom is the first country above it.
>
> ~~**Measured 2026-08-26 and it regressed, so it is gated off (entry 80).**~~ Twelve runs on
> `japan/IN/GB`: corpus-only the lift gave 4/4/4 roles and lost `document_checklist` and `fees` every
> time, against 4/6/5 without it; search-up 3/5/5 against 4/5/5. It never helped. The cause is that
> only 115 of 860 candidates carried index text — 90% of `evisa.mofa.go.jp`, **0% of the UK post** —
> so the lift ranked pages by who had been crawled. `_text_scoring_is_fair` now requires the index to
> cover half a candidate set before it may rank it, and **no country is close**, so this is inert
> until item 32 lands. **Item 32 is therefore the prerequisite for this, not the follow-up.**
>
> **Built 2026-08-26 (entry 79), and the measurement below has now been taken.** Step 3b of
> `_resolve` scores every candidate whose text the index holds, before `_shortlist`; `text_scores`
> is its own field so stored text may lift a candidate and never sink one; `best_combined()`
> replaces `link_scores.best()` throughout the shortlist so a page reserved for its text cannot then
> be cut by an ordering blind to it. Live on `japan/IN/GB` with search up: **all six roles**, 115
> candidates ranked on text.
>
> **What is not done is the A/B.** One corpus-only run of each arm gave four roles either way, a
> different four — and the recall log says both contested pages were shortlisted *and fetched* in
> both arms, so the difference is adjudication variance (known problem 10), not ranking. The repeat
> runs stopped when the OpenAI account ran out of credit. **Three runs of each arm, over the ten
> corpus countries, is what settles it.**

**Why:** entry 78 built the index and stopped one step short of using it. `discovery/page_text.py`
holds the body text of 684 Japanese pages and nothing in the request path reads it. Every measurement
in that entry is offline; **the end-to-end claim — that a corpus-only run keeps its checklist — is
unmeasured.**

**What to build, and the shape matters.** Not "replace `score_link` with `score_body`". The top of
Japan's text ranking for `document_checklist` is Calgary and Houston consulate pages: real checklists,
for the wrong post. `score_body` takes a nationality and **no residence**, so it has none of
`mission_host_bonus` or `other_mission_penalty` — and entry 70 established that the post is the
dimension that actually varies. The link score knows about posts, depth and host kind; the body score
knows what the page *is*. So: keep `score_link` as the ranker, and add the body score for candidates
whose text is held, combining rather than replacing.

**The measurement that decides it** is the one entry 76 already ran: the ten corpus countries,
corpus-only, and whether Canada, Japan, Germany and the United States keep the checklist they lost.
Search does not need to be down to run it — the resolver can be asked for a corpus-only candidate set.

**Do not let a cheap ranker gate the good one.** Entry 78 made this mistake inside `rank` itself and
caught it only by measuring: BM25 put the answering page 116th of 122. `MAXIMUM_SCORED_MATCHES` is an
absolute bound and must not become a multiple of the shortlist size.

### 32. ~~Raise the corpus page budget~~ / ~~fix the budget split~~ — `closed, entry 82`

> **Reframed, built, measured and closed 2026-08-26 (entry 82).** The reframing was: the problem is
> not the *total* budget but the *even split* — `maximum_pages // seed_hosts` caps every host at the
> same share, and the United Kingdom's fee tables (one path per nationality) stopped at 15 of ~198
> where Canada's `?country=XX` reached 213. `HostBudget` was built to give each host a floor and let
> the rest compete for a surplus. **It is tested, it works, and it is defaulted off, because the
> reframing was wrong too.** A UK rebuild at `--pages 3000` moved `visa-fees.homeoffice.gov.uk` from
> 91 pages to 113 and 15 nationalities to **20**. It was never budget-limited: **zero** of its pages
> were reached from another nationality's page, because the country selector is a form. Canada's 425
> came from a page listing every country as a link. The difference is what the authority published.
>
> **And the change cost something**: with no cap the surplus goes to whichever host offers the most
> links, which for the UK is `www.gov.uk` — the whole government site. Its corpus went 922 entries
> to 4,530, **4,252 of them on gov.uk**. See entry 82 before turning `DEFAULT_CORPUS_HOST_FLOOR`
> back on; the floor half is worth revisiting on its own, the surplus half is what inflated it.

> **Measured and closed 2026-08-26 without building it (entry 81).** The 13% counts a denominator
> that is 90% inert: 1,073 of Japan's 1,189 candidates score zero for every role and can never be
> shortlisted, so they cannot distort a ranking. Among candidates actually in contention coverage is
> **50%**, and among those shortlisted it is **100%**. A bigger crawl would raise a number, not an
> answer. What blocks item 31 is not coverage — see entry 81 for what it is.

**Why (as originally written):** text coverage is **13% of corpus entries** (Japan, 605 of 4,803). The bound is the per-host
budget: `1500 // 48 seed hosts` ≈ 31 fetches against `mofa.go.jp`'s thousands of pages, which is why
`visaonline.html` — depth 1, on a host the corpus holds hundreds of pages of — still has no crawled
text and is in the index only because a live corridor cached it.

**This is not entry 77's disproved proposal.** That measured a bigger budget buying no improvement in
*entry* hit rate, and it was right: more discovered links is not more readable pages while 91% of them
are excluded from being fetched. With `CORPUS_EXPANSION_THRESHOLD = 0.0` the budget binds text coverage
directly — every extra fetch is an extra indexed page. Measure it on one country before the other 42.

**And watch `unreadable`**, which went 28 → 721 on Japan's rebuild. The crawl now tries links it used
to skip and many are dead or non-HTML. Nothing is wrong; the number is honest. But a build report that
says "721 unreadable" without saying why invites someone to fix a problem that is not there.

### 33. ~~Measure the model candidate selector~~ — `done and turned on, entry 85`

> **Re-measured across all ten corpus countries and turned on (entry 85).** Eight text indexes
> built (~420 searches, ~3 hours of crawling). Selection recall **86% against 79%, reading 112 pages
> against 274** — wins or ties 8 of 10, loses the UAE and the United States. `discovery_selector:
> model`. Entry 84's +30 points was a sample artefact: four of its five corridors were the UK, and
> over ten countries the gain is **+7**.
>
> **What is left is variance, not direction.** One run per corridor per arm, one corridor per country,
> all `IN/GB` — nationality and residence are not varied at all. And nobody has timed the fetch
> saving. See entry 85's closing section.

> ~~**Measured 2026-08-26 (entry 84), and it wins.**~~ Graded on selection recall over 33 pages proven
> to fill a role: **model at 85% reading 73 pages, heuristic at 55% reading 143.** Both named
> hypotheses were right — "prefer fewer" had the trade backwards, and `DEFAULT_SELECTION_SIZE` is now
> 20. Twelve of the oracle's pages were found *only* by the wider selection, so ranking 35 links never
> reached them.
>
> **What is left is the default.** `discovery_selector: heuristic` still. Five corridors in two
> countries, four of them the UK, and the oracle is adjudicator-derived. Widen to the ten corpus
> countries — which needs text indexes for the eight without one — then flip it.

**Why (as originally written):** entry 83 built it and ran it once. `discovery_selector: model` reads stored page text for
every candidate in contention and picks ~7 to fetch, where the heuristic ranks links and fetches 35.
It is off by default and the first run filled *fewer* roles, so it is a prototype and a hypothesis.

**The measurement, and it must not be role counts.** Entry 81 measured that metric swinging ±2 roles
on identical input. Grade the **selection**: for corridors whose role-filling pages are known from
the recall logs already on disk, count how often the selection contains them. Deterministic, no
adjudicator, no model variance. Role counts come second and only across many corridors.

**Two hypotheses the first run named, neither tested.** The model chose
`gov.uk/government/publications/visitor-visa-guide-to-supporting-documents` — a publication landing
page — where the heuristic used its content child, which is where the checklist actually is. So:
(1) `DEFAULT_SELECTION_SIZE` is 10 and the model used 7 because the prompt says "prefer fewer";
fetching is cheap next to being wrong, and that advice may be worth withdrawing. (2) A landing page
and its child look alike in an excerpt of the head.

**Where it can run at all:** the United Kingdom (82% of its contention set has stored text) and Japan
(50%). Everywhere else falls back to the heuristic and says so in the corridor's notes.

### 2. Amend the trust rule for governments with no marker, and for Schengen — `next`

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

### 17. Decide what a corridor that flips between runs should do — `next`

**Why:** measured 2026-08-21, and it changes how every other number in this file should be read.
`canada/GB/GB/tourism`, run cold twice within the hour on the same code against the same five domains,
**refused once and resolved once.** The difference was not scoring: on the resolving run
`entry-requirements-country.html` was candidate **15 of 470** at 53.4, comfortably inside 25 shortlist
places, arriving both as a `site:canada.ca` search seed and by crawl at depth 1. On the refusing run
search did not return it at all. Entry 43, known problem 19.

**So a resolved corridor is not evidence the pipeline is reliable, only that this run of it was.** And
the corridor store then keeps the lucky answer for three weeks, which hides the flip until it expires —
a traveller in week one and a traveller in week four get different products from identical code.

**This is a decision to argue before it is code**, which is why it sits here rather than in a fix. The
options are not equal and at least two are wrong:

1. **Re-search on refusal.** Cheap to write and the worst of them: it turns a refusal into "search until
   something answers", which is how a pipeline talks itself into an answer. Rejected unless argued.
2. **Widen or vary the queries.** Fifteen queries against five domains is already the cold-path cost
   (known problem 5). More queries is more surface, more latency and more quota, for an unknown gain.
3. **Keep what was found.** The candidate *set* could persist per corridor the way the resolution does,
   so a page found once is not lost when search forgets it. This makes runs sticky rather than lucky,
   and its risk is the opposite one: a page that has since been withdrawn stays in the set. The evidence
   TTL still governs whether it can be read, so the risk is bounded, but it needs saying out loud.
4. **Accept it and report it.** A corridor could state that its sources were what this run could find,
   which is honest and does nothing for the traveller who got the unlucky run.

**Do:** run one corridor three times and count, so the rate is a number rather than an anecdote — the
recall log makes this cheap to read now. Then write the decision entry. **Note it changes item 3:** one
run per corridor cannot distinguish a corridor that works from one that works half the time, so the
20-corridor measurement should either run each corridor twice or say plainly that it did not.

**Answered 2026-08-21 as [DECISIONS.md](DECISIONS.md) entry 44 — option 3, widened from per corridor to
per country.** The candidate set persists as a **corpus of official pages per country**, populated by an
offline job, and search leaves the request path for a populated country. A page found for
`canada/GB/GB/tourism` then also serves `canada/IN/IN/business`, which per-corridor persistence would
not. Options 1, 2 and 4 are rejected there in the terms above. **What is left of this item is the
counting**, which the entry does not replace and which sizes everything after it: run one corridor three
times, count the flips, and write the rate down. Items 18 and 19 are the implementation.

**The tooling for the counting landed 2026-08-22 (entry 45), so this is now one command and some
credit:**

```bash
.venv/bin/visa-discover corridor --destination canada --nationality GB --from GB --runs 3
```

It resolves the corridor three times and reports which candidates only some runs saw, ordered by how
far each got — a page one run actually *read* and another never saw is the case that decides
corridors, so it sorts to the top. It does **not** go through `AutomaticDestinationService`, because
that reads the corridor store and a stored corridor would answer runs two and three from run one.
Registry destinations now work from the command at all, which they did not before; that is what had
forced every previous live check into a throwaway script.

**Clear `var/cache/` first** if the point is to measure cold recall, and note the honest limit: this
measures *search and crawl* variance. The adjudication is still a model call, so two runs with an
identical candidate set can still disagree (known problem 10), and the report does not separate
those.

**Run 2026-08-22, and the flip did not reproduce.** `canada/GB/GB/tourism`, three runs, source cache
cleared beforehand, ~43s each:

| | |
| --- | --- |
| Outcome | **resolved, all three** — `visa_decision` and `general_entry` |
| Candidates | **471, and every run saw all 471.** Nothing varied at all |
| `entry-requirements-country.html` | found every run — **both** as a `site:canada.ca` search seed *and* by crawl at depth 1 from `check-visa-eta.html`; 53.4, shortlisted, fetched |
| `document_checklist` | unfilled all three times |

**So the flip rate is not 0 — it is "0 of 3 back-to-back", which is a weaker claim and must not be
written up as the stronger one.** The runs were ~2 minutes apart; the flip entry 43 measured was an
hour apart, and the 08-19/08-21 difference was two days. A search API can serve a stable result set
within a short window, so this cannot distinguish *"recall is stable"* from *"recall is stable over
two minutes"*.

**What is left of this item:** re-run the same corridor after a gap of hours or a day and compare
against `var/recall/` — that is the measurement that would actually establish a rate. Until then the
one observed flip stands as a single observation, and **entry 44 should be read with that in mind**;
its case now rests mainly on crawl depth and latency rather than on a measured frequency.

**One finding that is not about variance at all:** `document_checklist` went unfilled on every run
even though `.../visit-canada/supporting-documents` scored **64.0** for exactly that role and was
fetched. The adjudicator declined it three times running. That is item 9's question — "no checklist
exists" versus "we failed to find it" — with a third answer visible: *we found and read a plausible
one and the decider said no*. Worth reading its reason before item 18 assumes recall is the problem.

### 18. Build the offline corpus job, and run it on more destinations — `next`

**Why:** [DECISIONS.md](DECISIONS.md) entry 44. Recall is currently re-rolled from search on every
request, and entry 43 measured what that costs: the page that answers Canada was fifteenth of 470 on one
run and absent on the next. A corpus makes a good run durable — **but only a good run.** The job's own
recall therefore becomes the whole ballgame, which is the argument for it being an offline job rather
than a cached request: with no latency budget it can go deeper than a 60-second request ever will.

**Do:** a `visa-discover` command that crawls one country thoroughly — deeper hops, many more queries,
sitemaps (item 10) — and writes the country's page corpus. Then run it for the roughly eight
destinations item 3 needed (now done — see *Done*), so
the measurement describes the architecture the project intends to keep. The same command scales to 198
countries afterwards with no rework, which is why the count is not the hard part.

**Reuse `recall_log.ConsideredCandidate` for the row shape** — URL, title, `found_by`, depth,
`discovered_from`, per-role scores, `shortlisted`, `fetched` — it is already exactly right.

**Do not collapse the two stores.** Entry 43's recall log is overwritten per corridor, depends on
nothing, and swallows its own write errors, and every one of those is correct *for a diagnostic*. The
corpus is keyed by country, additive, and depended on. Same rows, opposite contract; inheriting the code
must not inherit the sentence "nothing depends on it".

**Additive, and never pruned by a bad run.** A URL that answered once stays in the corpus even when a
later crawl misses it. That is the entire point, and it is also what makes the refresh job's `404` check
(item 20) the only thing standing between the corpus and rot.

**Built 2026-08-22 (entry 46). The store, the job and `visa-discover corpus` exist; what is left is
running it for the other destinations and closing the recall gap below.**

```bash
.venv/bin/visa-discover corpus --country CA
```

| Run | Queries | Seeds | Crawled | New | Held |
| --- | --- | --- | --- | --- | --- |
| `--pages 60`, 36s | 30 | 203 | 355 | 355 | 355 |
| `--pages 200`, 97s | 30 | 203 | 1071 | 716 | **1071** |

The merge behaved: all 355 from the first build survived the second with `times_seen` at 2, and nothing
was dropped. **`entry-requirements-country.html` is in the corpus at depth 1** — the page whose absence
refused the corridor on 2026-08-21 is now durable, which is the thing this was built to do.

> **And the corpus is not yet a superset of what a corridor finds, which is the finding that matters.**
> `.../visit-canada/supporting-documents` — scored **64.0** for `document_checklist` and **fetched** by
> the corridor run the same day — is **absent from the corpus at 1,071 entries**. The cause is the
> traveller-free query set: `corridor_queries` asks `site:canada.ca Canada visa requirements United
> Kingdom`, and `corpus_queries` deliberately cannot. So the very thing that keeps the corpus
> corridor-independent also costs it recall that corridor-specific search has.
>
> **Both fixes are built — entry 47, 2026-08-22 — and the second is the one that worked.** The purpose
> sweep landed (30 queries → 70, 1,071 entries → 3,130, depth genuinely exercised) and **still did not
> find the page**: the exact query that had once surfaced it was re-run and search did not return it.
> **Search is nondeterministic at the source, so no offline sweep can guarantee a superset.** What
> closed it was write-back — after one corridor run through the new path, **24 of 24** pages that run
> fetched are held. The candidate set is now `corpus ∪ live`, pinned by what already filled a role.

### 19. Take search out of the request path too — `next`, **and this is the project's goal**

> **Updated 2026-08-26.** This item *is* the goal: a country built offline answers its corridors from
> the store, with live search only where it is genuinely unavoidable. Three things moved under it
> today and none of them closes it.
>
> **The nationality measurement this was always gated on now exists** (entry 82). It is not the
> 198-valued risk the item feared. Across 30 corridors into the ten corpus countries, 18 had **zero**
> misses and **none of the 67 misses were on a host the corpus lacks**. Half the misses are URLs
> naming a nationality — and the crawl reaches those where the authority published a country index
> (Canada: 213 values) and cannot where it published a form (the UK: 15, and a rebuild moved it only
> to 20). So the residual risk of dropping search is **concentrated in form-gated spaces**, which is
> a nameable, bounded thing rather than an unmeasured dimension.
>
> **What is still missing before switching it off.** Nobody has run a corridor set corpus-only and
> compared it to the same set with search, on a metric that is not roles-filled — entry 81 measured
> that metric at ±2 noise, and entry 76's "corpus-only costs 4 of 10 their checklist" predates both
> the rebuilds and the noise measurement, so it should not be quoted as current. **Item 34's oracle is
> what makes that comparison meaningful**, which is why 34 comes first.
>
> **And search is no longer the single point of failure it was**: entry 74 gave a corpus country a
> fallback when search is down, and it is reported rather than silent.


**Why:** the crawl half of this is done (entry 51) and search is what remains. It is now the largest
live component of a corridor — roughly 3s and **three queries per trusted domain** — and, since entries
44–57 removed everything else, the **only remaining single point of failure for a fully built
destination**: `search_all` raises if any query fails and `_resolve` searches *before* reading the
corpus, so Canada's 3,216 stored pages cannot answer a corridor when the provider is down. See
"smaller things".

**The bar for doing it is unchanged and has not been met.** `corridor_queries` interpolates purpose
*and* nationality; purpose is swept offline (four values), and **nationality is 198-valued and still
never measured** (entry 48). Removing search trades a known cost for an unmeasured recall risk on the
one dimension nobody has examined. Item 3's twenty corridors varied nationality four ways across five
destinations and changed the outcome **once**, which is suggestive and is not the measurement.

**Narrowed 2026-08-22 by entry 47.** The gap that blocked this is closed for Canada — the union plus
write-back holds 24 of 24 pages the live run fetched — so what is left here is no longer "make the
corpus a superset" but **stop paying for live discovery once it is one**. Decay rather than switch:
a proven, fresh corridor whose corpus holds no better-scoring unseen candidate needs no searches at
all, which is where the cost goes to zero and determinism becomes total. Gate it on the superset bar
holding for more than one destination; Canada alone is not evidence.

**Narrowed again 2026-08-23 by entry 51: the crawl half is done.** A country whose corpus offers more
than `DEFAULT_CRAWL_PAGES` pages on trusted domains no longer crawls in the request path at all, so
what remains here is **search** — the other 9.1s — and search stays until nationality has been measured
(entry 48). Note the two halves failed differently and only one of them ever refused a corridor: the
crawl was pure redundancy, while search is the dimension the corpus is not yet known to cover.

**Two things entry 47 leaves for this item.** Eviction is designed and unbuilt, so the corpus only
grows — 723 of Canada's original 1,071 entries scored zero on role vocabulary, which is the Noise tier
that should age out. And a **dead pin must never silently degrade**: if a pinned page 404s and the role
cannot be refilled, the corridor refuses, exactly as it would have without a pin.

**Do:** seed `CorridorResolver` from the country's corpus instead of from `corridor_queries` + crawl,
score and shortlist as now, and adjudicate as now. **The corridor-dependent step does not move** — which
page answers this traveller is still decided live, per entry 44's three-column table.

**Refuse on a miss, and flag the country.** Entry 38's rule applied to pages: falling back to live search
would silently restore the lottery for exactly the corridors that need it not to be one. The refusal must
tell three cases apart, because their fixes differ:

| What happened | What it means | Fix |
| --- | --- | --- |
| No corpus for this country | the job has not run here | run item 18 |
| A corpus exists, no page fills `visa_decision` | the job's recall missed, or the country publishes it behind a wizard | deepen the job, or item 5 |
| Stored URLs no longer resolve | **the corpus has rotted** | repopulate |

Only the third is corpus rot, and only the third should be alarming. **Refusals become the repopulation
queue**, which is observability the current system has none of.

**Careful:** trust is unchanged and must stay so. A seeded URL is still checked against `trusted_domains`
and still fetched through `LiveSourceFetcher`, so `validate_route` still runs and a corpus entry cannot
survive a later narrowing of the domain registry.

### 5. Answer the challenge, honour every `robots.txt`, and get a checklist out of France — `next`

**Why:** DECISIONS entry 41. `france-visas.gouv.fr` was never refusing this program — it serves a
Cloudflare challenge (`cf-mitigated: challenge`, *"enable JavaScript and cookies to continue"*), and it
serves the same challenge for `/robots.txt`, so no policy was ever stated. The project's own renderer,
under our own user agent with nothing spoofed, reads the page: 221,476 bytes, 2,277 visible characters,
`blocked_hosts: []`, ~7s. Three corridors' worth of coverage sits behind this, and one sentence
currently shipping to travellers is false because of it.

**A `403` reaches neither renderer today, so turning `render_mode: on_demand` on changes nothing.**
Both paths return at the blocking branch before the render branch: in `live_sources.py` the
`BLOCKING_STATUS_CODES` check precedes the `self._render(...)` call, and in `crawl.py` it precedes
`_render_if_empty`. Rendering is only ever attempted on a thin `200`. **Named by symbol rather than by
line, deliberately** — the line numbers written here on 2026-08-19 had drifted by seven within three
days, and a stale pointer reads as a claim about code that has moved. This is the first thing to fix and the easiest to get subtly wrong.

**Do, in this order:**

1. **Separate a challenge from a refusal at the point of detection.** A `403` carrying
   `cf-mitigated: challenge`, or a body carrying `cf_chl_opt` / `/cdn-cgi/challenge-platform/`, is a
   challenge. A `401`, a bare `403`, and a `429` are refusals and keep every rule entry 18 gives them.
   Detect it from the response, not from the host, so it cannot become "France gets special treatment".
2. **Add `challenged` as its own `FailureOutcome`**, beside `blocked` and `disallowed`. It must sit
   **outside** `blocked_urls()` and `persistent_refusals()` for the same reason `disallowed` does
   (entry 36): it may never reach `inaccessible_urls` or `decision_blocking_urls`, and it may never
   resolve a corridor. France's present resolution is exactly this bug and flips between runs.
3. **Let a challenge trigger the renderer**, in both `live_sources.py` and `crawl.py`, under the
   existing per-run render budget (entry 37) and the existing trust gate — which needs no widening,
   because the challenge scripts are same-origin. A render that comes back still challenged stays
   `challenged`; it is not retried.
4. **Fix the false sentence.** `static/app.js` gives every `blocked` failure with a URL
   *"does not permit automated retrieval"*. That is untrue of a challenge, and every reason reported
   has to be true of what was seen (entries 33 and 36). A challenge reads as *an automated-access
   check stood in front of this page and we could not answer it* — and once step 3 lands, the pages we
   *did* read this way are ordinary evidence and say nothing at all.
5. **Then measure what it actually buys**, per corridor, before believing any of it: France, Singapore's
   VFS page, and `travel.state.gov`.

**The checklist is not on the page, and this is the part to read before promising one.** Measured after
rendering: `/en/demande-de-visa` carries three generic items (passport, "photocopies according to your
situation", 2 ICAO photos); `/en/assistant-visa` is a four-step wizard with a nationality dropdown;
`/en/visa-de-court-sejour` defines the visa without saying who needs one; and
`www.france-visas.gouv.fr/en/web/france-visas/india` — the top-scoring France-Visas candidate at 74.4 —
is a **404** the challenge had been hiding. So steps 1–4 make France *honest and readable*; they do not
by themselves produce a corridor checklist.

**Getting the checklist needs the wizard, and that needs its own decision entry first.** The France-Visas
assistant is a read-only questionnaire that returns published guidance, not an application — but
`CLAUDE.md` puts *form filling* on the permanent out-of-scope list, and the distinction between
"answering four questions to be shown the published rules" and "filling in an application" is exactly
the kind of thing that must be argued in writing rather than assumed by whoever is holding the
keyboard. **Do not write wizard-driving code before that entry exists.**

**Entry 59 is now half of that argument, and it went the other way.** It measured GOV.UK's checker —
server-rendered, addressable, robots-allowed, answerable with plain GETs under our own user agent —
and still declined to drive it, because two of its questions are not in a corridor and answering them
means inventing traveller input. France's assistant has a nationality dropdown the corridor *does*
answer, so it is not settled by that reasoning alone; what entry 59 settles is that "it is technically
retrievable" is not the argument, and that naming the tool is the outcome to fall back to when driving
it is declined. Whatever France's entry concludes, it lands on top of that floor rather than instead of
it. Note it interacts with the
excerpt (entry 42): a wizard result is per-corridor by construction, so it would arrive as text nobody
else can re-derive, and it would be short enough to sit inside the head of the excerpt whatever else the
page holds.

**Careful:** the two prohibitions are unchanged and are what keep this from being circumvention — no
user-agent spoofing, and no retrying past a rate limit. And `robots.txt` outranks all of it: a
`Disallow`ed path is still not fetched, a policy that could not be read is still reported as unread
rather than as permission, and a `Disallow` still may not resolve a corridor.

### 1. Fix the post-over-nationality weighting, and find out why Sweden does not move — `next`

**Why:** DECISIONS entries 39 and 40. Widening the shortlist fixed two corridors and left two problems
standing, and they are now separable.

**The weighting bug is precise and reproducible.** For an Indian national applying from Great Britain the
scorer gives `checklist-schengen-visa-tourism/india` **113.0** and `.../united-kingdom` **73.0**. For a
consular checklist the **post** governs, not the passport: they apply at the Dutch mission in the UK. The
adjudicator correctly refuses a wrong-post page, so the corridor discards a checklist it already fetched.
Make `applying_from` outrank `passport_nationality` where a URL or link text names a post — and measure
across the verified corridors, because link scoring decides what every corridor reads.

**Sweden is unexplained.** It reads `migrationsverket.se`, fills `general_entry`, and neither widening
the window nor correcting its domain moved the visa decision or the checklist. It has not been traced the
way the Netherlands was, and it should be before anything else is changed on its account.

---

## Next up

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

**Reordered after the direction work**, because deploying before item 2 ships a product whose two
highest-volume corridors return no checklist.

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
   **This cannot be done with `visa-discover corridor` today** — see *Smaller things*: the command reads
   `get_destination_registry()`, so it cannot reach a registry destination, which is most of them. Fix
   that first or precompute from a script, as every live check so far has had to.
2. **Prefer a host that keeps a disk and a long-running process.** The stores persist and warm requests
   stay warm. If a disposable host is preferred, all three are small classes behind a `load`/`store`
   pair — except `FileRecallLog`, which is `write`/`read` and, being a diagnostic nothing depends on,
   need not survive at all.
3. **Set three secrets:** `OPENAI_API_KEY`, `OPENAI_MODEL`, `SEARCH_API_KEY`.
4. **Keep `render_mode: never`** unless the host can carry Chromium (~150MB plus system libraries).
   Vietnam will refuse without it, which is correct rather than broken.
5. **Put a key or a rate limit on `POST /visa-plans`.** It is unauthenticated and a cold corridor spends
   real money — search plus two model calls — so a public URL is a public wallet.

**Do not** deploy with `source_mode: fixtures`: it only knows Singapore, and would look like a working
product that answers exactly one corridor.

**Say it on the page:** this shows official guidance with citations and promises nothing about
correctness or currency. That framing is what makes the product safe to publish, so it belongs in the
interface rather than only in these files.

### 8. Confirm a blocked authority actually reads usefully — `soon`

**Why, and this item changed on 2026-08-18.** It used to say a blocked authority was named *only* when it
cost the decision, and that the US plan therefore never mentioned `travel.state.gov`. **Checking the code
showed that is wrong:** `to_destination_config` fills `unreadable_authorities` from `inaccessible_urls`
unconditionally, the extractor carries them into `unavailable_sources` whatever `decision_is_unverified`
says, retrieval-time blocks arrive separately through `RetrievalReport.failures`, and the interface already
gives any `blocked` failure with a URL the sentence *"does not permit automated retrieval"* plus a link.

**And that sentence is false for France — 2026-08-19, entry 41.** `france-visas.gouv.fr` serves a
Cloudflare challenge, not a refusal, so nothing there "does not permit" anything. Item 5 owns the fix.
Read a real plan for a genuine refusal — `travel.state.gov` is one — rather than for France, or this
item will measure the wrong sentence.

So there is **no plumbing left to do**, and writing some would have been work against a problem that did
not exist. What is unverified is whether it *reads* as useful — which no test can answer.

**Do, during item 3's live runs:** read a real plan for a corridor with a blocked page whose decision
resolved elsewhere, and check the authority is named, the link works, and the sentence sits where a
traveller will see it. Also check the narrower question entry 24 left open: the two `travel.state.gov`
places were never crawled, so confirm the US corridor records that block **somewhere** rather than
silently dropping it.

**Careful:** the causality requirement from entry 32 governs whether a block may *resolve a corridor*,
never whether it may be *reported* — every block is still reported, and that must stay true.

### 9. Tell "no checklist exists" apart from "we failed to find it" — `soon`

**Why:** `document_checklist` is not load-bearing (entry 14), so a corridor resolves without one. Right
for Vietnam, which publishes none. Wrong for a country that publishes one we failed to find or read —
and **discovery emits the same result in both cases.** The plan is honest either way (`VisaPlan` forces
it to state the gap and forbids inventing requirements) and is marked `partial`, but nobody is told
which case they are looking at.

**Live rather than hypothetical:** the United States ships exactly such a plan. And it is a *third* case
again — not "none exists", not "we failed to find it", but "we were not allowed to read it".

**Do:** the design already considered is a reviewed per-country declaration — `no_official_checklist:
true`, with a required note saying where the requirements actually live. A human decides once, in git,
exactly as `trusted_domains` works. Undeclared countries go back to refusing.

**Put it in `authority_domains.yaml`, not `destinations.yaml`** — corrected 2026-08-22. This item used to
name the latter, and a flag there would reach only the seven configured destinations:
`resolve_destination` falls through to `AutomaticDestinationService` for everything else, and that path
never reads `destinations.yaml` at all. The entry 34 registry is the per-country artifact of the right
shape, it is already reviewed row by row, and `CountryAuthorities` is where a country-level human
judgement belongs.

**Do not** try to infer the difference heuristically. "No checklist found" and "no checklist exists" look
identical from inside the crawler, which is the whole problem.

### 20. Make the stores substrate-swappable and durable — `soon`

**Why:** `var/cache/`, `var/corridors/` and `var/recall/` are local directories, so **a disposable host
makes every request cold** — up to fifteen searches, twenty-five fetches, two model calls, on an
unauthenticated endpoint. Item 7 already notes this; entry 44 makes it structural, because a corpus that
does not survive a restart is not a corpus. Both existing stores are small classes with `load`/`store`,
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

### 21. Fill the three provenance gaps — `soon`

**Why:** the system cannot answer *"why did you say an Indian passport holder needs this visa?"* with
more than a URL and a timestamp. Found while tracing entry 44, and **explicitly not an argument for the
store** — all three are schema and plumbing, worth fixing either way, and folding them into the corpus
work would let a large change borrow justification from a small one. Known problems 20, 21 and 22.

1. **`SourceReference.supporting_excerpt` is never populated on the live path.** Written only by
   `FixtureSourceFetcher` from the Singapore manifest; `LiveSourceFetcher._build` does not set it and
   `OpenAIVisaPlanExtractor` passes references through unchanged. Every live plan cites a URL with **no
   supporting quote**. The excerpt has to come from the model naming the sentence it read, and it must
   then be **checked against the retrieved text** rather than trusted — an unverified quote attributed to
   a government page is worse than none.
2. **`content_hash` never reaches `VisaPlan`.** It is on `FetchedSource`; `SourceReference` has no hash
   field, so a plan cannot be tied to the exact text it was read from.
3. **`decided_by`, `score` and `signals` never leave `ResolvedCorridor`.** Why a page was chosen for a
   role is on disk and invisible in the response.

---

---

## Later

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
applies. It would speed corpus builds, which currently cost search quota (item 18).

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
it out of the request path *by design* is item 19, which still wants the nationality dimension
measured first.

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

**A corpus build loses everything to one failed search query.** `search_all` raises if any query
fails, and a corpus build runs up to 70. One DNS blip on 2026-08-23 lost Japan's whole build. That
contract is right for a *corridor* — its docstring says tolerating a failure is a separate decision
about serving partly-searched evidence — but a corpus is additive and never claims completeness, so
the same rule costs far more than it protects. Decide it for the corpus path only.

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
