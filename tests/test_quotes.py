"""A supporting quote reaches a plan only where the retrieved text holds it (TODO item 21)."""

from visa_research_agent.domain.models import SupportingQuote
from visa_research_agent.research.quotes import (
    MAXIMUM_QUOTE_CHARACTERS,
    QuoteChecker,
    normalise,
)

PAGE = (
    "An ordinary Indian travel document requires an entry\n"
    "visa. Visitors need six months’ validity — at least."
)


def quote(text: str, source_id: str = "page") -> SupportingQuote:
    return SupportingQuote(source_id=source_id, text=text)


def test_a_quote_copied_from_the_page_survives_line_breaks_and_typography() -> None:
    """A cleaned page and a model's copy differ in spacing, quote marks, dashes and case."""

    kept = QuoteChecker({"page": PAGE}).keep(
        [
            quote("an ordinary Indian travel document requires an entry visa."),
            quote("Visitors need six months' validity - at least."),
        ],
        ["page"],
    )

    assert len(kept) == 2


def test_a_paraphrase_is_dropped() -> None:
    """Right in meaning is not enough: the words have to be on the page."""

    assert (
        QuoteChecker({"page": PAGE}).keep(
            [quote("An Indian passport holder needs a visa to enter.")], ["page"]
        )
        == []
    )


def test_a_quote_from_a_source_the_claim_does_not_cite_is_dropped() -> None:
    checker = QuoteChecker({"page": PAGE, "other": "Something else entirely, at length."})

    assert checker.keep([quote("requires an entry visa. Visitors need")], ["other"]) == []


def test_a_quote_from_a_source_this_run_did_not_retrieve_is_dropped() -> None:
    assert (
        QuoteChecker({"page": PAGE}).keep(
            [quote("requires an entry visa. Visitors", source_id="missing")], ["missing"]
        )
        == []
    )


def test_a_quote_too_short_or_too_long_is_dropped() -> None:
    long_page = "x" * (MAXIMUM_QUOTE_CHARACTERS + 50)
    checker = QuoteChecker({"page": PAGE, "long": long_page})

    assert checker.keep([quote("an entry visa")], ["page"]) == []
    assert (
        checker.keep([quote("x" * (MAXIMUM_QUOTE_CHARACTERS + 1), source_id="long")], ["long"])
        == []
    )


def test_at_most_two_quotes_are_kept_for_one_claim() -> None:
    kept = QuoteChecker({"page": PAGE}).keep(
        [
            quote("An ordinary Indian travel document"),
            quote("requires an entry visa. Visitors"),
            quote("six months' validity - at least."),
        ],
        ["page"],
    )

    assert [item.text for item in kept] == [
        "An ordinary Indian travel document",
        "requires an entry visa. Visitors",
    ]


def test_normalising_forgives_typography_and_nothing_else() -> None:
    assert normalise("Six  months’\n– VALID") == "six months' - valid"
    assert normalise("six months") != normalise("six month")
