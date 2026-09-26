"""HTTP routing kept deliberately thin around the research workflow."""

import asyncio
import json
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Annotated, Any, get_args

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse

from visa_research_agent.api.dependencies import (
    get_automatic_destinations,
    get_traveller_source,
    get_visa_plan_service,
)
from visa_research_agent.api.schemas import (
    DestinationsResponse,
    DestinationSummary,
    HealthResponse,
    VisaPlanRequest,
)
from visa_research_agent.api.signin import SignIn, get_sign_in, require_signed_in_for_plans
from visa_research_agent.api.templates import static_asset_version, templates
from visa_research_agent.api.traveller import TravellerSource
from visa_research_agent.config.loader import get_destination_registry, get_runtime_policy
from visa_research_agent.config.settings import settings
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.discovery.automatic import (
    AutomaticDestinationService,
    AutomaticDiscoveryError,
)
from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.discovery.models import Corridor
from visa_research_agent.discovery.registry import get_authority_registry
from visa_research_agent.domain.models import (
    DestinationConfig,
    TravellerProfile,
    TravelPurpose,
    VisaPlan,
)
from visa_research_agent.research.errors import InsufficientEvidenceError, VisaResearchError
from visa_research_agent.research.service import VisaPlanService

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(
    request: Request, sign_in: Annotated[SignIn | None, Depends(get_sign_in)]
) -> HTMLResponse:
    policy = get_runtime_policy()
    signed_in = sign_in is not None and sign_in.signed_in_user(request) is not None
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "destinations": researchable_destinations(),
            "countries": sorted(get_country_registry().countries, key=lambda c: c.name),
            "purposes": get_args(TravelPurpose),
            # A signed-in traveller is asked, never handed the default (TODO item 55, rule 4):
            # their passport comes from Ofself or from them, and where they apply from from them.
            "traveller": None if signed_in else DEFAULT_TRAVELLER_PROFILE,
            "sign_in_configured": sign_in is not None,
            "sign_in_required": settings.require_sign_in,
            "signed_in": signed_in,
            "source_mode": policy.source_mode,
            "extraction_mode": policy.extraction_mode,
            "static_asset_version": static_asset_version(),
        },
        headers={"Cache-Control": "no-store"},
    )


def researchable_destinations() -> list[DestinationSummary]:
    """Every destination a plan can be asked for.

    Under `destination_mode: automatic` that is every country with a usable row in
    `authority_domains.yaml`, not only the handful written into `destinations.yaml`. A country
    without one is refused before anything is fetched (`trusted_domains_for`), so offering it would
    only offer a refusal. A configured entry keeps its own route type, because Schengen membership
    is a fact about the destination rather than about how its sources were found.
    """

    registry = get_destination_registry()
    configured = {destination.slug: destination for destination in registry.destinations}
    if get_runtime_policy().destination_mode == "configured":
        return [
            DestinationSummary(
                slug=destination.slug,
                name=destination.display_name,
                route_type=destination.route_type,
                status=destination.implementation_status,
            )
            for destination in registry.destinations
        ]

    authorities = get_authority_registry()
    summaries: list[DestinationSummary] = []
    for country in sorted(get_country_registry().countries, key=lambda item: item.name):
        row = authorities.get(country.code)
        if row is None or not row.domains:
            continue
        entry = configured.get(country.slug)
        summaries.append(
            DestinationSummary(
                slug=country.slug,
                name=country.name,
                route_type=entry.route_type if entry is not None else "national",
                status="available",
            )
        )
    return summaries


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/destinations", response_model=DestinationsResponse, tags=["visa research"])
async def destinations() -> DestinationsResponse:
    return DestinationsResponse(destinations=researchable_destinations())


def corridor_for(destination_slug: str, traveller: TravellerProfile) -> Corridor:
    """The corridor a traveller profile describes.

    A straight mapping now that the profile holds ISO codes: the schema normalised whatever the
    caller wrote into the one form corridors, cache keys and the lexicon all use.
    """

    return Corridor(
        destination_slug=destination_slug,
        passport_nationality=traveller.passport_nationality,
        applying_from=traveller.country_of_residence,
        purpose=traveller.travel_purpose,
    )


def destination_country_code(requested: str) -> str | None:
    """The ISO code of the country a request names, however the caller wrote it."""

    registry = get_country_registry()
    wanted = requested.strip().lower()
    configured = get_destination_registry().get(wanted)
    if configured is not None:
        wanted = configured.display_name.lower()
    country = registry.by_slug(wanted) or next(
        (
            item
            for item in registry.countries
            if item.name.lower() == wanted
            or wanted in {synonym.lower() for synonym in item.synonyms}
        ),
        None,
    )
    return country.code if country else None


def refuse_impossible_corridors(requested: str, traveller: TravellerProfile) -> None:
    """Turn away a corridor that cannot have an answer, before anything is spent on it.

    A national of the destination does not apply to visit their own country, so there is no official
    visa guidance to find. Left alone it would search, crawl and spend two model calls to arrive at
    a refusal, which is slow, costs money, and reads as a fault rather than as the question being
    the wrong one.

    This is deliberately not a claim about entry rights — it says only that this agent researches
    visas for travellers who need one, which is a fact about the product.
    """

    code = destination_country_code(requested)
    if code is not None and code == traveller.passport_nationality:
        named = requested.replace("-", " ").title()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "message": (
                    f"This passport is issued by {named}, so there is no visa to research: a "
                    "country's own nationals do not apply for a visa to visit it. Choose a "
                    "different destination, or a different passport."
                ),
                "status": "not_applicable",
            },
        )


async def resolve_destination(
    requested: str,
    traveller: TravellerProfile,
    automatic: AutomaticDestinationService | None,
    *,
    on_phase: Callable[[str], None] | None = None,
) -> DestinationConfig:
    """Research the destination, or use its hand-written entry when research is switched off.

    `on_phase` hears each research phase as it starts; a hand-written entry has none.
    """

    registry = get_destination_registry()
    destination = registry.get(requested)
    if automatic is None:
        # Only here may a hand-written entry answer. Under `automatic` it answered every traveller
        # from the pages written for one — Singapore's checklist is ICA's page for Indian travel
        # documents, Japan's the London embassy's — so a Filipino asking about Japan and a
        # Nigerian asking about Singapore were refused while discovery answers both from their own
        # post. DECISIONS entry 149.
        if destination is not None and destination.implementation_status == "available":
            return destination
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
    country = automatic.country_named(name)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "message": (
                    f"{requested} is not a country this agent holds reference data for, so its "
                    "own government's domains cannot be told apart from other countries' pages "
                    "about it."
                ),
                "supported_destinations": [item.slug for item in researchable_destinations()],
            },
        )
    # Keyed on the country's own slug, never on the request as written. "united states" fails the
    # corridor's slug pattern, and "usa" fits it but would be stored as a corridor of its own beside
    # the `united-states` one the interface asks for. DECISIONS entry 168.
    corridor = corridor_for(country.slug, traveller)
    try:
        discovered = await automatic.destination_for(name, corridor, on_phase=on_phase)
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
        status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in with Ofself"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Unsupported destination"},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Could not be verified"},
    },
    tags=["visa research"],
    # Checked before anything is spent: nothing past this line runs for a browser not signed in.
    dependencies=[Depends(require_signed_in_for_plans)],
)
async def create_visa_plan(
    request: VisaPlanRequest,
    service: Annotated[VisaPlanService, Depends(get_visa_plan_service)],
    automatic: Annotated[AutomaticDestinationService | None, Depends(get_automatic_destinations)],
    travellers: Annotated[TravellerSource, Depends(get_traveller_source)],
) -> VisaPlan:
    traveller = await travellers.traveller_for(request)
    refuse_impossible_corridors(request.destination, traveller)
    return await research_plan(request.destination, traveller, service, automatic)


@router.post(
    "/visa-plans/stream",
    response_class=StreamingResponse,
    responses={
        status.HTTP_200_OK: {
            "description": (
                "Newline-delimited JSON: a `stage` event as each step starts, then exactly one "
                "`plan`, `refusal` or `error` event."
            ),
            "content": {"application/x-ndjson": {}},
        },
        status.HTTP_401_UNAUTHORIZED: {"description": "Not signed in with Ofself"},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Unsupported destination"},
    },
    tags=["visa research"],
    dependencies=[Depends(require_signed_in_for_plans)],
)
async def stream_visa_plan(
    request: VisaPlanRequest,
    service: Annotated[VisaPlanService, Depends(get_visa_plan_service)],
    automatic: Annotated[AutomaticDestinationService | None, Depends(get_automatic_destinations)],
    travellers: Annotated[TravellerSource, Depends(get_traveller_source)],
) -> StreamingResponse:
    """The same plan as `POST /visa-plans`, with each step announced as it starts (TODO item 57).

    **Only progress streams, never content.** A stage event names which step has started — search,
    choosing pages, reading them, writing the plan — and carries nothing a step found. The plan
    arrives whole, after every validator has passed, exactly as the other route returns it: a
    half-written plan has passed none of them, and a claim it could still drop is the unverified,
    alarming answer entry 6 forbids.

    The checks that cost nothing run first, so a request that cannot be answered still gets its
    ordinary status code. From the first stage on the status is 200, and a refusal arrives as an
    event carrying the same `detail` the other route would have answered with.
    """

    traveller = await travellers.traveller_for(request)
    refuse_impossible_corridors(request.destination, traveller)

    async def work(report: Callable[[str], None]) -> VisaPlan:
        return await research_plan(
            request.destination, traveller, service, automatic, report=report
        )

    return StreamingResponse(
        plan_events(work),
        media_type="application/x-ndjson",
        # Without these a proxy may hold the stream back until it ends, which is the wait this
        # route exists to break up.
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


async def research_plan(
    requested: str,
    traveller: TravellerProfile,
    service: VisaPlanService,
    automatic: AutomaticDestinationService | None,
    *,
    report: Callable[[str], None] | None = None,
) -> VisaPlan:
    """Resolve the destination and write its plan, turning a refusal into an HTTP answer.

    Shared by both plan routes so they cannot disagree about what is refused or how.
    """

    destination = await resolve_destination(requested, traveller, automatic, on_phase=report)
    try:
        return await service.generate(destination, traveller, on_stage=report)
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


async def plan_events(
    work: Callable[[Callable[[str], None]], Coroutine[Any, Any, VisaPlan]],
) -> AsyncIterator[str]:
    """Run `work`, yielding one JSON line per stage it reports and then one for its outcome.

    The work runs as its own task so a stage can be sent while it is still going. If the browser
    goes away the task is cancelled rather than left to spend searches and model calls on a plan
    nobody will read.
    """

    stages: asyncio.Queue[str | None] = asyncio.Queue()
    task = asyncio.create_task(work(stages.put_nowait))
    # The end of the work is one more item in the same queue, so every stage it reported is sent
    # before its outcome.
    task.add_done_callback(lambda _: stages.put_nowait(None))
    try:
        while (stage := await stages.get()) is not None:
            yield event_line({"event": "stage", "stage": stage})
        try:
            plan = task.result()
        except HTTPException as exc:
            yield event_line(
                {"event": "refusal", "status_code": exc.status_code, "detail": exc.detail}
            )
        except Exception:
            # Past the first line the status is already 200, so a fault has to be said in the
            # stream. It is still raised, so the server logs it as it would any other.
            yield event_line({"event": "error", "message": "The plan could not be generated."})
            raise
        else:
            yield event_line({"event": "plan", "plan": plan.model_dump(mode="json")})
    finally:
        if not task.done():
            task.cancel()


def event_line(event: dict[str, Any]) -> str:
    return json.dumps(event, separators=(",", ":")) + "\n"
