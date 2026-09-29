"""Print passages of a stored page around a pattern: look.py CODE URL PATTERN [width]."""

import re
import sys
from pathlib import Path

sys.path.insert(0, "src")
from visa_research_agent.discovery.page_text import PageTextStore  # noqa: E402

code, url, pattern = sys.argv[1:4]
width = int(sys.argv[4]) if len(sys.argv) > 4 else 250
body = PageTextStore(Path("var/pagetext")).text_for_selection(code, [url]).get(url) or ""
print(f"[{len(body)} chars] {url}")
hits = list(re.finditer(pattern, body, re.IGNORECASE))
print(f"  {len(hits)} matches")
for m in hits[:4]:
    s, e = max(0, m.start() - width), min(len(body), m.end() + width)
    print("  «", " ".join(body[s:e].split()), "»")
