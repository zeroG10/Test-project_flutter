"""The mobile reports' names and look, on top of the shared brand.

`brand.py` (shared with the web reports; the company's layer and `setup/project.yaml → report:`) is used as it
is: the company, "Prepared by", client, confidentiality, approver, colours, fonts, logo. This module adds only
what the mobile reports need and the web ones do not:

- **slices** — one report subject per platform and one for both: `report.mobile.slices.{ios,android,all}`
  (product name, PDF prefix, the run it describes, published links);
- the mobile reports' wording — `report.mobile.{environment,subject,scope_notes,out_of_scope,client_groups,
  client_blocked}`;
- two status colours the mobile pages use beside the brand's (Blocked is violet, never green) and the header
  pieces every mobile page shares (brand bar, the Internal tag, the Document block).

The mobile tools import it as `brand`, so a name is looked up in one place: here, then in the shared `brand`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import brand as shared
from brand import (  # noqa: F401 — re-exported: the mobile tools read every brand name from this module
    APPROVED_BY,
    BLUE,
    CLIENT,
    COMPANY,
    CONFIDENTIALITY,
    FONTS_LINK,
    GREY,
    NAVY,
    PREPARED_BY,
    brand_line,
)

REPO_ROOT = shared.MANIFEST.parents[1]
_filled = shared._filled
_MOBILE: dict[str, Any] = (shared._REPORT.get("mobile") or {}) if isinstance(shared._REPORT, dict) else {}


def _text(source: dict[str, Any], key: str, default: str = "—") -> str:
    value = source.get(key)
    return str(value) if _filled(value) else default


ENVIRONMENT = _text(_MOBILE, "environment", "the test environment")
SUBJECT = _text(_MOBILE, "subject", "mobile app")  # the app in running prose: "regression of the <subject>"
SCOPE_NOTES = [
    str(x) for x in (_MOBILE.get("scope_notes") or []) if _filled(x)
]  # the internal report's "Scope of this run"
OUT_OF_SCOPE = [str(x) for x in (_MOBILE.get("out_of_scope") or []) if _filled(x)]
CLIENT_GROUPS: dict[str, str] = {str(k): str(v) for k, v in (_MOBILE.get("client_groups") or {}).items() if _filled(v)}
CLIENT_BLOCKED: dict[str, str] = {
    str(k): str(v) for k, v in (_MOBILE.get("client_blocked") or {}).items() if _filled(v)
}

SLICES = ("ios", "android", "all")  # a platform each, and both together


@dataclass(frozen=True)
class Slice:
    """One report's subject: `ios`, `android` or `all` (both)."""

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
    raw = (_MOBILE.get("slices") or {}).get(key) or {}
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


# Beside the shared palette: Blocked (violet — could not run, never looks like a pass) and the colour of big
# figures, each in the three theme states the shared tokens use.
_EXTRA_LIGHT = "--block:#5B4B9A; --block-soft:#ECE8F7; --figure:#122E52;"
_EXTRA_DARK = "--block:#B7A8F0; --block-soft:#252244; --figure:#E7EDF7;"
TOKENS_CSS = (
    shared.TOKENS_CSS
    + f"""
:root{{ {_EXTRA_LIGHT} }}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{ {_EXTRA_DARK} }} }}
:root[data-theme="dark"]{{ {_EXTRA_DARK} }}
.brandbar{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;
  padding-bottom:12px;border-bottom:1px solid var(--line)}}
.brandline{{font:600 12px/1.3 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.tag{{display:inline-block;font:700 11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  color:var(--on-navy);background:var(--navy);padding:6px 9px;border-radius:6px;vertical-align:middle}}
.docinfo{{margin-top:12px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--surface);
  font-size:13px;color:var(--muted)}}
.docinfo b{{color:var(--ink)}} .docinfo a,.docinfo code{{overflow-wrap:anywhere;word-break:break-all}}
"""
)


def logo_svg(height_px: int = 26) -> str:
    return shared.logo_svg(height_px)


def brandbar(audience: str) -> str:
    return f'<div class="brandbar">{logo_svg(26)}<span class="brandline">{brand_line(audience)}</span></div>'
