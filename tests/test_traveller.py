"""The traveller a request describes, and the default when it describes nobody."""

import pytest
from pydantic import ValidationError

from visa_research_agent.api.schemas import TravellerRequest, VisaPlanRequest
from visa_research_agent.config.traveller import DEFAULT_TRAVELLER_PROFILE


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
