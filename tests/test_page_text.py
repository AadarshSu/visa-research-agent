"""The page-text index: what it keeps, what it refuses to hand back, and what it can now rank.

Every test here is offline. The one that matters is `test_a_page_its_anchor_misfiles_is_ranked_by
_its_text`: it is the whole argument for the module, written as the case that produced it.
"""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from visa_research_agent.discovery.corpus import CorpusEntry
from visa_research_agent.discovery.lexicon import Country, get_country_registry, get_lexicon
from visa_research_agent.discovery.models import CandidatePage, Corridor, PageLink, RoleScores
from visa_research_agent.discovery.page_text import (
    MINIMUM_INDEXABLE_CHARS,
    RETRIEVAL_INTERSTITIAL_MARKER,
    PageTextError,
    PageTextStore,
    StoredPage,
    TextMatch,
    backfill_from_cache,
)
from visa_research_agent.discovery.scoring import score_link
from visa_research_agent.research.source_cache import CachedSource, FileSourceCache

NOW = datetime(2026, 8, 26, 9, 0, tzinfo=UTC)

# Trimmed from the real page, which is what made the case: mofa.go.jp/files/000121327.pdf, the page
# that fills `document_checklist` for japan/IN/GB. The corpus knows it as "Single Entry Visas (PDF)"
# under "Application Procedures for", at a URL of pure digits.
CHECKLIST_BODY = """
Checklist for "Single-Entry Short-Term Stay Visa"
for all nationalities except China, Russia, CIS Countries, Ukraine, Georgia, and the Philippines
Purpose of Visit: Short-Term Business Affairs, Visiting Relatives/Friends, Tourism
Documents to be submitted:
A. Provided by visa applicant: passport, application form, photograph,
   bank statement showing proof of funds, itinerary of stay in Japan.
B. Provided by inviter: letter of invitation, certificate of employment.
"""

CHECKLIST_URL = "https://www.mofa.go.jp/files/000121327.pdf"


def corridor() -> Corridor:
    return Corridor(
        destination_slug="japan",
        passport_nationality="IN",
        applying_from="GB",
        purpose="tourism",
    )


def nationality() -> Country:
    return next(c for c in get_country_registry().countries if c.code == "IN")


def page(url: str, body: str) -> StoredPage:
    return StoredPage(url=url, fetched_at=NOW, body=body)


def test_a_page_its_anchor_misfiles_is_ranked_by_its_text(tmp_path: Path) -> None:
    """The finding this module exists for, as one assertion.

    From its anchor the checklist is not merely ranked low for `document_checklist` — it is filed
    under a **different role entirely**, so no widening of the shortlist could ever recover it. From
    its own text it is the answer. Measured on the live corpus before this was written: 22.0 as
    `visa_decision` from the anchor, 73.5 as `document_checklist` from the body.
    """

    entry = CorpusEntry(
        url=CHECKLIST_URL,
        title="",
        link_text="Single Entry Visas (PDF)",
        heading="Application Procedures for",
        depth=1,
        first_seen=NOW,
        last_seen=NOW,
    )
    lexicon = get_lexicon()
    from_anchor, _ = score_link(
        entry.to_link(),
        corridor(),
        lexicon,
        nationality(),
        nationality(),
    ).best()
    assert from_anchor != "document_checklist"

    store = PageTextStore(tmp_path)
    store.write("JP", [page(CHECKLIST_URL, CHECKLIST_BODY)])
    matches = store.rank(
        "JP",
        role="document_checklist",
        corridor=corridor(),
        nationality=nationality(),
        lexicon=lexicon,
    )
    assert [match.url for match in matches] == [CHECKLIST_URL]


def test_a_match_carries_no_text(tmp_path: Path) -> None:
    """Structural, not a convention.

    Stored text is older than the freshness rules that govern what a traveller may be told, so a
    body reaching a caller is a quote served outside `source_maximum_stale_hours`. There is no
    accessor for one and `TextMatch` has no field to put one in; this fails if either changes.
    """

    store = PageTextStore(tmp_path)
    store.write("JP", [page(CHECKLIST_URL, CHECKLIST_BODY)])
    match = store.rank(
        "JP",
        role="document_checklist",
        corridor=corridor(),
        nationality=nationality(),
        lexicon=get_lexicon(),
    )[0]
    assert "body" not in TextMatch.model_fields
    assert not any(
        CHECKLIST_BODY[:40].strip() in str(value) for value in match.model_dump().values()
    )
    # One method does return bodies — `text_for_selection`, added by entry 83 for a caller whose
    # response type cannot carry prose. It is named for that single use, and this is the assertion
    # that keeps it single: a second body-returning accessor has to change this line and argue for
    # itself, which is exactly what entry 78 wanted the absence of an accessor to force.
    returns_text = {
        name
        for name in dir(store)
        if not name.startswith("_") and name in {"text_for_selection", "snippet", "body_of"}
    }
    assert returns_text == {"text_for_selection"}


def test_a_page_too_short_to_rank_is_not_indexed(tmp_path: Path) -> None:
    store = PageTextStore(tmp_path)
    indexed = store.write("JP", [page("https://www.mofa.go.jp/stub.html", "x" * 10)])
    assert indexed == 0
    assert store.count("JP") == 0


def test_rewriting_a_page_replaces_it_rather_than_duplicating_it(tmp_path: Path) -> None:
    """Unlike the corpus, a newer body of the same URL is simply better and replaces the old one."""

    store = PageTextStore(tmp_path)
    store.write("JP", [page(CHECKLIST_URL, CHECKLIST_BODY)])
    store.write("JP", [page(CHECKLIST_URL, CHECKLIST_BODY + "\nrevised April 2026")])
    assert store.count("JP") == 1


def test_a_country_with_no_index_raises_rather_than_reading_as_empty(tmp_path: Path) -> None:
    """The corpus's rule, for the same reason: "nothing indexed" and "nothing to find" differ."""

    with pytest.raises(PageTextError):
        PageTextStore(tmp_path).count("JP")


def test_backfill_indexes_the_cache_and_skips_hosts_on_no_trusted_domain(tmp_path: Path) -> None:
    """A cached page whose host belongs to no country's authority is skipped, never guessed at."""

    cache_directory = tmp_path / "cache"
    cache = FileSourceCache(cache_directory)
    for url in (CHECKLIST_URL, "https://visa-agency.example.com/japan.html"):
        cache.store(
            CachedSource(
                url=url,
                final_url=url,
                fetched_at=NOW,
                content=CHECKLIST_BODY,
                content_hash="hash",
                http_status=200,
            )
        )
    store = PageTextStore(tmp_path / "pagetext")

    report = backfill_from_cache(
        store,
        cache_directory,
        country_of_host=lambda host: "JP" if host.endswith("mofa.go.jp") else None,
    )

    assert report.indexed == {"JP": 1}
    assert report.skipped_unmapped == 1
    assert store.count("JP") == 1


def test_backfill_counts_pages_too_short_to_rank_separately(tmp_path: Path) -> None:
    """An empty index from an empty cache and one from unusable pages need different fixes."""

    cache_directory = tmp_path / "cache"
    url = "https://www.mofa.go.jp/stub.html"
    FileSourceCache(cache_directory).store(
        CachedSource(
            url=url,
            final_url=url,
            fetched_at=NOW,
            content="x" * (MINIMUM_INDEXABLE_CHARS - 1),
            content_hash="hash",
            http_status=200,
        )
    )

    report = backfill_from_cache(
        PageTextStore(tmp_path / "pagetext"), cache_directory, country_of_host=lambda host: "JP"
    )

    assert report.indexed == {}
    assert report.skipped_short == 1


def test_stored_text_lifts_a_candidate_and_never_sinks_one() -> None:
    """The asymmetry that makes `text_scores` a second field rather than an early `body_scores`.

    A fetched body scoring zero for a role is a fact about the page. Stored text scoring zero can
    equally be a stale row or a bad PDF extraction — and if that could lower a candidate, *holding*
    a page's text would cost it its shortlist place. Entry 40: a page ranked out is never fetched.
    """

    link = PageLink(
        url="https://x.gov.example/a", text="", heading="", depth=1, discovered_from="s"
    )
    strong_link = RoleScores(scores={"document_checklist": 60.0})

    silent_text = CandidatePage(
        link=link, link_scores=strong_link, text_scores=RoleScores(scores={})
    )
    assert silent_text.combined("document_checklist") == 60.0

    helpful_text = CandidatePage(
        link=link,
        link_scores=RoleScores(scores={"document_checklist": 10.0}),
        text_scores=RoleScores(scores={"document_checklist": 70.0}),
    )
    assert helpful_text.combined("document_checklist") > 10.0

    # A body this run fetched is trusted in both directions, and takes precedence over stored text.
    fetched = CandidatePage(
        link=link,
        link_scores=strong_link,
        text_scores=RoleScores(scores={"document_checklist": 90.0}),
        body_scores=RoleScores(scores={}),
    )
    assert fetched.combined("document_checklist") == pytest.approx(24.0)


def test_score_held_scores_only_the_pages_the_index_holds(tmp_path: Path) -> None:
    store = PageTextStore(tmp_path)
    store.write("JP", [page(CHECKLIST_URL, CHECKLIST_BODY)])

    scored = store.score_held(
        "JP",
        [CHECKLIST_URL, "https://www.mofa.go.jp/never-indexed.html"],
        corridor=corridor(),
        nationality=nationality(),
        lexicon=get_lexicon(),
    )

    assert list(scored) == [CHECKLIST_URL]
    assert scored[CHECKLIST_URL].score_for("document_checklist") > 0


def test_score_held_is_silent_for_a_country_with_no_index(tmp_path: Path) -> None:
    """Asked mid-corridor, not about the index — so no index means what it meant before there
    were any: rank on the link alone. `count` and `rank` raise instead, being asked a different
    question."""

    assert (
        PageTextStore(tmp_path).score_held(
            "JP",
            [CHECKLIST_URL],
            corridor=corridor(),
            nationality=nationality(),
            lexicon=get_lexicon(),
        )
        == {}
    )


INTERSTITIAL = (
    "Just a moment... www.example.gov Performing security verification "
    "This website uses a security service to protect against malicious bots. "
    "This page is displayed while the website verifies you are not a bot. " * 3
)
GUIDANCE_TEXT = (
    "Nigerian passport holders require a short-stay visa for tourism. "
    "Bring a passport valid for three months beyond departure. " * 8
)


def test_a_stored_bot_check_page_is_purged_and_real_guidance_is_not(tmp_path: Path) -> None:
    """Entry 117's repair. The detector fix stops new ones; this removes what is already stored.

    414 rows across nine countries were Cloudflare's interstitial saved as the authority's page —
    Lithuania's visa page and `egov.uscis.gov/processing-times` among them. `write` replaces only a
    URL it re-reads, and a page now correctly recorded `challenged` is never written, so those rows
    do not heal on a rebuild.
    """

    store = PageTextStore(tmp_path)
    now = datetime(2026, 8, 30, 9, 0, tzinfo=UTC)
    store.write(
        "XX",
        [
            StoredPage(url="https://gov.example/visa", fetched_at=now, body=INTERSTITIAL),
            StoredPage(url="https://gov.example/fees", fetched_at=now, body=GUIDANCE_TEXT),
        ],
    )
    assert store.count("XX") == 2

    removed = store.purge_retrieval_interstitials("XX")

    assert removed == 1
    assert store.count("XX") == 1, "the guidance page must survive"


def test_purging_is_matched_on_the_whole_sentence_not_a_loose_phrase(tmp_path: Path) -> None:
    """The narrowness is the safeguard, because this deletes data.

    "Just a moment" and "attention required" are phrases a real guidance page can contain, and
    measuring all 53 indexes showed no row needed them: every one of the 414 carried Cloudflare's
    full sentence. So a page that merely says "just a moment" keeps its text.
    """

    store = PageTextStore(tmp_path)
    now = datetime(2026, 8, 30, 9, 0, tzinfo=UTC)
    innocent = (
        "Attention required: just a moment of your time. Checking your browser settings is not "
        "necessary to apply for this visa. " * 6
    )
    store.write("XX", [StoredPage(url="https://gov.example/notice", fetched_at=now, body=innocent)])

    assert RETRIEVAL_INTERSTITIAL_MARKER not in innocent.lower()
    assert store.purge_retrieval_interstitials("XX") == 0
    assert store.count("XX") == 1
