"""The country page corpus: what it keeps, what it refuses to lose, and what it re-checks.

Every test here is offline and none needs the crawler — the store is a pure structure, and the rules
worth pinning are the ones a plausible simplification would break. See DECISIONS entry 44.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from visa_research_agent.discovery.corpus import (
    CorpusEntry,
    CorpusError,
    CountryCorpus,
    FileCorpusStore,
    merge,
)

FIRST = datetime(2026, 8, 20, 9, 0, tzinfo=UTC)
LATER = datetime(2026, 8, 22, 9, 0, tzinfo=UTC)


def entry(url: str, **overrides: object) -> CorpusEntry:
    payload: dict[str, object] = {
        "url": url,
        "first_seen": FIRST,
        "last_seen": FIRST,
    }
    payload.update(overrides)
    return CorpusEntry.model_validate(payload)


def corpus(*entries: CorpusEntry, trusted: list[str] | None = None) -> CountryCorpus:
    return CountryCorpus(
        country_code="CA",
        country_name="Canada",
        trusted_domains=trusted if trusted is not None else ["canada.ca"],
        built_at=FIRST,
        entries=list(entries),
    )


def test_a_crawl_that_finds_less_never_removes_what_an_earlier_one_found() -> None:
    """The rule the whole store exists for.

    A crawl finding fewer pages is ordinary — search moves, a host times out — and treating that as
    a deletion would rebuild the exact failure being designed away: a page one run has and the next
    does not. Canada's answering page is the concrete case.
    """

    answering = "https://www.canada.ca/entry-requirements-country.html"
    before = corpus(entry(answering), entry("https://www.canada.ca/visit.html"))

    after = merge(before, [entry("https://www.canada.ca/visit.html")], now=LATER)

    assert [item.url for item in after.entries] == [
        answering,
        "https://www.canada.ca/visit.html",
    ]
    kept = after.find("entry-requirements")[0]
    assert kept.last_seen == FIRST, "a page this crawl did not see must not look freshly seen"
    assert kept.times_seen == 1


def test_seeing_a_page_again_keeps_its_first_sighting_and_counts_the_rest() -> None:
    before = corpus(entry("https://www.canada.ca/visit.html"))

    after = merge(before, [entry("https://www.canada.ca/visit.html", last_seen=LATER)], now=LATER)

    kept = after.entries[0]
    assert kept.first_seen == FIRST
    assert kept.last_seen == LATER
    assert kept.times_seen == 2


def test_a_shallower_route_to_the_same_page_replaces_a_deeper_one() -> None:
    """The shortest known way in is what a later crawl should follow."""

    url = "https://www.canada.ca/entry-requirements-country.html"
    before = corpus(entry(url, depth=2, discovered_from="https://www.canada.ca/deep.html"))

    after = merge(
        before,
        [entry(url, depth=1, discovered_from="https://www.canada.ca/check-visa-eta.html")],
        now=LATER,
    )

    assert after.entries[0].depth == 1
    assert after.entries[0].discovered_from.endswith("check-visa-eta.html")


def test_a_later_failure_records_itself_without_erasing_a_page_read_before() -> None:
    """Unreadable once is not withdrawn. Dropping it would be the pruning this store forbids."""

    url = "https://www.canada.ca/visit.html"
    before = corpus(entry(url, status="readable"))

    after = merge(before, [entry(url, status="unreadable", detail="answered HTTP 502")], now=LATER)

    assert after.entries[0].status == "readable", "a 502 today does not unmake yesterday's read"


def test_a_page_that_becomes_readable_clears_its_earlier_failure() -> None:
    url = "https://www.canada.ca/visit.html"
    before = corpus(entry(url, status="unreadable", detail="answered HTTP 502"))

    after = merge(before, [entry(url, status="readable")], now=LATER)

    assert after.entries[0].status == "readable"
    assert after.entries[0].detail == ""


def test_trust_is_applied_when_the_corpus_is_read_not_when_it_was_written() -> None:
    """A corpus outlives the registry row that produced it.

    So a domain a person later removes from `authority_domains.yaml` has to stop being read without
    anyone remembering to rebuild every corpus. The stored list says what was true then.
    """

    held = corpus(
        entry("https://www.canada.ca/visit.html"),
        entry("https://cic.gc.ca/old.html"),
        trusted=["canada.ca", "cic.gc.ca"],
    )

    allowed = held.entries_within(["canada.ca"])

    assert [item.url for item in allowed] == ["https://www.canada.ca/visit.html"]
    assert len(held.entries) == 2, "narrowing what may be read must not delete what was found"


def test_a_corpus_survives_a_round_trip_through_the_store(tmp_path: Path) -> None:
    store = FileCorpusStore(tmp_path)
    store.store(corpus(entry("https://www.canada.ca/visit.html", title="Visit Canada")))

    loaded = store.load("CA")

    assert loaded is not None
    assert loaded.entries[0].title == "Visit Canada"
    assert store.countries() == ["CA"]


def test_a_country_with_no_corpus_reads_as_absent(tmp_path: Path) -> None:
    assert FileCorpusStore(tmp_path).load("CA") is None


def test_an_unreadable_corpus_raises_rather_than_reading_as_an_empty_country(
    tmp_path: Path,
) -> None:
    """Deliberately unlike `corridor_store.py`, and the difference is the contract.

    A corridor that cannot be parsed is safely re-resolved, so it reads as a miss. A corpus is the
    candidate source for every corridor into that country, so treating a corrupt file as "no pages
    here" would turn it into a refusal indistinguishable from a country nobody has built yet.
    """

    (tmp_path / "CA.json").write_text('{"schema_version": 99}', encoding="utf-8")

    with pytest.raises(CorpusError) as raised:
        FileCorpusStore(tmp_path).load("CA")

    assert "not treated as an absence" in str(raised.value)


def test_an_entry_becomes_the_page_link_a_corridor_would_have_crawled() -> None:
    """The corpus stores no scores, so what it hands back has to be scoreable as a fresh link."""

    held = entry(
        "https://www.canada.ca/index_000070.html",
        link_text="Temporary Visitor Visa",
        heading="Visas",
        depth=1,
    )

    link = held.to_link()

    assert link.text == "Temporary Visitor Visa"
    assert link.heading == "Visas"
    assert link.depth == 1


def test_a_naive_timestamp_is_refused() -> None:
    with pytest.raises(ValueError):
        CorpusEntry.model_validate(
            {
                "url": "https://www.canada.ca/visit.html",
                "first_seen": datetime(2026, 8, 20, 9, 0),
                "last_seen": FIRST,
            }
        )


def test_a_page_is_recognised_under_a_host_or_scheme_alias() -> None:
    """Measured on Canada: 3,130 stored URLs are 2,996 pages, and `visas.asp` is held four times.

    Without an equivalence key a superset check reports pages missing that sit right there under
    another host, and a pin fails to match the page it names.
    """

    held = corpus(entry("https://www.cic.gc.ca/english/visit/visas.asp"))

    assert held.holds("http://cic.gc.ca/english/visit/visas.asp")
    assert held.holds("https://CIC.gc.ca/English/visit/visas.asp".lower())
    assert not held.holds("https://www.cic.gc.ca/english/visit/other.asp")


def test_query_strings_are_not_folded_away() -> None:
    """`?qnum=416` and `?qnum=1453` are different pages; Canada publishes 407 of them."""

    held = corpus(entry("https://ircc.canada.ca/english/helpcentre/answer.asp?qnum=416&top=16"))

    assert not held.holds("https://ircc.canada.ca/english/helpcentre/answer.asp?qnum=1453&top=16")


def test_a_proven_page_is_never_demoted_by_a_later_sighting() -> None:
    """A page that answered a corridor does not stop having answered it.

    Without the status ranking a single `502` on a later crawl would demote it to `unreadable`, and
    its retention tier — the one tier that is never evicted — would drop with it.
    """

    url = "https://www.canada.ca/entry-requirements-country.html"
    before = corpus(entry(url, status="proven"))

    seen_again = merge(before, [entry(url, status="unknown")], now=LATER)
    then_failed = merge(seen_again, [entry(url, status="unreadable", detail="502")], now=LATER)

    assert then_failed.entries[0].status == "proven"
    assert then_failed.entries[0].detail == ""


def test_status_only_ever_moves_up() -> None:
    url = "https://www.canada.ca/visit.html"
    held = corpus(entry(url, status="unknown"))

    for arriving, expected in (
        ("unreadable", "unreadable"),
        ("readable", "readable"),
        ("unknown", "readable"),
        ("proven", "proven"),
        ("readable", "proven"),
    ):
        held = merge(held, [entry(url, status=arriving)], now=LATER)
        assert held.entries[0].status == expected, arriving
