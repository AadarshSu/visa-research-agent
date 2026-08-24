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

**Where it stands, as of 2026-08-24**, so the rest of this file reads in context. The pipeline works
end to end and has been measured against a bar committed in advance (entry 35): over twenty
high-volume corridors run twice each, **75% confirm the visa decision** (bar ≥70%) and **50% yield a
document checklist** (bar ≥50%) — a pass, by one corridor and by nothing at all. Corridors are served
from **stored per-country page corpora** rather than a live crawl, at a median 27.4s. The largest
remaining coverage limit is **not** bot-blocking: it is authorities that put the answer inside an
interactive wizard, which costs every United Kingdom corridor its entire plan. Entries 44–58.

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
  the cost lands on search count and crawl budget — three searches per trusted domain, so five domains
  is fifteen queries on the cold path (entry 22).

  **Which domains are trusted is now committed data, not a live search (entry 38).**
  `config/authority_domains.yaml` is generated offline by `visa-discover registry` and read at
  construction; a country missing from it is **refused**, never bootstrapped live, because falling back
  would silently reintroduce the per-request variance the file exists to remove. The rule itself is
  unchanged — `auto_trusted_domains` still decides — so everything below still applies.

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
- **Never work around an authority that blocks automated retrieval.** Do not spoof a user agent, do
  not retry to get around a rate limit, do not point the renderer at a page an authority refused. A
  block is not evidence that the guidance is wrong or missing — it means *we cannot independently
  retrieve and verify it in this execution environment*, which is a narrower claim and the only honest
  one. Mark the source inaccessible, say so, and let the role go unfilled. Never substitute
  plausibility for evidence, in a product whose wrong answers send someone to a visa centre without
  the right papers.

  **First establish that it *is* a block, because for France it was not (entry 41, 2026-08-19).** This
  rule used to open by naming France's portal as a site that "answers `403` to anything that is not a
  browser". Measured, `france-visas.gouv.fr` answers a Cloudflare **challenge** — `cf-mitigated:
  challenge`, *"enable JavaScript and cookies to continue"* — and answers it for `robots.txt` as well,
  so the authority never stated anything. A challenge is a capability test, and answering it by running
  the page's own JavaScript in a real browser **under our own user agent** misrepresents nothing to
  anybody: the project's own renderer, announcing `VisaResearchAgent/0.1`, reads the page. So a
  challenge is its own outcome, may be answered by the renderer, and — like a `Disallow` — **may never
  resolve a corridor**. **The line is "did the authority state anything", not "which status came
  back".** A `401`, a bare `403` with no challenge markers, and a `429` are refusals and this rule
  governs them in full. Not yet implemented: see [TODO.md](TODO.md) item 5, and note the interface
  still tells travellers a challenged authority *"does not permit automated retrieval"*, which is
  false.

  **What is allowed, and is not a workaround: naming it.** A blocked page may be reported with its
  URL so the traveller can open it themselves, which is the one thing they can act on. The line is
  absolute — the page may be *named*, never *read*, inferred from, retried, or counted as a source.
  So `UnreadableAuthority` is deliberately not a `ConfiguredSource`, the research packet carries its
  URL and no text, and it is still checked against the approved domains, because nobody read it and
  the domain is the only thing vouching for it (entry 27).

  **And naming it must stay narrow (entry 32).** Only `401`/`403` may qualify a corridor — a `429` is a
  transient rate limit, and "try again later" is the honest advice. **A challenged `403` may not qualify
  one either (entry 41):** a refusal is at least a page an authority withheld, while a challenge is a
  page nobody asked the authority about. The blocked URL must also have been
  a credible `visa_decision` candidate: a `403` on a footer link is not grounds to declare the decision
  unverifiable.

  **Whether it is credible is now *judged*, never keyword-matched (entry 57).** `_decision_blocking`
  asks a model over the refused page's **address and label only** — there is no page text, because the
  authority refused it, and `build_blocked_packet` has no parameter through which any could be passed.
  Keep it that way: a packet that ever grew an excerpt field would be inferring content about a page
  nobody read, which is the thing this rule forbids outright. It fails closed after two attempts, and
  with no adjudicator configured the keyword test still runs, which is the deterministic baseline rather
  than entry 31's forbidden fallback. Measured: France qualifies its own United Kingdom and India pages
  and rejects its FAQ, its application form and its visa-category page — where the keyword version had
  qualified a **blank CERFA form**. Without both bounds, corridors whose decision was merely *not found* — which must refuse
  — drift into presenting as authority-blocked, which resolves. Every block is still *reported*
  regardless; the bounds govern what may *resolve a corridor*.

  **The posture is honest client, not anonymous client (entry 35).** This rule forbids *deception* —
  spoofing, retrying, rendering past a **refusal** — and none of that has changed or will. Rendering
  past a *challenge* is a different act and is now allowed (entry 41); the word doing the work in that
  sentence is "refusal". It does not
  require being an anonymous, unauthenticated client, and treating those as the same thing was costing
  coverage under the banner of a rule that never demanded it. So: `robots.txt` **is now read and obeyed**
  (entry 36), and asking an authority for access is ordinary. Client-side retrieval through the
  traveller's own browser is an **open question, explicitly not approved** — argue it in a decision
  entry before writing any code for it.

  **A `Disallow` is reported, and it may never resolve a corridor (entry 36).** `disallowed` is its own
  `FailureOutcome` so a page nobody asked for can never read as a page that did not exist — but it is
  deliberately outside `blocked_urls()` and `persistent_refusals()`, so it reaches neither
  `inaccessible_urls` nor `decision_blocking_urls`. A `403` was observed *on the page*; a `Disallow`
  covers a path we chose not to request, and treating it as evidence the answer sat behind that page
  would widen entry 32's narrow exception by a route entry 32 never considered. **And the reason
  reported must be true of what was seen**: a policy that could not be read is *"could not be read, so
  whether this client may fetch it is unknown"*, never *"does not permit"*, and an unreachable host is
  still reported as unreachable rather than as a policy nobody read.
- **A visa decision that could not be confirmed must be `null`, and the application enforces that.**
  Not the prompt: a model asked for null returned `true` in testing. A wrong yes or no about whether
  someone needs a visa is the most damaging thing this can say, so `decision_is_unverified` overrides
  the model rather than trusting it, and such a plan can never be `verified` (entry 27).
- **What may be stored is a *page*, never an *answer* (entry 44).** The corridor is not the unit of
  precomputation at any width — `destination × nationality × residence × purpose` is 196,020 corridors
  even with residence reduced to post selection, roughly 2.9M searches per refresh cycle, and the layer
  it would freeze is the one with the most inference in it. What *is* stored is a country's **page
  corpus**, because *which pages exist* does not vary by corridor; only which one answers a given
  traveller does, and that stays live. A **plan is a rendering, never a stored fact.** A `visa_rule`
  decision table is deliberately not built: one page names ~200 nationalities, so a wrong row would sit
  in a store for weeks and be served with a citation, where a wrong pick today is ephemeral. If it is
  ever built, a nationality the page did not name yields **no row**, never a false one.
  **A corpus miss must never be answered by *quietly* falling back** — entry 38's rule applied to pages.
  Deciding a corridor from that day's search after the store came up short would restore the
  per-request lottery for exactly the corridors that need it not to be one.

  **Read that as the constraint it is, not as a description of today.** Entry 44 wrote it as "a miss
  refuses and flags the country", and entry 47 chose a different shape that satisfies the same
  constraint: the candidate set is **`corpus ∪ live search`**, with search running on *every* corridor
  rather than as a fallback after a miss, so nothing silently degrades because nothing was ever
  conditional. A country with **no** corpus simply crawls, exactly as before. Refusing on a miss is
  still unbuilt and still wanted — [TODO.md](TODO.md) item 19 — and it only becomes safe once search
  has left the request path, which needs the nationality dimension measured first (entry 48).
- **A stored row records when the evidence was retrieved, never when the row was written.** A failed
  refresh serves cached text flagged `stale` and **keeps its original `fetched_at`**; only a validator
  match moves it, because a `304` proves the text is still current (entry 4). Past
  `source_maximum_stale_hours` a stored page is **refused rather than served**. Both hold in any store,
  and both are easy to lose in a migration — a schema that collapses `retrieved_at` and `row_written_at`
  starts lying about how current its guidance is. A content-hash change **marks** a source and may never
  auto-swap a role-bearing one: that is the wrong-checklist failure with the human removed.
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
and the pattern has now repeated in five separate sessions: the written-down diagnosis named the wrong
cause, and only running the thing showed it.

| what the file said | what a run showed |
| --- | --- |
| the trust rule's gap is in the TLD half | it is the governmental half (entry 33) |
| a blocked authority never reaches the plan | it reaches it by two routes (known problem 7) |
| consuming the corpus is slow because of *scoring* | it was `wrong_country`, 33× (entry 50) |
| removing the crawl risks *reporting* | reporting held; **qualification** broke (entries 55–56) |
| `visa_decision` needs its floor guard removed | the vocabulary could not recognise an answer (entry 56) |
| bot-blocks are the largest coverage limit | the **wizard** is (entry 58) |

Prefer a run, a test, or a printed result over a careful reading. When a TODO item proposes a fix,
**measure the proposal before implementing it** — three of the rows above are proposals that were
wrong, and each was cheap to disprove and expensive to have shipped.

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

```bash
.venv/bin/visa-discover corpus --country CA     # build a country's offline page corpus
```

Ten countries have a corpus in `var/corpus/` (AE, CA, DE, FR, GB, JP, NL, SE, SG, US). A country
without one crawls in the request path, exactly as before.

Clear `var/cache/` when testing a retrieval change, and `var/corridors/` when testing a discovery
change — either one will serve a pre-change result and make a fix appear not to work. A stored
corridor is kept for three weeks. **`var/corpus/` is deliberately not cleared between runs**; it is
the store, not a cache, and rebuilding one costs search quota.

**Both providers meter, and they fail differently.** OpenAI answers `429 credit_balance_exhausted`
when out; Brave answers **`HTTP 402`** both when out of credit *and* when queried too fast, so a `402`
is not proof the account is empty — check a single query before believing it. `search_all` has no
rate limiting (TODO, smaller things).
