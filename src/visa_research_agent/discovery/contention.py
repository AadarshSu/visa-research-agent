"""Rebuilding a corridor's contention set offline, so an oracle row can be curated without a run.

`oracle/selection_oracle.yaml` is ground truth built by hand: for each corridor, the page that
answers each role, chosen from **every candidate that scored above zero** rather than from what any
selector fetched. Entry 87 built the first ten rows that way, in a throwaway script — which is the
thing item 34 complained about in the first place, one level up. Widening the oracle to a
second traveller needs the same contention set for a corridor nobody has run, so this is that step,
committed and testable.

**It is the resolver's own machinery, not a second implementation.** `score_link` scores the links,
`is_archived` / `is_boilerplate` / `wrong_audience` / `wrong_country` reject them, and
`CandidatePage.best_combined` decides what "in contention" means — all imported, none reimplemented.
Entry 61 is the record of what a reimplementation costs: one disagreed with an observed run, while
binding the real thing reproduced 26 of 26 recorded shortlists.

**The set is corpus-only, and that is a real difference from the first ten rows.** Those were read
out of live runs, whose contention is `corpus ∪ search`. Reconstructed here the sets come out
close — 417/552/87/206/329/132/443/77/172/306 recorded against
365/539/83/201/260/99/452/73/140/270 rebuilt — and `visa-discover coverage` says the corpus holds
the answering page for all 47 curated roles. So corpus-only is a good approximation of the whole
set and it is **not** the same set: a role whose only answer search would have surfaced cannot be
curated from here. That biases a row toward the corpus,
it biases both graded arms equally, and it is recorded in the fixture rather than left to be
rediscovered.

Nothing here fetches, searches or calls a model.
"""

from __future__ import annotations

from dataclasses import dataclass

from visa_research_agent.discovery.corpus import CountryCorpus
from visa_research_agent.discovery.lexicon import CountryRegistry, Lexicon
from visa_research_agent.discovery.models import (
    CandidatePage,
    Corridor,
    DiscoveryRole,
    PageLink,
)
from visa_research_agent.discovery.scoring import (
    foreign_post_labels,
    is_archived,
    is_boilerplate,
    score_link,
    wrong_audience,
    wrong_country,
)
from visa_research_agent.discovery.search import resolve_corridor_countries
from visa_research_agent.domain.models import DestinationConfig


@dataclass(frozen=True)
class Contention:
    """Every candidate a corridor would rank, and how much of it anybody could read.

    `text_held` is the bound on the whole row and the reason the fixture records it: a role can only
    be curated from a page somebody could read, so France sits at 18 of 201 because its portal
    answers a Cloudflare challenge, and an arm that picks the right France page earns no credit for
    it. That is a limit on the metric, not on the arm — known problem 30.
    """

    corridor: Corridor
    candidates: tuple[CandidatePage, ...]
    rejected: int
    """Corpus entries a rule threw out before scoring — archived, boilerplate, wrong audience, wrong
    country. Counted rather than listed because it is large and uninteresting until it is wrong:
    entry 50 found `wrong_country` firing 33 times too often, and only a count made that visible."""

    text_held: int

    @property
    def key(self) -> str:
        corridor = self.corridor
        return (
            f"{corridor.destination_slug}/{corridor.passport_nationality}/"
            f"{corridor.applying_from}/{corridor.purpose}"
        )


def contention_for(
    corpus: CountryCorpus,
    destination: DestinationConfig,
    corridor: Corridor,
    *,
    countries: CountryRegistry,
    lexicon: Lexicon,
    destination_code: str,
    indexed: frozenset[str] = frozenset(),
) -> Contention:
    """The corridor's whole contention set, rebuilt from the store.

    Deliberately takes no fetcher and no search provider. A curator needs the set a *ranking* would
    see, and the one thing that must not happen while building ground truth is a live call whose
    result nobody can reproduce next month.
    """

    nationality, residence = resolve_corridor_countries(corridor, countries)
    # Once per corridor rather than once per link: it walks the whole country registry and depends
    # only on the corridor's two endpoints, which is how the resolver does it too.
    other_posts = foreign_post_labels(countries, destination_code, residence)

    kept: list[CandidatePage] = []
    rejected = 0
    for stored in corpus.entries_within(destination.trusted_domains):
        link: PageLink = stored.to_link()
        if _rejected(link, corridor, lexicon, countries, destination_code):
            rejected += 1
            continue
        candidate = CandidatePage(
            link=link,
            link_scores=score_link(
                link, corridor, lexicon, nationality, residence, other_posts=other_posts
            ),
            title=stored.title or None,
            found_by="corpus",
        )
        if candidate.best_combined()[1] > 0:
            kept.append(candidate)

    kept.sort(key=lambda candidate: (-candidate.best_combined()[1], candidate.link.url))
    return Contention(
        corridor=corridor,
        candidates=tuple(kept),
        rejected=rejected,
        text_held=sum(1 for candidate in kept if candidate.link.url in indexed),
    )


def _rejected(
    link: PageLink,
    corridor: Corridor,
    lexicon: Lexicon,
    countries: CountryRegistry,
    destination_code: str,
) -> bool:
    """The resolver's own `reject`, in the same order. Kept in step with it by importing it."""

    if is_archived(link.url, lexicon) or is_boilerplate(link.url, lexicon):
        return True
    if wrong_audience(link, corridor, lexicon) is not None:
        return True
    return wrong_country(link, corridor, countries, destination_code) is not None


def ranked_for_role(
    contention: Contention, role: DiscoveryRole, *, limit: int = 20
) -> list[tuple[CandidatePage, float]]:
    """The best candidates for one role, which is how a curator works through six roles at a time.

    Ordered by that role's own score rather than by the overall best, because a page can be third
    overall and first for `document_checklist` — and the fixture names an answer per role.
    """

    scored = [
        (candidate, candidate.link_scores.score_for(role))
        for candidate in contention.candidates
        if candidate.link_scores.score_for(role) > 0
    ]
    scored.sort(key=lambda pair: (-pair[1], pair[0].link.url))
    return scored[:limit]
