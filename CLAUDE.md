# Visa Research Agent

Bounded, source-backed visa research. Every claim must be grounded in an official government source,
and the traveller must be told plainly when something could not be verified.

## Read these first

This file is loaded automatically; the documents below are not. **Read them before starting work.**

| File | What it holds |
| --- | --- |
| [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) | **Start here.** Current state, known problems, current task, next steps |
| [ARCHITECTURE.md](ARCHITECTURE.md) | How it is built — trust model, pipeline, retrieval, discovery |
| [DECISIONS.md](DECISIONS.md) | Why it is built that way, including what was tried and rejected |
| [TODO.md](TODO.md) | What remains, ordered, with the reasoning for each |
| [AGENTS.md](AGENTS.md) | Full contributor rules |

## Rules that must not be broken

These are repeated here because they are the ones where a plausible-looking "simplification"
produces a serious defect.

- **Officialness is a property of who controls the domain, never of how a page reads.** Enforced
  when configuration loads, after every HTTP redirect, and after every meta-refresh forward. A
  change to retrieval must preserve all three.
- **Never disable TLS verification.** Incomplete certificate chains are fixed by bundling the
  missing intermediate in `config/tls_intermediates/`, each verified to chain to an already-trusted
  root. An attacker able to impersonate an immigration authority could dictate what documents a
  traveller brings.
- **Refusing is a correct output.** A plausible but wrong document checklist is worse than no
  answer. Prefer refusing with a diagnosis over substituting something that looks right.
- **Web search belongs only in `discovery/`, and only as a candidate generator.** Nothing search
  returns becomes evidence until it passes the domain-trust rules.
- **A domain is trusted automatically only when it is the destination's *own* government** —
  governmental **and** under that country's own top-level domain. No human approves domains any
  more, but the rule they were applying still runs, and both halves are load-bearing: without the
  first, a commercial insurer under `.fr` gets in; without the second, the US embassy's page about
  Vietnam does. Never relax it to "looks official". If no such domain is found, nothing is fetched
  and the destination is refused.
- **Never work around an authority that blocks automated retrieval.** France's visa portal and
  Singapore's VFS page answer `403` to anything that is not a browser. Do not spoof a user agent,
  do not point the renderer at them, do not retry to get around a rate limit. A block is not
  evidence that the guidance is wrong or missing — it means *we cannot independently retrieve and
  verify it in this execution environment*, which is a narrower claim and the only honest one.
  Mark the source inaccessible, say so, and let the role go unfilled. Never substitute plausibility
  for evidence. This costs real coverage — France is unservable — and that is the correct trade for
  a product whose wrong answers send someone to a visa centre without the right papers.
- **Never** add application submission, appointment booking, form filling, or any claim that
  approval is guaranteed.
- **Tests must not touch the network or an LLM.** Use the `transport=` and `now=` seams and the fake
  generators; see `tests/discovery_site.py`.

## Before finishing a session

Run `ruff check .`, `ruff format --check .`, `mypy`, `pytest`, then update the handoff:
current state and known problems in `PROJECT_HANDOFF.md`, any decision and its reasoning in
`DECISIONS.md`, and what is now next in `TODO.md`.

Do not record a problem as fixed unless it is fixed, or a result as verified unless it was run.
These files are read by someone with no other context.

## Running it

```bash
.venv/bin/uvicorn visa_research_agent.api.app:create_app --factory   # the app
.venv/bin/visa-discover corridor --destination japan --nationality IN --from GB
```

Secrets (`OPENAI_API_KEY`, `SEARCH_API_KEY`) live only in `.env`. Reviewable policy — source mode,
extraction mode, cache TTL, stale ceiling — is committed in `config/runtime.yaml`.

Clear `var/cache/` when testing a retrieval change, or a fix will appear not to work.
