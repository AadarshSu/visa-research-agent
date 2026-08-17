# Decisions

Why the project is shaped the way it is, including what was tried and rejected. The reasoning is
recorded because it is the part that cannot be recovered from the code later — a deleted feature
leaves no trace, and a rule with an obvious-looking alternative invites someone to "simplify" it
back into a bug.

Newest first. Add an entry when a decision is made, not afterwards.

---

## 24. A fetch place is not spent on a page already proved unreadable
**2026-08-17**

Inspecting the US shortlist directly showed **five of its ten fetch places going to pages that
cannot be read**: `sample2.usembassy.gov` — a documentation sample host that does not exist in DNS —
scoring highest of everything at 122.2 and taking the place reserved for the mission network,
`go.usa.gov` twice (a decommissioned shortener, also no DNS), and `travel.state.gov` twice (the 403).
Brazil spent one of its ten on `brics2019.itamaraty.gov.br`, likewise dead. Ten places decide what is
read, and only a read page can fill a role, so this was the largest remaining waste in a corridor.

**Decided: drop a candidate only for a failure already observed, never for one predicted.** Two
kinds qualify, and the distinction between them is the whole design:

- **A host whose name does not resolve** is skipped for every path beneath it. DNS failure is a fact
  about the *host*, so nothing under it can be read.
- **A URL an authority refused** is not requested again. Asking twice is a retry, which is the one
  thing a block must never provoke, and it would answer the same way.

**Detected by exception type, not by message.** `host_does_not_resolve` walks the cause chain for
`socket.gaierror`, because the wording differs per platform — macOS `[Errno 8] nodename nor servname
provided`, Linux `[Errno -2] Name or service not known` — while the exception type does not.
`CrawlFetcher` now records a `FailureOutcome` beside each prose reason, which also lets
`inaccessible_domains` be derived from `outcome == "blocked"` instead of matching the substring
"refused automated retrieval" in a sentence someone could reword.

**Deliberately not skipped: everything else.** A page that was too large, was not HTML, or answered
`502` stays a candidate, because **retrieval is not the crawler** — it reads PDFs, renders, and
carries different limits, so a page the crawl could not use may still be readable evidence. Losing a
real page costs a refusal, and that is the more expensive mistake.

**Measured, 2026-08-17.** Three of the five places came back, and they went to real pages:
`in.usembassy.gov/apply-for-a-nonimmigrant-visa` (95.6), `in.usembassy.gov/immigrant-visas`, and
`www.usa.gov/non-immigrant-visas` now sit in the shortlist where dead hosts did. Identical across two
cleared-cache runs. Brazil's roles are unchanged, all still filled including the Edinburgh checklist.
China is untouched by design: its unreadable hosts answered `502`, which stays a candidate.

**`document_checklist` is still unfilled for the US, and the freed places did not change that** — the
prediction in the todo that they might was wrong. The canonical B1/B2 checklist is on
`travel.state.gov`, which is blocked, and no mission page was judged to be one. That is the honest
outcome rather than a remaining bug.

**What is left, and why it was not taken.** Two places still go to `travel.state.gov`, because those
two URLs were never crawled — one is a PDF, which the crawl skips by design — so nothing was observed
about them and the per-URL rule does not apply. Skipping the whole host would recover them, and
`travel.state.gov` has in fact refused every request made to it. It is not taken here because a `403`
on one path is genuinely not evidence about another: real sites refuse some paths and serve others.
Recorded in [TODO.md](TODO.md) as a measured follow-up — a host that has refused every request and
served none — rather than assumed now.

---

## 23. Entry 14's decision never reached a traveller, because extraction refused first
**2026-08-17**

With the corridor fixed (entry 22), `united-states/IN/IN/tourism` still answered *"The visa plan
could not be generated safely."* Discovery resolved; the **extractor** refused:

```
LLMExtractionError: Application document sources are not available in this run
```

**The bug is an unimplemented decision, not a new one.** Entry 14 stopped a missing checklist
refusing the corridor and built `VisaPlan.validate_absent_checklist` to make the resulting plan safe:
with no document source a plan may state the gap but never fill it. `VisaPlan.requirements` was
documented as *"May be empty: some authorities publish no checklist"*. But
`openai_extraction.extract` still required `application_document_source_ids` to be non-empty, so that
validator could never run and no traveller ever saw the outcome entry 14 chose. Vietnam — the
country entry 14 was written for — would have hit the same wall.

**Decided:** an *undeclared* checklist is a fact about the world and is allowed. A *declared but
unretrieved* one is a broken run and still refuses, before the model call, via
`require_load_bearing_sources`. The distinction is the whole point: relaxing the first must not
relax the second.

Two consequences kept deliberately strict:

- **Anything the model offers as a document requirement is dropped** when no checklist source backs
  it. Nothing could honestly cite one, so keeping it would mean publishing a checklist inferred from
  an eligibility rule or an application form — the single most damaging output this project can
  produce, and what entry 6 was deleted over. The prompt asks; the filter and the validator
  guarantee.
- **A plan with no checklist source is never `verified`.** It is missing evidence a traveller would
  expect a complete plan to rest on, and `verified` beside an empty document list is the one label
  that would hide that. `resolve_plan_status` takes `has_checklist_source` so both extraction paths
  answer this the same way. The interface already renders `partial` with a reliability block.

**Also fixed:** the old code made the model call and *then* refused, so a run that could not succeed
still cost money — contradicting the comment three lines above it. Both remaining preconditions now
run before the call.

**Verified live, 2026-08-17.** `POST /visa-plans` for an Indian passport, resident in India,
travelling to the United States for tourism: **HTTP 200 in 16.6s**, `status: partial`,
`visa_required: true`, `B-2 visitor (tourist) visa`, five application steps, three cited sources,
zero document requirements, and three unresolved questions — the first of which names the missing
checklist and points the traveller at the Department of State and their nearest post. That is the
honest shape of this corridor: the canonical B1/B2 checklist is on `travel.state.gov`, which answers
403, and by entry 18 we may not work around it.

**What this exposes, and does not fix.** The plan cannot say *why* the checklist is missing. Its
`unavailable_sources` covers only its own retrieval, and this block happened during **discovery**, so
`ResolvedCorridor.inaccessible_domains` never reaches the plan. The traveller is told the checklist
is absent but not that an authority refused us — which is the more useful sentence, because they can
open that page themselves. That is the existing todo *"Tell a traveller what an inaccessible source
means"*, now with a concrete instance rather than a hypothetical one.

---

## 22. A large government passes the same rule with far more domains, so how many is capped
**2026-08-17**

`united-states/IN/IN/tourism` refused, and not reliably: two runs of the identical corridor, one
resolved, one refused. One of the highest-volume corridors there is, decided by search ordering.

**The rule was not wrong; it was calibrated against small governments.** Entry 19 trusts a domain
that is `looks_governmental and belongs_to_destination`, and for the United States that still admits
only the US government — nothing foreign gets in. But its own top-level domain *is* `gov`, so the
second test stops narrowing anything and the whole federal namespace qualifies: `doi.gov` (the
Interior) and `federalregister.gov` alongside State and USCIS. Measured: **eight domains**, against
Brazil's one, France's two, China's four. `countries.yaml` has exactly one entry like this today,
which is why six corridors never showed it.

Width is expensive in three places at once, and this is the part worth remembering: three search
queries are run **per trusted domain**, the crawl's per-host budget is the page budget **divided by**
the hosts seeded, and the shortlist has ten places. So a wide set spends more, reads less of each
site, and makes the right page compete with more noise. The measured US bootstrap:

| domain | queries seen in | hostname hint |
| --- | --- | --- |
| `state.gov`, `usa.gov` | 4 | — |
| `dhs.gov` | 3 | — |
| `usembassy.gov` | 2 | embassy |
| `doi.gov`, `federalregister.gov`, `ice.gov`, `uscis.gov` | 1 | — |

**Decided, in two parts, neither naming a country.**

1. **The relaxed evidence bar is scoped to where it was earned.** One corroborating query is enough
   for the destination's own government (entry 19) *because* that is two independent signals. Where
   the country's own top-level domain is itself the governmental marker it is one signal, so the
   ordinary two-query bar applies. The test is which top-level domain actually matched, so it is a
   property of `countries.yaml` data and not of any country. This is what removes all four
   single-query agencies above — and it does **not** touch `usembassy.gov`, which is corroborated
   twice.
2. **A universal cap of five, ordered by the hostname's authority hint.** A bound on the consequence
   rather than a test for the cause: a large government under a plain ccTLD would cost the same.
   `suggest_kind` — `emb`, `consul`, `immi`, `mofa` — is already committed, country-neutral, and
   already used to name authorities; ordering by it is the generic form of "rank the mission network
   first", where hardcoding those names would be special-casing one country in effect.

**Five is calibration, not derivation.** It is chosen to sit above every accept in entry 19's audit
(one, two and four) so no recorded decision changes, and below the eight that caused this. Say it
plainly, because a reader will otherwise look for the reasoning that produced the number.

**Two admissions about the ordering.** Ranking the mission network above the State Department is
desirable here only because `travel.state.gov` answers 403 — a happy accident, not a principle. And
among equally-corroborated domains with no hint the order is alphabetical: a hostname simply carries
no signal about whether that part of a government issues visas. On this corridor the corroboration
bar made that moot, but a wider case would be decided arbitrarily-but-stably.

**Third part, downstream and independent of trust: the shortlist reserves a place per domain.** The
ten places decide what is *read*, and only a read page can fill a role, so an authority whose pages
all score below another's is not merely ranked low — it is absent, and the corridor refuses with the
answer one slot outside the cut. Each registrable domain's best page is now reserved one place.
Keyed on the registrable domain, not the host, or a mission network's posts would reserve every
place; that is a deliberate difference from the crawl's per-host budget, which prevents hammering
one site rather than one site starving another. Reservation is drawn from **every** candidate rather
than those already picked, since the per-role cut takes three and a domain's best page can be fourth.

**Rejected: raising `shortlist_size` from ten.** It makes the right page more likely to be read
without ever guaranteeing it, at similar cost. The floor guarantees it.

**Rejected: detecting the collapsed rule and treating that country specially.** Considered and
dropped in favour of the two changes above precisely so that no code path tests for the condition.
Nothing here can be a country-shaped fix, because nothing here asks about a country.

**Verified live, 2026-08-17.** The US corridor run three times with `var/cache/` and `var/corridors/`
cleared between runs gave **identical** results each time — trusted set `usembassy.gov`, `state.gov`,
`usa.gov`, `dhs.gov`; `visa_decision`, `application_route` and `general_entry` filled by the model;
twelve corridor queries where eight domains had produced twenty-four. `document_checklist` stays
unfilled, correctly: the canonical B1/B2 checklist is `travel.state.gov`, which answers 403, so it is
reported as `blocked` and nothing is substituted (entry 18). Brazil filled every role including the
Edinburgh post for a UK applicant; China returned its checklist and fees and still declined
`visa_decision`, matching what entry 17 recorded. No corridor changed for the worse.

**What the runs also showed, and did not fix.** Half the US shortlist is spent on hosts that cannot
be read: `sample2.usembassy.gov` and `go.usa.gov` do not resolve in DNS, and two `travel.state.gov`
pages are the 403. The reserved place for a domain goes to its best-scoring candidate even when the
crawl has already recorded that host as unreachable, so Brazil spends one place on
`brics2019.itamaraty.gov.br` the same way. Recorded in [TODO.md](TODO.md) rather than fixed here: a
DNS failure is host-level and definitive, but a 403 on one path is not evidence about another, so the
two cannot be skipped by the same test.

---

## 21. Any country is a destination, and a country name stops matching inside a word
**2026-08-16**

The interface still offered the seven entries in `destinations.yaml`, most of them disabled, and
its copy announced research "for an ordinary Indian passport holder resident in the UK". Both were
left over from when that was true.

**Decided:** the destination list is every country the agent holds reference data for, and the copy
describes the product rather than one traveller. `countries.yaml` grew from 14 to **198**. A country
is now identified by a slug derived from its name, so "United Arab Emirates" and
"united-arab-emirates" reach the same place however a caller writes it.

The fourteen curated entries keep their hand-written synonyms, demonyms, host labels and mission
cities, learned from corridors actually run. The other 184 carry only what can be stated without
guessing: the name and the ccTLD, which is the ISO alpha-2 lowercased for every one of them.
**`tlds` is the load-bearing field** — it is what decides whether a domain belongs to the
destination's own government, the rule that replaced human approval. The rest are scoring aids the
model decider does not need, so a generated country is fully researchable, just with weaker hints.

**A live bug this uncovered, and the reason the expansion was not safe without it.**
`_matches_country` matched country tokens as **substrings** of link text. Its own docstring promised
codes are "never matched inside a word", but that guard was only ever applied to path segments. So:

    "Business visa"   -> vetoed as United States      ("us" inside "business")
    "Chadwick House"  -> vetoed as United States      ("us" inside "House")

`wrong_country` is a **veto**, so every business-purpose corridor was silently throwing away its
most relevant page. Matching is now on word boundaries. Adding 184 more country names to a
substring veto would have multiplied this — "oman" sits inside "Romania", "chad" inside "Chadwick" —
which is what made the bug worth finding before the data grew.

**Verified after the change:** Brazil still resolves the Edinburgh checklist with 198 countries in
the veto list, and a page genuinely about another country is still rejected.

---

## 20. The traveller becomes input; countries become codes
**2026-08-16**

The last fixed piece. `TravellerProfile` was one constant — Indian passport, UK resident, tourism —
with `uk_immigration_status` and `uk_permission_expiry` baked into the model and `travel_purpose`
narrowed to `Literal["tourism"]`.

**Decided:** the profile comes from the request. Three things are required, because three things
select the guidance: the passport, the country applied from, and the purpose. Everything else is
optional — a plan that does not use a detail should not ask for it, and this is personal data.

**Countries are stored as ISO codes, not names.** A name has many spellings and a code has one, and
every corridor, cache key and lexicon lookup is already keyed by code. The API accepts whatever a
person wrote — "IN", "in", "India", "Republic of India" — and normalises once, at the edge. A
country with no reference data is refused there too, before anything runs, because without its own
domains and demonyms the right pages cannot be identified.

**But the model is shown names.** The packet renders "India (IN)": codes are the canonical *key*
and the wrong *input* for something reading government prose, where an entry table may say either
and the prompt forbids using knowledge the packet does not contain. Caught by a test that had
asserted "India" and started seeing "IN" — the assertion was right and the change was wrong.

**`uk_immigration_status` became `residence_status`, and optional.** Not a rename: a citizen of
where they live holds no permit. It stays because it is frequently decisive — Brazil and China both
require a non-citizen resident to prove regular status, and the Brazil plan cited exactly that.

**`passport_type` stays `Literal["ordinary"]`, deliberately.** Diplomatic and official passport
pages are a hard veto in discovery's scoring (entry 8), so those travellers cannot be researched.
Widening the field would let a request be accepted and then answered with the ordinary-passport
rules, which is precisely the confident wrong answer this project refuses. Refusing at the schema
is the honest form.

**Verified:** a corridor nobody had run — Chinese passport, resident in the UAE, to Brazil —
resolved to Brazil's **visa waiver page for China**, where the same destination for an Indian
passport resolves to a VIVIS document checklist. The traveller changes the answer, end to end.

---

## 19. The human approval gate becomes a rule, not an absence
**2026-08-16**

Discovery was an offline command whose output a person reviewed before anything could serve a
traveller (entry 7). The product needs destinations nobody has configured, so that gate is removed
and discovery runs in the request path.

**What removing it does not mean.** The gate was the concentration point for the entire added risk
of search (entry 11), so deleting it outright would put a commercial visa agency one lucky ranking
away from being quoted as an authority. Reading back six real bootstraps, the human was not
exercising taste. Every accept and reject reduced to one question — *is this the destination
country's own government?* — which is `looks_governmental and belongs_to_destination`, both already
computed. Checked against all 22 recorded decisions: **22 agreements, 0 disagreements.**

**Decided:** `destination_mode: automatic` resolves an unconfigured destination at request time,
trusting only domains that pass that rule. What it keeps out is the point: France's bootstrap
surfaced `axa-schengen.com`, a commercial travel insurer; Vietnam's ranked `usembassy.gov` first, a
real government describing the rules for *Americans*; Brazil's offered VFS, an appointed provider
that by design cannot pass domain trust.

Everything downstream is untouched. Public suffixes are still refused, so `gov.br` cannot be
trusted whole. Pages are still fetched only from approved domains, redirects and renders still
re-checked, a corridor missing a load-bearing role still refused, and `VisaPlan` still rejects a
checklist with no source behind it. If no own-government domain is found, **nothing is fetched**.

**Verified end to end.** Brazil, which has no configured sources, produced a `verified` plan:
visa required, Visitor Visa (VIVIS), six requirements each citing a discovered page — including
"proof of regular UK immigration status", correct for an Indian national resident in the UK.

**Why this is safe to ship without human review**, in the product's own terms: the plan promises
nothing. It shows information, shows its citations, and says plainly what it could not verify. The
traveller decides. That only holds while the refusals stay honest, which is why every refusal path
above is load-bearing rather than decorative.

**A latent crash this surfaced:** a search engine returns titles far longer than any anchor text,
and `PageLink.text` caps at 300 characters. China's ministry returned a 300-plus character speech
headline and the corridor raised instead of trimming. Search titles are now truncated exactly as
crawled anchor text always was.

**Still fixed, and next to change:** the traveller profile. The corridor is derived from it rather
than hard-coded, so making it variable changes one function instead of the request path.

---

## 18. A block is not a fact about the guidance; never work around one
**2026-08-16**

France's portal answers `403` to anything that is not a browser. A headless Chromium would very
likely pass that check, and the renderer is already built and already trusted. The tempting fix is
one line: render on `403` as well as on thin text.

**Decided: never.** No user-agent spoofing, no pointing the renderer at a refusal, no retrying past
a rate limit. The reasoning is about what a block actually licenses us to say. It is not evidence
that the guidance is wrong, missing, or stale. It supports exactly one claim:

> We cannot independently retrieve and verify this in this execution environment.

That is narrower than "unreachable", and far narrower than anything that would justify filling the
gap from a different page. So the source is marked inaccessible, the role goes unfilled, and
nothing is inferred in its place. `FailureOutcome` gained `blocked` to say it precisely, and
`ResolvedCorridor.inaccessible_domains` carries it as data rather than prose, so a refusal can
never be mistaken for "nothing found".

**Why this is a feature.** The alternative architecture is "if France blocks us, figure out how to
defeat the bot protection", and that is a posture, not a patch — it would sit oddly beside every
other rule here, all of which prefer refusing to guessing. For visa requirements specifically,
inferred or stale information sends someone to a visa centre without the right papers. A product
that cannot verify something should say so.

**What it costs, stated plainly:** France is unservable. Singapore's VFS page stays unread. That is
the correct trade, and it is recorded in `CLAUDE.md` under the rules that must not be broken,
because the "helpful" one-line fix will occur to someone again.

**Not the same as:** reading a page a site serves us normally. Rendering client-side pages stays on
demand and unchanged — that is running a page the way it was published, not circumventing a refusal.

---

## 17. France and China: the decider refuses well, and the wall is now access, not ranking
**2026-08-16**

Two fresh corridors against the model decider, neither built against. Both **exit 2**, and what
they refused on is the finding.

**France.** Both approved government domains answer **HTTP 403** to anything that is not a browser
— `france-visas.gouv.fr`, the authoritative portal, and `www.diplomatie.gouv.fr`. Ten pages were
still fetched from paths that slipped through, so the model had ample plausible material. It filled
only `general_entry`, and refused `visa_decision` and `document_checklist` outright. That is the
behaviour the containment was built for, tested under real pressure rather than with a fake.

**China.** Reachable, and the two roles it filled are the best evidence yet that judgement beats
scoring. For `document_checklist` it chose the UK embassy's own page and justified it with "names
the required passport, photo, **UK legal-stay evidence for non-British applicants**, and round-trip
tickets" — it noticed the traveller is an Indian national *resident in* the UK, which no keyword in
the lexicon expresses. For `fees` it read a rate table and reasoned "gives the rate for 'Other
countries,' which includes an Indian passport holder". It refused `visa_decision`, which is
load-bearing, so the corridor is refused.

**Where the limit has moved.** Of six corridors, ranking is no longer what fails. What fails now is
**access**: bot-blocked portals (France ×2, Singapore's VFS), client-rendered shells, and
502-ing endpoints. Discovery cannot judge a page it was never allowed to read.

**Deliberately not done: defeating the bot blocks.** Settled in entry 18.

**A staleness gap this surfaced**, now addressed. China's chosen checklist lives at
`/eng/visa/qzxz/201303/t20130315_3383966.htm`, and `is_archived` did not fire because it only
recognised a bare four-digit year segment. Detection is now widened — `published_date_in_path`
reads `YYYYMM`, `YYYYMMDD` and `tYYYYMMDD` — but the *consequence* deliberately is not a veto.
Measured first: **two of China's correct picks carry dated paths**, the checklist at `2013-03` and
the fee table at `2024-08`. Vetoing dated paths would have discarded the only two roles that
corridor resolved. Publication is not staleness, and a URL cannot tell them apart. So the date is
reported — to the adjudicator, which holds the page's text and can weigh the two, and in the
proposal, where a human sees "published in path: 2013-03" beside the choice.

---

## 16. Judgement decides the last step; heuristics decide everything before it
**2026-08-16**

Entry 15 recorded that keyword ranking does not generalise. Two fixes followed — a checklist is
identified by the documents it *names*, and the post serving the traveller governs the roles that
depend on the post — and both worked: Brazil picked the right page, Japan and Singapore held. But
they worked by adding **27 English document nouns** and per-country city labels in Portuguese, and
that is a treadmill. It will not survive an authority publishing in Thai.

The decisive observation is *where* the failure was. In every Brazil run the correct page was found
by search, passed domain trust, survived the crawl, made the shortlist, and was fetched and read
with its full text available. Only the final choice among ten trusted, already-fetched pages was
wrong. Everything upstream — the safety-critical part — was right.

**Decided:** keep search, trust, crawl, shortlisting and refusal deterministic, and ask a model
exactly one question: which of these fetched pages fills each role. `ResolvedSource.decided_by`
was already `Literal["heuristic", "model"]` and `ResolvedCorridor.model_calls` already existed —
the seam was designed in and left unused.

**The containment is the whole safety story**, and none of it may be removed:

- the model chooses from an explicit list of candidates the application built; an id it invents is
  **discarded** and the role left unfilled, so it can never introduce a page that did not pass
  domain trust;
- it never widens trust — officialness was settled by who controls the domain, long before this
  runs;
- page text reaches it under `untrusted_content` and the prompt says so;
- it may refuse, and is told refusing beats guessing;
- heuristic scores are **withheld** from the packet, because passing them would anchor the model to
  the very ranking that got Brazil wrong;
- a failed call falls back to the heuristic, so a corridor degrades to a worse answer, never none.

**Measured on all four corridors** (`discovery_decider: model`): Brazil picks the Edinburgh
checklist and explains why — "it specifically lists the application form/RER, valid passport,
passport photo, return-ticket evidence, financial evidence" — and reads India's row out of a
national visa table for the decision. Japan picks the UK embassy's items-required page. Singapore
puts five roles on the ICA per-nationality page, arriving unaided at what entry 9 had to be taught.
**Vietnam still refuses the checklist**, which was the risk worth testing: the model did not invent
one where none is published.

**Rejected — staying fully deterministic.** It keeps zero model calls and total explainability, but
buys them with a new failure mode per country and per language, and Brazil showed those failures are
silent.

**Rejected — model classification earlier in the pipeline.** Letting a model decide what to crawl or
what to trust would put it upstream of the domain rules, which is the one place it must never be.

**What this costs:** one model call per corridor, non-determinism in the final choice, and a new
dependence on `OPENAI_API_KEY` for `visa-discover`. The heuristic path remains, is tested, and stays
the regression baseline.

---

## 15. Brazil, the out-of-sample test: discovery ranks the wrong page, confidently
**2026-08-16**

Discovery's scoring was tuned against Singapore and Japan; Vietnam turned out to publish no
checklist, so it could not test ranking. Brazil is the first corridor that genuinely could, and the
answer is that **ranking does not generalise**. Recorded rather than fixed, deliberately: this is
the only out-of-sample signal there is, and tuning weights to make it pass would spend it.

`visa-discover corridor --destination brazil --nationality IN --from GB` **exits 0** — every
load-bearing role filled, full confidence — and picks this as the document checklist:

    43.1  embaixada-riade/how-to-apply-for-services-on-e-consular      (Riyadh, Saudi Arabia)

The correct page exists, was found by search at depth 0, was shortlisted, and was fetched and read:

    32.3  consulado-edimburgo/.../visit-visa-vivis-1/tourism-and-transit-vivis   (Edinburgh, UK)

It ranked **third**, behind Riyadh and a Kuala Lumpur page. So this is not a crawl or a rendering
failure — the right answer was in hand and the ranking rejected it.

**Finding 1 — the scorer rewards pages that talk *about* documents over pages that *list* them.**
The Riyadh page is generic e-consular boilerplate; it scored `body:documents required+25`,
`body:required documents+25`, `body:application documents+18` purely by repeating the phrases. The
Edinburgh page is the actual checklist and names passport, bank statement, proof of funds,
itinerary and return ticket — in prose, without chanting "documents required". Singapore and Japan
hid this because their checklists happen to contain the literal phrases too.

**Finding 2 — mission detection is inoperative for a consolidated portal, and it is not latent.**
`_mission_domains` returned `[]` for Brazil. It looks for the residence country's label in the
*host*, but Brazil publishes every mission on one host with the post in the *path*
(`www.gov.br/mre/pt-br/consulado-edimburgo`). So Riyadh, Kuala Lumpur, Atlanta and Abu Dhabi
compete on equal terms with Edinburgh for a UK applicant, and four of the six resolved roles came
from missions on the wrong continent. This was recorded as a latent gap; Brazil shows it changing
the answer.

**Finding 3 — the failure is silent, which is the worst part.** Exit 0 means "every load-bearing
role filled". Nothing in the output suggests the checklist belongs to a different mission from the
one serving this traveller, because nothing checks that. A refusal would have been safe; this is a
confident wrong answer, the outcome entries 5 and 6 exist to prevent.

**Not fixed here, on purpose.** Any change now would be fitted to Brazil. The honest next step is
to decide what *should* rank a checklist — plausibly: does the page name specific documents, and
does it belong to the mission serving this traveller — and only then to look at whether Singapore
and Japan still pass.

---

## 14. A missing document checklist stops refusing the corridor
**2026-08-16**

Entry 13 established that Vietnam publishes **no document checklist anywhere** on its approved
domains — its e-visa states requirements as upload fields inside the application form. Discovery
treated `document_checklist` as load-bearing, so Vietnam refused permanently for having correctly
observed reality.

**Decided:** `LOAD_BEARING_ROLES` is now `("visa_decision",)` alone. A corridor resolves without a
checklist; `visa-discover` exits `1` rather than `2`, and the absence is still named in
`unresolved_roles` and the notes via a new `REPORTED_ROLES`. Vietnam now resolves at exit 1 with
`visa_decision`, `general_entry`, `application_route` and `fees` filled.

**The reservation, recorded because it did not go away.** Discovery cannot distinguish *"this
country publishes no checklist"* from *"one exists and we failed to find or read it"* — a crawl that
stopped short, a language we do not score, a bot-block. Both emit the same note. Accepting the
absence everywhere therefore converts every find-or-read failure into a plan with a silently missing
checklist, and those are the more common case. A per-country human declaration was proposed instead,
matching how `trusted_domains` works; the global relaxation was chosen deliberately over it.

**What makes it survivable, and must not be removed.** The absence is carried structurally rather
than trusted to the prompt. `VisaPlan.validate_absent_checklist` refuses any plan that, with no
document source, either lists document requirements or stays silent about the gap. So the failure
mode this opens is a *visibly* incomplete plan, never a confidently invented checklist — the
distinction entry 6 was deleted over. Deleting that validator re-opens the worst outcome this
product can produce. The prompt gained a matching rule (8a), but the prompt is the polite request
and the validator is the guarantee.

**Fixed alongside, and independently a bug:** `load_bearing_source_ids` was
`required_source_ids or application_document_source_ids`. The `or` meant that naming any required
source silently discarded the checklist requirement — a destination could declare a checklist and
still produce a plan without it. It is now a union.

**Still open:** nothing tells a reviewer which of the two cases they are looking at. If plans start
shipping with empty checklists for countries that *do* publish one, that is this decision failing,
and the per-country declaration is the fix that was already designed.

---

## 13. Render client-side pages, on demand only, trusting nothing new
**2026-08-15**

Whole corridors were unservable because the authority publishes a client-rendered page. Measured
before deciding, through the project's own cleaning: `evisa.gov.vn` gave **39** readable characters;
`xuatnhapcanh.gov.vn` gave **402**, and those 402 turned out to be *translation keys*
(`home.banner-huong-dan-viet-nam`, `lienKet`) with the real strings fetched client-side.

That second finding decided more than the first. 402 characters **clears the 400-character floor**,
so a page saying nothing would have passed into extraction as though it were official guidance —
the wrong-checklist failure the floor exists to prevent. Whatever was decided about browsers, that
hole had to be closed, so `looks_untranslated` marks such a page unusable. It was checked against
all 13 configured Singapore and Japan sources first: **zero false positives**.

**Decided:** a headless Chromium behind a `PageRenderer` protocol, attempted at exactly one point —
after an ordinary fetch already failed to produce readable text. Pages that work today never meet a
browser. `render_mode` in `runtime.yaml` is committed as `never`; Playwright is an optional extra.

**The trust model did not move**, which was the precondition for doing this at all. Every request
the rendered page makes — document *and* subresource — is aborted unless its host is already
approved. Verified live: rendering `evisa.gov.vn` blocked `firebase.googleapis.com`,
`firebaseinstallations.googleapis.com` and `www.googletagmanager.com`, and the page still rendered
to 21,853 characters of real guidance. Where a render lands is re-checked exactly as a redirect is.

**Rejected — always rendering.** Slower on every page, and it exposes the pages that already work
to a whole new class of failure for no gain.

**Rejected — declining to render.** Defensible, and refusing is a supported honest outcome, but the
measurement showed this is not a scoring problem that could be worked around: the text is simply
absent from the response, however you arrive at it.

**Rejected — parsing the embedded framework payload** (the Next.js flight data) instead of running
a browser. It is per-site, per-framework, and breaks silently on redesign — the kind of fragility
that produces a confidently wrong checklist rather than a visible failure.

**Got wrong once, then fixed:** retrieval and the crawl first shared one render budget. The crawl
spent all five renders before the shortlist was read, so a working renderer produced no evidence.
Each caller now holds its own allowance. Worth remembering as a shape: a shared budget between a
broad phase and a narrow one always starves the narrow one.

**Two shortlisting bugs this exposed, both fixed.** Rendering made `evisa.gov.vn` readable, and it
*still* never became evidence. Chasing that found two defects that had nothing to do with browsers:

1. `api.evisa.gov.vn/client-service/public/ngon-ngu/get-all` — a JSON endpoint listing the site's
   *languages* — scored 56.4 and took the third and last `application_route` place, pushing every
   readable `evisa.gov.vn` page off the shortlist, then failed as "not an HTML page". Retrieval
   already refused JSON, but only *after* the fetch, by which time the place was spent.
   `is_machine_endpoint` now rejects it before it can be a candidate.
2. `_shortlist` took three per role and stopped, using **six of its ten places** while every
   `evisa.gov.vn` page sat just outside the per-role cut. The budget is now filled with the next
   best overall after the per-role picks.

Together: 6 pages read → 10, and `evisa.gov.vn` is now actually fetched.

**Vietnam still refuses, and that is the correct answer.** With both fixes and rendering on, every
one of the eight readable candidates scores **exactly 0.0** for `document_checklist` — zero, not
just below the threshold. Reading the rendered text by hand says why: `evisa.gov.vn` (21,853
characters), its FAQ (15,786) and its support page carry *eligibility* law — "not falling under
Clauses 1, 2, 3, and 4 of Article 8" — and process steps, not a list of documents. Vietnam's e-visa
states its requirements as upload fields inside the application form itself. **There is no document
checklist page on the approved domains to find.** Refusing beats nominating the eligibility page as
a checklist, which is decision 5 working exactly as intended.

**Also corrected:** Singapore's VFS page answers **HTTP 403**, a bot-block rather than a
client-rendered page, so rendering never applies to it. The handoff had recorded it under the wrong
cause.

---

## 12. Complete certificate chains; never disable verification
**2026-08-15 · commit `4032824`**

Vietnam's official e-visa portal failed TLS verification. The temptation was to skip verification
for "known legitimate" sites.

Diagnosis first: the certificate is genuine, issued by GlobalSign to Cục Quản lý xuất nhập cảnh (the
Vietnam Immigration Department), organisation-validated. The server simply omits the intermediate
linking it to the root. Browsers fetch that automatically; Python does not.

**Decided:** bundle the missing intermediates in `config/tls_intermediates/`, each verified to chain
to a root already in the trust store, so **no new trust is granted** — a server misconfiguration is
worked around and nothing else.

**Rejected:** `verify=False`, per-host or otherwise. An attacker able to intercept the connection
could impersonate an immigration authority and dictate what documents a traveller brings. That is
the single worst outcome this product can produce, and it would have been invisible.

Tests assert that expired, self-signed, hostname-mismatched and unknown-CA certificates are still
rejected, so a future "simplification" cannot quietly loosen this.

---

## 11. Search may generate candidates; it may never widen trust
**2026-08-15 · commit `42eec19`**

`AGENTS.md` said *"never add open-ended web search"*. Discovery needs some way to find pages.

Two readings were considered: crawl only within already-approved domains, seeded from official
travel-advice services; or use a search engine. Search was chosen because it is how a person
actually finds these pages and it works for any country without a per-country seed.

**Decided:** search is permitted **only inside `discovery/`**, and only as a candidate generator.
Nothing it returns becomes evidence until it passes the domain-trust rules. `AGENTS.md` was amended
rather than quietly contradicted, stating the constraint that replaces the old rule.

The resulting safety story: for *pages*, spam is structurally unreachable because results are
filtered to approved domains before anything is fetched. For *domains*, the human approves. The
entire added risk is concentrated in one human-gated decision per country rather than diffused.

---

## 10. A destination's own government outranks other countries' pages about it
**2026-08-15 · commit `50236df`**

The first live Vietnam bootstrap ranked `usembassy.gov` **first** — the US embassy in Vietnam. It is
`.gov`, so "looks governmental" passed, but it describes the rules for American citizens.

**Decided:** check that a domain sits under the destination country's own top-level domain, held as
data in `countries.yaml`. Foreign government pages still appear for review, flagged and never first.
A country's own government needs only one corroborating query, since that is a much stronger prior;
this also rescued `mofa.gov.vn`, which had been discarded for appearing once.

Found only because a third country was tested. Singapore and Japan could never have surfaced it.

---

## 9. A page can fill several roles
**2026-08-15**

Discovery originally assigned one role per page, on the assumption that a page is one thing.
Singapore's own hand-written configuration disproves it: the per-nationality page is listed as both
the decision source and the document checklist.

Forcing exclusivity meant that page won the decision role and the checklist role then went to a
narrower, wrong page. `ResolvedSource.roles` is now a list.

---

## 8. Wrong audience is a veto, not a penalty
**2026-08-15**

After fixing the above, Japan regressed to the **diplomatic passport** exemption list. It names many
nationalities, so it collected a nationality bonus and outscored the correct page.

**Decided:** hard wrong-audience terms — `diplomatic`, `official passport`, `spouse` — reject a page
outright rather than reducing its score. Some exclusions must not be outweighable by any
accumulation of positive signals. Archived paths and other-country pages work the same way.

---

## 7. Discovery is an offline command, not part of a request
**2026-08-15**

Discovery contacts many pages and changes what the application would treat as official.

**Decided:** it runs as `visa-discover`, deliberately, with a person looking at the result.
Generating a plan still visits only configured URLs and never searches. Wiring discovery into
request time is deferred until its ranking is trusted, and would sit behind per-corridor caching.

---

## 6. Structured conflict detection: built, then deliberately deleted
**2026-08-14 · recorded in commit `c4c0287`**

A deterministic conflict detector was fully built and working. The model reported what each source
said about four questions in a canonical form; the application compared them and applied precedence.
It correctly found the real Singapore discrepancy — three pages requiring six months of passport
validity measured from entry, from departure, and from an unstated point.

**Deleted anyway.** Nothing recorded *who a claim applied to*, so a general page listing visa-free
nationalities and a nationality-specific page requiring a visa compared as though they contradicted
each other. A false "sources disagree on whether you need a visa" is the most damaging thing this
product could emit.

The generalised lesson, which governs later decisions: **a feature whose wrong answers are alarming
must have a near-zero false-positive rate, or it should not ship.** Errors a user sees must be
near-impossible; errors only the maintainer sees can be noisy.

If revisited: record the population each claim applies to and compare only same-scope claims; leave
the visa decision out entirely, since it has stronger guards already; restrict comparison to
quantitative rules where a wrong flag costs a caveat rather than alarm.

---

## 5. Refuse rather than serve evidence that may be wrong
**2026-08-14 · commit `1c9fec9`**

Originally any failure collapsed the whole run into an opaque 503.

**Decided:** each source resolves to a typed outcome; a plan is `verified` or `partial`; and a
missing *required* source refuses the run **before the model is called**, naming what was missing.
A plausible substitute for a document checklist is worse than no answer.

---

## 4. Cached evidence reports when it was really retrieved
**2026-08-13 · commit `672f0e9`**

When serving from cache, `retrieved_at` is the original fetch time, never now.

Stamping the current time would replace a *visible* staleness problem — a plan showing an old date —
with an invisible one. The same reasoning drives the stale ceiling: past it, a source is refused
rather than served, because "no answer" beats "confidently out-of-date answer".

---

## 3. Reviewable policy in git; secrets in `.env`
**2026-08-13 · commit `672f0e9`**

`.env` had collected three different kinds of setting: secrets, behavioural policy, and machine
tuning. Only the first belongs in an untracked file.

**Decided:** `source_mode`, `extraction_mode`, the cache TTL and the stale ceiling moved to a
committed `config/runtime.yaml`. They decide whether government sites are contacted, whether a paid
model runs, and when stale guidance is refused — all of which deserve code review and a diff.

A concrete cost had already been paid: inspecting which mode was active meant printing the file, and
the API key went with it.

---

## 2. Trust the domain, never the prose
**2026-08-13 · commit `1c9fec9`**

The founding rule. Officialness is decided by who controls the domain, checked at configuration
load, after every redirect, and after every forward. Page content is never a factor, because a
convincing page is exactly what an attacker or an SEO-optimised agency produces.

Consequence worth stating: an appointed provider such as VFS **cannot** pass domain trust, and is
authorised only by an official page naming it.

---

## 1. Separate retrieval from extraction behind a protocol
**2026-08-12 · commit `28a6e30`**

`SourceFetcher` and `VisaPlanExtractor` are protocols, so fixtures and live retrieval are
interchangeable and the offline path remains a deterministic regression baseline.

This paid off repeatedly: live retrieval, PDF support and discovery's shortlist fetching were all
added without touching the extractor. Discovery reuses `LiveSourceFetcher` wholesale rather than
reimplementing trust checks.
