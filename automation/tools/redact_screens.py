#!/usr/bin/env python3
"""The test account's personal data on screenshots → the boxes the shared reports pixelate, and the check that none
is left.

The shared copy of a report hides the test account's email, phone and name in its text (`build_summary.Redactor`);
on the screens they are pixelated by boxes listed in a redactions file. Finding those boxes by eye does not scale
(the Android run alone saved 138 screens), so this reads every screen with macOS Vision — on the machine, nothing
leaves it — and boxes each text line that carries an account's email (or its local part), phone (its last 7 digits)
or first / last name — for every test account in the .env: the shared one and each platform's own. `--check DIR` runs the same reading over a built copy and fails on any match.

The values are read from `automation/mobile/.env` and, for the name, from the DEV API (one read, in memory); none
is printed or written anywhere.

    uv run python redact_screens.py boxes --platform android --images <dir> --out <redactions.json>
    uv run python redact_screens.py check <dir> [<dir> …]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path

from dotenv import dotenv_values

TOOLS = Path(__file__).resolve().parent
MOBILE = TOOLS.parent / "mobile"
OCR_SOURCE = TOOLS / "ocr" / "ocr_lines.swift"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg")
PAD = 10  # pixels around a matched line


def ocr_binary() -> Path:
    """The Vision helper, compiled once per version of its source into the system temp folder."""
    target = Path(tempfile.gettempdir()) / f"qa-ocr-lines-{int(OCR_SOURCE.stat().st_mtime)}"
    if not target.exists():
        subprocess.run(["swiftc", "-O", str(OCR_SOURCE), "-o", str(target)], check=True, capture_output=True)
    return target


def ocr(paths: list[Path]) -> Iterable[dict]:
    binary = ocr_binary()
    for i in range(0, len(paths), 40):
        out = subprocess.run([str(binary), *map(str, paths[i : i + 40])], check=True, capture_output=True, text=True)
        for line in out.stdout.splitlines():
            if line.strip():
                yield json.loads(line)


def account_names() -> list[str]:
    """The first and last names of every test account a run signs in with (the shared one and each platform's
    own — PARALLEL-RUNS.md), read from the DEV API in a child process — returned, never printed."""
    code = (
        "import json, sys\n"
        "from config.settings import settings\n"
        "from helpers.field_services_api import FieldServicesApi\n"
        "api = FieldServicesApi()\n"
        "names = []\n"
        "for email, _ in settings.accounts():\n"
        "    techs = api.find_technicians_by_email(email) if email else []\n"
        "    u = (techs[0].get('user') or {}) if techs else {}\n"
        "    names += [u.get('firstName', ''), u.get('lastName', '')]\n"
        "print(json.dumps(names))\n"
        "api.close()\n"
    )
    python = MOBILE / ".venv" / "bin" / "python"
    done = subprocess.run([str(python), "-c", code], cwd=MOBILE, capture_output=True, text=True, timeout=120)
    if done.returncode != 0:
        raise RuntimeError("Blocked: could not read the account's name from the API")
    return [n for n in json.loads(done.stdout.strip().splitlines()[-1]) if n]


class Terms:
    """What counts as the account's personal data in a line of screen text."""

    def __init__(self, names: list[str]) -> None:
        env = dotenv_values(MOBILE / ".env")
        self.emails: list[str] = []
        self.locals: list[str] = []
        self.phones: list[str] = []
        for prefix in ("APP_USER", "IOS_USER", "ANDROID_USER"):  # the shared account and each platform's own
            email = (env.get(f"{prefix}_EMAIL") or "").strip().lower().replace(" ", "")
            digits = re.sub(r"\D", "", env.get(f"{prefix}_PHONE") or "")
            if email and email not in self.emails:
                self.emails.append(email)
                local = email.split("@")[0].split("+")[0]
                if len(local) >= 5 and local not in self.locals:
                    self.locals.append(local)
            if len(digits) >= 7 and digits[-7:] not in self.phones:
                self.phones.append(digits[-7:])
        self.names = sorted({n for n in names if len(n) >= 3})
        if not (self.emails and self.phones and self.names):
            raise RuntimeError("Blocked: the accounts' email, phone or name is unknown — nothing to look for")

    def in_page(self, body: str) -> bool:
        """A page's own text (markup stripped) naming the account: its email, a phone number ending in its digits,
        or its name."""
        plain = re.sub(r"<[^>]+>", " ", body)
        low = body.lower()
        if any(e in low for e in self.emails) or any(x in plain.lower() for x in self.locals):
            return True
        numbers = [re.sub(r"\D", "", m) for m in re.findall(r"\+?\d[\d\s().-]{6,}\d", plain)]
        if any(phone in number for phone in self.phones for number in numbers):
            return True
        return any(re.search(rf"(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])", plain, re.IGNORECASE) for n in self.names)

    def hit(self, text: str) -> bool:
        flat = text.lower().replace(" ", "")
        if any(e in flat for e in self.emails) or any(x in flat for x in self.locals):
            return True
        digits = re.sub(r"\D", "", text)
        if any(phone in digits for phone in self.phones):
            return True
        return any(re.search(rf"(?<![A-Za-z]){re.escape(n)}(?![A-Za-z])", text, re.IGNORECASE) for n in self.names)


def files_in(paths: list[Path], suffixes: tuple[str, ...]) -> list[Path]:
    """Files with these suffixes: the paths themselves when they are files, everything under them when folders."""
    found = [p for d in paths for p in ([d] if d.is_file() else d.rglob("*")) if p.suffix.lower() in suffixes]
    return sorted(set(found))


def images_in(dirs: list[Path]) -> list[Path]:
    return files_in(dirs, IMAGE_SUFFIXES)


def boxes(images: list[Path], terms: Terms) -> tuple[int, dict[str, list[list[int]]]]:
    found: dict[str, list[list[int]]] = {}
    width = 0
    for page in ocr(images):
        width = width or int(page["width"])
        name = Path(page["file"]).name
        for line in page["lines"]:
            if terms.hit(line["text"]):
                x0, y0, x1, y1 = line["box"]
                found.setdefault(name, []).append(
                    [max(0, x0 - PAD), max(0, y0 - PAD), min(page["width"], x1 + PAD), min(page["height"], y1 + PAD)]
                )
    return width, found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("boxes", help="write the redactions file for a platform's screens")
    b.add_argument("--images", type=Path, action="append", required=True)
    b.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("check", help="fail if any screen or page in the folders still shows the account's data")
    c.add_argument("dirs", type=Path, nargs="+")
    args = parser.parse_args(argv)
    terms = Terms(account_names())
    if args.cmd == "boxes":
        images = images_in(args.images)
        width, found = boxes(images, terms)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps({"points_width": width, "boxes": found}, indent=1), encoding="utf-8")
        print(f"boxes: {sum(len(v) for v in found.values())} on {len(found)} of {len(images)} screens -> {args.out}")
        return 0
    images = images_in(args.dirs)
    _, left = boxes(images, terms)
    text_hits = [p for p in files_in(args.dirs, (".html",)) if terms.in_page(p.read_text(encoding="utf-8", errors="ignore"))]
    videos = files_in(args.dirs, (".mp4", ".mov", ".webm"))
    print(f"screens read: {len(images)} · screens still showing the account's data: {len(left)} · "
          f"pages naming it: {len(text_hits)} · videos: {len(videos)}")
    for name in sorted(left)[:20]:
        print(f"  screen: {name}")
    for page in text_hits[:20]:
        print(f"  page: {page}")
    return 1 if (left or text_hits or videos) else 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
