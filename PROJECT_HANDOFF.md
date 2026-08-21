# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-21 — update this line when you touch the handoff |
| **Tests** | 376 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean |
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

**Working end to end for any traveller and any of 198 destinations** — with one correction measured on
2026-08-18 that this line used to overstate. 198 destinations are *reachable*; **19 of 51 countries
checked cannot be researched at all**, because no domain of their government passes
`looks_governmental` (entry 33). Germany, Italy, the Netherlands, Sweden and Canada among them. They
refuse safely, with a message that misdescribes why.

Seven corridors verified live; the table below is what each one actually did.

**This table predates the registry (entry 38) and the wider shortlist (entry 40), and at least two rows
are now wrong.** Japan and Canada both fill every role at a 25-place shortlist where they previously left
the visa decision unfound. Treat it as the record of a 2026-08-16/17 run, not as current behaviour, until
the twenty-corridor measurement re-runs it.

**And "Canada fills every role" does not generalise — measured 2026-08-19.** `canada/GB/GB/tourism`
refused. Entry 40's row is consistent with an *Indian* passport, whose answer happened to fall inside the
adjudicator's then 6,000-character excerpt at offset 5,325, while a British citizen's sits at 8,858 and
was cut off. A corridor's fate depended on where the nationality fell in an alphabetical list.
**Nationality is part of a corridor; a country row in this table is not a result.**
The excerpt was widened and anchored on 2026-08-21 (entry 42) and that should now resolve, but **it has
not been re-run against the model** — [TODO.md](TODO.md) item 15 is exactly that run.

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
**truncation**. The excerpt now follows the traveller rather than the page (entry 42), which should
remove that corridor's cause; until item 15 re-runs it, treat "access" as an incomplete diagnosis.

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
11. **Bot-blocked official portals are the largest coverage limit — but "permanent" was the wrong
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
   omissions with `[…]` (entry 42). **What has not:** nobody has run a corridor through the model since.
   The replay that proved the cause predates the fix, and the fix is evidenced by cached pages and tests
   only. This item comes off the list when [TODO.md](TODO.md) item 15 has run it.

---

## Current task

**Updated 2026-08-21. Of the two corridors investigated on 2026-08-19, one fix has landed and one has
not.** `canada/GB/GB/tourism` refused because the adjudicator's 6,000-character excerpt cut off the page
that answers it; the excerpt now follows the traveller — head plus a window around every later mention of
their own country, at 20,000 characters, with omissions marked (entry 42, known problem 18). **It has
never been run against the model**, which is why [TODO.md](TODO.md) item 15 leads the list: this changed
what every adjudication sees, so it is a decider change and unmeasured until a corridor is run.

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

**Amended 2026-08-21: the excerpt item is done and the two that lead now are a run and a fix.** Pick up
**[TODO.md](TODO.md) items 15 and 5 first**:

- **Item 15 — re-run the verified corridors against the widened excerpt.** The change is on `main`,
  evidenced offline only, and it changes what every adjudication sees. Needs search and model credit.
  Known problem 18, entry 42.
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

### What changed on 2026-08-21, in one line each

| Entry | What it changed |
| --- | --- |
| 42 | The adjudicator's excerpt stops being a flat head slice. It is the head plus a 3,000-character window centred on every later mention of the traveller's own nationality or residence, to 20,000 characters, with omissions marked `[…]` and prompt rule 12 explaining the mark. Short country words ("US", "UK") match in upper case only. **Implemented and tested offline; not yet run live** — item 15. |

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

**First: [TODO.md](TODO.md) items 15 and 5** — confirm the widened excerpt against real corridors, then
treat France's challenge as a challenge. Item 15 needs credit; item 5 does not. See *Current task* above.

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
