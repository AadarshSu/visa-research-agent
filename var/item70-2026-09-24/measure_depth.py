"""TODO item 70, next-work 1: what the depth penalty on corpus entries costs the selector.

For each oracle corridor (and the item-70 corridors with a known answer page), run the real
resolver up to `_choose_what_to_read` with **search stubbed out** — the change touches only
corpus-sourced candidates — and record, in two arms:
  `penalty`: today, a corpus entry scored at the depth its build recorded;
  `flat`:    a corpus entry scored at depth 0.
For each: the pool (scored above zero, plus text admissions), what the selector is shown after the
120 + 40 cut, and which known answer pages are in each. No model call, no network.

usage (repo root): measure_depth.py OUT.json
"""

import asyncio
import json
import sys
from pathlib import Path

from visa_research_agent.config.settings import settings
from visa_research_agent.discovery import cli
from visa_research_agent.discovery.corpus import CorpusEntry, FileCorpusStore, canonical_key
from visa_research_agent.discovery.models import Corridor, PageLink
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.selection import admitted_on_text, shown_to_selector
from visa_research_agent.discovery.selection_recall import load_oracle
from visa_research_agent.discovery.urls import is_pdf_url

ROOT = Path("/Users/aadarsh/Documents/Visa Research Agent")

# Known answer pages for item-70 corridors the oracle does not cover.
EXTRA = {
    "belgium/BD/AE/tourism": {
        "visa_decision": [
            "https://dofi.ibz.be/sites/default/files/2024-12/List%20of%20third%20countries%20that%20are%20required%20to%20hold%20a%20visa.pdf"
        ]
    },
    "slovenia/BD/AE/tourism": {
        "visa_decision": [
            "https://www.gov.si/en/representations/embassy-new-delhi/visa-information",
            "https://www.gov.si/predstavnistva/veleposlanistvo-new-delhi/vizumske-informacije-veleposlanistva-new-delhi",
        ]
    },
    "malta/BD/AE/tourism": {
        "visa_decision": [
            "https://identita.gov.mt/wp-content/uploads/2023/10/List-of-Third-Countries-whose-nationals-must-be-in-possession-of-a-visa-when-crossing-the-external-borders-.pdf"
        ]
    },
}


class NoSearch:
    async def search(self, query, *, count):  # type: ignore[no-untyped-def]
        return []


class Captured(Exception):
    pass


_to_link = CorpusEntry.to_link


def flat_to_link(self: CorpusEntry) -> PageLink:
    return _to_link(self).model_copy(update={"depth": 0})


def pdf_flat_to_link(self: CorpusEntry) -> PageLink:
    link = _to_link(self)
    return link.model_copy(update={"depth": 0}) if is_pdf_url(link.url) else link


ARMS = {"penalty": _to_link, "flat": flat_to_link, "pdf_flat": pdf_flat_to_link}


async def measure(key: str, answers: dict[str, list[str]], arm: str) -> dict:
    slug, nat, res, purpose = (key.split("/") + ["tourism"])[:4]
    corridor = Corridor(
        destination_slug=slug, passport_nationality=nat, applying_from=res, purpose=purpose
    )
    destination = cli.corridor_destination(slug, corridor, sys.stderr)
    country = cli.get_country_registry().by_slug(slug)
    CorpusEntry.to_link = ARMS[arm]  # type: ignore[method-assign]
    resolver = cli.build_resolver(
        None, None, corpus=FileCorpusStore(settings.corpus_directory).load(country.code)
    )
    resolver.provider = NoSearch()
    resolver.recall_log = None
    resolver.usage_log = None
    text = PageTextStore(settings.page_text_directory)
    out: dict = {}

    async def grab(destination, corridor, candidates, stored_scores, notes, trace):  # type: ignore[no-untyped-def]
        admitted = admitted_on_text(
            [c for c in candidates.values() if c.best_combined()[1] <= 0], stored_scores
        )
        pool = [c for c in candidates.values() if c.best_combined()[1] > 0] + admitted
        held = set(text.indexed(country.code, [c.link.url for c in pool]))
        offered, withheld = shown_to_selector(pool, stored_scores, lambda u: u in held)
        keys = lambda cs: {canonical_key(c.link.url) for c in cs}  # noqa: E731
        in_pool, in_offer, in_store = keys(pool), keys(offered), keys(candidates.values())
        found = {}
        for role, urls in answers.items():
            k = {canonical_key(u) for u in urls}
            found[role] = {
                "store": bool(k & in_store),
                "pool": bool(k & in_pool),
                "shown": bool(k & in_offer),
            }
        out.update(
            candidates=len(candidates),
            pool=len(pool),
            shown=len(offered),
            withheld=len(withheld),
            answers=found,
        )
        raise Captured

    resolver._choose_what_to_read = grab  # type: ignore[method-assign]
    try:
        await resolver.resolve(destination, corridor)
    except Captured:
        pass
    CorpusEntry.to_link = _to_link  # type: ignore[method-assign]
    return out


async def main() -> None:
    oracle = load_oracle(ROOT / "oracle/selection_oracle.yaml")
    jobs = {
        row.corridor: {role: [p.url for p in pages] for role, pages in row.answers.items()}
        for row in oracle.corridors
    }
    jobs.update(EXTRA)
    if len(sys.argv) > 3:
        jobs = {k: v for k, v in jobs.items() if any(f in k for f in sys.argv[3].split(","))}
    results = {}
    for key, answers in jobs.items():
        results[key] = {}
        for arm in sys.argv[2].split(",") if len(sys.argv) > 2 else ARMS:
            try:
                results[key][arm] = await measure(key, answers, arm)
            except Exception as exc:  # report and carry on
                results[key][arm] = {"error": f"{type(exc).__name__}: {exc}"[:200]}
        sizes = {a: (r.get("pool"), r.get("shown")) for a, r in results[key].items()}
        print(key, sizes, flush=True)
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1), encoding="utf-8")


asyncio.run(main())
