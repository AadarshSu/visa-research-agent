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

import ast
from pathlib import Path
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
    "AT": Authority("bmeia.gv.at"),  # `gv` is simply missing from the marker list
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
    "CA": Authority("canada.ca", "cic.gc.ca"),  # content moved off the special-cased gc.ca
    "BR": Authority("gov.br"),
    "MX": Authority("inm.gob.mx"),
    "AR": Authority("migraciones.gob.ar"),
    "CL": Authority("serviciomigraciones.cl", "gob.cl"),
    "CO": Authority("cancilleria.gov.co"),
    "PE": Authority("migraciones.gob.pe"),
    "UY": Authority("gub.uy"),  # `gub` is simply missing from the marker list
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
        "AT",
        "BE",
        "CA",
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
        "UY",
    }
)

# The subset with no reachable government domain at all, so the destination refuses outright with
# "no domain belonging to X's own government could be identified". For the rest, bootstrap succeeds
# and builds a trusted set that cannot contain the page holding the answer — the quieter failure.
REFUSED_OUTRIGHT = frozenset({"AT", "BE", "DE", "DK", "FI", "NL", "NO", "SE", "UY"})


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
    assert len(unreachable) == len(UNREACHABLE_VISA_GUIDANCE) == 19


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


def test_the_request_path_cannot_reach_the_baseline_arm() -> None:
    """The control arm has no trust model. Nothing that answers a traveller may import it.

    `baseline.py` fetches through its own `httpx` client precisely so it never touches
    `LiveSourceFetcher`, whose `validate_route` is what makes a URL safe to read. A single import
    from the resolver or the API is all it would take for "read whatever the search engine ranked"
    to become reachable from a request, so the boundary is asserted rather than trusted to review —
    the same discipline as the mechanism tests above.

    Read as source text rather than by importing: an import graph built at runtime would only see
    modules something already loaded, and the point is to catch the edge before anyone runs it.
    """

    root = Path(__file__).resolve().parent.parent / "src" / "visa_research_agent"
    request_path = [
        root / "discovery" / "resolver.py",
        root / "discovery" / "automatic.py",
        root / "discovery" / "adjudication.py",
        root / "research" / "service.py",
        root / "research" / "live_sources.py",
        *sorted((root / "api").glob("*.py")),
    ]

    for module in request_path:
        assert module.exists(), module
        source = module.read_text(encoding="utf-8")
        assert "discovery.baseline" not in source, (
            f"{module.name} imports the baseline arm, which has no trust model at all"
        )
        assert "import baseline" not in source, module.name


def test_the_baseline_arm_never_builds_a_plan_or_a_trusted_fetcher() -> None:
    """The other direction: the arm must not quietly acquire the gate it exists without.

    If it ever reached for `LiveSourceFetcher` it would either reproduce the trust check — making
    it a control for nothing — or need a way to switch that check off, which is a code path that
    must not exist. And its output must stay a report: a `VisaPlan` is the type a traveller is
    served, and this one's claims are sourced from whatever a search engine ranked.
    """

    path = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "visa_research_agent"
        / "discovery"
        / "baseline.py"
    )
    # Parsed rather than grepped, because the module's own docstring names all three of these to
    # explain why they are absent. A text search would fail on the documentation of the rule.
    names = _identifiers(path)

    assert "LiveSourceFetcher" not in names
    assert "VisaPlan" not in names
    assert "validate_route" not in names
    # It must still behave itself as a client: entries 36, 18 and 12 are about our conduct, not
    # about the pipeline under test, so the control arm keeps them.
    assert "RobotsCache" in names, "robots.txt is obeyed here too — entry 36"
    assert "verify=False" not in path.read_text(encoding="utf-8")


def _identifiers(path: Path) -> set[str]:
    """Every name a module actually refers to, ignoring docstrings and comments."""

    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            found.add(node.id)
        elif isinstance(node, ast.Attribute):
            found.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
    return found
