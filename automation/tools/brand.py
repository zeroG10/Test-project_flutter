"""The brand, in one place: the company's look every report draws from, and this project's names read from the manifest.

Two layers, kept apart on purpose (the same split as the web project's reports, 2026-09-28):

- **The company** — name, "Prepared by", colours, faces, the logo — is TRIARE's, the same in every project, so it
  lives here. The owner's brand: #3282EB (blue), #122E52 (navy), #F6F7FA (grey). The status colours (green / amber /
  red / violet) are deliberately NOT brand colours: a verdict has to read the same in any company's palette.
- **The project** — client, each report's product name, PDF file prefix, approver, confidentiality, published links,
  the runs each report describes — is read from `setup/project.yaml → report:`. No copy of those values lives in
  code, so a new project changes one file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "setup" / "project.yaml"

COMPANY = "TRIARE"
PREPARED_BY = "TRIARE QA"  # the author line


def _manifest() -> dict[str, Any]:
    try:
        data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    except OSError:
        return {}
    return data if isinstance(data, dict) else {}


def _filled(value: Any) -> bool:
    """A value someone actually set: not empty, not a <PLACEHOLDER> the setup has not replaced yet."""
    return bool(value) and not (isinstance(value, str) and value.strip().startswith("<"))


_REPORT: dict[str, Any] = _manifest().get("report") or {}


def _text(source: dict[str, Any], key: str, default: str = "—") -> str:
    value = source.get(key)
    return str(value) if _filled(value) else default


CLIENT = _text(_REPORT, "client")
CONFIDENTIALITY = _text(_REPORT, "confidentiality", "Confidential")
APPROVED_BY = _text(_REPORT, "approved_by")
ENVIRONMENT = _text(_REPORT, "environment", "the test environment")
OUT_OF_SCOPE = [str(x) for x in (_REPORT.get("out_of_scope") or []) if _filled(x)]
CLIENT_GROUPS: dict[str, str] = {str(k): str(v) for k, v in (_REPORT.get("client_groups") or {}).items() if _filled(v)}
CLIENT_BLOCKED: dict[str, str] = {str(k): str(v) for k, v in (_REPORT.get("client_blocked") or {}).items() if _filled(v)}


@dataclass(frozen=True)
class Slice:
    """One report's subject: `ios`, `android` or `mobile` (both)."""

    key: str
    product: str
    product_short: str
    file_prefix: str
    run: Path | None = None  # the run the report describes (a platform slice)
    history: list[Path] = field(default_factory=list)
    history_note: str = ""
    internal_url: str = ""
    client_url: str = ""

    def pdf_name(self, report: str, run_date: str) -> str:
        """The one spelling of a PDF's name: `<prefix>_<Report>_<date of the run it describes>.pdf`."""
        return f"{self.file_prefix}_{report}_{run_date}.pdf"


def slice_(key: str) -> Slice:
    raw = (_REPORT.get("slices") or {}).get(key) or {}
    product = _text(raw, "product")
    run = raw.get("run")
    return Slice(
        key=key,
        product=product,
        product_short=_text(raw, "product_short", product),
        file_prefix=_text(raw, "file_prefix", "".join(ch for ch in product.title() if ch.isalnum()) or "QA"),
        run=REPO_ROOT / run if _filled(run) else None,
        history=[REPO_ROOT / h for h in (raw.get("history") or []) if _filled(h)],
        history_note=_text(raw, "history_note", ""),
        internal_url=_text(raw, "internal_url", ""),
        client_url=_text(raw, "client_url", ""),
    )


def unset(slc: Slice) -> list[str]:
    """What a client document still lacks: a report with any of these unset is a draft, not for sending."""
    return [k for k, v in (("client", CLIENT), ("product", slc.product), ("approved_by", APPROVED_BY)) if v == "—"]


BLUE = "#3282EB"
NAVY = "#122E52"
GREY = "#F6F7FA"

# The brand font is not named yet: Manrope stands in (as in the web project's reports) and swaps in this one line.
FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800'
    '&family=IBM+Plex+Mono:wght@400;600;700&display=swap">'
)

_DARK = """color-scheme:dark;
  --ground:#0E1A2E; --surface:#162540; --ink:#E7EDF7; --muted:#97A6BE; --line:#263A57;
  --accent:#6FA8F5; --accent-soft:#1B2E4D; --navy:#0B1526; --on-navy:#E7EDF7; --figure:#E7EDF7;
  --pass:#5DD394; --known:#E3A94F; --fail:#F07167; --block:#B7A8F0; --idle:#3D4F6B;
  --pass-soft:#12352A; --known-soft:#33260F; --fail-soft:#3A1A1F; --block-soft:#252244;"""

# Light palette on bare :root; the dark palette under both the system preference (unless the viewer chose light)
# and an explicit dark choice, so a page reads right in all three viewer states.
TOKENS_CSS = (
    """
:root{
  --ground:#F6F7FA; --surface:#FFFFFF; --ink:#122E52; --muted:#5B6B85; --line:#DCE3EE;
  --accent:#3282EB; --accent-soft:#E6F0FD; --navy:#122E52; --on-navy:#FFFFFF; --figure:#122E52;
  --pass:#1E8E5A; --known:#B4761A; --fail:#C62828; --block:#5B4B9A; --idle:#C7CFDB;
  --pass-soft:#E3F3EA; --known-soft:#F8EDD9; --fail-soft:#FBE3E1; --block-soft:#ECE8F7;
  --display:"Manrope","Segoe UI",system-ui,sans-serif;
  --body:"Manrope",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){"""
    + _DARK
    + """} }
:root[data-theme="dark"]{"""
    + _DARK
    + """}
/* the logo's own colours, and the wordmark turned light on a dark ground */
.brand-logo .st0{fill:#122E52} .brand-logo .st1{fill:#3282EB}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .brand-logo .st0{fill:#FFFFFF} }
:root[data-theme="dark"] .brand-logo .st0{fill:#FFFFFF}
@media print{ .brand-logo .st0{fill:#122E52 !important} }
.brandbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;
  padding-bottom:12px;border-bottom:1px solid var(--line)}
.brandline{font:600 12px/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.tag{display:inline-block;font:700 11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  color:var(--on-navy);background:var(--navy);padding:6px 9px;border-radius:6px;vertical-align:middle}
.docinfo{margin-top:12px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--surface);
  font-size:13px;color:var(--muted)}
.docinfo b{color:var(--ink)} .docinfo a,.docinfo code{overflow-wrap:anywhere;word-break:break-all}
"""
)

_LOGO = Path(__file__).resolve().parent / "brand" / "triare-logo.svg"


def logo_svg(height_px: int = 26) -> str:
    """The logo inline, so no page depends on an external address; sized by height, width follows the viewBox."""
    svg = _LOGO.read_text(encoding="utf-8").strip()
    width = round(height_px * 180.9 / 46.4)
    return svg.replace("<svg ", f'<svg class="brand-logo" height="{height_px}" width="{width}" ', 1)


def brand_line(audience: str) -> str:
    """The line beside the logo: who prepared the report and for whom."""
    if audience == "client":
        return f"Prepared by {COMPANY} for {CLIENT}"
    return f"{COMPANY} · QA delivery team · Internal"


def brandbar(audience: str) -> str:
    return f'<div class="brandbar">{logo_svg(26)}<span class="brandline">{brand_line(audience)}</span></div>'
