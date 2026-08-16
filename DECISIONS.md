# Decisions

Why the project is shaped the way it is, including what was tried and rejected. The reasoning is
recorded because it is the part that cannot be recovered from the code later — a deleted feature
leaves no trace, and a rule with an obvious-looking alternative invites someone to "simplify" it
back into a bug.

Newest first. Add an entry when a decision is made, not afterwards.

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
