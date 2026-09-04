# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

**How to read this file.** **Now** is what to pick up, in the order written; **Next up** follows it;
**Later** is real but not urgent; **Done** keeps finished work because what building it found is usually
why the item after it exists; **Smaller things** are one-paragraph defects with no owner yet.

**The goal this list serves.** A country is built offline — corpus plus page-text index — and a
corridor answers from that store. Live search is acceptable where genuinely unavoidable, not as the
ordinary source of recall. **Item 19 is that goal as a work item**, and it is now measured rather
than argued: of 382 pages read by runs that postdate their country's corpus, **59 were not in the
corpus and all 59 came from search — 17 of them covering a role nothing else in the run covered**.
So the corpus is not yet a superset, not even where it is large: Bulgaria has 7,098 entries and
still gets its visa decision from a search-only PDF. Read item 19 before proposing to switch search
off for anything.

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
win is search recall, which nobody has measured** — see item 19 and known problem 13.

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
| **Now** | 31. The anchor scorer gates 94% of the corpus: measure it, scope a fix, test it | `next` |
|  | 19. Take search out of the request path too | `next` |
|  | 17. Decide what a corridor that flips between runs should do | `next` |
|  | 47. Find out how much of the world the family detector cannot see | `next` |
|  | 35. Finish the Netherlands, then roll the family reservation across the other nine | `next` |
|  | 9. Tell "no checklist exists" apart from "we failed to find it" | `next` |
|  | 2. Amend the trust rule for governments with no marker, and for Schengen | `next` |
|  | 5. Answer the challenge, honour every `robots.txt`, and get a checklist out of France | `next` |
| **Next up** | 4. Decide the client-side retrieval question | `soon` |
|  | 7. Put it somewhere others can open it aka deployment | `soon` |
|  | 8. Confirm a blocked authority actually reads usefully | `soon` |
|  | 20. Make the stores substrate-swappable and durable | `soon` |
|  | 21. Fill the three provenance gaps | `soon` |
| **Later** | 46. Decide what to do about a refusal served as `HTTP 200` | `later` |
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
documentation said it was — the corrections table in [CLAUDE.md](CLAUDE.md) has eighty-five rows and every
one cost a session. **Prefer running a corridor to reading a code path**, and when an item below
proposes a fix, measure the proposal before implementing it. Several items here were written from a
careful reading and were wrong.

---

## Now — pick these up in this order

### 31. The anchor scorer is a hard recall gate on 94% of the corpus: measure it, scope a fix, test it — `next`, **start here**, **re-scoped 2026-09-02**

> **Re-scoped three times on 2026-09-02. Read the third one first — it changes what the item is
> about (entry 126).**
>
> **The scorer's ordering is consumed by nothing.** `_choose_what_to_read` pools on
> `best_combined() > 0` and hands the pool to the model **unsorted**; `build_selection_packet`
> withholds the scores deliberately, because *"passing them would anchor the model to the ranking
> this call exists to replace"*. So `score_link`'s numeric output reaches the request path as a
> **boolean**. Ranking still matters on the heuristic fallback — no selector, no stored text, or a
> failed model call — and nowhere else.
>
> **That collapses this item to one question:** the admission test is a threshold on a score
> computed from a URL and an anchor, and it excludes 94% of the corpus from a model that would
> otherwise be reading the pages' own text. Item 1 was a *weighting* fix under this item and it
> moved the pool by 35 pages of 186,596; no amount of further weighting work will do better, because
> weighting is not what the gate reads. **Every remedy below should be judged on whether it changes
> what is admitted.**
>
> The two earlier re-scopings, kept because the reasoning still holds: it first asked for a *numeric
> text lift inside `combined`* — better ordering of what the model already sees, which entry 123
> measured as the wrong end and finding 1 above now explains. Then it asked to *admit zero-scored
> pages on their stored text* — which is one remedy, named before the problem had been sized.
>
> **The principle is not new and the number is.** Known problem 9 has said since entry 40 that the
> heuristic *"is a recall gate rather than a decider"* and that the conclusion is **widen the gate,
> not improve the ranking** — entry 61 is the same lesson a second time. What nobody had was the
> size of the gate, and it is 6%.

**It sits ahead of item 19, and the reason is measured (entry 125).** The gate admits **search
results at 49% and corpus pages at 5.5%** — a 9× difference, because a search engine returns pages
whose URL and title already match visa vocabulary, which is exactly what the anchor scorer rewards.
Item 19 asks whether search can leave the request path; it is measuring the corpus's contribution
through a filter biased nine to one **against** the corpus. That does not make search dispensable —
its results are genuinely more relevant — but it does mean item 19's "17 search-only pages covered a
role nothing else covered" is an **upper bound** on search's necessity, and this item is what tightens
it.

**Three questions, in this order. Do not skip to the third.**

**1. How big is the gate?** — answered, entry 123. One line of `_choose_what_to_read` decides it,
and everything downstream comes from its result.

**2. Is that bad?** — **answered twice, and the second answer is the one that sizes the item.**
Entry 127: yes, at least once. Entry 128: **3 role-cells of the 35 the pool cannot answer, 8.6%,
concentrated in 2 of 21 corridors** — and 19 of 21 corridors lose nothing to the gate at all.

> **The framing that produced the useful number, and it was the owner's.** "Does the discarded 94%
> hold a relevant page" is the wrong question: a corridor filling all six roles from pooled pages
> loses nothing to the gate however much relevant material sits outside it. The question is whether
> the outside answers a role the pool **cannot** — the gate's *marginal* cost. Six corridors answer
> every role that arises out of the pool alone; **widening the gate is not a general improvement,
> and any remedy has to be worth 3 roles of 35.** That makes "stop filtering and start capping" the
> most attractive of the four below, because it is the only one that bounds the selection packet by
> construction, which matters more at this size of prize than when the prize was unknown.
>
> **Do not quote "19 of 21 lose nothing" without its caveat:** nineteen of those rows were curated
> *from* the pool and cannot report an outside answer by construction. What is informative is the
> other side — **of the two rows curated against the whole corpus, both lose something.** The gap is
> closed by triage rather than by fixture: all 38 open cells across all 21 corridors were listed
> with their top five unpooled candidates ranked by stored text, and every cell whose candidates
> were not plainly chaff, the wrong post or the wrong purpose was read in full. Three came back
> positive and are in the fixture; the rest are the Casino Ordinance, IRCC contact forms,
> `business.gov.nl` tax pages, trademark filing and a USCIS blog.
>
> **The three:** Czechia's UK supporting-documents list (`document_checklist` **and**
> `general_entry`) and the Dutch EES leaflet (`general_entry`). The Dutch one is the sharper case
> because the pool is not empty for that role — it offers `.../entering-without-visa`, whose
> audience is travellers who do not need a visa, which this one does.

> **How it is measured, so the next change can be graded the same way.** `role_reach` classifies
> each (corridor, role) as `pooled` / `outside` / `absent` against the rebuilt contention set, and
> `selection-recall` prints role recall split by the first two — an arm cannot be charged for a page
> it was never shown. `absent` is held out of both columns: an address nobody crawled says nothing
> about the gate in either direction (item 35). The arm split has a thin denominator, 0/1 outside,
> because two of the three recovered roles are in Czechia, which has never been run and so has no
> recall log to replay.
>
> The fixture could not previously say anything here, and the reason was structural:
> `oracle/selection_oracle.yaml` was curated "from every candidate that scored above zero", which is
> the same filter `_choose_what_to_read` applies, so no page the gate removed could appear in it at
> all — 88 of 88 answering pages inside the pool is a tautology, not a result (entry 123). A fixture
> cannot detect a filter it shares.
>
> **What is now built:** `Contention.unpooled` keeps the losing side of the pool test instead of
> discarding it; `unpooled_by_text` orders it with `PageTextStore.rank`, which reads inside a page,
> because the anchor scorer scores every member zero by definition and using it would reproduce the
> bias under audit; `visa-discover contention --outside-pool` is the curation view; `curated_from:`
> on each row records which set the curator read, defaulting to `pool` and never inferred; and
> `selection-recall` prints a **pool audit** splitting each row's answers into pooled, outside, and
> absent from the corpus. Where every row is `curated_from: pool` the report says its own zero is a
> tautology rather than printing it as a result.
>
> **What it found.** Swept over all 53 corpora at `IN/GB`: 9,666 pooled candidates against 141,789
> unpooled, 843 of which score on their own text. Most is chaff exactly as this item allowed —
> Liechtenstein's whole discarded set is its law collection, top two read out being the Casino
> Ordinance and the Law on the Organization of the Ordinary Courts. But `czechia/IN/GB/tourism`
> holds `mzv.gov.cz/public/d3/71/2a/4835385_2943205_UK_EN.PDF`, the EC decision *"establishing the
> list of supporting documents to be submitted by applicants for short stay visas in the United
> Kingdom"* — this traveller exactly — at **link score 0.0 for every role**, while the pool's best
> `document_checklist` candidate is an Entry/Exit System page at 36.0 and its runner-up is a
> *student* visa checklist. Committed as the fixture's first `whole_corpus` row.
>
> **So "the 94% is chaff and this item closes" is ruled out**, and any remedy below now has a
> fixture that can tell whether it worked. What is still unmeasured is *how often* — one row, one
> corridor, one traveller. Two bounds carry forward: `contention_for` is corpus-only, so a role only
> search would surface cannot be curated from it, and the text index holds 23% of the corpus, so a
> role answered only by an address nobody opened is invisible to this instrument (item 35).

**3. What would fix it, if it is bad?** Four candidates, and they are not alternatives to each other
— the first is already measured and ships on its own:

- **Score what the anchor already says.** ~~Item 1~~ — **done, entry 126, and its result is the
  argument for the rest of this list.** A page about the country the traveller applies from now
  earns `residence_weight` on the post-specific roles. Measured across all 53 corpora it admits
  **35 pages of 186,596**, and three of the four families it was built for already hold the answer
  in their own stored text — the Netherlands' UK apply page opens *"Applying for a Schengen visa
  for the Netherlands in the United Kingdom"*, and the index has held those 8,594 characters all
  along. **A weighting change is not a way past a boolean gate.**
- **More signals of the same kind.** The scorer rests on an English vocabulary and per-country city
  labels, so it degrades on new countries and languages (known problem 9). Entries 103–105 widened
  three role vocabularies and moved real corridors. Cheap, incremental, and bounded by the same
  ceiling: an anchor cannot say what a page contains.
- **Admit on the body, not only on the anchor.** The built-and-gated text lift, used as an
  *admission* test rather than an ordering one. `_text_scoring_is_fair` requires the index to cover
  half a candidate set before the lift may **order** it; that bar is right for ordering and wrong for
  admission, since a page scoring on its own text is worth showing whether or not its neighbours have
  text. **Bounded by coverage:** the index holds bodies for **23%** of the corpus overall and 7% for
  Liechtenstein, so this reaches only part of the 94% and the rest stays anchor-only.
- **Stop filtering and start capping.** Take the best N by combined score instead of everything above
  zero, so a zero-anchor page with good body text displaces a weak one rather than being excluded
  categorically, and N stays fixed. **This is the only candidate that bounds the packet by
  construction**, which matters — see the budget note below.

**And a fifth that is not a scoring change at all:** read more of what the corpus records. A build
opens 3–15% of what it discovers (entry 88) and the text index holds 23% of it, so for most of the
94% there is no body to score even in principle. That is item 35, and it is the same bottleneck from
the other end. **Question 2's fixture will say which end binds** — if Liechtenstein's answers sit in
pages we hold text for but score zero, it is this item; if they sit in addresses nobody opened, no
gate change reaches them.

**The packet has a real budget and "show everything" is not on the table.** `excerpt_budget` shrinks
rather than drops, with a 200-character floor: France's 615 candidates get 650 characters each,
about **100k tokens**, which is the design target. Liechtenstein's 7,482 would blow past it while
529 of them have any text to show. Every remedy above has to stay inside that.

**How to test whichever ships.** Entry 81's rule, without exception: **grade the shortlist, not the
plan.** Role count swings by 4, 4, 4, 4, 5, 6 on six runs of identical code, so any A/B with an
adjudicator in it cannot see a ranking change. Measure against the question-2 fixture, offline.

**The gate, in one line of `_choose_what_to_read`:**

```python
pool = [c for c in candidates.values() if c.best_combined()[1] > 0]
```

Everything downstream — `by_id`, `build_selection_packet`, the model's choice — comes from `pool`.
A candidate the link scorer rates zero for every role is never shown, never fetched, never judged.
Over the 24 runs postdating 2026-08-30: **71,798 candidates, 4,450 in the pool.** Liechtenstein
offers **2 of 7,482**; Bulgaria **8 of 6,847**; Morocco 19 of 1,801; Austria 96 of 3,670. The widest
is Norway at 34%.

> **It has a confirmed instance as of entry 127, so read the paragraph below as history.** What
> follows was true when the item's motivating example fell over and before the fixture could name a
> page outside the pool; question 2 above now carries the answer.
>
> **Its motivating example evaporated on examination, 2026-09-02 (entry 124), and the item
> survived on the 6% alone.** Romania was the case that promoted this to the top of the queue; the
> pages its gate discarded turn out to be Romanian **legislation** PDFs — chaff, exactly as the "do
> nothing" outcome below allows for. What nearly cost Romania its answer was a **missing residence
> score**, which was item 1 and is now shipped (entry 126). So this item has a real number (6%
> shown, 94% discarded) and **no confirmed instance of an answer inside the 94%.** Curate first;
> the item may close.
>
> **And note what item 1 could and could not reach.**
> It admitted 35 pages and every one is a page the anchor *nearly* scored — a page with role
> vocabulary that was missing one traveller signal. Nothing it did, or could have done, reaches a
> page whose anchor says nothing at all, and Canada's `?country=GB&lob=visit` — the page a
> *tourism* corridor actually wants — is exactly that: `score_link` returns early on an empty
> vocabulary before any traveller signal applies, so it scores 0.0 and stays outside the pool while
> its `lob=citizenship` sibling is admitted. **That page is inside the 94% and it is not chaff.**
> It is the nearest thing to a confirmed instance the item has, and it has no stored text either,
> so it is also a case only remedy five reaches.

**Do not confuse this with the per-role filter, which is a different thing.** `rank_for_role` drops
a page scoring zero **for that role**; the pool drops a page scoring zero for **every** role. Entry
91's UAE page — five roles answered, 0.0 for three of them — is the first kind: its
`best_combined()` is **49.6**, it is in the pool, and it was shortlisted and fetched in four
recorded runs. It says nothing about the pool gate, and an earlier draft of this item cited it as
though it did.

**The present oracle cannot measure this, and that is the finding, not an obstacle to work around.**
`oracle/selection_oracle.yaml` was curated "from every candidate that scored above zero"
(`contention.py`), and entry 87 built the first ten rows from "the corridor's **whole** contention
set" believing that was the whole set. Checked 2026-09-02: of the pages the oracle names as
answering a role, **88 of 88 are in the pool and none scores zero**. That number could not have come
out any other way — **a fixture curated from the pool cannot name a page outside it.**

**So the measurement is a curation job, and it is the honest cost of this item.** Take a small
number of corridors and name the answering pages from the **whole** candidate set — using
`page_text.rank` over stored body text, the only instrument that can see inside a page — then ask
how many of them the anchor scorer rates zero for every role. **Liechtenstein (2 of 7,482) and
Bulgaria (8 of 6,847) are the right two**: the answer matters most there, and a row is cheapest to
justify where the current pool is two pages. If those rows come back with every answer already in
the pool, the 94% is chaff and this item closes.

**Then: what could put a candidate into the pool, given the packet has a real bound.**
`DEFAULT_SELECTION_CHARACTERS` is 400,000 shared across candidates, so a pool of 7,482 leaves each
one a few dozen characters and the answer is **not** "drop the filter". Candidates worth arguing:

- **Score the body where the index holds it, and admit on that** — the built-and-gated lift, used as
  an *admission* test rather than an ordering one. `_text_scoring_is_fair` demands the index cover
  half the candidate set before the lift may order anything, and that bar is right for ordering and
  wrong for admission: a page that scores on its text is worth showing whether or not its neighbours
  have text.
- **Cap the pool rather than filter it** — take the best N by combined score, so a zero-scoring page
  with body text can displace a low-scoring one instead of being excluded categorically.
- **Do nothing, if the measurement says the 94% is chaff.** That is a real outcome and would close
  this item; entry 62 and item 32 are both precedents for measuring a proposal and shipping nothing.

**Two constraints that do not move.** Entry 78: stored text **ranks and never speaks** — `rank`
returns URLs and scores, `TextMatch` has no field for a body, and nothing here may add one. And
entry 81: grade the **shortlist, not the plan** — role count swings by two on identical input, so
any A/B with an adjudicator in it cannot see a ranking change.

**What this unblocks if it works.** Liechtenstein, Bulgaria, Morocco and Austria have had their
results attributed to challenges and stated `Disallow`s. Those causes are real and entry 18 forbids
working around them — but nobody has shown they are *sufficient*, because the pool gate has never
been separated from them. A corridor choosing from 2 pages of 7,482 is not evidence about
Cloudflare.

---

<details>
<summary>The previous scope, kept because its measurements stand</summary>


> **Status corrected 2026-08-30.** This used to read "blocked on item 32"; item 32 is closed
> (entry 82, no change shipped), so nothing external blocks this. What gates it is the
> measurement below — one with no adjudicator in it.

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
> ~~until item 32 lands.~~ **Item 32 closed with no change shipped (entry 82), so this is no longer
> waiting on it** — what gates it is a measurement with no adjudicator in it.
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
for the wrong post. `score_body` takes a nationality and **no residence** — entry 126 gave
`score_link` a residence signal and deliberately left `score_body` alone — so it has none of
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

</details>


### 19. Take search out of the request path too — `next`, **and this is the project's goal**

> **Reordered behind item 31 on 2026-09-02, and the reason is a number (entry 125).** The pool the
> selector chooses from admits **49% of search results and 5.5% of corpus pages** — a 9× gap,
> because search returns pages whose URL and title already match visa vocabulary, which is precisely
> what the anchor scorer scores. So the measurement below — 59 of 382 pages read came only from
> search, 17 of them load-bearing — was taken through a filter that systematically disadvantages the
> alternative it is comparing against. **Read the 17 as an upper bound on search's necessity, not as
> its value.** Item 31 is what tightens it, and it should run first.

> **Measured 2026-08-30, and the answer is: not yet, and not the way either obvious option would do
> it.** This is the comparison the item had been gated on since entry 82. It is offline, and it has
> **no model and no adjudicator in it** — entry 81's requirement — because it grades what a corridor
> *read*, not what its plan came out as.
>
> **Method.** For every recall log, take the pages the run actually fetched and ask whether the
> country's corpus holds them, comparing on `canonical_key`. **Restricted to runs that happened
> after that country's corpus was built** — the first cut read 26.7% and was meaningless, because
> most logs predate the corpora they were being compared against (Egypt's run is five days older
> than its corpus, and "22 of 22 missing" said nothing at all).
>
> | | |
> | --- | --- |
> | runs measured after their corpus was built | 36 |
> | pages read | 382 |
> | **pages read that the corpus does not hold** | **59 (15.4%)** |
> | runs where the corpus held everything read | **13 of 36** |
> | how those 59 were found | **search — all 59** |
> | of the 59, covering a role nothing else in that run covered | **17** |
>
> **So search is not redundant today, and the 17 are load-bearing:**
>
> - `mfa.bg/upload/…VisaRegime…pdf` — **the page Bulgaria's visa decision comes from**, with its
>   Type-C checklist PDF beside it. Bulgaria has a 7,098-entry corpus and neither page is in it.
> - `um.dk/nigeria/…` — Denmark's Nigeria checklist page, scoring 84.
> - `visa-fees.homeoffice.gov.uk/y/philippines/…` — the UK's per-nationality fee table. Exactly the
>   form-gated space entry 82 predicted would be the residual risk, now confirmed as a real loss.
> - Lithuania's `keliauk.urm.lt` decision and documents pages; Liechtenstein's `llv.li` visa pages.
>
> **This kills both of the obvious shortcuts.** *Disabling search only where a corpus exists* fails
> because the 17 are all in corpus countries. *Waiting until every country has a corpus* fails for
> the same reason from the other side: the failure is not "no corpus", it is that **a corpus is not
> a superset even where it exists**.
>
> **The lever is the write-back, and it is not running everywhere.** Entry 47's `_write_back` is
> this item's own "decay rather than switch" plan — keep what a live run finds so later runs start
> from more — and it is well built. But `automatic.py:414` is its only call site, so it runs on the
> **API/webpage path only**: `visa-discover corridor` builds its resolver directly
> (`cli.py:744`) and folds nothing back. Bulgaria has **`proven` entries: 0** and still lacks the
> PDF it resolved from, and every corridor run from the CLI this session contributed nothing.
>
> **Do next, in this order.**
>
> 1. **Decide whether the CLI should write back**, and note it is not free: the CLI deliberately
>    withholds *pins* so `--runs` measures variance without run 1 contaminating run 2, and
>    write-back mutates the store in exactly that way. A flag defaulting off for `--runs` is the
>    obvious shape; it has not been agreed.
> 2. **Re-run this measurement after a period of normal use** and watch the 15.4% fall. The script
>    is a dozen lines over `var/recall/` and `var/corpus/`; it should become
>    `visa-discover search-dependence` if it is going to be run more than twice.
> 3. **Retire search per country, never globally.** A country whose load-bearing search-only count
>    is zero across several travellers can drop it; Bulgaria plainly cannot. 13 of 36 runs are
>    already fully covered, so the first candidates exist today.
>
> **What this does not measure.** Whether a page the corpus lacks would have been *replaced* by an
> adequate corpus page the adjudicator never saw. Reading is not using, and 42 of the 59 had their
> role covered by a corpus page in the same run — the 17 are the honest floor, not the ceiling.


> **Updated 2026-08-26.** This item *is* the goal: a country built offline answers its corridors from
> the store, with live search only where it is genuinely unavoidable. Three things moved under it
> today and none of them closes it.
>
> **The nationality measurement this was always gated on now exists** (entry 82), and the
> 2026-08-30 measurement above confirms where its residual risk landed: the UK's form-gated fee
> table is one of the 17 pages search alone supplied. It is not the
> 198-valued risk the item feared. Across 30 corridors into the ten corpus countries, 18 had **zero**
> misses and **none of the 67 misses were on a host the corpus lacks**. Half the misses are URLs
> naming a nationality — and the crawl reaches those where the authority published a country index
> (Canada: 213 values) and cannot where it published a form (the UK: 15, and a rebuild moved it only
> to 20). So the residual risk of dropping search is **concentrated in form-gated spaces**, which is
> a nameable, bounded thing rather than an unmeasured dimension.
>
> ~~**What is still missing before switching it off.** Nobody has run a corridor set corpus-only and
> compared it to the same set with search…~~ **Superseded by the 2026-08-30 measurement above**,
> which answers it from the recall logs without needing a second live arm at all: the question
> "would search's absence have cost this run a page" is settled by asking whether the corpus holds
> what the run read. Entry 76's "corpus-only costs 4 of 10 their checklist" is still not current and
> should still not be quoted; entry 81's ±2 noise on roles-filled is why the new measurement counts
> pages rather than roles.
>
> **And search is no longer the single point of failure it was**: entry 74 gave a corpus country a
> fallback when search is down, and it is reported rather than silent.


**Why:** the crawl half of this is done (entry 51) and search is what remains. It is the largest
live component of a corridor — roughly 3s and **three queries per trusted domain**, so a five-domain
country like China spends fifteen live queries on every page load, paced at 1.3s each. `_resolve`
searches *before* reading the corpus, unconditionally; the corpus can only suppress the **crawl**
(`_crawl_is_worth_running`), which is what the "the crawl was skipped" note in a corridor means.
Search is no longer a single point of failure — entry 74 gives a corpus country a reported fallback
when the provider is down — but it is still the whole of the remaining live cost.

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
| No corpus for this country | the job has not run here | run `visa-discover corpus --country XX`; only BR and UY lack one |
| A corpus exists, no page fills `visa_decision` | the job's recall missed, or the country publishes it behind a wizard | deepen the job, or item 5 |
| Stored URLs no longer resolve | **the corpus has rotted** | repopulate |

Only the third is corpus rot, and only the third should be alarming. **Refusals become the repopulation
queue**, which is observability the current system has none of.

**Careful:** trust is unchanged and must stay so. A seeded URL is still checked against `trusted_domains`
and still fetched through `LiveSourceFetcher`, so `validate_route` still runs and a corpus entry cannot
survive a later narrowing of the domain registry.

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

**A second flip, 2026-09-01, and it is not the same one — it has no search in it (entry 118).**
`united-states/IN/GB/tourism`, twice within seven minutes, corpus-routed with the crawl skipped:
run 1 read 9 pages, filled nothing and refused `decision_not_found`; run 2 read 14, filled
`application_route` and `general_entry`, and resolved **`resolved_decision_blocked`**. The refused
set was the same three `travel.state.gov` URLs both times and all three were in `candidates`, so
`_decision_blocking_judged` was asked the same question about the same pages — `visitor.html`
labelled *"Visitor Visa"* among them — and answered it both ways.

**That moves this item's centre of gravity.** Entry 43's flip was *recall*, which entry 44's corpus
was built to remove, and the 2026-08-22 counting found nothing. This one is the model, on the call
that decides **whether the corridor resolves at all** rather than which roles fill — known problem
10 reaching further than that problem has ever recorded. Options 1–4 above are all about recall and
none of them addresses it. **Count this one before designing anything:** `--runs 3` on
`united-states/IN/GB` is corpus-routed, so it costs no search quota and isolates the model, which is
exactly what the 2026-08-22 run could not do.

**One finding that is not about variance at all:** `document_checklist` went unfilled on every run
even though `.../visit-canada/supporting-documents` scored **64.0** for exactly that role and was
fetched. The adjudicator declined it three times running. That is item 9's question — "no checklist
exists" versus "we failed to find it" — with a third answer visible: *we found and read a plausible
one and the decider said no*. Worth reading its reason before assuming recall is the problem.

### 47. Find out how much of the world the family detector cannot see — `next`

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


### 35. Finish the Netherlands, then roll the family reservation across the other nine — `next`, **re-scoped by entry 101**

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


### 9. Tell "no checklist exists" apart from "we failed to find it" — `next`, **promoted 2026-09-02**

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

### 2. Amend the trust rule for governments with no marker, and for Schengen — `next`, **and Germany is the worked example**

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
and stated `Disallow`s already named, plus the pool gate of item 31, which has never been separated
from them. **What is left of this item is the rule question, not the coverage one** — Schengen and
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

**One `robots.txt` question is open and is deliberately not folded in here (entry 119).** Five of
five hosts that ever tripped the size cap answer `/robots.txt` with `200 text/html` and a web page —
a "Technical Difficulties" notice or an app shell — and the reason reported is now true of that.
What was **not** changed is the verdict for a *small* HTML page at that path: it is parsed into an
empty ruleset and the host is crawled. Closing it would stop crawling hosts crawled today, so it
needs its own count first — how many authority hosts serve markup at `/robots.txt` at all. That is a
sweep over `authority_domains.yaml`, one GET per host, no model and no search.

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

**~~And that sentence is false for France.~~ Fixed by entry 75 and verified 2026-09-02.**
`challenged` became its own `FailureOutcome` and never becomes `blocked`, and `static/app.js`
branches on `failure.outcome === "blocked"` — so a challenged authority already renders its true
detail sentence instead. Read a real plan for a genuine refusal — `travel.state.gov` is one — rather
than for France, or this item will measure the wrong sentence.

So there is **no plumbing left to do**, and writing some would have been work against a problem that did
not exist. What is unverified is whether it *reads* as useful — which no test can answer.

**Do, during item 3's live runs:** read a real plan for a corridor with a blocked page whose decision
resolved elsewhere, and check the authority is named, the link works, and the sentence sits where a
traveller will see it. Also check the narrower question entry 24 left open: the two `travel.state.gov`
places were never crawled, so confirm the US corridor records that block **somewhere** rather than
silently dropping it.

**Careful:** the causality requirement from entry 32 governs whether a block may *resolve a corridor*,
never whether it may be *reported* — every block is still reported, and that must stay true.

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
| 1. Score a page for being about where the traveller applies from | 09-02 | 126 | **The scorer's ordering is consumed by nothing** — the pool goes to the model unsorted with scores withheld, so `score_link` reaches a corridor as a *boolean*. Shipped as a swap and cut back to adding only: the withdrawal removed **25 pages from the pool and added none**. Admits 35 of 186,596, and 3 of its 4 families already held the answer in stored text — which is the argument for item 31. Also: `_describes_country` could not read `united-kingdom` in a path, so every multi-word country was invisible unless the anchor said it |
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


**Singapore's hand-written configuration is India-specific, and a traveller can now read that.**
Found 2026-08-28, entry 98. `destinations.yaml` names `sg_ica_india_visa_details` — a page about
Indian travel documents — as `application_document_source_ids` for *every* traveller, so a Filipino
request fetches it as a required source and the model's explanation mentioned it: *"the listed
India-specific document checklist does not apply to this traveller"*. Honest, and a configuration
artefact leaking into a plan. It also broke the visa-free shape until entry 98 conditioned the
empty-checklist guard, which is how it was found. The seven hand-configured destinations should be
checked for the same shape — a per-nationality page pinned as if it were the country's checklist —
and the fix is per-destination, not a code change. Note that the *automatic* path does not have this
problem: it resolves the corridor for the traveller who asked.

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
