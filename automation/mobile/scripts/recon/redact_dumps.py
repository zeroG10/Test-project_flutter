"""Replace the test account's personal data in recon XML dumps before they are committed.

The dumps are raw Appium trees: a Profile or OTP screen carries the account's name, email and
phone. Screenshots never leave the scratchpad; the trees go to the repo, so they are redacted.

    cd automation/mobile
    PYTHONPATH=. uv run python scripts/recon/redact_dumps.py <dumps-dir> [--name "<shown name>"]

Replaces APP_USER_EMAIL, APP_USER_PHONE (E.164 and its 10 national digits) and the optional shown
name with [APP_USER_EMAIL], [APP_USER_PHONE], [APP_USER_NAME] — square brackets keep the XML
well-formed. Prints what it changed.
"""

import argparse
import re
from pathlib import Path

from config.settings import settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dumps")
    parser.add_argument("--name", default="")
    args = parser.parse_args()
    digits = re.sub(r"\D", "", settings.app_user_phone)
    national = digits[-10:]
    pairs = [
        (settings.app_user_email, "[APP_USER_EMAIL]"),
        (settings.app_user_phone, "[APP_USER_PHONE]"),
        (f"({national[:3]}) {national[3:6]}-{national[6:]}", "[APP_USER_PHONE]"),
        (national, "[APP_USER_PHONE]"),
    ]
    if args.name:
        pairs.append((args.name, "[APP_USER_NAME]"))
    for path in sorted(Path(args.dumps).glob("*.xml")):
        text = path.read_text(encoding="utf-8")
        hits = {}
        for secret, placeholder in pairs:
            if secret and secret in text:
                hits[placeholder] = hits.get(placeholder, 0) + text.count(secret)
                text = text.replace(secret, placeholder)
        if hits:
            path.write_text(text, encoding="utf-8")
            print(f"{path.name}: {hits}")


if __name__ == "__main__":
    main()
