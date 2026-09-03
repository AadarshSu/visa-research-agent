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
- **First, check whether the page was ever a candidate at all.** With `discovery_selector: model`
  the model only sees `[c for c in candidates.values() if c.best_combined()[1] > 0]`, which over 24
  runs is **6% of the candidate set** — Liechtenstein offers 2 of 7,482 (entry 123). A page scoring
  zero for every role is invisible to the selector however good it is, so *"the model did not pick
  it"* and *"the model never saw it"* look identical from the outside. `var/recall/<corridor>.json`
  distinguishes them: `best_score` of `0.0` means the second. **What matters is whether the score
  crossed zero, not where it ranked** — the pool goes to the model unsorted with the scores withheld,
  so ordering is consumed only by the heuristic fallback (entry 126). **And read the signals for
  `residence:`** — on the four `POST_SPECIFIC_ROLES` a page about where the traveller applies from
  gains `residence_weight`, which is often what put it above zero. It never fires when the passport
  and the residence are the same country, never touches `visa_decision` or `general_entry`, and
  never subtracts from a page about the passport country.
- **To see the shortlist** — 35 places since entry 61, five reserved per role — wrap
  `resolver.shortlist`, print each candidate's score, role, link text, inherited heading and
  `link_scores.signals`, and return the list unchanged. Nothing else exposes it. **With
  `discovery_selector: model` the shortlist is no longer what gets read**, so wrap
  `CorridorResolver._choose_what_to_read` to see the actual selection, or `_fetch_bodies` to see
  which of it was *readable*.
- **To replay a past corridor offline, join the corpus, not the recall log.** Every run writes
  `var/recall/<corridor>.json` with all candidates and their scores. Rebuilding a `PageLink` from that
  file's `title` reproduces only 70% of recorded scores; joining `var/corpus/<CC>.json`, which stores
  `link_text`, `heading` and `depth` as the crawl found them, reproduces 99% (entry 62).
- **To replay the *ranking* at a budget nobody ran, call `resolver.shortlist()` on the recall log's
  own scores.** It is a module-level function precisely so this needs no resolver, no fetcher and no
  model client (entry 87), and the recorded scores are exact input to it because the numeric text
  lift is off everywhere. Never reimplement it: a reimplementation disagreed with an observed run,
  while binding the real thing reproduced 26 of 26 recorded shortlists (entry 61).
- **A delegated service is not a source and cannot become one.** Where an authority contracts its
  guidance out — the Netherlands sends most residences to VFS Global for the document checklist —
  the crawler records the `href` off the approved page and the plan *names* it. It is never fetched,
  quoted or cited, and it fills no role. Two things must both hold before one is recorded: an
  approved government page linked it, and its registrable domain is in
  `config/service_providers.yaml`. The model picks by `delegate_id` from what we recorded and can
  never supply a URL. Entry 89.
- **Two different questions, two different commands, and do not merge them.** Whether the *store*
  holds the answer is **`visa-discover coverage`**; whether the *corridor* then finds it is selection
  recall, below. A single number covering both would hide which half failed, which is the mistake
  `visa-discover audit` exists not to make.
- **A visa-free plan is an entry plan** (entry 95 — decided, not yet built, TODO item 39). The
  traveller still has duties; they are just not an application. Expect `application_steps` to hold
  entry steps, `where_to_apply` to be `None` and `requirements` to be empty — and expect it only
  where a source *states* `visa_required is False`.
- **A role can fail to arise, and that is not a gap** (entry 94). No visa means no application, so
  a visa-free corridor has no checklist, route, fee or processing time to find — Singapore's
  Philippine row is 2 answered and 4 that do not arise, against the Indian row's 6 answered, because
  India is on the same list the Philippines is absent from. The oracle records it as
  `not_applicable` and refuses the claim unless a page answers `visa_decision`: **"we could not find
  the checklist" must never become "there is no checklist".** The plan cannot say this yet — item 39.
- **A role an official questionnaire settles is answered, and is counted apart** (entry 93). The
  distinction is *direct* answer — "Filipino citizens residing in the Philippines need a visa" —
  against *tool-mediated* — "France-Visas' Visa Wizard determines whether you need a visa; use it
  here". Both give the traveller an authoritative path; only the first is citable. So `coverage`
  reports them in separate columns and never merges them, a plan naming a decision tool still
  resolves, and a tool-settled checklist still lists no requirement.
- **`visa-discover coverage`** answers "is this country's corpus good enough to serve a corridor" in
  two halves that are never added, and it is the promotion rule for stage 3 (entry 90). Half one is
  the 47 of 47 answers a human named in `oracle/selection_oracle.yaml` — **one traveller, `IN/GB`,
  so it is a regression check and never evidence a corpus is ready.** Half two is every
  per-traveller family the store holds, and the verdict comes from that half alone. **Five verdicts**
  since entry 120: *no per-traveller dimension*, *covered* and *bounded by the authority* are passes;
  *incomplete* means rebuild before promoting; **`ungraded`** means neither half could say anything —
  no family and no oracle row — and **42 of 53 countries are `ungraded`**. Do not read that as 42
  curation jobs; entry 120 argues the oracle grows one country at a time. Reads three stores, calls nothing, has no model in it anywhere —
  keep it that way, because entry 81 is what grading this on roles filled would cost.
- **`visa-discover selection-recall`** grades what a selector chose to read against
  `oracle/selection_oracle.yaml`, and prints entries 85–86's jointly-built oracle beside it.
  **It cannot grade a change that widens the pool**, and that limit is structural rather than a
  bug: the fixture was curated "from every candidate that scored above zero" (`contention.py`), so
  no page outside the pool can appear in it — 88 of 88 oracle-named answering pages are in the pool,
  which is a tautology rather than a result (entry 123). Anything touching `_choose_what_to_read`'s
  filter needs a fixture curated from the **whole** candidate set first; item 31 owns that. Reads
  two files, calls nothing. **A recall log that cannot say which selector fetched its pages is
  refused, not graded** (entry 91): a run's fetched URLs are read as the model's picks, so grading a
  heuristic run that way puts the heuristic in the model's own arm. Every log written before
  `RecallRecord.selector` existed is in that state, so this currently grades nothing — re-run the
  corridors rather than loosening the check.
- **`visa-discover contention`** rebuilds a corridor's candidate set from the store — the resolver's
  own `score_link` and `reject`, no search, no model, no fetch — so an oracle row can be curated for
  a corridor nobody has run. `--role` ranks within one role, `--show <url>` prints that candidate's
  stored text, which is how a role is judged. The set is **corpus-only** and the first ten oracle
  rows were curated from `corpus ∪ search`; see entry 91 for what that costs.
- **An offline build answers browser challenges far more than a corridor can.** Both are handed the
  same renderer; the budget differs — `DEFAULT_CORPUS_RENDERS` is 400 against the request path's 12,
  because a build has no traveller waiting (entry 92). A host whose challenge cannot be answered is
  given up on after **three consecutive** failures, so `urm.lt` costs three renders rather than the
  whole job. None of this moves entry 41's line: a bare `403`, a `401` and a `429` state a decision,
  are never rendered past, and never reach the renderer at all.
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

