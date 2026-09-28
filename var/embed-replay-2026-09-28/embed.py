"""Embed every pooled page's stored text, and every role query, with Voyage (TODO item 67).

Only the oracle corridors' pools are embedded — what the measurement reads — not all of
`var/pagetext`. Vectors go to `vectors.sqlite` beside this file, keyed by a hash of the text, so a
re-run embeds only what is missing and an interrupted run resumes.

usage: embed.py [--dry-run] [--only japan_IN_GB,...] [--batch 32]

Needs VOYAGE_API_KEY in the environment or in .env. Run from the repository root.
"""

import argparse
import os
import sys
import time
from array import array
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402

ENDPOINT = "https://api.voyageai.com/v1/embeddings"
MAX_BATCH_CHARACTERS = 200_000  # ~50k tokens, well under a request's token ceiling


def api_key() -> str:
    key = os.environ.get("VOYAGE_API_KEY")
    env = common.ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("VOYAGE_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("'\"")
    if not key:
        sys.exit("VOYAGE_API_KEY is not set (environment or .env)")
    return key


def wanted() -> tuple[dict[str, str], dict[str, str], int]:
    """(document texts by hash, query texts by hash, pages) across every capture."""

    documents, queries, pages = {}, {}, 0
    for name in selected:
        cap = common.load(name)
        pages += len(cap["held"])
        for body in cap["held"].values():
            for piece in common.chunks(body):
                documents[common.text_hash(piece)] = piece
        for role in ROLE_ORDER:
            for mode in common.QUERY_MODES:
                text = common.query_text(cap["corridor"], role, mode)
                queries[common.text_hash(text)] = text
        print(f"{name}: pool {len(cap['pool'])}, with text {len(cap['held'])}", flush=True)
    return documents, queries, pages


def embed(client: httpx.Client, texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    body = {
        "input": texts,
        "model": common.MODEL,
        "input_type": input_type,
        "output_dimension": common.DIMENSION,
    }
    for attempt in range(8):
        response = client.post(ENDPOINT, json=body)
        if response.status_code == 429 or response.status_code >= 500:
            wait = float(response.headers.get("retry-after") or min(60, 2 ** (attempt + 1)))
            print(f"  {response.status_code}; waiting {wait:.0f}s", flush=True)
            time.sleep(wait)
            continue
        if response.status_code != 200:
            sys.exit(f"Voyage answered {response.status_code}: {response.text[:500]}")
        data = response.json()
        ordered = sorted(data["data"], key=lambda row: row["index"])
        return [row["embedding"] for row in ordered], int(data["usage"]["total_tokens"])
    sys.exit("Voyage kept refusing; stopped. Re-run to resume where it left off.")


def run(items: dict[str, str], input_type: str, batch: int) -> int:
    connection = common.connect()
    have = common.vectors_for(connection, items.keys(), input_type)
    todo = [(h, t) for h, t in items.items() if h not in have]
    print(f"{input_type}: {len(items)} texts, {len(have)} already embedded, {len(todo)} to do")
    tokens, done, started = 0, 0, time.monotonic()
    with httpx.Client(headers={"Authorization": f"Bearer {api_key()}"}, timeout=120) as client:
        while todo:
            part, size = [], 0
            while todo and len(part) < batch and size + len(todo[0][1]) <= MAX_BATCH_CHARACTERS:
                size += len(todo[0][1])
                part.append(todo.pop(0))
            if not part:  # one text alone over the character bound
                part.append(todo.pop(0))
            vectors, used = embed(client, [t for _, t in part], input_type)
            connection.executemany(
                "INSERT OR REPLACE INTO vectors VALUES (?, ?, ?, ?)",
                [
                    (h, input_type, common.MODEL, array("f", v).tobytes())
                    for (h, _), v in zip(part, vectors, strict=True)
                ],
            )
            connection.commit()
            tokens += used
            done += len(part)
            rate = tokens / max(time.monotonic() - started, 1e-6) * 60
            print(f"  {done} embedded, {tokens:,} tokens, ~{rate:,.0f} tokens/min", flush=True)
    return tokens


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--only", default="")
    p.add_argument("--batch", type=int, default=32)
    a = p.parse_args()
    selected = [n for n in common.names() if not a.only or n in a.only.split(",")]
    if not selected:
        sys.exit(f"no captures found under {common.CAPTURES}")
    documents, queries, pages = wanted()
    characters = sum(len(t) for t in documents.values())
    print(
        f"\n{len(selected)} corridors, {pages} pages with stored text, {len(documents)} unique "
        f"chunks, {characters:,} characters — roughly {characters // 4:,} to {characters // 3:,} "
        f"tokens — and {len(queries)} role queries. Model {common.MODEL}, {common.DIMENSION} dims."
    )
    if a.dry_run:
        sys.exit(0)
    total = run(queries, "query", a.batch) + run(documents, "document", a.batch)
    print(f"\ndone: {total:,} tokens used this run. Vectors in {common.VECTORS}")
