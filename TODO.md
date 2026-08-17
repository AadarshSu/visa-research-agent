# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

Status: `next` · `soon` · `later` · `blocked`

---

## Next

### The United States refuses a tourist visa for an Indian passport holder — `next`

**Why:** this is one of the highest-volume visa corridors in the world, and it produces
`EVIDENCE UNAVAILABLE`. A corridor this ordinary failing is worse than an exotic one failing: it is
what most people will try first. Resolving this is imperative for resolving similar issues with other corridors.

**Reproduce:** `united-states/IN/IN/tourism` through the automatic path, with a cleared
`var/corridors/`. It refuses with *"no page could be confirmed as the visa decision, document
checklist"*.

**It is not deterministic**, which is the first thing to know. Two consecutive runs of the identical
corridor gave different answers — one resolved `usa.gov/tourist-visa` and
`dhs.gov/visit-united-states`, the next refused outright. So this is a marginal corridor being
tipped either way by search ordering, not a corridor that cannot be researched.

**Three causes, compounding. The first is structural and the most important:**

1. **The own-government rule degenerates for the United States.** Every other country is checked
   as "governmental **and** under its own ccTLD" — two independent tests. The US's own TLD *is*
   `gov`, so both halves reduce to the same question and **every federal agency is auto-trusted**:
   `doi.gov` (the Interior), `federalregister.gov`, and equally `nasa.gov` or `irs.gov` were they
   to rank. Eight domains were trusted for the US, against Brazil's one, France's two, China's
   four. The crawl budget and the ten-slot shortlist are then spread across agencies with nothing
   to do with visas, and the right page has to win a much noisier field.
2. **`travel.state.gov` answers HTTP 403.** The canonical B1/B2 page — the single most
   authoritative source for this corridor — is bot-blocked. Per `CLAUDE.md` and DECISIONS entry 18
   that is not to be worked around, so it must simply be treated as absent.
3. **Nothing narrows a federal government to its visa authorities.** For most countries the
   ccTLD does that implicitly, because a small government has few domains.

**The parts needed are already there.** Readable, correct, unblocked pages exist:
`https://in.usembassy.gov/visas/` returns 200 and is the US mission *in India* — precisely the post
serving this traveller — and `mission_affinity` already resolves it as `own`, because `in` is in
India's `mission_labels`. `https://www.usa.gov/tourist-visa` returns 200 as well. Discovery is not
short of evidence; it is failing to keep hold of it.

**Do, in this order:**

1. Make the trusted set for a country whose TLD is `gov` narrower than "every federal agency".
   The honest options are ranking `usembassy.gov` and `state.gov` above general agencies for visa
   roles, or capping how many domains one bootstrap may auto-trust and taking the best-corroborated.
   Decide which, and record it — this is a change to the rule that replaced human approval, so it
   deserves a DECISIONS entry.
2. Give the shortlist a floor per *domain*, so eight trusted domains cannot crowd out the one that
   matters, in the same spirit as the crawl's existing per-host budget.
3. Re-run `united-states/IN/IN/tourism` several times and require it to resolve **consistently**.
   A corridor that passes once is not fixed; the current failure is exactly a coin-flip.

**Careful:** do not special-case the United States by name. The general defect is "a country whose
own TLD is also the generic governmental marker", and hard-coding `US` would leave the same hole
for any country that later gets one.

### Make a cold corridor faster than 53 seconds — `next`

**Why:** it is what makes the thing hard to host, and it is mostly one avoidable thing. Measured on
2026-08-17 for `brazil/IN/GB/tourism`:

| phase | time |
| --- | --- |
| bootstrap — 4 searches | 4.5s |
| **search + crawl** | **41.9s** |
| shortlist fetch — 10 pages, already concurrent | 7.2s |
| model adjudication — 1 call | 8.1s |
| corridor total | **53.4s** |

**The crawl is 73% of it, and it is sequential by accident rather than by design.**
`CrawlFetcher.fetch_html` awaits `self.sleep(self.host_delay_seconds)` — 0.5s — before *every*
request, whatever host it is for, and `LinkCrawler.crawl` walks its frontier one page at a time.
Forty pages therefore cost at least twenty seconds of pure waiting, and a second host waits behind
the first for no reason. The delay is meant to be politeness *to one host*; applied globally it is
just latency.

**Do:**

1. Make the delay per host, keyed off `host_of(url)`, and crawl different hosts concurrently. This
   is **more** correct about politeness, not less — each host still gets its spacing. Expect most
   of the 42s back, since a corridor typically spans two to four hosts.
2. Run the four bootstrap searches concurrently. Small, ~4.5s, and trivially safe.
3. Leave the shortlist fetch alone: 7.2s for 10 pages is already concurrent and reasonable.

**Careful:** do not buy speed by lowering `maximum_pages` or `maximum_pages_per_host`. Those bound
coverage, and Japan's checklist was found two hops deep — cutting depth would trade a real answer
for a fast refusal. And keep the delay: hammering a government site is exactly what the user agent
promises not to do.

**Verify:** re-time the same corridor and re-run the six known corridors. Speed must not change
which pages are chosen; if it does, the crawl order was load-bearing and that is worth knowing.

### Put it somewhere others can open it — `next`

**Why:** it runs on one laptop with a `.env`. The goal is a URL to share. Keep this simple — a host,
some environment variables, done. No pipelines, no orchestration; CI already runs the checks and
that is enough.

**The one thing that makes it non-trivial.** A cold request is **70.7s** (53.4s corridor + 17.3s
plan), all inside a single `POST`. Typical request timeouts are 30–60s, so the first request for any
destination would fail even though the work succeeds. And `var/cache/` and `var/corridors/` are
local directories, so anywhere with a disposable filesystem makes **every** request cold, not just
the first.

**The simple way through:** a warm corridor takes **0.0s**, so resolve the popular ones ahead of
time rather than on demand.

1. **Precompute and ship corridors.** Resolve them locally with `visa-discover`, keep the JSON, and
   point `FileCorridorStore` at that directory. The deployed app then answers instantly for anything
   precomputed and refuses politely for the rest — already an honest, supported outcome. No external
   services, nothing to orchestrate.
2. **Prefer a host that keeps a disk and a long-running process** over a disposable one. It removes
   the whole problem: the stores persist, warm requests stay warm, and a slow cold request has time
   to finish. If a disposable host is preferred anyway, the stores need somewhere shared to live —
   both are small classes with `load`/`store`, so a second implementation is contained.
3. **Set three secrets:** `OPENAI_API_KEY`, `OPENAI_MODEL`, `SEARCH_API_KEY`. They come from `.env`
   today, which is gitignored.
4. **Keep `render_mode: never`** unless the host can carry Chromium (~150MB plus system libraries).
   It is already the committed default; Vietnam will refuse without it, which is correct rather than
   broken.
5. **Put a key or a rate limit on `POST /visa-plans`.** It is unauthenticated and a cold corridor
   spends real money — search queries plus two model calls — so a public URL is a public wallet.

**Do not** deploy with `source_mode: fixtures`: it only knows Singapore, and would look like a
working product that answers exactly one corridor.

**Say it on the page:** this shows official guidance with citations and promises nothing about
correctness or currency. That framing is what makes the product safe to publish, so it belongs in
the interface rather than only in these files.

### Tell "no checklist exists" apart from "we failed to find it" — `next`

**Why:** `document_checklist` is no longer load-bearing (DECISIONS entry 14), so a corridor now
resolves without one. That is right for Vietnam, which publishes none. It is wrong for a country
that publishes one we simply failed to find or read — a crawl that stopped short, a language we do
not score, a bot-block — and **discovery emits the same result in both cases**. The plan is honest
either way (`VisaPlan` forces it to state the gap and forbids inventing requirements), but nobody is
told which case they are looking at.

**Do:** the design already considered is a reviewed per-country declaration —
`no_official_checklist: true` in `destinations.yaml`, with a required note saying where the
requirements actually live. A human decides once, in git, exactly as `trusted_domains` works.
Undeclared countries would go back to refusing. Adopt it if empty checklists start appearing for
countries that do publish one; that is the signal this decision is failing.

**Do not** try to infer the difference heuristically. "No checklist found" and "no checklist exists"
look identical from inside the crawler, which is the whole problem.

### Watch where the two deciders disagree — `next`

**Why:** the last step now asks a model (DECISIONS entry 16) and the heuristic remains as shortlist
builder and fallback. Both are recorded: `decided_by` says which chose, and the heuristic's score is
kept beside the model's choice. That divergence is free evidence about both, and nobody is reading
it yet.

**Do:** on a corridor run, note every role where the model chose a page the heuristic did not rank
first. A pattern in those disagreements is either a lexicon gap worth closing or a model error worth
prompting against. Four corridors currently disagree on `general_entry` and `visa_decision` most.

**Careful:** do not tune the lexicon to agree with the model. The heuristic's job is to build a good
shortlist and to be a safe fallback, not to reproduce the model's judgement.

### Tell a traveller what an inaccessible source means — `next`

**Why:** discovery now distinguishes a blocked authority from a broken one, and says so
(`blocked`, `inaccessible_domains`, DECISIONS entry 18). The *plan* side does not yet. A traveller
seeing a partial plan is told a source "could not be used"; they are not told the difference between
"this site is down", "this page said nothing usable", and "this authority does not permit automated
retrieval, so we could not verify its guidance here — check it yourself at this URL".

The third is the one worth saying out loud, because the traveller *can* act on it: they can open the
page in their own browser. That turns a gap into a next step.

**Do:** surface the `blocked` outcome distinctly in the plan interface, with the URL and a plain
sentence naming what we could not verify. Do not soften it into "unavailable"; do not let the model
fill the gap from another page — `VisaPlan` already forbids inventing a checklist, and the same
discipline applies here.

**Do not:** work around the block. See `CLAUDE.md`; that decision is closed.

---

## Later

### Revisit conflict detection, with claim scope — `later`

**Why:** `conflicts` on a plan is unverified free text written by the model. Nothing checks it,
names which pages differ, or decides which governs.

**Do:** record the population each claim applies to, and compare only same-scope claims — the exact
gap that killed the previous attempt. Leave the visa decision out of comparison; it already has
stronger guards. Restrict to quantitative rules (validity periods, stay lengths, processing times)
where a wrong flag costs a caveat rather than alarm. Full post-mortem in
[DECISIONS.md](DECISIONS.md) entry 6 — read it before starting.

### Detect drift in configured sources — `later`

**Why:** every source already stores a content hash, so a changed government page is detectable and
currently ignored.

**Do:** on a hash change, mark the source rather than refusing — government pages change whitespace
constantly. **Never** auto-rediscover and swap a role-bearing source: that is the wrong-checklist
failure with the human removed. A persistent failure over several runs is the honest trigger to
propose a replacement.

---

## Smaller things

- **Singapore's VFS page is a 403, not a JavaScript problem.** It was recorded as client-rendered;
  it is actually bot-blocked at the HTTP layer, so rendering never applies (the render only runs
  after a `200` whose text was thin). Whether to do anything about it is an open question —
  defeating bot detection is not obviously something this project should do.
- **`xuatnhapcanh.gov.vn/en` answers `200` with `location: http://localhost:4000/vi`** and an empty
  body: a misconfigured Next.js i18n redirect. Browsers ignore `Location` on a `200`, so rendering
  does not fix it either. The site root works. Possibly worth reporting to the authority; there is
  nothing to fix in this codebase.
- **Missions named by city are still unrecognised** — Singapore's `london.mfa.gov.sg`. Folded into
  the ranking item above, since path-based mission detection has to solve the same problem: the
  residence country is not always a host label. Add city names to `countries.yaml` beside
  `host_labels` as part of that work.
- **Cache invalidation on rule changes.** After changing what counts as usable, cached entries still
  serve the old result until the TTL expires. This cost real debugging time — a fix appeared not to
  work until `var/cache/` was cleared. Consider keying entries by a rules version.
- **`is_bare_public_suffix` is a heuristic**, not a real public suffix list. It correctly rejects
  `gov.sg`, `gov.uk`, `go.jp`, `gouv.fr` and `co.uk` while allowing `usa.gov` and `service.gov.uk`,
  but review it as countries are added.
- **The eVisa "Go here" link for Japan** points at an information page that is itself a PDF shell,
  so clicking it downloads a PDF rather than opening the application portal. The plan's own
  unresolved questions flag this, so it is visible rather than silently wrong.
- **Discovery has no per-corridor result store yet.** `visa-discover` prints and exits; nothing is
  saved. Needed before request-time integration.
- **`domain/state.py` has gone stale.** It is an intentional placeholder for the deferred LangGraph
  workflow and is referenced nowhere, but it still describes `fetched_sources: list[FetchedSource]`,
  which retrieval stopped returning when it moved to `RetrievalReport`. Either update it to the
  current shape or delete it until LangGraph is actually picked up; a placeholder describing an
  architecture that no longer exists is worse than none.
