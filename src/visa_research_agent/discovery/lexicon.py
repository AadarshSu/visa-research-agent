"""Loading the country reference data, scoring vocabulary and denylist.

All three are version-controlled YAML so they can be reviewed and tuned without a code change.
"""

from functools import lru_cache
from typing import Any, Literal

import yaml
from pydantic import Field, model_validator

from visa_research_agent.config.loader import config_path
from visa_research_agent.domain.models import StrictModel
from visa_research_agent.domain.trust import host_is_within


class Country(StrictModel):
    """One country, with the several ways it is written in URLs and link text."""

    code: str = Field(pattern=r"^[A-Z]{2}$")
    name: str = Field(min_length=1)
    synonyms: list[str] = Field(default_factory=list)
    demonyms: list[str] = Field(default_factory=list)
    host_labels: list[str] = Field(default_factory=list)

    @property
    def text_tokens(self) -> list[str]:
        """Every phrase that means this country in prose or a URL path."""

        return sorted({token.lower() for token in [self.name, *self.synonyms, *self.demonyms]})


class CountryRegistry(StrictModel):
    schema_version: Literal[1]
    countries: list[Country] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_codes(self) -> "CountryRegistry":
        codes = [country.code for country in self.countries]
        if len(codes) != len(set(codes)):
            raise ValueError("country codes must be unique")
        return self

    def get(self, code: str) -> Country | None:
        normalized = code.strip().upper()
        return next((c for c in self.countries if c.code == normalized), None)

    def require(self, code: str) -> Country:
        country = self.get(code)
        if country is None:
            raise ValueError(f"country {code} is not in countries.yaml; add it before using it")
        return country


class LexiconTerm(StrictModel):
    phrase: str = Field(min_length=1)
    weight: float


class RoleTerms(StrictModel):
    terms: list[LexiconTerm] = Field(default_factory=list)


class PurposeTerms(StrictModel):
    terms: list[str] = Field(default_factory=list)
    weight: float = 20.0


class OffScopeTerms(StrictModel):
    weight: float = -30.0
    terms: list[str] = Field(default_factory=list)


class Lexicon(StrictModel):
    """The scoring vocabulary, loaded from `discovery_lexicon.yaml`."""

    schema_version: Literal[1]
    link_text_weight: float = 1.2
    heading_weight: float = 0.5
    base_purpose_weight: float = 18.0
    breadth_threshold: int = 2
    index_page_penalty: float = -18.0
    index_page_stems: list[str] = Field(default_factory=list)
    roles: dict[str, RoleTerms] = Field(default_factory=dict)
    purposes: dict[str, PurposeTerms] = Field(default_factory=dict)
    off_scope: OffScopeTerms = Field(default_factory=OffScopeTerms)
    archive_tokens: list[str] = Field(default_factory=list)
    hard_off_scope: list[str] = Field(default_factory=list)
    form_penalty: float = -35.0
    form_terms: list[str] = Field(default_factory=list)
    language_penalty: float = -25.0
    language_terms: list[str] = Field(default_factory=list)
    base_visa_weight: float = 6.0
    nationality_weight: float = 40.0
    purpose_bonus_weight: float = 20.0
    shallow_path_weight: float = 8.0
    depth_penalty_weight: float = -10.0
    mission_host_bonus: float = 8.0
    pdf_checklist_bonus: float = 10.0
    authority_kind_bonus: dict[str, float] = Field(default_factory=dict)

    def off_scope_terms_for(self, purpose: str) -> list[str]:
        """Off-scope terms, minus any that belong to the traveller's own purpose.

        Without this subtraction a study-purpose corridor would penalise the very pages it needs.
        """

        own = {term.lower() for term in self.purposes.get(purpose, PurposeTerms()).terms}
        return [term for term in self.off_scope.terms if term.lower() not in own]


class Denylist(StrictModel):
    """Domains that may never be proposed as authorities."""

    schema_version: Literal[1]
    commercial: list[str] = Field(default_factory=list)
    reference: list[str] = Field(default_factory=list)
    media: list[str] = Field(default_factory=list)

    @property
    def domains(self) -> list[str]:
        return [*self.commercial, *self.reference, *self.media]

    def blocks(self, host: str) -> bool:
        """True when a host is denied, including any subdomain of a denied domain."""

        return host_is_within(host, self.domains)


def _load_yaml(filename: str) -> Any:
    with config_path(filename).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=1)
def get_country_registry() -> CountryRegistry:
    return CountryRegistry.model_validate(_load_yaml("countries.yaml"))


@lru_cache(maxsize=1)
def get_lexicon() -> Lexicon:
    return Lexicon.model_validate(_load_yaml("discovery_lexicon.yaml"))


@lru_cache(maxsize=1)
def get_denylist() -> Denylist:
    return Denylist.model_validate(_load_yaml("discovery_denylist.yaml"))
