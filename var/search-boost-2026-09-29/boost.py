"""Does favouring pages live search found let today's ranking keep its answers in a smaller cut?
No network, no model (DECISIONS entry 243).

Pages search returned for this traveller are 6% of the pool but 36% of the oracle's answers, and
today's link + text fusion lifts them only to 15% of its top 40 (entry 242's follow-up). Arms, each
cut to the top N plus the 40 best-linked pages with no stored text, as `sweep.py` cuts:

- today: link + text, by reciprocal-rank fusion (`fusion_order`);
- +search: the same with a third ranking — per role, the search-found pages by that role's link
  score, then address — fused alongside the other two;
- search always shown: today's top N plus every search-found page it left out (the shortlist grows,
  and the table says by how much);
- link + embeddings: entry 239's arm, for comparison.

A page search and the corpus both returned usually carries the corpus's version and `found_by:
corpus` (the resolver keeps the better link score), so "search-found" undercounts what search saw.

usage: boost.py            (the 21 corridors of the 2026-09-24 capture)
       EMBED_CAPTURES=var/embed-test1-2026-09-29/cap/new boost.py   (entry 241's six)
"""

import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "embed-replay-2026-09-28"))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402
from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

CUTS = (20, 30, 40, 60, 80, 120)


def search_ranking(cap) -> dict[str, list[str]]:
    found = [c for c in cap["pool"] if c.found_by == "search"]
    return {
        role: [
            c.link.url
            for c in sorted(found, key=lambda c, r=role: (-c.link_scores.score_for(r), c.link.url))
        ]
        for role in ROLE_ORDER
    }


def main() -> None:
    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    connection = common.connect()
    kept: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    size: dict[str, dict[int, list[int]]] = defaultdict(lambda: defaultdict(list))
    positions: dict[str, list[int]] = defaultdict(list)
    roles = 0
    for name in common.names():
        slug, nat, res = name.rsplit("_", 2)
        row = oracle.get(f"{slug}/{nat}/{res}/tourism")
        if row is None:
            continue
        cap = common.load(name)
        answers = {u for role in ROLE_ORDER for u in row.answering_urls(role)}
        texts = dict(cap["held"])
        texts.update(
            PageTextStore(common.PAGETEXT).text_for_selection(cap["code"], answers - texts.keys())
        )
        link, text = common.link_ranking(cap), common.text_ranking(cap)
        searched = {c.link.url for c in cap["pool"] if c.found_by == "search"}
        orders = {
            "today (link + text)": common.fused_order(cap, [link, text]),
            "+search as a third ranking": common.fused_order(
                cap, [link, text, search_ranking(cap)]
            ),
        }
        embedded = common.embed_ranking(cap, "neutral", connection)
        if embedded is not None:
            orders["link + embeddings"] = common.fused_order(cap, [link, embedded])
        by_url = {c.link.url: c for c in cap["pool"]}
        for role in ROLE_ORDER:
            answering = row.answering_urls(role)
            if not answering:
                continue
            roles += 1
            for arm, order in orders.items():
                positions[arm].append(
                    next(
                        (
                            i
                            for i, c in enumerate(order, 1)
                            if common.credited(texts, {c.link.url}, answering)
                        ),
                        len(order) + 1,
                    )
                )
            for cut in CUTS:
                shown_by_arm = {
                    arm: [c.link.url for c in common.shown(cap, order, cut)]
                    for arm, order in orders.items()
                }
                today = shown_by_arm["today (link + text)"]
                shown_by_arm["search always shown"] = today + [
                    u for u in sorted(searched) if u not in set(today) and u in by_url
                ]
                for arm, shown in shown_by_arm.items():
                    kept[arm][cut] += common.credited(texts, set(shown), answering)
                    size[arm][cut].append(len(shown))
    print(
        f"oracle roles kept, of {roles}, at the top N plus {common.BLIND} blind "
        "(mean pages shown in brackets)"
    )
    print(f"{'arm':28}" + "".join(f"{cut:>12}" for cut in CUTS))
    for arm in kept:
        cells = "".join(
            f"{kept[arm][cut]:>5} ({statistics.mean(size[arm][cut]):>4.0f})" for cut in CUTS
        )
        print(f"{arm:28}{cells}")
    print("\nbest answer's median position:")
    for arm, values in positions.items():
        print(f"  {arm:28} {statistics.median(values):.0f}")


main()
