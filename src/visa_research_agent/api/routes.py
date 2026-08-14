"""HTTP routing kept deliberately thin around the research workflow."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from visa_research_agent.api.dependencies import get_visa_plan_service
from visa_research_agent.api.schemas import (
    DestinationsResponse,
    DestinationSummary,
    HealthResponse,
    VisaPlanRequest,
)
from visa_research_agent.api.templates import static_asset_version, templates
from visa_research_agent.config.loader import get_destination_registry, get_runtime_policy
from visa_research_agent.config.traveller import TRAVELLER_PROFILE
from visa_research_agent.domain.models import VisaPlan
from visa_research_agent.research.errors import InsufficientEvidenceError, VisaResearchError
from visa_research_agent.research.service import VisaPlanService

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request) -> HTMLResponse:
    registry = get_destination_registry()
    policy = get_runtime_policy()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "destinations": registry.destinations,
            "source_mode": policy.source_mode,
            "extraction_mode": policy.extraction_mode,
            "static_asset_version": static_asset_version(),
        },
        headers={"Cache-Control": "no-store"},
    )


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
async def create_visa_plan(
    request: VisaPlanRequest,
    service: Annotated[VisaPlanService, Depends(get_visa_plan_service)],
) -> VisaPlan:
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

    if destination.implementation_status != "available":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": (
                    f"Visa-plan generation for {destination.display_name} is not available yet."
                )
            },
        )

    try:
        return await service.generate(destination, TRAVELLER_PROFILE)
    except InsufficientEvidenceError as exc:
        # A refusal explains which official evidence was missing, rather than failing opaquely.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": (
                    f"A verified plan for {destination.display_name} could not be produced "
                    "because required official evidence was unavailable."
                ),
                "status": "unable_to_verify",
                "reasons": exc.reasons,
                "unavailable_sources": [
                    failure.model_dump(mode="json") for failure in exc.failures
                ],
            },
        ) from exc
    except VisaResearchError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "The visa plan could not be generated safely."},
        ) from exc
