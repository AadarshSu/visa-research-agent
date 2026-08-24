"""Command line entry points for discovery.

Discovery is a separate command rather than part of a research run. It contacts many pages and its
output changes what the application would treat as official, so it stays a deliberate act with a
person looking at the result.

Exit codes are meaningful, so this can be used in a script:
    0  resolved, every load-bearing role filled
    1  resolved with a non-essential role missing
    2  refused, a load-bearing role could not be filled
    3  configuration error
"""

import argparse
import asyncio
import sys
from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from visa_research_agent.config.loader import (
    config_path,
    get_destination_registry,
    get_runtime_policy,
)
from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.adjudication import (
    LangChainRoleAdjudicator,
    RoleAdjudicator,
)
from visa_research_agent.discovery.audit import (
    CAUSE_LABELS,
    CAUSE_ORDER,
    POSTURE_COST,
    Reachability,
    RecallAudit,
    audit_records,
    counted,
    reachability,
    read_records,
)
from visa_research_agent.discovery.automatic import (
    AutomaticDiscoveryError,
    find_country,
    prepare_destination,
    trusted_domains_for,
)
from visa_research_agent.discovery.bootstrap import (
    BootstrapReport,
    bootstrap_destination,
    entry_point_for,
)
from visa_research_agent.discovery.corpus import CountryCorpus, FileCorpusStore
from visa_research_agent.discovery.corpus_build import (
    DEFAULT_CORPUS_DEPTH,
    DEFAULT_CORPUS_PAGES,
    CorpusBuild,
    build_country_corpus,
)
from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.lexicon import (
    CountryRegistry,
    get_country_registry,
    get_denylist,
)
from visa_research_agent.discovery.models import Corridor, ResolvedCorridor
from visa_research_agent.discovery.proposal import render_corridor_yaml
from visa_research_agent.discovery.recall_log import (
    FileRecallLog,
    RecallRecord,
    VarianceReport,
    compare_runs,
)
from visa_research_agent.discovery.registry import (
    REGISTRY_FILENAME,
    get_authority_registry,
    load_authority_registry,
)
from visa_research_agent.discovery.registry_build import (
    BuildProgress,
    build_authority_registry,
    write_registry,
)
from visa_research_agent.discovery.resolver import CorridorResolver
from visa_research_agent.discovery.search import BraveSearchProvider, SearchError
from visa_research_agent.domain.models import DestinationConfig, RuntimePolicy
from visa_research_agent.research.errors import LLMConfigurationError, VisaResearchError
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.rendering import (
    PageRenderer,
    PlaywrightPageRenderer,
    build_page_renderer,
)
from visa_research_agent.research.source_cache import FileSourceCache


def build_search_provider() -> BraveSearchProvider:
    key = settings.search_api_key.get_secret_value() if settings.search_api_key else ""
    return BraveSearchProvider(key, timeout_seconds=settings.search_timeout_seconds)


def build_role_adjudicator(policy: RuntimePolicy) -> RoleAdjudicator | None:
    """Build the decider the policy asks for, or none when it asks for the heuristic.

    Missing credentials raise rather than silently falling back: `discovery_decider` is a
    committed, reviewed line, so a machine that cannot honour it should say so.
    """

    if policy.discovery_decider == "heuristic":
        return None
    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value().strip():
        raise LLMConfigurationError("OPENAI_API_KEY is required for model role adjudication")
    if settings.openai_model is None or not settings.openai_model.strip():
        raise LLMConfigurationError("OPENAI_MODEL is required for model role adjudication")
    return LangChainRoleAdjudicator(
        api_key=settings.openai_api_key.get_secret_value(),
        model_name=settings.openai_model,
        request_timeout_seconds=settings.openai_request_timeout_seconds,
        max_output_tokens=settings.openai_max_output_tokens,
        reasoning_effort=settings.openai_reasoning_effort,
    )


def build_resolver(
    renderer: PageRenderer | None = None,
    adjudicator: RoleAdjudicator | None = None,
    *,
    corpus: CountryCorpus | None = None,
    pinned: list[str] | None = None,
) -> CorridorResolver:
    # One renderer for both fetchers, so a corridor starts at most one browser and its render
    # budget is shared between finding pages and reading them.
    crawl_fetcher = CrawlFetcher(
        timeout_seconds=settings.source_fetch_timeout_seconds,
        user_agent=settings.source_user_agent,
        host_delay_seconds=settings.discovery_host_delay_seconds,
        renderer=renderer,
        maximum_renders=settings.maximum_crawl_renders,
    )
    live_fetcher = LiveSourceFetcher(
        FileSourceCache(settings.cache_directory),
        ttl_hours=24.0,
        maximum_stale_hours=168.0,
        timeout_seconds=settings.source_fetch_timeout_seconds,
        concurrency=settings.source_fetch_concurrency,
        maximum_characters=settings.maximum_source_characters,
        minimum_characters=settings.minimum_source_characters,
        user_agent=settings.source_user_agent,
        maximum_bytes=settings.maximum_source_bytes,
        renderer=renderer,
        maximum_renders=settings.maximum_source_renders,
    )
    return CorridorResolver(
        build_search_provider(),
        crawl_fetcher,
        live_fetcher,
        adjudicator=adjudicator,
        # On by default in both the command and the API. A recall failure is diagnosable only from
        # the run that had it, and the run that had it is over by the time anyone asks.
        recall_log=FileRecallLog(settings.recall_log_directory),
        corpus=corpus,
        pinned=pinned,
    )


def print_bootstrap(report: BootstrapReport, stream: TextIO) -> None:
    print(f"\nCandidate authority domains for {report.destination_name}\n", file=stream)
    if not report.proposals:
        print("  none survived the checks.", file=stream)
    for proposal in report.proposals:
        if proposal.is_own_government:
            marker = "OWN GOV"
        elif proposal.looks_governmental:
            marker = "gov    "
        else:
            marker = "       "
        print(f"  [{marker}] {proposal.domain}", file=stream)
        print(f"        seen in {proposal.corroboration} queries", file=stream)
        if proposal.looks_governmental and not proposal.belongs_to_destination:
            print(
                f"        WARNING: governmental, but not under {report.destination_name}'s own "
                "domain — this may be another country's advice about this destination",
                file=stream,
            )
        if proposal.suggested_kind:
            print(f"        looks like: {proposal.suggested_kind}", file=stream)
        entry = entry_point_for(proposal)
        if entry:
            print(f"        entry point: {entry}", file=stream)
    if report.rejected:
        print("\n  rejected:", file=stream)
        for domain, reason in sorted(report.rejected.items()):
            print(f"    {domain}: {reason}", file=stream)
    print(
        "\n  Nothing is approved automatically. Add the domains you accept to "
        "trusted_domains in destinations.yaml.\n",
        file=stream,
    )


def print_corridor(resolved: ResolvedCorridor, stream: TextIO) -> None:
    print(f"\nCorridor {resolved.corridor.key}\n", file=stream)
    for source in resolved.sources:
        roles = ", ".join(source.roles)
        print(f"  {roles:<34} {source.score:>6.1f}  {source.url}", file=stream)
        print(f"  {'':<34} {'':>6}  {source.title}", file=stream)
        if source.signals:
            print(f"  {'':<34} {'':>6}  why: {', '.join(source.signals[:4])}", file=stream)
    if resolved.inaccessible_domains:
        print("\n  refused automated retrieval:", file=stream)
        for domain in resolved.inaccessible_domains:
            print(f"    {domain}", file=stream)
        print(
            "    These authorities were not read, so nothing here rests on them. That is not a\n"
            "    judgement about their guidance: it could not be verified from here.",
            file=stream,
        )
    if resolved.interactive_tools:
        print("\n  answered only by an official tool:", file=stream)
        for tool in resolved.interactive_tools:
            print(f"    {tool.role:<22} {tool.url}", file=stream)
        print(
            "    These pages were read. They ask the traveller questions and work the answer out\n"
            "    from them, so nothing here states what they would say.",
            file=stream,
        )
    if resolved.unresolved_roles:
        print("\n  could not be identified:", file=stream)
        for role in resolved.unresolved_roles:
            print(f"    {role}", file=stream)
    for note in resolved.notes:
        print(f"  note: {note}", file=stream)
    print(
        f"\n  {resolved.pages_fetched} pages read, {resolved.model_calls} model calls\n",
        file=stream,
    )


async def run_bootstrap(args: argparse.Namespace, stream: TextIO) -> int:
    # Knowing the destination's own top-level domains is what separates its authorities from
    # another government's pages about it.
    country = next(
        (
            item
            for item in get_country_registry().countries
            if item.name.lower() == args.destination_name.strip().lower()
        ),
        None,
    )
    if country is None:
        print(
            f"{args.destination_name} is not in countries.yaml. Add it so its own domains can be "
            "told apart from other governments' pages about it.",
            file=stream,
        )
        return 3

    report = await bootstrap_destination(
        args.destination_name,
        build_search_provider(),
        get_denylist(),
        destination_tlds=country.tlds,
    )
    print_bootstrap(report, stream)
    return 0 if report.proposals else 2


async def run_registry(args: argparse.Namespace, stream: TextIO) -> int:
    """Generate the committed authority registry — the one command that costs search quota.

    Deliberately not something a request can trigger. Four queries per country times 198 countries
    is most of an hour and a real bill, and the whole point of DECISIONS entry 34 is that this
    happens once and is reviewed, rather than on every cold request for a nationality nobody has
    asked about before.
    """

    destination = Path(args.output)
    existing = None
    if destination.exists():
        # Loaded even when rebuilding: `--rebuild` replaces search output, never a person's
        # reviewed domains, and those live in the same rows.
        existing = load_authority_registry(str(destination))
        if args.rebuild:
            print("rebuilding all countries; reviewed domains kept", file=stream)
        else:
            print(
                f"resuming: {len(existing.countries)} countries already in {destination}",
                file=stream,
            )

    countries = get_country_registry()
    if args.only:
        # A subset is a first-class operation, not a shortcut: after a review finds a country's
        # trusted set wrong, rebuilding that one country must not cost 792 searches. It also lets
        # the file be grown deliberately rather than all at once.
        wanted = {code.strip().upper() for code in args.only.split(",") if code.strip()}
        unknown = wanted - {country.code for country in countries.countries}
        if unknown:
            print(f"not in countries.yaml: {', '.join(sorted(unknown))}", file=stream)
            return 3
        countries = CountryRegistry(
            schema_version=1,
            countries=[c for c in countries.countries if c.code in wanted],
        )

    remaining = len(countries.countries)
    if existing and not args.rebuild:
        remaining -= sum(1 for c in countries.countries if existing.get(c.code))
    print(f"{remaining} countries to build, about {remaining * 4} searches\n", file=stream)

    def report(progress: BuildProgress) -> None:
        if progress.error is not None:
            print(f"  {progress.country.code}  FAILED  {progress.error}", file=stream)
            return
        row = progress.row
        assert row is not None
        trusted = ", ".join(row.trusted) if row.trusted else "(none — refused)"
        print(f"  {row.code}  {trusted}", file=stream)
        if row.unconfirmable:
            print(f"      unconfirmable: {', '.join(row.unconfirmable)}", file=stream)

    registry, failures = await build_authority_registry(
        countries,
        build_search_provider(),
        get_denylist(),
        existing=existing,
        rebuild=args.rebuild,
        on_progress=report,
        write=lambda current: write_registry(current, destination),
    )
    write_registry(registry, destination)

    confirmed = sum(1 for row in registry.countries if row.trusted)
    print(
        f"\n{len(registry.countries)} countries written to {destination}; "
        f"{confirmed} have a confirmed domain, {len(registry.countries) - confirmed} are refused.",
        file=stream,
    )
    if failures:
        # Named rather than counted: these are not in the file at all, so a later run will retry
        # exactly these, and a reader has to be able to tell them from a country that was refused.
        print(f"{len(failures)} could not be searched and were left out:", file=stream)
        for code, reason in sorted(failures.items()):
            print(f"  {code}  {reason}", file=stream)
        return 2
    return 0


def corridor_destination(slug: str, corridor: Corridor, stream: TextIO) -> DestinationConfig | None:
    """Which config a corridor resolves against: the configured one, else the committed registry.

    **Falls back rather than refusing**, which it did not until 2026-08-22. `destinations.yaml`
    holds seven destinations and `authority_domains.yaml` holds forty, so `--destination canada`
    answered *"Unknown destination: canada"* while the API resolved that same corridor perfectly
    well through `AutomaticDestinationService`. Every live check of a registry corridor had
    therefore to be run from a throwaway script — which is why nobody had a candidate list until
    entry 43, and why nobody has yet counted how often a corridor flips (TODO item 17).

    A configured destination still wins where it has domains, because its hand-written sources and
    appointed providers carry authorisations the registry knows nothing about: Singapore's VFS
    provider is named by an official page, and that naming exists only in `destinations.yaml`.

    Deliberately **not** the automatic service, and so deliberately not the corridor store either.
    A stored corridor would answer the second and third runs from the first, which is precisely the
    variance being measured.
    """

    configured = get_destination_registry().get(slug)
    if configured is not None and configured.trusted_domains:
        return configured
    try:
        return prepare_destination(slug, corridor).config
    except AutomaticDiscoveryError as exc:
        print(str(exc), file=stream)
        return None


def print_variance(report: VarianceReport, stream: TextIO) -> None:
    """What several runs of one corridor disagreed about, worst first."""

    print(f"\n{report.runs} runs: {', '.join(report.outcomes)}", file=stream)
    if not report.comparison_is_complete:
        # Said before the numbers, not after: without a record from every run, an absence below
        # means "no record" rather than "this run did not find it", and those read identically.
        print(
            f"  only {report.records_read} of {report.runs} runs left a recall record, so the "
            "candidate comparison below is incomplete.",
            file=stream,
        )
    if not report.flipped:
        print("  every run reached the same outcome.", file=stream)
    else:
        print(
            f"  **the corridor flipped** — {report.resolved_runs} of {report.runs} resolved. "
            "A stored corridor would have kept whichever came first for three weeks.",
            file=stream,
        )
    print(
        f"  {report.stable} candidates seen by every run, {len(report.unstable)} by only some.",
        file=stream,
    )
    changed = [item for item in report.unstable if item.reached_the_model]
    if not report.unstable:
        # Kept apart from the branch below, because the two are different facts and the first
        # printing of this conflated them: with nothing unstable at all it announced "the variance
        # is real but did not reach the decider", which was false of a run where every candidate set
        # was identical. A reason has to be true of what was seen — entries 33 and 36.
        print(
            "  every run saw exactly the same candidate set, so nothing varied at this level.\n"
            "  Note what this does and does not cover: it is search and crawl recall only. The\n"
            "  adjudication is a model call, so identical candidates can still be judged\n"
            "  differently between runs (known problem 10), and that is not measured here.",
            file=stream,
        )
        return
    if not changed:
        print(
            "  none of the varying candidates was ever fetched, so none of them could have\n"
            "  changed the answer. The variance is real but did not reach the decider.",
            file=stream,
        )
        return
    print("\n  varying candidates that at least one run actually read:", file=stream)
    for item in changed:
        seen = ",".join(str(run) for run in item.runs_seen)
        fetched = ",".join(str(run) for run in item.runs_fetched)
        print(f"    {item.best_score:>6.1f}  {item.url}", file=stream)
        print(f"            seen in runs {seen}; read in runs {fetched}", file=stream)


def print_reachability(report: Reachability, stream: TextIO) -> None:
    """How much of the world can be researched, and what stands in the way of the rest."""

    print(
        f"\nReachability, from committed data — {report.countries} countries offered", file=stream
    )
    # Each row names the key its cost is looked up under, rather than the cost itself, so the
    # answer to "is this the price of rigor" has one home and cannot drift between the two halves
    # of this report. `researchable` has no key because it cost nothing — it is the successes.
    rows = (
        ("researchable", len(report.researchable), ""),
        ("row, no confirmable domain", len(report.row_without_domain), "row_without_domain"),
        ("no registry row at all", len(report.no_row), "no_row"),
    )
    for label, count, key in rows:
        cost = POSTURE_COST.get(key, "—")
        share = 100.0 * count / report.countries if report.countries else 0.0
        print(f"  {label:<28} {count:>4}  {share:>5.1f}%  {cost}", file=stream)
    print(
        f"  {report.refused} of {report.countries} are refused before any page is fetched. "
        "None of them leaves a recall log,\n  so they cannot appear in the causes below — which is "
        "why the two halves are counted apart.",
        file=stream,
    )
    if report.unconfirmable_candidates:
        total = sum(report.unconfirmable_candidates.values())
        named = ", ".join(
            f"{code} ({count})" for code, count in report.unconfirmable_candidates.items()
        )
        plural = "domain" if total == 1 else "domains"
        print(
            f"\n  {len(report.unconfirmable_candidates)} of the refused countries had "
            f"{total} candidate {plural} the rule declined: {named}.\n"
            "  Those are the ones with something a reviewer could promote by hand; the rest "
            "found nothing at all.",
            file=stream,
        )


def print_recall_audit(report: RecallAudit, stream: TextIO) -> None:
    """What the runs on disk actually did, bucketed by a cause each of them recorded."""

    print(f"\nOutcomes, over {report.records} recorded runs", file=stream)
    if not report.records:
        print("  no recall logs found. Run a corridor first.", file=stream)
        return
    for cause, count in counted(report.causes, CAUSE_ORDER):
        if cause == "not recorded":
            continue
        label = CAUSE_LABELS.get(cause, cause)
        cost = POSTURE_COST.get(cause, "")
        print(f"  {label:<52} {count:>4}  {cost}", file=stream)
    if report.unrecorded:
        # Said as its own paragraph rather than as a row, because it is not a bucket — it is the
        # absence of bucketing, and a reader skimming a column of counts would read it as one.
        print(
            f"\n  {report.unrecorded} of {report.records} runs predate the cause field and are "
            "not bucketed above.\n  They cannot be repaired by reading their outcome line: a "
            "corridor that refused for want of\n  a visa decision and one that resolved by handing "
            'over the questionnaire stating it both\n  wrote "resolved, with no visa_decision", '
            "and nothing else in the record separates them.\n  Re-run them to fill this in.",
            file=stream,
        )
    if report.unresolved_roles:
        print("\n  roles left unfilled, counted across the same runs:", file=stream)
        for role, count in sorted(report.unresolved_roles.items(), key=lambda i: (-i[1], i[0])):
            print(f"    {role:<50} {count:>4}", file=stream)
    print("\n  pages that could not be read:", file=stream)
    if not report.unreadable:
        print(
            "    none recorded. Note what that does and does not mean: until 2026-08-24 this\n"
            "    field was filled from the crawl alone, and the crawl left the request path\n"
            "    (entry 51), so a run older than that records nothing here however many\n"
            "    authorities refused it.",
            file=stream,
        )
        return
    for outcome, count in sorted(report.unreadable.items(), key=lambda item: (-item[1], item[0])):
        print(f"    {outcome:<50} {count:>4}  {POSTURE_COST.get(outcome, '')}", file=stream)
    for host, count in sorted(report.unreadable_hosts.items(), key=lambda i: (-i[1], i[0]))[:8]:
        print(f"      {host:<48} {count:>4}", file=stream)


def run_audit(args: argparse.Namespace, stream: TextIO) -> int:
    """Both halves of the question, always. Exit code reports whether anything went unanswered.

    The reachability half is printed even when there are no logs, because it is the larger number
    and it needs no runs — a reader who has never run a corridor should still learn that most of
    the world is refused before a page is fetched.
    """

    print_reachability(reachability(get_authority_registry(), get_country_registry()), stream)
    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"\nNo recall logs at {directory}; the outcome half needs runs.", file=stream)
        return 1
    report = audit_records(read_records(directory))
    print_recall_audit(report, stream)
    refused = sum(
        count
        for cause, count in report.causes.items()
        if cause in {"decision_not_found", "no_candidates", "adjudication_failed", "run_raised"}
    )
    return 1 if refused or report.unrecorded else 0


# One cold resolution of a corridor. Named so `run_corridor` can take a fake in tests.
Resolve = Callable[[DestinationConfig, Corridor, RuntimePolicy], Awaitable[ResolvedCorridor]]


def corpus_for(destination: DestinationConfig) -> CountryCorpus | None:
    """The stored page corpus for whatever country this destination is, or none.

    The command did not read one until 2026-08-23, so every measurement taken through it described
    a pipeline the product had already stopped being — no corpus meant no corpus candidates and,
    now, an unconditional crawl. [TODO.md](TODO.md) item 22.

    A corpus that cannot be read **raises**, exactly as it does in the request path: it is the
    candidate source, and treating an unreadable file as "this country has no pages" would turn a
    corrupt corpus into a quietly worse run.
    """

    country = get_country_registry().by_slug(destination.slug)
    if country is None:
        return None
    return FileCorpusStore(settings.corpus_directory).load(country.code)


async def resolve_once(
    destination: DestinationConfig, corridor: Corridor, policy: RuntimePolicy
) -> ResolvedCorridor:
    """One cold resolution, with the browser closed afterwards whatever happened.

    The corpus is passed and the **pins are not**, and the difference is what each one depends on.
    A corpus is corridor-independent, so reading it makes this command behave as the product does.
    Pins come from the stored resolution of *this* corridor, so passing them would let run one
    decide part of run two's shortlist — which is the variance `--runs` exists to measure.
    """

    renderer = build_page_renderer(policy)
    adjudicator = build_role_adjudicator(policy)
    try:
        resolver = build_resolver(renderer, adjudicator, corpus=corpus_for(destination))
        return await resolver.resolve(destination, corridor)
    finally:
        # The browser outlives the resolver, so closing it is this function's job.
        if isinstance(renderer, PlaywrightPageRenderer):
            await renderer.aclose()


async def run_corridor(
    args: argparse.Namespace,
    stream: TextIO,
    *,
    resolve: Resolve = resolve_once,
) -> int:
    """Resolve one corridor, or the same corridor several times to see what varies.

    `resolve` is a seam, in the sense `AGENTS.md` means it — the same role `transport=` and `now=`
    play elsewhere. It exists because this function had none: it built its own resolver from global
    settings and went straight to the network, so a test could only avoid contacting real
    authorities by relying on the command bailing out early for some other reason. One did, and when
    the early exit went away on 2026-08-22 the test suite spent 21 seconds making live Brave
    searches and a live model call. `tests/conftest.py` now blocks the socket as well, so the
    convention and the seam back each other up.
    """

    corridor = Corridor(
        destination_slug=args.destination.strip().lower(),
        passport_nationality=args.nationality.upper(),
        applying_from=getattr(args, "from").upper(),
        purpose=args.purpose,
    )
    destination = corridor_destination(args.destination, corridor, stream)
    if destination is None:
        return 3

    policy = get_runtime_policy()
    runs = max(1, int(getattr(args, "runs", 1)))
    log = FileRecallLog(settings.recall_log_directory)
    records: list[RecallRecord] = []
    outcomes: list[str] = []
    resolved: ResolvedCorridor | None = None

    for attempt in range(1, runs + 1):
        started = datetime.now(UTC)
        resolved = await resolve(destination, corridor, policy)
        if runs == 1:
            continue
        outcomes.append("resolved" if resolved.is_usable else "refused")
        filled = ", ".join(sorted({role for s in resolved.sources for role in s.roles})) or "—"
        print(
            f"  run {attempt}: {outcomes[-1]:<8}  {resolved.pages_fetched:>3} read  "
            f"roles: {filled}",
            file=stream,
        )
        # Read back before the next run overwrites it. The log keeps only the newest run per
        # corridor (entry 43), so comparing runs means holding each record as it is produced.
        #
        # `recorded_at` is checked because the file may predate this command entirely: running two
        # corridors a week apart leaves a week-old record sitting exactly where this looks, and
        # comparing run 2 against last week's run 1 would invent variance that never happened.
        record = log.read(corridor)
        if record is not None and record.recorded_at >= started:
            records.append(record)

    assert resolved is not None
    if runs > 1:
        print_variance(compare_runs(outcomes, records), stream)
    else:
        print_corridor(resolved, stream)

    if args.format == "yaml":
        print(render_corridor_yaml(resolved))

    if not resolved.is_usable:
        return 2
    return 1 if resolved.unresolved_roles else 0


def print_corpus_build(build: CorpusBuild, stream: TextIO) -> None:
    print(
        f"  {build.country_code}  {build.queries} queries, {build.seeds} seeds, "
        f"{build.crawled} crawled  ->  {build.added} new, {build.total} held"
        + (f", {build.unreadable} unreadable" if build.unreadable else ""),
        file=stream,
    )
    depths = ", ".join(f"depth {d}: {n}" for d, n in sorted(build.by_depth.items()))
    print(f"      {depths}", file=stream)
    if not build.depth_is_exercised:
        # The one thing this job exists to do better than the request path. Said out loud, because
        # on 2026-08-22 it silently did not happen: 203 seeds against a 200-page budget meant the
        # whole allowance went on seeds, and nothing in the output showed it.
        print(
            f"      only {build.deep_share:.0%} of what it found lies beyond depth 1 — this crawl "
            "fetched its seeds and stopped, which is the request path's behaviour, not this job's. "
            "Raise --pages well above the seed count.",
            file=stream,
        )


async def run_corpus(args: argparse.Namespace, stream: TextIO) -> int:
    """Build one country's page corpus, offline and deliberately (DECISIONS entry 44).

    Not something a request can trigger, for the same reason `registry` is not: it crawls hundreds
    of pages and spends search quota, and the whole point of the corpus is that this happens on a
    schedule rather than while a traveller waits.
    """

    countries = get_country_registry()
    # By ISO code first, because everything downstream is keyed by one: the authority registry,
    # the corpus filename, the corridor. `find_country` matches slugs, names and synonyms and is
    # what the API uses, so it is left alone rather than widened — a request asking for the
    # destination "in" should not quietly become India.
    wanted = args.country.strip()
    country = countries.get(wanted.upper()) if len(wanted) == 2 else None
    country = country or find_country(wanted, countries)
    if country is None:
        print(
            f"{args.country} is not a country in countries.yaml. Give an ISO code (CA) or a name "
            "(Canada).",
            file=stream,
        )
        return 3
    try:
        trusted, _ = trusted_domains_for(country, get_authority_registry())
    except AutomaticDiscoveryError as exc:
        # The same refusal the API gives, for the same reason: a country whose government cannot be
        # identified has nothing safe to crawl, and guessing here would put unreviewed domains into
        # a store every later corridor reads.
        print(str(exc), file=stream)
        return 3

    store = FileCorpusStore(settings.corpus_directory)
    existing = store.load(country.code)
    print(
        f"building {country.name} from {len(trusted)} domains "
        f"({'existing corpus: ' + str(len(existing.entries)) + ' entries' if existing else 'new'})",
        file=stream,
    )

    policy = get_runtime_policy()
    renderer = build_page_renderer(policy)
    fetcher = CrawlFetcher(
        timeout_seconds=settings.source_fetch_timeout_seconds,
        user_agent=settings.source_user_agent,
        host_delay_seconds=settings.discovery_host_delay_seconds,
        renderer=renderer,
        maximum_renders=settings.maximum_crawl_renders,
    )
    try:
        corpus, build = await build_country_corpus(
            country,
            trusted,
            build_search_provider(),
            fetcher,
            existing=existing,
            now=datetime.now(UTC),
            maximum_pages=args.pages,
            maximum_depth=args.depth,
        )
    finally:
        if isinstance(renderer, PlaywrightPageRenderer):
            await renderer.aclose()

    store.store(corpus)
    print_corpus_build(build, stream)
    # Nothing found is not an error to a script — the corpus is unchanged and still readable — but
    # it is worth an exit code, because a country that crawls to nothing needs a person.
    return 0 if build.total else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visa-discover",
        description="Find official visa sources for a traveller, from official domains only.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    bootstrap = commands.add_parser(
        "bootstrap", help="propose the official domains for a country, for human approval"
    )
    bootstrap.add_argument("--destination-name", required=True, help='e.g. "Brazil"')

    registry = commands.add_parser(
        "registry", help="generate the reviewed authority-domain registry for every country"
    )
    registry.add_argument(
        "--output",
        default=str(config_path(REGISTRY_FILENAME)),
        help="where to write the registry",
    )
    registry.add_argument(
        "--rebuild",
        action="store_true",
        help="rebuild every country instead of resuming; costs the full search quota again",
    )
    registry.add_argument(
        "--only",
        default="",
        help="comma-separated ISO codes to build, e.g. FR,DE,JP; the rest of the file is kept",
    )

    corpus = commands.add_parser(
        "corpus",
        help="crawl one country's official sites and record what pages exist, with no traveller",
    )
    corpus.add_argument("--country", required=True, help="ISO code or name, e.g. CA or Canada")
    corpus.add_argument(
        "--pages",
        type=int,
        default=DEFAULT_CORPUS_PAGES,
        help="how many pages the crawl may read; far above the request path's forty on purpose",
    )
    corpus.add_argument(
        "--depth",
        type=int,
        default=DEFAULT_CORPUS_DEPTH,
        help="how many hops from a seed; the request path affords two, this is not that path",
    )

    audit = commands.add_parser(
        "audit",
        help="count why travellers go unanswered: reachability from data, causes from runs",
    )
    audit.add_argument(
        "directory",
        nargs="?",
        default="var/recall",
        help="a directory of recall logs; the reachability half needs no runs and is always shown",
    )

    corridor = commands.add_parser(
        "corridor", help="find the pages one traveller needs within approved domains"
    )
    corridor.add_argument("--destination", required=True, help="destination slug, e.g. japan")
    corridor.add_argument("--nationality", required=True, help="ISO code, e.g. IN")
    corridor.add_argument("--from", required=True, help="ISO code of where they apply, e.g. GB")
    corridor.add_argument(
        "--purpose", default="tourism", choices=["tourism", "business", "study", "transit"]
    )
    corridor.add_argument("--format", default="table", choices=["table", "yaml"])
    corridor.add_argument(
        "--runs",
        type=int,
        default=1,
        help=(
            "resolve the corridor this many times and report what varied between runs. "
            "Costs the full search and model quota each time; TODO item 17"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "bootstrap":
            return asyncio.run(run_bootstrap(args, sys.stderr))
        if args.command == "registry":
            return asyncio.run(run_registry(args, sys.stderr))
        if args.command == "corpus":
            return asyncio.run(run_corpus(args, sys.stderr))
        if args.command == "audit":
            return run_audit(args, sys.stderr)
        return asyncio.run(run_corridor(args, sys.stderr))
    except SearchError as exc:
        print(f"Search is unavailable: {exc}", file=sys.stderr)
        return 3
    except VisaResearchError as exc:
        print(f"Discovery could not complete: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
