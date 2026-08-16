# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-15 — update this line when you touch the handoff |
| **Tests** | 213 passing, 1 skipped (needs a browser, opt-in); `ruff` and `mypy --strict` clean |
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

**Working end to end.** Two destinations produce real plans from live government sources.

| | Singapore | Japan | Vietnam | Brazil |
| --- | --- | --- | --- | --- |
| Configured sources | 6 | 7 | none (discovery test case) | none (discovery test case) |
| Offline snapshots | yes | no | no | no |
| Live retrieval | works | works | works, with rendering on | works |
| Discovery finds the right pages | yes | yes | resolves; no checklist exists | yes |

All four verified live on 2026-08-16 with `discovery_decider: model`. Brazil was the out-of-sample
test: keyword ranking failed it silently, and the last step now asks a model instead — see
[DECISIONS.md](DECISIONS.md) entries 15 and 16.

Runtime mode is `source_mode: live`, `extraction_mode: openai`, `render_mode: never`,
`discovery_decider: model` in `src/visa_research_agent/config/runtime.yaml`. `visa-discover` now
needs `OPENAI_API_KEY`; set `discovery_decider: heuristic` for the free, offline, deterministic
path, which is still tested and still the regression baseline. Japan only works live, because its checklist is a PDF
and there are no snapshots for it.

**Client-rendered pages can now be read**, but rendering is off in committed config. Turning it on
means `render_mode: on_demand` plus the optional extra:

```bash
.venv/bin/pip install -e ".[render]" && .venv/bin/playwright install chromium
```

Selecting `on_demand` without the extra raises rather than silently skipping rendering.

**The traveller profile is still fixed**: Indian ordinary passport, resident in the UK, tourism.
It lives in `config/traveller.py`. Making it variable is the next significant piece of work and is
a prerequisite for wiring discovery into request time.

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

1. **Nothing distinguishes "this country publishes no checklist" from "we failed to find it."**
   Both produce the same empty result, and since a missing checklist no longer refuses the corridor,
   a find-or-read failure now yields a plan with a visibly empty checklist rather than a refusal.
   The plan says so — `VisaPlan` enforces that — but nobody is told *which* case it is. If plans
   start shipping empty checklists for countries that do publish one, this is the cause; a
   per-country human declaration is the designed fix. See [DECISIONS.md](DECISIONS.md) entry 14.
2. **The heuristic decider still mis-ranks, and is still the fallback.** With
   `discovery_decider: model` the failing case is fixed, but a failed model call falls back to the
   heuristic, which picked a Riyadh page for a UK applicant before entry 15's fixes. Two fixes
   landed — a checklist is known by the documents it names, and the traveller's post governs — but
   both rest on English vocabulary and per-country city labels, so the fallback will keep degrading
   on new countries and languages.
3. **The model decider is non-deterministic and unverified beyond four corridors.** Its containment
   is tested; its *judgement* is evidenced by four corridors on one day. Re-run them after any
   prompt change, and read `decided_by` and the recorded heuristic score to see where the two
   deciders disagreed.
4. **Singapore's VFS page answers HTTP 403** — a bot-block, not a client-rendered page as this file
   previously recorded. Rendering does not apply to it: the render only runs after a `200` whose
   text was thin, and a `403` never gets that far.
5. **Scoring is English-only.** A destination publishing solely in its own language will score near
   zero and refuse. Now visible in practice: rendering `xuatnhapcanh.gov.vn` yields 9,327
   characters of Vietnamese, which scores nothing.
6. **`xuatnhapcanh.gov.vn/en` is broken server-side.** It answers `200` with a
   `location: http://localhost:4000/vi` header and an empty body — a misconfigured Next.js i18n
   redirect. Browsers ignore `Location` on a `200`, so **rendering does not fix this one either**;
   it renders to 0 characters. The site root works; only the `/en` path is broken.
7. **An authority's own outdated microsite is undetectable** — right domain, live, linked,
   text-rich, so every check passes.
8. **Mission detection only works when a mission has its own subdomain**, and does nothing at all
   for a consolidated portal. `_mission_domains` returns `[]` for Brazil, whose every mission sits
   on `www.gov.br` with the post in the *path* — so Riyadh and Atlanta outrank Edinburgh for a UK
   applicant. It also misses Singapore's `london.mfa.gov.sg`, which is named by city rather than
   country code. Recorded here as latent; Brazil proved it changes the answer.
9. **`conflicts` on a plan is unverified free text** written by the model. Nothing checks it. The
   structured replacement was built and deliberately removed — see [DECISIONS.md](DECISIONS.md).
10. **The retrieval cache is not re-validated against changed rules.** After changing what counts as
   usable, cached entries still serve the old result until their TTL expires. Clear `var/cache/`
   when testing a retrieval change, or a fix will appear not to work.

---

## Current task

**None — the ranking question is answered.** Brazil showed keyword scoring does not generalise
(entry 15); the last step now asks a model, bounded so it cannot introduce a page, widen trust, or
be anchored by the ranking that failed (entry 16). All four corridors verified live.

Pick up from *Next steps*. The most valuable open item is telling "no checklist exists" apart from
"we failed to find it", which is known problem 1 and is now the largest silent-failure risk left.

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
