# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-17 — update this line when you touch the handoff |
| **Tests** | 290 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean |
| **Companion docs** | [ARCHITECTURE.md](ARCHITECTURE.md) · [DECISIONS.md](DECISIONS.md) · [TODO.md](TODO.md) · [README.md](README.md) |
| **Agent entry point** | [CLAUDE.md](CLAUDE.md) is loaded automatically and points back here |

---

## Goal

Produce visa application plans for a traveller where **every claim is grounded in an official
government source**, and the traveller is told plainly when something could not be verified.

The headline production goal — **automatic source discovery**, finding the right official pages for
a traveller and destination with nobody curating URLs — is **done and running in the request path**,
and a cold request now costs 34s rather than 71s. What remains is confirming one shipped change
against a live run, and hosting it; see [TODO.md](TODO.md).

Deliberately out of scope, permanently: submitting applications, booking appointments, filling
forms, or claiming an approval is guaranteed.

---

## Current state

**Working end to end for any traveller and any of 198 destinations.** Seven corridors verified live;
the table below is what each one actually did.

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
with its URL, and the plan marked `partial`. **That is untested live** — known problem 3.

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

Ordered by how much they limit the product. None of these are secretly fixed; they are all live.

1. **A cold request takes 34 seconds, synchronously** — 19.4s corridor and 14.7s plan, inside one
   `POST` (entry 25 brought this down from 70.7s). It now fits a typical 30–60s proxy timeout, but not
   comfortably, and what remains is two model calls plus search latency, so it varies with someone
   else's load rather than with anything here. Warm is instant, and the local `var/` stores are what
   make it warm — an ephemeral container would make every request cold.
2. **A destination is now trusted on a rule, with no human in the loop.** The rule reproduces all
   22 recorded human decisions, but it has only ever been checked against seven countries. A country
   whose government publishes outside its own TLD would resolve to nothing; one whose TLD hosts a
   convincing government-shaped domain it does not control would be a genuine hole. Watch the
   `withheld_domains` on resolved corridors for domains being declined that should not be — it now
   carries everything declined, including what the cap left out and what bootstrap rejected outright.
   **The cap (entry 22) is where a wrong call would show first:** at most five of a destination's own
   domains are used, ordered by the hostname's authority hint then corroboration, so a country whose
   guidance genuinely spans six or more of its own domains loses one, and that reason is the only
   warning. Five is calibrated against corridors run, not derived.
3. **The blocked-source plan has never been run live.** Entry 27 lets a corridor resolve when the
   only gap is behind a block, states the decision as unknown, and hands the traveller the URL. The
   chain is covered by tests, but the Brave API answered HTTP 402 (out of credit) before France could
   be re-run, so what a model actually writes for it is unverified — as is whether "Uncertain" reads
   as *we could not check* rather than *no visa needed*. First item to close in [TODO.md](TODO.md).
4. **A discovery-time block reaches the plan only when it blocked the *decision*.** Entry 27 carries
   the blocked authority into the plan when `decision_is_unverified`, which is what France needed.
   Where the decision *was* confirmed, the block still stops at discovery: the US plan says its
   checklist is absent without saying that `travel.state.gov` declined us, because the corridor
   resolved on `dhs.gov` and never set the flag. The traveller still misses the sentence they could
   act on, so the remaining work is to name blocked authorities whenever there are any, not only when
   they cost the decision.
5. **Nothing distinguishes "this country publishes no checklist" from "we failed to find it."**
   Both produce the same empty result, and since a missing checklist no longer refuses the corridor,
   a find-or-read failure now yields a plan with a visibly empty checklist rather than a refusal.
   The plan says so — `VisaPlan` enforces that — but nobody is told *which* case it is. If plans
   start shipping empty checklists for countries that do publish one, this is the cause; a
   per-country human declaration is the designed fix. See [DECISIONS.md](DECISIONS.md) entry 14.
6. **The heuristic decider still mis-ranks, and is still the fallback.** With
   `discovery_decider: model` the failing case is fixed, but a failed model call falls back to the
   heuristic, which picked a Riyadh page for a UK applicant before entry 15's fixes. Two fixes
   landed — a checklist is known by the documents it names, and the traveller's post governs — but
   both rest on English vocabulary and per-country city labels, so the fallback will keep degrading
   on new countries and languages.
7. **The model decider is non-deterministic and evidenced by six corridors on one day.** Its
   containment is tested with a fake; its *judgement* is not something tests can pin. Re-run the
   six after any prompt change, and read `decided_by` and the recorded heuristic score to see where
   the two deciders disagreed.
8. **Bot-blocked official portals are the largest coverage limit, and will stay one.** Three found:
   `france-visas.gouv.fr`, `www.france-visas.gouv.fr` and Singapore's VFS page. France is the clearest
   case, quantified in entry 26: **every** readable French government page delegates the visa decision
   to the blocked portal, so no amount of better ranking can confirm it. This is **not** a bug to fix
   — working around a block is forbidden by [DECISIONS.md](DECISIONS.md) entry 18 and by `CLAUDE.md`.
   What changed is the output rather than the limit: instead of refusing, such a corridor now produces
   a plan that states the decision as unknown and hands the traveller the URL (entry 27). The coverage
   loss is real and permanent — the guidance itself is still unread.
9. **Discovered pages still have no staleness check.** A CMS publication date is now read from the
   path and reported — to the adjudicator, which can weigh it against the page's text, and in the
   proposal for a human. But that is a *report*, not a check: it is deliberately not a veto,
   because two of China's correct picks carry dated paths and one is from 2013. Content-hash drift
   detection remains a TODO and covers configured sources only.
10. **Scoring is English-only.** A destination publishing solely in its own language will score near
   zero and refuse. Now visible in practice: rendering `xuatnhapcanh.gov.vn` yields 9,327
   characters of Vietnamese, which scores nothing.
11. **`xuatnhapcanh.gov.vn/en` is broken server-side.** It answers `200` with a
   `location: http://localhost:4000/vi` header and an empty body — a misconfigured Next.js i18n
   redirect. Browsers ignore `Location` on a `200`, so **rendering does not fix this one either**;
   it renders to 0 characters. The site root works; only the `/en` path is broken.
12. **An authority's own outdated microsite is undetectable** — right domain, live, linked,
   text-rich, so every check passes.
13. **Mission detection only works when a mission has its own subdomain**, and does nothing at all
   for a consolidated portal. `_mission_domains` returns `[]` for Brazil, whose every mission sits
   on `www.gov.br` with the post in the *path* — so Riyadh and Atlanta outrank Edinburgh for a UK
   applicant. It also misses Singapore's `london.mfa.gov.sg`, which is named by city rather than
   country code. Recorded here as latent; Brazil proved it changes the answer. **Broader than
   recorded:** `_mission_domains` reads `destination.sources`, and the automatic path builds a config
   with none, so it returns `[]` for **every** discovered destination regardless of how its missions
   are named. Mission detection survives there only through `mission_affinity`'s host-label check —
   which is what still recognises `in.usembassy.gov` as the post serving an Indian traveller.
14. **`conflicts` on a plan is unverified free text** written by the model. Nothing checks it. The
   structured replacement was built and deliberately removed — see [DECISIONS.md](DECISIONS.md).
15. **The retrieval cache is not re-validated against changed rules.** After changing what counts as
   usable, cached entries still serve the old result until their TTL expires. Clear `var/cache/`
   when testing a retrieval change, or a fix will appear not to work.

---

## Current task

Nothing is half-finished in the working tree, and every check is clean. Two things are outstanding,
in this order.

**1. One shipped change has never been run live, and it is the one most worth reading as a
traveller.** A corridor whose only missing piece is behind a block now resolves rather than refusing:
the plan states the visa decision as *unknown*, names the authority that refused us, and hands over
its URL (entry 27). Every link in that chain is covered by tests, and the page layout was checked by
driving the real renderer. **What has not happened is a live run**, because the Brave search API
answered `HTTP 402` — out of credit — before `france/IN/GB/tourism` could be re-run. So what a model
actually writes for France is unverified. First item in [TODO.md](TODO.md), with the three things to
judge that a test cannot.

**2. Nothing is deployed**, and speed no longer shapes that decision. A cold request is **34.1s**
(19.4s corridor, 14.7s plan) where it was 70.7s, which fits an ordinary 30–60s proxy timeout. The
same corridor warm is **0.0s**, so resolving popular corridors ahead of time is still worth shipping.
`var/cache/` and `var/corridors/` are local directories, so an ephemeral container makes every
request cold rather than just the first.

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

## Next steps

In the order that makes sense. Detail and reasoning in [TODO.md](TODO.md). The three that used to
head this list — run a country that publishes a checklist, make the traveller profile variable, wire
discovery into request time — are all done; see *Current state*.

1. **Run France live and read the plan as a traveller** — the one shipped change with no live run
   behind it. Needs Brave credit; the layout is already confirmed, so what is left is the model's own
   words and whether "Uncertain" reads as *we could not check* rather than *no visa needed*.
2. **Deploy it.** No longer shaped by speed — a cold request is 34.1s and fits an ordinary timeout.
   Resolving popular corridors ahead of time is still worth shipping.
3. **Tell "no checklist exists" apart from "we failed to find it."** The US now makes this concrete
   rather than hypothetical: its checklist is unfilled because a page is blocked, and that is a third
   case again.
4. **Name a blocked authority whenever there is one**, not only when it cost the decision. Entry 27
   covers the France shape; the US resolved its decision on `dhs.gov`, so its plan still never
   mentions that `travel.state.gov` refused us.
5. **Decide whether a host that refused every request may be skipped** — two US fetch places turn on
   it, and it is inductive, so measure before adopting.
6. **Revisit conflict detection**, with claim scope recorded — the specific reason it failed before.

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
