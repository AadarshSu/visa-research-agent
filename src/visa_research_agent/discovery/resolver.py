"""Turning a corridor into a set of official sources, or refusing to.

The order is deliberate: search to arrive, crawl to pinpoint, then fetch the shortlist through the
ordinary retrieval path so that discovered pages are subject to exactly the same trust, PDF and
freshness rules as hand-configured ones.

If a load-bearing role cannot be filled confidently the corridor is refused. A plausible substitute
for a document checklist is worse than no answer, because the traveller would be told to bring the
wrong papers with full confidence.
"""

import re
from collections.abc import Callable
from datetime import UTC, datetime
from urllib.parse import urlsplit

from visa_research_agent.discovery.crawl import CrawlFetcher, LinkCrawler
from visa_research_agent.discovery.lexicon import (
    CountryRegistry,
    Lexicon,
    get_country_registry,
    get_lexicon,
)
from visa_research_agent.discovery.models import (
    LOAD_BEARING_ROLES,
    ROLE_ORDER,
    CandidatePage,
    Corridor,
    DiscoveryRole,
    PageLink,
    ResolvedCorridor,
    ResolvedSource,
    RoleScores,
)
from visa_research_agent.discovery.scoring import (
    is_archived,
    rank_for_role,
    score_body,
    score_link,
    wrong_audience,
    wrong_country,
)
from visa_research_agent.discovery.search import (
    SearchProvider,
    corridor_queries,
    resolve_corridor_countries,
    usable_results,
)
from visa_research_agent.discovery.urls import canonicalise_url, is_crawlable
from visa_research_agent.domain.models import (
    ConfiguredSource,
    DestinationConfig,
    SourceKind,
)
from visa_research_agent.domain.trust import host_is_within, host_of
from visa_research_agent.research.live_sources import LiveSourceFetcher

MINIMUM_ROLE_SCORE = 20.0
DEFAULT_SHORTLIST_SIZE = 10


def _slugify(value: str, *, maximum: int = 24) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return cleaned[:maximum].strip("_")


def build_source_id(destination_slug: str, url: str, taken: set[str]) -> str:
    """A stable identifier derived from the URL alone.

    Deriving it from the URL rather than the rank or role means the same page keeps the same id
    between runs, so two proposals can be compared.
    """

    prefix = _slugify(destination_slug, maximum=8) or "dst"
    host = host_of(url)
    host_label = _slugify(host.split(".")[0] if host else "src", maximum=16)
    segments = [segment for segment in urlsplit(url).path.split("/") if segment]
    stem = _slugify(segments[-1].rsplit(".", 1)[0], maximum=24) if segments else "index"
    if not stem or stem.isdigit():
        stem = _slugify(segments[-2], maximum=24) if len(segments) > 1 else "page"

    base = "_".join(part for part in (prefix, host_label, stem) if part)[:48].strip("_")
    if not base or not base[0].isalnum():
        base = f"src_{base}".strip("_")

    candidate = base
    suffix = 2
    while candidate in taken:
        candidate = f"{base[:44]}_{suffix}"
        suffix += 1
    taken.add(candidate)
    return candidate


def derive_authority(url: str, destination: DestinationConfig) -> tuple[str, SourceKind]:
    """Name the authority behind a URL, preferring what a human already wrote down."""

    host = host_of(url)
    for configured in destination.sources:
        if host_of(str(configured.url)) == host:
            return configured.authority, configured.kind
    for configured in destination.sources:
        if host_is_within(host, [host_of(str(configured.url))]):
            return configured.authority, configured.kind

    # An approved domain with no configured page yet: describe it plainly rather than guess.
    lowered = host.lower()
    if "emb" in lowered or "consul" in lowered:
        return f"{destination.display_name} mission ({host})", "embassy_or_high_commission"
    if "immi" in lowered or "ica" in lowered:
        return f"{destination.display_name} immigration authority", "immigration_authority"
    return f"{destination.display_name} authority ({host})", "foreign_ministry"


def clean_title(raw: str | None, fallback: str) -> str:
    """Tidy a page title, dropping the trailing site name authorities append."""

    if not raw or not raw.strip():
        return fallback
    title = " ".join(raw.split())
    for separator in ("|", "—", " - "):
        if separator in title:
            head = title.split(separator)[0].strip()
            if len(head) >= 8:
                title = head
                break
    return title[:90] or fallback


class CorridorResolver:
    """Find the official sources one traveller needs."""

    def __init__(
        self,
        provider: SearchProvider,
        crawl_fetcher: CrawlFetcher,
        live_fetcher: LiveSourceFetcher,
        *,
        lexicon: Lexicon | None = None,
        countries: CountryRegistry | None = None,
        shortlist_size: int = DEFAULT_SHORTLIST_SIZE,
        minimum_role_score: float = MINIMUM_ROLE_SCORE,
        results_per_query: int = 8,
        now: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.provider = provider
        self.crawl_fetcher = crawl_fetcher
        self.live_fetcher = live_fetcher
        self.lexicon = lexicon or get_lexicon()
        self.countries = countries or get_country_registry()
        self.shortlist_size = shortlist_size
        self.minimum_role_score = minimum_role_score
        self.results_per_query = results_per_query
        self.now = now

    async def resolve(self, destination: DestinationConfig, corridor: Corridor) -> ResolvedCorridor:
        nationality, residence = resolve_corridor_countries(corridor, self.countries)
        destination_code = self._destination_code(destination)
        notes: list[str] = []
        mission_domains = self._mission_domains(destination, residence)

        def score(link: PageLink) -> RoleScores:
            return score_link(
                link,
                corridor,
                self.lexicon,
                nationality,
                residence,
                mission_domains=mission_domains,
            )

        def reject(link: PageLink) -> str | None:
            if is_archived(link.url, self.lexicon):
                return "the path marks it as archived or superseded"
            audience = wrong_audience(link, corridor, self.lexicon)
            if audience is not None:
                return f"the page is for {audience} holders, not this traveller"
            other = wrong_country(link, corridor, self.countries, destination_code)
            if other is not None:
                return f"the page is about {other}, which is not part of this corridor"
            return None

        # 1. Search to arrive.
        queries = corridor_queries(corridor, destination, nationality, residence)
        seeds: list[str] = []
        search_candidates: dict[str, CandidatePage] = {}
        for query in queries:
            results = usable_results(
                await self.provider.search(query, count=self.results_per_query), destination
            )
            for result in results:
                url = canonicalise_url(result.url)
                if not is_crawlable(url, destination):
                    continue
                link = PageLink(
                    url=url, text=result.title, heading="", depth=0, discovered_from=query
                )
                if reject(link) is not None:
                    continue
                if url not in search_candidates:
                    search_candidates[url] = CandidatePage(
                        link=link, link_scores=score(link), title=result.title, found_by="search"
                    )
                if url not in seeds:
                    seeds.append(url)

        if not seeds:
            notes.append("search returned nothing on an approved domain for this corridor")

        # 2. Crawl to pinpoint.
        crawler = LinkCrawler(self.crawl_fetcher, score, reject=reject)
        crawled = await crawler.crawl(destination, corridor, seeds)
        page_titles = crawler.titles

        # Name the domains that could not be read at all. Without this a refusal reads as "nothing
        # scored well enough" when the real cause was an unreachable or client-rendered site, which
        # tells the reader to look in a completely different place.
        unreadable: dict[str, str] = {}
        for url, reason in self.crawl_fetcher.failures.items():
            unreadable.setdefault(host_of(url), reason)
        for host, reason in sorted(unreadable.items()):
            notes.append(f"{host} could not be read because {reason}")

        candidates: dict[str, CandidatePage] = dict(search_candidates)
        for candidate in crawled:
            existing = candidates.get(candidate.link.url)
            if existing is None or candidate.link_scores.best()[1] > existing.link_scores.best()[1]:
                candidates[candidate.link.url] = candidate
        for url, candidate in candidates.items():
            if not candidate.title:
                candidate.title = page_titles.get(url) or candidate.link.text or None

        if not candidates:
            return self._refused(corridor, queries, notes, "no candidate pages were found")

        # 3. Fetch the shortlist through the ordinary retrieval path.
        shortlist = self._shortlist(list(candidates.values()))
        fetched = await self._fetch_bodies(destination, shortlist, corridor, nationality)

        # 4. Assign roles from the combined evidence.
        sources, unresolved = self._assign_roles(destination, fetched, notes)
        return ResolvedCorridor(
            corridor=corridor,
            resolved_at=self.now(),
            sources=sources,
            unresolved_roles=unresolved,
            notes=notes,
            queries=queries,
            pages_fetched=len(shortlist),
        )

    def _mission_domains(self, destination: DestinationConfig, residence: object) -> list[str]:
        """Hosts that look like the post serving the traveller's residence.

        Missions sit on a per-country label of the umbrella domain, so a UK applicant is served by
        uk.emb-japan.go.jp. The label rarely matches the ISO code, which is why it comes from data.
        """

        labels = getattr(residence, "host_labels", [])
        found: list[str] = []
        for configured in destination.sources:
            host = host_of(str(configured.url))
            # Drop a leading "www." before reading the country label, or every host looks like
            # "www" and the mission is never recognised.
            bare = host[4:] if host.startswith("www.") else host
            first = bare.split(".")[0]
            if first and any(first == label for label in labels):
                found.append(bare)
        return found

    def _destination_code(self, destination: DestinationConfig) -> str | None:
        country = next(
            (
                country
                for country in self.countries.countries
                if country.name.lower() == destination.display_name.lower()
            ),
            None,
        )
        return country.code if country else None

    def _shortlist(self, candidates: list[CandidatePage]) -> list[CandidatePage]:
        """The best few candidates per role, so only a handful of pages are ever fetched.

        Per-role first, so no role is crowded out by another's strong results, then the budget is
        filled with the next best overall. Filling it matters: taking three per role left four of
        Vietnam's ten places empty while every readable `evisa.gov.vn` page sat just outside the
        per-role cut, so the site that needed rendering most was never read.
        """

        chosen: dict[str, CandidatePage] = {}
        for role in ROLE_ORDER:
            for candidate, _ in rank_for_role(candidates, role)[:3]:
                chosen.setdefault(candidate.link.url, candidate)

        by_score = sorted(candidates, key=lambda c: (-c.link_scores.best()[1], c.link.url))
        for candidate in by_score:
            if len(chosen) >= self.shortlist_size:
                break
            # Only pages that scored for something. A candidate no role wants is not worth a fetch.
            if candidate.link_scores.best()[1] > 0:
                chosen.setdefault(candidate.link.url, candidate)

        ordered = sorted(chosen.values(), key=lambda c: (-c.link_scores.best()[1], c.link.url))
        return ordered[: self.shortlist_size]

    async def _fetch_bodies(
        self,
        destination: DestinationConfig,
        shortlist: list[CandidatePage],
        corridor: Corridor,
        nationality: object,
    ) -> list[CandidatePage]:
        """Read each shortlisted page and score its own text.

        The throwaway config is the point: building it re-runs `validate_route`, so a candidate
        that somehow left the approved domains cannot even be constructed, let alone requested.
        """

        shortlist = [
            candidate
            for candidate in shortlist
            if host_is_within(host_of(candidate.link.url), destination.trusted_domains)
        ]
        if not shortlist:
            return shortlist

        taken: set[str] = set()
        probe_sources: list[ConfiguredSource] = []
        by_id: dict[str, CandidatePage] = {}
        for candidate in shortlist:
            source_id = build_source_id(destination.slug, candidate.link.url, taken)
            authority, kind = derive_authority(candidate.link.url, destination)
            by_id[source_id] = candidate
            probe_sources.append(
                ConfiguredSource.model_validate(
                    {
                        "source_id": source_id,
                        "title": clean_title(candidate.title, candidate.link.url),
                        "url": candidate.link.url,
                        "authority": authority,
                        "kind": kind,
                        "research_pass": "primary",
                    }
                )
            )

        payload = destination.model_dump(mode="json")
        payload["sources"] = [source.model_dump(mode="json") for source in probe_sources]
        payload["application_document_source_ids"] = []
        payload["required_source_ids"] = []
        # An appointed provider is authorised by a named official page. Those pages are not in this
        # throwaway config, so the authorisation does not hold here and the provider is dropped
        # rather than assumed. Candidates were already restricted to trusted domains above.
        payload["appointed_providers"] = []
        probe = DestinationConfig.model_validate(payload)

        report = await self.live_fetcher.fetch(probe)
        for item in report.fetched:
            fetched_candidate = by_id.get(item.source.source_id)
            if fetched_candidate is None:
                continue
            fetched_candidate.body_scores = score_body(
                item.content,
                item.source.title,
                corridor,
                self.lexicon,
                self.countries.require(corridor.passport_nationality),
            )
            fetched_candidate.content_hash = item.content_hash
        # Only pages that were actually readable can be proposed.
        readable = {item.source.source_id for item in report.fetched}
        return [by_id[source_id] for source_id in readable if source_id in by_id]

    def _assign_roles(
        self,
        destination: DestinationConfig,
        candidates: list[CandidatePage],
        notes: list[str],
    ) -> tuple[list[ResolvedSource], list[DiscoveryRole]]:
        """Pick the best page for each role independently.

        Roles are not exclusive. One page can be both the page that says a visa is needed and the
        page listing the documents, which is exactly how Singapore's per-nationality page is
        configured by hand, so forcing one role per page loses the right answer.
        """

        best_by_url: dict[str, tuple[CandidatePage, list[DiscoveryRole], float]] = {}
        unresolved: list[DiscoveryRole] = []

        for role in ROLE_ORDER:
            ranked = [
                (candidate, score)
                for candidate, score in rank_for_role(candidates, role)
                if score >= self.minimum_role_score
            ]
            if not ranked:
                if role in LOAD_BEARING_ROLES:
                    unresolved.append(role)
                    notes.append(f"no page scored high enough to be the {role.replace('_', ' ')}")
                continue

            candidate, score = ranked[0]
            url = candidate.link.url
            if url in best_by_url:
                existing_candidate, roles, best_score = best_by_url[url]
                roles.append(role)
                best_by_url[url] = (existing_candidate, roles, max(best_score, score))
            else:
                best_by_url[url] = (candidate, [role], score)

        taken: set[str] = set()
        sources: list[ResolvedSource] = []
        # Order by the most important role each page fills, so proposals read top-down.
        for candidate, roles, score in sorted(
            best_by_url.values(), key=lambda item: (ROLE_ORDER.index(item[1][0]), item[0].link.url)
        ):
            authority, kind = derive_authority(candidate.link.url, destination)
            signals: list[str] = []
            for role in roles:
                signals.extend(candidate.link_scores.signals.get(role, []))
            sources.append(
                ResolvedSource(
                    source_id=build_source_id(destination.slug, candidate.link.url, taken),
                    title=clean_title(candidate.title, candidate.link.url),
                    url=candidate.link.url,  # type: ignore[arg-type]
                    authority=authority,
                    kind=kind,
                    roles=roles,
                    score=round(score, 1),
                    decided_by="heuristic",
                    signals=list(dict.fromkeys(signals))[:6],
                )
            )
        return sources, unresolved

    def _refused(
        self,
        corridor: Corridor,
        queries: list[str],
        notes: list[str],
        reason: str,
    ) -> ResolvedCorridor:
        return ResolvedCorridor(
            corridor=corridor,
            resolved_at=self.now(),
            sources=[],
            unresolved_roles=list(LOAD_BEARING_ROLES),
            notes=[*notes, reason],
            queries=queries,
        )
