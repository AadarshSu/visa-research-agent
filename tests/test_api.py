from collections.abc import AsyncIterator

import httpx
import pytest

from visa_research_agent.api.app import create_app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


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
        "united-states",
        "france",
    ]


@pytest.mark.anyio
async def test_unsupported_destination_returns_helpful_error(client: httpx.AsyncClient) -> None:
    response = await client.post("/visa-plans", json={"destination": "canada"})

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "message": "Unsupported destination: canada",
        "supported_destinations": ["singapore", "japan", "united-states", "france"],
    }


@pytest.mark.anyio
async def test_supported_but_unimplemented_destination_is_explicit(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/visa-plans", json={"destination": " Singapore "})

    assert response.status_code == 503
    assert "Phase 2" in response.json()["detail"]["message"]
