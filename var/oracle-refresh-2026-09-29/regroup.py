"""Regroup review.txt by destination, one entry per (role, page) with the travellers it is a
candidate for, into r_<destination>.txt. Run after candidates.py, from the repository root."""

import re
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
blocks = re.split(r"\n=== ", (HERE / "review.txt").read_text())
by_dest = defaultdict(lambda: defaultdict(OrderedDict))
for block in blocks[1:]:
    head, *rest = block.split("\n")
    name, role = head.split()[:2]
    dest, nat, res = name.rsplit("_", 2)
    current = None
    for line in rest:
        if line.startswith("- "):
            current = line[2:].strip()
            entry = by_dest[dest][role].setdefault(
                current.split("  (= ")[0], {"trav": [], "p": [], "full": current}
            )
            entry["trav"].append(f"{nat}_{res}")
        elif line.startswith("    « ") and current:
            entry = by_dest[dest][role][current.split("  (= ")[0]]
            if len(entry["p"]) < 2 and line not in entry["p"]:
                entry["p"].append(line)
        elif line.startswith("########"):
            current = None
count = 0
for dest, roles in by_dest.items():
    with (HERE / f"r_{dest}.txt").open("w") as f:
        for role, pages in roles.items():
            f.write(f"\n=== {dest} {role} ({len(pages)})\n")
            for entry in pages.values():
                count += 1
                f.write(f"- [{','.join(entry['trav'])}] {entry['full']}\n")
                for passage in entry["p"]:
                    f.write(passage[:560] + "\n")
print(count, "entries")
