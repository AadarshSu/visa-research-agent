"""Item 67, entry 236: how many oracle roles each arm keeps at a smaller cut. No network, no model.

`rank.py` grades the shipped cut, 120 plus 40 blind, where today's order already keeps 91 of 92
roles. This asks what a smaller packet would lose: the same arms and crediting, with the top `N`
of the fused order plus the 40 best-linked candidates with no stored text, for several `N`.

usage: sweep.py    (run from the repository root, after embed.py)
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402

from visa_research_agent.discovery.models import ROLE_ORDER  # noqa: E402
from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402
from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: E402

CUTS = (20, 30, 40, 60, 80, 120)


def main() -> None:
    oracle = {row.corridor: row for row in load_oracle(common.ORACLE).corridors}
    connection = common.connect()
    totals: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
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
        arms = {"link+text (today)": [link, text]}
        for mode in common.QUERY_MODES:
            embedded = common.embed_ranking(cap, mode, connection)
            if embedded is None:
                sys.exit(f"no vectors for {name}: run embed.py first")
            arms[f"link+embed [{mode}]"] = [link, embedded]
            arms[f"link+text+embed [{mode}]"] = [link, text, embedded]
        for arm, rankings in arms.items():
            order = common.fused_order(cap, rankings)
            for cut in CUTS:
                common.SHOWN = cut
                shown = {c.link.url for c in common.shown(cap, order)}
                for role in ROLE_ORDER:
                    if row.answering_urls(role):
                        totals[arm][cut] += common.credited(texts, shown, row.answering_urls(role))
        roles += sum(1 for role in ROLE_ORDER if row.answering_urls(role))
    print(f"oracle roles kept, of {roles}, at the top N plus {common.BLIND} blind")
    print(f"{'arm':28}" + "".join(f"{cut:>6}" for cut in CUTS))
    for arm, t in totals.items():
        print(f"{arm:28}" + "".join(f"{t[cut]:>6}" for cut in CUTS))


main()
