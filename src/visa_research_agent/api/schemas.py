"""Request and lightweight response models specific to the HTTP API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class VisaPlanRequest(ApiModel):
    destination: str = Field(min_length=1)

    @field_validator("destination")
    @classmethod
    def normalize_destination(cls, value: str) -> str:
        return value.strip().lower()


class ErrorDetail(ApiModel):
    message: str
    supported_destinations: list[str] | None = None
