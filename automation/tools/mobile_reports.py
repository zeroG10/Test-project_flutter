#!/usr/bin/env python3
"""Every test completion report at once, from the runs `setup/project.yaml → report.mobile.slices` names.

Two copies, one command each — nothing runs against an environment, the reports are read from runs already made:

  local (default)  automation/mobile/reports/<slice>/{internal,client}/   gitignored — the full internal copy, with
                   API bodies, page sources and screen videos; for the QA machine only.
  --share          reports/mobile/<slice>/{internal,client,pdf}/ + reports/mobile/{internal,client}.html — the copy
                   people get: the test account's email, phone and name hidden in the text and pixelated on the
                   screens (boxes found by mobile_redact_screens.py), no API bodies, page sources or videos, screens
                   shrunk; checked by `mobile_redact_screens.py check` before anything else may use it. The final reports
                   of a regression are this copy, committed.

    cd automation/tools && uv run python mobile_reports.py [--share]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import mobile_brand as brand
import paths
import mobile_summary as bs
import mobile_client_report
import mobile_combined_report
import mobile_redact_screens
import mobile_report_data as rd

SHARE_ROOT = paths.REPORTS_DIR / "mobile"  # reports/<platform>/ — the layout the web reports use


def build(root: Path, share: bool) -> int:
    platforms: dict[str, rd.Platform] = {}
    name_vars: list[str] = []
    if share:
        # every test account's first and last name (the shared one and each platform's own), hidden in
        # the text like the email; held in this process's environment only
        for i, value in enumerate(mobile_redact_screens.account_names()):
            os.environ[f"QA_ACCOUNT_NAME_{i}"] = value
            name_vars.append(f"QA_ACCOUNT_NAME_{i}")
    for key in bs.PLATFORMS:
        slc = brand.slice_(key)
        if not slc.run:
            print(f"Blocked: no run for {key} in setup/project.yaml → report.mobile.slices.{key}.run", file=sys.stderr)
            return 2
        out = root / key / "internal"
        args = ["--platform", key, "--allure-dir", str(slc.run), "--out-dir", str(out)]
        for checklist in rd.checklists():
            args += ["--checklist", str(checklist)]
        for h in slc.history:
            args += ["--history-dir", str(h)]
        if slc.history_note:
            args += ["--history-note", slc.history_note]
        if share:
            boxes = bs.REPORTS / key / f"redactions-{slc.run.name}.json"
            code = mobile_redact_screens.main(
                ["boxes", "--images", str(bs.default_out(key) / "assets"), "--out", str(boxes)]
            )
            if code:
                return code
            args += ["--public", "--redact-boxes", str(boxes)]
            for var in name_vars:
                args += ["--redact-text-env", var]
        code = bs.main(args)
        if code:
            return code
        platforms[key] = rd.Platform(key, rd.load_report(key))
        print(f"internal: {out / 'index.html'}")
    both = [platforms["ios"], platforms["android"]]
    print(f"internal: {mobile_combined_report.write(both, root, entry=share)}")
    for key, ps in (("ios", [platforms["ios"]]), ("android", [platforms["android"]]), ("all", both)):
        print(f"client:   {mobile_client_report.write(key, ps, root)}")
        end = max(p.end for p in ps)
        slc = brand.slice_(key)
        # which run each report describes: the PDFs take their names and footers from here
        (root / key / "run.json").write_text(json.dumps({
            "date": end.strftime("%Y-%m-%d"), "runs": {p.key: p.run_date for p in ps}, "company": brand.COMPANY,
            "product": slc.product, "file_prefix": slc.file_prefix,
            "verdict": rd.worst(ps)[0],
        }, indent=1), encoding="utf-8")
    if share:
        print(f"client:   {mobile_client_report.write_entry(both, root)}")
        for name in ("internal", "client"):
            print(f"publish:  {publish_fragment(root / f'{name}.html', PUBLISH / f'{name}-page.html')}")
    return 0


PUBLISH = bs.REPORTS / "publish"  # gitignored: the main pages of the two published sites


def publish_fragment(page: Path, out: Path) -> Path:
    """An entry page as the Artifact host wants its main page: the host adds the document skeleton itself, so the
    page goes without doctype / html / head / body — head content first (title, fonts, style), then the body."""
    text = page.read_text(encoding="utf-8")
    text = re.sub(r"^<!doctype html><html lang=['\"]en['\"]><head><meta charset=['\"]utf-8['\"]>"
                  r"<meta name=['\"]viewport['\"][^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</body></html>\s*$", "", text.replace("</head><body>", "\n", 1))
    if re.search(r"<!doctype|<html|<head>|<body", text, re.IGNORECASE):
        raise ValueError(f"{page}: not a page this builder wrote — no fragment made")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--share", action="store_true", help="build the copy people get (reports/), checked")
    args = parser.parse_args(argv)
    root = SHARE_ROOT if args.share else bs.REPORTS
    code = build(root, args.share)
    if code or not args.share:
        return code
    # the shared copy is only done when nothing of the account is left on it
    return mobile_redact_screens.main(["check", *(str(root / k) for k in brand.SLICES),
                                str(root / "internal.html"), str(root / "client.html")])


if __name__ == "__main__":
    raise SystemExit(main())
