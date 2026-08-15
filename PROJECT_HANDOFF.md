# Visa Research Agent — Project Handoff

**Read this first when picking the project up.** It is the entry point for a new session and the
source of truth for where things stand. The chat is not the source of truth; this file is.

| | |
| --- | --- |
| **Repository** | `github.com/AadarshSu/visa-research-agent` |
| **Last updated** | 2026-08-15 — update this line when you touch the handoff |
| **Tests** | 157 passing; `ruff` and `mypy --strict` clean |
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

| | Singapore | Japan | Vietnam |
| --- | --- | --- | --- |
| Configured sources | 6 | 7 | none (discovery test case) |
| Offline snapshots | yes | no | no |
| Live retrieval | works | works | partly |
| Discovery finds the right pages | 2/2 roles | 2/2 roles | refuses, correctly |

Runtime mode is `source_mode: live`, `extraction_mode: openai` in
`src/visa_research_agent/config/runtime.yaml`. Japan only works live, because its checklist is a PDF
and there are no snapshots for it.

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

1. **JavaScript-only sites cannot be read at all.** Retrieval has no browser. Vietnam's e-visa
   portal and Singapore's VFS page are both unreadable for this reason. This blocks whole corridors
   and no amount of scoring works around it.
2. **Discovery's scoring is tuned against Singapore and Japan**, so their results are in-sample.
   Vietnam is held out but refuses for unrelated reasons, so *whether the ranking generalises is
   still unknown*. This is the biggest open question about discovery.
3. **Scoring is English-only.** A destination publishing solely in its own language will score near
   zero and refuse.
4. **An authority's own outdated microsite is undetectable** — right domain, live, linked,
   text-rich, so every check passes.
5. **Mission detection is country-code based**, so Singapore's London high commission
   (`london.mfa.gov.sg`, named by city) is not recognised as the mission serving a UK applicant.
6. **`conflicts` on a plan is unverified free text** written by the model. Nothing checks it. The
   structured replacement was built and deliberately removed — see [DECISIONS.md](DECISIONS.md).
7. **The retrieval cache is not re-validated against changed rules.** After changing what counts as
   usable, cached entries still serve the old result until their TTL expires. Clear `var/cache/`
   when testing a retrieval change, or a fix will appear not to work.

---

## Current task

**Reading JavaScript-rendered government sites** — known problem 1, and the largest coverage limit.
Whole corridors are unservable because the authority publishes a client-rendered page that retrieval
returns as empty. See the "Handle JavaScript-rendered sites" entry in [TODO.md](TODO.md), which
carries the measured character counts per site, both fetch paths that would need changing, and the
four questions to settle before building — including how it can be tested when tests may not touch
the network.

Nothing has been built for this yet. The first decision is whether a headless browser is worth its
weight at all; deciding *not* to is defensible and should be recorded either way.

### Also open

**Whether discovery's ranking generalises** beyond Singapore and Japan, which it was tuned against.
Vietnam was the held-out test and behaved correctly — it found the one readable Vietnamese official
page, classified it correctly, and refused the checklist rather than substituting something
plausible — but it refused because the portal is JavaScript-rendered, so it never exercised ranking.
A destination publishing readable HTML is still needed to answer this. Note the two threads are
related: fixing rendering would also let Vietnam finally test ranking.

---

## Next steps

In the order that makes sense. Detail and reasoning in [TODO.md](TODO.md).

1. **Decide on rendering JavaScript sites** — the current task above.
2. **Run a third country with readable HTML** — Thailand or Brazil. Outstanding validation, not a
   new feature.
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
