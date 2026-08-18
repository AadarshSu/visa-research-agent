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
    is_archived,
    is_boilerplate,
    mission_affinity,
    mission_in_path,
    names_documents,
    score_body,
    score_link,
    wrong_country,
)
from visa_research_agent.discovery.urls import published_date_in_path
from visa_research_agent.domain.models import TravelPurpose

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


# --- publication dates in CMS paths ---------------------------------------------------------


def test_a_cms_date_in_the_path_is_read_rather_than_guessed_at() -> None:
    """Widened from the old rule, which only saw a bare four-digit year segment.

    China's UK embassy serves its current checklist from `/201303/t20130315_...`, so the date was
    invisible to `is_archived` and nothing reported it.
    """

    china = "https://gb.china-embassy.gov.cn/eng/visa/qzxz/201303/t20130315_3383966.htm"
    fees = "https://manchester.china-consulate.gov.cn/eng/visa/visa/202408/t20240802_11465159.htm"

    assert published_date_in_path(china) == "2013-03"
    assert published_date_in_path(fees) == "2024-08"


def test_a_path_with_no_date_reports_none() -> None:
    for url in (
        "https://www.uk.emb-japan.go.jp/itpr_en/sightseeing.html",
        "https://www.gov.br/mre/pt-br/consulado-edimburgo/visa-section",
        "https://x.gov.example/visa/100000/page.htm",
        "https://x.gov.example/visa/201399/page.htm",
    ):
        assert published_date_in_path(url) is None, url


def test_a_publication_date_does_not_archive_a_page() -> None:
    """The load-bearing distinction: publication is not staleness.

    Both of China's correct picks carry dated paths, and one is from 2013. Treating a dated path as
    an archive marker would have discarded the only two roles that corridor resolved.
    """

    lexicon = get_lexicon()
    china = "https://gb.china-embassy.gov.cn/eng/visa/qzxz/201303/t20130315_3383966.htm"

    assert published_date_in_path(china) is not None
    assert not is_archived(china, lexicon)


def test_an_explicit_archive_section_is_still_vetoed() -> None:
    # Widening detection must not have loosened the veto that already worked.
    lexicon = get_lexicon()

    assert is_archived("https://immigration.gov.example/visa/2019/tourist-checklist.html", lexicon)
    assert is_archived("https://immigration.gov.example/visa/archive/checklist.html", lexicon)


# --- a country name must not match inside a word ---------------------------------------------


def wrong_country_for(text: str, purpose: TravelPurpose = "business") -> str | None:
    registry = get_country_registry()
    return wrong_country(
        PageLink(
            url="https://www.mofa.go.jp/visa",
            text=text,
            heading="",
            depth=0,
            discovered_from="seed",
        ),
        Corridor(
            destination_slug="japan",
            passport_nationality="IN",
            applying_from="GB",
            purpose=purpose,
        ),
        registry,
        "JP",
    )


def test_a_country_code_inside_an_ordinary_word_is_not_a_country() -> None:
    """`wrong_country` is a veto, so a substring match silently threw the best page away.

    "us" sits inside "business", "house" and "because" — every business-purpose page was being
    rejected as though it were about the United States.
    """

    for harmless in ("Business visa", "Because of the pandemic", "Campus visit", "Chadwick House"):
        assert wrong_country_for(harmless) is None, harmless


def test_a_country_named_in_full_is_still_vetoed() -> None:
    # The fix must not blunt the veto: a page genuinely about another country still goes.
    assert wrong_country_for("Visa for United States nationals") == "United States"
    assert wrong_country_for("Visa requirements for China") == "China"


def test_every_country_has_the_field_the_trust_rule_depends_on() -> None:
    """`tlds` decides whether a domain is the destination's own government.

    A country without it is not merely weaker at scoring — it can never have a domain trusted, so
    it would silently be unresearchable.
    """

    countries = get_country_registry().countries

    assert len(countries) > 150, "destinations should not be limited to a curated handful"
    assert all(country.tlds for country in countries)
    assert all(country.code.isupper() and len(country.code) == 2 for country in countries)


# --- who a page is about, and which post published it ----------------------------------------


def route_link(url: str, text: str = "", heading: str = "") -> float:
    registry = get_country_registry()
    scores = score_link(
        PageLink(url=url, text=text, heading=heading, depth=0, discovered_from="seed"),
        corridor(),
        get_lexicon(),
        registry.require("IN"),
        registry.require("GB"),
    )
    return scores.score_for("application_route")


def test_the_post_a_traveller_applies_at_outranks_the_post_of_their_own_country() -> None:
    """France's India post outranked its UK post for a traveller applying from the UK.

    `in.diplomatie.gouv.fr` is France's mission *in India*, so that label says which post published
    the page. Reading it as "this page is for Indian nationals" handed the nationality bonus to
    everything that post publishes — its accessibility statement included — and 40 beat the 30 the
    UK post earns for actually serving this traveller: 65.6 against 55.6 on the identical page.
    """

    india_post = route_link(
        "https://in.diplomatie.gouv.fr/en/applying-for-a-visa", "Applying for a visa"
    )
    uk_post = route_link(
        "https://uk.diplomatie.gouv.fr/en/applying-for-a-visa", "Applying for a visa"
    )

    assert uk_post > india_post


def test_a_page_whose_own_words_name_the_nationality_still_earns_it() -> None:
    """The narrowing must not cost the real signal. A path or a title naming the country is the
    page describing itself, which is a different thing from the host it sits on."""

    about_indians = route_link(
        "https://in.diplomatie.gouv.fr/en/applying-for-a-visa-indian-nationals",
        "Applying for a visa: Indian nationals",
    )
    generic = route_link(
        "https://in.diplomatie.gouv.fr/en/applying-for-a-visa", "Applying for a visa"
    )

    assert about_indians > generic


def test_site_furniture_is_vetoed_however_well_it_scores() -> None:
    """These took three of France's ten fetch places. A footer link inherits the last heading above
    it, so the legal notice collected the heading bonus from a news article about visa
    requirements — and a legal notice cannot be visa guidance whatever it scores."""

    lexicon = get_lexicon()

    assert is_boilerplate("https://in.diplomatie.gouv.fr/accessibilite", lexicon)
    assert is_boilerplate("https://in.diplomatie.gouv.fr/en/donnees-personnelles", lexicon)
    assert is_boilerplate("https://in.diplomatie.gouv.fr/mentions-legales", lexicon)
    assert is_boilerplate("https://example.gov.uk/privacy", lexicon)
    # Real guidance is untouched, including a path that merely mentions a document.
    assert not is_boilerplate("https://uk.diplomatie.gouv.fr/en/applying-for-a-visa", lexicon)
    assert not is_boilerplate(f"{EDINBURGH}", lexicon)


def test_the_heading_a_footer_link_inherits_cannot_carry_it_alone() -> None:
    """The mechanism behind the last test, recorded so it is not mistaken for a scoring accident:
    the boilerplate page's score came almost entirely from a heading about someone else's page."""

    registry = get_country_registry()
    inherited = score_link(
        PageLink(
            url="https://in.diplomatie.gouv.fr/mentions-legales",
            text="Mentions légales",
            heading="France lifts airport transit visa requirements for Indian nationals",
            depth=0,
            discovered_from="seed",
        ),
        corridor(),
        get_lexicon(),
        registry.require("IN"),
        registry.require("GB"),
    ).best()[1]

    # The shortlist ranks on the best role, and this reached 69 in the real run — high enough to
    # take a fetch place. It still scores; the veto is what stops it, not the score.
    assert inherited > 20
    assert is_boilerplate("https://in.diplomatie.gouv.fr/mentions-legales", get_lexicon())
