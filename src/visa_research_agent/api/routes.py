"""HTTP routing kept deliberately thin around the future workflow."""

from fastapi import APIRouter, HTTPException, status

from visa_research_agent.api.schemas import (
    DestinationsResponse,
    DestinationSummary,
    HealthResponse,
    VisaPlanRequest,
)
from visa_research_agent.config.loader import get_destination_registry
from visa_research_agent.domain.models import VisaPlan

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/destinations", response_model=DestinationsResponse, tags=["visa research"])
async def destinations() -> DestinationsResponse:
    registry = get_destination_registry()
    return DestinationsResponse(
        destinations=[
            DestinationSummary(
                slug=destination.slug,
                name=destination.display_name,
                route_type=destination.route_type,
                status=destination.implementation_status,
            )
            for destination in registry.destinations
        ]
    )


@router.post(
    "/visa-plans",
    response_model=VisaPlan,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Unsupported destination"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Destination not implemented yet"},
    },
    tags=["visa research"],
)
async def create_visa_plan(request: VisaPlanRequest) -> VisaPlan:
    registry = get_destination_registry()
    destination = registry.get(request.destination)
    if destination is None:
        supported = [item.slug for item in registry.destinations]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "message": f"Unsupported destination: {request.destination}",
                "supported_destinations": supported,
            },
        )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "message": (
                f"Visa-plan generation for {destination.display_name} is not available yet. "
                "Singapore will be implemented in Phase 2."
            )
        },
    )
