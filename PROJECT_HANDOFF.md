# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-18 — update this line when you touch the handoff |
| **Tests** | 341 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean |
| **Companion docs** | [ARCHITECTURE.md](ARCHITECTURE.md) · [DECISIONS.md](DECISIONS.md) · [TODO.md](TODO.md) · [README.md](README.md) |
| **Agent entry point** | [CLAUDE.md](CLAUDE.md) is loaded automatically and points back here |

---

## Goal

Produce visa application plans for a traveller where **every claim is grounded in an official
government source**, and the traveller is told plainly when something could not be verified.

The headline production goal — **automatic source discovery**, finding the right official pages for
a traveller and destination with nobody curating URLs — is **done and running in the request path**,
and a cold request now costs 34s rather than 71s.

**The direction changed on 2026-08-18**, after an outside review that was agreed with in full and is
recorded as [DECISIONS.md](DECISIONS.md) entries 29–35, plus entry 36 which came out of implementing one
of them. Nothing in it weakens the grounding principle. What it changes is the diagnosis of why coverage is
poor, and it found three things shipping that this project's own rules argue against. **Implemented: 36,
33, 32, 31, 30 and 29. Not: 34, and two of entry 35's three steps** — and [TODO.md](TODO.md) is the rest in
order. The three sentences worth carrying:

- **The blocker is the posture, not the principle.** "Grounded in an official page" and "grounded only in
  what an anonymous Python client can fetch" were treated as one commitment. Entry 18 forbids
  *deception*, not *legitimacy* (entry 35). The first step is shipped: `robots.txt` is now read once per
  origin and obeyed, by the crawl and by retrieval (entry 36). It is expected to *cost* coverage, and
  nothing has been run live since, so it has not been measured.
- **The trust rule's governmental half fails closed for a fifth of the world**, measured: 19 of 51
  countries, including Germany, Italy, the Netherlands, Sweden and Canada (entry 33). Known problem 2 had
  been warning about the other half.
- **Whether this is a product is now a measurement with a bar committed in advance** — top 20 corridors
  by volume, product if ≥70% confirm the decision and ≥50% yield a checklist (entry 35). Blocked on
  search credit, and nothing large should be built before it.

Deliberately out of scope, permanently: submitting applications, booking appointments, filling
forms, or claiming an approval is guaranteed. **Also settled: LangGraph is not adopted** — the pipeline
is linear, the trust checkpoints are typed validators rather than graph nodes, and the one loop the old
placeholder imagined is a retry loop this project rejects (entry 29).

---

## Current state

**Working end to end for any traveller and any of 198 destinations** — with one correction measured on
2026-08-18 that this line used to overstate. 198 destinations are *reachable*; **19 of 51 countries
checked cannot be researched at all**, because no domain of their government passes
`looks_governmental` (entry 33). Germany, Italy, the Netherlands, Sweden and Canada among them. They
refuse safely, with a message that misdescribes why.

Seven corridors verified live; the table below is what each one actually did.

| | Singapore | Japan | Vietnam | Brazil | France | China | United States |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Configured sources | 6 | 7 | none | none | none | none | none |
| Offline snapshots | yes | no | no | no | no | no | no |
| Live retrieval | works | works | needs rendering | works | **portal 403** | works | works |
| Visa decision | found | found | found | found | **unverified — blocked** | not confirmed | found |
| Checklist found | yes | yes | none published | yes | no — blocked | yes | no — blocked |
| Plan produced | yes | yes | no — rendering | yes | expected, **untested live** | no | yes, `partial` |

Read the France and China columns carefully, because they are not the same failure. China's decision
was **not confirmed** from readable pages, so that corridor still refuses. France's is unverified
because an authority refused us, which is the case entry 27 now turns into a plan that says so.

France was re-examined on 2026-08-17 because `france/IN/GB/tourism` is a common corridor to refuse —
entries 26 and 27. **It no longer refuses**: a corridor whose only missing piece is behind a block now
resolves, with the visa decision stated as *unknown* rather than guessed, the blocked authority named
with its URL, and the plan marked `partial`. **That is untested live** — known problem 4.

The underlying fact is unchanged, and it is why the decision cannot be stated: France publishes the
visa decision only on `france-visas.gouv.fr`, which answers 403, and every readable French government
page delegates to it rather than saying it. Two real scoring defects turned up on the way and are
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
Corridor ──▶ search ──▶ crawl ──▶ fetch shortlist ──▶ score ──▶ ResolvedCorridor
             (Brave)   (2 hops)   (via LiveSourceFetcher)       or a refusal
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

Ordered by how much they limit the product. **None of these are secretly fixed; they are all live.**
Several carry a *decision* (entries 29–35), and a decision is not a fix — items 3 and 4 below are decided
and still unimplemented. Three were **removed** on 2026-08-18 because they are genuinely fixed: a block resolving a corridor
it had nothing to do with (entry 32), the unverified `conflicts` field (entry 30), and a failed model
call silently substituting the heuristic (entry 31).

1. **Whether this is a product is genuinely unmeasured.** Two of the highest-volume corridors there are,
   India→US and India→France, yield a plan with **no document checklist**, because the pages holding the
   answer are bot-blocked. Seven corridors cannot say whether that is the rule or the exception, and the
   sample was chosen partly for being easy. Entry 35 commits a bar in advance — top 20 corridors by
   volume, product if ≥70% confirm the decision and ≥50% yield a checklist — precisely so the answer
   cannot be rationalised after the fact. Blocked on Brave credit. **Nothing large should be built before
   this runs.**
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
5. **A cold request takes 34 seconds, synchronously** — 19.4s corridor and 14.7s plan, inside one
   `POST` (entry 25 brought this down from 70.7s). It now fits a typical 30–60s proxy timeout, but not
   comfortably, and what remains is two model calls plus search latency, so it varies with someone
   else's load rather than with anything here. Warm is instant, and the local `var/` stores are what
   make it warm — an ephemeral container would make every request cold.
6. **A destination is trusted on a rule, with no human in the loop, and the audit behind it was
   survivorship.** The rule reproduces all 22 recorded human decisions, but every country in that audit
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
9. **The heuristic decider still mis-ranks.** With `discovery_decider: model` the failing case is
   fixed. Two fixes landed — a checklist is known by the documents it names, and the traveller's post
   governs — but both rest on English vocabulary and per-country city labels, so it will keep degrading
   on new countries and languages. **It is no longer the fallback** (entry 31), but it still matters,
   because it builds the shortlist the model chooses from: a page it ranks out of the ten fetch places
   is one the model never sees. It also remains the offline regression baseline.
10. **The model decider is non-deterministic and evidenced by six corridors on one day.** Its
   containment is tested with a fake; its *judgement* is not something tests can pin. Re-run the
   six after any prompt change, and read `decided_by` and the recorded heuristic score to see where
   the two deciders disagreed.
11. **Bot-blocked official portals are the largest coverage limit — but "permanent" was the wrong
   word.** Three found: `france-visas.gouv.fr`, `www.france-visas.gouv.fr` and Singapore's VFS page.
   France is the clearest case, quantified in entry 26: **every** readable French government page
   delegates the visa decision to the blocked portal, so no amount of better ranking can confirm it.
   Working around a block stays forbidden by entry 18 and by `CLAUDE.md`, and nothing about that has
   changed. What entry 35 corrects is the conclusion drawn from it: the loss is permanent *given an
   anonymous, unauthenticated client*, and that posture was never itself decided. Honouring
   `robots.txt` — **now read and obeyed** (entry 36) — asking for access, and the open
   client-side-retrieval question are all legitimacy rather than circumvention. Until item 3's twenty
   corridors are run against that posture, the size of this limit is unknown rather than
   known-and-accepted. Note the new posture can only *widen* this problem before it narrows it: a
   `Disallow` previously walked past is now a refusal, and nothing has been run live since.
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

---

## Current task

Nothing is half-finished in the working tree and every check is clean. The 2026-08-18 review was agreed
with in full, recorded as entries 29–35, and turned into an ordered list in [TODO.md](TODO.md). **Five of
its seven entries are now implemented, and nothing is left shipping against the project's own rules.**

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
- **`robots.txt` is read and obeyed** (entry 36) — `research/robots.py`, one policy per origin with a
  24-hour expiry, consulted by `discovery/crawl.py` before every page and by `research/live_sources.py`
  before every source and every meta-refresh forward. 19 tests, all offline. A skip is the new `disallowed` outcome
  and gets its own corridor note, so it can never read as "nothing found"; it is reported and may never
  resolve a corridor. **Expected to cost coverage and not yet measured** — nothing has been run against
  a real authority since, which is why TODO item 3's twenty corridors matter more, not less.

**Four findings came out of doing the work, all recorded rather than left in the diff. The pattern in
them is worth carrying: each was a claim that turned out to be wrong when finally tested or run.**

1. **The 19 unreachable countries are two different failures**, and the second is worse (entry 33's
   table). Nine have no marked domain at all and refuse outright with a misleading message. **Ten do have
   one** — `interno.gov.it`, `gov.ie`, `gob.cl`, `cic.gc.ca` — so bootstrap *succeeds* and builds a trusted
   set that cannot contain the visa guidance, and **nothing measures that**. Canada is sharpest: `gc.ca`
   still passes, but immigration content moved to `canada.ca`. The reasons now describe it where the
   ministry was seen at all; measuring it properly is part of TODO item 1.
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

**Everything that needed no credit is now done, and nothing is shipping against the project's own
rules.** `robots.txt` was the last of those (entry 36); what remains all costs something — a
198-country registry, search quota, or a decision nobody has argued yet — so pick up
[TODO.md](TODO.md) item 1 and work down:

1. **The committed domain registry** (entry 34), then **2. the trust-rule amendment** for the 19
   governments with no hostname marker and for Schengen. Item 2's own next step is a measurement: how
   many of the 19 are covered by a published government domain list, registry organisation data, or a
   TLS certificate organisation — which decides whether it is automatable or genuinely needs a human.
3. **The 20-corridor measurement against the committed bar** — **blocked on Brave credit**, and the
   thing that decides whether this is a product. Nothing large should be built before it. It now has a
   posture worth measuring: `robots.txt` landed first on purpose.

**Deployment has moved down the list deliberately.** It is not blocked on speed — a cold request is
**34.1s** (19.4s corridor, 14.7s plan) where it was 70.7s, which fits an ordinary 30–60s proxy timeout,
and warm is **0.0s**. It is blocked on item 3: publishing a URL whose two highest-volume corridors return
no checklist is publishing the demonstration rather than the product. Item 1 also changes what a cold
request does, so deploying first means deploying twice.

### What changed on 2026-08-18, in one line each

Seven entries, from one outside review, agreed with in full, plus entry 36 which came out of
implementing one of them. **Entries 36, 33, 32, 31, 30 and 29 are implemented; 34 is not, and 35 is one
of three steps in.** Read them in [DECISIONS.md](DECISIONS.md).

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

[TODO.md](TODO.md) is the ordered list and the reasoning; this is its shape. **Everything that needed no
credit is done**, so each remaining item costs something — a crawl policy, a 198-country registry, or
search quota.

1. **Move "who to believe" into committed data** — generate the country → trusted-domains registry offline
   for all 198 countries, commit it, skim it once (entry 34). Not the gate entry 19 removed: that was URLs,
   which stay automated. TODO item 1.
2. **Amend the trust rule** for the 19 governments with no hostname marker, and for Schengen. **Its own
   first step is a measurement**, because "a reviewed authority domain" would otherwise mean hand-curating
   198 countries — the manual work the production goal exists to remove: check how many of the 19 are
   covered by a published government domain list, by registry organisation data, or by a TLS certificate
   organisation field. If most are, this stays automatable; if not, the review is 19 countries rather than
   198. TODO item 2.
3. **Measure the top 20 corridors against the bar committed in advance** — product if ≥70% confirm the
   decision and ≥50% yield a checklist. **Blocked on Brave credit**, and the thing that decides the
   project's direction, so nothing large should be built before it. Fold in the France read-through, which
   needs the same credit and is still the one shipped change never run live. TODO item 3.
4. **Decide the client-side retrieval question** in writing, either way (entry 35 raises it and explicitly
   does not approve it). TODO item 4.
6. **Then deploy**, precompute popular corridors, and put a key or a rate limit on `POST /visa-plans`.
7. Standing work: confirm a blocked authority reads usefully (the plumbing turned out to already exist —
   see known problem 7); tell "no checklist exists" apart from "we failed to find it"; decide whether a
   host that refused everything may be skipped; try sitemaps before crawling; revisit conflict detection
   with claim scope recorded.

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
- **To see the ten fetch places** — where the wasted budget, the boilerplate and the wrong post were
  all found — wrap `CorridorResolver._shortlist`, print each candidate's score, role, link text,
  inherited heading and `link_scores.signals`, and return the list unchanged. Nothing else exposes it.
- **To time a cold corridor by phase**, wrap `BraveSearchProvider.search`, `CrawlFetcher.fetch_html`,
  `LinkCrawler.crawl`, `_fetch_bodies` and `_decide_roles` with a timer. Note that summed fetch time
  now exceeds wall-clock crawl time, which is what concurrency looks like.
- **Clear `var/cache/` and `var/corridors/` between cold runs**, or a stored corridor answers
  instantly and a retrieval fix appears not to work.
- **A `HTTP 402` from search means the Brave quota is spent**, not that anything is broken. It is what
  stopped the France run on 2026-08-17.
