# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

**How to read this file.** **Now** is what to pick up, in the order written; **Next up** follows it;
**Later** is real but not urgent; **Done** keeps finished work because what building it found is usually
why the item after it exists; **Smaller things** are one-paragraph defects with no owner yet.

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

**The owner decided to rebuild the other 50 and parked it until model adjudication moves to a new
OpenAI API key** — item 48, now in Later. A build itself calls no model; the key gates the
corridors run afterwards.

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
| **Now** | 5. Answer the challenge, honour every `robots.txt`, and get a checklist out of France | `next` |
|  | 56. Make the written plan shorter | `next` |
| **Next up** | 2. Amend the trust rule for governments with no marker, and for Schengen | `soon` |
|  | 4. Decide the client-side retrieval question | `soon` |
|  | 7. Put it somewhere others can open it aka deployment | `soon` |
|  | 20. Make the stores substrate-swappable and durable | `soon` |
|  | 55. Take the traveller from Ofself's shared identity, through one adapter | `soon` |
|  | 57. Stream the plan to the screen as it is written | `soon` |
|  | 59. Guard the 272K-token price threshold | `soon` |
| **Later** | 58. What is left of model-call cost and research latency | `later` |
|  | 48. Rebuild the other 50 corpora so they keep their search seeds — parked until the new OpenAI key | `later` |
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
documentation said it was — the corrections table in [CLAUDE.md](CLAUDE.md) has over two hundred and fifty rows and every
one cost a session. **Prefer running a corridor to reading a code path**, and when an item below
proposes a fix, measure the proposal before implementing it. Several items here were written from a
careful reading and were wrong.

---

## Now — pick these up in this order

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

### 56. Make the written plan shorter — `next`, **measured live 2026-09-15 (entry 174); the wording trims wait on the owner's read**

**Why it matters.** Writing the plan is the longest single wait in a request and happens on every
request, because a plan is never stored (entry 44): about **29s of a fresh corridor's ~55s** and
nearly all of a repeat's ~24s (entry 171). Its time tracks what it writes, about 11 ms a token.

**Where it stands — entry 174, 99 live plan calls on five fixed packets.**
- **Trim 1, short source ids, is declined.** It was the one trim claimed to change nothing a
  traveller reads. In 48 calls it gave **two refused plans** and **two wrong "no visa required"
  answers for Japan `IN/GB`**, status `verified`, read off MOFA's visa-exemption list. The 48 calls on
  today's ids gave neither.
- **Trims 2–4 together take the call from 25.1s to 21.4s** (−15%) and its output from 2,314 to 1,947
  tokens, with nothing refused. Money barely moves, about $0.003 a request. Germany, Japan and the
  Netherlands save; Canada and Singapore are inside the noise.

**Open — the owner's decision, one trim at a time.** Entry 174 has what each one changes, read side
by side.
- **Trim 2 — one quote of at most 150 characters.** It saves most, about 1.2s. It gets there by
  quoting headings — "Completed Visa Application Form (Sample)" — which support the claim less, and
  quotes exist for the owner's check (entry 156).
- **Trim 3 — a few words of "why it applies" where nothing conditions the document.** About 1.0s, and
  the least lost.
- **Trim 4 — at most 40 words an action and 15 a timing.** About 0.8s. Japan kept its processing
  window in one arm and lost it in the other.
- **Whether any of it is worth doing next to item 57**, which does not shorten the wait but makes it
  feel much shorter.

**If a trim ships.**
- **Change the prompt only.** `QuoteChecker`'s bounds stay as they are, since a longer quote than
  asked for is still a real one.
- **Re-run Japan `IN/GB` and Singapore `PH/PH` several times each first.** Rule 8e's bounds live only
  in the prompt; they held 16 of 16 on Japan's exemption list and broke twice under a packet change.
- **Update the tests** that assert on the prompt's wording (`test_openai_extraction.py`).

**Constraints that do not move.**
- **Do not lower `openai_reasoning_effort`** to cut the hidden reasoning without an accuracy
  measurement (CLAUDE.md).
- **A visa-free plan still lists only the entry duties its sources state**, with no minimum (entries 95
  and 96).
- **Every quote is still checked against the retrieved text** (entry 156), and a requirement still needs
  a designated document source (`validate_absent_checklist`).
- **Do not rename source ids or field names in what the model reads** without re-measuring as entry
  174 did. Field names are a fifth to a quarter of a visible plan and look like the next lever; trim 1
  is what that kind of change did.

**How to measure it again.** Rebuild each packet from a stored corridor and the warm page cache —
`AutomaticDestinationService.destination_for`, then `LiveSourceFetcher.fetch`, which costs no search
and no model call. Call the real extractor with a generator that swaps the prompt, so validation and
`var/usage/` see every call. Compare several calls an arm, on output tokens as well as seconds, and
tally the visa decision per arm, not only the length.

## Next up

### 2. Amend the trust rule for governments with no marker, and for Schengen — `soon`, **and Germany is the worked example**

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
5. **Put a key or a rate limit on `POST /visa-plans`.** It is unauthenticated and a cold corridor spends
   real money — search plus two model calls — so a public URL is a public wallet. Ofself's login
   is the likely answer; plan this step with item 55.

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
- **Three places assume the one input path:** `create_visa_plan` reads `request.traveller` directly,
  the page's form pre-selects from `DEFAULT_TRAVELLER_PROFILE` (`api/routes.py:49`), and `app.js`
  posts three form fields.

**Do:**
1. **Make where the profile comes from an injected dependency.** A small protocol with one method
   returning this request's `TravellerProfile`, whose first implementation is today's request body.
   `create_visa_plan` asks the dependency instead of reading `request.traveller`. `Depends` is
   already how the plan service and automatic destinations reach the route, so this follows the
   pattern in `api/dependencies.py`.
2. **Move `normalise_country` out of `api/schemas.py`** to where both adapters can use it, so an
   identity from Ofself passes the same "no reference data, refused" check a typed one does.
3. **Once Ofself's schema for this project exists, write its adapter as one module**, Ofself
   identity to `TravellerProfile`, tested on fixture identities with no network. Nothing past the
   edge should change.

**What this project asks Ofself for is ours to state now; the adapter is not.** The list is
`TravellerProfile`'s fields and no more: passport nationality and passport type, country of
residence, and the optional city, residence status and permission expiry. **Purpose stays a
question on the page**, because it belongs to a trip, not to a person. Field names and format are
Ofself's, and a seam designed against a guessed schema lands in the wrong place, so steps 1 and 2
can go ahead now if they stay small and step 3 waits.

**Open, and for the owner to settle with Ofself:** whether this project writes the requested schema
or Ofself does, and whether a field says which app wrote it and when.

**Six things an adapter must not lose, each easy to lose by mapping fields one to one:**
1. **Ask for only the fields that select guidance, and drop anything else that arrives.** The shared
   identity will hold a name, a date of birth, a passport number, an address. `build_research_packet`
   (`research/openai_extraction.py:108`) sends `traveller_profile.model_dump()` to OpenAI **whole**,
   so any field added to `TravellerProfile` goes to a third party on every plan. Request the list
   above; the adapter drops what the plan does not use, and `TravellerProfile` is not widened to
   hold it. Keep `StrictModel`'s `extra="forbid"`, which stops a stray field at construction.
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

**Plan it with item 7.** Ofself's login is also the likely answer to item 7's fifth step: `POST
/visa-plans` is unauthenticated and a cold corridor spends real money.

### 57. Stream the plan to the screen as it is written — `soon`, **a UX improvement, added 2026-09-15**

**Why it matters.** A fresh request takes about 55s and a repeat about 24s (entry 171), and the
traveller sees nothing until the whole plan arrives. More than half of a fresh request, and nearly
all of a repeat, is the model writing the plan. Streaming would not shorten any of that, but text
could appear seconds after the plan call starts rather than when it ends. **Item 56 shortens the
wait; this makes it feel shorter, and the two do not compete.**

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

**Open for whoever picks it up:** whether streaming progress alone is enough, and whether any plan
content can be shown before validation without breaking entry 6's rule against unverified claims that
would alarm a traveller if wrong.

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

---

## Later

### 58. What is left of model-call cost and research latency — `later`, **split from item 19 on 2026-09-15 (entry 173)**

**Where it stands.** A fresh corridor that resolves costs **$0.251 in model calls**, plus about $0.054 of
search, and takes about **55s**: ~25s of research and ~29s of writing the plan (entry 171). The plan
call's wait is items 56 and 57; the 272K price threshold is item 59. The instrumentation is on: every
model call goes to `var/usage/model-calls-YYYY-MM-DD.jsonl`, and every stage's seconds to the recall
log's `phase_seconds`.

**Cost, biggest first — none of it decided.**
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

### 48. Rebuild the other 50 corpora so they keep their search seeds — `later`, **parked 2026-09-15 by the owner until the new OpenAI key**

> **Parked 2026-09-15 by the owner.** The matched test is conclusive enough to rebuild, and the
> rebuild waits until model adjudication moves to a new OpenAI API key. **A corpus build calls no
> model** — it spends Brave search and crawl time, about $17 and 13 hours for the 50 — so the key is
> not what the build uses; it is what every corridor run afterwards uses, including any
> re-measurement. When it is in: `visa-discover corpus --country XX` for each of the 50 still on
> the old build (NO, TH and JP are done), then the `pre-seeds-*.bak` copies in `var/corpus/` and
> `var/pagetext/` can go once nobody needs the old arm.

> **Worked 2026-09-15 (entry 161): root seeding rejected, a different discovery defect fixed, and its
> benefit not yet measured.**
>
> - **Root seeding, probed on eight hosts** with the build's own crawler and nothing written: **0 of
>   9 target pages reached**. Thailand's root *is* the arrival-card form and links nothing; Japan's
>   London embassy root answers `404`; Spain read 57 pages and found nothing that scores; the UK fee
>   host drifted into 147 GOV.UK pages. By the rule below that is "worse", and Thailand's positive did
>   not appear. Not built.
> - **The gap was a build discarding its own search seeds.** `crawl` records links found on pages,
>   never the seeds, and a PDF seed was never read. Today's build queries return 146 of Norway's 194
>   seeds, 122 of Thailand's 152 and 167 of Japan's 282 that the corpora did not hold — including
>   Norway's January 2024 checklist, Thailand's arrival card and Japan's London-embassy tourism page,
>   all pages corridors had been getting only from live search. **Fixed in `corpus_build.py`**, with
>   two tests shown failing on the old code; the request path is unchanged.
> - **Norway, Thailand and Japan were rebuilt with the fix**: 174, 127 and 156 seeds kept, and all
>   three pages are now held.
>
> **What is left, in order:**
>
> 1. **~~Measure whether it changes an answer~~ — done the same day (entry 161).** 24 matched runs
>    over `norway/IN/IN`, `thailand/IN/GB` and `japan/IN/GB`, old corpus against new, with search
>    off and on:
>    - **Thailand went from no decision to resolved in 4 of 4 runs.** The decision came from the Thai
>      foreign ministry's 2026 visa-exemption summary, a kept seed that live search never returned.
>    - **Japan filled every role from its London embassy with search off**, where the old corpus
>      could not.
>    - **Norway did not change.**
>
>    Cost with search on: **about +9% a corridor**, all of it selection input.
> 2. **Decided by the owner: rebuild the other 50 — parked until the new OpenAI API key is in**,
>    per the note at the top of this item.
> 3. **The two allocation findings below** — fair shares between unequal hosts, and `www.` counted as
>    its own host — are untouched.
>
> The item as first written follows; its root-seeding experiment is the part now answered.

**Entry 130 proposed seeding every trusted host's root and deliberately did not build it.** This is
that experiment, plus the thing measuring it turned up: **item 35 is two problems, and the fix for
the first can make the second worse.**

> **Discovery** — the build enters a host below the page that matters. **1,148 of 2,222 hosts
> across all 53 corpora (51.7%) have pages and their root was never visited at all**; only 20 roots
> were seeds. A build seeds from search results, and a search result is a **page, not a site**, so a
> host enters the corpus wherever the engine pointed. Thailand is the worked case: three
> `tdac.immigration.go.th` pages, all children of one seed at `/manual/en/`, and the arrival-card
> form linked from none of them.
>
> **Allocation** — once inside a large site, the budget goes to the wrong part of it. **These are
> not the same problem and must not be merged**: the first is about where a crawl starts, the second
> about what it spends. Seeding roots without fixing allocation feeds the second one more frontier.

**Measure these five, and the fifth is the one that can veto the change.**

1. How many pages does root seeding newly **discover** — recorded entries that no previous build held?
2. How many of those are **relevant**, scored offline by role vocabulary rather than by eye?
3. How many previously **search-only load-bearing** pages become corpus-reachable? Entry 129's
   24 are the list to check against, and it is the only measurement that maps to a traveller.
4. What does it **cost**: pages fetched per useful page found, against `DEFAULT_CORPUS_PAGES` of
   1,200 and `DEFAULT_CORPUS_PAGES_PER_HOST` of 400.
5. **Does it make allocation worse** by giving a huge irrelevant subtree more frontier to expand?

**The control set, chosen so each case can fail differently.**

| | why it is in the set |
| --- | --- |
| **Thailand** | the known positive: TDAC's form is one hop from a root nobody visited |
| **Bulgaria** | the **negative** control: `mfa.bg` refuses this client at every address (entry 131), so nothing here should move it |
| **Spain** | `www.interior.gob.es` holds 1,930 pages and **109 were opened**; the sample is press-release pagination |
| **Finland** | `um.fi` holds 1,736 and opened 173; a parameterised asset-publisher space |
| **Greece** | `portal.immigration.gov.gr`, 428 pages on sequential numeric ids |

**What "worse" would look like, decided in advance:** a root seed that raises pages fetched on a
host without raising role-scoring pages found on it. If Spain and Finland show that and Thailand
shows the positive, the answer is **not** "seed roots" but section-aware crawling — a notion of
*part of a site* the crawler does not currently have.

---

**Three things measuring this turned up that are separable from the experiment.**

**A per-host fair share treats unequal hosts equally.** Thailand opened 1,041 pages across 63
hosts and the top hosts each got **41 or 42** — Uthai Thani province, population ~330,000, took the
same share as the national immigration service. 31 of those 63 hosts are provincial offices, so
Thailand's national guidance was diluted 31-fold: **44 pages for `www.immigration.go.th`, 3 for
TDAC, 2,615 recorded for the provinces.** The provincial sites are WordPress installations whose
category and archive pages present an effectively unbounded link graph. **The crawler is not being
greedy; it is being fair between things that are not equal.**

**~~`host_of` does not fold `www.`, so one authority can take several shares~~ — fixed 2026-09-15,
DECISIONS entry 163.** Bulgaria opened 587 pages: `www.mvr.bg` 149, `mvr.bg` 161, `e-uslugi.mvr.bg`
110 — 420 of 587 on the interior ministry across three spellings — while `mfa.bg` opened 0. Nothing
documented it as deliberate, and 44 of 53 corpora held such a pair. The crawl budget now folds a
leading `www.`; trust, politeness and reporting keep the exact host.

**~~And Bulgaria's zero may be a stale failure~~ — re-run on 2026-09-04, and it is not (entry
131).** The hypothesis was that its 175 `mfa.bg` failures were stale, because three of those URLs
answered `200` in a browser. The rebuild crawled **7,149 pages for 193 new addresses and 21 newly
opened**, `mfa.bg` stayed at **0 opened of 399**, and the failure count went **up to 176**.

Asked with this program's own user agent, `https://mfa.bg/en` redirects to
`validate.perfdrive.com` — **Radware Bot Manager, serving a CAPTCHA**. It is rate-shaped, so
`/en/155` answers `200` in the same session, which is why a browser check could not see it: **a
browser passes the bot check, so looking with one cannot tell you whether your crawler is being
intercepted.**

So Bulgaria is a **permanent ceiling**, not a crawl gap — completing a bot check is prohibited
outright, and this interception lands on a third-party domain that could never be evidence anyway.
It stays in the control set below only as a **negative** control: no crawl change should move it.
The reason string is fixed (the crawl now names the landing host); the refusal is not, and must not
be.

**Why:** entries 129 and 130. Item 35 owns the crawl; this is the measurement that says which half
of it to change, and entry 82 is the standing warning — "a surplus goes to the largest host" was
found by measuring a budget change that looked obviously good.

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
