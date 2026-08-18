# Decisions

Why the project is shaped the way it is, including what was tried and rejected. The reasoning is
recorded because it is the part that cannot be recovered from the code later — a deleted feature
leaves no trace, and a rule with an obvious-looking alternative invites someone to "simplify" it
back into a bug.

Newest first. Add an entry when a decision is made, not afterwards.

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

These corridors do not refuse. They resolve, against domains that cannot hold the answer, which is
exactly the failure mode this project treats as worse than refusing.

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
**2026-08-17**

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
