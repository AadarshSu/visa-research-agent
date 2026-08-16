# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-15 — update this line when you touch the handoff |
| **Tests** | 245 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean |
| **Companion docs** | [ARCHITECTURE.md](ARCHITECTURE.md) · [DECISIONS.md](DECISIONS.md) · [TODO.md](TODO.md) · [README.md](README.md) |
| **Agent entry point** | [CLAUDE.md](CLAUDE.md) is loaded automatically and points back here |

---

## Goal

Produce visa application plans for a traveller where **every claim is grounded in an official
government source**, and the traveller is told plainly when something could not be verified.

The headline production goal is **automatic source discovery**: finding the right official pages for
a given traveller and destination without a human curating URLs. Hand-configuring sources is the
bottleneck that stops the product working across countries, and removing it is the point of the
current work.

Deliberately out of scope, permanently: submitting applications, booking appointments, filling
forms, or claiming an approval is guaranteed.

---

## Current state

**Working end to end for any traveller and any of 198 destinations.** Six corridors verified live;
the table below is what each one actually did.

| | Singapore | Japan | Vietnam | Brazil | France | China |
| --- | --- | --- | --- | --- | --- | --- |
| Configured sources | 6 | 7 | none | none | none | none |
| Offline snapshots | yes | no | no | no | no | no |
| Live retrieval | works | works | needs rendering | works | **403 bot-blocked** | works |
| Discovery exit code | 0 | 0 | 1 | 0 | **2** | **2** |
| Checklist found | yes | yes | none published | yes | no — site unreadable | yes |

All six verified live on 2026-08-16 with `discovery_decider: model`. Brazil was the out-of-sample
test that broke keyword ranking, so the last step now asks a model — entries 15 and 16. France and
China were the confirmation runs, and both **refuse correctly**: entry 17.

**The limit has moved from ranking to access.** Of six corridors, none now fails because a page was
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

Discovery sits *before* this, offline, and produces the `DestinationConfig` that the pipeline
consumes:

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

1. **The own-government rule collapses for a country whose own TLD is `gov`.** For everyone else
   "governmental" and "under its own ccTLD" are independent tests; for the United States they are
   the same test, so any federal agency is trusted as a visa authority. This is the current task
   above. Do not fix it by naming the US — the defect is the shape of the rule.
2. **A destination is now trusted on a rule, with no human in the loop.** The rule reproduces all
   22 recorded human decisions, but it has only ever been checked against six countries. A country
   whose government publishes outside its own TLD would resolve to nothing; one whose TLD hosts a
   convincing government-shaped domain it does not control would be a genuine hole. Watch the
   `withheld_domains` on resolved corridors for domains being declined that should not be.
3. **Nothing distinguishes "this country publishes no checklist" from "we failed to find it."**
   Both produce the same empty result, and since a missing checklist no longer refuses the corridor,
   a find-or-read failure now yields a plan with a visibly empty checklist rather than a refusal.
   The plan says so — `VisaPlan` enforces that — but nobody is told *which* case it is. If plans
   start shipping empty checklists for countries that do publish one, this is the cause; a
   per-country human declaration is the designed fix. See [DECISIONS.md](DECISIONS.md) entry 14.
4. **The heuristic decider still mis-ranks, and is still the fallback.** With
   `discovery_decider: model` the failing case is fixed, but a failed model call falls back to the
   heuristic, which picked a Riyadh page for a UK applicant before entry 15's fixes. Two fixes
   landed — a checklist is known by the documents it names, and the traveller's post governs — but
   both rest on English vocabulary and per-country city labels, so the fallback will keep degrading
   on new countries and languages.
5. **The model decider is non-deterministic and evidenced by six corridors on one day.** Its
   containment is tested with a fake; its *judgement* is not something tests can pin. Re-run the
   six after any prompt change, and read `decided_by` and the recorded heuristic score to see where
   the two deciders disagreed.
6. **Bot-blocked official portals are the largest coverage limit, and will stay one.** Three found:
   `france-visas.gouv.fr` and `www.france-visas.gouv.fr` (which make France unservable) and
   Singapore's VFS page. This is **not** a bug to fix — working around a block is forbidden by
   [DECISIONS.md](DECISIONS.md) entry 18 and by the rules in `CLAUDE.md`. They now produce the
   `blocked` outcome and appear under `inaccessible_domains`, so a refusal reads as "we were not
   allowed to check" rather than "nothing found".
7. **Discovered pages still have no staleness check.** A CMS publication date is now read from the
   path and reported — to the adjudicator, which can weigh it against the page's text, and in the
   proposal for a human. But that is a *report*, not a check: it is deliberately not a veto,
   because two of China's correct picks carry dated paths and one is from 2013. Content-hash drift
   detection remains a TODO and covers configured sources only.
8. **Scoring is English-only.** A destination publishing solely in its own language will score near
   zero and refuse. Now visible in practice: rendering `xuatnhapcanh.gov.vn` yields 9,327
   characters of Vietnamese, which scores nothing.
9. **`xuatnhapcanh.gov.vn/en` is broken server-side.** It answers `200` with a
   `location: http://localhost:4000/vi` header and an empty body — a misconfigured Next.js i18n
   redirect. Browsers ignore `Location` on a `200`, so **rendering does not fix this one either**;
   it renders to 0 characters. The site root works; only the `/en` path is broken.
10. **An authority's own outdated microsite is undetectable** — right domain, live, linked,
   text-rich, so every check passes.
11. **Mission detection only works when a mission has its own subdomain**, and does nothing at all
   for a consolidated portal. `_mission_domains` returns `[]` for Brazil, whose every mission sits
   on `www.gov.br` with the post in the *path* — so Riyadh and Atlanta outrank Edinburgh for a UK
   applicant. It also misses Singapore's `london.mfa.gov.sg`, which is named by city rather than
   country code. Recorded here as latent; Brazil proved it changes the answer.
12. **`conflicts` on a plan is unverified free text** written by the model. Nothing checks it. The
   structured replacement was built and deliberately removed — see [DECISIONS.md](DECISIONS.md).
13. **The retrieval cache is not re-validated against changed rules.** After changing what counts as
   usable, cached entries still serve the old result until their TTL expires. Clear `var/cache/`
   when testing a retrieval change, or a fix will appear not to work.

---

## Current task

**The United States refuses a tourist visa for an Indian passport holder** — one of the highest
volume corridors there is. Top of [TODO.md](TODO.md), with the reproduction and diagnosis.

The short form: the own-government rule **degenerates for the US**, because its own TLD *is* `gov`,
so both halves of the rule collapse into one test and every federal agency is auto-trusted — the
Interior Department and the Federal Register were, alongside State and USCIS. Eight domains against
Brazil's one. The crawl and the ten-slot shortlist spread thin, and the outcome becomes a coin
flip: two consecutive runs of the identical corridor, one resolved, one refused. Compounding it,
`travel.state.gov` — the canonical B1/B2 page — answers `403`, which by entry 18 is left alone.

Readable correct pages do exist: `in.usembassy.gov/visas/` is the US mission *in India* and already
resolves as the traveller's own post. Discovery is losing evidence it has, not lacking it.

### Otherwise complete end to end Any traveller, any destination: the request
describes who is travelling, the destination is researched if nobody configured it, and the plan
cites what it found or says what it could not verify. Verified live on a corridor nobody had run —
Chinese passport, UAE resident, Brazil — which resolved to Brazil's visa waiver page for China,
where an Indian passport resolves to a VIVIS checklist.

What is left is hardening rather than building. The known problems below are ordered by how much
they limit it; the first three are the ones that would change an answer a traveller sees.

### Answered, for background
 Six corridors run live. The model
decider refuses well under pressure — France gave it ten fetched pages and it still declined both
load-bearing roles rather than guess — and its judgement is better than the scorer's where it can
read at all: for China it picked the UK embassy checklist because that page "names the required
passport, photo, **UK legal-stay evidence for non-British applicants**", noticing the traveller is
an Indian national resident in the UK, which no lexicon keyword expresses.

**That decision is now settled: never work around a block** (entry 18). No user-agent spoofing, no
pointing the renderer at a `403`, no retrying past a rate limit. A block is not evidence that the
guidance is wrong or missing — it means only *we cannot independently retrieve and verify it in
this execution environment*. The source is marked inaccessible, the role goes unfilled, and nothing
is inferred in its place. France is unservable as a result, and that is the accepted trade.

## Next steps

In the order that makes sense. Detail and reasoning in [TODO.md](TODO.md).

1. **Run a third country that actually publishes a checklist** — Thailand or Brazil. Now the only
   way to learn whether discovery's ranking generalises, since Vietnam turned out to have no
   checklist page to rank. This is the highest-value thing left.
3. **Make the traveller profile variable** — nationality, residence, purpose, duration as input.
   Everything in discovery is already corridor-aware; the profile is the last fixed piece.
4. **Wire discovery into request time**, behind caching, once the ranking is trusted.
5. **Revisit conflict detection**, with claim scope recorded — the specific reason it failed before.

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
