# Ofself platform feedback

What integrating this app with Ofself (Paradigm, its CLI, Personas) showed about the platform, for
Ofself's developers. This app's own design is in [CRUX.md](CRUX.md), DECISIONS entry 180 and TODO
item 55; this file is only about the platform.

Each point says how it is known — **[observed]** against the live API or CLI, **[read]** in the CLI's
source or the authorize page's JavaScript, **[docs]** from the developer guide alone. Seen with
`paradigm-cli` 0.5.0 against `api.ofself.ai`, 2026-09-16 to 2026-09-18. Mark a point resolved
rather than deleting it.

---

## 1. The live API differs from the guide

- **1.1 `GET /nodes` returns `"total": null`** [observed]. The guide's paging examples compare against
  a count, so they stop after one page or raise. *Suggest:* return the count, or document paging on
  a short page.
- **1.2 `POST /nodes` returns the node unwrapped** [observed]. The guide's test-user example reads
  `resp.json()["node"]["id"]`, which raises `KeyError`.
- **1.3 A DLR can request single fields** [read, observed]. The guide says field masks are set only
  by the user. But `paradigm dlr add-read --fields` exists, the app record stores `fields`, the
  consent card shows it, and a real grant carries it (9.8). Whether a read then returns only those
  fields is still unseen.
- **1.4 `GET /my-permissions` also returns `effective_access`** [observed], the full granted access
  document. The guide doesn't mention it, and it's the field that shows which schemas and fields were
  granted.

## 2. The docs disagree with themselves or the CLI

- **2.1 Where the DLR lives: three answers** [read, observed].
  - The guide says §9 of a nine-section `CRUX.md`.
  - `crux init` scaffolds sixteen sections and says there is no DLR section, and `crux sync` calls §9
    "legacy".
  - `crux validate` then fails until a `dlr.requests` block is added, while `crux check` reports the
    same file complete.
  - The bundled skill still says §9.
- **2.2 When a DLR expands** [docs]. §15 says existing grants are paused. §34.4 says `app push`
  requires `--ep-action cancel|continue`, which is what the CLI does.
- **2.3 Two error envelopes, two code vocabularies** [docs; one observed].
  - §18 shows `{"error": "forbidden", …}` and §29 shows `{"error": {"code", "message"}}`.
  - The codes are `NO_AUTHORIZATION`, `NO_PERMISSIONS` and the `EP_*` family.
  - Live, an unauthorised user got `EP_NOT_FOUND` in the §29 shape.
- **2.4 Three names for the permissions endpoint** [docs]: `/my-permissions`, `/third-party/me`,
  `/third-party/my-permissions`.
- **2.5 "Never sees plaintext" vs delegated decryption** [docs]. §1 says an app's infrastructure never
  sees plaintext. §6 hands the app the user's whole private key (`enc_user_privkey`), which isn't
  scoped to the grant. This app declined encrypted fields partly for that.
- **2.6 "`app push` asks for the app's metadata once"** [read]. It doesn't ask. Without the
  `.paradigm/pending.toml` that `init` writes, it exits with "Not a Paradigm project".

## 3. Integrating an existing codebase

- **3.1 No supported way to register an existing project** [read, observed].
  - `app push` needs `pending.toml`, which only `init` writes.
  - `init` refuses when `README.md` or `.env.example` exist. With `--force` it overwrites them.
  - `init`'s default setup installs `paradigm-sdk` from git into the project's `.venv`.

  This app wrote `pending.toml` by hand. *Suggest:* `app create --name … --redirect-uri …`, or an
  `init` that writes only the binding.
- **3.2 `crux sync` says "Pushed" when it only staged** [observed]. `dlr show` read `requests (0)` and
  the consent card was empty until `paradigm commit`. The guide's DLR sections don't mention the
  staging step.
- **3.3 `app push` registers with an empty DLR** [read, observed]. It doesn't read `CRUX.md`. Worth
  saying when it finishes.
- **3.4 Good: `crux sync` refuses a non-interactive shell** [read], so an AI assistant can't confirm a
  consent screen on a developer's behalf.

## 4. Sandbox users

- **4.1 Full access only** [observed]. A sandbox grant ignores the DLR: the app read `notes`,
  `source` and `work_authorized_in` although it asks for `citizenships` alone. So narrowed grants and
  hidden fields can't be tested without a real authorisation. *Suggest:* a sandbox user whose grant
  is exactly the DLR.

## 5. Gaps in the docs

- **5.1 Hosting** [docs, CLI]. Registration implies the developer hosts the app, and the CLI has no
  deploy command. Nothing says:
  - whether Ofself hosts apps, and any provider or data-residency preference
  - whether apps are linked out to or embedded in app.ofself.ai
  - domain rules
  - mobile support: deep-link redirect URIs, a mobile `@ofself/shell`
  - what happens when an app goes down or is retired, including paid subscribers and whether
    grants are revoked
- **5.2 `http://localhost` redirect URIs are accepted** [observed]. Say so outright.
- **5.3 The guides can't be read by tools** [observed]. `init` copies `DEVELOPER_GUIDE.md` and
  `API_REFERENCE.md` from package data, but 0.5.0 ships neither. The hosted reference is a
  JavaScript app. Personas' plain-markdown `/api/v1/docs` is the model to copy.
- **5.4 Domains are moving** [observed]. `app.ofself.ai` redirects to `nucleus.ofself.com`, and
  `personas.ofself.ai` to `personas.ofself.com`. The guides still give `.ai`.
- **5.5 No app-side per-user cost cap** [docs]. Only the user can set an exposure profile's
  `rate_limit`. That matters for an app paying about $0.31 in search and model calls per request.

## 6. Schema registry

- **6.1 Nothing for travel identity** [observed]. No passport, nationality, residence or
  immigration schema. `work-authorization.citizenships` is the nearest. The owner plans to propose
  one.
- **6.2 `citizenships` allows alpha-2 or alpha-3** [observed], so every reader must accept both. One
  format would spare them.
- **6.3 A DLR narrows fields but not rows** [docs, CLI]. `place` can't be limited to a home, or
  `trip` to future trips, so this app asks the user instead.
- **6.4 `fact` invites misplaced trust** [observed]. It stores "a tax rule, a visa floor, a fee" with
  a `source` URL written by another app. That URL isn't verification, and this app never reads `fact`
  as evidence. Worth a note on what `basis` and `source` establish.
- **6.5 `schema search` repeats names** [observed], e.g. `nutrition:food`, apparently once per
  version.

## 7. Security and setup

- **7.1 The install leaves the developer token behind** [observed]. `--extra-index-url
  https://paradigm:<TOKEN>@…` puts the `ofs_dev_` token in shell history and pipx's
  `pipx_metadata.json`. *Suggest:* keyring, netrc or a prompt.
- **7.2 §26 suggests appending user-written prompts to an app's model prompt** [docs]. That's outside
  text steering the model. It needs a caution.
- **7.3 `paradigm` isn't on `PATH` after install on macOS** [observed]. Mention `pipx ensurepath`.

## 8. Personas, for this app's model calls

Evaluated 2026-09-17 after Personas headless mode was suggested for model credits [docs]:
- **No structured output.** This app needs a JSON schema on every model call.
- **A wrapper prompt that can't be switched off.** Small prompt changes here have altered visa
  decisions.
- **Model settings stop at provider, model and temperature.** There's no reasoning effort or cache
  control, and passing `llm_model` once changes the agent permanently.
- **Every run needs a Paradigm user.**
- **`hmac_key` travels in the body as well as signing it.**
- **Cost and limits are undocumented.**

## 9. Signing a user in

The guide shows only SDK helpers (`build_oauth_url`, `verify_callback`), the SDK repository is
private, and the reference isn't shipped (5.3). So this flow was read from the authorize page's
JavaScript and confirmed with one real sign-in.

- **9.1 The callback trusts nothing** [read]. It redirects with `code=success` (a literal),
  `client_id`, `user_id`, `username` and `sid_code`. An app that trusts `user_id` signs a visitor in
  as anyone a link names. `verify_callback(code, user_id, username)` suggests exactly that.
- **9.2 `sid_code` is the only proof, and it's undocumented** [read, observed].
  - An app redeems it at `POST /api/v1/auth/session/exchange` with `X-API-Key` and `{"code": …}`,
    found by probing: `404 INVALID_CODE`, `400 VALIDATION_ERROR`, `401 MISSING_API_KEY`.
  - A real sign-in on 2026-09-17 succeeded and named the user as a UUID, but which response field
    held it wasn't recorded.
  - The page silently omits `sid_code` if `POST /auth/session/start` fails.

  *Suggest:* document the exchange, and make `sid_code` required.
- **9.3 No `state`** [read]. A callback can't be tied to the sign-in that began it, so login CSRF is
  open. This app's short-lived cookie narrows it. *Suggest:* echo `state`, per OAuth 2.0.
- **9.4 Three authorize addresses** [docs, read]:
  - `paradigm.ofself.ai` in `build_oauth_url`
  - `app.ofself.ai/authorize/<app_id>` in the skill
  - `app.ofself.ai/authorize?client_id=…` in webhooks and Personas

  The page reads `client_id` and `redirect_uri`.
- **9.5 `redirect_uri` is sent to the server at approval** [read], so it can be checked against the
  registered URIs. Not tested. If it isn't checked, `sid_code` could be sent anywhere.
- **9.6 The consent page contradicts the server** [observed]. With no `work-authorization` record, the
  page said "Full Access… Reaches none of what Visa Research Desk requires". `GET /authorize/preview`
  said Full Access `fits: true`, `missing: []`. It appears to count data held, not permission.
  *Suggest:* "You have none of this yet" when the realm fits.
- **9.7 `sid_code` lands in server logs** [observed]. Uvicorn's default access log recorded it, and a
  refused callback leaves it unredeemed. This app now redacts it. *Suggest:* seconds-long expiry, or
  deliver it by POST or fragment.
- **9.8 A real grant carries the DLR's `fields`** [observed]. `effective_access` was exactly
  `nodes:read` on `work-authorization`, `fields: ["citizenships"]`, and no other records were
  readable. The grant expires in 30 days, and the guide doesn't say if that's the default.

## 10. What worked well

- **`crux validate`** resolves schemas against the registry and pushes reuse over invention.
- **`paradigm dlr preview`** shows the exact consent card before publishing.
- **Error messages are actionable,** e.g. `EP_NOT_FOUND`: "The user must complete the OAuth
  authorization flow first."
- **Sandbox users:** one command, a working `X-User-ID`, no OAuth.
- **Personas' `/api/v1/docs`** is versioned with the deployment and readable as markdown.

---

## Open questions

| Question | Raised | Put to Ofself | Answer |
| --- | --- | --- | --- |
| Does Ofself host apps; linked out or embedded? (5.1) | 09-17 | — | — |
| Does any app record a `trip` before it happens? | 09-17 | — | — |
| Direct model access behind the `ofself` provider, and who pays? (8) | 09-17 | — | — |
| Does a read return only a DLR's `fields`? (1.3, 9.8) | 09-17 | — | In the grant yes (9.8); on data, untested |
| What does `/auth/session/exchange` return, and can `sid_code` be relied on? (9.2) | 09-17 | — | — |
| Will the authorize redirect echo `state`? (9.3) | 09-17 | — | — |
| Is `redirect_uri` checked at approval? (9.5) | 09-17 | — | — |
| Is a 30-day grant expiry the default? (9.8) | 09-18 | — | — |
