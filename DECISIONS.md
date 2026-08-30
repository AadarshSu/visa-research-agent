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
**60** (a questionnaire is an answer, not a blockade), **44** + **78** (a page may be stored, an answer may
not — and stored text ranks, it never speaks).

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
| [71](#71-two-defects-a-sweep-found-that-no-corridor-had-status-990-and-a-chain-morocco-does-not-send) | **Status `990` crashed a corridor; Morocco's chain is now bundled** — two defects only breadth found |
| [70](#70-stage-2-of-batch-1-all-41-run-and-both-things-entry-69-expected-were-wrong) | **Stage 2, all 41 run** — authorities publish per *post*; the demonym bonus buys 0.18 places, all noise |
| [69](#69-batch-1-bounds-destinations-never-nationalities--and-184-of-198-passports-have-no-demonym) | **Batch 1 bounds destinations, not nationalities** — and 184 of 198 passports have no demonym |
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
| [73](#73-cyprus-and-slovakia-were-never-refusing-us--entry-70-read-a-challenge-as-a-refusal) | **A header-only test read a challenge as a refusal** — Cyprus and Slovakia are answerable |
| [35](#35-the-posture-is-honest-client-not-anonymous-client--and-the-bar-that-decides-whether-this-is-a-product) | **Honest client, not anonymous client** — and the bar that decided the product question |
| [36](#36-robotstxt-is-read-and-obeyed-and-a-page-skipped-for-it-is-its-own-outcome) | `robots.txt` is read and obeyed; a page skipped for it is its own outcome |
| [75](#75-the-challenge-is-answered-cyprus-resolves-greece-still-refuses-and-the-wait-had-to-be-a-poll) | **The challenge is answered** — Cyprus resolves, Greece still refuses, and a fixed wait races the redirect |
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
| [96](#96-the-entry-plan-is-built-and-the-floor-it-needed-was-not-a-number) | **The entry plan is built** — three visa-free corridors state 3, 5 and 7 duties, so the floor is no floor |
| [97](#97-recallrecordselector-recorded-which-selector-was-configured-and-a-credit-outage-proved-it) | **`selector` recorded the configuration, not the run** — a credit outage put the heuristic in the model's arm again |
| [98](#98-a-model-produced-the-entry-plan-and-a-sixth-thing-was-in-the-way) | **A model produced the entry plan** — and a sixth blocker read a correct empty checklist as a failure |
| [115](#115-the-shallow-crawl-warning-gave-the-same-advice-to-two-opposite-failures) | **The shallow-crawl advice was wrong half the time** — the Philippines spent 425 of 1,200 pages |
| [114](#114-one-pdf-with-nul-bytes-discarded-a-whole-countrys-crawl) | **One PDF discarded China's crawl** — the text layer had NUL bytes and the failure landed after the crawl |
| [113](#113-gov-bg-is-a-public-suffix-so-bulgaria-was-not-thin-it-was-unresearchable) | **`gov.bg` made Bulgaria unresearchable** — a reviewed domain nothing constructed until a build tried |
| [112](#112-a-third-traveller-the-corpus-was-never-tuned-for-scores-higher-than-the-two-it-was-built-on) | **A third traveller scores 87%** — higher than the two the system was built on |
| [111](#111-twelve-more-domains-on-the-owners-judgement-and-what-that-standard-is) | **Twelve more on judgement** — `reviewed` now means "a person decided", in three marked tiers |
| [110](#110-six-domains-for-five-countries--and-the-proposed-lists-were-wrong-about-which-domain-to-want) | **Six domains, five countries** — and three for three, the right domain was not the proposed one |
| [109](#109-travelstategov-was-never-a-challenge--it-is-a-block-and-we-were-rendering-past-it) | **`travel.state.gov` is a block, not a challenge** — one shared marker had us rendering past a refusal |
| [108](#108-germanys-rebuild-closed-three-of-four-slots-the-united-states-closed-none) | **Germany 1 host → 87, three slots closed** — and the US challenge is a real ceiling |
| [107](#107-diplode-is-reviewed-and-trusted-because-the-ministry-itself-names-it) | **`diplo.de` reviewed and trusted** — TLS could not confirm it; the ministry's own page did |
| [106](#106-the-ceiling-nine-open-slots-two-countries-two-causes--and-the-selector-ab-is-closed) | **The ceiling: nine slots, two countries, two causes** — and the selector A/B is closed |
| [105](#105-the-vocabulary-work-verified-end-to-end-and-a-role-scoring-zero-can-still-be-filled) | **Verified end to end** — the heuristic gained 12 points; a zero-scoring role can still be filled |
| [104](#104-fees-and-processing_times-get-the-same-treatment-and-one-term-is-rejected-for-a-reason-worth-keeping) | **`fees` and `processing_times` widened** — and `payment` rejected: a checkout page is not a fee |
| [103](#103-the-roles-that-go-unanswered-are-the-roles-with-the-fewest-words) | **The unanswered roles are the ones with fewest words** — 3 terms, 0 candidates in two countries |
| [102](#102-a-family-needs-a-visa-word-not-merely-a-government-word) | **A family needs a visa word** — `apply`/`appointment`/`fees` let passport renewals hold a verdict |
| [101](#101-a-rebuild-cannot-open-what-a-build-recorded-and-the-gate-was-counting-the-wrong-thing) | **A rebuild cannot open what a build recorded** — and `opened` undercounted fetches by 2.6× |
| [100](#100-the-oracle-is-left-wrong-on-purpose-because-every-distortion-in-it-runs-one-way) | **The oracle is left wrong on purpose** — the distortions run against the model, so the number is a floor |
| [99](#99-text-coverage-is-not-the-constraint-and-selection-recall-does-not-measure-what-it-looks-like) | **Coverage is not the constraint** — France 7% scores 100%, the UK 81% scores 40%; item 40 dropped |

### Finding the right page: ranking, recall, judgement
| | |
| --- | --- |
| [9](#9-a-page-can-fill-several-roles) | A page can fill several roles |
| [15](#15-brazil-the-out-of-sample-test-discovery-ranks-the-wrong-page-confidently) | Brazil: the heuristic ranks the wrong page, confidently |
| [16](#16-judgement-decides-the-last-step-heuristics-decide-everything-before-it) | Judgement decides the last step; heuristics everything before it |
| [17](#17-france-and-china-the-decider-refuses-well-and-the-wall-is-now-access-not-ranking) | France and China: the wall is access, not ranking |
| [40](#40-the-shortlist-is-a-recall-budget-and-ten-places-made-the-heuristic-the-real-decider) | The shortlist is a recall budget, not a ranking |
| [42](#42-the-excerpt-is-the-second-recall-gate-and-a-flat-6000-made-truncation-the-decider) | The excerpt is the second recall gate |
| [74](#74-search-a-spend-cap-is-not-a-throttle-a-burst-is-not-a-pace-and-a-corpus-may-answer-alone) | **A capped account killed every corpus country** — paced, classified, and a corpus may now answer alone |
| [43](#43-write-down-what-a-corridor-considered-because-ranked-out-and-never-found-had-looked-identical) | Write down what a corridor considered |
| [50](#50-the-routing-index-removes-the-wrong-cost-it-is-wrong_country-not-scoring) | The routing index removed the wrong cost |
| [52](#52-entry-47s-pin-only-half-existed-the-truncation-dropped-it) | Entry 47's pin only half existed |
| [56](#56-the-vocabulary-asked-the-question-and-could-not-recognise-the-answer) | The vocabulary could not recognise the answer |
| [61](#61-the-united-kingdoms-answer-was-five-deep-in-a-list-that-reserved-three) | **Five reserved places per role** — the United Kingdom went 0/8 → 4/4 |
| [72](#72-a-post-named-in-the-host-was-no-post-at-all--and-the-fix-that-looked-obvious-was-wrong-twice) | **A post named in the host read as no post** — and the obvious fix broke 165 correct pages |
| [62](#62-the-nationality-bonus-is-left-alone--four-fixes-four-disproofs-and-a-cost-of-027-places) | The nationality bonus is left alone — four fixes, four disproofs |

### The stores: corpus, corridors, freshness
| | |
| --- | --- |
| [4](#4-cached-evidence-reports-when-it-was-really-retrieved) | Cached evidence reports when it was **really** retrieved |
| [89](#89-guidance-an-authority-contracts-out-named-never-read-never-believed) | **Guidance an authority contracts out** — named, never read; the model selects and may never supply |
| [95](#95-a-visa-free-plan-is-an-entry-plan-not-an-empty-application) | **A visa-free plan is an entry plan** — the spec; built in [96](#96-the-entry-plan-is-built-and-the-floor-it-needed-was-not-a-number) |
| [94](#94-no-visa-required-is-a-complete-answer-and-four-of-singapores-six-questions-stop-existing) | **"No visa required" is a complete answer** — four of Singapore's six questions stop existing |
| [93](#93-a-tool-mediated-answer-is-an-answer-and-the-metric-was-the-only-thing-saying-otherwise) | **A tool-mediated answer is an answer** — the product always said so; only the metric did not |
| [92](#92-the-corpus-build-always-rendered-twelve-renders-is-what-left-france-unreadable) | **The corpus build always rendered** — the budget was twelve, and France met 64 challenges |
| [91](#91-a-second-traveller-in-the-oracle-the-corpus-answers-78-of-roles-for-one-and-68-for-the-other) | **A second traveller in the oracle** — 78% of roles answerable for one, 68% for the other |
| [90](#90-the-corpus-gate-the-100-is-kept-and-demoted-and-the-number-that-matters-is-per-traveller) | **The corpus gate** — the 47/47 is one traveller; the number that matters is the per-traveller family |
| [88](#88-the-corpus-does-not-generalise-across-travellers-and-the-ceiling-is-not-the-crawler) | **The corpus does not generalise across travellers** — and the ceiling is VFS Global, not the crawl |
| [87](#87-an-oracle-neither-selector-built-entry-86s-41-is-30-and-the-direction-holds) | **An oracle neither selector built** — entry 86's +41 is +30; the joint oracle scored address luck |
| [86](#86-matched-budget-the-selector-is-not-7-points-better-than-ranking-it-is-41) | **Matched budget: +41 points, not +7** — entry 85 compared configurations, not selectors |
| [85](#85-ten-countries-ten-text-indexes-the-selector-wins-by-seven-points-and-reads-59-fewer-pages) | **Ten countries: +7 points, 59% fewer pages read.** The selector goes on; entry 84's +30 was a sample artefact |
| [84](#84-graded-on-the-selection-instead-of-the-plan-the-model-reads-half-as-much-and-finds-30-points-more) | **Graded on the selection, not the plan** — 85% against 55%, reading half as many pages |
| [83](#83-a-model-chooses-what-to-read-and-the-stored-text-barrier-moves-from-an-absence-to-a-type) | **A model chooses what to read** — 7 pages instead of 35; the stored-text barrier becomes a type |
| [82](#82-the-nationality-dimension-is-not-a-budget-problem-canada-published-links-the-uk-published-a-form) | **Canada published links, the UK published a form** — the crawl gap is a questionnaire, not a budget |
| [81](#81-item-32s-premise-is-false-and-so-was-entry-80s-the-metric-could-not-see-what-it-claimed) | **The metric could not see what it claimed** — role count swings ±2 on identical input; entry 80 withdrawn |
| [80](#80-entry-79-shipped-a-regression-and-twelve-runs-found-it-stored-text-may-not-rank-a-set-it-barely-covers) | **Stored text may not rank a set it barely covers** — the lift ranked by who was crawled, and cost two roles |
| [79](#79-the-body-score-moves-in-front-of-the-shortlist-and-stored-text-may-lift-but-never-sink) | **The body score moves in front of the shortlist** — stored text lifts and never sinks |
| [78](#78-the-corpus-stored-the-link-not-the-page--and-91-of-a-country-was-never-read-at-all) | **The corpus stored the link, not the page** — 29 characters of anchor against 3,602 of body, and 91% never read |
| [77](#77-does-the-corpus-inherit-searchs-weaknesses-three-diagnoses-all-wrong-and-one-real-defect) | **A corpus build stops at its seeds** — and Japan's missing embassy was a `403`, not recall |
| [76](#76-what-a-corpus-can-and-cannot-buy-measured--and-the-seven-that-no-corpus-will-fix) | **A corpus buys speed, stability and outage tolerance — not coverage.** Seven refusals no crawl can fix |
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

## 115. The shallow-crawl warning gave the same advice to two opposite failures

**2026-08-30 · found by the 43-country build, item 41**

`depth_is_exercised` prints when under 10% of a crawl's entries lie beyond depth 1, and it closed
with one fixed sentence: *"Raise --pages well above the seed count."* Two countries in this build
triggered it and only one of them could have been helped by that.

| | crawled | budget | what actually stopped it |
| --- | --- | --- | --- |
| Slovakia | 1,203 | 1,200 | spent the allowance at depth 1 — the advice fits |
| Philippines | **425** | 1,200 | 43 links redirected off the approved domains, three DFA consular hosts refused with `403`, timeouts and `500`s — **the budget was never the constraint** |

Telling the Philippines to raise `--pages` sends a reader to change the one number the run had
already shown was not binding. That is entry 36's rule about reasons, in the build's own reporting
rather than in a traveller's: **the remedy printed has to be true of the run that printed it.**

**The fix is to carry the budget, not to guess from the shape.** `CorpusBuild.page_budget` records
the allowance the build was given and `budget_was_spent` compares it to what was crawled, so the
two cases are told apart by measurement rather than by a threshold on the same number that raised
the warning. A crawl that stayed shallow with budget to spare is now told so, with the figures, and
pointed at the lost hosts and the unreadable count — where its actual cause is already printed.

**What this does not do is diagnose the frontier.** Both countries stayed at depth 1 and the reason
the Philippines' frontier ran dry — off-domain redirects and refusals — is reported but not
counted against the depth question. Whether a crawl that cannot expand should say more than "read
the lines above" is open, and unmeasured; this entry only stops the output asserting something the
run disproved.

---

## 114. One PDF with NUL bytes discarded a whole country's crawl

**2026-08-30 · found by the 43-country build, item 41**

China crawled for eighteen minutes and then wrote nothing:

```
ValidationError: 1 validation error for StoredPage
body  Input should be a valid string, unable to parse raw data as a unicode string
      input_value='اࣿﷻ\x00\x00\x00 ...'
```

A PDF's text layer carried NUL bytes. `StoredPage.body` is a pydantic `str`, which refuses them —
correctly, since SQLite cannot hold a NUL in a TEXT column either. What made it expensive is
*where* it landed: `_read_pdfs` runs **after** the crawl, in the same call that writes the corpus,
so the failure fell between doing the work and saving it. Nothing was written — not the PDF, not
the 1,200 pages of crawl.

**Dropping the characters is not editing guidance, and that is the argument for fixing it this
way.** A NUL carries no meaning; truncating at `DEFAULT_KEPT_TEXT_CHARACTERS` can also cut a
surrogate pair in half and leave an unpaired half behind, which fails the same validator for the
same non-reason. This text is ranking input that never reaches a traveller (entry 78), so removing
a character that cannot be stored changes nothing a traveller could ever see. The alternative on
offer was not "keep the page intact" — it was losing every page in the country.

`storable_text` strips the C0 controls and repairs unpaired surrogates, keeping tab, newline and
carriage return. It is applied in `keep`, which is the single funnel into the index for both the
crawl and the PDF pass, so no future caller can route around it.

**Checked both ways rather than reasoned about.** The regression test drives a PDF whose text layer
holds `\x00\x00` and a lone surrogate; with the sanitiser bypassed it fails with the exact
production error, and with it in place the build completes and reports its PDF read.

**The class of defect is entry 71's, one country wider.** Status `990` crashed a corridor and
Morocco's chain had to be bundled, both found only by running countries nobody had run. This is the
third: breadth keeps finding crashes that depth cannot, because the input space is other people's
web servers.

---

## 113. `gov.bg` is a public suffix, so Bulgaria was not thin — it was unresearchable

**2026-08-30 · found by the 43-country build, item 41**

Bulgaria's corpus build failed in two seconds, before a single query:

```
Value error, trusted domain gov.bg is a public suffix and would trust every site beneath it
```

`gov.bg` was added the day before in entry 111's batch of twelve, and **the reviewer's note is
correct** — `www.gov.bg` really does serve the Council of Ministers, which is what they wrote down.
What nothing checked is that the string they wrote could be *loaded*. `gov.bg` is on the Public
Suffix List, so `DestinationConfig` refuses it, and the refusal is right: trusting a public suffix
trusts every site beneath it, which is the whole failure mode entry 2 exists to prevent.

**The consequence is worse than a thin corpus, and that is the point worth keeping.** A country
whose corpus crawls badly still answers corridors from live search. A country whose *config* will
not construct fails at construction on every path — corpus build and request path alike. Bulgaria
had been sitting in the "55 researchable destinations" count while being researchable by nothing.

**The fix was already the file's own convention.** Brazil carries `www.gov.br` for exactly this
reason, and so do `www.gov.pl`, `www.gob.mx`, `www.gov.ie`, `www.gov.cy`, `www.gov.si` and
`www.gov.za`. Bulgaria now carries `www.gov.bg`, verified live: it returns 200 and titles itself
"Council of Ministers of the Republic of Bulgaria". A scan of all 55 committed rows found this was
the only one.

**What is new is the guard, not the correction.** `test_every_committed_row_builds_the_config_a
_corridor_needs` constructs a `DestinationConfig` from every committed row — the same object both
the corpus build and the request path make — and it fails on `gov.bg` and passes on `www.gov.bg`,
checked both ways rather than reasoned about. The existing committed-file test checked that each
reviewed domain *carries evidence*; it never checked that the domain *works*. With 143 countries
still to be added to that file, a convention that lived in six other rows and one person's memory
is now enforced.

---

## 112. A third traveller the corpus was never tuned for scores higher than the two it was built on

**2026-08-29 · the mini-goal's actual test**

Every number in this file came from two travellers — `IN/GB` and `PH/PH` — and entry 90's argument is
that one traveller cannot outvote 197. A Nigerian passport applying from Nigeria was run across the
ten built countries: a nationality needing a visa for all ten, applying from a country neither
existing traveller uses, with **no oracle row and no curation**. Corridor health is a free signal
(entries 99, 100), so `unresolved_roles` is the measurement and nothing had to be hand-built.

### The result

**52 of 60 role slots accounted for — 45 by a page and 7 by an official tool, 87%.** The twenty
corridors for the two tuned travellers read 99 of 120, **82.5%**. The traveller nobody optimised for
scored *higher* than the two the whole system was measured against.

Six of the ten countries account for all six roles — the United Kingdom, Japan and Singapore purely
from pages, Canada, France and Sweden with a tool. Of the eight gaps, **four are the United States**,
which is entry 109's block and a known ceiling. Excluding it, the other nine countries reach **50 of
54, 93%**.

### What makes it convincing is which pages were chosen

The corridors did not fall back on generic guidance. They found pages published **for Nigeria
specifically**, in five different countries, and each one exercises a different piece of machinery
built this week:

| page | what it demonstrates |
| --- | --- |
| `nigeria.diplo.de/ng-en/service/visastart` | entry 107's trust decision — the German mission network generalising to a traveller it was never checked against |
| `netherlandsworldwide.nl/…/schengen-visa/apply-nigeria` | the per-traveller family reservation, item 35 |
| `ica.gov.sg/…/visa-detail-page/nigeria` | Singapore's per-nationality family, which `coverage` calls *bounded by the authority* at 32 of 198 — Nigeria is one of the 32 |
| `visa-fees.homeoffice.gov.uk/y/nigeria/usd/visit/all` | entry 82's United Kingdom fee wall, which no crawl reaches at any budget and search seeded |
| `france-visas.gouv.fr/en/nigeria` | France's per-country page, readable only since entry 92's render budget |

**That is the mini-goal answered.** The store was built and tuned for two travellers and serves a
third at least as well, using the per-country pages rather than generic ones.

### What it does not show

One run per corridor, and entry 81's rule stands — role counts on a single corridor are noisy. There
is **no oracle for `NG/NG`**, so this measures whether the corridor filled its roles, not whether it
chose the pages a person would have named; those are different questions and entry 100 is what
happens when they are conflated. And ten countries is not 198.

Germany is the one country that filled `document_checklist` for both tuned travellers and **not** for
this one — `uk.diplo.de` and `manila.diplo.de` yielded it, `nigeria.diplo.de` did not. That is a
per-traveller gap of exactly the kind this exercise exists to surface, and it is not yet diagnosed.

---

## 111. Twelve more domains on the owner's judgement, and what that standard is

**2026-08-29 · trust decisions taken by the project owner · TODO item 2**

Entry 110 added six domains it could confirm independently and listed six countries where the
evidence was not there, saying `migracija.lt` and `regjeringen.no` were "almost certainly right, and
almost certainly is what this rule refuses". **The owner's answer was that almost certainly is fine.**
That is theirs to decide — the `reviewed` field exists precisely as the human escape hatch entries 33
and 34 designed — and what this entry does is make the standard explicit rather than let it blur.

### Nine countries, and none is thin any more

| | domains after | what was added |
| --- | --- | --- |
| Bulgaria | 3 | `mvr.bg`, `gov.bg` |
| Denmark | 4 | `nyidanmark.dk` |
| Iceland | 3 | `government.is`, `island.is` |
| Liechtenstein | 2 | `llv.li` |
| Lithuania | 4 | `migracija.lt`, `vrm.lt`, `mfa.lt` |
| Luxembourg | 3 | `mae.lu` |
| Norway | 3 | `norway.no`, `regjeringen.no` |
| Slovakia | 2 | `minv.sk` |

Every domain is under its own country's top-level domain, and every entry records the evidence that
supports it — **saying which kind it is**, because the kinds are not equal:

- **Read from the page itself**, which is real evidence: `norway.no` serves "The Norway Portal -
  Norwegian Ministry of Foreign Affairs"; `mae.lu` serves "Ministere des Affaires etrangeres et
  europeennes"; `government.is` serves "Government of Iceland"; `minv.sk` serves "Ministerstvo vnutra
  Slovenskej republiky"; `mvr.bg` serves Bulgaria's interior ministry in Cyrillic.
- **Judgement, marked as judgement**: `migracija.lt`, `vrm.lt`, `mfa.lt`, `regjeringen.no`, `llv.li`
  and `island.is` could not be read — four sit behind a Cloudflare challenge and two render
  client-side with no title — and Wikidata names none of them. Their entries say "Judgement" and
  "Owner's call" in the file, so a future reader can tell them from the confirmed ones without coming
  back here.

**Bulgaria and Slovakia were not promotions.** Their `unconfirmable` lists held nothing usable, so
their interior ministries were found by looking — which is how the other two thirds of the world will
have to be done.

### Two were still refused, and the owner's licence does not reach them

- **`iom.sk`** serves "Medzinárodná organizácia pre migráciu (IOM) Slovensko" — the **International**
  Organization for Migration's Slovak office. An intergovernmental body, not Slovakia's government.
  "Almost certainly right" is not the question when a domain is *certainly a different organisation*.
  Left in `unconfirmable` so the next reviewer meets it and refuses it too.
- **`liveinuruguay.uy`** serves "Live in Uruguay" and reads as a relocation promotion rather than an
  authority. Uruguay already has `www.gub.uy`, the whole-government portal, so nothing is lost.

Brazil and Uruguay therefore still carry one domain each, and that is the correct outcome rather than
an unfinished one.

### What the standard now is, said plainly

`reviewed` no longer means "independently confirmed". It means **a person decided, and the file says
what they had.** Three tiers live in it now — an independent source (Wikidata, TLS), the page's own
words, and judgement — and mixing them silently is the failure this entry exists to avoid. The rule
the file states is unchanged and still binds: **governmental *and* under the country's own top-level
domain**, which is what `iom.sk` fails on the first half while passing the second.

`visa-discover audit` still reads `row, no confirmable domain: 0` and 55 researchable. **Reachability
is unchanged** — all nine could already be researched from one domain. What changed is how much of
each government a corridor may see, which is what turned Germany's four open slots into six filled
ones (entry 108). Whether these nine gain the same way is untested.

---

## 110. Six domains for five countries — and the proposed lists were wrong about which domain to want

**2026-08-29 · trust decisions, recorded as `authority_domains.yaml` requires · TODO item 2**

Entry 107 fixed Germany and entry 108 measured what it bought. Eleven more countries were thin — nine
with a single domain, and Iceland and Liechtenstein **refused outright with none**. The obvious move
was to promote their `unconfirmable` entries. That move is wrong, and finding out why is the useful
part of this entry.

### The method that worked is the one entry 67 already named

Germany's warrant — an approved page naming the domain — needs a corpus, and these countries have
none. So the evidence came three ways:

- **Wikidata, by organisation** (entry 67's "ask Wikidata about the domain", run in reverse): look up
  the authority, read `P856` official website and `P17` country. This produced **`us.dk`**, the Danish
  Immigration Service; **`stjornarradid.is`**, the Government of Iceland; **`regierung.li`**, the
  Government of the Principality of Liechtenstein.
- **TLS, for one of fifteen.** `swiss-visa.ch` presents `O=Bundesamt für Justiz (BJ), C=CH` — the
  Swiss Federal Office of Justice, named in the certificate. The other fourteen candidates are
  domain-validated certificates naming nobody, which is entry 66's limit showing up worse than the 9
  of 16 it recorded.
- **Entry 107's two-part warrant**, for `denmark.dk` (named on the reviewed `um.dk`) and `public.lu`
  (named on the reviewed `gouvernement.lu`), both under their own top-level domain.

Every one was then fetched and serves a page identifying itself: *Udlændingestyrelsen*, *Regierung
des Fürstentums Liechtenstein*, *Online visa system*, *Welcome to the official website of Denmark*.

### The finding: `unconfirmable` is a list of guesses, not a shortlist

**Denmark's proposed domain was `nyidanmark.dk`** — "New to Denmark", which anyone would take for the
immigration portal. Wikidata gives the Danish Immigration Service's official website as **`us.dk`**,
which was **not in the proposed list at all**. **Iceland's proposals were `government.is` and
`island.is`**; the Government of Iceland's official website is **`stjornarradid.is`**, also absent.
**Liechtenstein's proposal was `llv.li`**; the government is at **`regierung.li`**.

Three for three, the right domain was not the proposed one. `unconfirmable` records what a search
turned up under the country's own top-level domain — it is not a ranked list of the authority's real
addresses, and reviewing it as though it were would have trusted three wrong domains while missing
three right ones. **Ask Wikidata for the organisation; do not promote from the list.**

### What was rejected

**`iom.sk` is the International Organization for Migration.** It is an intergovernmental body, not
Slovakia's government, so it fails the governmental half no matter how many Slovak pages link it or
that it sits under `.sk`. It is the clearest illustration in the file of why "under the right
top-level domain" is only half the rule, and it is left in `unconfirmable` deliberately — a future
reviewer should meet it and reject it again.

**Bulgaria, Brazil, Lithuania, Norway, Slovakia and Uruguay got nothing**, and that is the honest
outcome rather than a failure to try. Wikidata has no official website for Lithuania's Migration
Department, Slovakia's Interior Ministry, Uruguay's Dirección Nacional de Migración or Luxembourg's
MAE; the trusted homepages do not name the candidates; TLS names nobody. `migracija.lt` and
`regjeringen.no` are almost certainly right and "almost certainly" is the reasoning this rule exists
to refuse. They need a person with a source, which is what item 2 is.

### What it moved

`visa-discover audit` now reads **`row, no confirmable domain: 0`**, where two countries sat before,
and **55 researchable**. Iceland and Liechtenstein were refused before any page was fetched and are
now reachable. Whether they *answer* is stage 2 and untested — this entry only settles what may be
read.

---

## 109. `travel.state.gov` was never a challenge — it is a block, and we were rendering past it

**2026-08-29 · corrects entries 106 and 108, and closes a rule violation**

Asked why the United States' slots were unanswerable, the honest answer was that "three failed
renders" is thin evidence for "cannot be answered". Fetching the page settled it, and the answer is
not the one this file has been carrying.

### What `travel.state.gov` actually says

Under our own user agent it answers `403` with **"Sorry, you have been blocked. You are unable to
access travel.state.gov… The action you just performed triggered the security solution"**, and offers
to let us email the site owner. There is **no script to run**. Side by side with a genuine challenge:

| | `france-visas.gouv.fr` | `travel.state.gov` |
| --- | --- | --- |
| `cf-mitigated: challenge` | **yes** | no |
| `_cf_chl_opt` | **yes** | no |
| "Enable JavaScript and cookies to continue" | **yes** | no |
| `cdn-cgi/challenge-platform` | yes | **yes** |
| "you have been blocked" | no | **yes** |
| `<title>` | One moment please | Attention Required! \| Cloudflare |

**`cdn-cgi/challenge-platform` is Cloudflare scaffolding common to the challenge page and the block
page**, and it was in `CHALLENGE_BODY_MARKERS`. It is the only marker `travel.state.gov` carries.

### Three things that were wrong because of one marker

1. **We pointed the renderer at a page an authority refused**, three times per host per build. Entry
   18 forbids that outright — it is the first thing on the list, above retries and user-agent
   spoofing. It was not a judgement call anybody made; a shared string made a refusal look like a
   question.
2. **The recorded reason was false.** The corpus stored *"it asked this client to prove it is a
   browser (HTTP 403), and that challenge could not be answered here"* about a page that says it
   blocked us. CLAUDE.md's rule is that the reason reported must be true of what was seen, and this
   one was not.
3. **The corridor could not use the outcome entries 27 and 32 exist for.** A settled refusal on a
   credible `visa_decision` page may *qualify* the corridor — naming the page so the traveller opens
   it themselves. Misread as an unanswered challenge, it named nothing and the corridor simply
   failed.

### The fix

`cdn-cgi/challenge-platform` is removed; `_cf_chl_opt`, `azure waf js challenge` and the
`cf-mitigated` header remain and each correctly separates the two pages. A **negative** guard is
added and **checked first**: a body carrying "you have been blocked" or "attention required" is a
refusal whatever else it carries, including a `cf-mitigated: challenge` header. That ordering is the
point — the cost of being wrong is asymmetric, and a marker that starts appearing on block pages
would otherwise silently reopen the violation.

The test fixtures were part of the problem: both used a challenge body whose *only* marker was the
shared one, so nothing could have caught this. They now carry `_cf_chl_opt` like a real challenge,
and a new fixture is the real block page — **keeping** the shared marker, so the guard has to hold
because the page says it blocked us rather than because the marker went away.

### Verified end to end, and the corridor's outcome changed

The reason is correct — both corridors report *"travel.state.gov could not be read because the
authority refused automated retrieval (HTTP 403), so its guidance could not be independently verified
here"* — and the outcome moved with it. **`united-states/PH/PH` now records
`cause=resolved_decision_blocked` where it recorded `decision_not_found`**, and both corridors exit
resolved-with-gaps rather than refused. The third model call is `_decision_blocking` judging the
refused page a credible `visa_decision` candidate from its address and label alone, which is entry
57's bound.

`POST /visa-plans` for `united-states/IN/GB/tourism` **returned a plan where it previously returned a
503 with nothing**:

- `visa_required: None` and `status: partial` — the override holding, and `verified` unreachable
- *"The visa decision could not be verified because United States authority (travel.state.gov)
  guidance could not be read here."*
- **six** `travel.state.gov` URLs listed as `blocked`, each with the true reason
- an unresolved question giving the traveller the exact page to open themselves
- a first step that says to open it

That is entries 27, 32 and 57 working as designed, on a corridor that had been silently failing
because one string made a refusal look like a question. **The five US role slots are still unfilled
and still a ceiling** — what changed is that the traveller is now told the truth and handed the link
instead of getting nothing.

### What this corrects

Entry 108 called the United States "a real ceiling, not a backlog" because "the challenge is not
answerable by our renderer". **It was never a challenge**, so the ceiling is real for a different and
better-understood reason: the authority refuses this client, which is a fact we may *report* rather
than a capability we lack. Entry 106's "a browser challenge nobody could answer" is wrong in the same
way. The five US slots stay unfilled either way; what changes is that the traveller can now be told
the truth about why.

---

## 108. Germany's rebuild closed three of four slots; the United States' closed none

**2026-08-29 · the measured outcome of entry 107 and of the US render question**

Both rebuilds ran. One worked and one did not, and the failure is as useful as the success.

### Germany: 1 host to 87, and the checklist arrived

`diplo.de` trusted, corpus rebuilt: **1,565 entries on one host → 5,712 entries across 87 hosts**,
4,147 of them new, and the text index 389 → 1,530 pages. The oracle travellers' own missions are now
held — `uk.diplo.de` at 226 pages, `manila.diplo.de` at 133 — and the corpus holds real artefacts it
never could before, like `canada.diplo.de/…/checklist-tourist-visa`.

Live, against entry 106's prediction of four slots:

| corridor | before | after |
| --- | --- | --- |
| `germany/IN/GB` | 4 roles, no checklist | **5** — `document_checklist` from `uk.diplo.de/…/what-documents-do-i-need-for-a-c-visa` |
| `germany/PH/PH` | 4 roles, no checklist | **6 of 6** — checklist, route, fees and times all off one Manila page, entry off another |

**Three of the four predicted slots closed**, both `document_checklist` and one `general_entry`.
`general_entry` for `IN/GB` is still open. The prediction was four and the result is three, which is
recorded that way rather than rounded.

The mechanism is exactly what entry 106 argued: the ministry defers to its missions for documents,
and the missions were unreachable by committed data rather than by crawl budget.

### The United States: rebuilt, and the challenge still cannot be answered

The US corpus predated the render fix — built 2026-08-27, and `DEFAULT_CORPUS_RENDERS = 400` landed
2026-08-28 — so it had never been given a budget that could answer a challenge. It has now.
**`travel.state.gov` still holds zero stored pages.** 76 entries, 73 never opened, 3 marked
unreadable with the same recorded reason, which is `CHALLENGE_FAILURES_PER_HOST` giving up after
three consecutive failures. The index grew 467 → 576 pages from elsewhere.

Both US corridors are unchanged: `visa_decision` and `document_checklist` still unidentified for
both travellers.

**So the US's five slots are a genuine ceiling, not a backlog.** Entry 41 permits answering a
challenge and this one is not answerable by our renderer; entry 18 forbids working around it by any
other means. What remains readable is `adoption.state.gov`, the partial mirror entry 87 found. This
is the honest end of that line unless the mirror is deliberately leaned on, which is its own
decision.

### Where the ceiling stands

Of entry 106's nine open slots: **three closed, six remain** — one `general_entry` in Germany and
five in the United States behind a challenge nobody can answer. Against the twenty corridors, the
four Singapore slots still correctly do not arise.

---

## 107. `diplo.de` is reviewed and trusted, because the ministry itself names it

**2026-08-29 · decided by the project owner · a trust decision, recorded as `authority_domains.yaml`
requires**

Entry 106 traced four of Germany's open role slots to one line of committed data: **`diplo.de` sat in
`unconfirmable`**, so no German mission was ever fetched, so Germany's corpus was 1,565 entries and
**every one of them `www.auswaertiges-amt.de`**. The Federal Foreign Office defers to its missions
for documents in its own words. The ministry could be crawled forever and never answer
`document_checklist`.

### The evidence, and the two sources that did not work

- **TLS did not confirm it.** `diplo.de`, `uk.diplo.de` and `manila.diplo.de` all present
  `CN=*.diplo.de` issued by Let's Encrypt — a domain-validated wildcard naming **no organisation**.
  That is entry 66's measured limit ("TLS names the authority for 9 of 16") and it is why the
  generator filed the domain unconfirmable rather than wrongly.
- **The corpus could not confirm it either**, and for a reason worth noting: it holds **zero**
  `diplo.de` addresses, because `is_crawlable` rejects an untrusted domain before recording it. A
  domain the rule refuses leaves no trace to argue from, which is a small trap for anyone trying to
  review one from stored data.
- **The stored page text did.** `auswaertiges-amt.de` — already reviewed and trusted — publishes on
  its own country-information page: *"Website http://www.washington.diplo.de"*, under the heading
  **"Consulate General of the Federal Republic of Germany"**. Thirty-six stored pages on the trusted
  host mention it.

That is **entry 89's two-part warrant**, which was written for contractors and applies unchanged
here: an approved government page names it, **and** its registrable domain is under the destination
country's own top-level domain. Either half alone fails closed; both together are what the trust rule
has always asked for, arrived at by a route the generator cannot take.

### What was deliberately not done

**`bundesregierung.de` stays `unconfirmable`.** It is the federal government's portal, it is not
where visa guidance lives, and the case above is specifically about missions. A trust decision should
move exactly the domain the evidence covers — widening to "the German government" is the "looks
official" reasoning the rule exists to refuse.

**The rule itself is unchanged.** This is the `reviewed` escape hatch entries 33 and 34 designed for
governments that mark no hostname, used as designed and with the evidence written down. Nothing about
`auto_trusted_domains` moves, and no other country is affected.

### What it should buy, stated before the rebuild

Four role slots: `document_checklist` and `general_entry` for both oracle travellers into Germany.
The mission pages are where the documents are named. Whether the crawl reaches them is a separate
question from whether it is allowed to, and this entry only settles the second.

---

## 106. The ceiling: nine open slots, two countries, two causes — and the selector A/B is closed

**2026-08-29 · decided by the project owner (stop the A/B) · classification run the same day**

Two things, and the first is a decision rather than a finding.

### The selector experiment is closed

The model beats the heuristic and has done so on every measurement since entry 84 — most recently
**90% against 59% at matched budget** (entry 105). The question is settled, `discovery_selector:
model` is shipped, and **the twenty corridors are no longer re-run to refresh that number.**
`visa-discover selection-recall` stays as a regression check anybody can run offline; what stops is
treating its figure as a headline and spending quota to keep it current. Read entries 87 and 100
before quoting it at all: it measures agreement with pages a person named, its known errors run
against the model, and the number is a floor.

### The ceiling, which is what the corpus work is actually judged against

The goal is a corpus that answers most travellers for the ten countries built, and "99 of 120 roles"
does not say whether the remaining 21 are *findable*. Classified:

| cause | slots | fillable? |
| --- | --- | --- |
| Singapore, visa-free | **4** | **No, and correct** — no application, so no checklist, route, fee or wait (entry 94) |
| Closed by entries 103–104 | **7** | Already fixed — France's times ×2, the Netherlands' fees, Canada's and Japan's entry, the US route |
| **Germany** | **4** | **Yes — one reviewed domain** |
| **United States** | **5** | **Only if a challenge can be answered** |

Nine slots remain, in two countries, with one cause each.

### Germany: its corpus is one host, because its missions are `unconfirmable`

Germany's corpus is **1,565 entries and every one is `www.auswaertiges-amt.de`**. Not one mission
page. The Federal Foreign Office defers in its own words — *"you should consult the requirements well
in advance of your departure date to find out about the documentation which has to be submitted"* —
and the mission is what names documents.

`authority_domains.yaml` explains it exactly: **`diplo.de` is listed `unconfirmable`.** It is under
Germany's own top-level domain and carries no governmental hostname marker, so the rule refuses it,
so it is never fetched, so no German mission is in the corpus. That is **entry 33's measured defect
biting one country in a countable way**, and entry 34 already names the remedy: a reviewed domain in
committed data. `diplo.de` is the Federal Foreign Office's own mission network — `uk.diplo.de`,
`manila.diplo.de` — so the evidence for reviewing it is the same evidence that justified
`auswaertiges-amt.de`.

**Not done here, because it is a trust decision.** The file says editing `trusted` by hand is one, and
it belongs to [TODO.md](TODO.md) item 2 with its reasoning written down, not to a classification
exercise.

### The United States: `travel.state.gov` answers a challenge nobody could answer

70 `travel.state.gov` entries are in the corpus, **67 never opened and 3 marked unreadable**, with the
recorded reason *"it asked this client to prove it is a browser (HTTP 403), and that challenge could
not be answered here"*. The index holds **zero** pages from it and 24 from `adoption.state.gov`,
which entry 87 found publishes the same tree and is the only reason any of it is readable.

All five US slots are that one cause. Entry 92 counted the US at 19 unanswered challenges and
predicted little from fixing it, on the grounds that `egov.uscis.gov` and `ceac.state.gov` are
application portals — **which was the wrong host to look at.** `travel.state.gov` is the United
States' entire visa guidance tree.

Entry 41 permits answering a challenge, so this is allowed; whether our renderer *can* answer this
one is untested, and `CHALLENGE_FAILURES_PER_HOST` gives up after three.

### What this says about the corpus

Of 120 role slots over twenty corridors, **four should never be filled, seven were filled this week,
and the remaining nine are two known defects with owners.** The corpus is not 21 problems away from
serving these countries; it is two.

---

## 105. The vocabulary work verified end to end, and a role scoring zero can still be filled

**2026-08-29 · re-runs the twenty corridors under entries 103 and 104**

Entries 103 and 104 changed how three roles rank and measured it **offline only** — contention
counts and top pages. Nothing had confirmed a corridor filled more roles. The twenty corridors were
re-run, which also refreshed recall logs that had gone stale: they were written under the old
lexicon, and `selection-recall` replays from them.

### The falsifiable prediction held

Sweden's `processing_times` went from **zero scoring candidates to fifteen** offline. Live, the
corridor now fills both `fees` and `processing_times` off
`migrationsverket.se/…/visiting-sweden-for-up-to-90-days-entry-visa`, with the adjudicator quoting
**"the Schengen visa fee is EUR 90"** and **"a decision is normally made within 15 days"**. Both were
unfilled before.

### What moved, and the caveat that governs how to read it

Roles accounted for — filled by a page or named as a tool — across the nineteen corridors comparable
between runs: **91 → 97 of 114.** Nine gains against four losses. The largest single move is
`united-arab-emirates/PH/PH` at 2 → 6.

**Entry 81's rule applies and must not be waved past**: role count on one corridor is noisy — six runs
of identical code gave 4, 4, 4, 4, 5 and 6. So a corridor moving by one is nothing, and the losses
(`visa_decision` in UAE `IN/GB` and `netherlands/PH/PH`, `document_checklist` in `sweden/IN/GB`) are
as likely variance as regression. What survives that caveat is the aggregate direction and Sweden's
two roles, where the mechanism is visible in the adjudicator's own words.

### Selection recall, which is the cleaner instrument, and it splits

| arm | before | after |
| --- | --- | --- |
| heuristic, matched budget | 41/88 — 47% | **52/88 — 59%** |
| model | 81/88 — 92% | 79/88 — 90% |
| heuristic, shipped budget | 78/88 — 89% | 76/88 — 86% |
| tools found by the model | 7/12 | **10/12** |

**The arm that gained is the arm made of vocabulary.** The heuristic *is* the ranking, so better
words move it directly: +12 points. The model reads stored text and was already at 92; a wider
contention set hands it more candidates, some of them noise, and it dipped two points. The model's
lead over the matched heuristic narrows from +45 to +31 and is still large.

That split matters more than it looks. **The heuristic is what serves the 43 countries with no text
index** — a country without one falls back to it and says so in the corridor's notes. This change
helps them most, and they are the ones stage 3 is about.

### The correction: a role scoring zero candidates can still be filled

Entries 103 and 104 both say "a page scoring nothing for a role can never be selected *for* that role
at any budget". True, and it does not mean the role goes unanswered. **Germany proves it.** It scores
**zero** candidates for `fees` and for `processing_times`, and it fills both — off
`auswaertiges-amt.de/en/visa-service/215870-215870`, a page that entered contention on
`application_route` and which the adjudicator then read as also stating "the normal processing fee
for a Schengen visa is EUR 90" and "up to 15 calendar days to decide".

**A page enters contention on its best role; the adjudicator assigns roles afterwards, from the
text.** So a zero-candidate role is a *selection* defect, not necessarily a coverage one, and the
vocabulary work should be understood as buying better fetches rather than directly buying answers.
That is exactly the shape of the result above: the ranking arm gained twelve points and the
role-filling total gained six, noisily.

It also softens entry 103's Germany conclusion. "Its problem is discovery and no scoring change
reaches it" is true of Germany's *corpus* and not of its corridors, because the live candidate set is
**corpus ∪ live search** (entry 47) and search supplies what the corpus lacks.

---

## 104. `fees` and `processing_times` get the same treatment, and one term is rejected for a reason worth keeping

**2026-08-29 · TODO item 35 · finishes what entry 103 measured**

Entry 103 found that the three roles with four terms or fewer were exactly the three producing no
scoring candidate at all, and widened one of them so its effect could be attributed. This does the
other two. `fees` had four terms, all saying "fee" or "charge"; `processing_times` had three, two of
which were the same phrase singular and plural.

### Measured across the twenty corridors

**Corridors scoring zero for `fees` or `processing_times`: 14 → 10.**

| | before | after |
| --- | --- | --- |
| `sweden` ×2, processing times | **0** | **15, top 46.4** |
| `singapore` ×2, fees | **0** | 3, top 18 |
| `netherlands` ×2, fees | 31, top 64 | **76, top 112.8** |
| `canada` ×2, fees | 40, top 34 | 53, top 51 |
| `germany` ×2, both | 0 | **still 0** |
| `france`/`united-arab-emirates`, times | 0 | still 0 |

Sweden's is the clean win and the clean diagnosis: GOV.UK publishes "visa decision **waiting**
times" and Migrationsverket puts `you-are-waiting-for-a-decision` in the URL path, and **neither
contains the word "processing"**. Its new top candidate is that page at 46.4, where before nothing
scored at all. The Netherlands' is the other: `consular fee` reaches `consular-fees/india`, the page
published for that traveller, at **112.8**.

Germany stays at zero for both, as it did for `general_entry` and for the same reason — its pages are
in the text index by cache backfill and not in its corpus. Three roles now point at the same
conclusion: **Germany's problem is discovery, and no scoring change will touch it.**

### The term that was rejected, which is the part worth keeping

`payment`, weight 10, looked like the best addition in the set. On the numbers it raised Canada's top
fee candidate from **51 to 61** and the United States' from 27 to 32, and dropping it cost those and
gained only the loss of two Swedish candidates scoring 3.0 and 2.0.

Reading the pages behind the score, it had promoted `eservices.cic.gc.ca/epay/order.do` — **"Pay Your
Application Fees, Online Payment"** — above the fee schedule. A traveller needs the amount, not the
till. It is dropped, and a test asserts a page stating a fee outranks a page collecting one.

**A score that rose is not a page that improved.** That is entry 81's rule — grade the shortlist, not
the metric that moved — reached in a vocabulary change, and it is the second time in two entries that
a count-and-score summary hid the thing that mattered. The first was `customs` in entry 103, kept
because it could not be attributed in a change of thirteen terms; it is still there and still pulling
Canada's vehicle-import page, and it should be re-checked on its own.

### The damage check, which is the same one entry 103 used

The top page for `visa_decision`, `document_checklist`, `application_route` and `general_entry`,
across the nine corridors any of these roles moved in, before against after: **identical, every one.**

---

## 103. The roles that go unanswered are the roles with the fewest words

**2026-08-29 · TODO item 35 · widens `general_entry`, and corrects two numbers this file was
carrying**

### Two corrections first, because the second changed what got built

**`document_checklist` is not the dominant gap.** Entries 99 to 102 and the handoff all said it was
unfilled in 8 of 20 corridors and "the only role that recurs". That came from `unresolved_roles` in
the recall logs, **which counts a role handed to a questionnaire as unresolved** — the exact
conflation entry 93 fixed for the coverage metric, read back in through a different file. Against the
oracle with tool-settled and does-not-arise roles removed, **16 of 120 role slots are genuinely
open** — 87% accounted for — and they fall out like this:

| role | terms in the lexicon | corridors of 20 with **zero** scoring candidates | genuinely open |
| --- | --- | --- | --- |
| `visa_decision` | 18 | 0 | 1 |
| `application_route` | 13 | 0 | 1 |
| `document_checklist` | 8 | 0 | 3 |
| `fees` | 4 | 6 | 1 |
| `processing_times` | 3 | 8 | 3 |
| **`general_entry`** | **3** | **4** | **7** |

**The three roles with four terms or fewer are exactly the three that produce no candidates at all**,
and they hold 11 of the 16 open slots. A page scoring zero for a role is not merely ranked low — it
can never be shortlisted or selected *for that role* at any budget. That is entry 78's finding
(`document_checklist` filed as `visa_decision`, unrecoverable at any shortlist depth) in a second
place, reached from the opposite direction: there, one page had the wrong role; here, no page has
the role at all.

**And the delegated-checklist column would change nothing measurable.** The owner is right that a VFS
Global link the plan already hands over should count as accounted-for — it is entry 93's defect one
instance later, and it is filed. But measured, France's open role is `processing_times` and the
Netherlands' are `general_entry` and `fees`; both already answer the checklist. An earlier claim that
it "would change the Netherlands most" was reasoning from 236 recorded delegations, not from any
role it unblocks.

### What the seven open `general_entry` slots actually are

The oracle records a reason per slot, and they are not one thing:

- **Nothing scores at all** — `germany` ×2, `japan/PH/PH`, whose reason says outright "no candidate
  scored above zero for it". Confirmed live: **0 of 83** candidates score in Germany, **0 of 99** in
  Japan.
- **The page present is the wrong one** — `netherlands` ×2, where the only entry-condition candidate
  is the ETIAS page, which is for travellers who need no visa. A correct exclusion, not a defect.
- **Wrong pages present** — `canada/PH/PH`, whose candidates are a vehicle-import page and a
  customs-on-return page. Both attracted by `customs`, a term in this very role.
- **Nothing states it** — `united-states/PH/PH`.

So widening the vocabulary could only ever fix some of the seven, and that was said before the terms
were written rather than discovered after.

### The change, and what it bought

Thirteen terms, from pages already read: `landing permission` (Japan), `means of subsistence` and
`travel insurance` (Germany's Schengen rule), `sufficient funds` and `onward travel` (Singapore),
`entry conditions`, `immigration clearance`, `period of stay` and the rest. `entry requirements` was
deliberately **not** added — it is already `visa_decision`'s at weight 12, and one phrase deciding
two roles is its own defect.

Measured across all twenty corridors, before and after:

| | before | after |
| --- | --- | --- |
| `japan/IN/GB`, `japan/PH/PH` | **0**, **0** | **2**, **1** |
| `united-kingdom` ×2 | 10 candidates, top 30 | **23, top 43** |
| `sweden` ×2 | 4, top 24 | **9, top 31** |
| `canada` ×2 | 19, top 24 | 22, top 31 |
| `france/IN/GB` | 2, top 42 | 3, top 64 |
| `germany` ×2 | 0 | **still 0** |

Japan is the case the oracle named, and it moves. **Germany does not, and was predicted not to**: its
entry-condition pages are in the *text index* — put there by a cache backfill — and **not in its
corpus**, so no scoring change can reach them. That is a discovery gap and belongs to item 30.

**The damage check is the one that matters and it is clean.** Two corridors lost a single
`visa_decision` candidate each — 96→95, 73→72 — with the top score unchanged, which is a page whose
best role became `general_entry`. Comparing the **top page for every other role** across the five
affected corridors, before against after: **identical, every one.** Entry 81's rule — grade the
shortlist, not the plan — applied to a vocabulary change.

### What was left alone, deliberately

`customs` stays at weight 8 despite being the term that pulled Canada's vehicle-import page in.
Removing it in the same change that adds thirteen terms would make neither attributable, and the new
terms outrank it three-to-one. Re-check it against a measurement of its own.

`fees` and `processing_times` are untouched. The table above says they have the same defect — 6 and 8
corridors with no candidate at all — and fixing them is the same shape of work, but this entry
changed one role so that one role's effect could be read.

---

## 102. A family needs a visa word, not merely a government word

**2026-08-29 · TODO item 35, step 1 · narrows `CORPUS_FAMILY_PATTERN`**

Entry 101 found the Netherlands held at `incomplete` by three families no corridor could use, all
admitted by a gate that keyword-matches the address on
`visa|permit|entry|checklist|consular|appointment|apply|immigrat|fees`. Three of those tokens —
**`apply`, `appointment`, `fees`** — are words every public service in the world uses, and they are
what let in `passport-id-card/abroad/apply-{}` (Dutch citizens renewing a passport) and
`making-appointment/{}` (booking, which this project never does).

The pattern now requires a visa-domain word: `visa|permit|immigrat|consular|checklist|entry`.

### Measured before it was written, over all ten corpora

It drops **exactly those two families and keeps every other family in every country** — 13 Dutch
families become 11, and AE, CA, DE, FR, GB, JP, SE, SG and US are unchanged to the family. Two
survivals were the ones worth checking: `consular-fees/{}` keeps its place on `consular` rather than
on `fees`, and the United Kingdom's fee wall keeps its place on `visa`.

It also stops the crawl reserving budget for them, because `corpus_build` passes the same pattern to
`LinkCrawler`. That is a second, quieter win: 40% of an offline build is reserved for families, and
two of the Netherlands' were passport renewals and appointment bookings.

### What it does not fix, asserted in a test so it stays visible

`caribbean-visa/short-stay/apply-{}` matches on `visa` and survives. It is the Kingdom's **Caribbean**
visa — Aruba, Curaçao, Bonaire, all outside Schengen — so for a `netherlands` corridor it is the
**wrong** answer rather than a useless one. Excluding it needs a notion of territory this gate does
not have, and `coverage` is offline with no model by design (entry 90), so the fix is not "ask a
model". A test asserts the pattern still admits it, so the limitation cannot quietly be believed
solved.

### The verdict text was also wrong and is fixed

`incomplete` read *"a gateway family is held but mostly unopened; a rebuild buys coverage"*. Entry
101 measured that a rebuild buys nothing — it re-walks its search seeds — so the advice now says a
crawl seeded from the recorded addresses is the only thing that reaches them.

### Where the Netherlands stands after this

Still `incomplete`, and every reason is now real: `airport-transit-visa/apply-{}` at **52% read**
(in scope — it serves the `transit` purpose), `mvv-long-stay/apply-{}` at 1% (long-stay, arguably
not this product's business), and the Caribbean family above. The schengen family that actually
serves tourism reads **100%**.

---

## 101. A rebuild cannot open what a build recorded, and the gate was counting the wrong thing

**2026-08-29 · TODO item 35's first job, run and diagnosed rather than completed**

Item 35 said: rebuild the Netherlands, and `visa-discover coverage --country NL` flipping off
`incomplete` is the acceptance test. The rebuild was run. **42 queries, 162 seeds, 2,965 pages
crawled, 919 indexed — 27 new entries and no change of verdict.** Three things came out of that,
and none of them is "crawl harder".

### A rebuild re-walks the same ground, by construction

`build_corpus` seeds the crawl from **search results only**; the existing corpus is merged in
afterwards and is never a frontier. Same queries, same seeds, same scores, same walk. **An address a
build recorded and left unfetched stays unfetched however many times the build is re-run.** Entry
88's "a build opens 3 to 15% of what it records" is therefore not a budget symptom that a rebuild
buys back — it is structural, and item 35's acceptance test could never have passed.

### The gate's `opened` column was wrong by 2.6×

`opened` counted a member that some other entry names as its `discovered_from` — a member that
**fathered a recorded link**. A member that was fetched and linked nothing therefore read as never
fetched:

| Dutch family | counted `opened` | actually fetched |
| --- | --- | --- |
| `schengen-visa/apply-{}` | 72 | **185** |
| `entry-visa/apply-{}` | 61 | **204** |
| `consular-fees/{}` | 42 | **183** |

The schengen gap is **113**, and 113 is a number this project already had written down: item 35's own
warning says *"of 185 gateway pages read, 113 link nothing and 58 link only language forks, because
for most residences the Netherlands publishes its checklist on VFS Global"*. **The gate was
reporting entry 89's contractor ceiling as a crawl gap**, and advising a rebuild to go and fetch
pages it already held.

`Family.read` is now `max(opened, text_held)` — the maximum because neither signal is sound alone:
the index misses a page fetched with no readable body, and `discovered_from` misses a page that led
nowhere. The verdict is computed from it. A country with no text index falls back to `opened` and
behaves exactly as before.

**`shape` deliberately stays on `opened`.** It divides country-named children by opened members, so
both sides have to be counted the same way; swapping `read` into the denominator alone turns 168
children over 72 into 168 over 185 and flips the Dutch schengen family — a gateway by any reading —
to `leaf`. Two tests pin this, one per direction.

### What that changed, and what it did not

Schengen goes **39% → 100% read**, `entry-visa` to 94%, `consular-fees` to 99%. **The verdict is
still `incomplete`, and now for honest reasons**: five families really are unread — and three of
them should never have been in the count at all.

### Three of the families holding the verdict are out of scope, and their own headings say so

- `passport-id-card/abroad/apply-{}` — *"Applying for your Dutch passport or ID card"*. For Dutch
  citizens abroad. No visa applicant needs it.
- `caribbean-visa/short-stay/apply-{}` — *"Applying for a short-stay **Caribbean** visa"*. Aruba,
  Curaçao, Bonaire — outside Schengen. Serving it to a `netherlands` tourism corridor would be
  **wrong**, not merely useless.
- `making-appointment/{}` — booking, which is permanently out of scope.

All three pass `CORPUS_FAMILY_PATTERN`, which keyword-matches the address on
`visa|permit|entry|checklist|consular|appointment|apply|immigrat|fees`. It cannot tell "apply for a
Dutch passport" from "apply for a visa" — the keyword-versus-meaning problem entry 57 settled for
blocked pages, in a new place. **Not fixed here**, because tightening the pattern per country is
whack-a-mole and the alternative — asking whether a family could answer a role for a corridor into
this destination — is a design change that should be argued on its own.

What remains genuinely unread and genuinely in scope is **`airport-transit-visa/apply-{}` at 52%**,
which serves the `transit` purpose, and arguably `mvv-long-stay/apply-{}` at 1%, which does not.

### What was rejected

- **Raising the page budget or the family share.** Neither bound: the last build opened 661 pages
  against a 1,200 budget and 290 on `netherlandsworldwide.nl` against a 400 per-host cap.
- **Reading `opened` as fetched everywhere.** It breaks `shape`, measurably and in the direction
  that hides a gateway.
- **Seeding the crawl from the corpus's unfetched addresses.** It is the fix for the first finding
  and it is a real change to crawl shape — 600 depth-0 seeds where there were 162 — so it needs its
  own decision, and on this country it would spend that budget on Dutch passport renewals.

---

## 100. The oracle is left wrong on purpose, because every distortion in it runs one way

**2026-08-28 · decided by the project owner · how `selection-recall` is read and maintained**

Entry 99 found that `united-kingdom/PH/PH` scores 2 of 5 while filling every role, and said "the
oracle simply named a different page". Looking properly, its three misses are **three different
things**, and only one of them is that:

| role | what is actually going on |
| --- | --- |
| `processing_times` | **not a miss.** `visa-decision-waiting-times-applications-outside-the-uk` and the `visa-processing-times-applications-outside-the-uk` the oracle names hold the **same 7,003 bytes, same SHA**, along with a third address. GOV.UK renamed the page and kept them all live |
| `fees` | **the oracle is wrong.** `gov.uk/visa-fees` states no fee — its body is "Use this tool to work out the cost… Start now on the Home Office website". Its `why` calls it "the published fee schedule for every visa type", which is false of that page. It is a **tool** by entries 59–60 |
| `general_entry` | genuinely different — nothing fetched matches the oracle's page by content hash or looks like an alias of it |

Both of the first two are error classes entry 87 already found and fixed once each: the alias
(ICA at three addresses) and the page whose title is not its content (`imm5484.html`). They recur
because the fix was applied to a row rather than to the method.

### Why nothing is being corrected

**A content-hash matcher was designed and declined.** It would fix the alias class in every country
permanently and cannot be gamed toward one arm. It was declined because it addresses the narrowest
of the three, does nothing for the other two, and would make the figure *look* more precise than the
ground truth under it is — which is what invited this number to be over-read twice in one day.

**The instrument is an A/B, and errors that hit every arm cancel.** `selection-recall` exists to say
whether the model picks better than the heuristic. A row that names a stale URL or credits the wrong
page penalises whichever arm did not fetch that exact URL, which is usually all of them. The absolute
figure suffers; the comparison does not.

**And the errors that do not cancel run against the model.** Aliasing only bites when an arm fetches
the answer at an address the oracle does not name — and the more pages an arm reads, the likelier it
also hits the named one. So it penalises the **low-budget** arms:

- **92% model against 47% matched heuristic** — both read 203 pages, so aliasing roughly cancels and
  this comparison stands as measured.
- **92% model against 89% shipped heuristic** — the heuristic reads 700. That gap is **understated**.

So the reported number is a **floor**. An instrument that under-flatters the thing it is being used
to advocate for is erring in the right direction, and that is the whole warrant for leaving it.

### The rule going forward

**Audit a row when it scores especially low; do not audit on a schedule and do not rebuild the
grader.** A low row means *go read what the row names* — not that the selector is broken. Both
directions are now proven in one sitting: `united-kingdom/PH/PH` reads 2/5 and filled every role,
`united-arab-emirates/PH/PH` reads 6/6 and left the checklist unfilled.

**Corridor health is a different, free signal and stays separate:** `unresolved_roles` in the recall
log. Never substitute one for the other — entry 99 is what happens when they are conflated.

**Whoever re-curates the United Kingdom row must not read a recall log first.** Both corrections
identified above would *raise* the model's score, and they were found by someone who had spent an
afternoon looking at what the model picked. The row carries a note saying exactly this, so the
warning travels with the data rather than living here.

---

## 99. Text coverage is not the constraint, and `selection-recall` does not measure what it looks like

**2026-08-28 · kills TODO item 40 before it was built, and corrects entry 87's headline reading**

Item 40 proposed letting curation fetch a page the index does not hold. Asked to build it, the
better version looked like a **corpus-build** pass filling the index for every recorded-but-unopened
entry — 29,641 of 40,718 corpus entries hold no text, and in contention only **46%** do, so the
model selector was choosing blind on more than half of what it saw. The project owner asked the
question that killed it: *France has 7% coverage and fills five of six roles — do we fetch for
everything, or only where a role is unfilled?*

### Coverage does not predict recall, measured three ways

| | |
| --- | --- |
| corridors that missed an oracle page (5) | mean contention coverage **44%** |
| corridors that hit every oracle page (15) | mean contention coverage **51%** |

Seven points on n=5 against n=15 is noise, and the extremes run backwards: **France at 6–7% scores
100%** for both travellers, while **the United Kingdom at 81% — the second-highest — scores 40%**.

Then the direct test, which is the one that settles it. All **7 missed roles across 20 corridors**
were pages already in the candidate set and already scored; not one was absent, and **all eight of
those pages held stored text the model had read**. `gov.uk/visa-fees` scored **134.4 as `fees`** —
the top candidate for the role it fills, 951 characters in the index — and was passed over. Adding
text to more pages cannot improve a choice made among pages that already had text.

**So the pass was not built, and item 40 is dropped rather than rewritten.** The 46% is real and is
not, on this evidence, costing anything.

### Why the United Kingdom looked worst and is not

`united-kingdom/PH/PH` scores **2 of 5** against the oracle and its recall log says
`unresolved_roles: []` — **every role filled, corridor resolved.** The model chose
`visa-fees.homeoffice.gov.uk/y/philippines/…`, the fee page keyed to this traveller, over the generic
`gov.uk/visa-fees` the oracle names.

**"The oracle simply named a different page" was this entry's first reading of that and it is wrong
for two of the three roles — see entry 100.** `processing_times` is the *same document* at another
of its three live addresses, and the `fees` row credits a page that states no fee. Only
`general_entry` is the different-but-valid case described here. Entry 98's handoff called this row "the weakest in the new grading and the place to look next";
it is the opposite.

### The two numbers are nearly uncorrelated, and this is the durable finding

| corridor | oracle | actually unfilled |
| --- | --- | --- |
| `united-kingdom/PH/PH` | 2/5 | — none |
| `canada/PH/PH` | 4/5 | — none |
| `united-arab-emirates/PH/PH` | **6/6** | `document_checklist` |
| `germany/IN/GB` | **4/4** | `document_checklist` |

A perfect oracle score sits on top of an unfilled role; a poor one sits on a complete corridor.
`selection-recall` measures **agreement with pages a person named**, not whether the traveller got an
answer. Entry 87's 92% should be read as "the model reads 92% of the specific pages we curated" — it
is the right metric for grading a *selector against a selector*, which is what it exists for, and it
is the wrong number to quote for coverage or for corridor health. The CLI legend now says so, because
this entry is the second time the two have been conflated.

### What the corridors actually lack

Reading `unresolved_roles` across the twenty: `document_checklist` is unfilled in **9**, of which
Singapore's is correct — the question does not arise for a visa-free traveller (entry 94) — so
**8 genuine gaps, and it is the only role that recurs.** `visa_decision` is unfilled in 7, but 5 of
those are `resolved_decision_tool`, which entry 63 settled as a resolution; the two real ones are
**the United States, for both travellers**, which is `decision_not_found`.

Entry 88 already diagnosed the checklist gap — the page is one hop below something the crawl recorded
and never opened, or the authority contracted it out. That is **item 35**, and it is what should be
next.

### What was rejected

- **Filling the index for every unopened entry.** 29,641 pages, hours per country, and the
  measurement says it buys nothing here.
- **Filling it only where a role is unfilled.** The right instinct — it is the owner's question —
  but the misses are not coverage misses, so the condition never fires on the real gaps.
- **Item 40 as written.** Its premise, "a limit of the curation tool, not of the corpus", was
  already false for a different reason: since entry 85 the selector is a model that reads stored
  text, so the index *is* what the product chooses from. Both the original premise and its
  replacement were wrong, in opposite directions.

---

## 98. A model produced the entry plan, and a sixth thing was in the way

**2026-08-28 · finishes TODO items 38 and 39**

Entry 96 built the visa-free shape and verified it from a hand-made plan; the model had never been
asked to produce one, because the OpenAI account was out of credit. With credit restored,
`POST /visa-plans` for `singapore/PH/PH/tourism` refused — and the reason was neither the schema nor
the prompt.

### The sixth blocker, in the assembly rather than a validator

```python
if application_source_ids and not requirements:
    raise LLMExtractionError("Model output contains no source-backed application documents")
```

Singapore is one of the seven hand-configured destinations, and its
`application_document_source_ids` is **`sg_ica_india_visa_details`** — a page about Indian travel
documents, configured for every traveller. A Filipino needs no visa, so the model correctly returned
no requirements, and this guard read a correct answer as a failed extraction.

The guard is right for an application: a destination that designates a checklist and gets nothing
back has had its checklist ignored. It is wrong for an entry plan, where there is no application to
have documents for. It is now conditioned on `entry_only`, which is `visa_required is False` on the
plan about to be built — the same stated-decision gate everything else in this shape uses. Two
things move with it: `application_document_source_ids` is emptied, so the interface never announces
a checklist with nothing under it, and `has_checklist_source` follows, so the status is graded on
what the plan actually designates.

**That makes six things in the way, against entry 95's three.** The step floor, the
unresolved-question clause, `resolve_plan_status`, `where_to_apply` being required rather than
permitted (entry 96), and now this. The pattern in all six is the same: every one assumed a plan
describes an application, because until now every plan did.

### What the model produced

`visa_required: false`, `where_to_apply: null`, `requirements: []`,
`application_document_source_ids: []`, `unresolved_questions: []`, **`status: verified`**, and five
entry steps — passport validity, the SG Arrival Card and its three-day window, cash and onward
travel, biometrics at clearance, and the Visit Pass conditions — every one citing ICA's general
entry page and linking with `link_target: "source"`. Rendered, it reads *"There is nowhere to apply"*,
*"There are no application documents to gather"*, and **Before you travel**. Every one of the six
changes is load-bearing in that plan: remove any and it either refuses or misdescribes itself.

### The floor did not bite, and saying so matters

Three runs gave **6, 4 and 5** steps. The oracle counts three entry duties for this corridor, from
the two pages it credits; the model reads ICA's whole entry page and finds more. So **nothing here
tested the low end** — the no-floor decision rests on entry 96's argument and on Japan and the
United Kingdom, not on this run, and a corridor whose sources state one duty has still never been
seen. Recorded because the temptation is to read a passing run as evidence for the choice that made
it pass, and this one is not.

### Left alone, deliberately

Singapore's configuration names an India-specific page as the checklist for every traveller, and the
model's explanation mentions it — *"the listed India-specific document checklist does not apply to
this traveller"* — which is honest and is a configuration artefact leaking into a traveller's plan.
That is a defect in `destinations.yaml`, not in this shape, and it belongs with the other
hand-configured destinations rather than being patched here. TODO, smaller things.

---

## 97. `RecallRecord.selector` recorded which selector was *configured*, and a credit outage proved it

**2026-08-28 · found while running TODO item 38, which it invalidated and then unblocked**

Item 38 exists because entry 91 found that nothing in a recall log said which selector fetched its
pages, so grading a pre-entry-85 log put the heuristic inside the model's own arm. `selector` was
added to fix that. Running the twenty oracle corridors showed the fix recorded the wrong fact.

### What happened

Part-way through the batch the **OpenAI account ran out of credit**. `SelectionQuotaExhausted` came
back for the last seven corridors, the heuristic ranking chose instead — honestly, with a note, and
exactly as entry 83 designed — and all seven wrote `selector: model`, because the value was derived
at the write as `"model" if self.selector is not None else "heuristic"`. **That is the
configuration, not the run.**

`selection-recall` then reported 20 corridors graded, 94% for the model against 64% for the matched
heuristic. Seven of those twenty had *identical picks in both arms*: `japan/PH/PH` read 34 pages and
scored 5/5 in the model column and 5/5 in the matched-heuristic column, and so did `sweden/PH/PH` at
6/6 and `united-kingdom/PH/PH` at 5/5. The heuristic was being graded against itself and credited to
the model.

**Configuring a model selector is four steps away from a model having chosen anything.** The index
may hold nothing for the destination, the scored pool may be empty, the call may fail, and the call
may name no id this program recorded. Every one falls back to `_shortlist`. So the fact is now set
where it is known — `ResolutionTrace.selector`, defaulting to `heuristic` and assigned `model` at
the single exit where a validated selection is returned — and the write passes it through.

### Why this is entry 91's defect and not a new one

Entry 91 wrote that "nothing recorded which selector ran" and added a field. The field recorded
which selector was *available*. Both errors have the same shape and the same consequence: an arm's
number is computed from picks the other arm made. The corrections table has carried "the grader
compares a model against a heuristic / six logs put the heuristic in both arms" since entry 91; this
entry is that row a second time, which is why the guard is now a **positive control** in the tests —
one case asserting `model` is still recorded when a model actually chose, so the fix cannot decay
into "always heuristic".

### The numbers, on logs that say who chose

Thirteen of the twenty corridors ran with the model; the other seven were re-run so their logs say
`heuristic` rather than being edited, and `selection-recall` refuses them by name.

| arm | roles | read |
| --- | --- | --- |
| heuristic, matched budget | 32/60 — **53%** | 131 |
| **model** | 57/60 — **95%** | 131 |
| heuristic, shipped budget | 51/60 — **85%** | 455 |

Entry 87 read 100% / 70% / 91% over ten `IN/GB` corridors. This is 95% / 53% / 85% over thirteen
corridors including three `PH/PH`, from logs that name their own arm — the first figure that is
reproducible from disk rather than from a scratchpad. **The direction held and the gap widened**:
+42 points at matched budget, and the model still beats the heuristic given 3.5× the reads.

**Do not read the `PH/PH` column as the second traveller's number.** Three of ten is not a
measurement of a traveller; it is what the credit lasted for. Seven remain, and item 38 stays open
for them.

### What was rejected

- **Editing the seven logs to say `heuristic`.** They are records of what a run did. Re-running them
  costs seven searches and produces the same correction without anybody writing a fact by hand.
- **Deleting them.** `selection-recall` would then report them as never run, which is false — they
  ran, and what they measured was the heuristic.
- **Grading them anyway with a caveat.** The number was already printed once with no caveat
  available, because nothing in the file knew there was something to caveat.

---

## 96. The entry plan is built, and the floor it needed was not a number

**2026-08-28 · builds entry 95, TODO item 39**

Entry 95 decided the shape and left one sub-decision open: `application_steps` carries
`Field(min_length=4, max_length=8)`, Singapore's honest entry list is three, and "the visa-free
shape needs its own bound, and picking it is part of the work". Singapore was a sample of one, so
two more visa-free corridors were curated from the committed stores before anything was written —
offline, no network, no model, with `visa-discover contention` and the page-text index.

### The measurement, and what it says about a floor

| corridor | what the store states | entry duties stated |
| --- | --- | --- |
| `singapore/PH/PH` | ICA's visa-requirement list does not name the Philippines | **3** — SG Arrival Card within three days, passport valid past the stay, onward travel |
| `japan/GB/GB` | MOFA's `novisa.html`: the United Kingdom is one of 74, under Note 8 | **~5** — ICAO-compliant passport, landing permission granted at the port and not by the exemption, no remunerative activity, insurance "highly recommended", an extension applied for past 90 days |
| `united-kingdom/US/US` | GOV.UK's ETA nationality list plus `standard-visitor` | **~7** — hold an ETA, passport valid for the whole stay, show you will leave, show you can support yourself, show you can pay the return journey, permitted activities only, expect border questions |

Three, five, seven. The range fits inside `max_length=8` and its low end is already under four, so
"lower the floor to three" would be fitting a number to the smallest of three samples, and nothing
says a fourth country cannot state two duties or one.

**The stronger reason is that the floor's warrant does not transfer.** Four exists because an
application is *known* to be multi-step — a form, an appointment, a fee, a wait — so a model that
summarised it into one line has produced a worse description of a process we know the shape of.
An entry list has no known shape: it is exactly as long as the duties the authority states. A floor
there is a quota, and a quota on a list with no evidence left to draw from is an invitation to
invent an entry duty — which entry 95 already identified as the failure mode of the zero-step
option it rejected, and which is the alarming-wrong-answer class of entry 6.

**So the answer to "what number" is that there is no number.** `_check_step_count` keeps four for
an application and withholds it entirely from an entry plan, including the empty case: a page that
states the decision and nothing else yields a plan with no steps, and the interface drops the panel
rather than filling it. The cost is a recall risk — a lazy model returns nothing where the sources
did state duties — and that is the trade this project takes everywhere: an omission is recoverable
and a fabricated entry duty is not.

**And it is the guard, read from the other side.** "Fewer than four steps requires
`visa_required is False`" is the same check as "only a stated no may use the short shape", so one
validator does both jobs. `visa_required` can only be `False` on a final plan when a page said so —
extraction overrides it to `None` whenever `decision_is_unverified`, and
`validate_tools_leave_their_questions_open` refuses a stated decision beside a questionnaire that
settles it — so a blocked page and a tool are already excluded by code that predates this entry.
Entry 95's guard turned out to be mostly built.

### Two more things stood in the way, and entry 95 named neither

**`validate_absent_checklist`'s third clause.** Entry 95 says this validator is unchanged, and its
first clause is — with no document source a plan still may not list one requirement, which is the
rule this project exists to enforce. But its third clause requires such a plan to *record what could
not be answered*, and for a visa-free traveller nothing failed to be answered. The sentence a model
would write to satisfy it — "no official checklist was published" — describes a search that failed,
which is entry 93's defect exactly, in the product half rather than the metric. The clause is now
skipped where `visa_required is False`, and only that clause.

**`resolve_plan_status`.** It grades every checklist-less plan `partial`, so a visa-free plan could
never have been `verified` however cleanly its pages were read — which contradicts entry 95's own
table. Entry 14's reason for that rule is that a traveller would expect a complete plan to rest on a
checklist; a visa-free traveller expects no such thing. `no_visa_required` now lifts it, and
`decision_is_unverified` is checked **first**, so a caller that passed both flags is refused the
label rather than trusted.

### What the United Kingdom changed in the spec, and it is worth stating plainly

Entry 95's table says `where_to_apply` is `None` because "there is nowhere to apply". That is true
of Singapore and **false of the United Kingdom**: a visa-free American must still hold an ETA, which
is applied for online, costs money and takes days. Forcing `None` would suppress the one thing that
stops that traveller at the gate — the same harm the entry shape's guard exists to prevent, arriving
by the opposite route.

So `where_to_apply` is **permitted** to be `None` rather than **required** to be. The spec's three
operative commitments are untouched: the checklist stays empty, the steps are entry steps, and the
shape needs a stated decision. `validate_requirement_sources` is what makes this safe and it is
unchanged — a step may link to an application route only where there is one, so a Singapore plan
still cannot link to a route it does not have, and a United Kingdom plan may link to the ETA it
does. Entry 95 called that validator "the guard working"; it works in both directions.

### What was rejected

- **A floor of three.** The smallest of three samples is not a bound, and a country stating two
  duties would be forced to invent a third.
- **A floor of one.** It looks harmless and is the same quota at a smaller size: the filler that
  satisfies it — "check the authority's page before you travel" — is a step no source stated.
- **A separate minimum on the draft only.** The floor is on `VisaPlanDraft` *and* `VisaPlan`, as it
  was before, so a model that summarises a route away is refused where it answered.
- **Forcing `where_to_apply` to `None` in code when the decision is no.** See above: it would have
  deleted the ETA.

---

## 95. A visa-free plan is an entry plan, not an empty application
**2026-08-28 · decided by the project owner, specified here, and built the same day in entry 96**

Entry 94 built the measurement half of TODO item 39 and left one question open: when the answer is
"no visa required", does the plan render as an application with nothing in it, or as a different
shape whose steps are *entry* steps? **The owner chose entry steps.** This entry records the
decision and what it commits to; the code is item 39 and **is now written — entry 96**, which
corrects two things below. There were **five** validators in the way, not three:
`validate_absent_checklist`'s unresolved-question clause and `resolve_plan_status` are the two this
entry missed. And `where_to_apply` is *permitted* to be `None`, not required to be — a visa-free
American still needs a UK ETA, and forcing `None` would have deleted it.

### The shape

A plan whose `visa_required` is `False` still has to be *useful*, and what a visa-free traveller
needs is not a thinner version of an application — it is a different list. Singapore asks such a
traveller for three things and none of them is an application: submit the SG Arrival Card within
three days of arrival, hold a passport valid past the stay, and be able to show onward travel. Those
are `application_steps` in the model's vocabulary and **entry steps** in the traveller's, and the
gap between those two readings is the whole of this decision.

So a visa-free plan carries:

| field | value |
| --- | --- |
| `visa_required` | `False`, from a page that says so |
| `decision_source_ids` | that page. Still `min_length=1`, unchanged |
| `requirements` / `application_document_source_ids` | **empty** — there are no application documents |
| `where_to_apply` | `None` — there is nowhere to apply |
| `application_steps` | the **entry** steps, each `link_target: "source"` or `"none"` |
| `status` | `verified` is available; a stated decision is a stated decision |

### The three validators that stand in the way, named so nobody has to rediscover them

1. **`application_steps: Field(min_length=4, max_length=8)`** — twice, on `VisaPlan` and
   `VisaPlanDraft`. Singapore's honest entry list is three. The floor exists so an application is
   not described in one line, and it should not be removed for everybody; the visa-free shape needs
   its own bound, and picking it is part of the work. **Entry 96 picked no bound at all**: three
   visa-free corridors state 3, 5 and 7 entry duties, so a floor here is a quota rather than a
   sanity check.
2. **`validate_requirement_sources`** — *"application-route step links require an application
   location"*. It fires when `where_to_apply is None` and any step has
   `link_target == "application_route"`. That rule is **correct and stays**: a visa-free plan has no
   route, so no step may link to one. It is named here because it will look like an obstacle and is
   actually the guard doing its job.
3. **`validate_absent_checklist`** — must keep forbidding a requirement while
   `application_document_source_ids` is empty. Unchanged, and the reason is unchanged: entry 60.

### The guard, which is the reason this is a decision and not a refactor

**A wrong "no visa required" that then suppresses four questions is worse than a wrong one that
leaves them visible**, because the traveller has nothing left to notice the error with. So the entry
shape may only be produced where `visa_required is False` is **stated by a source** — never on a
tool, never on a blocked page, never with `decision_is_unverified` set. Where the decision could not
be confirmed, the plan keeps the application shape and says the decision is unverified, exactly as
it does today.

`load_oracle` already enforces the fixture's half of that rule — a row may not call a role
`not_applicable` without a page answering `visa_decision` — and it is the model for the plan's.

### What else has to move, in the order a session will meet it

- **`prompts/extract_visa_plan.txt`** has to be told the shape exists, and told not to invent an
  application when the decision is no. It is the one place a model could reintroduce the failure.
- **`static/app.js`** renders the documents panel and today names three reasons a checklist is
  absent (entry 89): behind a questionnaire, contracted out, or both. A fourth is needed and it is
  not a variant of the others — *this traveller needs no checklist because they need no visa*. The
  panel currently reads "Extracted from the designated official application-document source", which
  is wrong for a plan that designates none.
- **The "where to apply" panel** must say there is nowhere to apply rather than rendering empty.

### What was rejected

- **An application with zero steps.** It satisfies the type system and misdescribes the world: the
  traveller is not making an application badly, they are not making one at all. It also leaves
  `min_length=4` to be satisfied with filler, which is how a model is invited to invent.
- **A separate `EntryPlan` model.** One plan type keeps one renderer, one validator set and one
  contract; `visa_required` already distinguishes the two cases and every consumer reads it.
- **Deciding it in discovery.** The adjudicator assigns pages to roles and never reads the decision
  out of them — `visa_required` is known at extraction. Suppressing anything earlier would put the
  suppression before the evidence that licenses it.

---

## 94. "No visa required" is a complete answer, and four of Singapore's six questions stop existing
**2026-08-28 · TODO item 39, the measurement half. The product half is specified and not built**

Entry 93 fixed a metric that scored a tool-mediated answer as a gap. This is the same defect's other
instance and the last one: Singapore's Philippine row read **two of six** while resolving perfectly.

A Filipino needs no visa for Singapore. So there is no application — and with no application there
is no checklist to bring to one, no route to take, no fee to pay and nothing to process. Those four
roles were recorded `unanswered`, which says *the store failed to find four pages*. What the store
had actually found is that **there is nothing to find**.

```
singapore/PH/PH   2 answered by a page, 4 do not arise, 0 open      6/6 accounted for
singapore/IN/GB   6 answered by a page                              6/6 accounted for
```

The Indian row is the control and it is what makes this a fact about the corridor rather than about
Singapore's website: India **is** on the very list the Philippines is absent from, so all six
questions arise for that traveller and all six are answered.

### The distinction, and why a third bucket rather than a wider second

`unanswered` and `not_applicable` mean opposite things about the store:

- **`unanswered`** is a recall problem. Somebody could fix it by crawling deeper, reading better, or
  waiting for the authority to publish. It belongs in the column that judges us.
- **`not_applicable`** is a fact about the world. A bigger corpus would not touch it, and no amount
  of effort will produce a visa fee for a visa-free traveller.

Merging them would be entry 93's mistake in reverse — and merging `not_applicable` into *answered*
would be worse still, because "we know the answer" and "the question does not arise" are different
things to tell a traveller.

### The guard, which is the whole risk

**A wrong "no visa required" that then suppresses four questions is far worse than a wrong one that
leaves them visible**, because the traveller has nothing left to notice the error with. So
`load_oracle` refuses a row that claims `not_applicable` **without a page answering
`visa_decision`**:

> only a stated decision can say a role does not arise

That closes the failure this bucket would otherwise invite: "we could not find the checklist"
quietly becoming "there is no checklist". A role is also refused if it is called not applicable and
answered, or not applicable and unanswered — one status per role, always.

### What is built and what is not

**Built:** the fixture's fourth outcome, its two validators, and `visa-discover coverage`'s fourth
column. `PH/PH` now reads **50 of 60 accounted for** — 41 answered by a page, 5 settled by an
official tool, 4 that do not arise, 10 genuinely open.

**Not built: the product half.** A `VisaPlan` still has no way to say a question does not arise, and
looking for one turned up why it is more than a field: `application_steps` is `min_length=4` and
`where_to_apply` and `requirements` are shaped for an application that a visa-free traveller never
makes. There is no no-visa path anywhere in `research/` — the only mention is
`require_load_bearing_sources`, which is about missing evidence rather than an absent application.

So the product half needs its own decision: whether a visa-free plan renders as an application with
zero steps, or as a different shape whose steps are *entry* steps — submit the arrival card, carry
an onward ticket, hold six months of passport validity. The second is almost certainly right and it
is not a rename. It stays TODO item 39, now reduced to that question, and it must key on
`visa_required is False` **from a stated source** — never a tool, never a blocked page, never
`decision_is_unverified`, for the reason above.

### What was rejected

- **Inferring "no visa" in discovery.** The adjudicator assigns pages to roles and never reads the
  decision out of them; `visa_required` is known at extraction. Guessing it a step early would put
  the suppression before the evidence that licenses it.
- **Letting a curator mark a role not applicable on judgement.** The validator requires an answered
  `visa_decision` in the same row, so the claim is anchored to a page somebody named.
- **Counting the four as answered.** They are accounted for, not answered. A traveller reading
  "checklist: none required" is being told something true; a metric reading "checklist: answered"
  would be telling us something false.

---

## 93. A tool-mediated answer is an answer, and the metric was the only thing saying otherwise
**2026-08-28 · a correction from the project owner, and the code already agreed with them**

Asked whether France's Visa Wizard could be credited with the three roles France-Visas' own FAQ says
it settles, entry 92 answered "named, never filled" and was **half wrong**. The owner drew the
distinction that the entry had blurred:

> **Direct answer** — "Filipino citizens residing in the Philippines need a visa."
> **Tool-mediated answer** — "France-Visas' official Visa Wizard determines whether you need a visa.
> Use it here."
>
> The second is still a legitimate answer from the agent because it gives the traveller the
> authoritative path to resolve the question without fabricating missing information.

**That is entry 60's own position**, whose heading reads *"a questionnaire is an answer, and may be
named, never driven"*, and whose text says a questionnaire "is not a blockade in front of the
guidance; it is the form the authority published the guidance in". What entry 60 forbids is **filling
the role's content** — inventing what the Wizard would say. It never said the corridor goes
unanswered.

**The product had it right all along.** `audit.py` has put `resolved_decision_tool` in the *resolved*
group since entry 63, with the posture-cost column reading "no — the authority publishes it only as
a tool". A plan that names a decision tool resolves. Only `visa-discover coverage`, written on
2026-08-28, treated a tool as a gap — and it was the newest thing in the repository, disagreeing with
the oldest.

### What it was costing

France's Philippine row read **two of six**. A traveller using it gets an authoritative path for
**five** — two roles from pages, three from the Wizard the authority publishes them in. Reported as
2/6, France looked like the fixture's failure; reported honestly it is a country that publishes
per-traveller guidance through a form, which is entry 82's wall seen from the traveller's side rather
than the crawler's.

Half one of `coverage` now reports three columns and a total:

```
IN/GB/tourism   47 answered by a page,  7 settled by an official tool,  6 open  ->  54/60 (90%)
PH/PH/tourism   41 answered by a page,  5 settled by an official tool, 14 open  ->  46/60 (77%)
```

### What is kept apart, and why the columns are not merged

`settled` is **never added into `held` or `answerable`**, for the reason `audit.py` keeps its two
halves apart: the difference between them is what a reader has to be able to see.

- A page answer is **citable**. The plan quotes it, `SourceReference` carries its URL, and the
  freshness rules govern it.
- A tool is **not**. Nothing about it may be quoted, `application_document_source_ids` stays empty
  so `validate_absent_checklist` still forbids listing one requirement, and a `VisaPlan` naming a
  decision tool can never be `verified`.

Merging them would let "we hold the answer" and "we hold the address of the machine that computes
the answer" become one number, which is precisely the confusion this entry is correcting in the
other direction.

A role a page answers is **not** also counted as settled, so the two can never double-count. The
page wins, because it is the one this project can cite.

### What has not changed

Driving the Wizard is still out of scope, and entry 92's measurement is why rather than a rule:
step one requires **travel-document type, age, marriage to a French national, and whether the
traveller is joining an EU-citizen relative.** A corridor holds none of those and two of them change
the answer. Handing the traveller the form is the honest act precisely *because* we cannot fill it
in. If it is ever revisited, the route is a wider traveller profile as **corridor input**, so the
answers come from the traveller — never from us.

### The same defect has one instance left

Singapore's Philippine row reads two of six, and three of the four gaps are gaps *because the answer
is "no visa"* — there is no application, so no route, no checklist, no fee. That is the same shape:
a correct, complete outcome scored as a thin one. TODO item 39, now the last of these.

---

## 92. The corpus build always rendered; twelve renders is what left France unreadable
**2026-08-28 · TODO item 5b. The item's own premise was wrong, and checking it took one grep**

France is the weakest corridor in `oracle/selection_oracle.yaml` — **18 readable candidates of
201**, so neither curated traveller can be given more than one answer there, and known problem 30
names it as the bound on the whole metric. Item 5b was written to fix that and said the reason was
that the offline corpus build does not answer Cloudflare challenges the way the request path does.

**It does. It always has.** `run_corpus` builds a `PlaywrightPageRenderer` from the same
`render_mode` the request path reads and hands it to the same `CrawlFetcher`, which calls the same
`_answer_challenge`. What it also hands over is `settings.maximum_crawl_renders`, which is **12**.

### What twelve renders buys on a site that challenges everything

Counted from the France corpus built 2026-08-27:

```
160  disallowed by robots.txt          — obeyed, and nothing to do about it
 64  challenge, unanswered             — all on france-visas.gouv.fr (46 + 18)
 34  connection failures
 32  HTTP 404
```

Sixty-four challenged pages, twelve renders, and `_render_if_empty` drawing on the same budget. So
most of those 64 were recorded *"it asked this client to prove it is a browser (HTTP 403), and that
challenge could not be answered here"* — a sentence that is true of that crawl and false of the
authority, which is the failure mode this project's rules care most about. The corpus recorded
`france-visas.gouv.fr` as 133 unopened addresses and 67 unreadable ones.

**This is the corrections table's most repeated shape**: the documented diagnosis named a missing
capability, and the capability was there with a number set for a different job. A corridor gets
twelve renders because a traveller is waiting for it. A nightly build has nobody waiting.

### Raising it alone would have bought a worse failure

`DEFAULT_CORPUS_RENDERS = 400` for the offline job. On its own that is a trap: `urm.lt` fingerprints
past our user agent and its challenge cannot be answered at all (entry 75), so it would take 400
renders at up to `render_challenge_settle_milliseconds` — 20 seconds — apiece, and spend over two
hours proving the same thing four hundred times. Entry 75 recorded that hazard for Slovakia and
nothing acted on it.

So the budget is bounded on a second axis: **`CHALLENGE_FAILURES_PER_HOST = 3`.** Three *consecutive*
unanswered challenges and this crawl stops offering that host renders. Three rather than one because
a challenge fails for reasons that are not the host's — a slow page, a redirect caught mid-flight —
and consecutively rather than cumulatively because a site that mostly passes must never be written
off. One page that answers clears the host.

A render that comes back still carrying the interstitial counts as a failure, which is the ordinary
way this fails: `_wait_out_challenge` polls and returns whatever the page last held when its deadline
passes, so the caller has to check the result rather than the call.

### The line entry 41 draws has not moved

Answering a challenge is legitimate because a challenge **states no policy** — it is a question about
the client, and our renderer answers it announcing `VisaResearchAgent/0.1`, deceiving nobody. What
stays forbidden is unchanged and now has tests on the crawl path as well as the request path: a bare
`403`, a `401` and a `429` are refusals, are never rendered past, and never reach the renderer at
all. `robots.txt` is still obeyed — France's 160 disallowed pages are untouched by this and should
be. A page whose challenge goes unanswered is still reported `challenged`, which keeps "we could not
prove we are a browser" a statement about us.

### The rebuild, measured

`visa-discover corpus --country FR --pages 1200`, ten minutes, 42 queries:

```
corpus entries                    5,317  ->  6,277
pages with stored text            1,227  ->  1,353
france-visas.gouv.fr with text       12  ->    104
```

**A site that was effectively unreadable is now eight and a half times readable**, and one of the
pages it gave up answers a role for both curated travellers: `france-visas.gouv.fr/en/
votre-arrivee-en-france` — *"a valid passport issued less than 10 years before and valid for at least
3 months after the envisaged departure date... proof of accommodation covering the whole duration of
the stay"*. France goes from one answered role to two for the Philippine traveller.

**One role, from ninety-two newly readable pages, and that ratio is the finding.** France's remaining
four gaps are not a text-coverage problem and a bigger crawl will not touch them: the decision, the
checklist and the fee are inside the **Visa Wizard**, which is a tool rather than a page — entries 59
and 60 — and the row already names it as one three times over. The FAQ is readable and its stored
text is the cookie-consent panel.

**And the ratio moved the wrong way even as the count moved the right way.** France's contention set
grew with the corpus, from 201 candidates to 523, so readable-of-contention went 18/201 to 33/523 —
9% to 6%. A percentage whose denominator is the crawl's own reach is not a coverage measure, which is
the same trap entry 91 hit with `held`.

So the mechanism is settled — the renderer was never the missing piece, the budget was, and an
unanswerable host now costs three renders instead of the job — and **France stays the weakest row in
the fixture for a reason no crawl fixes.**

### Sweden is where the same change paid, and it was found by counting before crawling

Which corpora are worth rebuilding is answerable offline for nothing: count each one's
`challenge, unanswered` entries. Across the ten — **FR 66, SE 216, US 19, and zero for the other
seven.** So Sweden, not France, was where the render budget was costing the most, and it took one
query to know it rather than nine crawls to find out.

```
corpus entries              2,246  ->  3,586
pages with stored text        819  ->  1,325
government.se with text         0  ->    863
```

`government.se` answered a challenge on **every** page, so it held stored text for none — which is
exactly why both Sweden rows recorded its visa-requirement list as `unverifiable` or `title_only`.
It now reads *"List of third countries whose nationals must be in possession of visas when entering
Sweden"*, with **"India \*\*)"** and **"The Philippines \*)"** both on it. The Indian row's
`seen: title_only` becomes `seen: text`, and the Philippine row gains a stated visa decision.

**Sweden's row went 2 of 6 to 6 of 6**, and only one of those four came from the rebuild. The other
three came from noticing that the Indian row already credited
`migrationsverket.se/…/visiting-sweden-for-up-to-90-days-entry-visa.html` with five roles where the
Philippine row credited it with two — the page states EUR 90, fifteen days and the document list, and
a shallow re-check had missed all three. **`PH/PH` overall: 24 of 60 when this session started,
now 41 of 60.** Seventeen of those roles were always answerable and nobody had looked properly.

### What the rebuild let us check, and the answer is still "name it"

Reading the Wizard was the point of rebuilding France, and it is now readable. The project owner
checked the current France-Visas material independently and found the FAQ sentence, which the index
now holds too:

> the visa wizard "instantly informs you of the type of visa required, the supporting documents to
> be provided and the amount to be paid, depending on the elements you have filled in"

**That is the authority's own account, and it names exactly the three roles both France rows already
attribute to it** — `visa_decision`, `document_checklist`, `fees`. Independent corroboration of a
curation made from the other side, which is worth more than either half alone. Both rows now point
those tools at the Wizard itself rather than at a post's page that mentions it.

**It does not make them answered, and reading the form is what settles that.** Step one alone —
"All fields below are required" — asks for **nationality, official supporting document, age, whether
the traveller is married to a French national, and whether they are joining a close relative who is
an EU, EEA, Swiss or protected-UK citizen.** A corridor contains the first and none of the other
four. The last two are not colour: marrying a French national or joining an EU relative moves the
traveller to a different regime, and age moves the fee — children 6 to 11 pay 45 euros and under-6s
nothing. So filling these roles from the Wizard means inventing traveller input on the questions
that decide the answer, which is entry 59's bar failed more clearly than GOV.UK failed it. Entry 60
stands: named, offered beside the question, never filled.

The fourth role the owner asked about, `application_route`, is **already answered** in both rows and
not by the Wizard — `ph.diplomatie.gouv.fr/en/applying-for-a-visa` for the Philippine traveller and
`uk.diplomatie.gouv.fr/en/applying-for-a-visa` for the Indian one. France's genuinely open role is
`processing_times`, which the Wizard does not claim to give and its Manila page explicitly declines:
"waiting times... will vary depending on your country and the time of year".

### A corpus build could never record a success, so it could never correct a failure

Checking the Wizard turned up something the rebuild should have fixed and had not: twelve France
entries still read *"it asked this client to prove it is a browser (HTTP 403), and that challenge
could not be answered here"* **while the page-text index held their bodies.** A reason untrue of
what was seen is the one thing this project's failure text may never be.

The cause is one line. `_entry` wrote `"unreadable" if reason else "unknown"` — so `readable`, a
documented retention tier, was **assigned by no build ever**. And `merge` moves a status up and never
down, with `unknown` ranking *below* `unreadable`: a page that failed in one build and was read in
the next kept the old failure and its sentence for ever. `LinkCrawler` now records what it actually
opened and `_entry` reads it, so a later build clears a failure the page no longer has.

### What was rejected

- **Raising `settings.maximum_crawl_renders`.** That is the request path's number and a corridor has
  a latency budget; the two jobs want different values, so the offline one passes its own.
- **Giving up on a host after one failure.** A challenge that fails once has told us about a page.
  Three consecutive failures have told us about a host.
- **Counting failures cumulatively.** A site that challenges intermittently would eventually be
  written off for good, which is the opposite of what the count is for.
- **Retrying a refusal in a browser.** Not considered, and named here only because raising a render
  budget is exactly the change that could be mistaken for it later.

---

## 91. A second traveller in the oracle: the corpus answers 78% of roles for one and 68% for the other
**2026-08-28 · known problem 29, closed by curation. It found a defect in the grader on the way through**

Every recall number this project quoted rested on the same ten corridors, all `IN/GB/tourism`:
`visa-discover coverage`'s 47 of 47, `selection-recall`'s 100% against 70%, and entry 90's whole
second half. Known problem 29 called that "the largest untested dimension in the whole harness".
`oracle/selection_oracle.yaml` now holds **twenty** corridors — the same ten countries for a
Philippine passport applying in the Philippines.

**Why `PH/PH`.** `IN/GB` has the passport and the residence apart, and its three sharpest findings all
turn on residence — the UAE's visa on arrival for Indians living in Britain, the UK fee table keyed on
the application country, the Netherlands' UK-specific checklist. A second row where the two coincide
tests the opposite arrangement. It is also the profile entry 88's rebuild was proved on, so it is the
one place a corpus change can be seen at all.

### The headline: both travellers read 100% held, and that was never the number

```
IN/GB/tourism   47/47 of its answers held (100%)   47/60 roles answerable at all (78%)
PH/PH/tourism   41/41 of its answers held (100%)   41/60 roles answerable at all (68%)
```

The corpus holds every page a human could name, for both. What moves is **how much can be answered at
all**: the same ten stores answer 47 of 60 roles for one traveller and 41 of 60 for the other. That is
the traveller dimension, and a percentage whose denominator is itself the finding could not show it —
so `visa-discover coverage` now prints both figures per traveller and `KnownAnswer` carries `roles`
so the denominator cannot move.

**The 100% is a real finding for `IN/GB` and close to circular for `PH/PH`, and the first version of
this entry did not say so.** The Indian rows were curated from the page-text index, which holds
corpus pages *and* pages fetched by live search — 10,444 pages, of which **1,691 are not in the
corpus**. A curated answer could have landed on one of those and none did. The Philippine rows were
curated with `visa-discover contention`, whose set is built *from* the corpus, so any page nameable
there is held by construction. The only way to score below 100% was to mistype a URL, which happened
once — Canada, where the corpus holds `…/supporting-documents.html/1000.html` and the store's copy of
it is Canada.ca's 404 page. So `PH/PH`'s held column measures transcription; **its finding is
entirely the 41 of 60.**

**The zero-answer corridors are counted.** France and Sweden answer *none* of their six roles for this
traveller, and skipping them — which the first implementation did, by filtering on `not
corridor.answers` — read 24 of **48**, flattering exactly the traveller the row exists to be honest
about.

### The first pass read three candidates deep and got three rows wrong

Asked whether the UAE's row meant *no applicable page exists* or *an applicable page was not
selected*, the answer was the second, and it took one look to find out. The row was built from a
dump of two roles and recorded five as unanswered, reasoning that a Filipino resident at home falls
outside the UAE's residence-keyed services. The reasoning was sound and the conclusion was false:
`gdrfad.gov.ae/en/services/f9e586fe-…`, "Issuance of a single-entry tourist visa", answers **five**
roles for anybody —

```
document_checklist   "1. One personal photo. 2. Copy of the passport."      scores 36.0
application_route    Service Steps, and "only accredited tourism offices"   scores 39.6
fees                 "30-day tourist visa fee: AED 252"                     scores  0.0
processing_times     "Expected Completion Time 48.0 Hour(s)"                scores  0.0
general_entry        passport valid six months, a ticket to leave           scores  0.0
```

**Three of the five roles it answers, it scores zero for.** That is entry 78's defect in its sharpest
form: the ranking reads a link and cannot see inside a page, and the pages that *do* score for those
roles state nothing — the top `fees` candidate at **126.4** is `u.ae/…/visa-fees`, which says "visa
charges are stated on each service card on the websites of ICP and GDRFA-D" and prices nothing.

Two more rows moved on the re-check. Sweden went 0 → 2: the first pass found the page for
*extending* a visa and missed the one for applying, which states the route and the SEK 700 per day
and EUR 30,000 insurance conditions. France went 0 → 1 plus three tools: `ph.diplomatie.gouv.fr/en/
applying-for-a-visa` is the Manila post's actual visa page, 20 points *below* the tourism-marketing
page at the same host that the first pass excluded.

**Asked to re-check the other seven rows, the same mechanism turned up two more.** Germany's
`visa-service/215870-215870` — "Visas for Germany" — answers `application_route`, `fees` and
`processing_times` and **link-scores 7.6**, so it sits near the bottom of every role ranking. The
United States' `fees-visa-services.html` prices a B-2 at $185 and link-scores 16.4. Neither was found
by ranking links; both were found by ranking stored **body** text with `page_text.rank`, which is the
only instrument here that can see inside a page.

**The re-check had to change instrument, and that is the transferable part.** The first re-check
ranked each unanswered role by link score — and `ranked_for_role` filters on `score_for(role) > 0`,
so a page scoring zero for the role it answers can never appear. That is the *same blind spot* that
produced the original error, applied to the audit of the original error. Ranking by body text finds
them; ranking by link score cannot, by construction.

**The older `IN/GB` rows held up.** Germany's Indian row already names `215870-215870` for all three
roles, and names a second alias for it. So this was a fault in the new curation rather than in the
fixture's method — which is itself worth knowing, because it means entry 87's ten rows do not need
redoing.

**So `PH/PH` is 36 of 60, not 24**, and the lesson is about curation rather than about the store: a
fixture read three candidates deep describes the ranking, not the corpus.

### Where the 11 remaining gaps are, which is four different things

- **Stored text runs out.** France is bounded at **18 readable candidates of 201** by its Cloudflare
  challenge, and Sweden's decision page sits on `government.se` with no body indexed.
- **The authority defers in its own words.** Sweden on documents: "the documents you must submit
  depend on the country in which you are applying... check on the website of the correct embassy."
  That is not the corpus lacking a page, and it is worth counting apart from one.
- **The corpus is thin.** Germany answers one role for either traveller, out of 83 candidates and a
  1,565-entry corpus. A statement about the crawl, not about either passport.
- **The answer is "no visa", and three roles then have nothing to answer.** Singapore: there is no
  application, so no route, no checklist and no fee. A corridor that resolves correctly can leave
  most roles empty, which is worth knowing before reading any roles-filled number — and it is an
  argument for not asking the other five questions at all once the decision is "no visa required".
  TODO item 39.

Two roles moved the *other* way. The Netherlands answers four against three, because the Manila fee
page holds stored text where the London one does not — **entry 88's rebuild appearing in a
measurement for the first time**, which the `IN/GB` row is structurally unable to see. And the United
States' Visa Waiver country list, recorded as unreadable in the Indian row, reads here because the
`adoption.state.gov` mirror was found.

### `visa-discover contention` — the set is rebuilt offline, not run

Entry 87 curated the first ten rows out of live runs in a throwaway script, which is what item 34
objected to one level up. Curating a corridor nobody has run needs its contention set, so that is now
a command: the resolver's own `score_link` and `reject` over the stored corpus, no search, no model,
no fetch. Rebuilt sets come out close to the recorded ones — 365 against 417 for the UAE, 539 against
552 for Canada, 83 against 87 for Germany.

**It is corpus-only, and the first ten rows were not.** Those saw `corpus ∪ search`, so a role whose
only answer live search would have surfaced cannot be curated from here. It biases a row toward the
corpus and biases both graded arms equally; entry 90 measured the corpus as holding the answering
page for all 47 curated roles, which is what makes the approximation good enough to use and not good
enough to leave unsaid.

Reading a candidate to judge it needs its stored text, so `PageTextStore.body_for_review` is the third
amendment to entry 78's rule and is argued rather than slipped in. The rule is that no sentence
written from stored text reaches a **traveller**; `rank` and `score_body` already read it, and entry
87 read it by hand. This chain ends at a terminal a curator is looking at — one URL, named on the
command line — and there is no caller in `research/`, none in `api/`, and none on the request path.

### The defect it found: the grader could not tell which selector ran

`arms_from_logs` reads a run's fetched URLs as *the model's picks*, and nothing in `RecallRecord`
said which selector fetched them. That was harmless only by accident — the ten oracle corridors all
had logs from the model runs behind entries 85 to 87. The second traveller brought in **six logs
written before entry 85 turned the model selector on**, and grading them put the heuristic into the
arm labelled `model` and compared it against itself. The printed figure moved from 100% to 92% with
nothing in the output to say why.

`RecallRecord.selector` now records it, and a log that cannot name its selector is **not graded** —
`cause`'s rule applied to a second field, from entry 63: a record written before the field existed is
reported as unrecorded, never inferred. It is reported apart from `skipped`, because the two need
different reading: a skipped corridor was never run, while one of these was run and the file cannot
say by what.

**The cost is that `selection-recall` grades nothing today**, and the honest statement of entry 87's
numbers is that they stand as recorded and are **not currently reproducible from disk**. Re-running
the ten `IN/GB` corridors restores them and grades the ten new ones for the first time. That is the
next measurement, and it is the first one that will say anything about a selector on more than one
traveller.

### What was rejected

- **Grading the six unattributable logs anyway.** They are real runs of real corridors and the arm
  labels would have been wrong. A wrong label on a published number is the single most repeated
  failure in this project's corrections table.
- **Dating the cutoff from `recorded_at`.** Entry 85 turned the model selector on at a known moment,
  so a date test would work today and rot silently. The file should say what it is.
- **A third traveller.** Two is what makes a number a comparison; the next question is *purpose*,
  where all twenty rows are still `tourism`.

### Three things it hands to the queue

- **A "no visa required" answer should end the corridor, not open five more questions** (TODO item
  39). Singapore's row records three roles unanswered *because* the answer is no visa — there is no
  application, so there is no route, no checklist and no fee. Asking anyway makes a correct, complete
  answer look like a 2-of-6 failure in every metric this project has.
- **France's challenge is answerable and the corpus never answered it** (item 5). Entry 41 settled
  that a Cloudflare challenge is not a refusal and may be answered by our own renderer under our own
  user agent, and entry 75 built that for the request path. The *corpus build* did not get it, which
  is why France holds 18 readable candidates of 201.
- **Curation should be able to fetch a page the index does not hold** (item 40). Sweden's decision
  list and the Netherlands' Philippine checklist are recorded `unverifiable` for want of stored text,
  and the product would simply fetch them. `visa-discover contention` is offline by design and that
  should stay the default, so this is an opt-in for a single named candidate.

### What it does not answer

- **Still one purpose.** Twenty corridors, `tourism` throughout. Business, study and transit are
  untested and the roles most likely to move are `document_checklist` and `application_route`.
- **The `PH/PH` rows have no selector grade yet**, and cannot until those corridors are run.
- **Correctness, as always.** These rows say a page *answers* a role; whether the guidance is right
  is verified outside this repository (entry 68, known problem 26).

---

## 90. The corpus gate: the 100% is kept and demoted, and the number that matters is per traveller
**2026-08-28 · TODO item 37, built. Two of its three expectations came out differently when run**

The question that gates promoting a country to stage 3 is *"if we build a corpus for X, can a
corridor into X be answered from it?"* Until now that was a judgement made because a corpus file
existed. `visa-discover coverage` makes it a number — offline, no model, no search, reading only
`var/corpus/`, `var/pagetext/` and the committed oracle.

### Why it is two halves and why they are never added

Asked of `oracle/selection_oracle.yaml`, *"is the page that answers each role already in the
corpus"* comes back **47 of 47**. That is true, it is reproduced by a test, and on its own it is
close to useless: every corridor in that oracle is `IN/GB/tourism`, and the Netherlands' three
answers were held both **before and after** entry 88's rebuild — so the fix that measurement should
have caught improved Philippine, Pakistani and Chinese residents and improved `IN/GB` by nothing.

So half one is kept and labelled for what it is, a **regression** check that should stay at 100%,
and half two measures the dimension that varies. They are printed apart, which is `audit.py`'s
discipline: one number covering both hides which half failed. The verdict is computed from half two
**alone**, so a 100% meaning "fine for one traveller" can never outvote a family measurement meaning
"unserved for the other 197".

### The trap that had already produced a wrong number once

The first run of half one read **46 of 47**. The miss was `www.gdrfad.gov.ae/en/services/727c…`
against `gdrfad.gov.ae/en/services/727c…` — one page. Comparison is on `canonical_key`, never on the
raw string, and the alias is reported rather than silently folded so the count can be checked.

### Gateway or leaf cannot be settled by counting children

Opening a member of the Dutch `…/schengen-visa/apply-{}` family yields 2.4 children apiece; opening a
member of Singapore's `…/visa-detail-page/{}` yields 1.5. Those are not far enough apart to divide
on, and the two families are opposites — the Dutch member leads to that residence's checklist and the
Singaporean member **is** the answer.

Asking whether the child is itself *about one country* separates them completely:

```
NL  …/schengen-visa/apply-{}     169 children,  168 country-named   gateway
NL  …/consular-fees/{}            44 children,    0 country-named   leaf
SG  …/visa-detail-page/{}          3 children,    0 country-named   leaf
```

Singapore's three are a landing page, a public advisory and a user manual. The shape is counted from
opened members and is honestly `unopened` where none has been opened, because nothing distinguishes a
gateway from a leaf before one is — which is the same fact that forces `FamilyQueues` to give every
family its turn rather than back a winner.

### Two of the item's three expected verdicts held; the Netherlands' did not

Item 37 predicted the Netherlands would read *covered*. It reads **incomplete**, and the numbers are
why: its largest gateway family is **71 of 184 opened (39%)**, and three complete families have
**never been opened at all** — `making-appointment/{}` at 188 held, `caribbean-visa/short-stay/
apply-{}` at 185, `passport-id-card/abroad/apply-{}` at 184. Entry 88 proved the mechanism on one
country and did not finish the country. That is item 35's work, now with a number on it.

The other two held. Six of the ten have no qualifying family and read *no per-traveller dimension*;
Singapore reads *bounded by the authority* at 32 of 198, which is a **pass** — the missing 166 are
behind a selector and no crawl budget crosses one (entry 82), so saying so and stopping is correct.

### The United Kingdom has a per-traveller family, and entry 88 said it had none

Entry 88 counted qualifying families as **NL 9, SG 1, and zero for CA, JP and GB**. Measured
corpus-wide the counts are **NL 13, SG 2, GB 1**, and the difference is not a disagreement — it is
two different questions:

- `LinkCrawler._queue` groups the links found on **one page**, because a family is a list an
  authority published in one place and siblings on unrelated pages are a coincidence. Grouping that
  way reproduces entry 88's 9 / 1 / 0 **exactly**.
- This groups across the whole corpus, because the question is what the authority *publishes*, not
  what a crawl can act on.

The four extra Dutch families are the `checklist-schengen-visa-…/{}` leaves, which exist one per
gateway and are listed together nowhere. The extra British one is
`visa-fees.homeoffice.gov.uk/y?previous-answer={}` — **entry 82's fee wall appearing as a family for
the first time**, 14 of 198 held and none opened. Per-page grouping would have reported the United
Kingdom as having no per-traveller dimension, which is false. So both groupings are kept: the report
groups corpus-wide and marks each family `listed` or `spread` for whether the reservation can see it.

### What was rejected

- **One number.** It would be half one's 100%, because half one has a denominator and half two does
  not have a comparable one. See above.
- **Grading on roles filled.** Entry 81 measured it swinging by two on identical input and entries 79
  to 81 are three consecutive entries that were wrong for leaning on it. There is no model anywhere
  in this command, by construction.
- **Counting "opened" as coverage.** An unopened URL is still a usable candidate — what does not
  exist is the *child* of a member nobody opened. So `opened` gates the verdict only for a gateway,
  and a complete leaf family reads *covered* with nothing opened.
- **A `text_for_selection` call with the values discarded.** `PageTextStore.indexed` returns a set of
  URLs, so no prose can reach a report. Entry 83's barrier is a type, and the second caller wanting
  bodies is still the change somebody has to argue for.

### What it does not answer

- **Whether the corridor then *finds* what the store holds.** That is `selection-recall` (entry 87),
  and merging them would hide which half failed.
- **A complete, under-opened family that no page lists.** It is printed as `spread` and does not push
  the verdict either way. No such family exists in the ten corpora — every one that is `spread` is
  also far short of the world — so the case is documented rather than machined for.
- **Correctness.** Like every number this project quotes about itself, this measures whether the
  store *holds* an answer, never whether the answer is right (known problem 26).

---

## 89. Guidance an authority contracts out: named, never read, never believed
**2026-08-28 · asked by the project owner, built, proved on the corridor that motivated it**

Entry 88 found that for most residences the Netherlands does not publish its document checklist on
any government domain — it says, on its own page, "on the VFS Global website you'll find a checklist
with the documents you need". That entry called it a ceiling. **It is a ceiling on *reading*, not on
*answering*, and treating the two as the same thing was the mistake.** The owner said so, twice, and
was right: entry 27 already names a page an authority refused, entries 59 and 60 already name a
questionnaire that asks instead of answering. A delegated service is the third member of that family
and the rule is the family's rule — *a next step the traveller can take and this program may not.*

### What was refused, and why it is not this

Trusting `vfsglobal.com` as a source, or crawling it into the corpus, was considered and declined.
It is **one domain serving around sixty destinations**, so `belongs_to_destination` — the check that
stops the United States embassy's page about Vietnam answering a Vietnam corridor — has no analogue
there. The artefact at stake is the document checklist, which is the single output this project
exists to get right, and a contractor's copy can drift from the authority's with nothing able to
detect it. Entry 2 stands: officialness is a property of who controls the domain.

Naming needs none of that, and gets most of the value.

### The warrant is two independent things, and one of them is not the government page

The obvious design — the authority's own page linked it, so it is legitimate — is **not enough**, and
the reason is the one that governs everything else here. The link is extracted from HTML, and HTML is
`untrusted_content`. A compromised or spoofed government page could hand a traveller any address at
all, *for the checklist*. So, exactly as `auto_trusted_domains` demands governmental **and** own-TLD:

1. an approved page on the destination's own government domain linked it, and
2. the registrable domain is on `config/service_providers.yaml`, a committed reviewed list.

Either alone fails closed. The list is deliberately **not** `authority_domains.yaml`: that file
records who may be *believed*, this one records who may be *pointed at*, and merging them would put
a commercial contractor one boolean away from being citable.

### The model selects; it may never supply

`crawl._expand` still refuses the off-domain link — `is_crawlable` is untouched — and now writes it
down on the way past. The adjudicator is handed `delegated_services` as **addresses with no content
field**, the same shape `build_blocked_packet` uses for a refused page and for the same reason:
nobody read it, so there is nothing that could be quoted. It answers with a `delegate_id` indexing
the list our crawler built, and `validated_delegates` discards anything else exactly as an invented
`source_id` is discarded.

**So the URL a traveller follows always came from an `href` our own code read off an approved
government page, never from a model reading page text.** That is the whole safety argument, and it
is why the fast version — have the model extract the URL from the excerpt, which would have worked
today for Singapore and Japan — was not built.

### It fills nothing, and the checks that matter still fire

`application_document_source_ids` stays empty, so `validate_absent_checklist` still forbids listing a
single requirement. It never sets `decision_is_unverified`: that flag has two causes — an authority
withholding a page, and an official tool — and a company's website is neither. It is dropped for any
role a source already answered. `Delegation` and `DelegatedService` have nowhere to put an excerpt,
which is the same enforcement-by-type as `Selection` in entry 83.

### Measured on the Netherlands, and proved on the corridor that motivated it

A rebuild recorded **236 delegations**, and what they are matters more than the count: 44 are "track
the status of your application", 30 are "find out which documents you need", the rest are appointment
addresses and contact pages. Only the second kind is guidance, which is why the prompt says a
contractor that merely takes the appointment does not answer the role.

`netherlands/PK/PK/tourism`, end to end:

```
could not be identified:  visa_decision, document_checklist
published by a company the authority contracts with:
  document_checklist  https://visa.vfsglobal.com/one-pager/netherlands/pakistan/english
                      named on .../schengen-visa/apply-pakistan
```

The checklist role is still **unfilled**, so the plan may not list a document — and the traveller is
handed the page anyway, with the government page that appointed it. The model chose the one-pager
over four appointment and tracking links on the same host, and grounded it in what the Dutch page
says. Before this, that corridor said nothing about documents at all.

### What is not settled

- **The interface wording has not been read by a traveller.** It is amber rather than the tools'
  green, states the limit beside the link rather than in a footnote, and the empty-checklist panel
  now says which of three reasons applies instead of always claiming a questionnaire — but that is
  a design judgement, not a measurement.
- **Only the Netherlands has been rebuilt with recording on.** The other nine hold no delegations
  yet, so the feature is inert for them.
- **Nobody has checked whether a delegate's page still exists.** A dead contractor URL would be
  named as confidently as a live one. It is a link rather than a claim, which is why this was not
  treated as blocking, but it is the obvious next defect.

---

## 88. The corpus does not generalise across travellers, and the ceiling is not the crawler
**2026-08-27 · asked, measured offline, fixed, and proved on one country. Three bugs found by running it**

The question was whether entry 87's result holds across traveller profiles, asked in order to get the
corpus build right before building the remaining forty-three. Entry 87's *selector* numbers are still
`IN/GB/tourism` × 10 and this does not touch them. What it answers is the half that gates the corpus:
**does a store built once serve every traveller?** It does not, and the reason is precise.

### Only 3 to 15% of each corpus was ever opened

`discovered_from` names the page a link was found on, so its distinct values are exactly the pages a
crawl read. Across the ten: AE 265, CA 692, DE 238, FR 646, GB 72, JP 340, NL 262, SE 323, SG 69,
US 139 — against 922 to 9,655 entries each. Of the children of indexes with 30 or more links, **85 to
96% were never opened.**

**That is not itself the defect, and saying why matters.** An unopened URL is still a candidate: it
has an address, and a selector can pick it and fetch it live. The defect is one level down — *a page
whose parent nobody opened does not exist in any form.*

### The Netherlands is the clean case, because one host shows both outcomes

| family | held before |
| --- | --- |
| `schengen-visa/apply-{country}` | **219** — the index linked every one |
| `consular-fees/{country}` | **214** |
| `checklist-schengen-visa-tourism/{country}` | **5** |

217 of the 219 were never opened, and opening one yields that country's checklist for every purpose
plus its fee page. So for 193 of 198 residences the store held **no tourism checklist at all**, and
that page is the whole of the Netherlands' `document_checklist` answer in
`oracle/selection_oracle.yaml`. Japan looks better and is not: 215 mission hosts, of which **160 are
a single landing-page URL**, 27 ever opened, and seven checklist-shaped leaves in the whole network.

### The cause is a scoring failure, and entry 78 already named it

A family member's anchor text is a bare country name. `score_role_vocabulary` has nothing to say
about "Anguilla", so every one of the 219 scores **8.0**, the index listing them scores 17.6, and the
checklist each one leads to would score **25.0** — a page ranked by an anchor that carries no
information about it, which is entry 78 in a new place.

**Lifting the score does not reach them, and that was measured before anything was built:** 764
unopened Dutch pages already score above the index. So the family is given reserved budget instead —
`DEFAULT_CORPUS_FAMILY_SHARE = 0.4`, **zero on the request path**, where a corridor has one traveller
and opening 218 other countries' pages is the definition of a wasted fetch.

**This is not entry 82's proposal.** That closed "raise the total" and "split the total unevenly
between hosts", both by measurement. This changes neither the total nor the split — it changes what
the budget is spent on, within one host.

### Three bugs, none of them visible from reading the code

1. **One reserved pool is not a reservation.** Score-ordered, so the 214-member `consular-fees/{}`
   family (anchors at 12.0) took every slot from `apply-{}` (8.0). The first rebuild read **131 fee
   pages and zero gateway pages**. Only the gateway leads anywhere, and nothing distinguishes a
   gateway from a leaf before one is opened — so it is one queue per family, taken in turn, which is
   `_reserved_per_domain`'s design at a different granularity.
2. **A turned-away family lost its place.** A wave holds one page per host and a family lives on one
   host, so the second family drawn each wave is always refused — and without rewinding the rotation
   it reset to the same family every wave and degenerated back into the pool it replaced. Caught by
   writing the regression test for (1), not by a rebuild.
3. **The destination is named in its own addresses.** `country_family_key` blanked the first country
   token, and `…/visa-the-netherlands/schengen-visa/apply-india` carries two — so all 219 got
   distinct keys, no family formed, and the second rebuild read **zero** gateway pages while passing
   every test. A country named in its own URLs is the ordinary case; `country_family_keys` now
   returns all of them and the caller keeps whichever grouping is largest.

### What the third rebuild did

```
gateway pages read           0  ->  185
tourism checklists held      5  ->   14
checklists, all purposes    40  ->   84
corpus entries           4,571  ->  4,841        indexed page text  1,099 -> 1,771
```

End to end, `netherlands/PH/PH/tourism` — a profile the store could not serve at all — now fills
**four of six roles from the corpus with the crawl skipped, reading nine pages**. Of the four pages
it used, three were already held as unopened candidates and exactly one was absent before: the
Philippines tourism checklist. That is the layer this change adds, isolated.

### The prediction was wrong, and the correction is the useful part

Before building it, this entry's author predicted ~438 pages would take the Netherlands from 5
residences to ~219. **It bought 14.** Of the 185 gateway pages read, 14 link a checklist, 58 link
only Spanish and French forks of themselves, and 113 link nothing — because for most residences *the
Netherlands does not publish a checklist on a government domain at all.* Kenya, Pakistan and Egypt
all say it outright: "On the **VFS Global** website you'll find a checklist with the documents you
need." Nigeria is handled by Belgium's TLScontact.

**So the ceiling on the residence dimension is the authority's publishing choice, not the crawl.**
That is entry 82's form and entry 59's questionnaire in a third shape, and the sharpest of the three:
the guidance exists, is official, and sits on a commercial contractor's domain that the trust rule
refuses — correctly, because `vfsglobal.com` is not a government.

### What is safe to roll out, and what is not

The reservation is gated on the family's shared address (`CORPUS_FAMILY_PATTERN`), because members
cannot be told apart by score — scoring at the floor is the defect — and because the largest country
family on several sites is not guidance: **Canada's is 176 travel-advisory pages and Japan's are 141
country-relations pages.** Without the gate a rebuild of either would spend 40% of its budget on
those. With it, qualifying families are **NL 9, SG 1, and zero for CA, JP and GB**, so the change is
inert for six of the ten — which is the intended outcome, not a shortfall.

- **Proved on one country.** The other nine are untested, and Singapore is the one to do next: its
  per-nationality page fills five roles and the store holds 34 of 198.
- **Entry 87's selector numbers are untouched** and still rest on one nationality and one residence.
- Three rebuilds of one country cost roughly 126 searches and two hours of crawling.

---

## 87. An oracle neither selector built: entry 86's +41 is +30, and the direction holds
**2026-08-27 · TODO item 34. Ten corridors curated by hand; both numbers reported side by side**

Entries 84 to 86 were all graded against a set the two arms constructed between them. A page counted
as answering a role only if some arm had fetched it *and* the adjudicator had credited it, so a page
neither arm read could never enter the oracle. Entry 86 said so and could not do anything about it
from its own data. This is the independent version, and it is now committed:
`oracle/selection_oracle.yaml`, ten corridors, every role named by hand from the corridor's **whole**
contention set — 77 to 552 candidates each — read out of the page-text index, which is filled by the
corpus crawl and the retrieval cache and is indifferent to what either selector picked.

### The result, both columns

```
                             ROLES (independent)   JOINT (entries 85-86)   read
  heuristic, matched budget    33/47    70%          13/29    45%           112
  model                        47/47   100%          25/29    86%           112
  heuristic, shipped budget    43/47    91%          23/29    79%           350
```

**The joint column reproduces entry 86 exactly** — 13, 25 and 23 of 29 — which is the check that says
the replay is the same replay. Against ground truth neither selector helped build, the same three
arms land somewhere else:

- **The selector's margin at matched budget is +30 points, not +41.** Entry 86's headline was
  inflated by eleven points by its own oracle. The decision it justified is untouched; the number
  is not the number.
- **Against the heuristic at its shipped 35 places the margin is +9, where the joint oracle said
  +7** — so the bias did not run one way. It exaggerated the comparison that flattered the model and
  understated the one that did not.
- The heuristic given 35 places reaches **91%**. The practical gap between the two shipped
  configurations is 100% against 91%, at **3.1× the fetches** — a cost argument at least as much as
  a recall one, which is not how entries 85 and 86 read.

Robustness: matching on the model's 127 *selections* rather than its 112 successful fetches moves
the heuristic to 34/47 and the model not at all, so +30 is +28 under the least favourable framing.

### Where the joint oracle was actually wrong: it scored address luck

Singapore's matched-budget heuristic scores **6/6 roles and 0/1 joint**. Both numbers are about the
same document. ICA publishes its India page at three path generations —
`/enter-depart/entry_requirements/…`, `/enter-transit-depart/entering-singapore/…` (byte-identical
text, 4,655 characters each) and `/enter-depart/arriving/overview/…`, which the index never read —
and the joint oracle held whichever one the arm that built it happened to fetch. Canada carries three addresses for "What you
need to enter Canada", three for "How to apply for a visitor visa" and two each for Guide 5256 and
the fee list; GOV.UK serves three chapter URLs of one guide with the same bytes, and publishes its
processing-times guidance under both its old and its new slug. **Fifteen of the fixture's 71 pages
entered it as aliases**, filling 23 role rows, added by a mechanical rule — identical stored body,
same document, same target — because the alternative is a curator's choice of address deciding a
selector's score.

That is a different failure from the one entry 86 named. It expected the joint oracle to be too
*small*; it was also, in places, keyed on the wrong copy.

### The metric changed too, and the reason is the same one

**Role recall, not pages hit.** Entry 86 counted pages, and one page often answers five roles: the
United Arab Emirates corridor is answered end to end by a single GDRFA service page, so an arm
finding it scores 1 there against a five-page denominator elsewhere. The question a selection change
is about is *did this arm choose to read something that answers this question*, so a role several
pages answer is one target. Roles filled stays out entirely — entry 81 measured it swinging ±2 on
identical input, and it grades the adjudicator.

### What the fixture records that no metric does

Thirteen of the sixty roles have **no** answer in their contention set, and saying so is half the
value of the file. France cannot state its decision, its checklist, its fee or its processing time
anywhere readable — all four live behind the Visa Wizard. The United States decision is not
establishable from disk: the Visa Waiver Program page's country list did not extract into stored
text, which is the corridor's own `decision_not_found` seen from the other side. The Netherlands
publishes its UK consular fee at a page holding no text at all.

Two rows are corrections to earlier entries, and both are recorded in the fixture with the rule that
made them:

- **The United Kingdom's per-nationality fee table is keyed on the wrong dimension for this
  corridor.** Entry 82 treated those tables as the UK's unreachable answer. Its first question is
  "Select the country you are **making your application from**" — India — so the ₹18,322 it returns
  is for applying in India. This traveller applies from Britain and pays the £135 on gov.uk. A fee
  table behind a form is still the finding; *which* traveller it answers for is not what entry 82
  assumed.
- **Canada's `imm5484.html` is not a checklist**, despite being titled "Document Checklist:
  Temporary Resident Visa". Its whole text explains how to open Acrobat Reader. Rule 4 of
  `adjudicate_roles.txt` excludes exactly that, and the model arm read it.

### How honest this is, stated plainly

- **The bound is what could be read.** A role can only be answered by a page somebody could read,
  and coverage runs from 21 of 206 candidates in France to 269 of 329 in the United Kingdom. 108 of
  113 curated rows were judged from the page's own stored text; 3 through a byte-identical mirror at
  another address, which is the only way the United States corridor could be judged at all; 2 from
  the address and label alone.
- **There is one residual bias, and it is much weaker than the one it replaces.** After scanning
  each contention set, every page any of the three arms read was reviewed a second time as a
  completeness check, and five real answers were added that the first pass missed — IRCC's fee list
  states "$100" for a visitor visa and the first pass did not open it. That pass covered all three
  arms equally, so it does not favour one; what it does favour is pages *some* arm read over pages
  *no* arm read. Entry 85's oracle could not contain the latter at all; this one can and does.
- **The model at 47/47 should be read with that caveat**, not as proof it is perfect.
- Still one run per corridor, one corridor per country, all `IN/GB/tourism`. Nationality and
  residence are still not varied, which is now the largest untested dimension in the whole harness.

### What is committed

`visa-discover selection-recall` grades any directory of recall logs against the fixture and prints
both columns every time, so the bias entry 86 acknowledged in prose is a number on every run. The
ranking moved out of `CorridorResolver` into a module-level `shortlist()` to make that possible:
replaying it at budgets nobody ran must not require a fetcher, a search provider and a model client.
`_readable_only` stays a method, because it asks the crawl what it saw this run. Fifteen tests, no
network, no model — entries 84 to 86 cost quota to produce and could never be checked twice.

### The method note

Item 34 offered two ways to build this and recommended the slower one. That was right for a reason
neither option statement gave: **the fetch-everything oracle would have inherited the alias bug**,
because it would still have been a set of URLs somebody fetched, and the three ICA addresses would
still have been three different pages to it. Curating by hand is what surfaced that they are one.

---

## 86. Matched-budget: the selector is not 7 points better than ranking, it is 41
**2026-08-26 · re-analysis of entry 85's runs, at no cost. Corrects entry 85's headline and its two "losses"**

Entry 85 compared the heuristic reading **35** pages against the model reading **11**, and reported
the difference as the selector's. **It is not**: two things varied — who chooses, and how many they
choose — so the number measured a *configuration*, not a selector. The project owner said so, and
the controlled version was free, because the recall logs hold every candidate and its scores and
`_shortlist` can be re-run at any size.

### Give both the same number of picks

```
MATCHED BUDGET — both selectors given the same 112 picks
  heuristic @K   13/29   45%
  model          25/29   86%

for reference, heuristic at its shipped 35 places (274 pages)   23/29   79%
```

**+41 points, not +7.** At matched budget the model wins seven corridors, ties three and **loses
none**. The heuristic needs 2.4× the budget to reach 79%, still short of what the model gets from 112
picks.

The confound ran *against* the model, which is why entry 85's number was too small rather than too
large — but "conservative" is not a defence of a design that cannot separate its variables.

### Entry 85's two "losses" were budget, not judgement

It named the United Arab Emirates and the United States as corridors the model lost. At matched
budget:

| | heuristic @K | model | at 35 places |
| --- | --- | --- | --- |
| United Arab Emirates | 1/3 | **2/3** | 3/3 |
| United States | 2/4 | **2/4** | 4/4 |

The UAE flips — the model is better per pick and only lost because it took eleven. The United States
ties. **Neither is evidence that the selector judges worse on thin text coverage**, which is what
entry 85 speculated the US result meant. That speculation is withdrawn.

### The sharpest single row

The Netherlands: the heuristic's top six contain **none** of the four proven pages, where the model's
six contain all four. Singapore's top eleven contain none of its one. A ranking that fills its budget
in score order is not merely coarser than a model reading the pages — for a small budget it can be
uninformative.

### What this changes, and what it does not

- **The decision stands.** `discovery_selector: model` was already turned on; this says the margin is
  far larger than the number that justified it.
- **What it costs is unchanged**: a second model call per corridor, against 2.4× fewer fetches.
- **The oracle is still jointly constructed** from what the two arms read, so a page neither read can
  never enter it. Both arms are graded on a set they made together, and that is the remaining
  weakness of this harness.
- **`_shortlist` was re-run from the recorded scores**, with no pins and an empty crawl-failure set.
  The ordering is exact given those scores; the two omissions could only help the heuristic.
- Still one run per corridor, one corridor per country, all `IN/GB`.

### The method note

Entry 85 was pushed with a headline that a five-minute re-analysis of data already on disk shows was
wrong by a factor of six. Nothing new had to be run and no quota was spent. **When two things differ
between arms, hold one fixed before reporting the other** — and the recall log usually makes that
free after the fact.

---

## 85. Ten countries, ten text indexes: the selector wins by seven points and reads 59% fewer pages
**2026-08-26 · measured across all ten corpus countries. Turns `discovery_selector: model` on**

Entry 84 measured the selector on five corridors, four of them the United Kingdom, and found +30
points of selection recall. This is the same measurement across all ten corpus countries, after
building the eight text indexes that were missing.

### The eight builds

```
      corpus    text            corpus    text
  AE    4,151     755      NL    4,571   1,099
  CA    9,655   1,406      SE    2,246     819
  DE    1,565     389      SG    2,107   1,321
  FR    5,317   1,227      US    2,811     467
  GB      922   1,598      JP    4,803     689
```

~420 searches and about three hours of crawling. Every country now has stored text; coverage of a
corridor's *contention set* ranges from 10% (France) to 82% (the United Kingdom).

### The result, one corridor per country, `IN/GB` throughout

```
SELECTION RECALL over 29 pages proven to fill a role in either arm
  heuristic   23/29   79%   reading 274 pages   11.9 per proven page
  model       25/29   86%   reading 112 pages    4.5 per proven page
```

The model wins or ties **8 of 10** and reads **59% fewer pages**. It loses two: the United Arab
Emirates 2/3 against 3/3, and the United States 2/4 against 4/4.

Roles filled — 22 against 20 — is inside entry 81's ±2 band and settles nothing either way, which is
why it is not the headline.

### Entry 84's +30 points was a sample artefact, and saying so is the point

Four of those five corridors were the United Kingdom, the country with 82% coverage because entry
82's rebuild happened to leave it there. Widened to ten countries the gain is **+7 points**, not +30.
The direction held; the magnitude did not. Any future claim from this harness should say how many
countries it rests on.

### What the two losses look like

The United States has the **lowest text coverage of the ten at 21%**, and the model read 8 pages
against the heuristic's 24 — it chose narrowly on thin evidence and missed two proven pages. That is
the shape entry 80 warned about, arriving in a form the coverage bar cannot see, because here the
model is *told* what it does not know and still chose to read few.

But coverage does not cleanly predict it: France sits at **10%** and the model won there, 3/3 against
2/3. So "low coverage hurts" is a hypothesis this data is too small to test — one corridor per
country — and it is the obvious next measurement.

### The default is flipped, and what it costs

`discovery_selector: model`. Better recall, 2.4× fewer fetches, and the fallback for a country with
no stored text is the heuristic, reported in the corridor's notes rather than silent.

**It costs a second model call per corridor.** That is the honest price: roughly double the
adjudication spend, against a large fetch saving in latency, politeness delay and bandwidth. One line
in `runtime.yaml` reverts it.

### What is still not established

- **One run per corridor per arm.** The selection is deterministic at temperature 0, but the oracle —
  which pages "fill a role" — comes from the adjudicator, and that is the noisy part.
- **One corridor per country, all `IN/GB`.** Nationality and residence are not varied at all here.
- **No latency measurement.** 112 fetches against 274 should be a real saving on a step entry 55
  measured at roughly 40% of a corridor, but nobody has timed it.

---

## 84. Graded on the selection instead of the plan, the model reads half as much and finds 30 points more
**2026-08-26 · measured, five corridors, both arms. Answers TODO item 33; still off by default**

Entry 83 shipped the selector as a prototype with n=1 and one named suspect: the prompt said "prefer
fewer" and the model used 7 of an allowed 10, choosing a publication landing page over the content
child that held the checklist. Entry 81 said how to measure it — **grade the selection, not the
plan** — and this is that measurement.

### The metric

For five corridors, run every arm and pool the pages that filled a role in **any** of them. That
pooled set is the oracle. Then ask the only question a ranking change is really about: *did this arm
choose to read them?* Role counts are reported second because entry 81 measured that metric swinging
±2 on identical input.

### The result

```
SELECTION RECALL over 33 pages proven to fill a role in some arm
  heuristic (35 places)      18/33   55%   reading 143 pages   7.9 read per proven page
  model, choose <=10         15/33   45%   reading  30 pages   2.0
  model, choose <=20         28/33   85%   reading  73 pages   2.6
```

**The wider selection beats the heuristic by thirty points while reading half as many pages.** Per
corridor it wins or ties everywhere: 5/6 against 2/6, 6/8 against 4/8, 6/7 against 4/7, 7/8 against
4/8, and 4/4 against 4/4 on Japan.

**Read the heuristic's 55% carefully — it is not a fall.** Its absolute hits never moved, at 18. The
denominator grew from 21 to 33 because the wider selection *proved twelve more pages fill roles*,
pages the heuristic's 35 places never read. That is the finding stated most plainly: **a model
choosing 15 pages from stored text found role-filling pages that ranking 35 links did not reach.**

Roles filled, secondary and noisy: 24, 16 and 10 across the five corridors, in the same order.

### So "prefer fewer" was the defect, and it is worth naming why

Reading a page is cheap; being wrong is not. The instruction traded a fetch against a role and got
the exchange rate backwards. It now says to take a second candidate wherever the first might be a
landing page, an index, or the wrong post — the three shapes entry 83 watched it get caught by —
and `DEFAULT_SELECTION_SIZE` is 20. At 2.6 pages per proven page it is still three times more
economical than the heuristic's 7.9.

### What this does not settle

- **The oracle is adjudicator-derived.** Which pages "fill a role" comes from the noisy call, so the
  denominator carries some of that noise even though the recall question does not. A thirty-point gap
  is far outside entry 81's ±2 band, but it is not a clean measurement, and pretending otherwise is
  how entry 80 happened.
- **Five corridors, one run each, two countries.** The United Kingdom is four of the five.
- **It only runs where stored text exists** — the UK at 82% of its contention set, Japan at 50%.
  Everywhere else falls back to the heuristic and says so in the corridor's notes.
- **It costs two model calls against one**, and a selection packet of a few hundred excerpts. Fewer
  fetches, more tokens.

### Still off by default, and what would change that

`discovery_selector: heuristic`. The measurement is favourable and the fallback is safe and reported,
so the case for turning it on is real — but it rests on five corridors in two countries, and the one
country with good coverage got there through entry 82's rebuild, which was itself a mistake being
undone. Widen it to the ten corpus countries before flipping the default, and build text indexes for
the eight that have none.

---

## 83. A model chooses what to read, and the stored-text barrier moves from an absence to a type
**2026-08-26 · prototype, off by default. Amends entry 78's rule deliberately**

The heuristic shortlist is the **recall gate**: measured over 135 recall logs it decides in 100 of
them, with a median of 72 candidates in contention for 35 places, and a page it ranks out is never
fetched and never judged (entry 40). This replaces that gate with a model call over stored page text
and moves the fetch *after* the choice.

```
today     score_link -> 35 fetches -> model over 35 fetched pages -> pick 6
prototype model over stored text of every in-contention candidate -> pick ~7 -> fetch those
```

### Two calls, because one would break entry 78

`Selection` carries source ids and **has no field for prose**. Stored text is older than
`source_maximum_stale_hours` and carries nothing to say how old it is, so a sentence written from it
and shown to a traveller is guidance served outside the freshness rules. Splitting the work keeps
that impossible rather than discouraged:

| | reads | may produce |
| --- | --- | --- |
| selection | stored text | source ids, nothing else |
| adjudication | text fetched **this run** | every word a traveller sees |

Naming a questionnaire stays in the second call, on fetched text, so entry 60 is untouched —
selection can route a suspected wizard into the fetch set and never describe one.

**And the barrier moved rather than went away.** Entry 78 said there is no accessor for a stored
body and named `snippet()` as the thing not to add. `text_for_selection` is now exactly that
accessor. The amendment is deliberate: the reason for that rule was never that reading stored text is
wrong — `rank` reads it — but that a *sentence written from it* must not reach a traveller. That
property now lives in `Selection`'s shape instead of in the absence of a method, and
`test_a_selection_cannot_carry_a_word_of_stored_text` is where it is enforced. The method is named
for its single caller so a second one has to argue for itself.

### Why a model and not a better score, which entry 80 answered by failing

Stored text covers some candidates and not others. Entry 80 folded that into `combined` as a numeric
lift and it went wrong for a reason worth stating once more: **a scalar cannot represent "nothing is
known about this page".** Absent text scores zero, zero is a number, and a number competes. The
packet says it in words — `no_stored_text`, with the prompt told explicitly that this is an absence
of evidence and not evidence of absence — and the candidate is still offered. **No candidate is ever
dropped for want of room**: a wide field shortens excerpts instead, down to 200 characters.

### First run, `united-kingdom/IN/GB`, and it is one run

```
                    read   roles filled                                    cost
heuristic             35   document_checklist, processing_times            1 call
model selection        7   general_entry                                   2 calls
both                       visa_decision handed over as gov.uk/check-uk-visa
```

329 candidates in contention, 269 with stored text, 7 chosen. **The fetch saving is real — 7 pages
against 35** — and the questionnaire was spotted by both.

**It filled fewer roles, and the visible cause is precise.** The model chose
`gov.uk/government/publications/visitor-visa-guide-to-supporting-documents`, the publication landing
page; the heuristic used its content child
`.../guide-to-supporting-documents-visiting-the-uk`, which is where the checklist actually is. The
model picked the right *document* and the wrong *URL for it*, and at seven pages there was no
redundancy to absorb the near-miss. Thirty-five places buy exactly that redundancy.

Two suspects, neither measured: `DEFAULT_SELECTION_SIZE` is 10 and the model used 7, so the prompt's
"prefer fewer" may be advice worth withdrawing — fetching is cheap next to being wrong. And a landing
page and its child are hard to tell apart from a stored excerpt of the head.

**This is n=1 per arm against a metric entry 81 measured swinging ±2 roles, so none of it is a
result.** It is a working prototype and a specific hypothesis.

### What is deliberately not claimed

- Not that this is better. One run, noisy metric, and it filled fewer roles.
- Not that it is cheaper. Two calls against one; the selection packet was ~270 excerpts. Fewer
  fetches, more tokens.
- Not that the coverage problem is solved. The United Kingdom has 82% of its contention set stored
  because entry 82's rebuild left a 1,598-page index. Japan has 50%. **Everywhere else falls back to
  the heuristic and says so** — reported in the corridor's notes, never silent, because a selection
  made from anchors alone is the weak version of this idea wearing the strong version's name.

### How to measure it, when it is measured

Entry 81's rule: **grade the selection, not the plan.** For corridors with known role-filling pages,
count how often the selection contains them, with no adjudicator in the loop. That is deterministic,
free of the ±2 noise, and answerable from recall logs already on disk. Role counts come second.

---

## 82. The nationality dimension is not a budget problem: Canada published links, the UK published a form
**2026-08-26 · built, measured, defaulted off. Closes item 32 and corrects entry 81's own reframing**

Item 32 was reframed twice and both framings were wrong. This records what the crawl is actually
limited by, because the answer is not about the crawler at all.

### The reframing, which was a real improvement on the first version

Entry 81 closed "raise the total budget" by showing 90% of a candidate set can never be shortlisted.
The obvious successor: the problem is not the *total* but the **even split**. `host_budget` is
`maximum_pages // seed_hosts`, the same cap for every host regardless of what each holds — and the
comparison looked decisive:

```
Canada  ircc.canada.ca ?country=XX     425 pages over 213 country values
UK      visa-fees.homeoffice.gov.uk     91 pages over  15 country values
```

Same code, same rule. So `HostBudget` was built: a **floor** every seeded host is guaranteed, a
**surplus** the rest compete for on score, and a **ceiling** of half the crawl so the surplus cannot
become the old problem in reverse. It is tested, it does what it says, and the United Kingdom was
rebuilt at `--pages 3000` to prove it.

### It moved almost nothing, and the reason ends the line of enquiry

```
visa-fees.homeoffice.gov.uk     91 -> 113 pages     15 -> 20 nationalities
```

It was never budget-limited. Measured on the rebuilt corpus:

> **Zero of its 86 fee pages were reached from a *different* nationality's page.** Seventy-eight came
> from within the same nationality's subtree; the eight entry points came from search seeds that
> happened to name a country.

The country selector on that service is a **form**. There are no links between nationalities, so a
crawl holds exactly the nationalities search seeded and no budget changes that. Canada's 425 pages,
checked the same way, came from **outside** the `?country=` space entirely — a page on `canada.ca`
that lists every country as an ordinary link.

**So the difference between 213 and 15 is what the authority published, not what the crawler was
allowed to spend.** That is entry 59's wall — the answer behind a questionnaire — one layer down,
and it is the same wall whether a corridor meets it live or a corpus meets it offline.

### And removing the cap cost something, which is why the default is off

With no even cap the surplus goes to whichever host offers the most links. For the United Kingdom
that is `www.gov.uk`, the whole government website:

```
UK corpus   922 entries, 12 hosts  ->  4,530 entries, 25 hosts
                                       4,252 of them on www.gov.uk
```

Most of that is not visa guidance. `DEFAULT_CORPUS_HOST_FLOOR` is therefore **0** — the even split
stays, and `HostBudget` keeps it as a named special case rather than an accident of arithmetic. The
mechanism is kept because the two halves are separable and only one misbehaved: the **floor** is a
guarantee that a small mission host is never starved, which is known problem 24's failure mode, and
it is the **surplus** that inflated the corpus. Revisit the floor on its own, with a measurement.

### What the rebuild did leave, and it is the useful part

```
GB text index   0 -> 1,598 pages
UK corridor     3,784 candidates, 34% with text overall
                705 in contention, 602 with text -> 85%
```

Japan is at 13% either way. **If entry 81 is right that the coverage bar should count candidates that
can actually be shortlisted rather than all of them, the United Kingdom is the first country above
it** — and the first place item 31's lift could be tested on something other than a country where it
is inert. That is a lead, not a result: one UK corridor after the rebuild filled two roles and refused
the decision, which is inside entry 81's ±2 noise band and cannot be read either way without the
adjudicator-free measurement item 31 now calls for.

### What this says about the original question

The question behind items 19, 31 and 32 was whether a corpus can serve a corridor without live
search. Measured across 30 corridors into the ten corpus countries: **18 had zero misses, and of the
67 pages missed in total, none were on a host the corpus lacks.** Site-level recall is solved. What
remains is one page-level gap with two different causes, and only one of them is ours:

1. **Deep pages on covered hosts** — ordinary crawlable links the budget did not reach. Fixable.
2. **Spaces behind a form** — the UK's per-nationality fee tables. **Not fixable by crawling**, at
   any budget, by any allocation. It is the questionnaire outcome (entries 59 and 60) appearing as a
   corpus gap rather than as a corridor one, and the honest response is the same: name the tool.

---

## 81. Item 32's premise is false, and so was entry 80's: the metric could not see what it claimed
**2026-08-26 · measured. Withdraws entry 80's mechanism and its regression; closes item 32 unbuilt**

Item 32 said: text coverage is 13%, the coverage bar needs half, so raise the corpus page budget.
Measuring the proposal before implementing it — which is what [CLAUDE.md](CLAUDE.md) requires and
what entry 77 records the cost of skipping — killed it, and took entry 80 with it.

### 90% of a candidate set can never be shortlisted, so the bar counts the wrong thing

```
japan/IN/GB, 1,189 candidates            with text   share
  every candidate                          113/1189     10%
  scores for some role at all              58/116       50%
  scores >= 20                             45/64        70%
  actually shortlisted                     35/35       100%
```

**1,073 of 1,189 candidates score zero for every role.** They cannot be shortlisted, so the lift can
neither promote them nor be distorted by them. Entry 80's bar counts them all, which is why Japan
reads as 13% covered while the pages that actually compete are 50–100% covered. A bigger crawl would
have spent hours raising a number whose denominator is inert.

### And entry 80's mechanism was wrong

Entry 80 said the lift "ranked by who was crawled": all eleven pages it added had index text, so the
uncovered ones — the UK post among them — could never be lifted. The check that entry did not run:

```
with-index shortlist    35/35 have index text   (100%)
without-index shortlist 33/35 have index text   ( 94%)
```

**The shortlist was already 94% indexed without the lift.** There was no coverage skew to find. What
the lift actually did was different again: five of the eleven pages it promoted had a link score of
**0.0** — MOFA's long-stay category pages for Professor, Student and Cultural activities — lifted to
+39 on a tourism corridor because a long-stay page also says "necessary documents". With
`link_score` at zero, `max(link, 0.4·link + 0.6·text)` is just `0.6·text`: the text was not refining a
link score, it was creating one.

That is fixed and kept — `combined` now applies stored text only to a page the link scorer scored for
*something*, so text may **re-file** a page across roles (Japan's checklist PDF: 22.0 as
`visa_decision`, nothing for `document_checklist`) and never rescue one the link rejected outright.

**But fixing it changed nothing measurable, which is the actual finding.**

### The metric cannot resolve the question, and six runs of one configuration prove it

With the lift disabled in both arms — **identical code, identical inputs** — six corpus-only runs of
`japan/IN/GB`:

```
roles filled   4  4  4  4  5  6
```

and *which* roles fill moves too: one run gave `application_route, fees, processing_times`, the next
`document_checklist, general_entry, fees`. **The noise floor is ±2 roles and the role identity is
unstable.** Every A/B in entries 79 and 80 was three runs an arm inside that band.

So entry 80's "the lift cost two roles on every one of three runs" is **withdrawn**. 4/4/4 against
4/6/5 is not a regression; it is two samples from the same distribution. Entry 79's "all six roles"
was withdrawn for the same reason one entry earlier, and I did not apply the lesson to the entry
doing the withdrawing.

### What the right metric is, and by it the lift is neutral

Role count is measured *after* adjudication, so it grades the model, not the ranking. The question a
ranking change actually asks is whether the pages that fill roles reach the shortlist. Checked
directly, under every configuration tried:

> The Edinburgh fees page (92.4), the MOFA checklist PDF and the Edinburgh checklist PDF are
> **shortlisted and fetched in every arm.** The lift never lost them. It changed which eleven *other*
> pages shared the packet, and the model answered differently.

So the lift is recall-neutral on this corridor, and its effect on role counts is an artifact of
packet composition reaching a model that is sensitive to it. Neither harm nor benefit is established.

### What ships, and why it is the conservative choice

The lift stays **off**. Not because it was shown harmful — that claim is withdrawn — but because
nothing shows it helps, and this project does not ship an unproven change to the layer that decides
what a traveller is told. The coverage bar is what holds it off; its *stated reason* in entry 80 was
wrong and is corrected here, and the bar itself is now doing a job it was not designed for.

**Item 32 is closed unbuilt.** Coverage is not what limits this, so ~70 searches and a multi-hour
crawl would buy a number, not an answer.

### What would actually settle it

Not more runs of this corridor. Either:

1. **Grade the shortlist, not the plan** — for a set of corridors with known role-filling pages,
   count how often each reaches the shortlist, with no model in the loop. Deterministic, free of
   adjudication noise, and answerable from recall logs already on disk.
2. **Enough corridors that ±2 roles averages out** — entry 58's twenty-corridor harness, both arms.
   That is the expensive option and it should come second.

Known problem 10 has said adjudication varies between runs since it was written. This is the first
time it was measured, and it is larger than anything built on top of it assumed.

---

## 80. Entry 79 shipped a regression, and twelve runs found it: stored text may not rank a set it barely covers
**2026-08-26 · measured, and it corrects entry 79 rather than extending it**

Entry 79 wired the body score in front of the shortlist and said the corpus-only comparison was
inconclusive because both contested pages had been shortlisted and fetched in either arm, so the
difference must be adjudication variance. **Credit was restored and the runs were repeated. That was
wrong, and the mechanism was one entry 79 had already named and then failed to apply to itself.**

### The result, `japan/IN/GB`, corpus-only, three runs each way

```
with the lift      4  4  4 roles   never document_checklist, never fees
without it         4  6  5 roles   always both
```

**The with-lift arm is identical three times out of three**, which rules out adjudication variance
outright: it is not noise, it is a stable, worse answer. Entry 58's rule about needing two runs of a
corridor caught this; one run of each arm had not.

### Why, and it is the dimension entry 79 predicted and then did not guard

`combined` refuses to let stored text *lower* a score. **That protects the score and not the place.**
A shortlist is finite, so lifting some candidates displaces others — and which candidates *can* be
lifted is decided by whichever hosts the crawl happened to reach:

```
index coverage over this corridor's 860 candidates
   90%  www.evisa.mofa.go.jp
   61%  www.ezairyu.mofa.go.jp
   34%  www.edinburgh.uk.emb-japan.go.jp
   13%  www.anzen.mofa.go.jp
    5%  www.mofa.go.jp
    0%  www.uk.emb-japan.go.jp      <- the post serving a traveller applying from Britain
```

**All eleven pages the lift added to the shortlist had index text. The eleven it displaced included
the UK post's own fee and checklist pages.** 115 of 860 candidates carried the signal, so the lift
was not ranking pages by what they say; it was ranking them by whether anyone had crawled them.

This is entry 62's finding in a new place — a bonus only some candidates can earn ranks by
eligibility — and it is the **post** dimension again, which entry 70 established is the one that
actually varies and entry 79's own closing section warned `score_body` cannot see.

### The rule, and it is a statement rather than a threshold

`_text_scoring_is_fair`: stored text may rank a candidate set only when it covers **at least half**
of it. Below that, presence in the index predicts rank better than anything a page says. Above it
the uncovered pages are the exception rather than the rule.

`DEFAULT_TEXT_COVERAGE_BAR` is a constructor argument **so the rule can be measured against, never
so a caller can lower it to get more pages through**. A country under the bar is fixed by covering
it ([TODO.md](TODO.md) item 32), not by moving the bar.

### And the search-up path says the same thing, where one run had suggested otherwise

Entry 79 quoted a single search-up run filling all six roles with 115 candidates lifted. Repeated:

```
gate on  (no lift)   4  5  5 roles   always document_checklist
gate off (lift)      3  5  5 roles   lost document_checklist once
```

So the six-role run was an outlier. **Across twelve runs on both paths the lift never helped and
sometimes hurt.** With the gate, Japan's corridors are byte-for-byte what they were before entry 79 —
which is the correct outcome for a country at 13% coverage, and the honest description of what the
index currently contributes to ranking: **nothing, and that is now enforced rather than hoped.**

### What is actually settled, and what entry 79 over-claimed

- **Entry 78 stands.** The corpus really did store 29 characters of anchor against 3,602 of body, and
  the checklist page really is filed under the wrong role by its anchor. Keeping the text is right.
- **Entry 79's plumbing stands** — `text_scores`, `best_combined`, step 3b. What it lacked was a
  precondition.
- **Entry 79's "all six roles" is withdrawn** as evidence. It was one run, and three runs of the same
  configuration produce three, five and five.
- **The index has not yet been shown to improve ranking at all.** It cannot be, until a country is
  covered past the bar. That makes item 32 the prerequisite for item 31 rather than a follow-up to it,
  which is the reverse of the order entry 79 left them in.

### The method note, because this is the fifth time

The corrections table in [CLAUDE.md](CLAUDE.md) exists because a written-down diagnosis keeps naming
the wrong cause. This entry adds two rows and both are *mine, from yesterday's session and from four
hours ago*. The one that would have saved the most: **"both pages were shortlisted, so the difference
is downstream" is not a finding, it is a hypothesis** — and the run that would have tested it cost six
model calls.

---

## 79. The body score moves in front of the shortlist, and stored text may lift but never sink
**2026-08-26 · implemented. TODO item 31; the measurement that would settle it is blocked on credit**

Entry 78 built the index and stopped one step short. This wires it into `resolver.py`.

### Where it goes, and the order is the whole point

`score_body` has existed all along and has always run at step 5, on pages already fetched
(`resolver.py:1113`). A page the anchor scorer filed under the wrong role was never shortlisted,
never fetched, and so never had its text read at all — **the right scorer, running after the gate it
should be part of**. The new step 3b scores every candidate whose text the index holds, before
`_shortlist`, and the corridor's notes say how many.

Every candidate is offered, never a promising subset. Narrowing first would put the link scorer back
in front of the text scorer, which is the defect being removed and the one `MAXIMUM_SCORED_MATCHES`
records being made inside `rank` itself.

### `text_scores` is a second field, and the asymmetry is why

`CandidatePage.combined` already blended link and body at 0.4/0.6. Assigning index text to
`body_scores` would have reused it for free and been wrong.

> After a fetch, a zero for a role is a **fact**: we read the page and it does not answer this.
> Before one, a zero can just as easily be a stale row or a PDF whose text layer came out badly. Run
> through the blend, that page drops to 0.4× its link score — **beneath a page nobody has any text
> for at all.** Holding a page's text would cost it its shortlist place, and entry 40 says a page
> ranked out is never fetched and never recovers.

So stored text may **raise** a candidate and never lower one: `max(link, 0.4·link + 0.6·text)`. A
fetched `body_scores` still governs in both directions and takes precedence.

`best_combined()` replaces `link_scores.best()` throughout `_shortlist`. It had to: the per-role pass
ranks on `combined`, so without it a page could be reserved a place for the text it holds and then be
cut by an ordering that could not see that text. **Reserved-then-cut is worse than never reserved,
because it looks like the protection worked.**

### Live, `japan/IN/GB`, search up

**All six roles filled**, 115 candidates ranked on text as well as link, crawl skipped, 35 pages read,
one model call. The checklist came from the UK post — `uk.emb-japan.go.jp/itpr_en/sightseeing.html`,
*"ITEMS REQUIRED FOR TEMPORARY VISITOR VISA APPLICATION (For sightseeing)"* — and the route from
`visaonline.html`, the page entry 77 wrongly called unreachable.

### The corpus-only comparison is **not** settled, and the reason is not the one expected

One run of each arm, search disabled:

```
without the index   visa_decision  document_checklist  fees            general_entry
with the index      visa_decision  application_route   processing_times general_entry
```

Four roles either way, a different four. That looks like a regression on the checklist, and reading
the recall log says it is not a recall result at all: **both contested pages were shortlisted and
fetched in both arms.** `edinburgh.../00_000203.html` was fetched at 92.4 with `fees` as its best
role, and `fees` still went unfilled. The difference is downstream of everything this entry changed —
known problem 10, adjudication variance, which entry 58 already says one run cannot see through.

**So the honest position is that item 31's measurement has not been taken.** Repeating each arm three
times was the plan and it stopped at the second run: the OpenAI account ran out of credit. The
corridor refused rather than degrading, which is entry 31 working.

### A reporting defect that cost an hour, found by hitting it

Diagnosing that took a hand-written API call, because every adjudication failure arrived as the same
sentence: *"The role adjudication request failed"*. The cause was in hand at
`adjudication.py:441` and thrown away.

This is **entry 74's finding on the other provider**, and it is now fixed the same way.
`AdjudicationQuotaExhausted` is its own type, told from ordinary rate limiting by the body's
`insufficient_quota` / `credit_balance_exhausted` rather than by the status — OpenAI answers `429`
for both, and waiting is the remedy for one and useless for the other. Every other failure now
carries its cause instead of replacing it.

**And it is not retried.** `_adjudicate_with_one_retry` exists for momentary failures; a second call
against an empty account cannot succeed and is billed the same as the first. A classification no
caller acts on is worth nothing, which is the half of entry 74 that was easy to miss.

### What is left

Item 31 is code-complete and **unmeasured**. When there is credit: three runs of each arm on the ten
corpus countries, which is entry 76's test. Until then the only claim supported is the one above —
all six roles, once, with search up.

And text ranking is still not a replacement for `score_link`. `score_body` takes a nationality and no
residence, so it carries none of the post logic (`mission_host_bonus`, `other_mission_penalty`) that
entry 70 established is the dimension that actually varies. The blend is what keeps that: the link
score knows about posts, the body score knows what the page is.

---

## 78. The corpus stored the link, not the page — and 91% of a country was never read at all
**2026-08-26 · implemented and measured. Answers the architecture question behind entries 44, 76 and 77**

The question asked was whether the corpus is worth having at all, given that visa guidance varies by
passport and residence and a corpus can carry neither. The answer is that the premise is half wrong
and the half that is right was never the problem.

**Nationality costs the corpus nothing.** Entry 70 measured it across 41 destinations: not one
published a page per passport. A passport changes the answer read *off* a page, not which page
exists. **Residence is real**, and entry 70 named its shape — the **post** — which is a bounded,
enumerable list per destination (Japan's corpus holds 48 mission hosts), not a 198-valued dimension.

So the corpus can cover what matters. What it could not do was **find** anything in itself.

### What the corpus actually stored

`CorpusEntry` holds `url`, `title`, `link_text`, `heading`, `depth`. `crawl._expand` read each page's
HTML, took the title and the links, and let `html` go out of scope. Every byte of every body a crawl
fetched was discarded at that line.

| | |
| --- | --- |
| JP corpus entries with no title at all | **93%** (CA 92%, US 95%) |
| median description per entry | **29 characters** |
| median body of a page in `var/cache/` | **3,602 characters** |

So a corridor ranked three thousand pages on a median of 29 characters — an anchor, a heading, and
whatever words were in the URL — while a search engine ranked the same pages on their full text.
**That asymmetry, not crawl depth, is what entries 76 and 77 were measuring.** "A crawl reaches pages
by following links; search reaches them directly" (entry 77) is true, and the reason is that Brave
indexes bodies and this project indexed slugs.

### The case, and it is worse than "ranked out"

`mofa.go.jp/files/000121327.pdf` fills `document_checklist` for `japan/IN/GB`. The corpus knows it as
`link_text="Single Entry Visas (PDF)"` under `heading="Application Procedures for"`, at a URL of pure
digits. Its first two hundred characters read *"Checklist for Single-Entry Short-Term Stay Visa, for
all nationalities except China, Russia... Purpose of Visit... Tourism... Documents to be submitted"*.

```
ANCHOR, document_checklist, over 3,029 JP corpus entries
  pages scoring for the role at all : 166
  position of the checklist PDF     : NOT SCORED FOR THIS ROLE AT ALL   (it scores 22.0 as visa_decision)
```

It is not ranked low. It is filed under a **different role**, so entry 61's fix — reserving more
shortlist places per role — could never have recovered it at any depth. The anchor is not junk
either: "Single Entry Visas (PDF)" is a good short label. **A 40-character label can name a page's
subject; it cannot name the roles it fills or the populations it covers.** Literal junk anchors
("here", "PDF") are 19% of Japan's entries and 0.7% of Canada's — never the failure mode.

Across the 32 pages held in both a corpus and the new index, anchor and body **agree on the role 9
times out of 32**. The largest disagreement class is `visa_decision → document_checklist`, 6 pages —
which is exactly the role entry 76 measured corpus-only runs losing in four of ten countries.

### What was built

**`discovery/page_text.py`** — one SQLite/FTS5 database per country, mirroring `FileCorpusStore`.
Not in the corpus JSON, and that is the point: that file is read whole and validated through pydantic
on every request (51ms for Japan's 1.4MB), and text would take it to ~35MB and about a second of
parsing per corridor, on a pipeline whose entire justification is latency.

**It is ranking, never evidence, and the type says so.** `rank` returns URLs and scores; there is no
accessor for a body and `TextMatch` has no field to hold one, for the same reason `build_blocked_packet`
has no parameter for page text (entry 57). Stored text is older than the rules governing what a
traveller may be told, so a quote from it would be guidance served outside `source_maximum_stale_hours`
with nothing to say how old it was. A page this index ranks is still fetched through `LiveSourceFetcher`
before a word reaches a plan; the worst a stale row does is win a shortlist place for a page that has
changed, which is a wasted fetch and not a wrong answer.

**Two ways in, complementary.** `visa-discover pagetext --backfill` indexes every body the retrieval
cache already holds — no fetch, no search, 154 pages across 11 countries on the first run. And
`visa-discover corpus` now keeps the text and title of every page it reads, streamed through an
`on_page` callback rather than accumulated, since an offline crawl reads thousands.

### `rank` reuses `score_body`, and the first version proved why

The first `rank` scored the text itself and gave a page 40 points for naming the traveller's
nationality anywhere in its body. The comment above `written_for_nationality` in `scoring.py` records
that exact mistake already made and measured: **Japan's ministry-wide checklist names India once,
inside a table of nationality exceptions, and that alone made it beat the UK post's own checklist.**
`score_body` reads nationality from the title and URL for that reason.

So FTS5 does **recall** — narrowing to pages whose text carries the role vocabulary at all, the thing
anchor text cannot do — and `score_body` does **precision**, unchanged and uncopied. Which surfaced
the finding underneath: **`score_body` was already the right scorer, running after the gate it should
be part of.** It is called at `resolver.py:1113`, on pages that have already been fetched. A page that
anchor text ranked out is never fetched, so its text is never scored. The index is what lets the same
judgement run *before* the shortlist instead of after it.

### Two gates were deciding what got read, and both were the request path's

Keeping the text exposed how little a corpus build actually reads. On Japan, of 3,103 entries:

| gate | cost |
| --- | --- |
| `expansion_threshold = 10.0` — a link is followed only if its **anchor score** clears 10 | **2,834 of 3,103 (91%)** never qualify |
| PDFs are never followed — `_expand` will not queue one | **795 of 3,103 (26%)** |

The threshold is a latency compromise for a sixty-second corridor, and this job has no such bound.
The PDF rule is correct as far as it goes — a PDF is a destination, not a signpost, and fetching one
to look for links it cannot have is waste — but authorities publish checklists as PDFs, which is what
`pdf_checklist_bonus` exists for. So `CORPUS_EXPANSION_THRESHOLD = 0.0` for the offline job (the page
and per-host budgets still bound it, and the frontier is still best-first, so this only decides what
fills the remainder), and PDFs are read in a **second pass, for text only**, best-scoring first.

**Every guard survives.** `fetch_pdf_text` and `fetch_html` share one `_get`: the same `robots.txt`
verdict, the same politeness delay, the same trust re-check on the landing URL after a redirect, the
same challenge-versus-refusal reading of a blocking status. A second retrieval path that checked less
would be the hole all three checkpoints exist to close. A challenge answered by the renderer returns
HTML whatever the URL's extension said, so `fetch_pdf_text` refuses it rather than reading a rendered
page as a document.

### Measured: Japan rebuilt, same 70 queries, same `--pages 1500`

```
                     before          after
crawled               1,890          3,682
corpus entries        3,103          4,803    (+1,700)
depth                 d1 1805        d1 1819  d2 814  d3 1049
                      d2   85        depth_is_exercised: 4% -> ~50%, warning gone
text kept               176            650    including 101 PDFs
index                 209 pages      684 pages    39 -> 48 hosts
                       17 PDFs        94 PDFs    176 -> 574 titled
disk                   3.6 MB         7.3 MB
```

Entry 77 found that a 2.4× page budget bought nothing on the measure that mattered. It bought nothing
because more *entries* is not more *readable* pages: the threshold was excluding 91% of them from ever
being fetched. The same budget, with the threshold dropped, took the build from "fetched its seeds and
stopped" to genuine depth 3.

### A third instance of the same defect, made by this entry

After the rebuild the checklist PDF vanished from the results. `rank` had been taking the BM25 top
`limit × 8` and handing only those to `score_body` — **a cheap ranker gating the good one, which is
the defect this entry is about.** The checklist sits at **BM25 position 116 of 122**: a 15,000-character
document that says "checklist" once is what BM25 punishes and what `names_documents` rewards. Asking
for six results silently narrowed recall to 48.

Every page matching the role vocabulary is now scored — 121 of 684 for Japan's widest role, so the
MATCH was always the real filter. `MAXIMUM_SCORED_MATCHES` is an absolute safety bound and deliberately
not a multiple of `limit`. Result:

```
  8. 73.5  https://www.mofa.go.jp/files/000121327.pdf         <- of 121 scored
 11. 73.5  https://www.uk.emb-japan.go.jp/itpr_en/sightseeing.html
```

### What this does not do, stated so it is not oversold

- **Nothing reads the index yet.** No resolver wiring; the corpus path is untouched. The end-to-end
  claim — that a corpus-only run keeps its checklist — is **unmeasured**.
- **Text ranking is not a replacement for `score_link`, and must not become one.** The top of Japan's
  checklist ranking is Calgary and Houston consulate pages: genuinely good checklists, for the wrong
  post. `score_body` takes nationality and no residence, so it has none of `score_link`'s
  `mission_host_bonus` or `other_mission_penalty`. The link score knows about posts, depth and host
  kind; the body score knows what the page *is*. Combining them is the next step; swapping one for
  the other would lose the residence dimension that entry 70 established is the real one.
- **Text coverage is 13% of corpus entries** (605 of 4,803), up from 7%. The remaining bound is the
  per-host budget: `1500 // 48 hosts` ≈ 31 fetches against `mofa.go.jp`'s thousands of pages. Unlike
  entry 77's finding, `--pages` binds this directly — every extra fetch is an extra indexed page.
- **`unreadable` went 28 → 721.** The crawl now tries links it used to skip and many are dead or
  non-HTML. That is honest reporting of what was always there, but a reader of the build output
  should know why the number moved.

---

## 77. Does the corpus inherit search's weaknesses? Three diagnoses, all wrong, and one real defect
**2026-08-26 · measured. Rewrites known problem 24; gates TODO item 30's stage 3**

A fair question before paying for 43 corpora: **the corpus builder seeds itself from search, so does a
search-recall gap get frozen into the store?** The mechanism is exactly as suspected —
`build_country_corpus` runs `all_corpus_queries` (70 for Japan) and every host in the corpus descends
from those results. The conclusion, measured, is that search recall is **not** what limits them.

### What the corpus is actually made of

Across the ten built corpora, **97–100% of entries lie beyond the seeds**: AE 100%, CA 98.9%, NL 99.3%,
JP 100%. Search picks the entry points; the crawl does all the volume. And seeds are already
privileged — pushed onto the frontier at `-1000.0`, ahead of every discovered link, under a fair
per-host budget.

### The test case, and three diagnoses that were all wrong

Known problem 24 said Japan's corpus holds 29 mission hosts and **not** the London embassy, "where five
of its six roles came from". A per-post authority missing the busiest post is exactly the shape that
would prove the worry.

| diagnosis | whose | what the measurement said |
| --- | --- | --- |
| search never seeds London | the question's | **wrong** — running Japan's own 70 corpus queries returns `www.uk.emb-japan.go.jp` |
| the crawl budget starves it | mine | **wrong** — seeds already sort ahead of everything at `-1000.0` |
| the corpus has a recall gap there | known problem 24's | **wrong** — `www.uk.emb-japan.go.jp` answers a genuine Akamai `403`, the same signature as Greece's `www.mfa.gr`. Nothing can fetch it, by search or by crawl |

**And the premise was stale too.** Japan's latest run filled **all six roles from `mofa.go.jp`**, out of
the corpus, with search down. It does not need the London embassy at all. Four plausible readings, one
`curl`, and only the `curl` was right — the fourth time in two days.

### The real defect, which the rebuild reported about itself

Rebuilding Japan: **70 queries, 276 seeds, 1,918 crawled** — and the job's own warning:

> *only 7% of what it found lies beyond depth 1 — this crawl fetched its seeds and stopped, which is
> the request path's behaviour, not this job's. Raise --pages well above the seed count.*

`DEFAULT_CORPUS_PAGES` is **1,200** against **7%** measured, where `MINIMUM_DEEP_SHARE` wants 10%.

> **The framing here was corrected by the project owner, and the correction matters more than the
> finding.** A corpus is not for reaching depth the request path cannot; **both paths are supposed to
> find the right page.** The corpus exists because a live corridor took 50+ seconds and *which pages
> exist* does not change per traveller — entry 44's own words, and entry 55's 2.1×–5.2×. Depth is a
> means, never the point, and `depth_is_exercised` is a **proxy** for cache completeness, not a goal.
>
> **So the acceptance test for a corpus is its hit rate on the pages that actually fill roles.**
> Measured on `japan/IN/GB` with search up, immediately after a rebuild:
>
> ```
> visa_decision      corpus
> document_checklist search   <- www.uk.emb-japan.go.jp, a host the corpus does not hold at all
> application_route  search   <- mofa.go.jp/j_info/visit/visa/visaonline.html, a host it holds 200+ pages of
> fees               corpus
> processing_times   corpus
>                    -------  3 of 5
> ```
>
> That single number explains the outage result exactly: corpus-only cost Canada, Japan, Germany and
> the United States their document checklist, because the checklist is disproportionately the role
> live search was supplying.
>
> **Rebuilt at `--pages 5000`, with lost hosts now named — and the hit rate did not improve.**
>
> ```
> entries   1,977 -> 3,029      hosts 50 -> 68      beyond depth 1  7% -> 36%
> candidates this corridor saw: 837 corpus, 23 search   (the crawl was skipped entirely)
> corpus hit rate on role pages: 2 of 4      (it was 3 of 5)
> ```
>
> A 2.4× bigger page budget bought 1,052 new entries, 18 new mission hosts and five times the depth,
> and **bought nothing at all on the measure that matters.** The same two roles still came from live
> search — and `visaonline.html` sits on `mofa.go.jp`, of which the corpus now holds hundreds of
> pages. A crawl reaches pages by following links; search reaches them directly.
>
> **The structural reason, which no budget can fix:** `corridor_queries` carries the traveller's
> nationality and residence, and `corpus_queries` deliberately carries neither — entry 44 forbids it,
> because a corpus built for one nationality is not a corpus. So the pages that only a
> corridor-specific query surfaces can never be in the store, **by design**, and the document
> checklist is exactly such a page. That is why corpus-only runs lose checklists.
>
> Small sample — one country, two runs, and the second filled four roles where the first filled five,
> which is known problem 10. The direction agrees with entry 76's 30–67% across ten countries.
>
> **And the lost-host report, now built, did not explain London either.** `www.uk.emb-japan.go.jp` is
> absent from the rebuild *and* absent from the lost list — so it was never seeded at all this time,
> where a probe an hour earlier had search returning it. Search's seed set varies between runs
> (known problem 19), and a host that was never seeded cannot be reported as lost. The report catches
> hosts that **failed**; it cannot catch hosts that were never **asked for**.
>
> **And the two failure kinds have different causes and different fixes.** `visaonline.html` sits on a host
> the corpus covers heavily — that is a page the crawl never reached, and a bigger `--pages` is the
> fix. `www.uk.emb-japan.go.jp` is missing **entirely**: it answered a transient Akamai `403` during
> the build (the build reported "3 unreadable" and named nothing), so the corpus silently lacks the
> host and, being additive and rebuilt rarely, will lack it indefinitely. **A corpus build that loses
> a host to a transient failure never notices**, and nothing reports it. That is the more serious of
> the two and it is unfixed.

**Corrected arithmetic, 2026-08-26:** this entry first said "four pages per host", dividing 1,200 by
the 276 *seeds*. `host_budget` divides by seed **hosts** — `min(400, max(4, 1200 // 50))` = **24 pages
per host**. The number was wrong; the conclusion is not, and it never rested on it. `depth_is_exercised`
is the tool's own designed check and it **fails**: 7% of entries lie beyond depth 1 against a 10% bar,
so by the job's own definition this build "fetched its seeds and stopped". A corpus in that state is
little more than its search results plus one hop — **the store would not be inheriting search's
*recall*; it would be inheriting search's *shape*.**

**And this is the same defect recurring.** `DEFAULT_CORPUS_PAGES` was already raised once, from 200 to
1,200, after Canada's build put 1,032 of 1,071 entries at depth 1. Japan at 276 seeds has outgrown
1,200 the same way. The constant is not the fix; sizing it per country from the seed count is.

So the ordering instinct behind the question is right and the reason is not. **Size `--pages` from the
seed count before building 43 of them**, and read `depth_is_exercised` on the first before paying for
the rest. That is a fetch cost, not a search cost — the 1,792 searches are unchanged.

### And search recall is still unmeasured

Separately from all of the above, nothing has ever measured how often the answering page is returned by
search *at all*. Entry 70 found the one hard example — Belgium refusing an Indian passport and
resolving an American one on a page the losing run never saw — and `corridor_queries`' three English
templates with the nationality's name inside one are the obvious suspect. That is a live-corridor
problem rather than a corpus one, because `corpus_queries` deliberately carries no nationality. It
belongs to item 19, not to stage 3.

---

## 76. What a corpus can and cannot buy, measured — and the seven that no corpus will fix
**2026-08-25 · measured before spending stage 3's ~1,792 searches. Answers known problem 24's open count**

Before building 43 corpora, two questions were asked directly rather than assumed: *is search as good
as it can be*, and *will corpora make batch 1 largely work*. Both were measured. The answer to the
second is **no**, and the reason is structural rather than a matter of degree.

### Where the pages that actually filled roles came from

Known problem 24 said nothing counted how often the corpus was the only source and came up short.
Counted now, from `found_by` in the recall logs, over the **shortlist that was actually read**:

| | search | corpus |
| --- | --- | --- |
| United Arab Emirates | 14 | 7 |
| United Kingdom | 9–15 | 16–18 |
| Canada | 9–11 | 13–15 |
| United States | 4–5 | 7–14 |
| Germany | 4–7 | 11–14 |

**Search contributes between 30% and 67% of the pages a corridor reads, in the ten countries with the
best-built corpora.** The corpus is not a superset and never was (entry 47 said so); this is the first
number attached to it.

### And what corpus-only actually costs, observed on a real outage

While the search account was capped, all ten ran from the corpus alone:

```
resolved in full      singapore, united-arab-emirates
resolved, no checklist canada, japan, germany, united-states
handed over a tool     france, sweden, united-kingdom
REFUSED                netherlands   <- decision_not_found
```

So corpus-only is not equivalent to a normal run: **one of the ten refuses outright**, and four lose
their document checklist. A corpus keeps a country *working*; it does not keep it working *as well*.

### The seven that no corpus can fix, and why the reason is structural

The renderer arriving (entry 75) took the nine countries that refused every passport down to seven —
**Cyprus** and **India** now resolve, India with all six roles. The remaining seven fail like this:

| | why | would a corpus crawl fare differently? |
| --- | --- | --- |
| DK | every `um.dk` mission's `robots.txt` answers `520`, so nothing is requested | **no** — the corpus crawler obeys the same policy |
| RO | every `mae.ro` host's `robots.txt` answers `503` | **no** — same |
| LT | Cloudflare challenge fingerprints past our user agent | **no** — same client, same challenge |
| SK | challenges every page; the render budget runs out before the decision | **no** — a crawl meets the same wall, more of it |
| MX | `consulmex.sre.gob.mx` redirects to `validate.perfdrive.com`, and **rendering it navigates there too** and is refused as untrusted | **no** — same redirect |
| SA | `embassies.mofa.gov.sa` redirects to `saudiembassy.sa`, off the trusted domains | **no** — same |
| MA | pages come back with too little readable text even rendered | **no** — same pages |

> **A corpus is built by crawling the very pages that currently fail.** Every one of these seven fails
> at *retrieval*, before ranking or recall enter into it, so a crawl run offline meets the identical
> wall. Stage 3 cannot convert any of them.

### What stage 3 is therefore for, stated so it is not oversold

Three things, all real and none of them coverage:

1. **Latency** — 2.1×–5.2× (entry 55).
2. **Recall stability across passports** — entry 70's finding that a one-page-names-all destination
   only closes the nationality dimension when the page is reached by crawl or corpus, because
   `corridor_queries` puts the passport's name literally into one of three templates.
3. **Outage tolerance** — entry 74, now with the caveat above about what corpus-only costs.

**Coverage is not on that list.** 34 of 41 already answer at least one passport with no corpus at all.

### Is search as good as it can be? No, and the gaps are recall rather than reliability

Entry 74 fixed **reliability** — pacing, `402` classification, outage tolerance. Nothing has touched
**recall**, and what is known about it is unflattering:

- `corridor_queries` is **three fixed English templates per trusted domain**, and one of them carries
  the nationality's name literally. Entry 70 measured the consequence: Belgium refused an Indian
  passport and resolved an American one on the *same page*, which was never a candidate in the losing
  run.
- Scoring is English-only (known problem 13), so a destination publishing in its own language scores
  near zero.
- The five-domain cap is calibrated against corridors run, not derived (known problem 6).
- **Nobody has ever measured search recall directly** — how often the answering page was returned by
  search at all, as opposed to ranked out. The recall log now holds enough to compute it.

None of that blocks stage 3. It does mean "search is fixed" is a statement about reliability only, and
the next real coverage win is more likely to be here than in corpora.

---

## 75. The challenge is answered: Cyprus resolves, Greece still refuses, and the wait had to be a poll
**2026-08-25 · implemented and confirmed live. Closes TODO item 5's challenge half; implements entries 41 and 73**

Entry 41 decided in August that a challenge may be answered by the renderer. Entry 73 measured what
that was worth and left it unbuilt. This builds it, and the shape of the fix was decided by
measurement rather than by the design.

### What was built

- **`challenged` is a `FailureOutcome`**, beside `blocked` and `disallowed`. It sits outside
  `blocked_urls()` and `persistent_refusals()`, so it can never resolve a corridor, can never reach
  `inaccessible_domains`, and can never be handed to a traveller as a page an authority withheld.
  Nobody asked the authority anything.
- **`is_challenge` reads headers *and* body**, because Cloudflare sets `cf-mitigated` and **Azure
  declares it only in the body**. It fires on `401`/`403`/`503` alone — the markers on a `200` would
  throw away a page that merely embeds Cloudflare's script.
- **Both paths answer one**: retrieval renders the challenged URL and, if the page behind it is
  readable, caches and returns it as ordinary evidence; the crawl does the same and shares the render
  budget, so a site that challenges every page cannot consume a whole crawl.
- **`render_mode` is now `on_demand`**, which is the committed policy change this needed. Without it
  nothing above ever runs.

### The wait had to become a poll, and three numbers are why

The first live attempt still reported *"that challenge could not be answered here"* on every Cyprus
page, and the standalone probe had passed. The difference was the settle: 8,000ms in the probe,
2,500ms in production. Raising it did not fix it either:

```
settle  2,500ms -> 12,724 chars, still the interstitial
settle  9,000ms -> render returns None: content() read while the challenge was mid-redirect
settle 15,000ms -> 70,976 chars, the real page
```

**So the variable is not how long to wait but what to wait for.** A challenge replaces itself by
navigating, and a fixed wait races that navigation — the 9,000ms case is worse than the 2,500ms one,
which no amount of tuning a constant would have revealed. `_wait_out_challenge` polls once a second
until the markers are gone or a 20s deadline passes, and treats the navigation errors thrown while it
happens as the signal they are rather than as failures.

Returning whatever the page last held is deliberate: the caller re-checks it, and an unanswered
challenge is reported as unanswered. *"We could not prove we are a browser"* stays a statement about
us.

### Live results

**Cyprus resolves.** A country that refused every passport this morning now answers on
`www.gov.cy/mfa/en/documents/countries-whose-nationals-are-required-to-hold-a-visa-to-enter-the-republic-of-cyprus`
— the all-nationality list, which is exactly the right page. Its other two domains are unchanged and
still honestly reported: `www.mip.gov.cy`'s certificate expired on 2026-08-02, and `police.gov.cy`
publishes a `robots.txt` that excludes this client, which is obeyed.

**Slovakia is better and not fixed.** `mzv.sk` challenges *every* page, so the render budget is spent
before the decision page is reached: a `document_checklist` now comes back where nothing did before,
and `visa_decision` is still unresolved. The budget is doing its job — one host may not consume a
crawl — and raising it is a latency decision nobody has taken. Reported honestly in the meantime.

**Greece still refuses, and that is the test that mattered.** `www.mfa.gr` answers an Akamai
"Access Denied" with no script to run, `is_challenge` does not match it, the renderer is never pointed
at it, and it appears under *"refused automated retrieval"* exactly as before. The markers are narrow
on purpose: widening them until a refusal matched would turn entry 18 into its opposite.

### What this does not change

Lithuania stays refused. Its Cloudflare challenge fingerprints past the user agent, and the only way
through is to disguise the client, which entry 35 forbids in terms and which is not attempted. It is
recorded as `challenged` — neither a refusal nor a pass — which is the honest third answer.

---

## 74. Search: a spend cap is not a throttle, a burst is not a pace, and a corpus may answer alone
**2026-08-25 · three fixes, tested offline and confirmed live against a genuinely capped account**

Three defects in how this project uses search, all recorded under TODO *Smaller things* and none
fixed until a real outage made the third one impossible to keep deferring.

### A `402` was reported as one thing, and it is two

Brave answers `402` both for a spend cap and for queries sent too fast, and *"payment required"*
reads as *out of credit* either way. That cost an earlier session an hour of believing an account was
empty while single queries answered fine.

**Only the body separates them**, and it does so with numbers rather than prose:
`error.meta.current_spend` against `error.meta.usage_limit`. So `SearchQuotaExhausted` and
`SearchThrottled` are now distinct types under `SearchError`, decided by `classify_payment_required`
from those figures — never by matching words in a message, which is entry 36's rule.

**A `402` with no figures is treated as a throttle**, deliberately the safer way round: a throttle
retried is a delay, an exhausted account retried is noise aimed at somebody else's service.

### The concurrency outran the pace, because the pace lived nowhere

`search_all` runs four queries at once and `BraveSearchProvider` paced nothing, so a capped plan met
four simultaneous requests and refused three. The limiter is now **on the provider** — one lock, one
monotonic clock, `DEFAULT_QUERY_INTERVAL_SECONDS = 1.3` — so it holds however many callers ask at
once. Per-call pacing would not have: four calls each waiting their own interval still leave together.

`sleep` and `now` are injectable, so the test asserts the pacing without spending 2.6 seconds.

### A country with 2,450 stored pages could not answer while search was down

The one that mattered. `_resolve` searched **before** reading the corpus and `search_all` raises if
any query fails, so Canada — 1.7 MB of corpus, resolving in 12s off a file — died with
`Search is unavailable: HTTP 402`. Every one of the ten corpus countries did. Entry 48 kept search
for **recall**; nothing ever decided it should be the single point of failure for a fully built
country, and entries 44–57 made it one by attrition.

**A search failure now falls back to the corpus, and the fallback is loud, bounded and not kept:**

- **Only where a corpus exists.** With nothing stored, search was the only recall there was, and
  falling through would turn *we could not look* into *there is nothing to find* — the statement
  entry 18 forbids outright. The refusal stands, and a test pins it.
- **Recorded as a typed field**, `ResolvedCorridor.ran_without_search`, not as a sentence. What acts
  on it is the corridor store.
- **Never stored.** `AutomaticDestinationService` skips `store.store` for such a corridor. The store
  keeps what it is given for three weeks, and serving a narrower resolution long after search came
  back, with nobody told, is entry 44's rejected shape arriving by another route.
- **Said plainly**, naming the real cause with its numbers: *"search was unavailable (the search
  account has spent 25.01 against its 25.0 limit …), so this corridor was answered from Canada's
  stored page corpus alone. Nothing was substituted … and this result is not kept for reuse."*

**And one note had to be silenced to keep the rest true.** With search down, *"search returned
nothing on an approved domain"* is false — nothing was returned because nothing was asked — and two
notes describing one event as two failures is how a reader concludes the corpus came up empty.

### Confirmed live, on the outage itself

With the account genuinely capped, all ten corpus countries were run. **None died.** Canada resolved
in 31.7s from 2,450 stored pages; Singapore filled five roles; Japan, Germany, the United States and
the United Arab Emirates confirmed the decision; France, Sweden, the Netherlands and the United
Kingdom handed over their questionnaires. Before this change every one of them raised.

### What this does and does not buy

It does **not** make search optional. A country with no corpus still needs it, which is 43 of the 53,
and the corpus half of a built country is thinner than it looks — known problem 24 records Japan's
holding 1 of its 6 role pages. What it buys is that **building a corpus now insulates that country
from a search outage**, which it did not before, and that is a second reason for stage 3 beyond
latency and beyond entry 70's recall-stability finding.

TODO item 19 — taking search out of the request path *by design* rather than as a fallback — is
untouched and still wants the nationality dimension measured first.

---

## 73. Cyprus and Slovakia were never refusing us — entry 70 read a challenge as a refusal
**2026-08-25 · measured. Corrects entry 70 and known problem 11; TODO item 5 is now worth two countries**

Entry 70, written earlier the same day, said `www.gov.cy` answers *"a plain `403` … with **no
`cf-mitigated` header** — a real refusal, not France's challenge, so entry 41 does not apply"*. **That
is wrong, and it was wrong because only the headers were read.**

### What the four `403` hosts actually say

Fetched with the project's own user agent, headers **and body**:

| | what came back | what it is |
| --- | --- | --- |
| `www.gov.cy` | `403`, body: `<meta name="description" content="Azure WAF JS Challenge">` | **challenge** |
| `www.mzv.sk` | `403`, `cf-mitigated: challenge`, *"Just a moment…"* — and `robots.txt` answers **`200`**, disallowing only `/*p_auth` | **challenge**, with permission stated |
| `urm.lt` | `403`, `cf-mitigated: challenge`, *"Just a moment…"* | **challenge** |
| `www.mfa.gr` | `403`, Akamai, *"You don't have permission to access…"*, no JS anywhere | **refusal** |

**Azure does not set `cf-mitigated`; it declares the challenge in the body.** So a header-only test
finds Cloudflare and misses Azure entirely, and entry 41's own line — *"the line is 'did the authority
state anything', not 'which status came back'"* — is exactly the line a header-only test cannot draw.
Cyprus stated nothing. It asked whether we could run JavaScript.

Slovakia is the sharpest case in the whole registry: its `robots.txt` **answers, and permits us**. The
authority's stated crawl policy is yes, and a WAF in front of it is testing for a browser.

### Whether an honest client can answer them, measured

The project's own `PlaywrightPageRenderer`, under the project's own user agent
(`VisaResearchAgent/0.1 (personal visa research; contact repository owner)`) — no spoofing, nothing
disguised:

```
https://www.gov.cy/mfa/   -> PASSED   70,977 chars   (?afd_azwaf_tok=… appended by the WAF)
https://www.mzv.sk/en/    -> PASSED  377,224 chars
https://www.urm.lt/en/    -> CHALLENGE STILL  (also at a 20s settle)
https://www.mfa.gr/en/    -> Access Denied, 289 chars
```

So **two of the four countries that lose their entire trusted set to a "403" are answerable by an
honest client**, and one is not answerable at all.

**Lithuania is a third outcome and it must be named as one.** Cloudflare's managed challenge is
fingerprinting past the user agent — headless Chromium, most likely. Getting through it would mean
disguising the client, which is the deception entry 35 forbids in terms, and it is not being
attempted. *"Challenged, and the challenge could not be answered honestly"* is neither a refusal nor a
pass, and reporting it as either would be false.

**Greece stays refused, and that is the rule working.** An Akamai `Access Denied` with no JS to run is
an authority saying no. Entry 41 does not touch it and neither does this.

### What follows, and what is deliberately not done yet

The decision is already made — entry 41 decided a challenge may be answered by the renderer, and TODO
item 5 has carried it as unimplemented since 2026-08-19. What this entry adds is a **price**: it is
worth Cyprus and Slovakia outright, on top of France, and it needs a challenge test that reads the
**body** as well as the headers.

**Not implemented in this session**, and the reason is not doubt about the decision. It changes
`render_mode`, which is committed reviewable policy, and it cannot be verified end to end right now
because the search account hit its cap mid-session. Shipping a retrieval change verified only by unit
tests is how this project has previously convinced itself of things that were not true. The
measurement above is the part that was missing; the implementation is item 5.

**And the interface still says the wrong thing.** A challenged authority is described to travellers as
one that *"does not permit automated retrieval"*. That was untrue of France when entry 41 said so in
August, and it is now untrue of Cyprus, Slovakia and Lithuania as well.

---

## 72. A post named in the host was no post at all — and the fix that looked obvious was wrong twice
**2026-08-25 · measured, disproved twice, then implemented. Narrows known problem 9; TODO item 1**

Entry 70 reported that for an Indian passport holder resident in Great Britain, Australia, Brazil and
Slovenia all answered from their **New Delhi** post. **Two-thirds of that was wrong**, and running it
rather than re-reading it is what showed the difference:

- **Brazil was right.** Its checklist, route, fees and processing times all came from
  `consulado-edimburgo` — the Edinburgh consulate, which serves a UK resident. Only the *decision*
  came from New Delhi, and a visa decision is the same at every consulate.
- **Australia** was not a ranking failure either: `uk.embassy.gov.au` *was* shortlisted and fetched,
  and answered `HTTP 500`.
- **Slovenia is real.** Its `general_entry` is `gov.si/assets/predstavnistva/new-delhi/…`, the common
  information sheet *for applicants in India*, handed to someone in London.

The mechanism, measured with `mission_affinity` rather than inferred:

```
india.embassy.gov.au/ndli/...            -> None      (should be "other")
uk.embassy.gov.au/lhlh/...               -> own
gov.br/.../embaixada-nova-delhi/...      -> other     path names the post
gov.si/assets/predstavnistva/new-delhi/  -> None      bare segment, no marker prefix
```

Two gaps. **A post named in a host label** was never concluded as "other" — only "own" was ever read
from a host — so `india.embassy.gov.au` competed as though it were a neutral ministry page. **A post
named as a bare path segment** is missed too, because `mission_in_path` requires a `<marker>-<post>`
shape like `consulado-edimburgo`.

### The obvious fix, and the two measurements that killed it

Treat any token claimed as a mission label by a country that is not the residence as another post.
Over the 132 recorded corridors:

```
58,209 candidates flip to "other" — and 165 pages that had FILLED A ROLE would be penalised
```

Among the casualties: Estonia's *"List of supporting documents in the United Kingdom"*,
`gov.pl/web/unitedkingdom`, `dirco.gov.za/uk`, `conslondra.esteri.it`. The fix would have broken
precisely the corridors that were already correct.

**Why**, and it is not what it looked like. The blamed tokens were `cz`, `be`, `hr`, `ch`, `in`, `id`,
`lv`, `eg` — **every one the destination's own country code**, read out of its own hostname.
`mzv.gov.cz` is not another post; it is Czechia. The rule was treating the destination as a foreign
mission.

Exempting the destination *and* skipping the registrable domain gives:

```
host subdomain labels only:  703 flip; ONE had filled a role — india.embassy.gov.au, the page
                                       this exists to demote
host labels and path too:  4,178 flip; three had filled a role
```

**The host-only rule is what shipped.** The path variant is more aggressive, two of its three
role-page changes are corrections rather than harm, and it is the only thing that would catch
Slovenia — but "would have been right twice out of three" is not a measurement, and the bare-segment
gap is left open and written down rather than guessed at.

### Which roles a post governs

`fees` and `processing_times` join `document_checklist` and `application_route` in
`POST_SPECIFIC_ROLES`. Measured cause: `brazil/US/US` took the **Edinburgh** fee page for a traveller
in the United States. A fee is quoted in the post's currency; a processing time is that post's queue.

**`visa_decision` is deliberately left out**, and this is the load-bearing part. Whether a passport
needs a visa is set by the destination's law and is identical at every consulate, so demoting the page
that states it would refuse corridors to buy nothing — and it is the one role whose absence refuses a
corridor at all. `general_entry` is out for the same reason: Schengen entry conditions do not vary by
where someone lodges. So the New Delhi decision pages entry 70 complained about **keep their places on
purpose**; what changes is that they stop competing for the four roles where the post is the answer.

### Verified live, on a regression set chosen to include what the rejected fix would have broken

Seven corridors, 2026-08-25, after the search cap was raised:

| | post-specific roles now come from | |
| --- | --- | --- |
| `slovenia/IN/GB` | `gov.si/en/representations/**embassy-london**` | **fixed** — was New Delhi, and the corridor went from four roles to six |
| `brazil/IN/GB` | `consulado-**edimburgo**`, all four | unchanged, and it was already right |
| `estonia/IN/GB` | *"List of supporting documents in the **United Kingdom**"* | unchanged — the page the rejected fix would have penalised |
| `poland/IN/GB` | `gov.pl/web/**unitedkingdom**` | unchanged, likewise |
| `czechia/IN/GB` | `mzv.gov.cz`, with `mzv.gov.cz/**london**` for the route | unchanged — the host the rejected fix read as a foreign post |
| `australia/IN/GB` | — | no post-specific role filled either way |
| `brazil/US/US` | `consulado-**edimburgo**` for `fees` | **not fixed** |

**Six of seven, and the seventh is worth stating plainly.** Brazil still quotes an Edinburgh fee to a
traveller in the United States. The page is now demoted rather than neutral, but the mission
adjustment is a penalty and not a veto, and where nothing better is among the candidates the
adjudicator still picks the best available. That is a recall problem, not a scoring one, and it is
the residual this entry leaves open.

---

## 71. Two defects a sweep found that no corridor had: status 990, and a chain Morocco does not send
**2026-08-25 · both fixed, one with a regression test. Found by TODO item 30, stage 2**

Running 41 countries instead of five turned up two failures that twelve years of five-country
corridors could not have, and they are opposite kinds of thing.

### `mofa.gov.sa` answered `HTTP 990`, and the corridor died rather than reported it

`SourceFailure.http_status` was `Field(ge=100, le=599)`. `www.sta.gov.sa` answered **990**, so
building the failure raised a Pydantic `ValidationError` inside `_serve_stale`, which escaped
`_fetch_source`'s `except httpx.HTTPError`, propagated out through `asyncio.gather`, and ended both
Saudi Arabia corridors in a traceback with no output at all.

**The bound was describing the standard where the field describes the wire.** A status line is three
digits (RFC 9112), so anything from `100` to `999` arrives parsed and has to be *recordable* —
refusing to record one converts a strange server into a crashed corridor, which is the opposite of
this project's posture. The bound is now `100`–`999`, named once as `MINIMUM_HTTP_STATUS` /
`MAXIMUM_HTTP_STATUS` so `SourceFailure` and `CachedSource` cannot drift apart.

**Widening it cannot widen what a refusal may claim**, which is the property that had to survive.
Everything acting on a status tests membership of `PERSISTENT_REFUSAL_STATUS_CODES` or
`BLOCKING_STATUS_CODES`; `990` is in neither, so it reports as `unreachable` and can never resolve a
corridor or be handed to a traveller as an authority's refusal. `tests/test_live_sources.py` pins
both halves — the status is recorded, and it is in neither set.

Saudi Arabia still refuses, and now says why: *"www.sta.gov.sa could not be read because it answered
HTTP 990"*. That is the bar — a named reason true of what was seen — where before there was a stack
trace.

### Morocco sends a leaf and no intermediate, which is exactly what `tls_intermediates/` is for

Every Morocco corridor failed with *"certificate verify failed: unable to get local issuer
certificate"* on `diplomatie.ma`, `in.diplomatie.ma` and `uk.diplomatie.ma`. The site is genuine; it
serves only its own certificate and omits **Sectigo Public Server Authentication CA DV R36**, which
browsers fetch automatically and Python does not.

Fetched from the leaf's own AIA URL and checked by the rule the directory's README already sets:

```
openssl verify -CAfile $(python -c 'import certifi;print(certifi.where())') r36.pem
r36.pem: OK          # issued by Sectigo Public Server Authentication Root R46, already trusted
```

So it is added, and **verification stays fully on** — entry 12's whole point. `www.diplomatie.ma` now
answers `200` where it answered a TLS error.

**Morocco still refuses**, and that is the honest outcome rather than a disappointment: the pages come
back with too little readable text to trust, because they are client-rendered and `render_mode` is
`never`. The diagnosis moved from a defect on our side to a property of the site, which is the whole
value of fixing it. Morocco is a candidate for the `on_demand` renderer, and that is a policy change
to argue separately, not to slip in here.

### What is general about the two

Both were invisible at five destinations and unmissable at forty-one, and neither is a scoring or
recall problem — the two things stage 2 was designed to look for. That is an argument for the breadth
being the point, and against the reflex to widen a batch only after the current one is perfect: some
defects are only reachable by volume. It does not overturn entry 68's staging, which is about not
*trusting* untested rows; it qualifies what a stage-2 sweep is worth beyond its own countries.

---

## 70. Stage 2 of batch 1: all 41 run, and both things entry 69 expected were wrong
**2026-08-25 · measured on 103 live corridors across all 41 never-run destinations. TODO item 30, stage 2**

Entry 69 said stage 2 must classify each destination by **how its authority publishes**, named three
shapes, and told this stage to measure the missing-demonym defect before anyone wrote 184 demonym
lists. All 41 destinations have now been run — two or three passports each, 103 corridors — and both
of entry 69's expectations came out backwards.

### The result

| | |
| --- | --- |
| corridors | **103**, over all 41 destinations |
| resolved outright | **54** |
| decision handed over as a blocked page (entries 27, 32, 57) | **4** |
| decision handed over as a questionnaire (entries 59, 60) | **4** |
| refused, nothing stated the visa decision | **41** |
| the run raised, or the model call failed | **0** |
| document checklist present | **45 of 103** |

**32 of 41 destinations answered at least one passport. The other nine refused every passport, each
for a reason verified against what was actually seen**, which is the bar TODO item 30 sets:

| | why every passport refuses |
| --- | --- |
| CY | `www.gov.cy` answers `403`, `www.police.gov.cy` `301`s into it, `www.mip.gov.cy`'s certificate **expired 2026-08-02** |
| DK | every `um.dk` mission's `robots.txt` answers `520`, so nothing was requested (entry 36) |
| IN | its own domains carry the checklist, route and fees, and no page states **who needs a visa** |
| LT | `urm.lt` and `keliauk.urm.lt` — its whole trusted set — answer `403` |
| MA | certificate chain fixed this session (entry 71); the pages are client-rendered and `render_mode: never` |
| MX | `consulmex.sre.gob.mx` redirects to `validate.perfdrive.com`, off the trusted domains |
| RO | every `mae.ro` host's `robots.txt` answers `503` — policy unreadable, so not requested |
| SA | `www.sta.gov.sa` answers **`990`**, `moi.gov.sa` times out, `embassies.mofa.gov.sa` redirects to `saudiembassy.sa` |
| SK | `mzv.sk` — its only trusted domain — answers `403` |

Do not read the 54/103 against entry 58's bars. That sample was five high-volume destinations
replicated four times; this is every country nobody had ever run, and the two measure different
things.

### The shape entry 69's table does not have: **per post**

Entry 69 listed one-page-names-all, page-per-nationality, and questionnaire. The corridors were run
with **`--from` deliberately different from `--nationality`** (`IN/GB` beside `US/US`) so the two axes
could be told apart, and a fourth shape is plainly there: the answer comes from the page of the
**diplomatic post that serves the applicant**, chosen by *where they apply from*, and that page then
names many nationalities.

```
south-africa  IN/GB -> dirco.gov.za/uk              US/US -> dirco.gov.za/washingtondc
poland        IN/GB -> gov.pl/web/unitedkingdom     US/US -> gov.pl/web/usa-en
estonia       IN/GB -> "List of supporting documents in the United Kingdom.PDF"
italy         IN/GB -> conslondra.esteri.it         hungary IN/GB -> london.mfa.gov.hu
```

That closes the nationality dimension and **opens the residence one**, which is the same size. Entry
69 reasoned about `passport_nationality` alone because the defect it found lives there; the
authorities largely index on the other axis. Known problem 9 knew this from the other end — "for a
consular checklist the **post** governs" — without connecting it to what a batch has to test.

**And three destinations answered the *decision* from the post serving the passport rather than the
residence** — Australia from `india.embassy.gov.au`, Brazil from `embaixada-nova-delhi`, Slovenia from
`embassy-new-delhi`, all for an Indian passport holder resident in Great Britain.

> **Corrected by entry 72, which measured it rather than re-reading it.** Brazil's checklist, route,
> fees and processing times all came from `consulado-edimburgo` — the *right* post — so Brazil is not
> a wrong-post case at all, and Australia's London post was fetched and answered `HTTP 500`. What is
> real is Slovenia's `general_entry`, and a Brazilian **fee** page from Edinburgh served to a
> traveller in the United States. Entry 72 has the mechanism and the fix.

**A page per nationality — entry 69's "the real risk" — was not the shape of a single one of the 41.**

### The nationality risk that is real is **search recall**

Belgium refused an Indian passport applying from India and resolved an American one **on the same
page** — and the page was not ranked out, it was **never a candidate**: 0 hits in 137 for that run,
found by *search* in the other. Moving the same Indian passport's residence to Great Britain resolved
it, all six roles. Bulgaria is the mirror image, its all-nationality PDF appearing for `IN` and not
for `US`.

`corridor_queries` builds three templates per trusted domain and puts the nationality's **name**
literally into one of them, so on a destination whose answer sits on one page, whether that page is
found can turn on the passport in the query. Czechia is the control: its
`list_of_states_whose_citizens_are_exempt` page was reached by **crawl**, scored the same, and
answered all three passports identically.

> **A one-page-names-all destination closes the nationality dimension only when the page is reached by
> crawl or corpus. Where it depends on search, nationality still decides.**

That is a reason to build corpora which entry 68 did not have: stage 3 was costed purely as latency
(2.1×–5.2×), and on this evidence it also buys **recall stability across passports**. It does not
reorder the stages — a corpus for a country that refuses is still worth nothing — but it changes what
stage 3 is for.

### Known problem 27, measured twice: the demonym bonus buys 0.18 places, all of them noise

Over the **122 recorded corridors** on disk, counting candidates that `_describes_country` matches on
a **demonym and not on the country's name**:

```
76 candidates matched by demonym alone
22 of them took a shortlist place        ->  0.18 places per corridor
 0 of the 22 filled a role in any run
```

They are approved-travel-insurer lists (Switzerland, Hungary, Denmark), a Work Holiday notice for
Indian nationals, an `mfa.gr` press release about embassy staffing in New Delhi, `gov.uk/ads-visa`,
and several `indianvisaonline.gov.in` pages in a corridor whose destination *is* India. **Not one is
the page any corridor answered from.** The same measurement at 59 corridors gave 0.20 and 12 of 12;
it did not move when the sample doubled.

So the bonus's demonym half, where it fires, is a fetch spent on noise — entry 62's conclusion about
the whole bonus, reached from the other side. **Writing 184 demonym lists would buy ~0.2 wasted
fetches per corridor and, on this evidence, no answers.** Not done, and it should not be done on a
recall argument.

**Method, and its limit.** `_describes_country` reads a link's URL path and its text. The URL half is
exact — the recall log stores the URL the scorer saw. The text half is approximate, because the log
stores a page **title** where the scorer saw link text and a heading (entry 62's fidelity note), and
no corpus exists for these countries to join against. So 22 is a **lower bound** on matches, which
cuts the right way: more matches of this quality is a worse case for demonyms, not a better one.

### Estonia is fixed; Romania's diagnosis changed and the row was still right

Estonia refused exactly as entry 67 warned — the only readable page on its trusted set was
`learn.e-resident.gov.ee`, the e-Residency help centre. Reviewed rows were added for both watched
countries by entry 67's own method, the exact-statement lookup from the domain plus `P17`:

| | domain | Wikidata | |
| --- | --- | --- | --- |
| EE | `vm.ee` | Q6867006 | Ministry of Foreign Affairs (Estonia), `P856 = http://www.vm.ee`, `P17 = Q191` |
| RO | `mae.ro` | Q15628977 | Ministry of Foreign Affairs of Romania, `P856 = http://www.mae.ro`, `P17 = Q218` |

**Estonia now resolves all three passports on `vm.ee`, all six roles for `IN/GB`.** Romania still
refuses — but the row changed the *diagnosis*, which is what it was for: `mae.ro` and its missions are
now reached, and every one of their `robots.txt` answers `503`, so the reason moved from "the trusted
set cannot hold the answer" to "the authority's crawl policy could not be read". Both are true of what
was seen; only the second is about Romania.

**Note for whoever repeats the lookup**: those two `P856` values are `http://www.vm.ee` and
`http://www.mae.ro`, with no trailing slash. A query that tries only `https://<domain>/` returns
nothing and the domain reads as unconfirmable when it is not — which is how the batch-1 sweep
mislaid both.

### Blocks, and one that finally qualified

Across the run set 80 pages are `blocked` and 102 `disallowed`, against 0 and 23 before this stage.

> **This entry originally called Cyprus's `403` a real refusal, on the strength of a missing
> `cf-mitigated` header. That is wrong — see entry 73.** Azure declares its challenge in the *body*,
> so a header-only test finds Cloudflare and misses Azure entirely. `www.gov.cy` and `www.mzv.sk` are
> **challenges**, both answerable by our own renderer under our own user agent; `urm.lt` is a
> challenge our renderer cannot honestly answer; only Greece's `www.mfa.gr` is a real refusal.

**Malta and Thailand produced the first `resolved_decision_blocked` corridors ever recorded** — four
of them. Entries 27, 32 and 57 have been live since August and had never fired on a real corridor:
the block is judged a credible `visa_decision` candidate, the page is named with its URL, nothing is
read from it, and the decision stays unknown. Cyprus, by contrast, refuses outright and correctly does
**not** claim it, because entry 32 requires a source to have been read and nothing was.

### The interruption, and that the pipeline handled it correctly

The OpenAI account ran out of credit part-way through and 18 corridors refused with
`role adjudication failed on all 2 attempts`. Entry 31 forbids falling back to the heuristic and it
did not. Every one of those corridors was re-run after the account was topped up, so the run set now
records **0** model failures and **0** raised runs. What is worth fixing is that nothing noticed at the
time: 16 corridors' search quota went on runs that could not answer. That is a sweep-harness job, not
the resolver's — TODO, *Smaller things*.

---

## 69. Batch 1 bounds destinations, never nationalities — and 184 of 198 passports have no demonym
**2026-08-25 · direction, set by the project owner, with a measured consequence**

Entry 68 set the three stages. This fixes what they are measured *over*, because the two dimensions are
not treated alike:

> **Batch 1 bounds the destination list. It does not bound nationality. Whatever passport a traveller
> holds, a batch-1 destination must answer them.**

A destination is not done because it answered an Indian and a Chinese passport. 53 destinations × 198
nationalities is 10,494 corridors, so exhaustive testing is out — which makes it a question about
*mechanism* rather than sample size, and there is a defect in the mechanism.

### What actually varies with nationality, measured

`Country.text_tokens` is `name + synonyms + demonyms`, and it feeds `_describes_country`, which awards
the **nationality bonus** in `score_link`. **184 of 198 countries have no demonyms** — only the
fourteen hand-curated ones do, and `countries.yaml` says so plainly for anyone who reads that far.

The consequence, probed rather than reasoned about:

```
page: "Visa requirements for Indian nationals"  /visa-for-indian-nationals
      IN  ->  nationality bonus fires
page: "Visa requirements for Kenyan nationals"  /visa-for-kenyan-nationals
      KE  ->  does not fire
page: "Entry requirements: Kenya"               /entry-requirements-kenya
      KE  ->  fires
```

Matching is anchored to word and segment boundaries, so `kenya` does not match `kenyan`. **Stemming
would not fix it either**: the Philippines' demonym is *Filipino*, Poland's is *Polish*, the
Netherlands' is *Dutch*. These are lexicon entries, not morphology.

**Bounded honestly: this is a scoring aid, not a gate.** `countries.yaml` is right that a country
without demonyms is still researchable, and the model decides the last step. But entry 40 established
that the scorer is a **recall gate** — a page ranked out is unrecoverable — so a bonus that does not
fire can cost the answering page its shortlist place, which is how a corridor fails. Entry 62 measured
what *having* the bonus is worth at 0.27 shortlist places; **what lacking it costs has never been
measured**, and that is now the question stage 2 has to answer.

### How stage 2 tests a dimension it cannot enumerate

Not by sampling harder. **Classify each destination by how its authority publishes**, because that
decides whether nationality is a recall problem at all:

| shape | example | nationality risk |
| --- | --- | --- |
| **One page naming every nationality** | a Schengen annex table, Germany's country list | **None.** One page answers all 198; find it once and the dimension is closed |
| **A page per nationality** | Canada's per-nationality pages | **The real risk.** Recall must find the right one of ~200, and this is where a missing demonym bites |
| **A questionnaire** | `gov.uk/check-uk-visa` | **None.** The tool is handed over whole (entries 59–60), and it serves every passport by construction |

So stage 2 records the shape per destination, and tests nationality **only where the shape makes it a
risk** — a handful of deliberately awkward passports against the per-nationality destinations, chosen
for demonyms that do not resemble the country name.

**Do not fix this by hand-writing 184 demonym lists before measuring.** That is the manual curation the
production goal exists to remove, and entry 62 is a standing reminder that four plausible scorer fixes
were measured and all four were wrong.

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

**Amended 2026-08-28: stage 3 has no test, and that is now a known gap.** A country counts as
*fast* because a corpus file exists, not because anything measured whether that corpus can answer
a corridor. The one measurement that exists — 47 of 47 answerable roles held, against
`oracle/selection_oracle.yaml` — covers a single traveller and is blind to the dimension entry 88
found failing. [TODO.md](TODO.md) item 37 is the gate that should decide stage 3 instead.
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
