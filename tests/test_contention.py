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
