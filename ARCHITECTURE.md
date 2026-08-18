# Architecture

How the system is put together and why it is shaped this way. For *what* it does and how to run it,
see [README.md](README.md); for the reasoning behind specific choices, [DECISIONS.md](DECISIONS.md).

---

## The trust model

Everything else follows from this, so it comes first.

> **Officialness is a property of who controls the domain, never of how a page reads.**

A page is evidence because it sits on a domain belonging to the destination country's **own
government**, not because it looks authoritative.
Convincing prose earns nothing. This makes an unofficial page *unreachable* rather than merely
low-scoring, which is a much stronger property than filtering.

> **Measured limit, 2026-08-18.** "Own government" is implemented as *governmental* **and** *under the
> country's own TLD*, and the first half is a list of hostname patterns (`gov`, `go.xx`, `gouv.xx`,
> `gob.xx`, `govt.xx`, `gc.ca`, `admin.ch`, `europa.eu`). **19 of 51 countries checked have no such
> marker** — Germany's `auswaertiges-amt.de`, Italy's `esteri.it`, the Netherlands' `ind.nl`, Canada's
> `canada.ca` — so their entire government fails the rule and the destination refuses. The rule fails
> *closed*, which is correct, but the diagnosis it reports is wrong. The amendment is a reviewed
> authority domain per country, **never a wider pattern list**: adding `.de` or `.nl` as governmental
> markers would trust every commercial site in those countries, and for exactly these countries the
> own-TLD test is the only other signal there is. **Schengen is a further problem of definition** — for
> short-stay visas the decision lives at EU level as much as nationally, and `europa.eu` can never
> belong to a member state. See [DECISIONS.md](DECISIONS.md) entry 33 and entry 34.

### Where it is enforced

Three checkpoints. A change to retrieval must preserve all three.

| When | What is checked | Code |
| --- | --- | --- |
| Configuration loads | Every configured source URL sits on a trusted domain, or the whole registry fails to load | `DestinationConfig.validate_route` in `domain/models.py` |
| After an HTTP redirect | The **final** URL is still trusted | `LiveSourceFetcher._fetch_source` |
| After a meta-refresh forward | Both the forward target and where it lands are trusted | `LiveSourceFetcher._read_document` |

### How host matching works

`domain/trust.py`, about 60 lines and worth reading in full.

- `host_is_within` matches exactly or on a **dot boundary**, so `london.mfa.gov.sg` is within
  `mfa.gov.sg` but `notmfa.gov.sg` is not, and neither is `mfa.gov.sg.evil.example`.
- `is_bare_public_suffix` rejects entries like `gov.sg` or `co.uk` that would trust every site
  beneath them. It is a heuristic — two labels whose first is a suffix marker — not a real public
  suffix list, and needs review as countries are added.

### Appointed providers

Some legitimate steps happen on non-government domains: Singapore's applications go through VFS
Global. Such a domain **cannot** pass domain trust, by design. It is authorised only by naming the
official page that appoints it (`appointed_by`), and that page must itself be a configured source.
Authorising a provider is a human judgement and is never automated.

---

## The plan pipeline

One seam, deliberately narrow, so the offline and live paths are interchangeable.

```
DestinationConfig
      │
      ▼
SourceFetcher.fetch(destination) ──▶ RetrievalReport { fetched[], failures[] }
      │                                     fixtures → snapshots on disk
      │                                     live     → HTTP, with cache and trust checks
      ▼
VisaPlanExtractor.extract(destination, traveller, report) ──▶ VisaPlan
                                     fixture → deterministic golden output
                                     openai  → one structured model call
```

`research/service.py` is the whole orchestration and is six lines. `api/dependencies.py` chooses the
implementations from `runtime.yaml`.

### Evidence outcomes

Every configured source resolves to exactly one outcome. Two carry content; three do not.

| Outcome | Usable | Meaning |
| --- | --- | --- |
| `ok` | yes | Fetched fresh, or cache-fresh inside the TTL |
| `stale` | yes | Refresh failed; cached text served inside the stale ceiling |
| `untrusted` | no | Final URL left the approved domains |
| `unreachable` | no | Timeout, connection error, or error status |
| `unusable` | no | Retrieved but not evidence — client-rendered shell, unreadable PDF, JSON API, too little text |
| `blocked` | no | The authority refused automated retrieval (`401`, `403`, `429`) |

`blocked` is the subtle one and is kept apart on purpose. A site refusing automated clients is not
saying its guidance is wrong or missing — it is saying this program may not read it. The only claim
that supports is *"we could not independently retrieve and verify this here"*, which is narrower
than "unreachable" and must never be softened into an inference from another page. Working around
such a block is forbidden; see [DECISIONS.md](DECISIONS.md) entry 18 and the rules in `CLAUDE.md`.

Two things about `blocked` are **decided and not yet implemented**, and both matter because a block can
now resolve a corridor rather than only annotate one:

- **`BLOCKING_STATUS_CODES` is `{401, 403, 429}`, but only `401`/`403` may qualify a corridor.** A `429`
  is a transient rate limit, where "try again later" is the honest advice — the same reasoning entry 27
  applies to a `502`. It stays reported as `blocked`; it stops being grounds to resolve.
- **A block must have cost us the thing we were looking for.** `decision_is_unverified` currently fires
  on *any* blocked URL plus *any* readable source, so a `403` on a footer link can force the visa
  decision to unknown and hand a traveller an irrelevant URL. The blocked page must have been a credible
  `visa_decision` candidate. Without this, corridors whose decision was merely *not found* — which must
  refuse — drift into presenting as authority-blocked, which resolves. See entry 32.

`unreachable` and `unusable` are kept apart deliberately: one is a transient site problem, the other
needs a different retriever. They demand different remedies even though they grade the same.

### Grading and refusal

`research/outcomes.py`, shared by both extractors so the modes can never disagree.

- Each destination declares `required_source_ids` — what the plan cannot stand without.
  `load_bearing_source_ids` is the **union** of those and the document checklist, never a fallback
  between them: naming a required source must not quietly discard the checklist requirement.
- A required source missing → **refuse before the model is called**, so a doomed run costs nothing.
  The API answers `503` naming the missing evidence.
- **A blocked authority is named rather than worked around, and can now carry a plan.** When the
  only page that could confirm the visa decision refused this program, the corridor resolves with
  `decision_is_unverified` and the plan states the decision as **unknown** — enforced in the
  extractor, not asked of the prompt — while naming the page and its URL under
  `unavailable_sources`. `UnreadableAuthority` is deliberately not a source: nothing read it, so
  nothing may cite it, and it is still validated against the approved domains because the domain is
  the only thing vouching for it. A decision that was simply *not found* still refuses. See
  [DECISIONS.md](DECISIONS.md) entry 27.
- **A destination may legitimately have no checklist at all.** Some authorities publish none —
  Vietnam states its e-visa requirements as upload fields inside the application form. That is not
  a refusal, but the absence must be carried rather than smoothed over: `VisaPlan` rejects any plan
  that lists document requirements without a document source behind them, and rejects one that
  stays silent about the gap. The model is never left to infer a checklist from a page that is not
  one. See [DECISIONS.md](DECISIONS.md) entry 14.
- Any failure or any stale source → plan status `partial`. The interface says so *above* the
  guidance in one line, and sets out the reasons and links at the end: a partial plan must not look
  complete, and a wall of caveats above the answer buries the answer. A section with nothing in it —
  a checklist with no source behind it — is not rendered at all, because the absence is already
  stated under unresolved questions, which such a plan is structurally required to carry.
- Everything present and current → `verified`.

### The trust boundary at the model

The model never originates a trusted field. Page text enters the prompt under an explicitly named
`untrusted_content` key; afterwards the application rebuilds `sources`, `last_checked`, `status` and
`application_document_source_ids` from its own configuration, and `VisaPlan`'s validators reject any
citation of a source that was not actually fetched.

---

## Live retrieval

`research/live_sources.py`. Visits only URLs already in the destination registry.

**Caching and freshness** — one JSON file per URL under `var/cache/`, keyed by SHA-256 of the URL,
written atomically.

- Below `source_cache_ttl_hours`: served from cache, no request.
- Above it: revalidated with `If-None-Match` / `If-Modified-Since`, so an unchanged page costs a
  cheap `304`. A changed content hash marks that the guidance moved.
- Refresh failed: cached text is served **flagged stale and keeping its original retrieval time**,
  so it can never present itself as freshly checked.
- Past `source_maximum_stale_hours`: refused rather than served.

**Documents, not just pages.** Authorities publish checklists as PDFs behind tiny HTML pages that
meta-refresh to them. Retrieval reads PDFs and follows one such forward, capped at two hops, with
the trust check applied to each. Provenance records the document actually read, not the page that
pointed at it.

**Rendering.** Some authorities publish an application shell and fetch the guidance client-side, so
an ordinary request returns nothing usable. `research/rendering.py` re-reads such a page in a
headless Chromium, behind the `PageRenderer` protocol.

It is deliberately narrow:

- **On demand only.** Rendering is attempted at exactly one point — after a fetch produced text
  below the readable floor, or text that is translation placeholders rather than sentences. Pages
  that already work never meet a browser, and never pay for one.
- **It widens no trust.** Every request the page makes, document *and* subresource, is aborted
  unless its host is already approved for that destination. A third-party script is not evidence,
  but it decides what the evidence says. Where the render lands is re-checked exactly as a redirect
  is; landing off the approved domains is an `untrusted` failure and the rendered text is discarded.
- **Off by default.** `render_mode` in `config/runtime.yaml` is committed as `never`. Selecting
  `on_demand` without the optional `[render]` extra installed raises rather than silently
  degrading, because the policy line is a reviewed statement about how sites are contacted.
- **Budgeted per caller.** Retrieval and discovery's crawl hold separate allowances. A single
  shared count let the crawl spend everything before the shortlist — the pages that actually become
  evidence — was read, so a working renderer produced no evidence at all.

`looks_untranslated` in `research/live_sources.py` is what catches the second failure: a page of
i18n keys can clear the character floor while saying nothing, and it must not reach extraction as
though it were guidance.

**TLS.** Some authorities send an incomplete certificate chain. Missing intermediates are bundled in
`config/tls_intermediates/`, which fixes the connection **without weakening verification** — each
one must already chain to a trusted root. Verification is never disabled; there are tests asserting
that expired, self-signed, hostname-mismatched and unknown-CA certificates are still rejected.

---

## Source discovery

`discovery/`. Runs two ways, on the same code:

- **`visa-discover`**, a deliberate command with a person reading the result. Still the way to
  investigate a corridor.
- **In the request path**, when `destination_mode: automatic` — a destination nobody configured is
  researched when a plan is asked for. No human approves a domain; the rule below does. See
  `discovery/automatic.py` and [DECISIONS.md](DECISIONS.md) entry 19.

Resolving a corridor cold costs about **53 seconds** — a bootstrap, a crawl, ten fetches and a model
call — so results go in `discovery/corridor_store.py`, one JSON file per corridor, keyed by the
whole corridor and expiring in **weeks**. That is deliberately a much longer life than the evidence
cache's hours: which *pages* answer a corridor changes when a site is redesigned, not when its
guidance is edited, and the pages themselves are re-fetched under their own short TTL every time a
plan is produced. It is a file store rather than an `lru_cache` because a process-lifetime memo
would serve a weeks-old corridor for as long as the server stayed up.

### The corridor

The correct pages depend on the **corridor** — destination, passport nationality, and the country
applied from — because authorities publish per-nationality pages and route applicants to the mission
serving where they live. There are far too many corridors to curate by hand, which is exactly why
this is automated while per-country trust is not.

| | Who to believe (domains) | Which page to read (URLs) |
| --- | --- | --- |
| Corridor-dependent? | No — `mofa.go.jp` serves everyone | Yes |
| How many | ~3 per country | Tens of thousands |
| Decided by | **A rule, once per country** | **The machine, every corridor** |

> **The code does not yet implement the left column, and that is a live problem.**
> `bootstrap_destination` runs *inside every cold request*, and its result is cached **per corridor** —
> so a country's trusted set is re-derived from that day's search rankings for every new nationality,
> and the answer to "who is Germany's government" varies between runs. Entry 22's US coin flip was this
> mechanism, diagnosed at the time as a ranking problem. [DECISIONS.md](DECISIONS.md) entry 34 moves it
> to a registry generated offline for all 198 countries, committed beside `countries.yaml`, and skimmed
> once by a person. That is not a return to the gate entry 19 removed: that gate was over *URLs*, which
> stay fully automated: this is ~3 domains per country, machine-proposed, frozen in review.

### The stages

0. **Politeness** — *not implemented, and owed.* Nothing in this codebase reads `robots.txt`. A crawl
   that computes a per-host delay while ignoring the file stating that host's own policy is inconsistent
   on its own terms, and the posture this project wants is *honest client* rather than *anonymous
   client*. Expect it to **cost** coverage: a path currently walked past becomes a refusal, which is the
   right direction. A `Disallow` is a stated policy, not a block to route around.
   See [DECISIONS.md](DECISIONS.md) entry 35.
1. **Search** (`search.py`) — templated queries constrained with `site:` to approved domains, run
   four at a time rather than one after another; bounded because a search API is someone else's rate
   limit.
   Queries are built from the corridor alone: never model-written, never derived from fetched page
   content, so a page cannot influence what is searched next. Results are filtered again by
   `trusts_host`, so the restriction is enforced twice.
2. **Crawl** (`crawl.py`) — best-first, two hops, inside approved domains. Search lands on a section
   index; the checklist is usually one link further on. Budget is shared between seeded hosts so a
   large ministry portal cannot starve the mission site. The frontier is walked in **waves** of at
   most one page per host, fetched together: the politeness delay is owed to a host, so applying it
   globally made every site wait behind every other. Results are handled in frontier order rather
   than completion order, because which page a corridor resolves to must not depend on which site
   answered first.
3. **Fetch the shortlist** (`resolver.py`) — by building a throwaway `DestinationConfig` and passing
   it to the ordinary `LiveSourceFetcher`. This inherits redirect trust, PDF reading, forwarding,
   size caps and caching with no duplicated code — and because `validate_route` runs on that config,
   an off-domain candidate cannot even be constructed. Pages the crawl already proved unreadable are
   dropped first — a host whose name does not resolve, or a URL an authority refused, both facts
   already established rather than predicted. A page that was merely too large, not HTML, or `502`
   stays: retrieval reads PDFs and renders where the crawler does not, so it may still be evidence.
   Ten places: the best three per role, then the
   next best overall, then **one place reserved for each registrable domain's best page**. The
   reservation matters because these places decide what is *read*, and only a read page can fill a
   role — so without it an authority whose pages all score below another's is absent rather than
   merely ranked low, and the corridor refuses with the answer one place outside the cut.
4. **Score** (`scoring.py`) — deterministic, **no model calls**. Vocabulary and weights live in
   `config/discovery_lexicon.yaml` so they can be tuned without touching Python.
5. **Assign roles or refuse** — by judgement when `discovery_decider: model`, otherwise by the
   heuristic. Only `visa_decision` is load-bearing; a missing checklist is reported and moves the
   exit code from `0` to `1` rather than refusing, because some authorities publish none.

### Who decides the last step

Keyword ranking got Brazil wrong, and wrong *confidently* — see [DECISIONS.md](DECISIONS.md)
entry 15. The failure was localised: the correct page was found, trusted, crawled, shortlisted and
read, and only the final choice among ten fetched pages was wrong. So that one step, and no other,
asks a model (`discovery/adjudication.py`).

What it may do is bounded hard, and the bounds are the safety story:

- it chooses from an explicit candidate list the application built. **An id it invents is discarded
  and the role left unfilled** — it cannot introduce a page that never passed domain trust.
- it never widens trust. Officialness is settled by who controls the domain, before this runs.
- candidate text reaches it under `untrusted_content`, and the prompt says it is evidence rather
  than instructions.
- it may return null for a role, and the prompt states that refusing beats guessing. A refusal is
  honoured rather than filled in from the ranking.
- heuristic scores are withheld from the packet, so the ranking that failed cannot anchor it.
- a failed call currently falls back to the heuristic. **This is being reversed** ([DECISIONS.md](DECISIONS.md)
  entry 31): the fallback silently substitutes the decider entry 15 proved gives *confident wrong
  answers*, so an outage turns the best decider into the worst one with only `decided_by` to show it. A
  failed call will retry once and then refuse the corridor, which is an outcome this product supports
  and states honestly.

The heuristic is not replaced. It builds the shortlist the model chooses from — which stays
load-bearing, since a page it ranks outside the ten fetch places is one the model never sees — it
answers when no adjudicator is configured, and its score is recorded beside the model's choice so a
reviewer can see where the two disagreed.

### Scoring, in brief

Two rules carry most of the weight:

- **Link text outweighs the URL.** Japan's checklist parent is `index_000070.html`, which says
  nothing; only its label "Temporary Visitor Visa" identifies it. A URL-only scorer fails outright.
- **Wrong-audience pages must lose decisively.** A spouse-visa checklist on the correct domain in
  the correct format is the most dangerous candidate there is, because every other check passes.

Some exclusions are **vetoes rather than penalties**, because no accumulated score should overcome
them: archived paths, a page about another country, hard wrong-audience terms such as `diplomatic`,
and **site furniture** — an accessibility statement or a legal notice cannot be visa guidance
whatever it scores, and France's scored 69 because a footer link inherits the last heading above it.

Country identity is read from a page's **own words** — its path and title — and not from its host,
because a host label names which *post* published a page. `in.diplomatie.gouv.fr` is France's mission
in India, and reading that as "written for Indian nationals" put the traveller's home post above the
post they must actually apply at (entry 26). Which post serves a traveller is decided separately, by
where they are applying from. A page can fill **several roles** — Singapore's per-nationality page is both the
decision source and the checklist.

### Bootstrapping a new country

`bootstrap.py` proposes authority domains from search. A human used to approve them; the rule that
replaced that approval is **`is_own_government`** — governmental **and** under the destination's own
top-level domain. Both halves are load-bearing, and it reproduces all 22 recorded human decisions
(entry 19). The safeguards exist because this is the one place search results are not already
bounded by an approved domain:

- a **denylist** removes commercial visa agencies before anyone reads the list;
- a domain must be **corroborated** by two independent queries — relaxed to one when it is the
  destination's own government, and *only* where that is genuinely two independent signals. Where a
  country's own top-level domain is itself the governmental marker the two halves ask one question,
  so the ordinary bar applies (entry 22);
- **bare public suffixes** are rejected outright;
- the domain must plausibly **belong to the destination country**. "Looks governmental" is satisfied
  by any country's `.gov`, which is how the US embassy in Vietnam once outranked Vietnam's own
  immigration department. Foreign government pages are shown, flagged, and never first.

**The rule says which domains may be used, and a bound says how many.** A large government passes it
with far more domains than a small one — the United States with eight, Brazil with one — and width is
expensive three times over: three searches are run per trusted domain, the crawl's per-host budget is
the page budget divided by the hosts seeded, and the shortlist has ten places. So at most five are put
to use, ordered by the authority hint in the hostname (`emb`, `consul`, `immi`, `mofa`) and then by
corroboration. Everything left out is reported with its reason, and the reason distinguishes "this
destination's own government, not among the best evidenced" from "another country's government" —
they are different problems with different fixes. See entry 22.

The `bootstrap` command still approves nothing: it prints the whole list for a person to read. The
cap applies where domains are put to use without one, in `automatic.py`.

---

## Configuration

Split by what a thing *is*, not by convenience.

| Where | Holds | Committed? |
| --- | --- | --- |
| `config/runtime.yaml` | source mode, extraction mode, cache TTL, stale ceiling | **Yes** — these decide whether government sites are contacted, whether a paid model runs, and when stale guidance is refused, so they belong under review |
| `config/destinations.yaml` | destinations, trusted domains, appointed providers, required sources | **Yes** — the trust anchor |
| `config/discovery_*.yaml`, `countries.yaml` | scoring vocabulary, denylist, country reference data | **Yes** — tunable without code changes |
| `.env` | `OPENAI_API_KEY`, `SEARCH_API_KEY`, timeouts, limits, cache directory | **Never** |

---

## Testing

`AGENTS.md` requires that tests never touch the network or an LLM. The seams that make this possible
are `transport=` (an `httpx.MockTransport`) and `now=` (a controllable clock) on both fetchers,
`renderer=` (a `PageRenderer`) for the browser, and fake generators for the model.

- `tests/discovery_site.py` is a fake two-host government site reproducing the shapes actually hit
  in the wild: an opaque URL identifiable only by anchor text, a per-nationality page two hops deep,
  a checklist behind a forward to a PDF, a wrong-audience sibling, a client-rendered shell, and an
  off-domain link that must never be requested.
- `tests/test_rendering.py` injects a fake renderer rather than starting a browser. Its one real
  Chromium check is marked `manual` and skipped unless `VISA_RENDER_MANUAL=1`, and even then it
  renders a `data:` URL rather than reaching the network.
- `tests/test_pdf_sources.py` builds real PDFs by hand, so there are no binary fixtures.
- The load-bearing assertions are the safety ones: no off-domain host is ever requested, a spam
  result is dropped before any fetch, and zero model calls when the heuristics are confident.
