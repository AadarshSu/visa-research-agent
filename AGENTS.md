# Contributor instructions

## Start here

Read [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) before doing anything else. It is the source of truth
for where the project stands; a chat transcript is not. It links to
[ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md) and [TODO.md](TODO.md).

[CLAUDE.md](CLAUDE.md) carries the same pointers and the critical safety rules, for tools that load
it automatically at the start of a session.

Before finishing a session, update the handoff:

- **PROJECT_HANDOFF.md** — current state, current task, known problems. A stale handoff is worse
  than none, because it is believed.
- **DECISIONS.md** — any decision made, with the reasoning and what was rejected. The reasoning is
  the part that cannot be recovered from the code later.
- **TODO.md** — what is now next, and why.

Do not record a problem as fixed unless it is fixed, and do not describe a result as verified unless
it was run. These documents are read by someone with no other context.

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

