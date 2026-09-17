"""The traveller a request describes, and the default when it describes nobody."""

import pytest
from pydantic import ValidationError

from visa_research_agent.api.countries import normalise_country
from visa_research_agent.api.schemas import TravellerRequest, VisaPlanRequest
from visa_research_agent.api.traveller import RequestBodyTravellerSource
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE
from visa_research_agent.discovery.lexicon import get_country_registry


def test_the_default_profile_is_the_one_the_singapore_fixture_was_recorded_against() -> None:
    assert DEFAULT_TRAVELLER_PROFILE.model_dump(mode="json") == {
        "passport_nationality": "IN",
        "passport_type": "ordinary",
        "country_of_residence": "GB",
        "city_of_residence": "Edinburgh",
        "residence_status": "Graduate visa",
        "residence_permission_expiry": "2027-12-23",
        "travel_purpose": "tourism",
    }


def test_a_country_is_accepted_however_it_was_written() -> None:
    """One canonical form, whatever the caller sent: corridors and cache keys are keyed by code."""

    for written in ("IN", "in", "India", "Republic of India"):
        request = TravellerRequest(passport_nationality=written, country_of_residence="GB")
        assert request.passport_nationality == "IN"


def test_a_country_with_no_reference_data_is_refused_rather_than_guessed() -> None:
    # Without its own domains and demonyms, the right official pages cannot be identified.
    with pytest.raises(ValidationError, match="reference data"):
        TravellerRequest(passport_nationality="Atlantis", country_of_residence="GB")


def test_the_country_check_is_usable_outside_the_request_schema() -> None:
    """Item 55: an identity from Ofself must pass the same check a typed country does, so the
    check cannot live only inside the form's schema."""

    assert normalise_country(" united kingdom ") == "GB"
    assert normalise_country("IND") == "IN"
    with pytest.raises(ValueError, match="reference data"):
        normalise_country("Atlantis")


def test_every_countrys_alpha_3_code_normalises_to_its_own_alpha_2() -> None:
    """Ofself may record a citizenship as alpha-3 (TODO item 55). Checked for all 198, so a wrong or
    missing code in `countries.yaml` fails here rather than as a traveller's wrong passport."""

    for country in get_country_registry().countries:
        assert normalise_country(country.alpha3) == country.code
        assert normalise_country(country.alpha3.lower()) == country.code


def test_only_the_deciding_details_are_required() -> None:
    """A plan that does not use a detail must not demand it."""

    profile = TravellerRequest(passport_nationality="IN", country_of_residence="GB").to_profile()

    assert profile.travel_purpose == "tourism"
    assert profile.city_of_residence is None
    assert profile.residence_status is None


def test_a_purpose_other_than_tourism_is_carried_through() -> None:
    profile = TravellerRequest(
        passport_nationality="CN", country_of_residence="AE", travel_purpose="business"
    ).to_profile()

    assert (profile.passport_nationality, profile.country_of_residence) == ("CN", "AE")
    assert profile.travel_purpose == "business"


def test_a_request_naming_no_traveller_falls_back_to_the_default() -> None:
    assert VisaPlanRequest(destination="singapore").traveller is None


def test_a_diplomatic_passport_cannot_be_requested() -> None:
    """Discovery vetoes diplomatic and official passport pages, so such a plan cannot be
    researched — and must not be quietly answered with the ordinary-passport rules."""

    with pytest.raises(ValidationError):
        VisaPlanRequest(
            destination="singapore",
            traveller={  # type: ignore[arg-type]
                "passport_nationality": "IN",
                "country_of_residence": "GB",
                "passport_type": "diplomatic",
            },
        )


@pytest.mark.anyio
async def test_the_request_body_source_uses_the_traveller_the_request_describes() -> None:
    request = VisaPlanRequest(
        destination="japan",
        traveller=TravellerRequest(passport_nationality="PH", country_of_residence="PH"),
    )

    profile = await RequestBodyTravellerSource().traveller_for(request)

    assert (profile.passport_nationality, profile.country_of_residence) == ("PH", "PH")


@pytest.mark.anyio
async def test_only_the_request_body_source_falls_back_to_the_default_traveller() -> None:
    """The anonymous form opens on the default traveller. The fallback lives in this source, not
    the route, so an Ofself source can never inherit it (item 55, rule 4)."""

    profile = await RequestBodyTravellerSource().traveller_for(
        VisaPlanRequest(destination="singapore")
    )

    assert profile == DEFAULT_TRAVELLER_PROFILE
