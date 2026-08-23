# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

**How to read this file.** **Now** is what to pick up, in the order written. **Item 22 has left it** —
done and measured live on 2026-08-23, entries 49–53. **Item 3 is now the thing most of this list waits
on**, even though it sits in **Next up** rather than here; nothing large should be built before it, and
after item 22 nothing large is queued. Items 17, 18 and 19 are the work item 22 grew out of — the corridor variance that started it
(17) and the corpus that answers it (18, 19, entry 44). Item 23 is **done** — the vocabulary could not
recognise a page that *states* the visa answer, so entry 27's exception had stopped firing; entry 56.
**Everything now waits on credit**: the OpenAI account is exhausted, which blocks item 3 and the last
step of item 23.
**Next up** is what follows. **That reasoning and item 18 are not in conflict, but the reconciliation is deliberate
and worth stating**: item 18 is built once and run first on only the ~8 destinations item 3 needs, so
the measurement describes the architecture the project means to keep, and scaling it to 198 countries
afterwards needs no rework. Building the corpus for all 198 *before* measuring would be the thing entry
35 forbids. **Later** is real but not urgent. **Done** is finished work, kept because what building it found is
usually why the item after it exists. **Smaller things** are one-paragraph defects with no owner yet.

Status: `next` · `soon` · `later` — the label on each heading matches the section it sits in, so the two
can never disagree. There is no **Blocked** section at the moment: the 20-corridor measurement was the
only item in it, and Brave credit arrived on 2026-08-21. Give a blocked item its own section again if
one appears.

**Every open item has a number, and numbering is append-only** so that the cross-references in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) stay valid. The numbers are names, not an order: **the section
decides the order**, and a gap in the sequence means an item was finished or dropped. Finished items
keep no number — a number is a handle for pointing at work still to be done — and *Smaller things* are
one-paragraph defects rather than items.

| | | |
| --- | --- | --- |
| **Now** | 17. Decide what a corridor that flips between runs should do | `next` |
| | 18. Build the offline corpus job, and run it on item 3's destinations | `next` |
| | 22. Route the request path through the corpus and drop the crawl | `next` |
| | 19. Read the corpus in the request path, and refuse on a miss | `next` |
| | 15. Re-run the remaining six verified corridors against the widened excerpt | `next` |
| | 5. Answer the challenge, and get a checklist out of France | `next` |
| | 1. Fix the post-over-nationality weighting, and trace Sweden | `next` |
| **Next up** | 3. Measure the top 20 corridors against a bar committed in advance | `soon` |
| | 2. Amend the trust rule for governments with no marker, and for Schengen | `soon` |
| | 4. Decide the client-side retrieval question | `soon` |
| | 7. Put it somewhere others can open it aka deployment | `soon` |
| | 8. Confirm a blocked authority actually reads usefully | `soon` |
| | 9. Tell "no checklist exists" apart from "we failed to find it" | `soon` |
| | 20. Make the stores substrate-swappable and durable | `soon` |
| | 21. Fill the three provenance gaps | `soon` |
| **Later** | 10. Try sitemaps before crawling | `later` |
| | 11. Decide whether a host that has refused everything should be skipped | `later` |
| | 12. Watch where the two deciders disagree | `later` |
| | 13. Revisit conflict detection, with claim scope | `later` |
| | 14. Detect drift in configured sources | `later` |

---

## Background

**Read [DECISIONS.md](DECISIONS.md) entries 29–35 first**, then 36–42, which are what came out of
building them. The outside review on 2026-08-18 was agreed with in full and changed the direction: the
posture, not the principle, is what has been costing coverage (entry 35); "who to believe" moves out of
the request path into committed data (entry 34); the trust rule's governmental half was measured and
fails closed for a fifth of the world (entry 33); and three things shipped that the project's own rules
argue against (entries 30, 31, 32).

**All seven review entries are now implemented or explicitly answered**, along with five more that came
out of doing the work: `robots.txt` (36), the per-run render allowance (37), the committed domain
registry (38), the reviewed override (39) and the shortlist width (40). **Left from the review itself:**
the rest of entry 35 — asking authorities for access, and the client-side retrieval question nobody has
argued yet.

**Why items 5 and 6 lead — added 2026-08-19.** Both came out of investigating why France resolves
without a checklist and why `canada/GB/GB/tourism` refuses, and neither cause was where these files said
it was. France's portal is not refusing us at all — it serves a Cloudflare challenge, and serves it for
`robots.txt` too, so no policy was ever stated (entry 41). Canada refuses because the adjudicator's
6,000-character excerpt cuts off the page that answers it.

**What the building found matters more than the list it came from.** Three separate times, a constraint
turned out not to be where the documentation said: the domain classifier was failing on countries the
search had already found; a wrong trusted set made corridors *refuse* rather than answer; and the
scorer's ranking was never binding — the ten-place window in front of it was. Prefer running a corridor
to reading a code path. Every item here assumes that.

---

## Now — pick these up in this order

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

### 18. Build the offline corpus job, and run it on item 3's destinations — `next`

**Why:** [DECISIONS.md](DECISIONS.md) entry 44. Recall is currently re-rolled from search on every
request, and entry 43 measured what that costs: the page that answers Canada was fifteenth of 470 on one
run and absent on the next. A corpus makes a good run durable — **but only a good run.** The job's own
recall therefore becomes the whole ballgame, which is the argument for it being an offline job rather
than a cached request: with no latency budget it can go deeper than a 60-second request ever will.

**Do:** a `visa-discover` command that crawls one country thoroughly — deeper hops, many more queries,
sitemaps (item 10) — and writes the country's page corpus. Then run it for the roughly eight
destinations [item 3](#3-measure-the-top-20-corridors-against-a-bar-committed-in-advance--soon) needs, so
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

### 19. Read the corpus in the request path, and refuse on a miss — `next`

**Why:** item 18 buys nothing until the request path reads it. Together they are what removes search from
a populated country's cold path — up to fifteen Brave queries and a two-hop crawl — and what makes two
runs of the same corridor consider the same candidates.

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
keyboard. **Do not write wizard-driving code before that entry exists.** Note it interacts with the
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

### 3. Measure the top 20 corridors against a bar committed in advance — `soon`

**Why:** DECISIONS entry 35. This is the measurement that decides whether the project is a product or a
demonstration, so **nothing large should be built before it.** Seven corridors cannot answer whether
bot-blocks are the rule, and choosing a threshold after seeing the numbers is how a demonstration talks
itself into being a product.

**Do:** run the top 20 corridors by real traveller volume cold — India/China/Nigeria/Philippines →
US/UK/Schengen/Gulf/Canada — and count per corridor: decision confirmed, checklist found, checklist
blocked.

> **The bar, committed now: product if ≥70% confirm the decision and ≥50% yield a checklist.** Below
> that, the anonymous-crawl posture is dead and the choice is licensed data (which forfeits the
> verifiability that is the whole differentiator) or client-side retrieval.

Today's seven are 5/7 and 4/7 — which would pass, on a sample chosen partly because it was easy.
**Treat those two fractions as a stale floor, not a baseline.** They come from the corridor table in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md), which that file itself marks as predating the registry and the
wider shortlist, with at least two rows now wrong — Japan and Canada both fill every role at 25 places.
Re-derive them from this measurement rather than comparing against them.

**Run each corridor at least twice — item 17.** `canada/GB/GB/tourism` refused once and resolved once
within an hour on identical code, so **one run cannot tell a corridor that works from one that works half
the time**, and a single-run measurement would report the flip rate as the pass rate. If credit does not
stretch to twenty corridors twice, halve the sample rather than the repeats, and say plainly in the
write-up which it was. Note the ordering question this raises: measuring **before** items 18 and 19 sizes
the problem the corpus is meant to fix, and measuring **after** describes the architecture the project
intends to keep. Doing it before and repeating the outliers after is the cheap version of both.

**One destination has been through the corpus-routed path, and it is Canada** (entry 53). These runs are
what generalise it — and note that the corpus job (item 18) has only ever been run for Canada, so every
other destination here will still crawl. Expect two populations in the results, and say which is which.

**No longer blocked — 2026-08-21:** Brave credit is available again, so this can run. `robots.txt`
landed first (entry 36), so the numbers describe the posture the project intends to keep.

**Fold in the France read-through**, which was the previous head of this list and needs the same credit:
run `france/IN/GB/tourism` and read the plan as a traveller. Three things no test can judge:

1. Does the explanation say plainly that the decision could not be verified, and name France-Visas?
2. Do the application steps stay useful when the first is "check the authority yourself"? Rule 8b asks;
   whether the model obliges is unknown.
3. Does "Uncertain" read as *we could not check* rather than *no visa needed*? If it reads as the latter
   to anyone, the wording is wrong and it matters more than anything else on this list.

The layout was already confirmed by injecting a France-shaped plan into the real renderer (entry 28), so
what is left to judge is the model's own words. **Careful:** if it reads as verified, the fix is the
wording and the banner, never a narrower `visa_required`. A corridor stored before 2026-08-17 has no
`inaccessible_urls` field, so clear `var/corridors/`.


### 2. Amend the trust rule for governments with no marker, and for Schengen — `soon`

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
| *only these are official* (necessary) | **Wrong, measured 19 of 51.** Where a country has no government namespace there is no signal to find, so no regex can ever fix it. |
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
2. **Registry (RDAP/WHOIS) organisation data.** `esteri.it`'s registrant is Italy's foreign ministry —
   authoritative registry data, not prose. **Measure coverage before committing:** GDPR redaction is
   heaviest on European ccTLDs, which is exactly the 19.
3. **TLS certificate organisation.** OV/EV certificates carry a CA-validated `O=` field, and this project
   already handles certificates (entry 12). Partial: many authorities now use DV certificates with no
   organisation. Note it needs a TLS handshake before trust is decided — closer to DNS resolution than to
   fetching evidence, but say so explicitly rather than sliding past it.
4. **Cross-vouching from an already-trusted domain.** For the ten countries that *do* have a marked
   domain, `interno.gov.it` naming `esteri.it` as the foreign ministry is the government vouching for its
   own domain — the existing `appointed_by` idea generalised. **The hole:** governments link to
   contractors, partners and news, so "linked from a trusted domain" is far too weak, and
   `ARCHITECTURE.md` says appointing a provider is human judgement never automated. This is a decision to
   argue, not a patch to apply.

**Do the measurement first** — for the 19, how many are covered by (1), (2) and (3)? It is offline-ish,
needs no search credit, and it decides whether this item is automatable or genuinely needs a human. If
most are covered, the production goal survives; if not, reviewed data is the honest answer and the review
is 19 countries rather than 198.

**Then the two problems the measurement is for:**

- **19 of 51 governments have no governmental marker in their hostname.** The amendment is an authority
  domain named in the entry 34 registry, by whichever of the four mechanisms above survives measurement
  — **never a wider regex.** Adding `.de`, `.nl`, `.it` as markers would trust every commercial site in
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

**Do first, separately, because they are corrections inside the existing rule rather than relaxations
of it:** add `gv` and `gub` as markers, and add `canada.ca` beside the `gc.ca` special case — Canada
fails only because immigration content moved and the pattern did not.

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

### ~~Give `visa_decision` its floor back~~ — **done 2026-08-24, and the proposal was wrong** (was item 23)

DECISIONS entry 56. This item proposed removing the `not scores` guard so `mentions_visa` always
contributes a `visa_decision` floor. **Measured, that would have made things worse**, and the real
defect was one the item had not identified.

**Why the guard stays.** Removing it gives a positive `visa_decision` to **12–58% of a country's
pages** (Netherlands 58%, US 44%, Japan 25%), because `mentions_visa` is a substring test against the
flattened URL and a visa authority's paths nearly all contain the word. `_decision_blocking` admits
anything above zero, so entry 32's test would have become "the URL contains the word visa". The guard
also costs no recall — Sweden's page was shortlisted anyway on `general_entry`.

**The real defect: every `visa_decision` term was a way of *asking*** — `visa requirement`,
`do i need a visa`, `check if you need` — with no way to recognise a page that *states the answer*.
Seven answering phrasings added, including `require visa` in its **slug form**, because
`searchable_url` flattens hyphens and slugs drop the article that prose keeps.

**Measured by replaying the real candidate sets** of all seven corridors: Sweden's blocked decision
page goes `visa_decision` **0.0 → 82.4** and now qualifies its own refusal; **no shortlist changes
anywhere**; France still correctly refuses.

**`need a visa` was tried and rejected** — it sits inside `check if you need a visa`, so both fired and
a Caribbean page displaced the Netherlands' own UK application page. Seven such overlapping pairs
already exist and are now frozen by a test rather than fixed.

**Live verification stopped one step short**: the page scores 82.4 and `government.se` still `403`s
it, but the corridor could not be re-resolved because **the OpenAI account ran out of credit**. That
last step — Sweden resolving `partial` with the decision unknown and the URL handed over — is
outstanding, and it needs the same credit as item 3.

### ~~Re-run the remaining six verified corridors~~ — **done 2026-08-23** (was item 15)

Japan, the Netherlands, Sweden, the United States, France and Singapore, each twice on the crawl path,
then again corpus-routed after building their corpora. 24 live runs. DECISIONS entry 55.

**Speed: 2.1×–5.2× faster, crawl 0.0s everywhere** — Singapore 56.1s → 10.8s, Japan 37.5s → 14.9s,
US 31.4s → 14.9s, Netherlands 30.9s → 12.9s, Sweden 39.9s → 18.0s, France 23.6s → 11.2s. The candidate
pool grew every time, and both runs of every corridor saw an identical candidate count.

**Roles genuinely found: neutral to better.** Japan and Singapore fill all five, unchanged. The US
gained `fees`, the Netherlands gained `processing_times`. France lost `processing_times`.

**The excerpt question this item was originally about is answered by default**: no corridor refused
for want of text, and the two that refuse do so for a reason that has nothing to do with the excerpt.

**Two corridors flipped resolve → refuse — Sweden and France — and that is now item 23.** Both lost
`decision_blocking_urls`. Reporting is intact (entry 49 works; the blocked hosts and URLs are still
named); what broke is *qualification*. France is a **correction** — its baseline qualified on a blank
CERFA form. Sweden is a **real loss** — a blocked page that plainly is the visa decision cannot
qualify, because of the scoring rule in item 23.

**Japan's corpus holds 1 of its 6 baseline role pages** and no London embassy at all — 29 mission
hosts including Edinburgh, not London — and it resolved all six roles anyway, because search still
runs. The strongest evidence yet for keeping search (entry 48).

**Three of six corpus builds fired `depth_is_exercised`** (Japan 9%, France 6%, Singapore 3% beyond
depth 1): the 1,200-page budget was tuned against Canada's seed count and does not generalise. See
the smaller things below.

### ~~Route the request path through the corpus and drop the crawl~~ — **done 2026-08-23, measured live**

Item 22 asked for a view on the design before building it, and the view disagreed with it in two places.
DECISIONS entries 49, 50 and 51. 7 new tests, all offline; 432 passing.

**The routing index is not built, because it removes the wrong cost.** Entry 48's ~3.6s for consuming
Canada's whole corpus is reproducible, but it is not scoring — it is `wrong_country`, at **3,330ms** of a
measured 4,757ms, scanning 198 countries per candidate and rebuilding the link's segments, text and host
labels once per country. A word index in front of the existing exact check made it **98ms, byte-identical
on all 3,216 entries**, and the whole corpus → candidates path **4,757ms → 346ms** — cheaper than the
575ms the top-400 was meant to cost.

**And the top-400 would have cut recall.** `cbsa-asfc.gc.ca/travel-voyage/td-dv-eng.html` is
`status="proven"` and scores **0.0** on role vocabulary, ranking **2,871 of 3,216**: every top-N below
~2,900 drops it, and a pin cannot rescue it because `_shortlist` looks for pinned URLs *inside*
`candidates`. Flat ranking is lopsided too — top-400 spends 238 slots on `application_route` and 20 on
`visa_decision`, where a per-role top-25 covers every role in 150 entries. If a bound is ever needed it
should be per-role, with `proven` and pinned carved out; entry 50 says when to revisit.

**The crawl is gone for a built country**, on a derived bound rather than a tuned one: a crawl visits at
most `DEFAULT_CRAWL_PAGES` (40), so a corpus offering more than that on currently trusted domains cannot
be out-covered by one. Below it, and with no corpus at all, behaviour is exactly as before, and the skip
is recorded in the notes.

**A third defect turned up while verifying the second claim above** (entry 52). With no pre-filter at
all the pin *still* fails: `_shortlist` honoured the per-domain reservation through its truncation and
not the pins, so entry 47's "keeps its place regardless of ranking" had been half-true since it landed —
and only for pages that did not need it. Fixed; `test_a_pin_survives_the_shortlist_truncation` fails on
the old code.

**Two things in item 22's "careful part" were wrong, and one was worse than described.** `_fetch_bodies`
did not merely need its refusals rerouted — it **discarded `report.failures` entirely**, so every refusal
a corridor has ever reported came from the crawl (entry 49). And the corpus's `status` cannot stand in
for `_readable_only`: `corpus_build` never writes `readable`, and skipping a page on a stored refusal
would mean never observing it live, which is what a France-shaped corridor needs to resolve at all.

**Step 4 is done, and it earned its cost.** `canada/GB/GB/tourism` run four times, instrumented at entry
48's four boundaries (entry 53):

| run | total | search | **crawl** | fetch | adjudicate | roles filled |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 21.75s | 4.12s | **0.00s** | 6.34s | 10.16s | **refused** |
| 2 | 12.73s | 2.77s | **0.00s** | 1.16s | 7.69s | decision, fees, times |
| 3 | 13.24s | 3.45s | **0.00s** | 1.24s | 7.70s | decision, fees |
| 4 | 12.82s | 2.86s | **0.00s** | 1.06s | 8.05s | decision, fees |

Against 54.2s. **Do not read 12.7s as beating the ~21s projection on merit** — search answered in
2.8–3.5s where entry 48 saw 9.1s, and adjudication in 7.7–8.1s where it saw 10.8s, both someone else's
latency on a different day. The supported claim is narrow: **the crawl's 33.6s is gone and nothing grew
to replace it**, and 2,387 of 2,455 candidates now come from a file.

**Run 1 refused, which is what the measurement was for.** Removing the crawl exposed a defect it had
been repairing on every run since entry 47: `_resolve` seeded search first and folded the corpus in with
`setdefault`, so the corpus could never displace a search candidate for the **same URL** — and search's
title scores far less than the anchor text and heading an offline crawl harvests. Canada's answering page
entered at **32.0** instead of **63.4** and was never read. Fixed; three consecutive runs then resolved.

**Adjudication is now ~60% of the corridor.** Whatever is optimised next, that is where it is.

### ~~Find out whether Canada's answering page was ranked out or never found~~ — **done 2026-08-21**

**Answered: neither, on the run that was asked.** `discovery/recall_log.py` now writes one record per
corridor per run — every candidate with its scores, the shortlist and fetch flags, the queries, the
seeds, and each unreadable URL with its reason — to `var/recall/`, on refusals too, on by default in both
the command and the API. 8 new tests, all offline. DECISIONS entry 43.

Run immediately after it landed, `canada/GB/GB/tourism` **resolved**: `entry-requirements-country.html`
was candidate **15 of 470** at 53.4, shortlisted, fetched, and used by the model to fill `visa_decision`
— quoting the sentence at offset 8,597, which the old flat 6,000-character excerpt could not have shown.
So it was never a ranking problem. On the refusing run an hour earlier, search did not return the page at
all.

**What that turned into:** entry 42 confirmed live, and item 17, which is the real problem — the same
corridor refuses or resolves depending on the run. The log is what makes the next one diagnosable rather
than inferred; it does not explain search's variance, only prove it.

### ~~Stop the adjudicator's excerpt cutting the answer off~~ — **done 2026-08-21**

`DEFAULT_EXCERPT_CHARACTERS` is 20,000 and no longer a flat head-of-page slice: `anchored_excerpt` shows
the head of each candidate plus a 3,000-character window centred on every later mention of the
traveller's own nationality or residence, marks what it left out with `[…]`, and prompt rule 12 tells the
model what the mark means. 11 new tests, all offline. DECISIONS entry 42.

**What it was costing.** `canada/GB/GB/tourism` ranked the right page first, fetched it, and refused: the
sentence answering a British traveller sits at offset 8,597 of 16,465 and the excerpt ended at 6,000,
mid-alphabet at "Morocco". So **whether a corridor resolved depended on where the traveller's nationality
fell in a list** — India at 5,325 answered, every visa-exempt nationality not — and entry 40's "Canada:
every role filled" turns out to have been an Indian-passport result that did not generalise.

**Anchoring is not what makes it affordable, and the file should not pretend otherwise.** Over the 27
cached `canada.ca`/`gc.ca` pages, packet text goes 84,704 → 153,862 characters; a flat 20,000 costs
153,852, because only 2 of the 27 exceed the budget. Anchoring is what stops the new number from being
another fixed offset: on the 50,000-character visitor-visa PDF a US traveller's second window sits at
24,449, which a flat 20,000 cuts.

**Run live on Canada twice: one refusal, then one resolution** — the refusing run never retrieved the
answering page, and the resolving one filled `visa_decision` from exactly the sentence the old excerpt
cut. Confirmed. The flip between the two runs is item 17; the six other corridors were re-run on
2026-08-23 and are in **Done**.

### ~~Move "who to believe" out of the request path~~ — **done 2026-08-18, for 40 of 198 countries**

`config/authority_domains.yaml` is generated by `visa-discover registry`, read by
`discovery/registry.py`, and consulted by `AutomaticDestinationService` in place of a live bootstrap.
The trust rule is untouched — `auto_trusted_domains` still decides every domain — only *when* it runs
moved. 13 new tests, all offline. DECISIONS entry 38.

**Verified live:** New Zealand, never configured, resolved a visa decision, a document checklist, an
application route and a general-entry page from committed domains, with **0 searches** spent in the
service where 4 went on bootstrap before.

**Reading the file is what paid for it**, and it found three things:

- The 5 refusals (AT, BE, DE, DK, SE) are entry 33's known failure and now name their own fix in
  `unconfirmable` — `gv.at`, `auswaertiges-amt.de`, `nyidanmark.dk`, `migrationsverket.se`.
- **Twelve countries are confirmed *and wrong*** — the Netherlands trusts only its business portal,
  Italy trusts two ministries that are not the foreign ministry, Canada trusts five `gc.ca` domains
  while IRCC's content lives on the unconfirmable `canada.ca`. These corridors do not refuse; they
  resolve against domains that cannot hold the answer. Entry 33 predicted this and could not measure it.
- **The cap spends slots on the wrong parts of a government**, which nobody had predicted. India's five
  include two United States missions; South Korea's include a county; Spain's put the prime minister's
  office ahead of the foreign ministry. `_trust_priority` falls back to alphabetical among domains with
  no hostname hint, and for a large government that is arbitrary.

**158 countries are unbuilt** and refuse with a message naming the command. That is 632 searches of
quota, not work: `visa-discover registry` resumes, and `--only FR,DE` rebuilds any subset.

### ~~Read and honour `robots.txt`~~ — **done 2026-08-18**

`research/robots.py` fetches one policy per **origin** and re-reads it after 24 hours;
`discovery/crawl.py` consults it before every crawled page and after every redirect, and
`research/live_sources.py` before every source and every meta-refresh forward. Matching implements
RFC 9309 directly — `urllib.robotparser` was tried and rejected, because it supports neither `*` nor `$`
and so obeys none of the rules `www.gov.uk` publishes. 32 new tests, all offline. DECISIONS entry 36.

**Three things came out of building it that the entry above did not anticipate:**

- **A skip needed to be its own outcome, and `disallowed` is it.** Otherwise a page nobody asked for is
  indistinguishable from a page that did not exist — the failure entry 18 names. The corridor reports it in
  its own note rather than the generic "could not be read" one, because only the first failure per host
  survives that note and a `Disallow` could be masked by an unrelated `404` on the same site.
- **A boolean verdict produced a false reason, and that had to be caught.** The first version collapsed
  every non-answer into "disallowed", so every **unreachable** host was described as *"its robots.txt does
  not permit this client"* — a sentence about a policy nobody had read, and the same class of falsehood
  entry 33 had just removed from `withheld_domains`. Now: `5xx` or oversized is `UNREADABLE`, a parsed rule
  excluding us is `DISALLOWED`, and a transport failure **raises** so the caller diagnoses the host.
- **A `Disallow` is reported but may never resolve a corridor.** `disallowed_urls()` is outside
  `blocked_urls()` and `persistent_refusals()`, so it reaches neither `inaccessible_urls` nor
  `decision_blocking_urls`. A `403` was observed on the page; a `Disallow` covers a path we chose not to
  request, and letting it stand in would widen entry 32's exception by a route entry 32 never considered.

**Measured live, six corridors, 2026-08-18 — entry 36 has the table.** The cost was almost nothing:
France lost one news listing, China lost two portals already answering `502`, and Japan, Singapore,
Vietnam and Brazil lost nothing. **The negative result matters more:** France and the US answer `403` to
their own `robots.txt`, so this step buys nothing on the two corridors that motivated entry 35 — it is a
WAF there, not a stated policy. Item 3's twenty corridors still decide the size of that limit.

### ~~Commit the 51-country trust-rule test~~ — **done 2026-08-18**

`tests/test_trust_coverage.py`, 7 tests, offline. Freezes the 19 failures so a change is a visible diff,
asserts every one fails on the governmental half rather than the TLD half, and guards `countries.yaml`
against another country acquiring a governmental marker in its `tlds` unreviewed. Verified the tripwire
fires by simulating the forbidden fix.

**It also refined the finding, and the refinement matters** — see DECISIONS entry 33's table. The 19 are
two different failures. Nine (AT, BE, DE, DK, FI, NL, NO, SE, UY) have no marked domain at all and refuse
outright. Ten (CA, CL, CZ, GR, HU, IE, IT, PT, RO, RU) **do** have one, so bootstrap *succeeds* and builds
a trusted set that cannot contain the visa guidance — quieter and worse, because nothing reports it. Canada
is the sharpest: `gc.ca` still passes, but the content moved to `canada.ca`. Item 2 is what fixes both;
its marker corrections (`gv`, `gub`, `canada.ca`) shrink the first group on their own. **It also
turned up a defect since fixed — see the entry below:** the one mitigation known problem 2 recommends — reading
`withheld_domains` — currently labels these ministries "not a government domain for this destination",
which is false and identical to what a commercial agency gets.

### ~~Narrow what a block may hand over~~ — **done 2026-08-18**

`PERSISTENT_REFUSAL_STATUS_CODES = {401, 403}`, and `ResolvedCorridor.decision_blocking_urls` carries the
refusals that plausibly held the decision — apart from `inaccessible_urls`, since every refusal is worth
reporting while only a refusal of a page that could have answered licenses resolving. Credibility is the
`visa_decision` link score above zero, low on purpose because the scorer already vetoes site furniture
outright. **Verified by mutation:** reintroducing either defect fails exactly the intended test. France's
shape still resolves. DECISIONS entry 32.

**Known limit, failing toward refusal:** the crawl discards a page it could not fetch, so a refusal first
met at crawl depth is not a candidate and cannot qualify. A national visa portal is what search returns
first, so the France case is covered.

### ~~Delete three things~~ — **done 2026-08-18**

`conflicts` is gone from both plan models, the prompt's rule 5, both extractors, the Singapore fixture and
the interface; `domain/state.py` and the `langgraph` dependency are deleted. Two things worth knowing:
Singapore's real passport-validity discrepancy was **moved** into `unresolved_questions` rather than lost,
with a test asserting it; and the interface's `.reliability-grid` was `1fr 1fr`, so the wrapper and its
now-dead CSS went too rather than leaving one block in half the width. Checked by injecting a plan into the
real page. DECISIONS entries 30 and 29.

### ~~Make a failed adjudication refuse~~ — **done 2026-08-18**

`ADJUDICATION_ATTEMPTS = 2`, then `AdjudicationRefusal`, which `resolve` turns into an ordinary refusal
naming the reason. Retrying a model provider is not what entry 18 forbids. `_refused` now takes
`model_calls`, so a corridor that spent two calls and resolved nothing says so — a cost that appears only
on success is one nobody notices. **Verified by mutation:** reinstating the fallback fails the end-to-end
test. DECISIONS entry 31.

**The heuristic keeps its two real jobs:** it builds the shortlist the model chooses from, and it answers
when `discovery_decider: heuristic` is set, which stays the offline regression baseline.

### ~~Stop `withheld_domains` telling a reviewer something false~~ — **done 2026-08-18**

The branch in `auto_trusted_domains` now splits three ways, so a domain under the destination's own
top-level domain with no recognised marker says it could not be **confirmed** as an authority, may well be
a real one, and needs naming in reviewed data — rather than "not a government domain for this destination",
which was false and identical to what a commercial agency got. `unconfirmable_authorities` names those
candidates and the refusal message uses them, so it no longer claims none could be *identified* when two
were. **Reporting only:** nothing is accepted for want of a marker, and a test holds the accepted set
empty. DECISIONS entry 33.

**Still not detected:** whether an accepted trusted set plausibly contains a visa authority at all. For
the ten countries with a marked domain elsewhere in government, bootstrap succeeds and the corridor
resolves against domains that cannot hold the guidance. The withheld reasons now describe it where the
ministry was seen at all; it is measured in DECISIONS entry 38's table.

### ~~Find out why a corridor refuses on a domain it can now read~~ — **done 2026-08-18**

Traced, and the answer was not in the scorer's rules. `DEFAULT_SHORTLIST_SIZE` was **10** — the number
of pages the model is allowed to see — which made the heuristic the effective decider for every corridor
whose right page sat eleventh. Changing only that number to 25: **Canada and Japan went from refusing to
filling every role**, the Netherlands gained its checklist, Sweden did not move. No latency penalty
(fetching is concurrent; 44.5s→39.3s and 45.2s→41.7s, both within noise) and adjudication input roughly
doubles to ~19k tokens. DECISIONS entry 40; a test pins the width.

**Three things it did not fix:** Sweden and the `/india`-over-`/united-kingdom` weighting (entry 39),
which are item 1, and English-only scoring, which is known problem 13 in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) rather than an item here.

---

## Smaller things

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
