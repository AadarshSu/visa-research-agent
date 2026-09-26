# TODO

Ordered by what unblocks the most. Each item says why it matters, so it can be picked up cold.

**Now** is what to pick up, in the order written; **Next up** follows; **Blocked** waits on something
external; **Later** is real but not urgent; **Done** is a one-line index of finished work, whose
reasoning is in DECISIONS; **Smaller things** are one-paragraph defects with no owner yet.

**Numbering is append-only**, because PROJECT_HANDOFF, DECISIONS and code comments cite item numbers.
The numbers are names, not an order: the section decides the order. Finished items move to *Done*.

## The four goals — the owner, 2026-09-23 (entry 182)

Unordered, as the owner gave them. Until the owner orders them, entry 148's order is the tie-break:
correctness, then optimisation, then expansion. A fifth goal, model calls paid through Ofself
Personas, is done and is the route from now on (entry 188).

| goal | where it stands | items | waits on |
| --- | --- | --- | --- |
| **~30s a corridor, with information on screen while it runs** | A fresh request is ~55s: ~25s research, ~29s plan (entry 171); the graded runs of 2026-09-25 took 35–70s. Each step now shows on screen as it starts (entry 226). A repeat within 24h reuses the plan draft, not timed live | **57**, **58** | nothing external |
| **Hosted at a URL** | Runs on one laptop. Ofself signs users in (required since entry 191) but does not host; the stores are local files | **7**, **20** | choosing a host; item 7's refusal-storing decision |
| **Most corridors accurate and useful** | Item 63's second round: decisions 7 of 10, checklists 5 of 10 (entry 214); the owner's verdicts in entries 216 and 224. Nothing in the repo measures *right*, only *answered* (known problem 26) | **63** | the owner's own checking (entry 68) |
| **55 → 100+ countries** | 55 have a registry row and a rebuilt store; 143 have none, and the page offers all 198 (known problem 23) | **64**, **2** | search credit only |

**Offline cost is not the constraint — the owner, 2026-09-23 (entry 184).** Build time and a higher
one-time cost are acceptable for anything that makes each live request better. Prefer an offline fix
to a per-request one.

**Settled, do not re-propose without a new argument:** search stays on every corridor, purpose query
included (entries 159, 160); refusing on a corpus miss is dropped (entry 173); the corpus holds what
every traveller shares and live search fetches what this traveller needs (entry 148), which is why
items 35, 47 and 49 are parked.

**One habit matters more than the list.** A constraint has repeatedly turned out not to be where the
documentation said — [CORRECTIONS.md](CORRECTIONS.md) has over two hundred and fifty rows. Prefer
running a corridor to reading a code path, and measure a proposed fix before implementing it.

| | | |
| --- | --- | --- |
| **Now** | 57. Stream the plan to the screen — progress shipped; content is the owner's call | `next` |
|  | 64. Expand from 55 countries to 100+ — ask the owner before a batch | `next` |
| **Next up** | 61. Decide whether a corridor's five renders should grow | `soon` |
|  | 2. Reviewed authority domains for governments with no hostname marker | `soon` |
|  | 4. Decide the client-side retrieval question | `soon` |
|  | 7. Put it somewhere others can open it | `soon` |
|  | 20. Make the stores substrate-swappable and durable | `soon` |
|  | 55. Take the traveller from Ofself's shared identity, through one adapter | `soon` |
|  | 71. Take the city the traveller lives in, and name the one post that serves them | `soon` |
|  | 59. Guard the 272K-token price threshold | `soon` |
|  | 58. What is left of model-call cost and research latency | `soon` |
|  | 73. Tell the traveller exactly why their corridor was refused | `soon` |
|  | 72. Improve the interface | `soon` |
|  | 63. Make most corridors return accurate and useful information | `ongoing` |
| **Blocked** | 67. Test ranking by embeddings of stored page text — on OpenAI credit | `blocked` |
| **Later** | 69. Read scanned PDFs — for ranking first, as evidence only after a decision | `later` |
|  | 49. Walk the mission family to the traveller's post — stopped by entry 148 | `later` |
|  | 35. Finish the Netherlands' family reservation — parked by entry 148 | `later` |
|  | 47. Find out how much of the world the family detector cannot see — parked | `later` |
|  | 46. Decide what to do about a refusal served as `HTTP 200` | `later` |
|  | 27. Decide whether a hosted scraping service may be used, for corpus discovery only | `later` |
|  | 10. Try sitemaps before crawling | `later` |
|  | 11. Decide whether a host that has refused every request should be skipped | `later` |
|  | 12. Watch where the two deciders disagree | `later` |
|  | 13. Revisit conflict detection, with claim scope | `later` |
|  | 14. Detect drift in configured sources | `later` |

---

## Now — pick these up in this order

**Reordered by the owner, 2026-09-26.** Item 57 first; expansion (64) follows and asks the owner
before a batch. Item 63 moved to *Next up* as ongoing work. Items 60 (Fast mode) and 65 (GPT-6 Sol)
were removed.

### 57. Stream the plan to the screen as it is written — `next`, **progress shipped (entry 226); the rest is the owner's decision**

**Done 2026-09-26 (entry 226):** `POST /visa-plans/stream` sends each step's name as it starts —
search, gather, choose, read, check, collect, write — and then the whole validated plan, and the page
shows the steps ticking off with elapsed seconds. Seen live: eight steps over about a minute.

**Open, for the owner — whether anything more than progress may appear before the plan is whole.**
Nothing streamed may show a claim the finished plan could still drop or refuse, the visa decision
above all (entry 6). Candidates, safest first:
- **What research found, as facts about the run:** the official sites searched, or the pages chosen
  to read, with their links. True whatever the plan later says, but a traveller may read a listed page
  as the answer.
- **The plan's sections as each is final.** Needs the validators split so a section can be checked
  alone; the decision, which the whole plan's grade depends on, would still come last.
- **The model's text as it is written.** The plan call uses strict structured output
  (`with_structured_output`, `json_schema`), so this is partial JSON through LangChain or Personas,
  and a refusal can arrive after text has appeared. The first token comes 7–15s into the call (entry
  177).

### 64. Expand from 55 countries to 100+ — `next`, **ask the owner before a batch**

**Why.** It is the owner's goal. The page offers 198 destinations and refuses 143 (known problem 23).

**What adding a country takes — the three stages of entry 68.**
0. **Ask the owner first**: which countries, and how many. Pick by traveller volume, as batch 1 did
   (entry 67).
1. **Reachable:** a row in `config/authority_domains.yaml`, from `visa-discover registry`. Where the
   rule cannot confirm a domain, ask Wikidata about the *organisation*, then read its `P856`/`P17`,
   and review by hand, marking the evidence tier (entries 67, 110, 111). Item 2 covers governments
   with no marker; the rule itself never bends.
2. **Resolves:** a corpus and page-text index from `visa-discover corpus --country XX`, then run
   corridors and read every refusal's reason, as stage 2 of batch 1 did (entry 70).
3. **Fast:** the corridor answers from the store without crawling.

**Cost, as arithmetic, not measured.** The registry sweep is ~4 searches a country, ~$3 for all 143.
Corpus builds were 42–56 queries and ~22 minutes a country two at a time in the 2026-09-25 rebuild,
so fifty countries is ~$12 and ~10 hours. No model cost to build; stage-2 corridors cost search only.

---

## Next up

### 61. Decide whether a corridor's five renders should grow — `soon`

**Settled already.** EUR-Lex pages may reach AWS's challenge-token host (entry 201). Allowing
Cloudflare's challenge script was measured and not shipped: 6 of 7 Cloudflare pages still refused our
headless browser, and passing would mean disguising the client (entry 202). An interactive check — a
checkbox or a puzzle — is a CAPTCHA and stays out of bounds. The same five renders now go to the most
promising pages first (entry 212).

**Open: whether five should grow.** France's corridors left 14 of 17 challenged pages unrendered
because the five were spent (entry 179). An answered challenge costs 4–13s and a failing one 20s.
Nothing yet shows the extra pages change an answer. **Before shipping**, run France `BD/AE` and a
Liechtenstein corridor several times in each arm, cache warm in both (entry 136), and count roles
rather than pages.

### 2. Reviewed authority domains for governments with no hostname marker — `soon`

**Done:** the Schengen half — the EU may answer a member's visa decision (entry 201); every one of
the 55 rows carries a confirmable domain (entries 110, 111); Germany's `diplo.de` took its corpus
from one host to 87 (entries 107, 108). Checked 2026-09-02: all corpora carry their current domains,
so there is no Germany-shaped win left among the 55.

**What is left** is the rule question for new countries (item 64): governments whose hostnames carry
no marker. **Never widen `GOVERNMENT_PATTERNS`** — adding `.de` or `.nl` would trust every commercial
site there, and for those countries the own-TLD test is the only other signal
(`tests/test_trust_coverage.py` asserts the trap).

**What `looks_governmental` is.** It matches a marker only at a label boundary anchored to the end,
so it cannot be spoofed (`visa-gov.com`, `gov.sg.evil.example` are rejected). It is a sound
*sufficient* test — it means "inside a registry-controlled government namespace" — and a wrong
*necessary* one. So add other sufficient conditions; never loosen this one.

**How to supply them, measured (entry 66):**
- **TLS certificate organisation** — names the authority for 9 of 16; yields a name, not a verdict,
  and a person confirms it.
- **Wikidata** — ask about the organisation, then its `P856`/`P17` (entry 110). `unconfirmable` is
  what a search turned up, not a shortlist of the real domains.
- **RDAP** — dropped: 1 of 16, and 13 of the 16 ccTLDs run no RDAP.
- **A government's own published domain list** — unmeasured; matters only where the others fail.
- **Cross-vouching from a trusted domain** — too weak alone (governments link to contractors); a
  decision to argue, not a patch.

A marker added to `GOVERNMENT_NAMESPACE_LABELS` **must** also be in `trust.SUFFIX_MARKER_LABELS`, or
trusting one authority trusts its whole government (entry 65, asserted by a test). A rule change
reaches nobody until the affected registry rows are rebuilt.

### 4. Decide the client-side retrieval question — `soon`

DECISIONS entry 35 raises it and deliberately does **not** approve it. The traveller's own browser can
open a page this program may not read; whether the agent may then read what their session received is
near entry 18's boundary. **Write the decision either way before any code** — content arriving through
a browser has not passed the checkpoints `LiveSourceFetcher` applies, and the domain rule must still
hold. Nothing here licenses spoofing or retrying.

### 7. Put it somewhere others can open it — `soon`

**Why:** it runs on one laptop with a `.env`. Keep it simple — a host, some environment variables. CI
already runs the checks. Plan it with item 20: `var/cache/`, `var/corridors/`, `var/corpus/`,
`var/pagetext/` and `var/plans/` are local directories, so a disposable filesystem makes every
request cold.

1. **Prefer a host that keeps a disk and a long-running process.** Ofself provides sign-in, not
   hosting, as far as its documentation shows (entry 180); ask Ofself before choosing.
2. **Secrets:** the model route's (`PERSONAS_*`, `OPENAI_MODEL`), `SEARCH_API_KEY`, and the sign-in
   ones — `PARADIGM_CLIENT_ID`, `PARADIGM_API_KEY`, `SESSION_SECRET`, plus `PARADIGM_REDIRECT_URI`
   (registered on the app) and `SESSION_COOKIE_SECURE=true`.
3. **Chromium** (~150MB plus system libraries) for `render_mode: on_demand`, or accept that some
   countries refuse without it.
4. **Access:** a plan already needs an Ofself session (entry 191); while the app is in incubator
   mode, the allowlist decides who may sign in. There is no per-user rate limit.
5. **Say it on the page:** official guidance with citations, promising nothing about correctness or
   currency.

**Decide first — the owner's call (entry 151).** A refusal is never stored and a resolution is kept
three weeks, so behind a public URL every refused request is retried by the next traveller until one
run resolves, and that run is served to everyone. Keep it, store refusals briefly, or require two
agreeing runs. The same store freezes what was said: the web app once served a 16-day-old corridor
that never named the London embassy a fresh run names (entry 152).

**Do not** deploy with `source_mode: fixtures`: it knows only Singapore.

### 20. Make the stores substrate-swappable and durable — `soon`

**Do:** put the corpus, the source snapshots and the corridor resolutions behind their existing
`load`/`store` protocols with a networked implementation. Add a weekly refresh job — a conditional
`GET` over every stored URL, cheap because most answer `304`, and where a `404` or an off-domain
redirect flags the country.

**Three things right today and easy to lose in a migration:**
1. **A row records when the evidence was retrieved, never when it was written** (entry 4).
2. **Past `source_maximum_stale_hours` a stored page is refused**, whatever the store.
3. **A hash change marks a source and never auto-swaps a role-bearing one** — item 14.

`content_hash` is already over the *cleaned* text; do not add a second hash over raw bytes.

### 55. Take the traveller from Ofself's shared identity, through one adapter — `soon`

**Why — the owner, 2026-09-15.** This app is to be one app in Ofself, whose apps share one identity
structure per person. Integrating should be **one module mapping their schema onto ours**. The design
is in [CRUX.md](CRUX.md), argued in entries 180 and 181; platform surprises are in
[OFSELF_FEEDBACK.md](OFSELF_FEEDBACK.md).

**Built and seen working.**
- **The seam:** `create_visa_plan` asks an injected `TravellerSource` (`api/traveller.py`); the
  country check lives in `api/countries.py` and accepts alpha-3 codes. Discovery never sees the
  profile — only the `Corridor` codes.
- **The adapter** `api/ofself.py`: `passport_nationalities` reads `work-authorization.citizenships`;
  `traveller_defaults` reads `travel-document`, `travel-plan` and (only to resolve a plan's
  candidate) `place`. Errors distinguish a lost grant (`OfselfAuthorizationLost`) from an
  unavailable service (`OfselfUnavailable`), so a broken answer is never read as an empty one. Run
  live against sandbox user `66a3241b-5130-4ca9-9ce7-baaa69f84745`.
- **Sign-in** `api/signin.py`: `/oauth/login` → Ofself's authorize page → `/oauth/callback`, which
  trusts only the `sid_code` exchange (`POST /api/v1/auth/session/exchange`) for the user id. The
  session is one HMAC-signed cookie (`SESSION_SECRET`), 12 hours. The owner signed in for real on
  2026-09-17 as `43b82f83-66c4-449b-a9ce-eb1f690c433b`; the grant expires **2026-10-17**. A lost
  grant now ends the session. `sid_code` is redacted from uvicorn's access log.
- **The page:** signed in, passport, residence, destination and purpose start empty and are filled
  from Ofself as defaults the traveller confirms; one statement above the form says whether Ofself
  filled anything. `.claude/launch.json` has `visa-research-agent-signin` on port 8000.
- **Registration:** `.paradigm/secrets.toml` holds the CLI's binding (gitignored); the app's key is
  `PARADIGM_API_KEY` in `.env`. The DLR is published (spec version 5) and the owner re-authorised;
  `crux review` passes all five criteria, 13 of 16 checks. Readiness is capped at 2 of 5 because level
  3 needs a graph write, which rule 6 below forbids — accepted deliberately (feedback 5.6).

**Left to do.**
- **See the form fill from live data:** put real `travel-document` and `travel-plan` records in the
  owner's account.
- **Check authorisation twice per request** — before reading, and before returning a plan, since a
  plan takes ~55s. Handle `EP_NOT_FOUND`, `EP_REVOKED`, `EP_PAUSED`, `EP_EXPIRED` and legacy
  `NO_AUTHORIZATION`; none may fall back to `DEFAULT_TRAVELLER_PROFILE`.
- **Revocation:** our session is our own cookie, so revoking on Ofself logs no one out here. Ofself
  fires `session.revoked` to a webhook, which needs item 7's public host. Record what the exchange
  returns on the next real sign-in.
- **Stop keeping plan drafts past their reuse window.** `FilePlanStore` never deletes, and a draft
  holds the whole `TravellerProfile`.
- The authorize page echoes no `state`, so a callback cannot be tied to its login; the pending cookie
  refuses a browser that never started. Cannot be closed from this side.

**Six rules an adapter must not lose.**
1. **Read only fields that select guidance; drop the rest.** `build_research_packet` sends the whole
   profile to the model, so any field added to `TravellerProfile` goes to a third party on every
   plan. Keep `StrictModel`'s `extra="forbid"`.
2. **A passport type the program cannot research is refused, never coerced** to `ordinary`.
3. **A traveller with more than one passport chooses; the adapter never picks.** Residence likewise —
   another app's record is a default to confirm, never the corridor.
4. **A missing deciding field is asked, never defaulted** — the anonymous form's default traveller
   must not answer someone else's corridor.
5. **After the adapter a country is an ISO alpha-2 code.**
6. **Nothing is written back without a decision entry.** A plan is a rendering, never a stored fact
   (entry 44); `travel-requirement` rows are never read as evidence. `fact` nodes are never evidence.

### 71. Take the city the traveller lives in, and name the one post that serves them — `soon`

**Why — the owner, 2026-09-26.** Where a traveller applies often turns on where in a country they
live: South Korea splits India between New Delhi, Mumbai and Chennai; most destinations take UK
applications only in London. The aim is **the one post or centre that serves this traveller**, not a
list of every post.

**Decided (entry 225):** the traveller gives a **city** instead of a country of residence, and the
country is derived from it.

**To build on:** plans already notice ("the profile does not provide a city"); mission pages usually
publish their jurisdiction; `mission_labels` recognises posts by city (entry 134); Ofself may hold
the city (item 55).

**Bounds.** The city is traveller input, never inferred. A post's jurisdiction must come from a page
that states it, under the usual trust rules; where none does, the plan names the posts and asks.
Nothing per city is stored as an answer (entry 44).

**Open:** where the city-to-country data comes from, and ambiguous names (London, Ontario; Hyderabad)
— a city with no reference data is refused, never guessed; matching a city to jurisdiction lists that
name states; whether the corridor key gains the city or the post it resolves to (it splits the
corridor store and the plan reuse key, entry 178); what Ofself supplies.

### 59. Guard the 272K-token price threshold — `soon`

**Why.** OpenAI bills a request over 272K input tokens at 2× input and 1.5× output for the whole
request (entry 167). Nothing caps a selection packet as a whole; Canada's was ~92K after entry 170,
and entry 195's cut has since reduced every packet. The other calls stay below it by arithmetic.

**Open — measure first:** how close any country comes (rebuild the largest pools offline with
`contention_for`); what a guard should do — silently dropping candidates is not an option
(`selection.py`'s docstring); whether to warn near it from `var/usage/`.

### 58. What is left of model-call cost and research latency — `soon`

**Where it stands.** ~55s a fresh request, ~25s of it research (entry 171). Every model call is
logged to `var/usage/model-calls-YYYY-MM-DD.jsonl`, every stage's seconds to the recall log's
`phase_seconds`. The selection cut (entry 195) is done.

**Cost, none decided:**
- **A cheaper model for selection only** (~63% of the bill). Grade it with entry 170's
  selection-only A/B; a failed selection may fall back to the heuristic (entry 31 governs the
  decider, not the selector).
- **Trim the roles call's packet**, as entry 170 trimmed selection's.
- **Store a refusal briefly** (entry 151) — a freshness question as much as a cost one.
- **Entry 146's reusable country-stable packet** waits for traffic.

**Latency, none decided** — means over five corridors (entry 171): roles 8.2s, selection 6.6s,
search 3.5s, crawl stage 3.2s, fetch 2.7s.
- **Overlap search with the fetches** rather than blocking on it.
- **Find out what `fetch` is made of** before touching it.

**Grade any change on several runs and price it in both seconds and dollars** (entries 144, 145).

**Carried over:** should `visa-discover corridor` write back to the corpus (it would contaminate
`--runs` comparisons)? Corpus eviction is designed and unbuilt. A dead pinned page must refuse the
corridor rather than silently degrade.

### 73. Tell the traveller exactly why their corridor was refused — `soon`

**Why — the owner, 2026-09-26.** Every refusal lands under the same "No verified plan / Evidence
unavailable" heading (`renderRefusal` in `static/app.js`), and the sentence under it is whatever the
exception said (`str(exc)` in `resolve_destination`, `api/routes.py`). A traveller cannot tell "we
have not built this country yet" from "its government refused our reader" from "our model call
failed — try again". They call for different actions: pick another destination, open the named page
themselves, or retry.

**What already exists.** The cause is typed — `RefusalCause` in `discovery/models.py`
(`decision_not_found`, `no_candidates`, `adjudication_failed`, `run_raised`, and the resolved kinds),
from `outcome_cause()` — but it reaches only the recall log and `visa-discover audit`, never the
response. Refused pages are already named once per authority (item 54, entry 155).

**Do.**
1. **Read what each cause says today** — collect the refusal `message` for one corridor of each cause
   before writing new text; some may already be specific.
2. **Send the cause with the refusal** (`detail.cause`), and give each its own heading and next step
   on the page. At least: *not built yet* (no registry row or corpus — known problem 23, which also
   wants unbuilt countries marked before they are chosen); *the government's pages refused us*
   (blocked/challenged, with the links); *no official page answered the question*; *the check could
   not run* (`adjudication_failed`, a provider out of credit — say retrying may answer); *an internal
   fault*.
3. **Every sentence must be true of the cause that applies** — the same bar as `withheld_domains`
   (entry 33). "Could not be confirmed" never becomes "does not exist", and a failed model call never
   reads as a missing page.

**Absorbs** the *Smaller things* entry "a failed model call reads to the traveller as a missing
page". **Does not change** what a plan may conclude, only how a refusal is explained — anything that
would turn a refusal into an answer is the owner's decision (entries 206–209).

### 72. Improve the interface — `soon`

**Why — the owner, 2026-09-26.** Asked for as a goal; the specifics are not yet set. **Ask the owner
what to change first** — layout, reading order of the plan, mobile, the country picker — before
building. Related work already on the list: what may stream before the plan is whole (item 57), the
refusal screen (item 73), marking the 143 unbuilt destinations (known problem 23). The page is
`templates/index.html`, `static/app.js`, `static/styles.css`; test changes in a browser, not only with
`pytest`.

### 63. Make most corridors return accurate and useful information — `ongoing`

**The bound.** Correctness is checked by the owner, outside this repository (entry 68). Do not build a
truth set, grader or accuracy metric without asking. This item may measure what corridors *answer*,
reported with known problem 26's caveat.

**Where it stands.** Ten destinations — Australia, New Zealand, China, South Korea, Thailand,
Vietnam, Turkey, South Africa, Spain, Switzerland — for `IN/IN`, twice each. First round (entry 205)
found a wrong "no visa" from a flattened table, fixed. Second round (entry 214): decisions 7 of 10,
checklists 5 of 10. The owner's verdicts and what was fixed after are in PROJECT_HANDOFF's *Next
session*. What changed in the plan along the way, all on the owner's decisions: rules 8f–8j (entries
206–209, 218), checklists linked rather than copied (211, 213), renders ordered by promise (212).

**Open.**
- South Korea's rare wrong checklist — *Smaller things*.
- About 30 of the rebuilt countries have had no corridor run.
- **Proposed, not measured:** de-duplicate near-identical series before the selector's cut —
  Australia once read seven quarterly reports while its step-by-step page was cut.

---

## Blocked

### 67. Test ranking by embeddings of stored page text — `blocked` on OpenAI credit

Personas offers chat calls only (entry 188), so this waits on an OpenAI top-up or another embeddings
source the owner approves.

**Why.** What separates the model selector from the heuristics is judgement, not information: same
inputs, 83% of answers against 53–60% (entry 183). Embeddings match meaning, so they may rank "what
to bring" or another language where keywords cannot. They cannot help a page with no stored text, and
may not separate near-identical pages for different travellers.

**Build offline:** embed every stored body in `var/pagetext/` (~$1 with `text-embedding-3-small`),
chunked, stored beside the text index — **ranking input, never evidence** (entries 78, 83).

**Measure offline** against `oracle/selection_oracle.yaml`: as a selector (bar: the model's 83%) and
as the selector's cut (bar: `fusion_order`'s 80.0 of 90, via `var/selection-replay-2026-09-24/`).
Record per-request time. Any adoption is a recall change, graded live over several runs.

---

## Later

### 69. Read scanned PDFs — for ranking first, as evidence only after a decision — `later`

**196 PDFs score for a role on their link alone and cannot be read:** 95 with an empty text layer
(Thailand's fee tables, Czechia's fees, Swiss fee sheets, Norwegian checklists) and 101 that fail to
parse, mostly IRCC's dynamic Adobe forms. None holds an oracle answer.
- **Ranking** — text recognition at build time into `var/pagetext`, which ranks and never speaks.
  Low risk.
- **Evidence** — needs a decision entry first: a misread digit is a wrong fee with a citation, and
  nothing downstream can catch a recognition error.

**First step:** count, offline over `var/recall`, how often a corridor's selection includes one.

### 49. Walk the mission family to the traveller's post — `later`, stopped by entry 148

The corpus often holds no post for the country a traveller applies from — Australia holds pages on
its Riyadh post and none on `uae.embassy.gov.au` (entries 132, 133). Search supplies those pages at
request time, which is the owner's rule (entry 148). **Shipped and kept:** `mission_labels` (entry
134), the mission-index seed (137), family queues ordered by what the store lacks and host back-off
(139). **Left:** Australia's family has 169 members and a build walks ~25; the ways out — let it sweep
over builds, a per-family host allowance (reopens a deliberate decision in `_next_wave`), or seeding
members directly (entry 101's failure) — are unmeasured. **Do not add `{residence}` to
`corpus_queries`.** Reopen only if a sweep shows search failing to supply a post.

### 35. Finish the Netherlands' family reservation — `later`, parked by entry 148

The reservation (entry 88) makes the store cover per-traveller pages offline, which entry 148 hands to
search. Left: `airport-transit-visa/apply-{}` at 52% read. A rebuild re-walks its seeds and cannot
open an address a previous build recorded and skipped (entry 101); seeding from unfetched addresses
is unmeasured. Do not raise the share — nothing was capping it.

### 47. Find out how much of the world the family detector cannot see — `later`, parked

`country_family_keys` matches the URL only, so it misses Romania's Romanian-named checklist PDFs and
Canada's `?country=IN` (below `FAMILY_TOKEN_MINIMUM`). An anchor-text instrument finds them (entry
126); the residual blind spot is mostly English aliases and dependent territories (entry 124), not
translations. Both `coverage` half two and the crawl's family reservation rest on it.

### 46. Decide what to do about a refusal served as `HTTP 200` — `later`

Morocco's F5 block answers `200` with "Request Rejected", reported as `unusable`, when the truth is
that we were not permitted to check (entry 121). Not a safety defect — the thinness guard stops it
becoming a source — but only by a size accident. Reclassifying it as `blocked` changes what resolves a
corridor (entries 32, 57, 109). **Do first:** count such bodies across the corpora; if it is Morocco
alone, a truer `unusable` reason may be enough.

### 27. Decide whether a hosted scraping service may be used, for corpus discovery only — `later`

Retrieval through a service like Firecrawl is already refused by existing rules: it sells anti-bot
bypass (never work around a refusal), it hides our honest client (entry 35), delegates `robots.txt`
(entry 36) and TLS verification (entry 12), and muddies provenance (entry 4). **Only `/map`, for
offline URL enumeration, is open** — a candidate generator like search. Try item 10 first.

### 10. Try sitemaps before crawling — `later`

`sitemap.xml` gives a site's URL inventory without a crawl. Check first whether pages that filled
roles appear in their domains' sitemaps.

### 11. Decide whether a host that has refused every request should be skipped — `later`

It would recover fetch places on hosts like `travel.state.gov`, but a `403` on one path is not
evidence about another, and France showed a "blocked" URL behind a challenge was a plain `404`. Count
per-host refusals first; skip only if it changes what a corridor resolves. The block must still be
reported, and nothing here may become a retry.

### 12. Watch where the two deciders disagree — `later`

`decided_by` and the heuristic's score are kept beside the model's choice. A pattern of disagreement
is a lexicon gap or a model error. Do not tune the lexicon to agree with the model.

### 13. Revisit conflict detection, with claim scope — `later`

Entry 30 deleted the unverified `conflicts` field. If it returns: record the population each claim
applies to, compare only same-scope claims, leave the visa decision out, and restrict to quantitative
rules where a wrong flag costs a caveat. Read entry 6 first.

### 14. Detect drift in configured sources — `later`

Every source stores a content hash over cleaned text. On a change, **mark** the source; **never**
auto-rediscover and swap a role-bearing one — that is the wrong-checklist failure with the human
removed. Item 20 makes this the corpus-rot check.

---

## Done

The reasoning is in the DECISIONS entry; this is the index. Code comments cite some of these numbers.

| Was | Done | Entry | What building it found |
| --- | --- | --- | --- |
| — The full rebuild of every store | 09-25 | 193, 203, 204 | All 55 rebuilt and graded; stores hold every oracle answer. The archived-year veto was dropping filed guidance, widened |
| 68. Read more of what a build records | 09-25 | 185–187, 189, 192, 200 | The cause was the per-host split: a scored link may now read past its share, and is scored with its surrounding text |
| 70. Why a corridor that read its authority has no decision | 09-25 | 198–202 | The roles call was right every time it refused. Eight measured fixes took 11 of 14 to an answer; the EU tier answers Schengen decisions |
| 66. Keep the selector's picks as good as its pools grow | 09-24 | 194, 195 | A shorter list, not more text: the fusion top 120 plus 40 with no text, at 42% less input, shipped without the live A/B |
| 62. Pay for model calls through Ofself Personas | 09-24 | 188 | One plain call at `capabilities: []`; graded equal to the direct route. The route from now on |
| 5. Answer the challenge, honour every `robots.txt`, get France's checklist | 09-16 | 75, 92, 93, 109, 179 | Half the challenges need Cloudflare's script host; France's checklist is behind its wizard — named, never driven |
| 48. Test root seeding; separate discovery from allocation | 09-15 | 161–163, 176 | Root seeding rejected; the gap was a build discarding its own search seeds. All 53 then rebuilt |
| — Reuse a plan written for the same inputs | 09-16 | 178 | The draft is kept 24h, never the plan; every request still validates and grades. Not timed live |
| 56. Make the written plan shorter | 09-15 | 174, 175 | Short source ids declined (wrong answers); one short quote per claim shipped, ~1.5s saved |
| 19. Get a corridor under ten seconds | 09-15 | 140–146, 159–173 | Closed, not reached. Search pace 19.0s → 2.6s; every call's cost recorded; $0.394 → $0.251 a corridor |
| 51. Search only for what is specific to this traveller | 09-15 | 159, 160 | Nothing built: neither conditional shape pays, and the purpose query is not traveller-neutral |
| 31. The anchor scorer gates 94% of the corpus | 09-14 | 123, 125–128, 158 | Five best per role on stored text added to the pool, nothing removed, +16% selection input |
| 21. Fill the three provenance gaps | 09-14 | 156, 157 | Sources carry content hash and why chosen; the checked quotes were later removed (entry 227) |
| 54. Say which refused page mattered, once per authority | 09-14 | 155 | One sentence per authority, decision pages first |
| 9. "No checklist exists" vs "we failed to find it" | 09-14 | 153, 154 | Re-scoped: say what was found; name likely unread checklists with links |
| 8. Confirm a blocked authority reads usefully | 09-14 | 152 | Reads as "we could not check"; found items 54 and 7's storing question |
| 17. What a corridor that flips between runs should do | 09-14 | 43, 44, 118, 151 | A refusal is retried until one run resolves — deferred to item 7 |
| 53. A null-decision plan graded `verified` | 09-14 | 150 | Now refused by `VisaPlan` |
| 52. Hand-configured destinations answering from one traveller's pages | 09-14 | 149 | Singapore and Japan now researched like every other country |
| 1. Score a page for where the traveller applies from | 09-02 | 126 | The scorer's order is consumed by nothing — it reaches a corridor as a boolean |
| 50. Cap renders per host on the request path | 09-05 | 135, 136 | The shortlist shares 5 renders, not 12; one host may no longer take all five |
| 45. Re-run five countries measured before their corpus | 09-01 | 121, 122 | Romania fills 5 of 6; found items 46 and 47 |
| 43. Give the new 43 something the coverage gate can grade | 09-01 | 120 | An `ungraded` verdict; the oracle is not growing to 53 |
| 44. Re-measure countries whose ranking text was a bot-check page | 09-01 | 118, 119 | NO and ID fill 6 of 6; the US corridor flips |
| 42. Why Liechtenstein's 7,456 pages yield two candidates | 08-30 | 117 | `is_challenge` read only 20,000 characters; 414 stored bodies were bot-check pages |
| 41. Build corpora for the 43 remaining countries | 08-30 | 116 | 10 → 53; three defects only breadth found (113–115) |
| 30. Perfect batch 1 before adding a country | 08-30 | 116 | All three stages met |
| 18. Build the offline corpus job | 08-30 | 44, 116 | A build records far more than it reads (entry 88) |
| 40. Let curation fetch one page the index lacks | 08-28 | 99 | Dropped; the premise was wrong |
| 39, 39a. The visa-free plan as an entry plan | 08-28 | 96, 98 | No step floor; `where_to_apply` may be null, never forced |
| 38. Re-run the twenty oracle corridors | 08-28 | 97, 98 | `selector` recorded the configured selector, not the one that ran |
| 37. The gate that says whether a corpus is good enough | 08-28 | 90 | `visa-discover coverage` |
| 36. Guidance on a commercial contractor | 08-28 | 89 | Named, never read, never believed |
| 34. An oracle neither selector helped make | 08-27 | 87 | Entry 86's +41 is +30 |
| 33. Measure the model candidate selector | 08-27 | 85 | Turned on |
| 32. Raise the corpus page budget | 08-27 | 82 | No change; the UK's fee host published a form |
| 26. The nationality bonus rewards naming a country | 08-24 | 62 | Closed with no code change |
| 25. Get the answering page into the shortlist | 08-24 | 61 | Five per role at 35 places; the UK went 0/8 → 4/4 |
| 24. "The answer is behind a tool we cannot drive" | 08-24 | 59, 60 | A questionnaire is an answer, for every role |
| 3. Measure the top 20 corridors against a bar set in advance | 08-24 | 58 | A marginal pass; the wizard, not blocks, is the largest limit |
| 23. Give `visa_decision` its floor back | 08-24 | 56 | The vocabulary could not recognise an answer |
| 15. Re-run the six verified corridors | 08-23 | 55 | Qualification broke when the crawl left |
| 22. Route the request path through the corpus | 08-23 | 49–53 | 2–5× faster |
| — Earlier (08-18 to 08-24) | — | 29–43, 63 | robots.txt, the registry, block narrowing, failed adjudication refuses, the recall log, typed refusal causes |

## Smaller things

**The roles call can credit a generic sentence as the checklist (entries 223, 224).** South Korea
`IN/IN` once credited the Chennai consulate's exemption page ("passport, application forms, a recent
photograph, and other relevant documents") and was graded `verified`. About 1 run in 18; a stricter
rule 4 did no better on replay. Untried: a deterministic floor on how many distinct documents a
credited checklist names (`names_documents` in `scoring.py`); refusing a checklist credited from the
page the same call credited as an exemption list. Measure on the saved packets first.

**Egypt `BD/SA` credits its decision 1 run in 3 on a byte-identical packet (entry 204).** A prompt
question — measure with `replay_roles.py` before changing anything.

**`coverage` reports the EU store as a country nobody has built.** Skip a union's store as the two
corpus tests do (entry 204).

**A PDF served as `application/octet-stream` from a path without `.pdf` is read as HTML (entry
216).** Checking the `%PDF-` signature would catch it. Waits for a corridor it would help.

**`canonicalise_url` drops a trailing slash before a query string, and some servers care** (entry
201: EUR-Lex). Changing it changes stored addresses, so measure first and ship with a rebuild.

**A `TypeError` from the model call reports itself as bad model output.** Separate the invoke from the
parse, in its own change.

**A per-host fair share treats unequal hosts equally.** Thailand's 31 provincial WordPress sites each
took the same share as the national immigration service. Changes what a build spends; needs its own
rebuild.

**`CorpusEntry` holds one `link_text`/`heading` per URL**, so one section's context (Sweden's
"studying for less than three months") can attach to a page every traveller needs (entry 55).

**A footer link inherits the heading above it** (entry 26). The boilerplate veto covers the cases
seen; the inheritance is still wrong.

**A reserved shortlist place guarantees a domain, not a page** — the US mission's went to an
immigrant-visa appointments page. The fix is in mission scoring.

**The corpus page budget is fixed at 1,200 rather than derived from the seed count**;
`depth_is_exercised` already reports the symptom.

**The corridor crawl's 40-page budget is spent at depth 0** for a country with no usable corpus.
A per-domain seed cap would restore depth-2 discovery.

**Nothing validates a `tlds` entry in `countries.yaml` that widens trust.** `tests/test_trust_coverage.py`
is the natural guard.

**`is_bare_public_suffix` is a heuristic**, not a real public suffix list — review it as countries
are added.

**A plan can leak an internal field name** (`application_document_source_ids`) into traveller-facing
text. A prompt matter.

**Sweden's ranking is unexplained**; trace it as the Netherlands was before changing anything for it.

**Germany fills `document_checklist` for `IN/GB` and `PH/PH` but not `NG/NG`**, though
`nigeria.diplo.de` is in the corpus (entry 112). Not held, or not selected — nobody has looked.

**A delegated checklist counts as `open` in `coverage`**, though the plan hands over its link.
Give it its own column, never added into `held` (entry 93's reasoning).

**Cyprus names `mip.gov.cy`, which does not resolve; `www.mip.gov.cy` does.** Unmeasured whether
naming the `www` host would seed more.

**Ireland reports the dead `inis.gov.ie` two different ways** — an oversized robots file and a
certificate failure. Cosmetic.

**`www.ph.emb-japan.go.jp` answered 404 twice.** Check whether the corpus address is stale.

**25 recall logs predate `RecallRecord.cause`**; only a re-run fills them. Fold into the next
measurement that needs live runs.

**A sweep cannot notice every corridor failing for the same non-country reason** (an out-of-credit
provider). Stop after N consecutive `adjudication_failed` and say which provider said what.

**The Japan eVisa "Go here" link downloads a PDF shell** rather than opening the portal. The plan
flags it.
