"""Entry 207: index one page a build recorded as a 429 into a COPY of Thailand's text store.

usage, from the repository root: .venv/bin/python var/item70-2026-09-24/thailand/fill_copy.py
Copies var/pagetext/TH.sqlite3 to var/item70-2026-09-24/thailand/pagetext/, fetches the ministry's
2026 revision PDF once under our own user agent, and writes its text into the copy only. The real
store is untouched; a corridor is then pointed at the copy with PAGE_TEXT_DIRECTORY.
"""

import shutil
from datetime import UTC, datetime
from pathlib import Path

import httpx

from visa_research_agent.discovery.page_text import PageTextStore, StoredPage
from visa_research_agent.research.live_sources import extract_pdf_text

HERE = Path(__file__).resolve().parent
URL = (
    "https://image.mfa.go.th/mfa/0/wdW3FTtVMc/2026-05-22/"
    "%E0%B8%95%E0%B8%B2%E0%B8%A3%E0%B8%B2%E0%B8%87%E0%B8%97%E0%B8%9A%E0%B8%97%E0%B8%A7"
    "%E0%B8%99%E0%B8%A1%E0%B8%B2%E0%B8%95%E0%B8%A3%E0%B8%81%E0%B8%B2%E0%B8%A3_ver._eng.pdf"
)
TITLE = "Summary: The revision of Thailand’s visa exemption and VoA schemes, 2026"

copy = HERE / "pagetext"
copy.mkdir(exist_ok=True)
shutil.copy2("var/pagetext/TH.sqlite3", copy / "TH.sqlite3")
response = httpx.get(URL, headers={"User-Agent": "VisaResearchAgent/0.1"}, timeout=60)
response.raise_for_status()
body = extract_pdf_text(response.content, maximum_characters=200_000)
print(len(body), "characters;", "India" in body, "India named")
for line in body.splitlines():
    if "India" in line or "30 days" in line.lower():
        print("  ", line[:200])
written = PageTextStore(copy).write(
    "TH", [StoredPage(url=URL, fetched_at=datetime.now(UTC), body=body, title=TITLE)]
)
print("indexed", written)
