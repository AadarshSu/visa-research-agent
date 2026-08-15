from collections.abc import AsyncIterator

import httpx
import pytest

from visa_research_agent.api.app import create_app
from visa_research_agent.api.dependencies import get_visa_plan_service
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
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    get_visa_plan_service.cache_clear()


@pytest.mark.anyio
async def test_health_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_destinations_endpoint(client: httpx.AsyncClient) -> None:
    response = await client.get("/destinations")

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["destinations"]] == [
        "singapore",
        "japan",
        "vietnam",
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
    assert "Generate fixture plan" in response.text
    assert "Singapore" in response.text


@pytest.mark.anyio
async def test_unsupported_destination_returns_helpful_error(client: httpx.AsyncClient) -> None:
    response = await client.post("/visa-plans", json={"destination": "canada"})

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "message": "Unsupported destination: canada",
        "supported_destinations": ["singapore", "japan", "vietnam", "united-states", "france"],
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
