"""FastAPI application factory and default ASGI application."""

from fastapi import FastAPI

from visa_research_agent import __version__
from visa_research_agent.api.routes import router
from visa_research_agent.config.settings import settings


def create_app() -> FastAPI:
    """Build the HTTP application without running a server as an import side effect."""

    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "A bounded personal visa research API. It reports configured official-source "
            "information and never guarantees visa eligibility or approval."
        ),
    )
    application.include_router(router)
    return application


app = create_app()
