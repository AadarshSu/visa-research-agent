"""Supporting quotes are kept only where the text this run retrieved actually holds them.

TODO item 21. A plan could say *which page* a claim came from and never *which sentence*. The model
now copies the sentence, and this module is why that is safe: a quote reaches a traveller only if it
is found in the cited source's retrieved text. The model's word is not enough, because an invented
or drifted quote attributed to a government page is worse than no quote at all.

Measured before building (DECISIONS entry 156): asked for quotes over three real corridors, the
model offered 35 and all 35 passed this check, covering 29 of 29 claims.
"""

import re
import unicodedata
from collections.abc import Collection, Mapping, Sequence

from visa_research_agent.domain.models import SupportingQuote

MINIMUM_QUOTE_CHARACTERS = 20
"""Below this a quote matches by accident — "a copy of the passport" is on most visa pages."""

MAXIMUM_QUOTE_CHARACTERS = 300
"""Above this it stops being a quote and starts reproducing the page."""

MAXIMUM_QUOTES_PER_CLAIM = 2

_QUOTE_MARKS = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})
_DASHES = re.compile("[‐-―−]")
_WHITESPACE = re.compile(r"\s+")


def normalise(text: str) -> str:
    """Forgive what copying changes and nothing that changes the words.

    Line breaks, runs of spaces, curly against straight quotation marks, the several dashes and
    letter case all differ between a cleaned page and a model's copy of it without changing what it
    says. Everything else — a missing word, a reordered clause, an ellipsis — has to match.
    """

    text = unicodedata.normalize("NFKC", text).translate(_QUOTE_MARKS)
    return _WHITESPACE.sub(" ", _DASHES.sub("-", text)).strip().casefold()


class QuoteChecker:
    """Checks quotes against one run's retrieved sources, normalising each source once."""

    def __init__(self, contents: Mapping[str, str]) -> None:
        self._texts = {source_id: normalise(text) for source_id, text in contents.items()}

    def keep(
        self, quotes: Sequence[SupportingQuote], cited_source_ids: Collection[str]
    ) -> list[SupportingQuote]:
        """The quotes that pass, in the order given, at most `MAXIMUM_QUOTES_PER_CLAIM`.

        A quote is dropped when it cites a source the claim does not, falls outside the length
        bounds, or is not found in that source's text. Dropped silently from the plan: the claim
        still stands on its citation, exactly as it did before quotes existed.
        """

        kept: list[SupportingQuote] = []
        for quote in quotes:
            if len(kept) == MAXIMUM_QUOTES_PER_CLAIM:
                break
            text = quote.text.strip()
            source_text = self._texts.get(quote.source_id)
            if (
                quote.source_id not in cited_source_ids
                or not MINIMUM_QUOTE_CHARACTERS <= len(text) <= MAXIMUM_QUOTE_CHARACTERS
                or source_text is None
                or normalise(text) not in source_text
            ):
                continue
            kept.append(SupportingQuote(source_id=quote.source_id, text=text))
        return kept
