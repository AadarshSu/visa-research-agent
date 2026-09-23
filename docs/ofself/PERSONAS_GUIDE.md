> **Snapshot, 2026-09-23.** Everything down to the second guide's title is `https://personas.ofself.com/api/v1/docs?format=md` as served that day. The *Personas Headless Agent API* below it is the owner's copy of 2026-09-18, and has not been re-checked.

# Integrating Your App with Personas

> A lifecycle guide for external developers building apps that talk to a Personas agent.
> It follows a request from end to end: **register → declare an agent → the agent boots → run it → consume the stream → render the result.**

---

**Base URLs**

| | |
|---|---|
| **API (prod)** | `https://personas.ofself.com` |
| **Frontend (prod)** | `https://personas.ofself.com` |
| **API base path** | all endpoints below are under `/api/v1` (e.g. `…/api/v1/internal/headless/run/stream`) |

---

**Two ways to use this guide**

It is served by the deployment it describes, so the copy you fetch always matches the
code you are calling — no cloning, no auth:

```bash
curl https://personas.ofself.com/api/v1/docs                    # the whole guide
curl https://personas.ofself.com/api/v1/docs/sections           # section slugs
curl "https://personas.ofself.com/api/v1/docs?section=register-your-app"
```

The `paradigm` CLI wraps the whole lifecycle below, so most of this is one command
rather than a hand-signed request:

```bash
paradigm personas register                       # §1 — stores the HMAC key for you
paradigm personas agent create coach --user <id> --system-prompt "..."   # §3.2
paradigm personas run coach "hello" --user <id>  # §5 — streams §6's events
paradigm personas docs --section run-the-agent-streaming
```

Read on if you are integrating directly rather than through the CLI — everything
below is what it does under the hood.

---

## 0. The mental model (read this first)

### Why not just call OpenAI?

Wrong question, and the honest answer is a bit funny: **at zero capabilities this
IS that call.** `capabilities: []` sends your system prompt and the conversation,
no platform text, no tools — your provider, your model, optionally your key. If
you only ever want a paragraph rewritten, Personas costs you nothing over calling
the vendor yourself, and buys you auth, persistence and token accounting on the
way past.

So the question is not *which one*. It is **what happens the day you want more.**

Wanting more means wanting the model to act on one person's data, and that is
four problems you would otherwise build:

| | you would have to build | Personas already has |
|---|---|---|
| **Permission** | ask the user what this agent may touch, store it, enforce it on every call | the Exposure Profile, enforced server-side in the sandbox |
| **Execution** | a sandbox that runs model-written code against their data without exfiltrating it | RestrictedPython + the `paradigm` SDK, scoped to the EP |
| **Attribution** | a ledger of what the agent did, as the agent, on whose behalf | every write carries the sub-entity and the calling app |
| **Composition** | decide what the model is told it can do, and keep that honest as the grant changes | capabilities (§4) |

**The point is that you do not choose upfront.** Adding `"graph"` to a list is a
one-field change to a call you already make — not a migration onto a different
platform. Start at the floor, move when you need to, and the integration does not
change shape underneath you.

The cost of *not* choosing is the thing to know: an agent that declares nothing
gets everything, which is **~37,000 characters** of platform instruction every
turn — artifact doctrine, sandbox rules, a pandas cookbook, markdown house style,
the full `paradigm.*` reference — whether or not it can use any of it. On a real
agent the app's own prompt is 5–15% of what the model reads. Capabilities are how
you get that back.

### The shape of it

Personas runs an **agent** on behalf of one of your users. The agent reasons with
an LLM and acts on the user's data in **Paradigm** by writing and running Python
in a sandbox. Your app never touches Paradigm directly through Personas — the
agent does, and only within the permissions (the *Exposure Profile*, "EP") the
user granted.

Four things you choose, and the rest follows:

```
call_ofself_agent(
    credential,      # your Personas HMAC key — `paradigm personas register`
    capabilities,    # what the agent is MADE OF        (§4)
    system_prompt,   # what it SAYS                     (§3.2)
    llm_config,      # which model, on whose key        (§5.1)
)
```

What the agent may **reach** is deliberately not in that list. That is the user's
EP intersected with the sub-entity's ceiling, resolved per request — see §3.
Election decides whether the agent is *told* a surface exists; the EP decides how
far it reaches. Keep those apart and the rest of this document is easy.

There are **two directions** of traffic, and one decision dominates everything:

```
  YOUR APP  ──(1) run request──▶  PERSONAS  ──▶ LLM + Paradigm sandbox
            ◀─(2) results───────            
```

**For direction (2), you choose blocking or streaming — and this is the single most common source of "why is it slow?" confusion:**

| Endpoint | Behaviour | Time to first byte | Use when |
|---|---|---|---|
| `POST /internal/headless/run` | **Blocking.** Runs the *entire* multi-step agent loop, then returns one JSON. | ~the full run (often 10–30s) | A webhook/cron caller that just needs the final answer. |
| `POST /internal/headless/run/stream` | **Streaming (SSE).** Emits events as they happen. | ~1–2s (first `scope`/`thinking`) | Anything user-facing. **This is what the Personas UI uses.** |

The agent is **exactly as fast either way** — the work is identical. The blocking endpoint just shows nothing until it's done, so a 30s run *feels* like 30s. The streaming endpoint shows thinking and partial answers within a second or two, so the same 30s run *feels* instant. **If your app feels slow, you are almost certainly on `/run` instead of `/run/stream`.**

The rest of this guide follows the streaming path.

---

## 1. Register your app (once)

Registration is open and unauthenticated. It issues a **per-app HMAC key** — your app's secret. You get it **once**; store it securely.

```bash
curl -X POST https://personas.ofself.com/api/v1/internal/headless/apps/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My Journaling App", "paradigm_client_id": "tp_your_paradigm_app_client_id"}'
```

```json
{
  "app_id": "a1b2c3d4-...",
  "name": "My Journaling App",
  "hmac_key": "sk_hdls_9f8e7d...",
  "hmac_key_prefix": "sk_hdls_9f8e7d...",
  "paradigm_client_id": "tp_your_paradigm_app_client_id",
  "message": "Store the hmac_key securely — it cannot be retrieved again."
}
```

Keep `app_id` and `hmac_key`. Every runtime call is signed with them.

### 1.1 Bind your Paradigm app (`paradigm_client_id`) — do this

If your product is ALSO a registered Paradigm app (it has its own `tp_...` client_id and
users authorize it), bind that identity to your tenant — at registration
(`"paradigm_client_id": "tp_..."` in the register body) or later:

```bash
curl -X PATCH https://personas.ofself.com/api/v1/internal/headless/apps/<app_id> \
  -H "Content-Type: application/json" -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"hmac_key": "sk_hdls_...", "paradigm_client_id": "tp_..."}'
```

Binding buys you two things, both enforced Paradigm-side from the HMAC-verified tenant
identity (never a spoofable per-request field):

1. **Capping** — every agent your app runs is capped to *(its own EP) ∩ (the user's grant
   to YOUR app)*, scope-aware. An agent can never do more than the user allowed your app.
2. **EP delegation (no-handshake provisioning)** — if the user has authorized **your app**
   but never Personas, Paradigm roots the agent's sub-entity EP in *your app's* grant.
   The §3.3 handshake then never fires for your users: consent they already gave your
   app carries the agent.

Unbound tenants (`paradigm_client_id: null`) get neither: agents derive only from the
user's Personas grant, and users who never authorized Personas hit the handshake.

> **`paradigm_client_id` (recommended) — your OWN Paradigm app's client id.** Setting it caps your agents by *your* app's per-user grant, not just Personas' (see §3). Omit it and your agents fall back to Personas' ceiling alone. You can set it later with `PATCH /internal/headless/apps/<app_id>` (`{hmac_key, paradigm_client_id}`). Prerequisite: register a Paradigm app and have your users authorize it.

### 1.2 Give the agent your own tools (optional)

Beyond `execute_code`, an app can register **its own HTTP endpoints as tools** the
agent may call. Personas proxies the call for you: the agent picks the tool, Personas
hits your URL, and the response comes back into the agent's reasoning.

```bash
curl -X PUT https://personas.ofself.com/api/v1/internal/headless/apps/<app_id>/tools \
  -H "Content-Type: application/json" \
  -d '{"hmac_key": "sk_hdls_...", "tools": [
        {"tool_name": "lookup_order",
         "description": "Look up an order by id.",
         "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}},
         "endpoint_url": "https://api.yourapp.com/orders/lookup",
         "http_method": "POST",
         "static_headers": {"X-Env": "prod"},
         "secret_id": "<from the secrets route below>"}]}'
```

`PUT` **replaces the whole set** — a tool you omit is deleted. Amend one with
`PATCH /apps/<app_id>/tools/<tool_name>`, remove one with `DELETE` on the same path.
`parameters` is a JSON-Schema object; it is what the model sees when deciding whether
to call your tool, so describe it as carefully as you would a prompt.

**Never put a credential in `static_headers`** — that field is stored and returned in
plain text by `GET /apps/<app_id>`. Register the credential as a secret instead and
reference it by id:

```bash
curl -X POST https://personas.ofself.com/api/v1/internal/headless/apps/<app_id>/secrets \
  -H "Content-Type: application/json" \
  -d '{"hmac_key": "sk_hdls_...", "label": "Orders API key",
       "header_name": "Authorization", "header_value": "Bearer abc123"}'
```

It returns a `secret_id`. The value is **encrypted at rest and never returned again**;
Personas injects it as `header_name` when it calls your endpoint. Rotate by POSTing a
new one and re-pointing the tool. `DELETE /apps/<app_id>/secrets/<secret_id>` removes
it and nulls the `secret_id` on any tool still referencing it — those tools keep
working, unauthenticated, so re-point them **before** you delete.

> **`renders_node_refs` — accepted, but not yet active.** The registration endpoint
> takes this field and currently ignores it: the backing column is not live yet, so it
> is stored nowhere and changes nothing. It is the future opt-in for agents citing
> graph nodes inline as pressable pills. Setting it today is harmless and has no
> effect; there is also no way to change it later, since `PATCH /apps/<app_id>`
> accepts only `name` and `paradigm_client_id`. Don't build against it yet.

---

## 2. Authenticate every runtime request

All runtime endpoints use **per-app HMAC signing**. Each request must carry:

- Body field `app_id` — your UUID from step 1
- Body field `hmac_key` — your `sk_hdls_...` key from step 1
- Header `X-Internal-Signature: sha256=<hmac_sha256(raw_request_body, hmac_key)>`

The signature is computed over the **exact raw bytes** of the JSON body you send — serialize once, sign those bytes, send those bytes. (Re-serializing after signing will change the bytes and fail verification.)

```python
import hashlib, hmac, json

def sign_body(raw_body: bytes, hmac_key: str) -> str:
    digest = hmac.new(hmac_key.encode(), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"

payload = {"app_id": APP_ID, "hmac_key": HMAC_KEY, "paradigm_user_id": USER_ID, "message": "..."}
raw = json.dumps(payload).encode()          # serialize ONCE
headers = {"Content-Type": "application/json", "X-Internal-Signature": sign_body(raw, HMAC_KEY)}
# ...send `raw` as the body, not a re-serialized dict
```

A bad/missing signature returns `401 UNAUTHORIZED`.

**Two auth tiers — don't sign the wrong one.** The signature above is required by the
**runtime** routes: running an agent, creating/updating agents, conversations,
artifacts, context, automations.

The **app-management** routes are different. `PATCH`/`GET /apps/<app_id>`, the tool
routes and the secret routes (§1, §11) authenticate on the **bare `hmac_key` in the
body alone** — they do not verify `X-Internal-Signature`, and sending one is harmless
but pointless. Two consequences worth knowing:

- These calls are **strictly server-side**. The raw key travels in the body, so a
  request you could safely make from a signed backend is one you must never make from
  a browser or a mobile client.
- `GET /apps/<app_id>` also accepts the key as a **`?hmac_key=` query parameter**.
  Prefer the body: query strings end up in access logs, proxy logs and browser
  history, and this one is your app's long-lived secret.

---

## 3. The identity & permission model (read before declaring an agent)

This is the part most integrations get wrong, so be precise about who is who:

- **Personas holds the API key; your app brings its own Paradigm identity.** Personas is a registered Paradigm app (it holds the Paradigm API key). Your app should ALSO be its own registered Paradigm app — you tell Personas its `client_id` via `paradigm_client_id` at registration (§1). Agents you drive are then capped by **both** grants (below). If you skip `paradigm_client_id`, your app is a pure Personas tenant and agents run under Personas' ceiling alone.
- **Each agent is a Paradigm sub-entity** under Personas, keyed by its slug (`sub_entity_key`, derived from `agent_name`).
- **Agents are owned by the app that created them.** Every runtime operation that names an agent by `agent_id` — fetch, run, update, delete — is scoped to your HMAC-authenticated `app_id`: an `agent_id` that belongs to a *different* app returns `404 NOT_FOUND`, exactly as if it didn't exist. Agents a user created directly in the Personas UI (owned by the user, not an app) are likewise not reachable over the app API. You never borrow or operate another app's agents.
- **The user grants access to the agent, once,** via a Paradigm authorization page (§3.3). That grant gives the agent a **privacy realm** + an Exposure Profile (EP). If you set `paradigm_client_id`, the user must **also** have authorized *your* Paradigm app (a one-time consent), or runtime calls fail `403 CALLING_APP_NOT_AUTHORIZED`.
- **`consent` is the agent's ceiling.** At creation you may pass a `consent` blob that caps what the agent can ever do, *within* what the user's realm grant allows.

> **On `client_id` (updated model):** the calling-app identity is now bound to the `paradigm_client_id` on your **registration record**, NOT a per-request field. Personas sends it as `X-Calling-App-Client-Id` on every agent call, so an agent's data access is the intersection **`agent EP ∩ Personas' base EP ∩ your app's per-user EP`** — enforced by scope (schemas/nodes), not just verbs. An agent can never reach data your app itself isn't authorized for. A per-request `client_id` body field is **ignored** (it used to be a soft guard against Personas' own id — that check was removed). If `paradigm_client_id` is unset, the intersection degrades to `agent EP ∩ Personas' base EP`.
>
> *(`403 AGENT_EXCEEDS_CALLING_APP` on declare / `403 CALLING_APP_NOT_AUTHORIZED` at runtime both come from this intersection. The exact math is enforced inside Paradigm.)*

### 3.1 The `consent` blob (the agent's permission ceiling)

`consent` is optional. Omit it and the agent uses whatever the user's realm authorization grants. Provide it to **narrow** the agent below that grant. Its canonical shape:

```
{ <resource>: { <verb>: { "schemas": { <schema_id>: {"fields": [...], "filter": {...}} },
                          "nodes":   [<node_id>, ...] } } }
```

- **resources:** `nodes`, `relationships`, `plugins` (the resources an agent typically narrows). `discovery`, `activity`, `automations` and `sub_entity` are also valid, but are rarely part of an agent's consent ceiling.
- **node verbs — six of them:** `read`, `create`, `edit`, `delete`, `propose`, `modify`. `modify` is not a synonym for `edit`: it is the broader verb that satisfies **both** `edit` and `delete`, so an agent holding `modify` can do either. Grant `edit` alone if you do not want deletes.
- `edit_content` is a **seventh name you will see** but not a seventh grant: it appears in an app's DLR and folds to `edit` at check time. Write `edit` in a consent blob.
- `schemas` scopes the verb to specific schema ids (and optionally specific `fields` / a `filter`); `nodes` scopes it to specific node ids. Empty/omitted inner objects mean "all in realm."

Example — an agent that may read and propose changes to one schema:

```json
{
  "nodes": {
    "read":    { "schemas": { "journal_entry": { "fields": [], "filter": {} } } },
    "propose": { "schemas": { "journal_entry": {} } }
  }
}
```

> **Where do the schema ids come from?** They are **not** in this doc — they belong to the user's Paradigm data and your app's declared DLR (Data Lender Request). Get them from the Paradigm side: the `paradigm schema list/search` CLI, your app's DLR on the app record (`paradigm dlr show`), or at runtime via `paradigm.list_schemas()`/`get_schema()`. **If you don't have specific schema ids, omit `consent` entirely** — the agent then inherits the full realm grant, which is the right default for most apps.

### 3.2 Create (or fetch) the agent

You can let `/run/stream` auto-create the agent on first call (pass `agent_name`), but pre-creating is cleaner because it returns a stable `agent_id`:

```
POST /internal/headless/agents
```

| Field | Required | Meaning |
|---|---|---|
| `app_id`, `hmac_key` | ✅ | Auth (§2). |
| `paradigm_user_id` | ✅ | The user the agent acts for. |
| `agent_name` | ✅ | Stable name. Slugified into the agent's `sub_entity_key` — the slug **is** the key. If you also declare a roster, this must match its `key`; see §3.5 for the exact rule and the collision case. |
| `system_prompt` | ✅ | **Required.** The agent's identity/instructions, stored permanently. Creation fails with `VALIDATION_ERROR` without it. |
| `app_name` | — | Your app's display name (shown in the user's data console). |
| `description` | — | Human description. |
| `consent` | — | Permission ceiling (§3.1). |
| `llm_provider` | — | Default `"ofself"`. |
| `llm_model` | — | Default `"gpt-5.5"`. |
| `temperature` | — | **Has no effect.** Stored on the agent and never sent to a provider — it is in the kwargs of neither, on none of the four chat paths. Accepted here for backward compatibility; `llm_config` (§5.1) refuses it outright rather than repeat the lie. |
| `web_search` | — | Boolean → the agent's `tools_config`. Prefer electing the `web.search` capability (§4). `wikipedia_search` is **gone** — it was ungated where its sibling was gated, and advertised to agents with no internet capability at all. |

**Response:**

```json
{ "agent_id": "…", "agent_name": "My Coach", "created": true }
```

It's idempotent on `(user, agent_name)`: a second call returns the existing agent with `"created": false`.

**What a second creation call will and won't change.** Re-POSTing here never rewrites the stored `system_prompt`, `tools_config`, `consent` or `temperature` — those take effect only on the call that actually creates the agent (and `temperature` takes effect nowhere — see its row above). `llm_provider` / `llm_model` are the exception: any call carrying them **updates the stored agent** (see §5's caution — a one-off model override silently becomes permanent).

**To change an agent afterwards, use the dedicated update route** — creation-time immutability is not permanent immutability:

```
PATCH /internal/headless/agents/<agent_id>
```

Body `{app_id, hmac_key, paradigm_user_id, ...}`. It updates `system_prompt`, `llm_provider`, `llm_model` and `temperature` on the stored agent — though `temperature` changes nothing about a run, since it reaches no provider. `tools_config` and `consent` are **not** editable here: tools are fixed at creation, and re-narrowing an agent's ceiling means re-declaring its sub-entity, not patching a row. For a single turn without persisting anything, pass a per-request `system_prompt` on the run instead (§5).

### 3.3 The one-time authorization handshake

> **Auth is once per user, not once per agent — and a bound tenant may never pay it at all.** A Personas agent is a Paradigm *sub-entity* that inherits realm + grant from a **base authorization**: the user's grant to Personas, **or — via EP delegation — the user's grant to your bound Paradigm app** (§1.1). If either exists, agents provision silently and `/run` streams immediately. The handshake below fires only when **neither** grant exists. There is still **no API to pass/forge an EP** — delegation works precisely because the user *did* consent, to your app; the agent runs within that grant, never beyond it.
>
> *(Passing `calling_app_client_id` does **not** skip auth — it **narrows** the agent to the intersection with a second already-authorized app's grant, and errors `CALLING_APP_NOT_AUTHORIZED` if that app isn't authorized. Don't use it to avoid the handshake.)*

> **What makes provisioning "silent" — and what quietly breaks it.** Declaring an agent calls
> Paradigm's `declare_sub_entity`, which requires **`sub_entity:declare`** — a permission that
> must be (a) in **Personas' own Paradigm app DLR** and (b) **granted by the user** when they
> authorized Personas. If a user's authorization predates that permission, declaration fails
> (`403`, surfaced as an EP re-authorization prompt) and the agent can't provision until they
> **re-authorize**. Similarly, an agent's realm can never exceed the user's Personas grant:
> assigning a broad realm (e.g. *Full Access*) to an agent errors `EXCEEDS_BASE_AUTHORIZATION`
> unless the user actually granted Personas those verbs (`discovery:groups`, `automations`, …).
> Your app manages none of this — but it's why a user occasionally has to re-authorize even
> though "auth is once per user."

The handshake below only fires for a user who has **neither authorized the Personas app nor (for bound tenants, §1.1) your own Paradigm app** — no base EP exists anywhere to derive from. In that case the sub-entity declaration can't complete, the agent is created **realm-less**, and the next run returns a **JSON body (not an SSE stream)**:

```json
{
  "requires_realm_assignment": true,
  "agent_id": "…",
  "redirect_url": "https://<paradigm-frontend>/authorize?client_id=<personas>&sub_entity_key=<slug>&display_name=<name>&redirect_uri=<personas_callback>",
  "message": "Authorize this automation agent once, then retry execution."
}
```

**You must handle this branch** — until it's resolved, no conversation starts and no stream opens. The flow:

1. Detect it: when you POST to `/run/stream`, check whether the response is JSON (vs `text/event-stream`); if `requires_realm_assignment` is set, don't try to parse SSE.
2. Redirect the user to `redirect_url` (Paradigm's authorization page). Note the `client_id` there is **Personas'**, confirming the user is authorizing the agent-under-Personas.
3. To bring the user back to your app afterward, pass `return_to` in your `/run` body — Personas embeds it in the `redirect_url` so Paradigm's callback returns to your URL.
4. After approval, retry the same `/run/stream` call — it now streams normally.

---

### 3.4 Agent modes — read, ask, act

One agent, three ceilings. A person talking to your agent about their own data
should be able to choose how much it may do, and that choice has to be a **ceiling,
not an instruction**. A prompt saying "ask before you rewrite" is a promise the model
can break; a mode is a real permission ceiling the platform enforces.

| Mode | `mode` value | The agent may | It may not |
|---|---|---|---|
| **Act** | omit the field | Read, create, edit, delete, run plugins | — |
| **Ask** | `"propose"` | Read, and **propose** changes you approve one by one | Write directly; run plugins |
| **Read** | `"read"` | Read only | Write, propose, run plugins |

**Read is deliberately not the same as ask.** A proposal writes a row into the
person's approval queue and asks for their attention — small, but not nothing. Read
promises their **queue** stays empty; ask promises their **data** doesn't change
without a press. Someone exploring a graph they don't own wants the first.

**Ask mode does not need `propose` in your DLR.** If your app holds any write verb,
ask mode converts exactly those verbs into proposable ones. It cannot widen you: a
create-only app in ask mode still cannot propose a delete.

**Plugins are withheld below act mode, not deferred.** There is no plugin-execution
proposal type, so a plugin call can't degrade into a question. In read or ask mode
`paradigm.execute_plugin(...)` fails.

Pass it per run:

```json
{ "agent_name": "coach", "message": "tidy up my notes", "mode": "read" }
```

Three things to know about how it behaves:

- **Personas validates nothing.** A mode only ever narrows, so the worst a caller can
  do is give itself less. Paradigm enforces it. An unrecognised value is **ignored**
  (you get act mode), not rejected — so typo-check your own input.
- **The agent is told which mode it's in, every turn**, so it says "I can only read
  right now" instead of attempting a write and handing your user a 403.
- **The `scope` event echoes the mode** that actually applied (§6), so your UI can
  show it and a transcript can be read back knowing which ceiling was in force.

> **You are expected to build the control.** In read mode the agent is instructed to
> tell users they can change the mode "with the control beside the message box" — so
> if you offer modes at all, put a visible switch near your composer. Without one,
> the agent refers to something that doesn't exist. Offering no control and never
> sending `mode` is also fine: the agent then runs in act mode and never mentions it.

### 3.5 Declaring your roster in Paradigm (`agents.yaml`)

Everything above declares an agent **at runtime**, by calling Personas. You can also
declare the agents your app offers **at build time**, in a file in your repo, pushed to
your Paradigm app record:

```bash
paradigm agents init          # scaffold agents.yaml
paradigm agents declare       # push it (--check validates locally, pushes nothing)
paradigm agents list          # the roster as Paradigm actually holds it
```

```yaml
agents:
  - key: reflections-partner
    display_name: Reflection Assistant
    description: Reads what you are writing and thinks with you about it.
    default: true
    consent: inherit
```

**This is optional.** An app that never declares a roster works exactly as described
above; its agents are simply marked `undeclared`, which is the common case. Note the
credential differs from everything else in this guide: `paradigm agents` authenticates
as **you, the developer**, with your Paradigm PAT — not with your app's Personas HMAC
key.

**What declaring buys you.** Each agent is a named subset of your app's own DLR, so
the platform can check the chain at push time:

```
agent consent  ⊆  app DLR  ⊆  what the user granted
```

The left link is verified when you push. An agent asking for a verb your app was never
granted fails in CI, rather than on a user's consent screen. You also get a real
picker: `display_name`, `description` and the derived mode list (§3.4) come back from
the roster, so a person choosing an agent sees what it is and what it may do.

**`consent` is required, and its two extremes are both meaningful:**

| Value | Means |
|---|---|
| `inherit` | This agent carries the app's **whole** grant. |
| `{}` | This agent has **no** access to the graph at all — a plain model. |
| *omitted* | An **error**, deliberately. An omission is not a decision, and a field whose whole job is narrowing must never widen by accident. |

> **⚠ The `key` is the join between two services — get it wrong and nothing lines up.**
> An agent has two records: Personas holds its behaviour, Paradigm holds its
> permissions. Personas derives the link from `agent_name` by **slugifying** it —
> lowercase, every run of non-alphanumeric characters becomes a single `-`, leading
> and trailing `-` stripped, truncated to 100 characters. That slug **is** the
> `sub_entity_key`, and your `agents.yaml` `key` must equal it exactly.
>
> So `agent_name: "Reflection Assistant"` produces `reflection-assistant`. If your
> file says anything else, the halves come apart in a way that looks like three
> separate bugs: the picker lists an agent nothing runs, the ceiling is attached to an
> agent nobody uses, and the one actually running shows up as `undeclared`.
>
> **One collision case to watch.** Slugs are unique per user, so if that user already
> has an agent on `coach`, the next one named "Coach" silently becomes `coach-2` — and
> no longer matches a roster key of `coach`. Keep agent names distinct per user, or
> pre-create agents (§3.2) and check the returned slug.

---

## 3.6 The same lifecycle from the terminal (`paradigm`)

Everything above has a CLI equivalent, and for building and debugging it is
usually faster. The full reference is `paradigm_sdk/CLAUDE.md`; what matters here
is **which credential each namespace uses**, because that is what the split is
for:

| namespace | talks to | with |
|---|---|---|
| `paradigm agents …` | **Paradigm** | your developer PAT (`~/.paradigm/credentials.toml`) |
| `paradigm personas …` | **Personas** | this app's HMAC key (`.paradigm/secrets.toml`) |

### Register the app with Personas — once

```bash
paradigm personas register              # → app_id + hmac_key, stored + gitignored
paradigm personas status                # registered? bound? which host?
```

**Binding matters.** `register` sends this project's `[app].client_id` as
`paradigm_client_id`. A bound tenant gets agents capped by the user's grant to
*your* app, and its already-authorized users skip the one-time handshake (§3.3).
An unbound one gets neither, and registering while unbound is now refused rather
than warned — `--unbound` is the deliberate way through. `paradigm doctor` reports
the state.

The host resolves env → secrets → default: `PARADIGM_PERSONAS_BASE`, then
`[personas].base_url`, then `https://personas.ofself.com`. **Never hardcode it** —
and note that both `paradigm login` and `paradigm personas register` default to
**prod**, so local work needs `--api-base http://localhost:5001` and
`--base-url http://localhost:5050` respectively. Registering a local app against
prod Personas fails as *"App not found"*, which reads like a problem with the app
rather than with the host.

### The agent's identity and ceiling — Paradigm side

An agent is a **sub-entity**: an ExposureProfileGrant per (app, user), with a verb
ceiling of its own. The chain is `agent consent ⊆ app DLR ⊆ user grant`.

```bash
paradigm agents list                    # the agents this app declared for you
paradigm agents show <key>              # ceiling / consent / effective — all three
paradigm agents declare <key>           # create one (acts as THE APP — needs an app key)
paradigm agents update <key>            # change what it may do, in place
paradigm agents expandable <key>        # what it is missing that its app now holds
paradigm agents sync <key> [--all]      # raise its consent to that
paradigm agents revoke <key>            # withdraw access (soft — the row survives)
```

`show` prints **three** values because they disagree by design: `ceiling` (the
most it may ever hold), `consent` (what it holds now, stable across realm edits)
and `effective` (what it can do right now, once the user's realm has had its say).
A read-only realm makes a write-capable agent read-only at runtime while its
consent still says write — both are true, and printing one is being wrong about
the other.

`declare` is the one command that acts as **the app** rather than as you, so it
needs `paradigm app key create` first. Naming an app by `client_id` proves nothing
about controlling it, and a PAT path there would let anyone declare an agent on
anyone's app.

### The roster — what your app OFFERS

```bash
paradigm agents roster init             # scaffold a roster file
paradigm agents roster push --check     # validate locally, push nothing
paradigm agents roster push             # push it
paradigm agents roster show             # what Paradigm holds
```

The roster is a field on the app record (`declared_agents`); a YAML file is only
how you author it, so `--file` takes any path and the name is never stored.
Pushing **replaces** the roster — an agent dropped from the file stops being
offered, though it does not revoke an EP a user already granted.

`consent: inherit` means the app's whole grant; `consent: {}` means **no graph
access at all**; omitting `consent` is an **error**, because inheriting
everything is the widest reading of an omission and this field exists to narrow.

### What the agent SAYS — Personas side

```bash
paradigm personas agent create <name> --user <id> --system-prompt "..."
paradigm personas agent list --user <id>     # `authorized: NO` → needs §3.3
paradigm personas agent show <agent-id> --user <id>
paradigm personas run <agent> "message" --user <id> [--conversation <id>]
```

**`--user` should be you, or a test user** (`paradigm app test-users create`) —
never one of your real end users. The CLI is a developer tool: you are still
authenticated as the APP here, and `--user` only says whose graph the agent is
created against. In production nothing runs these commands — your app calls
`/internal/headless/agents` per person as they arrive (§3.2).

It is not optional, though, and that is structural rather than a CLI choice: a
Personas agent has a non-null `user_id` with `UNIQUE(user_id, slug)`. There is no
userless agent to create. What the flag decides is *whose*, and from a terminal
the only right answers are yourself and a sandbox user.

There is no `--group-id` on any of these, for the same reason. An agent CAN act on
a group's graph — `group_id` is a run-body field and the runner passes it through
— but a group agent is made by an app serving that group's members at runtime, not
by a developer naming a group at a prompt.

Three that bite: `--system-prompt` is required at creation and **locked
afterwards**; `--model` on a run **persists onto the agent** rather than applying
once; and an unauthorized user makes `/run/stream` answer **JSON, not SSE**.

---

## 4. Capabilities — what your agent is made of

Personas assembles the agent's system prompt and tool list **fresh every turn**
from the capabilities the agent elected. You do not write that assembly; you
choose what goes into it.

**The rule:** a capability contributes its own prompt fragments, its own sandbox
globals and its own tools when elected, and **none of them** when not. Elect
nothing and the agent is a plain LLM call.

### 4.1 The tree

Capabilities nest, because most of them *are* functions inside the sandbox.
`save_artifact` is a sandbox global — remove code execution and artifacts do not
get smaller, they lose their body. **Electing a child elects its parents.**

```
system_prompt                        ← yours. The floor everything attaches to.
│
├─ code.execute                      the execute_code tool + the sandbox
│  ├─ artifacts                      save / get / preview / list_artifact
│  ├─ dataframes                     the pandas cookbook (95 lines)
│  ├─ web.search                     web_search
│  └─ graph                          paradigm.* — nodes, schemas, relationships
│     ├─ files                       paradigm.download_file (user uploads)
│     ├─ graph.propose               create / update / list_proposal
│     ├─ plugins                     list / get / execute_plugin
│     ├─ automations                 list / trigger / status / runs — AND flows
│     │                               (chained automations, a.k.a. a canvas)
│     ├─ citations                   {{title|id|schema}} pills      ⟨app flag⟩
│     └─ node_cards                  ```widget:node cards           ⟨app flag⟩
│
├─ formatting                        markdown house style
│  └─ choices                        ```widget:choice               ⟨app flag⟩
│
├─ conduct                           platform voice ("be concise", "finish
│                                    autonomously") — default OFF is defensible
│
└─ identity                          who the agent acts for — the one profile
                                     face Paradigm resolves for your grant:
                                     display_name and @username, from
                                     /me/contexts. The profile node is never
                                     read. Pure prompt; one lookup per turn.
```

Two edges cross the tree:

- `query_nodes(..., artifact_name=…)` reads from **graph** and writes to
  **artifacts**, so it needs both.
- `citations` and `node_cards` sit under `graph` but are also gated on the **app
  record**, because they are claims about what your surface can draw. An embedder
  that cannot render the token prints raw braces, which is worse than not citing.

⟨app flag⟩ means exactly that: electing it is necessary and not sufficient.

### 4.2 What each one costs

Characters the model reads, per turn, before your prompt and the conversation:

| elected | system (platform) | tool schema | tools |
|---|---|---|---|
| *nothing set — the legacy default* | 20,371 | 16,915 | 1 |
| `graph`, `graph.propose`, `formatting`, `citations` | 11,569 | 10,074 | 1 |
| `graph`, `artifacts`, `dataframes` | 16,925 | 6,345 | 1 |
| `graph`, `formatting` | 11,569 | 4,955 | 1 |
| `code.execute`, `web.search`, `artifacts`, `formatting` | 8,480 | 2,611 | 1 |
| `[]` | **0** | **0** | **0** |

Those are three different places in the request:

```jsonc
{
  "messages": [
    { "role": "system", "content": "<platform fragments> + <YOUR system_prompt>" },
    { "role": "user",   "content": "…" }
  ],
  "tools": [                                   // ← "tools" column: the count
    { "name": "execute_code",
      "description": "<the tool schema column>",
      "parameters": { … } }
  ]
}
```

`execute_code` is the **only** tool there is. Every other capability is a
function inside it — which is why not electing `code.execute` returns an empty
`tools` array rather than a smaller one.

### 4.3 Declaring them

```jsonc
// at creation — POST /internal/headless/agents
{ "capabilities": ["code.execute", "graph", "artifacts"] }

// per run — /internal/headless/run | invoke | run/stream | invoke/stream
{ "capabilities": ["graph"] }        // narrows THIS run only
```

- **Omitting the field means "do not touch."** A client that has never heard of
  capabilities cannot strip an agent by updating its name.
- **`null` ≠ `[]`.** `null` is "never elected" and resolves to *everything* —
  every agent created before capabilities existed. `[]` is "elected nothing" and
  is the floor. Collapsing them would either break every existing agent or make
  the floor unreachable.
- **A run may narrow, never widen.** `run ⊆ agent ⊆ app`. Asking for more than
  the agent holds is `403 CAPABILITY_EXCEEDS_AGENT`; more than the app declared
  is `403 CAPABILITY_EXCEEDS_APP`.
- **Stored closed.** Electing `artifacts` records `code.execute` too, so reading
  the column tells you what the agent has without knowing the tree.

### 4.4 What the agent is actually told

The dynamic part is the **Data Access Context**, derived from the live EP:

```
--- Paradigm Data Access Context ---

Nodes: read, view history, create
Schema catalogue: list and inspect any schema definition (this is not data access)
Code execution: available (sandboxed Python)

Data scope:
  • nodes limited to 5 schema(s)

Only call tools listed in your available tools. Operations outside your grant will be rejected.
--- End Paradigm Context ---
```

Two things that are **no longer** in the prompt, and were until recently:

- **Schema definitions.** Personas used to fetch every schema and paste up to
  twenty full `json_schema` bodies in, every turn, truncated silently at twenty.
  It does not any more — the agent calls `paradigm.get_schema_by_name()` in the
  sandbox when it needs one. If your agent was leaning on them being free, this
  is the one behavioural change to test.
- **A promise about PDFs.** It said *"For PDFs, extracted text is included when
  possible"*, which told the model to expect a transcript. PDFs now arrive as
  documents — see §5.2.
- **A state machine block.** Removed, along with the `set_state` tool.

Note the deliberate distinction in that block: the **schema catalogue** (which
schemas exist) is gated by visibility, not by the EP; **data scope** (whose nodes
you may touch) is the EP. Knowing a `belief` schema exists reveals nothing about a
person; reading their beliefs does.

Capabilities are not the permission system. **The EP still decides what the agent
can reach** — if it is empty or deactivated the agent can do nothing, and an agent
that "sees 0 schemas" is almost always a broken EP rather than a Personas bug.

### 4.5 What de-electing actually removes — and how it fails

**Nothing is disabled. The agent is simply not told.** The `paradigm.*` bridge in
the sandbox is not capability-gated; election decides what goes into the prompt
and the tool description. So de-electing a capability does not make its functions
raise — it makes the model unaware they exist, and a model that does not know
about `create_automation_flow` never calls it.

That matters because of how it fails:

| | a permission failure | a de-elected capability |
|---|---|---|
| the agent tries and | is refused by the EP | never tries |
| you see | an error, a log line, a 403 | **nothing** |
| you notice | immediately | weeks later, "it used to do that" |

There is no error to grep for. If an agent quietly stops doing something it used
to do, **check its election before anything else** — that is the one failure on
this platform with no symptom other than absence.

**Two capabilities carry more than their name suggests.** Read the tree in §4.1
as a list of *surfaces*, not of functions:

- **`automations`** carries **flows** — chained automations, what the UI calls a
  canvas. An agent without it is never told that chaining exists, so it will
  build a single automation, or nothing, where it would previously have wired a
  flow.
- **`graph`** carries `files`, `graph.propose`, `plugins`, `automations`,
  `citations` and `node_cards` as children, but **a parent does not elect its
  children** — `["graph"]` gets you nodes and schemas and none of those. Only the
  reverse closes: electing a child elects its parents, because a child is a
  function inside the parent's sandbox.

**And the converse of §4.4's warning.** That section says capabilities are not
the permission system. The reverse is equally true: **permission is not
capability.** An agent can hold a perfectly valid EP for automations, with every
verb granted, and still never touch one — because nothing in its prompt said
they were there. A grant you can see in the portal is not a behaviour you will
see in the product.

---

## 5. Run the agent (streaming)

```
POST /internal/headless/run/stream
Content-Type: application/json
X-Internal-Signature: sha256=<...>
```

### Request body

| Field | Required | Notes |
|---|---|---|
| `app_id`, `hmac_key` | ✅ | Auth (see §2). |
| `paradigm_user_id` | ✅ | The Paradigm user the agent acts for. |
| `message` | ✅ | The user's prompt / instruction. |
| `app_name` | ✅ | Your app's display name. |
| `agent_id` *or* `agent_name` | ✅ | Identify the agent. `agent_name` auto-creates/reuses (and then `system_prompt` is required — see below). |
| `conversation_id` | — | Omit to start a new thread; pass to **continue** one (see §9). |
| `conversation_title` | — | Title for a new conversation. |
| `mode` | — | `"read"` or `"propose"` (ask). Omit for act mode. A **permission ceiling** for this run, enforced by Paradigm — see §3.4. Unknown values are ignored. |
| `group_id` | — | Run the agent against a **group's** graph rather than the user's own. The agent's key is namespaced per group, and Paradigm re-checks membership regardless of what you send. |
| `system_prompt` | — | **Per-request override** of the agent's instructions (single turn). **Required** if this call auto-creates the agent. The strongest lever for steering output shape. |
| `consent` | — | Permission ceiling (§3.1), applied only when the agent is created on this call. |
| `llm_provider` / `llm_model` | — | Defaults `ofself` / `gpt-5.5`. **Caution:** these are NOT creation-only — if passed on any run they are **persisted onto the agent** when they differ from what is stored. Omit them to keep the agent's config, or use `llm_config` (§5.1), which does not persist. |
| `temperature` | — | **Has no effect anywhere.** See the creation table above. |
| `capabilities` | — | **What the agent is made of** (§4). A list narrows THIS run; omit to use the agent's own election. Cannot widen past the agent, or the app. |
| `llm_config` | — | **Which model, on whose key** (§5.1). Supersedes `llm_provider`/`llm_model`/`temperature` and does not persist onto the agent. |
| `web_search` | — | Boolean → agent `tools_config`, at creation. Prefer electing the `web.search` capability. |
| `return_to` | — | URL to send the user back to after the authorization handshake (§3.3). |
| `client_id` | — | **Ignored** (a per-request `client_id` is no longer read). Your app's Paradigm identity is the `paradigm_client_id` on your registration record (§1, §3), not a run-body field. |
| `artifact_ids` | — | Pin existing artifacts into context. |
| `timezone` | — | IANA zone (`"America/New_York"`) the person is in — what "today" means in the prompt's date line. Omit and it falls through to the Paradigm user's stored zone when `identity` is elected (same call, no extra cost), else UTC. Unvalidated; junk falls through too. |
| `callback_url` | — | Optional completion callback. |
| `debug` | — | `true` adds `debug` events (raw request/response summaries). |

### 5.1 `llm_config` — which model, and on whose key

```jsonc
{
  "provider":       "openai",           // an ALLOWLISTED NAME, never a URL
  "model":          "gpt-5.5",
  "api_key":        "sk-…",             // BRING YOUR OWN KEY. Omit → the ofself account
  "context_window": 200000,             // REQUIRED with a key on an unlisted model
  "max_tokens":     8192,

  // How the model should ANSWER, and how hard it should THINK. One shape in,
  // translated per provider on the way out — you should not have to know which
  // vendor you are talking to.
  "response_format": { "type": "json_object" },
  "reasoning":       { "effort": "high" }      // or { "budget_tokens": 8192 }
}
```

| field | OpenAI | Anthropic |
|---|---|---|
| `reasoning.effort` | `reasoning_effort` | `thinking: {enabled, budget_tokens}`, `max_tokens` raised above it |
| `reasoning.budget_tokens` | mapped to the nearest effort | used directly |
| `response_format` | native | **refused — `400 RESPONSE_FORMAT_UNSUPPORTED`** |
| `max_tokens` | `max_completion_tokens` | `max_tokens` |

`response_format` on Anthropic fails **at validation, before the run starts**,
rather than warning and proceeding. An app asking for a schema is about to parse
the answer; letting the call through returns prose that breaks `json.loads()`
somewhere downstream, at a point that says nothing about the cause — which is
the exact failure the field exists to remove. The error names the way forward
(use an OpenAI model, or ask for JSON in the prompt and parse defensively).

**`temperature` is gone**, and is refused with a reason rather than ignored. It
was accepted here, stored on the agent and documented — and put into the kwargs
of neither provider, on none of the four chat paths. It had never reached a
model. A setting that silently does nothing is worse than an absent one: it
reads as a lever someone already pulled.

Omit `api_key` and nothing changes: the run is on the ofself account and billed as
it is today. Send one and the call is yours — your provider, your quota, your
rate limits.

**Four rules a key brings with it.**

**1. The provider is a name, not a URL.** `base_url`, `azure_endpoint` and
`api_base` are refused by name. This endpoint carries a person's identity graph,
so a caller-supplied host is not "someone pinged an internal service" — it is
that, with their data in hand. Unknown fields are refused rather than ignored,
because a silently dropped field reads as accepted to whoever sent it.

**2. `context_window` is mandatory for a model we do not know.** Personas
compacts a conversation by comparing the last turn's *real* `input_tokens`
against the model's window. For a model the registry has never listed that falls
back to a default: a 1M-context model would compact at ~90k for no reason, and a
smaller one would overflow into a provider-side error instead of compacting. So a
key plus an unlisted model without a declared window is
`400 CONTEXT_WINDOW_REQUIRED` rather than a quiet wrong answer. A declared window
beats the registry — you know your model and we do not.

**3. The key is never logged, echoed, or returned.** Anything reporting config
reports it as `<redacted:N chars>` — the length is kept so "no key was sent" and
"a key was sent and hidden" stay distinguishable, which is the whole of whether a
run was billed to you or to us.

**4. Your key, your failures.** A 401 or a rate limit from your provider is
surfaced as your provider's error, not rewritten as a Personas one. It is your
account to fix and we would only send you to the wrong place.

Token usage is reported either way — `input_tokens`/`output_tokens` land on the
assistant message as they always have. What changes is who pays, not whether the
numbers exist.

### Response

An SSE stream (`Content-Type: text/event-stream`). The server emits a `: heartbeat` comment during long silences to keep proxies from dropping the connection — ignore lines starting with `:`.

---

### 5.2 Attachments — images and PDFs reach the model directly

`artifact_ids` on a run pins existing artifacts into the turn. What happens next
depends on what they are:

| attachment | how it reaches the model |
|---|---|
| **image** (`image/*`) | an image block — the model sees the pixels |
| **PDF** (`application/pdf`) | a **document block** — the model sees the pages |
| anything else | inlined as text above your message |

**A PDF is no longer a transcript.** It used to take the third row: extracted
text, or whatever string the artifact happened to hold. So a chart, a diagram or
a scanned page was gone by the time the model read it — and the model had no way
to know something was missing, so it would answer confidently about a document it
had never seen. It now goes to the provider as the file: Anthropic as a
`document` block, OpenAI as a `file` part.

Four things worth knowing:

- **The bytes decide, not the declared type.** A `%PDF-` magic number, not the
  upload's `mime_type` — a renamed archive does not sail through.
- **Current turn only**, unlike images. A PDF is one to two orders of magnitude
  more tokens than a photo, so silently re-sending every document in a thread
  would exhaust the window by turn three. Attach it again if it matters again.
- **32 MB cap**, checked before the provider sees it, so the error names your
  attachment rather than a vendor complaining about a request body.
- **The filename travels** on the OpenAI path, because the model reads it —
  `q3-results.pdf` is a hint that `document.pdf` is not.

#### Getting a figure back out

You may want the actual picture of a chart, not a description. The model cannot
return one — no chat API emits images, and asking for base64 in a JSON field
gets you hallucinated bytes. But it can now **see** the page, which is enough:

```jsonc
// llm_config.response_format, with your own schema
{ "figures": [ { "label": "Figure 2", "page": 3,
                 "bbox": [0.12, 0.34, 0.88, 0.71],
                 "caption": "Revenue by segment, FY24" } ] }
```

Your app crops from the PDF it already has. No code execution anywhere, and the
document never leaves Paradigm. Pad the crop — a model reading a rendered page
gives roughly-right boxes, not pixel-exact ones; if you need exactness,
`pdfplumber` can find image XObjects and their true rectangles, which is text
extraction and needs no rasteriser.

---

## 6. Consume the stream — event catalog

Each event is `event: <type>\ndata: <json>\n\n`. Subscribe by type:

| Event | When | Payload | What to do with it |
|---|---|---|---|
| `scope` | First, before the LLM | `permissions`, `enabled_tools`, `selected_schema_ids`, `selected_node_ids`, `realm_name`, `mode`, `force_read_only`, `identity`, `timezone` | Show what the agent can access this run. `mode` is the ceiling that actually applied (§3.4). `identity` is who it was told it acts for — `{kind, display_name, username, identity_node_id}` (+ `group_id`, `member` on a group run); `null` when `identity` is not elected or nothing resolved. `timezone` is what the prompt's date line used — always a string, `"UTC"` when nothing else resolved. |
| `thinking` | During reasoning (Claude models) | `{text}` — incremental | Render as a dim "thinking…" stream, separate from the answer. |
| `content` | The final answer | `{text}` — incremental tokens | **This is the answer.** Append chunks to render live. |
| `tool_call_start` | Agent invokes a tool | `{id, name}` | Show "running code…" / a spinner. |
| `tool_result` | Tool finished (incl. `execute_code`) | `{tool_call_id, name, arguments, result, exec_duration_ms}` | Code stdout/output lives in `result` (see §7). |
| `inline_reasoning` | During `execute_code`, **before** its `tool_result` | `{tool_call_id, seq, text, evidence}` | One `reason()` call the agent made from inside its own code. Render as the agent's voice, attached to the step named by `tool_call_id` (see §6.1). |
| `write_receipt` | After a code block that wrote to Paradigm | `{tool_call_id, ledger:{nodes_created,…}, manifest:[…]}` | What the bridge actually recorded. Only sent when something was written. Render as a record, not as prose (see §6.1). |
| `tool_error` | A tool failed — usually just before a silent retry | `{tool_call_id, name, kind:"code"\|"system", error}` | Show the attempt and its cause. Without this, two failed attempts and one slow call look identical. |
| `authorization_required` | Before the LLM, when the agent's grant is gone | `{agent_id, agent_name, sub_entity_key, scope:"user"\|"group", reason, message}` | The exposure profile expired or was revoked. **Nothing self-heals this and no retry helps** — offer the user a re-authorization action. The turn still runs; only data access is dead. |
| `message_complete` | A full message is finalized | `{role, content, thinking, tool_calls, input_tokens, output_tokens, llm_provider, llm_model, error, exec_duration_ms}` | Authoritative per-message record; good for token accounting. |
| `paradigm_write` | The agent mutated Paradigm | `{tool, summary, success, error, timestamp, tool_call_id, meta}` | Surface "Created node X" / "Proposal pending". |
| `artifact` | A structured artifact was produced | full artifact dict (see §7) | **Render by `artifact_type`.** |
| `artifact_saved` | `save_artifact()` ran inside code | `{name, artifact_type, id, size_chars, updated}` | Lightweight notice that an artifact exists. |
| `state_change` | State machine transitioned | `{previous_state, new_state, reason, timestamp}` | Update any state UI. |
| `debug` | Only if `debug:true` | `{type, payload}` | Diagnostics. |
| `done` | End of run | `{conversation_id, agent_id, usage:{input_tokens, output_tokens, total_tokens}}` | Persist `conversation_id`; record usage. |
| `error` | Failure | `{message}` | Surface and stop. |

> **Do not build on `force_read_only`.** It is still present in the `scope` payload
> for backward compatibility, but it is **reported and not enforced** — an agent with
> that flag set can still write. It was superseded by `mode` (§3.4), which is a real
> ceiling held by Paradigm rather than a label attached by Personas. If you are
> currently reading `force_read_only` to decide whether to show a read-only badge,
> switch to `mode`, or you are promising your users something nothing enforces.

### Thinking vs. answer vs. code output — how to tell them apart

- **Thinking** → `thinking` events. Render separately/dimmed.
- **Final answer** → `content` events. This is the user-facing text.
- **Code execution output** is **not** streamed token-by-token (the sandbox runs synchronously). Its stdout/result arrives as a block in the `tool_result` event and in the `role:"tool"` `message_complete`, as JSON: `{"success": true, "data": {"stdout": "...", "saved_artifacts": [...], "proposals_created": [...], "reasoning": [...], "write_ledger": {...}, "write_manifest": [...]}}`.

> **A FAILED block returns its payload FLAT.** Success nests everything under
> `data`; a block that raised returns `{"stdout": …, "error": "<traceback>",
> "reasoning": [...], "write_ledger": {...}}` with **no `data` wrapper**. Read
> `result.data ?? result`, or your integration will show nothing on exactly the
> runs where the user most needs an explanation. A transport-level failure is a
> third shape again — `{"error": true, "message": "…"}` — so `error` carries its
> kind in its *type*: `true` means the call failed, a *string* IS the traceback.

### 6.1 Inline reasoning and the write receipt — narration and record

`execute_code` runs synchronously, so a long block is silent by default and the
user cannot tell a slow job from a stuck one. Two events fill that gap, and they
are deliberately **not** the same kind of thing:

**`inline_reasoning` is authored.** The agent calls `reason(text, evidence)` from
inside the code it is running. *Which* call fires is decided by the data — a line
appearing proves its branch executed — but the words were written by the agent
before it saw any data. It is an honest account, not a proof: nothing stops
narration that misdescribes the line beside it. `evidence` is the computed value
that made the branch fire, and it is what lets a reader check the claim instead of
taking an adjective on trust.

**`write_receipt` is observed.** The bridge increments the ledger on each real
write and sandbox code cannot reach it. Thin on meaning, un-forgeable.

Each is weak where the other is strong, so **render the pair and let them agree**.
If narration claims three nodes and the ledger shows zero, that disagreement is
real signal — and it is only visible because the agent could not author the second
half. Style them differently for the same reason: narration as the agent's voice,
the receipt as a record. Styled alike, an authored claim borrows the credibility
of an observed fact.

`reason()` is **opt-in**. The system prompt asks for it at decision points, but
nothing validates, retries, or requires it — an agent that never calls it simply
emits no `inline_reasoning` events. Do not build a UI that depends on their
presence.

Both also persist: they are serialized into the `role:"tool"` message's `content`,
so a **blocking** `/internal/headless/run` caller finds them under
`messages[].content` → `data.reasoning` / `data.write_ledger`, and a UI that
reloads a conversation can rebuild exactly what the live stream showed.

---

## 7. Render the result

> **There is no `response_format` / JSON-schema enforcement.** If your app does nothing, the default output is **free-text markdown** streamed via `content`. Plan your rendering around that, and use the levers below when you need structure.

From weakest to strongest control:

1. **Default — free text.** Concatenate `content` chunks, render as markdown.

   The agent may also emit interactive widgets inline — but **only if you elected
   the capability AND your app record carries the flag** (§4.1). `widget:choice`
   comes with `choices`, `widget:node` with `node_cards`, and `{{title|id|schema}}`
   pills with `citations`. If you do not render them, do not elect them: an agent
   told to emit a widget your surface cannot draw prints the raw markup at the
   person, which is worse than never offering the choice.
2. **Steer with `system_prompt`.** Per request, instruct the agent to produce a specific shape or to emit an artifact. This is the most practical lever.
3. **Artifacts — the structured channel.** When the agent calls `save_artifact(...)` or creates a Paradigm object, you get an `artifact` event carrying:

   ```json
   {
     "id": "...", "conversation_id": "...", "agent_id": "...",
     "tool_call_id": "...", "name": "Q2 summary",
     "artifact_type": "data_table",
     "content": { ... },          // the structured payload
     "render_inline": true,
     "summary": "...", "created_at": "..."
   }
   ```

   Switch your renderer on `artifact_type`. Known types include:
   `document`, `data_table`, `chart`, `code_execution`, `node_created`, `node_updated`,
   `proposal`, `relationship`, `raw_file`, `custom`.
   `render_inline` tells you whether to show it in the chat flow or a side panel.

4. **Paradigm nodes / proposals — schema-validated.** For data the agent writes, schemas validate `value_json` server-side. Writes surface as `artifact` + `paradigm_write`.

   **Propose and write are not mutually exclusive.** An older rule said an agent
   creates a proposal only when it *lacks* write rights. That is no longer true: an
   agent that may perform an action directly may also **ask first**, on the principle
   that asking is strictly safer than doing and shouldn't be gated harder. So expect
   proposals from write-capable agents too — in ask mode (§3.4) every change arrives
   that way by construction. A proposal is inert until approved, and approval
   re-checks the same permission, so this never becomes a route to an effect your app
   was not granted.

**Recommendation:** if you need reliable machine-readable output, instruct the agent (via `system_prompt`) to emit a `save_artifact(artifact_type="data_table" | "custom", content=...)` and render off the `artifact` event — don't parse the free-text `content`.

---

## 8. Data access & pagination (what the agent does on your user's data)

Inside `execute_code`, the agent uses the `paradigm.*` SDK (no import needed):

- **Nodes:** `list_nodes`, `list_all_nodes`, `get_node`, `create_node`, `update_node`, `delete_node`, `count_nodes`
- **Schemas:** `list_schemas`, `get_schema`, `get_schema_by_name`
- **Relationships:** `list_relationships`, `create_relationship`, … *(pass `relationship_types` to `list_nodes` to filter by them)*
- **Proposals:** `create_proposal`, `update_proposal`, `list_proposals`
- **Plugins:** `list_plugins`, `get_plugin`, `execute_plugin`
- **Other:** `query_timeseries`, `web_search`, `save_artifact`, `download_file`

> **Filtering** is by `schema_id` / `schema_ids` (a schema id or name like `journal:entry`) and `relationship_types`.

**Pagination** (your "render further nodes after limit=10" question): `list_nodes` defaults to `limit=20, offset=0` and returns `{ "nodes": [...], "total": N }`. The agent knows there's more from `total`, and gets the next page by re-querying with a higher `offset`. For "everything," `list_all_nodes()` auto-loops in `page_size=1000` chunks until `offset >= total` and returns a flat list. So pagination is offset-driven and `total`-guided — there's no opaque cursor.

Every one of these calls is EP-gated on Paradigm's side via the sub-entity + calling-app headers (§3). The agent physically cannot read or write outside the granted realm/schemas/nodes.

---

## 9. Continuity, automations, plugins, errors

### Conversation continuity
The `done` event returns `conversation_id`. Pass it back as `conversation_id` on the next `/run/stream` to continue the same thread (the agent gets the full history). Omit it to start fresh — and pass `conversation_title` on that first call, or the thread is titled with the raw first message. **Note:** message *database IDs* are not in the stream (they're assigned after `done` persists) — if you need them, re-fetch the conversation.

### Conversations API (history)
Conversations persist server-side per `(user, agent)`; your app can list, read, and delete them. All three use the standard HMAC auth (§2). List/get use POST (the signed body carries auth).

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/internal/headless/conversations` | `{ paradigm_user_id, app_name, agent_name, include_messages? }` | `{ conversations: [{id, title, created_at, updated_at, messages?}] }` (newest first, max 50) |
| POST | `/internal/headless/conversations/<id>` | `{ paradigm_user_id }` | `{ id, title, ..., messages: [{role, content, created_at}] }` |
| DELETE | `/internal/headless/conversations/<id>` | `{ paradigm_user_id }` | `{ message, conversation_id }` — removes the thread and its messages |
| POST | `/internal/headless/conversations/<id>/timeline` | `{ paradigm_user_id }` | `{ jobs: [{message_id, created_at, revert_status, events: [{tool, summary, success, error, timestamp, tool_call_id, meta}]}] }` |
| POST | `/internal/headless/conversations/<id>/messages/<message_id>/revert` | `{ paradigm_user_id }` | `{ status, results: [...], at, by_user_id }` |

Notes: `include_messages` returns only `user`/`assistant` messages with content (tool traffic is filtered). If your app prepends context to each user message (a data snapshot, instructions), remember that history returns the **full stored content** — strip your preamble before display, and set `conversation_title` explicitly so list titles aren't the preamble. The DELETE route was added 2026-08-12; a deployment predating it answers `405` — treat that as "not yet supported", not an error.

**Timeline & revert.** Timeline groups a conversation's Paradigm writes by *job* — one job is one agent turn, however many `paradigm_write` events it produced across however many `execute_code` calls (§6) — the same grouping `/revert` acts on. A turn that made no writes is left out entirely. `revert` undoes one job: a `create` is trashed, a `delete` is restored, a content `edit` is reconstructed from Paradigm's own version history (nothing your app needs to have captured — Paradigm snapshots every write on its own). Paradigm itself has no revert endpoint open to third-party apps at all (its own is permanently closed to the allowlist), so this is Personas' own mechanism, not a proxy to one.

`revert_status` on a job is `null` until someone reverts it, then `{status, results, at, by_user_id}`. `status` is `"reverted"` (everything in that turn undid cleanly), `"partial"` (some did, some didn't), or `"failed"` (none did) — each entry in `results` has its own `outcome`, including `"conflict"`: the node changed since this write (a different app, a human, a later turn), so nothing was touched rather than silently discarding that change. Reverting a turn with no writes returns `400 NOTHING_TO_REVERT`; reverting one already fully `"reverted"` returns `409 ALREADY_REVERTED` — a `"partial"` or `"failed"` job can be retried.

### Clearing silent context
`DELETE /internal/headless/conversations/<id>/context` (body `{ paradigm_user_id }`) clears a conversation's silent context without deleting the thread.

### Automations (scheduled agents)
Create one via `POST /agents/<agent_id>/automations` with a cron `trigger_config`. This registers a **scheduled automation in Paradigm**, not in Personas. When it fires, Paradigm's worker calls Personas back (signed) at `/internal/automation/run` with the `action_config` (agent, message, model). The automation runs under the agent's **own sub-entity EP** — if that EP is deactivated, the run silently produces nothing. Manage with `GET` / `DELETE` / `.../toggle` on the same route.

> **Creating/editing automations is governed by the EP verb — nothing else.** The agent's grant must hold `automations:write` (create/edit) or `automations:execute` (trigger/inspect). The agent's sub-entity EP **is** the per-agent grant, so the grant is the opt-in — there is no separate Personas-side flag. Grant `automations:write` in the realm/consent and the agent (including one creating automations from its own code via `paradigm.create_automation(...)`) can create them; grant only `execute` and it can trigger/inspect but not create/edit. (Earlier builds also required a `tools_config.automations_manage` opt-in; that redundant second gate was removed — the Scope panel now matches the realm/EP grant.) The Paradigm-side automation *callback endpoint* (`/internal/automation/run`) is registered for you automatically **at Personas startup** — it's an app-level setting on Personas' own Paradigm app record, not something declared per agent or per run — so you never set it up.

### Plugins
Two senses: (a) the agent can **call** Paradigm plugins from code (`paradigm.execute_plugin(...)`), gated by an `execute_plugins` EP verb; (b) an agent can itself be **published as** a discoverable plugin (`.../publish-plugin`) and invoked by other apps via `/internal/headless/invoke`.

### Error model
Errors come back as either an HTTP error response or an `error` SSE event, with a code + message. Common codes:
`VALIDATION_ERROR` (400), `UNAUTHORIZED` (401, bad signature/key), `NOT_FOUND` (404, e.g. unknown `conversation_id`), `AGENT_ERROR` (500, run failed), `AGENT_EXCEEDS_CALLING_APP` (403, agent's grant exceeds a *calling app's* grant on the plugin/broker path — auto-repaired; not seen in the basic embedded flow). Also handle the non-error `requires_realm_assignment` branch (§3).

> **Proposal 403s are rarer than they used to be.** Creating, updating, approving,
> rejecting, cancelling, applying and deleting a proposal no longer require a separate
> `propose` permission on top of the underlying action. The check that remains is the
> one that matters: you may propose or apply what you could have performed directly,
> and an app still only ever touches **its own** proposals. If you wrote retry or
> fallback logic around a `PERMISSION_DENIED` on these routes, it is now mostly dead
> code.

---

## 10. Full worked example — a streaming SSE client

A complete, copy-pasteable Python client: signs the request, opens the stream, dispatches every event type, accumulates the answer, and collects artifacts.

```python
import hashlib, hmac, json, requests

PERSONAS_HOST = "https://personas.ofself.com"
APP_ID   = "a1b2c3d4-..."        # from /apps/register
HMAC_KEY = "sk_hdls_..."         # from /apps/register — keep secret

def sign(raw: bytes) -> str:
    return "sha256=" + hmac.new(HMAC_KEY.encode(), raw, hashlib.sha256).hexdigest()

def run_agent(paradigm_user_id: str, message: str, *,
              agent_name="assistant", app_name="My App",
              conversation_id=None, system_prompt=None, return_to=None):
    body = {
        "app_id": APP_ID, "hmac_key": HMAC_KEY,
        "paradigm_user_id": paradigm_user_id,
        "app_name": app_name, "agent_name": agent_name,
        # system_prompt is REQUIRED if this call auto-creates the agent:
        "system_prompt": system_prompt or "You are a helpful assistant.",
        "message": message,
    }
    if conversation_id: body["conversation_id"] = conversation_id
    if return_to:       body["return_to"]       = return_to
    # NOTE: a run-body `client_id` is ignored; your app's identity is the
    # `paradigm_client_id` set at registration (see §1, §3).

    raw = json.dumps(body).encode()                       # serialize ONCE
    headers = {"Content-Type": "application/json", "X-Internal-Signature": sign(raw)}

    answer, thinking, artifacts, result = [], [], [], {}
    with requests.post(f"{PERSONAS_HOST}/api/v1/internal/headless/run/stream",
                       data=raw, headers=headers, stream=True, timeout=300) as resp:
        # The user may not have authorized this agent yet: Personas replies with a
        # JSON body (not SSE). Detect it BEFORE trying to parse the stream.
        if "application/json" in (resp.headers.get("Content-Type") or ""):
            j = resp.json()
            if j.get("requires_realm_assignment"):
                return {"requires_realm_assignment": True,
                        "redirect_url": j["redirect_url"], "agent_id": j.get("agent_id")}
            resp.raise_for_status()
            raise RuntimeError(j.get("message", "unexpected JSON response"))
        resp.raise_for_status()
        event_type, data_buf = None, []
        for line in resp.iter_lines(decode_unicode=True):
            if line is None:
                continue
            if line.startswith(":"):                       # heartbeat comment — ignore
                continue
            if line == "":                                  # blank line ends one event
                if event_type and data_buf:
                    handle(event_type, json.loads("".join(data_buf)),
                           answer, thinking, artifacts, result)
                event_type, data_buf = None, []
                continue
            if line.startswith("event:"):
                event_type = line[len("event:"):].strip()
            elif line.startswith("data:"):
                data_buf.append(line[len("data:"):].strip())

    return {
        "conversation_id": result.get("conversation_id"),
        "answer": "".join(answer),
        "thinking": "".join(thinking),
        "artifacts": artifacts,
        "usage": result.get("usage"),
    }

def handle(ev, data, answer, thinking, artifacts, result):
    if ev == "scope":
        # what the agent is allowed to touch this run
        print("[scope] tools:", data.get("enabled_tools"),
              "| realm:", data.get("realm_name"))
    elif ev == "thinking":
        thinking.append(data.get("text", ""))              # dim reasoning stream
    elif ev == "content":
        chunk = data.get("text", "")
        answer.append(chunk)
        print(chunk, end="", flush=True)                   # live answer
    elif ev == "tool_call_start":
        print(f"\n[running tool: {data.get('name')}]")
    elif ev == "tool_result":
        # execute_code stdout/output is here (not streamed token-by-token)
        out = (data.get("result") or {}).get("data", {})
        if isinstance(out, dict) and out.get("stdout"):
            print(f"\n[code output]\n{out['stdout']}")
    elif ev == "paradigm_write":
        print(f"\n[paradigm] {data.get('summary')}")
    elif ev == "artifact":
        artifacts.append(data)                             # render by data['artifact_type']
        print(f"\n[artifact: {data.get('artifact_type')} — {data.get('name')}]")
    elif ev == "state_change":
        print(f"\n[state: {data.get('previous_state')} -> {data.get('new_state')}]")
    elif ev == "done":
        result["conversation_id"] = data.get("conversation_id")
        result["usage"] = data.get("usage")
    elif ev == "error":
        raise RuntimeError(data.get("message", "agent error"))

if __name__ == "__main__":
    out = run_agent("user-uuid-123", "Summarize my journal entries from last week.",
                    return_to="https://yourapp.com/after-auth")
    if out.get("requires_realm_assignment"):
        # First time for this user: send them to authorize, then retry the same call.
        print("Send the user to authorize:", out["redirect_url"])
    else:
        print("\n\n--- DONE ---")
        print("conversation_id:", out["conversation_id"])
        print("usage:", out["usage"])
        print("artifacts:", [(a["artifact_type"], a["name"]) for a in out["artifacts"]])
        # Continue the thread:
        # run_agent("user-uuid-123", "Now turn that into a chart.",
        #           conversation_id=out["conversation_id"])
```

### Browser / Node note
The same stream works from JS, but `EventSource` only does GET — use `fetch` with a streaming body reader (or a POST-capable SSE library) to send the signed POST and parse `event:` / `data:` lines exactly as above.

---

## 11. Quick reference

**Endpoints**

| Method | Path | Purpose |
|---|---|---|
| GET | `/docs` | **This guide**, served by the deployment you're calling. Open — no signature. `?format=md\|json`, `?section=<slug>`; `GET /docs/sections` lists the slugs. |
| POST | `/internal/headless/apps/register` | Get `app_id` + `hmac_key` (once). |
| GET / PATCH | `/internal/headless/apps/<app_id>` | Read the app + its tools / update `name`, `paradigm_client_id`. Bare-key auth (§2). |
| PUT | `/internal/headless/apps/<app_id>/tools` | Replace the app's custom tool set (§1.2). `PATCH`/`DELETE` on `.../tools/<tool_name>` for one. |
| POST | `/internal/headless/apps/<app_id>/secrets` | Store an encrypted header credential → `secret_id` (§1.2). `DELETE .../secrets/<id>` removes it. |
| POST | `/internal/headless/agents` | Pre-create/fetch an agent (`system_prompt` required) → `{agent_id, created}`. |
| PATCH | `/internal/headless/agents/<agent_id>` | Update `system_prompt`, `llm_provider`, `llm_model`, `temperature` (§3.2). |
| POST | `/internal/headless/list-agents` | A user's active agents. Body `{paradigm_user_id}` → `{agents: [{id, name, description, slug, has_realm, sub_entity_plugin_id}]}`. `has_realm: false` = created but not yet authorized (§3.3). |
| POST | `/internal/headless/run/stream` | **Run, streaming (use this for UX).** |
| POST | `/internal/headless/run` | Run, blocking (final JSON only). |
| POST | `/agents/<id>/automations` | Create a scheduled automation. |
| POST | `/internal/headless/invoke` | Invoke an agent published as a plugin. |
| POST | `/internal/headless/conversations` | List a user+agent's conversations (`include_messages` optional). |
| POST | `/internal/headless/conversations/<id>` | Full thread with messages. |
| DELETE | `/internal/headless/conversations/<id>` | Delete a thread (added 2026-08-12; older deploys 405). |

This table is the lifecycle path, not the whole API. There are further routes for
artifacts, silent context, usage, agent scope, timelines, file upload and plugin
publication; see `HEADLESS_API_REFERENCE.md` for endpoint-level detail.

**Auth (every runtime call):** body `app_id` + `hmac_key`, header `X-Internal-Signature: sha256=hmac_sha256(raw_body, hmac_key)`. App-management routes (apps, tools, secrets) take the bare `hmac_key` in the body and verify no signature — §2.

**Golden rules**
- User-facing? Use `/run/stream`. Blocking `/run` is why it "feels slow."
- `mode` is a real ceiling; `force_read_only` is not. Build read-only UI on `mode` (§3.4).
- If you declare an `agents.yaml` roster, its `key` must equal the slug of your `agent_name` (§3.5). A mismatch silently splits one agent into two half-records.
- The answer is the `content` stream; structured data is the `artifact` stream; code output is in `tool_result`.
- Persist `conversation_id` from `done` to continue threads; set `conversation_title` on new ones.
- Never pass `llm_provider`/`llm_model` casually — they persist onto the agent.
- Handle `requires_realm_assignment` — it's a one-time authorization handshake (§3.3), not an error.
- The agent can only ever do `(its consent ceiling) ∩ (what the user authorized for its realm)` — and, for bound tenants, `∩ (the user's grant to YOUR app)`. No authorization anywhere ⇒ agent can do nothing.
- **You can only operate agents your app created.** A different app's `agent_id` returns `404 NOT_FOUND` — agents are owned by the app that created them (§3), never shared across apps by id.
- Bind `paradigm_client_id` (§1.1): it caps agents to your app's grant AND lets your already-authorized users skip the handshake entirely.
- A realm-less agent heals on its next run once the tenant is bound and the user has authorized the bound app (requires a deploy carrying the 2026-08-12 heal patch).
- Your app authenticates as a Personas tenant (HMAC key) AND should carry its own Paradigm identity — set `paradigm_client_id` at registration so agents are capped by your app's grant too (§1, §3). A run-body `client_id` is ignored.

# Personas Headless Agent — Developer Guide

This guide covers everything you need to embed a Personas-powered AI agent into your product: registration, secrets, tools, agent auth, context injection, conversation management, artifacts, and consuming the response stream.

---

## Table of Contents

1. [How It Works — The Big Picture](#1-how-it-works)
2. [Register Your App](#2-register-your-app)
3. [Secrets — What They Are and How They're Secured](#3-secrets)
4. [Tools — Giving the Agent Your APIs](#4-tools)
5. [Agent Auth — Connecting to a User's Data](#5-agent-auth)
6. [Writing a Good System Prompt](#6-system-prompt)
7. [Silent Context — Making the Agent Page-Aware](#7-silent-context)
8. [Sending a Message and Receiving the Stream](#8-streaming)
9. [Agent Scope — What Data the Agent Can Access](#9-scope)
10. [Data Flow End to End](#10-data-flow)
11. [Agent Lifecycle — Pre-create, Update, Inspect](#11-agent-lifecycle)
12. [Conversation & History Management](#12-conversation-history)
13. [Artifact Management](#13-artifact-management)
14. [Plugin Surface — Being Called by Other Apps](#14-plugin-surface)
15. [Automation — Background Celery Triggers](#15-automation)
16. [Quick Reference — All Endpoints](#16-endpoint-reference)

---

## 1. How It Works

Your product embeds a Personas agent per user. The agent has access to:
- **Your APIs** — custom tools you declare (the LLM calls them, we proxy the HTTP request)
- **The user's Paradigm data** — nodes, relationships in their privacy realm
- **Page context you push** — silent, ephemeral state the LLM sees but the user never does

The call flow every time a user sends a message:

```
Your frontend
    │
    │  POST /api/v1/internal/headless/run/stream
    │  (HMAC-signed with your per-app key)
    ▼
Personas Backend
    │  Verifies app_id + hmac_key
    │  Loads your registered tools
    │  Injects stored silent context
    │  Sends to LLM
    ▼
LLM reasons...
    │  Calls one of your tools
    ▼
Personas Backend
    │  Proxies HTTP → your API endpoint
    │  Injects your secret into the request header (LLM never sees it)
    │  Returns result to LLM
    ▼
LLM continues reasoning → final response
    │
    │  SSE stream back to your frontend
    ▼
Your frontend receives:
  scope             — what data the agent can access (permissions, schemas)
  thinking          — Claude extended thinking (Claude only)
  content           — text chunks from the LLM (reasoning mid-loop + final answer)
  tool_call_start   — agent decided to call a tool
  tool_result       — tool executed, result passed back to LLM
  paradigm_write    — emitted when agent writes to the user's Paradigm graph
  artifact          — structured data created during the run
  message_complete  — one full LLM message finalised
  done              — { conversation_id, agent_id, usage }
```

---

## 2. Register Your App

> **Base URL:** `https://personas.ofself.ai` in production, `http://localhost:XXXX` locally. Set `PERSONAS_URL` in your environment and use it throughout.

Registration is **open** — no platform secret or prior approval needed. Call `/register` once to get your per-app credentials. **The HMAC key is shown exactly once** — store it immediately in your secrets manager (AWS Secrets Manager, Vault, etc.).

### Step 1 — Register

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/apps/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My App"}'
```

**Response `201`:**
```json
{
  "app_id": "3f7a2c1d-...",
  "name": "My App",
  "hmac_key": "sk_hdls_a1b2c3d4e5f6...",
  "hmac_key_prefix": "sk_hdls_a1b2c3...",
  "message": "Store the hmac_key securely — it cannot be retrieved again."
}
```

Store both values in your environment:
```bash
PERSONAS_APP_ID=3f7a2c1d-...
PERSONAS_HMAC_KEY=sk_hdls_a1b2c3d4e5f6...
```

### How Auth Works After Registration

Every runtime request must include:
- `app_id` and `hmac_key` in the **request body**
- `X-Internal-Signature` header — HMAC-SHA256 of the raw request body signed with your `hmac_key`

The backend verifies both: `hash(hmac_key) == stored_hash` and `HMAC(body, hmac_key) == signature`. If either fails, the request is rejected.

**Why this is secure:** Compromise of one app's key affects only that app. The key is never stored in plaintext — only its SHA-256 hash is in the DB. The HMAC signature over the body prevents replay attacks and body tampering.

### Signing Requests

```python
import hmac, hashlib, json

def sign_body(body: dict, secret: str) -> str:
    raw = json.dumps(body, separators=(',', ':')).encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), raw, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

payload = {
    "app_id": PERSONAS_APP_ID,
    "hmac_key": PERSONAS_HMAC_KEY,
    # ... rest of your request fields
}

headers = {
    "Content-Type": "application/json",
    "X-Internal-Signature": sign_body(payload, PERSONAS_HMAC_KEY),
}
```

```javascript
const crypto = require('crypto');

function signBody(body, secret) {
  const raw = JSON.stringify(body);
  const sig = crypto.createHmac('sha256', secret).update(raw).digest('hex');
  return `sha256=${sig}`;
}

const payload = {
  app_id: process.env.PERSONAS_APP_ID,
  hmac_key: process.env.PERSONAS_HMAC_KEY,
  // ... rest of your request fields
};

const headers = {
  'Content-Type': 'application/json',
  'X-Internal-Signature': signBody(payload, process.env.PERSONAS_HMAC_KEY),
};
```

### View Your App

```bash
curl -G https://personas.ofself.ai/api/v1/internal/headless/apps/$PERSONAS_APP_ID \
  --data-urlencode "hmac_key=$PERSONAS_HMAC_KEY"
```

**Response `200`:**
```json
{
  "id": "3f7a2c1d-...",
  "name": "My App",
  "hmac_key_prefix": "sk_hdls_a1b2c3...",
  "created_at": "2025-01-15T10:00:00+00:00",
  "updated_at": "2025-01-15T10:00:00+00:00",
  "tools": [
    {
      "id": "tool-uuid",
      "tool_name": "search_crm",
      "description": "...",
      "parameters": { "type": "object", "properties": {...} },
      "endpoint_url": "https://api.yourapp.com/crm/search",
      "http_method": "POST",
      "static_headers": {},
      "secret_id": "9e4b1f2a-...",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

## 3. Secrets

### What Are Secrets?

When the LLM calls one of your tools, Personas proxies the HTTP request to your endpoint. If your endpoint requires an API key (e.g. `Authorization: Bearer xyz`), you register that key as a **secret**.

**Why it's secure:**
- Your secret is **encrypted at rest** using AES-256 (Fernet) with a server-side encryption key
- The secret value is **never returned** after registration — not in GET responses, not in logs
- When we proxy a tool call, we decrypt the secret server-side and inject it into the outgoing HTTP header **before** calling your endpoint
- The LLM **never sees the secret** — it only receives the response from your endpoint

### Register a Secret

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/apps/$PERSONAS_APP_ID/secrets \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "label": "stripe_api_key",
    "header_name": "Authorization",
    "header_value": "Bearer sk_live_your_actual_stripe_key"
  }'
```

**Response `201`:**
```json
{
  "secret_id": "9e4b1f2a-...",
  "label": "stripe_api_key",
  "header_name": "Authorization",
  "message": "Secret stored encrypted. Use secret_id when registering tools."
}
```

Save the `secret_id` — you'll reference it when declaring tools. The `header_value` is gone from here. To rotate, delete the old secret and add a new one.

### Delete / Rotate a Secret

```bash
curl -X DELETE https://personas.ofself.ai/api/v1/internal/headless/apps/$PERSONAS_APP_ID/secrets/$SECRET_ID \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'"}'
```

**Response `200`:**
```json
{ "message": "Secret deleted" }
```

---

## 4. Tools

### What Are Tools?

Tools are **API endpoints you expose to the LLM**. You describe what each tool does, what inputs it takes, and where to call it. At runtime, when the LLM decides to call your tool, Personas:

1. Validates the LLM's input against your parameter schema
2. Makes an HTTP request to your endpoint with the LLM's arguments as the JSON body
3. Injects your secret header (if configured)
4. Returns your endpoint's JSON response to the LLM

### Register Tools (replace all)

```bash
curl -X PUT https://personas.ofself.ai/api/v1/internal/headless/apps/$PERSONAS_APP_ID/tools \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "tools": [
      {
        "tool_name": "search_crm",
        "description": "Search the CRM for contacts, companies, or deals. Use this when the user asks about customers, leads, or sales data.",
        "parameters": {
          "type": "object",
          "properties": {
            "query": { "type": "string", "description": "Search query" },
            "entity_type": { "type": "string", "enum": ["contact", "company", "deal"] },
            "limit": { "type": "integer", "default": 10 }
          },
          "required": ["query"]
        },
        "endpoint_url": "https://api.yourapp.com/crm/search",
        "http_method": "POST",
        "static_headers": { "X-App-Version": "2.1" },
        "secret_id": "9e4b1f2a-..."
      }
    ]
  }'
```

**Response `200`:**
```json
{
  "tools": [
    {
      "id": "tool-uuid",
      "tool_name": "search_crm",
      "description": "...",
      "parameters": { "type": "object", "properties": {...} },
      "endpoint_url": "https://api.yourapp.com/crm/search",
      "http_method": "POST",
      "static_headers": { "X-App-Version": "2.1" },
      "secret_id": "9e4b1f2a-...",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

### Update a Single Tool

```bash
curl -X PATCH https://personas.ofself.ai/api/v1/internal/headless/apps/$PERSONAS_APP_ID/tools/search_crm \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "description": "Updated description...",
    "endpoint_url": "https://api.yourapp.com/v2/crm/search"
  }'
```

**Response `200`:** Full tool object (same shape as above). Changes take effect immediately on the next agent run.

### Remove a Tool

```bash
curl -X DELETE https://personas.ofself.ai/api/v1/internal/headless/apps/$PERSONAS_APP_ID/tools/search_crm \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'"}'
```

**Response `200`:**
```json
{ "message": "Tool 'search_crm' deleted" }
```

### What Your Endpoint Receives

When the LLM calls `search_crm`, Personas POSTs to your endpoint:

```http
POST https://api.yourapp.com/crm/search
Authorization: Bearer sk_live_your_actual_key    ← injected from secret
X-App-Version: 2.1                               ← from static_headers
Content-Type: application/json

{
  "query": "Acme Corp",
  "entity_type": "company",
  "limit": 5
}
```

Your endpoint returns JSON — the LLM receives exactly what you return.

### Writing Effective Tool Descriptions

```
✘ Bad:  "CRM search endpoint"
✔ Good: "Search the CRM for contacts, companies, or deals.
         Use when the user asks about customers, leads, sales pipeline,
         account status, or anything related to specific companies or people
         we do business with."
```

---

## 5. Agent Auth

Each user who interacts with your embedded agent needs to **authorize it once** against their Paradigm privacy realm.

> **⚠️ If you skip this step, every `/headless/run` call for that user will return a `requires_realm_assignment` JSON body.** No conversation will start, no SSE stream will open.

### How It Works

1. Your backend calls `/headless/run` or `/headless/run/stream` for a user for the first time
2. If the agent doesn't have a realm yet, Personas returns a **JSON body** (not an SSE stream):
   ```json
   {
     "requires_realm_assignment": true,
     "agent_id": "...",
     "redirect_url": "https://radius.ofself.ai/authorize?...",
     "message": "Authorize this automation agent once, then retry execution."
   }
   ```
3. You redirect the user to `redirect_url` — they see the Paradigm authorization page
4. They approve → Paradigm redirects back to your `PARADIGM_CALLBACK_URL`
5. Subsequent calls to `/headless/run` work normally

One agent is created automatically per `(app_name + agent_name, user)` pair on first call — you don't need to pre-provision agents (though you can via the lifecycle endpoints in Section 11).

### Handling It in Your Relay

```javascript
const personasRes = await fetch(`${PERSONAS_URL}/api/v1/internal/headless/run/stream`, {
  method: 'POST',
  headers: { ..., 'Accept': 'text/event-stream' },
  body: JSON.stringify(payload),
});

// Personas returned JSON instead of SSE — check for auth requirement
if (!personasRes.ok || personasRes.headers.get('content-type')?.includes('application/json')) {
  const body = await personasRes.json().catch(() => ({}));
  if (body.requires_realm_assignment) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.write(`data: ${JSON.stringify({ type: 'agent_auth_required', redirect_url: body.redirect_url })}\n\n`);
    return res.end();
  }
  return res.status(personasRes.status).json({ error: body.message || 'Agent error' });
}
// Normal SSE relay follows...
```

### The `return_to` Parameter

Pass `return_to` in your `/headless/run` body and Personas embeds it in the `redirect_url` so the user is sent back to your app after authorizing, rather than staying on Paradigm's UI:

```
https://radius.ofself.ai/authorize
  ?client_id=<personas_client_id>
  &sub_entity_key=my-coach
  &display_name=My+Coach
  &redirect_uri=<personas_callback_url>?return_to=https://yourapp.com/callback/personas
```

---

## 6. System Prompt

The system prompt defines who your agent is and how it should behave. It is set **once at agent creation** and stored permanently — it does not update automatically on subsequent runs.

> **Important:** Passing `system_prompt` in a `/headless/run` call will use it for that run only (ephemeral override). To permanently change a stored agent's system prompt, use `PATCH /internal/headless/agents/<agent_id>` (Section 11).

```python
payload = {
    "app_id": PERSONAS_APP_ID,
    "hmac_key": PERSONAS_HMAC_KEY,
    "paradigm_user_id": user.paradigm_id,
    "message": user_message,
    "app_name": "My App",
    "agent_name": "Sales Assistant",
    # On first call, this creates the agent with this prompt.
    # On subsequent calls, this overrides for the current run only.
    "system_prompt": f"""
You are an assistant for {user.name} ({user.account_tier} plan).

## Tools Available
- search_crm: Search their CRM records
- create_ticket: File support requests
""",
}
```

---

## 7. Silent Context

Silent context lets you tell the agent **what's happening in your product** without the user needing to explain it. It's injected as a hidden block just before each user message — the LLM sees it, the user never does.

### Push Context (Debounced)

Call this whenever meaningful state changes in your product. The **latest value always wins**.

```python
# POST /api/v1/internal/headless/context
payload = {
    "app_id": PERSONAS_APP_ID,
    "hmac_key": PERSONAS_HMAC_KEY,
    "conversation_id": conversation_id,  # required
    "context": "Page: /deals/detail\nSelected deal: Acme Corp (ID: d_4821, status: negotiation)",
}
requests.post(
    f"{PERSONAS_URL}/api/v1/internal/headless/context",
    json=payload,
    headers={"X-Internal-Signature": sign_body(payload, PERSONAS_HMAC_KEY)},
)
```

**Response `200`:**
```json
{ "message": "Context updated", "conversation_id": "uuid" }
```

### Clear Context

```bash
curl -X DELETE https://personas.ofself.ai/api/v1/internal/headless/conversations/$CONVO_ID/context \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{ "message": "Context cleared", "conversation_id": "uuid" }
```

### Good Context Format

Write context as **plain, dense facts** — not prose:

```
✔ Page: /pricing
  Plan viewed: Pro ($49/mo)
  Times viewed this session: 3
  Current plan: Starter
  Account age: 47 days
```

---

## 8. Sending a Message and Receiving the Stream

### Request Body — `/headless/run/stream` and `/headless/run`

```json
{
  "app_id":             "string (required) — from /register",
  "hmac_key":           "string (required) — from /register",
  "paradigm_user_id":   "string (required) — user's Paradigm identity",
  "message":            "string (required) — the user's message",
  "app_name":           "string (required) — your product name, e.g. 'Missions'",

  "agent_id":           "string — use this to target a specific known agent by ID (bypasses agent_name lookup)",
  "agent_name":         "string — required if agent_id not provided; name of this agent",

  "system_prompt":      "string — per-request system prompt override (does not update the stored prompt)",
  "conversation_id":    "string — existing conversation ID for continuity (omit to start fresh)",
  "conversation_title": "string — override auto-generated title for new conversations",

  "llm_provider":       "string — 'anthropic' | 'ofself' (default: 'ofself')",
  "llm_model":          "string — model identifier e.g. 'gpt-5.2'",
  "temperature":        "number — 0.0–2.0 (default: 0.4)",

  "web_search":         "boolean — enable live web search inside execute_code; only applies on the call that creates the agent, PATCH to change it later. See WEB_SEARCH.md (default: false)",
  "wikipedia_search":   "boolean — enable Wikipedia search (default: false)",

  "artifact_ids":       "array of strings — artifact UUIDs whose content is injected into this message",
  "callback_url":       "string — webhook URL; Personas POSTs { conversation_id, agent_id, usage } here after streaming completes",

  "return_to":          "string — URL to redirect after realm auth (if not yet authorized)",
  "group_id":           "string — Paradigm group ID if assigning a group realm",
  "headless_app_id":    "string — explicit HeadlessApp reference (auto-resolved from app_id if omitted)",
  "debug":              "boolean — enable debug-mode streaming"
}
```

**Conversation title:** When `conversation_id` is omitted (new conversation), the title defaults to the first 60 characters of the message, or `"{app_name} · {agent_name}"` if the message is very short. Pass `conversation_title` to override with a specific string.

### Send a Message (Streaming)

```python
import json, requests

payload = {
    "app_id": PERSONAS_APP_ID,
    "hmac_key": PERSONAS_HMAC_KEY,
    "paradigm_user_id": "user-paradigm-uuid",
    "message": "Show me our top 5 deals this quarter",
    "app_name": "My App",
    "agent_name": "Sales Assistant",
    "system_prompt": "You are a sales assistant...",
    "llm_provider": "ofself",
    "llm_model": "gpt-5.2",
}

response = requests.post(
    f"{PERSONAS_URL}/api/v1/internal/headless/run/stream",
    json=payload,
    headers={
        "Content-Type": "application/json",
        "X-Internal-Signature": sign_body(payload, PERSONAS_HMAC_KEY),
        "Accept": "text/event-stream",
    },
    stream=True,
)

for line in response.iter_lines():
    if not line:
        continue
    line = line.decode('utf-8')
    if line.startswith('event:'):
        event_type = line[7:].strip()
    elif line.startswith('data:'):
        data = json.loads(line[5:].strip())
        handle_event(event_type, data)
```

### SSE Event Types

| Event | Payload shape | What It Means |
|-------|--------------|---------------|
| `scope` | `{ permissions, enabled_tools, selected_schemas, selected_node_ids, realm_name }` | Emitted once at stream start — describes exactly what data the agent can access |
| `thinking` | `{ text }` | Model-level extended thinking (Claude only — internal reasoning before the first content/tool) |
| `content` | `{ text }` | Text chunk — either reasoning mid-loop or the final response |
| `tool_call_start` | `{ id, name }` | Agent decided to call a tool |
| `tool_result` | `{ tool_call_id, name, arguments, result }` | Tool executed, result passed back to LLM |
| `paradigm_write` | `{ tool, summary, success, error, timestamp, meta }` | Emitted when the agent writes to the user's Paradigm graph (creates/updates a node, relationship, etc.) |
| `artifact` | `{ id, conversation_id, agent_id, name, artifact_type, content, content_size, summary, render_inline, created_at }` | Structured data created during the run |
| `message_complete` | `{ role, content, thinking, tool_calls }` | One full LLM message finalised |
| `done` | `{ conversation_id, agent_id, usage }` | All iterations complete — save `conversation_id` for next message |
| `error` | `{ message }` | Something went wrong — stream ends |

**`usage` shape inside `done`:**
```json
{
  "input_tokens": 1240,
  "output_tokens": 318
}
```

### Handling Events in JavaScript

```javascript
const es = new EventSource('/api/relay-stream', { withCredentials: true });

let activeToolCalls = {};
let loopIteration   = 0;

es.addEventListener('scope', (e) => {
  const scope = JSON.parse(e.data);
  // scope.realm_name      — the privacy realm the agent operates in
  // scope.permissions     — { can_see_nodes, can_create_nodes, ... }
  // scope.enabled_tools   — ["list_nodes", "search_nodes", ...]
  // scope.selected_schemas— [{ id, name }, ...] (empty = all schemas)
  // scope.selected_node_ids — specific pinned node IDs (empty = none)
  renderScopePanel(scope);
});

es.addEventListener('thinking', (e) => {
  const { text } = JSON.parse(e.data);
  appendThinkingBubble(text); // Claude's internal pre-response reasoning
});

es.addEventListener('content', (e) => {
  const { text } = JSON.parse(e.data);
  if (Object.keys(activeToolCalls).length === 0 && loopIteration > 0) {
    appendToFinalResponse(text);
  } else {
    appendToReasoningStep(loopIteration, text);
  }
});

es.addEventListener('tool_call_start', (e) => {
  const { id, name } = JSON.parse(e.data);
  loopIteration++;
  activeToolCalls[id] = { name, startedAt: Date.now() };
  showToolIndicator(id, `${name}...`);
});

es.addEventListener('tool_result', (e) => {
  const { tool_call_id, name, arguments: args, result } = JSON.parse(e.data);
  delete activeToolCalls[tool_call_id];
  markToolDone(tool_call_id, result);
});

es.addEventListener('paradigm_write', (e) => {
  const { tool, summary, success, error } = JSON.parse(e.data);
  // Show the user what the agent wrote to their Paradigm graph
  showParadigmWriteIndicator({ tool, summary, success });
});

es.addEventListener('artifact', (e) => {
  const artifact = JSON.parse(e.data);
  // artifact.artifact_type — "node_created", "data_table", "document", etc.
  // artifact.content       — structured payload
  // artifact.summary       — human-readable description
  // artifact.render_inline — whether to show in chat vs. sidebar-only
  renderArtifact(artifact);
});

es.addEventListener('done', (e) => {
  const { conversation_id, agent_id, usage } = JSON.parse(e.data);
  saveConversationId(conversation_id); // pass back on next message for continuity
  saveAgentId(agent_id);              // use for lifecycle/artifact endpoints
  showUsage(usage);                   // { input_tokens, output_tokens }
  es.close();
});

es.addEventListener('error', (e) => {
  console.error('Agent error:', JSON.parse(e.data));
  es.close();
});
```

### Conversation Continuity

| `conversation_id` in request | Behaviour |
|------------------------------|-----------|
| **Omitted / null** | Personas creates a brand-new conversation. A new `conversation_id` is returned in `done`. |
| **Provided** | Personas loads the full message history for that conversation and feeds it to the LLM. You only send the new message. |

### Send a Message (Synchronous)

Use `/headless/run` instead of `/run/stream` for background jobs. You get the full response in a single JSON reply — no SSE consumer needed.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/run \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "paradigm_user_id": "user-uuid",
    "message": "Summarise goal progress for goals approaching their deadline this week.",
    "app_name": "My App",
    "agent_name": "My Coach",
    "system_prompt": "You are a goal coach...",
    "llm_provider": "ofself",
    "llm_model": "gpt-5.2"
  }'
```

**Response `200`:**
```json
{
  "agent_id": "uuid",
  "conversation_id": "uuid",
  "assistant_text": "### Goal: Launch beta\n\nDeadline in 3 days...",
  "thinking": null,
  "artifacts": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "agent_id": "uuid",
      "message_id": "uuid",
      "tool_call_id": "call_xyz",
      "name": "Goal Summary",
      "artifact_type": "document",
      "content": { "...": "..." },
      "content_size": 842,
      "summary": "Summary of goals approaching deadline",
      "render_inline": true,
      "created_at": "2025-01-15T10:00:00+00:00"
    }
  ],
  "messages": [
    { "role": "assistant", "content": "...", "tool_calls": null, "thinking": null, "input_tokens": 840, "output_tokens": 210 }
  ],
  "usage": {
    "total_input_tokens": 840,
    "total_output_tokens": 210,
    "model": "gpt-5.2"
  }
}
```

> **Note:** The text field is `assistant_text`, not `response`.

### Handling `requires_realm_assignment` (Sync)

The first time a user's agent runs, it may not yet have a privacy realm assigned. Personas returns this as a **200** (not an error status):

```javascript
const body = await res.json().catch(() => ({}));

if (body?.requires_realm_assignment) {
  return { status: 'needs_auth', auth_url: body.redirect_url };
}
if (!res.ok) {
  throw new Error(`Agent call failed: ${res.status}`);
}
return { status: 'completed', output_text: body.assistant_text };
```

**`requires_realm_assignment` response shape:**
```json
{
  "requires_realm_assignment": true,
  "agent_id": "uuid",
  "redirect_url": "https://radius.ofself.ai/authorize?client_id=...&sub_entity_key=...&redirect_uri=...",
  "message": "Authorize this automation agent once, then retry execution."
}
```

---

## 9. Agent Scope — What Data the Agent Can Access

The first event in every stream is `scope`. It tells you exactly what the agent is authorized to do for this user before any LLM output arrives.

```json
{
  "permissions": {
    "can_see_nodes":       true,
    "can_create_nodes":    false,
    "can_write_nodes":     false,
    "can_delete_nodes":    false,
    "can_propose":         false,
    "can_read_rels":       true,
    "can_create_rels":     false,
    "can_execute_plugins": false
  },
  "enabled_tools":     ["list_nodes", "get_node", "search_nodes", "list_relationships"],
  "selected_schemas":  [],
  "selected_node_ids": [],
  "realm_name":        "Personal"
}
```

You can also query scope at any time outside a run — see `POST /internal/headless/agents/<agent_id>/scope` in Section 11.

---

## 10. Data Flow End to End

```
┌─────────────────────────────────────────────────────────────────┐
│  1. USER NAVIGATES                                              │
│     POST /headless/context { conversation_id, context: "..." } │
│     Stored server-side — latest value wins                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  2. USER SENDS MESSAGE                                          │
│     POST /headless/run/stream { app_id, hmac_key,              │
│                                 paradigm_user_id, message, ... }│
│     X-Internal-Signature: sha256=HMAC(body, hmac_key)          │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  3. PERSONAS BACKEND AUTHENTICATES + PREPARES CONTEXT           │
│     • Verifies app_id + hash(hmac_key) + HMAC signature        │
│     • Resolves EP context (privacy realm, permissions)          │
│     → event: scope { permissions, enabled_tools, ... }         │
│     • Loads registered tools for this app                       │
│     • Loads silent context for this conversation                │
│     • Builds message history from DB                            │
│     • Builds full system prompt                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  4. AGENTIC LOOP  (repeats until no tool calls remain)          │
│     → event: thinking  (Claude only)                           │
│     → event: content   (LLM reasoning)                         │
│                                                                 │
│     LLM calls a tool:                                           │
│     → event: tool_call_start { id, name }                      │
│                                                                 │
│     Personas executes the tool:                                 │
│     • Paradigm tool  → Paradigm API                            │
│     • Custom tool    → decrypts secret, POSTs to your endpoint  │
│     → event: tool_result { tool_call_id, name, arguments,      │
│                             result }                            │
│     → event: paradigm_write (if agent wrote to Paradigm graph)  │
│     → event: artifact (if tool call produced structured data)   │
│                                                                 │
│     Result returned to LLM → next loop iteration               │
└──────────────────────────────┬──────────────────────────────────┘
                               │ (loop exits when LLM stops calling tools)
┌──────────────────────────────▼──────────────────────────────────┐
│  5. FINAL RESPONSE                                              │
│     → event: content  (final answer, streamed)                 │
│     → event: message_complete                                   │
│     → event: done { conversation_id, agent_id, usage }         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│  6. PERSISTENCE                                                 │
│     All messages saved to DB (full loop history + thinking)     │
│     All artifacts saved to DB                                   │
│     conversation_id + agent_id returned for next turn           │
│     callback_url POSTed to (if configured)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Agent Lifecycle — Pre-create, Update, Inspect

These endpoints let you manage the agent object independently from sending messages.

### Pre-create or Get an Agent

Create an agent before the user's first message so you have a stable `agent_id` to reference in subsequent calls.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "paradigm_user_id": "user-uuid",
    "agent_name": "My Coach",
    "system_prompt": "You are a goal coach...",
    "llm_provider": "ofself",
    "llm_model": "gpt-5.2",
    "temperature": 0.4,
    "web_search": false,
    "wikipedia_search": false,
    "description": "A coach that helps users track their goals",
    "app_name": "My App",
    "headless_app_id": "'$PERSONAS_APP_ID'"
  }'
```

**Response `201` (new agent) or `200` (existing):**
```json
{
  "agent_id": "uuid",
  "agent_name": "My Coach",
  "created": true
}
```

If an agent with `agent_name` already exists for this user, it returns the existing one with `"created": false`. Passing `agent_id` explicitly returns that agent without name lookup (idempotent).

### Update an Agent

Update a stored agent's configuration in-place. All fields are optional — only provided fields change.

```bash
curl -X PATCH https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "paradigm_user_id": "user-uuid",
    "system_prompt": "Updated system prompt...",
    "llm_model": "gpt-5.2",
    "temperature": 0.6,
    "agent_name": "My Coach v2",
    "description": "Updated description",
    "web_search": true,
    "wikipedia_search": false,
    "state_machine": { "states": ["idle", "active"], "initial": "idle" }
  }'
```

**Response `200`:**
```json
{
  "agent_id": "uuid",
  "agent_name": "My Coach v2",
  "updated_fields": ["system_prompt", "llm_model", "temperature", "agent_name", "tools_config"]
}
```

Updatable fields: `system_prompt`, `llm_provider`, `llm_model`, `temperature`, `web_search`, `wikipedia_search`, `description`, `agent_name`, `state_machine`.

### Get Agent Scope

Returns the agent's full Paradigm scope — the same structure as the streaming `scope` event, callable at any time outside a run.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID/scope \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "permissions": {
    "can_see_nodes": true,
    "can_create_nodes": false,
    "can_write_nodes": false,
    "can_delete_nodes": false,
    "can_propose": false,
    "can_read_rels": true,
    "can_create_rels": false,
    "can_execute_plugins": false
  },
  "enabled_tools": ["list_nodes", "get_node", "search_nodes"],
  "selected_schemas": [],
  "selected_node_ids": [],
  "realm_name": "Personal"
}
```

If the agent has no realm assigned yet, all fields return null/empty (no error):
```json
{ "permissions": null, "enabled_tools": [], "selected_schemas": [], "selected_node_ids": [], "realm_name": null }
```

### Get Agent EP Capabilities (Lighter)

Returns just `permissions` + `enabled_tools` — useful for quick permission checks without resolving schema names.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID/ep-capabilities \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "permissions": { "can_see_nodes": true, "can_create_nodes": false, "..." : "..." },
  "enabled_tools": ["list_nodes", "get_node"]
}
```

### Get Agent Usage

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID/usage \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "agent_id": "uuid",
  "conversation_count": 14,
  "total_input_tokens": 48200,
  "total_output_tokens": 12400
}
```

### Publish / Unpublish Agent as a Plugin

Publish an agent to make it discoverable in the Paradigm SDK plugin registry. Requires the agent to already have a `sub_entity_plugin_id` registered.

```bash
# Publish
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID/publish-plugin \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{ "message": "Agent published as plugin", "agent_id": "uuid", "is_published_as_plugin": true }
```

```bash
# Unpublish
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID/unpublish-plugin \
  ...same body...
```

**Response `200`:**
```json
{ "message": "Agent unpublished", "agent_id": "uuid", "is_published_as_plugin": false }
```

---

## 12. Conversation & History Management

### List Conversations

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/conversations \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{
    "app_id": "'$PERSONAS_APP_ID'",
    "hmac_key": "'$PERSONAS_HMAC_KEY'",
    "paradigm_user_id": "user-uuid",
    "agent_name": "My Coach",
    "include_messages": false
  }'
```

**Response `200`:** Last 50 conversations, newest first.
```json
{
  "conversations": [
    {
      "id": "convo-uuid",
      "title": "How do I improve my sleep?",
      "created_at": "2025-01-15T09:00:00+00:00",
      "updated_at": "2025-01-15T09:30:00+00:00"
    }
  ]
}
```

Pass `"include_messages": true` to get messages inline (user + assistant only, no tool rows):
```json
{
  "conversations": [
    {
      "id": "convo-uuid",
      "title": "...",
      "created_at": "...",
      "updated_at": "...",
      "messages": [
        { "role": "user", "content": "How do I improve my sleep?", "created_at": "..." },
        { "role": "assistant", "content": "Here are some strategies...", "created_at": "..." }
      ]
    }
  ]
}
```

### Get a Single Conversation

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/conversations/$CONVO_ID \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "id": "convo-uuid",
  "title": "How do I improve my sleep?",
  "created_at": "2025-01-15T09:00:00+00:00",
  "updated_at": "2025-01-15T09:30:00+00:00",
  "messages": [
    { "role": "user", "content": "How do I improve my sleep?", "created_at": "..." },
    { "role": "assistant", "content": "Here are some strategies...", "created_at": "..." }
  ]
}
```

### Conversation Timeline (Paradigm Write Events)

Returns an ordered log of everything the agent wrote to the user's Paradigm graph during a conversation. Useful for showing users what the agent actually did.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/conversations/$CONVO_ID/timeline \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "events": [
    {
      "tool": "create_node",
      "summary": "Created node 'Sleep Goal'",
      "success": true,
      "error": null,
      "timestamp": "2025-01-15T09:05:00+00:00",
      "meta": { "node_id": "n_abc123" }
    }
  ]
}
```

### Conversation State History

Returns the ordered list of state machine transitions if the agent uses a state machine.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/conversations/$CONVO_ID/state-history \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "transitions": [
    {
      "previous_state": "idle",
      "new_state": "active",
      "reason": "User started onboarding flow",
      "timestamp": "2025-01-15T09:02:00+00:00"
    }
  ],
  "current_state": "active"
}
```

### Debug: Inspect the LLM Context

Returns exactly what the LLM would see for this conversation — system prompt, full message history, and available tools. Useful for debugging agent behavior.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/conversations/$CONVO_ID/context \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{
  "messages": [
    { "role": "system", "content": "You are a goal coach..." },
    { "role": "user", "content": "How do I improve my sleep?" },
    { "role": "assistant", "content": "..." }
  ],
  "tools": [
    { "name": "list_nodes", "description": "...", "parameters": { "..." : "..." } }
  ],
  "model": "gpt-5.2"
}
```

---

## 13. Artifact Management

Artifacts are structured data objects created when the agent runs tools (e.g. creating a Paradigm node, generating a table, executing code). They're automatically saved during runs and can be fetched, listed, or deleted.

**Artifact object shape:**
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "agent_id": "uuid",
  "message_id": "uuid",
  "tool_call_id": "call_xyz",
  "name": "Goal Summary",
  "artifact_type": "document",
  "content": { "...": "..." },
  "content_size": 842,
  "summary": "Short description of what this artifact is",
  "render_inline": true,
  "created_at": "2025-01-15T10:00:00+00:00"
}
```

**`artifact_type` values:** `node_created`, `node_updated`, `proposal`, `tag_created`, `relationship`, `code_execution`, `document`, `data_table`, `custom`.

### List Artifacts for a Conversation

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/conversations/$CONVO_ID/artifacts \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{ "artifacts": [ { "...artifact object..." } ] }
```

### List All Artifacts for an Agent

All artifacts across all conversations for an agent, newest first.

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/agents/$AGENT_ID/artifacts \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{ "artifacts": [ { "...artifact object..." } ] }
```

### Get a Single Artifact

```bash
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/artifacts/$ARTIFACT_ID \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:** Full artifact object.

### Delete an Artifact

```bash
curl -X DELETE https://personas.ofself.ai/api/v1/internal/headless/artifacts/$ARTIFACT_ID \
  -H "Content-Type: application/json" \
  -H "X-Internal-Signature: sha256=<sig>" \
  -d '{"app_id": "'$PERSONAS_APP_ID'", "hmac_key": "'$PERSONAS_HMAC_KEY'", "paradigm_user_id": "user-uuid"}'
```

**Response `200`:**
```json
{ "message": "Artifact deleted" }
```

### Pinning Artifacts into a Message

Pass `artifact_ids` in a run request to inject artifact content into the message context. The agent will reason over the artifact content when forming its response.

```python
payload = {
    "app_id": PERSONAS_APP_ID,
    "hmac_key": PERSONAS_HMAC_KEY,
    "paradigm_user_id": "user-uuid",
    "message": "Based on this data, what should I focus on next?",
    "agent_name": "My Coach",
    "app_name": "My App",
    "artifact_ids": ["artifact-uuid-1", "artifact-uuid-2"],
}
```

---

## 14. Plugin Surface — Being Called by Other Apps

If you publish your agent as a Paradigm SDK plugin, the SDK calls Personas directly when another app invokes it. These endpoints use **Paradigm webhook signature auth** (`X-Paradigm-Signature`), not your HMAC key — you don't call them directly, but you need to know they exist when debugging invocation flows.

### Synchronous Plugin Invocation

Called by the Paradigm SDK broker.

**Request (from SDK to Personas):**
```http
POST /api/v1/plugin/invoke
X-Paradigm-Signature: sha256=<sig>
Content-Type: application/json

{
  "paradigm_user_id": "user-uuid",
  "sub_entity_key":   "my-coach",
  "message":          "What are my top goals?",
  "conversation_id":  "uuid (optional — continue existing)",
  "context_prompt":   "string (optional — ephemeral system prompt addition)"
}
```

**Response `200`:**
```json
{
  "response": "Your top goals this week are...",
  "thinking": null,
  "artifacts": [],
  "agent_id": "uuid",
  "conversation_id": "uuid",
  "sub_entity_key": "my-coach",
  "scope": {
    "permissions": { "..." : "..." },
    "enabled_tools": ["list_nodes", "..."],
    "selected_schema_ids": [],
    "selected_node_ids": [],
    "realm_name": "Personal"
  }
}
```

### Streaming Plugin Invocation

Same auth and body as synchronous, but returns an SSE stream with the same event types as `/headless/run/stream`.

```http
POST /api/v1/plugin/invoke/stream
X-Paradigm-Signature: sha256=<sig>
```

---

## 15. Automation — Background Celery Triggers

When a Paradigm SDK scheduled or event-driven automation targets Personas, the SDK's Celery worker calls this endpoint directly. Like the plugin surface, this uses Paradigm webhook signature auth — you configure it in the Paradigm SDK, not by calling it yourself.

**Request (from SDK Celery worker to Personas):**
```http
POST /api/v1/automation/run
X-Paradigm-Signature: sha256=<sig>
X-Paradigm-App-Id: <sdk-thirdparty-id>
Content-Type: application/json

{
  "automation_id":    "sdk-automation-uuid",
  "paradigm_user_id": "user-uuid",
  "action_config": {
    "agent_name":      "Research Analyst",
    "agent_id":        "uuid (takes priority over agent_name)",
    "headless_app_id": "headless-app-uuid",
    "app_name":        "Paradigm SDK Automation",
    "message":         "Run your daily analysis.",
    "system_prompt":   "optional override",
    "llm_provider":    "ofself",
    "llm_model":       "gpt-5.2",
    "temperature":     0.3,
    "conversation_id": "uuid (optional — continue existing)"
  }
}
```

**Response `200`:**
```json
{
  "status":          "completed",
  "output_text":     "Analysis complete. Here are the results...",
  "conversation_id": "uuid",
  "agent_id":        "uuid",
  "output_node_id":  null
}
```

If the agent has no realm assigned:
```json
{
  "status": "failed",
  "error": "requires_realm_assignment",
  "message": "Agent has no privacy realm assigned. User must authorize this agent first.",
  "agent_id": "uuid"
}
```
HTTP status: `403`.

---

## 16. Quick Reference — All Endpoints

All endpoints except `/register` require `app_id` + `hmac_key` in the body and `X-Internal-Signature: sha256=<hmac>` in the header, unless noted.

### App Management

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/internal/headless/apps/register` | Register app, get `app_id` + `hmac_key` — no auth required |
| `GET` | `/api/v1/internal/headless/apps/:app_id` | View app + registered tools (`hmac_key` as query param) |
| `PUT` | `/api/v1/internal/headless/apps/:app_id/tools` | Replace all tools |
| `PATCH` | `/api/v1/internal/headless/apps/:app_id/tools/:tool_name` | Update one tool |
| `DELETE` | `/api/v1/internal/headless/apps/:app_id/tools/:tool_name` | Remove a tool |
| `POST` | `/api/v1/internal/headless/apps/:app_id/secrets` | Add a secret |
| `DELETE` | `/api/v1/internal/headless/apps/:app_id/secrets/:secret_id` | Remove a secret |

### Agent Lifecycle

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/internal/headless/agents` | Create or get agent without sending a message |
| `PATCH` | `/api/v1/internal/headless/agents/:agent_id` | Update agent config in-place |
| `POST` | `/api/v1/internal/headless/agents/:agent_id/scope` | Full EP scope (permissions, tools, schemas, realm) |
| `POST` | `/api/v1/internal/headless/agents/:agent_id/ep-capabilities` | Permissions + enabled tools only |
| `POST` | `/api/v1/internal/headless/agents/:agent_id/usage` | Aggregate token usage |
| `POST` | `/api/v1/internal/headless/agents/:agent_id/publish-plugin` | Publish agent as SDK plugin |
| `POST` | `/api/v1/internal/headless/agents/:agent_id/unpublish-plugin` | Unpublish agent from SDK |

### Runtime

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/internal/headless/run` | Run agent synchronous — returns full JSON response |
| `POST` | `/api/v1/internal/headless/run/stream` | Run agent streaming — returns SSE ✅ recommended |

### Silent Context

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/internal/headless/context` | Upsert silent context for a conversation |
| `DELETE` | `/api/v1/internal/headless/conversations/:convo_id/context` | Clear silent context |

### Conversation & History

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/internal/headless/conversations` | List conversations for user + agent (up to 50) |
| `POST` | `/api/v1/internal/headless/conversations/:convo_id` | Get single conversation with full message history |
| `POST` | `/api/v1/internal/headless/conversations/:convo_id/timeline` | Ordered Paradigm write events for a conversation |
| `POST` | `/api/v1/internal/headless/conversations/:convo_id/state-history` | State machine transitions + current state |
| `POST` | `/api/v1/internal/headless/conversations/:convo_id/context` | Debug: exact LLM messages, tools, and model |
| `POST` | `/api/v1/internal/headless/conversations/:convo_id/artifacts` | List all artifacts for a conversation |

### Artifact Management

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/internal/headless/agents/:agent_id/artifacts` | All artifacts across all conversations for an agent |
| `POST` | `/api/v1/internal/headless/artifacts/:artifact_id` | Get single artifact |
| `DELETE` | `/api/v1/internal/headless/artifacts/:artifact_id` | Delete artifact |

### Plugin Surface (Paradigm SDK → Personas, uses `X-Paradigm-Signature`)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/plugin/invoke` | SDK invokes agent synchronously |
| `POST` | `/api/v1/plugin/invoke/stream` | SDK invokes agent with SSE stream |

### Automation (Celery → Personas, uses `X-Paradigm-Signature`)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/automation/run` | Celery worker fires a scheduled or event automation |

---

## Security Summary

| Concern | How It's Handled |
|---------|-----------------|
| Registration | Open — anyone can register; security is enforced per-app after |
| Request authenticity | Per-app HMAC-SHA256 signature on raw body — replay-resistant |
| Key storage | SHA-256 hash only in DB — plaintext key never stored |
| Key blast radius | Each app has its own key — one compromise doesn't affect others |
| Secret storage | AES-256 encrypted at rest (Fernet), server-side key |
| Secret transmission | Decrypted only at proxy time, injected into outbound header |
| LLM access to secrets | Impossible — secret injected after LLM produces the tool call |
| User data access | Scoped to user's Paradigm privacy realm — enforced by EP |
| Tool scope | Per-app — one app's tools cannot be invoked by another app |
| Plugin/automation auth | `X-Paradigm-Signature` HMAC over body, separate from per-app keys |
