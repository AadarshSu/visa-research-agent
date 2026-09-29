"""Item 75's crawl question: among the links a build recorded and never opened because they scored
nothing, would embeddings pick the ones that hold guidance? Step 1 of 3 — no page is fetched here.

For each country, every unopened entry on a domain trusted now, not a PDF, not rejected by the
build's rules, with no stored text and a link score of zero under the build's own scorer
(`score_link_in_context`). Each one's link text, heading and address are embedded with Voyage and
ranked by the best similarity to the six traveller-neutral role queries. Two samples go to
`samples.json`: the top `SAMPLE` by embedding, and `SAMPLE` drawn at random from the rest — today a
build opens zero-scoring links shallowest first and then in address order, which no more knows what
a page says than a random draw does.

usage: prepare.py AT JP TR      (needs VOYAGE_API_KEY; run from the repository root)
"""

import json
import random
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "var/embed-replay-2026-09-28"))

import common  # noqa: E402
import embed as embedder  # noqa: E402

from visa_research_agent.config.settings import settings  # noqa: E402
from visa_research_agent.discovery.automatic import trusted_domains_for  # noqa: E402
from visa_research_agent.discovery.corpus import FileCorpusStore  # noqa: E402
from visa_research_agent.discovery.corpus_build import _reject  # noqa: E402
from visa_research_agent.discovery.lexicon import get_country_registry, get_lexicon  # noqa: E402
from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.registry import get_authority_registry  # noqa: E402
from visa_research_agent.discovery.scoring import score_link_in_context  # noqa: E402
from visa_research_agent.discovery.urls import is_pdf_url  # noqa: E402

SAMPLE = 100


def link_text(entry) -> str:
    return " | ".join(part for part in (entry.link_text, entry.heading, entry.url) if part)


def query(country_name: str, role: str) -> str:
    return f"{common.ROLE_PHRASES[role]}, for a tourism visit to {country_name}"


def unit(v):
    n = sum(x * x for x in v) ** 0.5 or 1.0
    return [x / n for x in v]


def main(codes: list[str]) -> None:
    lexicon, countries = get_lexicon(), get_country_registry()
    store = FileCorpusStore(settings.corpus_directory)
    out = {}
    for code in codes:
        country = countries.get(code)
        trusted, _ = trusted_domains_for(country, get_authority_registry())
        held = {
            row[0]
            for row in sqlite3.connect(ROOT / f"var/pagetext/{code}.sqlite3").execute(
                "SELECT url FROM pages"
            )
        }
        pool = [
            e
            for e in store.load(code).entries_within(trusted)
            if e.status == "unknown"
            and not is_pdf_url(e.url)
            and e.url not in held
            and _reject(e.to_link(), lexicon) is None
            and score_link_in_context(e.to_link(), lexicon).best()[1] <= 0
        ]
        texts = {e.url: link_text(e) for e in pool}
        queries = {role: query(country.name, role) for role in ROLE_ORDER}
        embedder.run({common.text_hash(t): t for t in queries.values()}, "query", 32)
        embedder.run({common.text_hash(t): t for t in texts.values()}, "document", 128)
        connection = common.connect()
        qv = common.vectors_for(
            connection, [common.text_hash(t) for t in queries.values()], "query"
        )
        dv = common.vectors_for(
            connection, [common.text_hash(t) for t in texts.values()], "document"
        )
        qs = {role: unit(qv[common.text_hash(t)]) for role, t in queries.items()}
        best = {}
        for url, text in texts.items():
            d = unit(dv[common.text_hash(text)])
            sims = {role: sum(a * b for a, b in zip(q, d, strict=True)) for role, q in qs.items()}
            role = max(sims, key=sims.get)
            best[url] = (sims[role], role)
        ranked = sorted(best, key=lambda u: (-best[u][0], u))
        top = ranked[:SAMPLE]
        rest = sorted(set(ranked) - set(top))
        drawn = random.Random(f"crawl-sample/{code}").sample(rest, SAMPLE)
        by_url = {e.url: e for e in pool}

        def row(url, arm, by_url=by_url, best=best, ranked=ranked):
            e = by_url[url]
            return {
                "url": url,
                "arm": arm,
                "similarity": round(best[url][0], 4),
                "nearest_role": best[url][1],
                "rank": ranked.index(url) + 1,
                "link_text": e.link_text,
                "heading": e.heading,
                "depth": e.depth,
                "discovered_from": e.discovered_from,
            }

        out[code] = {
            "country": country.name,
            "slug": country.slug,
            "trusted": trusted,
            "unopened_zero_scoring": len(pool),
            "samples": [row(u, "embedding") for u in top] + [row(u, "random") for u in drawn],
        }
        print(f"{code}: {len(pool)} unopened zero-scoring links; sampled {SAMPLE} + {SAMPLE}")
    (HERE / "samples.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), "utf-8")


if __name__ == "__main__":
    main([c.upper() for c in sys.argv[1:]])
