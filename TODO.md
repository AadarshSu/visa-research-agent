# TODO

Ordered by what unblocks the most. Each item says why it matters, not just what to do, so it can be
picked up cold.

**How to read this file.** **Now** is what to pick up, in the order written — item 15 leads because a
change already on `main` changed what every adjudication sees and nothing has confirmed it live. **Next up** is what
follows it, item 3 first because its own reasoning is that nothing large should be built before it.
**Later** is real but not urgent. **Done** is finished work, kept because what building it found is
usually why the item after it exists. **Smaller things** are one-paragraph defects with no owner yet.

Status: `next` · `soon` · `later` — the label on each heading matches the section it sits in, so the two
can never disagree. There is no **Blocked** section at the moment: the 20-corridor measurement was the
only item in it, and Brave credit arrived on 2026-08-21. Give a blocked item its own section again if
one appears.

**Every open item has a number, and numbering is append-only** so that the cross-references in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) stay valid. The numbers are names, not an order: **the section
decides the order**, and a gap in the sequence means an item was finished or dropped. Finished items
keep no number — a number is a handle for pointing at work still to be done — and *Smaller things* are
one-paragraph defects rather than items.

| | | |
| --- | --- | --- |
| **Now** | 15. Re-run the verified corridors against the widened excerpt | `next` |
| | 5. Answer the challenge, and get a checklist out of France | `next` |
| | 1. Fix the post-over-nationality weighting, and trace Sweden | `next` |
| **Next up** | 3. Measure the top 20 corridors against a bar committed in advance | `soon` |
| | 2. Amend the trust rule for governments with no marker, and for Schengen | `soon` |
| | 4. Decide the client-side retrieval question | `soon` |
| | 7. Put it somewhere others can open it aka deployment | `soon` |
| | 8. Confirm a blocked authority actually reads usefully | `soon` |
| | 9. Tell "no checklist exists" apart from "we failed to find it" | `soon` |
| **Later** | 10. Try sitemaps before crawling | `later` |
| | 11. Decide whether a host that has refused everything should be skipped | `later` |
| | 12. Watch where the two deciders disagree | `later` |
| | 13. Revisit conflict detection, with claim scope | `later` |
| | 14. Detect drift in configured sources | `later` |

---

## Background

**Read [DECISIONS.md](DECISIONS.md) entries 29–35 first**, then 36–42, which are what came out of
building them. The outside review on 2026-08-18 was agreed with in full and changed the direction: the
posture, not the principle, is what has been costing coverage (entry 35); "who to believe" moves out of
the request path into committed data (entry 34); the trust rule's governmental half was measured and
fails closed for a fifth of the world (entry 33); and three things shipped that the project's own rules
argue against (entries 30, 31, 32).

**All seven review entries are now implemented or explicitly answered**, along with five more that came
out of doing the work: `robots.txt` (36), the per-run render allowance (37), the committed domain
registry (38), the reviewed override (39) and the shortlist width (40). **Left from the review itself:**
the rest of entry 35 — asking authorities for access, and the client-side retrieval question nobody has
argued yet.

**Why items 5 and 6 lead — added 2026-08-19.** Both came out of investigating why France resolves
without a checklist and why `canada/GB/GB/tourism` refuses, and neither cause was where these files said
it was. France's portal is not refusing us at all — it serves a Cloudflare challenge, and serves it for
`robots.txt` too, so no policy was ever stated (entry 41). Canada refuses because the adjudicator's
6,000-character excerpt cuts off the page that answers it.

**What the building found matters more than the list it came from.** Three separate times, a constraint
turned out not to be where the documentation said: the domain classifier was failing on countries the
search had already found; a wrong trusted set made corridors *refuse* rather than answer; and the
scorer's ranking was never binding — the ten-place window in front of it was. Prefer running a corridor
to reading a code path. Every item here assumes that.

---

## Now — pick these up in this order

### 15. Re-run the verified corridors against the widened excerpt — `next`

**Why:** DECISIONS entry 42 changed what every adjudication is shown — the head of each candidate plus a
window around the traveller's own country, at 20,000 characters instead of a flat 6,000 — and **that is a
decider change, not a tuning knob.** It is on `main` and it has never been run against the model. The
mechanism is verified offline (cached pages, 11 tests) and the underlying Canada finding was verified by
replay before the change, but which corridors now resolve, and what the model does with a longer and
occasionally discontinuous excerpt, is unmeasured.

**Do:** clear `var/cache/` and `var/corridors/`, then run the seven corridors that were verified before
this — Canada, Japan, the Netherlands, Sweden, the US, France, Singapore — and read, per corridor:

1. **`canada/GB/GB/tourism` must now resolve.** It is the corridor the change exists for. If it still
   refuses, the excerpt was not the only thing in its way and entry 42 needs a correction, not a retry.
2. **`decided_by` and the recorded heuristic scores**, for disagreements that appear or vanish. A model
   seeing three times as much text may pick differently on corridors that were already right, and a
   *changed* answer on a corridor that used to be correct is the failure mode worth catching.
3. **Whether a `[…]` gap ever misleads a reason.** The marker and prompt rule 12 exist so a cut list
   cannot read as a complete one; if a reason quotes across a gap, the marker is not doing its job.
4. **Input tokens per adjudication**, against the ~+17k characters measured on Canada's cached pages, so
   the cost is a number rather than an estimate.

**Careful:** the excerpt cannot fix a page that never contained the answer, and one of Canada's does not
— `ircc.canada.ca/english/visit/visas.asp` yields 1,144 characters saying the client needs JavaScript.
That is item 5's problem. Do not read a still-missing role as evidence this change failed without first
checking whether the page holds the answer at all.

### 5. Answer the challenge, honour every `robots.txt`, and get a checklist out of France — `next`

**Why:** DECISIONS entry 41. `france-visas.gouv.fr` was never refusing this program — it serves a
Cloudflare challenge (`cf-mitigated: challenge`, *"enable JavaScript and cookies to continue"*), and it
serves the same challenge for `/robots.txt`, so no policy was ever stated. The project's own renderer,
under our own user agent with nothing spoofed, reads the page: 221,476 bytes, 2,277 visible characters,
`blocked_hosts: []`, ~7s. Three corridors' worth of coverage sits behind this, and one sentence
currently shipping to travellers is false because of it.

**A `403` reaches neither renderer today, so turning `render_mode: on_demand` on changes nothing.**
Both paths return at the blocking branch before the render branch: `live_sources.py:377` precedes the
render at line 407, and `crawl.py:363` precedes line 387. Rendering is only ever attempted on a thin
`200`. This is the first thing to fix and the easiest to get subtly wrong.

**Do, in this order:**

1. **Separate a challenge from a refusal at the point of detection.** A `403` carrying
   `cf-mitigated: challenge`, or a body carrying `cf_chl_opt` / `/cdn-cgi/challenge-platform/`, is a
   challenge. A `401`, a bare `403`, and a `429` are refusals and keep every rule entry 18 gives them.
   Detect it from the response, not from the host, so it cannot become "France gets special treatment".
2. **Add `challenged` as its own `FailureOutcome`**, beside `blocked` and `disallowed`. It must sit
   **outside** `blocked_urls()` and `persistent_refusals()` for the same reason `disallowed` does
   (entry 36): it may never reach `inaccessible_urls` or `decision_blocking_urls`, and it may never
   resolve a corridor. France's present resolution is exactly this bug and flips between runs.
3. **Let a challenge trigger the renderer**, in both `live_sources.py` and `crawl.py`, under the
   existing per-run render budget (entry 37) and the existing trust gate — which needs no widening,
   because the challenge scripts are same-origin. A render that comes back still challenged stays
   `challenged`; it is not retried.
4. **Fix the false sentence.** `static/app.js` gives every `blocked` failure with a URL
   *"does not permit automated retrieval"*. That is untrue of a challenge, and every reason reported
   has to be true of what was seen (entries 33 and 36). A challenge reads as *an automated-access
   check stood in front of this page and we could not answer it* — and once step 3 lands, the pages we
   *did* read this way are ordinary evidence and say nothing at all.
5. **Then measure what it actually buys**, per corridor, before believing any of it: France, Singapore's
   VFS page, and `travel.state.gov`.

**The checklist is not on the page, and this is the part to read before promising one.** Measured after
rendering: `/en/demande-de-visa` carries three generic items (passport, "photocopies according to your
situation", 2 ICAO photos); `/en/assistant-visa` is a four-step wizard with a nationality dropdown;
`/en/visa-de-court-sejour` defines the visa without saying who needs one; and
`www.france-visas.gouv.fr/en/web/france-visas/india` — the top-scoring France-Visas candidate at 74.4 —
is a **404** the challenge had been hiding. So steps 1–4 make France *honest and readable*; they do not
by themselves produce a corridor checklist.

**Getting the checklist needs the wizard, and that needs its own decision entry first.** The France-Visas
assistant is a read-only questionnaire that returns published guidance, not an application — but
`CLAUDE.md` puts *form filling* on the permanent out-of-scope list, and the distinction between
"answering four questions to be shown the published rules" and "filling in an application" is exactly
the kind of thing that must be argued in writing rather than assumed by whoever is holding the
keyboard. **Do not write wizard-driving code before that entry exists.** Note it interacts with the
excerpt (entry 42): a wizard result is per-corridor by construction, so it would arrive as text nobody
else can re-derive, and it would be short enough to sit inside the head of the excerpt whatever else the
page holds.

**Careful:** the two prohibitions are unchanged and are what keep this from being circumvention — no
user-agent spoofing, and no retrying past a rate limit. And `robots.txt` outranks all of it: a
`Disallow`ed path is still not fetched, a policy that could not be read is still reported as unread
rather than as permission, and a `Disallow` still may not resolve a corridor.

### 1. Fix the post-over-nationality weighting, and find out why Sweden does not move — `next`

**Why:** DECISIONS entries 39 and 40. Widening the shortlist fixed two corridors and left two problems
standing, and they are now separable.

**The weighting bug is precise and reproducible.** For an Indian national applying from Great Britain the
scorer gives `checklist-schengen-visa-tourism/india` **113.0** and `.../united-kingdom` **73.0**. For a
consular checklist the **post** governs, not the passport: they apply at the Dutch mission in the UK. The
adjudicator correctly refuses a wrong-post page, so the corridor discards a checklist it already fetched.
Make `applying_from` outrank `passport_nationality` where a URL or link text names a post — and measure
across the verified corridors, because link scoring decides what every corridor reads.

**Sweden is unexplained.** It reads `migrationsverket.se`, fills `general_entry`, and neither widening
the window nor correcting its domain moved the visa decision or the checklist. It has not been traced the
way the Netherlands was, and it should be before anything else is changed on its account.

---

## Next up

### 3. Measure the top 20 corridors against a bar committed in advance — `soon`

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

**No longer blocked — 2026-08-21:** Brave credit is available again, so this can run. `robots.txt`
landed first (entry 36), so the numbers describe the posture the project intends to keep.

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


### 2. Amend the trust rule for governments with no marker, and for Schengen — `soon`

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

### 4. Decide the client-side retrieval question — `soon`

**Why:** DECISIONS entry 35 raises it and deliberately does **not** approve it. The traveller's own
browser can open `france-visas.gouv.fr`; a human reading a public page is not this program circumventing
a refusal. Whether the agent may then read what their session received is genuinely near entry 18's
boundary.

**Do:** write the decision either way before writing any code. It needs its own entry because it moves
page content through the client, which needs a trust argument of its own — the domain rule still has to
hold, and content arriving via a browser has not passed the checkpoints that content arriving via
`LiveSourceFetcher` has.

**Careful:** nothing here licenses spoofing or retrying. **Amended 2026-08-19:** it no longer reads
"or pointing this program's renderer at a refusal, entry 18 is unchanged" — entry 41 measured France's
`403` as a Cloudflare *challenge* rather than a refusal and allows the renderer to answer it under our
own user agent, which is item 5. That narrows this item rather than settling it: the client-side
question is about content arriving through *someone else's* session, and none of entry 41 speaks to
that.

### 7. Put it somewhere others can open it aka deployment — `soon`

**Why:** it runs on one laptop with a `.env`. The goal is a URL to share. Keep this simple — a host,
some environment variables, done. No pipelines, no orchestration; CI already runs the checks.

**Reordered after the direction work**, because deploying before item 2 ships a product whose two
highest-volume corridors return no checklist.

**The timing needs re-measuring before this is planned.** The **34.1s** figure (19.4s corridor + 14.7s
plan, `united-states/IN/IN/tourism`, both caches cleared) was taken before the domain registry and no
longer holds: the corridor phase alone measures **39–45s** now, because `corridor_queries` runs three
searches per trusted domain and the registry gives a country up to five where `destinations.yaml` gave
two. A full cold request has not been re-timed. The lever is the per-domain query count or the domain
cap, **not** the shortlist — that was measured separately and costs nothing (entry 40).

`var/cache/` and `var/corridors/` are local directories, so a disposable filesystem makes **every**
request cold.

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

### 8. Confirm a blocked authority actually reads usefully — `soon`

**Why, and this item changed on 2026-08-18.** It used to say a blocked authority was named *only* when it
cost the decision, and that the US plan therefore never mentioned `travel.state.gov`. **Checking the code
showed that is wrong:** `to_destination_config` fills `unreadable_authorities` from `inaccessible_urls`
unconditionally, the extractor carries them into `unavailable_sources` whatever `decision_is_unverified`
says, retrieval-time blocks arrive separately through `RetrievalReport.failures`, and the interface already
gives any `blocked` failure with a URL the sentence *"does not permit automated retrieval"* plus a link.

**And that sentence is false for France — 2026-08-19, entry 41.** `france-visas.gouv.fr` serves a
Cloudflare challenge, not a refusal, so nothing there "does not permit" anything. Item 5 owns the fix.
Read a real plan for a genuine refusal — `travel.state.gov` is one — rather than for France, or this
item will measure the wrong sentence.

So there is **no plumbing left to do**, and writing some would have been work against a problem that did
not exist. What is unverified is whether it *reads* as useful — which no test can answer.

**Do, during item 3's live runs:** read a real plan for a corridor with a blocked page whose decision
resolved elsewhere, and check the authority is named, the link works, and the sentence sits where a
traveller will see it. Also check the narrower question entry 24 left open: the two `travel.state.gov`
places were never crawled, so confirm the US corridor records that block **somewhere** rather than
silently dropping it.

**Careful:** the causality requirement from entry 32 governs whether a block may *resolve a corridor*,
never whether it may be *reported* — every block is still reported, and that must stay true.

### 9. Tell "no checklist exists" apart from "we failed to find it" — `soon`

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

---

## Later

### 10. Try sitemaps before crawling — `later`

**Why:** within already-approved domains, `sitemap.xml` gives the full URL inventory for scoring without
the politeness-heavy two-hop crawl. And the crawl has a known hole: its 40-page budget is spent entirely
at depth 0 (see *Smaller things*), so depth-2 discovery — where Japan's checklist was found — never
happens for a multi-domain destination.

**Do:** check first whether the seven verified corridors' chosen pages appear in their domains'
sitemaps. If most do, the crawl becomes a fallback rather than the primary mechanism. Cheap to check,
and worth checking before optimising the crawl further.

### 11. Decide whether a host that has refused every request should be skipped — `later`

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

**And do item 5 before this — 2026-08-19.** France looked like the strongest case for a host-level skip:
eight `france-visas.gouv.fr` paths refused in one run while eight more took shortlist places and refused
too, so 15 of 25 places were read. Measured, the right answer was not to skip the host but to answer its
challenge — and behind the challenge at least one of those "blocked" URLs was a plain **404**, which a
host-level skip would have permanently hidden rather than revealed. A skip is inductive; reading is not.

**Also still overstated:** `pages_fetched` is the shortlist length rather than the number of pages that
were readable, so it now reports up to 25 read when fewer are usable.

### 12. Watch where the two deciders disagree — `later`

**Why:** `decided_by` says which decider chose, and the heuristic's score is kept beside the model's
choice. That divergence is free evidence about both, and nobody is reading it.

**Do:** on a corridor run, note every role where the model chose a page the heuristic did not rank first.
A pattern is either a lexicon gap worth closing or a model error worth prompting against. Four corridors
currently disagree on `general_entry` and `visa_decision` most.

**Careful:** do not tune the lexicon to agree with the model. The heuristic's job is to build a good
shortlist, not to reproduce the model's judgement. It is no longer the fallback (entry 31), so
its remaining jobs are the shortlist and the offline baseline.

### 13. Revisit conflict detection, with claim scope — `later`

**Why:** entry 30 deletes the unverified `conflicts` field. That removes an alarming unchecked signal; it
does not answer the underlying question, which is real — official sources do disagree.

**Do:** record the population each claim applies to, and compare only same-scope claims — the exact gap
that killed the previous attempt. Leave the visa decision out of comparison; it already has stronger
guards. Restrict to quantitative rules (validity periods, stay lengths, processing times) where a wrong
flag costs a caveat rather than alarm. Full post-mortem in [DECISIONS.md](DECISIONS.md) entry 6 — read it
before starting.

### 14. Detect drift in configured sources — `later`

**Why:** every source already stores a content hash, so a changed government page is detectable and
currently ignored.

**Do:** on a hash change, mark the source rather than refusing — government pages change whitespace
constantly. **Never** auto-rediscover and swap a role-bearing source: that is the wrong-checklist failure
with the human removed. A persistent failure over several runs is the honest trigger to propose a
replacement.

---

## Done

### ~~Stop the adjudicator's excerpt cutting the answer off~~ — **done 2026-08-21**

`DEFAULT_EXCERPT_CHARACTERS` is 20,000 and no longer a flat head-of-page slice: `anchored_excerpt` shows
the head of each candidate plus a 3,000-character window centred on every later mention of the
traveller's own nationality or residence, marks what it left out with `[…]`, and prompt rule 12 tells the
model what the mark means. 11 new tests, all offline. DECISIONS entry 42.

**What it was costing.** `canada/GB/GB/tourism` ranked the right page first, fetched it, and refused: the
sentence answering a British traveller sits at offset 8,597 of 16,465 and the excerpt ended at 6,000,
mid-alphabet at "Morocco". So **whether a corridor resolved depended on where the traveller's nationality
fell in a list** — India at 5,325 answered, every visa-exempt nationality not — and entry 40's "Canada:
every role filled" turns out to have been an Indian-passport result that did not generalise.

**Anchoring is not what makes it affordable, and the file should not pretend otherwise.** Over the 27
cached `canada.ca`/`gc.ca` pages, packet text goes 84,704 → 153,862 characters; a flat 20,000 costs
153,852, because only 2 of the 27 exceed the budget. Anchoring is what stops the new number from being
another fixed offset: on the 50,000-character visitor-visa PDF a US traveller's second window sits at
24,449, which a flat 20,000 cuts.

**Not run live** — that is item 15, and it is the first thing in **Now** for that reason.

### ~~Move "who to believe" out of the request path~~ — **done 2026-08-18, for 40 of 198 countries**

`config/authority_domains.yaml` is generated by `visa-discover registry`, read by
`discovery/registry.py`, and consulted by `AutomaticDestinationService` in place of a live bootstrap.
The trust rule is untouched — `auto_trusted_domains` still decides every domain — only *when* it runs
moved. 13 new tests, all offline. DECISIONS entry 38.

**Verified live:** New Zealand, never configured, resolved a visa decision, a document checklist, an
application route and a general-entry page from committed domains, with **0 searches** spent in the
service where 4 went on bootstrap before.

**Reading the file is what paid for it**, and it found three things:

- The 5 refusals (AT, BE, DE, DK, SE) are entry 33's known failure and now name their own fix in
  `unconfirmable` — `gv.at`, `auswaertiges-amt.de`, `nyidanmark.dk`, `migrationsverket.se`.
- **Twelve countries are confirmed *and wrong*** — the Netherlands trusts only its business portal,
  Italy trusts two ministries that are not the foreign ministry, Canada trusts five `gc.ca` domains
  while IRCC's content lives on the unconfirmable `canada.ca`. These corridors do not refuse; they
  resolve against domains that cannot hold the answer. Entry 33 predicted this and could not measure it.
- **The cap spends slots on the wrong parts of a government**, which nobody had predicted. India's five
  include two United States missions; South Korea's include a county; Spain's put the prime minister's
  office ahead of the foreign ministry. `_trust_priority` falls back to alphabetical among domains with
  no hostname hint, and for a large government that is arbitrary.

**158 countries are unbuilt** and refuse with a message naming the command. That is 632 searches of
quota, not work: `visa-discover registry` resumes, and `--only FR,DE` rebuilds any subset.

### ~~Read and honour `robots.txt`~~ — **done 2026-08-18**

`research/robots.py` fetches one policy per **origin** and re-reads it after 24 hours;
`discovery/crawl.py` consults it before every crawled page and after every redirect, and
`research/live_sources.py` before every source and every meta-refresh forward. Matching implements
RFC 9309 directly — `urllib.robotparser` was tried and rejected, because it supports neither `*` nor `$`
and so obeys none of the rules `www.gov.uk` publishes. 32 new tests, all offline. DECISIONS entry 36.

**Three things came out of building it that the entry above did not anticipate:**

- **A skip needed to be its own outcome, and `disallowed` is it.** Otherwise a page nobody asked for is
  indistinguishable from a page that did not exist — the failure entry 18 names. The corridor reports it in
  its own note rather than the generic "could not be read" one, because only the first failure per host
  survives that note and a `Disallow` could be masked by an unrelated `404` on the same site.
- **A boolean verdict produced a false reason, and that had to be caught.** The first version collapsed
  every non-answer into "disallowed", so every **unreachable** host was described as *"its robots.txt does
  not permit this client"* — a sentence about a policy nobody had read, and the same class of falsehood
  entry 33 had just removed from `withheld_domains`. Now: `5xx` or oversized is `UNREADABLE`, a parsed rule
  excluding us is `DISALLOWED`, and a transport failure **raises** so the caller diagnoses the host.
- **A `Disallow` is reported but may never resolve a corridor.** `disallowed_urls()` is outside
  `blocked_urls()` and `persistent_refusals()`, so it reaches neither `inaccessible_urls` nor
  `decision_blocking_urls`. A `403` was observed on the page; a `Disallow` covers a path we chose not to
  request, and letting it stand in would widen entry 32's exception by a route entry 32 never considered.

**Measured live, six corridors, 2026-08-18 — entry 36 has the table.** The cost was almost nothing:
France lost one news listing, China lost two portals already answering `502`, and Japan, Singapore,
Vietnam and Brazil lost nothing. **The negative result matters more:** France and the US answer `403` to
their own `robots.txt`, so this step buys nothing on the two corridors that motivated entry 35 — it is a
WAF there, not a stated policy. Item 3's twenty corridors still decide the size of that limit.

### ~~Commit the 51-country trust-rule test~~ — **done 2026-08-18**

`tests/test_trust_coverage.py`, 7 tests, offline. Freezes the 19 failures so a change is a visible diff,
asserts every one fails on the governmental half rather than the TLD half, and guards `countries.yaml`
against another country acquiring a governmental marker in its `tlds` unreviewed. Verified the tripwire
fires by simulating the forbidden fix.

**It also refined the finding, and the refinement matters** — see DECISIONS entry 33's table. The 19 are
two different failures. Nine (AT, BE, DE, DK, FI, NL, NO, SE, UY) have no marked domain at all and refuse
outright. Ten (CA, CL, CZ, GR, HU, IE, IT, PT, RO, RU) **do** have one, so bootstrap *succeeds* and builds
a trusted set that cannot contain the visa guidance — quieter and worse, because nothing reports it. Canada
is the sharpest: `gc.ca` still passes, but the content moved to `canada.ca`. Item 2 is what fixes both;
its marker corrections (`gv`, `gub`, `canada.ca`) shrink the first group on their own. **It also
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
ministry was seen at all; it is measured in DECISIONS entry 38's table.

### ~~Find out why a corridor refuses on a domain it can now read~~ — **done 2026-08-18**

Traced, and the answer was not in the scorer's rules. `DEFAULT_SHORTLIST_SIZE` was **10** — the number
of pages the model is allowed to see — which made the heuristic the effective decider for every corridor
whose right page sat eleventh. Changing only that number to 25: **Canada and Japan went from refusing to
filling every role**, the Netherlands gained its checklist, Sweden did not move. No latency penalty
(fetching is concurrent; 44.5s→39.3s and 45.2s→41.7s, both within noise) and adjudication input roughly
doubles to ~19k tokens. DECISIONS entry 40; a test pins the width.

**Three things it did not fix:** Sweden and the `/india`-over-`/united-kingdom` weighting (entry 39),
which are item 1, and English-only scoring, which is known problem 13 in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) rather than an item here.

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
  **seed** cap would restore it without lowering `maximum_pages`, which must not be lowered. See also item 10,
  the sitemaps one, which may be the better answer.
- **Nothing validates `countries.yaml` against a `tlds` entry that widens trust.** Adding `gov` to a
  country's `tlds` would change what is trusted with no review of the rule itself. Bounded now by the cap
  and the corroboration bar (entry 22), but the data is still where a mistake would not be caught. `tests/test_trust_coverage.py`
  is the natural place to add a guard.
- **Missions named by city are still unrecognised** — Singapore's `london.mfa.gov.sg`. Folded into the
  ranking work: path-based mission detection has to solve the same problem, since the residence country is
  not always a host label. Add city names to `countries.yaml` beside `host_labels`.
- **Cache invalidation on rule changes.** After changing what counts as usable, cached entries still serve
  the old result until the TTL expires. This cost real debugging time — a fix appeared not to work until
  `var/cache/` was cleared. Consider keying entries by a rules version.
- **`is_bare_public_suffix` is a heuristic**, not a real public suffix list. It correctly rejects `gov.sg`,
  `gov.uk`, `go.jp`, `gouv.fr` and `co.uk` while allowing `usa.gov` and `service.gov.uk`, but review it as
  countries are added — and note it will need `gv` and `gub` per item 2.
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
  on it until a corridor actually needs it. **If it is ever measured, do it on code from 2026-08-18 or
  later:** before then the render allowances were process-lifetime rather than per-run, so a long-running
  server stopped rendering after 17 pages and reported the pages it skipped as unreadable (entry 37). Any
  earlier measurement of rendering's value would have been reading that, not reading rendering.
