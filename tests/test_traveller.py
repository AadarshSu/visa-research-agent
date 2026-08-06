from visa_research_agent.config.traveller import TRAVELLER_PROFILE


def test_fixed_traveller_profile_matches_personal_mvp() -> None:
    assert TRAVELLER_PROFILE.model_dump(mode="json") == {
        "passport_nationality": "India",
        "passport_type": "ordinary",
        "country_of_residence": "United Kingdom",
        "city_of_residence": "Edinburgh",
        "uk_immigration_status": "Graduate visa",
        "uk_permission_expiry": "2027-12-23",
        "travel_purpose": "tourism",
    }
