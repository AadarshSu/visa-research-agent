"""The control arm: open-web search with no trust model, measured rather than served.

Every test here is offline. What is being checked is mostly that the arm is *naive in the right
ways* — it reads what the engine ranked, including the commercial agency, and it says so afterwards
— because an arm that quietly filtered anything would be a control for nothing.
"""

from collections.abc import Callable
from pathlib import Path

import httpx
import pytest

from visa_research_agent.discovery.baseline import (
    BaselineAnswer,
    baseline_packet,
    baseline_query,
    gather_baseline,
    judge_hosts,
    load_baseline_prompt,
    run_baseline,
)
from visa_research_agent.discovery.lexicon import Country, get_country_registry
from visa_research_agent.discovery.models import Corridor, SearchResult

pytestmark = pytest.mark.anyio

AGENT = "VisaResearchAgent/0.1"

# The three shapes entry 19 recorded when France, Vietnam and Brazil were bootstrapped, plus the
# authority itself. This is what an ungated search actually puts in front of a reader.
MINISTRY = "https://www.auswaertiges-amt.de/en/visa/requirements"
INSURER = "https://www.axa-schengen.com/en/germany-visa"
OTHER_GOVERNMENT = "https://de.usembassy.gov/visas/"
AGENCY = "https://www.germany-visa.org/apply"

PAGE = (
    "<html><body><h1>Visa requirements</h1>"
    "<p>Indian passport holders require a Schengen visa for short stays in Germany.</p>"
    "</body></html>"
)


def corridor() -> Corridor:
    return Corridor(
        destination_slug="germany",
        passport_nationality="IN",
        applying_from="IN",
        purpose="tourism",
    )


def germany() -> Country:
    return get_country_registry().require("DE")


def india() -> Country:
    return get_country_registry().require("IN")


class StubSearch:
    def __init__(self, urls: list[str]) -> None:
        self.urls = urls
        self.queries: list[str] = []

    async def search(self, query: str, *, count: int) -> list[SearchResult]:
        self.queries.append(query)
        return [
            SearchResult(url=url, title=f"Result {rank}", snippet="", query=query, rank=rank)
            for rank, url in enumerate(self.urls[:count])
        ]


def site(
    *, refuse: set[str] | None = None, robots: dict[str, str] | None = None
) -> Callable[[httpx.Request], httpx.Response]:
    refused = refuse or set()
    policies = robots or {}

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            published = policies.get(request.url.host)
            if published is None:
                return httpx.Response(404, text="not found")
            return httpx.Response(200, text=published, headers={"Content-Type": "text/plain"})
        if str(request.url) in refused:
            return httpx.Response(403, text="forbidden")
        return httpx.Response(200, text=PAGE, headers={"Content-Type": "text/html; charset=utf-8"})

    return respond


class StubDecider:
    def __init__(self, answer: BaselineAnswer) -> None:
        self.answer_to_give = answer
        self.packets: list[str] = []

    async def answer(self, system_prompt: str, packet: str) -> BaselineAnswer:
        self.packets.append(packet)
        return self.answer_to_give


class FailingDecider:
    async def answer(self, system_prompt: str, packet: str) -> BaselineAnswer:
        raise RuntimeError("the provider is down")


# --- being naive in the right ways ---------------------------------------------------------------


async def test_it_reads_the_commercial_agency_the_request_path_would_never_fetch() -> None:
    """The whole point. A control that filtered anything would be a control for nothing."""

    search = StubSearch([MINISTRY, INSURER, OTHER_GOVERNMENT, AGENCY])

    run = await gather_baseline(
        search,
        corridor(),
        "Germany",
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(site()),
    )

    assert len(run.pages) == 4
    assert "www.axa-schengen.com" in run.hosts
    assert "de.usembassy.gov" in run.hosts


async def test_the_query_carries_no_site_restriction() -> None:
    """`corridor_queries` constrains every query to an approved domain; this must not."""

    search = StubSearch([MINISTRY])

    await gather_baseline(
        search,
        corridor(),
        "Germany",
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(site()),
    )

    assert "site:" not in search.queries[0]
    assert search.queries == [baseline_query(corridor(), "Germany", india())]


def test_the_query_reads_the_same_way_for_a_country_with_no_demonym() -> None:
    """Phrasing that varied with the country would confound the measurement it feeds."""

    registry = get_country_registry()
    with_demonym = baseline_query(corridor(), "Germany", registry.require("IN"))
    without = baseline_query(corridor(), "Germany", registry.require("NG"))

    assert not registry.require("NG").demonyms
    assert with_demonym.replace("India", "X") == without.replace("Nigeria", "X")


# --- what it keeps, because these are about our conduct ------------------------------------------


async def test_it_obeys_robots_here_too() -> None:
    """Entry 36 is a rule about how this program behaves, not a feature of the pipeline tested."""

    search = StubSearch([MINISTRY, INSURER])
    transport = httpx.MockTransport(
        site(robots={"www.axa-schengen.com": "User-agent: *\nDisallow: /"})
    )

    run = await gather_baseline(
        search,
        corridor(),
        "Germany",
        india(),
        user_agent=AGENT,
        transport=transport,
    )

    assert [page.host for page in run.pages] == ["www.auswaertiges-amt.de"]
    assert INSURER in run.failures
    assert "crawl policy" in run.failures[INSURER]


async def test_a_refusal_is_recorded_and_never_retried() -> None:
    """Entry 18 binds the control arm as well: a block is reported, not worked around."""

    search = StubSearch([MINISTRY, INSURER])
    seen: list[str] = []

    def counting(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="not found")
        seen.append(str(request.url))
        if str(request.url) == INSURER:
            return httpx.Response(403, text="forbidden")
        return httpx.Response(200, text=PAGE, headers={"Content-Type": "text/html"})

    run = await gather_baseline(
        search,
        corridor(),
        "Germany",
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(counting),
    )

    assert run.failures[INSURER] == "the page answered HTTP 403"
    assert seen.count(INSURER) == 1, "a refusal is final; asking again is what entry 18 forbids"


# --- the grading that needs no human -------------------------------------------------------------


def test_the_host_grading_separates_the_three_ways_a_source_can_be_wrong() -> None:
    """Each of these is a real case from entry 19, and they fail differently."""

    verdicts = {
        verdict.host: verdict
        for verdict in judge_hosts(
            [
                "www.auswaertiges-amt.de",
                "de.usembassy.gov",
                "www.axa-schengen.com",
                "irgendwas.de",
            ],
            germany(),
        )
    }

    # The reviewed authority: Germany's foreign ministry carries no governmental marker, which is
    # known problem 2 — so the rule declines it here exactly as it declines it in the request path,
    # and a reviewed row in committed data is what lets the real pipeline read it.
    assert not verdicts["www.auswaertiges-amt.de"].own_government
    assert verdicts["www.auswaertiges-amt.de"].belongs

    # A real government, correct for Americans, wrong for this traveller.
    assert verdicts["de.usembassy.gov"].governmental
    assert not verdicts["de.usembassy.gov"].belongs
    assert not verdicts["de.usembassy.gov"].own_government

    # A commercial insurer, and a commercial site under the destination's own TLD.
    assert not verdicts["www.axa-schengen.com"].own_government
    assert not verdicts["irgendwas.de"].governmental


async def test_the_citations_are_graded_apart_from_the_results() -> None:
    """An agency ranked third costs nothing if unused; an answer built on one is the failure."""

    search = StubSearch([MINISTRY, INSURER])
    decider = StubDecider(
        BaselineAnswer(
            visa_required=True,
            visa_name="Schengen visa",
            documents=["passport"],
            cited_urls=[INSURER],
            reasoning="the insurer's page states it",
        )
    )

    result = await run_baseline(
        search,
        decider,
        corridor(),
        germany(),
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(site()),
    )

    assert [verdict.host for verdict in result.hosts] == [
        "www.auswaertiges-amt.de",
        "www.axa-schengen.com",
    ]
    assert [verdict.host for verdict in result.cited] == ["www.axa-schengen.com"]
    assert result.own_government_citations == 0
    assert result.answered


# --- how it fails --------------------------------------------------------------------------------


async def test_a_failed_model_call_records_the_failure_and_substitutes_nothing() -> None:
    """A control that fell back to another method would measure something else."""

    result = await run_baseline(
        StubSearch([MINISTRY]),
        FailingDecider(),
        corridor(),
        germany(),
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(site()),
    )

    assert result.answer is None
    assert not result.answered
    assert result.error is not None and "RuntimeError" in result.error


async def test_nothing_is_asked_when_no_page_could_be_read() -> None:
    def dead(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="not found")
        return httpx.Response(500, text="broken")

    decider = StubDecider(BaselineAnswer())
    result = await run_baseline(
        StubSearch([MINISTRY]),
        decider,
        corridor(),
        germany(),
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(dead),
    )

    assert decider.packets == []
    assert result.error == "no page could be read, so nothing was asked"


async def test_an_unstated_decision_is_kept_as_unstated() -> None:
    """No enforcement, deliberately. The request path overrides the model here; this one does not,
    and that difference is part of what is being measured."""

    result = await run_baseline(
        StubSearch([MINISTRY]),
        StubDecider(BaselineAnswer(visa_required=None, cited_urls=[MINISTRY])),
        corridor(),
        germany(),
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(site()),
    )

    assert result.answer is not None
    assert result.answer.visa_required is None
    assert not result.answered


# --- the packet and the prompt -------------------------------------------------------------------


async def test_page_text_reaches_the_model_labelled_untrusted() -> None:
    search = StubSearch([INSURER])
    decider = StubDecider(BaselineAnswer())

    await run_baseline(
        search,
        decider,
        corridor(),
        germany(),
        india(),
        user_agent=AGENT,
        transport=httpx.MockTransport(site()),
    )

    assert "untrusted_content" in decider.packets[0]
    assert "Schengen visa" in decider.packets[0]


def test_the_packet_carries_the_traveller_and_the_rank() -> None:
    from visa_research_agent.discovery.baseline import BaselineRun, ReadPage

    run = BaselineRun(corridor=corridor(), query="q")
    run.pages.append(ReadPage(url=MINISTRY, title="Requirements", rank=0, text="text"))

    packet = baseline_packet(run, "Germany", india())

    assert '"passport_nationality": "India"' in packet
    assert '"search_rank": 0' in packet


def test_the_prompt_exists_and_names_the_untrusted_field() -> None:
    prompt = load_baseline_prompt()

    assert prompt
    assert "untrusted" in prompt.lower()
    assert "cited_urls" in prompt


def test_the_prompt_ships_with_the_package() -> None:
    packaged = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "visa_research_agent"
        / "prompts"
        / "baseline_answer.txt"
    )

    assert packaged.exists()
