"""How much of the world the own-government trust rule can actually reach.

`tests/test_trust.py` checks that the rule is *correct* — that a lookalike domain cannot pass, that
a public suffix is refused. This file checks something correctness says nothing about: how many
countries the rule can reach at all.

That question was never asked until 2026-08-18, and the answer is the project's largest coverage
limit. `is_own_government` requires a domain to be **governmental** and **under the destination's
own top-level domain**, and the first half is decided by a list of hostname patterns — `gov`,
`go.xx`, `gouv.xx`, `gob.xx`, `govt.xx`, plus `gc.ca`, `admin.ch` and `europa.eu`. Every country
verified live so far happens to sit inside that list, so the audit behind DECISIONS entry 19 — 22
human decisions reproduced, 0 disagreements — was **survivorship**. Germany's foreign ministry is
`auswaertiges-amt.de`: no marker in it, and no `gov.de` convention to find one under.

**What the table below is, and is not.** `AUTHORITIES` is hand-written from knowledge rather than
fetched, so individual rows may name the wrong domain. It is a tripwire rather than a survey, and
its job is to make the number moving a visible diff. Replace rows with real `visa-discover
bootstrap` output as corridors are run — see DECISIONS entry 33 and TODO item 1.

**The mechanism tests at the end depend on none of that**, and they are the load-bearing part: they
hold the shape of the failure, and they encode why the tempting fix is forbidden.
"""

from typing import NamedTuple

from visa_research_agent.discovery.bootstrap import (
    DomainProposal,
    belongs_to_destination,
    looks_governmental,
)
from visa_research_agent.discovery.lexicon import get_country_registry


class Authority(NamedTuple):
    """Where a country publishes visa guidance, and whether its government is reachable at all."""

    visa_guidance: str
    """The domain actually holding entry requirements and document checklists."""

    marked_government_domain: str | None = None
    """A domain of the same government that *does* carry a marker, where one is known to exist.

    This separates two failures that look identical from inside `bootstrap.py`. Where this is set,
    the country is reachable but the trusted set cannot contain the page holding the answer. Where
    it is None, no domain of that government can be trusted and the destination refuses outright.
    Only filled in for countries whose visa-guidance domain fails, since it is the diagnosis.
    """


# One row per country: the domain a traveller would actually need read.
AUTHORITIES: dict[str, Authority] = {
    # --- Western Europe: the concentration of the problem -------------------------------------
    "DE": Authority("auswaertiges-amt.de"),  # no gov.de convention exists
    "NL": Authority("ind.nl"),
    "SE": Authority("migrationsverket.se"),
    "NO": Authority("udi.no"),
    "DK": Authority("nyidanmark.dk"),
    "FI": Authority("migri.fi"),
    "BE": Authority("dofi.ibz.be"),  # Belgium uses fgov.be — also unmarked
    "AT": Authority("bmeia.gv.at"),  # reachable since 2026-08-25: `gv` added as a marker
    "IT": Authority("esteri.it", "interno.gov.it"),
    "IE": Authority("irishimmigration.ie", "gov.ie"),
    "PT": Authority("vistos.mne.pt", "gov.pt"),
    "GR": Authority("mfa.gr", "gov.gr"),
    "CZ": Authority("mvcr.cz", "gov.cz"),
    "HU": Authority("kormany.hu", "gov.hu"),
    "RO": Authority("mae.ro", "gov.ro"),
    "ES": Authority("exteriores.gob.es"),
    "PL": Authority("gov.pl"),
    "CH": Authority("sem.admin.ch"),
    "FR": Authority("france-visas.gouv.fr"),
    "GB": Authority("gov.uk"),
    # --- The Americas -------------------------------------------------------------------------
    "US": Authority("travel.state.gov"),
    "CA": Authority("canada.ca", "cic.gc.ca"),  # reachable since 2026-08-25: canada.ca named
    "BR": Authority("gov.br"),
    "MX": Authority("inm.gob.mx"),
    "AR": Authority("migraciones.gob.ar"),
    "CL": Authority("serviciomigraciones.cl", "gob.cl"),
    "CO": Authority("cancilleria.gov.co"),
    "PE": Authority("migraciones.gob.pe"),
    "UY": Authority("gub.uy"),  # reachable since 2026-08-25: `gub` added as a marker
    # --- Asia-Pacific -------------------------------------------------------------------------
    "JP": Authority("mofa.go.jp"),
    "KR": Authority("immigration.go.kr"),
    "CN": Authority("nia.gov.cn"),
    "IN": Authority("mea.gov.in"),
    "SG": Authority("ica.gov.sg"),
    "TH": Authority("immigration.go.th"),
    "VN": Authority("xuatnhapcanh.gov.vn"),
    "ID": Authority("imigrasi.go.id"),
    "MY": Authority("imi.gov.my"),
    "PH": Authority("immigration.gov.ph"),
    "AU": Authority("immi.homeaffairs.gov.au"),
    "NZ": Authority("immigration.govt.nz"),
    # --- Middle East and Africa ---------------------------------------------------------------
    "AE": Authority("icp.gov.ae"),
    "SA": Authority("visa.mofa.gov.sa"),
    "QA": Authority("moi.gov.qa"),
    "TR": Authority("evisa.gov.tr"),
    "IL": Authority("gov.il"),
    "ZA": Authority("dha.gov.za"),
    "NG": Authority("immigration.gov.ng"),
    "KE": Authority("immigration.go.ke"),
    "EG": Authority("mfa.gov.eg"),
    # --- Eastern Europe -----------------------------------------------------------------------
    "RU": Authority("mid.ru", "gov.ru"),
    "UA": Authority("mfa.gov.ua"),
}

# Frozen so that a change is a visible diff rather than a silent drift. Measured 2026-08-18: the
# visa-guidance domain of each of these fails `is_own_government`, every one of them on the
# governmental half. Removing a country from this set is progress and should be deliberate.
UNREACHABLE_VISA_GUIDANCE = frozenset(
    {
        "BE",
        "CL",
        "CZ",
        "DE",
        "DK",
        "FI",
        "GR",
        "HU",
        "IE",
        "IT",
        "NL",
        "NO",
        "PT",
        "RO",
        "RU",
        "SE",
    }
)

# The subset with no reachable government domain at all, so the destination refuses outright with
# "no domain belonging to X's own government could be identified". For the rest, bootstrap succeeds
# and builds a trusted set that cannot contain the page holding the answer — the quieter failure.
REFUSED_OUTRIGHT = frozenset({"BE", "DE", "DK", "FI", "NL", "NO", "SE"})


def proposal_for(domain: str, code: str) -> DomainProposal:
    """Build the proposal `bootstrap.py` would build for a domain, minus the search evidence."""

    country = get_country_registry().require(code)
    return DomainProposal(
        domain=domain,
        looks_governmental=looks_governmental(domain),
        belongs_to_destination=belongs_to_destination(domain, country.tlds),
    )


def test_the_reference_table_names_only_countries_the_registry_knows() -> None:
    """A typo in a country code must not quietly remove a row from the measurement."""

    registry = get_country_registry()
    for code in AUTHORITIES:
        assert registry.get(code) is not None, code
    assert UNREACHABLE_VISA_GUIDANCE <= set(AUTHORITIES)
    assert REFUSED_OUTRIGHT <= UNREACHABLE_VISA_GUIDANCE


def test_the_trust_rule_reaches_exactly_the_countries_it_reaches_today() -> None:
    """The frozen split. A diff here is the point of this file, not a nuisance."""

    unreachable = {
        code
        for code, authority in AUTHORITIES.items()
        if not proposal_for(authority.visa_guidance, code).is_own_government
    }

    newly_broken = unreachable - UNREACHABLE_VISA_GUIDANCE
    newly_fixed = UNREACHABLE_VISA_GUIDANCE - unreachable
    assert not newly_broken, f"these countries stopped being reachable: {sorted(newly_broken)}"
    assert not newly_fixed, (
        f"these countries are now reachable: {sorted(newly_fixed)} — good; update "
        "UNREACHABLE_VISA_GUIDANCE and the count in DECISIONS entry 33"
    )
    # The set is the tripwire, deliberately not the denominator: rows are meant to be added as
    # corridors are run, so asserting a total would fight the growth TODO item 1 asks for. The
    # "19 of 51" the documents quote is the original measurement; France was added afterwards and
    # passes the rule — it fails later, at HTTP, which is a different limit entirely.
    assert len(unreachable) == len(UNREACHABLE_VISA_GUIDANCE) == 16


def test_every_unreachable_country_fails_on_the_governmental_half() -> None:
    """The finding, and the reason the fix cannot be in `belongs_to_destination`.

    Known problem 2 had warned about the other half — a government publishing outside its own TLD.
    Not one of these failures is that. Every one is a hostname carrying no marker the pattern list
    recognises, which is why the amendment has to be reviewed data naming the authority.
    """

    for code in sorted(UNREACHABLE_VISA_GUIDANCE):
        proposal = proposal_for(AUTHORITIES[code].visa_guidance, code)
        assert not proposal.looks_governmental, code
        assert proposal.belongs_to_destination, (
            f"{code} fails on the TLD half, which no recorded finding predicted — read entry 33 "
            "before adjusting anything"
        )


def test_a_country_with_no_marked_domain_refuses_rather_than_misreads() -> None:
    """Two failures that look identical from inside bootstrap, and are not the same problem.

    Where a government has *some* marked domain, bootstrap succeeds and the corridor is resolved
    against a trusted set that cannot contain the visa guidance — which is quieter and worse than a
    refusal, because nothing reports it. Where it has none, the destination refuses outright with a
    message that misdescribes why.
    """

    for code in sorted(UNREACHABLE_VISA_GUIDANCE):
        marked = AUTHORITIES[code].marked_government_domain
        if code in REFUSED_OUTRIGHT:
            assert marked is None, f"{code} has a reachable domain, so it is not refused outright"
            continue
        assert marked is not None, code
        assert proposal_for(marked, code).is_own_government, (
            f"{code}'s {marked} was recorded as a reachable government domain and is not one"
        )


def test_widening_the_marker_list_would_trust_the_agencies_the_rule_exists_to_keep_out() -> None:
    """Why `GOVERNMENT_PATTERNS` must not simply gain `.de`, `.nl` and the rest.

    For these countries the own-TLD test is the *only* other signal, and it cannot discriminate: a
    commercial visa agency under `.de` belongs to Germany exactly as much as the foreign ministry
    does. So relaxing the governmental half does not widen trust a little — it admits every
    commercial site in the country, which is precisely what entry 19 records the rule keeping out.
    """

    agencies = {"DE": "guenstige-visa-agentur.de", "NL": "visumaanvraag-snel.nl"}
    for code, agency in agencies.items():
        authority = AUTHORITIES[code].visa_guidance
        # The agency is indistinguishable from the ministry on the only half that still applies.
        assert belongs_to_destination(agency, get_country_registry().require(code).tlds)
        assert proposal_for(agency, code).belongs_to_destination == (
            proposal_for(authority, code).belongs_to_destination
        )
        # And both are refused today, which is the rule failing safe rather than failing open.
        assert not proposal_for(agency, code).is_own_government, (
            f"{agency} now passes the own-government rule. If a marker for .{code.lower()} was "
            "just added to GOVERNMENT_PATTERNS to reach this country's ministry, it admitted this "
            "commercial visa agency too — see CLAUDE.md and DECISIONS entry 33. The fix is a "
            "reviewed authority domain in committed data, not a wider pattern."
        )
        assert not proposal_for(authority, code).is_own_government, (
            f"{authority} is now reachable — update UNREACHABLE_VISA_GUIDANCE, but check the "
            "assertion above passed for the right reason first"
        )


def test_only_the_united_states_carries_a_governmental_marker_in_its_own_tlds() -> None:
    """`tlds` is where a mistake in `countries.yaml` would widen trust unreviewed.

    A country whose own top-level domain *is* a governmental marker collapses the two halves of the
    rule into one question, which is what admitted the whole US federal namespace (entry 22). That
    is legitimate for the United States and would be a silent error anywhere else, so the set of
    countries in that position is asserted rather than left to review.
    """

    collapsed = {
        country.code
        for country in get_country_registry().countries
        if any(looks_governmental(tld) for tld in country.tlds)
    }

    assert collapsed == {"US"}, (
        f"{sorted(collapsed)} now collapse the own-government rule into one question; entry 22's "
        "corroboration bar and the cap in automatic.py are what bound the consequence"
    )


def test_a_supranational_authority_can_never_belong_to_a_member_state() -> None:
    """The Schengen problem, which is a definition rather than a defect.

    For short-stay visas the decision genuinely lives at EU level as much as nationally, and
    `europa.eu` is recognised as governmental — but it cannot be *any* member state's own
    government, so no member can ever trust it. The fix is a reviewed supranational list, which
    amends the rule stated in entry 19; this test holds the gap in place until then.
    """

    assert looks_governmental("europa.eu")
    for code in ("FR", "DE", "IT", "NL"):
        country = get_country_registry().require(code)
        assert not belongs_to_destination("europa.eu", country.tlds), code
        assert not proposal_for("europa.eu", code).is_own_government, code


# Hostnames an attacker would try if they wanted to be mistaken for a government. Probed by hand on
# 2026-08-18 and recorded in TODO item 2; committed 2026-08-25 because that is when the pattern list
# was widened, and a safety property checked by hand once is a property nothing is holding.
SPOOFED_GOVERNMENT_HOSTNAMES = (
    # The original probe: "gov" placed somewhere that is not a label boundary at the end.
    "visa-gov.com",
    "gov-uk.com",
    "govuk.com",
    "thegov.uk",
    "gov.sg.evil.example",
    "immigration.gov.in.attacker.net",
    "esteri.it.visa-help.com",
    # The three markers added 2026-08-25, attacked the same way.
    "gv.at.attacker.net",
    "bmeia-gv.at",
    "gv-at.com",
    "mygv.at",
    "gub.uy.attacker.net",
    "mygub.uy",
    "canada.ca.evil.example",
    "notcanada.ca",
    "my-canada.ca",
    "canada-ca.com",
)

# What the same three markers must still accept, or the widening bought nothing.
MARKED_GOVERNMENT_HOSTNAMES = (
    "bmeia.gv.at",
    "www.bmeia.gv.at",
    "gub.uy",
    "www.gub.uy",
    "canada.ca",
    "www.canada.ca",
    "ircc.canada.ca",
    "gc.ca",
)


def test_a_marker_cannot_be_spoofed_by_putting_it_in_a_name() -> None:
    """Why `looks_governmental` is sound as a *sufficient* test, held as a test rather than a claim.

    The patterns match a marker only at a **label boundary anchored to the end**, so what they
    really check is "sits inside a registry-controlled government namespace" — `gov.sg` and `gv.at`
    cannot be bought — rather than "reads as official", which is what entry 2 forbids. That is an
    unforgeable property and the reason the rule is worth keeping; it is also the property most
    easily lost by a careless edit to a regex, which is what this holds in place.
    """

    for hostname in SPOOFED_GOVERNMENT_HOSTNAMES:
        assert not looks_governmental(hostname), f"{hostname} passes as governmental"


def test_the_markers_added_for_austria_uruguay_and_canada_still_accept_them() -> None:
    """The other direction, so a tightening cannot silently undo the 2026-08-25 correction."""

    for hostname in MARKED_GOVERNMENT_HOSTNAMES:
        assert looks_governmental(hostname), f"{hostname} no longer reads as governmental"
