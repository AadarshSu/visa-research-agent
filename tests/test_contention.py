"""Rebuilding a corridor's contention set from the store, so an oracle row needs no run.

The first ten oracle rows were curated out of live runs in a throwaway script (entry 87), which is
the thing item 34 objected to one level up. These are the checks that the rebuilt set is the
resolver's own — same scoring, same rejections, same "in contention" — because a second
implementation that drifts would produce ground truth describing a pipeline the product is not.
"""

from datetime import UTC, datetime

from visa_research_agent.discovery.contention import Contention, contention_for, ranked_for_role
from visa_research_agent.discovery.corpus import CorpusEntry, CountryCorpus
from visa_research_agent.discovery.lexicon import get_country_registry, get_lexicon
from visa_research_agent.discovery.models import Corridor
from visa_research_agent.domain.models import DestinationConfig

NOW = datetime(2026, 8, 28, tzinfo=UTC)
HOST = "https://www.mofa.go.jp"


def entry(url: str, *, text: str = "", title: str = "") -> CorpusEntry:
    return CorpusEntry(url=url, link_text=text, title=title, depth=1, first_seen=NOW, last_seen=NOW)


def japan(entries: list[CorpusEntry]) -> CountryCorpus:
    return CountryCorpus(country_code="JP", country_name="Japan", built_at=NOW, entries=entries)


def destination() -> DestinationConfig:
    return DestinationConfig(
        slug="japan",
        display_name="Japan",
        route_type="national",
        implementation_status="available",
        trusted_domains=["mofa.go.jp"],
    )


def contention(
    entries: list[CorpusEntry], *, nationality: str = "PH", residence: str = "PH"
) -> Contention:
    corridor = Corridor(
        destination_slug="japan",
        passport_nationality=nationality,
        applying_from=residence,
        purpose="tourism",
    )
    return contention_for(
        japan(entries),
        destination(),
        corridor,
        countries=get_country_registry(),
        lexicon=get_lexicon(),
        destination_code="JP",
    )


def test_a_candidate_no_role_wants_is_not_in_contention() -> None:
    """ "In contention" is `best_combined() > 0`, which is the resolver's own bound — a page no role
    wants is not worth a fetch and so is not worth curating against either."""

    built = contention(
        [
            entry(f"{HOST}/visa/short-term-stay.html", text="Visa for temporary visitor"),
            entry(f"{HOST}/about/staff/telephone-directory.html", text="Telephone directory"),
        ]
    )
    urls = [candidate.link.url for candidate in built.candidates]
    assert f"{HOST}/visa/short-term-stay.html" in urls
    assert f"{HOST}/about/staff/telephone-directory.html" not in urls


def test_a_page_outside_the_trusted_domains_never_reaches_the_set() -> None:
    """The corpus outlives the registry row that produced it, so the filter is applied at read
    time — a curator must never be offered a page the product would refuse to fetch."""

    built = contention(
        [
            entry(f"{HOST}/visa/short-term-stay.html", text="Visa for temporary visitor"),
            entry("https://www.example.com/visa/japan-visa", text="Japan visa requirements"),
        ]
    )
    assert [candidate.link.url for candidate in built.candidates] == [
        f"{HOST}/visa/short-term-stay.html"
    ]


def test_a_rejected_page_is_counted_rather_than_scored() -> None:
    """Archived, boilerplate, wrong audience and wrong country are the resolver's `reject`, imported
    rather than restated. The count is kept because entry 50 found `wrong_country` firing 33 times
    too often, and only a count made that visible."""

    built = contention(
        [
            entry(f"{HOST}/visa/short-term-stay.html", text="Visa for temporary visitor"),
            entry(f"{HOST}/archive/visa/old-requirements.html", text="Visa requirements"),
        ]
    )
    assert built.rejected == 1
    assert len(built.candidates) == 1


def test_the_traveller_changes_the_ranking_which_is_the_whole_reason_to_widen_the_oracle() -> None:
    """A page naming the traveller's own country in a path segment outranks the generic one, and is
    rejected outright for somebody else. If this did not hold, one oracle row would speak for every
    traveller and known problem 29 would not exist."""

    entries = [
        entry(f"{HOST}/visa/checklist.html", text="Checklist of documents"),
        entry(f"{HOST}/visa/philippines/checklist.html", text="Checklist of documents"),
    ]
    filipino = {
        candidate.link.url: score
        for candidate, score in ranked_for_role(contention(entries), "document_checklist", limit=10)
    }
    indian = {
        candidate.link.url: score
        for candidate, score in ranked_for_role(
            contention(entries, nationality="IN", residence="GB"), "document_checklist", limit=10
        )
    }
    assert (
        filipino[f"{HOST}/visa/philippines/checklist.html"]
        > filipino[f"{HOST}/visa/checklist.html"]
    )
    assert f"{HOST}/visa/philippines/checklist.html" not in indian


def test_a_family_member_gets_no_nationality_bonus_which_is_why_it_ranks_at_the_floor() -> None:
    """Entry 88's defect, reproduced as arithmetic. The nationality bonus needs a whole path segment
    or the anchor text; a country named as the tail of a filename — `…/apply-philippines`, which is
    the shape of every per-traveller family the Netherlands publishes — gets nothing, so all 219
    members score identically and a curator must not expect the ranking to surface the right one."""

    entries = [
        entry(f"{HOST}/visa/checklist.html", text="Checklist of documents"),
        entry(f"{HOST}/visa/checklist-philippines.html", text="Checklist of documents"),
    ]
    scored = {
        candidate.link.url: score
        for candidate, score in ranked_for_role(contention(entries), "document_checklist", limit=10)
    }
    assert (
        scored[f"{HOST}/visa/checklist-philippines.html"] == scored[f"{HOST}/visa/checklist.html"]
    )


def test_a_role_is_ranked_by_its_own_score_not_the_best_overall() -> None:
    """The fixture names an answer per role, so a page that is third overall and first for
    `document_checklist` has to come first here."""

    built = contention(
        [
            entry(f"{HOST}/visa/short-term-stay.html", text="Do I need a visa for Japan"),
            entry(f"{HOST}/visa/documents.html", text="Checklist of documents to submit"),
        ]
    )
    ranked = ranked_for_role(built, "document_checklist", limit=10)
    assert ranked[0][0].link.url == f"{HOST}/visa/documents.html"
    assert all(score > 0 for _, score in ranked)


def test_the_key_names_the_corridor_the_way_the_oracle_does() -> None:
    assert contention([entry(f"{HOST}/visa/x.html", text="visa")]).key == "japan/PH/PH/tourism"


# --- the set the fixture could not see, TODO item 31 -------------------------------------------


def test_a_candidate_no_role_wants_is_kept_so_a_curator_can_still_find_it() -> None:
    """The complement of the test above, and the whole of what makes an oracle able to disagree.

    `oracle/selection_oracle.yaml` was curated "from every candidate that scored above zero", which
    is the same filter `_choose_what_to_read` applies — so checking the pool gate against it
    returned 88 of 88 answering pages inside the pool, a tautology rather than a result (entry 123).
    A fixture cannot detect a filter it shares. The zero-scoring candidates are kept here so a
    curator can read them, and `unpooled_by_text` is how they are ordered.
    """

    built = contention(
        [
            entry(f"{HOST}/visa/short-term-stay.html", text="Visa for temporary visitor"),
            entry(f"{HOST}/about/staff/telephone-directory.html", text="Telephone directory"),
        ]
    )

    assert [c.link.url for c in built.unpooled] == [f"{HOST}/about/staff/telephone-directory.html"]
    assert not {c.link.url for c in built.candidates} & {c.link.url for c in built.unpooled}


def test_the_two_sets_together_are_everything_that_survived_rejection() -> None:
    """Nothing is silently dropped between them: a page is pooled, unpooled, or rejected by a rule
    that `rejected` counts. Without that a curator reading `unpooled` would be reading a set with
    an unrecorded second filter in it, which is the defect this whole item is about."""

    entries = [
        entry(f"{HOST}/visa/short-term-stay.html", text="Visa for temporary visitor"),
        entry(f"{HOST}/about/staff/telephone-directory.html", text="Telephone directory"),
        entry(f"{HOST}/visa/2019/archive-checklist.html", text="Checklist"),
    ]
    built = contention(entries)

    assert len(built.candidates) + len(built.unpooled) + built.rejected == len(entries)


def test_the_unpooled_are_ordered_by_their_text_and_never_by_their_anchor() -> None:
    """`unpooled_by_text` takes the order from `PageTextStore.rank` and keeps it.

    Every member scores zero on the anchor scorer by definition, so that scorer cannot rank them —
    and using it would reproduce the bias the audit exists to detect. A page the index holds no body
    for cannot appear at all, which is the bound the curation view prints.
    """

    from visa_research_agent.discovery.contention import unpooled_by_text
    from visa_research_agent.discovery.page_text import TextMatch

    built = contention(
        [
            entry(f"{HOST}/a/telephone-directory.html", text="Telephone directory"),
            entry(f"{HOST}/b/staff-list.html", text="Staff list"),
            entry(f"{HOST}/visa/short-term-stay.html", text="Visa for temporary visitor"),
        ]
    )
    matches = [
        TextMatch(url=f"{HOST}/b/staff-list.html", score=40.0, bm25=1.0),
        # In the pool, so it must not be reported as something the selector cannot see.
        TextMatch(url=f"{HOST}/visa/short-term-stay.html", score=90.0, bm25=2.0),
        TextMatch(url=f"{HOST}/a/telephone-directory.html", score=10.0, bm25=0.5),
        TextMatch(url=f"{HOST}/never-crawled.html", score=99.0, bm25=9.0),
    ]

    found = unpooled_by_text(built, matches)

    assert [match.url for match, _ in found] == [
        f"{HOST}/b/staff-list.html",
        f"{HOST}/a/telephone-directory.html",
    ]
