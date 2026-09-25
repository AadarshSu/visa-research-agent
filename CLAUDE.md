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
| [OFSELF_FEEDBACK.md](OFSELF_FEEDBACK.md) | What has integrating with Ofself shown about **their** platform — kept for Ofself's developers; add to it whenever the platform surprises you |
| [docs/ofself/](docs/ofself/README.md) | **Before any Ofself work:** Ofself's own Paradigm and Personas guides, as dated snapshots — where they disagree with the live platform, OFSELF_FEEDBACK.md wins |

Each fact has one home. When one of these files summarises another, the two drift, and the drift is
what has wasted the most time here — see [CORRECTIONS.md](CORRECTIONS.md), whose rows — over two hundred and fifty now — are
mostly a written-down diagnosis that a run then contradicted.

**The goal, stated so everything below reads against it — the owner, 2026-09-07 (entry 147).**
**The objective is providing the right information. Latency and cost are the constraint it has to fit
inside, not the goal.** A country is built **offline** — its corpus and its page-text index — and a
corridor answers from that store; **search does not have to leave the request path, provided it can
be justified as giving reliable information at a cost that is not high.** The corpus is
general-purpose and the traveller arrives with the corridor, so search is the legitimate
traveller-specific complement to a traveller-neutral store; what it may *do* is unchanged, and every
rule below still holds.

**The owner's five goals, 2026-09-23 (entry 182)**, are unordered:
- model calls paid through Ofself Personas — **done 2026-09-24, and the route from now on** (entry 188);
- about 30s a corridor with information on screen (items 57, 58, 60);
- a URL (items 7, 20);
- accurate and useful answers for most corridors (item 63, with entry 68's bound unchanged);
- 100+ countries (item 64).

**Offline build time and a higher one-time cost are acceptable** for anything that makes each live
request better (entry 184). The live ~30s target and every storage rule are unchanged.

**The full rebuild finished and was graded on 2026-09-25 (entries 203, 204); what is next is the
first section of [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md).**

Where each stands is the table at the top of [TODO.md](TODO.md). What is left half-done is listed in
[PROJECT_HANDOFF.md](PROJECT_HANDOFF.md). **OpenAI has been out of credit since 2026-09-16**, and
since 2026-09-24 **model calls go through Ofself Personas instead, and will from now on** (the
owner; `model_route: personas`, entry 188), so corridors and plans run again. Setting
`model_route: openai` needs the OpenAI account topped up.

**The hybrid, settled — the owner, 2026-09-14 (entry 148).** **The corpus holds what every traveller
shares; live search fetches what this traveller needs, and stays the minority** of what a corridor
reads and pays for. Making the store cover every nationality and residence offline is not the
corpus's job, so **item 49 stopped where it was and items 35 and 47 moved to Later**; a
traveller-neutral gap still is — item 48, where the gap turned out to be pages a build's own search
found and discarded (entry 161). **The order is
correctness, then optimisation, then expansion.**

**Standing decisions from the measurement work.** Each is argued in the entry named; the current
numbers — seconds, dollars, store sizes — live in [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) and
nowhere else.

- Search stays on every corridor, and so does the purpose query. Do not re-propose conditional
  search without a new argument against both measured shapes (entries 159, 160).
- Do not build a truth set, a correctness grader or an accuracy metric without asking — correctness
  is checked by the owner outside this repository (entries 68, 147).
- `openai_reasoning_effort` is `low`; do not lower it without an accuracy measurement (entry 177).
- Grade a model-latency or cost change on several runs, never one, and price it in both seconds and
  dollars — they pull opposite ways (entries 144, 145).
- Read stage timings as an aggregate over corridors. A stage is the span between two numbered steps
  of `_resolve`, not the act it is named after (entries 142, 143).
- Measure the selector pool's gate by the roles it hides at the margin, never by whether a relevant
  page exists outside it (entry 128).
- The selector experiment is closed: the model selector stays, and the twenty corridors are not
  re-run to refresh it (entry 106).
- If a build comes back on one host, read `authority_domains.yaml` before touching crawl settings
  (entries 107, 110).

**Read entries 78–87 before touching discovery ranking.** Five of them correct the ones before them,
and [CORRECTIONS.md](CORRECTIONS.md) carries the specific traps.

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

  **`reviewed` means a person decided, not that a machine confirmed (entry 111).** Three tiers live
  in that field and each entry says which it is: an independent source (Wikidata `P856`/`P17`, or a
  TLS certificate naming the organisation), the page's own words, or the reviewer's judgement where
  the site could not be read at all. The rule itself never bends — **governmental *and* under the
  country's own top-level domain** — which is why `iom.sk` stays refused: the International
  Organization for Migration passes the second half and fails the first.

  **One reviewed exception, a supranational tier — the owner's decision, entry 201.** For a Schengen
  member the EU may answer **the visa decision and nothing else**: who needs a short-stay visa is EU
  law (Regulation 2018/1806), the same for all 29. The EU's domains live in
  `config/supranational_authorities.yaml`, each with independent evidence, travel beside
  `trusted_domains` and never in it, and a page from them chosen for any other role loses it
  (`confined_to_permitted_roles`). Where to apply, checklists and long-stay visas stay national.
  Ireland and Cyprus are not members until checked. A plan cites such a page as the EU's, never the
  member state's. Its one render exception — EUR-Lex pages may reach AWS's challenge-token host — is
  committed data (`challenge_script_hosts`) and extends to no other page. **Do not add a union, a
  role or a challenge host without a decision entry.**

  **Which domains are trusted is now committed data, not a live search (entry 38).**
  `config/authority_domains.yaml` is generated offline by `visa-discover registry` and read at
  construction; a country missing from it is **refused**, never bootstrapped live, because falling back
  would silently reintroduce the per-request variance the file exists to remove. The rule itself is
  unchanged — `auto_trusted_domains` still decides — so everything below still applies.

  **What that costs, measured on one country (entry 107).** Germany's corpus was 1,565 pages of a
  single host because `diplo.de` — where every German mission publishes — sat in `unconfirmable`,
  and the ministry defers to its missions for documents. It is now `reviewed`, on the warrant entry
  89 uses for contractors: an approved government page names it (`auswaertiges-amt.de` prints
  "Website http://www.washington.diplo.de") **and** it is under Germany's own top-level domain. TLS
  could not confirm it — a Let's Encrypt wildcard names no organisation — and note that a refused
  domain leaves **no** trace in the corpus to review from, because `is_crawlable` drops it before
  recording.

  **How to review one, because the obvious way is wrong (entry 110).** `unconfirmable` records what a
  search turned up under the country's own TLD; it is **not** a shortlist of the authority's real
  addresses. Asked properly — Wikidata for the *organisation*, then its `P856` and `P17` — the right
  domain was absent from the proposed list three times out of three: Denmark's immigration service is
  `us.dk` and not `nyidanmark.dk`, Iceland's government is `stjornarradid.is` and not `government.is`,
  Liechtenstein's is `regierung.li` and not `llv.li`. And `iom.sk` sits under `.sk` while being the
  **International** Organization for Migration, which is the standing reminder that the own-TLD half
  is only half.

  **A build seeds from search results and lands on whichever missions the engine surfaced, so
  24 of 27 corpora hold no post for the country a traveller applies from** (entry 133). Australia
  holds 1,599 pages on `embassy.gov.au` and **0** on `uae.embassy.gov.au` while holding 35 on its
  Riyadh post — same authority, same host pattern. That is TODO **item 49**, and the bar it has to
  clear is in `corpus_queries`' own docstring: a traveller dimension may enter the offline job only
  where it can be covered **exhaustively**, which is why purpose is swept in four passes. **Do not
  add `{residence}` to `corpus_queries`.**

  **The missing post is one the corpus can already point at, and the fix is a seed (entry 137).**
  **44 of the 53 corpora record the ministry's own index of its missions abroad and 34 never opened
  it** — Australia's is at depth 1, status `unknown`, and behind it are 194
  per-country mission pages leading on to the post — 70 of which the family gate groups, in two
  families of 45 and 25. So this was allocation, not discovery. It had to be a **seed** rather than a reservation because the chain is
  three hops and `maximum_depth` is 3: opening the index where it lies leaves the post's guidance
  pages at depth 4, where nothing records them. `CORPUS_FAMILY_PATTERN` was widened for the same
  reason it exists — `…/australian-embassy-{}` carries no visa word, so the gate built to find
  per-traveller families was refusing the largest one Australia publishes. **None of it is priced:
  no corpus has been rebuilt.** What is shown is that the seed reaches posts search never surfaced —
  a 300-page crawl from Australia's mission seeds alone found **six hosts the corpus lacks**,
  `bangladesh.embassy.gov.au` with 19 pages — and, since the Australian rebuild of 2026-09-06,
  that **a real build records the family and does not walk it** (entry 138): 1 member recorded
  became 166, `uae.embassy.gov.au` stayed at **0**, `www.dfat.gov.au` timed out on 22 of the 25
  members opened, and *which* 25 is document order because every member scores 0.0. **Do not read
  that build's ten new hosts as the seed working** — every one arrived from its own search seed.

  **Both of those are fixed and a second rebuild measured them (entry 139).** A corpus may order a
  family queue on **what it lacks** — never opened, then tried and failed, then read — and **may
  never order it on a traveller**, which is entry 44 and is why entry 126's residence signal is not
  the answer here. A host that stops answering is **slowed first**, its spacing doubling per
  consecutive transport failure to an 8s ceiling, and **given up on after six in a row**, any
  response clearing the streak; that is not entry 35's forbidden retry, which governs an authority
  that has *stated* something. Measured on Australia: members attempted **25 → 50**, read **3 →
  12**, and **6 of 11** new mission hosts entered *through the directory* against the previous
  build's **0 of 10**. `uae.embassy.gov.au` is **still 0** — the family has 169 members, a build
  walks about 25, and that last gap is a budget argument rather than a defect.

  **`mission_labels` was 184 of 198 countries carrying only their ISO code, and is now 723 labels
  (entry 134).** Name forms are derived from the file; cities are curated, because a post is usually
  named after its city. **A label two countries could claim is dropped from both** — it would
  otherwise demote a page for the wrong country through `foreign_post_labels`' -45.

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

  **And establish it from what the page states, not from a vendor's scaffolding (entry 109).**
  `cdn-cgi/challenge-platform` appears on Cloudflare's **block** page as well as its challenge page,
  and while it was a challenge marker this program pointed the renderer at `travel.state.gov` —
  which answers *"Sorry, you have been blocked"* with no script to run — and recorded the false
  reason that the authority had asked it to prove it is a browser. A body saying "you have been
  blocked" or "attention required" is now a refusal **before** any challenge marker or header is
  consulted, and that ordering is deliberate.

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
  governs them in full. Built in entry 75: `challenged` is its own outcome, both paths render one
  under the run's render budget, and the interface says *"does not permit automated retrieval"*
  only of `blocked`. **Half the challenges met on 2026-09-16 cannot be answered**: they load
  Cloudflare's script from `challenges.cloudflare.com`, which the render gate refuses, so they stay
  `challenged` — TODO item 61, the owner's decision (entry 179).

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
  traveller does, and that stays live. A **plan is a rendering, never a stored fact**:
  only the model's *draft* may be reused, for byte-identical inputs inside the page TTL, and every
  request still checks its quotes, validates it and grades its status itself (entry 178). A `visa_rule`
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
  conditional. A country with **no** corpus simply crawls, exactly as before. **Refusing on a
  miss is dropped (entry 173).** It was only ever safe once search left the request path, and entries
  148 and 159 keep search on every corridor. The constraint above still holds, by construction.
- **A stored row records when the evidence was retrieved, never when the row was written.** A failed
  refresh serves cached text flagged `stale` and **keeps its original `fetched_at`**; only a validator
  match moves it, because a `304` proves the text is still current (entry 4). Past
  `source_maximum_stale_hours` a stored page is **refused rather than served**. Both hold in any store,
  and both are easy to lose in a migration — a schema that collapses `retrieved_at` and `row_written_at`
  starts lying about how current its guidance is. A content-hash change **marks** a source and may never
  auto-swap a role-bearing one: that is the wrong-checklist failure with the human removed.
- **A visa-free plan is an entry plan, and it may only be built on a *stated* decision (entries 95
  and 96).** When `visa_required` is `False`, `application_steps` carries the **entry** steps — an
  arrival card, a passport-validity rule, onward travel — and `requirements` is empty. It must never
  be produced from a tool, a blocked page, or a plan with `decision_is_unverified`: a wrong "no visa
  required" that suppresses four questions is worse than a wrong one that leaves them visible,
  because the traveller has nothing left to notice the error with. That guard is mostly older code —
  extraction forces `visa_required` to `None` whenever `decision_is_unverified`, so `False` on a
  final plan already means a page said so.

  **One silence counts as saying so — the owner's decision, entry 172.** Absence from the
  authority's own visa-required list states that an unlisted passport needs no visa. It holds only
  within the bounds written into `extract_visa_plan.txt` rule 8e:
  - the whole list was read;
  - every name, footnote and exception was checked;
  - it is a list of who *needs* a visa and nothing else;
  - no other source says a visa is needed, or the decision stays null.

  The bounds live in the prompt, not in code, and they are all that stands between a silence and a
  confident wrong "no". **Do not widen them to another kind of silence without a decision entry.**

  **A second silence decides the other way — the owner's decision, entry 197.** Where an authority
  states the general rule that a foreign national needs a visa and its own complete exemption list
  leaves the traveller's country out, the plan says a visa **is** required (rule 8f). Japan is the
  case: MOFA's "in principle … required to have … a visa" and its 74-country list. Its bounds mirror
  8e's, the rule must be stated rather than inferred from the list existing, any exemption the
  traveller might meet keeps the decision null, and **an exemption list never decides "no visa"**.

  **A visa on arrival is a visa — the owner's decision, entry 199.** Where every route the sources
  describe for the passport issues a visa, in advance or on arrival, the plan says a visa **is**
  required even when which route applies turns on something the profile does not say (a UK
  residence visa, for the UAE); that condition becomes an unresolved question (rule 8g). Any
  visa-free way in the traveller might meet keeps the decision null.

  **The entry-step floor is no floor, and that is a decision rather than an omission (entry 96).**
  Three visa-free corridors state **3**, **~5** and **~7** entry duties, so the honest list has no
  natural minimum and its low end is already under the application's four. A floor there would be a
  quota, and a quota on a list with no evidence left to draw from invites a model to invent an entry
  duty — the alarming-wrong-answer class. `_check_step_count` keeps four for an application, withholds
  it entirely from an entry plan, and is *also* the guard: "fewer than four steps" and "only a stated
  no" are the same check read from two sides. **Do not add a minimum back "so the panel is not
  empty"** — an empty entry list means the pages stated a decision and no duty, and the interface
  drops the panel.

  **`where_to_apply` is permitted to be `None`, never forced to it (entry 96 corrects entry 95).** A
  visa-free American still needs a UK **ETA** — applied for, paid for, waited on — and forcing `None`
  would delete the one thing that stops them at the gate. Singapore is the case where nothing arises;
  the United Kingdom is not. `validate_requirement_sources` is what keeps this safe and is unchanged:
  a step may link to an application route only where there is one.

  **Three things the spec did not name are conditioned on a stated no, and one clause never moves.**
  `validate_absent_checklist` no longer demands "what could not be answered" from a plan where
  nothing failed to be answered; `resolve_plan_status` no longer grades such a plan `partial` for
  ever; and extraction's `if application_source_ids and not requirements: raise` no longer reads a
  correct empty checklist as a failed model call (entry 98) — a destination that *designates* a
  checklist designated it for the travellers who apply. `validate_absent_checklist`'s first clause
  is untouched and is the one this project exists to enforce: with no designated document source, a
  plan may not list a single requirement.
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

Over two hundred and fifty written-down diagnoses have been contradicted by a run; they are in
[CORRECTIONS.md](CORRECTIONS.md). **Read the rows for the area before changing it**, and add a row
whenever a run contradicts what a file said.

Prefer a run, a test, or a printed result over a careful reading. When a TODO item proposes a fix,
**measure the proposal before implementing it** — three of the rows in CORRECTIONS.md are proposals that were
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
.venv/bin/visa-discover pagetext --purge-interstitials  # drop stored bodies that are a bot-check page
.venv/bin/visa-discover selection-recall       # grade what was chosen to read; no network, no model
.venv/bin/visa-discover coverage --country NL  # is a country's corpus good enough? no network, no model
.venv/bin/visa-discover contention --destination netherlands --nationality PH --from PH  # curate an oracle row
.venv/bin/visa-discover contention --destination czechia --nationality IN --from GB --outside-pool \
    --role document_checklist                  # ...from the 94% the selector is never shown
```

**Two different questions, two different commands, and they must not be merged.** `coverage` asks
whether the **store** holds the answer; `selection-recall` asks whether the **corridor** then finds
it. A single number covering both would hide which half failed.

**A third question was unaskable until 2026-09-02: is the answer a page the selector is ever
*shown*?** `_choose_what_to_read` pools on `best_combined() > 0` — 6% of the corpus — and the oracle
was curated from inside that same filter, so it could not name a page the gate removed and reported
88 of 88 answers pooled, a tautology (entry 123). `contention --outside-pool` now ranks the
zero-scoring candidates by their own stored text (`PageTextStore.rank`, the one instrument that
reads inside a page), each row records `curated_from: pool | whole_corpus`, and `selection-recall`
prints a **pool audit** splitting a row's answers into pooled, outside, and absent from the corpus.
**The first row curated that way found a real answer in the 94%** — Czechia's EC supporting-documents
list for applicants in the United Kingdom, at 0.0 for every role (entry 127). Do not read a zero in
that audit as a result while every row still says `curated_from: pool`; the report says so itself.

**`coverage` says `ungraded` when it cannot grade, and 37 of 53 countries are** (entry 120; 42
until entry 137 widened the family gate, which moved BG, CA, GR, MT and NO). A
country with no per-traveller family and no oracle row is graded by neither half; it used to borrow
the wording of a pass. **Do not read that as 42 curation jobs** — the oracle grows one country at a
time, when a specific question needs the store-versus-selector split and a corridor run has failed
to settle it.

**A stored body can be a bot-check page rather than the authority's, and 414 were** (entry 117).
`is_challenge` truncated the body at 20,000 characters and Cloudflare's marker sits past it, so an
unanswered challenge was stored as the page and marked `readable`. Fixed, and the stores were
purged; **if a country ranks strangely, check for it before blaming the vocabulary.**

**Live search still runs on every corridor, including from the webpage, and that is now a measured
decision (entry 159)** — `_resolve` searches before it reads the corpus, and the corpus can only
suppress the *crawl*. Measured 2026-08-30: of
382 pages read by runs postdating their corpus, 59 were not in the corpus and **all 59 came from
search**, 17 covering a role nothing else in the run covered. So the corpus is not a superset even
where it is large, and **search may not be switched off for a country without measuring that
country** — entry 173 keeps the method, and entry 159 is why search stays.

**53 countries have a corpus in `var/corpus/` and a text index in `var/pagetext/`** — the ten of
entry 85 plus the 43 of entry 116. Only **BR and UY** are researchable without one, at a single
authority domain each. A country without either crawls in the request path and has its pages chosen
by the heuristic, exactly as before, which is the ordinary path and never a failure.

**Nine corridors were run over the new stores and all nine answered from them** — every one printed
"the crawl was skipped" (entry 116). Three served a Nigerian traveller that country's *own* pages
for them: China's Nigeria embassy, Portugal's and Slovakia's Abuja embassies.

**A one-host corpus is a trust-configuration symptom, not a crawler one.** Germany's held 1,565
entries on `www.auswaertiges-amt.de` alone until `diplo.de` was reviewed, then 5,712 across 87 hosts
(entries 107, 108). Read `authority_domains.yaml` before touching crawl settings.

**An offline build answers a browser challenge and a corridor barely can.** Both pass the renderer;
what differs is the budget — `DEFAULT_CORPUS_RENDERS` is 400, because a build has no traveller
waiting (entry 92). **The corridor path has two render budgets and they are easy to confuse:**
`MAXIMUM_CRAWL_RENDERS` is **12** on the crawl fetcher, while the pages that become *evidence* are
read by `LiveSourceFetcher` at `maximum_renders` = **5** — and `_fetch_bodies` calls it **once** for
the whole shortlist, so up to twenty pages share five renders. **One host may not take them all**:
three consecutive renders that come back with nothing readable and this run stops offering that host
any, which is `CHALLENGE_FAILURES_PER_HOST`'s rule on the crawl side. A success resets the count, so
a host where rendering works never approaches it. **A page that was not rendered says which bound
stopped it** rather than reporting itself as empty (entry 135). A host whose challenge cannot be answered is given up on
after **three consecutive** failures, so it costs three renders rather than the job. Entry 41's line
is unmoved: a bare `403`, a `401` and a `429` state a decision, are never rendered past, and never
reach the renderer.

**A corpus records far more than it reads — 3 to 15% of its entries were ever opened — and the page
answering a *specific* traveller is usually one hop below something it recorded and never opened**
(entry 88). An unopened address is still a usable candidate; its children do not exist in any form.
A **per-traveller family** — one page published once per country, `…/schengen-visa/apply-{country}` —
therefore gets a reserved share of an offline build's budget, one queue per family taken in turn, and
**zero on the request path**, where a corridor has one traveller. Only the Netherlands has been
rebuilt this way. The ceiling it hit is not the crawler's: for most residences the Netherlands
publishes its checklist on **VFS Global**, which the trust rule refuses — see TODO items 35 and 36.

**Run `visa-discover eu-store` before a rebuild and after the EU visa regulation is amended** — the
Schengen corridors read the newest consolidation it last found (entry 201).

Clear `var/cache/` when testing a retrieval change, and `var/corridors/` when testing a discovery
change — either one will serve a pre-change result and make a fix appear not to work. **And clear it
for both arms or for neither**: a cold-cache run faces a different web from a warm-cache baseline —
measured 2026-09-05, `blocked` went 1 → 15 and `challenged` 15 → 27 across 53 corridors, which was
enough to read as a two-point regression the code had nothing to do with (entry 136). A stored
corridor is kept for three weeks. **`var/corpus/` and `var/pagetext/` are deliberately not cleared
between runs**; they are stores, not caches, and rebuilding one costs search quota. Clear `var/plans/` too when testing a change to the plan call that its reuse key cannot see — the key covers the prompt, the packet, the schema and the model settings, not how the call is sent (entry 178).

`var/pagetext/` holds the body text of pages already fetched, one SQLite/FTS5 file per country, and
is filled two ways: `visa-discover corpus` keeps what it reads, and `pagetext --backfill` indexes the
retrieval cache for nothing. It is **ranking input only** — see the rule above, and entry 78.

**Two different things read this index and only one of them is on.** `discovery_selector: model`
**is on** (entry 85): a model reads stored text for every candidate in contention and picks up to 20
pages to fetch, replacing the shortlist as the recall gate, at the cost of a second model call per
corridor. **What "every candidate in contention" means is `best_combined() > 0` — 6% of the corpus
(entry 123) — plus the five best per role that the link scored zero and their own stored text puts
back (entry 158). A page scoring zero on its link with no stored text is still never shown.**
**And a big pool is cut before the model sees it (entry 195, the owner's decision):** the 120
likeliest by `fusion_order` — link rank and stored-text rank per role — plus the 40 best-linked
pages with no stored text, so at most 160; the notes say how many were withheld, and the recall
log marks each one `withheld_from_selection`. On replayed packets that found more roles than the
whole pool at 42% less input (entry 194). Graded against `oracle/selection_oracle.yaml` —
ground truth neither selector helped build, though curated from that same 6%
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
is (`SearchQuotaExhausted` / `SearchThrottled`), and the provider paces itself from one lock so
`search_all`'s concurrency cannot trip a capped plan — entry 74. **That pace was 1.3s and is now
0.05s** (entry 141): the account allows **50 queries a second**, so 1.3s was 65× too conservative and
cost 18.2 seconds of every corridor for nothing. Pace does not affect spend. **A search outage no longer kills
a country that has a corpus**: it falls back to the stored pages, says so, and is never kept for
reuse. With no corpus the refusal stands, because *we could not look* must never become *there is
nothing to find*.
