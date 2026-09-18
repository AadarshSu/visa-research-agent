# Integrating Your App with Personas

> A lifecycle guide for external developers building apps that talk to a Personas agent.
> It follows a request from end to end: **register → declare an agent → the agent boots → run it → consume the stream → render the result.**

---

**Base URLs**

| | |
|---|---|
| **API (prod)** | `https://personas.ofself.ai` |
| **Frontend (prod)** | `https://personas.ofself.ai` |
| **API base path** | all endpoints below are under `/api/v1` (e.g. `…/api/v1/internal/headless/run/stream`) |

---

**Two ways to use this guide**

It is served by the deployment it describes, so the copy you fetch always matches the
code you are calling — no cloning, no auth:

```bash
curl https://personas.ofself.ai/api/v1/docs                    # the whole guide
curl https://personas.ofself.ai/api/v1/docs/sections           # section slugs
curl "https://personas.ofself.ai/api/v1/docs?section=register-your-app"
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

Personas runs an **agent** on behalf of one of your users. The agent reasons with an LLM and acts on the user's data in **Paradigm** by writing and running Python in a sandbox. Your app never touches Paradigm directly through Personas — the agent does, and only within the permissions (the *Exposure Profile*, "EP") the user granted.

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
curl -X POST https://personas.ofself.ai/api/v1/internal/headless/apps/register \
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
curl -X PATCH https://personas.ofself.ai/api/v1/internal/headless/apps/<app_id> \
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

---

## 3. The identity & permission model (read before declaring an agent)

This is the part most integrations get wrong, so be precise about who is who:

- **Personas holds the API key; your app brings its own Paradigm identity.** Personas is a registered Paradigm app (it holds the Paradigm API key). Your app should ALSO be its own registered Paradigm app — you tell Personas its `client_id` via `paradigm_client_id` at registration (§1). Agents you drive are then capped by **both** grants (below). If you skip `paradigm_client_id`, your app is a pure Personas tenant and agents run under Personas' ceiling alone.
- **Each agent is a Paradigm sub-entity** under Personas, keyed by its slug (`sub_entity_key`, derived from `agent_name`).
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

- **resources:** `nodes`, `relationships`, `plugins` (the resources an agent typically narrows; `discovery` and `activity` are also valid resources but rarely part of an agent's consent ceiling)
- **node verbs:** `read`, `create`, `edit`, `delete`, `propose` (`edit_content` is a legacy alias the SDK now canonicalizes to `edit`)
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
| `agent_name` | ✅ | Stable name → becomes the agent's `sub_entity_key` slug. |
| `system_prompt` | ✅ | **Required.** The agent's identity/instructions, stored permanently. Creation fails with `VALIDATION_ERROR` without it. |
| `app_name` | — | Your app's display name (shown in the user's data console). |
| `description` | — | Human description. |
| `consent` | — | Permission ceiling (§3.1). |
| `llm_provider` | — | Default `"ofself"`. |
| `llm_model` | — | Default `"gpt-5.5"`. |
| `temperature` | — | Default `0.4`. |
| `web_search` / `wikipedia_search` | — | Booleans → folded into the agent's `tools_config`. |

**Response:**

```json
{ "agent_id": "…", "agent_name": "My Coach", "created": true }
```

It's idempotent on `(user, agent_name)`: a second call returns the existing agent with `"created": false`. The stored `system_prompt` and `tools_config` are **locked at creation** — pass a per-request `system_prompt` on `/run` to override for a single turn (§5). `llm_provider` / `llm_model` are the exception: any call that carries them **updates the stored agent** (see §5's caution — a one-off model override silently becomes permanent).

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

## 4. The agent boots — anatomy of its system prompt

When a run starts, Personas builds the agent's system prompt **fresh, in layers**, every turn. You don't send this prompt — Personas assembles it — but understanding it tells you exactly what the agent knows and can do:

```
┌─ _ARTIFACT_STRATEGY_PROMPT ─────────────────────────────────────────┐
│ How to use the execute_code sandbox, the RestrictedPython rules,     │
│ the shape of Paradigm node data, error-recovery discipline,          │
│ and how/when to persist artifacts.                                   │
├─ agent.system_prompt ───────────────────────────────────────────────┤
│ YOUR agent's own instructions. Override per-request with the         │
│ `system_prompt` field (see §5) to steer behaviour or output shape.   │
├─ state-machine block (optional) ────────────────────────────────────┤
│ Only present if the agent has a state machine; lists the current     │
│ state and allowed transitions.                                       │
├─ context block (DYNAMIC — fetched from Paradigm at boot) ────────────┤
│ Built from the live Exposure Profile (GET /third-party/me):          │
│   • which verbs the agent has (read / create / edit / propose /      │
│     delete / execute_plugins)                                        │
│   • which SCHEMAS are in scope — WITH their field definitions, so    │
│     the agent knows the exact value_json shape to read/write         │
│   • pinned nodes and the realm name                                  │
├─ _RESPONSE_FORMATTING_PROMPT ───────────────────────────────────────┤
│ Markdown rules + interactive widget syntax (widget:choice,           │
│ widget:node, widget:schema) the agent can emit for the UI.           │
└─────────────────────────────────────────────────────────────────────┘
```

Two consequences worth internalizing:

- **The agent's capabilities are not hard-coded — they are fetched from the EP at runtime.** If the EP is empty or misconfigured, the agent is told it can do *nothing* (the permission computation fails secure and denies all). An agent that "sees 0 schemas" almost always means a broken/deactivated EP, not a Personas bug.
- The agent has **one real tool: `execute_code`.** It does not call `read_nodes` as a named function — it writes Python that calls `paradigm.list_nodes(...)` inside the sandbox. The schema field definitions injected above are how it knows what to write.

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
| `system_prompt` | — | **Per-request override** of the agent's instructions (single turn). **Required** if this call auto-creates the agent. The strongest lever for steering output shape. |
| `consent` | — | Permission ceiling (§3.1), applied only when the agent is created on this call. |
| `llm_provider` / `llm_model` / `temperature` | — | Defaults `ofself` / `gpt-5.5` / `0.4`. **Caution:** `llm_provider`/`llm_model` are NOT creation-only — if passed on any run, they are **persisted onto the agent** when they differ from what's stored. Omit them to keep the agent's config; `temperature` truly applies only at creation. |
| `web_search` / `wikipedia_search` | — | Booleans → agent `tools_config`, at creation. |
| `return_to` | — | URL to send the user back to after the authorization handshake (§3.3). |
| `client_id` | — | **Ignored** (a per-request `client_id` is no longer read). Your app's Paradigm identity is the `paradigm_client_id` on your registration record (§1, §3), not a run-body field. |
| `artifact_ids` | — | Pin existing artifacts into context. |
| `callback_url` | — | Optional completion callback. |
| `debug` | — | `true` adds `debug` events (raw request/response summaries). |

### Response

An SSE stream (`Content-Type: text/event-stream`). The server emits a `: heartbeat` comment during long silences to keep proxies from dropping the connection — ignore lines starting with `:`.

---

## 6. Consume the stream — event catalog

Each event is `event: <type>\ndata: <json>\n\n`. Subscribe by type:

| Event | When | Payload | What to do with it |
|---|---|---|---|
| `scope` | First, before the LLM | `permissions`, `enabled_tools`, `selected_schema_ids`, `selected_node_ids`, `realm_name`, `force_read_only` | Optional: show what the agent can access this run. |
| `thinking` | During reasoning (Claude models) | `{text}` — incremental | Render as a dim "thinking…" stream, separate from the answer. |
| `content` | The final answer | `{text}` — incremental tokens | **This is the answer.** Append chunks to render live. |
| `tool_call_start` | Agent invokes a tool | `{id, name}` | Show "running code…" / a spinner. |
| `tool_result` | Tool finished (incl. `execute_code`) | `{tool_call_id, name, arguments, result, exec_duration_ms}` | Code stdout/output lives in `result` (see §7). |
| `message_complete` | A full message is finalized | `{role, content, thinking, tool_calls, input_tokens, output_tokens, llm_provider, llm_model, error, exec_duration_ms}` | Authoritative per-message record; good for token accounting. |
| `paradigm_write` | The agent mutated Paradigm | `{tool, summary, success, error, timestamp, tool_call_id, meta}` | Surface "Created node X" / "Proposal pending". |
| `artifact` | A structured artifact was produced | full artifact dict (see §7) | **Render by `artifact_type`.** |
| `artifact_saved` | `save_artifact()` ran inside code | `{name, artifact_type, id, size_chars, updated}` | Lightweight notice that an artifact exists. |
| `state_change` | State machine transitioned | `{previous_state, new_state, reason, timestamp}` | Update any state UI. |
| `debug` | Only if `debug:true` | `{type, payload}` | Diagnostics. |
| `done` | End of run | `{conversation_id, agent_id, usage:{input_tokens, output_tokens, total_tokens}}` | Persist `conversation_id`; record usage. |
| `error` | Failure | `{message}` | Surface and stop. |

### Thinking vs. answer vs. code output — how to tell them apart

- **Thinking** → `thinking` events. Render separately/dimmed.
- **Final answer** → `content` events. This is the user-facing text.
- **Code execution output** is **not** streamed token-by-token (the sandbox runs synchronously). Its stdout/result arrives as a block in the `tool_result` event and in the `role:"tool"` `message_complete`, as JSON: `{"success": true, "data": {"stdout": "...", "saved_artifacts": [...], "proposals_created": [...]}}`.

---

## 7. Render the result

> **There is no `response_format` / JSON-schema enforcement.** If your app does nothing, the default output is **free-text markdown** streamed via `content`. Plan your rendering around that, and use the levers below when you need structure.

From weakest to strongest control:

1. **Default — free text.** Concatenate `content` chunks, render as markdown. The prompt also permits interactive widgets (`widget:choice`, `widget:node`, `widget:schema`) inline.
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

4. **Paradigm nodes / proposals — schema-validated.** For data the agent writes, schemas validate `value_json` server-side. Writes surface as `artifact` + `paradigm_write`. Note the **propose vs. write** distinction: when the agent only has `propose` rights, it creates a **proposal** (pending the user's approval) rather than mutating data directly.

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

Notes: `include_messages` returns only `user`/`assistant` messages with content (tool traffic is filtered). If your app prepends context to each user message (a data snapshot, instructions), remember that history returns the **full stored content** — strip your preamble before display, and set `conversation_title` explicitly so list titles aren't the preamble. The DELETE route was added 2026-08-12; a deployment predating it answers `405` — treat that as "not yet supported", not an error.

### Clearing silent context
`DELETE /internal/headless/conversations/<id>/context` (body `{ paradigm_user_id }`) clears a conversation's silent context without deleting the thread.

### Automations (scheduled agents)
Create one via `POST /agents/<agent_id>/automations` with a cron `trigger_config`. This registers a **scheduled automation in Paradigm**, not in Personas. When it fires, Paradigm's worker calls Personas back (signed) at `/internal/automation/run` with the `action_config` (agent, message, model). The automation runs under the agent's **own sub-entity EP** — if that EP is deactivated, the run silently produces nothing. Manage with `GET` / `DELETE` / `.../toggle` on the same route.

> **Creating/editing automations is governed by the EP verb — nothing else.** The agent's grant must hold `automations:write` (create/edit) or `automations:execute` (trigger/inspect). The agent's sub-entity EP **is** the per-agent grant, so the grant is the opt-in — there is no separate Personas-side flag. Grant `automations:write` in the realm/consent and the agent (including one creating automations from its own code via `paradigm.create_automation(...)`) can create them; grant only `execute` and it can trigger/inspect but not create/edit. (Earlier builds also required a `tools_config.automations_manage` opt-in; that redundant second gate was removed — the Scope panel now matches the realm/EP grant.) The Paradigm-side automation *callback endpoint* is registered for you automatically the first time an automation-capable agent runs — you don't set it up.

### Plugins
Two senses: (a) the agent can **call** Paradigm plugins from code (`paradigm.execute_plugin(...)`), gated by an `execute_plugins` EP verb; (b) an agent can itself be **published as** a discoverable plugin (`.../publish-plugin`) and invoked by other apps via `/internal/headless/invoke`.

### Error model
Errors come back as either an HTTP error response or an `error` SSE event, with a code + message. Common codes:
`VALIDATION_ERROR` (400), `UNAUTHORIZED` (401, bad signature/key), `NOT_FOUND` (404, e.g. unknown `conversation_id`), `AGENT_ERROR` (500, run failed), `AGENT_EXCEEDS_CALLING_APP` (403, agent's grant exceeds a *calling app's* grant on the plugin/broker path — auto-repaired; not seen in the basic embedded flow). Also handle the non-error `requires_realm_assignment` branch (§3).

---

## 10. Full worked example — a streaming SSE client

A complete, copy-pasteable Python client: signs the request, opens the stream, dispatches every event type, accumulates the answer, and collects artifacts.

```python
import hashlib, hmac, json, requests

PERSONAS_HOST = "https://personas.ofself.ai"
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
| POST | `/internal/headless/agents` | Pre-create/fetch an agent (`system_prompt` required) → `{agent_id, created}`. |
| POST | `/internal/headless/list-agents` | A user's active agents. Body `{paradigm_user_id}` → `{agents: [{id, name, description, slug, has_realm, sub_entity_plugin_id}]}`. `has_realm: false` = created but not yet authorized (§3.3). |
| POST | `/internal/headless/run/stream` | **Run, streaming (use this for UX).** |
| POST | `/internal/headless/run` | Run, blocking (final JSON only). |
| POST | `/agents/<id>/automations` | Create a scheduled automation. |
| POST | `/internal/headless/invoke` | Invoke an agent published as a plugin. |
| POST | `/internal/headless/conversations` | List a user+agent's conversations (`include_messages` optional). |
| POST | `/internal/headless/conversations/<id>` | Full thread with messages. |
| DELETE | `/internal/headless/conversations/<id>` | Delete a thread (added 2026-08-12; older deploys 405). |

**Auth (every runtime call):** body `app_id` + `hmac_key`, header `X-Internal-Signature: sha256=hmac_sha256(raw_body, hmac_key)`.

**Golden rules**
- User-facing? Use `/run/stream`. Blocking `/run` is why it "feels slow."
- The answer is the `content` stream; structured data is the `artifact` stream; code output is in `tool_result`.
- Persist `conversation_id` from `done` to continue threads; set `conversation_title` on new ones.
- Never pass `llm_provider`/`llm_model` casually — they persist onto the agent.
- Handle `requires_realm_assignment` — it's a one-time authorization handshake (§3.3), not an error.
- The agent can only ever do `(its consent ceiling) ∩ (what the user authorized for its realm)` — and, for bound tenants, `∩ (the user's grant to YOUR app)`. No authorization anywhere ⇒ agent can do nothing.
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
