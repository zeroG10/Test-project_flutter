"""Where the deliverables live — the one place a report path is spelled out.

`reports/` is what the project hands over (the third role beside `docs/`, what we were given, and `qa/`, what we
made while working). Per platform:

- `reports/<platform>/internal/` — the detailed report for the delivery team: `summary.html`, one page per module
  with every check and its evidence, `index.html`;
- `reports/<platform>/client/`   — the test completion report for the client;
- `reports/<platform>/pdf/`      — both as PDF, named by the date of the run they describe;
- `reports/site/<platform>/`     — the publishable build of the internal report (gitignored; `npm run qa:site`).

Renaming the folder is one edit here plus `git mv` (owner's decision of 2026-09-28: `exports/` became `reports/`).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "reports"
REPORTS_NAME = "reports"  # for links and prose


def internal_dir(platform: str) -> Path:
    return REPORTS_DIR / platform / "internal"


def client_dir(platform: str) -> Path:
    return REPORTS_DIR / platform / "client"


def pdf_dir(platform: str) -> Path:
    return REPORTS_DIR / platform / "pdf"


def site_dir(platform: str) -> Path:
    return REPORTS_DIR / "site" / platform


def evidence_dir(platform: str) -> Path:
    return internal_dir(platform) / "evidence"
