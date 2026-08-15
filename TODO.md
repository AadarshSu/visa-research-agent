# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

Status: `next` · `soon` · `later` · `blocked`

---

## Next

### Run a third country with readable HTML — `next`

**Why:** discovery's scoring was tuned against Singapore and Japan, so their 2/2 results are
in-sample. Vietnam was meant to be the held-out check but refuses for an unrelated reason (its
portal is JavaScript-rendered), so it never exercised ranking. **Whether discovery generalises is
currently unknown**, and that is the single biggest open question about the feature.

**Do:** pick a destination that publishes readable HTML — Thailand or Brazil are likely candidates.
Run `visa-discover bootstrap`, approve its domains, run `visa-discover corridor`, then judge the
result against the real pages by hand. There is no gold answer to diff against, which is the point:
it cannot be tuned to pass.

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

### Handle JavaScript-rendered sites — `soon`

**Why:** the single largest coverage limit. It blocks Vietnam's e-visa portal, Singapore's VFS page,
and any corridor whose authority uses a client-rendered site. No amount of scoring works around it,
and search does not fix it either — the page is unreadable however you arrive at it.

**Measured evidence** (taken 2026-08-15 against the live sites, so it does not need re-deriving):

| URL | HTTP | Readable characters after cleaning |
| --- | --- | --- |
| `https://evisa.gov.vn/` | 200 | **39** |
| `https://xuatnhapcanh.gov.vn/en` | 200 | **0** |
| `https://immigration.gov.vn/` | 200 | 736 |
| `https://mofa.gov.vn/` | 200 | 4992 |

The floor is `minimum_source_characters`, default **400**, in `config/settings.py`. Anything below
it becomes the `unusable` outcome — deliberately, because an empty shell would otherwise read as
"this authority requires no documents", which is far worse than refusing.

**Where the change would go.** There are **two** fetch paths and both would need it:

- `research/live_sources.py` — `LiveSourceFetcher`, the audited path for anything a traveller sees.
- `discovery/crawl.py` — `CrawlFetcher`, which needs raw HTML for link extraction.

**Decide before building:**

1. *Is a headless browser worth it?* It is a heavy dependency, much slower per page, and a new class
   of failure. Record the decision in [DECISIONS.md](DECISIONS.md) either way — including a decision
   **not** to, which is defensible: refusing a corridor is already a supported, honest outcome.
2. *How is it tested?* `AGENTS.md` forbids network access in tests, and a browser cannot be faked by
   `httpx.MockTransport`. Likely answer: put rendering behind a protocol like `SourceFetcher`, so
   tests inject a fake renderer and only an opt-in manual check ever launches a real browser.
3. *Does it apply to everything, or only on demand?* Rendering every page would be wasteful and
   slow. Rendering only when a fetch comes back below the character floor is cheaper and targets
   exactly the failure being solved.
4. *Does it change the trust model?* It must not. A rendered page is still subject to the same
   domain checks, and script execution must not be allowed to navigate somewhere untrusted.

**Good first test case:** `xuatnhapcanh.gov.vn` (0 characters today) or Vietnam's `evisa.gov.vn`.
Vietnam is already configured with approved domains and currently refuses, so success is
unambiguous: `visa-discover corridor --destination vietnam --nationality IN --from GB` moves from
exit code 2 to finding a document checklist.

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
