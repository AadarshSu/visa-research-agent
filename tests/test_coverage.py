"""The gate: is a country's stored corpus good enough to serve a corridor?

Two halves that are never added together. The first is a regression check over the one traveller
`oracle/selection_oracle.yaml` covers and should stay at 47 of 47; the second measures the dimension
that actually varies, which is the traveller. TODO item 37 exists because the first returns 100% and
says nothing.

Everything here is arithmetic over three stores. Nothing fetches, searches or calls a model — that
is a requirement of the command rather than a convenience of the tests, because entry 81 measured
"roles filled" swinging by two on identical input and three consecutive entries were wrong for
leaning on it.
"""

import io
from datetime import UTC, datetime
from pathlib import Path

import pytest

from visa_research_agent.discovery.corpus import CorpusEntry, CountryCorpus
from visa_research_agent.discovery.coverage import (
    coverage,
    families_in,
    known_answers,
    report,
)
from visa_research_agent.discovery.selection_recall import DEFAULT_ORACLE_PATH, load_oracle

REPOSITORY = Path(__file__).resolve().parent.parent
NOW = datetime(2026, 8, 28, tzinfo=UTC)

COUNTRIES = (
    "india",
    "germany",
    "france",
    "brazil",
    "japan",
    "kenya",
    "mexico",
    "norway",
    "poland",
    "sweden",
    "canada",
)
SLUGS = frozenset(COUNTRIES)

AUTHORITY = "https://authority.gov.example"


def entry(url: str, *, parent: str = "", depth: int = 1) -> CorpusEntry:
    return CorpusEntry(url=url, depth=depth, discovered_from=parent, first_seen=NOW, last_seen=NOW)


def corpus_of(entries: list[CorpusEntry], *, code: str = "NL") -> CountryCorpus:
    return CountryCorpus(country_code=code, country_name="Elsewhere", built_at=NOW, entries=entries)


def gateway_site(opened: int) -> CountryCorpus:
    """A family of eleven `visa/apply-{country}` pages, `opened` of which lead to a checklist."""

    index = f"{AUTHORITY}/visa/apply"
    entries = [entry(index, parent=f"{AUTHORITY}/", depth=0)]
    for position, country in enumerate(COUNTRIES):
        member = f"{AUTHORITY}/visa/apply-{country}"
        entries.append(entry(member, parent=index))
        if position < opened:
            entries.append(entry(f"{AUTHORITY}/visa/checklist-{country}", parent=member, depth=2))
    return corpus_of(entries)


# --- half two: the per-traveller family --------------------------------------------------------


def test_a_family_is_grouped_the_way_the_crawler_reserves_budget_for_one() -> None:
    """The same keys, the same pattern, the same minimum. A report describing families the crawl's
    reservation would never spend a page on would be a gate nobody can act on."""

    families = families_in(gateway_site(opened=0), SLUGS, countries=200)
    assert [family.key for family in families] == [f"{AUTHORITY}/visa/apply-{{}}"]
    assert families[0].held == len(COUNTRIES)


def test_an_unopened_family_has_no_shape_and_is_not_guessed_at() -> None:
    """Nothing distinguishes a gateway from a leaf before a member is opened, which is exactly why
    `FamilyQueues` gives every family its turn rather than backing a winner."""

    family = families_in(gateway_site(opened=0), SLUGS, countries=200)[0]
    assert family.shape == "unopened"
    assert family.opened == 0


def test_a_gateway_is_told_from_a_leaf_by_whether_its_children_are_per_traveller() -> None:
    """A plain child count does not separate them — two Singaporean members yield three children and
    the Dutch equivalent yields 2.4 apiece. Asking whether the child is about one country does."""

    gateway = families_in(gateway_site(opened=4), SLUGS, countries=200)[0]
    assert gateway.shape == "gateway"
    assert gateway.country_named_children == 4

    index = f"{AUTHORITY}/visa/apply"
    entries = [entry(index, parent=f"{AUTHORITY}/", depth=0)]
    for country in COUNTRIES:
        member = f"{AUTHORITY}/visa/apply-{country}"
        entries.append(entry(member, parent=index))
        entries.append(entry(f"{AUTHORITY}/help/contact-us", parent=member, depth=2))
    leaf = families_in(corpus_of(entries), SLUGS, countries=200)[0]
    assert leaf.opened == len(COUNTRIES)
    assert leaf.shape == "leaf"
    assert leaf.country_named_children == 0


def test_a_family_no_single_page_lists_is_reported_and_marked_unreservable() -> None:
    """The one place this module deliberately groups differently from `LinkCrawler._queue`, and it
    is what makes the United Kingdom's fee wizard visible at all. `_queue` groups the links found on
    one page; this groups across the corpus. Per-page grouping reproduces entry 88's NL 9 / SG 1 /
    GB 0 exactly, and would report a country with a per-traveller dimension as having none."""

    index = f"{AUTHORITY}/visa/apply"
    listed = [entry(index, parent=f"{AUTHORITY}/", depth=0)]
    spread = []
    for country in COUNTRIES:
        listed.append(entry(f"{AUTHORITY}/visa/apply-{country}", parent=index))
        # One fee page per country, each reached from its own parent — never listed together.
        spread.append(
            entry(f"{AUTHORITY}/visa/fees/{country}", parent=f"{AUTHORITY}/visa/apply-{country}")
        )
    families = {
        family.key: family
        for family in families_in(corpus_of([*listed, *spread]), SLUGS, countries=200)
    }
    assert families[f"{AUTHORITY}/visa/apply-{{}}"].reservable
    assert not families[f"{AUTHORITY}/visa/fees/{{}}"].reservable


def test_a_family_far_short_of_the_world_is_bounded_by_the_authority_not_incomplete() -> None:
    """Singapore holds 32 of 198 and the missing 166 are behind a selector, so no crawl budget
    reaches them (entry 82). That is a verdict somebody can promote on, not a shortfall."""

    country = coverage(
        gateway_site(opened=0),
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="nowhere",
        slugs=SLUGS,
        countries=200,
    )
    assert country.families[0].completeness == pytest.approx(0.055)
    assert country.verdict == "bounded by the authority"


def test_a_complete_gateway_that_was_barely_opened_is_incomplete() -> None:
    """The case entry 88 fixed on one country: the members are held, and the page that answers a
    specific traveller is one hop below a member nobody opened."""

    country = coverage(
        gateway_site(opened=2),
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="nowhere",
        slugs=SLUGS,
        countries=11,
    )
    assert country.families[0].is_complete
    assert country.families[0].opened_share == pytest.approx(2 / 11)
    assert country.verdict == "incomplete"


def test_a_gateway_walked_to_its_leaves_is_covered() -> None:
    """The shape a finished country has: every gateway opened, and the leaves each one leads to
    opened as well. The leaves are a family in their own right — the Netherlands' four
    `checklist-schengen-visa-…/{}` families are exactly this — so a country is not covered while
    they sit unopened, whatever the gateway above them reads."""

    index = f"{AUTHORITY}/visa/apply"
    entries = [entry(index, parent=f"{AUTHORITY}/", depth=0)]
    for country in COUNTRIES:
        member = f"{AUTHORITY}/visa/apply-{country}"
        leaf = f"{AUTHORITY}/visa/checklist-{country}"
        entries.append(entry(member, parent=index))
        entries.append(entry(leaf, parent=member, depth=2))
        entries.append(entry(f"{AUTHORITY}/help/contact-us", parent=leaf, depth=3))
    walked = coverage(
        corpus_of(entries),
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="nowhere",
        slugs=SLUGS,
        countries=11,
    )
    assert {family.shape for family in walked.families} == {"gateway", "leaf"}
    assert walked.verdict == "covered"


def test_a_complete_family_nobody_opened_is_incomplete_because_its_shape_is_unknown() -> None:
    """An unopened URL is still a usable candidate, so `opened` is not itself coverage. But a family
    nobody has opened cannot be told from a gateway hiding a checklist apiece, and entry 88 is the
    record of what that cost. The honest verdict is "go and look", not "covered"."""

    country = coverage(
        gateway_site(opened=0),
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="nowhere",
        slugs=SLUGS,
        countries=11,
    )
    assert country.families[0].shape == "unopened"
    assert country.verdict == "incomplete"


def test_a_country_with_no_family_defers_to_the_half_that_has_rows() -> None:
    """`no per-traveller dimension` is a **deferral**, not a measurement — its sentence says the
    known-answer half settles the country. So it may only be said where that half has rows."""

    plain = corpus_of([entry(f"{AUTHORITY}/visa/apply", depth=0)])
    country = coverage(
        plain,
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="japan",
        slugs=SLUGS,
        countries=200,
    )
    assert country.families == ()
    assert country.known != ()
    assert country.verdict == "no per-traveller dimension"


def test_a_country_neither_half_can_speak_for_is_ungraded_not_passed() -> None:
    """The 43 built on 2026-08-30, and what the gate said about them. With no family and no oracle
    row, `no per-traveller dimension` deferred to a half holding nothing, and 42 of 53 countries
    read as passes nobody had earned. TODO item 43."""

    plain = corpus_of([entry(f"{AUTHORITY}/visa/apply", depth=0)])
    country = coverage(
        plain,
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="nowhere",
        slugs=SLUGS,
        countries=200,
    )
    assert country.families == ()
    assert country.known == ()
    assert country.verdict == "ungraded"


def test_a_family_grades_a_country_the_oracle_has_never_seen() -> None:
    """Only the *deferral* needs the oracle. A country outside it with a per-traveller family is
    measured from that family exactly as before — which is why Portugal reads `bounded by the
    authority` and not `ungraded`."""

    country = coverage(
        gateway_site(opened=11),
        load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH),
        slug="nowhere",
        slugs=SLUGS,
        countries=200,
    )
    assert country.known == ()
    assert country.verdict == "bounded by the authority"


def test_a_perfect_known_half_does_not_make_a_country_covered() -> None:
    """The failure this module exists to avoid, in one test. Every page the oracle named is held —
    the 100% of 2026-08-28 — and the country is still unserved for 197 other residences, because
    the oracle is `IN/GB/tourism` and cannot see them. Known problem 33."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    japan = next(row for row in oracle.corridors if row.slug == "japan")
    answers = [entry(page.url) for pages in japan.answers.values() for page in pages]
    site = gateway_site(opened=2)
    country = coverage(
        site.model_copy(update={"entries": [*site.entries, *answers]}),
        oracle,
        slug="japan",
        slugs=SLUGS,
        countries=11,
    )
    assert country.known[0].held == country.known[0].answerable == len(japan.answers)
    assert country.verdict == "incomplete"


def test_the_text_column_counts_what_the_selector_could_read() -> None:
    """Singapore holds 32 members and stored text for four. Coverage and legibility are different
    numbers with different fixes, so they are different columns."""

    members = {f"{AUTHORITY}/visa/apply-{country}" for country in COUNTRIES[:3]}
    family = families_in(
        gateway_site(opened=0),
        SLUGS,
        countries=200,
        indexed=lambda urls: {url for url in urls if url in members},
    )[0]
    assert family.text_held == 3
    assert family.held == len(COUNTRIES)


def test_a_member_that_was_read_and_linked_nothing_is_not_a_crawl_gap() -> None:
    """The Netherlands defect, as one assertion (entry 101).

    `opened` counts a member some entry names as its `discovered_from` — a member that *fathered a
    link*. A member fetched from a site that links nowhere onward reads as never fetched, so the
    gate called for a rebuild to go and get pages it already had: the Dutch schengen family scored
    39% opened while every one of its 184 members held stored text, and the rebuild run to check
    crawled 2,965 pages for 27 new entries.

    Here nothing led anywhere and the index holds every member, so the family is fully read and the
    verdict must not ask for a crawl."""

    corpus = gateway_site(opened=0)
    everything = {f"{AUTHORITY}/visa/apply-{country}" for country in COUNTRIES}
    family = families_in(
        corpus, SLUGS, countries=len(COUNTRIES), indexed=lambda urls: everything.intersection(urls)
    )[0]

    assert family.opened == 0, "nothing led on, which is true and is not the question"
    assert family.read == len(COUNTRIES), "and every one of them was fetched"
    assert family.read_share == 1.0


def test_the_gateway_test_stays_on_what_led_on_so_both_sides_agree() -> None:
    """`shape` divides country-named children by opened members, so swapping `read` into the
    denominator alone would flip a gateway to a leaf on the arithmetic rather than the evidence.
    On the Netherlands that is 168 children over 72 opened — a gateway — against 168 over 185
    read, which is not."""

    corpus = gateway_site(opened=3)
    everything = {f"{AUTHORITY}/visa/apply-{country}" for country in COUNTRIES}
    family = families_in(
        corpus, SLUGS, countries=len(COUNTRIES), indexed=lambda urls: everything.intersection(urls)
    )[0]

    assert family.read > family.opened, "the fixture has the gap this test is about"
    assert family.shape == "gateway", "three opened members each led to their own checklist"


def test_a_family_nobody_fetched_still_has_no_shape() -> None:
    """`unopened` now means *unread*, and with no index to say otherwise it is unchanged."""

    family = families_in(gateway_site(opened=0), SLUGS, countries=len(COUNTRIES))[0]

    assert family.read == 0
    assert family.shape == "unopened"


# --- half one: the answers a human named -------------------------------------------------------


def test_a_host_alias_is_not_a_miss() -> None:
    """The first run of this measurement read 46 of 47, and the miss was `www.gdrfad.gov.ae`
    against `gdrfad.gov.ae` — the same page. A number that treats those as different is wrong in
    the direction that looks like a finding."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    corridor = next(row for row in oracle.corridors if row.slug == "japan")
    named = next(iter(corridor.answers.values()))[0].url
    aliased = (
        named.replace("https://www.", "http://", 1)
        if named.startswith("https://www.")
        else named.replace("https://", "https://www.", 1)
    )
    held = known_answers(oracle, corpus_of([entry(aliased)], code="JP"), "japan")[0]
    assert held.held == 1
    assert held.aliased


def test_a_missing_answer_names_the_role_and_the_page() -> None:
    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    empty = next(
        r
        for r in known_answers(oracle, corpus_of([], code="JP"), "japan")
        if r.corridor.endswith("IN/GB/tourism")
    )
    assert empty.held == 0
    assert empty.answerable == len(
        next(row for row in oracle.corridors if row.slug == "japan").answers
    )
    assert set(empty.missing) == set(
        next(row for row in oracle.corridors if row.slug == "japan").answers
    )


def test_a_country_outside_the_oracle_reports_nothing_rather_than_zero() -> None:
    """Half one can only speak for the ten corridors somebody curated. A country it has never seen
    must not be reported as 0 of 0 held, which reads as a failure."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    assert known_answers(oracle, corpus_of([], code="XX"), "atlantis") == []


def test_the_committed_oracle_holds_for_every_curated_traveller() -> None:
    """The regression half, run for real, and **per traveller** — one number per curated profile
    rather than one for the fixture. It is the only test here that touches `var/corpus/`, and it is
    skipped rather than failed where those stores are absent: they are built by a job that spends
    search quota, not by the test suite."""

    from visa_research_agent.discovery.corpus import FileCorpusStore
    from visa_research_agent.discovery.lexicon import get_country_registry

    store = FileCorpusStore(REPOSITORY / "var" / "corpus")
    if not store.countries():
        pytest.skip("no corpus is built in this checkout")
    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    registry = get_country_registry()
    totals: dict[str, list[int]] = {}
    for code in store.countries():
        corpus = store.load(code)
        country = registry.get(code)
        assert corpus is not None and country is not None
        for row in known_answers(oracle, corpus, country.slug):
            running = totals.setdefault(row.traveller, [0, 0, 0])
            running[0] += row.held
            running[1] += row.answerable
            running[2] += row.roles
    assert set(totals) == {"IN/GB/tourism", "PH/PH/tourism"}
    for traveller, (held, answerable, _) in totals.items():
        assert held == answerable, f"{traveller} lost an answer the corpus used to hold"
    # 47 over the ten countries entry 91 curated, plus the two Czech roles entry 127 added and the
    # Dutch `general_entry` entry 128 added — the answers named from outside the selector's pool,
    # all of them held by the corpus.
    assert totals["IN/GB/tourism"][1] == 50
    # 41 as entry 91 curated it, plus the Dutch `general_entry` — the same EES leaflet as the
    # Indian row, because it is nationality-independent and nobody had looked (entry 129).
    assert totals["PH/PH/tourism"][1] == 42


def test_the_traveller_moves_what_is_answerable_which_is_the_whole_point() -> None:
    """Both travellers read 100% *held*, and that is not the finding — the denominators are. The
    same ten corpora answer 47 of 60 roles for the curated Indian traveller and 41 of 60 for the
    Filipino one, which is the dimension a single-traveller oracle could not show at all.

    **Held is a weak number for the `PH/PH` half and this test does not lean on it.** Those rows
    were curated with `visa-discover contention`, which builds its set *from* the corpus, so a page
    named there is in the corpus by construction — see entry 91. The `IN/GB` rows were curated from
    the page-text index, which holds 1,691 pages the corpus does not, so their 100% is a finding."""

    from visa_research_agent.discovery.corpus import FileCorpusStore
    from visa_research_agent.discovery.lexicon import get_country_registry

    store = FileCorpusStore(REPOSITORY / "var" / "corpus")
    if not store.countries():
        pytest.skip("no corpus is built in this checkout")
    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    registry = get_country_registry()
    answerable: dict[str, int] = {}
    for code in store.countries():
        country = registry.get(code)
        corpus = store.load(code)
        assert corpus is not None and country is not None
        for row in known_answers(oracle, corpus, country.slug):
            answerable[row.traveller] = answerable.get(row.traveller, 0) + row.answerable
    assert answerable["IN/GB/tourism"] > answerable["PH/PH/tourism"]


def test_a_role_an_official_tool_settles_is_credited_and_kept_apart() -> None:
    """The product has always treated this as resolved — `audit.py` puts `resolved_decision_tool` in
    the *resolved* group, "the authority publishes it only as a tool". The coverage metric did not,
    and so reported France as answering two of six when a traveller gets an authoritative path for
    five. Entry 60's heading is "a questionnaire **is** an answer"; what it forbids is filling the
    role's content from one, which is a different claim.

    Credited, and never added into `held` or `answerable` — a tool-settled `document_checklist`
    still means not one requirement may be listed.
    """

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    france = next(row for row in oracle.corridors if row.corridor == "france/PH/PH/tourism")
    row = next(
        r
        for r in known_answers(oracle, corpus_of([], code="FR"), "france")
        if r.corridor == france.corridor
    )
    assert set(row.settled) == set(france.tools)
    assert row.answerable == len(france.answers)
    assert row.held + len(row.settled) <= row.roles


def test_a_role_a_page_answers_is_not_also_counted_as_settled() -> None:
    """The two columns are reported side by side, so a role in both would inflate the total. A page
    answer wins: it is citable and a tool never is."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    for corridor in oracle.corridors:
        rows = known_answers(oracle, corpus_of([], code="XX"), corridor.slug)
        row = next(r for r in rows if r.corridor == corridor.corridor)
        assert not set(row.settled) & set(corridor.answers)


def test_the_report_shows_what_the_traveller_can_act_on_without_merging_the_columns() -> None:
    from visa_research_agent.discovery.cli import print_coverage

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    stream = io.StringIO()
    print_coverage(
        report(
            [coverage(corpus_of([], code="FR"), oracle, slug="france", slugs=SLUGS, countries=11)]
        ),
        stream,
    )
    printed = stream.getvalue()
    assert "settled by an official tool" in printed
    assert "of the traveller's questions accounted for" in printed
    # The two are still separable in the output — merging them is what would hide the difference
    # between a page this project can cite and a form only the traveller can fill in.
    assert "by a page" in printed


def test_a_role_that_does_not_arise_is_counted_apart_from_one_nobody_answered() -> None:
    """Singapore's Philippine row read two of six while resolving perfectly. A Filipino needs no
    visa, so four of the six questions do not arise — no application, so no checklist, route, fee or
    processing time. Recording them `unanswered` claimed the store had failed to find four pages
    when what it had found was that there is nothing to find. TODO item 39."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    singapore = next(r for r in oracle.corridors if r.corridor == "singapore/PH/PH/tourism")
    row = next(
        r
        for r in known_answers(oracle, corpus_of([], code="SG"), "singapore")
        if r.corridor == singapore.corridor
    )
    assert set(row.not_applicable) == {
        "document_checklist",
        "application_route",
        "fees",
        "processing_times",
    }
    assert row.answerable == 2
    # Every one of the six is accounted for: two answered, four that do not arise, none open.
    assert row.answerable + len(row.not_applicable) + len(row.settled) == row.roles


def test_the_same_country_keeps_those_roles_for_a_traveller_who_does_need_a_visa() -> None:
    """The control. India is on the very list the Philippines is absent from, so all six questions
    arise for that traveller and all six are answered — which is what makes the Philippine row's
    four a fact about the corridor and not about Singapore's website."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    indian = next(r for r in oracle.corridors if r.corridor == "singapore/IN/GB/tourism")
    assert indian.not_applicable == {}
    assert len(indian.answers) == 6


def test_a_corridor_answering_nothing_still_counts_in_the_denominator() -> None:
    """France and Sweden answer none of their six roles for the Philippine traveller. Skipping such
    a corridor took `answerable` from 24 of 60 to 24 of 48 — a denominator error flattering exactly
    the traveller this half of the fixture exists to be honest about."""

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    rows = {row.corridor for row in known_answers(oracle, corpus_of([], code="FR"), "france")}
    assert "france/PH/PH/tourism" in rows


# --- the report ---------------------------------------------------------------------------------


def test_the_command_prints_both_halves_and_never_adds_them() -> None:
    from visa_research_agent.discovery.cli import print_coverage

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    stream = io.StringIO()
    print_coverage(
        report(
            [
                coverage(
                    gateway_site(opened=2),
                    oracle,
                    slug="nowhere",
                    slugs=SLUGS,
                    countries=11,
                )
            ],
            unbuilt=["ZZ"],
        ),
        stream,
    )
    printed = stream.getvalue()
    assert "half 1" in printed and "half 2" in printed
    assert "incomplete" in printed
    assert "no corpus at all for ZZ" in printed
    assert "selection-recall" in printed


def test_the_report_names_the_ungraded_countries_once_at_the_end() -> None:
    """The per-country lines each carry their meaning string, and a reader scanning 53 identical
    sentences takes the shape of a pass from the column. So it is also said once, plainly, with the
    countries named — and it is kept apart from `unbuilt`, which is a different absence: no corpus
    at all rather than a corpus nothing graded."""

    from visa_research_agent.discovery.cli import print_coverage

    oracle = load_oracle(REPOSITORY / DEFAULT_ORACLE_PATH)
    plain = corpus_of([entry(f"{AUTHORITY}/visa/apply", depth=0)], code="XX")
    stream = io.StringIO()
    print_coverage(
        report(
            [coverage(plain, oracle, slug="nowhere", slugs=SLUGS, countries=200)],
            unbuilt=["ZZ"],
        ),
        stream,
    )
    printed = stream.getvalue()
    assert "UNGRADED — 1 of 1: XX." in printed
    assert "not a corpus that passed" in printed
    assert "no corpus at all for ZZ" in printed
    assert "the guidance is centralised" not in printed
