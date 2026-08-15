"""Deciding what a page is, deterministically.

Two rules do most of the work:

  * Link text outweighs the URL. Japan's tourism checklist lives at "index_000070.html" and is
    identifiable only by being labelled "Temporary Visitor Visa". A URL-only scorer fails outright.
  * Wrong-audience pages must be pushed down hard. A spouse-visa checklist on the correct domain,
    in the correct format, is the most dangerous candidate there is, because every other check
    passes and the traveller is told to bring the wrong documents.

No model is involved. Scores are explainable, repeatable, and free.
"""

from visa_research_agent.discovery.lexicon import (
    Country,
    CountryRegistry,
    Lexicon,
    PurposeTerms,
)
from visa_research_agent.discovery.models import (
    ROLE_ORDER,
    CandidatePage,
    Corridor,
    DiscoveryRole,
    PageLink,
    RoleScores,
)
from visa_research_agent.discovery.urls import is_pdf_url, path_segments
from visa_research_agent.domain.models import SourceKind
from visa_research_agent.domain.trust import host_is_within, host_of


def _contains_phrase(haystack: str, phrase: str) -> bool:
    return phrase.lower() in haystack.lower()


def searchable_url(url: str) -> str:
    """Flatten a URL so prose phrases match it.

    URLs separate words with hyphens, underscores and slashes where the vocabulary uses spaces, so
    without this "documents-required.pdf" would never match the phrase "documents required".
    """

    lowered = url.lower()
    for separator in ("-", "_", "/", ".", "+"):
        lowered = lowered.replace(separator, " ")
    return lowered


def _matches_country(link: PageLink, country: Country) -> bool:
    """True when a link plainly refers to a country.

    Two-letter codes are matched only as a whole path segment or host label, never inside a word,
    or "in" would match "information" on almost every government page.
    """

    segments = path_segments(link.url)
    text = link.text.lower()
    host_labels = host_of(link.url).split(".")

    for token in country.text_tokens:
        if token in text:
            return True
        if any(token == segment or token in segment.split("-") for segment in segments):
            return True
    return any(label in host_labels for label in country.host_labels)


def is_archived(url: str, lexicon: Lexicon) -> bool:
    """True when a path marks a page as superseded.

    An archived checklist that still reads plausibly is exactly what must never be selected, so
    this rejects rather than penalises.
    """

    segments = path_segments(url)
    if any(token in segments for token in lexicon.archive_tokens):
        return True
    # A year two or more years old in the path is a strong archive signal.
    return any(
        segment.isdigit() and len(segment) == 4 and 1990 <= int(segment) <= 2024
        for segment in segments
    )


def wrong_audience(link: PageLink, corridor: Corridor, lexicon: Lexicon) -> str | None:
    """Name the audience a page is for when it is plainly not this traveller.

    A veto rather than a penalty. A diplomatic-passport exemption list names many nationalities and
    reads like authoritative guidance, so no accumulated score should be able to carry it through.
    """

    own = {term.lower() for term in lexicon.purposes.get(corridor.purpose, PurposeTerms()).terms}
    haystack = f"{link.text} {link.heading} {searchable_url(link.url)}".lower()
    for term in lexicon.hard_off_scope:
        if term.lower() in own:
            continue
        if term.lower() in haystack:
            return term
    return None


def wrong_country(
    link: PageLink,
    corridor: Corridor,
    registry: CountryRegistry,
    destination_code: str | None,
) -> str | None:
    """Name a country the page is plainly about that is not part of this corridor.

    Used only to reject. The reverse inference is not safe: a page mentioning India is not
    necessarily a page *for* Indians.
    """

    allowed = {corridor.passport_nationality, corridor.applying_from}
    if destination_code:
        allowed.add(destination_code)
    for country in registry.countries:
        if country.code in allowed:
            continue
        if _matches_country(link, country):
            return country.name
    return None


def score_link(
    link: PageLink,
    corridor: Corridor,
    lexicon: Lexicon,
    nationality: Country,
    residence: Country,
    *,
    host_kind: SourceKind | None = None,
    mission_domains: list[str] | None = None,
) -> RoleScores:
    """Score a link for every role, from its URL, anchor text and heading."""

    url_text = searchable_url(link.url)
    label = link.text.strip().lower()
    heading = link.heading.strip().lower()
    # Kept together only for the cheap "does this mention X at all" checks below.
    anchor = f"{label} {heading}".strip()
    scores: dict[str, float] = {}
    signals: dict[str, list[str]] = {}

    for role_name in ROLE_ORDER:
        role_terms = lexicon.roles.get(role_name)
        if role_terms is None:
            continue
        total = 0.0
        reasons: list[str] = []
        for term in role_terms.terms:
            if _contains_phrase(url_text, term.phrase):
                total += term.weight
                reasons.append(f"url:{term.phrase}+{term.weight:g}")
            if label and _contains_phrase(label, term.phrase):
                weighted = term.weight * lexicon.link_text_weight
                total += weighted
                reasons.append(f"text:{term.phrase}+{weighted:g}")
            # A heading describes the section, not this link, so it counts for less. Without
            # this every form under "Visa Application Documents" reads as a checklist.
            elif heading and _contains_phrase(heading, term.phrase):
                weighted = term.weight * lexicon.heading_weight
                total += weighted
                reasons.append(f"heading:{term.phrase}+{weighted:g}")
        if total:
            scores[role_name] = total
            signals[role_name] = reasons

    mentions_visa = "visa" in url_text or (anchor and "visa" in anchor)
    if not scores and mentions_visa:
        scores["visa_decision"] = lexicon.base_visa_weight
        signals["visa_decision"] = [f"mentions-visa+{lexicon.base_visa_weight:g}"]
    elif mentions_visa and "visa_decision" in scores:
        scores["visa_decision"] += lexicon.base_visa_weight
        signals["visa_decision"].append(f"mentions-visa+{lexicon.base_visa_weight:g}")

    # A link labelled only with the traveller's purpose is still worth reading. Japan's tourism
    # checklist is reached by a link saying just "Tourism", whose URL never mentions visas, so
    # without this the correct page is scored zero and never even fetched.
    purpose_label = lexicon.purposes.get(corridor.purpose)
    if purpose_label and label and any(
        _contains_phrase(label, term) for term in purpose_label.terms
    ):
        for role_name in ("document_checklist", "application_route"):
            if role_name not in scores:
                scores[role_name] = lexicon.base_purpose_weight
                signals[role_name] = [
                    f"purpose-label:{corridor.purpose}+{lexicon.base_purpose_weight:g}"
                ]

    if not scores:
        return RoleScores()

    shared = 0.0
    shared_reasons: list[str] = []

    if _matches_country(link, nationality):
        shared += lexicon.nationality_weight
        shared_reasons.append(f"nationality:{nationality.code}+{lexicon.nationality_weight:g}")

    purpose_terms = lexicon.purposes.get(corridor.purpose)
    if purpose_terms and any(
        _contains_phrase(url_text, term) or (anchor and _contains_phrase(anchor, term))
        for term in purpose_terms.terms
    ):
        shared += purpose_terms.weight
        shared_reasons.append(f"purpose:{corridor.purpose}+{purpose_terms.weight:g}")

    # One penalty, not one per term: the presence of a wrong-audience signal is what matters.
    off_scope = lexicon.off_scope_terms_for(corridor.purpose)
    hit = next(
        (
            term
            for term in off_scope
            if _contains_phrase(url_text, term) or (anchor and _contains_phrase(anchor, term))
        ),
        None,
    )
    if hit is not None:
        shared += lexicon.off_scope.weight
        shared_reasons.append(f"off-scope:{hit}{lexicon.off_scope.weight:g}")

    # A blank form is not a list of what to bring, and a translated copy is not a new page.
    form_hit = next(
        (
            term
            for term in lexicon.form_terms
            if _contains_phrase(url_text, term) or (anchor and _contains_phrase(anchor, term))
        ),
        None,
    )
    if form_hit is not None:
        shared += lexicon.form_penalty
        shared_reasons.append(f"form:{form_hit}{lexicon.form_penalty:g}")

    language_hit = next(
        (term for term in lexicon.language_terms if anchor and _contains_phrase(anchor, term)),
        None,
    )
    if language_hit is not None:
        shared += lexicon.language_penalty
        shared_reasons.append(f"translation:{language_hit}{lexicon.language_penalty:g}")

    segments = path_segments(link.url)
    stem = segments[-1].rsplit(".", 1)[0] if segments else ""
    if stem in lexicon.index_page_stems:
        shared += lexicon.index_page_penalty
        shared_reasons.append(f"section-index{lexicon.index_page_penalty:g}")

    if len(path_segments(link.url)) <= 4:
        shared += lexicon.shallow_path_weight
        shared_reasons.append(f"shallow+{lexicon.shallow_path_weight:g}")

    if link.depth:
        shared += lexicon.depth_penalty_weight * link.depth
        shared_reasons.append(f"depth{link.depth}{lexicon.depth_penalty_weight * link.depth:g}")

    if host_kind:
        bonus = lexicon.authority_kind_bonus.get(host_kind, 0.0)
        if bonus:
            shared += bonus
            shared_reasons.append(f"{host_kind}+{bonus:g}")

    for scored_role in list(scores):
        scores[scored_role] += shared
        signals[scored_role].extend(shared_reasons)

    # How this traveller applies is set by the mission serving where they live, so it outranks a
    # ministry's general pages for those two roles only.
    if mission_domains and host_is_within(host_of(link.url), mission_domains):
        for mission_role in ("document_checklist", "application_route"):
            if mission_role in scores:
                scores[mission_role] += lexicon.mission_host_bonus
                signals[mission_role].append(f"mission+{lexicon.mission_host_bonus:g}")

    # Authorities routinely publish checklists as PDFs, so a PDF is evidence for that role only.
    if is_pdf_url(link.url) and "document_checklist" in scores:
        scores["document_checklist"] += lexicon.pdf_checklist_bonus
        signals["document_checklist"].append(f"pdf+{lexicon.pdf_checklist_bonus:g}")

    return RoleScores(scores=scores, signals=signals)


def score_body(
    text: str,
    title: str,
    corridor: Corridor,
    lexicon: Lexicon,
    nationality: Country,
) -> RoleScores:
    """Score a page from its own text, confirming or contradicting what the link suggested."""

    haystack = f"{title}\n{text}".lower()
    scores: dict[str, float] = {}
    signals: dict[str, list[str]] = {}

    for role_name in ROLE_ORDER:
        role_terms = lexicon.roles.get(role_name)
        if role_terms is None:
            continue
        total = 0.0
        reasons: list[str] = []
        for term in role_terms.terms:
            if _contains_phrase(haystack, term.phrase):
                total += term.weight
                reasons.append(f"body:{term.phrase}+{term.weight:g}")
        if total:
            scores[role_name] = total
            signals[role_name] = reasons

    if not scores:
        return RoleScores()

    shared = 0.0
    shared_reasons: list[str] = []
    if any(_contains_phrase(haystack, token) for token in nationality.text_tokens):
        shared += lexicon.nationality_weight
        shared_reasons.append(f"body-nationality:{nationality.code}+{lexicon.nationality_weight:g}")

    purpose_terms = lexicon.purposes.get(corridor.purpose)
    if purpose_terms and any(_contains_phrase(haystack, term) for term in purpose_terms.terms):
        shared += purpose_terms.weight
        shared_reasons.append(f"body-purpose:{corridor.purpose}+{purpose_terms.weight:g}")

    # In the body, a wrong-audience word only counts against the page when it is in the title,
    # because a passing mention in a list of visa types is normal and harmless.
    title_lower = title.lower()
    hit = next(
        (term for term in lexicon.off_scope_terms_for(corridor.purpose)
         if _contains_phrase(title_lower, term)),
        None,
    )
    if hit is not None:
        shared += lexicon.off_scope.weight
        shared_reasons.append(f"title-off-scope:{hit}{lexicon.off_scope.weight:g}")

    for scored_role in list(scores):
        scores[scored_role] += shared
        signals[scored_role].extend(shared_reasons)

    # A page that scores on many roles is usually a directory, not an answer, so breadth is
    # dampened. The exception is a page written for this nationality: Singapore's per-nationality
    # page genuinely covers the decision, the documents, the fee and the timing, and penalising it
    # for being comprehensive hands the checklist role to a narrower, wrong page.
    mentions_nationality = any(
        _contains_phrase(haystack, token) for token in nationality.text_tokens
    )
    breadth = len([role for role, value in scores.items() if value > 0])
    if breadth > lexicon.breadth_threshold and not mentions_nationality:
        factor = (lexicon.breadth_threshold / breadth) ** 0.5
        for scored_role in list(scores):
            scores[scored_role] *= factor
            signals[scored_role].append(f"breadth:{breadth}x{factor:.2f}")
    return RoleScores(scores=scores, signals=signals)


def rank_for_role(
    candidates: list[CandidatePage], role: DiscoveryRole
) -> list[tuple[CandidatePage, float]]:
    """Candidates for one role, best first, with ties broken by URL for determinism."""

    scored = [(candidate, candidate.combined(role)) for candidate in candidates]
    positive = [(candidate, score) for candidate, score in scored if score > 0]
    positive.sort(key=lambda pair: (-pair[1], pair[0].link.url))
    return positive
