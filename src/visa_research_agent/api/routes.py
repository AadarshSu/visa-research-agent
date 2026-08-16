"""HTTP routing kept deliberately thin around the research workflow."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse

from visa_research_agent.api.dependencies import (
    get_automatic_destinations,
    get_visa_plan_service,
)
from visa_research_agent.api.schemas import (
    DestinationsResponse,
    DestinationSummary,
    HealthResponse,
    VisaPlanRequest,
)
from visa_research_agent.api.templates import static_asset_version, templates
from visa_research_agent.config.loader import get_destination_registry, get_runtime_policy
from visa_research_agent.config.traveller import TRAVELLER_PROFILE
from visa_research_agent.discovery.automatic import (
    AutomaticDestinationService,
    AutomaticDiscoveryError,
)
from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.discovery.models import Corridor
from visa_research_agent.domain.models import DestinationConfig, TravellerProfile, VisaPlan
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


def corridor_for(destination_slug: str, traveller: TravellerProfile) -> Corridor:
    """The corridor a traveller profile describes.

    The profile is still fixed, so this is a single corridor today. It is derived rather than
    hard-coded so that making the profile variable changes one function, not the request path.
    """

    countries = get_country_registry()
    nationality = countries.code_for_name(traveller.passport_nationality)
    residence = countries.code_for_name(traveller.country_of_residence)
    if nationality is None or residence is None:
        raise AutomaticDiscoveryError(
            "The traveller's nationality or country of residence is not one this agent holds "
            "reference data for, so the right official pages cannot be identified."
        )
    return Corridor(
        destination_slug=destination_slug,
        passport_nationality=nationality,
        applying_from=residence,
        purpose=traveller.travel_purpose,
    )


async def resolve_destination(
    requested: str,
    automatic: AutomaticDestinationService | None,
) -> DestinationConfig:
    """Use the configured destination when there is one, otherwise research it."""

    registry = get_destination_registry()
    destination = registry.get(requested)
    if destination is not None and destination.implementation_status == "available":
        return destination

    if automatic is None:
        if destination is not None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "message": (
                        f"Visa-plan generation for {destination.display_name} is not available yet."
                    )
                },
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "message": f"Unsupported destination: {requested}",
                "supported_destinations": [item.slug for item in registry.destinations],
            },
        )

    name = destination.display_name if destination is not None else requested
    try:
        discovered = await automatic.destination_for(
            name, corridor_for(requested, TRAVELLER_PROFILE)
        )
    except AutomaticDiscoveryError as exc:
        # A refusal, not a fault. It names what could not be established rather than offering a
        # plan assembled from whatever happened to be readable.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": str(exc), "status": "unable_to_verify"},
        ) from exc
    return discovered.config


@router.post(
    "/visa-plans",
    response_model=VisaPlan,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Unsupported destination"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Could not be verified"},
    },
    tags=["visa research"],
)
async def create_visa_plan(
    request: VisaPlanRequest,
    service: Annotated[VisaPlanService, Depends(get_visa_plan_service)],
    automatic: Annotated[AutomaticDestinationService | None, Depends(get_automatic_destinations)],
) -> VisaPlan:
    destination = await resolve_destination(request.destination, automatic)

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
