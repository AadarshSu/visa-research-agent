# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-24 — update this line when you touch the handoff |
| **Tests** | 441 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean. **The suite is now blocked from the network** — `tests/conftest.py`, entry 45 |
| **Companion docs** | [ARCHITECTURE.md](ARCHITECTURE.md) · [DECISIONS.md](DECISIONS.md) · [TODO.md](TODO.md) · [README.md](README.md) |
| **Agent entry point** | [CLAUDE.md](CLAUDE.md) is loaded automatically and points back here |

---

## Goal

Produce visa application plans for a traveller where **every claim is grounded in an official
government source**, and the traveller is told plainly when something could not be verified.

The headline production goal — **automatic source discovery**, finding the right official pages for
a traveller and destination with nobody curating URLs — is **done and running in the request path**.
**Whose** domains a country may be researched from is no longer decided per request either: it is
generated offline, reviewed, and committed (entries 34 and 38).

**Decided 2026-08-21 and not yet built: *which pages exist* leaves the request path too** (entry 44).
Discovery re-derives a country's candidate pages from search on every request, and entry 43 measured what
that costs — the page answering Canada was fifteenth of 470 on one run and absent an hour later. So a
country's **page corpus** becomes a store, populated by an offline job, and search stops being the entry
point for a populated country. Only the corridor-dependent step — which of those pages answers *this*
traveller — stays live. **Not a move toward precomputed answers**: entry 44 rejects those on arithmetic,
and a plan stays a rendering rather than a stored fact.

**The cold-request timing in these files is stale — do not quote 34.1s.** It was measured before the
registry, on hand-configured destinations. Measured 2026-08-18 on the registry path, the *corridor phase
alone* is 39–45s for Japan and Canada. The cause is arithmetic rather than a regression in any component:
three searches run per trusted domain, and the registry gives a country up to five where `japan` in
`destinations.yaml` had two — six queries became fifteen. See known problem 5.

**The direction changed on 2026-08-18**, after an outside review that was agreed with in full and is
recorded as [DECISIONS.md](DECISIONS.md) entries 29–35, plus entries 36–42 which came out of building
them. Nothing in it weakens the grounding principle. What it changes is the diagnosis of why coverage is
poor, and it found three things shipping that this project's own rules argue against. **All of it is
implemented except two of entry 35's three legitimacy steps** — asking authorities for access, and the
client-side retrieval question — and [TODO.md](TODO.md) is what remains. The sentences worth carrying:

- **The blocker is the posture, not the principle.** "Grounded in an official page" and "grounded only in
  what an anonymous Python client can fetch" were treated as one commitment. Entry 18 forbids
  *deception*, not *legitimacy* (entry 35). The first step is shipped: `robots.txt` is now read once per
  origin and obeyed, by the crawl and by retrieval (entry 36). It is expected to *cost* coverage, and
  nothing has been run live since, so it has not been measured.
- **The trust rule's governmental half fails closed for a fifth of the world**, measured: 19 of 51
  countries, including Germany, Italy, the Netherlands, Sweden and Canada (entry 33). Known problem 2 had
  been warning about the other half.
- **Whether this is a product is now a measurement with a bar committed in advance** — top 20 corridors
  by volume, product if ≥70% confirm the decision and ≥50% yield a checklist (entry 35). **Brave credit
  arrived on 2026-08-21, so it can run**, and nothing large should be built before it does.

Deliberately out of scope, permanently: submitting applications, booking appointments, filling
forms, or claiming an approval is guaranteed. **Also settled: LangGraph is not adopted** — the pipeline
is linear, the trust checkpoints are typed validators rather than graph nodes, and the one loop the old
placeholder imagined is a retry loop this project rejects (entry 29).

---

## Current state

**Working end to end for any traveller, and for 39 of 198 destinations** — counted from the committed
files on 2026-08-22, and this line has now overstated twice.

**The binding limit is the authority registry, not the trust rule.** `config/authority_domains.yaml`
holds **40 rows**; a country with no row is **refused, never bootstrapped live** (entry 38), and Austria
has a row with no usable domain, so it refuses too. That leaves **39 researchable and 159 refused** —
158 with no row at all. This line said *"any of 198 destinations"* and *"198 destinations are
reachable"* until 2026-08-22, which was already false when entry 38 landed on 2026-08-18: the same file
says *"40 of 198 countries are built; the rest refuse"* two sections further down. **Both sentences were
in this file at once**, which is the failure mode these documents keep repeating — a headline claim
written from intent while the detailed claim below it was written from measurement.

The older correction still stands underneath it and is a *different* limit: **19 of 51 countries checked
have no domain passing `looks_governmental`** (entry 33) — Germany, Italy, the Netherlands, Sweden and
Canada among them — which is why twelve needed the `reviewed` override in entry 39. That is about which
domains a rule can confirm; the 39-of-198 figure is about which countries anyone has generated a row
for. Fixing the second is quota and review time (item 2); fixing the first needs data.

> **And the interface does not say any of this.** `researchable_destinations()` lists all 198 countries
> with `status="available"` under `destination_mode: automatic`, so a traveller is offered 159
> destinations that cannot be researched and gets a `503` on choosing one. Recorded as known problem 23.

**Eight corridors have now been run live, and seven of them on 2026-08-23 through both paths.** The
table below replaces the 2026-08-16/17 one that this file carried — and warned about — for a week.
Each cell is two runs on the crawl path and two corpus-routed, `visa-discover` registry domains
throughout, so it describes what the API does. DECISIONS entry 55.

| | Japan | Netherlands | Sweden | United States | France | Singapore | Canada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Corridor | IN/GB | IN/GB | IN/GB | IN/IN | IN/GB | IN/GB | GB/GB |
| Corpus entries | 1,558 | 2,698 | 521 | 1,840 | 1,590 | 928 | 3,216 |
| Crawl path | 37.5s | 30.9s | 39.9s | 31.4s | 23.6s | 56.1s | 54.2s |
| **Corpus path** | **14.9s** | **12.9s** | **18.0s** | **14.9s** | **11.2s** | **10.8s** | **12.7s** |
| Visa decision | found | **not found** | blocked | found | blocked | found | found |
| Checklist | found | found | found | **blocked** | **blocked** | found | **not found** |
| Resolves (corpus path) | 2/2 | **0/2** | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |

**A second, larger table now exists and supersedes this one for judging the project**: entry 58's
twenty corridors, run twice each on 2026-08-24. This table is seven corridors chosen for what they
taught; that one is the top twenty by volume, measured against a bar committed in advance.

**Read the "resolves" row against the row above it, not on its own.** The Netherlands has never
resolved — its visa decision is not found, which is an honest refusal, and the only corridor here that
refuses. Sweden and France resolve through entry 27's blocked-authority exception: an authority
refuses the page holding the decision, so the plan names it, states the decision **unknown**, and
hands over the URL. Both were broken for a day when the crawl left (entries 55–57) and both are
confirmed working live on 2026-08-24 — **the first time that exception has fired on a real
corridor.**

**Two rows that used to be here are gone deliberately.** Vietnam and China were last run on
2026-08-16 against hand-configured sources and have not been re-run; quoting them beside measured
numbers is what made the old table misleading. Vietnam needs rendering (known problem 14) and China
refused on a not-found decision.

**France and Sweden are not the same failure as the Netherlands, and the difference is the one this
project cares about.** The Netherlands cannot find its decision, so it refuses — correct. France and
Sweden *were* refused by an authority, which entry 27 turns into a plan that says so and hands over
the URL. They no longer do, and the reason is a scoring rule rather than anything about the block:
item 23.

France was re-examined on 2026-08-17 because `france/IN/GB/tourism` is a common corridor to refuse —
entries 26 and 27. **It no longer refuses**: a corridor whose only missing piece is behind a block now
resolves, with the visa decision stated as *unknown* rather than guessed, the blocked authority named
with its URL, and the plan marked `partial`.

**Run live on 2026-08-19, and both halves of that came out wrong — see entry 41 and known problem 11.**
Whether France resolves at all is **not reproducible**: it resolved at 13:30 and refused on a fresh run
an hour later. `is_usable` needs a refused URL that also scored for `visa_decision`, and none of the eight
`france-visas.gouv.fr` URLs that were refused does — every one scores `application_route` only,
including `/en/assistant-visa`, which is literally the visa-decision tool. (Two France-Visas URLs do
score for `visa_decision`, both 14.0, and neither was among the refusals.) The 13:30 run qualified on
`www.diplomatie.gouv.fr/spip.php?page=recherche&recherche=Demande+de+visa`, a **site-search results
page** scored on the words in its own query string. So the corridor resolves on an incidental WAF hit,
which is the opposite of entry 32's intent, and known problem 4's assumption that "France should be
unaffected" is false.

**And the 403 is not a refusal at all.** `france-visas.gouv.fr` answers `cf-mitigated: challenge` — a
Cloudflare interstitial reading *"enable JavaScript and cookies to continue"* — and answers it for
`/robots.txt` as well, so the authority never stated anything. The project's own renderer, under our own
user agent with nothing spoofed, reads the page. That is decided (entry 41) and unimplemented
([TODO.md](TODO.md) item 5).

The underlying coverage fact survives, with a narrower reason: France publishes the visa decision only on
`france-visas.gouv.fr`, and behind the challenge it sits inside a **four-step wizard** rather than on a
page, so no amount of reading reaches it. Every readable French government page delegates there rather
than saying it. Two real scoring defects turned up on the way and are
fixed — a mission host label read as who a page is *for*, which put France's India post above its UK
post for a UK applicant, and footer boilerplate taking three of the ten fetch places.

The first six were verified live on 2026-08-16 with `discovery_decider: model`. Brazil was the
out-of-sample test that broke keyword ranking, so the last step now asks a model — entries 15 and 16.
France and China were the confirmation runs, and both refused correctly at the time — entry 17;
France's outcome has since changed, above.

The United States was added on 2026-08-17 and is the corridor that showed the trust rule needs a
bound as well as a test — entry 22. It now resolves, and **identically on three consecutive runs**
with both caches cleared between them, where before it was a coin flip. Its `document_checklist`
goes unfilled because the canonical B1/B2 checklist lives on `travel.state.gov`, which answers 403;
that is reported as `blocked` and nothing is put in its place.

**It also produces a plan, which no checklist-less corridor previously could** — entry 23. Entry 14
decided a missing checklist should not refuse, and built the validator to make that safe, but the
extractor still demanded one, so the decision reached nobody and Vietnam would have hit the same wall.
`POST /visa-plans` for an Indian passport, resident in India, tourism, now answers **HTTP 200 in
16.6s**: `partial`, visa required, B-2, five steps, three cited sources, **zero document
requirements**, and unresolved questions naming the gap. A plan with no checklist source is never
`verified`, so it cannot look complete.

**The limit has moved from ranking to access.** Of seven corridors, none now fails because a page was
mis-ranked. They fail because a page could not be read at all — bot-blocked portals, client-rendered
shells, dead endpoints.

**Amended 2026-08-19: there is a third thing, and it is neither.** `canada/GB/GB/tourism` fetched and read
the page that answers it, and refused anyway, because the adjudicator's 6,000-character excerpt ended
2,597 characters before the sentence naming a British citizen as eTA-required. Not ranking, not access —
**truncation**. The excerpt now follows the traveller rather than the page (entry 42), and on 2026-08-21
that corridor resolved from exactly the sentence the old excerpt cut. But the run before it refused, on
the same code, because the page was never retrieved — so there is a fourth thing, **recall variance
between runs** (known problem 19), and "access" remains an incomplete diagnosis.

`countries.yaml` covers ISO 3166-1. Fourteen entries are curated from corridors actually run; the
rest carry the name and ccTLD, which is all the own-government trust rule needs. A country only
needs promoting to curated status once you have run it and seen which hints it lacks.

**Discovery is wired into the request path.** A destination nobody configured is researched when
it is asked for: its own government's domains are identified, the corridor resolved, and the plan
built from what was found. No human approves anything. Verified end to end — Brazil, with zero
configured sources, produces a `verified` plan with six source-cited requirements.

Runtime mode is `source_mode: live`, `extraction_mode: openai`, `render_mode: never`,
`discovery_decider: model`, `destination_mode: automatic` in
`src/visa_research_agent/config/runtime.yaml`. `visa-discover` now
needs `OPENAI_API_KEY`; set `discovery_decider: heuristic` for the free, offline, deterministic
path, which is still tested and still the regression baseline. Japan only works live, because its checklist is a PDF
and there are no snapshots for it.

**Client-rendered pages can now be read**, but rendering is off in committed config. Turning it on
means `render_mode: on_demand` plus the optional extra:

**Before turning it on, note what was fixed on 2026-08-18 (entry 37).** Two of the three render
allowances were counted on objects that outlive a run — `LiveSourceFetcher`, which is an
`lru_cache(maxsize=1)` singleton, and the renderer itself, which the API never closes. They were
process-lifetime budgets: after 5 rendered sources, and 17 rendered pages installation-wide,
rendering silently stopped and every client-rendered page reported *"too little readable text to
trust"* — a reason that was not true of what was seen, since the page had never been read. The
allowance is now a per-call value and the renderer keeps no count. **This was latent, not observed
in production**, because `render_mode: never` means nothing has rendered yet; the corridor it would
have hit first is Vietnam, which is exactly the one rendering exists for.

```bash
.venv/bin/pip install -e ".[render]" && .venv/bin/playwright install chromium
```

Selecting `on_demand` without the extra raises rather than silently skipping rendering.

**The traveller comes from the request.** Passport, country applied from and purpose are required;
city, residence status and permit expiry are optional. Countries are ISO codes, normalised at the
API from whatever the caller wrote. `config/traveller.py` holds the default the interface opens on
and the profile the Singapore fixture was recorded against.

Ordinary passports only, and that is deliberate: diplomatic and official passport pages are a hard
veto in scoring, so such a plan cannot be researched and the schema refuses it rather than
answering with the ordinary-passport rules.

---

## How the pieces fit

A plan is produced by a two-stage pipeline with one seam:

```
DestinationConfig ──▶ SourceFetcher ──▶ RetrievalReport ──▶ VisaPlanExtractor ──▶ VisaPlan
                      fixtures | live    fetched+failures    fixture | openai
```

Discovery sits *before* this and produces the `DestinationConfig` the pipeline consumes. It runs
either as the `visa-discover` command or, for a destination nobody configured, inside the request:

```
Corridor ──▶ search ──▶ corpus ──▶ crawl ──▶ fetch shortlist ──▶ score ──▶ ResolvedCorridor
             (Brave)  (var/corpus)  (skipped   (via LiveSourceFetcher)      or a refusal
                                     when the corpus
                                     out-covers it)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the detail, including the trust model, which is the part
most likely to be misunderstood.

---

## The one idea that explains most decisions

> **Officialness is a property of who controls the domain, never of how a page reads.**

An unofficial page cannot become evidence however convincing it looks, because it is unreachable
rather than merely low-scoring. This is enforced in three places, and any change touching retrieval
must keep all three: when configuration loads, after every HTTP redirect, and after every
meta-refresh forward.

The second idea, which follows from the first:

> **Refusing is a legitimate, and often correct, output.**

A plausible-but-wrong document checklist is worse than no answer, because the traveller is told with
full confidence to bring the wrong papers to a visa centre. Every layer prefers to refuse and say
why.

---

## Known problems

Ordered by how much they limit the product, **except that numbering is append-only**, because references
to these numbers exist in `CLAUDE.md`, `ARCHITECTURE.md` and `TODO.md`. **None of these are secretly
fixed; they are all live** — with one qualified exception, item 18, whose *cause* was changed on
2026-08-21 and whose corridor has not been re-run since. It stays on the list until it has.
Several carry a *decision* (entries 29–35), and a decision is not a fix — items 3 and 4 below are decided
and still unimplemented. Three were **removed** on 2026-08-18 because they are genuinely fixed: a block resolving a corridor
it had nothing to do with (entry 32), the unverified `conflicts` field (entry 30), and a failed model
call silently substituting the heuristic (entry 31).

1. **Whether this is a product is genuinely unmeasured.** Two of the highest-volume corridors there are,
   India→US and India→France, yield a plan with **no document checklist**, because the pages holding the
   answer are bot-blocked. Seven corridors cannot say whether that is the rule or the exception, and the
   sample was chosen partly for being easy. Entry 35 commits a bar in advance — top 20 corridors by
   volume, product if ≥70% confirm the decision and ≥50% yield a checklist — precisely so the answer
   cannot be rationalised after the fact. **Brave credit arrived on 2026-08-21, so it can run.** Nothing
   large should be built before it does.
2. **The trust rule refuses a fifth of the world, with a wrong diagnosis.** Measured offline on
   2026-08-18: `is_own_government` fails for **19 of 51** countries — Austria, Belgium, Canada, Chile,
   Czechia, Germany, Denmark, Finland, Greece, Hungary, Ireland, Italy, Netherlands, Norway, Portugal,
   Romania, Russia, Sweden, Uruguay. Every one fails on `looks_governmental`, whose pattern list happens
   to cover all seven verified countries — so entry 19's 22/22 agreement with human decisions is
   survivorship. Most of Schengen is unreachable, and **Schengen is additionally a definition problem** —
   `europa.eu` can never pass `belongs_to_destination` for a member state. Entry 33; fix is reviewed data,
   never a wider regex. Frozen in `tests/test_trust_coverage.py`, so the number moving is a visible diff.

   **These are two failures, and the second is the one to worry about.** Nine countries (AT, BE, DE, DK,
   FI, NL, NO, SE, UY) have no marked domain at all: they refuse, safely, with a message that misdescribes
   why. **Ten (CA, CL, CZ, GR, HU, IE, IT, PT, RO, RU) do have one** — `interno.gov.it`, `gov.ie`,
   `gob.cl`, `cic.gc.ca` — so bootstrap **succeeds** and resolves the corridor against a trusted set that
   cannot contain the page holding the guidance. Nothing reports that, so it will read as a ranking
   failure. Canada is the sharpest: `gc.ca` is special-cased and passes, but the content moved to
   `canada.ca`.
3. **"Who to believe" is decided inside every request and cached per corridor.** `bootstrap_destination`
   runs in the cold path, so a country's trusted set is re-derived from that day's search rankings for
   every new nationality — the variance entry 22 diagnosed as a ranking problem. `ARCHITECTURE.md`
   already says domains should be decided once per country. Entry 34 moves it to committed data.
4. **The blocked-source plan has never been run live.** Entry 27 lets a corridor resolve when the only
   gap is behind a block, states the decision as unknown, and hands the traveller the URL. The chain is
   covered by tests, but Brave answered `HTTP 402` before France could be re-run, so what a model
   actually writes for it is unverified — as is whether "Uncertain" reads as *we could not check* rather
   than *no visa needed*. **And the code changed before it was ever run live:** the block-handover
   narrowing (entry 32) landed first, so what needs re-running is the narrowed behaviour rather than what
   entry 27 originally shipped. France should be unaffected — `france-visas.gouv.fr` is exactly the
   credible decision candidate the narrowing keeps — but that is the assumption the live run tests.

   **Run again 2026-08-23 across six corridors, and the picture is now much clearer — see entry 55.**
   The chain *does* work end to end and Sweden proved it on the crawl path: `government.se` refuses five
   URLs including its visa list, `decision_blocking_urls` narrowed correctly to a credible decision page,
   `decision_is_unverified` was true, and the corridor resolved `partial` naming the blocked pages. **So
   this item's mechanism is confirmed live for the first time.** What is *not* confirmed is the last
   step — nobody has read the plan a traveller receives. And on the **corpus path** the exception stops
   firing entirely for both Sweden and France, which is known problem 25.

   **Run 2026-08-19, and the assumption is false.** None of the eight `france-visas.gouv.fr` URLs that
   were actually refused scores for `visa_decision` — every one scores `application_route` only,
   including `/en/assistant-visa`, the visa-decision tool itself — so none of them can qualify a
   corridor. France resolved once on
   `www.diplomatie.gouv.fr/spip.php?page=recherche&recherche=Demande+de+visa`, a **site-search results
   page** scored on the words in its own query string, then refused outright on a fresh run an hour
   later. So this is now two problems: the plan is *still* unread by a traveller, and what reaches it is
   decided by an incidental WAF hit. `boilerplate_tokens` vetoes legal notices and sitemaps but not
   search pages. Entry 41 and [TODO.md](TODO.md) item 5.
5. **A cold request is slower than the 34.1s these files used to quote, and the current figure is
   unmeasured.** That number was 19.4s corridor + 14.7s plan, measured before the registry on
   hand-configured destinations. **Measured 2026-08-18 on the registry path, the corridor phase alone is
   39–45s** (Japan 44.5s, Canada 45.2s at the old 10-place shortlist). The cause is arithmetic:
   `corridor_queries` runs **three searches per trusted domain**, and the registry gives a country up to
   five where `japan` in `destinations.yaml` had two — so six queries became fifteen. **This is a
   consequence of entry 38, not of entry 40**: the wider shortlist was measured separately and had no
   latency cost, because fetching is concurrent.
   **Nobody has timed a full cold request end to end since**, so the total is genuinely unknown rather
   than known-and-bad — but it plainly no longer fits a 30–60s proxy timeout comfortably, and deployment
   should not be planned against 34.1s. The obvious lever is the per-domain query count, not the
   shortlist. Warm is instant, and the local `var/` stores are what make it warm.
6. **A destination is trusted on a rule whose output a person now reviews once, and the audit behind
   the rule was survivorship.** **Changed on 2026-08-18 (entries 38 and 39):** the rule no longer runs
   per request — its output is committed in `config/authority_domains.yaml`, so a wrong call is a
   reviewable diff rather than a search ranking, and a person may override it in `reviewed` with the
   evidence. Twelve countries needed that override. **40 of 198 countries are built**; the rest refuse
   naming the command. The rule reproduces all 22 recorded human decisions, but every country in that audit
   was one `looks_governmental` already handled — see item 1, which is the concrete failure this warning
   used to describe hypothetically. The other half of the hole stands: a country whose TLD hosts a
   convincing government-shaped domain it does not control. Watch `withheld_domains` on resolved
   corridors for domains declined that should not be; it carries everything declined, including what the
   cap left out and what bootstrap rejected outright. **Trustworthy as of 2026-08-18, and it was not
   before:** Italy's real foreign ministry used to be declined as *"not a government domain for this
   destination"* — false, and character-identical to what a commercial visa agency got, so a reviewer
   following this very advice was misled rather than warned. It now reads *could not be confirmed as an
   authority … may be a real one*, and a refusal names such candidates instead of claiming none were
   found (entry 33). **Still not reported:** whether an accepted set plausibly holds a visa authority at
   all — the second failure in item 1. **The cap (entry 22) is where a wrong call would
   show first:** at most five of a destination's own domains are used, ordered by the hostname's
   authority hint then corroboration, so a country whose guidance genuinely spans six or more of its own
   domains loses one, and that reason is the only warning. Five is calibrated against corridors run, not
   derived.
7. **A blocked authority reaches the plan, but nobody has confirmed it reads usefully.** This entry
   used to claim a discovery-time block reached the plan *only* when it blocked the decision, and that
   the US plan therefore never said `travel.state.gov` refused us. **Checked on 2026-08-18, and that
   was wrong:** `to_destination_config` populates `unreadable_authorities` from `inaccessible_urls`
   unconditionally, the extractor turns those into `unavailable_sources` regardless of
   `decision_is_unverified`, and retrieval-time blocks arrive by a second route through
   `RetrievalReport.failures`. The interface then gives any `blocked` failure with a URL the sentence
   *"does not permit automated retrieval"* and a link. So the mechanism is in place by two paths.
   **Amended 2026-08-23 (entry 49): one of those two paths was narrower than described.**
   `inaccessible_urls` could only ever be populated by the **crawl** — `_fetch_bodies` discarded
   `report.failures`, so a page refused while the shortlist was being *read* contributed nothing to the
   corridor at all. The second path named above is the *plan* pipeline's own `RetrievalReport`, which is
   real and unchanged; what did not exist was the discovery-side one. It does now, which is what allowed
   the crawl to be dropped.
   **What is genuinely unknown** is whether a traveller reads it that way, which needs the live run in
   item 3 — and whether the two `travel.state.gov` places entry 24 left unfetched mean the US corridor
   records the block at all. Do not fix the mechanism before reading a real plan; the previous entry is
   an example of describing this from the code rather than from output.
8. **Nothing distinguishes "this country publishes no checklist" from "we failed to find it."**
   Both produce the same empty result, and since a missing checklist no longer refuses the corridor,
   a find-or-read failure now yields a plan with a visibly empty checklist rather than a refusal.
   The plan says so — `VisaPlan` enforces that — but nobody is told *which* case it is. If plans
   start shipping empty checklists for countries that do publish one, this is the cause; a
   per-country human declaration is the designed fix. See [DECISIONS.md](DECISIONS.md) entry 14.
9. **The heuristic scorer still mis-ranks — but it is a recall gate, not a decider, and that changes
   what to do about it (entry 40).** This entry used to say "a page it ranks out of the ten fetch places
   is one the model never sees" and then reason about improving the ranking. The conclusion to draw was
   the other one: **widen the gate.** At 25 places Canada and Japan went from refusing to filling every
   role, with no scoring rule touched and no latency cost. What remains is genuinely a ranking fault and
   is now sharply defined: for an Indian national applying from Great Britain the scorer gives
   `checklist-schengen-visa-tourism/india` **113.0** against **73.0** for `/united-kingdom`, when for a
   consular checklist the **post** governs. The adjudicator correctly discards the wrong-post page, so
   the corridor throws away a checklist it already fetched.
   Two older fixes landed — a checklist is known by the documents it names, and the traveller's post
   governs — but both rest on English vocabulary and per-country city labels, so it will keep degrading
   on new countries and languages. **It is no longer the fallback** (entry 31), but it still matters,
   because it builds the shortlist the model chooses from: a page it ranks outside the window is one the
   model never sees. It also remains the offline regression baseline.

   **There is a second recall gate behind this one, and on 2026-08-19 it was the binding one.** Getting a
   page into the shortlist was not enough — the adjudicator saw only its first 6,000 characters, so Canada
   ranked its answer *first* for `visa_decision`, fetched it, and refused anyway. Widening the shortlist
   without widening the excerpt moved the bottleneck rather than removing it. Changed 2026-08-21 —
   known problem 18 and entry 42.
10. **The model decider is non-deterministic and evidenced by six corridors on one day.** Its
   containment is tested with a fake; its *judgement* is not something tests can pin. Re-run the
   six after any prompt change, and read `decided_by` and the recorded heuristic score to see where
   the two deciders disagreed.
   **Isolated for the first time on 2026-08-23** (entry 53). With the candidate count and shortlist
   identical across three runs, run 2 filled `processing_times` and runs 3 and 4 did not — so that
   variance is adjudication rather than recall, which was never separable from known problem 19
   before. In the same three runs `document_checklist` went unfilled every time although **eleven**
   candidates scoring for the role were fetched, `supporting-documents.html` among them at 64.0. The
   recall gate did its job and the decider declined, which is the honest outcome; but it means a
   corridor can now be `is_usable` with a role unfilled for a purely model-side reason, and nothing
   distinguishes that from known problem 8's "no checklist exists".
11. **~~Bot-blocked official portals are the largest coverage limit~~ — measured 2026-08-24, and they
   are not. The *wizard* is.** Entry 58: across 40 runs, blocks cost the United States its checklist
   and turned one corridor's decision into *blocked*. An interactive tool cost **every United Kingdom
   corridor its entire plan** — eight runs refused after successfully finding the checklist, the
   route, the processing times and per-nationality fees, because `gov.uk/check-uk-visa` is a
   step-by-step wizard that was fetched, read, and correctly judged not to state the answer. France
   is the same cause with a `403` on top, which is the only reason France resolves and the UK does
   not. TODO item 24. The rest of this entry stands and is about blocks specifically.

   **Bot-blocked official portals are a large coverage limit — but "permanent" was the wrong
   word.** Three found: `france-visas.gouv.fr`, `www.france-visas.gouv.fr` and Singapore's VFS page.
   France is the clearest case, quantified in entry 26: **every** readable French government page
   delegates the visa decision to the blocked portal, so no amount of better ranking can confirm it.
   Working around a block stays forbidden by entry 18 and by `CLAUDE.md`, and nothing about that has
   changed. What entry 35 corrects is the conclusion drawn from it: the loss is permanent *given an
   anonymous, unauthenticated client*, and that posture was never itself decided. Honouring
   `robots.txt` — **now read and obeyed** (entry 36) — asking for access, and the open
   client-side-retrieval question are all legitimacy rather than circumvention. **Measured 2026-08-18:
   `robots.txt` buys nothing here at all.** `france-visas.gouv.fr`, `www.france-visas.gouv.fr` and
   `travel.state.gov` answer `403` **to their own `robots.txt`**, served as a bot-detection
   interstitial — there is no stated policy to honour, because it is a WAF rather than a rule. So the
   first legitimacy step is spent and this limit is exactly where it was. What remains of entry 35 is
   asking for access and the client-side question; item 3's twenty corridors still size it.

   **Reopened 2026-08-19: this item had the right observation and the wrong conclusion.** It noticed the
   `403`-on-`robots.txt` and concluded the limit was unchanged. The response headers say what it actually
   is: `cf-mitigated: challenge`, *"enable JavaScript and cookies to continue"* — a Cloudflare
   **challenge** rather than a refusal, and Cloudflare's act rather than the Ministry's. Nothing was ever
   stated to disobey. The project's own renderer, announcing `VisaResearchAgent/0.1` with nothing
   spoofed, reads the page: 221,476 bytes, `blocked_hosts: []`, ~7s. **So "largest permanent coverage
   limit" is wrong twice over** — not permanent, and never a policy. Decided as entry 41, unimplemented
   as item 5. **What survives:** France's answers sit inside a four-step wizard rather than on a page, so
   reading the host honestly is necessary and not sufficient — and "asking for access" is largely moot
   here, because there is nobody to ask about a rule that was never made.
12. **Discovered pages still have no staleness check.** A CMS publication date is now read from the
   path and reported — to the adjudicator, which can weigh it against the page's text, and in the
   proposal for a human. But that is a *report*, not a check: it is deliberately not a veto,
   because two of China's correct picks carry dated paths and one is from 2013. Content-hash drift
   detection remains a TODO and covers configured sources only.
13. **Scoring is English-only.** A destination publishing solely in its own language will score near
   zero and refuse. Now visible in practice: rendering `xuatnhapcanh.gov.vn` yields 9,327
   characters of Vietnamese, which scores nothing.
14. **`xuatnhapcanh.gov.vn/en` is broken server-side.** It answers `200` with a
   `location: http://localhost:4000/vi` header and an empty body — a misconfigured Next.js i18n
   redirect. Browsers ignore `Location` on a `200`, so **rendering does not fix this one either**;
   it renders to 0 characters. The site root works; only the `/en` path is broken.
15. **An authority's own outdated microsite is undetectable** — right domain, live, linked,
   text-rich, so every check passes.
16. **Mission detection only works when a mission has its own subdomain**, and does nothing at all
   for a consolidated portal. `_mission_domains` returns `[]` for Brazil, whose every mission sits
   on `www.gov.br` with the post in the *path* — so Riyadh and Atlanta outrank Edinburgh for a UK
   applicant. It also misses Singapore's `london.mfa.gov.sg`, which is named by city rather than
   country code. Recorded here as latent; Brazil proved it changes the answer. **Broader than
   recorded:** `_mission_domains` reads `destination.sources`, and the automatic path builds a config
   with none, so it returns `[]` for **every** discovered destination regardless of how its missions
   are named. Mission detection survives there only through `mission_affinity`'s host-label check —
   which is what still recognises `in.usembassy.gov` as the post serving an Indian traveller.
17. **The retrieval cache is not re-validated against changed rules.** After changing what counts as
   usable, cached entries still serve the old result until their TTL expires. Clear `var/cache/`
   when testing a retrieval change, or a fix will appear not to work.
18. **The adjudicator's excerpt silently decided corridors, and which travellers got an answer depended
   on the alphabet. Changed 2026-08-21; not yet confirmed live.** Added 2026-08-19, when
   `DEFAULT_EXCERPT_CHARACTERS` was a flat 6,000-character head slice. `canada/GB/GB/tourism` ranked the
   right page **first** for `visa_decision`, fetched it, and refused: the sentence answering a British
   traveller sits at offset 8,597 of 16,465 and the window ended at 6,000 — mid-alphabet in the
   *visa-required* list, at "Morocco".
   **Why it was worse than one corridor:** the page lists visa-required countries alphabetically and the
   eTA list only from offset 8,517, so Brazil (4,720), China (4,909) and India (5,325) were answered while
   Vietnam (7,787), Australia (8,815), a British citizen (8,858), Japan (9,647) and Singapore (9,856) were
   not — **every visa-exempt nationality was past the cut**. Nothing in the output distinguished "the page
   did not say" from "we stopped reading", and the adjudicator's refusal reason was accurate about what it
   had been shown, which is what made it invisible. It is also why entry 40's "Canada fills every role"
   did not generalise.
   **What changed:** `anchored_excerpt` shows the head plus a 3,000-character window centred on every
   later mention of the traveller's own nationality or residence, to a 20,000-character budget, marking
   omissions with `[…]` (entry 42).
   **Run live 2026-08-21, twice, and the two runs disagreed.** The first refused: of 24 candidates
   fetched, `entry-requirements-country.html` was not one, so the excerpt had nothing to widen. The
   second **resolved**, with `visa_decision` filled from that page by the model, quoting the sentence at
   offset 8,597 — which a flat 6,000-character excerpt could not have shown. So this defect is confirmed
   fixed on the corridor that found it. What the two runs also showed is known problem 19.
   **This item stays open** only until the other six corridors have been re-run
   ([TODO.md](TODO.md) item 15); nothing about the excerpt itself is outstanding.
19. **The candidate set for one corridor varies between runs, and the answer varies with it.** Measured
   2026-08-21: `canada/GB/GB/tourism` run cold twice within the hour, same five trusted domains, same
   fifteen queries, same code. The first run refused — `entry-requirements-country.html` was not among
   its candidates at all. The second **resolved**, with that page ranked **15th of 470** candidates at
   53.4, arriving both as a `site:canada.ca` search seed and by crawl at depth 1 from
   `check-visa-eta.html`. So it is not a marginal candidate that scoring pushed out; on the failing run
   search simply did not return it. That page is still the only one found that states Canada's
   requirement for a British citizen in static text.
   **What this means for every other corridor:** a resolved corridor is not evidence the pipeline is
   reliable, only that this run of it was. The corridor store then keeps the lucky result for three
   weeks, which hides the variance until re-resolution. TODO item 17 is what to do about it, and the
   20-corridor measurement (item 3) should be read with it in mind — one run per corridor cannot
   distinguish a corridor that works from a corridor that works half the time.
   **Now diagnosable, which it was not:** every run writes `var/recall/<corridor>.json` with all 470
   candidates, their scores, and the shortlist and fetch flags (entry 43).
   **Measured again 2026-08-23 on the corpus-routed path** (entry 53): four runs, **2,455 candidates
   every time**, the same 25-page shortlist and 24 fetched, and `visa_decision` filled from the same
   page on all three runs that resolved. That is the closest this has come to a stable candidate set,
   and it follows from 2,387 of the 2,455 coming from a file. **It still does not close this item**:
   minutes apart, one corridor, one destination, and 68 candidates still come from search, which is
   nondeterministic at the source. What it *does* buy is separation — see known problem 10.
   **Decided 2026-08-21 as entry 44, and not implemented.** The candidate set becomes a stored **corpus
   of official pages per country**, populated offline, so search leaves the request path for a populated
   country and two runs of one corridor consider the same candidates. It fixes the measured cause here —
   Canada's page was also reachable by crawl at depth 1, which an offline job with no latency budget
   reaches reliably — and it fixes **recall only**: adjudication is still a model call (known problem
   10), and a page the offline job never finds becomes a permanent gap rather than a coin flip. TODO
   items 18 and 19; item 17 keeps the counting that sizes it.
   **Counted 2026-08-22, and the flip did not reproduce.** Three back-to-back runs, cache cleared:
   **471 candidates, every run saw all 471**, all three resolved, and `entry-requirements-country.html`
   arrived every time by *both* a `site:canada.ca` seed and a depth-1 crawl. So the rate is **0 of 3
   back-to-back** — two minutes apart, against an hour for the observed flip and two days for the
   original divergence — which cannot tell *"recall is stable"* from *"recall is stable over two
   minutes"*. The gapped re-run is what would settle it, and until then entry 43's flip is one
   observation. This item stays open; it has not been shown to be fixed, only not to reproduce today.
20. **A live plan cites a URL with no supporting quote.** `SourceReference.supporting_excerpt` is written
   only by `FixtureSourceFetcher`, from the Singapore manifest (`fixtures.py:103`).
   `LiveSourceFetcher._build` does not set it and `OpenAIVisaPlanExtractor` passes retrieval's references
   through unchanged, so on the live path it is **always `None`**. *"Why did you say an Indian passport
   holder needs this visa?"* is therefore answerable as *which page*, never *which sentence*. Found while
   tracing entry 44; TODO item 21. **Careful when fixing:** an excerpt the model produces has to be
   checked against the retrieved text, because an unverified quote attributed to a government page is
   worse than no quote.
21. **A plan cannot be tied to the text it was read from.** `content_hash` is recorded on
   `FetchedSource` and `SourceReference` has no hash field, so nothing in a `VisaPlan` identifies the
   version of the page behind a claim. TODO item 21.
22. **Why a page was chosen for a role never leaves discovery.** `ResolvedSource.decided_by`, `score` and
   `signals` are stored in `ResolvedCorridor` and appear nowhere in the API response, so a reader of a
   plan cannot see whether the model or the heuristic picked its decision source, or on what reasoning.
   TODO item 21.
23. **The interface offers 198 destinations and can research 39.** `researchable_destinations()`
   ([api/routes.py](src/visa_research_agent/api/routes.py)) lists every country in `countries.yaml` with
   `status="available"` when `destination_mode: automatic`, but a country with no row in
   `authority_domains.yaml` is refused by `AutomaticDestinationService.destination_for` — 158 of them —
   and Austria's row has no usable domain. So a traveller picks from a full list and gets a `503` for
   four out of five choices. The refusal itself is honest and names the command; the *offer* is not.
   Counted 2026-08-22. The fix is either to mark unbuilt countries in the list or to build the registry
   out (item 2); do not fix it by loosening the refusal.
24. **A thin corpus now has no crawl behind it, and coverage varies enormously between countries.**
   **The first half of this item is closed** — the path has been run live on **seven** destinations
   (entries 53 and 55), 2.1×–5.2× faster with the crawl at 0.0s, and roles genuinely found are neutral
   to better.
   **What the six-corridor run added is how uneven corpus coverage is.** Measured against the pages
   that actually filled roles on the crawl path: Singapore 6/6, United States 3/3, Sweden 3/4, France
   2/3, Netherlands 1/2, **Japan 1/6**. Japan's corpus holds 29 mission hosts — Auckland, Boston, San
   Francisco, Edinburgh — and **not the London embassy**, where five of its six roles came from,
   because the offline build is traveller-free and takes whatever missions search returns. It resolved
   all six roles anyway **because search still runs**, which is the strongest evidence yet for entry
   48's refusal to drop search, and the clearest warning against doing so later.
   Second, **the safety net is thinner than it was.** For a country whose corpus passes
   `DEFAULT_CRAWL_PAGES` but whose corpus *recall* is poor, the crawl used to compensate — badly and
   nondeterministically, but it compensated. Now it does not. Entry 51 argues the trade, and entry 47's
   write-back is what repairs it over runs, but the first corridor into such a country pays the whole
   cost and **nothing counts how often the corpus was the only source and came up short.** The
   `found_by="corpus"` field added with entry 51 is what would make that countable from the recall log;
   nobody has counted it.
25. **~~Entry 27's blocked-authority exception stopped firing.~~ FIXED and confirmed live 2026-08-24.**
   The cause was a vocabulary gap, not the `not scores` guard item 23 blamed — the `visa_decision`
   terms were all ways of *asking* the question, with no way to recognise a page that states the
   answer (entry 56). Sweden's decision page went `visa_decision` **0.0 → 82.4**, and two live runs
   now give `usable: True`, `decision_is_unverified: True`, and `decision_blocking` naming the exact
   page `government.se` refused. **Entry 27's exception has now fired on a real corridor for the first
   time.** France still refuses with nothing qualifying, correctly — its old qualification was a blank
   CERFA form. Kept here for one cycle as a record; delete it after the next handoff edit.
   The original description follows.

   **Entry 27's blocked-authority exception has stopped firing, and it is a scoring bug, not a block
   bug.** Measured 2026-08-23 (entry 55): `sweden/IN/GB/tourism` and `france/IN/GB/tourism` both went
   from resolving to **refusing** on the corpus path. Reporting is intact — `inaccessible_domains` and
   `inaccessible_urls` still name the refusing hosts and pages, so entry 49 works. What broke is
   *qualification*: `_decision_blocking` requires a refusal observed on a page that scored for
   `visa_decision`, a 25-page fetch observes far fewer refusals than a crawl did (France: 6 against 18),
   and the pages it does observe score for the wrong role.
   **The root cause is one line in `score_role_vocabulary`**, which grants the "mentions visas" base
   score to `visa_decision` only when the page scored for *nothing else*. So
   `government.se/.../list-of-foreign-citizens-who-require-visa-for-entry-into-sweden` scores
   `general_entry` 22.4 and **no `visa_decision` at all**. Entry 41 saw this on France and recorded it
   as a French quirk; it is general.
   **Not all of it is a regression.** France's crawl-path qualification was on a **blank CERFA
   application form**, which is the incidental hit entry 41 warns about — refusing is better. Sweden is
   a genuine loss. [TODO.md](TODO.md) item 23; do not fix it by loosening `_decision_blocking`.

---

## Current task

> **The measurement that decides whether this is a product has run, and it passes — marginally.**
> Entry 58, 2026-08-24: **75%** confirm the decision against a ≥70% bar, **50%** yield a checklist
> against a ≥50% bar. The bar was committed in advance (entry 35) and was met. It was met by one
> corridor on the first number and by nothing at all on the second, so quote it as a marginal pass,
> and read the sample caveat below before quoting it at all.

**The sample is five destinations, not twenty corridors.** Nationality changed the outcome once in
twenty; destination decided the rest. So 75% is "three and three-quarters of five destinations", and
the next measurement should sample **destinations**, not corridors.

**Pick up [TODO.md](TODO.md) item 24 — say "the answer is behind a tool we cannot drive."** It is the
largest coverage limit there is, now measured rather than assumed:

- **All eight United Kingdom runs refused**, having already found the checklist, the application
  route, the processing times, and per-nationality fees down to the currency. Nothing was blocked.
  `gov.uk/check-uk-visa` was ranked, shortlisted, **fetched and read**, and the adjudicator correctly
  judged that it does not state the answer — because it is a step-by-step wizard.
- There are three outcomes and the code can express two. *Found* resolves; *blocked* resolves
  `partial` and hands over a URL (entries 27, 57); **"read it, and the answer is only inside a
  form"** has nowhere to go, so it becomes *not found* and the corridor throws away correct work.
- This inverts known problem 11. Blocks cost the US its checklist; the wizard cost the UK five
  destinations' worth of plans in one.

**The trap to avoid is entry 32's, exactly.** If "we could not find it" can present as "an authority
made it unavailable", every failed corridor drifts into looking authority-limited. The difference
here is that the page **was read**, so the claim is narrower and checkable — the model is saying the
text defers to a form, not guessing about a page nobody saw. Do not solve it by driving the wizard;
that is an application flow and it is on the permanent no list in [CLAUDE.md](CLAUDE.md).

**Then item 9** — tell "this country publishes no checklist" from "we failed to find it". Germany and
the United States both return 0/8 checklists and nothing distinguishes the two cases, which is now
two of five destinations rather than a hypothetical.

**Everything before this is done and confirmed live** — item 22 (entries 49–53), the six-corridor
re-run (entry 55), item 23 (entry 56), the `_decision_blocking` question (entry 57), and item 3
itself (entry 58).

### Where the previous work got to

**Updated 2026-08-21. Of the two corridors investigated on 2026-08-19, one fix has landed and one has
not.** `canada/GB/GB/tourism` refused because the adjudicator's 6,000-character excerpt cut off the page
that answers it; the excerpt now follows the traveller — head plus a window around every later mention of
their own country, at 20,000 characters, with omissions marked (entry 42, known problem 18).

**It was re-run cold twice the same day, and the two runs disagreed — which is the most useful thing on
this page.** The first refused: the answering page was not among the 24 candidates at all, and the
adjudicator refused because what it *did* get is the JavaScript wizard, which it described as showing
*"Your result is loading"* (item 5, named independently by the model). The second **resolved**, filling
`visa_decision` from that page with the sentence at offset 8,597 — which the old flat 6,000-character
excerpt could not have shown. **So entry 42 is confirmed, and a second gate upstream of it is now
visible:** whether the page arrives at all varies between runs (known problem 19).

**That variance is why `discovery/recall_log.py` now exists** (entry 43). Every run writes
`var/recall/<corridor>.json` — all 470 candidates Canada considered, their scores, and whether each was
shortlisted and fetched — so the next refusal can be diagnosed instead of inferred. It answered the
question on its first run. The other six verified corridors have not been re-run; that is the rest of
item 15.

**And the variance now has a decided answer, entry 44, which is where the next work is.** A database was
investigated on 2026-08-21 and the conclusion is narrower than the question: **persist the country's page
corpus, never the answer.** Which pages exist does not vary by corridor — only which one answers a given
traveller does — so the corpus is populated by an offline job with no latency budget, and search leaves
the request path for a populated country. That is entry 34's move one level down. A miss **refuses and
flags the country**, per entry 38, rather than falling back to live search.

**Read what it does not do, because it is easy to overstate.** It fixes recall, and Canada's page was
reachable at depth 1, which an offline crawl reaches reliably. It does **not** make adjudication
deterministic (known problem 10), and it turns a page the job never finds into a *permanent* gap rather
than a coin flip — a better failure, because a stable gap is visible and fixable, but a trade rather than
a win. Precomputing answers per corridor was rejected on arithmetic before safety: 196,020 corridors is
~2.9M searches a refresh cycle. Items 18 and 19 are the implementation; item 17 keeps the counting that
sizes it.

**Finished 2026-08-23, and the last step of it argued against its own design.** Entries 46 and 47 built
the store and made the candidate set ratchet; entry 48 measured where a corridor's 54.2s goes and
proposed a routing index; entries 49–51 built the outcome. **The crawl is out of the request path** for a
country whose corpus out-covers it, **the routing index is not built** because the cost it targeted was
`wrong_country` rather than scoring, and a reporting hole that predated all of it was closed first. Read
entry 50 before proposing a pre-filter over the corpus again: a flat top-400 drops a page that has
already answered a corridor, and a pin cannot rescue it. **Nothing here has been run live** — known
problem 24.

`france/IN/GB/tourism` is untouched. It resolves without a checklist because `france-visas.gouv.fr`
serves a Cloudflare *challenge* rather than a refusal — entry 41, item 5 — and **two things are still
shipping against the project's own rules:** the interface tells travellers a challenged authority
*"does not permit automated retrieval"*, which is untrue of what was seen, and France resolves on an
incidental WAF hit that flips between runs. Neither is a new defect; both were invisible because they
were described from code rather than from output.

The 2026-08-18 review was agreed with in full, recorded as entries 29–35, and turned into an ordered list
in [TODO.md](TODO.md). **All of it is implemented bar two of entry 35's three legitimacy steps.** Five
further entries (36–40) came out of the building, and entry 41 out of the investigation above.

**The pattern across all five is the one to carry forward.** Each time, the constraint was not where the
documentation said it was, and only running the thing showed it: the domain classifier was discarding
domains the search had already found; a wrong trusted set made corridors *refuse* rather than answer,
where these files claimed the opposite; the `robots.txt` parser was inert against every wildcard rule; and
the scorer's ranking was never binding — the ten-place window in front of it was. Four false lines in
these files in two days, every one of them written from reading a code path. **Prefer a corridor run to a
careful reading.**

**Done, all offline and all with tests:**

- **The trust-coverage measurement** (entry 33) — `tests/test_trust_coverage.py`, 7 tests. Freezes the 19
  unreachable countries so a change is a visible diff, asserts every failure is on the governmental half
  rather than the TLD half, and guards `countries.yaml` against another country acquiring a governmental
  marker in its `tlds` unreviewed.
- **The block-handover narrowing** (entry 32) — `PERSISTENT_REFUSAL_STATUS_CODES = {401, 403}` and
  `ResolvedCorridor.decision_blocking_urls`, so a `429` and a `403` on a footer link can no longer resolve
  a corridor or force a visa decision to unknown. Both are still reported. France's shape still resolves.
- **Three deletions** (entries 30 and 29) — the unverified `conflicts` field, `domain/state.py`, and the
  unused `langgraph` dependency.
- **A failed adjudication refuses** (entry 31) — two attempts, then an ordinary refusal, instead of
  silently substituting the heuristic that named Brazil's Riyadh page as a checklist at full confidence.
  A refusal now also reports the model calls it paid for.
- **`withheld_domains` stopped stating something false** (entry 33) — a ministry under its own country's
  top-level domain with no governmental marker now reads as *could not be confirmed*, not *not a
  government domain*, and no longer identically to a commercial visa agency. The refusal message names
  the candidates it could not confirm instead of claiming none were found. Reporting only; nothing new
  is trusted.
- **The shortlist widened from 10 to 25** (entry 40) — one constant, and it bought more than every
  scoring rule in the file. The scorer decides *what the model may see*, not what is chosen, so a page
  ranked out of the window is unrecoverable while a page ranked in wrongly costs an excerpt. At ten
  places the heuristic was the effective decider. **Canada and Japan went from refusing to filling every
  role**; the Netherlands gained its checklist. No latency penalty — fetching is concurrent, and both
  corridors were marginally *faster* at 25 — and adjudication input roughly doubles to ~19k tokens.
  A test pins the width, because narrowing it again fails silently.
- **A person may override the trust rule in committed data** (entry 39) — `CountryAuthorities.reviewed`,
  a domain-to-evidence map that leads the set, counts against the same cap, and **survives
  regeneration**. Twelve countries corrected, each confirmed by a Wikidata reverse lookup (the domain is
  the official website of an entity whose country is that country) — Germany, Italy, the Netherlands,
  Canada, Sweden, Belgium, Denmark, Greece, Ireland, Morocco, Portugal, the UAE. Four domains that could
  not be confirmed were left alone, so **Austria still refuses**, correctly.
  **Measured before and after, and it changed the diagnosis:** Sweden went from fetching *nothing* to
  reading `migrationsverket.se` with two roles filled; Canada gained its document checklist; the
  Netherlands did not move. **None of the three resolves end to end.** The binding constraint moved
  rather than lifted — from "we cannot tell which domain is this government" to "we cannot confirm the
  visa decision on pages we can now read".
- **The trusted-domain registry is committed** (entry 38) — `config/authority_domains.yaml`, generated
  by `visa-discover registry`, read by `AutomaticDestinationService` in place of a live bootstrap. The
  trust rule is untouched; only *when* it runs moved. **40 of 198 countries built**; the rest refuse with
  a message naming the command, which is quota rather than work. Verified live: New Zealand resolved
  fully from committed domains with **0 searches** in the service where 4 went on bootstrap.
  **Reading it found what running it could not** — five countries refused, **twelve confirmed *and
  wrong*** (the Netherlands trusts only its business portal; Canada trusts five `gc.ca` domains while
  IRCC's content is on the unconfirmable `canada.ca`), and the cap spending slots on United States
  missions for an India corridor. The first two are **fixed** by entry 39; the cap's alphabetical
  tie-break is not. **And entry 39 corrected this entry by running it:** a wrong trusted set makes a
  corridor *refuse*, not answer. The line above said the opposite, from reading the code path.
- **`robots.txt` is read and obeyed** (entry 36) — `research/robots.py`, one policy per origin with a
  24-hour expiry, consulted by `discovery/crawl.py` before every page and by `research/live_sources.py`
  before every source and every meta-refresh forward. 32 tests, all offline. A skip is the new
  `disallowed` outcome and gets its own corridor note, so it can never read as "nothing found"; it is
  reported and may never resolve a corridor. **Matching implements RFC 9309 rather than using
  `urllib.robotparser`**, which supports neither `*` nor `$` and so would obey none of the rules
  `www.gov.uk` publishes. **Measured live across six corridors** — the table is in entry 36. It cost
  almost nothing and nothing of value: France lost one news listing, China lost two portals already
  answering `502`, and Japan, Singapore, Vietnam and Brazil lost nothing at all.

**Five findings came out of doing the work, all recorded rather than left in the diff. The pattern in
them is worth carrying: each was a claim that turned out to be wrong when finally tested or run — and
the last was caught only by probing real authorities, not by any test.**

1. **The 19 unreachable countries are two different failures**, and the second is worse (entry 33's
   table). Nine have no marked domain at all and refuse outright with a misleading message. **Ten do have
   one** — `interno.gov.it`, `gov.ie`, `gob.cl`, `cic.gc.ca` — so bootstrap *succeeds* and builds a trusted
   set that cannot contain the visa guidance, and **nothing measures that**. Canada is sharpest: `gc.ca`
   still passes, but immigration content moved to `canada.ca`. The reasons now describe it where the
   ministry was seen at all; measuring it properly is part of TODO item 2.
2. **The trust rule's coverage gap was blamed on the wrong half of the rule** for a week. Known problem 2
   warned about a government publishing outside its own TLD; not one of the 19 failures is that. Every one
   is `looks_governmental`, whose pattern list happened to cover all seven verified countries — so entry
   19's "22 human decisions reproduced, 0 disagreements" was survivorship, not assurance.
3. **A known problem asserted something the code does not do.** It said a discovery-time block reached the
   plan *only* when it blocked the decision. Testing it showed a blocked authority reaches the plan by
   **two** routes regardless, and the interface already renders it with a link — so the plumbing that
   TODO item said to write was already there. Corrected in known problem 7 and in entry 23, and the todo
   became "confirm it reads usefully" instead. Both this and finding 2 were described from reading a code
   path rather than from output, which is the habit to break.
4. **A boolean `robots.txt` verdict produced a false reason, and the test suite caught it** (entry 36).
   Collapsing every non-answer into "disallowed" made the crawl describe **every unreachable host** as
   *"its robots.txt does not permit this client"* — a sentence about a policy nobody had read, and the
   same class of falsehood finding 1 had just removed from `withheld_domains`. The fix is three verdicts
   rather than two, and a transport failure that **raises** instead of deciding, so the caller keeps
   diagnosing an unreachable host as unreachable. The lesson repeats: a reason has to be true of what
   was actually observed, not merely of the branch that produced it.
5. **The stdlib `robots.txt` parser was inert, and only a live probe showed it** (entry 36).
   `urllib.robotparser` matches with `startswith` and supports neither `*` nor `$`. Every rule
   `www.gov.uk` publishes is a wildcard, so this shipped, tested and documented as honouring crawl
   policies while honouring almost none of them. **No unit test could have caught it** — the fake
   policies in the suite were all literal prefixes, because those are what a person writes from memory.
   Matching is now RFC 9309 implemented directly. Same lesson as findings 2 and 3, one level deeper: the
   justification for reaching for stdlib ("its shortfall errs toward fetching less") was written from
   reading the module and was the exact opposite of true.

**Amended 2026-08-23: the corpus is built and read, and the crawl is out of the request path.** Pick up
**[TODO.md](TODO.md) item 3 first** (see *Current task*), then:

- **Item 17 — count the flip rate.** The *decision* is made (entry 44); what is left is the measurement
  that sizes it. Run one corridor three times and write the rate down. Cheap now that the recall log
  exists — and now more interesting, because the crawl half of the variance is gone and what remains
  should be attributable to search and to the model.
- **Item 18 — run the offline corpus job** on the rest of the ~8 destinations item 3 needs. The job
  exists (entry 46); only Canada has been built. This is the one that costs credit.
- **Item 19 — decay live search.** Half of this landed with entry 51: the crawl no longer runs for a
  country whose corpus out-covers it. What remains is search, which stays until the nationality
  dimension has been measured. Costs no credit to build; the measurement it waits on does.
- **Item 15 — re-run the verified corridors against the widened excerpt.** Canada was run twice on
  2026-08-21 — one refusal, one resolution, same code (known problems 18 and 19); six corridors are
  left, and each should be run more than once. Needs search and model credit. Entries 42 and 43.
- **Item 5 — treat a challenge as a challenge.** France's `403` is Cloudflare asking whether we are a
  browser, not an authority refusing us; our own renderer answers it under our own name. It also fixes a
  sentence shown to travellers that is untrue of what was seen. Entry 41.

Then the pre-existing list, which all costs something — a 198-country registry, search quota, or a
decision nobody has argued yet:

- **Item 1 — fix the post-over-nationality weighting** — precise and reproducible: the scorer gives
  `checklist-schengen-visa-tourism/india` 113.0 against 73.0 for `/united-kingdom`, for a traveller
  applying *from* the UK. The adjudicator then correctly discards a checklist the corridor had already
  fetched. **And trace Sweden**, which neither the domain fix nor the wider window moved. Still
  outstanding from entry 38: the cap's alphabetical tie-break, which spends two of India's five slots on
  United States missions.
- **Item 3 — the 20-corridor measurement against the committed bar.** **No longer blocked: Brave credit
  arrived on 2026-08-21.** It decides whether this is a product, so nothing large should be built before
  it, and it now has a posture worth measuring: `robots.txt` landed first on purpose.

**Deployment has moved down the list deliberately, and speed is now part of why.** It used to be
"not blocked on speed — 34.1s, which fits a 30–60s proxy timeout". That number predates the registry and
is stale: the corridor phase alone measures 39–45s now, because three searches run per trusted domain and
the registry gives up to five where a hand-configured destination had two (known problem 5). A full cold
request has not been re-timed, so the total is unknown rather than known-and-bad. Warm is still **0.0s**.
It is also blocked on item 3 — publishing a URL whose two highest-volume corridors return no checklist is
publishing the demonstration rather than the product — and item 1 changes what a cold request does, so
deploying first means deploying twice. **Item 5 adds a reason of its own:** answering challenges needs
Chromium on the host (~150MB plus system libraries) and costs ~7s per rendered page, which the deployment
notes currently assume away with `render_mode: never`.

### What changed on 2026-08-19, in one line each

| Entry | What it changed |
| --- | --- |
| 41 | A Cloudflare challenge is not a refusal. France's `403` carries `cf-mitigated: challenge` and is served for `robots.txt` too, so no policy was ever stated; the project's own renderer reads the page under our own user agent. A challenge becomes its own outcome, may be answered by the renderer, and may never resolve a corridor. `robots.txt` stays obeyed everywhere and outranks it. Spoofing and retrying stay forbidden. **Decided, not implemented.** |

Known problem 18 was found the same day and taught the same lesson — a 6,000-character excerpt deciding
corridors by where a nationality falls in an alphabetical list — and became entry 42 on 2026-08-21.

### What changed on 2026-08-23, in one line each

Item 22 was written as a proposal and read as one. The measurements behind it held; two of the three
things built on them did not.

| Entry | What it changed |
| --- | --- |
| 58 | **The twenty-corridor measurement ran, and it passes the bar committed in advance** — 75% confirm the decision (bar 70%), 50% yield a checklist (bar 50%, *exactly*). 40 live runs, all corpus-routed, none crawled, median 27.4s. **Read the sample structure**: nationality changed the outcome once in twenty, so it is five destinations replicated four times, not twenty independent corridors. **The United Kingdom refuses all eight runs** after finding the checklist, route, times and per-nationality fees, because `gov.uk/check-uk-visa` is a **wizard** — France's cause without France's `403`. That inverts known problem 11: the wizard costs more coverage than bot-blocks. |
| 57 | **A block is now judged, not keyword-matched.** `_decision_blocking` asked "could this page have held the visa decision?" and answered by keyword, on a page **nobody read** — the one place the scorer decided what a page *means*. It now asks the model, over **address and label only** (there is no text; the authority refused it), and the packet has no parameter through which content could be passed. Fails closed after two attempts; the deterministic path keeps the keyword test. **France now qualifies `/en/royaume-uni`, `/en/web/france-visas` and `/india` and rejects the FAQ, the form page and the visa-category page** — where its old qualification was a blank CERFA form. Corridors whose decision is found make **no extra call**. |
| 56 | **The `visa_decision` vocabulary could only ask the question, never recognise the answer.** Every term was a way of asking — `visa requirement`, `do i need a visa` — so Sweden's `list-of-foreign-citizens-who-require-visa-for-entry-into-sweden` scored `general_entry` 22.4 and `visa_decision` **0.0**, and could not qualify its own refusal. Seven answering phrasings added, one in **slug form** because `searchable_url` flattens hyphens and slugs drop articles. Measured by replaying all seven corridors' real candidate sets: **0.0 → 82.4 and it now qualifies; no shortlist changes anywhere.** **Item 23's own proposal — removing the `not scores` guard — was measured and rejected**: it would give 12–58% of a country's pages a positive `visa_decision`. |
| 55 | **Six corridors through the corpus path, 24 live runs — 2.1×–5.2× faster, and two of them stopped resolving.** Crawl 0.0s everywhere; roles genuinely found are neutral to better (US gained `fees`, the Netherlands `processing_times`). **Sweden and France flipped resolve → refuse**: reporting survived (entry 49 works — the blocked hosts and URLs are still named) but *qualification* did not, because `_decision_blocking` needs a refusal observed on a page scoring for `visa_decision` and a 25-page fetch observes far fewer refusals than a crawl. France is a **correction** (its baseline qualified on a blank CERFA form); **Sweden is a real loss**. Root cause is a scoring rule — TODO item 23, deliberately not fixed here. Also: Japan's corpus holds **1 of its 6** role pages and no London embassy, and it resolved anyway **because search still runs**. |
| 54 | **One encrypted PDF aborted a whole corridor.** `pypdf`'s `DependencyError` extends `Exception` directly — not `PdfReadError`, not `PyPdfError` — so no narrowing of the old `except` tuple could have caught it. `extract_pdf_text` is now total: every input yields text or "could not be read". Latent all along; a corpus-built shortlist is what reached it. |
| 53 | **Run live, four times, and the first run refused.** `entry-requirements-country.html` — the only page that states Canada's rule for a British citizen in static text — entered at **32.0** from search's title instead of **63.4** from the corpus's harvested anchor text, missed the shortlist, and was never read. `_resolve` seeded search first and folded the corpus in with `setdefault`, so the *thinner* description of a page always won; **the crawl had been repairing that on every run**, which is why removing it was what exposed it. Fixed, then three consecutive runs resolved. **Crawl 33.6s → 0.00s; total 54.2s → 12.7–13.2s**, with adjudication now ~60% of the corridor. |
| 52 | **Entry 47's pin only half existed.** A page that already filled a role "keeps its shortlist place regardless of ranking" — it kept it as far as `chosen`, and `_shortlist` then cut the tail by score protecting only the per-domain reservation, so a **low-scoring pin was dropped**, which is the only pin that matters. Found while verifying entry 50's own claim on the real Canada corpus. Pins and reservations are both honoured at the truncation now, pins first. The existing pin tests missed it because they pin a page that scores well. |
| 51 | **The crawl leaves the request path** for a country whose corpus offers more pages than a crawl could visit — a *derived* bound (`DEFAULT_CRAWL_PAGES`, 40), not another tuned constant, and the skip is recorded in the notes. A country nobody has built, or one with a thin corpus, behaves exactly as before. Also closed: `visa-discover corridor` now reads the corpus, so a measurement taken through the command finally describes the product; pins are still withheld, because they would let run one decide run two's shortlist. `_readable_only` does **not** fall back to corpus status — item 22 proposed it, and it would have stopped a France-shaped corridor resolving. |
| 50 | **The routing index is not built, because it removes the wrong cost.** Entry 48's ~3.6s is `wrong_country`, not scoring: 198 countries scanned per candidate, the link's segments and text rebuilt once per country, a fresh regex per token. A word-index prefilter in front of the existing exact check made it **3,277ms → 98ms, byte-identical on all 3,216 entries**, and the whole corpus → candidates path **4,757ms → 346ms** — under the 575ms the top-400 was meant to cost. And the top-400 would have dropped a `proven` page ranked 2,871 of 3,216, which a pin could not have rescued. |
| 49 | **A refusal met while reading the shortlist was never reported at all.** `_fetch_bodies` discarded `report.failures`, so every refusal a corridor has ever reported came from the crawl. Fixed before the crawl could go, with `SourceFailure.http_status` so a `429` can be told from a `403` without parsing prose (entry 36's rule). Two tests refuse only to the retrieval user agent, so the crawl never sees it; both fail on the old code. |

### What changed on 2026-08-21, in one line each

| Entry | What it changed |
| --- | --- |
| 42 | The adjudicator's excerpt stops being a flat head slice. It is the head plus a 3,000-character window centred on every later mention of the traveller's own nationality or residence, to 20,000 characters, with omissions marked `[…]` and prompt rule 12 explaining the mark. Short country words ("US", "UK") match in upper case only. **Confirmed live**: Canada now fills `visa_decision` from a sentence at offset 8,597, which the old 6,000 could not show. Six corridors left to re-run (item 15). |
| 48 | Measured where a cold corridor's 54.2s goes: **crawl 33.6s (62%)**, search 9.1s, adjudicate 10.8s. Of 25 shortlisted pages, 14 came from the crawl and **all 14 were already in the corpus** — it spent 62% of the corridor re-deriving a map the offline job had. Corpus-only keeps all three role-filling pages, **non-circularly** (they came from the offline job, not write-back), so it needs the *destination* built rather than the *corridor* proven. Consuming the whole corpus costs 3.6s and grows, so it becomes a **routing index**: a stored corridor-independent score, pre-filtered to the top 400 — 575ms, 24/25, bounded. **Decided, not implemented — and deliberately left open to challenge.** TODO item 22. **Challenged and partly overturned on 2026-08-23: entries 50 and 51.** The phase split and the fourteen-of-fourteen redundancy held; the routing index did not. |
| 47 | The candidate set **ratchets**: `corpus ∪ live`, pinned by pages that already filled a role, fed by additive write-back. Measured — the purpose sweep alone did **not** close entry 46's gap, because search did not return the page for the *same query* that once surfaced it, so no offline sweep can guarantee a superset; write-back did, taking Canada to **24 of 24** fetched pages held. Offline, a total search failure now loses **zero** candidates. |
| 46 | Entry 44's store is built — `discovery/corpus.py`, `corpus_build.py`, `visa-discover corpus`. Canada holds **1,071 pages**, the additive merge kept every entry across two builds, and `entry-requirements-country.html` is durable at depth 1. **But the corpus is not a superset of what a corridor finds**: `supporting-documents`, fetched by the corridor run the same day, is absent, because traveller-free queries lose what corridor-specific ones surface. That gates item 19 — corpus-only today would trade variance for less coverage. |
| 45 | `visa-discover corridor` reaches a registry destination instead of answering *"Unknown destination"*, and `--runs N` resolves a corridor repeatedly and reports what varied — item 17's counting is now one command. Building it made the test suite perform a **live** corridor resolution (21s, real searches, a real model call), because `run_corridor` had no seam and the rule against it was convention only; `tests/conftest.py` now refuses `socket.connect` for every test, and it caught the offending call on its first run. |
| 44 | The candidate set stops being re-derived from search on every request: a country's **page corpus** is persisted, populated by an offline job, and search leaves the request path for a populated country. Entry 34's move one level down — *which pages exist* does not vary by corridor; only which one answers a given traveller does. A corpus miss **refuses and flags the country**, per entry 38, rather than falling back to live search. Answers TODO item 17 as option 3, widened from per corridor to per country. Fixes **recall only** — adjudication is still a model call, and a page the job never finds becomes a permanent gap. **Decided, not implemented.** |
| 43 | Every run writes down what it considered — all candidates with their scores, the shortlist and fetch flags, the queries, the seeds, and each unreadable URL — to `var/recall/`, on refusals too. It exists because "ranked out" and "never found" had looked identical twice, and it answered that question about Canada on its first run: rank 15 of **470**, and simply absent from the run before. A diagnostic nothing reads back; deleting it costs a question, never an answer. |

### What changed on 2026-08-18, in one line each

Seven entries from one outside review, agreed with in full, plus five more (36–40) that came out of
building them. **Everything is implemented except two of entry 35's three legitimacy steps** — asking
authorities for access, and the client-side retrieval question, which is deliberately unargued. Read them
in [DECISIONS.md](DECISIONS.md).

| Entry | What it changed |
| --- | --- |
| 29 | LangGraph is not adopted and the question is closed: no cycle to express, trust checkpoints are typed validators rather than graph nodes, and the only loop the placeholder imagined is one this project rejects. `domain/state.py` and the dependency are deleted. |
| 30 | `conflicts` is deleted. Entry 6 removed a *working* conflict detector for being too alarming when wrong; the unverified version is the same feature without the verification. |
| 31 | A failed adjudication refuses rather than falling back to the heuristic. Entry 16 chose the fallback thinking it conservative; it silently swaps in the decider entry 15 proved gives confident wrong answers. |
| 32 | A block may hand over a link only when it plausibly held the answer. `429` stops qualifying, and the blocked URL must have been a credible `visa_decision` candidate. Narrows entry 27, which behaves more broadly than it claims. |
| 33 | Measured: `is_own_government` fails for 19 of 51 countries, all on `looks_governmental`, not the TLD half. Amend through reviewed data, never a wider regex. Schengen is additionally a definition problem. |
| 34 | "Who to believe" leaves the request path and becomes a committed registry a person skims once. Not the gate entry 19 removed — that was URLs; this is ~3 domains per country, machine-proposed. |
| 35 | The posture is honest client, not anonymous client: read `robots.txt`, ask for access, and decide the client-side-retrieval question explicitly. Plus the bar that decides whether this is a product, committed before the measurement. |
| 36 | `robots.txt` is read once per origin and obeyed, by the crawl and by retrieval. A skip is the `disallowed` outcome, never an absence; it is reported but may never resolve a corridor; and an unread policy is never reported as a policy that refused us. |
| 37 | A per-run allowance may not be counted on an object that outlives the run. The render budget was process-lifetime, so rendering switched itself off after a handful of pages and never came back. |
| 38 | The trusted-domain registry is generated offline and committed; `bootstrap_destination` leaves the request path. Reviewing it found twelve countries confirmed *and wrong*, and the cap spending slots on the wrong parts of a government. |
| 39 | A person may override the trust rule in committed data, with required evidence, preserved across regeneration. Twelve countries corrected. Measured: they help but do not make a corridor resolve — the binding constraint moved to confirming the visa decision. |
| 40 | The shortlist is a recall budget, not a precision one. Ten places made the heuristic the effective decider; at 25, Canada and Japan resolve completely. One constant outperformed every scoring rule, at no measurable latency cost. |

### What changed on 2026-08-17, in one line each

Seven entries were added to [DECISIONS.md](DECISIONS.md) that day; read them there rather than here.

| Entry | What it changed |
| --- | --- |
| 22 | A large government's whole namespace passed the trust rule, so how many domains may be used is now bounded at five and the relaxed evidence bar is scoped. Fixed the US coin flip. |
| 23 | A checklist-less corridor could not produce a plan at all, because the extractor refused before entry 14's validator could run. Vietnam would have hit the same wall. |
| 24 | Five of the US corridor's ten fetch places went to pages already proved unreadable. Three recovered; DNS-dead and refused URLs are now skipped, nothing else is. |
| 25 | The politeness delay was owed to a host but applied to the whole crawl. Now per host, hosts crawled concurrently, searches four at a time: 54.5s → 19.4s. |
| 26 | France's India post outranked its UK post for a UK applicant, and footer boilerplate took three fetch places. Two scoring defects, both fixed. |
| 27 | A blocked authority can now carry a plan: named, linked, never read, with the decision forced to unknown. **Unverified live.** |
| 28 | Four things found by reading the rendered page: a truncated step heading, a corridor that cannot have an answer, an empty checklist panel, caveats burying the answer. |

### Answered, for background

Seven corridors have run live. The model decider refuses well under pressure and its judgement beats
the scorer's where it can read at all: for China it picked the UK embassy checklist because that page
names the required passport, photo and UK legal-stay evidence for non-British applicants, noticing the
traveller is an Indian national resident in the UK, which no lexicon keyword expresses.

**Never work around a block** (entry 18) is settled and unchanged. No user-agent spoofing, no
pointing the renderer at a `403`, no retrying past a rate limit. What entry 27 added is narrower than
it may sound: the page may now be **named** with its URL so the traveller can open it themselves. It
still may not be read, inferred from, or counted as a source.

**What entry 35 changes about that, precisely, because it is easy to misread.** Entry 18 is untouched:
it forbids *deception*, and every example above stays forbidden. What entry 35 rejects is a separate
belief that had attached itself to entry 18 — that being an anonymous, unauthenticated client is
therefore required. Honouring `robots.txt` is submitting to an authority's stated policy, not routing
around it; asking for access is asking. **Anything that involves this program presenting itself as
something it is not remains out of the question**, and the client-side-retrieval idea is explicitly *not
approved* — it is written down so it gets argued rather than drifted into.

**The first step is now shipped (entry 36), and it added a rule of its own.** A `Disallow` is obeyed and
*reported*, and it may **never** resolve a corridor: `disallowed_urls()` sits outside `blocked_urls()` and
`persistent_refusals()`, so it reaches neither `inaccessible_urls` nor `decision_blocking_urls`. A `403`
was observed on the page; a `Disallow` covers a path we chose not to request. And the reason reported must
be true of what was seen — a policy that could not be read is not a policy that refused us, which is the
same falsehood entry 33 removed from `withheld_domains`.

## Next steps

[TODO.md](TODO.md) is the ordered list and the reasoning; this is its shape.

**First: [TODO.md](TODO.md) item 3** — the twenty-corridor measurement. It decides whether this is a
product, Brave credit has been available since 2026-08-21, and after item 22 nothing large is queued
ahead of it. **Carry item 22's unpaid last step with it**: instrument one run's phase split the way
entry 48 did, because ~21s is still a projection and no live corridor has resolved through the
corpus-routed path. Run each corridor **twice** — one run cannot tell a corridor that works from one
that works half the time. See *Current task*.

**Then: [TODO.md](TODO.md) items 17, 18, 19, 15 and 5** — count the flip rate, run the offline corpus
job on the rest of item 3's destinations, decay live *search* the way the crawl has already gone, finish
re-running the corridors, then treat France's challenge as a challenge. Item 17's decision is made
(entry 44); what is left of it is the counting, which is cheap now that the recall log exists. Item 19
is now half done — entry 51 took the crawl out of the request path, and what remains there is search.
Items 15 and 18 need credit; 17, 19 and 5 do not, and Canada's own refusal reason named 5.

**On sequencing against item 3, because it is a fair objection.** Entry 35 commits that nothing large
ships before the 20-corridor measurement, and a corpus is large. The reconciliation is that item 18 is
built once and run first on only the ~8 destinations item 3 needs, so the measurement describes the
architecture the project intends to keep; scaling to 198 countries afterwards needs no rework. **That
argument is now spent, not open-ended:** item 22 was the last thing taken ahead of item 3 on it.

**Then the pre-existing list, in this order.** Each of these costs something — a crawl policy, a
198-country registry, or search quota. Bulleted rather than numbered, because the numbers that matter
are the TODO item numbers on each line.

- **Fix the post-over-nationality weighting**, and trace why Sweden does not move. Reproducible, written
  up under *Current task*, and it decides what every corridor reads. Entries 39 and 40. TODO item 1.
- **Measure the top 20 corridors against the bar committed in advance** — product if ≥70% confirm the
  decision and ≥50% yield a checklist. **No longer blocked: Brave credit arrived on 2026-08-21.** It
  decides the project's direction, so nothing large should be built before it. Fold in the France
  read-through, which needs the same credit and is still the one shipped change never run live.
  TODO item 3.
- **Amend the trust rule** for the governments with no hostname marker, for the twelve confirmed-and-wrong
  countries entry 38 found, and for Schengen. **The measurement it was waiting on is done** — entry 38's
  table names the countries and the domains, so this is now a data edit against a committed file rather
  than a regex change. `gv.at`, `canada.ca`, `esteri.it`, `government.nl`, `sef.pt`, `irishimmigration.ie`
  are the concrete cases. Fix the cap's alphabetical tie-break at the same time: India spends two of five
  slots on United States missions. TODO item 2.
- **Decide the client-side retrieval question** in writing, either way (entry 35 raises it and explicitly
  does not approve it). TODO item 4.
- **Then deploy**, precompute popular corridors, and put a key or a rate limit on `POST /visa-plans`.
  TODO item 7.
- Standing work: confirm a blocked authority reads usefully (item 8 — the plumbing turned out to already
  exist, see known problem 7); tell "no checklist exists" apart from "we failed to find it" (item 9); try
  sitemaps before crawling (item 10); decide whether a host that refused everything may be skipped
  (item 11); watch where the two deciders disagree (item 12); revisit conflict detection with claim scope
  recorded (item 13); detect drift in configured sources (item 14).

---

## Working agreements

- **Update this file at the end of a session**, particularly *Current state*, *Current task* and
  *Known problems*. A stale handoff is worse than none, because it is believed.
- **Record decisions in [DECISIONS.md](DECISIONS.md) as they are made**, with the reasoning and what
  was rejected. The reasoning is the part that cannot be recovered from the code later.
- Before handing off, run `ruff check .`, `ruff format --check .`, `mypy`, `pytest`.
- Contributor rules, including the safety boundaries, are in [AGENTS.md](AGENTS.md).

## Running it

```bash
python3.12 -m venv .venv && .venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env          # then add OPENAI_API_KEY and SEARCH_API_KEY
.venv/bin/uvicorn visa_research_agent.api.app:create_app --factory
```

Secrets live only in `.env`, which is gitignored. Reviewable policy — source mode, extraction mode,
cache TTL, stale ceiling — lives in `config/runtime.yaml` and is committed on purpose.

### Looking at a corridor, which is not obvious

Most of 2026-08-17's findings came from inspecting a corridor directly, and the way in is worth
writing down because the CLI does not offer it.

- **`visa-discover bootstrap --destination-name "United States"`** prints the proposed domains with
  their corroboration counts and hostname hints, and writes nothing. Four search queries. This is how
  the trusted set is checked before blaming ranking for anything.
- **`visa-discover corridor --destination france …` only works where `destinations.yaml` already
  lists `trusted_domains`.** For an unconfigured destination it exits 3, so it cannot exercise the
  automatic path — which is the path a request actually takes. Use
  `api.dependencies.build_automatic_destinations(get_runtime_policy())` and call
  `destination_for(country_name, corridor)`; about twenty lines, and it skips the plan call.
- **To see the shortlist** — 25 places since entry 40, and where the wasted budget, the boilerplate and
  the wrong post were all found — wrap `CorridorResolver._shortlist`, print each candidate's score, role,
  link text, inherited heading and `link_scores.signals`, and return the list unchanged. Nothing else
  exposes it. Wrapping `_fetch_bodies` instead also shows which of them were *readable*, which is how
  the Netherlands' 250-character signpost was found (entry 39).
- **To time a cold corridor by phase**, wrap `BraveSearchProvider.search`, `CrawlFetcher.fetch_html`,
  `LinkCrawler.crawl`, `_fetch_bodies` and `_decide_roles` with a timer. Note that summed fetch time
  now exceeds wall-clock crawl time, which is what concurrency looks like.
- **Clear `var/cache/` and `var/corridors/` between cold runs**, or a stored corridor answers
  instantly and a retrieval fix appears not to work.
- **A `HTTP 402` from search means the Brave quota is spent**, not that anything is broken. It is what
  stopped the France run on 2026-08-17.
