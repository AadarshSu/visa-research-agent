"""The single fixed traveller profile used by the personal MVP."""

from datetime import date

from visa_research_agent.domain.models import TravellerProfile

TRAVELLER_PROFILE = TravellerProfile(
    passport_nationality="India",
    passport_type="ordinary",
    country_of_residence="United Kingdom",
    city_of_residence="Edinburgh",
    uk_immigration_status="Graduate visa",
    uk_permission_expiry=date(2027, 12, 23),
    travel_purpose="tourism",
)
