"""A fake two-host government site for discovery tests.

It reproduces the shapes this project has actually hit in the wild, because those are what break
naive implementations:

  * a page whose URL says nothing and is identifiable only by its anchor text;
  * a per-nationality detail page two hops from the entry point;
  * a checklist behind a page that forwards to a PDF;
  * a wrong-audience page on the correct domain;
  * an off-domain link that must never be requested.
"""

import httpx

from visa_research_agent.domain.models import DestinationConfig

AUTHORITY = "immigration.gov.example"
MISSION = "uk.embassy.gov.example"

INDEX = f"https://{AUTHORITY}/visa/index.html"
EXEMPTIONS = f"https://{AUTHORITY}/visa/short/novisa.html"
DETAIL_INDIA = f"https://{AUTHORITY}/visa/detail/india.html"
DETAIL_CHINA = f"https://{AUTHORITY}/visa/detail/china.html"
ARCHIVED = f"https://{AUTHORITY}/visa/2019/tourist-checklist.html"
MISSION_INDEX = f"https://{MISSION}/visa/index.html"
MISSION_OPAQUE = f"https://{MISSION}/visa/index_000070.html"
MISSION_CHECKLIST = f"https://{MISSION}/visa/sightseeing.html"
MISSION_CHECKLIST_PDF = f"https://{MISSION}/files/checklist.pdf"
MISSION_SPOUSE = f"https://{MISSION}/visa/spouse.html"
OFF_DOMAIN = "https://cheap-visas.example/apply-now"


def page(title: str, body: str) -> str:
    return f"<html><head><title>{title}</title></head><body>{body}</body></html>"


def link(url: str, text: str) -> str:
    return f'<a href="{url}">{text}</a>'


def forwarding_shell(target: str) -> str:
    return (
        f"<html><head><title>Items required</title>"
        f'<meta http-equiv="refresh" content="0;URL={target}">'
        f"</head><body></body></html>"
    )


def site_pages() -> dict[str, str]:
    """URL to HTML for the whole fake site, keyed without a trailing slash."""

    return {
        INDEX: page(
            "Visa | Immigration Authority",
            "<h1>Visa</h1>"
            + link(EXEMPTIONS, "Visa Exemption Countries and Regions")
            + link(f"https://{AUTHORITY}/visa/detail", "Check if You Need an Entry Visa")
            + link(MISSION_INDEX, "Embassy in the United Kingdom")
            + link(OFF_DOMAIN, "Apply now with our partner"),
        ),
        f"https://{AUTHORITY}/visa/detail": page(
            "Visa detail pages",
            "<h1>By nationality</h1>"
            + link(DETAIL_INDIA, "India")
            + link(DETAIL_CHINA, "China")
            + link(ARCHIVED, "2019 tourist checklist"),
        ),
        EXEMPTIONS: page(
            "Exemption of Visa (Short-Term Stay)",
            "<h1>Visa exemptions</h1><p>Nationals of the countries listed do not need a visa. "
            "India is not listed, so Indian nationals require a visa to enter.</p>",
        ),
        DETAIL_INDIA: page(
            "Visa Requirements for Indian Travel Documents",
            "<h1>India</h1><p>You will need a visa if you hold a travel document issued by "
            "India. Tourism visits are covered by the temporary visitor visa.</p>",
        ),
        DETAIL_CHINA: page(
            "Visa Requirements for Chinese Travel Documents",
            "<h1>China</h1><p>Nationals of China require a visa.</p>",
        ),
        ARCHIVED: page(
            "Tourist checklist 2019",
            "<h1>Documents required</h1><p>Superseded tourism checklist from 2019.</p>",
        ),
        MISSION_INDEX: page(
            "Visa | Embassy in the United Kingdom",
            "<h1>Visa</h1>"
            + link(MISSION_OPAQUE, "Temporary Visitor Visa")
            + link(MISSION_SPOUSE, "Spouse or Child of a National Visa"),
        ),
        MISSION_OPAQUE: page(
            "Visa: Temporary Visitor Visa",
            "<h1>Temporary Visitor Visa</h1><p>For tourism and short stays of up to 90 days.</p>"
            + link(MISSION_CHECKLIST, "Tourism"),
        ),
        MISSION_CHECKLIST: forwarding_shell(MISSION_CHECKLIST_PDF),
        MISSION_SPOUSE: page(
            "Visa: Spouse Visa Documents Required",
            "<h1>Spouse visa</h1><p>Documents required for a spouse visa application.</p>",
        ),
    }


def handler(requests: list[httpx.Request]) -> object:
    """A MockTransport handler that records every request it receives."""

    pages = site_pages()

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        url = str(request.url).rstrip("/")
        if url in pages:
            return httpx.Response(
                200, text=pages[url], headers={"Content-Type": "text/html; charset=utf-8"}
            )
        return httpx.Response(404, text="not found")

    return respond


def destination() -> DestinationConfig:
    """The fake site's destination config, trusting only its own two hosts."""

    return DestinationConfig(
        slug="testland",
        display_name="Testland",
        route_type="national",
        implementation_status="available",
        trusted_domains=[AUTHORITY, "embassy.gov.example"],
    )
