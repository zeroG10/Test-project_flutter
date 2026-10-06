"""The brand, in one place: the company's look every report draws from, and this project's names read from the manifest.

Two layers, kept apart on purpose:

- **The company** — name, "Prepared by", colours, faces, the logo — is the same for every project made from this
  template, so it lives here: #3282EB (blue), #122E52 (navy), #F6F7FA (grey). The
  status colours (green / amber / red) are deliberately NOT brand colours: a verdict has to read the same in any
  company's palette.
- **The project** — client, product, how prose names it, PDF file prefix, confidentiality, approver, time zone — is
  read from `setup/project.yaml → report:`; what only the web reports state (published links, browser and history
  notes, scope notes, reviews, out of scope) from `report.web:`, and the mobile reports read `report.mobile:`. No
  copy of those values lives in code, so a new project changes one file (and `tests/test_brand.py` fails if a
  product name creeps back into the tooling).

Change a colour here and the internal report, the client report, the module pages, the defect pages and both PDFs
change together.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

import paths

COMPANY = "TRIARE"
PREPARED_BY = "TRIARE QA"  # the author line

MANIFEST = paths.REPO_ROOT / "setup" / "project.yaml"


def _manifest() -> dict[str, Any]:
    try:
        data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    except OSError:
        return {}
    return data if isinstance(data, dict) else {}


def _filled(value: Any) -> bool:
    """A value someone actually set: not empty, not a <PLACEHOLDER> the setup has not replaced yet."""
    return bool(value) and not (isinstance(value, str) and value.strip().startswith("<"))


_DATA = _manifest()
_REPORT: dict[str, Any] = _DATA.get("report") or {}
_WEB: dict[str, Any] = _REPORT.get("web") or {}
_PROJECT_NAME = (_DATA.get("project") or {}).get("name")


def _text(key: str, default: str = "—", source: dict[str, Any] | None = None) -> str:
    value = (_REPORT if source is None else source).get(key)
    return str(value) if _filled(value) else default


def _list(key: str, source: dict[str, Any] | None = None) -> list[str]:
    value = (_REPORT if source is None else source).get(key)
    return [str(x) for x in value if _filled(x)] if isinstance(value, list) else []


PRODUCT = _text("product", str(_PROJECT_NAME) if _filled(_PROJECT_NAME) else "—")
PRODUCT_SHORT = _text("product_short", PRODUCT)  # browser-tab titles
SUBJECT = _text("subject", PRODUCT)  # the product in running prose
CLIENT = _text("client")
FILE_PREFIX = _text("file_prefix", "".join(ch for ch in PRODUCT.title() if ch.isalnum()) or "QA")
CONFIDENTIALITY = _text("confidentiality", "Confidential")
APPROVED_BY = _text("approved_by")
TIMEZONE = _text("timezone", "UTC")  # the zone the reports state local times in (IANA name)

# The web reports: where each is published (a PDF prints these so it can never be mistaken for a different version)
# and this project's rulings, as the reports state them.
INTERNAL_REPORT_URL = _text("internal_url", "", _WEB)
CLIENT_REPORT_URL = _text("client_url", "", _WEB)
BROWSER_NOTE = _text("browser_note", "", _WEB)
HISTORY_NOTE = _text("history_note", "", _WEB)
SCOPE_NOTES = _list("scope_notes", _WEB)
OUT_OF_SCOPE = _list("out_of_scope", _WEB)
_reviews = _WEB.get("reviews") or {}
REVIEWS_NOTE = str(_reviews.get("note")) if _filled(_reviews.get("note")) else ""
REVIEW_DOCUMENTS = [str(x) for x in (_reviews.get("documents") or []) if _filled(x)]

BLUE = "#3282EB"
NAVY = "#122E52"
GREY = "#F6F7FA"

# Manrope stands in for the brand font — a geometric sans that sits well with the logo's rounded letterforms — and
# swaps for the real one in this one line.
FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800'
    '&family=IBM+Plex+Mono:wght@400;600;700&display=swap">'
)

# Light palette on bare :root; the dark palette under both the system preference (unless the viewer chose light)
# and an explicit dark choice, so a page reads right in all three viewer states.
TOKENS_CSS = """
:root{
  --ground:#F6F7FA; --surface:#FFFFFF; --ink:#122E52; --muted:#5B6B85; --line:#DCE3EE;
  --accent:#3282EB; --accent-soft:#E6F0FD; --navy:#122E52; --on-navy:#FFFFFF;
  --pass:#1E8E5A; --known:#B4761A; --fail:#C62828; --idle:#C7CFDB;
  --pass-soft:#E3F3EA; --known-soft:#F8EDD9; --fail-soft:#FBE3E1;
  --display:"Manrope","Segoe UI",system-ui,sans-serif;
  --body:"Manrope",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --ground:#0E1A2E; --surface:#162540; --ink:#E7EDF7; --muted:#97A6BE; --line:#263A57;
    --accent:#6FA8F5; --accent-soft:#1B2E4D; --navy:#0B1526; --on-navy:#E7EDF7;
    --pass:#5DD394; --known:#E3A94F; --fail:#F07167; --idle:#3D4F6B;
    --pass-soft:#12352A; --known-soft:#33260F; --fail-soft:#3A1A1F;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --ground:#0E1A2E; --surface:#162540; --ink:#E7EDF7; --muted:#97A6BE; --line:#263A57;
  --accent:#6FA8F5; --accent-soft:#1B2E4D; --navy:#0B1526; --on-navy:#E7EDF7;
  --pass:#5DD394; --known:#E3A94F; --fail:#F07167; --idle:#3D4F6B;
  --pass-soft:#12352A; --known-soft:#33260F; --fail-soft:#3A1A1F;
}
/* the logo's own colours, and the wordmark turned light on a dark ground */
.brand-logo .st0{fill:#122E52} .brand-logo .st1{fill:#3282EB}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .brand-logo .st0{fill:#FFFFFF} }
:root[data-theme="dark"] .brand-logo .st0{fill:#FFFFFF}
@media print{ .brand-logo .st0{fill:#122E52 !important} }
"""

_LOGO = Path(__file__).resolve().parent / "brand" / "triare-logo.svg"


def logo_svg(height_px: int = 28) -> str:
    """The logo inline, so no page depends on an external address; sized by height, width follows the viewBox."""
    svg = _LOGO.read_text(encoding="utf-8").strip()
    width = round(height_px * 180.9 / 46.4)
    return svg.replace("<svg ", f'<svg class="brand-logo" height="{height_px}" width="{width}" ', 1)


def brand_line(audience: str) -> str:
    """The line under the logo: who prepared the report and for whom."""
    if audience == "client":
        return f"Prepared by {COMPANY} for {CLIENT}"
    return f"{COMPANY} · QA delivery team · Internal"


def pdf_name(report: str, run_date: str) -> str:
    """The one spelling of a PDF's name: `<prefix>_<Report>_<date of the run it describes>.pdf`."""
    return f"{FILE_PREFIX}_{report}_{run_date}.pdf"


def names() -> dict[str, str]:
    """What the non-Python tools (the PDF exporter, the Allure config) need, written beside the run for them to read."""
    return {
        "company": COMPANY,
        "product": PRODUCT,
        "product_short": PRODUCT_SHORT,
        "subject": SUBJECT,
        "file_prefix": FILE_PREFIX,
    }
