# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It answers three questions and nothing else: where
the project stands, what to do next, and what is known to be broken. The chat is not the source of
truth; these files are.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-28 — update this line when you touch the handoff |
| **Tests** | 644 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean. The suite is blocked from the network — `tests/conftest.py`, entry 45 |

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
corrections table in [CLAUDE.md](CLAUDE.md) has a hundred and eighteen rows; three of them are *this file's* known
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
| **Countries with an offline page corpus** | **10** — AE, CA, DE, FR, GB, JP, NL, SE, SG, US; ~23,000 pages. **Germany was rebuilt on 2026-08-29 across 87 hosts (was 1) after `diplo.de` was trusted**, entries 107–108. France and Sweden were rebuilt on 2026-08-28 with a render budget that can answer a challenge (entry 92): FR 5,317 → 6,277 entries with `france-visas.gouv.fr` 12 → 104 readable, SE 2,246 → 3,586 with `government.se` 0 → 863. **A build opens 3–15% of what it records** (entry 88), and the page answering a specific traveller is usually one hop below something it recorded and never opened. The Netherlands is rebuilt with a reserved share for per-traveller families and is the only one so far; item 35. These are served without crawling. The other **43** crawl in the request path, which is the ordinary path for a country nobody has built — a corpus is a speed optimisation, never a prerequisite. |
| **Verified working** | **All 53 have now been run; 10 have a corpus.** Stage 2 cleared on 2026-08-25 (entry 70): 103 corridors over the 41 never-run destinations, every one resolving or refusing for a verified reason. **34 of the 41 answer at least one passport** — Cyprus and India were recovered by the renderer on the same day (entry 75), India with all six roles. **Seven refuse every passport** with a diagnosis checked against what was seen: DK, LT, MA, MX, RO, SA, SK. **No corpus will fix those seven** (entry 76) — every one fails at *retrieval*, and a corpus crawl meets the identical wall. Item 30's remaining work is stage 3, the 43 corpora. |
| **Corridor phase** | median **27.4s**, range 8.8–48.3s, over 40 live runs, all corpus-routed, none crawling. |
| **Full request** | `POST /visa-plans` measured at 33–43s on three corridors, each a corridor resolve *and* extraction, with the page cache warm. A fully cold request is still untimed. |
| **Page-text index** | **1 country built, 11 backfilled** — `var/pagetext/`, one SQLite/FTS5 file each. Japan holds 684 pages of body text (94 PDFs) after a rebuild; the other ten are cache backfills of 1–38 pages. **Read at step 3b of `_resolve`, before the shortlist — and currently inert, on purpose** (entry 80). The A/B was taken and **it could not answer the question**: six runs of identical code give 4, 4, 4, 4, 5 and 6 roles, so role count cannot see a ranking change on one corridor (entry 81, which withdraws entry 80's regression). What is established is that the role-filling pages are shortlisted and fetched in every arm — the lift is recall-neutral, nothing shows it helps, and it stays off. Entries 78–81. |
| **Runtime mode** | `source_mode: live`, `extraction_mode: openai`, `render_mode: on_demand`, `discovery_decider: model`, `discovery_selector: model`, `destination_mode: automatic` |
| **Model candidate selection** | **Built and on** (entries 83–87). `discovery_selector: model` reads stored page text for every candidate in contention and picks ~7 to fetch, against the heuristic's 35. **On by default since entry 85.** All ten corpus countries now have a text index (~420 searches, ~3 hours of crawling). Graded against **`oracle/selection_oracle.yaml`, ground truth neither selector helped build** (entry 87): **100% role recall against the heuristic's 70% at matched budget**, and 91% when the heuristic is allowed its shipped 35 places and 3.1× the fetches. On the jointly-built oracle entries 85–86 used, the same three arms read 86%, 45% and 79% — so **entry 86's +41 points is +30**, and its +7 against the shipped heuristic is +9. The direction held; the numbers moved. It costs a second model call per corridor; one line in `runtime.yaml` reverts it. Still one run per corridor, one corridor per country, all `IN/GB`. |
| **Selection ground truth** | **`oracle/selection_oracle.yaml`, committed — twenty corridors over two travellers** (entries 87, 91). `IN/GB/tourism` and `PH/PH/tourism` across the same ten countries, named by hand from each corridor's whole contention set. Both read **100% held**; the denominators are the finding — the same stores answer **47 of 60 roles for one traveller and 41 of 60 for the other**. A row for a corridor nobody has run is curated offline with `visa-discover contention`. No network, no model. |
| **Corpus sufficiency** | **`visa-discover coverage`, committed** (entries 90, 93) — the promotion rule for stage 3. Two halves, never added. Half one reports three columns per traveller — answered **by a page**, settled **by an official tool**, open — and never merges the first two: **IN/GB 47 + 7 = 54/60 actionable, PH/PH 41 + 5 = 46/60**. Half two is every per-traveller family the store holds, from which the verdict is computed alone. Today: six countries *no per-traveller dimension*, SG and GB *bounded by the authority* (a pass), **NL `incomplete`**. Offline, no model, no search. |

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

**[TODO.md](TODO.md) is the queue — go there.** Its index table is generated from its own headings, so
it cannot drift; this file deliberately does not copy it.

**Item 34 is finished** (entry 87). `oracle/selection_oracle.yaml` is ground truth neither selector
helped build, and `visa-discover selection-recall` grades against it and against entries 85–86's
jointly-built oracle side by side. **Entry 86's +41 points is +30**; the direction held. Two things
it hands forward: thirteen of sixty roles have no readable answer at all, and the fixture is one
nationality and one residence — known problems 29 and 30.

**Sweden's corpus is rebuilt and it is where the render budget was costing most** (entry 92).
Counting each corpus's unanswered challenges offline — FR 66, **SE 216**, US 19, zero for the other
seven — cost one query and pointed at Sweden rather than France. `government.se` answered a challenge
on every page and held stored text for none; it now holds **863**, its visa-requirement list is
readable, and Sweden's Philippine row went **2 of 6 to 6 of 6**. The United States, at 19, is what
remains and its hosts are application portals rather than guidance.

**The visa-free plan is an entry plan, and it is built** (entry 96, item 39). A traveller who needs
no visa now gets their **entry** duties rather than an application with nothing in it: the documents
panel says there is nothing to gather and why, the route panel says there is nowhere to apply, the
timeline becomes *Before you travel*, and the plan may still be `verified`. The guard holds and is
mostly older code — `visa_required` can only be `False` on a final plan when a page said so, because
extraction forces it to `None` whenever `decision_is_unverified`.

**The open sub-decision was the step floor and the answer is no number.** Curating two more
visa-free corridors offline before writing anything — no network, no model — gives **3** entry
duties for `singapore/PH/PH`, **~5** for `japan/GB/GB` and **~7** for `united-kingdom/US/US`. A floor
under a list with no known shape is a quota, and a quota is how a model is invited to invent an entry
duty. Four stays for an application and is withheld from an entry plan entirely. Two validators the
spec never named were also in the way — `validate_absent_checklist`'s unresolved-question clause and
`resolve_plan_status`, which would have made a visa-free plan `partial` for ever — and one part of
the spec was wrong: `where_to_apply` is permitted to be `None`, not required, because a visa-free
American still needs a UK ETA.

**Item 38 is done: all twenty corridors graded, none unattributed, and the figure is reproducible
from disk for the first time** (entries 97, 98). The model reaches **92% role recall against the
matched heuristic's 47%** at 203 reads each, and against the shipped heuristic's 89% at 700 reads.
Entry 87 read 100% / 70% / 91% over ten corridors and could not be regenerated; over all twenty the
direction held and the matched-budget gap widened to **+45 points**.

**Read that number as what it is: agreement with pages a person named, not corridor health** (entry
99). The two come apart in both directions — `united-kingdom/PH/PH` reads **2 of 5 and filled every
role**, `united-arab-emirates/PH/PH` reads 6 of 6 and left the checklist unfilled. An earlier version
of this file called the UK row "the weakest and the place to look next"; it is the opposite. For what
a corridor actually lacks, read `unresolved_roles` in its recall log.

**The oracle is knowingly imperfect and is left that way** (entry 100). The UK row credits a page
that states no fee, and names one of three live addresses for a byte-identical document. Both were
left uncorrected because every distortion of this kind penalises the arm that reads *fewest* pages —
so **92% is a floor, not a ceiling**, and the 92-against-89 gap with the shipped heuristic is the
understated one. The rule: audit a row when it scores especially low, never rebuild the grader, and
re-curate without reading a recall log first.

**The run found the defect that made its own first printing wrong** (entry 97). The OpenAI account
ran out of credit part-way through, seven corridors fell back to the heuristic ranking, and all
seven logged `selector: model` — the field recorded whether a selector was *configured*, not whether
one *chose*. `japan/PH/PH` scored 5/5 in both arms off the same 34 pages. Entry 91's defect one
level in, now fixed on `ResolutionTrace` with a positive control, and the seven were re-run rather
than edited.

**Item 40 is dropped unbuilt, and the measurement is why** (entry 99). Filling the page-text index
for the 29,641 recorded-but-unopened corpus entries looked like the highest-value work — in
contention only **46%** of candidates hold text. It buys nothing measurable: coverage does not
predict recall (44% for corridors that missed, 51% for corridors that did not), France scores 100% at
7% coverage, the UK scores 40% at 81%, and **all seven missed roles were pages already in contention
whose stored text the model had read**. Do not resurrect it by pointing at the 46%.

**Item 35's rebuild was run and its acceptance test could never have passed** (entry 101). A corpus
rebuild seeds from search results and merges the old corpus in afterwards, so it re-walks the same
ground — 2,965 pages crawled bought **27 entries** and no change of verdict. Entry 88's "a build
opens 3–15% of what it records" is structural; re-running never fixes it.

**And the gate was counting the wrong thing.** `opened` meant "fathered a recorded link", so a
member fetched from a page that links nowhere read as never fetched — the Dutch schengen family
showed **72 opened against 185 fetched**. That 113-page gap is entry 89's VFS Global ceiling being
reported as a crawl gap. `Family.read` is now `max(opened, text_held)` and the verdict uses it;
`shape` deliberately still uses `opened` so both sides of its ratio agree. Schengen reads **100%**
(was 39%). No other country's verdict moved.

**Item 35's step 1 is done** (entry 102). `CORPUS_FAMILY_PATTERN` now requires a visa-domain word
rather than any government word — `apply`, `appointment` and `fees` are gone, since they admitted
Dutch passport renewals and appointment booking into the verdict *and* into the crawl's reserved
budget. Measured over all ten corpora first: it drops exactly those two families and keeps every
other family in every country.

**The Netherlands is still `incomplete`, now honestly**: `airport-transit-visa` at 52% read is a
real in-scope gap (it serves `transit`), `mvv-long-stay` sits at 1%, and the Kingdom's *Caribbean*
visa family survives the pattern on the word `visa` though it is the wrong territory for a
`netherlands` corridor — a limitation a test now asserts so it stays visible. The schengen family
that serves tourism reads **100%**. **Step 2 — seeding the crawl from recorded-but-unfetched
addresses — is what remains, and item 35 says to measure before spending it.**

**What the corridors actually lack is `general_entry`, not the checklist** (entry 103, which
corrects what this file said twice). Counting `unresolved_roles` in a recall log counts a role handed
to a questionnaire as unresolved — entry 93's conflation, read back in through a different file.
Against the oracle with tool-settled and does-not-arise removed, **16 of 120 role slots are genuinely
open**, and they are `general_entry` 7, `document_checklist` 3, `processing_times` 3, and one each of
`fees`, `visa_decision` and `application_route`.

**The three roles with the fewest lexicon terms are exactly the three that score no candidates at
all** — `general_entry` and `processing_times` at three terms, `fees` at four — and they hold 11 of
the 16. A page scoring zero for a role can never be shortlisted or selected *for* it at any budget,
which is entry 78 in a second place. All three are now widened (entries 103, 104).
`general_entry` goes from 3 terms to 16 — Japan **0 candidates to 2**, the UK 10 → 23, Sweden 4 → 9 —
and `fees` and `processing_times` follow: **corridors scoring zero for those two fall 14 → 10**, with
Sweden's timings going **0 → 15** topped by the right page at 46.4, and the Netherlands' fees topped
by `consular-fees/india` at 112.8. The top page for every role not being changed is **identical**
before and after, in every affected corridor.

**Germany stays at zero for all three roles**, and that is now the clearest single finding: its
entry, fee and timing pages are in the text index by cache backfill and **not in its corpus**, so no
scoring change reaches them. Germany's problem is discovery — item 30.

**One term was rejected and the reason generalises:** `payment` raised Canada's top fee score from 51
to 61 by promoting "Pay Your Application Fees, Online Payment" above the fee schedule. A traveller
needs the amount, not the till. **A score that rose is not a page that improved.**

**All of it is now verified end to end** (entry 105). The twenty corridors were re-run: Sweden fills
`fees` and `processing_times` where both had zero candidates, quoting "EUR 90" and "15 days"; roles
accounted for went **91 → 97 of 114**, nine gains against four losses. On `selection-recall` the
split is the finding — the **heuristic gained 12 points (47% → 59%)** while the model dipped two to
90%, because the heuristic *is* the ranking and the model was already reading text. **That is the arm
serving the 43 countries with no text index**, which is what stage 3 is about. Entry 81's noise rule
still governs single-corridor moves.

**The corpus is two defects from serving these ten countries, not twenty-one** (entry 106). Of 120
role slots: **4** should never be filled (Singapore is visa-free), **7** were closed by the
vocabulary work, and the remaining **9 sit in two countries with one cause each**.

- **Germany — fixed, three of four slots closed** (entries 107, 108). `diplo.de` is now a
  **reviewed** trusted domain: TLS could not confirm it (a Let's Encrypt wildcard names no
  organisation), but the already-trusted `auswaertiges-amt.de` prints *"Website
  http://www.washington.diplo.de"* under "Consulate General of the Federal Republic of Germany" —
  entry 89's two-part warrant, satisfied from stored text. Rebuilt: **1,565 entries on one host →
  5,712 across 87**, and `germany/PH/PH` now fills **6 of 6** while `germany/IN/GB` fills 5. Both
  `document_checklist` slots closed. One `general_entry` remains.
- **The United States — a block, and we had been rendering past it** (entries 108, 109). Its corpus
  predated the render fix, so it was rebuilt with the budget France and Sweden got; `travel.state.gov`
  still stores **zero** pages. Asked why, the page turned out to answer *"Sorry, you have been
  blocked"* with no script to run — **not a challenge at all.** One marker did it:
  `cdn-cgi/challenge-platform` is Cloudflare scaffolding shared by the challenge page and the block
  page, and it was the only one that page carried. So the renderer was pointed at a refusal (which
  entry 18 forbids), a false reason was recorded, and the corridor could not use entry 32's
  name-the-page outcome. Fixed, with a negative guard checked first. **Verified end to end:**
  `united-states/PH/PH` now records `cause=resolved_decision_blocked` where it recorded
  `decision_not_found`, and `POST /visa-plans` for `united-states/IN/GB` **returns a plan where it
  previously returned a 503 with nothing** — `visa_required: null`, `status: partial`, six
  `travel.state.gov` URLs named as blocked with true reasons, and an unresolved question handing the
  traveller the page to open. The five US slots are still a ceiling; the traveller is now told the
  truth instead of getting nothing.

**The selector A/B is closed** (entry 106, owner's decision). The model wins and has on every
measurement since entry 84 — 90% against 59% at matched budget. The twenty corridors are no longer
re-run to refresh that figure; `selection-recall` stays as an offline regression check.

**And a correction that changes how to read entries 103–104:** a role with zero scoring candidates
can still be filled. Germany scores zero for `fees` and `processing_times` and fills both, off a page
that entered contention as `application_route` and which the adjudicator read for all three. A page
enters on its best role and roles are assigned afterwards, from the text — so thin vocabulary is a
**selection** defect, not automatically a coverage one.

**A model has now produced the visa-free plan** (entry 98). `singapore/PH/PH/tourism` returns
`visa_required: false`, nowhere to apply, no checklist, no unresolved questions, **`verified`**, and
five entry steps each citing ICA's entry page. It needed a **sixth** change entry 95 did not name:
the guard that raises when a destination designates a checklist source and the model returns no
requirements read a correct empty answer as a failed extraction, because Singapore's configuration
pins an India-specific page as the checklist for every traveller. **The step floor never bit** —
three runs gave 6, 4 and 5 steps — so the no-floor decision still rests on entry 96's argument
rather than on this run.

**"No visa required" is a complete answer, and the metric now says so** (entry 94). Singapore's
Philippine row read two of six while resolving perfectly: no visa means no application, so four of
the six questions do not arise. The oracle has a fourth outcome, guarded so it can only be claimed
where a page answers `visa_decision` — "we could not find the checklist" must never become "there is
no checklist". **The product half is not built**, and its shape is now decided rather than open: entry 95, TODO
item 39, first in the queue.

**A tool-mediated answer is an answer, and only the coverage metric said otherwise** (entry 93).
The product has treated `resolved_decision_tool` as *resolved* since entry 63 — "the authority
publishes it only as a tool" — and `visa-discover coverage`, written the same week, counted it as a
gap. Half one now reports three columns and never merges them: **IN/GB 47 by a page + 7 by a tool =
54/60 accounted for; PH/PH 41 + 5 + 4 that do not arise = 50/60.** France's Philippine row is **5 of 6**, not 2.
`settled` is never added into `held`, because a page is citable and a tool is not.

**France's Wizard was checked against the fixture and confirms it — three roles, named not filled**
(entry 92). France-Visas' own FAQ says the Wizard "instantly informs you of the type of visa
required, the supporting documents to be provided and the amount to be paid", which is exactly the
three roles both France rows already attribute to it. Reading its form settles why they stay named:
step one requires **age, marriage to a French national, and whether the traveller is joining an
EU-citizen relative**, none of which is in a corridor and two of which change the answer. Entry 59's
bar, failed more clearly than GOV.UK failed it. `application_route` is already answered by real
pages; France's one genuinely open role is `processing_times`.

**France's corpus is rebuilt and it is still the fixture's weakest row** (entry 92). The offline
build always answered browser challenges — it had **12** renders against France's **64** challenged
pages, which is why the previous build recorded them unanswerable. With 400 renders and a per-host
give-up, `france-visas.gouv.fr` went from 12 pages of stored text to **104**, and that bought exactly
**one** role: the arrival page's entry conditions. France's other four gaps are inside the Visa
Wizard, which is a tool rather than a page, and no crawl reaches those.

**Item 37 is done** (entry 90). `visa-discover coverage` is the gate: offline, no model, no search,
two halves that are never added, and the verdict computed from the second alone so the first cannot
outvote it. Half one is the 47 of 47 known answers and stays a **regression check over one
traveller**; half two is the per-traveller family. Six of the ten corpora have no per-traveller
dimension, Singapore and the United Kingdom are *bounded by the authority* — a pass, because no
crawl budget crosses a selector — and only the Netherlands is `incomplete`. Two things it corrected
while being built: a gateway cannot be told from a leaf by counting children, only by asking whether
the children are themselves per-traveller; and **the United Kingdom has a per-traveller family where
entry 88 counted none**, its fee wizard, because the crawler groups links found on one page and this
groups across the store.

**Start at item 38: re-run the twenty oracle corridors.** Widening the oracle (entry 91) found that
`arms_from_logs` could not tell a model run from a heuristic one — a run's fetched URLs are read as
the model's picks and nothing recorded which selector fetched them. `RecallRecord.selector` now does,
and an unattributable log is refused rather than mis-graded, so **`selection-recall` grades nothing
today**: entry 87's figures stand as recorded and are not reproducible from disk until those
corridors are run again. Twenty runs restores them and produces the first selector number for a
second traveller.

**Then item 35, and its first job is the Netherlands rather than the other nine.** Entry 88
proved the mechanism there and did not finish the country: the schengen gateway sits at 71 of 184
opened and three *complete* families have never been opened at all — `making-appointment/{}` at 188
held, `caribbean-visa/short-stay/apply-{}` at 185, `passport-id-card/abroad/apply-{}` at 184.
Whether those three are gateways or leaves is unknown until one is opened, which is why the verdict
is `incomplete`. Rerun the gate after the rebuild; the verdict is the acceptance test. Then the
other nine, six of which the gate has already shown to be no-ops. **Item 36 is done** (entry 89):
where an authority contracts its guidance out, the delegate is now named to the traveller — with the
page that appointed it, never read, never cited, and still unable to fill the role.

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
