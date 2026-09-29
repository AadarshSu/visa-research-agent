"""TODO item 77 (DECISIONS entry 245): should the stored-text score credit the traveller's own post
rather than any mention of their nationality? No network, no model; nothing in `src/` changes.

Every stored page in the 27 captured oracle corridors (`../search-boost-2026-09-29/cap/new`) is
re-scored under each variant of `score_body`; the pool is rebuilt as `_choose_what_to_read` builds
it (text scores decide `admitted_on_text`); today's link + text fusion is cut as `sweep.py` cuts it,
and the oracle roles each cut keeps are counted. The same with entry 244's search boost.

  V0  today's `score_body`, recomputed — must reproduce the captured scores
  V1  the nationality bonus reads the title and the URL's path, never its host (the rule
      `_describes_country` already follows for links: a host names the publishing post)
  V2  V1 + a residence credit on the post-specific roles where the title or path names the
      country the traveller applies from (the link scorer's entry-126 signal, for text)
  V3  V2 + `mission_affinity`: the post serving the traveller +, another post − (the link
      scorer's own adjustment, for text)
  V4  V3 without the purpose bonus on `visa_decision`, which a country table never earns
  SRC `score_body` with `residence` and `other_posts`, as shipped in entry 245 — V4 in `src/`

usage: rescore.py
"""

import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ.setdefault("EMBED_CAPTURES", str(ROOT / "var/search-boost-2026-09-29/cap/new"))
sys.path[:0] = [
    str(ROOT / "var/embed-replay-2026-09-28"),
    str(ROOT / "var/search-boost-2026-09-29"),
]

import boost  # noqa: E402
import common  # noqa: E402

from visa_research_agent.discovery.lexicon import get_country_registry, get_lexicon  # noqa: E402
from visa_research_agent.discovery.models import (  # noqa: E402
    ROLE_ORDER,
    CandidatePage,
    PageLink,
    RoleScores,
)
from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402
from visa_research_agent.discovery.scoring import (  # noqa: E402
    POST_SPECIFIC_ROLES,
    _describes_country,
    foreign_post_labels,
    mission_affinity,
    score_body,
)
from visa_research_agent.discovery.selection import admitted_on_text  # noqa: E402
from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

CUTS = (20, 40, 60, 120)
VARIANTS = tuple(os.environ.get("RESCORE_VARIANTS", "V0,V1,V2,V3,V4,SRC").split(","))
LEXICON = get_lexicon()
COUNTRIES = get_country_registry()


def path_only(url: str) -> str:
    parts = urlsplit(url)
    return parts.path + (f"?{parts.query}" if parts.query else "")


def rescore(variant, url, body, title, corridor, nationality, residence, other_posts) -> RoleScores:
    if variant == "V0":
        return score_body(body, title, corridor, LEXICON, nationality, url=url)
    if variant == "SRC":
        return score_body(
            body,
            title,
            corridor,
            LEXICON,
            nationality,
            url=url,
            residence=residence,
            other_posts=other_posts,
        )
    scored = score_body(body, title, corridor, LEXICON, nationality, url=path_only(url))
    scores, signals = dict(scored.scores), {r: list(s) for r, s in scored.signals.items()}
    if variant in ("V2", "V3", "V4") and residence.code != nationality.code:
        about = PageLink(url=url, text=title[:300], heading="", depth=0, discovered_from="")
        if _describes_country(about, residence):
            for role in POST_SPECIFIC_ROLES:
                if role in scores:
                    scores[role] += LEXICON.residence_weight
                    signals[role].append(f"body-residence:{residence.code}")
    if variant in ("V3", "V4"):
        affinity = mission_affinity(url, residence, LEXICON, other_posts=other_posts)
        if affinity is not None:
            adjustment = (
                LEXICON.mission_host_bonus if affinity == "own" else LEXICON.other_mission_penalty
            )
            for role in POST_SPECIFIC_ROLES:
                if role in scores:
                    scores[role] += adjustment
                    signals[role].append(f"body-{affinity}-post")
    if variant == "V4" and "visa_decision" in scores:
        purpose = f"body-purpose:{corridor.purpose}"
        weight = LEXICON.purposes[corridor.purpose].weight
        if any(s.startswith(purpose) for s in signals["visa_decision"]):
            scores["visa_decision"] -= weight
            signals["visa_decision"].append("no-purpose-on-decision")
    return RoleScores(scores=scores, signals=signals)


def load(name: str, variant: str, texts) -> dict:
    """`common.load`, with the stored-text scores recomputed and the pool rebuilt from them."""

    import json

    data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
    candidates = {
        row["link"]["url"]: CandidatePage.model_validate(row) for row in data["candidates"]
    }
    base = common.load(name)
    corridor = base["corridor"]
    nationality = COUNTRIES.get(corridor.passport_nationality)
    residence = COUNTRIES.get(corridor.applying_from)
    other_posts = foreign_post_labels(COUNTRIES, data["code"], residence)
    scores = {
        url: rescore(variant, url, body, title, corridor, nationality, residence, other_posts)
        for url, (body, title) in texts.items()
    }
    scores = {u: s for u, s in scores.items() if s.scores}
    linked = [c for c in candidates.values() if c.best_combined()[1] > 0]
    admitted = admitted_on_text(
        [c for c in candidates.values() if c.best_combined()[1] <= 0], scores
    )
    pool = linked + admitted
    held = {c.link.url: texts[c.link.url][0] for c in pool if c.link.url in texts}
    return dict(base, pool=pool, held=held, scores=scores, admitted=admitted), data["stored_scores"]


def bodies(code: str, urls) -> dict[str, tuple[str, str]]:
    import sqlite3

    wanted = list(urls)
    out = {}
    connection = sqlite3.connect(common.PAGETEXT / f"{code}.sqlite3")
    for start in range(0, len(wanted), 500):
        part = wanted[start : start + 500]
        rows = connection.execute(
            "SELECT page_text.url, page_text.body, coalesce(pages.title, '') FROM page_text "
            "LEFT JOIN pages ON pages.url = page_text.url "
            f"WHERE page_text.url IN ({','.join('?' * len(part))})",  # noqa: S608
            part,
        ).fetchall()
        out.update({u: (b, t) for u, b, t in rows})
    return out


def main() -> None:
    import json

    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    kept = defaultdict(lambda: defaultdict(int))
    positions = defaultdict(list)
    pool_sizes = defaultdict(list)
    mismatches = 0
    roles = 0
    for name in common.names():
        slug, nat, res = name.rsplit("_", 2)
        row = oracle.get(f"{slug}/{nat}/{res}/tourism")
        if row is None:
            continue
        data = json.loads((common.CAPTURES / f"{name}.json").read_text(encoding="utf-8"))
        texts = bodies(data["code"], {row["link"]["url"] for row in data["candidates"]})
        answers_by_role = {r: row.answering_urls(r) for r in ROLE_ORDER if row.answering_urls(r)}
        roles += len(answers_by_role)
        for variant in VARIANTS:
            cap, captured = load(name, variant, texts)
            if variant == "V0":
                for url, s in cap["scores"].items():
                    was = captured.get(url, {}).get("scores", {})
                    if any(abs(s.score_for(r) - was.get(r, 0.0)) > 1e-6 for r in ROLE_ORDER):
                        mismatches += 1
            pool_sizes[variant].append(len(cap["pool"]))
            answer_texts = dict(cap["held"])
            answer_texts.update(
                PageTextStore(common.PAGETEXT).text_for_selection(
                    cap["code"],
                    {u for a in answers_by_role.values() for u in a} - cap["held"].keys(),
                )
            )
            link, text = common.link_ranking(cap), common.text_ranking(cap)
            orders = {
                "today": common.fused_order(cap, [link, text]),
                "boost": common.fused_order(cap, [link, text, boost.search_ranking(cap)]),
            }
            for arm, order in orders.items():
                for answers in answers_by_role.values():
                    positions[(variant, arm)].append(
                        next(
                            (
                                i
                                for i, c in enumerate(order, 1)
                                if common.credited(answer_texts, {c.link.url}, answers)
                            ),
                            len(order) + 1,
                        )
                    )
                    for cut in CUTS:
                        shown = {c.link.url for c in common.shown(cap, order, cut)}
                        kept[(variant, arm)][cut] += common.credited(answer_texts, shown, answers)
    print(f"V0 recomputation mismatches against the captured scores: {mismatches}")
    print(f"\noracle roles kept, of {roles}, at the top N plus {common.BLIND} blind")
    print(f"{'variant':10}{'arm':8}" + "".join(f"{c:>6}" for c in CUTS) + "  median pos  pool")
    for variant in VARIANTS:
        for arm in ("today", "boost"):
            cells = "".join(f"{kept[(variant, arm)][c]:>6}" for c in CUTS)
            median = statistics.median(positions[(variant, arm)])
            pool = statistics.mean(pool_sizes[variant])
            print(f"{variant:10}{arm:8}{cells}  {median:>10.0f}  {pool:4.0f}")


if __name__ == "__main__":
    main()
