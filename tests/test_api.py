from collections.abc import AsyncIterator

import httpx
import pytest

from visa_research_agent.api.app import create_app
from visa_research_agent.api.dependencies import (
    get_automatic_destinations,
    get_visa_plan_service,
)
from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.domain.models import RuntimePolicy

OFFLINE_POLICY = RuntimePolicy(
    schema_version=1,
    source_mode="fixtures",
    extraction_mode="fixture",
    source_cache_ttl_hours=24.0,
    source_maximum_stale_hours=168.0,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[httpx.AsyncClient]:
    # Pin the policy so these tests never depend on the committed runtime.yaml or reach a network.
    # Both modules import the loader by name, so each reference needs replacing.
    for module in ("dependencies", "routes"):
        monkeypatch.setattr(
            f"visa_research_agent.api.{module}.get_runtime_policy",
            lambda: OFFLINE_POLICY,
        )
    get_visa_plan_service.cache_clear()
    get_automatic_destinations.cache_clear()
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    get_visa_plan_service.cache_clear()
    get_automatic_destinations.cache_clear()


@pytest.mark.anyio
async def test_health_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_destinations_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/destinations")

    assert response.status_code == 200
    # Under `configured` this is the hand-written registry, in its own order.
    assert [item["slug"] for item in response.json()["destinations"]] == [
        "singapore",
        "japan",
        "vietnam",
        "brazil",
        "china",
        "united-states",
        "france",
    ]
    assert response.json()["destinations"][0]["status"] == "available"


@pytest.mark.anyio
async def test_research_interface_is_available(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert 'id="plan-form"' in response.text
    assert "/static/styles.css?v=" in response.text
    assert "/static/app.js?v=" in response.text
    assert "Generate Plan" in response.text
    assert "Singapore" in response.text


@pytest.mark.anyio
async def test_unsupported_destination_returns_helpful_error(client: httpx.AsyncClient) -> None:
    response = await client.post("/visa-plans", json={"destination": "canada"})

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "message": "Unsupported destination: canada",
        "supported_destinations": [
            "singapore",
            "japan",
            "vietnam",
            "brazil",
            "china",
            "united-states",
            "france",
        ],
    }


@pytest.mark.anyio
async def test_singapore_fixture_plan_is_returned(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/visa-plans", json={"destination": " Singapore "})

    assert response.status_code == 200
    plan = response.json()
    assert plan["destination"] == "Singapore"
    assert plan["visa_required"] is True
    assert plan["visa_type"] == "Entry visa for a social visit (tourism)"
    assert plan["requirements"]
    assert plan["application_document_source_ids"] == ["sg_ica_india_visa_details"]
    assert all("category" not in requirement for requirement in plan["requirements"])
    assert all(
        "sg_ica_india_visa_details" in requirement["source_ids"]
        for requirement in plan["requirements"]
    )
    assert 4 <= len(plan["application_steps"]) <= 8
    assert all(
        {
            "title",
            "action",
            "timing",
            "source_ids",
            "link_target",
            "link_source_id",
        }
        == step.keys()
        for step in plan["application_steps"]
    )
    assert any(step["link_target"] == "application_route" for step in plan["application_steps"])
    assert len(plan["sources"]) == 5
    assert plan["last_checked"] == "2026-08-06T11:30:00Z"


@pytest.mark.anyio
async def test_supported_but_unimplemented_destination_is_explicit(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/visa-plans", json={"destination": "france"})

    assert response.status_code == 503
    assert response.json()["detail"]["message"] == (
        "Visa-plan generation for France is not available yet."
    )


@pytest.mark.anyio
async def test_the_interface_lets_a_traveller_be_described(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    for field in ('id="nationality"', 'id="residence"', 'id="purpose"'):
        assert field in response.text
    # The default the interface opens on, so an unchanged form reproduces the fixture baseline.
    assert '<option value="IN" selected>' in response.text
    assert '<option value="GB" selected>' in response.text
    assert '<option value="business"' in response.text


@pytest.mark.anyio
async def test_a_request_may_name_a_different_traveller(client: httpx.AsyncClient) -> None:
    """The fixture is recorded for one traveller, so a different one must be refused clearly
    rather than answered with the wrong person's plan."""

    response = await client.post(
        "/visa-plans",
        json={
            "destination": "singapore",
            "traveller": {"passport_nationality": "CN", "country_of_residence": "AE"},
        },
    )

    assert response.status_code == 503
    assert "could not be generated safely" in response.json()["detail"]["message"]


@pytest.mark.anyio
async def test_a_country_with_no_reference_data_is_rejected_before_anything_runs(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/visa-plans",
        json={
            "destination": "singapore",
            "traveller": {"passport_nationality": "Atlantis", "country_of_residence": "GB"},
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_the_interface_does_not_describe_one_particular_traveller(
    client: httpx.AsyncClient,
) -> None:
    """The page used to announce it researched an Indian passport holder living in Edinburgh.

    Any traveller can be asked about now, so copy naming one is simply wrong.
    """

    response = await client.get("/")

    for hardcoded in ("Edinburgh", "Indian passport holder", "resident in the UK"):
        assert hardcoded not in response.text


@pytest.mark.anyio
async def test_every_known_country_can_be_asked_for_when_destinations_are_automatic(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Destinations stop being the handful in `destinations.yaml`.

    An unconfigured country is researched when it is asked for, so offering only the configured
    ones would hide most of what the agent can actually do.
    """

    automatic = OFFLINE_POLICY.model_copy(update={"destination_mode": "automatic"})
    for module in ("dependencies", "routes"):
        monkeypatch.setattr(
            f"visa_research_agent.api.{module}.get_runtime_policy", lambda: automatic
        )

    slugs = [item["slug"] for item in (await client.get("/destinations")).json()["destinations"]]

    assert "united-arab-emirates" in slugs
    assert "thailand" in slugs
    assert len(slugs) == len(get_country_registry().countries)
    # Nothing is offered that cannot be acted on.
    assert all(
        item["status"] == "available"
        for item in (await client.get("/destinations")).json()["destinations"]
    )


@pytest.mark.anyio
async def test_a_passport_of_the_destination_is_turned_away_before_anything_is_spent(
    client: httpx.AsyncClient,
) -> None:
    """A national of the destination has no visa to research, so there is no guidance to find.

    Left alone this searched, crawled and spent two model calls to arrive at a refusal — slow, paid
    for, and reading as a fault rather than as the question being the wrong one. It is not a claim
    about entry rights: it says only what this agent researches.
    """

    response = await client.post(
        "/visa-plans",
        json={
            "destination": "singapore",
            "traveller": {
                "passport_nationality": "SG",
                "country_of_residence": "GB",
                "travel_purpose": "tourism",
            },
        },
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["status"] == "not_applicable"
    assert "own nationals do not apply" in detail["message"]


@pytest.mark.anyio
async def test_the_same_corridor_for_another_passport_is_still_researched(
    client: httpx.AsyncClient,
) -> None:
    """The guard must be narrow: only the passport matches the destination, never the residence.

    Applying from inside the destination is ordinary — in-country applications exist — so a resident
    of the destination holding another passport must still get a plan.
    """

    response = await client.post(
        "/visa-plans",
        json={
            "destination": "singapore",
            "traveller": {
                "passport_nationality": "IN",
                "country_of_residence": "SG",
                "travel_purpose": "tourism",
            },
        },
    )

    assert response.status_code != 422
