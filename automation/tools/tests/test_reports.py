"""The final reports' plumbing: names from the manifest, the PDF name rule, and what counts as the test account's
personal data on a screen or a page (redact_screens.Terms). Offline — no run, no device, no API."""

from __future__ import annotations

import brand
import redact_screens


def test_every_slice_is_named_in_the_manifest() -> None:
    for key in ("ios", "android", "mobile"):
        slc = brand.slice_(key)
        assert slc.product.startswith("Concert Technologies Field Technicians")
        assert slc.file_prefix.startswith("ConcertTechnologies_FieldTechnicians_")
        assert not brand.unset(slc), "a client report with an unset name is a draft"
    assert brand.slice_("ios").run and brand.slice_("android").run
    assert brand.slice_("mobile").run is None  # the combined report reads the two platform runs


def test_pdf_name_carries_the_run_date() -> None:
    slc = brand.slice_("android")
    assert slc.pdf_name("TestCompletionReport", "2026-10-02") == (
        "ConcertTechnologies_FieldTechnicians_Android_TestCompletionReport_2026-10-02.pdf"
    )


def _terms() -> redact_screens.Terms:
    terms = object.__new__(redact_screens.Terms)  # no .env, no API: the matching rules only
    terms.email = "someone+77@example.com"
    terms.local = "someone"
    terms.phone = "5550147"
    terms.names = ["Avery", "Quinlan"]
    return terms


def test_a_screen_line_with_the_account_is_found() -> None:
    t = _terms()
    assert t.hit("someone+77@example.com")
    assert t.hit("Code sent to someone+77@exa")  # a cut-off email still carries the local part
    assert t.hit("+1 (202) 555-0147")
    assert t.hit("Avery Quinlan")
    assert not t.hit("Format: +1234567890 or name@example.com")
    assert not t.hit("Averyday tasks")  # a name inside another word is not the name


def test_a_page_naming_the_account_is_found() -> None:
    t = _terms()
    assert t.in_page("<p>Signed in as <b>Avery</b></p>")
    assert t.in_page("<td>+1 202 555 0147</td>")
    assert not t.in_page("<p>645 checks · 482 passed · 2026-10-02 19:55 UTC</p>")


def test_a_publish_fragment_has_no_document_skeleton(tmp_path) -> None:
    import build_reports

    page = tmp_path / "internal.html"
    page.write_text(
        "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='x'>"
        "<title>Mobile App QA Report</title><style>:root{}</style></head><body><div class='wrap'>x</div></body></html>",
        encoding="utf-8",
    )
    out = build_reports.publish_fragment(page, tmp_path / "publish" / "internal-page.html")
    text = out.read_text(encoding="utf-8")
    assert text.startswith("<title>Mobile App QA Report</title>")
    assert "<div class='wrap'>x</div>" in text
    for tag in ("<!doctype", "<html", "<head>", "<body", "</body>"):
        assert tag not in text.lower()
