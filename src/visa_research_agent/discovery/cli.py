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
from collections.abc import Sequence
from typing import TextIO

from visa_research_agent.config.loader import get_destination_registry
from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.bootstrap import (
    BootstrapReport,
    bootstrap_destination,
    entry_point_for,
)
from visa_research_agent.discovery.crawl import CrawlFetcher
from visa_research_agent.discovery.lexicon import get_country_registry, get_denylist
from visa_research_agent.discovery.models import Corridor, ResolvedCorridor
from visa_research_agent.discovery.proposal import render_corridor_yaml
from visa_research_agent.discovery.resolver import CorridorResolver
from visa_research_agent.discovery.search import BraveSearchProvider, SearchError
from visa_research_agent.research.errors import VisaResearchError
from visa_research_agent.research.live_sources import LiveSourceFetcher
from visa_research_agent.research.source_cache import FileSourceCache


def build_search_provider() -> BraveSearchProvider:
    key = settings.search_api_key.get_secret_value() if settings.search_api_key else ""
    return BraveSearchProvider(key, timeout_seconds=settings.search_timeout_seconds)


def build_resolver() -> CorridorResolver:
    crawl_fetcher = CrawlFetcher(
        timeout_seconds=settings.source_fetch_timeout_seconds,
        user_agent=settings.source_user_agent,
        host_delay_seconds=settings.discovery_host_delay_seconds,
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
    )
    return CorridorResolver(build_search_provider(), crawl_fetcher, live_fetcher)


def print_bootstrap(report: BootstrapReport, stream: TextIO) -> None:
    print(f"\nCandidate authority domains for {report.destination_name}\n", file=stream)
    if not report.proposals:
        print("  none survived the checks.", file=stream)
    for proposal in report.proposals:
        if proposal.belongs_to_destination and proposal.looks_governmental:
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


async def run_corridor(args: argparse.Namespace, stream: TextIO) -> int:
    destination = get_destination_registry().get(args.destination)
    if destination is None:
        print(f"Unknown destination: {args.destination}", file=stream)
        return 3
    if not destination.trusted_domains:
        print(
            f"{destination.display_name} has no trusted_domains yet. "
            "Run `bootstrap` first and approve its domains.",
            file=stream,
        )
        return 3

    corridor = Corridor(
        destination_slug=destination.slug,
        passport_nationality=args.nationality.upper(),
        applying_from=getattr(args, "from").upper(),
        purpose=args.purpose,
    )
    resolved = await build_resolver().resolve(destination, corridor)
    print_corridor(resolved, stream)

    if args.format == "yaml":
        print(render_corridor_yaml(resolved))

    if not resolved.is_usable:
        return 2
    return 1 if resolved.unresolved_roles else 0


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "bootstrap":
            return asyncio.run(run_bootstrap(args, sys.stderr))
        return asyncio.run(run_corridor(args, sys.stderr))
    except SearchError as exc:
        print(f"Search is unavailable: {exc}", file=sys.stderr)
        return 3
    except VisaResearchError as exc:
        print(f"Discovery could not complete: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
