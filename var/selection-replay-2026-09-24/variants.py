"""What the selector is shown. `baseline` is exactly `_choose_what_to_read` today."""

from collections import Counter, defaultdict
from urllib.parse import urlsplit

from visa_research_agent.discovery.models import ROLE_ORDER
from visa_research_agent.discovery.resolver import build_source_id
from visa_research_agent.discovery.selection import (
    DEFAULT_SELECTION_CHARACTERS,
    DEFAULT_SELECTION_SIZE,
    MAXIMUM_EXCERPT_CHARACTERS,
    MINIMUM_EXCERPT_CHARACTERS,
    build_selection_packet,
)


def _ids(cap, pool):
    taken, by_id, text_by_id = set(), {}, {}
    for c in pool:
        sid = build_source_id(cap["slug"], c.link.url, taken)
        by_id[sid] = c
        if c.link.url in cap["held"]:
            text_by_id[sid] = cap["held"][c.link.url]
    return by_id, text_by_id


def shipped(cap, *, pool=None, total=DEFAULT_SELECTION_CHARACTERS, choose=DEFAULT_SELECTION_SIZE):
    pool = cap["pool"] if pool is None else pool
    by_id, text_by_id = _ids(cap, pool)
    packet = build_selection_packet(
        cap["corridor"], by_id, text_by_id, total_characters=total, choose=choose
    )
    return packet, by_id, {"pool": len(pool), "offered": len(by_id), "with_text": len(text_by_id)}


VARIANTS = {
    "baseline": shipped,
}


# --- directions from item 66 --------------------------------------------------------------------


RRF_K = 60


def fusion_order(cap):
    """Entry 183's ranking: per role, reciprocal-rank fusion of link rank and stored-text rank,
    then the roles taken in turn so every role's best come first. A page with no stored text
    still ranks on its link."""

    pool = cap["pool"]
    scores = cap["scores"]
    per_role = {}
    for role in ROLE_ORDER:
        fused = {}
        link = sorted(
            (c for c in pool if c.link_scores.score_for(role) > 0),
            key=lambda c: (-c.link_scores.score_for(role), c.link.url),
        )
        for rank, c in enumerate(link):
            fused[c.link.url] = fused.get(c.link.url, 0) + 1 / (RRF_K + rank + 1)
        text = sorted(
            (c for c in pool if (s := scores.get(c.link.url)) and s.score_for(role) > 0),
            key=lambda c: (-scores[c.link.url].score_for(role), c.link.url),
        )
        for rank, c in enumerate(text):
            fused[c.link.url] = fused.get(c.link.url, 0) + 1 / (RRF_K + rank + 1)
        per_role[role] = sorted(fused, key=lambda u: (-fused[u], u))
    by_url = {c.link.url: c for c in pool}
    order, seen = [], set()
    depth = 0
    while len(seen) < len(pool) and depth < len(pool):
        for role in ROLE_ORDER:
            if depth < len(per_role[role]):
                u = per_role[role][depth]
                if u not in seen:
                    seen.add(u)
                    order.append(by_url[u])
        depth += 1
    order += [c for c in pool if c.link.url not in seen]  # nothing scored for any role: last
    return order


def fusion_top(k):
    def variant(cap):
        order = fusion_order(cap)
        packet, by_id, info = shipped(cap, pool=order[:k])
        info["withheld"] = max(0, len(order) - k)
        return packet, by_id, info

    return variant


def budget(total):
    return lambda cap: shipped(cap, total=total)


def choose(n):
    return lambda cap: shipped(cap, choose=n)


def ranked_excerpts(
    long_n, long_chars=MAXIMUM_EXCERPT_CHARACTERS, total=DEFAULT_SELECTION_CHARACTERS
):
    """Every candidate shown, in fusion order; the first `long_n` get `long_chars`, the rest share
    what is left, never below the minimum. Same total budget as today."""

    def variant(cap):
        order = fusion_order(cap)
        by_id, text_by_id = _ids(cap, order)
        rest = max(1, len(order) - long_n)
        share = max(
            MINIMUM_EXCERPT_CHARACTERS,
            min(MAXIMUM_EXCERPT_CHARACTERS, (total - long_n * long_chars) // rest),
        )
        for i, sid in enumerate(by_id):
            if sid in text_by_id:
                text_by_id[sid] = text_by_id[sid][: long_chars if i < long_n else share]
        packet = build_selection_packet(cap["corridor"], by_id, text_by_id, total_characters=10**9)
        return (
            packet,
            by_id,
            {
                "pool": len(order),
                "offered": len(by_id),
                "with_text": len(text_by_id),
                "short_excerpt": share,
            },
        )

    return variant


def order_only(cap):
    """Fusion order, today's budget: does position alone change anything?"""
    order = fusion_order(cap)
    return shipped(cap, pool=order)


VARIANTS.update(
    {
        "fusion80": fusion_top(80),
        "fusion120": fusion_top(120),
        "fusion160": fusion_top(160),
        "fusion240": fusion_top(240),
        "budget800k": budget(800_000),
        "choose30": choose(30),
        "ranked100": ranked_excerpts(100),
        "order_only": order_only,
    }
)


def strip_chrome(held, share=0.3, floor=3, min_pages=4):
    """Drop the lines a host repeats across its pooled pages — cookie banners, menus, footers —
    keeping each page's first line, its title. Decided from the pool's own texts, per corridor."""

    by_host = defaultdict(list)
    for u, t in held.items():
        by_host[urlsplit(u).netloc].append(t)
    common = {}
    for host, texts in by_host.items():
        if len(texts) < min_pages:
            common[host] = set()
            continue
        c = Counter(line.strip() for t in texts for line in set(t.splitlines()[1:]) if line.strip())
        common[host] = {line for line, n in c.items() if n >= max(floor, share * len(texts))}
    out = {}
    for u, t in held.items():
        lines = t.splitlines()
        repeated = common[urlsplit(u).netloc]
        keep = lines[:1] + [
            line for line in lines[1:] if line.strip() and line.strip() not in repeated
        ]
        out[u] = "\n".join(keep)
    return out


def dechrome(cap):
    cap = dict(cap, held=strip_chrome(cap["held"]))
    return shipped(cap)


VARIANTS["dechrome"] = dechrome


def fusion_top_with_blind(k, blind):
    """Top `k` by fusion, plus the `blind` best candidates with no stored text by their link's own
    best score, added and never displacing — entry 158's route kept open for pages nobody read."""

    def variant(cap):
        order = fusion_order(cap)
        chosen = order[:k]
        seen = {c.link.url for c in chosen}
        no_text = sorted(
            (c for c in order[k:] if c.link.url not in cap["held"]),
            key=lambda c: (-c.link_scores.best()[1], c.link.url),
        )[:blind]
        # Keep fusion order for the whole list so position means the same thing as in fusion_top.
        pool = chosen + [c for c in order[k:] if c in no_text and c.link.url not in seen]
        packet, by_id, info = shipped(cap, pool=pool)
        info["withheld"] = len(order) - len(pool)
        return packet, by_id, info

    return variant


VARIANTS["fusion120_blind40"] = fusion_top_with_blind(120, 40)
