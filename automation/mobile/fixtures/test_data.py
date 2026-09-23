"""Test data behind the ``{{…}}`` placeholders of the test cases. Secrets stay in .env.

* ``{{tech.*}}``          — the existing DEV test technician (read-only, ``APP_USER_*``).
* ``{{new_user.*}}``      — generated per test, unique; created by the test through the UI
                            and removed through the API (fixtures/app_state.py ``new_user``).
* ``{{unregistered.*}}``  — generated, never registered, nothing is created.

Reserved ranges only, so no real person ever gets a message: ``@example.com`` (RFC 2606)
and the fictional NANP block ``202-555-0100…0199``. Every generated email starts with
``qa-auto+`` — the marker the API cleanup refuses to go without.
"""

import re
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime

from config.settings import settings

TEST_EMAIL_DOMAIN = "example.com"
TEST_EMAIL_RE = re.compile(r"^qa-auto\+[a-z0-9-]+@example\.com$")
FICTIONAL_PREFIX = "202555"  # + "01xx" -> (202) 555-01xx


def _stamp() -> str:
    """UTC time to the second + 6 random hex chars: unique across runs and tests."""
    return datetime.now(UTC).strftime("%Y%m%d%H%M%S") + secrets.token_hex(3)


def _letters(value: int) -> str:
    """Integer -> lower-case letters (names accept alphabetic characters only)."""
    out = ""
    while True:
        value, rem = divmod(value, 26)
        out = chr(ord("a") + rem) + out
        if value == 0:
            return out


def _fictional_national() -> str:
    """10-digit US number in the fictional 555-01xx block."""
    return f"{FICTIONAL_PREFIX}01{secrets.randbelow(100):02d}"


@dataclass(frozen=True)
class Tech:
    """``{{tech.*}}`` — the registered DEV test technician."""

    email: str
    phone: str  # E.164, as the login field's own hint asks: +1XXXXXXXXXX
    otp: str

    @property
    def phone_national(self) -> str:
        """10 digits without +1 — what the registration phone field takes."""
        digits = re.sub(r"\D", "", self.phone)
        return digits[-10:]

    @property
    def phone_last4(self) -> str:
        return re.sub(r"\D", "", self.phone)[-4:]


@dataclass(frozen=True)
class NewUser:
    """``{{new_user.*}}`` — a technician the test registers itself."""

    first_name: str
    last_name: str
    email: str
    phone_national: str

    @property
    def phone(self) -> str:
        return f"+1{self.phone_national}"


def tech() -> Tech:
    """The test technician from .env; missing values are a Blocked run, never a guess."""
    missing = [
        key
        for key, value in (
            ("APP_USER_EMAIL", settings.app_user_email),
            ("APP_USER_PHONE", settings.app_user_phone),
            ("APP_USER_OTP", settings.app_user_otp),
        )
        if not value
    ]
    if missing:
        raise LookupError(f"Blocked: {', '.join(missing)} not set in automation/mobile/.env")
    return Tech(settings.app_user_email, settings.app_user_phone, settings.app_user_otp)


def new_user() -> NewUser:
    stamp = _stamp()
    return NewUser(
        first_name="Qaauto",
        last_name="Run" + _letters(int(stamp, 16) % 26**6),
        email=f"qa-auto+{stamp}@{TEST_EMAIL_DOMAIN}",
        phone_national=_fictional_national(),
    )


def unregistered_email() -> str:
    return f"qa-auto+unreg-{_stamp()}@{TEST_EMAIL_DOMAIN}"


def unregistered_phone() -> str:
    """E.164 — the login field format."""
    return f"+1{_fictional_national()}"


def wrong_otp(real_otp: str) -> str:
    """Any 4 digits except the DEV code (``{{otp.wrong}}``)."""
    return "0000" if real_otp != "0000" else "1111"
