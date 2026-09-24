"""The EU may answer a Schengen member's visa decision, and nothing else (DECISIONS entry 201).

Offline: the committed YAML, the trust and render gates, the AWS challenge, and the role limit. The
live proof — Croatia `BD/AE` answering "visa required" from the regulation — is in the entry.
"""

import httpx
import pytest

from visa_research_agent.discovery.models import ResolvedSource, ResolvedTool
from visa_research_agent.discovery.resolver import (
    RoleDecision,
    confined_to_permitted_roles,
    derive_authority,
)
from visa_research_agent.discovery.supranational import (
    get_supranational_registry,
    newest_dated_link,
    with_union,
)
from visa_research_agent.domain.models import DestinationConfig, is_challenge
from visa_research_agent.research.rendering import may_answer_challenge_from
from visa_research_agent.research.robots import RobotsCache, RobotsVerdict

EUR_LEX = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20251230"


def croatia() -> DestinationConfig:
    return with_union(
        DestinationConfig(
            slug="croatia",
            display_name="Croatia",
            route_type="national",
            implementation_status="available",
            trusted_domains=["mvep.gov.hr"],
        ),
        "HR",
    )


def test_the_committed_tier_is_the_schengen_29_and_every_domain_is_evidenced() -> None:
    union = get_supranational_registry().by_code("EU")

    assert union is not None
    assert len(union.members) == 29 and "NO" in union.members, "a bare NO must not load as false"
    assert "IE" not in union.members and "CY" not in union.members
    assert union.roles == ["visa_decision"]
    assert all(evidence.strip() for evidence in union.reviewed.values())


def test_a_member_carries_the_union_apart_from_its_own_government_and_others_carry_nothing() -> (
    None
):
    config = croatia()
    ireland = with_union(croatia().model_copy(update={"supranational_domains": []}), "IE")

    assert config.trusted_domains == ["mvep.gov.hr"]
    assert config.trusts_host("eur-lex.europa.eu") and config.is_supranational("eur-lex.europa.eu")
    assert not config.is_supranational("mvep.gov.hr")
    assert not ireland.is_supranational("eur-lex.europa.eu")


def test_an_eu_page_is_cited_as_the_eus() -> None:
    authority, kind = derive_authority(EUR_LEX, croatia())

    assert authority == "European Union (eur-lex.europa.eu)"
    assert kind == "supranational_authority"


def test_an_eu_page_answers_the_decision_and_is_kept_from_every_other_role() -> None:
    eu = ResolvedSource(
        source_id="croatia_eur_lex",
        title="Regulation 2018/1806",
        url=EUR_LEX,  # type: ignore[arg-type]
        authority="European Union (eur-lex.europa.eu)",
        kind="supranational_authority",
        roles=["visa_decision", "document_checklist"],
        score=1.0,
    )
    own = eu.model_copy(
        update={
            "source_id": "croatia_checklist",
            "url": "https://mvep.gov.hr/checklist",
            "roles": ["document_checklist"],
        }
    )
    tool = ResolvedTool(role="document_checklist", url=EUR_LEX)
    notes: list[str] = []

    decision = confined_to_permitted_roles(
        RoleDecision(sources=[eu], unresolved=[], tools=[tool]), croatia(), notes
    )
    with_own = confined_to_permitted_roles(
        RoleDecision(sources=[eu, own], unresolved=[]), croatia(), []
    )

    assert [source.roles for source in decision.sources] == [["visa_decision"]]
    assert decision.unresolved == ["document_checklist"] and decision.tools == []
    assert any("may answer only visa_decision" in note for note in notes)
    assert "document_checklist" not in with_own.unresolved, "the country's own checklist stands"


def test_aws_wafs_challenge_is_a_challenge_and_its_captcha_is_not() -> None:
    assert is_challenge(202, {"x-amzn-waf-action": "challenge"}, "")
    assert not is_challenge(202, {}, "")
    assert not is_challenge(202, {"x-amzn-waf-action": "captcha"}, "")
    assert is_challenge(403, {}, "<script>AwsWafIntegration.saveReferrer();</script>")


def test_only_eur_lex_pages_may_reach_awss_token_host() -> None:
    token = "https://3e3378af7cd0.a62927d9.eu-west-1.token.awswaf.com/challenge.js"

    assert may_answer_challenge_from(token, EUR_LEX, croatia())
    assert not may_answer_challenge_from(token, "https://mvep.gov.hr/visas", croatia())
    assert not may_answer_challenge_from("https://evil.example/x.js", EUR_LEX, croatia())


@pytest.mark.anyio
async def test_a_challenged_robots_txt_is_no_policy_served() -> None:
    def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(202, headers={"x-amzn-waf-action": "challenge"}, text="")

    cache = RobotsCache(user_agent="VisaResearchAgent/test")
    async with httpx.AsyncClient(transport=httpx.MockTransport(answer)) as client:
        verdict = await cache.verdict(client, EUR_LEX)

    assert verdict is RobotsVerdict.ALLOWED


def test_the_refresh_follows_the_newest_link_exactly_as_the_page_writes_it() -> None:
    """`canonicalise_url` would drop the slash before `?uri=`, and EUR-Lex answers that address with
    "Page Not Found" (entry 201)."""

    html = (
        '<a href="/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20250203">old</a>'
        '<a href="/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20251230">new</a>'
        '<a href="/legal-content/EN/TXT/PDF/?uri=CELEX:02018R1806-20260101">pdf</a>'
    )
    pattern = r"legal-content/EN/TXT/HTML/?\?uri=CELEX(?::|%3A)02018R1806-(\d{8})$"

    newest = newest_dated_link(html, "https://eur-lex.europa.eu/eli/reg/2018/1806", pattern)

    assert newest == EUR_LEX
