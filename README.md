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
- a small Jinja and vanilla JavaScript research interface;
- fully offline tests and CI checks.

Live government-page retrieval, caching and LangGraph routing remain intentionally deferred.
Japan, the United States and France return a clear `503 Service Unavailable` response until their
later destination phases.

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

### Extraction modes

Keep the fully deterministic path for development and tests:

```dotenv
SOURCE_MODE=fixtures
EXTRACTION_MODE=fixture
```

To let a model interpret the same saved sources, configure `.env` locally:

```dotenv
SOURCE_MODE=fixtures
EXTRACTION_MODE=openai
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
