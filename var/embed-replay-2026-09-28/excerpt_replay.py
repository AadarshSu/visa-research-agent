"""Item 67's excerpt experiment (entry 238): does the selector choose better when each page's
excerpt is the part embeddings judge closest to the visa questions, rather than its first 2,000
characters?

Both arms show the same 120 + 40 candidates, built as production builds them — including the
traveller's own-country windows (`anchor_terms`, item 70), which the 2026-09-24 replay predates.
They differ only for a page longer than its excerpt that does not name the traveller past its head:
`excerpt_today` shows its first 2,000 characters, `excerpt_embed` its first 1,000 and then the
1,000-character window whose embedding is closest to any of the six role queries (traveller-neutral,
so it could be built offline). Same characters; only where they are taken from differs. Excerpts are
ranking input: the page is fetched live before a word reaches a plan (entries 78, 83).

usage (from the repository root):
    excerpt_replay.py embed [--dry-run]     embed the windows (Voyage; resumable)
    excerpt_replay.py OUT.jsonl --variants excerpt_today,excerpt_embed --runs 5 --concurrency 1
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPLAY = HERE.parent / "selection-replay-2026-09-24"
sys.path[:0] = [str(HERE), str(REPLAY)]

import common  # noqa: E402
import variants  # noqa: E402

from visa_research_agent.discovery.adjudication import names_traveller_after  # noqa: E402
from visa_research_agent.discovery.lexicon import get_country_registry  # noqa: E402
from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.resolver import (  # noqa: E402
    build_source_id,
    resolve_corridor_countries,
)
from visa_research_agent.discovery.selection import (  # noqa: E402
    DEFAULT_SELECTION_CHARACTERS,
    build_selection_packet,
    excerpt_budget,
)

HEAD = 1_000
WINDOW = 1_000
STRIDE = 500
SHOWN, BLIND = 120, 40


def anchor_terms(corridor) -> list[str]:
    nationality, residence = resolve_corridor_countries(corridor, get_country_registry())
    return sorted({*nationality.text_tokens, *residence.text_tokens})


def shortlist(cap) -> list:
    """`fusion_top_with_blind(120, 40)`, the shipped cut (entry 195)."""

    order = variants.fusion_order(cap)
    chosen = order[:SHOWN]
    seen = {c.link.url for c in chosen}
    no_text = sorted(
        (c for c in order[SHOWN:] if c.link.url not in cap["held"]),
        key=lambda c: (-c.link_scores.best()[1], c.link.url),
    )[:BLIND]
    return chosen + [c for c in order[SHOWN:] if c in no_text and c.link.url not in seen]


def windows(body: str) -> list[tuple[int, str]]:
    """Every candidate window past the head, by its start offset."""

    return [
        (i, body[i : i + WINDOW]) for i in range(HEAD, max(len(body) - WINDOW, HEAD) + 1, STRIDE)
    ]


def changed(cap, pool) -> dict[str, str]:
    """The pages whose excerpt the embedding arm would change: longer than the excerpt, and not
    naming the traveller past its head (those keep production's anchored windows in both arms)."""

    budget = excerpt_budget(len(pool), total=DEFAULT_SELECTION_CHARACTERS)
    terms = anchor_terms(cap["corridor"])
    return {
        c.link.url: cap["held"][c.link.url]
        for c in pool
        if c.link.url in cap["held"]
        and len(cap["held"][c.link.url]) > budget
        and not names_traveller_after(cap["held"][c.link.url], terms, budget)
    }


def embedded_excerpt(body: str, queries, connection) -> str:
    spans = windows(body)
    vectors = common.vectors_for(connection, [common.text_hash(t) for _, t in spans], "document")
    scored = [
        (max(common.cosine(q, vectors[common.text_hash(t)]) for q in queries), -start, t)
        for start, t in spans
        if common.text_hash(t) in vectors
    ]
    if not scored:
        raise SystemExit("windows are not embedded: run `excerpt_replay.py embed` first")
    best = max(scored)[2]
    return f"{body[:HEAD]} … {best}"


def packet_for(cap, embed: bool):
    pool = shortlist(cap)
    taken, by_id, text_by_id = set(), {}, {}
    swap = changed(cap, pool) if embed else {}
    connection = common.connect() if embed else None
    queries = []
    if embed:
        wanted = [
            common.text_hash(common.query_text(cap["corridor"], r, "neutral")) for r in ROLE_ORDER
        ]
        found = common.vectors_for(connection, wanted, "query")
        queries = [found[h] for h in wanted]
    for c in pool:
        source_id = build_source_id(cap["slug"], c.link.url, taken)
        by_id[source_id] = c
        body = cap["held"].get(c.link.url)
        if body:
            text_by_id[source_id] = (
                embedded_excerpt(body, queries, connection) if c.link.url in swap else body
            )
    packet = build_selection_packet(
        cap["corridor"], by_id, text_by_id, anchor_terms=anchor_terms(cap["corridor"])
    )
    info = {"pool": len(pool), "offered": len(by_id), "with_text": len(text_by_id)}
    info["excerpts_changed"] = len(swap)
    return packet, by_id, info


variants.VARIANTS["excerpt_today"] = lambda cap: packet_for(cap, embed=False)
variants.VARIANTS["excerpt_embed"] = lambda cap: packet_for(cap, embed=True)


def embed_windows(dry_run: bool) -> None:
    import embed  # noqa: PLC0415  (Voyage client; only this subcommand needs it)

    documents = {}
    for name in common.names():
        cap = common.load(name)
        for body in changed(cap, shortlist(cap)).values():
            for _, text in windows(body):
                documents[common.text_hash(text)] = text
    characters = sum(len(t) for t in documents.values())
    print(f"{len(documents)} windows, {characters:,} characters (~{characters // 4:,} tokens)")
    if not dry_run:
        used = embed.run(documents, "document", 64)
        print(f"done: {used:,} tokens")


if __name__ == "__main__":
    if sys.argv[1:2] == ["embed"]:
        embed_windows("--dry-run" in sys.argv)
    else:
        sys.argv[0] = str(REPLAY / "replay.py")
        runpy.run_path(str(REPLAY / "replay.py"), run_name="__main__")
