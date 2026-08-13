"""Shared server-rendered template configuration."""

from hashlib import sha256
from pathlib import Path

from fastapi.templating import Jinja2Templates

PACKAGE_DIRECTORY = Path(__file__).resolve().parents[1]
TEMPLATE_DIRECTORY = PACKAGE_DIRECTORY / "templates"
STATIC_DIRECTORY = PACKAGE_DIRECTORY / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIRECTORY))


def static_asset_version() -> str:
    """Return a content hash so changed CSS and JavaScript get a fresh browser URL."""

    digest = sha256()
    for filename in ("styles.css", "app.js"):
        digest.update(filename.encode())
        digest.update(STATIC_DIRECTORY.joinpath(filename).read_bytes())
    return digest.hexdigest()[:12]
