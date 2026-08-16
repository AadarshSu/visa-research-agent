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

### Run a third country that actually publishes a checklist — `next`

**Why:** discovery's scoring was tuned against Singapore and Japan, so their 2/2 results are
in-sample. Vietnam was meant to be the held-out check, and it is now fully readable — rendering is
done, two shortlisting bugs found along the way are fixed, and it resolves at exit 1. But it cannot
answer the question: Vietnam publishes **no document checklist page at all**, so there is nothing
for ranking to get right or wrong. Its e-visa states requirements as upload fields inside the
application form, and `evisa.gov.vn`, its FAQ and its support page carry eligibility law rather than
a document list — all eight readable candidates score **exactly 0.0** for the role.

**Whether ranking generalises is still unknown**, and a destination that does publish a checklist is
the only way to find out.

**Do:** pick a destination that publishes readable HTML *and a real checklist* — Thailand or Brazil
are likely candidates. Run `visa-discover bootstrap`, approve its domains, run
`visa-discover corridor`, then judge the result against the real pages by hand. There is no gold
answer to diff against, which is the point: it cannot be tuned to pass.

**Careful:** resist tuning weights to make the third country pass. That would consume the only
out-of-sample signal available. Record what it got wrong instead.

---

## Soon

### Make the traveller profile variable — `soon`

**Why:** the profile is fixed at Indian passport / resident in the UK / tourism in
`config/traveller.py`. Discovery is already corridor-aware and takes nationality, residence and
purpose as input; the profile is the last piece that is not. Nothing can be offered to a real user
until this changes.

**Do:** replace the fixed constant with request input. `TravellerProfile` currently carries
UK-specific fields (`uk_immigration_status`, `uk_permission_expiry`) that need generalising, and
`travel_purpose` is `Literal["tourism"]` and needs widening. Country values need normalising to ISO
codes — `discovery/lexicon.py` already holds that reference data.

**Watch for:** `destinations.yaml` holds one set of sources per destination, which silently assumes
one corridor. Once the profile varies, that assumption breaks and sources need to become
corridor-keyed. See the layering table in [ARCHITECTURE.md](ARCHITECTURE.md).


---

## Later

### Wire discovery into request time — `later` · blocked by the third-country check

**Why:** discovery is an offline command. Serving arbitrary corridors eventually needs it in the
request path.

**Do:** resolve a corridor from cache when fresh, otherwise resolve it live, otherwise refuse.
Cache per corridor for weeks, not hours; a resolved corridor is not evidence and has a different
lifetime from the evidence cache. **Do not** `@lru_cache` corridor lookups the way the registry is
cached — corridor artifacts expire, and a stale one would be served for the process lifetime.

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

### Recognise missions named by city — `later`

**Why:** mission detection matches the residence country's code against the host, so
`uk.emb-japan.go.jp` is found but Singapore's `london.mfa.gov.sg` is not, because it is named by
city. Singapore still resolves correctly, so this is a latent gap rather than a live bug.

**Do:** add major city names per country to `countries.yaml` alongside `host_labels`.

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
- **The whole repo was reformatted** by `ruff format` in this change. Nothing was edited by hand:
  ruff 0.16.2 formats differently from whatever version the files were last written with, and
  `ruff format --check .` was already failing on 16 untouched files before any of this work. It is
  a large, purely mechanical part of the diff — read it separately from the rendering change.
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
