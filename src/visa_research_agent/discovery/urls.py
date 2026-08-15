"""URL normalisation and the rules for what is worth fetching.

Every rejection here happens before a request is made, so an off-domain or junk URL costs nothing
and, more importantly, is never contacted.
"""

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from visa_research_agent.domain.models import DestinationConfig
from visa_research_agent.domain.trust import host_of

# Tracking parameters carry no meaning and would otherwise split one page into many candidates.
TRACKING_PARAMETERS = frozenset(
    {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
)

# Extensions that are never readable guidance. PDFs are deliberately absent: authorities publish
# checklists as PDFs and retrieval can read them.
SKIPPED_EXTENSIONS = frozenset(
    {
        ".zip", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
        ".mp3", ".mp4", ".avi", ".mov", ".css", ".js", ".xml", ".rss", ".json",
    }
)

# Site furniture that never contains visa guidance.
SKIPPED_PATH_PATTERN = re.compile(
    r"/(search|sitemap|privacy|accessibility|cookies?|login|signin|register|rss|feed"
    r"|press|news|tender|vacanc|recruit|contact|disclaimer|copyright)(/|$|\.)",
    re.IGNORECASE,
)


def canonicalise_url(url: str) -> str:
    """Reduce a URL to one comparable form, so the same page is not considered twice."""

    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]

    path = parts.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")

    kept = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMETERS
    ]
    query = urlencode(sorted(kept))
    return urlunsplit((scheme, netloc, path, query, ""))


def is_pdf_url(url: str) -> bool:
    return urlsplit(url).path.lower().endswith(".pdf")


def path_segments(url: str) -> list[str]:
    """The lowercase path segments, used for whole-segment matching.

    Whole segments matter: a two-letter country code must not match inside a longer word, or "in"
    would match "information" on nearly every page.
    """

    return [segment.lower() for segment in urlsplit(url).path.split("/") if segment]


def is_crawlable(url: str, destination: DestinationConfig) -> bool:
    """True when a URL is on an approved domain and looks like readable guidance.

    The trust check is the hard bound. It runs before any request, so the crawl is structurally
    incapable of leaving the domains a human approved.
    """

    parts = urlsplit(url)
    if parts.scheme.lower() not in {"http", "https"}:
        return False
    if not destination.trusts_host(host_of(url)):
        return False

    path = parts.path.lower()
    if any(path.endswith(extension) for extension in SKIPPED_EXTENSIONS):
        return False
    return not SKIPPED_PATH_PATTERN.search(path)
