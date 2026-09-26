# Ofself's own documentation

Snapshots of Ofself's documentation, kept so a session can read them without this conversation's
history. **They are Ofself's words, not this project's**, and they go stale.

| File | What it is | Where it came from |
| --- | --- | --- |
| [PARADIGM_DEVELOPER_GUIDE.md](PARADIGM_DEVELOPER_GUIDE.md) | Paradigm's developer guide: auth, nodes, schemas, DLR, exposure profiles, encryption, plugins | Pasted by the owner. The hosted copy is a JavaScript page that can't be fetched, and `paradigm-cli` 0.5.0 doesn't ship it |
| [PERSONAS_GUIDE.md](PERSONAS_GUIDE.md) | Personas' guide to running agents in headless mode | Two current Ofself developer guides. The *Personas App Integration Guide* comes first, as `https://personas.ofself.com/api/v1/docs?format=md` served it on **2026-09-23**; **that endpoint is authoritative for it**, since it's versioned with Personas' deployment, and it changes often — it grew from 589 lines to 1,321 in five days. After it is the *Personas Headless Agent API*, the owner's copy of 2026-09-18, which the endpoint doesn't serve. The two disagree in places (feedback 8.9–8.13) |

**Both were filled in by the owner on 2026-09-18; the Personas guide's first half was refreshed from the live endpoint on 2026-09-23.** Date each snapshot at the top of its file when
you refresh it.

**Where the guides are wrong, the live platform wins.** Everything checked against the live API or
CLI is in [OFSELF_FEEDBACK.md](../../OFSELF_FEEDBACK.md). Read it before trusting a guide on:
- paging (`total` is `null`)
- the error formats
- where the DLR lives
- sign-in, which the guide shows only through SDK helpers. The real flow and the `sid_code`
  exchange are in feedback §9.

**This project's own Ofself facts live elsewhere:**
- [CRUX.md](../../CRUX.md): the app's design as an Ofself app, including its DLR.
- [DECISIONS.md](../../DECISIONS.md) entry 180: why it reads one field and writes nothing.
- [TODO.md](../../TODO.md) item 55: what is built, what is left, the sandbox user and how to run
  sign-in. The registered app's id and client id are in [PROJECT_HANDOFF.md](../../PROJECT_HANDOFF.md).
- The code: `api/ofself.py` (the Paradigm adapter), `api/signin.py` (sign-in and the session),
  `api/countries.py` (the shared country check).

The `paradigm` CLI is installed at `~/.local/bin/paradigm` and logged in as the owner. The app's API
key is in `.env` as `PARADIGM_API_KEY`, and the CLI's own copy is in `.paradigm/secrets.toml`,
which is gitignored.
