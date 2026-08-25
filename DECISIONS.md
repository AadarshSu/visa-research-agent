# Decisions

Why the project is shaped the way it is, including what was tried and rejected. The reasoning is
recorded because it is the part that cannot be recovered from the code later — a deleted feature
leaves no trace, and a rule with an obvious-looking alternative invites someone to "simplify" it
back into a bug.

Newest first. Add an entry when a decision is made, not afterwards.

---

## Index

**If you read only a handful, read these.** They are the rules a plausible-looking change breaks, and
each is restated in [CLAUDE.md](CLAUDE.md): **2** (trust the domain, never the prose), **5** (refusing
is a correct output), **18** + **35** + **41** (never work around a block; honest client, not anonymous
client), **12** (never disable TLS verification), **27** + **32** (what a block may hand over),
**60** (a questionnaire is an answer, not a blockade), **44** (a page may be stored, an answer may not).

### Trust: who may be believed at all
| | |
| --- | --- |
| [2](#2-trust-the-domain-never-the-prose) | Officialness is a property of the domain, never of how a page reads |
| [10](#10-a-destinations-own-government-outranks-other-countries-pages-about-it) | A destination's own government outranks other countries' pages about it |
| [11](#11-search-may-generate-candidates-it-may-never-widen-trust) | Search generates candidates; it never widens trust |
| [12](#12-complete-certificate-chains-never-disable-verification) | Complete certificate chains; never disable TLS verification |
| [19](#19-the-human-approval-gate-becomes-a-rule-not-an-absence) | The human approval gate becomes a rule, not an absence |
| [21](#21-any-country-is-a-destination-and-a-country-name-stops-matching-inside-a-word) | Any country is a destination; a country name stops matching inside a word |
| [22](#22-a-large-government-passes-the-same-rule-with-far-more-domains-so-how-many-is-capped) | How many domains a government may contribute is capped |
| [33](#33-the-governmental-half-of-the-trust-rule-fails-closed-for-a-fifth-of-the-world) | **Measured:** the governmental half fails closed for a fifth of the world |
| [34](#34-who-to-believe-becomes-committed-data-only-which-page-is-decided-live) | Who to believe becomes committed data; only which page is decided live |
| [38](#38-the-trusted-domain-registry-is-generated-offline-and-committed-and-reviewing-it-found-what-running-it-could-not) | The trusted-domain registry is generated offline and committed |
| [39](#39-a-person-may-override-the-trust-rule-in-committed-data-and-doing-it-showed-the-rule-was-not-the-only-thing-wrong) | A person may override the trust rule, in committed data |
| [65](#65-three-missing-markers-and-the-second-list-nobody-remembered-was-there) | **Three missing markers** — 19 of 51 unreachable → 16, and a second list that had to move with it |
| [68](#68-a-batch-is-done-in-three-stages-and-accuracy-is-measured-outside-the-codebase) | **A batch is done in three stages** — reachable, resolves, fast. Accuracy is verified outside the codebase |
| [67](#67-the-registry-grows-in-batches-and-a-domain-can-be-confirmed-by-asking-wikidata-about-the-domain) | **Batch 1: EU/EEA, 41 → 53 researchable.** Confirm a domain by asking Wikidata about the domain |
| [66](#66-what-could-confirm-a-government-that-marks-no-hostname-tls-half-the-time-and-not-automatically) | **TLS names the authority for 9 of 16; RDAP for 1 and it is dropped.** The human job shrinks to seven |

### Refusal, blocks, and how we behave as a client
| | |
| --- | --- |
| [5](#5-refuse-rather-than-serve-evidence-that-may-be-wrong) | Refuse rather than serve evidence that may be wrong |
| [18](#18-a-block-is-not-a-fact-about-the-guidance-never-work-around-one) | A block is not a fact about the guidance; never work around one |
| [24](#24-a-fetch-place-is-not-spent-on-a-page-already-proved-unreadable) | A fetch place is not spent on a page already proved unreadable |
| [25](#25-the-politeness-delay-is-owed-to-a-host-not-to-the-crawl) | The politeness delay is owed to a host, not to the crawl |
| [27](#27-a-block-becomes-a-next-step-name-the-page-hand-over-the-link-decide-nothing) | A block becomes a next step: name the page, decide nothing |
| [32](#32-a-block-hands-over-a-link-only-when-it-plausibly-held-the-answer) | A block hands over a link only when it plausibly held the answer |
| [35](#35-the-posture-is-honest-client-not-anonymous-client--and-the-bar-that-decides-whether-this-is-a-product) | **Honest client, not anonymous client** — and the bar that decided the product question |
| [36](#36-robotstxt-is-read-and-obeyed-and-a-page-skipped-for-it-is-its-own-outcome) | `robots.txt` is read and obeyed; a page skipped for it is its own outcome |
| [41](#41-a-challenge-is-not-a-refusal-answer-it-as-an-honest-browser-and-honour-every-robotstxt) | A challenge is not a refusal — answer it as an honest browser |
| [49](#49-a-refusal-met-while-reading-the-shortlist-was-never-reported-at-all) | A refusal met while reading the shortlist must still be reported |
| [54](#54-one-encrypted-pdf-took-a-whole-corridor-down-and-no-narrower-except-could-have-caught-it) | One encrypted PDF took a whole corridor down |
| [57](#57-a-block-is-judged-not-keyword-matched--the-one-place-the-scorer-was-doing-semantics) | A block is judged, not keyword-matched |

### The questionnaire outcome
| | |
| --- | --- |
| [26](#26-france-refuses-because-france-does-not-publish-the-answer-anywhere-readable) | France: the answer exists only inside an interactive tool |
| [59](#59-the-third-outcome-the-answer-is-behind-a-tool-so-hand-over-the-tool) | The third outcome — hand over the tool. Declines URL-construction, with measurements |
| [60](#60-a-questionnaire-is-an-answer-for-every-role--not-a-blockade-in-front-of-one) | **A questionnaire is an answer, for every role** — widens 59 |

### What a plan may say to a traveller
| | |
| --- | --- |
| [6](#6-structured-conflict-detection-built-then-deliberately-deleted) | Conflict detection: built, then deliberately deleted |
| [8](#8-wrong-audience-is-a-veto-not-a-penalty) | Wrong audience is a veto, not a penalty |
| [14](#14-a-missing-document-checklist-stops-refusing-the-corridor) | A missing document checklist stops refusing the corridor |
| [23](#23-entry-14s-decision-never-reached-a-traveller-because-extraction-refused-first) | Entry 14's decision never reached a traveller |
| [28](#28-four-fixes-from-reading-the-interface-as-a-traveller) | Four fixes from reading the interface as a traveller |
| [30](#30-conflicts-is-deleted-by-entry-6s-own-rule) | `conflicts` is deleted, by entry 6's own rule |
| [31](#31-a-failed-adjudication-refuses-rather-than-falling-back-to-the-heuristic) | A failed adjudication refuses rather than falling back — **amends 16** |

### Finding the right page: ranking, recall, judgement
| | |
| --- | --- |
| [9](#9-a-page-can-fill-several-roles) | A page can fill several roles |
| [15](#15-brazil-the-out-of-sample-test-discovery-ranks-the-wrong-page-confidently) | Brazil: the heuristic ranks the wrong page, confidently |
| [16](#16-judgement-decides-the-last-step-heuristics-decide-everything-before-it) | Judgement decides the last step; heuristics everything before it |
| [17](#17-france-and-china-the-decider-refuses-well-and-the-wall-is-now-access-not-ranking) | France and China: the wall is access, not ranking |
| [40](#40-the-shortlist-is-a-recall-budget-and-ten-places-made-the-heuristic-the-real-decider) | The shortlist is a recall budget, not a ranking |
| [42](#42-the-excerpt-is-the-second-recall-gate-and-a-flat-6000-made-truncation-the-decider) | The excerpt is the second recall gate |
| [43](#43-write-down-what-a-corridor-considered-because-ranked-out-and-never-found-had-looked-identical) | Write down what a corridor considered |
| [50](#50-the-routing-index-removes-the-wrong-cost-it-is-wrong_country-not-scoring) | The routing index removed the wrong cost |
| [52](#52-entry-47s-pin-only-half-existed-the-truncation-dropped-it) | Entry 47's pin only half existed |
| [56](#56-the-vocabulary-asked-the-question-and-could-not-recognise-the-answer) | The vocabulary could not recognise the answer |
| [61](#61-the-united-kingdoms-answer-was-five-deep-in-a-list-that-reserved-three) | **Five reserved places per role** — the United Kingdom went 0/8 → 4/4 |
| [62](#62-the-nationality-bonus-is-left-alone--four-fixes-four-disproofs-and-a-cost-of-027-places) | The nationality bonus is left alone — four fixes, four disproofs |

### The stores: corpus, corridors, freshness
| | |
| --- | --- |
| [4](#4-cached-evidence-reports-when-it-was-really-retrieved) | Cached evidence reports when it was **really** retrieved |
| [44](#44-a-countrys-page-corpus-is-persisted-and-search-leaves-the-request-path) | **A page may be stored; an answer may not.** The corpus is the unit |
| [45](#45-the-corridor-command-reaches-the-registry-and-the-test-suite-stops-being-allowed-on-the-network) | The test suite stops being allowed on the network |
| [46](#46-the-corpus-is-built-and-it-is-not-yet-a-superset-of-what-a-corridor-finds) | The corpus is built, and is not yet a superset |
| [47](#47-the-candidate-set-ratchets-corpus--live-pinned-by-what-already-worked-fed-by-write-back) | The candidate set ratchets: corpus ∪ live, pinned, written back |
| [48](#48-the-crawl-was-rediscovering-a-map-the-corpus-already-had-the-corpus-becomes-a-routing-index) | The corpus becomes a routing index |
| [51](#51-the-crawl-leaves-the-request-path-for-a-country-whose-corpus-already-out-covers-it) | The crawl leaves the request path |
| [53](#53-measured-live-the-crawls-336s-is-gone-and-removing-it-exposed-a-defect-only-a-run-could-find) | Measured live: the crawl's 33.6s is gone |
| [55](#55-six-corridors-through-the-corpus-25-faster-and-it-breaks-the-blocked-authority-exception) | Six corridors through the corpus: faster, and it broke the block exception |

### Shape of the system
| | |
| --- | --- |
| [1](#1-separate-retrieval-from-extraction-behind-a-protocol) | Separate retrieval from extraction behind a protocol |
| [3](#3-reviewable-policy-in-git-secrets-in-env) | Reviewable policy in git; secrets in `.env` |
| [7](#7-discovery-is-an-offline-command-not-part-of-a-request) | Discovery is an offline command, not part of a request |
| [13](#13-render-client-side-pages-on-demand-only-trusting-nothing-new) | Render client-side pages, on demand only |
| [20](#20-the-traveller-becomes-input-countries-become-codes) | The traveller becomes input; countries become codes |
| [29](#29-langgraph-is-not-adopted-and-the-placeholder-goes-with-it) | **LangGraph is declined, not deferred** |
| [37](#37-a-per-run-allowance-may-not-be-counted-on-an-object-that-outlives-the-run) | A per-run allowance may not live on an object that outlives the run |

### Whether this is a product
| | |
| --- | --- |
| [58](#58-the-twenty-corridor-measurement-it-passes-the-bar-and-the-bar-was-nearly-the-wrong-question) | **The twenty-corridor measurement** — passes, marginally, against a bar set in advance |
| [64](#64-the-control-arm-built-run-on-three-corridors-and-deleted) | **The control arm, run then deleted** — 0 of 8 cited hosts passed the trust rule, and one should have |
| [63](#63-why-a-traveller-goes-unanswered-becomes-a-count-and-the-first-count-contradicts-the-assumption) | **Why a traveller goes unanswered becomes a count** — and the posture cost 0 of 15 lost pages |

---

## 68. A batch is done in three stages, and accuracy is measured outside the codebase
**2026-08-25 · direction, set by the project owner. Supersedes entry 67's "done"**

Entry 67 called batch 1 done. It was not, and the correction changes what every future batch costs.

**What entry 67 achieved is *reachability*:** fourteen countries have registry rows, twelve carry a
confirmed domain, and the trust rule accepts them. That is the first of three stages and the cheapest —
and counting the rest of the registry the same way showed the gap was never about those fourteen.

### What "done" means for a batch, from now on

**Batch 1 is every reachable country — all 53 — not the fourteen entry 67 added.** Those fourteen were
added to *catch up* to the ones already in the registry, and the ones already there are in no better
state: **41 of the 53 have never had a single corridor run against them.** A registry row was never
evidence that a country works.

| | stage | batch 1 today |
| --- | --- | --- |
| 1 | **Reachable** — a confirmed authority domain | **53 of 198** |
| 2 | **Resolves** — a representative nationality set yields a visa decision, or refuses for a named reason that is *correct* | **12 of 53.** 41 have never been run, which is not the same as failing |
| 3 | **Fast** — served from a stored corpus rather than a live crawl | **10 of 53** |

Fully done: AE, CA, DE, FR, GB, JP, NL, SE, SG, US — ten. Austria and Norway resolve but crawl.
Everything else is a row nobody has tried: AU, BE, BG, BR, CH, CN, CY, CZ, DK, EE, EG, ES, FI, GR, HR,
HU, ID, IE, IN, IT, KR, LT, LU, LV, MA, MT, MX, MY, NZ, PH, PL, PT, RO, SA, SI, SK, TH, TR, UY, VN, ZA.

**No more countries are added until batch 1 clears all three.** Adding breadth on top of untested depth
is how a registry of 198 rows becomes 198 unverified claims, and the cost of finding that out grows
with every batch. That failure had already happened quietly — 41 rows deep — before anyone counted.

### Accuracy is deliberately not a stage, and not the codebase's job

Whether a visa decision is **correct** is verified by the project owner, outside this repository. That
is a real division of labour rather than an omission, and it is recorded here so that no future session
builds a truth set, a correctness grader or an accuracy metric on the assumption that the gap is an
oversight. **Do not build one without asking.**

**What follows from it, and must not be lost:** `ResolvedCorridor.is_usable` and
`RefusalCause.resolved` mean *an official page stated a decision*, never *the decision is right*. So
every figure this project quotes about itself — entry 58's 75% included — measures whether it
**answered**, not whether the answer was good. That is a caveat on how the numbers are read, not a
defect to fix here. Known problem 26.

The parts of stage 2 that *are* the codebase's job stay: a corridor must resolve or refuse, and when it
refuses the named reason has to be true of what was seen — which is the discipline entries 33, 36 and
63 already enforce.

### Stage 3 is latency, and it is already understood

**43 of the 53 have no corpus**, so they crawl in the request path. Entry 55 measured corpus-routing at
**2.1×–5.2× faster** — Singapore 56.1s → 10.8s. So stage 3 is `visa-discover corpus` per country, and it
is by far the expensive stage: **~1,792 searches and up to 51,600 page fetches** for the 43, against 4
searches for a registry row.

**Deliberately after stage 2**, and the cost is why it matters. A corpus built for a country whose
corridors do not yet resolve is a corpus of unknown value, and known problem 24 records how badly
coverage varies — Japan's holds 1 of its 6 role pages. Build it where the corridors are known to work,
so a thin one is visible as a regression rather than baked in as a baseline. Running stage 2 first also
tells us which countries are worth 42 searches each and which are refusing for a reason a corpus cannot
fix.

### What this supersedes

Entry 67's closing line and TODO item 2's batch note both read as though batch 1 were finished. They
are corrected rather than deleted: what entry 67 records about *method* — confirming a domain by asking
Wikidata about the domain — is unaffected and remains how a batch's refusals are resolved.

---

## 67. The registry grows in batches, and a domain can be confirmed by asking Wikidata about the domain
**2026-08-25 · implemented, reviewed and confirmed live. TODO item 2, first batch**

The sweep is done **in batches** rather than all at once, so each one can be reviewed before the next is
paid for. Batch 1 completes the EU and EEA: BG, CY, EE, FI, IS, LI, LT, LU, LV, MT, NO, RO, SI, SK.

### What the rule alone did: 6 of 14

**56 searches, no `402`** — the rate limiter recorded under *Smaller things* does not bite at this size,
which is itself worth knowing before the 143 that remain.

Six confirmed automatically — CY, EE, LV, MT, RO, SI — and every one of them uses a `gov.xx`
convention. Eight refused: BG, FI, IS, LI, LT, LU, NO, SK. That split is entry 66's finding reproduced
on new countries: where a government runs a `gov` namespace the rule works, and where it does not there
is nothing for a pattern to find.

### The method that recovered 6 of the 8, and it is the reusable part

Entry 66 measured TLS certificates at 9 of 16. **On this batch TLS managed 2 of 8**, and one of those
two was Luxembourg's `gouvernement.lu` naming *Centre des technologies de l'État* — the Hungary case
again, an infrastructure operator rather than an authority. Only Finland's `migri.fi` →
`Maahanmuuttovirasto` was a clean hit.

**The samples are not the same question, and the difference matters.** Entry 66 probed each country's
*known-correct* visa-guidance domain, taken from a hand-written table. This probes *whatever search
found*, which is the harder and more realistic case — and the honest reading is that TLS is weaker in
production than entry 66's number suggests.

What worked instead was Wikidata, **queried from the domain rather than from a name**:

```
GET /w/api.php?action=query&list=search&srsearch=haswbstatement:P856=https://udi.no/
   -> Q12008658  Norwegian Directorate of Immigration   P17 = Norway
```

That is an exact statement match — *this entity's official website is this domain* — so no step guesses
an organisation's name and then looks for it. The country is then checked against `P17`. Both halves
were verified for all seven promoted domains.

| | domain | Wikidata | |
| --- | --- | --- | --- |
| BG | `mfa.bg` | Q1813345 | Ministry of Foreign Affairs of Bulgaria |
| FI | `migri.fi` | Q11880302 | Finnish Immigration Service |
| FI | `um.fi` | Q2639539 | Ministry of Foreign Affairs of Finland |
| LT | `urm.lt` | Q1548931 | Ministry of Foreign Affairs of Lithuania |
| LU | `gouvernement.lu` | Q21479996 | Government of Luxembourg |
| NO | `udi.no` | Q12008658 | Norwegian Directorate of Immigration |
| SK | `mzv.sk` | Q3499939 | Ministry of Foreign and European Affairs of Slovakia |

**Wikidata was already this file's evidence standard** — fifteen existing rows cite "P856/P17, checked
2026-08-18" from a lookup done by hand. What is new is doing it from the domain, which removes the
step where a person's own knowledge proposes the answer. The QID is now recorded too, so the claim is
checkable rather than merely cited.

**Iceland and Liechtenstein stay refused.** `government.is`, `island.is` and `llv.li` have no Wikidata
entity claiming them and DV certificates naming nobody. That is the right outcome: nothing was found,
so nothing is asserted.

**53 of 198 researchable, from 41.** The batch cost 56 searches, ~25 Wikidata lookups and one review.

> **This is *reachability*, not a working batch — see entry 68, which supersedes the word "done"
> here.** Twelve of the fourteen have a confirmed domain; one of the twelve has ever been run, and
> none has a corpus. What this entry records about *method* is unaffected.

### Three things the batch surfaced that are not about this batch

- **`iom.sk` was proposed for Slovakia and correctly declined.** The International Organization for
  Migration is a UN agency, not Slovakia's government, and it ranks for Slovak migration queries. A
  live example of the rule earning its keep, and of why "looks like an authority" may never be the test.
- **Two of the six automatic confirmations may be confirmed on the wrong domain.** Estonia was accepted
  on `e-resident.gov.ee` — the e-Residency programme, not visa guidance — while its foreign ministry
  `vm.ee` was declined; Romania on `euraxess.gov.ro`, a researcher-mobility portal, alongside the more
  plausible `mai.gov.ro`, while `mae.ro` was declined. This is known problem 2's *quieter* failure:
  bootstrap succeeds against a trusted set that need not contain the answer, and nothing reports it.
  Both will resolve or refuse on their own merits when a corridor runs; they are the two to watch.
- **`finlandvisa.fi` was proposed and matched nothing** — no Wikidata entity, no certificate
  organisation. The one candidate in the batch whose name reads commercial is also the one both
  mechanisms declined to vouch for.

### Verified live

`norway/IN/IN/tourism` resolves on the new reviewed row: visa decision confirmed, fees, processing
times and general entry all filled from `udi.no`, and the document checklist correctly handed over as
UDI's own checklist tool, which asks for the country of application rather than stating the answer
(entry 60). `forms.udi.no` was skipped for `robots.txt` and reported as skipped. First try, no
adjustment.

---

## 66. What could confirm a government that marks no hostname: TLS, half the time, and not automatically
**2026-08-25 · measured. TODO item 2's gating measurement; RDAP is dropped**

Item 2 named four mechanisms that might supply officialness without per-country judgement, and said to
measure before building because the answer decides whether the production goal survives. Measured
against the sixteen governments whose visa-guidance domain carries no hostname marker.

### The result

| mechanism | covers | of 16 |
| --- | --- | --- |
| **TLS certificate organisation** | CZ, DE, FI, HU, IT, NL, PT, RO, SE | **9** |
| **RDAP registrant** | FI | **1** |
| either | the same nine | **9** |
| **neither** | BE, CL, DK, GR, IE, NO, RU | **7** |

**RDAP is dropped.** It adds nothing — Finland is in both sets — and its failure is worse than item 2
predicted. The prediction was GDPR redaction; the reality is that **13 of the 16 ccTLDs answer no RDAP
at all**, so there is nothing to redact. Of the other three, the Netherlands is `REDACTED FOR PRIVACY`
and **Norway's response names only the registrar** — `Domeneshop AS`, the company that sold the domain,
which says precisely nothing about who owns it. A naive count says 2 of 16; the honest count is 1.

### What TLS actually returns, and why it is not a verdict

Nine certificates name an organisation, and the names are unambiguous:

```
CZ  mvcr.cz              Ministerstvo vnitra
DE  auswaertiges-amt.de  Auswärtiges Amt
FI  migri.fi             Maahanmuuttovirasto
IT  esteri.it            Ministero degli Affari Esteri e Cooperazione Internazionale
NL  ind.nl               Immigratie- en Naturalisatiedienst
PT  vistos.mne.pt        Ministério dos Negócios Estrangeiros
RO  mae.ro               Ministerul Afacerilor Externe
SE  migrationsverket.se  Migrationsverket
HU  kormany.hu           NISZ Zrt.
```

**Eight of the nine name the authority. Hungary names an infrastructure operator** — `NISZ Zrt.` is a
state IT provider, not a ministry — which is nearer an appointed provider than a government, and
exactly the distinction `appointed_providers` exists to keep. So the mechanism yields a **name, not a
verdict**, and turning "Auswärtiges Amt" into "this is Germany's own government" is still a judgement.
One in nine of those judgements has to come out *no*.

The other seven serve DV certificates naming nobody. There is no machine-readable proof to find.

### So the production goal does not survive as stated, and the job it leaves is small

Automating this away entirely was the goal. It is not available: 7 of 16 have nothing to read, and the
9 that do still need a person to say whether the named organisation is the government.

**What changes is the shape of the human work, and it changes a lot.** A reviewer filling `reviewed`
was previously researching a country's domain conventions from nothing. Now, for nine of them, they
read a CA-validated organisation name and confirm it in seconds — and that certificate is exactly the
"something independent of the page" that `CountryAuthorities.reviewed` demands as evidence. The
remaining seven are research, and **seven is a bounded, one-time job**, not the 198-country curation
the production goal exists to avoid.

**Mechanism (1), a government's own published domain list, is not measured here** and is not generically
probeable — there is no predictable location to fetch. It matters most for the seven with nothing, so
the follow-up is bounded to those seven rather than all sixteen.

**One property to state rather than slide past, as item 2 asked:** reading a certificate needs a TLS
handshake to the host *before* trust is decided. That is a connection, not a fetch — no page is
retrieved and nothing is read — but it is not nothing, and a mechanism that contacts a host in order
to decide whether it may be contacted deserves saying out loud.

### A correction inside the measurement itself

The first RDAP pass reported 1 of 16 with Finland showing `HTTP 406`. That was **this probe's own
`Accept` header**, not an absence: with `application/rdap+json`, Finland returns
`Maahanmuuttovirasto AM` as registrant. Three more results were `429` from the bootstrap redirector
rather than real answers. Retrying only the inconclusive ones changed the finding, and the numbers
above are from a clean pass with no inconclusives left. Recorded because "the tool said no" and "the
tool was not asked properly" look identical in a result table, which is the same failure this project
has now recorded several times.

**The probe is not kept.** It is ~60 lines: read `AUTHORITIES` in `tests/test_trust_coverage.py` for
the sixteen domains, `GET https://rdap.org/domain/<domain>` with `Accept: application/rdap+json`
looking for a `registrant` entity's `org`/`fn` and ignoring `registrar` roles, and
`ssl.create_default_context()` + `getpeercert()` reading `subject.organizationName`, falling back to
`www.`. Rebuildable in ten minutes if the question returns.

---

## 65. Three missing markers, and the second list nobody remembered was there
**2026-08-25 · implemented, rebuilt and confirmed live. TODO item 2, the corrections half**

Item 2's "do first, separately" step: add `gv` and `gub` as governmental markers and name `canada.ca`
beside `gc.ca`. These are **corrections inside the rule rather than relaxations of it** — Austria's
ministry is `bmeia.gv.at` and Uruguay's government is `gub.uy`, both the same idea as `gov` spelled the
way their own registry spells it, and Canada's immigration content had moved off the already-named
`gc.ca` to `canada.ca` while the rule stayed put.

**Trust-rule coverage: 19 of 51 unreachable → 16 of 51.** AT, CA and UY. The frozen tripwire in
`tests/test_trust_coverage.py` named exactly those three and nothing else, which is what it is for.

### The hole this would have opened, which neither file could see alone

`trust.SUFFIX_MARKER_LABELS` is a **second** hand-maintained list, and it decides something different:
not "is this a government namespace" but "is it too broad to trust whole". `gv` was missing from it.

So with the marker added and that list untouched, `registrable_domain("bmeia.gv.at")` returned
**`gv.at`** — trusting Austria's foreign ministry would have trusted **every Austrian public body**
under the same namespace. That is precisely what refusing `gov.br` whole exists to prevent,
reintroduced through the back door, and it was invisible from either file: `bootstrap.py` looked
correct, `trust.py` looked correct, and the defect lived in the gap.

The two lists now move together by construction — `GOVERNMENT_NAMESPACE_LABELS` is the source the
namespace patterns are built from, and `tests/test_trust.py` asserts it is a subset of
`SUFFIX_MARKER_LABELS` with an error message saying why. **The containment is one-directional**:
`co`, `com` and `org` belong in the suffix list and are not governmental.

`canada.ca` is the safer shape and is kept separate as `NAMED_GOVERNMENT_DOMAINS`: a single domain a
government holds, like `admin.ch`, where a subdomain can only exist if that government made it.
Reducing `ircc.canada.ca` to `canada.ca` is correct; reducing `bmeia.gv.at` to `gv.at` is not.

**The adversarial probe is now a test.** TODO item 2 recorded it as run by hand on 2026-08-18, which
meant nothing was holding it. Seventeen spoofs — `visa-gov.com`, `gv-at.com`, `mygub.uy`,
`canada.ca.evil.example`, `notcanada.ca` — all rejected, because matching is anchored to a label
boundary at the end.

### The rule changing moved nothing on its own

`visa-discover audit` immediately afterwards: still **39 researchable, Austria still refused.** The
registry is committed data generated under the old rule (entry 38), and a rule change does not reach a
traveller until the rows are rebuilt. Austria's row held only `gv.at` — the bare namespace, which the
fix above now correctly refuses as a suffix — because search had found the namespace and never the
ministry.

`visa-discover registry --only AT,UY --rebuild`, 8 searches:

| | before | after |
| --- | --- | --- |
| AT | `unconfirmable: [gv.at]`, nothing usable | `bmeia.gv.at`, `oesterreich.gv.at`, `migration.gv.at`, `wien.gv.at` |
| UY | no row at all | `www.gub.uy` |

**39 → 41 researchable, and the "row, no confirmable domain" bucket is now empty.**

### A false statement found by reading the command's own output

`run_registry` printed `41 countries written; 37 have a confirmed domain, 4 are refused`, and the four
were **Belgium, Germany, Denmark and Sweden** — every one of them researchable, on a `reviewed`
domain. It counted `row.trusted` and ignored `row.reviewed`, so the one command that *writes* reviewed
rows reported them as failures, for the governments the reviewed mechanism exists for. Germany had
confirmed the visa decision on 8 of 8 corridors (entry 58) while this line called it refused. Now
counted from `row.domains`, the same property the resolver reads.

### Austria live, and it qualifies entry 63

`austria/IN/IN/tourism` now reaches its own government and refuses **for a different and far more
honest reason**: `www.bmeia.gv.at` and `www.wien.gv.at` publish a `robots.txt` that does not permit
this client, and the remaining domains returned too little readable text. The corridor correctly does
not resolve — a `Disallow` may never resolve one (entry 36).

**This is the first measured case where the posture actually costs a corridor.** Entry 63 reported 0 of
15 unreadable pages `blocked`, and that literal statement still holds — there are still zero. But its
implication, that the honest-client posture was costing nothing measurable, does not survive Austria:
**23 pages `disallowed` across the run set, all Austrian, and they refuse the corridor outright.**
Obeying `robots.txt` is the same posture, and `POSTURE_COST` already marks `disallowed` as a cost of
it. The earlier reading was true of the two corridors it was drawn from and too broad as a conclusion.

**A limitation this exposes in entry 63's taxonomy:** Austria buckets as `decision_not_found` — "no,
recall or scoring" — when the decision was not found *because* the pages were disallowed. The cause
describes the corridor's outcome and the `disallowed` count sits in a separate section, so a reader
has to join them by hand. Not fixed here; recorded so the next person does not read that bucket as
purely a recall problem.

---

## 64. The control arm: built, run on three corridors, and deleted
**2026-08-25 · run, then removed. The code is gone; the finding is why item 2 is first**

Entry 63 made the denominator honest. This was the other half — `visa-discover baseline`, a
deliberately naive arm with **no** `is_own_government`, no corpus, no shortlist, no adjudication: one
plainly worded query, top 8 results, one model call. It existed to answer a question the project had
never been able to answer about itself, and **it is deleted now that it has.** Same shape as entry 30:
a thing built, used, and removed rather than carried.

### What it was for

Entry 35 committed a bar in advance and entry 58 measured against it — 75% decision, 50% checklist —
with **no comparison arm**. So "we are losing too much coverage for this rigor" and "the rigor is worth
it" were equally unfalsifiable, and every argument about relaxing a rule was settled by whoever was
talking.

### Three corridors, both arms, 2026-08-24

| corridor | this project | the naive arm |
| --- | --- | --- |
| `germany/IN/IN` | resolved; decision confirmed; **0 documents** | **5.3s**; decision + **18 documents** |
| `united-kingdom/IN/IN` | resolved; official checker handed over; checklist, route, times, fees | **3.5s**; decision + 8 documents |
| `kenya/IN/IN` | **refused** — no registry row | **5.9s**; decision + 3 documents |

Against entry 58's corridor median of **27.4s**. So the naive arm was roughly **5× faster, answered a
country this project refuses outright, and produced a checklist for Germany where this project
produces none.** That is the case for relaxing, and it is real.

### What it was built on: 0 of 8

**Not one cited host passed the trust rule.** Entry 19's three anecdotes — `axa-schengen.com`,
`usembassy.gov`, VFS — became eight of eight:

- **Germany's 18-item checklist** rested partly on a **travel insurer** and **an airline**.
- **The United Kingdom returned no `gov.uk` result in its top 8 at all.** Not ranked low — absent.
  Visa agencies, two Indian airlines and an insurer, for the destination whose `check-uk-visa` this
  project reads successfully and hands over by name.
- **Kenya contradicted itself in the field that matters most:** `visa_required: false` beside
  `visa_name: "Electronic Travel Authorization (eTA)"` in one answer. A traveller reads the first and
  boards without the second. No external ground truth is needed — the answer disagrees with itself,
  in the field `CLAUDE.md` calls the most damaging thing this program can get wrong.

### And the rule was wrong about one of them, which is the finding that survived

`india.diplo.de` **is** Germany's own diplomatic mission, giving guidance to exactly that traveller,
and the trust rule declines it because `diplo.de` carries no governmental marker. So the honest
reading of the eight is **seven commercial pages the rule correctly excluded, and one real authority
it wrongly excluded** — known problem 2 with a measured cost rather than a description. The naive arm
found it by having no rule at all.

### The conclusion, and it is what reordered the queue

**The rigor is cheap and the backlog is expensive, and it had been easy to mistake the second for the
first.** Of 159 countries refused before a page is fetched, 158 are a registry job nobody has run
(entry 63); of 15 pages lost mid-corridor, 0 were blocked. The posture that reads most restrictive
cost nothing measurable. So **item 2 moved to first** and nothing was relaxed.

### Why the code is not kept

Three corridors, one nationality, one purpose, one engine, one day: a pointer, not a rate. Keeping the
arm would have meant maintaining a second, trust-free retrieval path — guarded by tests, carried
through every refactor — to re-answer a question already answered well enough to act on. **What would
have justified keeping it** is the dimension it never graded: correctness against a truth set. If the
naive arm is right ~90% of the time the question becomes "accurate but unattributable versus accurate
and attributable", which is harder than the one above. Nobody built that truth set, and this entry is
the record so the arm can be rebuilt deliberately if that question is ever worth reopening.

**What it left behind:** nothing in the codebase. `visa-discover audit` (entry 63) is separate and
stays — it is a diagnostic over this project's own runs, with no second pipeline behind it.

---

## 63. Why a traveller goes unanswered becomes a count, and the first count contradicts the assumption
**2026-08-24 · implemented and confirmed live**

The project could say how often it succeeded — 75% of corridors confirmed a visa decision, 50% yielded
a checklist (entry 58) — and could not say, in any countable form, **why the rest did not.** Those
failures have completely different fixes and opposite bearing on the trust rules: a country with no row
in `authority_domains.yaml` is unfinished data, an authority answering `403` is a permanent cost of
entry 18's posture, and a page nobody could rank is recall. Reported as one number they argue for
whatever the reader already believed, which is how "the rigor is costing us too much" and "the rigor is
worth it" had both stayed unfalsifiable.

`visa-discover audit` counts it, in two halves that are deliberately **not** added together.

### The two halves, and why merging them would lie

**Reachability is decided before a resolver is ever built**, so a country refused for want of a registry
row leaves no recall log at all. It is computed from committed data instead — exact, no runs, no
network, read through the same `CountryAuthorities.domains` the request path reads so the two cannot
drift:

```
researchable                   39   19.7%  —
row, no confirmable domain      1    0.5%  partly — the trust rule's real cost
no registry row at all        158   79.8%  no — unfinished data
```

**159 of 198 are refused before a page is fetched, and 158 of those are a job nobody has run.** Sharing
a denominator with the recall causes would have buried that inside a percentage of corridors that
mostly succeed.

### The conflation this was built to end

`RecallRecord.outcome` is prose, and two outcomes write **the same sentence**: a corridor refused
because nothing stated the visa decision, and a corridor resolved by handing over the questionnaire
that states it, both record `"resolved, with no visa_decision"`. One refuses the traveller; the other
hands them the thing they can act on. Every United Kingdom run in the twenty-corridor logs is the
second wearing the first's words.

So `RefusalCause` is a value, derived from the result by `ResolvedCorridor.outcome_cause` rather than
set twice, and confirmed live on the two corridors that differ:

| run | `outcome` | `cause` |
| --- | --- | --- |
| `germany/IN/IN` | `resolved, with no document_checklist` | `resolved` |
| `united-kingdom/IN/IN` | `resolved, with no visa_decision` | **`resolved_decision_tool`** |

**Old logs are reported as unrecorded, never inferred.** All 27 predate the field, and they cannot be
repaired by reading `outcome` — nothing else in the record separates the two rows above. Guessing from
the sentence is the habit behind two of the corrections table's thirteen rows, and a `cause` recovered
that way would be a number nobody could check.

### A defect only running it could find

`RecallRecord.unreadable` was filled from **the crawl's failures alone.** That was complete while the
crawl ran; the crawl left the request path (entry 51) and the field silently went empty. All 27 logs
record nothing unreadable — on runs whose own `ResolvedCorridor` named three authorities that had
refused us. An audit over them would have reported the posture costing zero pages, by reading a field
that had stopped being filled. The shortlist fetch is now recorded too, with `unreadable_outcomes`
keeping the **typed** `FailureOutcome` beside the readable detail, because deciding a `Disallow` from a
`403` by matching words in a message is what entry 36 forbids.

This is the fourth time a documented claim survived only until something ran, and the second in this
file where the thing that ran was written to measure something else.

### What the first two corridors already say, and it is not what known problem 11 assumed

Fifteen pages could not be read across `germany/IN/IN` and `united-kingdom/IN/IN`. **Not one of them was
`blocked`:**

```
unusable       13   www.auswaertiges-amt.de (7), visa-fees.homeoffice.gov.uk (6)
unreachable     2   portal.immigrationadviceauthority.gov.uk, visa-processingtimes.homeoffice.gov.uk
```

Every loss is a page that answered and held too little readable text to trust, a dead hostname, or a
certificate chain that would not verify. **The refusal posture cost nothing in either run.** That is two
corridors and must not be quoted as a rate, but it points where entry 58 could not: Germany's 0/8
checklists sat under known problem 8 as *"publishes none, or we failed to find it"*, and there is now a
third answer on the table — **seven pages on the foreign ministry's own domain were fetched and held no
readable text.** That is a rendering question, not a recall one.

### What this deliberately does not do

It does not compare anything. The naive arm — top search results, no domain trust, one model call —
still does not exist, so the *rigor tax* is still unquantified; this only makes the denominator
honest enough for that comparison to mean something. Nothing here loosens a rule, and the exit code
reports unrecorded runs as work outstanding rather than as failures.

---

## 62. The nationality bonus is left alone — four fixes, four disproofs, and a cost of 0.27 places
**2026-08-24 · measured; **no code change**. Closes TODO item 26**

Item 26 said the scorer "rewards a page for naming a country, not for being about one", and pointed at
`gov.uk/india-young-professionals-scheme-visa` outranking `gov.uk/check-uk-visa` for a tourist. Four
ways to fix that were measured. All four are wrong, and the item is closed without touching the
scorer.

### The premise was wrong

`_describes_country` is already token-based, not a substring test: it matches a whole path segment, a
hyphen-separated token inside one, or a word in the anchor. The ballot page matches on `india` as a
token of `india-young-professionals-scheme-visa` and by the word "India" in its title — so it is
**genuinely about India**. What it is not about is a *tourist visa*. That is a question about the
page's subject, not about how its country was matched.

### Four candidate fixes, and what disproved each

| fix | disproved by |
| --- | --- |
| require the country as its own path segment | the ballot page also matches on the word "India" in its title, so the segment test never fires |
| **context may not exceed role evidence** | `gov.uk/standard-visitor/apply-standard-visitor-visa` fills the checklist **and** the route for every United Kingdom corridor on **0.0 vocabulary and 36 points of pure context**. Context standing in for evidence is deliberate and load-bearing — it is what the purpose-label branch exists to do (Japan's checklist is reached by a link saying only "Tourism") |
| **withhold the corridor bonus when `visa_decision` rests only on the `mentions-visa` floor** | implemented, and the test suite caught it: a per-nationality decision page with a terse URL — the fixture `…/visa/detail/india.html`, labelled "India" — is *also* floor-only, so the rule cannot tell the answer from the noise. Reverted |
| add the scheme names to `off_scope` | vocabulary work for a meaning question, which is the shape entries 56 and 57 reject; and it does not generalise past the schemes someone thought of |

The third is worth dwelling on, because it looked right. The measurement that motivated it is real —
the ballot page carries **6.0** of role evidence, the bare floor, and context adds **+38**; the checker
carries **32.4** and context takes it *down* to 30.4. But "a floor is not evidence" and "a terse
per-nationality page is the answer" are the same shape to the scorer, and only reading the page tells
them apart.

### And the cost is 0.27 shortlist places per corridor

Measured across 22 corridors whose candidates could be rescored faithfully from the corpus: pages
whose `visa_decision` rests on the floor **and** which took a shortlist place on the nationality bonus
average **0.27 of 35 places**. For the corridor that motivated the item it is 2 of 35, both of them
the same ballot scheme under two paths.

That is a lower bound — it counts only corpus-sourced candidates, and search-sourced ones are not
reproducible offline — but it is the right order of magnitude, and it is under one percent. **After
entry 61 the residual cost of this defect is a fetch, not a wrong answer:** the ballot page takes a
place, the adjudicator reads it, and does not choose it. Precision at the shortlist buys fetches;
correctness is the adjudicator's job, which is exactly where entries 56 and 57 put meaning questions.

### The adjacent thing that is real, and also not worth shipping

While measuring, 5.9% of shortlist places (54 of 910 over 26 corridors, up to **6 of 35** for Germany,
whose corpus is the thinnest) turned out to be **query-string duplicates of a page already in the
shortlist**. Two dedup rules were measured and both are unsafe:

- collapsing every query string mis-merges real pages — `j1visa.state.gov/?page_id=152` is a page, not
  a decoration of the site root, which is why `canonical_key` already refuses to do this;
- dropping a decorated URL only when the bare one is also a candidate hits the same case.

Restricted to parameters that provably change presentation and not content — GOV.UK's
`step-by-step-nav` and `utm_*` — it frees **0.8%**, 0.3 places per corridor. Not worth the rule. Noted
here so the 5.9% figure is not rediscovered and acted on without the two counter-examples.

### The method note

The measurements above rest on rescoring recorded corridors, and the first attempt at that was not
faithful: rebuilding a `PageLink` from the recall log's `title` reproduces only **70%** of recorded
scores, because the log stores a title where the scorer saw link text and a heading. Joining against
the country's **corpus**, which stores `link_text`, `heading` and `depth` as the crawl found them,
reproduces **99%** (799 of 804). Any future scoring measurement should join the corpus, not the recall
log.

---

## 61. The United Kingdom's answer was five deep in a list that reserved three
**2026-08-24 · measured, then implemented, then measured live. Closes TODO item 25**

Entries 59 and 60 gave a corridor the words to say *"an official tool answers this"*, and then could
not say it for half the United Kingdom, because the tool never reached the twenty-five pages the model
is shown. This is that gate.

### What the scorer actually does, measured with `score_link` rather than read

```
the checker      visa_decision= 30.4   text:check if you need+26.4, mentions-visa+6, shallow+8, depth1-10
ballot scheme    visa_decision= 44.0   mentions-visa+6, nationality:IN+40,          shallow+8, depth1-10
```

`nationality:+40` is the scorer's largest single term, and `gov.uk/india-young-professionals-scheme-visa`
earns all of it for a substring of its path — a ballot for under-35s, nothing to do with a tourist
visa. **The checker can never earn it**, because a page that asks the reader their nationality names
none. It scores **exactly 30.4 in all four recorded UK corridors**; only the pages around it move:

| corridor | checker's rank for `visa_decision` | what displaces it |
| --- | --- | --- |
| NG, PH | **3rd** — admitted | nothing nationality-named on `gov.uk` for those countries |
| IN | **5th** — excluded | the Young Professionals scheme at 54.0, on **two different paths** |
| CN | **5th** — excluded | `translated-visa-application-guidance` 54.0 and `ads-visa` 39.0 (a China-specific scheme) |

`_shortlist` reserves the top **three** per role. Three is why India and China had no plan.

### Two wrong diagnoses first, and a harness so there was not a third

This item was written twice from *reading* the shortlist and named the wrong cause both times — first
"eleven of twenty-five places go to near-duplicate fee pages" (real, but 115 pages outrank the checker
and only 41 are that host), then "the per-role reservation is discarded at truncation" (real, and
measured to change nothing for the better).

The third attempt replayed recorded candidate sets through **the real `_shortlist`**, by binding the
actual unbound methods to a stub. It reproduces **26 of 26 recorded corridors exactly**, which is the
property the first simulation lacked — that one predicted the checker would miss the shortlist for
Nigeria, where the real run admitted it, because it modelled neither `_reserved_per_domain`'s
registrable-domain key nor `_readable_only`.

### The grid, and why depth alone is not the answer

| depth | size 25 | size 30 | size 35 | pages dropped vs today, size 35 |
| --- | --- | --- | --- | --- |
| 3 (today) | NG PH | NG PH | NG PH | — |
| 4 | NG PH | NG PH | NG PH | 0.0 |
| **5** | all four | all four | **all four** | **0.0** |
| 6 | NG PH IN | all four | all four | 0.5 |

Depth alone is **non-monotone**: at size 25, depth 6 admits *fewer* corridors than depth 5. Six roles
five deep wants thirty places and there are twenty-five, so the deepest reservations are pushed back
out at truncation — and the truncation refills by raw score, where 30.4 loses. The two constants have
to move together, which is why both did: **depth 3 → 5 and size 25 → 35**.

At 35 the truncation barely fires, and replayed over all 26 recorded corridors **not one page that is
shortlisted today is dropped.** That is the property worth having: this is an addition, not a
reshuffle. Honouring the per-role reservation *inside* the truncation was tried and measured — it
raises churn and admits nothing extra, so the code is left alone.

### Live

The United Kingdom, all four corridors, cold and unpinned:

| | before | after |
| --- | --- | --- |
| UK/IN, UK/CN, UK/NG, UK/PH | **0 of 8 runs resolved** (entry 58) | **4 of 4** — checklist, route, fees and processing times filled, `visa_decision` handed over as a tool |

Seven regression corridors — Canada, Japan, Singapore, the United States, France, Germany, the
Netherlands — all still behave as recorded: 35 pages read each, roles filled as before, France still
reporting its twelve refusals with the blocked-page judgement still running (`model_calls: 2`).
Corridor phase 13–30s against a 27.4s median, though the page cache was warm, so read that as "no
blow-up" rather than as a timing measurement.

**France gained a checklist.** Its UK mission page — read, not refused — says the France-Visas wizard
will tell the applicant whether they need a visa, which documents to attach, and the fee, so it is now
named for all three. Entry 26 concluded France's checklist "needs the wizard"; naming the wizard turns
out to be enough to tell the traveller where it is.

### Two corrections this produced

- **Entry 60's URL deduplication was wrong and is reverted.** It collapsed one page settling several
  questions into a single entry, which hid France's checklist tool from the documents panel — exactly
  where a reader looking for documents goes. The same page under two questions is two answers. The
  interface suppresses a repeat only inside the catch-all panel that carries fees, times and entry
  conditions together.
- **`resolve_once` in the CLI never touches the corridor store** — no load, no write, deliberately, so
  `--runs` measures variance rather than replay. So CLI numbers are always cold *and* a CLI run never
  warms the store for the API. An earlier note claiming a 33.4s API request had been served from a
  CLI-populated corridor was wrong on that basis; it was a genuine cold resolve plus extraction, with
  only the page cache warm.

### What it does not fix

The scorer still rewards a page for **naming** a country rather than for being **about** one, which is
what put a ballot scheme above the checker in the first place. Depth 5 routes around it; it does not
remove it, and the next country whose gov.uk namespace holds three nationality-named schemes will hit
it again. That is [TODO.md](TODO.md) item 26, and it is a precision problem, which is what the
adjudicator is for. The adjudication packet also grew by up to 40% — 35 candidates rather than 25, at
the same per-candidate excerpt budget — and that was **not** measured in tokens; no call failed across
eleven live corridors.

---

## 60. A questionnaire is an answer, for every role — not a blockade in front of one
**2026-08-24 · decided; implemented; measured live. Widens entry 59, which was too narrow the day it shipped**

Entry 59 gave the pipeline a way to say *"the answer is behind an official tool"* and then allowed it
for exactly one role. That was the wrong shape, and the reason is visible in the run that motivated
it: the Netherlands corridor read `netherlandsworldwide.nl/visa-the-netherlands/entering-without-visa`
— *"a questionnaire of up to 9 questions to determine those requirements for the trip"* — and reported
nothing, because entry 59 only had a slot for the visa decision.

**The framing was wrong, not just the scope.** A wizard was being treated as an obstacle between us
and the guidance. It is not: it *is* the guidance, published in the form the authority chose. An
authority that answers "which documents do I bring" through nine questions has published its document
list, and a plan that stays silent withholds the one thing the traveller can actually act on — they
can answer nine questions in a minute, which is more than a page we could not find gives them.

So `tools` is now a list over roles. `RoleAdjudication.tools`, `ResolvedCorridor.interactive_tools`,
`DestinationConfig.official_tools`, `VisaPlan.official_tools`, each entry carrying the topic it
settles, and the interface offers it beside the question it answers: the decision in the decision
panel, the checklist in the documents panel, the route with the route, and fees, times and entry
conditions — which have no panel of their own — under evidence and caveats.

`DiscoveryRole` is now built from the domain's new `GuidanceTopic` rather than restated beside it, so
a role a page can fill and a topic a plan can offer a tool for cannot drift apart. `irrelevant` stays
discovery's alone: it is a verdict about a page, not a question a traveller has, and a tool named for
it is refused outright because there is nowhere in a plan to put it.

### What does not widen, and this is the load-bearing half

**Only `visa_decision` changes whether a corridor resolves**, because only `visa_decision` is
load-bearing. A questionnaire holding the fees adds a link to a plan that already stands; it can never
turn a corridor that should refuse into one that does not. That asymmetry is what makes widening the
*rest* cheap: entry 32's drift risk lives entirely in the load-bearing role, and it is untouched.

**A tool never fills the role it is named for.** The role stays in `unresolved_roles`, no source is
invented, and nothing about the tool is citable. For the checklist that is not a nicety but the rule
this project exists to enforce: naming a `document_checklist` tool leaves
`application_document_source_ids` empty, so `validate_absent_checklist` still forbids listing a single
requirement, and a new validator forbids the contradiction from the other side — a plan naming a
checklist tool may not also designate a checklist source. Both prompts say it explicitly, and both
validators would reject it anyway, because entry 27's lesson is that a model asked for null returned
`true`.

**The per-role suppression generalises rather than relaxes.** Entry 59 dropped a tool when a page
stated the decision; that is now applied per role, so a checklist found on a page suppresses only the
checklist tool. And because one page often settles several questions, the *plan* offers each URL once,
under the first topic in `ROLE_ORDER` it was named for — the corridor keeps every judgement, and a
plan is a rendering.

### Measured live

`netherlands/IN/GB/tourism` is the corridor [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md) has recorded as
resolving **0/2** since it was first run — the standing example of a corridor that finds a checklist
and refuses anyway.

| | before | after |
| --- | --- | --- |
| corridor | refused, `visa_decision` not found | **resolves**, naming `entering-without-visa` for `visa_decision` and `general_entry`, and `consular-fees` for `fees` |
| plan | `503`, nothing | **`partial`, 9 document requirements, 6 steps**, `visa_required: null`, the checker linked in the decision panel |

The model's own reasons are the discrimination the widening needed: the fees page *"asks the reader to
choose their country and says the resulting consular-fee list shows how much consular services cost"*,
while the same run declined to name anything for `application_route`. Under entry 59's wording, the
identical page had been assigned `general_entry` and reported as nothing at all.

The interface was checked against a plan carrying a decision tool, a checklist tool and a fees tool at
once: each rendered in its own panel, and the **documents panel appears at all**, which it previously
could not — with no requirements it returned nothing, so an authority publishing its list through a
questionnaire produced a plan with no document section and no explanation of why.

**One caveat, and it is known problem 10 again.** Two runs of the same Netherlands corridor named
three tools and then two — `consular-fees` appeared on one and not the other. The *outcome* did not
move (both resolved, both `decision_is_unverified`), but which tools are offered can differ between
runs, exactly as entry 57 found for blocked-page judgements.

---

## 59. The third outcome: the answer is behind a tool, so hand over the tool
**2026-08-24 · decided; implemented; measured live. Closes TODO item 24, and declines a larger version of it**

> **Widened the same day by entry 60**, which allows a tool for *any* role rather than only the visa
> decision. Everything below still holds — the bounds, the rejected URL-construction alternative, and
> the reasoning — but read `decision_tool` as one topic of several, and the field names have changed.

Entry 58 measured the largest coverage limit there is and it was not bot-blocking: it was authorities
that publish the visa decision inside an interactive tool. Every United Kingdom corridor refused
after correctly resolving the checklist, the application route, the processing times and
per-nationality fees, because `visa_decision` is load-bearing and `gov.uk/check-uk-visa` is a
questionnaire. The page was served willingly, fetched cleanly and read; the adjudicator judged it
does not state the answer, because it does not.

There were three outcomes and the code could express two. *Found* resolves. *Blocked* resolves
`partial`, names the page and says the decision could not be verified (entries 27 and 57). **"The
answer exists, on a page we read, but only inside a tool"** had nowhere to go, so it fell into *not
found* and threw a working plan away.

It is now its own outcome. `ResolvedCorridor.decision_tool_urls`, `DestinationConfig.decision_tools`
and `VisaPlan.decision_tools` carry it; `is_usable` and `decision_is_unverified` accept it the way
they accept a settled refusal; the plan states `visa_required` as null and the interface prints the
URL in the decision panel with a sentence saying that answering its questions there gives the
traveller their answer.

### The alternative that was measured and declined: construct the answer URL

GOV.UK's checker is a *server-rendered* smart answer, and its answers are addressable. Measured
2026-08-24 with `curl` under our own user agent, no browser and no JavaScript:

| probe | result |
| --- | --- |
| `gov.uk/robots.txt` | `/check-uk-visa/*` allowed — only `/*/print$` and `/search/all*` are disallowed |
| `GET /check-uk-visa/y/india/no/tourism/no` | **200**, server-rendered, *"You'll need a visa to come to the UK — Apply for a Standard Visitor visa"*, and it restates every question and answer used |
| `GET /check-uk-visa/y` (already in the GB corpus) | a `method="get"` form publishing **221 nationality slugs** as `<option value>`, and the purpose step publishes nine more as radio values |

So the transitions are published by the authority, and following them is a sequence of plain GETs to
URLs GOV.UK itself printed. That is **not** what CLAUDE.md's no-list forbids: nothing is rendered,
nothing is POSTed, no application is begun. The rejection is not on those grounds.

**It is rejected on what it would have to invent.** Two of the checker's questions — dual British or
Irish citizenship, and whether the traveller is visiting a partner or family member — are not in a
corridor. Answering them is supplying traveller input nobody gave us, on the one question where a
wrong answer is the most damaging thing this project can produce. A leaf walk requiring every
reachable branch to agree would avoid that, and measured it holds for the four nationalities entry 58
sampled — India, Nigeria and China all reach *"you'll need a visa"* on both branches, and only the
*"usually"* differs. But it holds by luck of those corridors, not by construction, and the failure
modes are quiet: an invalid slug (`united-states`, where the slug is `usa`) returns **200 with
question one**, not a 404, and branch depth varies by nationality, so `usa/no/tourism/no` **404s**
where India's five-segment path resolves. Two ways to be wrong that look like ordinary responses.

**And it generalises to almost nothing.** It is one authority's URL scheme. France — the other
wizard country, entry 26 — is a JavaScript application behind a Cloudflare challenge, and none of it
applies. Naming the tool works for both, today, with no per-country code.

It is written down rather than dismissed because the measurements are cheap to re-derive and the idea
is attractive. If it ever returns, the bar is: only options parsed from a page actually fetched, stop
at a page publishing no options, **unanimity across every reachable leaf**, 404 and restart-to-
question-one both treated as no answer, and never a question the corridor does not answer. And it
must sit *on top of* this entry, so a walk that fails lands on "here is the tool" rather than on a
guess.

### Keeping *not found* and *behind a tool* apart

Entry 32's lesson, on a new exception: if "we could not find it" can present as "an official tool
holds it", every failed corridor drifts into looking tool-limited and the refusal discipline leaks.
Four things hold it:

- **Only the adjudicator names one, and only on a page it was given the text of.** The heuristic
  never does. Whether a page is a questionnaire is a question about *meaning*, and entry 57 is what
  keyword-matching meaning cost the last time; with no adjudicator configured the corridor refuses
  exactly as before.
- **The application decides what is real.** An id the model invents is discarded, like every other,
  so it can only ever point at a page that was fetched.
- **Only when nothing filled `visa_decision`.** A tool named beside a found decision is dropped with
  a note — the same short-circuit `decision_blocking_urls` gets, and for entry 57's reason: a field
  describing something that did not happen is one a later reader will believe.
- **Officialness is still the domain's.** A tool URL off the approved domains is refused by
  `DestinationConfig`, exactly as an unreadable authority is. Reading the page changes nothing about
  what vouches for it, and a traveller is being sent there.

It does **not** need entry 32's second gate — the "could this page plausibly have held the decision"
test. That gate exists because a blocked page is judged with no text at all. Here the text is in
hand, so "this page defers the answer to a form" is the stronger and more checkable claim.

The plan-level guards are structural rather than requested in a prompt, for the reason entry 27 gives
about `decision_is_unverified`: a model asked for null returned `true`. A `VisaPlan` naming a tool
**cannot** also state `visa_required`, and can never be `verified`.

### Measured live, and the first version did not work

Run on the real corridors, corpus-routed:

| corridor | before | after |
| --- | --- | --- |
| `united-kingdom/NG/NG/tourism` | refused | **resolves `partial`** — checklist, route, fees, times, and `gov.uk/check-uk-visa` named. Full plan through the API: `visa_required: null`, 4 document requirements, 7 steps, first step *"Open the official visa checker and answer its questions"*, 33.4s |
| `netherlands/IN/GB/tourism` | refused, decision not found | **still refuses** — and the model saw a page that *"offers a questionnaire"* and declined to name it, because the page's subject is entry requirements rather than the decision |

**The first prompt wording produced nothing.** `gov.uk/check-uk-visa` was shortlisted, fetched and
read, and the model left `decision_tool` null — correctly, under the rule as first written, which
said to skip a page that "merely links to a tool". Measured, that landing page is **804 characters**:
a title, two sentences, and a "Start now". It reads as a signpost. The rule now names the case
explicitly — a short landing page whose whole purpose is to start the checker qualifies, a page about
another subject that links to one does not — and asks for two things together: the page's own subject
is the visa question, *and* it puts the reader into a checker instead of answering. That is a
sharpening, not a loosening, and the Netherlands run is the evidence: a questionnaire on a page about
something else is still declined.

### What it does not fix, and this is now the binding limit for the United Kingdom

**`gov.uk/check-uk-visa` does not reach the shortlist for every corridor.** Across the four recorded
UK runs it scores 30.4 every time and ranks 104th–116th of ~820, and it was shortlisted for **NG and
PH but not IN or CN**. So entry 58's *"it was ranked, shortlisted and fetched"* was true of the runs
it looked at and not of all of them, and this fix cannot fire where the page never arrives.

**The cause named here was wrong, and is corrected below** — it read the shortlist and blamed the
**11 of 25 places taken by near-duplicate `visa-fees.homeoffice.gov.uk` pages**, all one role, scoring
116–136 against the checker's 30.4. That crowding is real and it is not sufficient: counted off the
same log, **115 pages outrank the checker overall and only 41 are the fee host**, so freeing every fee
place still leaves 74 above it. The binding fact is scoring — the checker is **5th of 76** for its own
role, behind **two URLs for the same unrelated page**, `india-young-professionals-scheme-visa`, at
54.0 — and the gate is the top-*three*-per-role reservation, not the window. See
[TODO.md](TODO.md) item 25, which now says this; it is a ranking problem, not this one.

---

## 58. The twenty-corridor measurement: it passes the bar, and the bar was nearly the wrong question
**2026-08-24 · measured live; the bar was committed in advance as entry 35**

Twenty corridors, each run twice — India, China, Nigeria and the Philippines to the United States,
United Kingdom, Germany (Schengen), the UAE (Gulf) and Canada, applying from home, tourism. Forty
live runs, all corpus-routed, **none crawled**. Germany was chosen over France for Schengen because
France is already measured and entry 35 warns against a sample picked for being easy; Germany is the
trust rule's hard case, running on a single `reviewed` domain (entry 33).

### The result

| | | bar | |
| --- | --- | --- | --- |
| decision confirmed, both runs | **15/20 — 75%** | ≥70% | **pass** |
| checklist found, both runs | **10/20 — 50%** | ≥50% | **pass, exactly** |
| decision blocked and named | 1/20 | | US/Nigeria |
| decision not found | 4/20 | | every UK corridor |

**It passes. It passes by one corridor on the decision and by nothing at all on the checklist** — the
checklist number is exactly the threshold, and a single corridor moving either way changes the answer.
That is a pass, and it should be quoted as a marginal one.

### The sample is five destinations, not twenty corridors

This is the finding that should govern how much weight the numbers carry. Within every destination,
all four nationalities behave almost identically:

| destination | decision | checklist | produced a plan |
| --- | --- | --- | --- |
| Canada | 8/8 confirmed | 8/8 | 8/8 |
| UAE | 8/8 confirmed | 6/8 | 8/8 |
| Germany | 8/8 confirmed | **0/8** | 8/8 |
| United States | 6/8 confirmed, 2 blocked | **0/8** | 8/8 |
| United Kingdom | **0/8** — all not found | 7/8 | **0/8** |

Nationality changed the outcome exactly once in twenty (US/Nigeria, confirmed → blocked). So the
effective sample is **five independent observations replicated four times**, and "75%" is really
"three and three-quarters destinations out of five". Entry 35 specified twenty corridors and got
twenty corridors; what it did not anticipate is that a corridor is not the unit of variation. **A
future bar should sample destinations, not corridors.**

### The United Kingdom is the result worth acting on

Every UK corridor **refuses and throws away work it had already done**. It fills the checklist, the
application route, the processing times, and per-nationality fees down to the currency
(`visa-fees.homeoffice.gov.uk/y/philippines/usd/visit/standard-visitor-visa`) — and then produces
nothing, because `visa_decision` is load-bearing and unfilled.

**Nothing was blocked.** `inaccessible_domains` is empty. `gov.uk/check-uk-visa` was ranked, shortlisted
**and fetched**, and the adjudicator read it and correctly judged that it does not state the answer:
it is the entry page of a step-by-step wizard that asks questions rather than listing nationalities.

So this is not recall, not access, and not the model being wrong. It is the same cause entry 26 found
in France — *the answer exists only inside an interactive tool* — without France's `403` to trigger the
blocked-authority exception. France resolves `partial` and hands over a URL; the UK, whose page is
served willingly and read successfully, resolves nothing.

**That inverts known problem 11.** Bot-blocked portals were called the largest coverage limit. Measured
here, blocks cost the United States its checklist and turned one corridor's decision into *blocked*;
**the wizard cost every UK corridor its entire plan.** The wizard is the larger limit, and the project
has no way to say "the answer is behind a tool we cannot drive" — which is a third outcome, neither
found nor blocked.

### What else the run establishes

- **Reproducibility is far better than known problem 19 feared.** 19 of 20 corridors gave identical
  outcomes across both runs; the single exception is UK/Philippines, whose checklist was found on one
  run and not the other, on an identical 813-candidate set. That is adjudication variance with recall
  held fixed — known problem 10, now the only variance left.
- **The corpus path carried all of it.** 0 of 40 runs crawled; median corridor 27.4s, range 8.8–48.3s.
- **42 model calls for 40 runs** — the two extra are entry 57's blocked-page judgements, confirming
  that gating keeps it off the ordinary corridor.
- **Three authorities refused us**, consistently: `travel.state.gov` and `egov.uscis.gov` (8 runs each,
  which is what costs the US its checklist) and `gdrfad.gov.ae`.
- **Germany confirms 8/8 on one reviewed domain and a 294-entry corpus**, whose build had fired the
  `depth_is_exercised` warning at 2%. A thin corpus was enough for the decision and not for a checklist.

### What it does not establish

Purpose was tourism throughout and residence equalled nationality, so neither dimension is measured.
Germany's and the United States' 0/8 checklists are not distinguished between *the country publishes
none* and *we failed to find it* — known problem 8, still open and now attached to two of five
destinations rather than a hypothetical.

---

## 57. A block is judged, not keyword-matched — the one place the scorer was doing semantics
**2026-08-24 · decided; implemented**

`_decision_blocking` asks *"could this page have held the visa decision?"* and answers it by keyword
match, on a page **nobody read**. That is the only place in the pipeline where the heuristic decides
what a page *means* rather than whether it is worth reading, and entry 56 is what it cost: Sweden's
`list-of-foreign-citizens-who-require-visa-for-entry-into-sweden` scored `visa_decision` **0.0**, so
an authority refusing the visa-decision page could not make the decision unverifiable, and the
corridor refused instead of handing the traveller the URL. The fix was to add seven phrases to a word
list. That is the wrong kind of fix for a meaning question, and it will keep being needed.

### Why this is the right place to spend a model call, and the shortlist is not

The scorer has three jobs and does them very differently:

| job | verdict |
| --- | --- |
| reject obvious non-guidance | **well** — archived paths, site furniture, wrong audience, wrong country. Cheap, deterministic, and a veto is safe. |
| rank what survives | **poorly**, but survivably — measured over six corridors, 5 of the 18 pages the model chose ranked outside the 25 places (27th, 31st, 35th, 57th, 101st) and **every one was admitted by the top-3-per-role reservation**, not by its rank |
| **judge what a page means** | **badly, and it should not be doing it at all** |

Only the third moves. **The shortlist deliberately stays heuristic**, for three reasons that do not
apply here: something must cut ~2,455 candidates to what a model can read, and reading them all is
thousands of fetches and ~1.9M tokens per corridor; entries 44–53 spent four sessions making the
candidate set *deterministic*, and putting a model in front of it would reintroduce variance exactly
where it was removed; and entry 40 already showed the cheap fix for bad ranking is a wider window, not
a better ranker.

**The cost objection is weakest here.** A blocked page has a URL, an anchor text and a title, and
nothing else — there is no page text, because the authority refused it. So this is a small call over
metadata, and it only runs when a corridor has settled refusals *and* no `visa_decision` was found,
which is a handful of corridors. Most corridors make no extra call at all.

### What must not change, and how each is held

- **Nobody read the page, and nothing may be inferred about its content.** The packet carries the URL,
  the title and the anchor text — never `untrusted_content`, which does not exist for a refused page.
  The prompt says so explicitly, and the packet builder has no parameter through which text could be
  passed.
- **Only settled refusals.** `401`/`403` only, filtered by `persistent_refusals` **before** anything
  is asked. A `429` never reaches the model, so a rate limit still cannot resolve a corridor
  (entry 32).
- **The application decides what is real.** Ids the model invents are discarded, exactly as
  `validated_choices` does for roles. It may only ever narrow the set it was given.
- **Failure fails closed.** Two attempts, then an empty result — which means the corridor refuses,
  the same outcome as nothing qualifying. A model outage can never *create* a blocked-authority plan.
  It can cost one, which is why it retries (entry 31's reasoning).
- **The deterministic path is unchanged.** With no adjudicator configured — the offline regression
  baseline — the keyword test still runs. That is the same split `_decide_roles` already makes, and
  it is not entry 31's forbidden fallback: "no model configured" is a deliberate mode, where "the
  model call failed" is an outage.

### Measured live, and the prediction held

The test committed in advance was that France should resolve again **for the right reason** — its old
qualification was a blank CERFA application form (entry 55). Run 2026-08-24, twice, France's six
settled refusals were judged:

| | page |
| --- | --- |
| **qualified** | `/en/royaume-uni` — the page for applying **from the United Kingdom**, which is this traveller |
| **qualified** | `/en/web/france-visas` — the portal's main visa page |
| **qualified** | `/en/web/france-visas/india` — France's own India page, for an Indian passport |
| rejected | `/en/faq` |
| rejected | `/en/demande-de-visa` — the application form page |
| rejected | `/en/short-stay-visa` — a visa *category*, not a decision |

That is the discrimination keywords could not make: the keyword scorer rates `/india`
`application_route` 74.4 and `visa_decision` **0.0**, and rated the CERFA form 14.0. France now
resolves `partial`, `decision_is_unverified`, naming pages that plausibly hold the answer — which is
what entry 26 established was true of that portal and what entry 27 exists to produce.

Sweden qualifies its country list on both runs, unchanged and stable. **Canada makes no extra call at
all** — `model_calls` 1, because its decision was found — which is the gating working.

**Cost and variance, stated plainly.** A corridor whose decision is blocked pays one extra small call
(`model_calls` 2); every other corridor pays nothing. The judgement is non-deterministic like any
other: France returned three pages on one run and two on the next, dropping `/india`. The *outcome*
did not move — both runs resolved, both `decision_is_unverified` — but the reported list can differ,
and a corridor sitting on exactly one marginal refusal could flip. That is known problem 10's family,
now reaching one more field.

---

## 56. The vocabulary asked the question and could not recognise the answer
**2026-08-24 · measured; implemented; rejects item 23's own proposal**

[TODO.md](TODO.md) item 23 proposed removing the `not scores` guard from `score_role_vocabulary`, so
that "this page mentions visas" always contributes a `visa_decision` floor. **Measured, that is the
wrong fix, and the right one is smaller.**

### Why the guard is not the defect

Removing it would give a positive `visa_decision` score to **12–58% of a country's pages** — Canada
6%, France 12%, Singapore 18%, Japan 25%, United States 44%, **Netherlands 58%** — because
`mentions_visa` is a substring test against the flattened URL, and on a visa authority's site nearly
every path contains the word. `_decision_blocking` admits any refusal scoring above zero, so that
change would turn entry 32's test from *"real visa-decision signal was seen"* into *"the URL contains
the word visa"*, which is the precise drift entry 32 exists to prevent. Its own docstring would stop
being true.

**And the guard costs no recall.** Sweden's page was shortlisted anyway, on `general_entry`. The only
consumer of a `visa_decision` score that the guard changes is `_decision_blocking`. So the guard is
doing its job — the floor is a "do not lose this page" net, needed only when nothing else caught it.

### What the defect actually is

Every `visa_decision` term was a way of **asking**: `visa requirement`, `do i need a visa`,
`check if you need`, `visa exemption`. There was no way to recognise a page that **states the
answer**. Sweden's `list-of-foreign-citizens-who-require-visa-for-entry-into-sweden` matched none of
them — the list has `entry visa` and the page says *visa for entry*; it has `do i need a visa` and the
page says *who require visa* — so it scored `general_entry` **22.4** on the word "entering" in its
title, and `visa_decision` **0.0**. `government.se` then refused that exact page, the block was
correctly reported, and the corridor refused instead of handing the traveller the URL.

Seven answering phrasings are added: `needs a visa`, `require a visa`, `requires a visa`,
`require visa`, `visa for entry`, `countries whose nationals`, `countries whose citizens`.

`require visa` looks like a typo and is not. `searchable_url` flattens hyphens to spaces and URL slugs
routinely drop the article that prose keeps, so `require-visa-for-entry` can never match
`require a visa`. Half this scorer's signal comes from slugs; the vocabulary was written entirely in
prose.

### Measured, by replaying the real candidate sets

Each corridor's recorded candidates were rebuilt exactly as its run built them — search candidates
carrying the engine title, corpus candidates carrying the stored anchor text and heading — and
re-scored under both lexicons. The replay reproduces every recorded candidate count, so the
shortlists it produces are the shortlists those runs would have produced.

| | result |
| --- | --- |
| Sweden's blocked decision page | `visa_decision` **0.0 → 82.4**, and it **now qualifies its own refusal** |
| Shortlist changes, all seven corridors | **none** — 25 in, 25 out, same URLs |
| France | still **0** qualifying refusals, so it still correctly refuses |
| United States | unchanged at 2 qualifying |

### One term was tried and rejected, and only the shortlist diff caught it

`need a visa` is the obvious general form of `do i need a visa` and matches 25 pages across the seven
corpora. It sits **inside** `check if you need a visa`, so both terms fire and the page scores twice:
a Caribbean page on `netherlandsworldwide.nl` went 42.9 → 60.4 and displaced the Netherlands' own
**United Kingdom application page** from the shortlist. Counting how many pages a term matches would
never have shown that; diffing the shortlist did.

**Seven such overlapping pairs already exist** — `visa requirement`/`visa requirements`,
`processing time`/`processing times`, `fees`/`visa fees` and four more — each scoring up to double.
They are **frozen rather than fixed** by `test_no_new_overlapping_lexicon_terms`: correcting them
moves every score by up to 2× and needs its own measurement. What the test guards is a *new* one.

### How far this is verified

**Offline: completely.** The replay is faithful and the tests fail on the previous lexicon.

**Live: confirmed end to end, 2026-08-24.** Two runs of `sweden/IN/GB/tourism`, both identical:

```
usable: True   decision_is_unverified: True
decision_blocking: government.se/.../list-of-foreign-citizens-who-require-visa-for-entry-into-sweden
```

So the corridor now resolves `partial`, states the visa decision **unknown**, and hands the traveller
the URL of the page the authority refused. **That is entry 27's exception firing on a real corridor
for the first time**, and it closes known problem 25. France still refuses with `decision_blocking`
empty — correct, since its old qualification was a blank CERFA form — and Canada still resolves.

*Note for whoever verifies something like this:* a corridor that **refuses** populates only `notes`,
not `inaccessible_domains`/`inaccessible_urls`, because `_refused` does not carry them. A refusing run
therefore cannot be used to check block reporting; read the notes or the recall log. This cost a
verification step when adjudication was failing on exhausted credit.

---

## 55. Six corridors through the corpus: 2–5× faster, and it breaks the blocked-authority exception
**2026-08-23 · measured live; NOT fixed**

Item 15's six corridors, each run twice on the crawl path, then their corpora built offline
(TODO item 18, first time for any country but Canada), then each run twice again corpus-routed.
Twenty-four live runs. Registry path throughout, so these describe what the API does.

### Speed: unambiguous

| corridor | before | after | crawl | candidates |
| --- | --- | --- | --- | --- |
| japan | 37.5s | **14.9s** | 17.4s → 0.0s | 558 → 920 |
| netherlands | 30.9s | **12.9s** | 16.6s → 0.0s | 290 → 903 |
| sweden | 39.9s | **18.0s** | 23.3s → 0.0s | 83 → 396 |
| united-states | 31.4s | **14.9s** | 17.6s → 0.0s | 799 → 1,651 |
| france | 23.6s | **11.2s** | 9.9s → 0.0s | 413 → 1,181 |
| singapore | 56.1s | **10.8s** | 29.8s → 0.0s | 376 → 863 |

2.1× to 5.2×, and the candidate pool grew every time. Both runs of every corridor saw an identical
candidate count, before and after.

### Roles genuinely found: neutral to better

Japan and Singapore fill all five roles, unchanged. **The United States gained `fees`** (0/2 → 2/2)
and **the Netherlands gained `processing_times`** (0/2 → 2/2) and a second checklist run. Only France
lost one (`processing_times`).

**Japan is worth reading closely, because the prediction was wrong.** Its corpus holds **1 of 6**
baseline role pages: five came from `uk.emb-japan.go.jp`, and the corpus has 29 mission hosts —
Auckland, Boston, San Francisco, even `edinburgh.uk.emb-japan.go.jp` — and **not the London embassy**.
The offline build is traveller-free, so which posts it sweeps up is whatever search returned. It
resolved all six roles anyway, because **search still runs** and supplied them. That is entry 47's
union doing exactly the job it was built for, and it is the strongest argument yet for entry 48's
refusal to drop search.

### But two corridors went from resolving to refusing

**Sweden and France both flipped**, and both for one reason: `decision_blocking_urls` went empty, so
entry 27's exception — name the blocked page, state the decision unknown, produce a partial plan —
could not fire.

**The reporting did not break.** `inaccessible_domains` and `inaccessible_urls` still name the
refusing hosts and pages in both corridors; entry 49 works, and that was the constraint entry 48
named. What broke is **qualification**, which entry 48 did not consider: `_decision_blocking` needs a
refusal *observed on a page that scored for `visa_decision`*, and the crawl was observing far more
refusals than a 25-page shortlist fetch does. France's crawl met **18** `france-visas.gouv.fr` URLs;
the fetch meets **6**.

**The two are not the same case, and the difference matters.**

*France is a correction.* Its baseline qualified on
`france-visas.gouv.fr/documents/d/france-visas/cerfa_14076-04_court_-sejour_en` — a **blank CERFA
application form**. That is precisely the incidental hit entry 41 calls "the opposite of entry 32's
intent". Refusing is the better answer.

*Sweden is a real loss.* Its baseline qualified on `.../migration-and-asylum/information-on-visas`,
which scores 14.0 for `visa_decision` and is a credible decision page. On the corpus path that URL was
not shortlisted at all, while the page that **was** asked —
`.../list-of-foreign-citizens-who-require-visa-for-entry-into-sweden`, whose path could not state the
role more plainly — entered from **search** with the title *"List of third countries whose nationals
must be in possession of visas…"* and scored **`general_entry` 22.4, with no `visa_decision` score at
all**. So a blocked page that is unmistakably the visa decision cannot qualify the corridor.

### The scoring rule underneath both, which is the thing to fix

`score_role_vocabulary` grants the "this page mentions visas" base score to `visa_decision` **only
when the page scored for nothing else**:

```python
if not scores and mentions_visa:
    scores["visa_decision"] = base
elif mentions_visa and "visa_decision" in scores:
    scores["visa_decision"] += base
```

So any page that picks up *another* role's vocabulary loses its `visa_decision` floor entirely. Entry
41 recorded this for France — "every one of the eight `france-visas.gouv.fr` URLs scores
`application_route` only, including `/en/assistant-visa`, the visa-decision tool itself" — and treated
it as a French quirk. It is not: it is a general rule, and Sweden shows it on a URL that says
*who requires a visa* in English.

**Deliberately not fixed here.** Removing the `not scores` guard is a one-line change to the scorer
that decides what every corridor may see, and entry 40's asymmetry cuts both ways. It needs its own
measurement, not a same-session edit at the end of a long run. TODO item 23.

### Also found

**The corpus stores one `link_text`/`heading` per URL, and a page is linked from many places.**
Sweden's decision page is held with the heading *"I will be studying in Sweden for less than three
months"* — the section that happened to link to it — which is off-scope vocabulary for a tourism
corridor. So the corpus can attach one traveller's context to a page every traveller needs. Related
to entry 53's finding that richer link text is usually an advantage; here it is a liability.

**Three of six corpus builds fired `depth_is_exercised`** — Japan 9%, France 6%, Singapore 3% beyond
depth 1 — so they fetched their seeds and effectively stopped, exactly what that flag exists to say.
Canada's 1,200-page budget was tuned against Canada's seed count; a country with 272 seeds needs more.

**One failed search query loses a whole country's build.** `search_all` raises if any query fails,
which is right for a corridor — its docstring says tolerating a failure is a separate decision about
serving partly-searched evidence — but a corpus is additive and never claims completeness, so losing
70 queries of work to one DNS blip is the wrong trade. It happened once during this run.

---

## 54. One encrypted PDF took a whole corridor down, and no narrower `except` could have caught it
**2026-08-23 · found live; implemented**

`sweden/IN/GB/tourism`, run through the corpus-routed path, **raised** out of `_fetch_bodies` and
produced nothing at all:

```
DependencyError('cryptography>=3.1 is required for AES algorithm')
```

An AES-encrypted PDF sat in Sweden's shortlist. `extract_pdf_text` caught
`(PdfReadError, ValueError, OSError, KeyError)` — and `pypdf.errors.DependencyError` extends
**`Exception` directly**, not `PdfReadError` and not even `PyPdfError`, so no tightening of that
tuple would have caught it. The corridor did not degrade; it aborted.

**Why it appeared now, and why that is the interesting part.** Nothing about PDFs changed. The
*shortlist* changed: entry 51 removed the crawl for a built country, so the twenty-five pages fetched
are drawn from a different pool, and this one drew in a PDF the crawl-built shortlist had never
ranked. The bug was always reachable — any corridor whose shortlist happened to include an encrypted
PDF would have hit it — and it took a shortlist built a different way to reach it.

**The fix makes the function total.** `extract_pdf_text` now catches `Exception` and reports "the PDF
could not be read". The breadth is deliberate and is the opposite of the usual advice: this parses
arbitrary bytes served by an arbitrary authority, so its contract is that every input either yields
text or is reported as unreadable. Losing one source to a bad PDF is ordinary and already
well-handled — it becomes a `SourceFailure` with outcome `unusable`. Losing a traveller's entire
answer to one is not, and no enumerated tuple can be trusted to have covered every way a third-party
parser fails on hostile input.

Frozen by `test_a_pdf_that_needs_a_missing_dependency_is_unreadable_not_fatal`, which fails on the
previous code. The test fakes the error rather than shipping an encrypted PDF, because reproducing
one requires the very dependency whose absence causes the failure; what it freezes is the contract.

---

## 53. Measured live: the crawl's 33.6s is gone, and removing it exposed a defect only a run could find
**2026-08-23 · measured live; implemented**

[TODO.md](TODO.md) item 22's step 4, run on `canada/GB/GB/tourism` — entry 48's own corridor —
instrumented at the same four boundaries. **The first run refused, and finding out why is the point
of this entry.**

### The defect: the corpus lost to search on the same page

`entry-requirements-country.html` is the only page found that states Canada's requirement for a
British citizen in static text (known problem 19). It entered the run at **32.0**, missed the
shortlist, and was never fetched. Its **corpus** entry scores **63.4**.

The two describe the same URL from different evidence. Search knows the engine's title — *"What you
need to enter Canada - Canada.ca"*. The corpus knows the anchor text and section heading an offline
crawl harvested from the page linking to it — *"Entry requirements by country or territory"* under
*"Check if you need a visa or eTA to travel to Canada"* — and `link_text_weight` is why that is worth
twice as much. `_resolve` seeded `candidates` from search **first** and folded the corpus in with
`setdefault`, so the thinner description could never be displaced.

**It was latent until entry 51, and the crawl was what hid it.** The crawl re-found such pages with
their real anchor text, and *its* merge compares scores and replaces the weaker candidate. So the
crawl had been quietly repairing this line on every run — which is also why entry 48's corpus-only
experiment, done without a crawl but also without search, never met it.

The fix is one rule applied consistently: **the best evidence about a page wins, whichever stage
produced it**, exactly as the crawl loop already did.

### The measurement, after the fix

Four runs, minutes apart, evidence cache warm from run 1 onward:

| run | total | search | **crawl** | fetch | adjudicate | candidates | shortlist | roles filled |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 (defect) | 21.75s | 4.12s | **0.00s** | 6.34s | 10.16s | 2,455 | 25 / 24 | **refused** |
| 2 | 12.73s | 2.77s | **0.00s** | 1.16s | 7.69s | 2,455 | 25 / 24 | decision, fees, times |
| 3 | 13.24s | 3.45s | **0.00s** | 1.24s | 7.70s | 2,455 | 25 / 24 | decision, fees |
| 4 | 12.82s | 2.86s | **0.00s** | 1.06s | 8.05s | 2,455 | 25 / 24 | decision, fees |

Against entry 48's **54.2s**, of which the crawl was 33.6s. The projection was ~21s and the measured
figure is better than that, but **not because the design beat its estimate** — search came back in
2.8–3.5s where entry 48 saw 9.1s, and adjudication in 7.7–8.1s where it saw 10.8s. Both are
someone else's latency on a different day. **The claim this run supports is the narrow one: the
crawl's 33.6s is gone, and nothing else in the corridor grew to replace it.** 97% of candidates
(2,387 of 2,455) now come from a file rather than the network.

**Adjudication is now the corridor**, at ~60%. Whatever is optimised next, that is where it is.

### What three identical runs do and do not show

The candidate count, the shortlist size and the fetched count were **identical across all four runs**,
and `visa_decision` was filled from the same page in all three that resolved. That is the closest
this project has come to a stable candidate set, and it follows from where the candidates come from
rather than from luck.

**It is not proof that recall is stable**, and known problem 19 stays open. These runs were minutes
apart, on one corridor and one destination, and 68 candidates still came from search, which is
nondeterministic at the source (entry 47).

**What it does isolate is the model.** Run 2 filled `processing_times` and runs 3 and 4 did not, on
the same code with the same candidate count — so that variance is adjudication, not recall. Holding
recall fixed enough to say that is new; known problem 10 has never before been separable from
known problem 19.

`document_checklist` went unfilled in all three. That is **not** a recall failure: eleven candidates
scoring for the role were fetched, including `supporting-documents.html` at 64.0, and the model chose
none of them. The gate did its job and the decider declined — which is the honest refusal this
project prefers, and it is why the corridor is `is_usable` with a role unfilled rather than pretending.

---

## 52. Entry 47's pin only half existed: the truncation dropped it
**2026-08-23 · measured; implemented; fixes entry 47**

Entry 47 states that a page which already filled a role for a corridor "keeps its shortlist place
regardless of ranking". **It kept it as far as `chosen` and no further.** `_shortlist` then sorted by
score and cut the tail, protecting only the per-domain reservation, so a pinned page below the cut
was dropped — and that is the **only** pin that matters, because a page that wins the ranking never
needed pinning in the first place.

Found while checking entry 50's own claim, which is the useful part of how it turned up. Entry 50
argues a top-400 pre-filter would drop `cbsa-asfc.gc.ca/travel-voyage/td-dv-eng.html` — `proven`,
scoring **0.0** on role vocabulary, ranked 2,871 of 3,216 — and that a pin could not rescue it,
because `_shortlist` looks for pinned URLs *inside* `candidates`. Verifying that on the real corpus
showed something worse: with **no** pre-filter at all, the page is in `candidates`, is pinned into
`chosen`, and is still cut. So the pin was never load-bearing for the case it exists for.

**The fix**, and the ordering in it: pinned pages and per-domain reservations are both honoured at
the truncation, **pins first**. If the two together overflow the budget, a page that has answered
*this* corridor outranks a domain that merely has not been read yet — the first is evidence, the
second is a hedge.

Frozen by `test_a_pin_survives_the_shortlist_truncation`, which fails on the previous code. The
existing pin tests did not catch it because they pin a page that scores well, so the truncation was
never reached.

**The general lesson is the one these files keep re-learning.** Entry 47's claim was written from the
code path that adds pins, not from a run where a pin was needed, and it read as true for two days.
`CLAUDE.md` says to prefer a run, a test, or a printed result over a careful reading; this one was
caught only because a *different* entry's argument depended on it and got checked.

---

## 51. The crawl leaves the request path for a country whose corpus already out-covers it
**2026-08-23 · implemented**

Entry 48's central measurement stands and is what this acts on: the crawl is **33.6s of a 54.2s**
corridor, and of the 25 pages that reached the shortlist **14 came from the crawl and all 14 were
already in the corpus**. It contributed no unique shortlisted page.

**The better reason to drop it is determinism, not the 62%.** The request-path crawl is one of the
two places recall is re-rolled per run — known problem 19, the whole reason the corpus exists. Item
22 asks whether a *smaller* crawl seeded from the corpus would beat none at all, and the answer is
no: a smaller crawl keeps the lottery for a fraction of the saving. Pages published since the last
build are the offline job's problem, and entry 47's write-back already folds back whatever a live
run turns up.

### The condition is derived, not calibrated

`LinkCrawler` visits at most **40** pages. A corpus already offering more than 40 candidate pages,
on domains trusted right now, cannot be out-covered by one — so that is the bound, and
`DEFAULT_CRAWL_PAGES` is now named so the resolver can read it rather than repeat a number.

This is deliberately not another tuned constant like the shortlist's 25 or the domain cap's 5. It
also keeps entry 48's requirement exactly: **a country nobody has built behaves as it does today**,
and so does one whose corpus is a handful of pages. The skip is recorded in the notes, because a
corridor whose timing and candidate set changed with nothing visible saying why is the kind of thing
these files keep having to correct later.

### What was checked before the crawl could go

- **Reporting.** Entry 49 — refusals now come out of the shortlist fetch, and
  `test_a_corridor_that_does_not_crawl_still_reports_a_refusal` runs the whole corridor with the
  crawl skipped and asserts a `403` still reaches `inaccessible_domains`, `inaccessible_urls` and
  `decision_blocking_urls`.
- **`_readable_only`.** Item 22 proposed the corpus's `status` stand in for it. **It does not**, and
  the reasoning is in the method. `corpus_build` writes `unreadable` or `unknown` and never
  `readable`, so there is nothing to stand in with — Canada's 3,216 entries hold five unreadable and
  no readable ones. More importantly it is a fetch-budget optimisation reading an observation from
  *this* run; skipping a page on a stored refusal means the refusal is never seen live, so it can
  never reach `decision_blocking_urls`, and a France-shaped corridor would stop resolving
  altogether. The cost of not skipping is a few of twenty-five places on a 1.1s step.
- **`_mission_domains`.** Unaffected: it reads `destination.sources`, which the automatic path
  leaves empty, so it returns `[]` with or without a crawl (known problem 16).
- **Titles.** A crawl learns a page's `<title>` by fetching it; the corpus already stores one. It is
  now carried through, or a corpus-sourced candidate would fall back to its link text — the crawl's
  fallback, not a store's.
- **`found_by="corpus"`.** Entry 48's key measurement — how many shortlisted pages the crawl
  contributed that the corpus lacked — was taken by hand against a 3,216-entry store. Recorded on
  the candidate, the recall log answers it for free next time.

### Also closed

`visa-discover corridor` now reads the corpus. It did not, so every measurement taken through the
command described a pipeline the product had already stopped being. **Pins are still not passed**,
and that is not an oversight: a corpus is corridor-independent, while a pin comes from the stored
resolution of *this* corridor, so passing it would let run one decide part of run two's shortlist —
which is the variance `--runs` exists to measure.

### On the corpus doing three jobs, which item 22 asked for a view on

`status="proven"` does **not** cross entry 44's line. That line is against storing a *conclusion* —
"a British citizen needs an eTA" — which would be served weeks later with a citation. `proven`
records that a page **was used**, never what it said, and the page is still re-fetched and
re-adjudicated on every run; it can only ever change recall.

There is one thing worth naming rather than fixing. `proven` is corridor-*derived* and stored
per-country without which corridor proved it, so a page that answered `canada/IN/IN/tourism` is
marked proven for `canada/GB/GB/business` too. That is safe — it is a retention tier and a hint —
but it is the one place the store is not strictly corridor-independent, and the per-corridor version
of the same idea already exists as the pin. If `proven` ever starts carrying *which* corridor, it
has become a per-corridor store and entry 44's arithmetic applies to it.

---

## 50. The routing index removes the wrong cost: it is `wrong_country`, not scoring
**2026-08-23 · measured; implemented; amends entry 48**

Entry 48 measured that consuming Canada's whole 3,216-entry corpus for one corridor costs ~3.6s,
concluded that *scoring* is what scales badly, and designed a stored-score top-400 pre-filter around
that conclusion. **The total is reproducible. The attribution is wrong**, and with it the design.

### Where the seconds actually are

Measured on `var/corpus/CA.json`, 3,216 entries, `canada/GB/GB/tourism`:

| step | before | after |
| --- | --- | --- |
| load + `entries_within` + `to_link` | 50ms | 46ms |
| **`reject()`** | **4,362ms** | **134ms** |
| — of which `wrong_country` | **3,330ms** | — |
| `score_link` + `CandidatePage` | 345ms | 166ms |
| **total corpus → candidates** | **4,757ms** | **346ms** |

`wrong_country` scans all 198 countries for every candidate, and `_matches_country` rebuilds the
link's path segments, lowered text and host labels **once per country** — 198 times per candidate —
then compiles a fresh `\b…\b` regex per token, against roughly 600 distinct tokens and a 512-entry
`re` cache that therefore thrashes.

The fix is an index, but not over the corpus: `CountryRegistry.possible_for` maps a word to the
countries that could use it, so a candidate's own words select the handful worth checking, and the
**existing exact check then runs on those, in registry order**. Superset in, same answer out:
**3,277ms → 98ms, byte-identical on all 3,216 entries**, frozen by
`test_the_country_prefilter_names_exactly_what_a_full_scan_names`.

### So the index is not built

Scoring the **whole** corpus now costs 346ms, against the 575ms entry 48 proposed to pay for a
top-400. The pre-filter would remove ~145ms of a 54-second corridor and add a permanent recall cut.

**And the cut is not hypothetical.** `cbsa-asfc.gc.ca/travel-voyage/td-dv-eng.html` is
`status="proven"` in Canada's corpus — it filled a role in a resolved corridor — and scores **0.0**
on role vocabulary, ranking **2,871 of 3,216**. Every top-N below ~2,900 drops it. Worse, a pin
cannot rescue it: `_shortlist` looks for pinned URLs *inside* `candidates`, so a page removed
upstream is gone before pinning runs. (Checking that claim on the real corpus turned up entry 52 —
the pin did not rescue it even with no pre-filter at all, for a second and separate reason.) Entry 48's optimisation would have silently undone entry 47's
ratchet, and the fact that entry 48's own check found "3/3 role pages kept" is why — it counted the
pages that corridor happened to use, not the pages the country is known to have answered from.

**The flat ranking is also lopsided by role**, which is worth recording for whoever revisits this.
Flat top-400 on Canada spends **238 of 400 slots on `application_route` and 20 on `visa_decision`**;
flat top-100 keeps 2 of the 4 proven pages. A per-role top-25 covers every role in **150** entries —
so if a bound is ever needed, per-role beats flat, and `proven` and pinned pages must be carved out
of it unconditionally rather than left to win a ranking.

### When to revisit

Not on corpus size alone. The bound is now ~110µs per entry end to end, so 30,000 entries is ~3.5s —
still under a third of the 10.8s adjudication call, but no longer negligible. Revisit when a
destination's corpus passes roughly ten thousand entries **and** a measured phase split says this
step is the largest one left. Then build the per-role variant above, not the flat one.

`CorpusEntry.vocabulary_score` is deliberately **not** added. A stored score is a derived value that
goes stale the moment `role_vocabulary.yaml` changes, with nothing to say it has — the same class of
defect as a row recording when it was written rather than when its evidence was retrieved (entry 4).
If it is ever stored, it needs a lexicon fingerprint beside it and a recompute on mismatch.

---

## 49. A refusal met while reading the shortlist was never reported at all
**2026-08-23 · measured; implemented**

[TODO.md](TODO.md) item 22 lists "`blocked_urls` and `disallowed_urls` come from the crawl, so with
no crawl they must come from the shortlist fetch instead" as the careful part of dropping the crawl.
Building it turned up something narrower and worse: **they never came from the shortlist fetch at
all, and the crawl has been covering for it.**

`_fetch_bodies` read `report.fetched` and discarded `report.failures` entirely. So a page refused at
*retrieval* time reached `notes`, `inaccessible_domains`, `inaccessible_urls` and
`decision_blocking_urls` only if the crawl had happened to meet the same refusal first while
walking for links. Every refusal a corridor has ever reported came from `CrawlFetcher`.

That is invisible today because the crawl usually does meet it. It stops being invisible the moment
the crawl is conditional — which is the next commit — and the failure mode is the one entry 18
exists to prevent: a corridor that quietly stops saying an authority refused it, lost as a side
effect of a speed change.

### Two things had to exist before the crawl could go

**`FetchedShortlist.failures`**, carried out of `_fetch_bodies` and folded in beside the crawl's by
`_report_retrieval_refusals`. Every failure is noted, not only refusals: a shortlisted page that
could not be read is the difference between *"nothing scored well enough"* and *"the site would not
give us the page"*, and that is exactly what a reader cannot infer from an empty result. Notes are
deduplicated per host and reason across both stages, so a reader cannot tell which stage saw a
refusal — only that one was seen.

**`SourceFailure.http_status`.** `CrawlFetcher` has kept `refusal_statuses` since entry 32, because
whether a refusal is *settled* decides what a traveller may be told: a `403` supports saying an
authority would not permit this program to read a page and a `429` does not. Retrieval kept the same
fact **only inside the sentence** `detail`, so applying entry 32's rule here would have meant parsing
prose — which entry 36 forbids by name, for the reason that rewording a message then silently empties
a list something depends on. The status is now carried structurally, and
`PERSISTENT_REFUSAL_STATUS_CODES` reads it. A failure with no status — a DNS failure, a timeout, a
`robots.txt` `Disallow` — is excluded, which fails toward *not* claiming an authority refused us.

### How it was confirmed

Two tests where the refusal is answered **only to the retrieval user agent**, so the crawl never
meets it: a `403` reaches `inaccessible_domains`, `inaccessible_urls` and `decision_blocking_urls`;
a `429` reaches the notes and `inaccessible_domains` and goes no further. Both fail on the previous
code, which is the point — the old behaviour was not merely untested, it was wrong.

---

## 48. The crawl was rediscovering a map the corpus already had; the corpus becomes a routing index
**2026-08-23 · measured; decided; NOT implemented**

Entry 47 made recall monotonic and said plainly that it bought no speed. This is the measurement of
where the time actually goes, and it changes what the request path should do.

### Where a cold corridor spends 54 seconds

Instrumented live, `canada/GB/GB/tourism`, 2026-08-22:

| Phase | Time | Share |
| --- | --- | --- |
| search — 15 queries | 9.1s | 17% |
| **crawl — 40 pages, per-host politeness** | **33.6s** | **62%** |
| fetch shortlist — 25 pages | 1.1s | 2% |
| adjudicate — one model call | 10.8s | 20% |

Fetching is small only because the evidence cache was warm; adjudication is irreducible.

### The crawl contributed nothing

Of the 25 shortlisted pages, 14 were found by the crawl — and **all 14 were already in the corpus**.
Zero shortlisted pages came from the crawl and not the corpus. **The crawl spent 62% of the corridor
re-deriving a link graph the offline job had already mapped.**

That is not a defect in the crawl. It is what a crawl is *for*, and before a corpus existed it was the
only way to get the map. It is now redundant for any destination that has one.

### Corpus-only resolves the same corridor, and needs no prior proof

Scoring the corpus and shortlisting from it, with **no search and no crawl at all**: 19 of the same 25
pages, and **all three role-filling pages kept** — `entry-requirements-country`, `fees.asp`,
`check-processing-times`.

**And it is not circular.** All three have `first_seen` at 14:30–14:31, from the **offline job**, not
from entry 47's write-back. So this does not need the *corridor* to have been proven, only the
*destination* to have been built — which is the property that makes it apply to a nationality nobody
has ever asked about.

### But consuming the whole corpus scales the wrong way

Scoring all 3,216 entries for one corridor costs **3.6s**, and grows with the corpus. Left alone it
would eventually cost more than the crawl it replaced — the corpus would become the new bottleneck.

So the corpus is used as a **routing index**, not as a candidate list. `score_role_vocabulary` is
corridor-independent, so it can be computed **once at build time**, stored on the entry, and used to
pre-filter before anything corridor-specific runs:

| top-N by stored vocabulary score | corridor scoring | overlap with the real shortlist | role pages |
| --- | --- | --- | --- |
| 100 | 149ms | 20/25 | **2/3 — loses one** |
| 200 | 289ms | 22/25 | 3/3 |
| **400** | **575ms** | **24/25** | **3/3** |
| 3,216 (all) | 3,633ms | 25/25 | 3/3 |

**400 is the chosen bound**: 6× cheaper than scoring everything, keeps every role page with margin, and
is *bounded* — it stays 575ms whether the corpus holds three thousand pages or thirty thousand.
Computing the vocabulary score for all 3,216 costs 95ms and is paid offline.

**400 is calibration, not derivation**, exactly like the shortlist's 25 (entry 40) and the domain cap's
5 (entry 22). One corridor, one destination. It should be re-checked per destination, and 100 is
demonstrably too low, which is the useful half of the table.

### Decided: drop the crawl from the request path, keep search

| | Path | Corridor phase |
| --- | --- | --- |
| Today | search + crawl + fetch + adjudicate | 54.2s |
| **Chosen** | corpus-routed, **no crawl**, search kept | **~21s** |
| Rejected for now | corpus-routed, no crawl, no search | ~13–17s |

**Search is kept, and the reason is a gap that has been measured on one dimension and not the other.**
`corridor_queries` interpolates purpose, nationality and residence. Purpose is now swept offline (four
values, entry 47) and that is why the corpus contains what it does. **Nationality is 198-valued and has
never been checked**: nothing shows whether a nationality-specific query surfaces pages the offline
sweep misses. Dropping search would trade a known 9.1s for an unmeasured recall risk on exactly the
dimension not yet examined — and recall is the thing this whole line of work exists to protect.

Dropping search becomes correct once the superset bar holds across several destinations with
nationality-varied corridors. Then the crawl and search both leave the request path for good.

### How settled this is

**The measurements are solid; the design on top of them is one session's answer and has not been argued
against.** The phase split, the fourteen-of-fourteen redundancy, the top-N table and the non-circularity
check are all reproducible and should be trusted. That the right response is *a flat top-N index plus
dropping the crawl* is a judgement made quickly, on one destination, by whoever also took the
measurements — which is the weakest position from which to design. [TODO.md](TODO.md) item 22 lists
where it is most likely wrong and asks the next session for its own view before building.

What is not open for revision is below, and in the search decision above.

### What must not be lost when the crawl goes

- **A destination with no corpus still crawls.** Removing the crawl is conditional on having a map, not
  a blanket removal; a country nobody has built must behave exactly as it does today.
- **The crawl is where `crawl_failures`, `blocked_urls` and `disallowed_urls` come from**, and those
  feed `inaccessible_domains`, `decision_blocking_urls` and the notes a refusal is made of (entries 27,
  32, 36). Without a crawl those have to come from the shortlist fetch instead, or a corridor will
  quietly stop reporting that an authority refused it — which is the reporting discipline entry 18
  exists to protect, lost as a side effect of an optimisation.
- **`_readable_only` reads crawl state** to drop pages already proved unreadable. With no crawl it has
  no state to read, so the corpus's own `status` is what should stand in.

---

## 47. The candidate set ratchets: corpus ∪ live, pinned by what already worked, fed by write-back
**2026-08-22 · implemented**

Entry 46 left the corpus not a superset of what a corridor finds. The fix is not to make the offline
job exhaustive — **measurement says it cannot be** — but to make the candidate set *monotonic*.

**The property, stated exactly.** For a given corridor the candidate set is **non-decreasing** across
runs. Not identical, which would freeze recall; never smaller, which is what lost Canada its answer on
2026-08-21. Run two sees everything run one saw, plus whatever else turned up.

### Why an offline sweep cannot close the gap, which is the measurement that decided this

Entry 46's gap was blamed on traveller-free queries, and the specific term turned out to be the
**purpose**, not the nationality — four values, not 198. So the obvious fix was to sweep purposes
offline, and that was done: `corpus_queries` gained `corridor_queries`' purpose templates, and a Canada
rebuild went from 30 queries to 70 and from 1,071 entries to 3,130, now with depth genuinely exercised
(1,977 at depth 1, 972 at depth 2, 154 at depth 3).

**It still did not contain the page.** And the reason is the one that settles the architecture: the
exact query that had surfaced `supporting-documents` — `site:canada.ca tourism visa documents required` —
**was re-run, and search did not return it this time.** Search is nondeterministic *at the source*, so
no amount of offline query engineering can guarantee a superset. Only keeping what a live run actually
found can.

Measured against the live run's 24 fetched pages: 18 held, 6 apparently missing, of which **one was an
alias** — `cic.gc.ca/english/visit/visas.asp` sitting in the corpus as `www.cic.gc.ca/...`. Canada's
3,130 stored URLs are 2,996 distinct pages. So `canonical_key` folds scheme, case and a leading `www.`
for *comparison only*; the stored URL is untouched, because that is what gets fetched.

### The three mechanisms

- **Union.** `corpus ∪ live discovery`, seeded where candidates are assembled. Search still runs; the
  corpus supplies what search forgot, and search supplies what the corpus lacks. Trust is applied when
  the corpus is *read*, so a domain later removed from the registry stops being offered without anyone
  rebuilding a corpus and without deleting what was found.
- **Pins.** A page that already filled a role for this corridor keeps its shortlist place regardless of
  ranking. **No new store**: `StoredCorridor.resolved.sources` was already the proven set, used only as
  a whole-answer cache. This is what stops the corpus making the scorer *more* load-bearing — the pool
  grows from ~471 to ~3,000, and entry 40 says a page ranked out is unrecoverable. The age check
  deliberately does not apply: a corridor too old to serve as an answer is still a good hint about which
  pages matter.
- **Write-back.** What a run discovered folds into the corpus, additively. **This is not the fallback
  entry 44 rejects, and the direction is the difference.** That was *deciding a corridor* from a live
  search after a corpus miss, so the answer depended on that day's search. This keeps what a run already
  found, so later runs start from more. It cannot change the current answer — the resolution is made
  before it runs — and widens no trust.

### Measured, end to end

| | |
| --- | --- |
| Before | 18 of 24 fetched pages held; 5 genuine gaps |
| After one corridor run through the new path | **24 of 24 held** |
| Proven entries marked | 3 — the pages that filled roles |
| Offline: a total search failure | **loses zero candidates** (`test_the_candidate_set_never_shrinks_between_runs`) |

### One bug worth keeping, because it made the strongest tier unreachable

`status="proven"` was set only for pages in `resolver.discovered`, which correctly excludes anything the
corpus already held — a page from the corpus is not a discovery. But the common case is that the
*answering* page came from the corpus. A live Canada run wrote 86 entries and **zero** proven ones, so
the one tier that is never evicted could never be entered. Role-filling pages are now written back
whether or not this run discovered them, because proven is about answering, not about finding.

Status is also strictly monotonic now (`_STATUS_RANK`): a single `502` on a later crawl must not demote
a page that has answered a corridor, or its retention tier would drop with it.

### Still open

- **Live discovery has not yet been decayed away.** The corridor still spends its searches every cold
  run. Turning that off for a proven, fresh corridor is where the cost goes to zero and determinism
  becomes total; it is gated on the superset bar holding across more than one destination.
- **Eviction is designed and not built.** 723 of Canada's original 1,071 entries scored zero on role
  vocabulary, so the Noise tier is most of the store. Nothing evicts yet, so the corpus grows.

---

## 46. The corpus is built, and it is not yet a superset of what a corridor finds
**2026-08-22 · implemented, with a measured gap that gates item 19**

Entry 44's store exists: `discovery/corpus.py` holds a country's pages, `discovery/corpus_build.py`
gathers them, and `visa-discover corpus --country CA` runs it. Canada, twice:

| Run | Queries | Seeds | Crawled | New | Held |
| --- | --- | --- | --- | --- | --- |
| `--pages 60`, 36s | 30 | 203 | 355 | 355 | 355 |
| `--pages 200`, 97s | 30 | 203 | 1071 | 716 | **1071** |

The additive merge behaved: all 355 entries from the first build survived the second with `times_seen`
at 2, and nothing was dropped. **`entry-requirements-country.html` sits in the corpus at depth 1** —
the page whose absence refused `canada/GB/GB/tourism` on 2026-08-21 is now durable, which is what this
was built to do.

### What the corpus does differently from a corridor, and why each is deliberate

- **No traveller.** Queries name the destination only, and links are scored with
  `score_role_vocabulary` — extracted from `score_link` rather than copied, so the corridor-independent
  half has one implementation. A corpus guided by one nationality's vocabulary would be a corpus
  quietly built for that nationality.
- **Pages about other countries are kept.** `resolver.py` vetoes them, correctly, because for one
  traveller a page about Brazil is noise. The corpus serves every corridor, so Canada's per-nationality
  pages are exactly what a later India corridor needs. Archived paths and site furniture are still
  rejected: those are not guidance for anybody.
- **It never deletes.** A crawl finding less than last time is ordinary — search moves, a host times
  out — and treating that as a withdrawal would rebuild the failure the corpus exists to prevent.
- **Trust is applied when it is read, not when it is written.** A corpus outlives the registry row that
  built it, so narrowing `authority_domains.yaml` takes effect without anyone rebuilding every corpus,
  and without deleting what was found.
- **A corrupt corpus raises rather than reading as an empty country** — unlike `corridor_store.py`,
  because a corridor that will not parse is safely re-resolved while a corpus is the *candidate
  source*, and treating corruption as "no pages here" would disguise it as a country nobody built.

### The gap, which is the reason this entry is not a success report

**`.../visit-canada/supporting-documents` is absent from a 1,071-entry corpus, and the corridor run
fetched it the same day** — scored 64.0 for `document_checklist`. So the corpus is **not** a superset
of what a corridor finds.

The cause is the thing that makes it corridor-independent — but **the specific diagnosis written here
first was wrong, and the recall log had the answer sitting in it.** This paragraph originally said
`corridor_queries` asks `site:canada.ca Canada visa requirements United Kingdom` and blamed the
*nationality*. Checked 2026-08-22, the page entered the corridor run as a **search seed** from:

```
site:canada.ca tourism visa documents required
```

which is `corridor_queries`' second template, `f"site:{domain} {corridor.purpose} visa documents
required"`. **The discriminating term is the purpose, not the nationality**, and that changes the size
of the problem completely: purpose has **four** values where nationality has 198, so the measured gap is
closable offline with four passes rather than being a Cartesian trap. Whether nationality-specific
phrasing surfaces anything unique is **untested** and must not be assumed either way.

**Two further things this got wrong by inference rather than measurement**, both corrected on the same
day and both worth keeping visible because the habit is the point:

- **Depth was never exercised, so "depth did not close it" claimed more than was tested.** Of Canada's
  1,071 entries, **1,032 sit at depth 1** and only 39 deeper. The build produced **203 seeds** against a
  **200-page budget**, so it spent the whole allowance fetching seeds and barely crawled at all. The
  offline job's headline advantage over the request path — no latency bound, so it can go deeper — is
  not currently being realised. That is the same seed-frontier exhaustion already recorded for the
  corridor crawl under *Smaller things*.
- **Two-thirds of the corpus is noise.** Scored with the corridor-independent `score_role_vocabulary`,
  **723 of 1,071 entries score zero** and only 79 score 20 or above. Retention now has a measured basis
  instead of a guessed one.

The lesson repeats one this file records at least four times already: this was described from reading a
code path when a recall log written for exactly this question was one command away.

**This gates [TODO.md](TODO.md) item 19.** Switching the request path to corpus-only today would trade
variance for a *smaller* candidate set — better determinism, worse coverage, which is not the trade
entry 44 argued for. Two fixes, not exclusive: widen `corpus_queries`, and let a corridor run feed what
it discovered back into the corpus. **The second is not the fallback entry 44 rejects** — that was
*deciding a corridor* on a live search after a corpus miss; this is keeping what a run already found,
which is additive, widens no trust, and cannot change an answer on its own. It still needs arguing in
writing before it is built.

**And this is the second time in two days that building the thing moved the diagnosis.** Entry 44's
motivating number had already weakened when three back-to-back Canada runs produced no variance at all;
now its mechanism turns out to be incomplete in the other direction. Neither kills the corpus — the
answering page *is* durable now, and offline depth is real — but the case for it is narrower than the
entry as first written, and both corrections came from running it rather than reasoning about it.

---

## 45. The corridor command reaches the registry, and the test suite stops being allowed on the network
**2026-08-22 · implemented**

`visa-discover corridor` read `get_destination_registry()` and nothing else, so `--destination canada`
answered *"Unknown destination: canada"* while the API resolved that same corridor perfectly well.
Seven destinations are configured; forty have a registry row. **Every live check of a registry
corridor has therefore been run from a throwaway script** — which is why nobody had a candidate list
until entry 43, and why the flip rate item 17 asks for had not been counted.

It now falls back to `prepare_destination`, and a configured destination still wins where it has
domains, because its hand-written sources carry authorisations the registry knows nothing about —
Singapore's VFS provider is named by an official page, and that naming exists only in
`destinations.yaml`.

**`--runs N` resolves the corridor N times and reports what varied**, which is item 17's counting.
It deliberately does not go through `AutomaticDestinationService`, because that reads the corridor
store, and a stored corridor would answer runs two and three from run one — hiding exactly the thing
being measured.

### What this cost, and it is the finding worth keeping

**Removing that early exit made the test suite perform a live corridor resolution.** The existing
test asserted that `united-states` exits 3; with the fallback in place it went on to resolve — 21
seconds, live Brave searches, live page fetches, and a live model call, because `.env` sits on a
developer machine and `settings` reads it. A 243KB recall record was written for a corridor nobody
asked for.

**Nothing caught it.** `AGENTS.md` has always required that tests never touch the network or an LLM,
and until now that rule was upheld entirely by convention plus the seams — `transport=`, `now=`,
`renderer=`, the fake generators. Convention holds right up until a change adds a code path that has
no seam, and `run_corridor` was one: it built its own resolver from global settings and went
straight to the network. The test "passed" for years by relying on the command bailing out early for
an unrelated reason. When that reason went away the failure surfaced as an exit-code mismatch, and
the network access was invisible in the output.

**So the rule now has teeth**, and both halves matter:

- `tests/conftest.py` refuses `socket.socket.connect` for every test. Patched at the socket rather
  than at `httpx`, because that is the one chokepoint every client, resolver and driver reaches, so
  a new dependency cannot route around it.
- It raises `NetworkAccessDuringTest`, **not** an `OSError`. Several paths under test catch `OSError`
  and `httpx.HTTPError` and turn them into an ordinary "unreachable source" outcome — which is the
  reporting this project cares most about, and which would have swallowed the guard and let the
  offending test pass while describing the block as an authority being down.
- `run_corridor` takes a `resolve=` seam, so the command can be tested without one.

The guard found the offending call on its first run and nothing else in 390 tests, which is the
evidence that the suite was otherwise honest. It also took the suite from 4.0s to 2.7s, all of which
was the one test making real requests.

**The lesson is the one this project keeps relearning, one level over:** a rule that is only a
convention is a rule nobody is checking. Entry 36 found the `robots.txt` parser inert because no
unit test could catch it; this is the same shape — the safeguard was real, the enforcement was not,
and only running the thing showed it.

### Two defects in the variance report, both found by writing its test

Neither would have shown in a live run, and both would have quietly corrupted the number item 17
exists to produce:

- **The run count came from the recall records.** A run whose record could not be read simply
  vanished, so two runs where one write failed described themselves as one run. Entry 43
  *deliberately* swallows a recall-log write error rather than costing a corridor its answer, so
  this was reachable by design. Outcomes now come from the resolutions, which always exist, and
  records only supply candidates; when fewer records than runs survive, the report says so **before**
  the numbers, because otherwise an absence reads as "this run did not find it" rather than "no
  record".
- **A stale record could be read as this run's.** The log is keyed by corridor and keeps only the
  newest run, so a record from last week sits exactly where the second run looks. Comparing run 2
  against last week's run 1 would invent variance that never happened. Records are now accepted only
  when `recorded_at` is at or after the moment that run started.

---

## 44. A country's page corpus is persisted, and search leaves the request path
**2026-08-21 · decided; not implemented**

TODO item 17 asks what a corridor that flips between runs should do. This is the answer: **option 3,
widened.** The set of pages a corridor may consider stops being re-derived from search on every request
and becomes a stored corpus per **country**, populated by a deliberate offline job. Which of those pages
answers *this* traveller is unchanged and stays live.

**The evidence is entry 43's, and it is a measurement rather than an inference.**
`canada/GB/GB/tourism`, twice within an hour, same code, same five domains: refused once, resolved once.
On the resolving run `entry-requirements-country.html` was candidate **15 of 470** at 53.4 — comfortably
inside 25 shortlist places — and arrived **two ways**, as a `site:canada.ca` search seed *and* by crawl at
depth 1 from `check-visa-eta.html`. On the refusing run search did not return it at all. So the page is
not marginal and the scorer is not at fault: **recall flipped, and a resolved corridor is evidence only
that this run of the pipeline worked.** The corridor store then keeps the lucky answer for three weeks,
so a traveller in week one and a traveller in week four get different products from identical code.

> **Measured 2026-08-22, and it weakens the urgency of this entry — recorded here rather than left in
> the TODO, because an entry whose motivating number moved should say so where it is read.** Three
> back-to-back runs of `canada/GB/GB/tourism` with the cache cleared produced **471 candidates and no
> variance whatever**: all three resolved, and `entry-requirements-country.html` arrived every time by
> *both* routes. So the flip rate is "0 of 3 back-to-back", not 0 — the runs were two minutes apart,
> where the observed flip was an hour and the original divergence two days — but it does mean **the
> case for this entry now rests on crawl depth and latency, not on a measured frequency of flipping.**
> The one flip entry 43 caught remains a single observation. TODO item 17 keeps the gapped re-run that
> would settle it.

**This is entry 34's move one level down.** That entry took *who to believe* out of the request path
because domains do not vary by corridor. **Which pages exist** does not vary by corridor either. Only
which one answers a given traveller does:

| | Who to believe (domains) | **Which pages exist (corpus)** | Which page answers *this* traveller |
| --- | --- | --- | --- |
| Corridor-dependent? | No | **No** | Yes |
| How many | ~3–5 per country | **~20–50 per country** | one per role |
| Decided by | a rule, once per country | **a crawl, offline, refreshed** | the model, every corridor |
| Lives in | `config/authority_domains.yaml` (git) | **a store** | computed per request |

`ARCHITECTURE.md` has carried this as a two-column table asserting that URLs *are* corridor-dependent.
That is true of the chosen URL and false of the corpus, and the conflation is why discovery pays search
cost, at request latency, for a question that does not change between travellers.

### Why this is not merely caching what search returns

- **Recall effort moves off the latency budget.** The depth-0 budget exhaustion recorded under *Smaller
  things* — every seed popped before any child, so depth-2 discovery is lost — is a compromise forced by
  a 60-second request. An offline job has no such bound: deeper hops, sitemaps (item 10), far more
  queries per country. Canada's page was reachable at depth 1, and the pages currently lost are deeper.
- **The shortlist stops being a recall gate for most countries.** Entry 40 widened it to 25 because a
  page ranked out is unrecoverable. Choosing 25 from a curated 20–50-page corpus is a different problem
  from choosing 25 of 470 crawl candidates, and the scorer's known faults stop being load-bearing.
- **Cost amortises across nationalities.** One population crawl of Canada serves every corridor into
  Canada. Up to fifteen Brave queries and a two-hop crawl leave the request path entirely.

**Trust is untouched.** A stored URL is still checked against `trusted_domains` and still fetched through
`LiveSourceFetcher`, whose `validate_route` cannot be bypassed — so a corpus entry cannot survive a later
narrowing of the domain registry, and cannot smuggle in a page that would not pass today.

### On a corpus miss: refuse, and flag the country

Entry 38's rule, applied to pages. A country missing from `authority_domains.yaml` is refused, never
bootstrapped live, because falling back "would silently reintroduce the per-request variance the file
exists to remove". A thin or rotted corpus is the same situation: **refuse, name what was missing, and
put the country on the repopulation queue.** Falling back to live search would restore the lottery for
exactly the requests that most need it not to be one, and would do it invisibly.

The refusal must tell three cases apart, because they have different fixes: *no corpus for this country*,
*a corpus exists but no page fills `visa_decision`*, and *stored URLs no longer resolve*. Only the third
means the corpus has rotted.

### The other three options, in item 17's own terms

1. **Re-search on refusal** — rejected. It turns a refusal into "search until something answers", which
   is how a pipeline talks itself into an answer. Item 17 already calls it the worst of the four.
2. **Widen or vary the queries** — rejected. Fifteen queries against five domains is already the cold
   path's cost (known problem 5). More queries is more surface, latency and quota for an unknown gain,
   and it leaves recall a per-request lottery with better odds rather than removing the lottery.
3. **Keep what was found** — **taken, and widened from per corridor to per country.** Strictly stronger
   at identical risk: a page found for `canada/GB/GB/tourism` also serves `canada/IN/IN/business`.
4. **Accept and report it** — rejected as a resting place, though the reporting is kept. Item 17 is right
   that this alone "does nothing for the traveller who got the unlucky run".

### What it does not fix, which matters as much as what it does

1. **A page the offline job never finds is then missed deterministically, for ever.** This trades a coin
   flip for a stable outcome. That is the better failure — a stable gap is visible, diagnosable and
   fixable where a fifty-percent gap is none of those — but it makes the population job's recall the
   whole ballgame, and it is option 3's stated risk in mirror image.
2. **A withdrawn page persists in the corpus.** Bounded by the evidence TTL and by the refresh job
   catching `404`s and off-domain redirects, which is the corpus-rot signal. Bounded is not zero.
3. **Adjudication is still a model call.** Entry 43's resolving run was `decided_by=model`, and a later
   run could judge the same shortlist differently. This removes non-determinism at the **recall** layer
   only and must not be described as doing more. Known problem 10 stands unchanged.

**So the first step is still item 17's own:** run one corridor three times and count, so the flip rate is
a number rather than an anecdote. The recall log makes that cheap, and the number is what says how much
the corpus is worth. It also settles item 17's note about item 3 — **each of the twenty corridors runs
twice, or the write-up says plainly that it did not.** One run cannot tell a corridor that works from one
that works half the time.

### This does not undo entry 43

Entry 43 chose **overwritten per corridor, never accumulated**, and that stands. The corpus is a
different artifact with a different contract, and the two must be built as two:

| | Recall log (entry 43) | Corpus (this entry) |
| --- | --- | --- |
| Keyed by | corridor | **country** |
| Lifetime | overwritten each run | **additive, never pruned by a bad run** |
| Purpose | diagnose the run that just happened | **be the input to the next run** |
| Depended on? | **No** — deleting it costs a question | **Yes** — it is the candidate source |

The row shape is nearly the same: `ConsideredCandidate` already carries the URL, title, `found_by`,
depth, `discovered_from`, the per-role scores, `shortlisted` and `fetched`. But entry 43's *"not evidence
and nothing depends on it"* is load-bearing for that file — it is what makes a diagnostic safe to run
inside a request, and what lets a write failure be swallowed. Inheriting the code must not inherit that
sentence.

### Why the corpus and not precomputed answers

The question that prompted this was whether to precompute visa research per corridor. The arithmetic
refuses it before the safety argument has to:

| Design | Records | Refresh cost per cycle | Verdict |
| --- | --- | --- | --- |
| `destination × nationality × residence × purpose` | 38.8 billion | — | absurd |
| Residence reduced to post selection | 196,020 | ~2.9M searches, ~392k model calls | categorically impossible |
| Top ~200 corridors precomputed | 200 | ~3,000 searches, ~400 model calls | affordable, covers only the head |
| **Page corpus per country** | **~4,000–10,000 URLs** | **conditional GETs, mostly `304`** | **this entry** |
| Decision rows per nationality | ~157k rows, ~30MB | ~600 model calls to populate once | affordable, and the riskiest layer |

Storage is never the constraint — cleaned text is capped at 50,000 characters. **Search quota and model
calls are**, and both scale with pages read rather than corridors served. That is what makes a corpus
work where corridor precomputation cannot: one crawl of Canada serves every nationality asking about
Canada.

**A decision-row table is deliberately excluded for now, and its cheapness is the reason to be careful.**
Canada's page *is* a table of roughly 200 nationalities, so a few hundred model calls would populate the
world. But that is a bulk-inference surface, and this project's defining failure (entry 15) is a
confident wrong answer. A wrong pick is currently ephemeral and per-request; a wrong row would sit in a
store for weeks and be served with a citation. Entry 42 proved that a nationality's answer can fall
outside the excerpt **silently**. If it is ever built: a nationality the page did not name yields **no
row**, never a false one, and absence must be distinguishable from "no visa needed". It layers onto the
corpus without rework, so nothing is lost by waiting for item 3's numbers.

**A personalised plan is never stored as truth.** It is a rendering of the corpus and its snapshots for
one traveller, and the profile fields that would explode its key space — city, residence status, permit
expiry — change only prose. What may be stored is an audit copy of what a traveller was told and when,
which is a different artifact with a different purpose.

### What a store must not lose

These are already right in the file stores and are easy to lose in a migration:

- **A row records when the evidence was retrieved, never when the row was written.** `_serve_stale`
  keeps the original `fetched_at` and a `304` moves it, because a validator match proves currency. A
  schema that collapses the two starts lying about how current its guidance is (entry 4).
- **The stale ceiling still refuses.** A stored page past `source_maximum_stale_hours` is refused rather
  than served, exactly as today.
- **A hash change marks a source; it never auto-swaps a role-bearing one.** Auto-rediscovery of a
  checklist is the wrong-checklist failure with the human removed (item 14).
- **No effective dates and no temporal rules model.** `published_date_in_path` reports rather than vetoes
  (known problem 12), and inferring effective dates from prose is the class of confident guess this
  project refuses everywhere else.

### Three provenance gaps found while tracing this, and the store is not the fix for any of them

The brief asked whether the system can answer *"why did you say an Indian passport holder needs this
visa?"* with a traceable source. It can name the page and when it was read, and no more:

- **`SourceReference.supporting_excerpt` is never populated on the live path.** It is written only by
  `FixtureSourceFetcher` from the Singapore manifest; `LiveSourceFetcher._build` does not set it and the
  extractor passes references through unchanged. **Every live plan cites a URL with no supporting
  quote.**
- **`content_hash` never reaches `VisaPlan`.** It exists on `FetchedSource`, but `SourceReference` has no
  hash field, so a plan cannot be tied to the exact text it was read from.
- **`decided_by`, `score` and `signals` never leave `ResolvedCorridor`.** Why a page was chosen for a
  role is on disk and invisible in the response.

All three are schema and plumbing, they are worth fixing whether or not the corpus is built, and saying
so matters: **provenance is not an argument for the store**, and folding it in would let a large change
borrow justification from a small one. Known problems 20, 21 and 22.

### Rejected

- **Precomputing answers per corridor**, at any width — the arithmetic above, before any safety argument.
- **A `visa_rule` decision table now** — the riskiest layer, and item 3 is what should decide it.
- **Storing plans as truth** — a plan is a rendering, and its personalisation is what explodes the keys.
- **Falling back to live search on a corpus miss** — silently reintroduces the variance the corpus exists
  to remove, on exactly the corridors that need it most (entry 38).
- **Effective-date modelling**, and letting a hash change auto-swap a role-bearing source.
- **Moving `authority_domains.yaml` into the store** — entry 34's whole argument is that the riskiest
  automated decision in the system should be a reviewable diff. It stays in git.
- **Collapsing the corpus into `recall_log.py`** — same rows, opposite contract; see above.

---

## 43. Write down what a corridor considered, because "ranked out" and "never found" had looked identical
**2026-08-21 · implemented**

`discovery/recall_log.py` writes one JSON record per corridor, on every run including a refusal,
holding every candidate the corridor considered with its score, whether it was shortlisted, and whether
it was fetched — plus the queries, the seeds, and each unreadable URL with its reason. It is on by
default in `build_resolver`, so the command and the API both produce it. Nothing reads it back.

**Why it earned a place in the request path.** Twice now a corridor has refused for a reason that was
accurate about what the decider was shown, and twice the next question — *was the page that would have
answered it ranked out, or never found?* — could not be answered from anything the run left behind. The
two have different fixes: one is scoring, one is search or crawl. On 2026-08-21 `canada/GB/GB/tourism`
refused with the answering page absent from its 24 candidates, and the only reason anybody knew the page
existed was a cache file from two days earlier.

**It answered the question on the first run, which is the argument for it.** Immediately after it landed,
the same corridor, cold:

| | |
| --- | --- |
| Candidates considered | **470** |
| Shortlisted / fetched | 25 / 24 |
| `entry-requirements-country.html` | rank **15**, score 53.4 for `visa_decision`, shortlisted, fetched |
| How it arrived | a `site:canada.ca` search seed, and again by crawl at depth 1 from `check-visa-eta.html` |
| Outcome | **resolved** — `visa_decision` and `general_entry` filled by that page, `decided_by=model` |

So the page is not a marginal candidate: it is fifteenth of 470 and comfortably inside 25 places. It was
simply **not returned at all** on the previous run an hour earlier, from the same fifteen queries against
the same five domains. Known problem 19 is now a measurement rather than an inference.

**And it is the first live confirmation of entry 42.** The model's reason quotes the page: *"the page
lists 'British citizen' among eTA-required nationalities and says that, when travelling by air, they need
an eTA"*. That sentence sits at offset 8,597 of 16,465. **A flat 6,000-character excerpt could not have
shown it**, which is arithmetic rather than a claim about the model. The same corridor, the same page, the
same shortlist, and the excerpt is the difference between a filled role and a refusal.

**Design notes, each of which is the thing that would otherwise be got wrong.**

- **A refusal must be logged.** Refusals are the runs worth reading, and they are precisely the ones that
  return early — before candidates exist, or before a shortlist does. So the record is filled by a
  mutable trace as the run proceeds and written in a `finally`, not assembled from a return value.
- **A diagnostic may never cost an answer.** An `OSError` writing the log is swallowed. Failing a corridor
  because a log file could not be written would trade an answer for a note about an answer, and the
  failure is not silent in practice: the file is not there when someone looks.
- **Shortlisted and fetched are recorded apart.** "Shortlisted but unreadable" is a third answer to *why
  was this page not used*, and merging the two flags hides it.
- **Overwritten per corridor, never accumulated.** The question is almost always about the run that just
  happened. Comparing two runs — which is how the Canada variance was found — means deliberately keeping
  a copy, rather than a directory that grows for every request forever.
- **It is not evidence and nothing depends on it.** Deleting `var/recall/` costs a question, never an
  answer. That is what makes it safe to have in the request path at all.

**What it does not do.** It does not record *why* search returned what it did, so it cannot explain the
variance it exposes — only prove it happened and to which page. And a record exists only for runs made
after this landed, so the 2026-08-21 refusal stays diagnosed by inference.

---

## 42. The excerpt is the second recall gate, and a flat 6,000 made truncation the decider
**2026-08-21 · implemented**

`DEFAULT_EXCERPT_CHARACTERS` moves from 6,000 to 20,000, and stops being a flat head-of-page slice: the
adjudicator now sees the head of each candidate **plus a 3,000-character window centred on every later
mention of the traveller's own nationality or residence**, with what was left out marked `[…]`.

**This is entry 40 one layer down.** The shortlist decided which pages the model may see; the excerpt
decides which *part* of them it may see, and the same asymmetry governs both — text the model never sees
is text nothing downstream can recover. Entry 40 was applied to the shortlist and the comment on the
constant below it was left saying, correctly, that ten pages of prose "would push the call past any
sensible input bound". Nobody asked whether 6,000 characters was where the answers were.

**What it cost, measured on `canada/GB/GB/tourism`.** The corridor ranked the right page first, fetched
it, and refused. `entry-requirements-country.html` is 16,465 characters; it lists visa-required countries
alphabetically, starts the eTA list only at offset 8,517, and answers a British traveller at 8,597:
*"You need an eTA and a valid passport to board your flight to Canada … you **don't** need a visitor
visa"*, with "British citizen" naming them at 8,858. The excerpt ended at 6,000, mid-alphabet at
"Morocco". The adjudicator then refused `visa_decision` for a reason that was accurate about what it had
been given — *"No candidate shows the result for a GB passport holder"* — and the corridor refused.

**The defect is worse than "Canada refuses", and this is the sentence to keep: whether a corridor
resolved depended on where the traveller's nationality fell in an alphabet.** On that one page, India at
5,325 was inside the window and every visa-exempt nationality — Australia 8,815, a British citizen 8,858,
Japan 9,647, Singapore 9,856 — was outside it. That also explains entry 40's "Canada: every role filled"
at 25 places: that measurement is consistent with an Indian passport and does not generalise. Nothing in
the output said so, which is the part that should be uncomfortable.

**Why anchoring and not only widening.** A flat number is still a fixed offset, and a country-list page
puts the answer wherever the alphabet puts it. So the window follows the traveller: the head first,
because it carries the title and what the page is, then each later mention of their own country words.
The window is **centred** on the mention rather than started at it — Canada's answering sentence sits 261
characters *before* "British citizen", so a forward-only window would have cut exactly the sentence being
looked for. Budget the anchors do not spend is read straight on from the head, so a page that never names
the traveller is read *further into*, never less of, than the flat slice this replaces.

**Honest accounting of what each half buys.** Measured over the 27 cached `canada.ca`/`gc.ca` pages in
`var/cache`, packet text goes from 84,704 characters to 153,862 — about +17k tokens on one call. Almost
all of that is the raise: a flat 20,000 costs 153,852 on the same pages, because 19 of the 27 are shorter
than the head and only 2 exceed the budget at all. **Anchoring is not what makes this affordable.** It
changes nothing for a page under the budget and everything for one over it: on the 50,000-character
visitor-visa PDF, a US traveller's windows land at 19,452 and 24,449, and the second is text a flat
20,000 cuts. The two 50,000-character pages are the whole population where the two rules differ today,
and they are also where a further raise would get expensive.

**Two details that are not cosmetic.**

*The omission is marked.* `[…]` is written wherever text was dropped, including at the end, and rule 12
of the prompt tells the model what it means. Without it, a cut list reads as a finished list — which is
precisely how Canada's visa-required list, stopping at "Morocco", could be read as complete. Marking it
is the same principle as every other reason this project reports: what is shown has to be true of what
was seen.

*Short country words are matched in upper case only.* "us" is how the United States is written on a
government page and also an ordinary English pronoun; matched case-insensitively it anchored 34 windows
in one 50,000-character Canadian guide, none of them about an American traveller. "US", "UK" and "UAE"
in upper case are the country; longer words are matched either way. Word boundaries do the rest — an
unbounded "uk" matches inside "Ukraine".

**What this does not fix.** Raising the excerpt cannot help a page that never contained the answer.
`ircc.canada.ca/english/visit/visas.asp` — the natural decision page, and what search returns first —
yields 1,144 characters saying the client needs JavaScript, and its answer is behind a wizard; that is
item 5's problem, not this one. Canada resolves because a *different* page happens to publish the list
statically.

**Run live the same day, on the corridor it was built for, and it did not resolve.** Cold, with
`var/cache/` and `var/corridors/` cleared: `canada/GB/GB/tourism` refuses again, in 69s, and **the reason
is not the excerpt**. Of 24 candidates fetched, `entry-requirements-country.html` — the page holding the
answer, and the page the 2026-08-19 replay was performed on — **is not among them**. It was not fetched
at all. The excerpt cannot widen a page nobody retrieved.

What the run does establish:

- **The change shipped and is doing what it says.** Three candidates exceed the old 6,000 — 14,765,
  11,258 and 8,186 characters — so 16,209 more characters of page text (~+4k tokens) reached the model
  than a flat slice would have allowed, on a packet of 84,648. No candidate needed a `[…]`, because every
  one of them fits inside 20,000; the anchoring changed nothing here, exactly as the cost note predicts.
- **The adjudicator's refusal is now about a wizard, not a truncation.** Its reason: *"No candidate gives
  a result for a GB passport holder. The visa/eTA checker extracts only show 'Your result is loading'"* —
  which is item 5's problem, named by the model itself.
- **The candidate set for one corridor varies between runs**, and that is the finding worth carrying:
  the same corridor, from the same five trusted domains, retrieved the answering page on 2026-08-19 and
  did not on 2026-08-21. Whether it was discovered and ranked out of the 25 shortlist places or never
  discovered was not instrumented. Recall upstream of the excerpt is now the binding constraint on this
  corridor, and entry 40's asymmetry argument points at it as squarely as it pointed here.

**Then it was run once more, after entry 43 landed, and Canada resolved.** Same corridor, same day, same
five domains: this time search returned `entry-requirements-country.html` and the model filled
`visa_decision` from it, quoting the sentence at offset 8,597 — **which a flat 6,000-character excerpt
could not have shown**. That is this entry confirmed live, and it took a corridor that flips between runs
to show it. Both results stand: the excerpt was a real gate and is now open; whether the page arrives at
all is a separate gate that is still shaking. See entry 43 and known problem 19.

The remaining six verified corridors have still not been re-run; that is TODO item 15.

---

## 41. A challenge is not a refusal: answer it as an honest browser, and honour every `robots.txt`
**2026-08-19 · decided; not implemented**

Entry 18 opens by predicting that "a headless Chromium would very likely pass that check" and then
forbids trying. **Measured on 2026-08-19, the prediction is right and the premise underneath it was
wrong.** `france-visas.gouv.fr` is not refusing this program. It is challenging it, and the two are
different acts by different parties.

**What the `403` actually is.** Requesting `/en/demande-de-visa` with the client the app really uses
returns:

```
server: cloudflare
cf-mitigated: challenge
server-timing: chlray;desc="a2dabaff0fda5548"
set-cookie: __cf_bm=...
accept-ch / critical-ch: Sec-CH-UA-Bitness, Sec-CH-UA-Arch, Sec-CH-UA-Platform-Version, ...
```

with `cf_chl_opt` and the `/cdn-cgi/challenge-platform/` loader in the body, whose visible text reads
*"One moment please … Checking if the site connection is secure … Enable JavaScript and cookies to
continue"*, wrapped in a French page that calls itself *"Erreur 503 — le serveur que vous essayez
d'atteindre semble injoignable"* and advises trying again in a few minutes. `cf-mitigated: challenge`
is Cloudflare's own label for *prove you are a browser*. The `403` is the transport for a challenge,
not an authorisation decision, and the page contradicts itself about which status it even is.

**And `/robots.txt` is behind the same challenge**, which settles the question of whose decision this
is. There is no stated policy, because nothing published a policy — a WAF default sits in front of the
whole host. Entry 36's `robots.txt` work already measured this and known problem 11 already said it;
what neither did was draw the conclusion about the `403` itself.

**The distinction that decides it: entry 18's test is deception, not status codes.** A response that
says *"enable JavaScript and cookies to continue"* is a **capability test**. Answering it by running
the page's own JavaScript, in a real browser, under our own name, misrepresents nothing to anybody.
Measured: the project's own `PlaywrightPageRenderer`, announcing
`VisaResearchAgent/0.1 (personal visa research; contact repository owner)` — our identity, unchanged,
nothing spoofed — reads the page.

| | Result |
| --- | --- |
| `final_url` | `https://france-visas.gouv.fr/en/demande-de-visa`, unchanged |
| HTML | 221,476 bytes; 2,277 visible characters |
| Challenge markers in the result | none |
| `blocked_hosts` | `[]` — the render trust gate had to allow nothing new |
| Cost | ~7s per page |

That last row matters more than it looks: Cloudflare's challenge scripts are served **same-origin**
under `/cdn-cgi/challenge-platform/`, so the rule that aborts every request to an unapproved host
(entry 13) neither has to bend nor accidentally breaks the challenge.

**Decided, and it amends entry 18 rather than repealing it.**

- A challenge is **its own outcome**, not `blocked`. `blocked` means an authority refused us; that is
  a claim about the authority, and it is false here.
- A challenge **may be answered by the renderer**, under our own user agent. This is the one thing
  entry 18 named and forbade, and it is now allowed *because* it was measured to require no
  deception — not because the coverage was tempting.
- A challenge **may never resolve a corridor.** Entry 32's causality bound applies with more force
  here, not less: a page nobody was allowed to read is at least a page an authority withheld, whereas
  a challenge is a page nobody asked the authority about. This is also why France's current
  resolution is wrong — it resolves on an incidental challenge that happened to score for
  `visa_decision`, which flips between runs.
- **`robots.txt` is read and obeyed for every host, unchanged (entry 36), and it outranks all of the
  above.** A `Disallow`ed path is not fetched, challenge or no challenge; a policy that cannot be read
  is still reported as unread rather than as permission; a `Disallow` still may not resolve a corridor.
  Answering a challenge where no policy exists and ignoring a policy where one does would be the same
  mistake twice.

**What stays forbidden, in full.** No user-agent spoofing. No retrying past a `429`. No answering a
`401`, or a bare `403` carrying no challenge markers — those are refusals, and entry 18 governs them
completely. **The line moves from "which status came back" to "did the authority state anything".**

**Entry 18's cost statement is amended.** *"France is unservable"* was true of an anonymous HTTP
client. It was never a property of the principle, which is what entry 35 said and this measures.

**What it does not buy, measured, so that nobody expects it.** Answering the challenge yields the
pages; the answers are not on them.

| Page | What is actually there |
| --- | --- |
| `/en/demande-de-visa` | Three generic items — passport, "photocopies according to your situation", 2 ICAO photos — and a button into the wizard |
| `/en/assistant-visa` | "Step 1 of 4" with a nationality dropdown: the decision is behind form input |
| `/en/visa-de-court-sejour` | Defines what a short-stay visa is; never says who needs one |
| `www.france-visas.gouv.fr/en/web/france-visas/india` | **404** — and it was the top-scoring France-Visas candidate at 74.4 |

So the challenge had also been masking dead URLs, and the corridor was spending fetch places on them.
Getting a *corridor* checklist out of France needs the wizard, which is form input and collides with
the permanent scope rule on form filling. **That is a separate decision and is not taken here.**

**One thing shipping today is now known to be false.** The interface tells a traveller
*"<authority> does not permit automated retrieval"* for any `blocked` failure with a URL. For a
challenge that sentence is untrue of what was seen. Correcting it is part of the implementation, not a
separate nicety — see [TODO.md](TODO.md) item 5.

---

## 40. The shortlist is a recall budget, and ten places made the heuristic the real decider
**2026-08-18 · implemented**

`DEFAULT_SHORTLIST_SIZE` moves from 10 to 25. That is the whole change, and it bought more than every
scoring rule in `scoring.py`.

**The reasoning that kept it at ten was a category error.** The pipeline is: a heuristic scorer picks the
shortlist, and a model adjudicates roles from it. The scorer was being tuned as though it decided
something. It does not — it decides **what the model is allowed to see**. So its two errors are not
symmetric. A page ranked *in* wrongly costs one excerpt. A page ranked *out* is one nothing downstream
can recover: not the adjudicator, not the retry, not the traveller. At ten places, the heuristic was the
effective decider for every corridor whose right page sat eleventh — and known problem 9 had said exactly
this ("a page it ranks out of the ten fetch places is one the model never sees") without the conclusion
being drawn.

**Measured live, changing only this number:**

| Corridor | 10 places | 25 places |
| --- | --- | --- |
| Canada | refuses — no visa decision | **every role filled** |
| Japan | no visa decision | **every role filled**, same checklist |
| Netherlands | no checklist | checklist found (its decision is a JavaScript tool; see entry 39) |
| Sweden | two roles unfilled | unchanged — it fails for another reason |

Two corridors that refused now resolve completely. Nothing regressed.

**And it is close to free**, which is the part that was assumed rather than checked. Fetching is
concurrent, so cost scales with batches rather than pages: Japan's corridor took 44.5s at ten and 39.3s
at twenty-five, Canada's 45.2s and 41.7s — within noise both times, with no systematic penalty in either
direction. Adjudication input roughly doubles to about 19k tokens, which is small for one call.

**What this does not fix, and must not be read as fixing.** Sweden did not move. The `/india`-over-
`/united-kingdom` weighting from entry 39 is still wrong. Scoring is still English-only (known problem
13). The argument here is narrower: **the scorer did not need to be more accurate, it needed to stop
being a bottleneck**, and that was true before any of its rules were examined.

**Rejected for now: replacing the scorer** with an embedding or model-based ranker. It is the component
that does *not* need to be reliable — its failures cost recall, which fails safe into a refusal, because
the trust rules and the adjudicator sit downstream. Spending a rewrite on the safe component while a
constant was the binding constraint would have been the wrong order. If it returns, the case should be
the multilingual gap rather than the ranking.

**A test pins the width**, because narrowing it again would be invisible: corridors do not fail loudly,
they quietly refuse, and the page that would have answered is never fetched to be missed.

---

## 39. A person may override the trust rule in committed data, and doing it showed the rule was not the only thing wrong
**2026-08-18 · implemented for 12 countries**

Entry 33 said a government using no hostname marker "has to be named in reviewed data instead" and left
that hatch unbuilt. `CountryAuthorities.reviewed` is it: a map of domain to **the evidence that justified
it**, ahead of the machine-proposed list and counting against the same cap, so a correction displaces the
weakest automatic domain rather than widening the set.

Three properties make it safe enough to bypass the trust rule with:

* **The evidence is required, and validated non-empty.** A reviewed domain skips the rule that keeps
  commercial agencies out, so a reason nobody can check is a domain nobody has verified. The committed
  file is asserted against this in the test suite, not just the fixtures.
* **A regeneration cannot silently undo it.** `visa-discover registry --rebuild` replaces `trusted` and
  `unconfirmable` — search output, meant to be replaced — and carries `reviewed` through untouched. This
  was the one way that command could have done real damage: every correction reverted, with plans still
  refusing, and nothing in the output saying so.
* **The evidence is a claim about who controls the domain, made by something that is not the page.**
  Each of the twelve was confirmed by a Wikidata reverse lookup — the domain is the `official website`
  (P856) of an entity whose `country` (P17) is that country. That is the same question
  `belongs_to_destination` asks and the one `looks_governmental` cannot answer for these governments.
  Four domains the lookup could not confirm were **left alone**: `gv.at`, `swiss-visa.ch`, `mvep.hr`,
  `nyidanmark.dk`. Austria therefore still refuses, and that is the correct output.

**Rejected: a live Wikidata lookup in the trust path.** Wikidata is user-editable, so a claim that a
domain belongs to a government can be edited by anyone. As input to an offline file that a person reviews
as a diff, a bad edit is visible before it can reach a traveller; as a request-time authority it would be
an unreviewed third party deciding what this program trusts. Entry 34 is what makes the first version
acceptable. **Also rejected: asking a model.** It would likely classify more of these correctly, and it
produces no entity, no revision history and nothing to diff — in a system whose entire differentiator is
that every claim traces to something checkable.

### What running it found, and it corrects entry 38 and the reasoning behind this change

The diagnosis going in was that the domain classifier was the binding constraint: bootstrap proposes the
right domain for every failing country, and only the hostname regex throws it away. That is true, and it
is **not sufficient**. Measured before and after, three countries:

| | Before | After |
| --- | --- | --- |
| Sweden | refused with **nothing fetched** — no domain confirmed at all | reads `migrationsverket.se`; `application_route` and `general_entry` filled |
| Canada | refused: visa decision **and** checklist unfound | refused: checklist **found**, decision still unfound |
| Netherlands | refused | refused, unchanged |

So the corrections are real — Sweden went from fetching nothing to reading its actual immigration agency —
and **not one of the three resolves end to end.** The binding constraint has moved rather than lifted: it
is no longer "we cannot tell which domain is this government" but "we cannot confirm the visa decision on
pages we can now read."

### Following one of them all the way down, because "still refuses" is not a diagnosis

The Netherlands did not move, so it was traced page by page. Four distinct causes, and only the first
was the domain:

1. **The reviewed domain was right and incomplete.** `government.nl` is genuinely the Dutch government,
   but the Netherlands delegates visa content to `netherlandsworldwide.nl` — which the trust rule had
   left in `unconfirmable` and which the Wikidata lookup could not confirm either. It is now reviewed on
   **stronger** evidence than any other row: `government.nl` itself states that the traveller can see on
   Netherlands Worldwide whether they need a visa. That is the destination's own government vouching for
   the domain, which beats a third-party lookup.
2. **The page that ranked first was a signpost.** `check-visa-netherlands` scored 60.4, top of the
   shortlist, returned `200`, and yielded **250 readable characters against the 400 floor**. Correctly
   refused — it genuinely contains no guidance, only two links.
3. **With the delegated domain added, the right pages appear** — including
   `checklist-schengen-visa-tourism/india` at 123.0 and, separately,
   `checklist-schengen-visa-tourism/united-kingdom`, both readable and around 7,700 characters. **The
   scorer ranks the wrong one higher: 113.0 for `/india` against 73.0 for `/united-kingdom`.** For a
   consular checklist the **post** governs, not the passport: an Indian national applying from Great
   Britain applies at the Dutch mission in the UK. So the wrong-post page took the slot, and the
   adjudicator — correctly applying that rule — declined to name it. **The adjudicator was right and the
   scorer is wrong**, which is the reverse of how it first read.
4. **The visa decision is not published as a page at all.** `entering-without-visa` redirects to a
   nine-question JavaScript filter tool. No static Dutch page says an Indian national needs a Schengen
   visa. Refusing that role is correct and no amount of ranking fixes it.

So the binding constraint is not one thing. It is a scorer that weights nationality above post, and a
government that publishes its decision only as an interactive tool.

**And entry 38 was wrong about the shape of the failure.** It claimed a wrong trusted set makes a corridor
*resolve* against domains that cannot hold the answer — the failure this project treats as worse than
refusing. Run, they **refuse**. The refusal discipline held throughout; what a wrong trusted set costs is
coverage, not correctness. That claim was written from reading the code path, which is now the fifth time
in two days that habit has produced a false line in these files.

---

## 38. The trusted-domain registry is generated offline and committed, and reviewing it found what running it could not
**2026-08-18 · implemented for 40 countries; the remaining 158 are unbuilt**

Entry 34, built. `bootstrap_destination` no longer runs in a request. `discovery/registry.py` reads
`config/authority_domains.yaml`; `discovery/registry_build.py` and `visa-discover registry` generate it.
`auto_trusted_domains` — the whole of the trust rule — is unchanged and still the only thing deciding a
domain. **What moved is when it runs**, from every cold request to once per country.

Verified live: resolving New Zealand, a destination nobody had configured, spent **0 searches** in the
service where it previously spent 4, and produced a visa decision, a document checklist, an application
route and a general-entry page from committed domains alone.

**A missing row refuses rather than falling back to a live bootstrap.** Falling back would reintroduce the
per-request variance this entry exists to remove, silently, on exactly the countries nobody had reviewed.
The refusal names the command that fixes it.

**A country whose searches errored is left out of the file entirely**, never written with an empty
`trusted`. Those two mean different things — "the rule confirmed nothing for Germany" is a finding a
reviewer must act on, and "we never got to ask" is not — and the build is resumable precisely so the
second can be retried without repaying for the first.

### What the review found, which is the point of committing it

Forty countries built, 35 confirmed, 5 refused. Entry 34 argued that committing the rule's output makes
the riskiest automated decision in the system auditable. It does, and reading the file surfaced three
things no test and no corridor run had:

**The five refusals are entry 33's known failure, and now name their own fix.** `AT`, `BE`, `DE`, `DK`,
`SE` — with `gv.at`, `ibz.be`, `auswaertiges-amt.de`, `nyidanmark.dk` and `migrationsverket.se` sitting in
`unconfirmable`. `gv.at` in particular is a marker correction `CLAUDE.md` already blesses.

**Twelve more countries are confirmed *and wrong*, which is worse and was invisible before.** Entry 33
predicted this second failure and could not measure it; the file shows it plainly:

| Country | Trusted | Actually holds the visa guidance |
| --- | --- | --- |
| Netherlands | `business.gov.nl` — the business portal | `government.nl`, and IND, both unconfirmable |
| Italy | `integrazionemigranti.gov.it`, `mise.gov.it` | `esteri.it`, unconfirmable |
| Canada | five `gc.ca` domains | `canada.ca`, unconfirmable — IRCC moved there |
| Portugal | three ministry domains | `sef.pt`, unconfirmable |
| Ireland | `gov.ie`, `inis.gov.ie` | `irishimmigration.ie`, unconfirmable |

~~These corridors do not refuse. They resolve, against domains that cannot hold the answer.~~
**Wrong, and corrected in entry 39 by running it.** Measured on the Netherlands and Canada: a wrong
trusted set makes a corridor **refuse**, it does not make it answer. The refusal discipline held. The
cost of this failure is coverage, not wrong guidance — which is a materially smaller problem than the
sentence above claimed, and the sentence was written from reading the code rather than from output.

**A third finding nobody had predicted: the cap spends its slots on the wrong parts of a government.**
India's five include `indianembassyusa.gov.in` and `cgichicago.gov.in` — United States missions, occupying
two of five slots for *every* corridor including India-from-GB. South Korea's include `goesan.go.kr`, a
county. Spain's put `administracionespublicas.gob.es` and `lamoncloa.gob.es`, the prime minister's office,
ahead of `exteriores.gob.es`. Entry 22 predicted the cap would bite and assumed the ordering was sound;
`_trust_priority` falls back to **alphabetical** among domains with no hostname hint, and for a large
government that is the same as arbitrary. This is now item 2's problem, and it is a data-and-ordering
problem rather than the regex change entry 33 forbade.

**Forty rather than 198, deliberately.** 198 countries is 792 searches; the top forty by traveller volume
is 160 and answers the question the file was built to answer. The remaining 158 refuse with the message
naming `visa-discover registry`, and `--only` builds any subset. Building the rest is quota, not work.

---

## 37. A per-run allowance may not be counted on an object that outlives the run
**2026-08-18 · implemented**

Three render budgets described themselves as per-run — *"Retrieval's own allowance"*, *"Discovery's own
allowance"*, *"a last-resort ceiling on one browser's lifetime"* — and two of them were counted on objects
that outlive every run. Found while implementing entry 36, which hit the same singleton lifetime and solved
it with a TTL.

**What it actually did.** `LiveSourceFetcher.renders` starts at zero in `__init__` and was never reset,
and the fetcher is reached through `get_visa_plan_service`, an `lru_cache(maxsize=1)`. So `maximum_source_renders`
(5) was a budget for the *server process*, not for a request. Confirmed by running it rather than by reading
it: with the allowance set to 2, requests 3 and 4 never consulted the renderer at all. Past that point every
client-rendered page — Vietnam's e-visa portal, the pages rendering exists for — came back
`"the page returned too little readable text to trust"`, for as long as the process stayed up.

**That failure is a false reason, which is why it is a defect and not merely a limit.** The page had not
been read. Saying it returned too little text states something about what was seen, when what happened was
that we declined to look. This is the same fault as entry 33's `withheld_domains` wording and entry 36's
*"does not permit"* — a sentence describing a source nobody consulted.

**The fix is a value, not a reset.** `RenderBudget` is built inside `fetch()` and passed down to `_render`.
Resetting `self.renders = 0` on entry would look equivalent and is not: a server answers requests
concurrently, so two overlapping runs would each clear the other's count and both could render past the
limit. Held as a per-call value, no long-lived object carries a spent count. A test pins the concurrent
case, because it is the one a reset would silently pass in a single-threaded test and fail in production.

**`PlaywrightPageRenderer`'s own count is deleted rather than fixed.** It was `maximum_source_renders +
maximum_crawl_renders` = 17, documented as a last-resort ceiling on one browser's lifetime — but `aclose()`
is only ever called by the CLI, so on the API path that browser's lifetime *is* the server's. It bound
first and hardest: `dependencies.py` builds one renderer and closes over it in the resolver factory, so it
survived even the per-corridor fetchers, and after 17 rendered pages the whole installation stopped
rendering. A guard whose only observable effect is to switch a feature off silently is not a guard. Counting
belongs to whoever knows where a run begins, and both callers now bound it: retrieval per `fetch()`,
discovery per corridor. The trust check inside `render()` stays exactly where it is — that one is
belt-and-braces for *trust*, which is a different question.

**`CrawlFetcher.renders` was reported as having the same defect and does not.** It holds a spent count on
the instance, but `AutomaticDestinationService` holds a resolver **factory**, not a resolver, and calls it
per corridor — so an instance never outlives one run, and sharing the allowance across that run's many
`fetch_html` calls is the intent. Left alone, with the lifetime argument written next to the counter and a
test pinning that the factory is still called per corridor, since that invariant is now load-bearing for
this class and nothing had been asserting it.

**The general rule, worth stating because it is not visible at the definition site:** in this codebase a
counter, cache or accumulator on a service reached through `dependencies.py` is process-lifetime unless
something makes it otherwise. Entry 36 needed a TTL for it; this needed a per-call value. Check the caller,
and prefer running it to reading it — reading is what let all three of these stand.

The rest of that path was swept for the same shape while fixing this, and nothing else was found: after
the change the only zero-initialised counter on any object reachable from `dependencies.py` is
`RenderBudget.spent`, which is per-call by construction. The other long-lived stores are file-backed with
an age check (`FileSourceCache`, `FileCorridorStore`) or expire (`RobotsCache`).

---

## 36. `robots.txt` is read and obeyed, and a page skipped for it is its own outcome
**2026-08-18 · implemented**

The first of entry 35's three legitimacy steps, and the one owed regardless of what it buys. Until now
nothing here fetched `robots.txt` while the same code computed a per-host politeness delay for the same
hosts — a guess at what a site tolerates, running alongside a refusal to read the site saying it.

`RobotsCache` (`research/robots.py`) fetches one policy per **origin**, re-read after 24 hours, and both
fetchers consult it before every request: `discovery/crawl.py` before each crawled page, `research/live_sources.py` before each
source and before each meta-refresh forward.

**Matching is written here, and `urllib.robotparser` was tried first and rejected.** The original
reasoning — stdlib, better tested, and its shortfall "errs toward fetching less" — was wrong, and was
written from reading the module rather than running it. `urllib` matches with `filename.startswith(path)`
and supports **neither `*` nor `$`**. Measured against real authorities on 2026-08-18: every rule
`www.gov.uk` publishes is a wildcard, so a stdlib client obeys **none** of them, and `www.canada.ca` has
fourteen more it walks straight past. A parser that silently makes this fetch *more* than a site permits
is the one failure this module cannot have. The matcher now implements RFC 9309 §2.2.2–2.2.3 directly:
`*` matches any run, a trailing `$` anchors the path end, the longest pattern wins, `Allow` beats
`Disallow` at equal length, and a group is chosen by exact product token falling back to `*` — not by
`urllib`'s substring test, under which a record aimed at `Visa-Bot` would capture this client.

**Three things were decided while implementing it, and each is the reason a later "simplification" would
be a defect.**

**A skip is an outcome, never an absence.** `FailureOutcome` gains `disallowed`. Without it a page nobody
asked for is indistinguishable from a page that did not exist, which is the failure entry 18 named: a
refusal must never read as "nothing found". The corridor reports it in its own sentence rather than folding
it into the generic "could not be read" note, because only the first failure per host survives that note and
a `Disallow` could be masked by an unrelated `404` elsewhere on the same site.

**Three verdicts, not a boolean, because the reasons differ and the reason is what gets reported.** A first
attempt collapsed every non-answer into "disallowed", and the crawl then described **every unreachable
host** as *"its robots.txt does not permit this client"* — a sentence about a policy nobody had read, and
word-for-word the class of false reason entry 33 had just finished removing from `withheld_domains`. So:
a `5xx` or an oversized file is `UNREADABLE` (*"could not be read, so whether this client may fetch it is
unknown"*), a parsed rule that excludes us is `DISALLOWED` (*"does not permit"*), and a **transport failure
raises** rather than deciding anything — an unreachable host is not a crawl policy, and the callers already
describe one correctly, including telling a name that does not resolve from a request that merely failed.
`4xx` on the file itself, `401` and `403` included, means no policy is published: those say the file is
protected, not that the site is closed (RFC 9309 §2.3.1.3).

**A `Disallow` may be reported; it may never resolve a corridor.** `disallowed_urls()` is deliberately not
part of `blocked_urls()` or `persistent_refusals()`, so nothing here reaches `inaccessible_urls` or
`decision_blocking_urls`. A `403` was observed **on the page itself**; a `Disallow` covers a path we chose
not to request. Treating the second as evidence that the answer sat behind that page would be guessing about
a page nobody read, and it would widen entry 32's deliberately narrow exception by a mechanism entry 32
never considered.

**The expiry is not tuning.** `get_visa_plan_service` is an `lru_cache(maxsize=1)`, so the fetcher holding
the cache lives as long as the server process. Without a TTL a policy read at boot would be obeyed until
someone restarted the thing — a withdrawn `Disallow` honoured forever, and a newly published one ignored
just as long. This was found by checking the caller rather than by reading the class, which is the habit
`CLAUDE.md` asks for.

**Two smaller calls.** The policy fetch sits outside the crawl's politeness delay: that delay only ever
bites on the *second* request to a host, and a `robots.txt` fetch is always the first, so routing it through
the delay would space nothing and merely make first contact with every host cost the delay. And in
retrieval the check sits *after* the fresh-cache return, because `robots.txt` governs fetching — text
already held and still inside its TTL is re-read without a request, so a policy published since does not
retrospectively forbid reading what we have. Past the TTL a request is needed and the policy decides.

**A fourth thing, found by running it rather than reading it**, and the reason the paragraph above exists.
The stdlib parser was the first choice and it was inert: it obeys no wildcard rule, which is every rule
`www.gov.uk` publishes. This module had been shipped, tested and documented as honouring crawl policies
while honouring almost none of them, and no unit test could have caught it — the fake policies in the
suite were all literal prefixes, because those are the ones a person writes from memory. It took probing
real authorities. That is the third time in two days a documented claim here turned out to be written
from a code path rather than from output.

**Measured live on 2026-08-18, six corridors, all Indian nationals applying from GB.** Expected to cost
coverage; it cost almost none, and what it did cost was worth nothing.

| Corridor | Policies read | Pages skipped | What was actually lost |
| --- | --- | --- | --- |
| Japan | 6 | 0 | nothing |
| Singapore | 16 | 0 | nothing |
| Vietnam | 6 | 0 | nothing |
| Brazil | 16 | 0 | nothing |
| France | 6 | 1 | a news listing with a filter query, matched by `*/actualites?` |
| China | 6 | 5 | two application portals answering `502` to every path, policy included |

**The most important negative result is France and the United States.** Both were expected to be where
legitimacy might buy something, and `robots.txt` buys **nothing** there: `france-visas.gouv.fr`,
`www.france-visas.gouv.fr` and `travel.state.gov` all answer `403` **to their own `robots.txt`**, served
as a bot-detection interstitial. There is no policy to honour — it is a WAF, not a stated rule. So entry
35's "owed regardless of what it buys" was the correct justification, and it is the only one available:
the two corridors that motivated the review are untouched by this step. Their ten `403`s are still
reported as `blocked`, unchanged.

**Two live findings changed the code, and both were the same failure as before — a reason that was true
of the branch rather than of what was seen.**

- The unreadable case said only "its robots.txt could not be read". For China that pointed a reader at a
  crawl policy when the fact in front of them was a host serving `502` to everything. It now names what
  came back: *"its robots.txt answered HTTP 502, so whether this client may fetch it is unknown"*.
- The corridor-level note was a fixed sentence — *"publishes a robots.txt that does not permit this
  client"* — and for those same two Chinese hosts it **asserted a published refusal that nobody had
  read**. It now repeats the reason recorded against the page instead of composing its own.

That is the third and fourth time in this entry that a sentence describing a branch turned out not to
describe the observation. The rule generalises: **a reported reason must be built from what was
recorded, never written alongside it.**

Entry 35's twenty-corridor measurement — still blocked on credit — should now run against this posture.

---

## 35. The posture is honest client, not anonymous client — and the bar that decides whether this is a product
**2026-08-18 · decided; first of its three steps implemented as entry 36**

An outside review asked the question this project had been answering implicitly: two of the highest-volume
corridors there are — India→US and India→France — now yield a plan with **no document checklist**, because
the pages holding the answer are bot-blocked. If that is the normal case rather than the exception, this is
a careful demonstration of why the approach cannot work rather than a product.

**The finding that reframes it: two commitments had been treated as one.**

1. *Every claim is grounded in an official government page, and refusing beats guessing.* This is the
   product's identity, it is correct, and nothing here weakens it.
2. *Grounded only in what an anonymous, unauthenticated Python client can fetch at request time.* This is
   an **implementation posture**, never decided on its merits, and it is what actually fails on France and
   the United States.

Entry 18 forbids **deception** — spoofing a user agent, pointing the renderer at a refusal, retrying past a
rate limit. It says nothing about becoming a client authorities are willing to serve. Conflating the two has
been costing coverage under the banner of a rule that does not demand it.

**Decided: pursue legitimacy, never circumvention.** Three things follow, in increasing order of scope:

- **Read and honour `robots.txt`.** ~~Nothing in this codebase has ever fetched it.~~ **Done — entry 36.**
  A project that computes a per-host politeness delay (entry 25) while ignoring the file that states a
  host's own crawl policy was inconsistent on its own terms. This was owed regardless of what it buys, and
  it may cost coverage — a `Disallow` previously walked past is now a refusal — which is the correct
  direction for this product.
- **Ask.** An identified research client requesting access from an immigration authority is an ordinary
  thing to do, and the current user agent already invites contact.
- **Client-side retrieval, as an open question and not yet a decision.** The traveller's own browser can
  open `france-visas.gouv.fr`; a human reading a public page is not this program circumventing a refusal.
  Whether the agent may then *read what their session received* is genuinely near entry 18's boundary and
  needs its own entry either way. Recorded now so it is argued rather than drifted into. **Not approved.**

**And the bar, committed before the measurement rather than after it.** The seven-corridor sample cannot
answer whether blocks are the rule, and choosing a threshold after seeing results is how a demonstration
talks itself into being a product. So: run the **top 20 corridors by real traveller volume** cold, and count
per corridor whether the visa decision was confirmed, whether a checklist was found, and whether a checklist
was blocked.

> **Product if ≥70% confirm the decision and ≥50% yield a document checklist. Below that, the
> anonymous-crawl posture is dead** and the choice is licensed data (Timatic/Sherpa — which every airline
> uses and which would forfeit the verifiability that is the whole differentiator) or client-side retrieval.

Today's seven are 5/7 on the decision and 4/7 on a checklist, which would pass — on a sample chosen partly
because it was easy. Blocked on Brave credit; it is the measurement that decides the project's direction, so
nothing large should be built before it.

**Rejected: treating France as an acceptable permanent loss.** Entry 26 established the coverage loss is
real and permanent *given the posture*. What was never established is that the posture is required, and
entry 18 does not require it.

---

## 34. Who to believe becomes committed data; only which page is decided live
**2026-08-18 · decided; implemented as entry 38**

`ARCHITECTURE.md` already states the right division and the code does not implement it:

| | Who to believe (domains) | Which page to read (URLs) |
| --- | --- | --- |
| Corridor-dependent? | No — `mofa.go.jp` serves everyone | Yes |
| How many | ~3 per country | Tens of thousands |
| Decided by | **A rule, once per country** | **The machine, every corridor** |

But `bootstrap_destination` runs *inside every cold request*, and its result is cached **per corridor**. So
a country's trusted set is re-derived from that day's search rankings for every new nationality, and the
answer to "who is Germany's government" varies with Brave's mood. Entry 22's US coin flip was this
mechanism, treated as a ranking problem.

**Decided: generate the country → trusted-domains registry offline for all 198 countries, commit it beside
`countries.yaml`, and have a person skim it once.** Request-time discovery then begins at the corridor step.

What this is **not**: a return to the gate entry 19 removed. Nobody curates URLs — that stays automated and
is the production goal. This is *domains*, about three per country, proposed by the same `bootstrap.py` code
that runs today, with a human reading 198 rows once rather than approving anything per request.

Entry 19's own argument is why this is cheaper than what it replaced: the human was found not to be
exercising taste but applying one mechanical rule. **Committing that rule's output is strictly easier to
audit than re-running it live** — the riskiest automated decision in the system becomes a reviewable diff.

Four things it buys, and the fourth is the one that matters most:

- four searches leave the cold request path (entry 25's remaining time is search latency and two model
  calls);
- the trusted set stops varying between runs, removing the coin-flip class of bug at its source;
- `withheld_domains` becomes a thing a person actually reads, which known problem 2 asks for and nobody does;
- **entry 33's gap becomes fixable by editing a data row** rather than by widening a regex that guards
  everything.

**Rejected: keeping bootstrap in the request and caching it per country instead of per corridor.** It fixes
the variance but leaves the highest-risk decision unreviewed and unreviewable, and still spends the searches
on a cold country.

---

## 33. The governmental half of the trust rule fails closed for a fifth of the world
**2026-08-18 · measured, and its reporting fixed; the amendment itself is not implemented**

Known problem 2 named the wrong half as the risk. It warns about `belongs_to_destination` — "a country whose
government publishes outside its own TLD". The half that actually fails first, and far more widely, is
`looks_governmental`.

`GOVERNMENT_PATTERNS` in `bootstrap.py` recognises `gov`, `go.xx`, `gouv.xx`, `gob.xx`, `govt.xx`, `gc.ca`,
`admin.ch` and `europa.eu`. All seven verified countries happen to sit inside that list — `.gov.sg`,
`.go.jp`, `.gouv.fr`, `.gov.cn`, `.gov.br`, `.gov.vn`, `.gov`. The 22/22 agreement with recorded human
decisions behind entry 19 is therefore **survivorship**: every country audited was one the pattern list
already handled.

**Measured offline, 2026-08-18, no network and no search credit** — `is_own_government` run against a
hand-written table of 51 countries' real immigration or foreign-ministry domains: **32 pass, 19 fail.**

| | |
| --- | --- |
| Fail | AT, BE, **CA**, CL, CZ, **DE**, DK, FI, GR, HU, IE, **IT**, **NL**, NO, PT, RO, RU, **SE**, UY |
| Cause | uniformly *no governmental marker in the hostname* — never the TLD half |

Every failure returns `is_own_government == False` for the domain a traveller would actually need read.
The failure is **safe** — nothing is fetched, nothing is guessed — but it takes most of Schengen with it.

**Refined while committing the test, 2026-08-18: this is two failures, not one, and the quieter one is
worse.** The claim above was originally written as "the country's entire government is refused", which is
true only where the government has *no* marked domain anywhere:

| | Countries | What actually happens |
| --- | --- | --- |
| **Refused outright** | AT, BE, DE, DK, FI, NL, NO, SE, UY | Nothing passes, so `AutomaticDestinationService.destination_for` raises *"No domain belonging to Germany's own government could be identified"*. Honest refusal, **wrong diagnosis**. |
| **Reachable, but not where the answer is** | CA, CL, CZ, GR, HU, IE, IT, PT, RO, RU | Some marked domain exists (`interno.gov.it`, `gov.ie`, `gob.cl`, `cic.gc.ca`), so bootstrap **succeeds** — and builds a trusted set that cannot contain the page holding the visa guidance. |

The second row is the dangerous one, because **nothing reports it.** The corridor resolves against real
government domains and then refuses for looking like a ranking failure, or worse resolves to whatever those
domains do say. Canada is the sharpest case: `gc.ca` is special-cased and still passes, but immigration
content moved to `canada.ca`, so the rule trusts the old namespace and misses the live one. `AT` and `UY`
are narrower again — `gv.at` and `gub.uy` are conventions simply missing from the marker list.

**And it exposed a reporting defect that made the second row hard to notice — now fixed.**
`auto_trusted_domains` had two reasons for declining a domain and both were wrong for this case: Italy's
`esteri.it` was withheld as *"not a government domain for this destination"* — false, and
**character-identical to the reason a commercial visa agency got**. Known problem 2's only recommended
mitigation is to read `withheld_domains`, so the one safeguard misled rather than warned, and entry 34's
registry would have handed a human 198 countries of these labels to skim.

**Fixed 2026-08-18** by splitting that branch three ways. A domain under the destination's own top-level
domain with no recognised marker now says what is true — it could not be *confirmed* as an authority, it
may well be a real one, and for governments with no marker convention the domain has to be named in
reviewed data. A domain that is neither says so plainly. Measured on Italy's shape, the ministry and the
agency no longer read alike.

`unconfirmable_authorities` names those candidates, and `destination_for`'s refusal uses it: *"No domain
belonging to Germany's own government could be **confirmed** … Candidates under Germany's own top-level
domain were found — auswaertiges-amt.de — but none of their hostnames carries a marker this agent
recognises as governmental."* The old wording said none could be **identified**, which is false and sends
a reader to look at search or ranking rather than at the trust rule.

**Reporting only: nothing is accepted for want of a marker**, and a test asserts the accepted set stays
empty. "Looks like an authority" is exactly what the rule refuses.

**Committed as `tests/test_trust_coverage.py`** — 7 tests, offline, no credit. It freezes the failing set so
a change is a visible diff, asserts every failure is on the governmental half rather than the TLD half,
holds the two rows above apart, and guards `countries.yaml` against another country acquiring a governmental
marker in its `tlds` unreviewed. **Verified the tripwire actually fires** by simulating the forbidden fix:
adding `.de`/`.nl` to `GOVERNMENT_PATTERNS` trips three of the seven, including the one asserting that a
German commercial visa agency is indistinguishable from the ministry on the only half that would remain.
France was added to the table afterwards and passes — it fails at HTTP, which is a different limit.

**The mechanism is robust even where the table is not.** The domain list was written from knowledge rather
than fetched, so individual rows may be wrong. It does not matter for the finding: Germany, the Netherlands,
Italy and Sweden have no `gov.de`/`gov.nl` convention at all, so **no** choice of domain rescues them. Two
failures are narrower and worth separating: `gv.at` and `gub.uy` are simply markers missing from the list,
and **Canada** fails only because immigration content moved to `canada.ca` while the special case still
names `gc.ca`.

**Decided: amend through reviewed data, never by widening the regex.** Adding `.de`, `.nl`, `.it` and the
rest as governmental markers would trust every commercial site in those countries — `belongs_to_destination`
cannot narrow it, because these are the countries whose own TLD is the *only* other signal. The registry in
entry 34 is where a named authority domain is written down and reviewed, which is exactly the
"looks official" judgement the rule refuses to automate, made once by a person in git.

`gv` and `gub` may be added to `SUFFIX_MARKER_LABELS`/`GOVERNMENT_PATTERNS` as ordinary marker fixes, and
`gc.ca` should gain `canada.ca` — those are corrections within the existing rule, not relaxations of it.

**And a second break the same measurement exposes, which is not a bug but a definition problem.** For
Schengen short-stay visas the decision genuinely lives at EU level as much as nationally. `europa.eu` passes
`looks_governmental` but can **never** pass `belongs_to_destination` for any member state, so "the
destination's own government" is the wrong trust unit for a supranational visa regime. The fix is data — a
reviewed supranational-domain list per member — but it amends the rule stated in entry 19 and in `CLAUDE.md`,
so it needs deciding rather than patching.

**Done: the check is committed** as `tests/test_trust_coverage.py`, which was the cheapest evidence this
project could buy and needed no network, model or search credit. What remains is the amendment itself —
the registry in entry 34, then reviewed authority domains for the 19, then the supranational list.

---

## 32. A block hands over a link only when it plausibly held the answer
**2026-08-18 · defect found by review; narrowed and implemented**

Entry 27 is the one shipped change never run live, and reading it against the code found the prose and the
behaviour disagree in two ways. Both widen the exception beyond what entry 27 argued for.

**1. Entry 27 says only `401`/`403` qualify. The code also accepts `429`.**
`BLOCKING_STATUS_CODES` is `{401, 403, 429}` in `domain/models.py`, `CrawlFetcher` records all three as
`blocked`, and `ResolvedCorridor.inaccessible_urls` is built from `blocked_urls()` with no filter. So a
transient rate limit can resolve a corridor, force the visa decision to unknown, and be handed to a
traveller as *"this authority refused us"*. Entry 27's own reasoning about `502` applies exactly: a `429` is
a transient fault where "try again later" is the honest advice.

**2. `decision_is_unverified` never checks that the blocked page could have held the decision.**

```python
return "visa_decision" not in filled and bool(self.inaccessible_urls)
```

Any blocked URL anywhere in the crawl, plus any readable source, is enough. The blocked page need not be a
plausible decision source — a `403` on a footer link qualifies. **This is the refusal discipline leaking**,
and it leaks in the worst available direction: WAF `403`s on incidental pages are common at scale, so
corridors whose decision was simply *not found* — the case that must refuse — will increasingly present as
*authority-blocked*, the case that resolves. Entry 27's narrowness was the whole reason it was safe to ship.

**Decided:** drop `429` from what may be handed over (it stays `blocked` for reporting — entry 18 requires
that — but stops qualifying a corridor), and require the blocked URL to have been a **credible
`visa_decision` candidate**: shortlisted for that role, or scoring above a floor for it. A block that cost
us nothing we were looking for is a fact worth reporting and not a reason to resolve.

This narrows entry 27; it does not reverse it. France is unaffected — `france-visas.gouv.fr` is precisely a
credible decision candidate, which is the case the exception was built for.

**Implemented 2026-08-18.** `PERSISTENT_REFUSAL_STATUS_CODES = {401, 403}` sits beside
`BLOCKING_STATUS_CODES`, `CrawlFetcher` records which status a refusal came back with, and
`ResolvedCorridor` gained `decision_blocking_urls` — carried *apart* from `inaccessible_urls`, because
every refusal is worth reporting while only the refusal of a page that could have answered the question
licenses resolving one. `is_usable` and `decision_is_unverified` read the new field. Three things must now
hold: the refusal is settled, the page plausibly held the decision, and something readable remains to cite.

**Credibility is the score the page already earned for `visa_decision` as a link, above zero.** A low bar
deliberately, rather than a tuned one: the scorer already **vetoes** site furniture, archived paths and
wrong-audience pages outright, so any positive score means real signal was seen. Nothing here judges what
the page *says* — nobody read it, and nobody may.

**A limit worth recording, because it fails toward refusing.** Only pages the pipeline scored can be
judged, and the crawl discards a page it could not fetch, so a refusal first met at crawl depth is not a
candidate and cannot qualify. An authority's own visa portal is what search returns first — France-Visas is
exactly that — so the case this exists for is covered, and a corridor that loses its answer this way
refuses.

**Verified by mutation rather than by the tests merely passing.** Reintroducing each defect fails exactly
the intended test: letting `429` qualify again trips
`test_a_rate_limit_is_reported_but_can_never_resolve_a_corridor`, and reverting `decision_is_unverified` to
read `inaccessible_urls` trips `test_a_block_that_could_not_have_held_the_decision_resolves_nothing`.
301 tests pass.

---

## 31. A failed adjudication refuses rather than falling back to the heuristic
**2026-08-18 · amends entry 16 · implemented**

Entry 16 chose: *"a failed call falls back to the heuristic, so a corridor degrades to a worse answer, never
to none."* That reads as conservative and is the opposite.

The heuristic is the decider **entry 15 proved gives confident wrong answers**: Brazil's Riyadh page as the
document checklist, at exit 0, full confidence, nothing in the output suggesting the checklist belonged to a
mission on another continent. Entry 15 called that "the outcome entries 5 and 6 exist to prevent." So the
fallback converts a transient OpenAI outage into precisely that outcome, in production, distinguishable only
by a reviewer noticing `decided_by`.

Every other layer of this product prefers refusing to guessing. This one line prefers guessing.

**Decided:** a failed adjudication call refuses the corridor. Retrying the call once is acceptable — a model
call is not an authority refusing us, so entry 18 does not apply — and if it still fails, the corridor is
refused with the reason, which is an outcome the product already supports and states honestly.

**What the heuristic keeps**, because neither job is affected: it builds the shortlist the model chooses
from, and it answers when `discovery_decider: heuristic` is configured, which stays tested and stays the
offline regression baseline.

**The cost, stated plainly:** an OpenAI outage takes discovery down instead of degrading it. That is the
correct trade for a product whose wrong answers send someone to a visa centre without the right papers, and
it is the same trade entry 18 makes about blocks.

---

## 30. `conflicts` is deleted, by entry 6's own rule
**2026-08-18 · implemented**

Entry 6 built a deterministic conflict detector, found a real discrepancy with it, and **deleted it anyway**
because nothing recorded who a claim applied to, so a general visa-free-nationalities page and a
nationality-specific page compared as a contradiction. It recorded the generalised lesson:

> a feature whose wrong answers are alarming must have a near-zero false-positive rate, or it should not
> ship.

What shipped instead was `conflicts` on `VisaPlan`: free text written by the model, shown to travellers in
the interface's reliability panel, with **nothing checking it**. On the axis entry 6 deleted its predecessor
for, that is strictly worse — the checked version was removed and the unchecked version kept.

**Decided: delete the field.** From `VisaPlan` and `VisaPlanDraft` in `domain/models.py`, from the
extraction prompt's rule 5, from `openai_extraction.py` and `fixtures.py`, and from the Singapore fixture
plan. A genuine disagreement between official sources still reaches the traveller through
`unresolved_questions`, which is where an unverified model observation honestly belongs.

Revisit it as the scoped redesign already specified in entry 6 and in `TODO.md` — claim scope recorded,
visa decision excluded, quantitative rules only — and not before.

**Done 2026-08-18**, from `VisaPlanDraft` and `VisaPlan`, the extraction prompt's rule 5, both extractors,
the Singapore fixture and the interface. Two details worth knowing:

- **The one real conflict this project ever found was preserved, not dropped.** Singapore's own pages
  measure passport validity from entry and from departure, which is the discrepancy entry 6's detector
  correctly caught. It is now a sentence in `unresolved_questions`, where an unverified observation
  honestly belongs, and a test asserts it is still there. Rule 5 was rewritten rather than deleted —
  disagreements must still be recorded, and never silently resolved in favour of one page — and it kept
  its number, because other documents cite rules 8a and 8b.
- **The interface lost a two-column grid, not just a block.** `.reliability-grid` was
  `grid-template-columns: 1fr 1fr`, so removing one of its two children would have left the remaining
  block rendering in half the width beside an empty column. Both the wrapper and its now-dead CSS went
  with it. Checked by injecting a plan into the real page rather than trusting the diff — the technique
  from entry 28 — confirming one heading, the block at 91% of the container, both questions rendered, no
  console error, and no horizontal overflow at 375px.

**Rejected: keeping it because it is the only conflict signal there is.** An alarming signal nobody
validates is not better than none; that is the entry 6 finding, and this field is the same mistake with the
verification removed.

---

## 29. LangGraph is not adopted, and the placeholder goes with it
**2026-08-18**

`domain/state.py` had described a "future LangGraph workflow" since the first week, `langgraph>=1,<2` was a
declared dependency in `pyproject.toml`, and **neither was imported anywhere** — verified by grep:
`VisaResearchState` appeared only on the line that defined it.

**Decided: this project does not need LangGraph, and the question is closed.** The reasoning, since a
graph framework is the obvious thing to reach for in an "agent" project:

- **There is no cycle to express.** The pipeline is linear — search → crawl → score → adjudicate → fetch →
  extract — and deliberately so. LangGraph earns its complexity on loops, conditional multi-actor routing
  and interrupts. `research/service.py`'s pipeline is two lines because there is nothing to orchestrate.
- **The control flow is the safety story, and it is Python.** Trust is enforced at three typed checkpoints
  (`validate_route`, after each redirect, after each meta-refresh). Expressing that as graph nodes over a
  `TypedDict` would move those guards from Pydantic validators — which cannot be skipped — into node bodies
  that can be reordered or bypassed. That is a real loss for no gain.
- **The one loop the placeholder imagines is one this project rejects.** `research_attempts` and
  `missing_fields` describe a re-research retry loop. Refusing beats retrying here (entries 5, 18, and 31),
  so the state shape encodes an architecture the decisions have since ruled out.
- **Durability already exists and is simpler.** `FileCorridorStore` and the source cache are the
  checkpoints a graph runner would offer, keyed to the two things whose lifetimes genuinely differ (weeks
  for corridors, hours for evidence). LangGraph checkpointing would not know that distinction.
- **LangChain stays**, and is a separate question: it is used only for structured output against a schema in
  `adjudication.py` and `openai_extraction.py`. That is a thin, working use and nothing here argues against
  it.

**Done 2026-08-18:** `domain/state.py` is deleted and `langgraph` is dropped from `pyproject.toml`. An
unused dependency in a project whose safety argument rests on a small audited surface is not free — it is
one more thing a reader must check is not load-bearing. `TODO.md` had this as "either update it or delete
it"; this was the decision to delete.

**If it is ever revisited**, the trigger to look for is a genuine cycle with human interrupts — plausibly
the client-side retrieval flow in entry 35, where a plan waits on the traveller fetching a blocked page.
Even then, one `await` in FastAPI is the cheaper first answer.

---

## 28. Four fixes from reading the interface as a traveller
**2026-08-17**

Reviewing a rendered plan rather than a JSON payload found four things, none of which a test was
going to catch.

**A step heading stopped mid-clause.** *"Create an account and complete the online application if the
wizard says a visa,"* — 79 characters against an 80-character limit. The model was writing a sentence
into a field meant for a label and ran out of room. The limit is now 70, the prompt says a title is a
short label of at most eight words with the substance in `action`, and a trailing comma is trimmed in
a validator. Trimming is safe here precisely because a heading is derived text rather than a claim.

**A corridor that cannot have an answer now costs nothing.** A national of the destination does not
apply to visit their own country, so there is no guidance to find — but the request searched, crawled
and spent two model calls to discover that, then read as a fault. It is refused up front with a plain
sentence. Deliberately *not* a claim about entry rights: it says only what this agent researches. And
deliberately narrow — it matches the **passport** only, never the residence, because applying from
inside the destination is ordinary.

**An empty checklist section is not rendered.** With no checklist source, no documents may be listed,
so the panel was a heading and a caveat above nothing. Dropping it hides nothing: the absence is
stated under unresolved questions, which such a plan is structurally required to carry (entry 23).

**The incomplete-evidence detail moved to the end.** It sat above the answer, and with a blocked
authority's reasons and links it had grown long enough to bury it. This entry does change what entry
13's era of the interface documented — *"the interface states what is incomplete above the
guidance"* — so it keeps the half that mattered: a one-line notice above the guidance, and the
reasons, links and caveats at the end. A partial plan still cannot look complete.

**Verified by driving the real renderer**, with a France-shaped plan injected into the page rather
than a live run — the search quota was exhausted (entry 27). Four panels, no checklist panel, banner
in the last one, and the blocked authority rendered as a working link. Reading it that way also caught
the banner still saying *"Everything below is still drawn only from official sources"* after it had
been moved to the bottom.

---

## 27. A block becomes a next step: name the page, hand over the link, decide nothing
**2026-08-17**

Entry 26 established that France refuses because every readable page delegates the visa decision to
a portal that answers 403. Refusing is honest but not useful: the traveller gets "no verified plan"
for one of the commonest corridors there is, when the sentence they could act on was available all
along — *France publishes this at france-visas.gouv.fr; we were not permitted to read it; open it
yourself*.

**Decided: a corridor resolves when the only thing missing is behind a block, and the plan says so.**
Three properties hold it in place, and none of them is a relaxation of entry 18:

- **Nothing is inferred.** `visa_required` is set to `null` — not guessed — and that is *enforced in
  the application*, not asked of the prompt: the model returned `true` in the test and the extractor
  overrode it. A wrong yes or no about whether someone needs a visa is the most damaging thing this
  product can say.
- **The page is named, never read.** `UnreadableAuthority` is deliberately not a `ConfiguredSource`:
  there is no content behind it, and a source with empty content is exactly what must never be
  citable. The research packet carries its URL and authority and no text, so the model is told where
  the guidance lives, not what it says.
- **It is still held to the domain rule.** A page shown to a traveller as this destination's own
  guidance must sit on an approved domain, validated in `validate_route`. This is the case that needs
  that rule most: nobody read the page, so the domain is the only thing vouching for it. The guard
  caught a test fixture of mine pairing Singapore's config with a French URL.

**The exception stays narrow.** A visa decision that was simply *not found* still refuses — the gap
must be one an authority imposed, which means a recorded `blocked` outcome, and only `401`/`403`
qualify. A `502` is a transient fault where "try again later" is the honest advice, and a host whose
DNS does not resolve must never be handed over as a link at all. Readable sources are still required:
with nothing to cite there is no plan, only a link, and
`ResolvedCorridor.is_usable` requires both.

Such a plan can never be `verified`, for the same reason a checklist-less one cannot (entry 23) and
more strongly. The interface renders the blocked authority with its URL and the plain sentence, so the
refusal becomes a next step rather than a dead end.

**Verified offline, end to end, and NOT verified live.** The chain is covered by tests from
`ResolvedCorridor.is_usable` through `to_destination_config` to the extracted plan: the decision is
forced to unknown, the authority is named with its URL in `unavailable_sources`, the status is
`partial`, and the packet carries no content for it. 286 tests pass.

**The live run could not be done: the Brave search API returned HTTP 402, out of credit.** So what a
model actually writes for France given the UK post's page plus a named blocked portal is *unverified*.
Re-run `france/IN/GB/tourism` when the quota resets, and read the plan as a traveller would before
trusting this. That is the one thing outstanding on this entry.

---

## 26. France refuses because France does not publish the answer anywhere readable
**2026-08-17 · qualified by entry 41 on 2026-08-19**

> **The title overstates what was measured.** France does not publish the answer anywhere *this client
> could read*, which is a narrower claim — the pages on `france-visas.gouv.fr` were never read, only
> challenged. Rendering them (entry 41) shows the decision and the corridor checklist sit behind a
> four-step wizard rather than on a page, so the conclusion below survives; the reason for it has
> changed from "nowhere readable" to "behind form input".

`france/IN/GB/tourism` — an Indian passport, applying from the UK — refused, and it is a corridor
common enough that the refusal deserved checking rather than attributing to the known 403.

**It was a coin flip, not a dead end.** Two consecutive runs over an identical shortlist: one
resolved, one refused. The shortlist was deterministic; the model was not. So the corridor was
marginal, and the reason was what the shortlist contained.

**Two real scoring defects, both fixed.**

1. **A host label was read as who a page is for.** `in.diplomatie.gouv.fr` is France's mission *in
   India*, and `_matches_country` matched India's host label `in`, so the nationality bonus of +40
   went to **everything that post publishes**. That beat the +30 the UK post earns for actually
   serving this traveller: on the identical page `/en/applying-for-a-visa`, the India post scored
   65.6 and the UK post 55.6. So the post for the traveller's *home* country outranked the post they
   must apply at — the same shape of bug as entry 21, a country code matching where it does not mean
   the country. The bonus now reads only the path and the title, which are the page describing
   itself; the host stays with the mission machinery, which is keyed on where the traveller applies
   from. After the fix the UK post leads 55.6 to 25.6.

   `_matches_country` itself is unchanged, because `wrong_country` needs the host label: it is what
   keeps *other* posts — France in Germany, France in Brazil — out of a corridor entirely.

2. **Site furniture took three of ten fetch places.** `/accessibilite`,
   `/en/donnees-personnelles` and `/mentions-legales` each scored 69, above the UK post's real
   pages. The mechanism is worth recording: `extract_links` gives a link the last heading seen above
   it, and footer links sit below everything, so France's legal notice inherited the heading of a
   news article about visa requirements and collected the heading bonus twice. A legal notice cannot
   be visa guidance whatever it scores, so `boilerplate_tokens` vetoes it exactly as `archive_tokens`
   does — rejecting rather than penalising.

**And with both fixed, France still refuses — correctly, and now consistently (3 runs of 3).** This
is the part that matters. The shortlist is now the right pages, and reading them shows the answer is
not there:

| readable page | what it actually says |
| --- | --- |
| `uk.diplomatie.gouv.fr/en/applying-for-a-visa` | Sends the reader to the France-Visas "visa wizard" to find out whether they need a visa |
| `uk.diplomatie.gouv.fr/en/visiting-france` | Tourism marketing — landscapes and monuments |
| `www.diplomatie.gouv.fr/en/services-to-foreigners/visiting-france` | Tourism marketing |
| `france-visas.gouv.fr` | **HTTP 403** — the wizard, and the only place the decision lives |

France's own government states the visa decision **only** on the portal that refuses automated
retrieval. Every readable page delegates to it. So there is no page that can be confirmed as the
visa decision, and refusing is the correct output rather than a ranking failure.

**Which makes the earlier resolving run the wrong one.** It named the India post's
`/en/applying-for-a-visa` as `visa_decision`, `document_checklist`, `application_route`, `fees` and
`processing_times` — five roles from a page that is a signpost saying "use the wizard". A checklist
assembled from that is exactly the output entry 6 was deleted over. The scoring fixes made the
refusal consistent by removing the noise the model was over-reaching on, but the guard against that
over-reach is `VisaPlan`'s validators, not the ranking.

**Verified no regression.** The United States is unchanged — same ten pages, same scores, same three
roles; its India-post pages keep the nationality bonus legitimately, because their *titles* name
India. Brazil's four role assignments are unchanged. China returned the same checklist and fees.

**What this says about the product, plainly:** France is unservable, and it is unservable because of
entry 18 rather than in spite of it. The honest thing to add is not a plan but the sentence a
traveller can act on — that an authority refused us, and here is the URL to check themselves. That
is already the open todo, and this corridor is now its strongest argument.

---

## 25. The politeness delay is owed to a host, not to the crawl
**2026-08-17**

A cold corridor took **54.5s**, and instrumenting it by phase showed where: the crawl spent 25.9s on
32 page fetches, of which **about 16s was sleeping**. `CrawlFetcher` awaited its 0.5s delay before
*every* request whatever host it was for, and `LinkCrawler` walked its frontier one page at a time,
so each site's spacing was also paid by every other site. Search added another 15s across 16 queries
run one after another.

**Decided: the delay is per host, and hosts are crawled concurrently.** This is *more* correct about
politeness rather than less — every host still gets its full 0.5s spacing, and the next slot is
claimed before sleeping so two requests to one host queue rather than both reading the same
last-request time. What stops is one site waiting behind another it has nothing to do with.

The frontier now yields a **wave**: the best few links, at most one per host. A second link on a host
already in the wave goes back to the frontier rather than being dropped, so nothing is lost by being
second in its queue. Results are handled in frontier order, never completion order, because which
page a corridor resolves to depends on the order candidates are seen and that must not depend on
which site answered first.

**Search runs concurrently too, bounded at four.** Measured first rather than assumed: four
concurrent Brave queries took 1.32s against 1.26s for one, with no rate-limit errors. Bounded rather
than unbounded because a search API is someone else's rate limit and a burst that trips it turns a
resolvable corridor into a refusal — `search()` raises on any non-200, and that becomes a 503. A
failing query still fails the run, exactly as when they ran in sequence; whether a partly-searched
corridor is safe to serve is a separate decision and has not been made.

**Measured, 2026-08-17, `united-states/IN/IN/tourism` cold with both caches cleared:**

| phase | before | after |
| --- | --- | --- |
| bootstrap (4 searches) | 4.5s | **1.1s** |
| crawl | 25.9s | **7.2s** |
| shortlist fetch | 1.5s | 0.9s |
| role adjudication | 11.2s | 8.1s |
| **corridor** | **54.5s** | **19.4s** |
| plan extraction | 11.8s | 14.7s |
| **cold request total** | **66.3s** | **34.1s** |

Brazil went 85.6s to 28.5s, China 161s to 43.1s. The remaining corridor time is now two model calls
and search latency, not waiting.

**What did not change, which was the condition on doing this at all.** The US corridor produced a
byte-identical shortlist — same ten pages, same order, same scores — and the same three roles.
Brazil's four role assignments are unchanged, Edinburgh checklist included. **Coverage bounds were
not touched:** `maximum_pages` is still 40 and `maximum_pages_per_host` still 20, because those bound
what can be found and Japan's checklist was two hops deep.

**One corridor did change, and it is worth knowing.** China's `document_checklist` resolved to
`gb.china-embassy.gov.cn/eng/visa/qzxz/201303/t20130315_3383966.htm` (38.2) where it had been
`.../eng/xnyfgk/201303/t20130315_3317069.htm` (34.2). Same title, same authority, same `201303`
publication path: the embassy publishes that document under two sections, and which duplicate is
discovered first depends on crawl order. The new one scores higher, and the roles are otherwise
identical. So crawl order *was* mildly load-bearing — for choosing between duplicates of one
document, which is the harmless end of that risk.

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

> **Corrected 2026-08-18.** The paragraph above stopped being true when entry 27 shipped, and stayed in
> the todo list for a day longer than it should have. `to_destination_config` fills
> `unreadable_authorities` from `inaccessible_urls` **unconditionally** — not only when the decision was
> blocked — the extractor carries them into `unavailable_sources` regardless, and the interface gives any
> `blocked` failure with a URL the sentence *"does not permit automated retrieval"* and a link. A
> retrieval-time block reaches the plan by a second route through `RetrievalReport.failures`. So the
> mechanism exists twice over, and the remaining question is only whether it *reads* usefully, which
> needs a live run. Left here rather than rewritten, because the mistake is instructive: this was
> described from reading the code path that used to exist instead of from a plan.

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
**2026-08-16 · amended by entry 41 on 2026-08-19**

> **Read entry 41 with this.** The prediction below — that a headless Chromium would pass France's
> check — was measured and is correct, and the premise was wrong: `france-visas.gouv.fr` serves a
> Cloudflare *challenge* (`cf-mitigated: challenge`), not a refusal, and serves it for `robots.txt`
> too, so no policy was ever stated. A challenge may now be answered by the renderer under our own
> user agent. Everything below still governs an actual refusal — a `401`, a bare `403`, a `429` — and
> the prohibitions on spoofing and retrying are untouched.

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
