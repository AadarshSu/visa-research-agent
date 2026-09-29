"""Apply decisions.yaml to oracle/selection_oracle.yaml by inserting lines, so every existing line,
comment and folded string stays exactly as it was and the diff shows only what the refresh changed.

usage: apply.py [--dry-run]    (from the repository root; validates with load_oracle afterwards)
"""

import sys
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / "oracle/selection_oracle.yaml"
DECISIONS = Path(__file__).resolve().parent / "decisions.yaml"
TRAVELLER = {"IN": "IN/GB", "PH": "PH/PH"}
REFRESH = "Added in the 2026-09-29 refresh (entry 239): "


def folded(key: str, text: str, indent: int) -> list[str]:
    """`key: >-` and the text folded under it, the file's own style: 100 columns."""

    pad = " " * (indent + 2)
    body = textwrap.wrap(" ".join(text.split()), width=100 - len(pad))
    return [f"{' ' * indent}{key}: >-"] + [pad + line for line in body]


class Row:
    """One corridor's lines, edited in place."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    def section(self, name: str) -> tuple[int, int] | None:
        """[start, end) of a 4-space key's block, header included."""

        head = f"    {name}:"
        for i, line in enumerate(self.lines):
            if line == head or line.startswith(head + " "):
                end = i + 1
                while end < len(self.lines) and (
                    self.lines[end].startswith("     ") or not self.lines[end].strip()
                ):
                    end += 1
                while end > i + 1 and not self.lines[end - 1].strip():
                    end -= 1
                return i, end
        return None

    def key_span(self, section: str, key: str) -> tuple[int, int] | None:
        """[start, end) of a 6-space key inside a section."""

        span = self.section(section)
        if span is None:
            return None
        start, end = span
        for i in range(start + 1, end):
            if self.lines[i].startswith(f"      {key}:"):
                j = i + 1
                while j < end and (
                    self.lines[j].startswith("       ") or not self.lines[j].strip()
                ):
                    j += 1
                return i, j
        return None

    def insert_section(self, name: str, after: tuple[str, ...]) -> tuple[int, int]:
        """Create an empty 4-space section after the last of `after` that exists."""

        at = 1
        for other in after:
            span = self.section(other)
            if span is not None:
                at = max(at, span[1])
        self.lines[at:at] = [f"    {name}:"]
        return at, at + 1

    # --- edits ------------------------------------------------------------------------------

    def answer_urls(self, role: str) -> set[str]:
        span = self.key_span("answers", role)
        if span is None:
            return set()
        return {
            line.split("- url:", 1)[1].strip()
            for line in self.lines[span[0] : span[1]]
            if line.strip().startswith("- url:")
        }

    def add_answer(self, role: str, url: str, seen: str, why: str) -> bool:
        if url in self.answer_urls(role):
            return False
        item = [f"        - url: {url}", f"          seen: {seen}"] + folded(
            "why", REFRESH + why, 10
        )
        span = self.key_span("answers", role)
        if span is None:
            answers = self.section("answers") or self.insert_section("answers", ("text_held",))
            self.lines[answers[1] : answers[1]] = [f"      {role}:"] + item
        else:
            self.lines[span[1] : span[1]] = item
        self.drop_list_item("unverifiable", url)
        return True

    def drop_unanswered(self, role: str) -> bool:
        span = self.key_span("unanswered", role)
        if span is None:
            return False
        del self.lines[span[0] : span[1]]
        section = self.section("unanswered")
        if section is not None and section[1] - section[0] == 1:
            del self.lines[section[0]]
        return True

    def drop_list_item(self, section: str, url: str) -> None:
        span = self.section(section)
        if span is None:
            return
        for i in range(span[0] + 1, span[1]):
            if self.lines[i].strip() == f"- {url}":
                del self.lines[i]
                break
        span = self.section(section)
        if span is not None and span[1] - span[0] == 1:
            del self.lines[span[0]]

    def to_tool(self, role: str, url: str, why: str) -> None:
        span = self.key_span("answers", role)
        if span is not None:
            start, end = span
            for i in range(start + 1, end):
                if self.lines[i].strip() == f"- url: {url}":
                    j = i + 1
                    while j < end and not self.lines[j].startswith("        - url:"):
                        j += 1
                    del self.lines[i:j]
                    break
            span = self.key_span("answers", role)
            if span is not None and span[1] - span[0] == 1:
                del self.lines[span[0]]
        tools = self.section("tools") or self.insert_section("tools", ("answers",))
        if self.key_span("tools", role) is None:
            self.lines[tools[1] : tools[1]] = [f"      {role}: {url}"]
        if not self.answer_urls(role):
            unanswered = self.section("unanswered") or self.insert_section(
                "unanswered", ("answers", "tools")
            )
            self.lines[unanswered[1] : unanswered[1]] = folded(role, why, 6)

    def add_excluded(self, url: str, why: str) -> None:
        span = self.section("excluded") or self.insert_section(
            "excluded", ("answers", "tools", "unanswered", "unverifiable", "not_applicable")
        )
        if any(line.strip() == f"- url: {url}" for line in self.lines[span[0] : span[1]]):
            return
        self.lines[span[1] : span[1]] = [f"      - url: {url}"] + folded("why", REFRESH + why, 8)


def split(text: str) -> tuple[list[str], dict[str, tuple[int, int]]]:
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith("  - corridor: ")]
    spans = {}
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        while end > start and (not lines[end - 1].strip() or lines[end - 1].startswith("  #")):
            end -= 1
        spans[lines[start].split("corridor:", 1)[1].strip()] = (start, end)
    return lines, spans


def main() -> None:
    decisions = yaml.safe_load(DECISIONS.read_text())
    lines, spans = split(ORACLE.read_text())
    rows = {key: Row(lines[s:e]) for key, (s, e) in spans.items()}
    counts = {"added": 0, "already": 0, "answered": 0, "tool": 0, "excluded": 0}

    def row_for(dest: str, traveller: str) -> Row:
        return rows[f"{dest}/{TRAVELLER[traveller]}/tourism"]

    for dest, block in decisions.items():
        for item in block.get("add", []):
            where = item.get("dest", dest)
            for traveller in item["for"]:
                done = row_for(where, traveller).add_answer(
                    item["role"], item["url"], item.get("seen", "text"), item["why"]
                )
                counts["added" if done else "already"] += 1
        for item in block.get("correct", []):
            for traveller in item["for"]:
                row = row_for(dest, traveller)
                if item["action"] == "answered":
                    if not row.drop_unanswered(item["role"]):
                        sys.exit(f"{dest} {traveller} {item['role']}: nothing unanswered to drop")
                    counts["answered"] += 1
                elif item["action"] == "to_tool":
                    row.to_tool(item["role"], item["url"], item["why"])
                    counts["tool"] += 1
        for item in block.get("excluded", []):
            for traveller in item["for"]:
                row_for(dest, traveller).add_excluded(item["url"], item["why"])
                counts["excluded"] += 1

    out = []
    cursor = 0
    for key, (start, end) in sorted(spans.items(), key=lambda kv: kv[1][0]):
        out += lines[cursor:start] + rows[key].lines
        cursor = end
    out += lines[cursor:]
    text = "\n".join(out)
    print(counts)
    if "--dry-run" in sys.argv:
        return
    ORACLE.write_text(text)
    sys.path.insert(0, str(ROOT / "src"))
    from visa_research_agent.discovery.selection_recall import load_oracle  # noqa: PLC0415

    oracle = load_oracle(ORACLE)
    print("loads:", len(oracle.corridors), "corridors,", len(oracle.mirrors), "mirror group(s)")


main()
