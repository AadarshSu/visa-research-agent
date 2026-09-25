"""Render a few pages with the project's renderer and report what came back, and how long it took.

    .venv/bin/python var/item70-2026-09-24/probe_render.py australia URL [URL ...]

Settings can be varied with PROBE_TIMEOUT (seconds) and PROBE_SETTLE (milliseconds).
"""

import asyncio
import os
import sys
import time

from visa_research_agent.config.settings import settings
from visa_research_agent.discovery.automatic import prepare_destination
from visa_research_agent.discovery.models import Corridor
from visa_research_agent.research.live_sources import clean_source_html
from visa_research_agent.research.rendering import PlaywrightPageRenderer


async def main() -> None:
    slug, urls = sys.argv[1], sys.argv[2:]
    corridor = Corridor(destination_slug=slug, passport_nationality="IN", applying_from="IN")
    destination = prepare_destination(slug, corridor).config
    timeout = float(os.environ.get("PROBE_TIMEOUT", settings.render_timeout_seconds))
    settle = int(os.environ.get("PROBE_SETTLE", settings.render_settle_milliseconds))
    print(f"timeout {timeout}s, settle {settle}ms")
    async with PlaywrightPageRenderer(
        user_agent=settings.source_user_agent, timeout_seconds=timeout, settle_milliseconds=settle
    ) as renderer:
        for url in urls:
            started = time.monotonic()
            try:
                page = await renderer.render(url, destination)
            except Exception as exc:  # noqa: BLE001 - a probe reports everything
                print(f"\n{url}\n  raised {type(exc).__name__}: {exc}")
                continue
            elapsed = time.monotonic() - started
            if page is None:
                print(f"\n{url}\n  None after {elapsed:.1f}s")
                continue
            text = clean_source_html(page.html, maximum_characters=60_000)
            print(f"\n{url}\n  {elapsed:.1f}s, html {len(page.html)}, text {len(text)}")
            print(f"  blocked hosts: {page.blocked_hosts}")
            print("  " + text[:600].replace("\n", " | "))


asyncio.run(main())
