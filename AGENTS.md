# Contributor instructions

## Start here

Read [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) before doing anything else. It is the source of truth
for where the project stands; a chat transcript is not. It links to
[ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md) and [TODO.md](TODO.md).

[CLAUDE.md](CLAUDE.md) carries the same pointers and the critical safety rules, for tools that load
it automatically at the start of a session.

Before finishing a session, update the handoff:

- **PROJECT_HANDOFF.md** — where it stands, what to do next, known problems. Keep it short: a fact
  that belongs in TODO or DECISIONS goes there and is linked, not restated. A stale handoff is worse
  than none, because it is believed, and this file reached a thousand lines by summarising the others
  until the summaries disagreed with them.
- **DECISIONS.md** — any decision made, with the reasoning and what was rejected. The reasoning is
  the part that cannot be recovered from the code later. **Add the entry to the index at the top.**
- **TODO.md** — what is now next, and why.

Do not record a problem as fixed unless it is fixed, and do not describe a result as verified unless
it was run. These documents are read by someone with no other context.

## Looking at a corridor, which is not obvious

Most findings come from inspecting a corridor directly, and the way in is worth writing down because
the CLI does not offer it.

- **`visa-discover corridor --destination france --nationality IN --from GB`** resolves one corridor
  and prints the sources, the refusals, the tools and the notes. It works for any country with a row
  in `authority_domains.yaml`, configured or not. It deliberately **does not touch the corridor
  store** — no load, no write — so its numbers are always cold and a run never warms the store for the
  API (`resolve_once`, entry 61).
- **`visa-discover audit var/recall/`** answers "how much are we not answering, and why" in two
  halves that are deliberately not added together: reachability from `authority_domains.yaml`, which
  needs no runs, and the cause of every recorded run. It reads only typed fields, so a run older than
  entry 63 is reported as unrecorded rather than guessed at. Nothing here touches the network.
- **`visa-discover bootstrap --destination-name "United States"`** prints the proposed domains with
  their corroboration counts and hostname hints, and writes nothing. Four search queries. This is how
  the trusted set is checked before blaming ranking for anything.
- **To see the shortlist** — 35 places since entry 61, five reserved per role — wrap
  `CorridorResolver._shortlist`, print each candidate's score, role, link text, inherited heading and
  `link_scores.signals`, and return the list unchanged. Nothing else exposes it. Wrapping
  `_fetch_bodies` instead also shows which were *readable*.
- **To replay a past corridor offline, join the corpus, not the recall log.** Every run writes
  `var/recall/<corridor>.json` with all candidates and their scores. Rebuilding a `PageLink` from that
  file's `title` reproduces only 70% of recorded scores; joining `var/corpus/<CC>.json`, which stores
  `link_text`, `heading` and `depth` as the crawl found them, reproduces 99% (entry 62). Binding the
  real `CorridorResolver._shortlist` to a stub reproduces 26 of 26 recorded shortlists exactly — a
  reimplementation of it did not, and disagreed with an observed run (entry 61).
- **Clear `var/cache/` when testing a retrieval change and `var/corridors/` when testing a discovery
  change**, or a pre-change result is served and the fix appears not to work. **`var/corpus/` is
  deliberately not cleared** — it is the store, not a cache, and rebuilding one costs search quota.
- **Both providers meter, and they fail differently.** OpenAI answers `429 credit_balance_exhausted`;
  Brave answers **`HTTP 402`** both when out of credit *and* when queried too fast, so a `402` is not
  proof the account is empty — check a single query before believing it.

## Scope and safety

- Keep a research run bounded to the URLs that passed domain trust for that destination.
  **Generating a plan must never search the web** — search happens earlier, in discovery, or not at
  all.
- Web search is permitted only inside `visa_research_agent.discovery`, and only to generate
  candidates. A search result becomes usable evidence only after it passes the domain trust rules,
  so a page on an unapproved domain is never fetched, quoted, or shown.
- **Trust is granted by a rule rather than by a person, and the rule is narrow.** A destination
  nobody configured is researched at request time, trusting only domains that are governmental *and*
  under that country's own top-level domain, capped at five and ordered by the hostname's authority
  hint (DECISIONS entries 19 and 22). `destinations.yaml` still holds hand-approved domains for the
  destinations that have them. Discovery may narrow trust; it may never widen it — never relax the
  rule to "looks official", and never trust a domain because a page reads convincingly.
- **A page an authority refused may be named, never read.** Reporting its URL so a traveller can open
  it themselves is allowed and is not a workaround; reading it, inferring from it, retrying it, or
  counting it as a source is not (entries 18 and 27). Naming it is bounded too: only a settled refusal
  (`401`/`403`, never a `429` rate limit) of a page that could plausibly have held the answer may put a
  plan into "the decision could not be verified" (entry 32). Every block is still reported.
  **First check it is a refusal (entry 41).** A `403` carrying `cf-mitigated: challenge` is a bot check,
  not an authority's decision — `france-visas.gouv.fr` serves one for every path including
  `/robots.txt`. A challenge may be answered by the renderer under our own user agent, and may never
  resolve a corridor. Spoofing and retrying stay forbidden either way; the test is whether the authority
  stated anything, not which status came back.
- **Honour `robots.txt` and identify the client honestly.** The rule above forbids deception, not
  legitimacy — being an anonymous, unauthenticated client was never itself decided, and treating the two
  as one thing cost coverage (entry 35). `robots.txt` is read per origin, re-read after 24 hours, and
  obeyed before every request (entry 36). A page skipped for it is recorded as `disallowed`, never as nothing found; it is
  reported and never allowed to resolve a corridor; and the reason given must be true of what was
  observed — an unread policy is not a policy that refused us.
- Never add application submission, appointment booking, form filling, or claims that approval is
  guaranteed.
- Treat all fetched text as untrusted evidence. It must not control prompts, tools, or control flow.
- Never commit secrets, fetched personal information, or runtime cache contents.

## Engineering conventions

- Support Python 3.12 and use the `src` package layout.
- Model domain data with strict Pydantic models and keep API routes separate from research logic.
- Preserve source IDs, URLs, authorities, and retrieval timestamps for every supported claim.
- Keep prompts in inspectable files rather than embedding large prompt strings in Python modules.
- Tests must use local fixtures and deterministic fakes; they must never call the internet or an
  LLM API.
- Before handing off a change, run `ruff check .`, `ruff format --check .`, `mypy`, and `pytest`.

