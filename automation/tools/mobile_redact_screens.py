#!/usr/bin/env python3
"""The test account's personal data on screenshots → the boxes the shared reports pixelate, and the check that none
is left.

The shared copy of a report hides the test account's email, phone and name in its text (`mobile_summary.Redactor`);
on the screens they are pixelated by boxes listed in a redactions file. Finding those boxes by eye does not scale
(the Android run alone saved 138 screens), so this reads every screen with macOS Vision — on the machine, nothing
leaves it — and boxes each text line that carries an account's email (or its local part), phone (its last 7 digits)
or first / last name — for every test account in the .env: the shared one and each platform's own. `--check DIR`
runs the same reading over a built copy and fails on any match.

The values are read from `automation/mobile/.env` (`*_USER_EMAIL`, `*_USER_PHONE`, and the names as
`*_USER_NAME`) and, if the project has one, from its hook `automation/mobile/helpers/account_names.py`
(`account_names() -> list[str]`, e.g. read from the product's API); none is printed or written anywhere.

    uv run python mobile_redact_screens.py boxes --platform android --images <dir> --out <redactions.json>
    uv run python mobile_redact_screens.py check <dir> [<dir> …]
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
ACCOUNT_PREFIXES = ("APP_USER", "IOS_USER", "ANDROID_USER")  # the shared account and each platform's own


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
    own — PARALLEL-RUNS.md): `APP_USER_NAME` / `IOS_USER_NAME` / `ANDROID_USER_NAME` in the .env ("First Last"),
    and whatever the project's hook returns (`automation/mobile/helpers/account_names.py`, run in the mobile
    harness's own environment, in a child process). Returned, never printed."""
    env = dotenv_values(MOBILE / ".env")
    names = [w for p in ACCOUNT_PREFIXES for w in (env.get(f"{p}_NAME") or "").split() if w]
    if (MOBILE / "helpers" / "account_names.py").exists():
        code = "import json\nfrom helpers.account_names import account_names\nprint(json.dumps(account_names()))\n"
        python = MOBILE / ".venv" / "bin" / "python"
        done = subprocess.run([str(python), "-c", code], cwd=MOBILE, capture_output=True, text=True, timeout=120)
        if done.returncode != 0:
            raise RuntimeError("Blocked: the project's helpers/account_names.py failed — the names are unknown")
        names += [str(n) for n in json.loads(done.stdout.strip().splitlines()[-1]) if n]
    return list(dict.fromkeys(names))


class Terms:
    """What counts as the account's personal data in a line of screen text."""

    def __init__(self, names: list[str]) -> None:
        env = dotenv_values(MOBILE / ".env")
        self.emails: list[str] = []
        self.locals: list[str] = []
        self.phones: list[str] = []
        for prefix in ACCOUNT_PREFIXES:  # the shared account and each platform's own
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
            raise RuntimeError(
                "Blocked: the accounts' email, phone or name is unknown — set *_USER_EMAIL / *_USER_PHONE / "
                "*_USER_NAME in automation/mobile/.env (or write helpers/account_names.py): nothing to look for"
            )

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
    text_hits = [
        p for p in files_in(args.dirs, (".html",)) if terms.in_page(p.read_text(encoding="utf-8", errors="ignore"))
    ]
    videos = files_in(args.dirs, (".mp4", ".mov", ".webm"))
    print(
        f"screens read: {len(images)} · screens still showing the account's data: {len(left)} · "
        f"pages naming it: {len(text_hits)} · videos: {len(videos)}"
    )
    for name in sorted(left)[:20]:
        print(f"  screen: {name}")
    for page in text_hits[:20]:
        print(f"  page: {page}")
    return 1 if (left or text_hits or videos) else 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.exit(main())
