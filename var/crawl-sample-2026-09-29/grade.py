"""Step 3 of 3: what the two samples turned out to hold. No network, no model.

`grade.py blind` writes `blind.jsonl`: every sampled page read with text, shuffled, with its arm
hidden, as its title, address and two excerpts — the head, and the 800 characters around the densest
run of visa and entry words in several languages (neither arm chose on the body, so this favours
neither). The judge writes one label per id to `labels.json`:
  G — guidance of one of the six role kinds for someone visiting (visa need, documents, how or where
      to apply, fees, processing time, entry conditions), in any language;
  R — related but not for a visitor (residence, work, study, citizenship, asylum);
  N — not about entering the country.
`grade.py report` joins the labels to the arms and prints the table.
"""

import json
import random
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

WORDS = re.compile(
    r"visa|visum|visa-free|entry|einreise|aufenthalt|reisepass|passport|pasaport|vize|giriş|"
    r"ikamet|査証|ビザ|入国|旅券|在留|consulate|konsulat|konsolosluk|embassy|botschaft|büyükelçilik|"
    r"fee|gebühr|harç|ücret|document|unterlagen|belge|evrak|schengen",
    re.IGNORECASE,
)


def bodies(code: str) -> dict[str, tuple[str, str]]:
    path = HERE / "pagetext" / f"{code}.sqlite3"
    if not path.exists():
        return {}
    db = sqlite3.connect(path)
    titles = dict(db.execute("SELECT url, title FROM pages"))
    return {
        url: (titles.get(url, ""), body)
        for url, body in db.execute("SELECT url, body FROM page_text")
    }


def densest(body: str, width: int = 800) -> str:
    hits = [m.start() for m in WORDS.finditer(body)]
    if not hits:
        return ""
    best, count, j = 0, 0, 0
    for i, start in enumerate(hits):
        while hits[j] < start - width:
            j += 1
        if i - j + 1 > count:
            count, best = i - j + 1, hits[j]
    return body[best : best + width]


def blind() -> None:
    samples = json.loads((HERE / "samples.json").read_text("utf-8"))
    rows = []
    for code in samples:
        held = bodies(code)
        for url in {r["url"] for r in samples[code]["samples"]}:
            if url in held:
                title, body = held[url]
                hits = len(WORDS.findall(body))
                rows.append(
                    {
                        "code": code,
                        "url": url,
                        "title": title,
                        "hits": hits,
                        "head": body[:300],
                        "dense": densest(body, 500),
                    }
                )
    random.Random("blind").shuffle(rows)
    with (HERE / "blind.jsonl").open("w", encoding="utf-8") as out:
        for i, row in enumerate(rows):
            out.write(json.dumps({"id": i, **row}, ensure_ascii=False) + "\n")
    print(f"{len(rows)} pages to judge in blind.jsonl")


def report() -> None:
    samples = json.loads((HERE / "samples.json").read_text("utf-8"))
    fetched = json.loads((HERE / "fetched.json").read_text("utf-8"))
    labels = json.loads((HERE / "labels.json").read_text("utf-8"))
    by_url = {}
    for line in (HERE / "blind.jsonl").read_text("utf-8").splitlines():
        row = json.loads(line)
        by_url[(row["code"], row["url"])] = labels.get(str(row["id"]))
    table = defaultdict(Counter)
    for code, spec in samples.items():
        read = set(fetched.get(code, {}).get("read", []))
        failures = fetched.get(code, {}).get("failures", {})
        for row in spec["samples"]:
            key = (code, row["arm"])
            label = by_url.get((code, row["url"]))
            if label:
                table[key][label] += 1
            elif row["url"] in failures:
                table[key]["failed"] += 1
            elif row["url"] in read:
                table[key]["read, no text"] += 1
            else:
                table[key]["not opened"] += 1
    columns = ["G", "H", "T", "R", "N", "E", "read, no text", "failed", "not opened"]
    print(f"{'country':8} {'arm':10} " + "".join(f"{c:>9}" for c in columns))
    for (code, arm), counts in sorted(table.items()):
        print(f"{code:8} {arm:10} " + "".join(f"{counts[c]:>9}" for c in columns))


if __name__ == "__main__":
    {"blind": blind, "report": report}[sys.argv[1]]()
