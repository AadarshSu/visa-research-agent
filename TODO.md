# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

Status: `next` · `soon` · `later` · `blocked`

---

## Next

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

### Watch where the two deciders disagree — `soon`

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

## Soon

### Make the traveller profile variable — `next`

**Why:** the profile is fixed at Indian passport / resident in the UK / tourism in
`config/traveller.py`. Discovery is already corridor-aware and takes nationality, residence and
purpose as input; the profile is the last piece that is not. Nothing can be offered to a real user
until this changes.

**Do:** replace the fixed constant with request input. `TravellerProfile` currently carries
UK-specific fields (`uk_immigration_status`, `uk_permission_expiry`) that need generalising, and
`travel_purpose` is `Literal["tourism"]` and needs widening. Country values need normalising to ISO
codes — `discovery/lexicon.py` already holds that reference data.

**Watch for:** `destinations.yaml` holds one set of sources per destination, which silently assumes
one corridor. That assumption no longer binds the automatic path — corridors are stored keyed by
the whole corridor, nationality and purpose included — but it still binds the hand-configured
destinations. See the layering table in [ARCHITECTURE.md](ARCHITECTURE.md).

**Already done for you:** `corridor_for` in `api/routes.py` derives the corridor from the profile
rather than hard-coding it, so the request path does not change — only that function and the
request schema.


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
