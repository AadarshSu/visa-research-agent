"""Turning a country however it arrived into the one form the program keys everything on.

It lives apart from the request schemas because more than one edge hands the program a country: a
person typing into the form today, and an identity held by Ofself once TODO item 55's adapter
exists. Both must pass the same check, so a country with no reference data is refused whichever
way it came in (DECISIONS entry 20).
"""

from visa_research_agent.discovery.lexicon import get_country_registry


def normalise_country(value: str) -> str:
    """Accept a country however a person wrote it, and store the one canonical form.

    "IN", "IND", "in", "India" and "Republic of India" are the same country; corridors, cache keys
    and every lexicon lookup are keyed by the alpha-2 code, so the conversion happens once, at the
    edge. The alpha-3 form is here because Ofself's `work-authorization` may record it.
    """

    cleaned = value.strip()
    registry = get_country_registry()
    if len(cleaned) == 2 and cleaned.isalpha() and registry.get(cleaned.upper()) is not None:
        return cleaned.upper()
    if len(cleaned) == 3 and cleaned.isalpha():
        from_alpha3 = registry.code_for_alpha3(cleaned)
        if from_alpha3 is not None:
            return from_alpha3
    named = registry.code_for_name(cleaned)
    if named is None:
        raise ValueError(f"{cleaned} is not a country this agent holds reference data for")
    return named
