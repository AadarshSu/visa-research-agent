# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

Status: `next` · `soon` · `later` · `blocked`

**Read [DECISIONS.md](DECISIONS.md) entries 29–35 first.** An outside review on 2026-08-18 was agreed
with in full and changed the direction: the posture, not the principle, is what has been costing
coverage (entry 35); "who to believe" moves out of the request path into committed data (entry 34);
the trust rule's governmental half was measured and fails closed for a fifth of the world (entry 33);
and three things shipped that the project's own rules argue against (entries 30, 31, 32). The list below
is that work in the order to do it.

**Done so far:** the trust-coverage measurement (33), the block-handover narrowing (32), the deletions
(30, 29), the adjudication refusal (31), and the withheld-reason fix. **Left:** entries 35 and 34 — the
posture and the registry, both larger and one of them blocked on credit. **Nothing is shipping against the project's own rules any more**, and every item that needed no credit is
done. What remains all costs something: a crawl policy, a 198-country registry, or search quota.

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
is the sharpest: `gc.ca` still passes, but the content moved to `canada.ca`. Items 2–3 are what fix both;
item 3's marker corrections (`gv`, `gub`, `canada.ca`) shrink the first group on their own. **It also
turned up a defect since fixed — see the entry below:** the one mitigation known problem 2 recommends — reading
`withheld_domains` — currently labels these ministries "not a government domain for this destination",
which is false and identical to what a commercial agency gets.

### ~~Narrow what a block may hand over~~ — **done 2026-08-18**

`PERSISTENT_REFUSAL_STATUS_CODES = {401, 403}`, and `ResolvedCorridor.decision_blocking_urls` carries the
refusals that plausibly held the decision — apart from `inaccessible_urls`, since every refusal is worth
reporting while only a refusal of a page that could have answered licenses resolving. Credibility is the
`visa_decision` link score above zero, low on purpose because the scorer already vetoes site furniture
outright. **Verified by mutation:** reintroducing either defect fails exactly the intended test. France's
shape still resolves. DECISIONS entry 32.

**Known limit, failing toward refusal:** the crawl discards a page it could not fetch, so a refusal first
met at crawl depth is not a candidate and cannot qualify. A national visa portal is what search returns
first, so the France case is covered.

### ~~Delete three things~~ — **done 2026-08-18**

`conflicts` is gone from both plan models, the prompt's rule 5, both extractors, the Singapore fixture and
the interface; `domain/state.py` and the `langgraph` dependency are deleted. Two things worth knowing:
Singapore's real passport-validity discrepancy was **moved** into `unresolved_questions` rather than lost,
with a test asserting it; and the interface's `.reliability-grid` was `1fr 1fr`, so the wrapper and its
now-dead CSS went too rather than leaving one block in half the width. Checked by injecting a plan into the
real page. DECISIONS entries 30 and 29.

### ~~Make a failed adjudication refuse~~ — **done 2026-08-18**

`ADJUDICATION_ATTEMPTS = 2`, then `AdjudicationRefusal`, which `resolve` turns into an ordinary refusal
naming the reason. Retrying a model provider is not what entry 18 forbids. `_refused` now takes
`model_calls`, so a corridor that spent two calls and resolved nothing says so — a cost that appears only
on success is one nobody notices. **Verified by mutation:** reinstating the fallback fails the end-to-end
test. DECISIONS entry 31.

**The heuristic keeps its two real jobs:** it builds the shortlist the model chooses from, and it answers
when `discovery_decider: heuristic` is set, which stays the offline regression baseline.

### ~~Stop `withheld_domains` telling a reviewer something false~~ — **done 2026-08-18**

The branch in `auto_trusted_domains` now splits three ways, so a domain under the destination's own
top-level domain with no recognised marker says it could not be **confirmed** as an authority, may well be
a real one, and needs naming in reviewed data — rather than "not a government domain for this destination",
which was false and identical to what a commercial agency got. `unconfirmable_authorities` names those
candidates and the refusal message uses them, so it no longer claims none could be *identified* when two
were. **Reporting only:** nothing is accepted for want of a marker, and a test holds the accepted set
empty. DECISIONS entry 33.

**Still not detected:** whether an accepted trusted set plausibly contains a visa authority at all. For
the ten countries with a marked domain elsewhere in government, bootstrap succeeds and the corridor
resolves against domains that cannot hold the guidance. The withheld reasons now describe it where the
ministry was seen at all; measuring it is part of item 2.

---

## Next — the direction change

### 1. Read and honour `robots.txt` — `next`

**Why:** DECISIONS entry 35. Nothing in this codebase has ever fetched it — grep finds no reference to
robots anywhere in `src/`. A project that computes a per-host politeness delay (entry 25) while ignoring
the file stating a host's own crawl policy is inconsistent on its own terms, and the posture this
project wants is *honest client*, not *anonymous client*. This is owed regardless of what it buys.

**Do:** fetch and cache `robots.txt` per host in `discovery/crawl.py` and `research/live_sources.py`,
honour `Disallow` for the declared user agent, and record a skip as its own outcome so it never reads as
"nothing found".

**Expect it to cost coverage.** A path we currently walk past becomes a refusal. That is the correct
direction, and a `Disallow` is an authority's stated policy rather than a block to route around.

### 2. Move "who to believe" out of the request path — `soon`

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
domains become something a person actually reads; and item 3 becomes a data edit rather than a regex
change.

### 3. Amend the trust rule for governments with no marker, and for Schengen — `soon`

**First, what `looks_governmental` actually is**, because its name misdescribes it and that makes the
whole rule read as flimsier than it is. Probed against adversarial hostnames 2026-08-18:

```
visa-gov.com  gov-uk.com  govuk.com  mygov.in  e-gov.in  thegov.uk
gov.sg.evil.example   immigration.gov.in.attacker.net   esteri.it.visa-help.com
    -> every one rejected
fakegov.gov   help.gov.co   visa.gov.tk   -> accepted
```

The regex only matches a marker at a **label boundary anchored to the end**, so it cannot be spoofed by
putting "gov" in a name — `gov.ica.sg` and `go.mofa.jp` are both rejected. What the three accepted ones
have in common is that they genuinely sit under `.gov`, `gov.co`, `gov.tk`: **namespaces whose registry
restricts who may register.** You cannot buy `foo.gov.sg`. So the check is not "reads as official" — it is
"sits inside a registry-controlled government namespace", which is a real, unforgeable property and
exactly the kind of thing this project's trust model wants.

**So judge it by the right standard:**

| As a test of | Verdict |
| --- | --- |
| *this IS official* (sufficient) | **Sound.** Registry-backed, zero false positives in the probe above. |
| *only these are official* (necessary) | **Wrong, measured 19 of 51.** Where a country has no government namespace there is no signal to find, so no regex can ever fix it. |
| *this is a **visa** authority* | **Does not try.** `nasa.gov` and `recreation.gov` pass as US own-government. Bounded by the cap and corroboration bar (entry 22), not by this rule. |

That is why the fix is to **add other sufficient conditions, never to loosen this one** — and why
renaming `looks_governmental` to something like `in_government_namespace` is worth doing while here.

**The tension this item must resolve, and currently ducks.** "A reviewed authority domain" was written
without saying *how the reviewer knows*, and hand-reviewing 198 countries is the manual curation the
production goal exists to remove. Four mechanisms could supply officialness without per-country
judgement, and the cheap measurement comes first:

1. **The government's own published domain list.** Where a country publishes one, that is the
   destination's own government asserting which domains are its own — this project's trust model applied
   recursively, no human taste involved. Strongest where it exists; coverage patchy.
2. **Registry (RDAP/WHOIS) organisation data.** `esteri.it`'s registrant is Italy's foreign ministry —
   authoritative registry data, not prose. **Measure coverage before committing:** GDPR redaction is
   heaviest on European ccTLDs, which is exactly the 19.
3. **TLS certificate organisation.** OV/EV certificates carry a CA-validated `O=` field, and this project
   already handles certificates (entry 12). Partial: many authorities now use DV certificates with no
   organisation. Note it needs a TLS handshake before trust is decided — closer to DNS resolution than to
   fetching evidence, but say so explicitly rather than sliding past it.
4. **Cross-vouching from an already-trusted domain.** For the ten countries that *do* have a marked
   domain, `interno.gov.it` naming `esteri.it` as the foreign ministry is the government vouching for its
   own domain — the existing `appointed_by` idea generalised. **The hole:** governments link to
   contractors, partners and news, so "linked from a trusted domain" is far too weak, and
   `ARCHITECTURE.md` says appointing a provider is human judgement never automated. This is a decision to
   argue, not a patch to apply.

**Do the measurement first** — for the 19, how many are covered by (1), (2) and (3)? It is offline-ish,
needs no search credit, and it decides whether this item is automatable or genuinely needs a human. If
most are covered, the production goal survives; if not, reviewed data is the honest answer and the review
is 19 countries rather than 198.

**Then the two problems the measurement is for:**

- **19 of 51 governments have no governmental marker in their hostname.** The amendment is an authority
  domain named in the entry 34 registry, by whichever of the four mechanisms above survives measurement
  — **never a wider regex.** Adding `.de`, `.nl`, `.it` as markers would trust every commercial site in
  those countries, and `belongs_to_destination` cannot narrow it, because for exactly these countries the
  own-TLD test is the only other signal there is. `tests/test_trust_coverage.py` asserts that trap
  directly: it checks a German visa agency is indistinguishable from the ministry on the only half that
  would remain.
- **Schengen is a definition problem, not a bug.** For short-stay visas the decision genuinely lives at
  EU level as much as nationally, and `europa.eu` passes `looks_governmental` but can never pass
  `belongs_to_destination` for any member state. "The destination's own government" is the wrong trust
  unit for a supranational regime. A reviewed supranational-domain list per member is the fix, and it
  amends the rule as stated in entry 19 and in `CLAUDE.md`, so **record a decision rather than
  patching.**

**Do first, separately, because they are corrections inside the existing rule rather than relaxations
of it:** add `gv` and `gub` as markers, and add `canada.ca` beside the `gc.ca` special case — Canada
fails only because immigration content moved and the pattern did not.

### 4. Measure the top 20 corridors against a bar committed in advance — `blocked`

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

**Blocked on:** Brave credit (`HTTP 402`). Run item 1 first so the numbers describe the posture the
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

### 5. Decide the client-side retrieval question — `soon`

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

**Reordered after the direction work**, because deploying before item 4 ships a product whose two
highest-volume corridors return no checklist, and item 2 changes what a cold request does.

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

### Confirm a blocked authority actually reads usefully — `soon`

**Why, and this item changed on 2026-08-18.** It used to say a blocked authority was named *only* when it
cost the decision, and that the US plan therefore never mentioned `travel.state.gov`. **Checking the code
showed that is wrong:** `to_destination_config` fills `unreadable_authorities` from `inaccessible_urls`
unconditionally, the extractor carries them into `unavailable_sources` whatever `decision_is_unverified`
says, retrieval-time blocks arrive separately through `RetrievalReport.failures`, and the interface already
gives any `blocked` failure with a URL the sentence *"does not permit automated retrieval"* plus a link.

So there is **no plumbing left to do**, and writing some would have been work against a problem that did
not exist. What is unverified is whether it *reads* as useful — which no test can answer.

**Do, during item 4's live runs:** read a real plan for a corridor with a blocked page whose decision
resolved elsewhere, and check the authority is named, the link works, and the sentence sits where a
traveller will see it. Also check the narrower question entry 24 left open: the two `travel.state.gov`
places were never crawled, so confirm the US corridor records that block **somewhere** rather than
silently dropping it.

**Careful:** the causality requirement from entry 32 governs whether a block may *resolve a corridor*,
never whether it may be *reported* — every block is still reported, and that must stay true.

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
shortlist, not to reproduce the model's judgement. It is no longer the fallback (entry 31), so
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
  countries are added — and note it will need `gv` and `gub` per item 3.
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
