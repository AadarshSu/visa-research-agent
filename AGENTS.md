# Contributor instructions

## Scope and safety

- Keep a research run bounded to the destinations and official URLs in
  `src/visa_research_agent/config/destinations.yaml`. Generating a plan must never search the web.
- Web search is permitted only inside `visa_research_agent.discovery`, and only to generate
  candidates. A search result becomes usable evidence only after it passes the domain trust rules,
  so a page on an unapproved domain is never fetched, quoted, or shown. Discovery may narrow trust;
  it may never widen it. Adding a domain to `trusted_domains` stays a human decision.
- Never add application submission, appointment booking, form filling, or claims that approval is
  guaranteed.
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

