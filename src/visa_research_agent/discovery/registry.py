"""The committed answer to "whose domains may this destination be researched from".

DECISIONS entry 34. `ARCHITECTURE.md` has always said domains are decided by a rule **once per
country** and pages by the machine **every corridor**, and the code did not implement the first
half: `bootstrap_destination` ran inside every cold request, keyed its cache per *corridor*, and so
re-derived a country's trusted set from that day's search rankings for every new nationality. The
United States coin flip in entry 22 was that mechanism, diagnosed at the time as a ranking problem.

So the rule's output is generated offline for every country, read by a person once, and committed
here as data. Request-time discovery then starts at the corridor step.

**This is not the human gate DECISIONS entry 19 removed.** That gate was over *URLs*, tens of
thousands of them, and it stays gone — finding the right page is automatic and is the production
goal. This is *domains*, about three per country, still proposed by the same `bootstrap.py` code,
frozen in review rather than approved per request. Entry 19's own finding is the argument for it:
the human it removed was found not to be exercising taste but applying one mechanical rule, and
**committing that rule's output is strictly easier to audit than re-running it live** — the riskiest
automated decision in the system becomes a reviewable diff instead of a search ranking.

What is committed is deliberately narrow. `trusted` is what may be fetched from. `unconfirmable`
names the candidates under the country's own top-level domain whose hostnames carry no governmental
marker — the 19-of-51 gap measured in entry 33 — because that is the one part of the file a reviewer
can act on, and it is where a missing authority will be hiding. Domains rejected as another
country's government, or as commercial agencies, are not carried: they are noise in a file whose
purpose is to be read.
"""

from datetime import datetime
from functools import lru_cache
from typing import Literal

import yaml
from pydantic import Field, model_validator

from visa_research_agent.config.loader import config_path
from visa_research_agent.discovery.bootstrap import BootstrapReport
from visa_research_agent.domain.models import StrictModel

REGISTRY_FILENAME = "authority_domains.yaml"


class CountryAuthorities(StrictModel):
    """One country's reviewed authority domains, and the gap the rule could not close."""

    code: str = Field(pattern=r"^[A-Z]{2}$")
    name: str = Field(min_length=1)
    trusted: list[str] = Field(default_factory=list)
    """Domains confirmed as this country's own government. Empty means the country is refused."""

    unconfirmable: list[str] = Field(default_factory=list)
    """Candidates under this country's own top-level domain with no governmental marker.

    Carried so a reviewer can see what the rule could not confirm, and so a refusal can name it
    rather than claiming nothing was found. **Never a route to trusting any of them** — the rule
    refuses "looks like an authority", and this only records what it refused. See entry 33.
    """

    @model_validator(mode="after")
    def validate_no_domain_is_both(self) -> "CountryAuthorities":
        overlap = set(self.trusted) & set(self.unconfirmable)
        if overlap:
            raise ValueError(
                f"{self.code}: {', '.join(sorted(overlap))} cannot be both trusted and "
                "unconfirmable"
            )
        return self


class AuthorityRegistry(StrictModel):
    """Every country's reviewed domains, as one committed file."""

    schema_version: Literal[1]
    generated_at: datetime
    countries: list[CountryAuthorities] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_codes(self) -> "AuthorityRegistry":
        codes = [country.code for country in self.countries]
        if len(codes) != len(set(codes)):
            raise ValueError("a country cannot appear twice in the authority registry")
        return self

    def get(self, code: str) -> CountryAuthorities | None:
        return next((entry for entry in self.countries if entry.code == code), None)


def authorities_from(report: BootstrapReport, code: str, accepted: list[str]) -> CountryAuthorities:
    """One registry row from a bootstrap and the domains the trust rule accepted from it.

    The accepted list is passed in rather than recomputed, so the file records exactly what
    `auto_trusted_domains` decided — the same function the request path used to call live, with the
    same cap. Nothing here re-judges a domain.
    """

    unconfirmable = sorted(
        proposal.domain
        for proposal in report.proposals
        if proposal.belongs_to_destination
        and not proposal.looks_governmental
        and proposal.domain not in set(accepted)
    )
    return CountryAuthorities(
        code=code,
        name=report.destination_name,
        trusted=accepted,
        unconfirmable=unconfirmable,
    )


def load_authority_registry(path: str | None = None) -> AuthorityRegistry:
    location = config_path(REGISTRY_FILENAME) if path is None else config_path(path)
    with location.open(encoding="utf-8") as handle:
        return AuthorityRegistry.model_validate(yaml.safe_load(handle))


@lru_cache(maxsize=1)
def get_authority_registry() -> AuthorityRegistry:
    return load_authority_registry()
