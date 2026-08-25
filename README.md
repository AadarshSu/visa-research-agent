# Visa Research Agent

Generates bounded, source-backed visa application plans for any traveller and any destination whose
government domains have been confirmed. It reports what official government sources say, cites every
claim, and states plainly what it could not verify. It does not guarantee eligibility, completeness, or
visa approval, and it never submits anything on anyone's behalf.

**53 of 198 countries are currently *reachable*.** Which domains a country may be researched from is
generated offline, reviewed once, and committed in `config/authority_domains.yaml`; a country absent from
it is refused rather than guessed at. The file holds **55 rows**; Iceland and Liechtenstein carry no
domain that could be confirmed, so they refuse too.

**Reachable is not the same as working**, and the difference is deliberate (`DECISIONS.md` entry 68).
The registry grows **in batches**, and a batch is done at four stages — *reachable*, then *resolves*,
then *accurate against a truth set*, then *fast from a stored corpus*. No further country is added until
the current batch clears all four. Batch 1 is the EU and EEA and is at stage 1. See
`visa-discover registry --only` and `visa-discover audit`.

> **Picking the project up?** Start with [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) — current state,
> open problems and what is next. Then [ARCHITECTURE.md](ARCHITECTURE.md) for how it is built,
> [DECISIONS.md](DECISIONS.md) for why, and [TODO.md](TODO.md) for what remains. This README covers
> what the application does and how to run it.

## Current status

Working end to end for any traveller and any destination it can reach, with **automatic source
discovery in the request path** — nobody curates URLs. What it does today:

- **finds its own sources.** A destination nobody configured is researched when it is asked for: its
  government's domains are read from the committed registry, the corridor is resolved, and the plan is
  built from what was found. Seven corridors verified live;
- **obeys each host's stated crawl policy.** `robots.txt` is read once per origin and honoured, matching
  RFC 9309 rather than `urllib`, which supports no wildcards. A page skipped for it is recorded as
  skipped, never as nothing found;
- **trusts a domain, never a page.** Per-destination domain trust, enforced when configuration loads,
  after every redirect, and after every meta-refresh forward;
- **takes the traveller from the request** — passport, country applied from, purpose, with residence
  and permit expiry optional;
- **reads documents, not just pages:** PDF retrieval, including the forwarding pages authorities hide
  checklists behind, and optional headless rendering for client-side pages (off by default);
- **asks a model exactly twice** — once to choose which fetched page fills each role, once to extract
  the plan — with a deterministic offline path that needs no key and stays the regression baseline;
- **degrades honestly.** Every source resolves to a typed outcome, a plan is `verified` or `partial`,
  and a missing load-bearing source refuses the run before the model is called;
- a small Jinja and vanilla JavaScript research interface, and fully offline tests and CI checks.

**Not deployed yet.** The question of whether this is a product was settled against a bar committed in
advance (DECISIONS entry 35) and measured on 2026-08-24 over twenty high-volume corridors, run twice
each: **75% confirm the visa decision** against a ≥70% bar and **50% yield a document checklist**
against a ≥50% bar. It passes, by one corridor on the first number and by nothing at all on the second.
Read entry 58 with it — the sample is five destinations replicated across four nationalities rather than
twenty independent corridors.

**What that measurement found matters more than the verdict.** Every United Kingdom corridor refused
after successfully finding the checklist, the application route, the processing times and
per-nationality fees, because `gov.uk/check-uk-visa` is a step-by-step wizard: the page is served
willingly, fetched and read, and simply does not state the answer. An interactive tool costs more
coverage than bot-blocking does. **All four United Kingdom corridors resolve as of 2026-08-24** — the
plan hands over the checker rather than refusing, and the shortlist now reserves enough places per
question for the checker to reach the model at all.

**So a page that *asks* a question is now its own outcome** (entries 59 and 60). A questionnaire is
not an obstacle in front of the guidance — it is the guidance, in the form the authority published it.
Read successfully and judged to work an answer out from questions rather than state it, the page is
named for whatever it settles, and the plan offers it beside that question: the visa decision in the
decision panel, the document checklist in the documents panel, fees and processing times with the
caveats. The Netherlands, whose corridor refused for weeks because no page states whether a visa is
needed, now produces a plan with nine document requirements and a link to the nine-question checker
that holds the decision.

Naming a tool never fills the role it stands in for — a checklist questionnaire still leaves the plan
structurally unable to list a single document — and only the visa decision changes whether a corridor
resolves at all. Driving the questionnaire is deliberately not done: some of a checker's questions are
not part of a corridor, and answering them for a traveller would be inventing the input to the one
question where being wrong is most damaging.

**A caveat on timing**, because it is the number a deployment plan would want: the **corridor phase**
measures a median of **27.4s** (40 live runs, 2026-08-24, all served from stored page corpora rather
than crawling). Plan extraction sits on top and the two have never been timed together, so the full
cold request is still an unknown — the one 33.4s API request measured on 2026-08-24 was served from an
already-stored corridor, so it times extraction, not the whole path. Ignore 34.1s and 54.2s wherever they survive in these files.

**A corridor that cannot be established says so rather than guessing.** France is the standing
example: its visa portal refuses automated retrieval, so the plan states the visa decision as
*unknown*, names the portal and links to it, and lists no documents it could not read. The page is
named, never read — and only a page that plausibly held the answer can put a plan in that state, so a
rate limit or a refused footer link cannot.

Conflict detection across sources remains intentionally deferred, and the unverified `conflicts` field
was deleted rather than kept — see [DECISIONS.md](DECISIONS.md) entries 6 and 30. **LangGraph is
not deferred but declined:** the pipeline is linear, and the trust checks are typed validators that
cannot be skipped rather than graph nodes that could be reordered (entry 29).

**A known coverage limit, measured 2026-08-18:** a destination is researchable only when its government
publishes under a hostname this agent recognises as governmental (`gov`, `go.xx`, `gouv.xx`, and a few
more). **19 of 51 countries checked did not; 16 since 2026-08-25**, when the markers Austria, Uruguay
and Canada actually use were added (entry 65). Germany, Italy, the Netherlands and Sweden are among
those still refused by the rule alone. **A person may name the domain instead**, in the registry's
`reviewed` field with the evidence for it; twelve countries have been corrected that way. See entries
33, 39 and 65.

### Source discovery

Adding a country used to mean hand-searching for its official pages. `visa-discover` does that
instead, for a specific traveller:

```bash
visa-discover registry                                   # generate the committed domain registry
visa-discover registry --only FR,DE                      # rebuild just these, keeping the rest
visa-discover bootstrap --destination-name Brazil        # propose one country's domains, to read
visa-discover corridor --destination japan --nationality IN --from GB --purpose tourism
visa-discover audit var/recall/                          # why travellers go unanswered, counted
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
| `blocked` | no | The authority refused this client (`401`, `403`, `429`); its guidance could not be verified here |
| | | *Over-claims today: a `403` that is really a Cloudflare bot challenge is reported as a refusal, which is untrue of what was seen. Decided as [DECISIONS.md](DECISIONS.md) entry 41, unimplemented.* |
| `disallowed` | no | The host's `robots.txt` excluded this client, or could not be read, so the page was not requested |

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
