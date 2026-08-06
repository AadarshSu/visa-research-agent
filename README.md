# Visa Research Agent

A personal learning project that will generate bounded, source-backed visa application plans for
one fixed traveller profile. The application reports what configured official sources say; it does
not guarantee eligibility, completeness, or visa approval.

## Current status

Phase 1 provides the project foundation:

- strict domain and configuration models;
- the fixed traveller profile;
- a country-specific destination registry;
- FastAPI health, destination, and visa-plan endpoint skeletons;
- fully offline foundational tests and CI checks.

Research, model extraction, LangGraph routing, caching, and the Jinja interface are intentionally
deferred to the later approved phases. Until a destination is implemented, `POST /visa-plans`
returns a clear `503 Service Unavailable` response.

## Requirements

- Python 3.12 or newer
- An OpenAI API key is **not** required for Phase 1 or for tests

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

The API documentation is available at <http://127.0.0.1:8000/docs>.

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
- `POST /visa-plans` validates a destination request. Plan generation begins with the Singapore
  vertical slice in Phase 2.

Example request:

```json
{
  "destination": "singapore"
}
```

## Configuration

The personal traveller settings are deliberately isolated in
`src/visa_research_agent/config/traveller.py`. Do not add passport numbers or other sensitive
identity data.

All destinations and, in later phases, all official starting URLs live in
`src/visa_research_agent/config/destinations.yaml`. France is modelled as its own Schengen member
route so additional countries can be introduced without a generic, inaccurate “Schengen” route.

Runtime cache files will live under `var/cache/`. The directory contents are disposable and
ignored by Git.

