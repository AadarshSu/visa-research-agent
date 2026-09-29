"""Step 2 of 3: open both samples exactly as a corpus build opens a page, into a scratch store.

The build's own `LinkCrawler` and `CrawlFetcher`, with every sampled address as a seed and
`maximum_depth=0`, so each page is opened and read and none of its links is followed. Trust
(`is_crawlable` on the seed and after every redirect), `robots.txt`, TLS, the challenge rules, the
per-host delay and the renderer are the build's, unchanged. Nothing is written to `var/corpus` or
`var/pagetext`: the text goes to `pagetext/` beside this file, and each address's outcome to
`fetched.json`.

usage: fetch.py [AT JP TR]   (from the owner's Terminal panel: the renderer needs Chromium)
"""

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from visa_research_agent.config.loader import get_runtime_policy
from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.corpus_build import storable_text
from visa_research_agent.discovery.crawl import CrawlFetcher, LinkCrawler
from visa_research_agent.discovery.models import DestinationConfig, RoleScores
from visa_research_agent.discovery.page_text import PageTextStore, StoredPage
from visa_research_agent.research.rendering import PlaywrightPageRenderer, build_page_renderer

HERE = Path(__file__).resolve().parent


async def fetch(code: str, spec: dict, skip: set[str]) -> dict:
    destination = DestinationConfig(
        slug=spec["slug"],
        display_name=spec["country"],
        route_type="national",
        implementation_status="available",
        trusted_domains=spec["trusted"],
    )
    urls = [u for u in dict.fromkeys(row["url"] for row in spec["samples"]) if u not in skip]
    renderer = build_page_renderer(get_runtime_policy())
    fetcher = CrawlFetcher(
        timeout_seconds=settings.source_fetch_timeout_seconds,
        user_agent=settings.source_user_agent,
        host_delay_seconds=settings.discovery_host_delay_seconds,
        renderer=renderer,
        maximum_renders=40,
    )
    now = datetime.now(UTC)
    kept: list[StoredPage] = []

    def keep(url: str, title: str, text: str) -> None:
        body = storable_text(text)
        if body:
            kept.append(StoredPage(url=url, fetched_at=now, body=body, title=storable_text(title)))

    crawler = LinkCrawler(
        fetcher,
        lambda _link: RoleScores(),
        maximum_depth=0,
        # Every sampled address is a seed and none is expanded, so the page allowance is the
        # sample itself. It is set far above it because `_budget_for` splits it evenly between
        # hosts, and the embedding sample sits on few hosts: at `len(urls)` most of it was dropped.
        maximum_pages=100_000,
        maximum_pages_per_host=len(urls),
        on_page=keep,
    )
    try:
        await crawler.crawl(destination, urls)
    finally:
        if isinstance(renderer, PlaywrightPageRenderer):
            await renderer.aclose()
    PageTextStore(HERE / "pagetext").write(code, kept)
    failures = {url: str(reason) for url, reason in fetcher.failures.items()}
    read = crawler.read
    print(
        f"{code}: {len(read)} of {len(urls)} asked for read, {len(kept)} with text, "
        f"{len(failures)} failed"
    )
    return {"read": sorted(read), "failures": failures, "fetched_at": now.isoformat()}


async def main(codes: list[str]) -> None:
    samples = json.loads((HERE / "samples.json").read_text("utf-8"))
    path = HERE / "fetched.json"
    done = json.loads(path.read_text("utf-8")) if path.exists() else {}
    for code in codes or list(samples):
        before = done.get(code, {"read": [], "failures": {}})
        # Only what no run has asked for yet: a page is never requested twice.
        skip = set(before["read"]) | set(before["failures"])
        result = await fetch(code, samples[code], skip)
        done[code] = {
            "read": sorted(set(before["read"]) | set(result["read"])),
            "failures": before["failures"] | result["failures"],
            "fetched_at": result["fetched_at"],
        }
        path.write_text(json.dumps(done, indent=1), "utf-8")


if __name__ == "__main__":
    asyncio.run(main([c.upper() for c in sys.argv[1:]]))
