# Visa Research Agent

A personal learning project that will generate bounded, source-backed visa application plans for
one fixed traveller profile. The application reports what configured official sources say; it does
not guarantee eligibility, completeness, or visa approval.

## Current status

Phase 2 now provides the first end-to-end destination with offline sources and switchable
extraction:

- strict domain and configuration models;
- the fixed traveller profile;
- a country-specific destination registry with verified Singapore official-source URLs;
- saved, paraphrased Singapore source snapshots dated 6 August 2026;
- deterministic fixture extraction for free, repeatable development;
- optional one-call OpenAI extraction through LangChain structured output;
- a unified, source-linked visa-application document checklist;
- a working Singapore `POST /visa-plans` response;
- optional live retrieval of the configured official pages, with a hash and TTL cache;
- per-destination domain trust, enforced when configuration loads and after every redirect;
- graceful degradation: a run reports which sources failed instead of collapsing;
- a small Jinja and vanilla JavaScript research interface;
- fully offline tests and CI checks.

Conflict detection across sources, automatic discovery of official sources, and LangGraph routing
remain intentionally deferred. Japan, the United States and France return a clear
`503 Service Unavailable` response until their later destination phases.

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
