"""Shared server-rendered template configuration."""

from pathlib import Path

from fastapi.templating import Jinja2Templates

PACKAGE_DIRECTORY = Path(__file__).resolve().parents[1]
TEMPLATE_DIRECTORY = PACKAGE_DIRECTORY / "templates"
STATIC_DIRECTORY = PACKAGE_DIRECTORY / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIRECTORY))
