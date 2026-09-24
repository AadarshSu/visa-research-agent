# Item 70, step 3 — the first link that broke, per corridor

Working notes, filled as runs land. Round 1 unless marked.

| corridor | round 1 | first link that broke | evidence |
| --- | --- | --- | --- |
| croatia/BD/AE | refused | **not in the store** (on Croatia's domains) | No HR page states the decision for Bangladesh. The overview says "the visa regime … is part of the EU acquis" and lists nothing; the New Delhi page says "visa applications from nationals of Bangladesh … must present himself" — procedure, not a decision. The answer is the EU list: stated only off the trusted domains (item 2). The refusal is correct on its packet. |
| malta/BD/AE, malta/BD/SA | refused | **not in the store — rejected by the build** | identita.gov.mt's requirements page links "List of Countries" → `/wp-content/uploads/2023/10/List-of-Third-Countries-whose-nationals-must-be-in-possession-of-a-visa…pdf`. `is_archived` vetoes any bare year 1990–2024 in a path, so the link is dropped by the build's `_reject` and by the corridor's `reject` (search results too). The model said so: "refers to attached country lists, but the extract does not show Bangladesh". |
| belgium/BD/AE | refused | **in the store, never shown** | The EN list page only links the PDF (`/sites/default/files/2024-12/List of third countries that are required to hold a visa.pdf`, 1,188 chars, BANGLADESH on it). As a depth-2 corpus entry its link scores +6 −20 (`depth2`) = −14 → not pooled; not admitted on text (a list of names has no role vocabulary). |
| belgium/BD/SA | **required / verified** | — | Search returned the same PDF at depth 0 (+6), the selector took it, the adjudicator credited "expressly includes BANGLADESH". Same store as BD/AE; the difference is which search query returned it. |
| italy/BD/AE | **required / partial** | — | Credited esteri.it's "paesi soggetti visto" page. |
| poland/BD/AE | resolved, plan **null** | **credited, then held back by the plan (rule 8f bound)** | Adjudicator credited the UAE mission's visa-free list (Bangladesh absent). The plan: "the supplied sources do not state the general rule that would make the omission decisive". Correct under 8f. |
| slovenia/BD/AE | refused | **shown, not picked** | The New Delhi embassy page — "Citizens of Bangladesh, Bhutan, Nepal and Sri Lanka Visa is required." — was pooled (14.0, one of 61, none withheld) and not selected. The adjudicator correctly refused the Cleveland PDF, which is the prior-consultation list, not a visa list. |
| india/BD/SA | **required** | — | |
| egypt/BD/SA | **required** | — | |
| mexico/IN/GB | refused | **read, but the list is an image** | inm.gob.mx "Países y regiones que requieren visa" says "nationals of the following countries … must obtain a visa" and the list is `wp-content/uploads/2024/03/PAISES-VISA2.jpg` — no country name in the text. The London consulate's visa pages redirect to `validate.perfdrive.com` (a bot wall off the trusted domains) — the set-aside class. Refusal correct. |
| saudi-arabia/IN/GB | refused | **picked, not readable** (set-aside class) | 2 pages read; `mofa.gov.sa` e-service pages "too little readable text", `sta.gov.sa` HTTP 990. SA's text index holds 113 pages and none names India with a visa. |
| united-arab-emirates/IN/GB | research resolved, **plan refused** | **credited, then the plan call failed validation** | The adjudicator credited mofa.gov.ae's exemptions table — "Republic of India … Visa Required" — and the plan's draft broke source/schema validation (`LLMExtractionError`). Run 1's cause was not captured; the runner keeps drafts and validation errors from round 2. Note the credited row is the general rule, and the oracle's answer is the residence-conditioned visa on arrival — see round 2. |
| netherlands/PH/PH | refused | **in the store, removed by the corridor's audience veto** | The Dutch "Do I need a visa for the Netherlands?" questionnaire (`/visa-the-netherlands/visa-required`, readable, depth 1) is recorded with the link text "Do I need a visa and/or a residence permit for the Netherlands?", and `wrong_audience` vetoes "residence permit". Not a candidate at all; only its `.es`/`.fr` copies were, withheld. In `netherlands/IN/GB` (2026-09-24) search returned it under its page title and it was named as the decision tool. |

## Rounds 2 and 3

- **Five round-2 runs measured a Personas outage, not the research.** Between 14:02:46 and 14:04:46 UTC
  every call — twelve in a row, one at a time — answered HTTP 500 within about a second: Belgium
  `BD/SA`, India and Egypt (selection and both roles attempts, so `adjudication_failed`), Slovenia
  (one roles attempt, then the plan), Mexico (selection, so the heuristic chose). Redone after round 3.
  The traveller-facing refusal for `adjudication_failed` still reads "no page could be confirmed as
  the visa decision", which does not say a model call failed.
- **Belgium `BD/AE` answered in rounds 2 and 3 only because `BD/SA` round 1 folded the PDF back into
  the corpus as a depth-0 `proven` entry** (`found_by: corpus`, depth 0, +6). The depth penalty that
  hid it in round 1 is untouched and still hides such pages in every other store.
- **Belgium `BD/SA` round 3** answered, required/verified.
- **Slovenia round 3** answered required/partial: the selector took the New Delhi page (its
  Slovenian-language address). So Slovenia's link is the selector's pick, varying run to run.
- **The UAE fails in the plan, by an application defect**, in rounds 1 and 2: the status is graded
  from this run's fetch, while `unavailable_sources` also carries the two `gdrfad.gov.ae` pages
  discovery found refused — so `verified` beside a named unavailable page, which `VisaPlan` refuses,
  and the traveller gets a 503. Round 3 escaped only because the plan left the decision null (so
  `partial`): the adjudicator credited GDRFA's visa-on-arrival service for Indians resident in the UK,
  and the plan held back because the profile does not say the traveller holds a UK residence visa.
- **India round 3: the plan input exceeded the 80,000-character guard** (14 pages read) and the
  plan refused — `LLMExtractionError`, a 503. The largest plan input that succeeded today was 71,369.
- **Poland: null, 3 of 3** — the 8f bound, every time.
- **Mexico, Saudi Arabia, Croatia, Malta: refused 3 of 3**, for the reasons in round 1.
- **Netherlands `PH/PH`: refused, tool, refused** — named the entry-requirements questionnaire once.

## The fixed arm and Malta's rebuild

- **Fixed arm** (worktree code, a copy of the corpus, three runs each): Netherlands `PH/PH` named the
  Dutch checker as the decision tool 3 of 3; Malta `BD/SA` visa required 3 of 3 (search found the
  list); Malta `BD/AE` null, then required ×2 (the first found only the exemption list, and 8f
  held); the UAE answered 3 of 3, every decision null.
- **Malta rebuilt** on main's code (36 min, 70 queries): 1,722 → 2,012 entries, 756 → 1,008 indexed
  pages, 149 uploads dated 2023–2024 recorded, both visa lists at depth 1 with text. Three runs
  each after: `BD/AE` visa required 3 of 3, list read from the store (link score 18–28); `BD/SA` 2 of
  3, the third held back because Malta's FAQ exempts holders of a Schengen residence permit and the
  profile does not say.
