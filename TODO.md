# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

Status: `next` · `soon` · `later` · `blocked`

---

## Next

### Decide whether a host that has refused every request should be skipped — `soon`

**Why:** DECISIONS entry 24 stopped a fetch place being spent on a page already proved unreadable,
and recovered three of the US corridor's five wasted places. **Two remain**, both
`travel.state.gov` — and they remain because neither URL was ever crawled, so nothing was observed
about them. One is a PDF, which the crawl skips by design; the other only ever appeared as a search
result. The per-URL rule cannot help, and every other `travel.state.gov` request has been refused.

**The question, and it is a judgement rather than a lookup:** may a host that has refused *every*
request and served *none* be treated as blocked for URLs never tried? It would recover two places out
of ten. It is inductive, which is why it was not simply done.

**Do:** count requests and refusals per host, and only consider this where the refusal count is high
and the served count is zero. Then measure whether the two recovered places change what the corridor
resolves. If they do not, leave the rule out — an inductive skip that buys nothing is not worth its
risk.

**Careful:** a `403` on one path is genuinely not evidence about another. Real sites put WAF rules on
some paths and serve the rest, so a host-level skip can silently lose a readable page, and losing
evidence costs a refusal. Whatever is decided, the block must still be **reported** as `blocked`
(entry 18), and nothing here may become a retry.

**Also still overstated:** `pages_fetched` is the shortlist length, so the US reports ten pages read
when eight are readable. Worth making it the count that was actually read.

### Put it somewhere others can open it aka deployment — `next`

**Why:** it runs on one laptop with a `.env`. The goal is a URL to share. Keep this simple — a host,
some environment variables, done. No pipelines, no orchestration; CI already runs the checks and
that is enough.

**What used to make this non-trivial is now much smaller.** A cold request was **70.7s**; after
DECISIONS entry 25 it is **34.1s** (19.4s corridor + 14.7s plan) for
`united-states/IN/IN/tourism`, measured with both caches cleared. That fits inside a typical 30–60s
proxy timeout, though not comfortably — the remaining time is two model calls and search latency, so
it will vary with someone else's load rather than with anything here. `var/cache/` and
`var/corridors/` are still local directories, so anywhere with a disposable filesystem makes
**every** request cold rather than just the first.

**The simple way through:** a warm corridor takes **0.0s**, so resolve the popular ones ahead of
time rather than on demand. Less essential than it was, and still worth doing: it turns a 34s first
request into an instant one, and it costs nothing to ship.

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
either way (`VisaPlan` forces it to state the gap and forbids inventing requirements) and is now
marked `partial` rather than `verified`, but nobody is told which case they are looking at.

**This is live rather than hypothetical now.** The United States ships exactly such a plan: no
document requirements, because the canonical B1/B2 checklist is a 403. That is the third case again —
not "none exists" and not "we failed to find it" but "we were not allowed to read it" — and it is the
one a traveller can act on, which is the item below.

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

**France is the strongest argument for doing this.** Entry 26 established that France refuses
because every readable page delegates the visa decision to `france-visas.gouv.fr`, which answers 403.
A traveller currently gets "no verified plan" for one of the most common corridors there is, when the
useful sentence is available and actionable: France publishes this, we are not permitted to read it
from here, open `france-visas.gouv.fr` yourself. That turns the refusal into a next step.

**The structural gap to close first, found on the US corridor.** A plan's `unavailable_sources`
covers only **its own** retrieval, and a discovery-time block never reaches it: `travel.state.gov`
answers 403 while the corridor is being resolved, so `ResolvedCorridor.inaccessible_domains` holds it
and the plan knows nothing. The US plan therefore tells a traveller the checklist is absent without
telling them an authority refused us — the one sentence they could act on. Carry
`inaccessible_domains` from the resolved corridor into the plan before writing any interface for it,
or the interface has nothing to render.

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

- **A footer link inherits the heading of whatever came above it.** `extract_links` assigns each
  link the last heading it has seen, and footer links sit below everything, so France's legal notice
  was scored against a news article's heading about visa requirements (entry 26). The boilerplate
  veto handles the pages this was observed on; the inheritance itself is still wrong, and will
  quietly inflate any other footer link. Telling a footer from markup is the hard part — there is no
  reliable signal — so this is recorded rather than fixed.
- **A plan can leak an internal field name into traveller-facing text.** The US plan's first
  unresolved question reads "no official application-document checklist was published in the
  configured `application_document_source_ids`". That is the model repeating a key from the research
  packet. Harmless but unpolished, and a prompt matter rather than a code one.
- **A reserved shortlist place guarantees a domain, not a page.** The floor from DECISIONS entry 22
  reserves each domain's best *link-scored* candidate, so the US mission's reserved place went to
  `in.usembassy.gov/scheduling-immigrant-visas-appointments` — right post, wrong visa class — rather
  than to `/visas/`. If that pattern matters, the fix is in mission scoring, not in the floor:
  `mission_affinity`'s bonus applies only to `document_checklist` and `application_route`, and only
  when those roles already scored, so a bare `/visas/` URL on the traveller's own post earns nothing
  for `visa_decision`.
- **`_mission_domains` returns `[]` for every automatically discovered destination.** It reads
  `destination.sources`, and `AutomaticDestinationService._base_config` builds a `DestinationConfig`
  with none — so the `on_mission_host` bonus never fires in the request path at all. This is a
  second and broader cause than the path-based one recorded as known problem 13, which describes only
  Brazil. Mission detection survives in the automatic path solely through `mission_affinity`'s host
  label check.
- **The corridor's 40-page crawl budget is spent entirely at depth 0.** Seeds enter the frontier at
  priority `-1000.0`, so every seed is popped before any child. Twelve corridor queries at eight
  results each produce well over 40 unique seeds, so "crawl to pinpoint" never reaches depth 1 for a
  multi-domain destination. Depth-1 links still become candidates without being fetched, so the loss
  is depth-2 discovery — which is where Japan's checklist was found. A per-domain **seed** cap would
  restore it without lowering `maximum_pages`, which must not be lowered.
- **Nothing validates `countries.yaml` against a `tlds` entry that widens trust.** Adding `gov` to a
  country's `tlds` would change what is trusted with no review of the rule itself. The consequence is
  now bounded by the cap and the corroboration bar (entry 22), but the data is still the place where
  a mistake would not be caught.
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
