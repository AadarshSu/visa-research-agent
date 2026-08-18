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
  answer. Prefer refusing with a diagnosis over substituting something that looks right. This includes
  **failing model calls**: a failed role adjudication refuses the corridor rather than falling back to
  the heuristic, because the heuristic is the decider that produced Brazil's wrong checklist at full
  confidence (entries 15 and 31). "Degrade to a worse answer" is not the conservative option here.
- **Web search belongs only in `discovery/`, and only as a candidate generator.** Nothing search
  returns becomes evidence until it passes the domain-trust rules.
- **A domain is trusted automatically only when it is the destination's *own* government** —
  governmental **and** under that country's own top-level domain. No human approves domains any
  more, but the rule they were applying still runs, and both halves are load-bearing: without the
  first, a commercial insurer under `.fr` gets in; without the second, the US embassy's page about
  Vietnam does. Never relax it to "looks official". If no such domain is found, nothing is fetched
  and the destination is refused. **How many** may be used is also bounded — at most five, and the
  relaxed one-query evidence bar applies only where "own government" is two independent signals.
  A country whose own top-level domain *is* `gov` otherwise admits its whole federal namespace, and
  the cost lands on search count, crawl budget and the ten fetch places (entry 22).

  **Measured 2026-08-18: the governmental half fails for 19 of 51 countries** — Germany, Italy, the
  Netherlands, Sweden, Canada and most of Schengen have no governmental marker in their hostnames, so
  the whole government is refused (entry 33). **Do not fix this by widening `GOVERNMENT_PATTERNS`.**
  Adding `.de` or `.nl` would trust every commercial site in those countries, and for exactly these
  countries the own-TLD test is the only other signal. The fix is a reviewed authority domain per
  country in committed data (entry 34). Adding `gv`/`gub` as markers and `canada.ca` beside `gc.ca` are
  corrections *within* the rule and are fine.

  **Every reason in `withheld_domains` must be true.** Reading that list is the only mitigation known
  problem 2 offers, so a false reason defeats the safeguard rather than merely reading badly. A domain
  under the destination's own TLD with no recognised marker is *"could not be confirmed as an authority,
  and may be a real one"* — never *"not a government domain"*, which is false and was word-for-word what
  a commercial visa agency got (entry 33).
- **Never work around an authority that blocks automated retrieval.** France's visa portal and
  Singapore's VFS page answer `403` to anything that is not a browser. Do not spoof a user agent,
  do not point the renderer at them, do not retry to get around a rate limit. A block is not
  evidence that the guidance is wrong or missing — it means *we cannot independently retrieve and
  verify it in this execution environment*, which is a narrower claim and the only honest one.
  Mark the source inaccessible, say so, and let the role go unfilled. Never substitute plausibility
  for evidence, in a product whose wrong answers send someone to a visa centre without the right
  papers.

  **What is allowed, and is not a workaround: naming it.** A blocked page may be reported with its
  URL so the traveller can open it themselves, which is the one thing they can act on. The line is
  absolute — the page may be *named*, never *read*, inferred from, retried, or counted as a source.
  So `UnreadableAuthority` is deliberately not a `ConfiguredSource`, the research packet carries its
  URL and no text, and it is still checked against the approved domains, because nobody read it and
  the domain is the only thing vouching for it (entry 27).

  **And naming it must stay narrow (entry 32).** Only `401`/`403` may qualify a corridor — a `429` is a
  transient rate limit, and "try again later" is the honest advice. The blocked URL must also have been
  a credible `visa_decision` candidate: a `403` on a footer link is not grounds to declare the decision
  unverifiable. Without both bounds, corridors whose decision was merely *not found* — which must refuse
  — drift into presenting as authority-blocked, which resolves. Every block is still *reported*
  regardless; the bounds govern what may *resolve a corridor*.

  **The posture is honest client, not anonymous client (entry 35).** This rule forbids *deception* —
  spoofing, retrying, rendering past a refusal — and none of that has changed or will. It does not
  require being an anonymous, unauthenticated client, and treating those as the same thing was costing
  coverage under the banner of a rule that never demanded it. So: read and honour `robots.txt` (nothing
  here ever has), and asking an authority for access is ordinary. Client-side retrieval through the
  traveller's own browser is an **open question, explicitly not approved** — argue it in a decision
  entry before writing any code for it.
- **A visa decision that could not be confirmed must be `null`, and the application enforces that.**
  Not the prompt: a model asked for null returned `true` in testing. A wrong yes or no about whether
  someone needs a visa is the most damaging thing this can say, so `decision_is_unverified` overrides
  the model rather than trusting it, and such a plan can never be `verified` (entry 27).
- **Never** add application submission, appointment booking, form filling, or any claim that
  approval is guaranteed.
- **Never show a traveller an unverified claim that would alarm them if wrong.** The rule from entry 6,
  which deleted a *working* conflict detector: a feature whose wrong answers are alarming needs a
  near-zero false-positive rate or it should not ship. The `conflicts` field violated it and was deleted
  (entry 30); a disagreement between official pages is now an unresolved question. **Do not add it back.**
  If conflict detection returns, it records the population each claim applies to, compares only same-scope
  claims, and leaves the visa decision out.
- **LangGraph is declined, not deferred (entry 29).** The pipeline is linear, so there is no cycle to
  express, and the trust checks are Pydantic validators that cannot be skipped rather than graph nodes
  that could be reordered or bypassed. Do not reintroduce it or a `state.py`-style placeholder. LangChain
  stays for structured output only.
- **Tests must not touch the network or an LLM.** Use the `transport=` and `now=` seams and the fake
  generators; see `tests/discovery_site.py`.

## Before finishing a session

Run `ruff check .`, `ruff format --check .`, `mypy`, `pytest`, then update the handoff:
current state and known problems in `PROJECT_HANDOFF.md`, any decision and its reasoning in
`DECISIONS.md`, and what is now next in `TODO.md`.

Do not record a problem as fixed unless it is fixed, or a result as verified unless it was run.
These files are read by someone with no other context.

**Check a documented claim against the code before carrying it forward.** These files are self-written,
and two claims turned out to be wrong when finally tested: the trust rule's coverage gap was blamed on
the wrong half of the rule for a week, and a known problem asserted that a blocked authority never
reached the plan when in fact it reached it by two separate routes. Both were described from reading a
code path rather than from output. Prefer a run, a test, or a printed result over a careful reading.

**Commits:** one lowercase subject line, no body, no attribution trailers, straight to `main`. One
concern per commit, **with the documentation for that concern in the same commit** — a `docs:` commit is
for when documentation is the only thing changing.

## Running it

```bash
.venv/bin/uvicorn visa_research_agent.api.app:create_app --factory   # the app
.venv/bin/visa-discover corridor --destination japan --nationality IN --from GB
```

Secrets (`OPENAI_API_KEY`, `SEARCH_API_KEY`) live only in `.env`. Reviewable policy — source mode,
extraction mode, cache TTL, stale ceiling — is committed in `config/runtime.yaml`.

Clear `var/cache/` when testing a retrieval change, and `var/corridors/` when testing a discovery
change — either one will serve a pre-change result and make a fix appear not to work. A stored
corridor is kept for three weeks.
