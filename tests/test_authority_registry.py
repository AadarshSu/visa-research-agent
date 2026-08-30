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
    MAXIMUM_AUTO_TRUSTED_DOMAINS,
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
from visa_research_agent.domain.models import DestinationConfig

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


# --- Reviewed domains: the escape hatch, and the ways it could quietly fail ------------------


def test_a_reviewed_domain_leads_the_set_because_a_person_confirmed_that_one() -> None:
    """Canada is the case. The rule established that five `gc.ca` domains belong to the Canadian
    government; a person established that `canada.ca` is where IRCC's guidance actually is. The
    second is a stronger claim and has to be searched first."""

    row = CountryAuthorities(
        code="CA",
        name="Canada",
        trusted=["travel.gc.ca", "international.gc.ca"],
        reviewed={"canada.ca": "official website of the Government of Canada — Wikidata P856/P17"},
    )

    assert row.domains == ["canada.ca", "travel.gc.ca", "international.gc.ca"]


def test_a_reviewed_domain_displaces_rather_than_widens() -> None:
    """The cap bounds cost — three searches per domain, a divided crawl budget, ten shortlist
    places. A correction must not buy its way past that; it takes the weakest domain's place."""

    row = CountryAuthorities(
        code="XX",
        name="Example",
        trusted=["a.gov.xx", "b.gov.xx", "c.gov.xx", "d.gov.xx", "e.gov.xx"],
        reviewed={"real-authority.xx": "confirmed"},
    )

    assert len(row.domains) == MAXIMUM_AUTO_TRUSTED_DOMAINS
    assert row.domains[0] == "real-authority.xx"
    assert "e.gov.xx" not in row.domains


def test_a_reviewed_domain_needs_the_evidence_that_justified_it() -> None:
    """It bypasses the rule that keeps commercial agencies out. Without a reason there is nothing
    standing behind it, and nobody later can tell a checked domain from a guessed one."""

    with pytest.raises(ValueError, match="need the evidence"):
        CountryAuthorities(code="IT", name="Italy", reviewed={"esteri.it": "   "})


def test_a_domain_cannot_be_reviewed_and_unconfirmed_at_once() -> None:
    with pytest.raises(ValueError, match="cannot be both"):
        CountryAuthorities(
            code="IT",
            name="Italy",
            reviewed={"esteri.it": "confirmed"},
            unconfirmable=["esteri.it"],
        )


async def test_a_rebuild_keeps_the_corrections_a_person_made() -> None:
    """The one way `visa-discover registry` could do real damage. `trusted` and `unconfirmable` are
    search output and are meant to be replaced; a reviewed domain is a correction, and regenerating
    over it would quietly undo every fix in the file — with the plans still resolving, against the
    wrong domains again."""

    provider = StubProvider({"Italy": ["https://www.mise.gov.it/visa"]})
    existing = AuthorityRegistry(
        schema_version=1,
        generated_at=NOW,
        countries=[
            CountryAuthorities(
                code="IT",
                name="Italy",
                trusted=["stale.gov.it"],
                reviewed={"esteri.it": "official website of the Italian foreign ministry"},
            )
        ],
    )

    registry, _ = await build_authority_registry(
        countries(country("IT", "Italy", ["it"])),
        provider,
        denylist(),
        existing=existing,
        rebuild=True,
        sleep=no_sleep,
        now=lambda: NOW,
    )

    row = registry.get("IT")
    assert row is not None
    assert "esteri.it" in row.reviewed, "a rebuild must never drop a person's correction"
    assert row.trusted == ["mise.gov.it"], "search output is replaced, as intended"
    assert row.domains[0] == "esteri.it"


async def test_a_rebuilt_country_does_not_re_list_a_promoted_domain_as_unconfirmed() -> None:
    """It would fail validation on the next load, so the file would stop loading entirely."""

    provider = StubProvider({"Italy": ["https://www.esteri.it/visa", "https://www.mise.gov.it/v"]})
    existing = AuthorityRegistry(
        schema_version=1,
        generated_at=NOW,
        countries=[
            CountryAuthorities(
                code="IT", name="Italy", reviewed={"esteri.it": "the Italian foreign ministry"}
            )
        ],
    )

    registry, _ = await build_authority_registry(
        countries(country("IT", "Italy", ["it"])),
        provider,
        denylist(),
        existing=existing,
        rebuild=True,
        sleep=no_sleep,
        now=lambda: NOW,
    )

    row = registry.get("IT")
    assert row is not None
    assert "esteri.it" not in row.unconfirmable


def test_the_committed_file_loads_and_every_reviewed_domain_carries_its_evidence() -> None:
    """The real file, not a fixture. A reviewed domain is the one place a person overrides the
    trust rule, so the guard that each carries a reason has to hold on what is actually shipped."""

    from visa_research_agent.discovery.registry import load_authority_registry as load_real

    registry = load_real()

    assert registry.countries, "the committed registry must not be empty"
    for row in registry.countries:
        for domain, reason in row.reviewed.items():
            assert len(reason.strip()) > 20, f"{row.code}/{domain} has no usable evidence"
        assert len(row.domains) <= MAXIMUM_AUTO_TRUSTED_DOMAINS


def test_every_committed_row_builds_the_config_a_corridor_needs() -> None:
    """The registry is only useful if its rows survive `DestinationConfig`, which is what both the
    corpus build and the request path construct from them.

    Written after `gov.bg` shipped in the entry 111 batch and made Bulgaria unresearchable: it is a
    public suffix, so the validator refused it, and the country failed at construction rather than
    crawling thinly. The reviewer's note was correct about the site — `www.gov.bg` really is the
    Council of Ministers — and nothing checked that the domain they wrote could be loaded. Every
    other `www.gov.XX` row in the file exists because of the same rule, so the convention was there
    to follow and only this test makes it enforced rather than remembered.
    """

    from visa_research_agent.discovery.registry import load_authority_registry as load_real

    for row in load_real().countries:
        if not row.domains:
            continue
        DestinationConfig(
            slug=row.name.lower().replace(" ", "-"),
            display_name=row.name,
            route_type="national",
            implementation_status="available",
            trusted_domains=list(row.domains),
        )
