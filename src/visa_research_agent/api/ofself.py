"""Reading a traveller's passport nationality from their Ofself identity (TODO item 55, step 3).

Ofself's developer platform is Paradigm. This app is registered there with one DLR request —
`nodes:read` on `work-authorization`, restricted to its `citizenships` field — and DECISIONS entry
180 and `CRUX.md` say why that is the whole of it. This module is the one place that reads it.

**What it returns is a default for the traveller to confirm, never a corridor.** The node may have
been parsed out of a CV by another app rather than stated by the person, and someone with two
citizenships chooses which passport a trip is on, so nothing here picks one (item 55, rule 3). An
identity that yields no nationality means *ask the traveller* — never the default traveller, which
belongs to the anonymous form alone (rule 4).

**What it does not do, deliberately:**
- **Guess.** A value that is not a country this program holds reference data for is returned as
  unrecognised. It is not matched loosely, and it is not dropped silently.
- **Decrypt.** The app holds no keypair (entry 180). A value that arrives encrypted is counted and
  never read as a country.
- **Store.** Nothing read here is written anywhere, and nothing is ever written back to Paradigm.
- **Retry.** A refused or lost authorisation is the user's decision, and is reported as such.
"""

import uuid

import httpx
from pydantic import Field

from visa_research_agent.api.countries import normalise_country
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.research.errors import VisaResearchError
from visa_research_agent.research.live_sources import transport_failure_reason

DEFAULT_BASE_URL = "https://api.ofself.ai"
WORK_AUTHORIZATION_SCHEMA = "work-authorization"
PAGE_SIZE = 100
"""`GET /nodes` caps a page at 100. `work-authorization` is one node per user, so one page is the
ordinary case, but more than one node is read correctly rather than assumed away.

Paging stops on a page that comes back short, not on `total`: live, on 2026-09-17, `total` was
`null` on every answer, though the developer guide shows a count."""

ENCRYPTED_VALUE_PREFIX = "paradigm_enc:"

AUTHORIZATION_CODES = frozenset(
    {"EP_NOT_FOUND", "EP_REVOKED", "EP_PAUSED", "EP_EXPIRED", "NO_AUTHORIZATION", "NO_PERMISSIONS"}
)
"""Every code Paradigm uses to say this user's grant to the app is gone or never existed. The
developer guide names two vocabularies — the `EP_*` codes and the older `NO_AUTHORIZATION` — so
both are handled."""


class OfselfError(VisaResearchError):
    """Raised when a traveller's Ofself identity could not be read."""


class OfselfUnavailable(OfselfError):
    """Paradigm could not be reached, refused the app's own credentials, or answered malformed."""


class OfselfAuthorizationLost(OfselfError):
    """The user has no active grant to this app: never given, revoked, paused or expired.

    The only honest response is to ask them to reconnect. It is never a reason to fall back to a
    default traveller.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class PassportNationalities(StrictModel):
    """What the traveller's identity says about their citizenships, for them to confirm."""

    nationalities: list[str] = Field(default_factory=list)
    """Alpha-2 codes, in the order recorded, without repeats. Empty means ask the traveller."""

    unrecognised: list[str] = Field(default_factory=list)
    """Recorded values that name no country this program holds reference data for."""

    encrypted_values: int = 0
    """Values that arrived encrypted, which this app cannot and does not read."""


class OfselfIdentity:
    """Reads one Paradigm user's identity on this app's behalf, within the grant they gave it."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key.strip():
            raise OfselfUnavailable("A Paradigm API key is required to read an Ofself identity")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def passport_nationalities(self, user_id: str) -> PassportNationalities:
        """The citizenships recorded in the user's `work-authorization`, normalised, unconfirmed."""

        try:
            user = str(uuid.UUID(user_id))
        except ValueError as exc:
            raise OfselfUnavailable("An Ofself user id must be a UUID") from exc

        values: list[object] = []
        offset = 0
        while True:
            page = await self._list_nodes(user, offset)
            nodes = page["nodes"]
            for node in nodes:
                values.extend(_citizenships_of(node))
            offset += len(nodes)
            if len(nodes) < PAGE_SIZE:
                break

        return _normalise(values)

    async def _list_nodes(self, user_id: str, offset: int) -> dict[str, list[object]]:
        headers = {
            "Accept": "application/json",
            "X-API-Key": self.api_key,
            "X-User-ID": user_id,
        }
        params: dict[str, str | int] = {
            "schema_id": WORK_AUTHORIZATION_SCHEMA,
            "fields": "id,value_json",
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        try:
            async with httpx.AsyncClient(
                transport=self.transport, timeout=self.timeout_seconds, headers=headers
            ) as client:
                response = await client.get(f"{self.base_url}/api/v1/nodes", params=params)
        except httpx.HTTPError as exc:
            raise OfselfUnavailable(
                f"Ofself could not be reached: {transport_failure_reason(exc)}"
            ) from exc

        if response.status_code != httpx.codes.OK:
            raise _refusal(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise OfselfUnavailable("Ofself answered with a body that is not JSON") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("nodes"), list):
            raise OfselfUnavailable("Ofself answered without a list of nodes")
        return payload


def _citizenships_of(node: object) -> list[object]:
    """A node's `citizenships`, or nothing where the field is absent, hidden or not a list."""

    if not isinstance(node, dict):
        return []
    value_json = node.get("value_json")
    if not isinstance(value_json, dict):
        return []
    citizenships = value_json.get("citizenships")
    return list(citizenships) if isinstance(citizenships, list) else []


def _normalise(values: list[object]) -> PassportNationalities:
    nationalities: list[str] = []
    unrecognised: list[str] = []
    encrypted = 0
    for value in values:
        if not isinstance(value, str) or not value.strip():
            continue
        if value.startswith(ENCRYPTED_VALUE_PREFIX):
            encrypted += 1
            continue
        try:
            code = normalise_country(value)
        except ValueError:
            if value not in unrecognised:
                unrecognised.append(value)
            continue
        if code not in nationalities:
            nationalities.append(code)
    return PassportNationalities(
        nationalities=nationalities, unrecognised=unrecognised, encrypted_values=encrypted
    )


def _refusal(response: httpx.Response) -> OfselfError:
    """Name why Paradigm refused, from the error code in the body rather than the status alone."""

    code, message = _error_of(response)
    if code in AUTHORIZATION_CODES:
        return OfselfAuthorizationLost(
            code, message or "This Ofself account has no active authorisation for this app"
        )
    if response.status_code == httpx.codes.UNAUTHORIZED:
        return OfselfUnavailable(
            f"Ofself refused this app's API key ({code or 'HTTP 401'}); check PARADIGM_API_KEY"
        )
    detail = f"{code}: {message}" if code and message else code or f"HTTP {response.status_code}"
    return OfselfUnavailable(f"Ofself could not provide the identity ({detail})")


def _error_of(response: httpx.Response) -> tuple[str | None, str | None]:
    """The code and message from either envelope Paradigm documents: under `error`, or flat."""

    try:
        body = response.json()
    except ValueError:
        return None, None
    if not isinstance(body, dict):
        return None, None
    nested = body.get("error")
    envelope = nested if isinstance(nested, dict) else body
    code = envelope.get("code")
    message = envelope.get("message")
    return (
        code if isinstance(code, str) else None,
        message if isinstance(message, str) else None,
    )
