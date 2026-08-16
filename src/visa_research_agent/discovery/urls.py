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
        ".zip",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".webp",
        ".ico",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".css",
        ".js",
        ".xml",
        ".rss",
        ".json",
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


# Government CMSs date their paths: /201303/t20130315_3383966.htm, /202408/t20240802_11465159.htm.
# Year, then month, optionally day, optionally prefixed "t" in the filename.
CMS_DATE = re.compile(r"^t?((?:19|20)\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])?(?:$|[_.\-])")


def published_date_in_path(url: str) -> str | None:
    """When a URL's own path says the page was published, if it says so at all.

    This is *publication*, not staleness, and the distinction is load-bearing. China's UK embassy
    serves its current tourist-visa checklist from a 2013-dated path and its 2024 fee table from a
    2024 one; both are correct and current. Vetoing dated paths would have thrown away both.

    So this reports rather than rejects. `is_archived` still vetoes an explicit archive section;
    what a bare publication date deserves is a reader — a human, or a decider holding the page's
    text — not a rule that guesses from the URL alone.
    """

    for segment in path_segments(url):
        match = CMS_DATE.match(segment)
        if match is None:
            continue
        year, month, day = match.group(1), match.group(2), match.group(3)
        return f"{year}-{month}-{day}" if day else f"{year}-{month}"
    return None


def is_machine_endpoint(url: str) -> bool:
    """True when a URL serves a program rather than a person.

    Retrieval already refuses JSON once it has been fetched, but by then the URL has taken a place
    on the shortlist that a real page needed. Vietnam's `api.evisa.gov.vn/client-service/public/
    ngon-ngu/get-all` — an endpoint listing the site's *languages* — outranked every readable
    evisa.gov.vn page and pushed all of them out.

    Matched on the host label and whole path segments only, so a page about "the API" is unaffected.
    """

    host = host_of(url)
    if host.split(".")[0] in {"api", "apis", "ws", "rest", "graphql"}:
        return True
    segments = path_segments(url)
    return any(segment in {"api", "rest", "graphql", "client-service"} for segment in segments)


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
    if is_machine_endpoint(url):
        return False
    return not SKIPPED_PATH_PATTERN.search(path)
