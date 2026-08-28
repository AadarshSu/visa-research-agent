# Visa Research Agent

Bounded, source-backed visa research. Every claim must be grounded in an official government source,
and the traveller must be told plainly when something could not be verified.

## Read these first

This file is loaded automatically; the documents below are not. **Read them before starting work.**

| File | The question it answers |
| --- | --- |
| [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) | **Start here.** Where it stands, what to do next, what is known to be broken |
| [TODO.md](TODO.md) | What is the ordered queue of work, and why each item matters |
| [DECISIONS.md](DECISIONS.md) | Why is it built this way, what was tried and rejected — **start at its index** |
| [ARCHITECTURE.md](ARCHITECTURE.md) | How is it built — trust model, pipeline, retrieval, discovery |
| [AGENTS.md](AGENTS.md) | How do I contribute, and how do I debug a corridor |

Each fact has one home. When one of these files summarises another, the two drift, and the drift is
what has wasted the most time here — see the corrections table further down, whose seventy-six rows are
mostly a written-down diagnosis that a run then contradicted.

**The goal, stated so everything below reads against it.** A country is built **offline** — its
corpus and its page-text index — and a corridor answers from that store. Live search is acceptable
where it is genuinely unavoidable; it is not acceptable as the ordinary source of recall. The corpus
has to be *useful*, and "useful" has a number: how often a corridor finds what it needs without
searching. [TODO.md](TODO.md) item 19 is that goal as a work item; items 30, 33 and 34 feed it.

**Where it stands, as of 2026-08-28.** The pipeline works end to end and passed a bar committed in
advance (entry 35, measured in entry 58): over twenty corridors, **75% confirm the visa decision** and
**50% yield a document checklist** — a marginal pass. Corridors are served from stored per-country
corpora at a median 27.4s. All 53 reachable destinations have been run at least once (entry 70); ten
have a corpus **and now a page-text index** (entry 85). A questionnaire is treated as an answer rather
than a blockade — named for the role it settles, offered beside that question (entries 59, 60), and
guidance an authority contracts out to a company is named the same way (entry 89).

**The gate is built and it is the promotion rule for stage 3** (entry 90, [TODO.md](TODO.md) item
37). `visa-discover coverage` answers "is this country's corpus good enough to serve a corridor" in
two halves that are never added — 47 of 47 known answers, which is **one traveller** and stays a
regression check, and every per-traveller family the store holds, from which the verdict is computed
**alone**. Six of the ten have no per-traveller dimension, SG and GB are *bounded by the authority*
(a pass), and only NL is `incomplete`. Offline, no model, no search.

**How close the corpus is to the goal, measured** (entry 82). Across 30 corridors into the ten corpus
countries, **18 had zero misses**, and of the 67 pages missed in total **none were on a host the
corpus lacks**. Site-level recall is solved. What remains is page-level and has two causes: ordinary
deep pages a bigger crawl reaches, and **spaces behind a form** — the United Kingdom publishes its
per-nationality fee tables through a country selector with no links between nationalities, so no
crawl reaches them at any budget, while Canada's equivalent reached 213 values because Canada
published a page listing every country as a link. The second cause is the questionnaire outcome
wearing a different hat, and the answer is the same: name the tool.

**And measured a second way on 2026-08-28: 47 of 47 answerable roles already have their answering
page in the corpus — for one traveller.** `oracle/selection_oracle.yaml` is `IN/GB/tourism` for all
ten countries, and the Netherlands' answers were held both before and after entry 88's rebuild, so
this measurement is blind to the thing that rebuild fixed. **Never quote the 100% as evidence a
corpus is ready** — it is half one of the gate above, and the gate's own verdict deliberately
ignores it.

**What chooses which pages to read is now a model, not the ranking** (entries 83–87). It reads stored
page text for every candidate in contention and picks up to 20 pages to fetch, where the heuristic
ranked links and fetched 35. It costs a second model call per corridor. `discovery_selector: model`.

**And selector work finally has ground truth it did not build** (entry 87, TODO item 34), **now for
two travellers** (entry 91). `oracle/selection_oracle.yaml` names, by hand, the page answering each
role for **twenty** corridors — `IN/GB/tourism` and `PH/PH/tourism` over the same ten countries —
from each corridor's whole contention set rather than from what any arm fetched. Both read 100%
*held* and the denominators are the finding: the same stores answer **47 of 60 roles for one
traveller and 36 of 60 for the other**. Read the `held` column with care — it is a finding for
`IN/GB`, curated from a wider set, and near-circular for `PH/PH`, curated from the corpus itself. Against it the model
reaches **100% role recall to the heuristic's 70% at matched budget**, and 91% when the heuristic is
allowed its shipped 35 places and 3.1× the fetches. On the jointly-built oracle entries 85–86 used,
the same arms read 86%, 45% and 79% — so **entry 86's +41 points is +30**, and its +7 against the
shipped heuristic is +9. `visa-discover selection-recall` prints both columns on every run, so the
bias is a number rather than a caveat.

**Read entries 78–87 before touching discovery ranking.** Five of them correct the ones before them,
and the corrections table below carries the specific traps.

## Rules that must not be broken

These are repeated here because they are the ones where a plausible-looking "simplification"
produces a serious defect.

- **Officialness is a property of who controls the domain, never of how a page reads.** Enforced
  when configuration loads, after every HTTP redirect, and after every meta-refresh forward. A
  change to retrieval must preserve all three.
- **Never disable TLS verification.** Incomplete certificate chains are fixed by bundling the
  missing intermediate in `config/tls_intermediates/`, each verified to chain to an already-trusted
  root. An attacker able to impersonate an immigration authority could dictate what documents a
  traveller brings.
- **Refusing is a correct output.** A plausible but wrong document checklist is worse than no
  answer. Prefer refusing with a diagnosis over substituting something that looks right. This includes
  **failing model calls**: a failed role adjudication refuses the corridor rather than falling back to
  the heuristic, because the heuristic is the decider that produced Brazil's wrong checklist at full
  confidence (entries 15 and 31). "Degrade to a worse answer" is not the conservative option here.
- **Web search belongs only in `discovery/`, and only as a candidate generator.** Nothing search
  returns becomes evidence until it passes the domain-trust rules.
- **A domain is trusted automatically only when it is the destination's *own* government** —
  governmental **and** under that country's own top-level domain. No human approves domains any
  more, but the rule they were applying still runs, and both halves are load-bearing: without the
  first, a commercial insurer under `.fr` gets in; without the second, the US embassy's page about
  Vietnam does. Never relax it to "looks official". If no such domain is found, nothing is fetched
  and the destination is refused. **How many** may be used is also bounded — at most five, and the
  relaxed one-query evidence bar applies only where "own government" is two independent signals.
  A country whose own top-level domain *is* `gov` otherwise admits its whole federal namespace, and
  the cost lands on search count and crawl budget — three searches per trusted domain, so five domains
  is fifteen queries on the cold path (entry 22).

  **Which domains are trusted is now committed data, not a live search (entry 38).**
  `config/authority_domains.yaml` is generated offline by `visa-discover registry` and read at
  construction; a country missing from it is **refused**, never bootstrapped live, because falling back
  would silently reintroduce the per-request variance the file exists to remove. The rule itself is
  unchanged — `auto_trusted_domains` still decides — so everything below still applies.

  **Measured 2026-08-18: the governmental half fails for 19 of 51 countries; 16 since 2026-08-25** —
  Germany, Italy, the Netherlands, Sweden and most of Schengen have no governmental marker in their
  hostnames, so the whole government is refused (entry 33). Austria, Canada and Uruguay came back when
  the markers they actually use were added (entry 65). **Do not fix the rest by widening
  `GOVERNMENT_PATTERNS`.**
  Adding `.de` or `.nl` would trust every commercial site in those countries, and for exactly these
  countries the own-TLD test is the only other signal. The fix is a reviewed authority domain per
  country in committed data (entry 34). Adding `gv`/`gub` as markers and `canada.ca` beside `gc.ca` are
  corrections *within* the rule and are fine.

  **Every reason in `withheld_domains` must be true.** Reading that list is the only mitigation known
  problem 2 offers, so a false reason defeats the safeguard rather than merely reading badly. A domain
  under the destination's own TLD with no recognised marker is *"could not be confirmed as an authority,
  and may be a real one"* — never *"not a government domain"*, which is false and was word-for-word what
  a commercial visa agency got (entry 33).
- **Never work around an authority that blocks automated retrieval.** Do not spoof a user agent, do
  not retry to get around a rate limit, do not point the renderer at a page an authority refused. A
  block is not evidence that the guidance is wrong or missing — it means *we cannot independently
  retrieve and verify it in this execution environment*, which is a narrower claim and the only honest
  one. Mark the source inaccessible, say so, and let the role go unfilled. Never substitute
  plausibility for evidence, in a product whose wrong answers send someone to a visa centre without
  the right papers.

  **First establish that it *is* a block, because for France it was not (entry 41, 2026-08-19).** This
  rule used to open by naming France's portal as a site that "answers `403` to anything that is not a
  browser". Measured, `france-visas.gouv.fr` answers a Cloudflare **challenge** — `cf-mitigated:
  challenge`, *"enable JavaScript and cookies to continue"* — and answers it for `robots.txt` as well,
  so the authority never stated anything. A challenge is a capability test, and answering it by running
  the page's own JavaScript in a real browser **under our own user agent** misrepresents nothing to
  anybody: the project's own renderer, announcing `VisaResearchAgent/0.1`, reads the page. So a
  challenge is its own outcome, may be answered by the renderer, and — like a `Disallow` — **may never
  resolve a corridor**. **The line is "did the authority state anything", not "which status came
  back".** A `401`, a bare `403` with no challenge markers, and a `429` are refusals and this rule
  governs them in full. Not yet implemented: see [TODO.md](TODO.md) item 5, and note the interface
  still tells travellers a challenged authority *"does not permit automated retrieval"*, which is
  false.

  **What is allowed, and is not a workaround: naming it.** A blocked page may be reported with its
  URL so the traveller can open it themselves, which is the one thing they can act on. The line is
  absolute — the page may be *named*, never *read*, inferred from, retried, or counted as a source.
  So `UnreadableAuthority` is deliberately not a `ConfiguredSource`, the research packet carries its
  URL and no text, and it is still checked against the approved domains, because nobody read it and
  the domain is the only thing vouching for it (entry 27).

  **And naming it must stay narrow (entry 32).** Only `401`/`403` may qualify a corridor — a `429` is a
  transient rate limit, and "try again later" is the honest advice. **A challenged `403` may not qualify
  one either (entry 41):** a refusal is at least a page an authority withheld, while a challenge is a
  page nobody asked the authority about. The blocked URL must also have been
  a credible `visa_decision` candidate: a `403` on a footer link is not grounds to declare the decision
  unverifiable.

  **Whether it is credible is now *judged*, never keyword-matched (entry 57).** `_decision_blocking`
  asks a model over the refused page's **address and label only** — there is no page text, because the
  authority refused it, and `build_blocked_packet` has no parameter through which any could be passed.
  Keep it that way: a packet that ever grew an excerpt field would be inferring content about a page
  nobody read, which is the thing this rule forbids outright. It fails closed after two attempts, and
  with no adjudicator configured the keyword test still runs, which is the deterministic baseline rather
  than entry 31's forbidden fallback. Measured: France qualifies its own United Kingdom and India pages
  and rejects its FAQ, its application form and its visa-category page — where the keyword version had
  qualified a **blank CERFA form**. Without both bounds, corridors whose decision was merely *not found* — which must refuse
  — drift into presenting as authority-blocked, which resolves. Every block is still *reported*
  regardless; the bounds govern what may *resolve a corridor*.

  **The posture is honest client, not anonymous client (entry 35).** This rule forbids *deception* —
  spoofing, retrying, rendering past a **refusal** — and none of that has changed or will. Rendering
  past a *challenge* is a different act and is now allowed (entry 41); the word doing the work in that
  sentence is "refusal". It does not
  require being an anonymous, unauthenticated client, and treating those as the same thing was costing
  coverage under the banner of a rule that never demanded it. So: `robots.txt` **is now read and obeyed**
  (entry 36), and asking an authority for access is ordinary. Client-side retrieval through the
  traveller's own browser is an **open question, explicitly not approved** — argue it in a decision
  entry before writing any code for it.

  **A `Disallow` is reported, and it may never resolve a corridor (entry 36).** `disallowed` is its own
  `FailureOutcome` so a page nobody asked for can never read as a page that did not exist — but it is
  deliberately outside `blocked_urls()` and `persistent_refusals()`, so it reaches neither
  `inaccessible_urls` nor `decision_blocking_urls`. A `403` was observed *on the page*; a `Disallow`
  covers a path we chose not to request, and treating it as evidence the answer sat behind that page
  would widen entry 32's narrow exception by a route entry 32 never considered. **And the reason
  reported must be true of what was seen**: a policy that could not be read is *"could not be read, so
  whether this client may fetch it is unknown"*, never *"does not permit"*, and an unreachable host is
  still reported as unreachable rather than as a policy nobody read.
- **A questionnaire is an answer, and may be named, never driven (entries 59 and 60).** A page read
  successfully and judged to *ask* a question rather than answer it is a third outcome beside *found*
  and *blocked*: it is named for the role it settles, and the plan offers it beside that question —
  the decision in the decision panel, the checklist in the documents panel, fees and times under
  caveats. **It is not a blockade in front of the guidance; it is the form the authority published
  the guidance in**, and a plan that stayed silent would withhold the one thing the traveller can act
  on in a minute.

  **A tool never fills the role it is named for.** The role stays unresolved, no source is invented,
  and nothing about the tool is citable. For `document_checklist` that is the rule this project
  exists to enforce: `application_document_source_ids` stays empty, so `validate_absent_checklist`
  still forbids listing a single requirement, and a plan naming a checklist tool may not designate a
  checklist source either.

  **Only `visa_decision` changes whether a corridor resolves**, because only it is load-bearing. That
  asymmetry is what makes the other roles cheap: entry 32's drift risk — *not found* presenting as
  *behind a tool* — lives entirely in the load-bearing role and is untouched. Its bounds are
  unchanged: **only the adjudicator names a tool**, on a page it was given the text of; the heuristic
  never does, because "is this a questionnaire" is a meaning question and entry 57 is what
  keyword-matching meaning cost. An invented id is discarded, a tool is dropped for any role a source
  already answers, and the URL is checked against the approved domains like everything else. A
  `VisaPlan` naming a decision tool cannot also state `visa_required`, and can never be `verified`.

  **Driving the tool stays out of scope, and entry 59 argues it against the strongest case.** GOV.UK's
  checker is *server-rendered*: `robots.txt` allows it, and a plain GET under our own user agent to
  `/check-uk-visa/y/india/no/tourism/no` returns *"You'll need a visa to come to the UK"*. So "we
  cannot retrieve it" is false and is **not** the reason. The reason is that two of the checker's
  questions — dual citizenship, travelling with family — are not in a corridor, and answering them is
  inventing traveller input on the one question where being wrong is most damaging. If it is ever
  revisited, the bar is in entry 59, and it must sit **on top of** naming the tool, never instead of it.
- **Guidance an authority contracts out may be named, never read, and never believed (entry 89).**
  The Netherlands tells most residences "on the VFS Global website you'll find a checklist with the
  documents you need", so for those travellers the choice is naming the delegate or saying nothing.
  It is entry 27's refused page and entry 60's questionnaire a third time: **a next step the
  traveller can take and this program may not.**

  **Trusting or crawling a contractor was considered and declined.** `vfsglobal.com` is one domain
  serving ~60 destinations, so `belongs_to_destination` — what stops the US embassy's Vietnam page
  answering a Vietnam corridor — has no analogue there, and the artefact at stake is the checklist.
  Entry 2 stands. Do not add one to `authority_domains.yaml`; `config/service_providers.yaml` is a
  separate file precisely so a delegate is never one boolean from being citable.

  **The warrant is two independent things, and the government page is only one of them.** An
  approved page linked it **and** its registrable domain is on the reviewed list — because the link
  comes out of HTML, and HTML is `untrusted_content`: without the second half a spoofed page could
  hand a traveller any address, for the checklist. Either alone fails closed.

  **The model selects; it may never supply.** The crawler records the `href`, the packet carries
  addresses with **no content field**, and `validated_delegates` discards any id it did not record —
  so the URL a traveller follows was read by our code off a government page, never written by a
  model. Do not "simplify" this into extracting the URL from the excerpt. Naming one fills nothing:
  `application_document_source_ids` stays empty, `validate_absent_checklist` still forbids listing a
  requirement, and it never sets `decision_is_unverified` — a company's site is not an authority
  withholding a page and is not an official tool.

- **A visa decision that could not be confirmed must be `null`, and the application enforces that.**
  Not the prompt: a model asked for null returned `true` in testing. A wrong yes or no about whether
  someone needs a visa is the most damaging thing this can say, so `decision_is_unverified` overrides
  the model rather than trusting it, and such a plan can never be `verified` (entry 27).
- **What may be stored is a *page*, never an *answer* (entry 44).** The corridor is not the unit of
  precomputation at any width — `destination × nationality × residence × purpose` is 196,020 corridors
  even with residence reduced to post selection, roughly 2.9M searches per refresh cycle, and the layer
  it would freeze is the one with the most inference in it. What *is* stored is a country's **page
  corpus**, because *which pages exist* does not vary by corridor; only which one answers a given
  traveller does, and that stays live. A **plan is a rendering, never a stored fact.** A `visa_rule`
  decision table is deliberately not built: one page names ~200 nationalities, so a wrong row would sit
  in a store for weeks and be served with a citation, where a wrong pick today is ephemeral. If it is
  ever built, a nationality the page did not name yields **no row**, never a false one.
  **A corpus miss must never be answered by *quietly* falling back** — entry 38's rule applied to pages.
  Deciding a corridor from that day's search after the store came up short would restore the
  per-request lottery for exactly the corridors that need it not to be one.

  **What is stored of a page is now its *text* as well, and that text ranks — it never speaks
  (entry 78), and only where the index covers at least half the candidate set (entry 80).** The corpus stored `url`, `title`, `link_text`, `heading` and threw the body away at
  `crawl._expand`, so a corridor ranked three thousand pages on a **median of 29 characters** against
  a median body of 3,602. `discovery/page_text.py` keeps the body in a per-country SQLite/FTS5 index.
  **It is ranking input and never evidence, and the type is what enforces that**: `rank` returns URLs
  and scores, there is no accessor for a body, and `TextMatch` has no field to hold one — exactly as
  `build_blocked_packet` has no parameter for page text. Stored text is older than the rules governing
  what a traveller may be told, so a quote from it would be guidance served outside
  `source_maximum_stale_hours` with nothing to say how old it was. A page it ranks is still fetched
  through `LiveSourceFetcher` before a word reaches a plan. **Do not add a `snippet()`, a body field,
  or a "just for debugging" accessor.**

  **One accessor now returns bodies, and the barrier moved rather than went away (entry 83).**
  `text_for_selection` hands stored text to `discovery/selection.py`, whose response type
  `Selection` holds source ids and **has no field for prose**. The invariant is the one that always
  mattered — no sentence written from stored text reaches a traveller — and it is now enforced by
  that type instead of by the absence of a method. Naming a questionnaire still happens in the
  adjudication call, on text fetched this run, so entry 60 is untouched. A *second* caller wanting
  bodies for anything else is the change that has to argue for itself.

  **Read that as the constraint it is, not as a description of today.** Entry 44 wrote it as "a miss
  refuses and flags the country", and entry 47 chose a different shape that satisfies the same
  constraint: the candidate set is **`corpus ∪ live search`**, with search running on *every* corridor
  rather than as a fallback after a miss, so nothing silently degrades because nothing was ever
  conditional. A country with **no** corpus simply crawls, exactly as before. Refusing on a miss is
  still unbuilt and still wanted — [TODO.md](TODO.md) item 19 — and it only becomes safe once search
  has left the request path, which needs the nationality dimension measured first (entry 48).
- **A stored row records when the evidence was retrieved, never when the row was written.** A failed
  refresh serves cached text flagged `stale` and **keeps its original `fetched_at`**; only a validator
  match moves it, because a `304` proves the text is still current (entry 4). Past
  `source_maximum_stale_hours` a stored page is **refused rather than served**. Both hold in any store,
  and both are easy to lose in a migration — a schema that collapses `retrieved_at` and `row_written_at`
  starts lying about how current its guidance is. A content-hash change **marks** a source and may never
  auto-swap a role-bearing one: that is the wrong-checklist failure with the human removed.
- **Never** add application submission, appointment booking, form filling, or any claim that
  approval is guaranteed.
- **Never show a traveller an unverified claim that would alarm them if wrong.** The rule from entry 6,
  which deleted a *working* conflict detector: a feature whose wrong answers are alarming needs a
  near-zero false-positive rate or it should not ship. The `conflicts` field violated it and was deleted
  (entry 30); a disagreement between official pages is now an unresolved question. **Do not add it back.**
  If conflict detection returns, it records the population each claim applies to, compares only same-scope
  claims, and leaves the visa decision out.
- **LangGraph is declined, not deferred (entry 29).** The pipeline is linear, so there is no cycle to
  express, and the trust checks are Pydantic validators that cannot be skipped rather than graph nodes
  that could be reordered or bypassed. Do not reintroduce it or a `state.py`-style placeholder. LangChain
  stays for structured output only.
- **Tests must not touch the network or an LLM.** Use the `transport=` and `now=` seams and the fake
  generators; see `tests/discovery_site.py`.

## Before finishing a session

Run `ruff check .`, `ruff format --check .`, `mypy`, `pytest`, then update the handoff:
current state and known problems in `PROJECT_HANDOFF.md`, any decision and its reasoning in
`DECISIONS.md`, and what is now next in `TODO.md`.

Do not record a problem as fixed unless it is fixed, or a result as verified unless it was run.
These files are read by someone with no other context.

**Check a documented claim against the code before carrying it forward.** These files are self-written,
and the pattern has now repeated in five separate sessions: the written-down diagnosis named the wrong
cause, and only running the thing showed it.

| what the file said | what a run showed |
| --- | --- |
| the trust rule's gap is in the TLD half | it is the governmental half (entry 33) |
| a blocked authority never reaches the plan | it reaches it by two routes (known problem 7) |
| consuming the corpus is slow because of *scoring* | it was `wrong_country`, 33× (entry 50) |
| removing the crawl risks *reporting* | reporting held; **qualification** broke (entries 55–56) |
| `visa_decision` needs its floor guard removed | the vocabulary could not recognise an answer (entry 56) |
| bot-blocks are the largest coverage limit | the **wizard** is (entry 58) |
| the UK's wizard page "was ranked, shortlisted and fetched" | for NG and PH; **not** for IN or CN (entry 59) |
| the UK answer is behind a tool we cannot drive | it is on a static URL — the reason not to is different (entry 59) |
| a wizard is a blockade in front of the guidance | it **is** the guidance, in the form published (entry 60) |
| the UK checker misses the shortlist because one host hogs places | it is **5th** for its role and three were reserved (entry 61) |
| a wider shortlist is the cheap fix for bad ranking | widening alone does nothing; the *per-role depth* is the gate (entry 61) |
| the scorer rewards *naming* a country, not being about one | it is token-based already; the page really is about India (entry 62) |
| a floor-only role score is safe to withhold bonuses from | a terse per-nationality decision page is floor-only too (entry 62) |
| the corpus ranks the answering page too low | it files it under the **wrong role**; no shortlist depth recovers it (entry 78) |
| junk anchors like "click here" are what lose the page | 2% of entries; the real case is a *good* 40-char label (entry 78) |
| a bigger page budget bought nothing, so depth is not the issue | 91% of links never cleared the *request path's* score threshold (entry 78) |
| BM25 is a safe way to pick what the real scorer sees | the answering page is 116th of 122 by BM25 (entry 78) |
| index text can just be assigned to `body_scores` | a zero would then *sink* a page for holding its text (entry 79) |
| the corpus-only arm lost its checklist to ranking | both pages were shortlisted **and fetched**; it is adjudication variance (entry 79) |
| ...so the checklist loss was adjudication noise | 3 of 3 identical runs: a stable *worse* answer, not noise (entry 80) |
| a lift that never lowers a score is safe | it protects the score, not the **place** — a shortlist is finite (entry 80) |
| the index made japan fill all six roles | one run; three of the same configuration give 3, 5, 5 (entry 80) |
| the lift ranked by who was crawled | the no-lift shortlist was **already 94% indexed** (entry 81) |
| ...so the lift cost japan two roles | six runs of *identical* code give 4,4,4,4,5,6 — it is inside the noise (entry 81) |
| role count measures a ranking change | it grades the adjudicator; the pages were shortlisted in every arm (entry 81) |
| raising the page budget will lift text coverage past the bar | 90% of candidates score zero and can never be shortlisted (entry 81) |
| ...so it is the even *split*, not the total, that starves a host | the UK's fee host went 15 → 20 nationalities; it was never budget-limited (entry 82) |
| a per-nationality URL space is crawlable, canada proves it | canada published a link index; the UK published a **form** (entry 82) |
| letting a productive host spend more is a clean win | the surplus goes to the *largest* host — gov.uk took 4,252 entries (entry 82) |
| a model picking 7 pages beats a heuristic picking 35 | it picked a landing page over its content child, with no redundancy left (entry 83) |
| ...so a model selector is worse than ranking | let it pick 20 and it finds 85% against 55%, reading half as many (entry 84) |
| ...and that +30 points is what it buys | four of those five corridors were the UK; over ten it is **+7** (entry 85) |
| ...and +7 is the selector's margin | that compared 35 picks against 11; at matched budget it is **+41** (entry 86) |
| the model lost the UAE and the US on thin text | at matched budget it wins the UAE and ties the US — it was the budget (entry 86) |
| "prefer fewer" is sensible advice for a page budget | a fetch is cheap and a missed role is not — it had the trade backwards (entry 84) |
| ...and +41 is the selector's margin | on an oracle neither arm built it is **+30**; both arms made the old one (entry 87) |
| a page proven to fill a role is one page | ICA publishes the same page at three addresses; the old oracle held one (entry 87) |
| the UK's per-nationality fee table is the answer it hides | it is keyed on the country you *apply from*, not the passport (entry 87) |
| a page titled "Document Checklist" is a checklist | `imm5484.html` is a download page whose text explains Acrobat Reader (entry 87) |
| a fetch-everything oracle is the automatable version of the same thing | it would still be URLs somebody fetched, so it inherits the alias bug (entry 87) |
| one oracle row per country is enough, the pages are the pages | the same store answers 47 of 60 roles for one traveller and 36 for another (entry 91) |
| a 100% held means the corpus is ready for that traveller | it is 100% of what *can* be answered; the denominator is the finding (entry 91) |
| ...and that 100% held is a finding for both travellers | curating from the corpus makes it circular; only `IN/GB` was curated wider (entry 91) |
| a keyed service not applying means the country cannot answer | one UAE page answers five roles for anybody; the row was three candidates deep (entry 91) |
| a page that answers a role scores something for that role | it answers `fees`, `times` and `entry` scoring **0.0** for all three (entry 91) |
| re-check a shallow row by ranking its unanswered roles again | that ranking filters on the link score, so a 0.0 page still cannot appear (entry 91) |
| the whole fixture needs redoing, the method was too shallow | the `IN/GB` rows already named the pages; only the new curation was thin (entry 91) |
| a corridor with no answers can be skipped when totalling | dropping the two that answered none read 24 of **48**, not 24 of 60 (entry 91) |
| the grader compares a model against a heuristic | nothing recorded which selector ran; six logs put the heuristic in both arms (entry 91) |
| a corpus that holds a page can serve any traveller who needs it | it holds 219 apply pages and **five** checklists; the leaf is a hop deeper (entry 88) |
| a gateway yields more children than a leaf, so count them | 2.4 apiece against 1.5 — ask if the child is *per traveller* (entry 90) |
| the netherlands is the covered case, entry 88 finished it | three complete families were never opened; it reads `incomplete` (entry 90) |
| CA, JP and GB have no per-traveller family | GB has one — the fee wizard; `_queue` groups per *page* (entry 90) |
| the corpus-sufficiency number is 47/47, so build the gate around it | the gate's verdict ignores it; one traveller cannot outvote 197 (entry 90) |
| the corpus is thin because the crawl did not go deep enough | it opened 3–15% of what it recorded; the rest are addresses (entry 88) |
| reserving budget for a family is enough to reach it | one pool is score-ordered, so the fee family took all of it (entry 88) |
| a family key can blank the first country it finds | the destination is named in its own path; all 219 got different keys (entry 88) |
| opening the gateway buys a checklist per residence | 113 of 185 link nothing — the checklist is on VFS Global (entry 88) |
| the biggest country-shaped family is the one worth crawling | Canada's is 176 travel advisories, Japan's 141 country pages (entry 88) |
| a contractor's checklist is a ceiling on what we can offer | it is a ceiling on *reading*; naming it was always allowed (entry 89) |
| the authority's own page linking it is warrant enough | the link comes out of HTML, which is untrusted content (entry 89) |
| most contractor links are the guidance | 44 of 236 are "track your application"; 30 are documents (entry 89) |
| singapore is the next family reservation win, it fills five roles | its page is a leaf, and ICA's index yields 6 children not 198 |
| the corpus is not yet good enough to serve a corridor alone | for `IN/GB` it holds 47 of 47 answerable roles, and did before entry 88 |
| so a corpus-sufficiency number settles it | that one is blind to the traveller dimension; 100% and uninformative |
| a page per nationality is the real nationality risk | not one of 41 countries had that shape; the shape is the **post** (entry 70) |
| a missing demonym can cost the answering page its place | the 22 places demonyms won were all noise, none filled a role (entry 70) |
| an outright `403` has not cost a corridor yet | Lithuania and Slovakia lose their whole trusted set to one (entry 70) |
| a wider sweep only tests the countries it runs | breadth found two defects five countries never could (entry 71) |
| a challenge just needs a longer settle | 9,000ms is *worse* than 2,500ms — it races the redirect (entry 75) |
| japan's corpus misses the london embassy on recall | that host answers a genuine `403`; nothing can fetch it (entry 77) |
| the corpus exists to reach depth the request path cannot | it exists for **latency**; both paths must find the right page (entry 77) |
| a corpus is judged by how deep it crawled | judge it by its hit rate on role-filling pages — Japan 3/5 (entry 77) |
| Cyprus's `403` is a refusal, so entry 41 does not apply | Azure declares its challenge in the **body**; it is answerable (entry 73) |
| three countries send a UK resident to their New Delhi post | Brazil sent them to Edinburgh; only one case was real (entry 72) |
| treating another country's label as another post is the fix | it broke 165 correct pages — the destination's own code (entry 72) |

Prefer a run, a test, or a printed result over a careful reading. When a TODO item proposes a fix,
**measure the proposal before implementing it** — three of the rows above are proposals that were
wrong, and each was cheap to disprove and expensive to have shipped.

**Commits:** one lowercase subject line, no body, no attribution trailers, straight to `main`. One
concern per commit, **with the documentation for that concern in the same commit** — a `docs:` commit is
for when documentation is the only thing changing.

## Running it

```bash
.venv/bin/uvicorn visa_research_agent.api.app:create_app --factory   # the app
.venv/bin/visa-discover corridor --destination japan --nationality IN --from GB
```

Secrets (`OPENAI_API_KEY`, `SEARCH_API_KEY`) live only in `.env`. Reviewable policy — source mode,
extraction mode, cache TTL, stale ceiling — is committed in `config/runtime.yaml`.

```bash
.venv/bin/visa-discover corpus --country CA     # build a country's offline page corpus
.venv/bin/visa-discover pagetext --backfill    # index the text the retrieval cache already holds
.venv/bin/visa-discover selection-recall       # grade what was chosen to read; no network, no model
.venv/bin/visa-discover coverage --country NL  # is a country's corpus good enough? no network, no model
.venv/bin/visa-discover contention --destination netherlands --nationality PH --from PH  # curate an oracle row
```

**Two different questions, two different commands, and they must not be merged.** `coverage` asks
whether the **store** holds the answer; `selection-recall` asks whether the **corridor** then finds
it. A single number covering both would hide which half failed.

Ten countries have a corpus in `var/corpus/` (AE, CA, DE, FR, GB, JP, NL, SE, SG, US) and all ten
now have a text index in `var/pagetext/` (entry 85). A country without either crawls in the request
path and has its pages chosen by the heuristic, exactly as before.

**A corpus records far more than it reads — 3 to 15% of its entries were ever opened — and the page
answering a *specific* traveller is usually one hop below something it recorded and never opened**
(entry 88). An unopened address is still a usable candidate; its children do not exist in any form.
A **per-traveller family** — one page published once per country, `…/schengen-visa/apply-{country}` —
therefore gets a reserved share of an offline build's budget, one queue per family taken in turn, and
**zero on the request path**, where a corridor has one traveller. Only the Netherlands has been
rebuilt this way. The ceiling it hit is not the crawler's: for most residences the Netherlands
publishes its checklist on **VFS Global**, which the trust rule refuses — see TODO items 35 and 36.

Clear `var/cache/` when testing a retrieval change, and `var/corridors/` when testing a discovery
change — either one will serve a pre-change result and make a fix appear not to work. A stored
corridor is kept for three weeks. **`var/corpus/` and `var/pagetext/` are deliberately not cleared
between runs**; they are stores, not caches, and rebuilding one costs search quota.

`var/pagetext/` holds the body text of pages already fetched, one SQLite/FTS5 file per country, and
is filled two ways: `visa-discover corpus` keeps what it reads, and `pagetext --backfill` indexes the
retrieval cache for nothing. It is **ranking input only** — see the rule above, and entry 78.

**Two different things read this index and only one of them is on.** `discovery_selector: model`
**is on** (entry 85): a model reads stored text for every candidate in contention and picks up to 20
pages to fetch, replacing the shortlist as the recall gate, at the cost of a second model call per
corridor. Graded against `oracle/selection_oracle.yaml` — ground truth neither selector helped build
— it reaches **100% role recall to the heuristic's 70% at matched budget**, and 91% when the
heuristic is allowed its shipped 35 places and 3.1× the fetches (entry 87; entries 85 and 86 read
86%, 45% and 79% on an oracle both arms made). A country with no stored text falls back to the
heuristic and **says so in the corridor's notes**. The *numeric* text lift in `combined` is a
separate thing and stays off:

**It may only rank a candidate set it covers past `DEFAULT_TEXT_COVERAGE_BAR` (half), and today no
country does**, so the lift is **off everywhere**. That is a conservative default, not a measured
harm: entry 80 claimed the lift cost Japan two roles and **entry 81 withdraws it** — six runs of
identical code give 4, 4, 4, 4, 5 and 6 roles, so the A/Bs were inside the metric's own noise. What
*is* established is that the role-filling pages are shortlisted and fetched in every arm, so the lift
is recall-neutral and nothing shows it helps. **Do not turn it on without a measurement that has no
adjudicator in it** — grade the shortlist, not the plan (entry 81).

**Both providers meter, and they fail differently.** OpenAI answers `429 credit_balance_exhausted`
when out — now raised as `AdjudicationQuotaExhausted`, told apart from ordinary `429` rate limiting
by the body rather than the status, and **not retried**, because a second call against an empty
account cannot succeed and is billed the same (entry 79). Brave answers **`HTTP 402`** both when out
of credit *and* when queried too fast. The
program now tells those apart from `error.meta.current_spend` against `usage_limit` and says which it
is (`SearchQuotaExhausted` / `SearchThrottled`), and the provider paces itself at 1.3s from one lock
so `search_all`'s concurrency cannot trip a capped plan — entry 74. **A search outage no longer kills
a country that has a corpus**: it falls back to the stored pages, says so, and is never kept for
reuse. With no corpus the refusal stands, because *we could not look* must never become *there is
nothing to find*.
