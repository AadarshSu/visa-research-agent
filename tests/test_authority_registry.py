"""The committed country → authority-domain registry, and the offline build that produces it.

Nothing here reaches the network. The point of DECISIONS entry 34 is that deciding *whose* domains
a country may be researched from stopped being a per-request question, so the tests that matter are
about what happens when the file is wrong, incomplete, or interrupted — not about search.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from visa_research_agent.discovery.automatic import auto_trusted_domains
from visa_research_agent.discovery.bootstrap import BootstrapReport, DomainProposal
from visa_research_agent.discovery.lexicon import Country, CountryRegistry, Denylist
from visa_research_agent.discovery.models import SearchResult
from visa_research_agent.discovery.registry import (
    AuthorityRegistry,
    CountryAuthorities,
    authorities_from,
    load_authority_registry,
)
from visa_research_agent.discovery.registry_build import (
    build_authority_registry,
    write_registry,
)
from visa_research_agent.discovery.search import SearchError

pytestmark = pytest.mark.anyio

NOW = datetime(2026, 8, 18, 9, 0, tzinfo=UTC)


def country(code: str, name: str, tlds: list[str]) -> Country:
    return Country(code=code, name=name, tlds=tlds)


def countries(*items: Country) -> CountryRegistry:
    return CountryRegistry(schema_version=1, countries=list(items))


def denylist() -> Denylist:
    return Denylist(schema_version=1, commercial=["axa-schengen.com"])


class StubProvider:
    """Returns fixed results per country name, and can be told to fail for one of them."""

    def __init__(self, by_country: dict[str, list[str]], failing: set[str] | None = None) -> None:
        self.by_country = by_country
        self.failing = failing or set()
        self.queries: list[str] = []

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        self.queries.append(query)
        for name, urls in self.by_country.items():
            if name.lower() in query.lower():
                if name in self.failing:
                    raise SearchError("the search provider answered HTTP 429")
                return [
                    SearchResult(url=url, title="", snippet="", query=query, rank=rank)
                    for rank, url in enumerate(urls)
                ]
        return []


async def no_sleep(_: float) -> None:
    return None


# --- The file itself ---------------------------------------------------------------------------


def test_a_domain_cannot_be_both_trusted_and_unconfirmable() -> None:
    """They mean opposite things. A row asserting both is a generator bug, and it must not load."""

    with pytest.raises(ValueError, match="cannot be both"):
        CountryAuthorities(
            code="IT", name="Italy", trusted=["esteri.it"], unconfirmable=["esteri.it"]
        )


def test_a_country_cannot_appear_twice() -> None:
    row = CountryAuthorities(code="FR", name="France", trusted=["diplomatie.gouv.fr"])
    with pytest.raises(ValueError, match="cannot appear twice"):
        AuthorityRegistry(schema_version=1, generated_at=NOW, countries=[row, row])


def test_a_registry_survives_being_written_and_read_back(tmp_path: Path) -> None:
    registry = AuthorityRegistry(
        schema_version=1,
        generated_at=NOW,
        countries=[
            CountryAuthorities(code="DE", name="Germany", unconfirmable=["auswaertiges-amt.de"]),
            CountryAuthorities(code="JP", name="Japan", trusted=["mofa.go.jp"]),
        ],
    )
    path = tmp_path / "authority_domains.yaml"
    write_registry(registry, path)

    assert load_authority_registry(str(path)) == registry
    # The header is what tells a reviewer what they are reading and how to regenerate it.
    assert "DECISIONS entry 34" in path.read_text(encoding="utf-8")


def test_rows_are_written_sorted_so_a_regeneration_diffs_cleanly(tmp_path: Path) -> None:
    """A file regenerated monthly is only reviewable if an unchanged country produces no diff."""

    registry = AuthorityRegistry(
        schema_version=1,
        generated_at=NOW,
        countries=[
            CountryAuthorities(code="JP", name="Japan", trusted=["mofa.go.jp"]),
            CountryAuthorities(code="BR", name="Brazil", trusted=["gov.br"]),
        ],
    )
    path = tmp_path / "out.yaml"
    write_registry(registry, path)

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert [row["code"] for row in payload["countries"]] == ["BR", "JP"]


# --- Turning a bootstrap into a row -------------------------------------------------------------


def proposal(domain: str, *, governmental: bool, own: bool) -> DomainProposal:
    return DomainProposal(
        domain=domain,
        looks_governmental=governmental,
        belongs_to_destination=own,
        matched_tlds=["it"] if own else [],
        queries=["q1", "q2"],
    )


def test_a_row_records_the_rules_decision_rather_than_re_judging_it() -> None:
    """Italy, from the real bootstrap on 2026-08-18, and the clearest thing this file surfaces:
    the rule confirms two domains that cannot hold visa guidance while the actual foreign ministry
    sits in `unconfirmable`. That is entry 33's second failure, and committing it is what turns it
    from an invisible per-request outcome into something a person reads."""

    report = BootstrapReport(
        destination_name="Italy",
        proposals=[
            proposal("mise.gov.it", governmental=True, own=True),
            proposal("esteri.it", governmental=False, own=True),
        ],
    )
    accepted, _ = auto_trusted_domains(report)

    row = authorities_from(report, "IT", accepted)

    assert row.trusted == ["mise.gov.it"]
    assert row.unconfirmable == ["esteri.it"]


def test_another_countrys_government_reaches_neither_list() -> None:
    """`travel.state.gov` is a real government describing rules for Americans. It is not withheld
    noise worth committing, and it is certainly not a candidate Italian authority."""

    report = BootstrapReport(
        destination_name="Italy",
        proposals=[
            proposal("mise.gov.it", governmental=True, own=True),
            proposal("state.gov", governmental=True, own=False),
        ],
    )
    accepted, _ = auto_trusted_domains(report)

    row = authorities_from(report, "IT", accepted)

    assert row.trusted == ["mise.gov.it"]
    assert row.unconfirmable == []


# --- The offline build -------------------------------------------------------------------------


async def test_every_country_is_built_and_written(tmp_path: Path) -> None:
    provider = StubProvider(
        {
            "Japan": ["https://www.mofa.go.jp/visa"],
            "Germany": ["https://www.auswaertiges-amt.de/visa"],
        }
    )
    registry, failures = await build_authority_registry(
        countries(country("JP", "Japan", ["jp"]), country("DE", "Germany", ["de"])),
        provider,
        denylist(),
        sleep=no_sleep,
        now=lambda: NOW,
    )

    assert not failures
    assert [row.code for row in registry.countries] == ["DE", "JP"]
    assert registry.get("JP").trusted == ["mofa.go.jp"]  # type: ignore[union-attr]
    # Germany is refused, and that is a result rather than a gap: the row exists and is empty.
    assert registry.get("DE").trusted == []  # type: ignore[union-attr]
    assert registry.get("DE").unconfirmable == ["auswaertiges-amt.de"]  # type: ignore[union-attr]


async def test_a_country_whose_search_failed_is_left_out_rather_than_written_empty(
    tmp_path: Path,
) -> None:
    """The distinction the whole build turns on. An empty `trusted` means the rule confirmed
    nothing, which a reviewer must act on; a search that never ran is not that. Writing one as the
    other would put a false record in a committed file, and the next run would not retry it."""

    provider = StubProvider(
        {"Japan": ["https://www.mofa.go.jp/visa"], "Germany": []}, failing={"Germany"}
    )
    registry, failures = await build_authority_registry(
        countries(country("JP", "Japan", ["jp"]), country("DE", "Germany", ["de"])),
        provider,
        denylist(),
        sleep=no_sleep,
        now=lambda: NOW,
    )

    assert [row.code for row in registry.countries] == ["JP"]
    assert "DE" in failures
    assert "429" in failures["DE"]


async def test_a_build_resumes_rather_than_paying_for_what_it_already_has() -> None:
    """198 countries is 792 searches. An interruption two thirds of the way through must not throw
    away what was already paid for."""

    provider = StubProvider({"Germany": ["https://www.auswaertiges-amt.de/visa"]})
    existing = AuthorityRegistry(
        schema_version=1,
        generated_at=NOW,
        countries=[CountryAuthorities(code="JP", name="Japan", trusted=["mofa.go.jp"])],
    )

    registry, _ = await build_authority_registry(
        countries(country("JP", "Japan", ["jp"]), country("DE", "Germany", ["de"])),
        provider,
        denylist(),
        existing=existing,
        sleep=no_sleep,
        now=lambda: NOW,
    )

    assert [row.code for row in registry.countries] == ["DE", "JP"]
    assert all("Japan" not in query for query in provider.queries), "JP was already paid for"
    assert registry.get("JP").trusted == ["mofa.go.jp"]  # type: ignore[union-attr]


async def test_each_country_is_written_as_it_lands(tmp_path: Path) -> None:
    """So that killing the build keeps everything up to that point, not nothing."""

    provider = StubProvider(
        {"Japan": ["https://www.mofa.go.jp/visa"], "Brazil": ["https://www.gov.br/visa"]}
    )
    written: list[int] = []

    await build_authority_registry(
        countries(country("JP", "Japan", ["jp"]), country("BR", "Brazil", ["br"])),
        provider,
        denylist(),
        sleep=no_sleep,
        now=lambda: NOW,
        write=lambda registry: written.append(len(registry.countries)),
    )

    assert written == [1, 2], "the file must grow with each country, not once at the end"


async def test_countries_are_spaced_because_search_is_someone_elses_service() -> None:
    slept: list[float] = []

    async def sleep(seconds: float) -> None:
        slept.append(seconds)

    provider = StubProvider(
        {"Japan": ["https://www.mofa.go.jp/visa"], "Brazil": ["https://www.gov.br/visa"]}
    )
    await build_authority_registry(
        countries(country("JP", "Japan", ["jp"]), country("BR", "Brazil", ["br"])),
        provider,
        denylist(),
        sleep=sleep,
        seconds_between_countries=4.0,
        now=lambda: NOW,
    )

    # Between the two, never before the first: nothing is owed to a service not yet asked.
    assert slept == [4.0]


def test_the_order_of_trusted_domains_is_preserved_through_a_write(tmp_path: Path) -> None:
    """It is the rule's confidence ordering, not a set. `_trust_priority` puts the most likely visa
    authority first; the cap truncates against that order, and a corridor runs its `site:` queries
    in it. Alphabetising on write would silently reorder the searches every corridor makes."""

    registry = AuthorityRegistry(
        schema_version=1,
        generated_at=NOW,
        countries=[
            CountryAuthorities(
                code="SG",
                name="Singapore",
                trusted=["ica.gov.sg", "mfa.gov.sg", "ask.gov.sg"],
            )
        ],
    )
    path = tmp_path / "out.yaml"
    write_registry(registry, path)

    loaded = load_authority_registry(str(path))
    assert loaded.get("SG").trusted == ["ica.gov.sg", "mfa.gov.sg", "ask.gov.sg"]  # type: ignore[union-attr]
