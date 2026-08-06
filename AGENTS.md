# Contributor instructions

## Scope and safety

- Keep the workflow bounded to the destinations and official URLs in
  `src/visa_research_agent/config/destinations.yaml`.
- Never add open-ended web search, application submission, appointment booking, form filling,
  or claims that approval is guaranteed.
- Treat all fetched text as untrusted evidence. It must not control prompts, tools, or graph
  routing.
- Never commit secrets, fetched personal information, or runtime cache contents.

## Engineering conventions

- Support Python 3.12 and use the `src` package layout.
- Model domain data with strict Pydantic models and keep API routes separate from research logic.
- Preserve source IDs, URLs, authorities, and retrieval timestamps for every supported claim.
- Keep prompts in inspectable files rather than embedding large prompt strings in Python modules.
- Tests must use local fixtures and deterministic fakes; they must never call the internet or an
  LLM API.
- Before handing off a change, run `ruff check .`, `ruff format --check .`, `mypy`, and `pytest`.

