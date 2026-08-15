# Architecture

How the system is put together and why it is shaped this way. For *what* it does and how to run it,
see [README.md](README.md); for the reasoning behind specific choices, [DECISIONS.md](DECISIONS.md).

---

## The trust model

Everything else follows from this, so it comes first.

> **Officialness is a property of who controls the domain, never of how a page reads.**

A page is evidence because it sits on a domain a human approved, not because it looks authoritative.
Convincing prose earns nothing. This makes an unofficial page *unreachable* rather than merely
low-scoring, which is a much stronger property than filtering.

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

`unreachable` and `unusable` are kept apart deliberately: one is a transient site problem, the other
needs a different retriever. They demand different remedies even though they grade the same.

### Grading and refusal

`research/outcomes.py`, shared by both extractors so the modes can never disagree.

- Each destination declares `required_source_ids` — what the plan cannot stand without.
- A required source missing → **refuse before the model is called**, so a doomed run costs nothing.
  The API answers `503` naming the missing evidence.
- Any failure or any stale source → plan status `partial`, and the interface states what is
  incomplete *above* the guidance.
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

**TLS.** Some authorities send an incomplete certificate chain. Missing intermediates are bundled in
`config/tls_intermediates/`, which fixes the connection **without weakening verification** — each
one must already chain to a trusted root. Verification is never disabled; there are tests asserting
that expired, self-signed, hostname-mismatched and unknown-CA certificates are still rejected.

---

## Source discovery

`discovery/`. Runs offline as `visa-discover`, never inside a plan request.

### The corridor

The correct pages depend on the **corridor** — destination, passport nationality, and the country
applied from — because authorities publish per-nationality pages and route applicants to the mission
serving where they live. There are far too many corridors to curate by hand, which is exactly why
this is automated while per-country trust is not.

| | Who to believe (domains) | Which page to read (URLs) |
| --- | --- | --- |
| Corridor-dependent? | No — `mofa.go.jp` serves everyone | Yes |
| How many | ~3 per country | Tens of thousands |
| Decided by | **A human, once per country** | **The machine, every corridor** |

### The stages

1. **Search** (`search.py`) — templated queries constrained with `site:` to approved domains.
   Queries are built from the corridor alone: never model-written, never derived from fetched page
   content, so a page cannot influence what is searched next. Results are filtered again by
   `trusts_host`, so the restriction is enforced twice.
2. **Crawl** (`crawl.py`) — best-first, two hops, inside approved domains. Search lands on a section
   index; the checklist is usually one link further on. Budget is shared between seeded hosts so a
   large ministry portal cannot starve the mission site.
3. **Fetch the shortlist** (`resolver.py`) — by building a throwaway `DestinationConfig` and passing
   it to the ordinary `LiveSourceFetcher`. This inherits redirect trust, PDF reading, forwarding,
   size caps and caching with no duplicated code — and because `validate_route` runs on that config,
   an off-domain candidate cannot even be constructed.
4. **Score** (`scoring.py`) — deterministic, **no model calls**. Vocabulary and weights live in
   `config/discovery_lexicon.yaml` so they can be tuned without touching Python.
5. **Assign roles or refuse** — no confident checklist means the corridor is unresolved, with a
   report naming what was considered and why each candidate was rejected.

### Scoring, in brief

Two rules carry most of the weight:

- **Link text outweighs the URL.** Japan's checklist parent is `index_000070.html`, which says
  nothing; only its label "Temporary Visitor Visa" identifies it. A URL-only scorer fails outright.
- **Wrong-audience pages must lose decisively.** A spouse-visa checklist on the correct domain in
  the correct format is the most dangerous candidate there is, because every other check passes.

Some exclusions are **vetoes rather than penalties**, because no accumulated score should overcome
them: archived paths, a page about another country, and hard wrong-audience terms such as
`diplomatic`. A page can fill **several roles** — Singapore's per-nationality page is both the
decision source and the checklist.

### Bootstrapping a new country

`bootstrap.py` proposes authority domains from search, for human approval. The safeguards exist
because this is the one place search results are not already bounded by an approved domain:

- a **denylist** removes commercial visa agencies before anyone reads the list;
- a domain must be **corroborated** by two independent queries — relaxed to one when it is under
  the destination's own top-level domain;
- **bare public suffixes** are rejected outright;
- the domain must plausibly **belong to the destination country**. "Looks governmental" is satisfied
  by any country's `.gov`, which is how the US embassy in Vietnam once outranked Vietnam's own
  immigration department. Foreign government pages are shown, flagged, and never first.

Nothing is approved automatically.

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
are `transport=` (an `httpx.MockTransport`) and `now=` (a controllable clock) on both fetchers, and
fake generators for the model.

- `tests/discovery_site.py` is a fake two-host government site reproducing the shapes actually hit
  in the wild: an opaque URL identifiable only by anchor text, a per-nationality page two hops deep,
  a checklist behind a forward to a PDF, a wrong-audience sibling, and an off-domain link that must
  never be requested.
- `tests/test_pdf_sources.py` builds real PDFs by hand, so there are no binary fixtures.
- The load-bearing assertions are the safety ones: no off-domain host is ever requested, a spam
  result is dropped before any fetch, and zero model calls when the heuristics are confident.
