"""Reading guidance that authorities publish as a PDF, often behind a forwarding page."""

from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from pypdf.errors import DependencyError
from test_live_sources import Clock, build_fetcher, destination

from visa_research_agent.research.live_sources import (
    extract_pdf_text,
    find_forward_target,
)
from visa_research_agent.research.source_cache import FileSourceCache

CHECKLIST_LINES = [
    "Items required for a temporary visitor visa application, for sightseeing purposes.",
    "One visa application form, completed in full and signed by the applicant themselves.",
    "One passport photograph taken within the last six months, on a plain background.",
    "A passport valid for the duration of the intended stay, presented as the original.",
    "Evidence of sufficient funds for the visit, such as a recent bank statement.",
    "A day-by-day itinerary covering the whole period of the intended stay in the country.",
    "Confirmed flight reservations showing both the arrival and the departure dates.",
    "Proof of the applicant's residence status in the United Kingdom, as the original.",
    "Documents that are not in English must be accompanied by a certified translation.",
    "Additional documents may be requested on a case-by-case basis after submission.",
]


def minimal_pdf(lines: list[str], *, encrypted: bool = False) -> bytes:
    """Build a small valid PDF containing the given lines of text."""

    text_operations = "\n".join(f"({line}) Tj T*" for line in lines)
    stream = f"BT /F1 12 Tf 20 700 Td 14 TL\n{text_operations}\nET"
    objects = [
        "<</Type/Catalog/Pages 2 0 R>>",
        "<</Type/Pages/Kids[3 0 R]/Count 1>>",
        "<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R"
        "/Resources<</Font<</F1 5 0 R>>>>>>",
        f"<</Length {len(stream)}>>stream\n{stream}\nendstream",
        "<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    document = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(document))
        document += f"{index} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref_at = len(document)
    document += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        document += f"{offset:010d} 00000 n \n".encode()
    encrypt = "/Encrypt 6 0 R" if encrypted else ""
    document += (
        f"trailer\n<</Size {len(objects) + 1}/Root 1 0 R{encrypt}>>\nstartxref\n{xref_at}\n%%EOF\n"
    ).encode()
    return bytes(document)


def forwarding_shell(target: str) -> str:
    """The pattern used by several authorities: a tiny page that forwards to the real document."""

    return (
        "<html><head><title>Items required</title>"
        f'<meta http-equiv="refresh" content="0;URL={target}">'
        "</head><body></body></html>"
    )


def test_pdf_text_is_extracted() -> None:
    text = extract_pdf_text(minimal_pdf(CHECKLIST_LINES), maximum_characters=50_000)

    assert "One visa application form" in text
    assert "day-by-day itinerary" in text


def test_pdf_extraction_respects_the_character_budget() -> None:
    text = extract_pdf_text(minimal_pdf(CHECKLIST_LINES), maximum_characters=60)

    assert len(text) <= 60


def test_an_unreadable_pdf_is_rejected_rather_than_returned_empty() -> None:
    with pytest.raises(ValueError, match="could not be read"):
        extract_pdf_text(b"%PDF-1.4 this is not really a pdf", maximum_characters=50_000)


def test_a_forwarding_page_target_is_resolved_against_the_page_url() -> None:
    target = find_forward_target(
        forwarding_shell("/files/100355579.pdf"),
        "https://immigration.gov.example/visa/sightseeing.html",
    )

    assert target == "https://immigration.gov.example/files/100355579.pdf"


def test_an_ordinary_page_has_no_forward_target() -> None:
    page = "<html><body><p>Real content.</p></body></html>"
    assert find_forward_target(page, "https://immigration.gov.example/visa") is None


@pytest.mark.anyio
async def test_a_pdf_served_directly_becomes_usable_evidence(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=minimal_pdf(CHECKLIST_LINES),
            headers={"Content-Type": "application/pdf"},
        )

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    report = await fetcher.fetch(destination())

    assert not report.failures
    assert "One visa application form" in report.fetched[0].content


@pytest.mark.anyio
async def test_a_forwarding_page_is_followed_to_the_pdf_it_points_at(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(".pdf"):
            return httpx.Response(
                200,
                content=minimal_pdf(CHECKLIST_LINES),
                headers={"Content-Type": "application/pdf"},
            )
        return httpx.Response(200, text=forwarding_shell("/files/checklist.pdf"))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    report = await fetcher.fetch(destination())

    assert not report.failures, f"unexpected gaps: {report.failures}"
    assert len(requests) == 2
    assert "day-by-day itinerary" in report.fetched[0].content
    # Provenance records the document actually read, not the page that pointed at it.
    assert report.fetched[0].source.is_stale is False


@pytest.mark.anyio
async def test_a_forward_off_the_trusted_domains_is_refused(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(_: httpx.Request) -> httpx.Response:
        # An approved page forwarding to an unapproved host is the same threat as a redirect,
        # and a PDF full of plausible guidance must not rescue it.
        return httpx.Response(200, text=forwarding_shell("https://visa-agent.example/list.pdf"))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    report = await fetcher.fetch(destination())

    assert not report.fetched
    failure = report.failures[0]
    assert failure.outcome == "untrusted"
    assert "visa-agent.example" in failure.detail
    assert len(requests) == 1, "an untrusted forward must not be fetched at all"


@pytest.mark.anyio
async def test_a_forwarding_chain_that_never_ends_is_refused(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=forwarding_shell(f"/next-{len(requests)}.html"))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    report = await fetcher.fetch(destination())

    assert report.failures[0].outcome == "unusable"
    assert "too many redirects" in report.failures[0].detail


@pytest.mark.anyio
async def test_an_oversized_document_is_refused(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, content=b"%PDF-1.4" + b"0" * 5000, headers={"Content-Type": "application/pdf"}
        )

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    fetcher.maximum_bytes = 1_000
    report = await fetcher.fetch(destination())

    assert report.failures[0].outcome == "unusable"
    assert "size limit" in report.failures[0].detail


@pytest.mark.anyio
async def test_a_cached_pdf_is_reused_without_refetching(tmp_path: Path) -> None:
    clock = Clock()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith(".pdf"):
            return httpx.Response(
                200,
                content=minimal_pdf(CHECKLIST_LINES),
                headers={"Content-Type": "application/pdf"},
            )
        return httpx.Response(200, text=forwarding_shell("/files/checklist.pdf"))

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    first = await fetcher.fetch(destination())
    clock.advance(5)
    second = await fetcher.fetch(destination())

    assert len(requests) == 2, "the forwarded PDF must be cached like any other source"
    assert second.fetched[0].from_cache is True
    assert second.fetched[0].content_hash == first.fetched[0].content_hash


def test_the_cache_directory_is_only_created_when_something_is_stored(tmp_path: Path) -> None:
    cache = FileSourceCache(tmp_path / "unused")

    assert cache.load("https://immigration.gov.example/visa") is None
    assert not (tmp_path / "unused").exists()


@pytest.mark.anyio
async def test_a_json_api_response_is_not_treated_as_guidance(tmp_path: Path) -> None:
    """Discovery surfaced Vietnam's e-visa language API, whose JSON cleared the readable-text
    floor and would otherwise have been quoted as official advice."""

    clock = Clock()
    requests: list[httpx.Request] = []
    entries = ",".join(f'{{"id":{index},"name":"language {index}"}}' for index in range(40))
    payload = '{"data":[' + entries + "]}"

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=payload, headers={"Content-Type": "application/json"})

    fetcher = build_fetcher(tmp_path, clock, handler, requests)
    report = await fetcher.fetch(destination())

    assert len(payload) > 400, "the payload must be long enough to clear the text floor"
    assert not report.fetched
    assert report.failures[0].outcome == "unusable"
    assert "data for a program" in report.failures[0].detail


def test_a_pdf_that_needs_a_missing_dependency_is_unreadable_not_fatal() -> None:
    """An encrypted PDF must cost one source, never the whole corridor.

    `pypdf.errors.DependencyError` — raised for an AES-encrypted PDF when the `cryptography` extra
    is absent — extends `Exception` **directly**, not `PdfReadError` and not even `PyPdfError`, so
    the original narrow `except` tuple could not catch it however carefully it was written. Sweden's
    corpus-routed shortlist held one, and `sweden/IN/GB/tourism` raised out of `_fetch_bodies` and
    resolved nothing at all (DECISIONS entry 54).

    The fake stands in for the encrypted file because reproducing one needs the very dependency
    whose absence causes the failure; what is being frozen is the *contract* — this function turns
    every input into text or into "could not be read", and never into an exception.
    """

    class Unparseable:
        def __init__(self, *args: object, **kwargs: object) -> None:
            raise DependencyError("cryptography>=3.1 is required for AES algorithm")

    with patch("visa_research_agent.research.live_sources.PdfReader", Unparseable):
        with pytest.raises(ValueError, match="the PDF could not be read"):
            extract_pdf_text(b"%PDF-1.7 encrypted", maximum_characters=1000)
