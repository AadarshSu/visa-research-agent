"""Request and lightweight response models specific to the HTTP API."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.domain.models import TravellerProfile, TravelPurpose


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(ApiModel):
    status: Literal["ok"] = "ok"


class DestinationSummary(ApiModel):
    slug: str
    name: str
    route_type: Literal["national", "schengen_member"]
    status: Literal["planned", "available"]


class DestinationsResponse(ApiModel):
    destinations: list[DestinationSummary]


def normalise_country(value: str) -> str:
    """Accept a country however a person wrote it, and store the one canonical form.

    "IN", "in", "India" and "Republic of India" are the same country; corridors, cache keys and
    every lexicon lookup are keyed by the ISO code, so the conversion happens once, here.
    """

    cleaned = value.strip()
    registry = get_country_registry()
    if len(cleaned) == 2 and cleaned.isalpha() and registry.get(cleaned.upper()) is not None:
        return cleaned.upper()
    named = registry.code_for_name(cleaned)
    if named is None:
        raise ValueError(f"{cleaned} is not a country this agent holds reference data for")
    return named


class TravellerRequest(ApiModel):
    """The traveller a request is asking about.

    Only the passport, the country applied from and the purpose are required: those three select
    the guidance. The rest is optional because a plan that does not use a detail should not ask
    for it.
    """

    passport_nationality: str = Field(min_length=1)
    country_of_residence: str = Field(min_length=1)
    travel_purpose: TravelPurpose = "tourism"
    city_of_residence: str | None = None
    residence_status: str | None = None
    residence_permission_expiry: date | None = None

    _normalise = field_validator("passport_nationality", "country_of_residence")(normalise_country)

    def to_profile(self) -> TravellerProfile:
        return TravellerProfile(
            passport_nationality=self.passport_nationality,
            passport_type="ordinary",
            country_of_residence=self.country_of_residence,
            travel_purpose=self.travel_purpose,
            city_of_residence=self.city_of_residence,
            residence_status=self.residence_status,
            residence_permission_expiry=self.residence_permission_expiry,
        )


class VisaPlanRequest(ApiModel):
    destination: str = Field(min_length=1)
    traveller: TravellerRequest | None = None
    """Absent means the default profile. The interface opens on one, and the offline Singapore
    fixture was recorded against it."""

    @field_validator("destination")
    @classmethod
    def normalize_destination(cls, value: str) -> str:
        return value.strip().lower()


class ErrorDetail(ApiModel):
    message: str
    supported_destinations: list[str] | None = None
