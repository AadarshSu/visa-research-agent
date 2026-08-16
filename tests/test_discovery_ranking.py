"""What identifies a document checklist, and which post serves this traveller.

These pin the two signals added after Brazil — the first corridor that tested discovery's ranking
out of sample, and failed it. Both cases below are taken from the real pages:

  * a generic "how to apply on e-consular" page in Riyadh repeated "documents required" and
    "required documents" and named no document at all, and it beat Edinburgh's real tourism
    checklist, which names a passport, a bank statement and an itinerary and never says
    "checklist";
  * Brazil publishes every mission under one host with the post in the path, so a host-based
    check could not tell `consulado-edimburgo` from `embaixada-riade`, and four of six resolved
    roles came from missions on the wrong continent.
"""

from visa_research_agent.discovery.lexicon import get_country_registry, get_lexicon
from visa_research_agent.discovery.models import Corridor, PageLink
from visa_research_agent.discovery.scoring import (
    mission_affinity,
    mission_in_path,
    names_documents,
    score_body,
    score_link,
)

BR = "https://www.gov.br/mre/pt-br"
VIVIS = "visa-section/types-of-visa/visit-visa-vivis-1/tourism-and-transit-vivis"
EDINBURGH = f"{BR}/consulado-edimburgo/{VIVIS}"
RIYADH = f"{BR}/embaixada-riade/how-to-apply-for-services-on-e-consular"

# Shortened from the real pages, keeping what each one does with the word "document".
CHECKLIST_TEXT = (
    "Tourism and Transit (VIVIS). Applicants must upload a passport valid for at least six "
    "months, a recent passport photo, the completed application form, a bank statement for the "
    "last three months as proof of funds, a travel itinerary and a return ticket."
)
ABOUT_DOCUMENTS_TEXT = (
    "How to apply for services on e-consular. Select the service, then upload the documents "
    "required for your application. The required documents vary by service. Applications with "
    "missing application documents will be returned. Check the necessary documents before you "
    "submit and remember that documents required for tourism differ from other purposes."
)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="brazil",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def link_at(url: str, text: str = "") -> PageLink:
    return PageLink(url=url, text=text, heading="", depth=0, discovered_from="seed")


def checklist_body(text: str, title: str) -> float:
    registry = get_country_registry()
    scores = score_body(text, title, corridor(), get_lexicon(), registry.require("IN"))
    return scores.score_for("document_checklist")


def checklist_link(url: str, text: str = "") -> float:
    registry = get_country_registry()
    scores = score_link(
        link_at(url, text),
        corridor(),
        get_lexicon(),
        registry.require("IN"),
        registry.require("GB"),
    )
    return scores.score_for("document_checklist")


# --- naming a post from the path ------------------------------------------------------------


def test_a_post_is_read_from_the_path_when_the_host_cannot_distinguish_it() -> None:
    lexicon = get_lexicon()

    assert mission_in_path(EDINBURGH, lexicon) == "edimburgo"
    assert mission_in_path(RIYADH, lexicon) == "riade"


def test_a_path_naming_no_post_returns_nothing() -> None:
    lexicon = get_lexicon()

    assert mission_in_path("https://www.gov.br/mre/pt-br/assuntos/portal-consular", lexicon) is None
    # A bare section index names no particular post, so it must not be read as one.
    assert mission_in_path("https://example.gov.br/embassy/index.html", lexicon) is None


def test_the_post_serving_the_traveller_is_recognised_in_a_foreign_language() -> None:
    """Brazil writes the UK posts in Portuguese, so the labels have to be data, not code."""

    lexicon, gb = get_lexicon(), get_country_registry().require("GB")

    assert mission_affinity(EDINBURGH, gb, lexicon) == "own"
    assert mission_affinity(f"{BR}/consulado-londres/visas", gb, lexicon) == "own"


def test_another_post_is_recognised_as_another_post() -> None:
    lexicon, gb = get_lexicon(), get_country_registry().require("GB")

    assert mission_affinity(RIYADH, gb, lexicon) == "other"
    assert mission_affinity(f"{BR}/embaixada-kuala-lumpur/eng/visit-visa", gb, lexicon) == "other"
    assert mission_affinity(f"{BR}/consulado-atlanta/visas", gb, lexicon) == "other"


def test_a_page_belonging_to_no_post_is_neither() -> None:
    # Most ministry pages belong to no mission, and must not be penalised as though they did.
    lexicon, gb = get_lexicon(), get_country_registry().require("GB")

    assert mission_affinity("https://www.ica.gov.sg/enter-transit-depart", gb, lexicon) is None
    assert mission_affinity(f"{BR}/mre/pt-br/assuntos/portal-consular", gb, lexicon) is None


def test_a_post_named_by_city_in_the_host_is_recognised() -> None:
    """Singapore's London high commission is named by city, so a country-code check missed it."""

    lexicon, gb = get_lexicon(), get_country_registry().require("GB")

    assert mission_affinity("https://london.mfa.gov.sg/visa", gb, lexicon) == "own"


# --- naming documents rather than talking about them ----------------------------------------


def test_a_checklist_is_recognised_by_the_documents_it_names() -> None:
    named = names_documents(CHECKLIST_TEXT.lower(), get_lexicon())

    assert {"passport", "bank statement", "itinerary", "return ticket"} <= set(named)


def test_a_page_about_documents_names_none_of_them() -> None:
    assert names_documents(ABOUT_DOCUMENTS_TEXT.lower(), get_lexicon()) == []


def test_the_real_checklist_outscores_the_page_that_only_talks_about_documents() -> None:
    """The Brazil regression, in one assertion.

    The Riyadh page repeats four separate checklist phrases and still must lose to a page that
    names actual documents and never says "checklist".
    """

    real = checklist_body(CHECKLIST_TEXT, "Tourism and Transit (VIVIS)")
    about = checklist_body(ABOUT_DOCUMENTS_TEXT, "How to apply for services on e-consular")

    assert real > about, f"checklist {real} did not beat the page about checklists {about}"


def test_one_document_in_passing_does_not_make_a_page_a_checklist() -> None:
    # Nearly every page on a visa site mentions a passport once.
    assert checklist_body("You will need a valid passport to enter.", "Entry") == 0.0


# --- the post decides the two roles it governs ----------------------------------------------


def test_another_posts_page_loses_the_roles_that_post_governs() -> None:
    own = checklist_link(EDINBURGH, "Tourism and Transit")
    other = checklist_link(
        f"{BR}/embaixada-riade/visa-section/types-of-visa/tourism-and-transit-vivis",
        "Tourism and Transit",
    )

    assert own > other, "the traveller's own post must outrank an identical page at another post"


def test_a_ministry_page_is_not_penalised_for_belonging_to_no_post() -> None:
    """Singapore and Japan resolve from ministry pages, and must not be caught by this."""

    registry, lexicon = get_country_registry(), get_lexicon()
    scores = score_link(
        link_at("https://www.ica.gov.sg/enter-transit-depart/entering-singapore/visa_requirements"),
        Corridor(
            destination_slug="singapore",
            passport_nationality="IN",
            applying_from="GB",
            purpose="tourism",
        ),
        lexicon,
        registry.require("IN"),
        registry.require("GB"),
    )

    assert not any(
        "other-mission" in signal for signals in scores.signals.values() for signal in signals
    )
