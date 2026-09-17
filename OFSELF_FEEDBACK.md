# Ofself platform feedback

What integrating this app with Ofself — through its developer platform Paradigm, its CLI and
Personas — showed about the platform itself, written for Ofself's developers. The owner works
with them directly and shares this as a picture of how an outside developer meets the platform.

**The rules for this file:**
- **Only what the platform does.** This app's own design lives in [CRUX.md](CRUX.md), its
  reasoning in [DECISIONS.md](DECISIONS.md) entry 180, and the work in [TODO.md](TODO.md) item 55.
- **Every entry says how it is known:** *observed* against the live API or CLI, *read* in the
  CLI's source, or *from the docs* alone. Nothing is written as a platform bug that was not seen.
- **Dated, with the versions it was seen on,** because the platform is moving. Add to it as
  integration goes on, and mark an entry resolved rather than deleting it.

Seen with `paradigm-cli` 0.5.0 against `https://api.ofself.ai`, 2026-09-16 to 2026-09-17, using the
developer guide (as pasted by the owner) and the Personas guide served at `/api/v1/docs`.

---

## 1. Where the live platform differs from the developer guide

**1.1 `GET /nodes` answers `"total": null`.** *Observed.* Every answer for a sandbox user, with and
without `limit`, carried `"total": null`. The guide shows a count and its sync examples page on it
(`if offset + limit >= resp["total"]`). A client following the guide stops after one page, or raises
comparing an integer with `None`. This app now pages until a page comes back short.
*Suggest:* return the count, or document that it is absent and show paging on a short page.

**1.2 `POST /nodes` returns the node at the top level.** *Observed.* The response is the node itself
(`{"id": …, "value_json": …}`). The guide's test-user example reads `resp.json()["node"]["id"]`,
which raises `KeyError`.

**1.3 A DLR can request specific fields — the guide says it cannot.** *Read, and observed on the app
record.* The guide says field and row masks are set by the user and "as a developer you don't set
this yourself". `paradigm dlr add-read --fields` exists, a `fields` key in a DLR request is stored
(`paradigm dlr show` reports `fields: [citizenships]`), and the consent preview shows it. This
changed a real design decision here: the app now asks for `work-authorization.citizenships` alone
instead of the whole node, including the user's `notes`.
**Not yet known whether it is enforced** — see 4.1.

**1.4 `GET /my-permissions` returns `effective_access`, which the guide does not mention.**
*Observed.* It is the full access document, beside the `effective_verbs` the guide describes. It
is what an app needs to see which schemas and fields it was actually granted.

---

## 2. Where the documentation disagrees with itself or with the CLI

**2.1 Where the DLR lives — three sources, three answers.** *Read and observed.*
- The developer guide: `CRUX.md` has nine sections; §9 holds the DLR; `crux sync` pushes it.
- `paradigm crux init` (0.5.0) scaffolds a **sixteen**-section `CRUX.md` that says *"there is no
  DLR section here"*, and `crux sync`'s own help calls §9 *"legacy"*.
- `paradigm crux validate` then **fails** on that same template until a `dlr.requests` block is
  added, while `paradigm crux check` reports *"All 16 sections filled. CRUX is complete."*
- The Claude Code skill `crux init` installs still says to author §9.

A developer following the scaffold is told there is no DLR section and then refused for lacking one.

**2.2 What happens to existing users when a DLR expands.** *From the docs.* §15 says their grants
are **paused** until they re-authorise. §34.4 says `app push` makes the developer choose
`--ep-action cancel` (revoke) or `continue` (keep the old scope working). The CLI implements the
second.

**2.3 Two error envelopes and two code vocabularies.** *From the docs; one observed.* §18 documents
`{"error": "forbidden", "message": …, "detail": …}`; §29 documents
`{"error": {"code": …, "message": …}}`. §4 and §10 use `NO_AUTHORIZATION`; §29 lists `EP_NOT_FOUND`,
`EP_REVOKED`, `EP_PAUSED`, `EP_EXPIRED`; `/my-permissions` is documented as `NO_PERMISSIONS`.
**Observed:** an unauthorised user returned `EP_NOT_FOUND` in the §29 shape, with a clear message.
*Suggest:* retire §18's envelope and list which codes can come back from which endpoint.

**2.4 Three names for the permissions endpoint.** *From the docs.* `GET /my-permissions`,
`GET /third-party/me` and `GET /third-party/my-permissions` all appear, described slightly
differently. Only the first was tried here.

**2.5 "Your infrastructure never sees plaintext" against delegated decryption.** *From the docs.*
§1 says sensitive fields are encrypted client-side and an app's infrastructure never sees
plaintext. §6 and §34.8 describe `enc_user_privkey`: the user's **whole** private key, wrapped for
the app and unwrapped in its memory at runtime, which decrypts any encrypted field — not only those
the grant covers. Both are true, but §1 leads a developer to believe something §6 contradicts. This
app declined encrypted fields partly for this reason.

**2.6 "`app push` asks for the app's metadata once."** *Read.* It does not ask. Without the
`.paradigm/pending.toml` that `paradigm init` writes, it exits: *"Not a Paradigm project, or the
app is not registered yet."*

---

## 3. Integrating an existing codebase

This app was a mature Python project before Ofself: its own `.venv`, `README.md`, `.env.example`
and test suite. The CLI assumes a new project.

**3.1 There is no supported way to register an existing project.** *Read and observed.*
- `app push` needs `.paradigm/pending.toml`, and only `paradigm init` writes it (2.6).
- `paradigm init` refuses because `README.md` and `.env.example` exist, unless `--force`, which
  overwrites them and `CRUX.md` with templates.
- Its default `--setup` installs `requirements.txt` — including `paradigm-sdk` from git — into the
  project's existing `.venv`, and copies `.env.example` to `.env` when `.env` is missing.

It was registered by writing `pending.toml` by hand, from reading the CLI's source.
*Suggest:* `paradigm app create --name … --redirect-uri …`, or `init --no-scaffold` that writes only
`CRUX.md` and the binding.

**3.2 A DLR sync says "pushed" when it has only been staged.** *Observed.* `paradigm crux sync`
printed *"✓ Pushed 1 request item(s) to the app's DLR"*. Straight afterwards `paradigm dlr show`
said `requests (0)` and `paradigm dlr preview` showed an empty consent card, until
`paradigm commit` applied it. Neither the message nor the guide mentions the staging step.

**3.3 `app push` registers with an empty DLR.** *Read and observed.* It does not read `CRUX.md`, so
the app exists with `requests (0)` until `crux sync` and `paradigm commit`. Worth saying at the end of
`app push`.

**3.4 Asking a human before publishing a DLR is good, and worth keeping.** *Read.* `crux sync`
refuses a non-interactive shell so that an AI assistant cannot confirm what users will consent to
on the developer's behalf, and says so. It was the right call here: the owner ran it themselves.

---

## 4. What the sandbox cannot test

**4.1 Sandbox users have full access, so narrowed grants cannot be tested.** *Observed.* A sandbox
user's `/my-permissions` grants every verb with no scope. Reading its `work-authorization` returned
`notes`, `source` and `work_authorized_in` although the DLR asks for `citizenships` only — which
says nothing about a real user, because a sandbox grant is not built from the DLR. So whether a
field restriction is enforced (1.3), and what an app sees when a user hides a field, can only be
learnt from a real OAuth authorisation.
*Suggest:* a sandbox user whose grant is exactly the app's DLR, and one with a field hidden.

---

## 5. Gaps in the documentation

**5.1 Hosting is not mentioned.** *From the docs and the CLI.* An app registers a redirect URI,
webhook URL and plugin endpoint, which implies the developer hosts it, and the CLI has no deploy
command. Nothing says so, and nothing answers:
- does Ofself host apps, or plan to; is there a preferred provider, region or data-residency rule;
- does a user open an app at its own URL, or is it embedded in app.ofself.ai — which changes frame
  headers, cookies and allowed origins;
- are there domain requirements (HTTPS only, custom domain, subdomain);
- is mobile supported — may a redirect URI be a deep link, and is there a mobile `@ofself/shell`;
- if an app goes down, is it flagged or delisted, and is anyone told; does reachability count in
  readiness or verification;
- what happens to paid subscribers during an outage, or when an app is retired;
- how an app is retired — does deleting it revoke every grant, and are users told why.

**5.2 `http://localhost` redirect URIs work, but only by trying.** *Observed.* Registration
accepted `http://localhost:8000/oauth/callback`. The guide implies it ("one per environment
(local, staging, prod)"); stating it outright would save the question.

**5.3 The guides cannot be read by tools.** *Observed.*
- `paradigm init` copies `DEVELOPER_GUIDE.md` and `API_REFERENCE.md` from package data, but neither
  file is in the installed `paradigm-cli` 0.5.0.
- The hosted reference redirects from `app.ofself.ai/documentation` to
  `nucleus.ofself.com/documentation/…` and is a JavaScript application, so its text cannot be
  fetched.
- Personas serves its guide as plain markdown at `/api/v1/docs`, which worked well. The same for
  Paradigm would help both people and coding assistants.

**5.4 Domains are moving.** *Observed.* `app.ofself.ai` redirects to `nucleus.ofself.com`, and
`personas.ofself.ai` to `personas.ofself.com`. `api.ofself.ai` answered directly. The guides still
give the `.ai` addresses.

**5.5 No per-user cost control for the app.** *From the docs.* An exposure profile's `rate_limit` is
set by the user. An app whose every request costs real money — about $0.31 of search and model
calls here — has no documented way to cap a user's usage except charging for the app.

---

## 6. Schema registry

**6.1 Nothing for travel identity.** *Observed.* `paradigm schema search` for passport, nationality,
residence, residency and immigration returned nothing. The nearest was `work-authorization`
(category `work`), whose `citizenships` stands in for passport nationality. There is no passport
type or expiry, no country of residence apart from `place`, and nothing for residence status or
permit expiry. The owner plans to propose a schema for these.

**6.2 `work-authorization.citizenships` allows alpha-2 or alpha-3.** *Observed in the schema.* Its
description says either, so every app reading it must accept both. This app added alpha-3 codes for
all 198 countries it knows to do so. One format in the schema would spare every consumer.

**6.3 A DLR can narrow fields but not rows.** *From the docs and the CLI.* `place` holds a home's
country, but a request for it returns every place the person holds — properties, towns, airports —
because `add-read` has `--fields` and no filter. `trip` cannot be limited to future trips. For both,
this app asks the user instead. A row filter in a DLR request would make both usable.

**6.4 `fact` stores rules with a source URL, which invites misplaced trust.** *Observed in the
schema.* Its description covers *"a tax rule, a visa floor, a fee"*, with a `source` URL, written by
apps such as `allocations_ofself`. For a domain where a wrong rule sends someone to a visa centre
without the right papers, a URL in another app's record is not verification, and this app never
reads `fact` as evidence. Worth a note in the schema about what `basis` and `source` do and do not
establish.

**6.5 Search results repeat.** *Observed.* `schema search` returns the same schema name several
times (for example `nutrition:food`), presumably one row per version.

---

## 7. Design and security observations

**7.1 The CLI install puts the developer token in two places.** *Observed.* The documented
`pipx install … --pip-args="--extra-index-url https://paradigm:<TOKEN>@…"` leaves the `ofs_dev_`
token in shell history and in pipx's `pipx_metadata.json` (mode 600). A token grants full access to
the developer's account.
*Suggest:* `pip`'s keyring or netrc, or a `paradigm` installer that reads the token from a prompt.

**7.2 The guide recommends appending user-authored prompts to an app's model prompt.** *From the
docs.* §26 suggests `system_prompt += custom_prompts` from `GET /guidelines`. For any app where a
model's output matters, that is outside text steering the model, and this app declines it. Worth a
caution beside the example.

**7.3 `pipx` leaves `paradigm` off `PATH` on macOS.** *Observed.* `~/.local/bin` was not on `PATH`,
so the documented `paradigm login` failed with `command not found` straight after install. One line
about `pipx ensurepath` would cover it.

---

## 8. Personas

Evaluated for this app's model calls on 2026-09-17, after an Ofself developer suggested Personas'
headless mode for model credits. *From the Personas guide at `/api/v1/docs`.*

- **No structured output.** *"There is no `response_format` / JSON-schema enforcement."* This app's
  four model calls each require a JSON schema.
- **A wrapper prompt that cannot be switched off.** Each run adds Personas' own instructions — the
  sandbox, Paradigm data, markdown and widgets — around the app's prompt. This app's measurements
  show small prompt changes altering a visa decision.
- **Model settings.** Provider, model and temperature only; no reasoning effort and no prompt-cache
  control. And passing `llm_model` once changes the agent permanently, which is easy to do by
  accident.
- **Every run needs a Paradigm user.** Calls that serve no particular user, and offline jobs with no
  user at all, cannot use it.
- **The signing key travels in the request body** (`hmac_key`) as well as keying the signature, so
  the signature adds little beyond TLS.
- **Nothing says who pays** or what limits apply.

**Asked of Ofself:** is there direct, OpenAI-compatible model access behind the `ofself` provider,
with structured outputs, reasoning effort and caching, and who is billed?

---

## 9. What worked well

- **The design gate.** `crux validate` resolving schemas against the registry, and the prompts to
  search before inventing a schema, caught nothing wrong here but asked the right questions.
- **`paradigm dlr preview`.** Seeing the exact consent card before publishing is the right check.
- **Error messages.** `EP_NOT_FOUND` came back with *"The user must complete the OAuth authorization
  flow first."* — actionable as written — and a bad key with `INVALID_API_KEY`.
- **Sandbox users.** One command, a working `X-User-ID`, no OAuth. It made the adapter testable
  against the live API in minutes, within the limit in 4.1.
- **Personas' guide at `/api/v1/docs`.** Versioned with the deployment and readable as markdown.

---

## Open questions for Ofself

Raised in this project on the date shown. Fill in when each was put to Ofself, and the answer.

| Question | Raised | Put to Ofself | Answer |
| --- | --- | --- | --- |
| Does Ofself host apps, and is an app linked out to or embedded? (5.1) | 2026-09-17 | — | — |
| Does any app record a `trip` before it happens? | 2026-09-17 | — | — |
| Is direct model access available behind the `ofself` provider, and who is billed? (8) | 2026-09-17 | — | — |
| Is a DLR `fields` restriction enforced on a real grant? (1.3, 4.1) | 2026-09-17 | — | — |
