"""Generating the committed authority registry, offline and once per country.

Kept apart from `registry.py` so nothing in the request path can import a code path that searches.
Reading the file is what serving a request does; building it is a deliberate command someone runs.

Three properties matter here and none of them matters at request time, which is why this is its own
module:

* **It is resumable.** 198 countries is 792 searches over the better part of an hour, and a quota
  error or a dropped connection two thirds of the way through must not throw away what was already
  paid for. Every country is written as it completes, and an existing file is loaded and extended
  rather than replaced.
* **It is rate limited.** Search is someone else's service and the free tier allows one query a
  second. A generator that ignored that would be refused and would look like a code fault.
* **It records a failure as a failure.** A country whose searches errored is left out of the file
  entirely rather than written with an empty `trusted` list, because those two mean different
  things: "this rule found nothing for Germany" is a finding, and "we never got to ask" is not.
"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from visa_research_agent.discovery.automatic import auto_trusted_domains
from visa_research_agent.discovery.bootstrap import bootstrap_destination
from visa_research_agent.discovery.lexicon import Country, CountryRegistry, Denylist
from visa_research_agent.discovery.registry import (
    AuthorityRegistry,
    CountryAuthorities,
    authorities_from,
)
from visa_research_agent.discovery.search import SearchError, SearchProvider

# One query a second is the free tier's limit, and four queries run per country. Spacing the
# countries rather than the queries keeps `search_all`'s concurrency — which the request path also
# uses — untouched.
DEFAULT_SECONDS_BETWEEN_COUNTRIES = 4.0


@dataclass(frozen=True)
class BuildProgress:
    """What one country's build came to, for a caller that wants to print as it goes."""

    country: Country
    row: CountryAuthorities | None
    error: str | None


async def build_authority_registry(
    countries: CountryRegistry,
    provider: SearchProvider,
    denylist: Denylist,
    *,
    existing: AuthorityRegistry | None = None,
    rebuild: bool = False,
    on_progress: Callable[[BuildProgress], None] | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    seconds_between_countries: float = DEFAULT_SECONDS_BETWEEN_COUNTRIES,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
    write: Callable[[AuthorityRegistry], None] | None = None,
) -> tuple[AuthorityRegistry, dict[str, str]]:
    """Bootstrap every country not already present, returning the registry and what failed.

    Countries already in `existing` are skipped, which is what makes a second run cheap: a build
    interrupted at country 150 resumes at 151 rather than paying for the first 150 again. Delete a
    row to have it rebuilt.
    """

    rows: dict[str, CountryAuthorities] = (
        {row.code: row for row in existing.countries} if existing else {}
    )
    failures: dict[str, str] = {}
    pending = [country for country in countries.countries if country.code not in rows]
    if rebuild:
        # Everything is rebuilt, but `rows` is kept so each country's reviewed domains survive.
        pending = list(countries.countries)

    for index, country in enumerate(pending):
        if index:
            await sleep(seconds_between_countries)
        try:
            report = await bootstrap_destination(
                country.name, provider, denylist, destination_tlds=country.tlds
            )
        except SearchError as exc:
            # Left out of the file rather than written empty. An empty `trusted` means the rule
            # confirmed nothing, which is a result a reviewer must be able to act on; a search that
            # never ran is not that, and writing one as the other would be a false record.
            failures[country.code] = str(exc)
            if on_progress is not None:
                on_progress(BuildProgress(country, None, str(exc)))
            continue

        accepted, _ = auto_trusted_domains(report)
        # Carried through the rebuild. `trusted` and `unconfirmable` are search output and are
        # meant to be replaced; `reviewed` is a person's correction, and regenerating over it would
        # quietly undo every fix in the file — the one way this command could do real damage.
        previous = rows.get(country.code)
        row = authorities_from(
            report, country.code, accepted, reviewed=previous.reviewed if previous else None
        )
        rows[country.code] = row
        if on_progress is not None:
            on_progress(BuildProgress(country, row, None))
        if write is not None:
            # Written as each country lands, so an interruption keeps everything paid for so far.
            write(_assemble(rows, now()))

    return _assemble(rows, now()), failures


def _assemble(rows: dict[str, CountryAuthorities], generated_at: datetime) -> AuthorityRegistry:
    return AuthorityRegistry(
        schema_version=1,
        generated_at=generated_at,
        countries=sorted(rows.values(), key=lambda row: row.code),
    )


HEADER = """\
# Which domains each country's own government may be researched from.
#
# GENERATED, then reviewed by a person, then committed. Regenerate with:
#
#     visa-discover registry --output src/visa_research_agent/config/authority_domains.yaml
#
# It is generated rather than curated, and reviewed rather than trusted: `bootstrap.py` proposes,
# the same `auto_trusted_domains` rule the request path used to run live decides, and a person
# reads the result once. See DECISIONS entry 34 for why this is not the URL-approval gate entry 19
# removed, and entry 33 for what `unconfirmable` is.
#
#   trusted       — confirmed as this country's own government; the only domains ever fetched from.
#                   Empty means the country is refused, which is a real answer and not a bug.
#   reviewed      — added by a person, with the evidence that justified it. This is the escape hatch
#                   entry 33 said the rule would need: a government using no hostname marker cannot
#                   be confirmed by the rule, so its domain is named here instead. These come first
#                   and count against the same cap, so one displaces the weakest machine domain
#                   rather than widening the set. **Preserved when this file is regenerated.**
#   unconfirmable — under the country's own top-level domain, but the hostname carries no marker
#                   this rule recognises as governmental. A real immigration authority may well be
#                   sitting here: 16 of 51 countries measured have theirs here, because no `gov.de`
#                   or `gov.nl` convention exists for one to be found under. Reported so a refusal
#                   can name it. **Never trusted** — that would be "looks official", which is the
#                   one thing the trust rule refuses to do.
#
# Editing `trusted` by hand is a trust decision. Do it deliberately, and say why in DECISIONS.md.
"""


def write_registry(registry: AuthorityRegistry, path: Path) -> None:
    """Write the registry as commented YAML, sorted, so a regeneration diffs cleanly."""

    # Countries are sorted here rather than trusted to the caller: "an unchanged country produces no
    # diff" is what makes a regenerated file reviewable, and it must hold however it was assembled.
    #
    # `trusted` is deliberately **not** sorted. Its order is `_trust_priority`'s — most likely to be
    # a visa authority first — which is what the cap truncates against and what orders the `site:`
    # queries a corridor runs. Alphabetising it here would quietly reorder the searches a corridor
    # makes, and the resolver's determinism rests on candidates being seen in a fixed order.
    payload = {
        "schema_version": registry.schema_version,
        "generated_at": registry.generated_at.isoformat(),
        "countries": [
            {
                "code": row.code,
                "name": row.name,
                "trusted": row.trusted,
                "reviewed": row.reviewed,
                "unconfirmable": row.unconfirmable,
            }
            for row in sorted(registry.countries, key=lambda row: row.code)
        ],
    }
    body = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(HEADER + body, encoding="utf-8")
