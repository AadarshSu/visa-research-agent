# Visa Research Agent

A personal learning project that will generate bounded, source-backed visa application plans for
one fixed traveller profile. The application reports what configured official sources say; it does
not guarantee eligibility, completeness, or visa approval.

## Current status

Phase 2 now provides the first end-to-end destination in offline fixture mode:

- strict domain and configuration models;
- the fixed traveller profile;
- a country-specific destination registry with verified Singapore official-source URLs;
- saved, paraphrased Singapore source snapshots dated 6 August 2026;
- deterministic structured extraction with no model or network calls;
- a working Singapore `POST /visa-plans` response;
- a small Jinja and vanilla JavaScript research interface;
- fully offline tests and CI checks.

Live retrieval, OpenAI-backed extraction, caching and LangGraph routing remain intentionally
deferred. Japan, the United States and France return a clear `503 Service Unavailable` response
until their later destination phases.

## Requirements

- Python 3.12 or newer
- An OpenAI API key is **not** required for fixture mode or for tests

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
mode deliberately demonstrates the complete product shape without presenting the result as live
research.

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

Runtime cache files will live under `var/cache/`. The directory contents are disposable and
ignored by Git.
