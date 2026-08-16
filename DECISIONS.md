# Decisions

Why the project is shaped the way it is, including what was tried and rejected. The reasoning is
recorded because it is the part that cannot be recovered from the code later — a deleted feature
leaves no trace, and a rule with an obvious-looking alternative invites someone to "simplify" it
back into a bug.

Newest first. Add an entry when a decision is made, not afterwards.

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
