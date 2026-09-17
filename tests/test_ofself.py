"""Reading a passport nationality from an Ofself identity (TODO item 55, step 3).

Nothing here reaches Paradigm: a fake answers through `httpx.MockTransport`, shaped as the
developer guide documents `GET /api/v1/nodes` and its two error envelopes.
"""

from collections.abc import Callable

import httpx
import pytest

from visa_research_agent.api.ofself import (
    AUTHORIZATION_CODES,
    OfselfAuthorizationLost,
    OfselfIdentity,
    OfselfUnavailable,
)

pytestmark = pytest.mark.anyio

USER = "2f0c9b8e-4d7a-4e61-9a1b-3c5d7e9f1a2b"
API_KEY = "ofs_tp_test.secret"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def identity(handler: Callable[[httpx.Request], httpx.Response]) -> OfselfIdentity:
    return OfselfIdentity(
        API_KEY, base_url="https://paradigm.test", transport=httpx.MockTransport(handler)
    )


def nodes(*value_jsons: dict[str, object], total: int | None = None) -> httpx.Response:
    listed = [{"id": f"node-{i}", "value_json": value} for i, value in enumerate(value_jsons)]
    return httpx.Response(
        200, json={"nodes": listed, "total": len(listed) if total is None else total}
    )


async def test_it_asks_paradigm_for_this_users_work_authorization_as_this_app() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return nodes({"citizenships": ["IN"]})

    await identity(handler).passport_nationalities(USER)

    (request,) = seen
    assert request.url.path == "/api/v1/nodes"
    assert request.url.params["schema_id"] == "work-authorization"
    assert request.headers["X-API-Key"] == API_KEY
    assert request.headers["X-User-ID"] == USER


async def test_citizenships_are_normalised_whether_recorded_as_alpha_2_or_alpha_3() -> None:
    """The schema allows either; everything past the edge is keyed on alpha-2."""

    found = await identity(lambda _: nodes({"citizenships": ["IND", "gb"]})).passport_nationalities(
        USER
    )

    assert found.nationalities == ["IN", "GB"]


async def test_every_citizenship_is_offered_and_none_is_chosen() -> None:
    """Rule 3: a traveller with two passports picks one; the adapter keeps both, in order."""

    found = await identity(
        lambda _: nodes({"citizenships": ["PH", "US"]}, {"citizenships": ["USA", "IN"]})
    ).passport_nationalities(USER)

    assert found.nationalities == ["PH", "US", "IN"]


@pytest.mark.parametrize(
    "value_json",
    [{}, {"citizenships": []}, {"citizenships": None}, {"citizenships": "IN"}],
    ids=["field hidden or unrecorded", "empty", "null", "not a list"],
)
async def test_an_identity_that_yields_no_nationality_means_ask(
    value_json: dict[str, object],
) -> None:
    """Rule 4: nothing usable is an empty answer, never the default traveller.

    The sandbox users have full access, so a field the user hid is only ever seen here.
    """

    found = await identity(lambda _: nodes(value_json)).passport_nationalities(USER)

    assert found.nationalities == []


async def test_no_work_authorization_at_all_means_ask() -> None:
    found = await identity(lambda _: nodes()).passport_nationalities(USER)

    assert found.nationalities == []


async def test_a_value_naming_no_known_country_is_reported_and_never_guessed() -> None:
    found = await identity(
        lambda _: nodes({"citizenships": ["Atlantis", "IN", "Atlantis", 42]})
    ).passport_nationalities(USER)

    assert found.nationalities == ["IN"]
    assert found.unrecognised == ["Atlantis"]


async def test_an_encrypted_value_is_counted_and_never_read_as_a_country() -> None:
    """The app holds no keypair, so ciphertext must not reach the country check at all."""

    found = await identity(
        lambda _: nodes({"citizenships": ["paradigm_enc:v2:AAAA", "GB"]})
    ).passport_nationalities(USER)

    assert found.nationalities == ["GB"]
    assert found.unrecognised == []
    assert found.encrypted_values == 1


async def test_more_nodes_than_one_page_are_all_read() -> None:
    offsets: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        offset = request.url.params["offset"]
        offsets.append(offset)
        if offset == "0":
            return nodes({"citizenships": ["IN"]}, total=2)
        return nodes({"citizenships": ["GB"]}, total=2)

    found = await identity(handler).passport_nationalities(USER)

    assert offsets == ["0", "1"]
    assert found.nationalities == ["IN", "GB"]


@pytest.mark.parametrize("code", sorted(AUTHORIZATION_CODES))
@pytest.mark.parametrize("nested", [True, False], ids=["under error", "flat"])
async def test_a_lost_authorization_is_named_by_its_code(code: str, nested: bool) -> None:
    """The guide documents both envelopes, and both vocabularies of authorization code."""

    error = {"code": code, "message": "no active authorization"}
    body = {"error": error} if nested else error

    with pytest.raises(OfselfAuthorizationLost) as raised:
        await identity(lambda _: httpx.Response(403, json=body)).passport_nationalities(USER)

    assert raised.value.code == code


async def test_a_refused_api_key_is_the_apps_problem_not_the_users() -> None:
    body = {"error": {"code": "INVALID_API_KEY", "message": "Key not found"}}

    with pytest.raises(OfselfUnavailable, match="PARADIGM_API_KEY"):
        await identity(lambda _: httpx.Response(401, json=body)).passport_nationalities(USER)


async def test_any_other_refusal_is_reported_with_its_code() -> None:
    body = {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}}

    with pytest.raises(OfselfUnavailable, match="RATE_LIMIT_EXCEEDED") as raised:
        await identity(lambda _: httpx.Response(429, json=body)).passport_nationalities(USER)

    assert not isinstance(raised.value, OfselfAuthorizationLost)


async def test_a_transport_failure_with_an_empty_message_still_says_what_happened() -> None:
    """Entry 122: `ConnectTimeout` carries no message, so the class name is the only fact."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("", request=request)

    with pytest.raises(OfselfUnavailable, match="ConnectTimeout"):
        await identity(handler).passport_nationalities(USER)


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, text="<html>maintenance</html>"),
        httpx.Response(200, json={"results": []}),
    ],
    ids=["not JSON", "no node list"],
)
async def test_a_malformed_answer_is_unavailable_not_empty(response: httpx.Response) -> None:
    """An empty answer means "ask the traveller"; a broken one must not be mistaken for it."""

    with pytest.raises(OfselfUnavailable):
        await identity(lambda _: response).passport_nationalities(USER)


async def test_a_user_id_that_is_not_a_uuid_is_refused_before_anything_is_sent() -> None:
    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return nodes()

    with pytest.raises(OfselfUnavailable, match="UUID"):
        await identity(handler).passport_nationalities("alice")

    assert sent == []


def test_an_adapter_without_an_api_key_cannot_be_built() -> None:
    with pytest.raises(OfselfUnavailable, match="API key"):
        OfselfIdentity("  ")
