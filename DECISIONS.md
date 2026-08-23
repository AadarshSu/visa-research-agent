# Decisions

Why the project is shaped the way it is, including what was tried and rejected. The reasoning is
recorded because it is the part that cannot be recovered from the code later — a deleted feature
leaves no trace, and a rule with an obvious-looking alternative invites someone to "simplify" it
back into a bug.

Newest first. Add an entry when a decision is made, not afterwards.

---

## 48. The crawl was rediscovering a map the corpus already had; the corpus becomes a routing index
**2026-08-23 · measured; decided; NOT implemented**

Entry 47 made recall monotonic and said plainly that it bought no speed. This is the measurement of
where the time actually goes, and it changes what the request path should do.

### Where a cold corridor spends 54 seconds

Instrumented live, `canada/GB/GB/tourism`, 2026-08-22:

| Phase | Time | Share |
| --- | --- | --- |
| search — 15 queries | 9.1s | 17% |
| **crawl — 40 pages, per-host politeness** | **33.6s** | **62%** |
| fetch shortlist — 25 pages | 1.1s | 2% |
| adjudicate — one model call | 10.8s | 20% |

Fetching is small only because the evidence cache was warm; adjudication is irreducible.

### The crawl contributed nothing

Of the 25 shortlisted pages, 14 were found by the crawl — and **all 14 were already in the corpus**.
Zero shortlisted pages came from the crawl and not the corpus. **The crawl spent 62% of the corridor
re-deriving a link graph the offline job had already mapped.**

That is not a defect in the crawl. It is what a crawl is *for*, and before a corpus existed it was the
only way to get the map. It is now redundant for any destination that has one.

### Corpus-only resolves the same corridor, and needs no prior proof

Scoring the corpus and shortlisting from it, with **no search and no crawl at all**: 19 of the same 25
pages, and **all three role-filling pages kept** — `entry-requirements-country`, `fees.asp`,
`check-processing-times`.

**And it is not circular.** All three have `first_seen` at 14:30–14:31, from the **offline job**, not
from entry 47's write-back. So this does not need the *corridor* to have been proven, only the
*destination* to have been built — which is the property that makes it apply to a nationality nobody
has ever asked about.

### But consuming the whole corpus scales the wrong way

Scoring all 3,216 entries for one corridor costs **3.6s**, and grows with the corpus. Left alone it
would eventually cost more than the crawl it replaced — the corpus would become the new bottleneck.

So the corpus is used as a **routing index**, not as a candidate list. `score_role_vocabulary` is
corridor-independent, so it can be computed **once at build time**, stored on the entry, and used to
pre-filter before anything corridor-specific runs:

| top-N by stored vocabulary score | corridor scoring | overlap with the real shortlist | role pages |
| --- | --- | --- | --- |
| 100 | 149ms | 20/25 | **2/3 — loses one** |
| 200 | 289ms | 22/25 | 3/3 |
| **400** | **575ms** | **24/25** | **3/3** |
| 3,216 (all) | 3,633ms | 25/25 | 3/3 |

**400 is the chosen bound**: 6× cheaper than scoring everything, keeps every role page with margin, and
is *bounded* — it stays 575ms whether the corpus holds three thousand pages or thirty thousand.
Computing the vocabulary score for all 3,216 costs 95ms and is paid offline.

**400 is calibration, not derivation**, exactly like the shortlist's 25 (entry 40) and the domain cap's
5 (entry 22). One corridor, one destination. It should be re-checked per destination, and 100 is
demonstrably too low, which is the useful half of the table.

### Decided: drop the crawl from the request path, keep search

| | Path | Corridor phase |
| --- | --- | --- |
| Today | search + crawl + fetch + adjudicate | 54.2s |
| **Chosen** | corpus-routed, **no crawl**, search kept | **~21s** |
| Rejected for now | corpus-routed, no crawl, no search | ~13–17s |

**Search is kept, and the reason is a gap that has been measured on one dimension and not the other.**
`corridor_queries` interpolates purpose, nationality and residence. Purpose is now swept offline (four
values, entry 47) and that is why the corpus contains what it does. **Nationality is 198-valued and has
never been checked**: nothing shows whether a nationality-specific query surfaces pages the offline
sweep misses. Dropping search would trade a known 9.1s for an unmeasured recall risk on exactly the
dimension not yet examined — and recall is the thing this whole line of work exists to protect.

Dropping search becomes correct once the superset bar holds across several destinations with
nationality-varied corridors. Then the crawl and search both leave the request path for good.

### How settled this is

**The measurements are solid; the design on top of them is one session's answer and has not been argued
against.** The phase split, the fourteen-of-fourteen redundancy, the top-N table and the non-circularity
check are all reproducible and should be trusted. That the right response is *a flat top-N index plus
dropping the crawl* is a judgement made quickly, on one destination, by whoever also took the
measurements — which is the weakest position from which to design. [TODO.md](TODO.md) item 22 lists
where it is most likely wrong and asks the next session for its own view before building.

What is not open for revision is below, and in the search decision above.

### What must not be lost when the crawl goes

- **A destination with no corpus still crawls.** Removing the crawl is conditional on having a map, not
  a blanket removal; a country nobody has built must behave exactly as it does today.
- **The crawl is where `crawl_failures`, `blocked_urls` and `disallowed_urls` come from**, and those
  feed `inaccessible_domains`, `decision_blocking_urls` and the notes a refusal is made of (entries 27,
  32, 36). Without a crawl those have to come from the shortlist fetch instead, or a corridor will
  quietly stop reporting that an authority refused it — which is the reporting discipline entry 18
  exists to protect, lost as a side effect of an optimisation.
- **`_readable_only` reads crawl state** to drop pages already proved unreadable. With no crawl it has
  no state to read, so the corpus's own `status` is what should stand in.

---

## 47. The candidate set ratchets: corpus ∪ live, pinned by what already worked, fed by write-back
**2026-08-22 · implemented**

Entry 46 left the corpus not a superset of what a corridor finds. The fix is not to make the offline
job exhaustive — **measurement says it cannot be** — but to make the candidate set *monotonic*.

**The property, stated exactly.** For a given corridor the candidate set is **non-decreasing** across
runs. Not identical, which would freeze recall; never smaller, which is what lost Canada its answer on
2026-08-21. Run two sees everything run one saw, plus whatever else turned up.

### Why an offline sweep cannot close the gap, which is the measurement that decided this

Entry 46's gap was blamed on traveller-free queries, and the specific term turned out to be the
**purpose**, not the nationality — four values, not 198. So the obvious fix was to sweep purposes
offline, and that was done: `corpus_queries` gained `corridor_queries`' purpose templates, and a Canada
rebuild went from 30 queries to 70 and from 1,071 entries to 3,130, now with depth genuinely exercised
(1,977 at depth 1, 972 at depth 2, 154 at depth 3).

**It still did not contain the page.** And the reason is the one that settles the architecture: the
exact query that had surfaced `supporting-documents` — `site:canada.ca tourism visa documents required` —
**was re-run, and search did not return it this time.** Search is nondeterministic *at the source*, so
no amount of offline query engineering can guarantee a superset. Only keeping what a live run actually
found can.

Measured against the live run's 24 fetched pages: 18 held, 6 apparently missing, of which **one was an
alias** — `cic.gc.ca/english/visit/visas.asp` sitting in the corpus as `www.cic.gc.ca/...`. Canada's
3,130 stored URLs are 2,996 distinct pages. So `canonical_key` folds scheme, case and a leading `www.`
for *comparison only*; the stored URL is untouched, because that is what gets fetched.

### The three mechanisms

- **Union.** `corpus ∪ live discovery`, seeded where candidates are assembled. Search still runs; the
  corpus supplies what search forgot, and search supplies what the corpus lacks. Trust is applied when
  the corpus is *read*, so a domain later removed from the registry stops being offered without anyone
  rebuilding a corpus and without deleting what was found.
- **Pins.** A page that already filled a role for this corridor keeps its shortlist place regardless of
  ranking. **No new store**: `StoredCorridor.resolved.sources` was already the proven set, used only as
  a whole-answer cache. This is what stops the corpus making the scorer *more* load-bearing — the pool
  grows from ~471 to ~3,000, and entry 40 says a page ranked out is unrecoverable. The age check
  deliberately does not apply: a corridor too old to serve as an answer is still a good hint about which
  pages matter.
- **Write-back.** What a run discovered folds into the corpus, additively. **This is not the fallback
  entry 44 rejects, and the direction is the difference.** That was *deciding a corridor* from a live
  search after a corpus miss, so the answer depended on that day's search. This keeps what a run already
  found, so later runs start from more. It cannot change the current answer — the resolution is made
  before it runs — and widens no trust.

### Measured, end to end

| | |
| --- | --- |
| Before | 18 of 24 fetched pages held; 5 genuine gaps |
| After one corridor run through the new path | **24 of 24 held** |
| Proven entries marked | 3 — the pages that filled roles |
| Offline: a total search failure | **loses zero candidates** (`test_the_candidate_set_never_shrinks_between_runs`) |

### One bug worth keeping, because it made the strongest tier unreachable

`status="proven"` was set only for pages in `resolver.discovered`, which correctly excludes anything the
corpus already held — a page from the corpus is not a discovery. But the common case is that the
*answering* page came from the corpus. A live Canada run wrote 86 entries and **zero** proven ones, so
the one tier that is never evicted could never be entered. Role-filling pages are now written back
whether or not this run discovered them, because proven is about answering, not about finding.

Status is also strictly monotonic now (`_STATUS_RANK`): a single `502` on a later crawl must not demote
a page that has answered a corridor, or its retention tier would drop with it.

### Still open

- **Live discovery has not yet been decayed away.** The corridor still spends its searches every cold
  run. Turning that off for a proven, fresh corridor is where the cost goes to zero and determinism
  becomes total; it is gated on the superset bar holding across more than one destination.
- **Eviction is designed and not built.** 723 of Canada's original 1,071 entries scored zero on role
  vocabulary, so the Noise tier is most of the store. Nothing evicts yet, so the corpus grows.

---

## 46. The corpus is built, and it is not yet a superset of what a corridor finds
**2026-08-22 · implemented, with a measured gap that gates item 19**

Entry 44's store exists: `discovery/corpus.py` holds a country's pages, `discovery/corpus_build.py`
gathers them, and `visa-discover corpus --country CA` runs it. Canada, twice:

| Run | Queries | Seeds | Crawled | New | Held |
| --- | --- | --- | --- | --- | --- |
| `--pages 60`, 36s | 30 | 203 | 355 | 355 | 355 |
| `--pages 200`, 97s | 30 | 203 | 1071 | 716 | **1071** |

The additive merge behaved: all 355 entries from the first build survived the second with `times_seen`
at 2, and nothing was dropped. **`entry-requirements-country.html` sits in the corpus at depth 1** —
the page whose absence refused `canada/GB/GB/tourism` on 2026-08-21 is now durable, which is what this
was built to do.

### What the corpus does differently from a corridor, and why each is deliberate

- **No traveller.** Queries name the destination only, and links are scored with
  `score_role_vocabulary` — extracted from `score_link` rather than copied, so the corridor-independent
  half has one implementation. A corpus guided by one nationality's vocabulary would be a corpus
  quietly built for that nationality.
- **Pages about other countries are kept.** `resolver.py` vetoes them, correctly, because for one
  traveller a page about Brazil is noise. The corpus serves every corridor, so Canada's per-nationality
  pages are exactly what a later India corridor needs. Archived paths and site furniture are still
  rejected: those are not guidance for anybody.
- **It never deletes.** A crawl finding less than last time is ordinary — search moves, a host times
  out — and treating that as a withdrawal would rebuild the failure the corpus exists to prevent.
- **Trust is applied when it is read, not when it is written.** A corpus outlives the registry row that
  built it, so narrowing `authority_domains.yaml` takes effect without anyone rebuilding every corpus,
  and without deleting what was found.
- **A corrupt corpus raises rather than reading as an empty country** — unlike `corridor_store.py`,
  because a corridor that will not parse is safely re-resolved while a corpus is the *candidate
  source*, and treating corruption as "no pages here" would disguise it as a country nobody built.

### The gap, which is the reason this entry is not a success report

**`.../visit-canada/supporting-documents` is absent from a 1,071-entry corpus, and the corridor run
fetched it the same day** — scored 64.0 for `document_checklist`. So the corpus is **not** a superset
of what a corridor finds.

The cause is the thing that makes it corridor-independent — but **the specific diagnosis written here
first was wrong, and the recall log had the answer sitting in it.** This paragraph originally said
`corridor_queries` asks `site:canada.ca Canada visa requirements United Kingdom` and blamed the
*nationality*. Checked 2026-08-22, the page entered the corridor run as a **search seed** from:

```
site:canada.ca tourism visa documents required
```

which is `corridor_queries`' second template, `f"site:{domain} {corridor.purpose} visa documents
required"`. **The discriminating term is the purpose, not the nationality**, and that changes the size
of the problem completely: purpose has **four** values where nationality has 198, so the measured gap is
closable offline with four passes rather than being a Cartesian trap. Whether nationality-specific
phrasing surfaces anything unique is **untested** and must not be assumed either way.

**Two further things this got wrong by inference rather than measurement**, both corrected on the same
day and both worth keeping visible because the habit is the point:

- **Depth was never exercised, so "depth did not close it" claimed more than was tested.** Of Canada's
  1,071 entries, **1,032 sit at depth 1** and only 39 deeper. The build produced **203 seeds** against a
  **200-page budget**, so it spent the whole allowance fetching seeds and barely crawled at all. The
  offline job's headline advantage over the request path — no latency bound, so it can go deeper — is
  not currently being realised. That is the same seed-frontier exhaustion already recorded for the
  corridor crawl under *Smaller things*.
- **Two-thirds of the corpus is noise.** Scored with the corridor-independent `score_role_vocabulary`,
  **723 of 1,071 entries score zero** and only 79 score 20 or above. Retention now has a measured basis
  instead of a guessed one.

The lesson repeats one this file records at least four times already: this was described from reading a
code path when a recall log written for exactly this question was one command away.

**This gates [TODO.md](TODO.md) item 19.** Switching the request path to corpus-only today would trade
variance for a *smaller* candidate set — better determinism, worse coverage, which is not the trade
entry 44 argued for. Two fixes, not exclusive: widen `corpus_queries`, and let a corridor run feed what
it discovered back into the corpus. **The second is not the fallback entry 44 rejects** — that was
*deciding a corridor* on a live search after a corpus miss; this is keeping what a run already found,
which is additive, widens no trust, and cannot change an answer on its own. It still needs arguing in
writing before it is built.

**And this is the second time in two days that building the thing moved the diagnosis.** Entry 44's
motivating number had already weakened when three back-to-back Canada runs produced no variance at all;
now its mechanism turns out to be incomplete in the other direction. Neither kills the corpus — the
answering page *is* durable now, and offline depth is real — but the case for it is narrower than the
entry as first written, and both corrections came from running it rather than reasoning about it.

---

## 45. The corridor command reaches the registry, and the test suite stops being allowed on the network
**2026-08-22 · implemented**

`visa-discover corridor` read `get_destination_registry()` and nothing else, so `--destination canada`
answered *"Unknown destination: canada"* while the API resolved that same corridor perfectly well.
Seven destinations are configured; forty have a registry row. **Every live check of a registry
corridor has therefore been run from a throwaway script** — which is why nobody had a candidate list
until entry 43, and why the flip rate item 17 asks for had not been counted.

It now falls back to `prepare_destination`, and a configured destination still wins where it has
domains, because its hand-written sources carry authorisations the registry knows nothing about —
Singapore's VFS provider is named by an official page, and that naming exists only in
`destinations.yaml`.

**`--runs N` resolves the corridor N times and reports what varied**, which is item 17's counting.
It deliberately does not go through `AutomaticDestinationService`, because that reads the corridor
store, and a stored corridor would answer runs two and three from run one — hiding exactly the thing
being measured.

### What this cost, and it is the finding worth keeping

**Removing that early exit made the test suite perform a live corridor resolution.** The existing
test asserted that `united-states` exits 3; with the fallback in place it went on to resolve — 21
seconds, live Brave searches, live page fetches, and a live model call, because `.env` sits on a
developer machine and `settings` reads it. A 243KB recall record was written for a corridor nobody
asked for.

**Nothing caught it.** `AGENTS.md` has always required that tests never touch the network or an LLM,
and until now that rule was upheld entirely by convention plus the seams — `transport=`, `now=`,
`renderer=`, the fake generators. Convention holds right up until a change adds a code path that has
no seam, and `run_corridor` was one: it built its own resolver from global settings and went
straight to the network. The test "passed" for years by relying on the command bailing out early for
an unrelated reason. When that reason went away the failure surfaced as an exit-code mismatch, and
the network access was invisible in the output.

**So the rule now has teeth**, and both halves matter:

- `tests/conftest.py` refuses `socket.socket.connect` for every test. Patched at the socket rather
  than at `httpx`, because that is the one chokepoint every client, resolver and driver reaches, so
  a new dependency cannot route around it.
- It raises `NetworkAccessDuringTest`, **not** an `OSError`. Several paths under test catch `OSError`
  and `httpx.HTTPError` and turn them into an ordinary "unreachable source" outcome — which is the
  reporting this project cares most about, and which would have swallowed the guard and let the
  offending test pass while describing the block as an authority being down.
- `run_corridor` takes a `resolve=` seam, so the command can be tested without one.

The guard found the offending call on its first run and nothing else in 390 tests, which is the
evidence that the suite was otherwise honest. It also took the suite from 4.0s to 2.7s, all of which
was the one test making real requests.

**The lesson is the one this project keeps relearning, one level over:** a rule that is only a
convention is a rule nobody is checking. Entry 36 found the `robots.txt` parser inert because no
unit test could catch it; this is the same shape — the safeguard was real, the enforcement was not,
and only running the thing showed it.

### Two defects in the variance report, both found by writing its test

Neither would have shown in a live run, and both would have quietly corrupted the number item 17
exists to produce:

- **The run count came from the recall records.** A run whose record could not be read simply
  vanished, so two runs where one write failed described themselves as one run. Entry 43
  *deliberately* swallows a recall-log write error rather than costing a corridor its answer, so
  this was reachable by design. Outcomes now come from the resolutions, which always exist, and
  records only supply candidates; when fewer records than runs survive, the report says so **before**
  the numbers, because otherwise an absence reads as "this run did not find it" rather than "no
  record".
- **A stale record could be read as this run's.** The log is keyed by corridor and keeps only the
  newest run, so a record from last week sits exactly where the second run looks. Comparing run 2
  against last week's run 1 would invent variance that never happened. Records are now accepted only
  when `recorded_at` is at or after the moment that run started.

---

## 44. A country's page corpus is persisted, and search leaves the request path
**2026-08-21 · decided; not implemented**

TODO item 17 asks what a corridor that flips between runs should do. This is the answer: **option 3,
widened.** The set of pages a corridor may consider stops being re-derived from search on every request
and becomes a stored corpus per **country**, populated by a deliberate offline job. Which of those pages
answers *this* traveller is unchanged and stays live.

**The evidence is entry 43's, and it is a measurement rather than an inference.**
`canada/GB/GB/tourism`, twice within an hour, same code, same five domains: refused once, resolved once.
On the resolving run `entry-requirements-country.html` was candidate **15 of 470** at 53.4 — comfortably
inside 25 shortlist places — and arrived **two ways**, as a `site:canada.ca` search seed *and* by crawl at
depth 1 from `check-visa-eta.html`. On the refusing run search did not return it at all. So the page is
not marginal and the scorer is not at fault: **recall flipped, and a resolved corridor is evidence only
that this run of the pipeline worked.** The corridor store then keeps the lucky answer for three weeks,
so a traveller in week one and a traveller in week four get different products from identical code.

> **Measured 2026-08-22, and it weakens the urgency of this entry — recorded here rather than left in
> the TODO, because an entry whose motivating number moved should say so where it is read.** Three
> back-to-back runs of `canada/GB/GB/tourism` with the cache cleared produced **471 candidates and no
> variance whatever**: all three resolved, and `entry-requirements-country.html` arrived every time by
> *both* routes. So the flip rate is "0 of 3 back-to-back", not 0 — the runs were two minutes apart,
> where the observed flip was an hour and the original divergence two days — but it does mean **the
> case for this entry now rests on crawl depth and latency, not on a measured frequency of flipping.**
> The one flip entry 43 caught remains a single observation. TODO item 17 keeps the gapped re-run that
> would settle it.

**This is entry 34's move one level down.** That entry took *who to believe* out of the request path
because domains do not vary by corridor. **Which pages exist** does not vary by corridor either. Only
which one answers a given traveller does:

| | Who to believe (domains) | **Which pages exist (corpus)** | Which page answers *this* traveller |
| --- | --- | --- | --- |
| Corridor-dependent? | No | **No** | Yes |
| How many | ~3–5 per country | **~20–50 per country** | one per role |
| Decided by | a rule, once per country | **a crawl, offline, refreshed** | the model, every corridor |
| Lives in | `config/authority_domains.yaml` (git) | **a store** | computed per request |

`ARCHITECTURE.md` has carried this as a two-column table asserting that URLs *are* corridor-dependent.
That is true of the chosen URL and false of the corpus, and the conflation is why discovery pays search
cost, at request latency, for a question that does not change between travellers.

### Why this is not merely caching what search returns

- **Recall effort moves off the latency budget.** The depth-0 budget exhaustion recorded under *Smaller
  things* — every seed popped before any child, so depth-2 discovery is lost — is a compromise forced by
  a 60-second request. An offline job has no such bound: deeper hops, sitemaps (item 10), far more
  queries per country. Canada's page was reachable at depth 1, and the pages currently lost are deeper.
- **The shortlist stops being a recall gate for most countries.** Entry 40 widened it to 25 because a
  page ranked out is unrecoverable. Choosing 25 from a curated 20–50-page corpus is a different problem
  from choosing 25 of 470 crawl candidates, and the scorer's known faults stop being load-bearing.
- **Cost amortises across nationalities.** One population crawl of Canada serves every corridor into
  Canada. Up to fifteen Brave queries and a two-hop crawl leave the request path entirely.

**Trust is untouched.** A stored URL is still checked against `trusted_domains` and still fetched through
`LiveSourceFetcher`, whose `validate_route` cannot be bypassed — so a corpus entry cannot survive a later
narrowing of the domain registry, and cannot smuggle in a page that would not pass today.

### On a corpus miss: refuse, and flag the country

Entry 38's rule, applied to pages. A country missing from `authority_domains.yaml` is refused, never
bootstrapped live, because falling back "would silently reintroduce the per-request variance the file
exists to remove". A thin or rotted corpus is the same situation: **refuse, name what was missing, and
put the country on the repopulation queue.** Falling back to live search would restore the lottery for
exactly the requests that most need it not to be one, and would do it invisibly.

The refusal must tell three cases apart, because they have different fixes: *no corpus for this country*,
*a corpus exists but no page fills `visa_decision`*, and *stored URLs no longer resolve*. Only the third
means the corpus has rotted.

### The other three options, in item 17's own terms

1. **Re-search on refusal** — rejected. It turns a refusal into "search until something answers", which
   is how a pipeline talks itself into an answer. Item 17 already calls it the worst of the four.
2. **Widen or vary the queries** — rejected. Fifteen queries against five domains is already the cold
   path's cost (known problem 5). More queries is more surface, latency and quota for an unknown gain,
   and it leaves recall a per-request lottery with better odds rather than removing the lottery.
3. **Keep what was found** — **taken, and widened from per corridor to per country.** Strictly stronger
   at identical risk: a page found for `canada/GB/GB/tourism` also serves `canada/IN/IN/business`.
4. **Accept and report it** — rejected as a resting place, though the reporting is kept. Item 17 is right
   that this alone "does nothing for the traveller who got the unlucky run".

### What it does not fix, which matters as much as what it does

1. **A page the offline job never finds is then missed deterministically, for ever.** This trades a coin
   flip for a stable outcome. That is the better failure — a stable gap is visible, diagnosable and
   fixable where a fifty-percent gap is none of those — but it makes the population job's recall the
   whole ballgame, and it is option 3's stated risk in mirror image.
2. **A withdrawn page persists in the corpus.** Bounded by the evidence TTL and by the refresh job
   catching `404`s and off-domain redirects, which is the corpus-rot signal. Bounded is not zero.
3. **Adjudication is still a model call.** Entry 43's resolving run was `decided_by=model`, and a later
   run could judge the same shortlist differently. This removes non-determinism at the **recall** layer
   only and must not be described as doing more. Known problem 10 stands unchanged.

**So the first step is still item 17's own:** run one corridor three times and count, so the flip rate is
a number rather than an anecdote. The recall log makes that cheap, and the number is what says how much
the corpus is worth. It also settles item 17's note about item 3 — **each of the twenty corridors runs
twice, or the write-up says plainly that it did not.** One run cannot tell a corridor that works from one
that works half the time.

### This does not undo entry 43

Entry 43 chose **overwritten per corridor, never accumulated**, and that stands. The corpus is a
different artifact with a different contract, and the two must be built as two:

| | Recall log (entry 43) | Corpus (this entry) |
| --- | --- | --- |
| Keyed by | corridor | **country** |
| Lifetime | overwritten each run | **additive, never pruned by a bad run** |
| Purpose | diagnose the run that just happened | **be the input to the next run** |
| Depended on? | **No** — deleting it costs a question | **Yes** — it is the candidate source |

The row shape is nearly the same: `ConsideredCandidate` already carries the URL, title, `found_by`,
depth, `discovered_from`, the per-role scores, `shortlisted` and `fetched`. But entry 43's *"not evidence
and nothing depends on it"* is load-bearing for that file — it is what makes a diagnostic safe to run
inside a request, and what lets a write failure be swallowed. Inheriting the code must not inherit that
sentence.

### Why the corpus and not precomputed answers

The question that prompted this was whether to precompute visa research per corridor. The arithmetic
refuses it before the safety argument has to:

| Design | Records | Refresh cost per cycle | Verdict |
| --- | --- | --- | --- |
| `destination × nationality × residence × purpose` | 38.8 billion | — | absurd |
| Residence reduced to post selection | 196,020 | ~2.9M searches, ~392k model calls | categorically impossible |
| Top ~200 corridors precomputed | 200 | ~3,000 searches, ~400 model calls | affordable, covers only the head |
| **Page corpus per country** | **~4,000–10,000 URLs** | **conditional GETs, mostly `304`** | **this entry** |
| Decision rows per nationality | ~157k rows, ~30MB | ~600 model calls to populate once | affordable, and the riskiest layer |

Storage is never the constraint — cleaned text is capped at 50,000 characters. **Search quota and model
calls are**, and both scale with pages read rather than corridors served. That is what makes a corpus
work where corridor precomputation cannot: one crawl of Canada serves every nationality asking about
Canada.

**A decision-row table is deliberately excluded for now, and its cheapness is the reason to be careful.**
Canada's page *is* a table of roughly 200 nationalities, so a few hundred model calls would populate the
world. But that is a bulk-inference surface, and this project's defining failure (entry 15) is a
confident wrong answer. A wrong pick is currently ephemeral and per-request; a wrong row would sit in a
store for weeks and be served with a citation. Entry 42 proved that a nationality's answer can fall
outside the excerpt **silently**. If it is ever built: a nationality the page did not name yields **no
row**, never a false one, and absence must be distinguishable from "no visa needed". It layers onto the
corpus without rework, so nothing is lost by waiting for item 3's numbers.

**A personalised plan is never stored as truth.** It is a rendering of the corpus and its snapshots for
one traveller, and the profile fields that would explode its key space — city, residence status, permit
expiry — change only prose. What may be stored is an audit copy of what a traveller was told and when,
which is a different artifact with a different purpose.

### What a store must not lose

These are already right in the file stores and are easy to lose in a migration:

- **A row records when the evidence was retrieved, never when the row was written.** `_serve_stale`
  keeps the original `fetched_at` and a `304` moves it, because a validator match proves currency. A
  schema that collapses the two starts lying about how current its guidance is (entry 4).
- **The stale ceiling still refuses.** A stored page past `source_maximum_stale_hours` is refused rather
  than served, exactly as today.
- **A hash change marks a source; it never auto-swaps a role-bearing one.** Auto-rediscovery of a
  checklist is the wrong-checklist failure with the human removed (item 14).
- **No effective dates and no temporal rules model.** `published_date_in_path` reports rather than vetoes
  (known problem 12), and inferring effective dates from prose is the class of confident guess this
  project refuses everywhere else.

### Three provenance gaps found while tracing this, and the store is not the fix for any of them

The brief asked whether the system can answer *"why did you say an Indian passport holder needs this
visa?"* with a traceable source. It can name the page and when it was read, and no more:

- **`SourceReference.supporting_excerpt` is never populated on the live path.** It is written only by
  `FixtureSourceFetcher` from the Singapore manifest; `LiveSourceFetcher._build` does not set it and the
  extractor passes references through unchanged. **Every live plan cites a URL with no supporting
  quote.**
- **`content_hash` never reaches `VisaPlan`.** It exists on `FetchedSource`, but `SourceReference` has no
  hash field, so a plan cannot be tied to the exact text it was read from.
- **`decided_by`, `score` and `signals` never leave `ResolvedCorridor`.** Why a page was chosen for a
  role is on disk and invisible in the response.

All three are schema and plumbing, they are worth fixing whether or not the corpus is built, and saying
so matters: **provenance is not an argument for the store**, and folding it in would let a large change
borrow justification from a small one. Known problems 20, 21 and 22.

### Rejected

- **Precomputing answers per corridor**, at any width — the arithmetic above, before any safety argument.
- **A `visa_rule` decision table now** — the riskiest layer, and item 3 is what should decide it.
- **Storing plans as truth** — a plan is a rendering, and its personalisation is what explodes the keys.
- **Falling back to live search on a corpus miss** — silently reintroduces the variance the corpus exists
  to remove, on exactly the corridors that need it most (entry 38).
- **Effective-date modelling**, and letting a hash change auto-swap a role-bearing source.
- **Moving `authority_domains.yaml` into the store** — entry 34's whole argument is that the riskiest
  automated decision in the system should be a reviewable diff. It stays in git.
- **Collapsing the corpus into `recall_log.py`** — same rows, opposite contract; see above.

---

## 43. Write down what a corridor considered, because "ranked out" and "never found" had looked identical
**2026-08-21 · implemented**

`discovery/recall_log.py` writes one JSON record per corridor, on every run including a refusal,
holding every candidate the corridor considered with its score, whether it was shortlisted, and whether
it was fetched — plus the queries, the seeds, and each unreadable URL with its reason. It is on by
default in `build_resolver`, so the command and the API both produce it. Nothing reads it back.

**Why it earned a place in the request path.** Twice now a corridor has refused for a reason that was
accurate about what the decider was shown, and twice the next question — *was the page that would have
answered it ranked out, or never found?* — could not be answered from anything the run left behind. The
two have different fixes: one is scoring, one is search or crawl. On 2026-08-21 `canada/GB/GB/tourism`
refused with the answering page absent from its 24 candidates, and the only reason anybody knew the page
existed was a cache file from two days earlier.

**It answered the question on the first run, which is the argument for it.** Immediately after it landed,
the same corridor, cold:

| | |
| --- | --- |
| Candidates considered | **470** |
| Shortlisted / fetched | 25 / 24 |
| `entry-requirements-country.html` | rank **15**, score 53.4 for `visa_decision`, shortlisted, fetched |
| How it arrived | a `site:canada.ca` search seed, and again by crawl at depth 1 from `check-visa-eta.html` |
| Outcome | **resolved** — `visa_decision` and `general_entry` filled by that page, `decided_by=model` |

So the page is not a marginal candidate: it is fifteenth of 470 and comfortably inside 25 places. It was
simply **not returned at all** on the previous run an hour earlier, from the same fifteen queries against
the same five domains. Known problem 19 is now a measurement rather than an inference.

**And it is the first live confirmation of entry 42.** The model's reason quotes the page: *"the page
lists 'British citizen' among eTA-required nationalities and says that, when travelling by air, they need
an eTA"*. That sentence sits at offset 8,597 of 16,465. **A flat 6,000-character excerpt could not have
shown it**, which is arithmetic rather than a claim about the model. The same corridor, the same page, the
same shortlist, and the excerpt is the difference between a filled role and a refusal.

**Design notes, each of which is the thing that would otherwise be got wrong.**

- **A refusal must be logged.** Refusals are the runs worth reading, and they are precisely the ones that
  return early — before candidates exist, or before a shortlist does. So the record is filled by a
  mutable trace as the run proceeds and written in a `finally`, not assembled from a return value.
- **A diagnostic may never cost an answer.** An `OSError` writing the log is swallowed. Failing a corridor
  because a log file could not be written would trade an answer for a note about an answer, and the
  failure is not silent in practice: the file is not there when someone looks.
- **Shortlisted and fetched are recorded apart.** "Shortlisted but unreadable" is a third answer to *why
  was this page not used*, and merging the two flags hides it.
- **Overwritten per corridor, never accumulated.** The question is almost always about the run that just
  happened. Comparing two runs — which is how the Canada variance was found — means deliberately keeping
  a copy, rather than a directory that grows for every request forever.
- **It is not evidence and nothing depends on it.** Deleting `var/recall/` costs a question, never an
  answer. That is what makes it safe to have in the request path at all.

**What it does not do.** It does not record *why* search returned what it did, so it cannot explain the
variance it exposes — only prove it happened and to which page. And a record exists only for runs made
after this landed, so the 2026-08-21 refusal stays diagnosed by inference.

---

## 42. The excerpt is the second recall gate, and a flat 6,000 made truncation the decider
**2026-08-21 · implemented**

`DEFAULT_EXCERPT_CHARACTERS` moves from 6,000 to 20,000, and stops being a flat head-of-page slice: the
adjudicator now sees the head of each candidate **plus a 3,000-character window centred on every later
mention of the traveller's own nationality or residence**, with what was left out marked `[…]`.

**This is entry 40 one layer down.** The shortlist decided which pages the model may see; the excerpt
decides which *part* of them it may see, and the same asymmetry governs both — text the model never sees
is text nothing downstream can recover. Entry 40 was applied to the shortlist and the comment on the
constant below it was left saying, correctly, that ten pages of prose "would push the call past any
sensible input bound". Nobody asked whether 6,000 characters was where the answers were.

**What it cost, measured on `canada/GB/GB/tourism`.** The corridor ranked the right page first, fetched
it, and refused. `entry-requirements-country.html` is 16,465 characters; it lists visa-required countries
alphabetically, starts the eTA list only at offset 8,517, and answers a British traveller at 8,597:
*"You need an eTA and a valid passport to board your flight to Canada … you **don't** need a visitor
visa"*, with "British citizen" naming them at 8,858. The excerpt ended at 6,000, mid-alphabet at
"Morocco". The adjudicator then refused `visa_decision` for a reason that was accurate about what it had
been given — *"No candidate shows the result for a GB passport holder"* — and the corridor refused.

**The defect is worse than "Canada refuses", and this is the sentence to keep: whether a corridor
resolved depended on where the traveller's nationality fell in an alphabet.** On that one page, India at
5,325 was inside the window and every visa-exempt nationality — Australia 8,815, a British citizen 8,858,
Japan 9,647, Singapore 9,856 — was outside it. That also explains entry 40's "Canada: every role filled"
at 25 places: that measurement is consistent with an Indian passport and does not generalise. Nothing in
the output said so, which is the part that should be uncomfortable.

**Why anchoring and not only widening.** A flat number is still a fixed offset, and a country-list page
puts the answer wherever the alphabet puts it. So the window follows the traveller: the head first,
because it carries the title and what the page is, then each later mention of their own country words.
The window is **centred** on the mention rather than started at it — Canada's answering sentence sits 261
characters *before* "British citizen", so a forward-only window would have cut exactly the sentence being
looked for. Budget the anchors do not spend is read straight on from the head, so a page that never names
the traveller is read *further into*, never less of, than the flat slice this replaces.

**Honest accounting of what each half buys.** Measured over the 27 cached `canada.ca`/`gc.ca` pages in
`var/cache`, packet text goes from 84,704 characters to 153,862 — about +17k tokens on one call. Almost
all of that is the raise: a flat 20,000 costs 153,852 on the same pages, because 19 of the 27 are shorter
than the head and only 2 exceed the budget at all. **Anchoring is not what makes this affordable.** It
changes nothing for a page under the budget and everything for one over it: on the 50,000-character
visitor-visa PDF, a US traveller's windows land at 19,452 and 24,449, and the second is text a flat
20,000 cuts. The two 50,000-character pages are the whole population where the two rules differ today,
and they are also where a further raise would get expensive.

**Two details that are not cosmetic.**

*The omission is marked.* `[…]` is written wherever text was dropped, including at the end, and rule 12
of the prompt tells the model what it means. Without it, a cut list reads as a finished list — which is
precisely how Canada's visa-required list, stopping at "Morocco", could be read as complete. Marking it
is the same principle as every other reason this project reports: what is shown has to be true of what
was seen.

*Short country words are matched in upper case only.* "us" is how the United States is written on a
government page and also an ordinary English pronoun; matched case-insensitively it anchored 34 windows
in one 50,000-character Canadian guide, none of them about an American traveller. "US", "UK" and "UAE"
in upper case are the country; longer words are matched either way. Word boundaries do the rest — an
unbounded "uk" matches inside "Ukraine".

**What this does not fix.** Raising the excerpt cannot help a page that never contained the answer.
`ircc.canada.ca/english/visit/visas.asp` — the natural decision page, and what search returns first —
yields 1,144 characters saying the client needs JavaScript, and its answer is behind a wizard; that is
item 5's problem, not this one. Canada resolves because a *different* page happens to publish the list
statically.

**Run live the same day, on the corridor it was built for, and it did not resolve.** Cold, with
`var/cache/` and `var/corridors/` cleared: `canada/GB/GB/tourism` refuses again, in 69s, and **the reason
is not the excerpt**. Of 24 candidates fetched, `entry-requirements-country.html` — the page holding the
answer, and the page the 2026-08-19 replay was performed on — **is not among them**. It was not fetched
at all. The excerpt cannot widen a page nobody retrieved.

What the run does establish:

- **The change shipped and is doing what it says.** Three candidates exceed the old 6,000 — 14,765,
  11,258 and 8,186 characters — so 16,209 more characters of page text (~+4k tokens) reached the model
  than a flat slice would have allowed, on a packet of 84,648. No candidate needed a `[…]`, because every
  one of them fits inside 20,000; the anchoring changed nothing here, exactly as the cost note predicts.
- **The adjudicator's refusal is now about a wizard, not a truncation.** Its reason: *"No candidate gives
  a result for a GB passport holder. The visa/eTA checker extracts only show 'Your result is loading'"* —
  which is item 5's problem, named by the model itself.
- **The candidate set for one corridor varies between runs**, and that is the finding worth carrying:
  the same corridor, from the same five trusted domains, retrieved the answering page on 2026-08-19 and
  did not on 2026-08-21. Whether it was discovered and ranked out of the 25 shortlist places or never
  discovered was not instrumented. Recall upstream of the excerpt is now the binding constraint on this
  corridor, and entry 40's asymmetry argument points at it as squarely as it pointed here.

**Then it was run once more, after entry 43 landed, and Canada resolved.** Same corridor, same day, same
five domains: this time search returned `entry-requirements-country.html` and the model filled
`visa_decision` from it, quoting the sentence at offset 8,597 — **which a flat 6,000-character excerpt
could not have shown**. That is this entry confirmed live, and it took a corridor that flips between runs
to show it. Both results stand: the excerpt was a real gate and is now open; whether the page arrives at
all is a separate gate that is still shaking. See entry 43 and known problem 19.

The remaining six verified corridors have still not been re-run; that is TODO item 15.

---

## 41. A challenge is not a refusal: answer it as an honest browser, and honour every `robots.txt`
**2026-08-19 · decided; not implemented**

Entry 18 opens by predicting that "a headless Chromium would very likely pass that check" and then
forbids trying. **Measured on 2026-08-19, the prediction is right and the premise underneath it was
wrong.** `france-visas.gouv.fr` is not refusing this program. It is challenging it, and the two are
different acts by different parties.

**What the `403` actually is.** Requesting `/en/demande-de-visa` with the client the app really uses
returns:

```
server: cloudflare
cf-mitigated: challenge
server-timing: chlray;desc="a2dabaff0fda5548"
set-cookie: __cf_bm=...
accept-ch / critical-ch: Sec-CH-UA-Bitness, Sec-CH-UA-Arch, Sec-CH-UA-Platform-Version, ...
```

with `cf_chl_opt` and the `/cdn-cgi/challenge-platform/` loader in the body, whose visible text reads
*"One moment please … Checking if the site connection is secure … Enable JavaScript and cookies to
continue"*, wrapped in a French page that calls itself *"Erreur 503 — le serveur que vous essayez
d'atteindre semble injoignable"* and advises trying again in a few minutes. `cf-mitigated: challenge`
is Cloudflare's own label for *prove you are a browser*. The `403` is the transport for a challenge,
not an authorisation decision, and the page contradicts itself about which status it even is.

**And `/robots.txt` is behind the same challenge**, which settles the question of whose decision this
is. There is no stated policy, because nothing published a policy — a WAF default sits in front of the
whole host. Entry 36's `robots.txt` work already measured this and known problem 11 already said it;
what neither did was draw the conclusion about the `403` itself.

**The distinction that decides it: entry 18's test is deception, not status codes.** A response that
says *"enable JavaScript and cookies to continue"* is a **capability test**. Answering it by running
the page's own JavaScript, in a real browser, under our own name, misrepresents nothing to anybody.
Measured: the project's own `PlaywrightPageRenderer`, announcing
`VisaResearchAgent/0.1 (personal visa research; contact repository owner)` — our identity, unchanged,
nothing spoofed — reads the page.

| | Result |
| --- | --- |
| `final_url` | `https://france-visas.gouv.fr/en/demande-de-visa`, unchanged |
| HTML | 221,476 bytes; 2,277 visible characters |
| Challenge markers in the result | none |
| `blocked_hosts` | `[]` — the render trust gate had to allow nothing new |
| Cost | ~7s per page |

That last row matters more than it looks: Cloudflare's challenge scripts are served **same-origin**
under `/cdn-cgi/challenge-platform/`, so the rule that aborts every request to an unapproved host
(entry 13) neither has to bend nor accidentally breaks the challenge.

**Decided, and it amends entry 18 rather than repealing it.**

- A challenge is **its own outcome**, not `blocked`. `blocked` means an authority refused us; that is
  a claim about the authority, and it is false here.
- A challenge **may be answered by the renderer**, under our own user agent. This is the one thing
  entry 18 named and forbade, and it is now allowed *because* it was measured to require no
  deception — not because the coverage was tempting.
- A challenge **may never resolve a corridor.** Entry 32's causality bound applies with more force
  here, not less: a page nobody was allowed to read is at least a page an authority withheld, whereas
  a challenge is a page nobody asked the authority about. This is also why France's current
  resolution is wrong — it resolves on an incidental challenge that happened to score for
  `visa_decision`, which flips between runs.
- **`robots.txt` is read and obeyed for every host, unchanged (entry 36), and it outranks all of the
  above.** A `Disallow`ed path is not fetched, challenge or no challenge; a policy that cannot be read
  is still reported as unread rather than as permission; a `Disallow` still may not resolve a corridor.
  Answering a challenge where no policy exists and ignoring a policy where one does would be the same
  mistake twice.

**What stays forbidden, in full.** No user-agent spoofing. No retrying past a `429`. No answering a
`401`, or a bare `403` carrying no challenge markers — those are refusals, and entry 18 governs them
completely. **The line moves from "which status came back" to "did the authority state anything".**

**Entry 18's cost statement is amended.** *"France is unservable"* was true of an anonymous HTTP
client. It was never a property of the principle, which is what entry 35 said and this measures.

**What it does not buy, measured, so that nobody expects it.** Answering the challenge yields the
pages; the answers are not on them.

| Page | What is actually there |
| --- | --- |
| `/en/demande-de-visa` | Three generic items — passport, "photocopies according to your situation", 2 ICAO photos — and a button into the wizard |
| `/en/assistant-visa` | "Step 1 of 4" with a nationality dropdown: the decision is behind form input |
| `/en/visa-de-court-sejour` | Defines what a short-stay visa is; never says who needs one |
| `www.france-visas.gouv.fr/en/web/france-visas/india` | **404** — and it was the top-scoring France-Visas candidate at 74.4 |

So the challenge had also been masking dead URLs, and the corridor was spending fetch places on them.
Getting a *corridor* checklist out of France needs the wizard, which is form input and collides with
the permanent scope rule on form filling. **That is a separate decision and is not taken here.**

**One thing shipping today is now known to be false.** The interface tells a traveller
*"<authority> does not permit automated retrieval"* for any `blocked` failure with a URL. For a
challenge that sentence is untrue of what was seen. Correcting it is part of the implementation, not a
separate nicety — see [TODO.md](TODO.md) item 5.

---

## 40. The shortlist is a recall budget, and ten places made the heuristic the real decider
**2026-08-18 · implemented**

`DEFAULT_SHORTLIST_SIZE` moves from 10 to 25. That is the whole change, and it bought more than every
scoring rule in `scoring.py`.

**The reasoning that kept it at ten was a category error.** The pipeline is: a heuristic scorer picks the
shortlist, and a model adjudicates roles from it. The scorer was being tuned as though it decided
something. It does not — it decides **what the model is allowed to see**. So its two errors are not
symmetric. A page ranked *in* wrongly costs one excerpt. A page ranked *out* is one nothing downstream
can recover: not the adjudicator, not the retry, not the traveller. At ten places, the heuristic was the
effective decider for every corridor whose right page sat eleventh — and known problem 9 had said exactly
this ("a page it ranks out of the ten fetch places is one the model never sees") without the conclusion
being drawn.

**Measured live, changing only this number:**

| Corridor | 10 places | 25 places |
| --- | --- | --- |
| Canada | refuses — no visa decision | **every role filled** |
| Japan | no visa decision | **every role filled**, same checklist |
| Netherlands | no checklist | checklist found (its decision is a JavaScript tool; see entry 39) |
| Sweden | two roles unfilled | unchanged — it fails for another reason |

Two corridors that refused now resolve completely. Nothing regressed.

**And it is close to free**, which is the part that was assumed rather than checked. Fetching is
concurrent, so cost scales with batches rather than pages: Japan's corridor took 44.5s at ten and 39.3s
at twenty-five, Canada's 45.2s and 41.7s — within noise both times, with no systematic penalty in either
direction. Adjudication input roughly doubles to about 19k tokens, which is small for one call.

**What this does not fix, and must not be read as fixing.** Sweden did not move. The `/india`-over-
`/united-kingdom` weighting from entry 39 is still wrong. Scoring is still English-only (known problem
13). The argument here is narrower: **the scorer did not need to be more accurate, it needed to stop
being a bottleneck**, and that was true before any of its rules were examined.

**Rejected for now: replacing the scorer** with an embedding or model-based ranker. It is the component
that does *not* need to be reliable — its failures cost recall, which fails safe into a refusal, because
the trust rules and the adjudicator sit downstream. Spending a rewrite on the safe component while a
constant was the binding constraint would have been the wrong order. If it returns, the case should be
the multilingual gap rather than the ranking.

**A test pins the width**, because narrowing it again would be invisible: corridors do not fail loudly,
they quietly refuse, and the page that would have answered is never fetched to be missed.

---

## 39. A person may override the trust rule in committed data, and doing it showed the rule was not the only thing wrong
**2026-08-18 · implemented for 12 countries**

Entry 33 said a government using no hostname marker "has to be named in reviewed data instead" and left
that hatch unbuilt. `CountryAuthorities.reviewed` is it: a map of domain to **the evidence that justified
it**, ahead of the machine-proposed list and counting against the same cap, so a correction displaces the
weakest automatic domain rather than widening the set.

Three properties make it safe enough to bypass the trust rule with:

* **The evidence is required, and validated non-empty.** A reviewed domain skips the rule that keeps
  commercial agencies out, so a reason nobody can check is a domain nobody has verified. The committed
  file is asserted against this in the test suite, not just the fixtures.
* **A regeneration cannot silently undo it.** `visa-discover registry --rebuild` replaces `trusted` and
  `unconfirmable` — search output, meant to be replaced — and carries `reviewed` through untouched. This
  was the one way that command could have done real damage: every correction reverted, with plans still
  refusing, and nothing in the output saying so.
* **The evidence is a claim about who controls the domain, made by something that is not the page.**
  Each of the twelve was confirmed by a Wikidata reverse lookup — the domain is the `official website`
  (P856) of an entity whose `country` (P17) is that country. That is the same question
  `belongs_to_destination` asks and the one `looks_governmental` cannot answer for these governments.
  Four domains the lookup could not confirm were **left alone**: `gv.at`, `swiss-visa.ch`, `mvep.hr`,
  `nyidanmark.dk`. Austria therefore still refuses, and that is the correct output.

**Rejected: a live Wikidata lookup in the trust path.** Wikidata is user-editable, so a claim that a
domain belongs to a government can be edited by anyone. As input to an offline file that a person reviews
as a diff, a bad edit is visible before it can reach a traveller; as a request-time authority it would be
an unreviewed third party deciding what this program trusts. Entry 34 is what makes the first version
acceptable. **Also rejected: asking a model.** It would likely classify more of these correctly, and it
produces no entity, no revision history and nothing to diff — in a system whose entire differentiator is
that every claim traces to something checkable.

### What running it found, and it corrects entry 38 and the reasoning behind this change

The diagnosis going in was that the domain classifier was the binding constraint: bootstrap proposes the
right domain for every failing country, and only the hostname regex throws it away. That is true, and it
is **not sufficient**. Measured before and after, three countries:

| | Before | After |
| --- | --- | --- |
| Sweden | refused with **nothing fetched** — no domain confirmed at all | reads `migrationsverket.se`; `application_route` and `general_entry` filled |
| Canada | refused: visa decision **and** checklist unfound | refused: checklist **found**, decision still unfound |
| Netherlands | refused | refused, unchanged |

So the corrections are real — Sweden went from fetching nothing to reading its actual immigration agency —
and **not one of the three resolves end to end.** The binding constraint has moved rather than lifted: it
is no longer "we cannot tell which domain is this government" but "we cannot confirm the visa decision on
pages we can now read."

### Following one of them all the way down, because "still refuses" is not a diagnosis

The Netherlands did not move, so it was traced page by page. Four distinct causes, and only the first
was the domain:

1. **The reviewed domain was right and incomplete.** `government.nl` is genuinely the Dutch government,
   but the Netherlands delegates visa content to `netherlandsworldwide.nl` — which the trust rule had
   left in `unconfirmable` and which the Wikidata lookup could not confirm either. It is now reviewed on
   **stronger** evidence than any other row: `government.nl` itself states that the traveller can see on
   Netherlands Worldwide whether they need a visa. That is the destination's own government vouching for
   the domain, which beats a third-party lookup.
2. **The page that ranked first was a signpost.** `check-visa-netherlands` scored 60.4, top of the
   shortlist, returned `200`, and yielded **250 readable characters against the 400 floor**. Correctly
   refused — it genuinely contains no guidance, only two links.
3. **With the delegated domain added, the right pages appear** — including
   `checklist-schengen-visa-tourism/india` at 123.0 and, separately,
   `checklist-schengen-visa-tourism/united-kingdom`, both readable and around 7,700 characters. **The
   scorer ranks the wrong one higher: 113.0 for `/india` against 73.0 for `/united-kingdom`.** For a
   consular checklist the **post** governs, not the passport: an Indian national applying from Great
   Britain applies at the Dutch mission in the UK. So the wrong-post page took the slot, and the
   adjudicator — correctly applying that rule — declined to name it. **The adjudicator was right and the
   scorer is wrong**, which is the reverse of how it first read.
4. **The visa decision is not published as a page at all.** `entering-without-visa` redirects to a
   nine-question JavaScript filter tool. No static Dutch page says an Indian national needs a Schengen
   visa. Refusing that role is correct and no amount of ranking fixes it.

So the binding constraint is not one thing. It is a scorer that weights nationality above post, and a
government that publishes its decision only as an interactive tool.

**And entry 38 was wrong about the shape of the failure.** It claimed a wrong trusted set makes a corridor
*resolve* against domains that cannot hold the answer — the failure this project treats as worse than
refusing. Run, they **refuse**. The refusal discipline held throughout; what a wrong trusted set costs is
coverage, not correctness. That claim was written from reading the code path, which is now the fifth time
in two days that habit has produced a false line in these files.

---

## 38. The trusted-domain registry is generated offline and committed, and reviewing it found what running it could not
**2026-08-18 · implemented for 40 countries; the remaining 158 are unbuilt**

Entry 34, built. `bootstrap_destination` no longer runs in a request. `discovery/registry.py` reads
`config/authority_domains.yaml`; `discovery/registry_build.py` and `visa-discover registry` generate it.
`auto_trusted_domains` — the whole of the trust rule — is unchanged and still the only thing deciding a
domain. **What moved is when it runs**, from every cold request to once per country.

Verified live: resolving New Zealand, a destination nobody had configured, spent **0 searches** in the
service where it previously spent 4, and produced a visa decision, a document checklist, an application
route and a general-entry page from committed domains alone.

**A missing row refuses rather than falling back to a live bootstrap.** Falling back would reintroduce the
per-request variance this entry exists to remove, silently, on exactly the countries nobody had reviewed.
The refusal names the command that fixes it.

**A country whose searches errored is left out of the file entirely**, never written with an empty
`trusted`. Those two mean different things — "the rule confirmed nothing for Germany" is a finding a
reviewer must act on, and "we never got to ask" is not — and the build is resumable precisely so the
second can be retried without repaying for the first.

### What the review found, which is the point of committing it

Forty countries built, 35 confirmed, 5 refused. Entry 34 argued that committing the rule's output makes
the riskiest automated decision in the system auditable. It does, and reading the file surfaced three
things no test and no corridor run had:

**The five refusals are entry 33's known failure, and now name their own fix.** `AT`, `BE`, `DE`, `DK`,
`SE` — with `gv.at`, `ibz.be`, `auswaertiges-amt.de`, `nyidanmark.dk` and `migrationsverket.se` sitting in
`unconfirmable`. `gv.at` in particular is a marker correction `CLAUDE.md` already blesses.

**Twelve more countries are confirmed *and wrong*, which is worse and was invisible before.** Entry 33
predicted this second failure and could not measure it; the file shows it plainly:

| Country | Trusted | Actually holds the visa guidance |
| --- | --- | --- |
| Netherlands | `business.gov.nl` — the business portal | `government.nl`, and IND, both unconfirmable |
| Italy | `integrazionemigranti.gov.it`, `mise.gov.it` | `esteri.it`, unconfirmable |
| Canada | five `gc.ca` domains | `canada.ca`, unconfirmable — IRCC moved there |
| Portugal | three ministry domains | `sef.pt`, unconfirmable |
| Ireland | `gov.ie`, `inis.gov.ie` | `irishimmigration.ie`, unconfirmable |

~~These corridors do not refuse. They resolve, against domains that cannot hold the answer.~~
**Wrong, and corrected in entry 39 by running it.** Measured on the Netherlands and Canada: a wrong
trusted set makes a corridor **refuse**, it does not make it answer. The refusal discipline held. The
cost of this failure is coverage, not wrong guidance — which is a materially smaller problem than the
sentence above claimed, and the sentence was written from reading the code rather than from output.

**A third finding nobody had predicted: the cap spends its slots on the wrong parts of a government.**
India's five include `indianembassyusa.gov.in` and `cgichicago.gov.in` — United States missions, occupying
two of five slots for *every* corridor including India-from-GB. South Korea's include `goesan.go.kr`, a
county. Spain's put `administracionespublicas.gob.es` and `lamoncloa.gob.es`, the prime minister's office,
ahead of `exteriores.gob.es`. Entry 22 predicted the cap would bite and assumed the ordering was sound;
`_trust_priority` falls back to **alphabetical** among domains with no hostname hint, and for a large
government that is the same as arbitrary. This is now item 2's problem, and it is a data-and-ordering
problem rather than the regex change entry 33 forbade.

**Forty rather than 198, deliberately.** 198 countries is 792 searches; the top forty by traveller volume
is 160 and answers the question the file was built to answer. The remaining 158 refuse with the message
naming `visa-discover registry`, and `--only` builds any subset. Building the rest is quota, not work.

---

## 37. A per-run allowance may not be counted on an object that outlives the run
**2026-08-18 · implemented**

Three render budgets described themselves as per-run — *"Retrieval's own allowance"*, *"Discovery's own
allowance"*, *"a last-resort ceiling on one browser's lifetime"* — and two of them were counted on objects
that outlive every run. Found while implementing entry 36, which hit the same singleton lifetime and solved
it with a TTL.

**What it actually did.** `LiveSourceFetcher.renders` starts at zero in `__init__` and was never reset,
and the fetcher is reached through `get_visa_plan_service`, an `lru_cache(maxsize=1)`. So `maximum_source_renders`
(5) was a budget for the *server process*, not for a request. Confirmed by running it rather than by reading
it: with the allowance set to 2, requests 3 and 4 never consulted the renderer at all. Past that point every
client-rendered page — Vietnam's e-visa portal, the pages rendering exists for — came back
`"the page returned too little readable text to trust"`, for as long as the process stayed up.

**That failure is a false reason, which is why it is a defect and not merely a limit.** The page had not
been read. Saying it returned too little text states something about what was seen, when what happened was
that we declined to look. This is the same fault as entry 33's `withheld_domains` wording and entry 36's
*"does not permit"* — a sentence describing a source nobody consulted.

**The fix is a value, not a reset.** `RenderBudget` is built inside `fetch()` and passed down to `_render`.
Resetting `self.renders = 0` on entry would look equivalent and is not: a server answers requests
concurrently, so two overlapping runs would each clear the other's count and both could render past the
limit. Held as a per-call value, no long-lived object carries a spent count. A test pins the concurrent
case, because it is the one a reset would silently pass in a single-threaded test and fail in production.

**`PlaywrightPageRenderer`'s own count is deleted rather than fixed.** It was `maximum_source_renders +
maximum_crawl_renders` = 17, documented as a last-resort ceiling on one browser's lifetime — but `aclose()`
is only ever called by the CLI, so on the API path that browser's lifetime *is* the server's. It bound
first and hardest: `dependencies.py` builds one renderer and closes over it in the resolver factory, so it
survived even the per-corridor fetchers, and after 17 rendered pages the whole installation stopped
rendering. A guard whose only observable effect is to switch a feature off silently is not a guard. Counting
belongs to whoever knows where a run begins, and both callers now bound it: retrieval per `fetch()`,
discovery per corridor. The trust check inside `render()` stays exactly where it is — that one is
belt-and-braces for *trust*, which is a different question.

**`CrawlFetcher.renders` was reported as having the same defect and does not.** It holds a spent count on
the instance, but `AutomaticDestinationService` holds a resolver **factory**, not a resolver, and calls it
per corridor — so an instance never outlives one run, and sharing the allowance across that run's many
`fetch_html` calls is the intent. Left alone, with the lifetime argument written next to the counter and a
test pinning that the factory is still called per corridor, since that invariant is now load-bearing for
this class and nothing had been asserting it.

**The general rule, worth stating because it is not visible at the definition site:** in this codebase a
counter, cache or accumulator on a service reached through `dependencies.py` is process-lifetime unless
something makes it otherwise. Entry 36 needed a TTL for it; this needed a per-call value. Check the caller,
and prefer running it to reading it — reading is what let all three of these stand.

The rest of that path was swept for the same shape while fixing this, and nothing else was found: after
the change the only zero-initialised counter on any object reachable from `dependencies.py` is
`RenderBudget.spent`, which is per-call by construction. The other long-lived stores are file-backed with
an age check (`FileSourceCache`, `FileCorridorStore`) or expire (`RobotsCache`).

---

## 36. `robots.txt` is read and obeyed, and a page skipped for it is its own outcome
**2026-08-18 · implemented**

The first of entry 35's three legitimacy steps, and the one owed regardless of what it buys. Until now
nothing here fetched `robots.txt` while the same code computed a per-host politeness delay for the same
hosts — a guess at what a site tolerates, running alongside a refusal to read the site saying it.

`RobotsCache` (`research/robots.py`) fetches one policy per **origin**, re-read after 24 hours, and both
fetchers consult it before every request: `discovery/crawl.py` before each crawled page, `research/live_sources.py` before each
source and before each meta-refresh forward.

**Matching is written here, and `urllib.robotparser` was tried first and rejected.** The original
reasoning — stdlib, better tested, and its shortfall "errs toward fetching less" — was wrong, and was
written from reading the module rather than running it. `urllib` matches with `filename.startswith(path)`
and supports **neither `*` nor `$`**. Measured against real authorities on 2026-08-18: every rule
`www.gov.uk` publishes is a wildcard, so a stdlib client obeys **none** of them, and `www.canada.ca` has
fourteen more it walks straight past. A parser that silently makes this fetch *more* than a site permits
is the one failure this module cannot have. The matcher now implements RFC 9309 §2.2.2–2.2.3 directly:
`*` matches any run, a trailing `$` anchors the path end, the longest pattern wins, `Allow` beats
`Disallow` at equal length, and a group is chosen by exact product token falling back to `*` — not by
`urllib`'s substring test, under which a record aimed at `Visa-Bot` would capture this client.

**Three things were decided while implementing it, and each is the reason a later "simplification" would
be a defect.**

**A skip is an outcome, never an absence.** `FailureOutcome` gains `disallowed`. Without it a page nobody
asked for is indistinguishable from a page that did not exist, which is the failure entry 18 named: a
refusal must never read as "nothing found". The corridor reports it in its own sentence rather than folding
it into the generic "could not be read" note, because only the first failure per host survives that note and
a `Disallow` could be masked by an unrelated `404` elsewhere on the same site.

**Three verdicts, not a boolean, because the reasons differ and the reason is what gets reported.** A first
attempt collapsed every non-answer into "disallowed", and the crawl then described **every unreachable
host** as *"its robots.txt does not permit this client"* — a sentence about a policy nobody had read, and
word-for-word the class of false reason entry 33 had just finished removing from `withheld_domains`. So:
a `5xx` or an oversized file is `UNREADABLE` (*"could not be read, so whether this client may fetch it is
unknown"*), a parsed rule that excludes us is `DISALLOWED` (*"does not permit"*), and a **transport failure
raises** rather than deciding anything — an unreachable host is not a crawl policy, and the callers already
describe one correctly, including telling a name that does not resolve from a request that merely failed.
`4xx` on the file itself, `401` and `403` included, means no policy is published: those say the file is
protected, not that the site is closed (RFC 9309 §2.3.1.3).

**A `Disallow` may be reported; it may never resolve a corridor.** `disallowed_urls()` is deliberately not
part of `blocked_urls()` or `persistent_refusals()`, so nothing here reaches `inaccessible_urls` or
`decision_blocking_urls`. A `403` was observed **on the page itself**; a `Disallow` covers a path we chose
not to request. Treating the second as evidence that the answer sat behind that page would be guessing about
a page nobody read, and it would widen entry 32's deliberately narrow exception by a mechanism entry 32
never considered.

**The expiry is not tuning.** `get_visa_plan_service` is an `lru_cache(maxsize=1)`, so the fetcher holding
the cache lives as long as the server process. Without a TTL a policy read at boot would be obeyed until
someone restarted the thing — a withdrawn `Disallow` honoured forever, and a newly published one ignored
just as long. This was found by checking the caller rather than by reading the class, which is the habit
`CLAUDE.md` asks for.

**Two smaller calls.** The policy fetch sits outside the crawl's politeness delay: that delay only ever
bites on the *second* request to a host, and a `robots.txt` fetch is always the first, so routing it through
the delay would space nothing and merely make first contact with every host cost the delay. And in
retrieval the check sits *after* the fresh-cache return, because `robots.txt` governs fetching — text
already held and still inside its TTL is re-read without a request, so a policy published since does not
retrospectively forbid reading what we have. Past the TTL a request is needed and the policy decides.

**A fourth thing, found by running it rather than reading it**, and the reason the paragraph above exists.
The stdlib parser was the first choice and it was inert: it obeys no wildcard rule, which is every rule
`www.gov.uk` publishes. This module had been shipped, tested and documented as honouring crawl policies
while honouring almost none of them, and no unit test could have caught it — the fake policies in the
suite were all literal prefixes, because those are the ones a person writes from memory. It took probing
real authorities. That is the third time in two days a documented claim here turned out to be written
from a code path rather than from output.

**Measured live on 2026-08-18, six corridors, all Indian nationals applying from GB.** Expected to cost
coverage; it cost almost none, and what it did cost was worth nothing.

| Corridor | Policies read | Pages skipped | What was actually lost |
| --- | --- | --- | --- |
| Japan | 6 | 0 | nothing |
| Singapore | 16 | 0 | nothing |
| Vietnam | 6 | 0 | nothing |
| Brazil | 16 | 0 | nothing |
| France | 6 | 1 | a news listing with a filter query, matched by `*/actualites?` |
| China | 6 | 5 | two application portals answering `502` to every path, policy included |

**The most important negative result is France and the United States.** Both were expected to be where
legitimacy might buy something, and `robots.txt` buys **nothing** there: `france-visas.gouv.fr`,
`www.france-visas.gouv.fr` and `travel.state.gov` all answer `403` **to their own `robots.txt`**, served
as a bot-detection interstitial. There is no policy to honour — it is a WAF, not a stated rule. So entry
35's "owed regardless of what it buys" was the correct justification, and it is the only one available:
the two corridors that motivated the review are untouched by this step. Their ten `403`s are still
reported as `blocked`, unchanged.

**Two live findings changed the code, and both were the same failure as before — a reason that was true
of the branch rather than of what was seen.**

- The unreadable case said only "its robots.txt could not be read". For China that pointed a reader at a
  crawl policy when the fact in front of them was a host serving `502` to everything. It now names what
  came back: *"its robots.txt answered HTTP 502, so whether this client may fetch it is unknown"*.
- The corridor-level note was a fixed sentence — *"publishes a robots.txt that does not permit this
  client"* — and for those same two Chinese hosts it **asserted a published refusal that nobody had
  read**. It now repeats the reason recorded against the page instead of composing its own.

That is the third and fourth time in this entry that a sentence describing a branch turned out not to
describe the observation. The rule generalises: **a reported reason must be built from what was
recorded, never written alongside it.**

Entry 35's twenty-corridor measurement — still blocked on credit — should now run against this posture.

---

## 35. The posture is honest client, not anonymous client — and the bar that decides whether this is a product
**2026-08-18 · decided; first of its three steps implemented as entry 36**

An outside review asked the question this project had been answering implicitly: two of the highest-volume
corridors there are — India→US and India→France — now yield a plan with **no document checklist**, because
the pages holding the answer are bot-blocked. If that is the normal case rather than the exception, this is
a careful demonstration of why the approach cannot work rather than a product.

**The finding that reframes it: two commitments had been treated as one.**

1. *Every claim is grounded in an official government page, and refusing beats guessing.* This is the
   product's identity, it is correct, and nothing here weakens it.
2. *Grounded only in what an anonymous, unauthenticated Python client can fetch at request time.* This is
   an **implementation posture**, never decided on its merits, and it is what actually fails on France and
   the United States.

Entry 18 forbids **deception** — spoofing a user agent, pointing the renderer at a refusal, retrying past a
rate limit. It says nothing about becoming a client authorities are willing to serve. Conflating the two has
been costing coverage under the banner of a rule that does not demand it.

**Decided: pursue legitimacy, never circumvention.** Three things follow, in increasing order of scope:

- **Read and honour `robots.txt`.** ~~Nothing in this codebase has ever fetched it.~~ **Done — entry 36.**
  A project that computes a per-host politeness delay (entry 25) while ignoring the file that states a
  host's own crawl policy was inconsistent on its own terms. This was owed regardless of what it buys, and
  it may cost coverage — a `Disallow` previously walked past is now a refusal — which is the correct
  direction for this product.
- **Ask.** An identified research client requesting access from an immigration authority is an ordinary
  thing to do, and the current user agent already invites contact.
- **Client-side retrieval, as an open question and not yet a decision.** The traveller's own browser can
  open `france-visas.gouv.fr`; a human reading a public page is not this program circumventing a refusal.
  Whether the agent may then *read what their session received* is genuinely near entry 18's boundary and
  needs its own entry either way. Recorded now so it is argued rather than drifted into. **Not approved.**

**And the bar, committed before the measurement rather than after it.** The seven-corridor sample cannot
answer whether blocks are the rule, and choosing a threshold after seeing results is how a demonstration
talks itself into being a product. So: run the **top 20 corridors by real traveller volume** cold, and count
per corridor whether the visa decision was confirmed, whether a checklist was found, and whether a checklist
was blocked.

> **Product if ≥70% confirm the decision and ≥50% yield a document checklist. Below that, the
> anonymous-crawl posture is dead** and the choice is licensed data (Timatic/Sherpa — which every airline
> uses and which would forfeit the verifiability that is the whole differentiator) or client-side retrieval.

Today's seven are 5/7 on the decision and 4/7 on a checklist, which would pass — on a sample chosen partly
because it was easy. Blocked on Brave credit; it is the measurement that decides the project's direction, so
nothing large should be built before it.

**Rejected: treating France as an acceptable permanent loss.** Entry 26 established the coverage loss is
real and permanent *given the posture*. What was never established is that the posture is required, and
entry 18 does not require it.

---

## 34. Who to believe becomes committed data; only which page is decided live
**2026-08-18 · decided; implemented as entry 38**

`ARCHITECTURE.md` already states the right division and the code does not implement it:

| | Who to believe (domains) | Which page to read (URLs) |
| --- | --- | --- |
| Corridor-dependent? | No — `mofa.go.jp` serves everyone | Yes |
| How many | ~3 per country | Tens of thousands |
| Decided by | **A rule, once per country** | **The machine, every corridor** |

But `bootstrap_destination` runs *inside every cold request*, and its result is cached **per corridor**. So
a country's trusted set is re-derived from that day's search rankings for every new nationality, and the
answer to "who is Germany's government" varies with Brave's mood. Entry 22's US coin flip was this
mechanism, treated as a ranking problem.

**Decided: generate the country → trusted-domains registry offline for all 198 countries, commit it beside
`countries.yaml`, and have a person skim it once.** Request-time discovery then begins at the corridor step.

What this is **not**: a return to the gate entry 19 removed. Nobody curates URLs — that stays automated and
is the production goal. This is *domains*, about three per country, proposed by the same `bootstrap.py` code
that runs today, with a human reading 198 rows once rather than approving anything per request.

Entry 19's own argument is why this is cheaper than what it replaced: the human was found not to be
exercising taste but applying one mechanical rule. **Committing that rule's output is strictly easier to
audit than re-running it live** — the riskiest automated decision in the system becomes a reviewable diff.

Four things it buys, and the fourth is the one that matters most:

- four searches leave the cold request path (entry 25's remaining time is search latency and two model
  calls);
- the trusted set stops varying between runs, removing the coin-flip class of bug at its source;
- `withheld_domains` becomes a thing a person actually reads, which known problem 2 asks for and nobody does;
- **entry 33's gap becomes fixable by editing a data row** rather than by widening a regex that guards
  everything.

**Rejected: keeping bootstrap in the request and caching it per country instead of per corridor.** It fixes
the variance but leaves the highest-risk decision unreviewed and unreviewable, and still spends the searches
on a cold country.

---

## 33. The governmental half of the trust rule fails closed for a fifth of the world
**2026-08-18 · measured, and its reporting fixed; the amendment itself is not implemented**

Known problem 2 named the wrong half as the risk. It warns about `belongs_to_destination` — "a country whose
government publishes outside its own TLD". The half that actually fails first, and far more widely, is
`looks_governmental`.

`GOVERNMENT_PATTERNS` in `bootstrap.py` recognises `gov`, `go.xx`, `gouv.xx`, `gob.xx`, `govt.xx`, `gc.ca`,
`admin.ch` and `europa.eu`. All seven verified countries happen to sit inside that list — `.gov.sg`,
`.go.jp`, `.gouv.fr`, `.gov.cn`, `.gov.br`, `.gov.vn`, `.gov`. The 22/22 agreement with recorded human
decisions behind entry 19 is therefore **survivorship**: every country audited was one the pattern list
already handled.

**Measured offline, 2026-08-18, no network and no search credit** — `is_own_government` run against a
hand-written table of 51 countries' real immigration or foreign-ministry domains: **32 pass, 19 fail.**

| | |
| --- | --- |
| Fail | AT, BE, **CA**, CL, CZ, **DE**, DK, FI, GR, HU, IE, **IT**, **NL**, NO, PT, RO, RU, **SE**, UY |
| Cause | uniformly *no governmental marker in the hostname* — never the TLD half |

Every failure returns `is_own_government == False` for the domain a traveller would actually need read.
The failure is **safe** — nothing is fetched, nothing is guessed — but it takes most of Schengen with it.

**Refined while committing the test, 2026-08-18: this is two failures, not one, and the quieter one is
worse.** The claim above was originally written as "the country's entire government is refused", which is
true only where the government has *no* marked domain anywhere:

| | Countries | What actually happens |
| --- | --- | --- |
| **Refused outright** | AT, BE, DE, DK, FI, NL, NO, SE, UY | Nothing passes, so `AutomaticDestinationService.destination_for` raises *"No domain belonging to Germany's own government could be identified"*. Honest refusal, **wrong diagnosis**. |
| **Reachable, but not where the answer is** | CA, CL, CZ, GR, HU, IE, IT, PT, RO, RU | Some marked domain exists (`interno.gov.it`, `gov.ie`, `gob.cl`, `cic.gc.ca`), so bootstrap **succeeds** — and builds a trusted set that cannot contain the page holding the visa guidance. |

The second row is the dangerous one, because **nothing reports it.** The corridor resolves against real
government domains and then refuses for looking like a ranking failure, or worse resolves to whatever those
domains do say. Canada is the sharpest case: `gc.ca` is special-cased and still passes, but immigration
content moved to `canada.ca`, so the rule trusts the old namespace and misses the live one. `AT` and `UY`
are narrower again — `gv.at` and `gub.uy` are conventions simply missing from the marker list.

**And it exposed a reporting defect that made the second row hard to notice — now fixed.**
`auto_trusted_domains` had two reasons for declining a domain and both were wrong for this case: Italy's
`esteri.it` was withheld as *"not a government domain for this destination"* — false, and
**character-identical to the reason a commercial visa agency got**. Known problem 2's only recommended
mitigation is to read `withheld_domains`, so the one safeguard misled rather than warned, and entry 34's
registry would have handed a human 198 countries of these labels to skim.

**Fixed 2026-08-18** by splitting that branch three ways. A domain under the destination's own top-level
domain with no recognised marker now says what is true — it could not be *confirmed* as an authority, it
may well be a real one, and for governments with no marker convention the domain has to be named in
reviewed data. A domain that is neither says so plainly. Measured on Italy's shape, the ministry and the
agency no longer read alike.

`unconfirmable_authorities` names those candidates, and `destination_for`'s refusal uses it: *"No domain
belonging to Germany's own government could be **confirmed** … Candidates under Germany's own top-level
domain were found — auswaertiges-amt.de — but none of their hostnames carries a marker this agent
recognises as governmental."* The old wording said none could be **identified**, which is false and sends
a reader to look at search or ranking rather than at the trust rule.

**Reporting only: nothing is accepted for want of a marker**, and a test asserts the accepted set stays
empty. "Looks like an authority" is exactly what the rule refuses.

**Committed as `tests/test_trust_coverage.py`** — 7 tests, offline, no credit. It freezes the failing set so
a change is a visible diff, asserts every failure is on the governmental half rather than the TLD half,
holds the two rows above apart, and guards `countries.yaml` against another country acquiring a governmental
marker in its `tlds` unreviewed. **Verified the tripwire actually fires** by simulating the forbidden fix:
adding `.de`/`.nl` to `GOVERNMENT_PATTERNS` trips three of the seven, including the one asserting that a
German commercial visa agency is indistinguishable from the ministry on the only half that would remain.
France was added to the table afterwards and passes — it fails at HTTP, which is a different limit.

**The mechanism is robust even where the table is not.** The domain list was written from knowledge rather
than fetched, so individual rows may be wrong. It does not matter for the finding: Germany, the Netherlands,
Italy and Sweden have no `gov.de`/`gov.nl` convention at all, so **no** choice of domain rescues them. Two
failures are narrower and worth separating: `gv.at` and `gub.uy` are simply markers missing from the list,
and **Canada** fails only because immigration content moved to `canada.ca` while the special case still
names `gc.ca`.

**Decided: amend through reviewed data, never by widening the regex.** Adding `.de`, `.nl`, `.it` and the
rest as governmental markers would trust every commercial site in those countries — `belongs_to_destination`
cannot narrow it, because these are the countries whose own TLD is the *only* other signal. The registry in
entry 34 is where a named authority domain is written down and reviewed, which is exactly the
"looks official" judgement the rule refuses to automate, made once by a person in git.

`gv` and `gub` may be added to `SUFFIX_MARKER_LABELS`/`GOVERNMENT_PATTERNS` as ordinary marker fixes, and
`gc.ca` should gain `canada.ca` — those are corrections within the existing rule, not relaxations of it.

**And a second break the same measurement exposes, which is not a bug but a definition problem.** For
Schengen short-stay visas the decision genuinely lives at EU level as much as nationally. `europa.eu` passes
`looks_governmental` but can **never** pass `belongs_to_destination` for any member state, so "the
destination's own government" is the wrong trust unit for a supranational visa regime. The fix is data — a
reviewed supranational-domain list per member — but it amends the rule stated in entry 19 and in `CLAUDE.md`,
so it needs deciding rather than patching.

**Done: the check is committed** as `tests/test_trust_coverage.py`, which was the cheapest evidence this
project could buy and needed no network, model or search credit. What remains is the amendment itself —
the registry in entry 34, then reviewed authority domains for the 19, then the supranational list.

---

## 32. A block hands over a link only when it plausibly held the answer
**2026-08-18 · defect found by review; narrowed and implemented**

Entry 27 is the one shipped change never run live, and reading it against the code found the prose and the
behaviour disagree in two ways. Both widen the exception beyond what entry 27 argued for.

**1. Entry 27 says only `401`/`403` qualify. The code also accepts `429`.**
`BLOCKING_STATUS_CODES` is `{401, 403, 429}` in `domain/models.py`, `CrawlFetcher` records all three as
`blocked`, and `ResolvedCorridor.inaccessible_urls` is built from `blocked_urls()` with no filter. So a
transient rate limit can resolve a corridor, force the visa decision to unknown, and be handed to a
traveller as *"this authority refused us"*. Entry 27's own reasoning about `502` applies exactly: a `429` is
a transient fault where "try again later" is the honest advice.

**2. `decision_is_unverified` never checks that the blocked page could have held the decision.**

```python
return "visa_decision" not in filled and bool(self.inaccessible_urls)
```

Any blocked URL anywhere in the crawl, plus any readable source, is enough. The blocked page need not be a
plausible decision source — a `403` on a footer link qualifies. **This is the refusal discipline leaking**,
and it leaks in the worst available direction: WAF `403`s on incidental pages are common at scale, so
corridors whose decision was simply *not found* — the case that must refuse — will increasingly present as
*authority-blocked*, the case that resolves. Entry 27's narrowness was the whole reason it was safe to ship.

**Decided:** drop `429` from what may be handed over (it stays `blocked` for reporting — entry 18 requires
that — but stops qualifying a corridor), and require the blocked URL to have been a **credible
`visa_decision` candidate**: shortlisted for that role, or scoring above a floor for it. A block that cost
us nothing we were looking for is a fact worth reporting and not a reason to resolve.

This narrows entry 27; it does not reverse it. France is unaffected — `france-visas.gouv.fr` is precisely a
credible decision candidate, which is the case the exception was built for.

**Implemented 2026-08-18.** `PERSISTENT_REFUSAL_STATUS_CODES = {401, 403}` sits beside
`BLOCKING_STATUS_CODES`, `CrawlFetcher` records which status a refusal came back with, and
`ResolvedCorridor` gained `decision_blocking_urls` — carried *apart* from `inaccessible_urls`, because
every refusal is worth reporting while only the refusal of a page that could have answered the question
licenses resolving one. `is_usable` and `decision_is_unverified` read the new field. Three things must now
hold: the refusal is settled, the page plausibly held the decision, and something readable remains to cite.

**Credibility is the score the page already earned for `visa_decision` as a link, above zero.** A low bar
deliberately, rather than a tuned one: the scorer already **vetoes** site furniture, archived paths and
wrong-audience pages outright, so any positive score means real signal was seen. Nothing here judges what
the page *says* — nobody read it, and nobody may.

**A limit worth recording, because it fails toward refusing.** Only pages the pipeline scored can be
judged, and the crawl discards a page it could not fetch, so a refusal first met at crawl depth is not a
candidate and cannot qualify. An authority's own visa portal is what search returns first — France-Visas is
exactly that — so the case this exists for is covered, and a corridor that loses its answer this way
refuses.

**Verified by mutation rather than by the tests merely passing.** Reintroducing each defect fails exactly
the intended test: letting `429` qualify again trips
`test_a_rate_limit_is_reported_but_can_never_resolve_a_corridor`, and reverting `decision_is_unverified` to
read `inaccessible_urls` trips `test_a_block_that_could_not_have_held_the_decision_resolves_nothing`.
301 tests pass.

---

## 31. A failed adjudication refuses rather than falling back to the heuristic
**2026-08-18 · amends entry 16 · implemented**

Entry 16 chose: *"a failed call falls back to the heuristic, so a corridor degrades to a worse answer, never
to none."* That reads as conservative and is the opposite.

The heuristic is the decider **entry 15 proved gives confident wrong answers**: Brazil's Riyadh page as the
document checklist, at exit 0, full confidence, nothing in the output suggesting the checklist belonged to a
mission on another continent. Entry 15 called that "the outcome entries 5 and 6 exist to prevent." So the
fallback converts a transient OpenAI outage into precisely that outcome, in production, distinguishable only
by a reviewer noticing `decided_by`.

Every other layer of this product prefers refusing to guessing. This one line prefers guessing.

**Decided:** a failed adjudication call refuses the corridor. Retrying the call once is acceptable — a model
call is not an authority refusing us, so entry 18 does not apply — and if it still fails, the corridor is
refused with the reason, which is an outcome the product already supports and states honestly.

**What the heuristic keeps**, because neither job is affected: it builds the shortlist the model chooses
from, and it answers when `discovery_decider: heuristic` is configured, which stays tested and stays the
offline regression baseline.

**The cost, stated plainly:** an OpenAI outage takes discovery down instead of degrading it. That is the
correct trade for a product whose wrong answers send someone to a visa centre without the right papers, and
it is the same trade entry 18 makes about blocks.

---

## 30. `conflicts` is deleted, by entry 6's own rule
**2026-08-18 · implemented**

Entry 6 built a deterministic conflict detector, found a real discrepancy with it, and **deleted it anyway**
because nothing recorded who a claim applied to, so a general visa-free-nationalities page and a
nationality-specific page compared as a contradiction. It recorded the generalised lesson:

> a feature whose wrong answers are alarming must have a near-zero false-positive rate, or it should not
> ship.

What shipped instead was `conflicts` on `VisaPlan`: free text written by the model, shown to travellers in
the interface's reliability panel, with **nothing checking it**. On the axis entry 6 deleted its predecessor
for, that is strictly worse — the checked version was removed and the unchecked version kept.

**Decided: delete the field.** From `VisaPlan` and `VisaPlanDraft` in `domain/models.py`, from the
extraction prompt's rule 5, from `openai_extraction.py` and `fixtures.py`, and from the Singapore fixture
plan. A genuine disagreement between official sources still reaches the traveller through
`unresolved_questions`, which is where an unverified model observation honestly belongs.

Revisit it as the scoped redesign already specified in entry 6 and in `TODO.md` — claim scope recorded,
visa decision excluded, quantitative rules only — and not before.

**Done 2026-08-18**, from `VisaPlanDraft` and `VisaPlan`, the extraction prompt's rule 5, both extractors,
the Singapore fixture and the interface. Two details worth knowing:

- **The one real conflict this project ever found was preserved, not dropped.** Singapore's own pages
  measure passport validity from entry and from departure, which is the discrepancy entry 6's detector
  correctly caught. It is now a sentence in `unresolved_questions`, where an unverified observation
  honestly belongs, and a test asserts it is still there. Rule 5 was rewritten rather than deleted —
  disagreements must still be recorded, and never silently resolved in favour of one page — and it kept
  its number, because other documents cite rules 8a and 8b.
- **The interface lost a two-column grid, not just a block.** `.reliability-grid` was
  `grid-template-columns: 1fr 1fr`, so removing one of its two children would have left the remaining
  block rendering in half the width beside an empty column. Both the wrapper and its now-dead CSS went
  with it. Checked by injecting a plan into the real page rather than trusting the diff — the technique
  from entry 28 — confirming one heading, the block at 91% of the container, both questions rendered, no
  console error, and no horizontal overflow at 375px.

**Rejected: keeping it because it is the only conflict signal there is.** An alarming signal nobody
validates is not better than none; that is the entry 6 finding, and this field is the same mistake with the
verification removed.

---

## 29. LangGraph is not adopted, and the placeholder goes with it
**2026-08-18**

`domain/state.py` had described a "future LangGraph workflow" since the first week, `langgraph>=1,<2` was a
declared dependency in `pyproject.toml`, and **neither was imported anywhere** — verified by grep:
`VisaResearchState` appeared only on the line that defined it.

**Decided: this project does not need LangGraph, and the question is closed.** The reasoning, since a
graph framework is the obvious thing to reach for in an "agent" project:

- **There is no cycle to express.** The pipeline is linear — search → crawl → score → adjudicate → fetch →
  extract — and deliberately so. LangGraph earns its complexity on loops, conditional multi-actor routing
  and interrupts. `research/service.py`'s pipeline is two lines because there is nothing to orchestrate.
- **The control flow is the safety story, and it is Python.** Trust is enforced at three typed checkpoints
  (`validate_route`, after each redirect, after each meta-refresh). Expressing that as graph nodes over a
  `TypedDict` would move those guards from Pydantic validators — which cannot be skipped — into node bodies
  that can be reordered or bypassed. That is a real loss for no gain.
- **The one loop the placeholder imagines is one this project rejects.** `research_attempts` and
  `missing_fields` describe a re-research retry loop. Refusing beats retrying here (entries 5, 18, and 31),
  so the state shape encodes an architecture the decisions have since ruled out.
- **Durability already exists and is simpler.** `FileCorridorStore` and the source cache are the
  checkpoints a graph runner would offer, keyed to the two things whose lifetimes genuinely differ (weeks
  for corridors, hours for evidence). LangGraph checkpointing would not know that distinction.
- **LangChain stays**, and is a separate question: it is used only for structured output against a schema in
  `adjudication.py` and `openai_extraction.py`. That is a thin, working use and nothing here argues against
  it.

**Done 2026-08-18:** `domain/state.py` is deleted and `langgraph` is dropped from `pyproject.toml`. An
unused dependency in a project whose safety argument rests on a small audited surface is not free — it is
one more thing a reader must check is not load-bearing. `TODO.md` had this as "either update it or delete
it"; this was the decision to delete.

**If it is ever revisited**, the trigger to look for is a genuine cycle with human interrupts — plausibly
the client-side retrieval flow in entry 35, where a plan waits on the traveller fetching a blocked page.
Even then, one `await` in FastAPI is the cheaper first answer.

---

## 28. Four fixes from reading the interface as a traveller
**2026-08-17**

Reviewing a rendered plan rather than a JSON payload found four things, none of which a test was
going to catch.

**A step heading stopped mid-clause.** *"Create an account and complete the online application if the
wizard says a visa,"* — 79 characters against an 80-character limit. The model was writing a sentence
into a field meant for a label and ran out of room. The limit is now 70, the prompt says a title is a
short label of at most eight words with the substance in `action`, and a trailing comma is trimmed in
a validator. Trimming is safe here precisely because a heading is derived text rather than a claim.

**A corridor that cannot have an answer now costs nothing.** A national of the destination does not
apply to visit their own country, so there is no guidance to find — but the request searched, crawled
and spent two model calls to discover that, then read as a fault. It is refused up front with a plain
sentence. Deliberately *not* a claim about entry rights: it says only what this agent researches. And
deliberately narrow — it matches the **passport** only, never the residence, because applying from
inside the destination is ordinary.

**An empty checklist section is not rendered.** With no checklist source, no documents may be listed,
so the panel was a heading and a caveat above nothing. Dropping it hides nothing: the absence is
stated under unresolved questions, which such a plan is structurally required to carry (entry 23).

**The incomplete-evidence detail moved to the end.** It sat above the answer, and with a blocked
authority's reasons and links it had grown long enough to bury it. This entry does change what entry
13's era of the interface documented — *"the interface states what is incomplete above the
guidance"* — so it keeps the half that mattered: a one-line notice above the guidance, and the
reasons, links and caveats at the end. A partial plan still cannot look complete.

**Verified by driving the real renderer**, with a France-shaped plan injected into the page rather
than a live run — the search quota was exhausted (entry 27). Four panels, no checklist panel, banner
in the last one, and the blocked authority rendered as a working link. Reading it that way also caught
the banner still saying *"Everything below is still drawn only from official sources"* after it had
been moved to the bottom.

---

## 27. A block becomes a next step: name the page, hand over the link, decide nothing
**2026-08-17**

Entry 26 established that France refuses because every readable page delegates the visa decision to
a portal that answers 403. Refusing is honest but not useful: the traveller gets "no verified plan"
for one of the commonest corridors there is, when the sentence they could act on was available all
along — *France publishes this at france-visas.gouv.fr; we were not permitted to read it; open it
yourself*.

**Decided: a corridor resolves when the only thing missing is behind a block, and the plan says so.**
Three properties hold it in place, and none of them is a relaxation of entry 18:

- **Nothing is inferred.** `visa_required` is set to `null` — not guessed — and that is *enforced in
  the application*, not asked of the prompt: the model returned `true` in the test and the extractor
  overrode it. A wrong yes or no about whether someone needs a visa is the most damaging thing this
  product can say.
- **The page is named, never read.** `UnreadableAuthority` is deliberately not a `ConfiguredSource`:
  there is no content behind it, and a source with empty content is exactly what must never be
  citable. The research packet carries its URL and authority and no text, so the model is told where
  the guidance lives, not what it says.
- **It is still held to the domain rule.** A page shown to a traveller as this destination's own
  guidance must sit on an approved domain, validated in `validate_route`. This is the case that needs
  that rule most: nobody read the page, so the domain is the only thing vouching for it. The guard
  caught a test fixture of mine pairing Singapore's config with a French URL.

**The exception stays narrow.** A visa decision that was simply *not found* still refuses — the gap
must be one an authority imposed, which means a recorded `blocked` outcome, and only `401`/`403`
qualify. A `502` is a transient fault where "try again later" is the honest advice, and a host whose
DNS does not resolve must never be handed over as a link at all. Readable sources are still required:
with nothing to cite there is no plan, only a link, and
`ResolvedCorridor.is_usable` requires both.

Such a plan can never be `verified`, for the same reason a checklist-less one cannot (entry 23) and
more strongly. The interface renders the blocked authority with its URL and the plain sentence, so the
refusal becomes a next step rather than a dead end.

**Verified offline, end to end, and NOT verified live.** The chain is covered by tests from
`ResolvedCorridor.is_usable` through `to_destination_config` to the extracted plan: the decision is
forced to unknown, the authority is named with its URL in `unavailable_sources`, the status is
`partial`, and the packet carries no content for it. 286 tests pass.

**The live run could not be done: the Brave search API returned HTTP 402, out of credit.** So what a
model actually writes for France given the UK post's page plus a named blocked portal is *unverified*.
Re-run `france/IN/GB/tourism` when the quota resets, and read the plan as a traveller would before
trusting this. That is the one thing outstanding on this entry.

---

## 26. France refuses because France does not publish the answer anywhere readable
**2026-08-17 · qualified by entry 41 on 2026-08-19**

> **The title overstates what was measured.** France does not publish the answer anywhere *this client
> could read*, which is a narrower claim — the pages on `france-visas.gouv.fr` were never read, only
> challenged. Rendering them (entry 41) shows the decision and the corridor checklist sit behind a
> four-step wizard rather than on a page, so the conclusion below survives; the reason for it has
> changed from "nowhere readable" to "behind form input".

`france/IN/GB/tourism` — an Indian passport, applying from the UK — refused, and it is a corridor
common enough that the refusal deserved checking rather than attributing to the known 403.

**It was a coin flip, not a dead end.** Two consecutive runs over an identical shortlist: one
resolved, one refused. The shortlist was deterministic; the model was not. So the corridor was
marginal, and the reason was what the shortlist contained.

**Two real scoring defects, both fixed.**

1. **A host label was read as who a page is for.** `in.diplomatie.gouv.fr` is France's mission *in
   India*, and `_matches_country` matched India's host label `in`, so the nationality bonus of +40
   went to **everything that post publishes**. That beat the +30 the UK post earns for actually
   serving this traveller: on the identical page `/en/applying-for-a-visa`, the India post scored
   65.6 and the UK post 55.6. So the post for the traveller's *home* country outranked the post they
   must apply at — the same shape of bug as entry 21, a country code matching where it does not mean
   the country. The bonus now reads only the path and the title, which are the page describing
   itself; the host stays with the mission machinery, which is keyed on where the traveller applies
   from. After the fix the UK post leads 55.6 to 25.6.

   `_matches_country` itself is unchanged, because `wrong_country` needs the host label: it is what
   keeps *other* posts — France in Germany, France in Brazil — out of a corridor entirely.

2. **Site furniture took three of ten fetch places.** `/accessibilite`,
   `/en/donnees-personnelles` and `/mentions-legales` each scored 69, above the UK post's real
   pages. The mechanism is worth recording: `extract_links` gives a link the last heading seen above
   it, and footer links sit below everything, so France's legal notice inherited the heading of a
   news article about visa requirements and collected the heading bonus twice. A legal notice cannot
   be visa guidance whatever it scores, so `boilerplate_tokens` vetoes it exactly as `archive_tokens`
   does — rejecting rather than penalising.

**And with both fixed, France still refuses — correctly, and now consistently (3 runs of 3).** This
is the part that matters. The shortlist is now the right pages, and reading them shows the answer is
not there:

| readable page | what it actually says |
| --- | --- |
| `uk.diplomatie.gouv.fr/en/applying-for-a-visa` | Sends the reader to the France-Visas "visa wizard" to find out whether they need a visa |
| `uk.diplomatie.gouv.fr/en/visiting-france` | Tourism marketing — landscapes and monuments |
| `www.diplomatie.gouv.fr/en/services-to-foreigners/visiting-france` | Tourism marketing |
| `france-visas.gouv.fr` | **HTTP 403** — the wizard, and the only place the decision lives |

France's own government states the visa decision **only** on the portal that refuses automated
retrieval. Every readable page delegates to it. So there is no page that can be confirmed as the
visa decision, and refusing is the correct output rather than a ranking failure.

**Which makes the earlier resolving run the wrong one.** It named the India post's
`/en/applying-for-a-visa` as `visa_decision`, `document_checklist`, `application_route`, `fees` and
`processing_times` — five roles from a page that is a signpost saying "use the wizard". A checklist
assembled from that is exactly the output entry 6 was deleted over. The scoring fixes made the
refusal consistent by removing the noise the model was over-reaching on, but the guard against that
over-reach is `VisaPlan`'s validators, not the ranking.

**Verified no regression.** The United States is unchanged — same ten pages, same scores, same three
roles; its India-post pages keep the nationality bonus legitimately, because their *titles* name
India. Brazil's four role assignments are unchanged. China returned the same checklist and fees.

**What this says about the product, plainly:** France is unservable, and it is unservable because of
entry 18 rather than in spite of it. The honest thing to add is not a plan but the sentence a
traveller can act on — that an authority refused us, and here is the URL to check themselves. That
is already the open todo, and this corridor is now its strongest argument.

---

## 25. The politeness delay is owed to a host, not to the crawl
**2026-08-17**

A cold corridor took **54.5s**, and instrumenting it by phase showed where: the crawl spent 25.9s on
32 page fetches, of which **about 16s was sleeping**. `CrawlFetcher` awaited its 0.5s delay before
*every* request whatever host it was for, and `LinkCrawler` walked its frontier one page at a time,
so each site's spacing was also paid by every other site. Search added another 15s across 16 queries
run one after another.

**Decided: the delay is per host, and hosts are crawled concurrently.** This is *more* correct about
politeness rather than less — every host still gets its full 0.5s spacing, and the next slot is
claimed before sleeping so two requests to one host queue rather than both reading the same
last-request time. What stops is one site waiting behind another it has nothing to do with.

The frontier now yields a **wave**: the best few links, at most one per host. A second link on a host
already in the wave goes back to the frontier rather than being dropped, so nothing is lost by being
second in its queue. Results are handled in frontier order, never completion order, because which
page a corridor resolves to depends on the order candidates are seen and that must not depend on
which site answered first.

**Search runs concurrently too, bounded at four.** Measured first rather than assumed: four
concurrent Brave queries took 1.32s against 1.26s for one, with no rate-limit errors. Bounded rather
than unbounded because a search API is someone else's rate limit and a burst that trips it turns a
resolvable corridor into a refusal — `search()` raises on any non-200, and that becomes a 503. A
failing query still fails the run, exactly as when they ran in sequence; whether a partly-searched
corridor is safe to serve is a separate decision and has not been made.

**Measured, 2026-08-17, `united-states/IN/IN/tourism` cold with both caches cleared:**

| phase | before | after |
| --- | --- | --- |
| bootstrap (4 searches) | 4.5s | **1.1s** |
| crawl | 25.9s | **7.2s** |
| shortlist fetch | 1.5s | 0.9s |
| role adjudication | 11.2s | 8.1s |
| **corridor** | **54.5s** | **19.4s** |
| plan extraction | 11.8s | 14.7s |
| **cold request total** | **66.3s** | **34.1s** |

Brazil went 85.6s to 28.5s, China 161s to 43.1s. The remaining corridor time is now two model calls
and search latency, not waiting.

**What did not change, which was the condition on doing this at all.** The US corridor produced a
byte-identical shortlist — same ten pages, same order, same scores — and the same three roles.
Brazil's four role assignments are unchanged, Edinburgh checklist included. **Coverage bounds were
not touched:** `maximum_pages` is still 40 and `maximum_pages_per_host` still 20, because those bound
what can be found and Japan's checklist was two hops deep.

**One corridor did change, and it is worth knowing.** China's `document_checklist` resolved to
`gb.china-embassy.gov.cn/eng/visa/qzxz/201303/t20130315_3383966.htm` (38.2) where it had been
`.../eng/xnyfgk/201303/t20130315_3317069.htm` (34.2). Same title, same authority, same `201303`
publication path: the embassy publishes that document under two sections, and which duplicate is
discovered first depends on crawl order. The new one scores higher, and the roles are otherwise
identical. So crawl order *was* mildly load-bearing — for choosing between duplicates of one
document, which is the harmless end of that risk.

---

## 24. A fetch place is not spent on a page already proved unreadable
**2026-08-17**

Inspecting the US shortlist directly showed **five of its ten fetch places going to pages that
cannot be read**: `sample2.usembassy.gov` — a documentation sample host that does not exist in DNS —
scoring highest of everything at 122.2 and taking the place reserved for the mission network,
`go.usa.gov` twice (a decommissioned shortener, also no DNS), and `travel.state.gov` twice (the 403).
Brazil spent one of its ten on `brics2019.itamaraty.gov.br`, likewise dead. Ten places decide what is
read, and only a read page can fill a role, so this was the largest remaining waste in a corridor.

**Decided: drop a candidate only for a failure already observed, never for one predicted.** Two
kinds qualify, and the distinction between them is the whole design:

- **A host whose name does not resolve** is skipped for every path beneath it. DNS failure is a fact
  about the *host*, so nothing under it can be read.
- **A URL an authority refused** is not requested again. Asking twice is a retry, which is the one
  thing a block must never provoke, and it would answer the same way.

**Detected by exception type, not by message.** `host_does_not_resolve` walks the cause chain for
`socket.gaierror`, because the wording differs per platform — macOS `[Errno 8] nodename nor servname
provided`, Linux `[Errno -2] Name or service not known` — while the exception type does not.
`CrawlFetcher` now records a `FailureOutcome` beside each prose reason, which also lets
`inaccessible_domains` be derived from `outcome == "blocked"` instead of matching the substring
"refused automated retrieval" in a sentence someone could reword.

**Deliberately not skipped: everything else.** A page that was too large, was not HTML, or answered
`502` stays a candidate, because **retrieval is not the crawler** — it reads PDFs, renders, and
carries different limits, so a page the crawl could not use may still be readable evidence. Losing a
real page costs a refusal, and that is the more expensive mistake.

**Measured, 2026-08-17.** Three of the five places came back, and they went to real pages:
`in.usembassy.gov/apply-for-a-nonimmigrant-visa` (95.6), `in.usembassy.gov/immigrant-visas`, and
`www.usa.gov/non-immigrant-visas` now sit in the shortlist where dead hosts did. Identical across two
cleared-cache runs. Brazil's roles are unchanged, all still filled including the Edinburgh checklist.
China is untouched by design: its unreadable hosts answered `502`, which stays a candidate.

**`document_checklist` is still unfilled for the US, and the freed places did not change that** — the
prediction in the todo that they might was wrong. The canonical B1/B2 checklist is on
`travel.state.gov`, which is blocked, and no mission page was judged to be one. That is the honest
outcome rather than a remaining bug.

**What is left, and why it was not taken.** Two places still go to `travel.state.gov`, because those
two URLs were never crawled — one is a PDF, which the crawl skips by design — so nothing was observed
about them and the per-URL rule does not apply. Skipping the whole host would recover them, and
`travel.state.gov` has in fact refused every request made to it. It is not taken here because a `403`
on one path is genuinely not evidence about another: real sites refuse some paths and serve others.
Recorded in [TODO.md](TODO.md) as a measured follow-up — a host that has refused every request and
served none — rather than assumed now.

---

## 23. Entry 14's decision never reached a traveller, because extraction refused first
**2026-08-17**

With the corridor fixed (entry 22), `united-states/IN/IN/tourism` still answered *"The visa plan
could not be generated safely."* Discovery resolved; the **extractor** refused:

```
LLMExtractionError: Application document sources are not available in this run
```

**The bug is an unimplemented decision, not a new one.** Entry 14 stopped a missing checklist
refusing the corridor and built `VisaPlan.validate_absent_checklist` to make the resulting plan safe:
with no document source a plan may state the gap but never fill it. `VisaPlan.requirements` was
documented as *"May be empty: some authorities publish no checklist"*. But
`openai_extraction.extract` still required `application_document_source_ids` to be non-empty, so that
validator could never run and no traveller ever saw the outcome entry 14 chose. Vietnam — the
country entry 14 was written for — would have hit the same wall.

**Decided:** an *undeclared* checklist is a fact about the world and is allowed. A *declared but
unretrieved* one is a broken run and still refuses, before the model call, via
`require_load_bearing_sources`. The distinction is the whole point: relaxing the first must not
relax the second.

Two consequences kept deliberately strict:

- **Anything the model offers as a document requirement is dropped** when no checklist source backs
  it. Nothing could honestly cite one, so keeping it would mean publishing a checklist inferred from
  an eligibility rule or an application form — the single most damaging output this project can
  produce, and what entry 6 was deleted over. The prompt asks; the filter and the validator
  guarantee.
- **A plan with no checklist source is never `verified`.** It is missing evidence a traveller would
  expect a complete plan to rest on, and `verified` beside an empty document list is the one label
  that would hide that. `resolve_plan_status` takes `has_checklist_source` so both extraction paths
  answer this the same way. The interface already renders `partial` with a reliability block.

**Also fixed:** the old code made the model call and *then* refused, so a run that could not succeed
still cost money — contradicting the comment three lines above it. Both remaining preconditions now
run before the call.

**Verified live, 2026-08-17.** `POST /visa-plans` for an Indian passport, resident in India,
travelling to the United States for tourism: **HTTP 200 in 16.6s**, `status: partial`,
`visa_required: true`, `B-2 visitor (tourist) visa`, five application steps, three cited sources,
zero document requirements, and three unresolved questions — the first of which names the missing
checklist and points the traveller at the Department of State and their nearest post. That is the
honest shape of this corridor: the canonical B1/B2 checklist is on `travel.state.gov`, which answers
403, and by entry 18 we may not work around it.

**What this exposes, and does not fix.** The plan cannot say *why* the checklist is missing. Its
`unavailable_sources` covers only its own retrieval, and this block happened during **discovery**, so
`ResolvedCorridor.inaccessible_domains` never reaches the plan. The traveller is told the checklist
is absent but not that an authority refused us — which is the more useful sentence, because they can
open that page themselves. That is the existing todo *"Tell a traveller what an inaccessible source
means"*, now with a concrete instance rather than a hypothetical one.

> **Corrected 2026-08-18.** The paragraph above stopped being true when entry 27 shipped, and stayed in
> the todo list for a day longer than it should have. `to_destination_config` fills
> `unreadable_authorities` from `inaccessible_urls` **unconditionally** — not only when the decision was
> blocked — the extractor carries them into `unavailable_sources` regardless, and the interface gives any
> `blocked` failure with a URL the sentence *"does not permit automated retrieval"* and a link. A
> retrieval-time block reaches the plan by a second route through `RetrievalReport.failures`. So the
> mechanism exists twice over, and the remaining question is only whether it *reads* usefully, which
> needs a live run. Left here rather than rewritten, because the mistake is instructive: this was
> described from reading the code path that used to exist instead of from a plan.

---

## 22. A large government passes the same rule with far more domains, so how many is capped
**2026-08-17**

`united-states/IN/IN/tourism` refused, and not reliably: two runs of the identical corridor, one
resolved, one refused. One of the highest-volume corridors there is, decided by search ordering.

**The rule was not wrong; it was calibrated against small governments.** Entry 19 trusts a domain
that is `looks_governmental and belongs_to_destination`, and for the United States that still admits
only the US government — nothing foreign gets in. But its own top-level domain *is* `gov`, so the
second test stops narrowing anything and the whole federal namespace qualifies: `doi.gov` (the
Interior) and `federalregister.gov` alongside State and USCIS. Measured: **eight domains**, against
Brazil's one, France's two, China's four. `countries.yaml` has exactly one entry like this today,
which is why six corridors never showed it.

Width is expensive in three places at once, and this is the part worth remembering: three search
queries are run **per trusted domain**, the crawl's per-host budget is the page budget **divided by**
the hosts seeded, and the shortlist has ten places. So a wide set spends more, reads less of each
site, and makes the right page compete with more noise. The measured US bootstrap:

| domain | queries seen in | hostname hint |
| --- | --- | --- |
| `state.gov`, `usa.gov` | 4 | — |
| `dhs.gov` | 3 | — |
| `usembassy.gov` | 2 | embassy |
| `doi.gov`, `federalregister.gov`, `ice.gov`, `uscis.gov` | 1 | — |

**Decided, in two parts, neither naming a country.**

1. **The relaxed evidence bar is scoped to where it was earned.** One corroborating query is enough
   for the destination's own government (entry 19) *because* that is two independent signals. Where
   the country's own top-level domain is itself the governmental marker it is one signal, so the
   ordinary two-query bar applies. The test is which top-level domain actually matched, so it is a
   property of `countries.yaml` data and not of any country. This is what removes all four
   single-query agencies above — and it does **not** touch `usembassy.gov`, which is corroborated
   twice.
2. **A universal cap of five, ordered by the hostname's authority hint.** A bound on the consequence
   rather than a test for the cause: a large government under a plain ccTLD would cost the same.
   `suggest_kind` — `emb`, `consul`, `immi`, `mofa` — is already committed, country-neutral, and
   already used to name authorities; ordering by it is the generic form of "rank the mission network
   first", where hardcoding those names would be special-casing one country in effect.

**Five is calibration, not derivation.** It is chosen to sit above every accept in entry 19's audit
(one, two and four) so no recorded decision changes, and below the eight that caused this. Say it
plainly, because a reader will otherwise look for the reasoning that produced the number.

**Two admissions about the ordering.** Ranking the mission network above the State Department is
desirable here only because `travel.state.gov` answers 403 — a happy accident, not a principle. And
among equally-corroborated domains with no hint the order is alphabetical: a hostname simply carries
no signal about whether that part of a government issues visas. On this corridor the corroboration
bar made that moot, but a wider case would be decided arbitrarily-but-stably.

**Third part, downstream and independent of trust: the shortlist reserves a place per domain.** The
ten places decide what is *read*, and only a read page can fill a role, so an authority whose pages
all score below another's is not merely ranked low — it is absent, and the corridor refuses with the
answer one slot outside the cut. Each registrable domain's best page is now reserved one place.
Keyed on the registrable domain, not the host, or a mission network's posts would reserve every
place; that is a deliberate difference from the crawl's per-host budget, which prevents hammering
one site rather than one site starving another. Reservation is drawn from **every** candidate rather
than those already picked, since the per-role cut takes three and a domain's best page can be fourth.

**Rejected: raising `shortlist_size` from ten.** It makes the right page more likely to be read
without ever guaranteeing it, at similar cost. The floor guarantees it.

**Rejected: detecting the collapsed rule and treating that country specially.** Considered and
dropped in favour of the two changes above precisely so that no code path tests for the condition.
Nothing here can be a country-shaped fix, because nothing here asks about a country.

**Verified live, 2026-08-17.** The US corridor run three times with `var/cache/` and `var/corridors/`
cleared between runs gave **identical** results each time — trusted set `usembassy.gov`, `state.gov`,
`usa.gov`, `dhs.gov`; `visa_decision`, `application_route` and `general_entry` filled by the model;
twelve corridor queries where eight domains had produced twenty-four. `document_checklist` stays
unfilled, correctly: the canonical B1/B2 checklist is `travel.state.gov`, which answers 403, so it is
reported as `blocked` and nothing is substituted (entry 18). Brazil filled every role including the
Edinburgh post for a UK applicant; China returned its checklist and fees and still declined
`visa_decision`, matching what entry 17 recorded. No corridor changed for the worse.

**What the runs also showed, and did not fix.** Half the US shortlist is spent on hosts that cannot
be read: `sample2.usembassy.gov` and `go.usa.gov` do not resolve in DNS, and two `travel.state.gov`
pages are the 403. The reserved place for a domain goes to its best-scoring candidate even when the
crawl has already recorded that host as unreachable, so Brazil spends one place on
`brics2019.itamaraty.gov.br` the same way. Recorded in [TODO.md](TODO.md) rather than fixed here: a
DNS failure is host-level and definitive, but a 403 on one path is not evidence about another, so the
two cannot be skipped by the same test.

---

## 21. Any country is a destination, and a country name stops matching inside a word
**2026-08-16**

The interface still offered the seven entries in `destinations.yaml`, most of them disabled, and
its copy announced research "for an ordinary Indian passport holder resident in the UK". Both were
left over from when that was true.

**Decided:** the destination list is every country the agent holds reference data for, and the copy
describes the product rather than one traveller. `countries.yaml` grew from 14 to **198**. A country
is now identified by a slug derived from its name, so "United Arab Emirates" and
"united-arab-emirates" reach the same place however a caller writes it.

The fourteen curated entries keep their hand-written synonyms, demonyms, host labels and mission
cities, learned from corridors actually run. The other 184 carry only what can be stated without
guessing: the name and the ccTLD, which is the ISO alpha-2 lowercased for every one of them.
**`tlds` is the load-bearing field** — it is what decides whether a domain belongs to the
destination's own government, the rule that replaced human approval. The rest are scoring aids the
model decider does not need, so a generated country is fully researchable, just with weaker hints.

**A live bug this uncovered, and the reason the expansion was not safe without it.**
`_matches_country` matched country tokens as **substrings** of link text. Its own docstring promised
codes are "never matched inside a word", but that guard was only ever applied to path segments. So:

    "Business visa"   -> vetoed as United States      ("us" inside "business")
    "Chadwick House"  -> vetoed as United States      ("us" inside "House")

`wrong_country` is a **veto**, so every business-purpose corridor was silently throwing away its
most relevant page. Matching is now on word boundaries. Adding 184 more country names to a
substring veto would have multiplied this — "oman" sits inside "Romania", "chad" inside "Chadwick" —
which is what made the bug worth finding before the data grew.

**Verified after the change:** Brazil still resolves the Edinburgh checklist with 198 countries in
the veto list, and a page genuinely about another country is still rejected.

---

## 20. The traveller becomes input; countries become codes
**2026-08-16**

The last fixed piece. `TravellerProfile` was one constant — Indian passport, UK resident, tourism —
with `uk_immigration_status` and `uk_permission_expiry` baked into the model and `travel_purpose`
narrowed to `Literal["tourism"]`.

**Decided:** the profile comes from the request. Three things are required, because three things
select the guidance: the passport, the country applied from, and the purpose. Everything else is
optional — a plan that does not use a detail should not ask for it, and this is personal data.

**Countries are stored as ISO codes, not names.** A name has many spellings and a code has one, and
every corridor, cache key and lexicon lookup is already keyed by code. The API accepts whatever a
person wrote — "IN", "in", "India", "Republic of India" — and normalises once, at the edge. A
country with no reference data is refused there too, before anything runs, because without its own
domains and demonyms the right pages cannot be identified.

**But the model is shown names.** The packet renders "India (IN)": codes are the canonical *key*
and the wrong *input* for something reading government prose, where an entry table may say either
and the prompt forbids using knowledge the packet does not contain. Caught by a test that had
asserted "India" and started seeing "IN" — the assertion was right and the change was wrong.

**`uk_immigration_status` became `residence_status`, and optional.** Not a rename: a citizen of
where they live holds no permit. It stays because it is frequently decisive — Brazil and China both
require a non-citizen resident to prove regular status, and the Brazil plan cited exactly that.

**`passport_type` stays `Literal["ordinary"]`, deliberately.** Diplomatic and official passport
pages are a hard veto in discovery's scoring (entry 8), so those travellers cannot be researched.
Widening the field would let a request be accepted and then answered with the ordinary-passport
rules, which is precisely the confident wrong answer this project refuses. Refusing at the schema
is the honest form.

**Verified:** a corridor nobody had run — Chinese passport, resident in the UAE, to Brazil —
resolved to Brazil's **visa waiver page for China**, where the same destination for an Indian
passport resolves to a VIVIS document checklist. The traveller changes the answer, end to end.

---

## 19. The human approval gate becomes a rule, not an absence
**2026-08-16**

Discovery was an offline command whose output a person reviewed before anything could serve a
traveller (entry 7). The product needs destinations nobody has configured, so that gate is removed
and discovery runs in the request path.

**What removing it does not mean.** The gate was the concentration point for the entire added risk
of search (entry 11), so deleting it outright would put a commercial visa agency one lucky ranking
away from being quoted as an authority. Reading back six real bootstraps, the human was not
exercising taste. Every accept and reject reduced to one question — *is this the destination
country's own government?* — which is `looks_governmental and belongs_to_destination`, both already
computed. Checked against all 22 recorded decisions: **22 agreements, 0 disagreements.**

**Decided:** `destination_mode: automatic` resolves an unconfigured destination at request time,
trusting only domains that pass that rule. What it keeps out is the point: France's bootstrap
surfaced `axa-schengen.com`, a commercial travel insurer; Vietnam's ranked `usembassy.gov` first, a
real government describing the rules for *Americans*; Brazil's offered VFS, an appointed provider
that by design cannot pass domain trust.

Everything downstream is untouched. Public suffixes are still refused, so `gov.br` cannot be
trusted whole. Pages are still fetched only from approved domains, redirects and renders still
re-checked, a corridor missing a load-bearing role still refused, and `VisaPlan` still rejects a
checklist with no source behind it. If no own-government domain is found, **nothing is fetched**.

**Verified end to end.** Brazil, which has no configured sources, produced a `verified` plan:
visa required, Visitor Visa (VIVIS), six requirements each citing a discovered page — including
"proof of regular UK immigration status", correct for an Indian national resident in the UK.

**Why this is safe to ship without human review**, in the product's own terms: the plan promises
nothing. It shows information, shows its citations, and says plainly what it could not verify. The
traveller decides. That only holds while the refusals stay honest, which is why every refusal path
above is load-bearing rather than decorative.

**A latent crash this surfaced:** a search engine returns titles far longer than any anchor text,
and `PageLink.text` caps at 300 characters. China's ministry returned a 300-plus character speech
headline and the corridor raised instead of trimming. Search titles are now truncated exactly as
crawled anchor text always was.

**Still fixed, and next to change:** the traveller profile. The corridor is derived from it rather
than hard-coded, so making it variable changes one function instead of the request path.

---

## 18. A block is not a fact about the guidance; never work around one
**2026-08-16 · amended by entry 41 on 2026-08-19**

> **Read entry 41 with this.** The prediction below — that a headless Chromium would pass France's
> check — was measured and is correct, and the premise was wrong: `france-visas.gouv.fr` serves a
> Cloudflare *challenge* (`cf-mitigated: challenge`), not a refusal, and serves it for `robots.txt`
> too, so no policy was ever stated. A challenge may now be answered by the renderer under our own
> user agent. Everything below still governs an actual refusal — a `401`, a bare `403`, a `429` — and
> the prohibitions on spoofing and retrying are untouched.

France's portal answers `403` to anything that is not a browser. A headless Chromium would very
likely pass that check, and the renderer is already built and already trusted. The tempting fix is
one line: render on `403` as well as on thin text.

**Decided: never.** No user-agent spoofing, no pointing the renderer at a refusal, no retrying past
a rate limit. The reasoning is about what a block actually licenses us to say. It is not evidence
that the guidance is wrong, missing, or stale. It supports exactly one claim:

> We cannot independently retrieve and verify this in this execution environment.

That is narrower than "unreachable", and far narrower than anything that would justify filling the
gap from a different page. So the source is marked inaccessible, the role goes unfilled, and
nothing is inferred in its place. `FailureOutcome` gained `blocked` to say it precisely, and
`ResolvedCorridor.inaccessible_domains` carries it as data rather than prose, so a refusal can
never be mistaken for "nothing found".

**Why this is a feature.** The alternative architecture is "if France blocks us, figure out how to
defeat the bot protection", and that is a posture, not a patch — it would sit oddly beside every
other rule here, all of which prefer refusing to guessing. For visa requirements specifically,
inferred or stale information sends someone to a visa centre without the right papers. A product
that cannot verify something should say so.

**What it costs, stated plainly:** France is unservable. Singapore's VFS page stays unread. That is
the correct trade, and it is recorded in `CLAUDE.md` under the rules that must not be broken,
because the "helpful" one-line fix will occur to someone again.

**Not the same as:** reading a page a site serves us normally. Rendering client-side pages stays on
demand and unchanged — that is running a page the way it was published, not circumventing a refusal.

---

## 17. France and China: the decider refuses well, and the wall is now access, not ranking
**2026-08-16**

Two fresh corridors against the model decider, neither built against. Both **exit 2**, and what
they refused on is the finding.

**France.** Both approved government domains answer **HTTP 403** to anything that is not a browser
— `france-visas.gouv.fr`, the authoritative portal, and `www.diplomatie.gouv.fr`. Ten pages were
still fetched from paths that slipped through, so the model had ample plausible material. It filled
only `general_entry`, and refused `visa_decision` and `document_checklist` outright. That is the
behaviour the containment was built for, tested under real pressure rather than with a fake.

**China.** Reachable, and the two roles it filled are the best evidence yet that judgement beats
scoring. For `document_checklist` it chose the UK embassy's own page and justified it with "names
the required passport, photo, **UK legal-stay evidence for non-British applicants**, and round-trip
tickets" — it noticed the traveller is an Indian national *resident in* the UK, which no keyword in
the lexicon expresses. For `fees` it read a rate table and reasoned "gives the rate for 'Other
countries,' which includes an Indian passport holder". It refused `visa_decision`, which is
load-bearing, so the corridor is refused.

**Where the limit has moved.** Of six corridors, ranking is no longer what fails. What fails now is
**access**: bot-blocked portals (France ×2, Singapore's VFS), client-rendered shells, and
502-ing endpoints. Discovery cannot judge a page it was never allowed to read.

**Deliberately not done: defeating the bot blocks.** Settled in entry 18.

**A staleness gap this surfaced**, now addressed. China's chosen checklist lives at
`/eng/visa/qzxz/201303/t20130315_3383966.htm`, and `is_archived` did not fire because it only
recognised a bare four-digit year segment. Detection is now widened — `published_date_in_path`
reads `YYYYMM`, `YYYYMMDD` and `tYYYYMMDD` — but the *consequence* deliberately is not a veto.
Measured first: **two of China's correct picks carry dated paths**, the checklist at `2013-03` and
the fee table at `2024-08`. Vetoing dated paths would have discarded the only two roles that
corridor resolved. Publication is not staleness, and a URL cannot tell them apart. So the date is
reported — to the adjudicator, which holds the page's text and can weigh the two, and in the
proposal, where a human sees "published in path: 2013-03" beside the choice.

---

## 16. Judgement decides the last step; heuristics decide everything before it
**2026-08-16**

Entry 15 recorded that keyword ranking does not generalise. Two fixes followed — a checklist is
identified by the documents it *names*, and the post serving the traveller governs the roles that
depend on the post — and both worked: Brazil picked the right page, Japan and Singapore held. But
they worked by adding **27 English document nouns** and per-country city labels in Portuguese, and
that is a treadmill. It will not survive an authority publishing in Thai.

The decisive observation is *where* the failure was. In every Brazil run the correct page was found
by search, passed domain trust, survived the crawl, made the shortlist, and was fetched and read
with its full text available. Only the final choice among ten trusted, already-fetched pages was
wrong. Everything upstream — the safety-critical part — was right.

**Decided:** keep search, trust, crawl, shortlisting and refusal deterministic, and ask a model
exactly one question: which of these fetched pages fills each role. `ResolvedSource.decided_by`
was already `Literal["heuristic", "model"]` and `ResolvedCorridor.model_calls` already existed —
the seam was designed in and left unused.

**The containment is the whole safety story**, and none of it may be removed:

- the model chooses from an explicit list of candidates the application built; an id it invents is
  **discarded** and the role left unfilled, so it can never introduce a page that did not pass
  domain trust;
- it never widens trust — officialness was settled by who controls the domain, long before this
  runs;
- page text reaches it under `untrusted_content` and the prompt says so;
- it may refuse, and is told refusing beats guessing;
- heuristic scores are **withheld** from the packet, because passing them would anchor the model to
  the very ranking that got Brazil wrong;
- a failed call falls back to the heuristic, so a corridor degrades to a worse answer, never none.

**Measured on all four corridors** (`discovery_decider: model`): Brazil picks the Edinburgh
checklist and explains why — "it specifically lists the application form/RER, valid passport,
passport photo, return-ticket evidence, financial evidence" — and reads India's row out of a
national visa table for the decision. Japan picks the UK embassy's items-required page. Singapore
puts five roles on the ICA per-nationality page, arriving unaided at what entry 9 had to be taught.
**Vietnam still refuses the checklist**, which was the risk worth testing: the model did not invent
one where none is published.

**Rejected — staying fully deterministic.** It keeps zero model calls and total explainability, but
buys them with a new failure mode per country and per language, and Brazil showed those failures are
silent.

**Rejected — model classification earlier in the pipeline.** Letting a model decide what to crawl or
what to trust would put it upstream of the domain rules, which is the one place it must never be.

**What this costs:** one model call per corridor, non-determinism in the final choice, and a new
dependence on `OPENAI_API_KEY` for `visa-discover`. The heuristic path remains, is tested, and stays
the regression baseline.

---

## 15. Brazil, the out-of-sample test: discovery ranks the wrong page, confidently
**2026-08-16**

Discovery's scoring was tuned against Singapore and Japan; Vietnam turned out to publish no
checklist, so it could not test ranking. Brazil is the first corridor that genuinely could, and the
answer is that **ranking does not generalise**. Recorded rather than fixed, deliberately: this is
the only out-of-sample signal there is, and tuning weights to make it pass would spend it.

`visa-discover corridor --destination brazil --nationality IN --from GB` **exits 0** — every
load-bearing role filled, full confidence — and picks this as the document checklist:

    43.1  embaixada-riade/how-to-apply-for-services-on-e-consular      (Riyadh, Saudi Arabia)

The correct page exists, was found by search at depth 0, was shortlisted, and was fetched and read:

    32.3  consulado-edimburgo/.../visit-visa-vivis-1/tourism-and-transit-vivis   (Edinburgh, UK)

It ranked **third**, behind Riyadh and a Kuala Lumpur page. So this is not a crawl or a rendering
failure — the right answer was in hand and the ranking rejected it.

**Finding 1 — the scorer rewards pages that talk *about* documents over pages that *list* them.**
The Riyadh page is generic e-consular boilerplate; it scored `body:documents required+25`,
`body:required documents+25`, `body:application documents+18` purely by repeating the phrases. The
Edinburgh page is the actual checklist and names passport, bank statement, proof of funds,
itinerary and return ticket — in prose, without chanting "documents required". Singapore and Japan
hid this because their checklists happen to contain the literal phrases too.

**Finding 2 — mission detection is inoperative for a consolidated portal, and it is not latent.**
`_mission_domains` returned `[]` for Brazil. It looks for the residence country's label in the
*host*, but Brazil publishes every mission on one host with the post in the *path*
(`www.gov.br/mre/pt-br/consulado-edimburgo`). So Riyadh, Kuala Lumpur, Atlanta and Abu Dhabi
compete on equal terms with Edinburgh for a UK applicant, and four of the six resolved roles came
from missions on the wrong continent. This was recorded as a latent gap; Brazil shows it changing
the answer.

**Finding 3 — the failure is silent, which is the worst part.** Exit 0 means "every load-bearing
role filled". Nothing in the output suggests the checklist belongs to a different mission from the
one serving this traveller, because nothing checks that. A refusal would have been safe; this is a
confident wrong answer, the outcome entries 5 and 6 exist to prevent.

**Not fixed here, on purpose.** Any change now would be fitted to Brazil. The honest next step is
to decide what *should* rank a checklist — plausibly: does the page name specific documents, and
does it belong to the mission serving this traveller — and only then to look at whether Singapore
and Japan still pass.

---

## 14. A missing document checklist stops refusing the corridor
**2026-08-16**

Entry 13 established that Vietnam publishes **no document checklist anywhere** on its approved
domains — its e-visa states requirements as upload fields inside the application form. Discovery
treated `document_checklist` as load-bearing, so Vietnam refused permanently for having correctly
observed reality.

**Decided:** `LOAD_BEARING_ROLES` is now `("visa_decision",)` alone. A corridor resolves without a
checklist; `visa-discover` exits `1` rather than `2`, and the absence is still named in
`unresolved_roles` and the notes via a new `REPORTED_ROLES`. Vietnam now resolves at exit 1 with
`visa_decision`, `general_entry`, `application_route` and `fees` filled.

**The reservation, recorded because it did not go away.** Discovery cannot distinguish *"this
country publishes no checklist"* from *"one exists and we failed to find or read it"* — a crawl that
stopped short, a language we do not score, a bot-block. Both emit the same note. Accepting the
absence everywhere therefore converts every find-or-read failure into a plan with a silently missing
checklist, and those are the more common case. A per-country human declaration was proposed instead,
matching how `trusted_domains` works; the global relaxation was chosen deliberately over it.

**What makes it survivable, and must not be removed.** The absence is carried structurally rather
than trusted to the prompt. `VisaPlan.validate_absent_checklist` refuses any plan that, with no
document source, either lists document requirements or stays silent about the gap. So the failure
mode this opens is a *visibly* incomplete plan, never a confidently invented checklist — the
distinction entry 6 was deleted over. Deleting that validator re-opens the worst outcome this
product can produce. The prompt gained a matching rule (8a), but the prompt is the polite request
and the validator is the guarantee.

**Fixed alongside, and independently a bug:** `load_bearing_source_ids` was
`required_source_ids or application_document_source_ids`. The `or` meant that naming any required
source silently discarded the checklist requirement — a destination could declare a checklist and
still produce a plan without it. It is now a union.

**Still open:** nothing tells a reviewer which of the two cases they are looking at. If plans start
shipping with empty checklists for countries that *do* publish one, that is this decision failing,
and the per-country declaration is the fix that was already designed.

---

## 13. Render client-side pages, on demand only, trusting nothing new
**2026-08-15**

Whole corridors were unservable because the authority publishes a client-rendered page. Measured
before deciding, through the project's own cleaning: `evisa.gov.vn` gave **39** readable characters;
`xuatnhapcanh.gov.vn` gave **402**, and those 402 turned out to be *translation keys*
(`home.banner-huong-dan-viet-nam`, `lienKet`) with the real strings fetched client-side.

That second finding decided more than the first. 402 characters **clears the 400-character floor**,
so a page saying nothing would have passed into extraction as though it were official guidance —
the wrong-checklist failure the floor exists to prevent. Whatever was decided about browsers, that
hole had to be closed, so `looks_untranslated` marks such a page unusable. It was checked against
all 13 configured Singapore and Japan sources first: **zero false positives**.

**Decided:** a headless Chromium behind a `PageRenderer` protocol, attempted at exactly one point —
after an ordinary fetch already failed to produce readable text. Pages that work today never meet a
browser. `render_mode` in `runtime.yaml` is committed as `never`; Playwright is an optional extra.

**The trust model did not move**, which was the precondition for doing this at all. Every request
the rendered page makes — document *and* subresource — is aborted unless its host is already
approved. Verified live: rendering `evisa.gov.vn` blocked `firebase.googleapis.com`,
`firebaseinstallations.googleapis.com` and `www.googletagmanager.com`, and the page still rendered
to 21,853 characters of real guidance. Where a render lands is re-checked exactly as a redirect is.

**Rejected — always rendering.** Slower on every page, and it exposes the pages that already work
to a whole new class of failure for no gain.

**Rejected — declining to render.** Defensible, and refusing is a supported honest outcome, but the
measurement showed this is not a scoring problem that could be worked around: the text is simply
absent from the response, however you arrive at it.

**Rejected — parsing the embedded framework payload** (the Next.js flight data) instead of running
a browser. It is per-site, per-framework, and breaks silently on redesign — the kind of fragility
that produces a confidently wrong checklist rather than a visible failure.

**Got wrong once, then fixed:** retrieval and the crawl first shared one render budget. The crawl
spent all five renders before the shortlist was read, so a working renderer produced no evidence.
Each caller now holds its own allowance. Worth remembering as a shape: a shared budget between a
broad phase and a narrow one always starves the narrow one.

**Two shortlisting bugs this exposed, both fixed.** Rendering made `evisa.gov.vn` readable, and it
*still* never became evidence. Chasing that found two defects that had nothing to do with browsers:

1. `api.evisa.gov.vn/client-service/public/ngon-ngu/get-all` — a JSON endpoint listing the site's
   *languages* — scored 56.4 and took the third and last `application_route` place, pushing every
   readable `evisa.gov.vn` page off the shortlist, then failed as "not an HTML page". Retrieval
   already refused JSON, but only *after* the fetch, by which time the place was spent.
   `is_machine_endpoint` now rejects it before it can be a candidate.
2. `_shortlist` took three per role and stopped, using **six of its ten places** while every
   `evisa.gov.vn` page sat just outside the per-role cut. The budget is now filled with the next
   best overall after the per-role picks.

Together: 6 pages read → 10, and `evisa.gov.vn` is now actually fetched.

**Vietnam still refuses, and that is the correct answer.** With both fixes and rendering on, every
one of the eight readable candidates scores **exactly 0.0** for `document_checklist` — zero, not
just below the threshold. Reading the rendered text by hand says why: `evisa.gov.vn` (21,853
characters), its FAQ (15,786) and its support page carry *eligibility* law — "not falling under
Clauses 1, 2, 3, and 4 of Article 8" — and process steps, not a list of documents. Vietnam's e-visa
states its requirements as upload fields inside the application form itself. **There is no document
checklist page on the approved domains to find.** Refusing beats nominating the eligibility page as
a checklist, which is decision 5 working exactly as intended.

**Also corrected:** Singapore's VFS page answers **HTTP 403**, a bot-block rather than a
client-rendered page, so rendering never applies to it. The handoff had recorded it under the wrong
cause.

---

## 12. Complete certificate chains; never disable verification
**2026-08-15 · commit `4032824`**

Vietnam's official e-visa portal failed TLS verification. The temptation was to skip verification
for "known legitimate" sites.

Diagnosis first: the certificate is genuine, issued by GlobalSign to Cục Quản lý xuất nhập cảnh (the
Vietnam Immigration Department), organisation-validated. The server simply omits the intermediate
linking it to the root. Browsers fetch that automatically; Python does not.

**Decided:** bundle the missing intermediates in `config/tls_intermediates/`, each verified to chain
to a root already in the trust store, so **no new trust is granted** — a server misconfiguration is
worked around and nothing else.

**Rejected:** `verify=False`, per-host or otherwise. An attacker able to intercept the connection
could impersonate an immigration authority and dictate what documents a traveller brings. That is
the single worst outcome this product can produce, and it would have been invisible.

Tests assert that expired, self-signed, hostname-mismatched and unknown-CA certificates are still
rejected, so a future "simplification" cannot quietly loosen this.

---

## 11. Search may generate candidates; it may never widen trust
**2026-08-15 · commit `42eec19`**

`AGENTS.md` said *"never add open-ended web search"*. Discovery needs some way to find pages.

Two readings were considered: crawl only within already-approved domains, seeded from official
travel-advice services; or use a search engine. Search was chosen because it is how a person
actually finds these pages and it works for any country without a per-country seed.

**Decided:** search is permitted **only inside `discovery/`**, and only as a candidate generator.
Nothing it returns becomes evidence until it passes the domain-trust rules. `AGENTS.md` was amended
rather than quietly contradicted, stating the constraint that replaces the old rule.

The resulting safety story: for *pages*, spam is structurally unreachable because results are
filtered to approved domains before anything is fetched. For *domains*, the human approves. The
entire added risk is concentrated in one human-gated decision per country rather than diffused.

---

## 10. A destination's own government outranks other countries' pages about it
**2026-08-15 · commit `50236df`**

The first live Vietnam bootstrap ranked `usembassy.gov` **first** — the US embassy in Vietnam. It is
`.gov`, so "looks governmental" passed, but it describes the rules for American citizens.

**Decided:** check that a domain sits under the destination country's own top-level domain, held as
data in `countries.yaml`. Foreign government pages still appear for review, flagged and never first.
A country's own government needs only one corroborating query, since that is a much stronger prior;
this also rescued `mofa.gov.vn`, which had been discarded for appearing once.

Found only because a third country was tested. Singapore and Japan could never have surfaced it.

---

## 9. A page can fill several roles
**2026-08-15**

Discovery originally assigned one role per page, on the assumption that a page is one thing.
Singapore's own hand-written configuration disproves it: the per-nationality page is listed as both
the decision source and the document checklist.

Forcing exclusivity meant that page won the decision role and the checklist role then went to a
narrower, wrong page. `ResolvedSource.roles` is now a list.

---

## 8. Wrong audience is a veto, not a penalty
**2026-08-15**

After fixing the above, Japan regressed to the **diplomatic passport** exemption list. It names many
nationalities, so it collected a nationality bonus and outscored the correct page.

**Decided:** hard wrong-audience terms — `diplomatic`, `official passport`, `spouse` — reject a page
outright rather than reducing its score. Some exclusions must not be outweighable by any
accumulation of positive signals. Archived paths and other-country pages work the same way.

---

## 7. Discovery is an offline command, not part of a request
**2026-08-15**

Discovery contacts many pages and changes what the application would treat as official.

**Decided:** it runs as `visa-discover`, deliberately, with a person looking at the result.
Generating a plan still visits only configured URLs and never searches. Wiring discovery into
request time is deferred until its ranking is trusted, and would sit behind per-corridor caching.

---

## 6. Structured conflict detection: built, then deliberately deleted
**2026-08-14 · recorded in commit `c4c0287`**

A deterministic conflict detector was fully built and working. The model reported what each source
said about four questions in a canonical form; the application compared them and applied precedence.
It correctly found the real Singapore discrepancy — three pages requiring six months of passport
validity measured from entry, from departure, and from an unstated point.

**Deleted anyway.** Nothing recorded *who a claim applied to*, so a general page listing visa-free
nationalities and a nationality-specific page requiring a visa compared as though they contradicted
each other. A false "sources disagree on whether you need a visa" is the most damaging thing this
product could emit.

The generalised lesson, which governs later decisions: **a feature whose wrong answers are alarming
must have a near-zero false-positive rate, or it should not ship.** Errors a user sees must be
near-impossible; errors only the maintainer sees can be noisy.

If revisited: record the population each claim applies to and compare only same-scope claims; leave
the visa decision out entirely, since it has stronger guards already; restrict comparison to
quantitative rules where a wrong flag costs a caveat rather than alarm.

---

## 5. Refuse rather than serve evidence that may be wrong
**2026-08-14 · commit `1c9fec9`**

Originally any failure collapsed the whole run into an opaque 503.

**Decided:** each source resolves to a typed outcome; a plan is `verified` or `partial`; and a
missing *required* source refuses the run **before the model is called**, naming what was missing.
A plausible substitute for a document checklist is worse than no answer.

---

## 4. Cached evidence reports when it was really retrieved
**2026-08-13 · commit `672f0e9`**

When serving from cache, `retrieved_at` is the original fetch time, never now.

Stamping the current time would replace a *visible* staleness problem — a plan showing an old date —
with an invisible one. The same reasoning drives the stale ceiling: past it, a source is refused
rather than served, because "no answer" beats "confidently out-of-date answer".

---

## 3. Reviewable policy in git; secrets in `.env`
**2026-08-13 · commit `672f0e9`**

`.env` had collected three different kinds of setting: secrets, behavioural policy, and machine
tuning. Only the first belongs in an untracked file.

**Decided:** `source_mode`, `extraction_mode`, the cache TTL and the stale ceiling moved to a
committed `config/runtime.yaml`. They decide whether government sites are contacted, whether a paid
model runs, and when stale guidance is refused — all of which deserve code review and a diff.

A concrete cost had already been paid: inspecting which mode was active meant printing the file, and
the API key went with it.

---

## 2. Trust the domain, never the prose
**2026-08-13 · commit `1c9fec9`**

The founding rule. Officialness is decided by who controls the domain, checked at configuration
load, after every redirect, and after every forward. Page content is never a factor, because a
convincing page is exactly what an attacker or an SEO-optimised agency produces.

Consequence worth stating: an appointed provider such as VFS **cannot** pass domain trust, and is
authorised only by an official page naming it.

---

## 1. Separate retrieval from extraction behind a protocol
**2026-08-12 · commit `28a6e30`**

`SourceFetcher` and `VisaPlanExtractor` are protocols, so fixtures and live retrieval are
interchangeable and the offline path remains a deterministic regression baseline.

This paid off repeatedly: live retrieval, PDF support and discovery's shortlist fetching were all
added without touching the extractor. Discovery reuses `LiveSourceFetcher` wholesale rather than
reimplementing trust checks.
