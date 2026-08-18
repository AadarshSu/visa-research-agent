# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

Status: `next` · `soon` · `later` · `blocked`

**Read [DECISIONS.md](DECISIONS.md) entries 29–35 first.** An outside review on 2026-08-18 was agreed
with in full and changed the direction: the posture, not the principle, is what has been costing
coverage (entry 35); "who to believe" moves out of the request path into committed data (entry 34);
the trust rule's governmental half was measured and fails closed for a fifth of the world (entry 33);
and three things ship today that the project's own rules argue against (entries 30, 31, 32). The list
below is that work in the order to do it. **The first item — the trust-coverage measurement — is done;
everything else is not.**

---

## Done

### ~~Commit the 51-country trust-rule test~~ — **done 2026-08-18**

`tests/test_trust_coverage.py`, 7 tests, offline. Freezes the 19 failures so a change is a visible diff,
asserts every one fails on the governmental half rather than the TLD half, and guards `countries.yaml`
against another country acquiring a governmental marker in its `tlds` unreviewed. Verified the tripwire
fires by simulating the forbidden fix.

**It also refined the finding, and the refinement matters** — see DECISIONS entry 33's table. The 19 are
two different failures. Nine (AT, BE, DE, DK, FI, NL, NO, SE, UY) have no marked domain at all and refuse
outright. Ten (CA, CL, CZ, GR, HU, IE, IT, PT, RO, RU) **do** have one, so bootstrap *succeeds* and builds
a trusted set that cannot contain the visa guidance — quieter and worse, because nothing reports it. Canada
is the sharpest: `gc.ca` still passes, but the content moved to `canada.ca`. Item 5 below is what fixes
both, and item 6's marker corrections (`gv`, `gub`, `canada.ca`) shrink the first group.

---

## Now — cheap, certain, and nothing depends on credit

### 1. Narrow what a block may hand over — `next`

**Why:** DECISIONS entry 32. The one shipped change never run live behaves more broadly than the entry
that shipped it argued for, in two ways, and the second matters:

- **`429` qualifies when entry 27 says only `401`/`403` do.** `BLOCKING_STATUS_CODES` is
  `{401, 403, 429}` in `domain/models.py` and `inaccessible_urls` is built from `blocked_urls()`
  unfiltered, so a transient rate limit can resolve a corridor and force the decision to unknown.
- **`decision_is_unverified` never checks the blocked page could have held the decision.** Any blocked
  URL anywhere plus any readable source is enough — a `403` on a footer link counts. **This is the
  refusal discipline leaking:** WAF `403`s on incidental pages are common at scale, so corridors whose
  decision was simply *not found* will increasingly present as *authority-blocked*, which resolves.

**Do:** stop `429` qualifying a corridor (it stays reported as `blocked` — entry 18 requires that), and
require the blocked URL to have been a credible `visa_decision` candidate: shortlisted for that role, or
scoring above a floor for it. Both changes are in `discovery/models.py` and `discovery/resolver.py`.

**Evidence:** a resolver test with an unrelated blocked footer URL and an unfound decision, asserting
the corridor still refuses. Offline.

**Careful:** this narrows entry 27, it does not reverse it. France must still resolve —
`france-visas.gouv.fr` is exactly a credible decision candidate, which is the case the exception exists
for. Confirm that with the France fixture before and after.

### 2. Delete three things — `next`

**Why:** DECISIONS entries 30 and 29. Each is more complexity than it earns, and one contradicts the
project's own recorded reasoning.

- **`conflicts` on `VisaPlan`** — free text written by the model, shown to travellers, checked by
  nothing (known problem 14). Entry 6 deleted a *working, deterministic* conflict detector for having
  too high a false-positive rate; keeping the unverified version is the same mistake with the
  verification removed. Remove from `domain/models.py` (`VisaPlan` and `VisaPlanDraft`), rule 5 of
  `prompts/extract_visa_plan.txt`, `research/openai_extraction.py`, `research/fixtures.py`, the
  Singapore fixture `plan.yaml`, and the assertions in `tests/test_models.py` and
  `tests/test_fixture_research.py`. A real disagreement still reaches the traveller through
  `unresolved_questions`.
- **`domain/state.py`** — describes a LangGraph workflow that is not happening (entry 29) and a
  `fetched_sources` shape retrieval abandoned. `VisaResearchState` appears only on the line defining it.
- **`langgraph` from `pyproject.toml`** — declared, never imported. In a project whose safety argument
  rests on a small audited surface, an unused dependency is one more thing a reader must prove is not
  load-bearing. LangChain stays; it is doing real work in `adjudication.py` and `openai_extraction.py`.

### 3. Make a failed adjudication refuse — `next`

**Why:** DECISIONS entry 31, which amends entry 16. A failed model call currently falls back to the
heuristic — the decider entry 15 proved gives **confident wrong answers** (Brazil's Riyadh page as the
document checklist, exit 0, nothing in the output hinting the checklist was from another continent). So
a transient OpenAI outage silently swaps the best decider for the worst one in production, visible only
to a reviewer who reads `decided_by`. Every other layer here prefers refusing to guessing.

**Do:** in `discovery/resolver.py` around the `AdjudicationError` handler (about line 565), retry the
call once and then refuse the corridor with the reason, rather than using the heuristic ranking.

**Keep:** the heuristic still builds the shortlist, and still answers when `discovery_decider:
heuristic` is configured — which stays tested and stays the offline regression baseline.

**The cost, accepted:** an OpenAI outage takes discovery down rather than degrading it.

---

## Next — the direction change

### 4. Read and honour `robots.txt` — `next`

**Why:** DECISIONS entry 35. Nothing in this codebase has ever fetched it — grep finds no reference to
robots anywhere in `src/`. A project that computes a per-host politeness delay (entry 25) while ignoring
the file stating a host's own crawl policy is inconsistent on its own terms, and the posture this
project wants is *honest client*, not *anonymous client*. This is owed regardless of what it buys.

**Do:** fetch and cache `robots.txt` per host in `discovery/crawl.py` and `research/live_sources.py`,
honour `Disallow` for the declared user agent, and record a skip as its own outcome so it never reads as
"nothing found".

**Expect it to cost coverage.** A path we currently walk past becomes a refusal. That is the correct
direction, and a `Disallow` is an authority's stated policy rather than a block to route around.

### 5. Move "who to believe" out of the request path — `soon`

**Why:** DECISIONS entry 34. `ARCHITECTURE.md` already says domains are decided by a rule once per
country and pages by the machine every corridor — but `bootstrap_destination` runs inside every cold
request and is cached **per corridor**, so a country's trusted set is re-derived from that day's search
rankings for every new nationality. Entry 22's US coin flip was this mechanism, diagnosed as ranking.

**Do:** generate the country → trusted-domains registry offline for all 198 countries with the existing
`bootstrap.py`, commit it beside `countries.yaml`, and skim it once. Request-time discovery then starts
at the corridor step.

**This is not the gate entry 19 removed.** Nobody curates URLs — that stays automated and is the
production goal. This is *domains*, ~3 per country, machine-proposed, frozen in review. Entry 19's own
finding is the argument: the human was applying one mechanical rule, so committing the rule's output is
strictly easier to audit than re-running it live.

**Buys:** four searches leave the cold path; the trusted set stops varying between runs; withheld
domains become something a person actually reads; and item 6 becomes a data edit rather than a regex
change.

### 6. Amend the trust rule for governments with no marker, and for Schengen — `soon`

**Why:** the committed `tests/test_trust_coverage.py` measurement. Two separate problems:

- **19 of 51 governments have no governmental marker in their hostname.** The amendment is a reviewed
  authority domain in the entry 34 registry — **never a wider regex.** Adding `.de`, `.nl`, `.it` as
  markers would trust every commercial site in those countries, and `belongs_to_destination` cannot
  narrow it, because for exactly these countries the own-TLD test is the only other signal.
- **Schengen is a definition problem, not a bug.** For short-stay visas the decision genuinely lives at
  EU level as much as nationally, and `europa.eu` passes `looks_governmental` but can never pass
  `belongs_to_destination` for any member state. "The destination's own government" is the wrong trust
  unit for a supranational regime. A reviewed supranational-domain list per member is the fix, and it
  amends the rule as stated in entry 19 and in `CLAUDE.md`, so **record a decision rather than
  patching.**

**Do first, separately, because they are corrections inside the existing rule rather than relaxations
of it:** add `gv` and `gub` as markers, and add `canada.ca` beside the `gc.ca` special case — Canada
fails only because immigration content moved and the pattern did not.

### 7. Measure the top 20 corridors against a bar committed in advance — `blocked`

**Why:** DECISIONS entry 35. This is the measurement that decides whether the project is a product or a
demonstration, so **nothing large should be built before it.** Seven corridors cannot answer whether
bot-blocks are the rule, and choosing a threshold after seeing the numbers is how a demonstration talks
itself into being a product.

**Do:** run the top 20 corridors by real traveller volume cold — India/China/Nigeria/Philippines →
US/UK/Schengen/Gulf/Canada — and count per corridor: decision confirmed, checklist found, checklist
blocked.

> **The bar, committed now: product if ≥70% confirm the decision and ≥50% yield a checklist.** Below
> that, the anonymous-crawl posture is dead and the choice is licensed data (which forfeits the
> verifiability that is the whole differentiator) or client-side retrieval.

Today's seven are 5/7 and 4/7 — which would pass, on a sample chosen partly because it was easy.

**Blocked on:** Brave credit (`HTTP 402`). Run item 4 first so the numbers describe the posture the
project intends to keep.

**Fold in the France read-through**, which was the previous head of this list and needs the same credit:
run `france/IN/GB/tourism` and read the plan as a traveller. Three things no test can judge:

1. Does the explanation say plainly that the decision could not be verified, and name France-Visas?
2. Do the application steps stay useful when the first is "check the authority yourself"? Rule 8b asks;
   whether the model obliges is unknown.
3. Does "Uncertain" read as *we could not check* rather than *no visa needed*? If it reads as the latter
   to anyone, the wording is wrong and it matters more than anything else on this list.

The layout was already confirmed by injecting a France-shaped plan into the real renderer (entry 28), so
what is left to judge is the model's own words. **Careful:** if it reads as verified, the fix is the
wording and the banner, never a narrower `visa_required`. A corridor stored before 2026-08-17 has no
`inaccessible_urls` field, so clear `var/corridors/`.

### 8. Decide the client-side retrieval question — `soon`

**Why:** DECISIONS entry 35 raises it and deliberately does **not** approve it. The traveller's own
browser can open `france-visas.gouv.fr`; a human reading a public page is not this program circumventing
a refusal. Whether the agent may then read what their session received is genuinely near entry 18's
boundary.

**Do:** write the decision either way before writing any code. It needs its own entry because it moves
page content through the client, which needs a trust argument of its own — the domain rule still has to
hold, and content arriving via a browser has not passed the checkpoints that content arriving via
`LiveSourceFetcher` has.

**Careful:** nothing here licenses spoofing, retrying, or pointing this program's renderer at a refusal.
Entry 18 is unchanged.

---

## Then

### Put it somewhere others can open it aka deployment — `soon`

**Why:** it runs on one laptop with a `.env`. The goal is a URL to share. Keep this simple — a host,
some environment variables, done. No pipelines, no orchestration; CI already runs the checks.

**Reordered after the direction work**, because deploying before item 7 ships a product whose two
highest-volume corridors return no checklist, and item 5 changes what a cold request does.

A cold request is **34.1s** (19.4s corridor + 14.7s plan) for `united-states/IN/IN/tourism` with both
caches cleared, which fits a typical 30–60s proxy timeout but not comfortably. `var/cache/` and
`var/corridors/` are local directories, so a disposable filesystem makes **every** request cold. Item 6
removes four searches from that path.

1. **Precompute and ship corridors.** A warm corridor is 0.0s. Resolve popular ones locally with
   `visa-discover`, keep the JSON, point `FileCorridorStore` at it. The deployed app answers instantly
   for anything precomputed and refuses politely for the rest.
2. **Prefer a host that keeps a disk and a long-running process.** The stores persist and warm requests
   stay warm. If a disposable host is preferred, both stores are small classes with `load`/`store`.
3. **Set three secrets:** `OPENAI_API_KEY`, `OPENAI_MODEL`, `SEARCH_API_KEY`.
4. **Keep `render_mode: never`** unless the host can carry Chromium (~150MB plus system libraries).
   Vietnam will refuse without it, which is correct rather than broken.
5. **Put a key or a rate limit on `POST /visa-plans`.** It is unauthenticated and a cold corridor spends
   real money — search plus two model calls — so a public URL is a public wallet.

**Do not** deploy with `source_mode: fixtures`: it only knows Singapore, and would look like a working
product that answers exactly one corridor.

**Say it on the page:** this shows official guidance with citations and promises nothing about
correctness or currency. That framing is what makes the product safe to publish, so it belongs in the
interface rather than only in these files.

### Name a blocked authority whenever there is one — `soon`

**Why:** a blocked authority is named only when it cost the *decision*. The US resolved its decision on
`dhs.gov`, so its plan says the checklist is absent without ever saying that `travel.state.gov` refused
us — the same useful sentence, withheld because the corridor happened to succeed elsewhere.

**Do:** `ResolvedCorridor.inaccessible_urls` already carries them, so this is plumbing rather than a
decision. Do it while re-running corridors for item 7. Note it interacts with item 1: the causality
requirement governs whether a block may *resolve a corridor*, not whether it may be *reported* — every
block is still reported.

### Try sitemaps before crawling — `later`

**Why:** within already-approved domains, `sitemap.xml` gives the full URL inventory for scoring without
the politeness-heavy two-hop crawl. And the crawl has a known hole: its 40-page budget is spent entirely
at depth 0 (see *Smaller things*), so depth-2 discovery — where Japan's checklist was found — never
happens for a multi-domain destination.

**Do:** check first whether the seven verified corridors' chosen pages appear in their domains'
sitemaps. If most do, the crawl becomes a fallback rather than the primary mechanism. Cheap to check,
and worth checking before optimising the crawl further.

### Tell "no checklist exists" apart from "we failed to find it" — `soon`

**Why:** `document_checklist` is not load-bearing (entry 14), so a corridor resolves without one. Right
for Vietnam, which publishes none. Wrong for a country that publishes one we failed to find or read —
and **discovery emits the same result in both cases.** The plan is honest either way (`VisaPlan` forces
it to state the gap and forbids inventing requirements) and is marked `partial`, but nobody is told
which case they are looking at.

**Live rather than hypothetical:** the United States ships exactly such a plan. And it is a *third* case
again — not "none exists", not "we failed to find it", but "we were not allowed to read it".

**Do:** the design already considered is a reviewed per-country declaration — `no_official_checklist:
true` in `destinations.yaml`, with a required note saying where the requirements actually live. A human
decides once, in git, exactly as `trusted_domains` works. Undeclared countries go back to refusing. This
sits naturally beside the entry 34 registry, which is the same shape of artifact.

**Do not** try to infer the difference heuristically. "No checklist found" and "no checklist exists" look
identical from inside the crawler, which is the whole problem.

### Decide whether a host that has refused every request should be skipped — `later`

**Why:** entry 24 recovered three of the US corridor's five wasted fetch places. **Two remain**, both
`travel.state.gov`, and they remain because neither URL was ever crawled — one is a PDF, which the crawl
skips by design. The per-URL rule cannot help, and every other `travel.state.gov` request has been
refused.

**The question, a judgement rather than a lookup:** may a host that has refused *every* request and
served *none* be treated as blocked for URLs never tried? It recovers two places out of ten, and it is
inductive, which is why it was not simply done.

**Do:** count requests and refusals per host; consider it only where refusals are high and served is
zero. Then measure whether the two recovered places change what the corridor resolves. If not, leave the
rule out — an inductive skip that buys nothing is not worth its risk. Item 5 may make this moot: a
`Disallow` is a stated policy covering paths never tried, which is the honest version of this inference.

**Careful:** a `403` on one path is genuinely not evidence about another — real sites put WAF rules on
some paths and serve the rest. A host-level skip can silently lose a readable page, and losing evidence
costs a refusal. The block must still be reported as `blocked` (entry 18), and nothing here may become a
retry.

**Also still overstated:** `pages_fetched` is the shortlist length, so the US reports ten pages read when
eight are readable.

### Watch where the two deciders disagree — `later`

**Why:** `decided_by` says which decider chose, and the heuristic's score is kept beside the model's
choice. That divergence is free evidence about both, and nobody is reading it.

**Do:** on a corridor run, note every role where the model chose a page the heuristic did not rank first.
A pattern is either a lexicon gap worth closing or a model error worth prompting against. Four corridors
currently disagree on `general_entry` and `visa_decision` most.

**Careful:** do not tune the lexicon to agree with the model. The heuristic's job is to build a good
shortlist, not to reproduce the model's judgement. Note that after item 3 it is no longer a fallback, so
its remaining jobs are the shortlist and the offline baseline.

---

## Later

### Revisit conflict detection, with claim scope — `later`

**Why:** entry 30 deletes the unverified `conflicts` field. That removes an alarming unchecked signal; it
does not answer the underlying question, which is real — official sources do disagree.

**Do:** record the population each claim applies to, and compare only same-scope claims — the exact gap
that killed the previous attempt. Leave the visa decision out of comparison; it already has stronger
guards. Restrict to quantitative rules (validity periods, stay lengths, processing times) where a wrong
flag costs a caveat rather than alarm. Full post-mortem in [DECISIONS.md](DECISIONS.md) entry 6 — read it
before starting.

### Detect drift in configured sources — `later`

**Why:** every source already stores a content hash, so a changed government page is detectable and
currently ignored.

**Do:** on a hash change, mark the source rather than refusing — government pages change whitespace
constantly. **Never** auto-rediscover and swap a role-bearing source: that is the wrong-checklist failure
with the human removed. A persistent failure over several runs is the honest trigger to propose a
replacement.

---

## Smaller things

- **A footer link inherits the heading of whatever came above it.** `extract_links` assigns each link the
  last heading it has seen, and footer links sit below everything, so France's legal notice was scored
  against a news article's heading about visa requirements (entry 26). The boilerplate veto handles the
  pages this was observed on; the inheritance itself is still wrong and will quietly inflate any other
  footer link. Telling a footer from markup is the hard part, so this is recorded rather than fixed.
- **A plan can leak an internal field name into traveller-facing text.** The US plan's first unresolved
  question reads "no official application-document checklist was published in the configured
  `application_document_source_ids`" — the model repeating a key from the research packet. A prompt matter
  rather than a code one.
- **A reserved shortlist place guarantees a domain, not a page.** Entry 22's floor reserves each domain's
  best *link-scored* candidate, so the US mission's reserved place went to
  `in.usembassy.gov/scheduling-immigrant-visas-appointments` — right post, wrong visa class — rather than
  `/visas/`. The fix is in mission scoring, not the floor: `mission_affinity`'s bonus applies only to
  `document_checklist` and `application_route`, and only when those roles already scored.
- **`_mission_domains` returns `[]` for every automatically discovered destination.** It reads
  `destination.sources`, and `AutomaticDestinationService._base_config` builds a `DestinationConfig` with
  none — so the `on_mission_host` bonus never fires in the request path at all. Broader than known problem
  13, which describes only Brazil's path-based case. Mission detection survives there solely through
  `mission_affinity`'s host-label check.
- **The corridor's 40-page crawl budget is spent entirely at depth 0.** Seeds enter the frontier at
  priority `-1000.0`, so every seed is popped before any child, and twelve corridor queries at eight
  results each produce well over 40 unique seeds. Depth-1 links still become candidates without being
  fetched, so the loss is depth-2 discovery — which is where Japan's checklist was found. A per-domain
  **seed** cap would restore it without lowering `maximum_pages`, which must not be lowered. See also the
  sitemap item above, which may be the better answer.
- **Nothing validates `countries.yaml` against a `tlds` entry that widens trust.** Adding `gov` to a
  country's `tlds` would change what is trusted with no review of the rule itself. Bounded now by the cap
  and the corroboration bar (entry 22), but the data is still where a mistake would not be caught. Item 1's
  test is the natural place to add a guard.
- **Missions named by city are still unrecognised** — Singapore's `london.mfa.gov.sg`. Folded into the
  ranking work: path-based mission detection has to solve the same problem, since the residence country is
  not always a host label. Add city names to `countries.yaml` beside `host_labels`.
- **Cache invalidation on rule changes.** After changing what counts as usable, cached entries still serve
  the old result until the TTL expires. This cost real debugging time — a fix appeared not to work until
  `var/cache/` was cleared. Consider keying entries by a rules version.
- **`is_bare_public_suffix` is a heuristic**, not a real public suffix list. It correctly rejects `gov.sg`,
  `gov.uk`, `go.jp`, `gouv.fr` and `co.uk` while allowing `usa.gov` and `service.gov.uk`, but review it as
  countries are added — and note it will need `gv` and `gub` per item 6.
- **Singapore's VFS page is a 403, not a JavaScript problem.** It was recorded as client-rendered; it is
  bot-blocked at the HTTP layer, so rendering never applies (the render only runs after a `200` whose text
  was thin).
- **`xuatnhapcanh.gov.vn/en` answers `200` with `location: http://localhost:4000/vi`** and an empty body: a
  misconfigured Next.js i18n redirect. Browsers ignore `Location` on a `200`, so rendering does not fix it
  either. The site root works. Possibly worth reporting to the authority; nothing to fix here.
- **The eVisa "Go here" link for Japan** points at an information page that is itself a PDF shell, so
  clicking it downloads a PDF rather than opening the application portal. The plan's own unresolved
  questions flag this, so it is visible rather than silently wrong.
- **Rendering has earned zero live corridors.** It is off in committed config, contained behind a protocol,
  and Vietnam still refuses with it on (for non-rendering reasons). Keep it, but build nothing downstream
  on it until a corridor actually needs it.
