"""Guidance an authority publishes by contracting it out: named, never read, never believed.

The Netherlands is why this exists. For most residences its own application page says, in as many
words, "on the VFS Global website you'll find a checklist with the documents you need" — so the
guidance is official, is current, and is on no government domain. Measured 2026-08-27: of 185 Dutch
pages published one per residence, 113 link no checklist of their own (DECISIONS entries 88, 89).

**The safety argument is that the model may select and may never supply.** A URL shown to a
traveller for the document checklist is the highest-stakes string this program emits, and it always
comes from an `href` our own crawler read off an approved government page — never from a model
reading `untrusted_content`, which a hostile or compromised page could steer. Most of this file is
that property, asserted from several directions.

Everything here is offline.
"""

from datetime import UTC, datetime

import httpx
import pytest
from discovery_site import destination
from pydantic import AnyHttpUrl

from visa_research_agent.config.loader import load_service_providers
from visa_research_agent.discovery.adjudication import (
    RoleAdjudication,
    RoleDelegate,
    build_candidate_packet,
    validated_delegates,
)
from visa_research_agent.discovery.corpus import CountryCorpus, merge
from visa_research_agent.discovery.crawl import CrawlFetcher, LinkCrawler
from visa_research_agent.discovery.models import (
    Corridor,
    Delegation,
    PageLink,
    ResolvedCorridor,
    ResolvedDelegate,
    ResolvedSource,
    RoleScores,
)

AUTHORITY = "authority.gov.example"
PAGE = f"https://{AUTHORITY}/visa/apply-india"
DELEGATE = "https://visa.vfsglobal.com/ind/en/xyz"
PROVIDERS = frozenset({"vfsglobal.com", "tlscontact.com"})
NOW = datetime(2026, 8, 28, tzinfo=UTC)


async def sleep_none(_: float) -> None:
    return None


def site() -> dict[str, str]:
    return {
        PAGE: (
            f'<a href="{DELEGATE}/">Find out which documents you need</a>'
            f'<a href="https://evil.example/phish">Apply here</a>'
            f'<a href="https://{AUTHORITY}/visa/fees">Visa fees</a>'
        ),
        f"https://{AUTHORITY}/visa/fees": "<p>90 euros</p>",
    }


def handler(requests: list[str]) -> object:
    pages = site()

    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="not found")
        url = str(request.url).rstrip("/")
        requests.append(url)
        if url in pages:
            return httpx.Response(
                200, text=pages[url], headers={"Content-Type": "text/html; charset=utf-8"}
            )
        return httpx.Response(404, text="not found")

    return respond


def crawler(requests: list[str], **kwargs: object) -> LinkCrawler:
    fetcher = CrawlFetcher(
        transport=httpx.MockTransport(handler(requests)),  # type: ignore[arg-type]
        sleep=sleep_none,
        host_delay_seconds=0.0,
    )
    return LinkCrawler(
        fetcher,
        lambda link: RoleScores(scores={"document_checklist": 20.0}),
        maximum_depth=2,
        maximum_pages=10,
        expansion_threshold=0.0,
        **kwargs,  # type: ignore[arg-type]
    )


def target() -> object:
    return destination().model_copy(update={"trusted_domains": [AUTHORITY]})


@pytest.mark.anyio
async def test_a_delegate_is_recorded_and_never_requested() -> None:
    """The whole shape in one test: written down, and not fetched.

    `is_crawlable` still refuses it — that is not weakened — and the recording happens on the
    refusal path precisely so the link is kept rather than silently dropped, which is what happened
    until 2026-08-28 and is why there was no record of where any authority sends anybody.
    """

    requests: list[str] = []
    walker = crawler(requests, provider_domains=PROVIDERS)

    await walker.crawl(target(), [PAGE])  # type: ignore[arg-type]

    assert DELEGATE in walker.delegations
    assert walker.delegations[DELEGATE].named_on == PAGE
    assert not any("vfsglobal" in url for url in requests), "a delegate must never be fetched"


@pytest.mark.anyio
async def test_an_off_domain_link_that_is_not_a_reviewed_provider_is_still_dropped() -> None:
    """The reviewed list is half the warrant, and this is the half that stops a hostile page.

    An approved government page linking `evil.example` proves only that the page linked it. Without
    the list, a compromised authority page could hand a traveller anything — for the checklist,
    which is the one output this project exists to get right.
    """

    requests: list[str] = []
    walker = crawler(requests, provider_domains=PROVIDERS)

    await walker.crawl(target(), [PAGE])  # type: ignore[arg-type]

    assert not any("evil.example" in url for url in walker.delegations)
    assert not any("evil.example" in url for url in requests)


@pytest.mark.anyio
async def test_recording_is_off_when_no_providers_are_configured() -> None:
    requests: list[str] = []
    walker = crawler(requests)

    await walker.crawl(target(), [PAGE])  # type: ignore[arg-type]

    assert walker.delegations == {}


def test_the_shipped_provider_list_holds_bare_lowercase_domains() -> None:
    """It is committed data a person edits, so the shape is checked rather than assumed."""

    registry = load_service_providers()

    assert registry.domains, "the list must not be empty while the feature is on"
    for provider in registry.providers:
        assert provider.domain == provider.domain.lower()
        assert "/" not in provider.domain and ":" not in provider.domain
        assert provider.name


def test_a_delegate_the_model_invented_is_discarded() -> None:
    """The safety property, stated at the boundary the model actually crosses.

    A `delegate_id` is an index into a list our crawler built. Anything else is dropped exactly as
    an invented `source_id` is, so no string a model produced can become a link a traveller follows.
    """

    recorded = {"delegate-1": Delegation(url=DELEGATE, named_on=PAGE)}
    adjudication = RoleAdjudication(
        delegates=[
            RoleDelegate(
                role="document_checklist",
                delegate_id="https://visa.vfsglobal-phishing.example/",
                reason="the checklist is here",
            )
        ]
    )

    kept, discarded = validated_delegates(adjudication, recorded)

    assert kept == {}
    assert discarded and "not a recorded delegation" in discarded[0]


def test_one_delegate_per_role_and_never_for_irrelevant() -> None:
    recorded = {
        "delegate-1": Delegation(url=DELEGATE, named_on=PAGE),
        "delegate-2": Delegation(url=DELEGATE + "b", named_on=PAGE),
    }
    adjudication = RoleAdjudication(
        delegates=[
            RoleDelegate(role="document_checklist", delegate_id="delegate-1", reason="here"),
            RoleDelegate(role="document_checklist", delegate_id="delegate-2", reason="also here"),
            RoleDelegate(role="irrelevant", delegate_id="delegate-1", reason="nowhere"),
        ]
    )

    kept, discarded = validated_delegates(adjudication, recorded)

    assert list(kept) == ["document_checklist"]
    assert kept["document_checklist"][0] == "delegate-1"
    assert len(discarded) == 2


def test_the_packet_gives_the_model_an_address_and_nothing_to_quote() -> None:
    """There is no field a body could go in, which is the same guard `build_blocked_packet` uses."""

    packet = build_candidate_packet(
        Corridor(destination_slug="xyz", passport_nationality="IN", applying_from="GB"),
        {},
        {},
        excerpt_characters=100,
        excerpt_head_characters=50,
        excerpt_window_characters=50,
        anchor_terms=["India"],
        delegations={"delegate-1": Delegation(url=DELEGATE, named_on=PAGE, link_text="Documents")},
    )

    assert "delegate-1" in packet and DELEGATE in packet
    assert "untrusted_content" not in packet.split("delegated_services")[1]


def test_a_corpus_keeps_delegations_and_never_drops_one() -> None:
    """Additive like the entries: a crawl that missed the page has not learned the deal ended."""

    corpus = CountryCorpus(
        country_code="NL",
        country_name="Netherlands",
        trusted_domains=[AUTHORITY],
        built_at=NOW,
        entries=[],
        delegations=[Delegation(url=DELEGATE, named_on=PAGE)],
    )

    after = merge(corpus, [], now=NOW, delegations=[])

    assert [item.url for item in after.delegations] == [DELEGATE]


def test_a_delegated_checklist_still_forbids_listing_a_requirement() -> None:
    """The rule this project exists to enforce, checked on the new path.

    Entry 60 made a questionnaire safe by leaving `application_document_source_ids` empty. A
    delegate has to be safe the same way, and for a stronger reason: nobody read the page at all.
    """

    resolved = ResolvedCorridor(
        corridor=Corridor(destination_slug="xyz", passport_nationality="IN", applying_from="GB"),
        resolved_at=NOW,
        sources=[],
        delegated_services=[
            ResolvedDelegate(role="document_checklist", url=DELEGATE, named_on=PAGE)
        ],
    )

    config = resolved.to_destination_config(target())  # type: ignore[arg-type]

    assert config.application_document_source_ids == []
    assert [service.topic for service in config.delegated_services] == ["document_checklist"]
    assert config.delegated_services[0].appointed_by == PAGE
    assert config.delegated_services[0].provider == "vfsglobal.com"
    assert not config.decision_is_unverified, "a company's site is not an authority withholding one"


def test_a_delegate_is_dropped_once_a_page_answers_the_role() -> None:
    """Sending someone to a contractor for a question a government page answered is noise."""

    resolved = ResolvedCorridor(
        corridor=Corridor(destination_slug="xyz", passport_nationality="IN", applying_from="GB"),
        resolved_at=NOW,
        sources=[
            ResolvedSource(
                source_id="checklist",
                title="Documents",
                url=AnyHttpUrl(f"https://{AUTHORITY}/visa/documents"),
                authority="Authority",
                kind="immigration_authority",
                roles=["document_checklist"],
                score=90.0,
                signals=[],
                decided_by="model",
            )
        ],
        delegated_services=[
            ResolvedDelegate(role="document_checklist", url=DELEGATE, named_on=PAGE)
        ],
    )

    config = resolved.to_destination_config(target())  # type: ignore[arg-type]

    assert config.delegated_services == []


def test_a_delegation_is_only_offered_while_its_warrant_is_still_trusted() -> None:
    """A domain narrowed since the corpus was built must stop vouching for what it once linked."""

    corpus = CountryCorpus(
        country_code="NL",
        country_name="Netherlands",
        trusted_domains=[AUTHORITY],
        built_at=NOW,
        entries=[],
        delegations=[
            Delegation(url=DELEGATE, named_on=PAGE),
            Delegation(url=DELEGATE + "x", named_on="https://withdrawn.example/page"),
        ],
    )

    kept = [
        record
        for record in corpus.delegations
        if PageLink(url=record.named_on, depth=0).url.startswith(f"https://{AUTHORITY}")
    ]

    assert [record.url for record in kept] == [DELEGATE]
