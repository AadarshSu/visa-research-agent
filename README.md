# Visa Research Agent

Generates bounded, source-backed visa application plans for any traveller and any of 198
destinations. It reports what official government sources say, cites every claim, and states
plainly what it could not verify. It does not guarantee eligibility, completeness, or visa
approval, and it never submits anything on anyone's behalf.

> **Picking the project up?** Start with [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) — current state,
> open problems and what is next. Then [ARCHITECTURE.md](ARCHITECTURE.md) for how it is built,
> [DECISIONS.md](DECISIONS.md) for why, and [TODO.md](TODO.md) for what remains. This README covers
> what the application does and how to run it.

## Current status

Phase 2 now provides the first end-to-end destination with offline sources and switchable
extraction:

- strict domain and configuration models;
- a traveller described by the request — passport, country applied from, purpose;
- a country-specific destination registry with verified Singapore official-source URLs;
- saved, paraphrased Singapore source snapshots dated 6 August 2026;
- deterministic fixture extraction for free, repeatable development;
- optional one-call OpenAI extraction through LangChain structured output;
- a unified, source-linked visa-application document checklist;
- a working Singapore `POST /visa-plans` response;
- optional live retrieval of the configured official pages, with a hash and TTL cache;
- per-destination domain trust, enforced when configuration loads and after every redirect;
- PDF retrieval, including following the forwarding pages authorities hide checklists behind;
- graceful degradation: a run reports which sources failed instead of collapsing;
- a small Jinja and vanilla JavaScript research interface;
- fully offline tests and CI checks.

A destination nobody has configured is **researched when it is asked for**: its own government's
domains are identified, the corridor resolved, and the plan built from what was found. A corridor
that cannot be established says so rather than guessing. France is the standing example: its visa
portal refuses automated retrieval, so the plan states the visa decision as *unknown*, names the
portal and links to it, and lists no documents it could not read.

Conflict detection across sources remains intentionally deferred, and the unverified `conflicts` field
was deleted rather than kept — see [DECISIONS.md](DECISIONS.md) entries 6 and 30. **LangGraph is
not deferred but declined:** the pipeline is linear, and the trust checks are typed validators that
cannot be skipped rather than graph nodes that could be reordered (entry 29).

**A known coverage limit, measured 2026-08-18:** a destination is researchable only when its government
publishes under a hostname this agent recognises as governmental (`gov`, `go.xx`, `gouv.xx`, and a few
more). **19 of 51 countries checked do not** — Germany, Italy, the Netherlands, Sweden and Canada among
them — so they refuse rather than answer. Being fixed through reviewed per-country data; see entry 33.

### Source discovery

Adding a country used to mean hand-searching for its official pages. `visa-discover` does that
instead, for a specific traveller:

```bash
visa-discover bootstrap --destination-name Brazil        # propose official domains to approve
visa-discover corridor --destination japan --nationality IN --from GB --purpose tourism
```

The correct pages depend on the **corridor** — destination, passport nationality, and the country
applied from — because authorities publish per-nationality pages and route applicants to the mission
serving where they live. There are far too many corridors to curate by hand, which is why this is
automated and per-country trust is not.

**Search finds candidates; it never decides what may be believed.** Two gates, and only one is new:

- *Finding pages* for a configured country: results are restricted to approved domains by the
  `site:` operator and filtered again by `trusts_host`, so a commercial visa agency is discarded
  before anything is fetched.
- *Finding domains* for a new country: the only place search adds real risk. A domain is used only
  when it is the destination country's **own** government — governmental *and* under that country's
  own top-level domain. That rule replaced a human approval gate and reproduces every decision the
  human made; both halves are load-bearing. A denylist removes agencies first, a domain must appear
  in at least two independent queries, and bare public suffixes are rejected. If no such domain is
  found, nothing is fetched and the destination is refused.

Queries are built from templates and the corridor alone — never written by a model, never derived
from fetched page content — so a page cannot influence what is searched for next.

Bootstrap also checks that a proposed domain belongs to the **destination country**, using its own
top-level domain. "Looks governmental" is satisfied by any country's `.gov`, which is how the US
embassy in Vietnam initially outranked Vietnam's own immigration department; a foreign government's
page is still shown for review, but flagged and never first.

Discovery then crawls two hops from the best results, staying inside approved domains, because
search lands on a section index while the checklist is usually one link further on. Candidates are
scored deterministically, with **no model calls**; page selection is free. If no page can
confidently fill a load-bearing role, the corridor is refused with a diagnosis rather than filled
with a plausible substitute. One exception, and it is not a relaxation: when the reason nothing could
confirm the visa decision is that an authority *refused* automated retrieval, the plan is produced
with the decision stated as unknown and that authority named and linked, so the traveller gets the
one thing they can act on. The page is named, never read.

Two destinations are configured. Singapore works in either source mode. **Japan has no saved
snapshots and therefore requires `source_mode: live`**, because both its document checklist and its
eVisa terms are published only as PDFs, which the offline fixture path was never built for.

A disagreement between sources is reported as an unresolved question, which is what it honestly is:
nothing checks which pages differ or decides which one governs. There was a separate `conflicts` field
carrying the same prose under a heading that made it read as a finding; it was deleted (entry 30) by the
rule entry 6 recorded when it deleted the *checked* version — a feature whose wrong answers are alarming
needs a near-zero false-positive rate, or it should not ship.

### Deferred: structured conflict detection

A deterministic version was designed, built and deliberately removed. Recording it here so the same
ground is not covered twice.

**The approach.** Keep one model call, but change its job. Instead of describing conflicts, the
model reports what each source states about a few questions in a canonical form, with the wording it
read — for example `6_months_from_entry` versus `6_months_from_departure`, each with its excerpt.
The application then compares those answers, so a disagreement is found the same way every run and
can be checked against the quoted text. Where sources differ, precedence picks the governing answer:
a page written for this traveller's nationality first, then immigration authority over foreign
ministry over mission over appointed provider. A tie stays unresolved and downgrades the plan to
`partial`.

It worked on the real Singapore evidence: two ICA pages and an MFA page all require six months of
passport validity but measure it from entry, from departure, and from an unstated point, and the
nationality-specific ICA page correctly governed.

**Why it was dropped.**

- *Scope mismatch is the unsolved problem.* Two pages can look contradictory while describing
  different populations. A general page listing visa-free nationalities and a nationality-specific
  page requiring a visa are not in conflict, but nothing in the claim recorded who a statement
  applied to, so they compared as though they were. A false "sources disagree on whether you need a
  visa" is the most damaging thing this product could emit.
- *It cost output tokens on every run*, for every source and every question, to guard against a case
  that is rare.

**If it is revisited.** Record the population each claim applies to and compare only same-scope
claims; leave the visa decision itself out of the comparison, since it already has stronger guards
(declared required sources, mandatory citation, rejection of unknown citations); and restrict
comparison to quantitative rules such as validity periods, stay lengths and processing times, where
a wrong flag costs a caveat rather than alarm. Fees should be split per payee before being compared,
because a government visa fee and an appointed provider's service fee are different amounts rather
than a disagreement.

### Evidence status

Every source resolves to one outcome, and the plan is graded from them:

| Outcome | Evidence usable | Meaning |
| --- | --- | --- |
| `ok` | yes | Retrieved fresh, or cached inside the TTL, from a trusted domain |
| `stale` | yes | A refresh failed, so cached text was served inside the stale ceiling |
| `untrusted` | no | The final URL after redirects left the approved authority domains |
| `unreachable` | no | Timeout, connection error, or an error status |
| `unusable` | no | Retrieved but not evidence — a client-rendered shell or too little text |

Each destination declares `required_source_ids` — the sources a plan cannot stand without,
defaulting to the document checklist. From there:

- **all sources `ok`** → the plan is `verified`;
- **a non-required source failed, or any source is stale** → the plan is `partial`, and the
  interface states which evidence is incomplete above the guidance itself;
- **a required source failed** → the run is refused before any model call is made, and the API
  answers `503` naming the evidence it could not verify.

### Live retrieval

Setting `source_mode: live` in `config/runtime.yaml` fetches only the primary URLs already approved
in the destination registry. Retrieved HTML is reduced to bounded readable text, and every
retrieval is cached under `CACHE_DIRECTORY` with its content hash and HTTP validators:

- below `source_cache_ttl_hours`, cached text is reused without a request;
- above it, the page is revalidated with `If-None-Match` and `If-Modified-Since`, so an unchanged
  page costs one cheap `304`, and a changed content hash marks that the guidance moved;
- when a refresh fails, cached text is served flagged as stale and keeps its original retrieval
  time, so it can never appear freshly checked;
- once cached text passes `source_maximum_stale_hours`, the source is refused instead of served;
- a page yielding less than `MINIMUM_SOURCE_CHARACTERS` is refused rather than treated as
  evidence, which is what happens to client-rendered pages such as the appointed provider's.

Authorities frequently publish a checklist as a PDF behind a small HTML page that forwards to it,
so retrieval reads PDFs as well as HTML and follows such a forward to reach the real document. A
forward is treated exactly like a redirect: its target must be on an approved authority domain, or
the source is refused. Forwards are limited to two hops, and documents above
`MAXIMUM_SOURCE_BYTES` are refused rather than read.

### Domain trust

Officialness is treated as a property of who controls the domain, never of how a page reads, so a
convincing blog can never qualify. Each destination declares its own `trusted_domains`, and a host
matches on a dot boundary, so `london.mfa.gov.sg` sits under `mfa.gov.sg` while `notmfa.gov.sg`
does not. Listing a bare public suffix such as `gov.sg` is rejected outright, because it would
trust every site beneath it — that guard is rule-based and should be reviewed as countries are
added.

Appointed providers such as VFS are not government domains and cannot pass domain trust. They are
authorised only by naming the official page that appoints them, and that page must itself be a
configured source.

Trust is checked twice: when configuration loads, so a mistake in review never reaches a research
run, and again on the final URL after redirects, so a page that redirects off the approved domains
is refused rather than quoted as official guidance.

## Requirements

- Python 3.12 or newer
- An OpenAI API key is **not** required for deterministic fixture extraction or for tests

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

Run the API:

```bash
uvicorn visa_research_agent.api.app:app --reload
```

Open the research interface at <http://127.0.0.1:8000/>. The API documentation is available at
<http://127.0.0.1:8000/docs>.

Run the quality checks:

```bash
ruff check .
ruff format --check .
mypy
pytest
```

## API

- `GET /health` reports application health.
- `GET /destinations` lists the four configured destinations and their implementation status.
- `POST /visa-plans` generates the validated Singapore fixture plan and rejects unsupported or
  not-yet-implemented destinations clearly.

Example request:

```json
{
  "destination": "singapore"
}
```

The source timestamp in the response is the saved snapshot time, not the current time. Fixture
source mode deliberately avoids presenting saved evidence as newly retrieved research.

## Configuration

The personal traveller settings are deliberately isolated in
`src/visa_research_agent/config/traveller.py`. Do not add passport numbers or other sensitive
identity data.

All destinations and official starting URLs live in
`src/visa_research_agent/config/destinations.yaml`. France is modelled as its own Schengen member
route so additional countries can be introduced without a generic, inaccurate “Schengen” route.

The saved Singapore evidence and deterministic output template live under
`src/visa_research_agent/fixtures/singapore/`. The source text is paraphrased, treated as untrusted
evidence, and never allowed to control application behaviour.

### Runtime policy and secrets

Configuration is split by what it is, not by convenience:

| Where | Holds | Why |
| --- | --- | --- |
| `src/visa_research_agent/config/runtime.yaml` (committed) | source mode, extraction mode, cache TTL, stale ceiling | These decide whether government sites are contacted, whether a paid model is called, and when stale guidance is refused, so they belong under review |
| `.env` (never committed) | `OPENAI_API_KEY`, `OPENAI_MODEL`, cache directory, retrieval timeouts and limits | Secrets and machine-local tuning |

Keep the fully deterministic path for development and tests:

```yaml
source_mode: fixtures
extraction_mode: fixture
```

To let a model interpret the same saved sources, set `extraction_mode: openai` in `runtime.yaml`
and put the credentials in `.env`:

```dotenv
OPENAI_API_KEY=your-local-secret
OPENAI_MODEL=gpt-5.6-terra
```

OpenAI extraction makes one structured request with no automatic retries. The model cannot browse
or choose new sources. Application code attaches trusted URLs and timestamps after extraction and
rejects unknown citations. Each destination config identifies which official sources can support
its application-document checklist without fixing a document count or assigning categories. The
model extracts a unified checklist from those sources, and the application removes items supported
only by general entry sources. It also returns a structured application timeline: each step has an
action, timing window, citations and an official link where the evidence provides one. Unsupported
account, collection or document-return details remain unresolved rather than being invented. The
inspectable model instructions are in
`src/visa_research_agent/prompts/extract_visa_plan.txt`.

`plan.yaml` remains the deterministic fixture output and golden expected result. OpenAI mode does
not load it when generating a plan. Tests force fixture extraction even when a developer's local
`.env` enables OpenAI mode. API usage may incur charges.

Runtime cache files will live under `var/cache/`. The directory contents are disposable and
ignored by Git.
