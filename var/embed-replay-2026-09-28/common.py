"""Shared by embed.py, rank.py and replay_embed.py (TODO item 67, DECISIONS entry 235).

Reads the candidate sets `selection-replay-2026-09-24/capture.py` saved, rebuilds each corridor's
pool exactly as that replay does, and ranks it three ways per role — link, stored text, and
embedding similarity — so arms can be fused and cut like `fusion_order`. Embeddings are ranking
input only: nothing here reaches a packet except through which candidates are shown (entries 78,
83).
"""

import hashlib
import json
import os
import re
import sqlite3
from array import array
from pathlib import Path

from visa_research_agent.discovery.lexicon import get_country_registry
from visa_research_agent.discovery.models import ROLE_ORDER, CandidatePage, Corridor, RoleScores
from visa_research_agent.discovery.page_text import PageTextStore
from visa_research_agent.discovery.selection import FUSION_RANK_CONSTANT, admitted_on_text
from visa_research_agent.discovery.selection_recall import load_oracle, same_pages

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Another capture directory can stand in, as item 75's test 1 does (entry 241).
CAPTURES = Path(
    os.environ.get("EMBED_CAPTURES") or ROOT / "var/selection-replay-2026-09-24/cap/new"
)
PAGETEXT = ROOT / "var/pagetext"
ORACLE = ROOT / "oracle/selection_oracle.yaml"
VECTORS = HERE / "vectors.sqlite"
MIRRORS = load_oracle(ORACLE).mirrors

MODEL = "voyage-4-large"
DIMENSION = 1024
CHUNK_CHARACTERS = 4_000
CHUNK_OVERLAP = 500
SHOWN = 120  # entry 195's cut
BLIND = 40  # plus the best-linked candidates with no stored text

ROLE_PHRASES = {
    "visa_decision": "whether a visa is required, visa exemptions and visa-free entry",
    "document_checklist": "the list of documents required for the visa application: what to "
    "bring and submit",
    "application_route": "how and where to apply for the visa: online, at an embassy, a "
    "consulate or a visa application centre",
    "fees": "visa fees: how much the visa application costs",
    "processing_times": "visa processing times: how long the application takes",
    "general_entry": "entry requirements at the border: passport validity, length of stay and "
    "conditions of entry",
}
QUERY_MODES = ("neutral", "traveller")


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def names() -> list[str]:
    return sorted(path.stem for path in CAPTURES.glob("*.json"))


def country_name(code: str) -> str:
    country = next((c for c in get_country_registry().countries if c.code == code), None)
    return country.name if country else code


def load(name: str) -> dict:
    """One corridor's capture, with the pool built exactly as `replay.load_capture` builds it."""

    data = json.loads((CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
    candidates = {}
    for row in data["candidates"]:
        candidate = CandidatePage.model_validate(row)
        candidates[candidate.link.url] = candidate
    scores = {u: RoleScores.model_validate(s) for u, s in data["stored_scores"].items()}
    admitted = admitted_on_text(
        [c for c in candidates.values() if c.best_combined()[1] <= 0], scores
    )
    pool = [c for c in candidates.values() if c.best_combined()[1] > 0] + admitted
    held = PageTextStore(PAGETEXT).text_for_selection(data["code"], [c.link.url for c in pool])
    return {
        "name": name,
        "code": data["code"],
        "corridor": Corridor.model_validate(data["corridor"]),
        "slug": data["destination_slug"],
        "pool": pool,
        "held": held,
        "scores": scores,
        "admitted": admitted,
    }


def chunks(body: str) -> list[str]:
    step = CHUNK_CHARACTERS - CHUNK_OVERLAP
    return [body[i : i + CHUNK_CHARACTERS] for i in range(0, max(len(body), 1), step)] or [body]


def query_text(corridor: Corridor, role: str, mode: str) -> str:
    destination = country_name_for_slug(corridor.destination_slug)
    text = f"{ROLE_PHRASES[role]}, for a {corridor.purpose} visit to {destination}"
    if mode == "traveller":
        text += (
            f", for a citizen of {country_name(corridor.passport_nationality)} applying from "
            f"{country_name(corridor.applying_from)}"
        )
    return text


def country_name_for_slug(slug: str) -> str:
    country = get_country_registry().by_slug(slug)
    return country.name if country else slug


# --- the vector store ---------------------------------------------------------------------------


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(VECTORS)
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS vectors (
            text_hash TEXT NOT NULL, input_type TEXT NOT NULL, model TEXT NOT NULL,
            vector BLOB NOT NULL, PRIMARY KEY (text_hash, input_type, model)
        );
        """
    )
    return connection


def vectors_for(connection, hashes, input_type) -> dict[str, array]:
    found: dict[str, array] = {}
    wanted = list(dict.fromkeys(hashes))
    for start in range(0, len(wanted), 500):
        part = wanted[start : start + 500]
        rows = connection.execute(
            "SELECT text_hash, vector FROM vectors WHERE input_type = ? AND model = ? "
            f"AND text_hash IN ({','.join('?' * len(part))})",  # noqa: S608
            [input_type, MODEL, *part],
        ).fetchall()
        for text_hash, blob in rows:
            vector = array("f")
            vector.frombytes(blob)
            found[text_hash] = vector
    return found


def cosine(a: array, b: array) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm = (sum(x * x for x in a) * sum(y * y for y in b)) ** 0.5
    return dot / norm if norm else 0.0


# --- rankings and fusion ------------------------------------------------------------------------


def link_ranking(cap) -> dict[str, list[str]]:
    return {
        role: [
            c.link.url
            for c in sorted(
                (c for c in cap["pool"] if c.link_scores.score_for(role) > 0),
                key=lambda c, role=role: (-c.link_scores.score_for(role), c.link.url),
            )
        ]
        for role in ROLE_ORDER
    }


def text_ranking(cap) -> dict[str, list[str]]:
    scores = cap["scores"]
    ranking = {}
    for role in ROLE_ORDER:
        held = [c for c in cap["pool"] if c.link.url in scores]
        held = [c for c in held if scores[c.link.url].score_for(role) > 0]
        held.sort(key=lambda c, role=role: (-scores[c.link.url].score_for(role), c.link.url))
        ranking[role] = [c.link.url for c in held]
    return ranking


def embed_ranking(cap, mode: str, connection) -> dict[str, list[str]] | None:
    """Per role, every pooled page with stored text, by its best chunk's similarity to the role."""

    queries = {role: text_hash(query_text(cap["corridor"], role, mode)) for role in ROLE_ORDER}
    query_vectors = vectors_for(connection, queries.values(), "query")
    page_chunks = {u: [text_hash(t) for t in chunks(body)] for u, body in cap["held"].items()}
    chunk_vectors = vectors_for(
        connection, [h for hs in page_chunks.values() for h in hs], "document"
    )
    if len(query_vectors) < len(queries) or not chunk_vectors:
        return None
    ranking = {}
    for role, query_hash in queries.items():
        q = query_vectors[query_hash]
        best = {
            url: max(cosine(q, chunk_vectors[h]) for h in hashes if h in chunk_vectors)
            for url, hashes in page_chunks.items()
            if any(h in chunk_vectors for h in hashes)
        }
        ranking[role] = sorted(best, key=lambda u: (-best[u], u))
    return ranking


def fused_order(cap, rankings: list[dict[str, list[str]]]) -> list[CandidatePage]:
    """`fusion_order` generalised to any number of rankings: RRF per role, roles taken in turn."""

    per_role = {}
    for role in ROLE_ORDER:
        fused: dict[str, float] = {}
        for ranking in rankings:
            for rank, url in enumerate(ranking[role], start=1):
                fused[url] = fused.get(url, 0.0) + 1 / (FUSION_RANK_CONSTANT + rank)
        per_role[role] = sorted(fused, key=lambda u: (-fused[u], u))
    by_url = {c.link.url: c for c in cap["pool"]}
    order, seen = [], set()
    for depth in range(max((len(v) for v in per_role.values()), default=0)):
        for role in ROLE_ORDER:
            if depth < len(per_role[role]):
                url = per_role[role][depth]
                if url not in seen and url in by_url:
                    seen.add(url)
                    order.append(by_url[url])
    return order + [c for c in cap["pool"] if c.link.url not in seen]


def shown(cap, order, top: int | None = None) -> list[CandidatePage]:
    """Top `top` (default `SHOWN`) plus the `BLIND` best-linked candidates with no stored text, in
    fused order — `fusion_top_with_blind(120, 40)` from the 2026-09-24 replay."""

    top = SHOWN if top is None else top
    chosen = order[:top]
    blind = sorted(
        (c for c in order[top:] if c.link.url not in cap["held"]),
        key=lambda c: (-c.link_scores.best()[1], c.link.url),
    )[:BLIND]
    blind_urls = {c.link.url for c in blind}
    return chosen + [c for c in order[top:] if c.link.url in blind_urls]


# --- crediting an answer, as `selection-recall` does ---------------------------------------------


def credited(texts: dict[str, str | None], picked: set[str], answers: set[str]) -> bool:
    """A pick is an answering page at its own address or another: identical stored text, a
    language switch naming it, or a host the oracle declares a mirror (`same_pages`)."""

    if picked & answers:
        return True
    stored = {u: t for u, t in texts.items() if t}
    groups = same_pages(picked | answers, stored, MIRRORS)
    return any(groups[u] & answers for u in picked)


_ENGLISH = re.compile(r"\b(the|and|of|to|for|you|your|is|are|visa|must|with)\b", re.IGNORECASE)


def is_english(body: str) -> bool:
    words = len(body.split()) or 1
    return len(_ENGLISH.findall(body[:20_000])) / min(words, 20_000 // 6) > 0.06
