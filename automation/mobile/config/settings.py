"""Runtime settings for the mobile stack, loaded from ``automation/mobile/.env``.

Two independent axes — never mix them:

* ``PLATFORM``       the OS the Appium driver talks to: ``android`` | ``ios``.
                     Overridden per run by ``pytest --platform=...``.
* ``APP_KIND``       what the build is: ``native`` | ``flutter``.
* ``FLUTTER_DRIVER`` Flutter builds only: ``native`` (UiAutomator2 / XCUITest through
                     ``Semantics(identifier:)`` — the default) | ``integration``
                     (appium-flutter-integration-driver — opt-in for debug builds).

``FLUTTER_ENABLED=true`` is a deprecated alias for ``APP_KIND=flutter`` and still works.

Parallel runs (PARALLEL-RUNS.md): everything a run shares with a run of the OTHER platform can
be given per platform — the test account (``IOS_USER_*`` / ``ANDROID_USER_*``) and the Appium
server (``IOS_APPIUM_PORT`` / ``ANDROID_APPIUM_PORT``). Unset → the shared ``APP_USER_*`` /
``APPIUM_PORT``, and the two platforms then run one at a time. ``settings.apply_platform()``
makes the choice once, when the platform of the run is known (conftest ``pytest_configure``,
the scripts).
"""

import hashlib
import warnings
from pathlib import Path
from typing import Literal, Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MOBILE_ROOT = Path(__file__).resolve().parents[1]
PLATFORMS: tuple[str, ...] = ("android", "ios")


def normalize_platform(value: str | None) -> str:
    """Lower-case and validate a platform name.

    Flutter is deliberately NOT a platform: it is an app kind (``APP_KIND``) that is
    tested through the Android / iOS drivers. Anything but android|ios raises a
    ``ValueError`` that says so.
    """
    platform = (value or "").strip().lower()
    if platform not in PLATFORMS:
        raise ValueError(
            f"platform must be android|ios (got {value!r}); "
            "Flutter is APP_KIND, see automation/mobile/README.md"
        )
    return platform


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=MOBILE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    appium_host: str = "127.0.0.1"
    appium_port: int = 4723

    platform: str = "android"
    app_kind: Literal["native", "flutter"] = "native"
    flutter_driver: Literal["native", "integration"] = "native"
    flutter_enabled: bool | None = None  # deprecated alias — see module docstring

    default_timeout: float = 15.0  # seconds, explicit waits (helpers/waits.py)
    # seconds, Appium session idle timeout. 900: API calls that wait out a network blip or the
    # server's code throttle must not end the one session a run shares (stable run 1, 2026-09-27:
    # 300 s of API timeouts ended it and 89 tests errored)
    new_command_timeout: int = 900

    android_device_name: str = "Pixel_7_API_34"
    android_platform_version: str = "14"
    android_app_path: str = "./builds/android/app-debug.apk"
    android_app_package: str = "com.example.app"
    android_app_activity: str = "com.example.app.MainActivity"

    # How scripts/qa.sh boots the emulator when none is running. The DNS servers: an emulator keeps
    # the DNS of the network it booted on and resolves nothing after the Mac changes network.
    android_emulator_args: str = "-netdelay none -netspeed full -dns-server 8.8.8.8,1.1.1.1"

    ios_device_name: str = "iPhone 15"
    ios_platform_version: str = "17.4"
    ios_app_path: str = "./builds/ios/App.app"
    ios_bundle_id: str = "com.example.app"

    # Тестовий акаунт Field Technician. Вхід = телефон|email -> 4-значний OTP,
    # пароля в апці немає (SRS FR-LOG-05). На DEV код захардкоджений.
    app_user_phone: str = ""
    app_user_email: str = ""
    app_user_otp: str = ""
    # The same, per platform — a second account lets iOS and Android run at the same time
    # (PARALLEL-RUNS.md). Empty → the shared APP_USER_* value above.
    ios_user_phone: str = ""
    ios_user_email: str = ""
    ios_user_otp: str = ""
    android_user_phone: str = ""
    android_user_email: str = ""
    android_user_otp: str = ""
    # One Appium server per platform for parallel runs; None → APPIUM_PORT.
    ios_appium_port: int | None = None
    android_appium_port: int | None = None
    # Set by apply_platform(): one letter that marks the test data of this platform's run
    # (fixtures/jobs.py run stamp) — two runs seeding in the same second never share an id.
    run_tag: str = "-"

    # Field Services API — лише підготовка/прибирання даних для UI-тестів
    # (docs/api/dev-test-data.md). Порожній API_BASE_URL -> фікстури з API = Blocked.
    api_base_url: str = ""
    api_admin_email: str = ""
    api_admin_password: str = ""
    api_timeout: float = 30.0  # seconds per request

    # Докази (README, "Evidence"): off = не писати (за замовчуванням — робочі прогони, запис
    # коштує ~5 с на тест); auto = писати кожен тест, зберігати лише для впалих або Blocked і
    # тестів з маркером e2e; all = зберігати всі. Звітний прогін: EVIDENCE_VIDEO=auto (рішення
    # власника 2026-09-24).
    evidence_video: Literal["auto", "all", "off"] = "off"

    @field_validator("platform")
    @classmethod
    def _validate_platform(cls, value: str) -> str:
        return normalize_platform(value)

    @field_validator("app_kind", "flutter_driver", "evidence_video", mode="before")
    @classmethod
    def _lowercase(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def _apply_deprecated_alias_and_cross_check(self) -> Self:
        if self.flutter_enabled:
            warnings.warn(
                "FLUTTER_ENABLED is deprecated: set APP_KIND=flutter instead "
                "(and FLUTTER_DRIVER=integration if you relied on the old Flutter driver)",
                DeprecationWarning,
                stacklevel=2,
            )
            self.app_kind = "flutter"
        if self.flutter_driver == "integration" and self.app_kind != "flutter":
            raise ValueError("FLUTTER_DRIVER=integration requires APP_KIND=flutter")
        return self

    def account(self, platform: str) -> tuple[str, str, str]:
        """(email, phone, otp) of the test account ``platform`` runs under."""
        p = normalize_platform(platform)
        return (
            getattr(self, f"{p}_user_email") or self.app_user_email,
            getattr(self, f"{p}_user_phone") or self.app_user_phone,
            getattr(self, f"{p}_user_otp") or self.app_user_otp,
        )

    def accounts(self) -> list[tuple[str, str]]:
        """Every (email, phone) a run may sign in with — what a shared report must hide."""
        seen = {(self.app_user_email, self.app_user_phone)}
        seen |= {self.account(p)[:2] for p in PLATFORMS}
        return sorted(pair for pair in seen if any(pair))

    def account_key(self, platform: str) -> str:
        """A fingerprint of the platform's account: tells two accounts apart in a lock file or a
        log without naming either."""
        email = self.account(platform)[0].strip().lower()
        return hashlib.sha256(email.encode()).hexdigest()[:12] if email else ""

    def appium_port_for(self, platform: str) -> int:
        return getattr(self, f"{normalize_platform(platform)}_appium_port") or self.appium_port

    def can_run_in_parallel(self) -> tuple[bool, str]:
        """May an iOS run and an Android run go at the same time? (yes, "") or (no, why)."""
        if not all(self.account_key(p) for p in PLATFORMS):
            return False, "a platform has no test account"
        if self.account_key("ios") == self.account_key("android"):
            return False, (
                "both platforms use ONE test account — set IOS_USER_* or ANDROID_USER_* to a "
                "second account"
            )
        if self.appium_port_for("ios") == self.appium_port_for("android"):
            return False, (
                "both platforms use ONE Appium server — set IOS_APPIUM_PORT and "
                "ANDROID_APPIUM_PORT to different ports"
            )
        return True, ""

    def apply_platform(self, platform: str) -> None:
        """Make this process a run of ``platform``: its account, its Appium server, its data tag.
        Idempotent; every reader of ``app_user_*`` / ``appium_url`` then sees the platform's own."""
        p = normalize_platform(platform)
        self.app_user_email, self.app_user_phone, self.app_user_otp = self.account(p)
        self.appium_port = self.appium_port_for(p)
        self.platform = p
        self.run_tag = p[0].upper()  # "I" | "A"

    @property
    def appium_url(self) -> str:
        return f"http://{self.appium_host}:{self.appium_port}"

    @property
    def is_flutter(self) -> bool:
        return self.app_kind == "flutter"

    @property
    def uses_flutter_integration(self) -> bool:
        """True only when a Flutter build is driven by the FlutterIntegration driver."""
        return self.is_flutter and self.flutter_driver == "integration"

    def app_path(self, platform: str) -> Path:
        """Absolute build path for ``platform``; relative paths resolve from automation/mobile/."""
        raw = (
            self.android_app_path
            if normalize_platform(platform) == "android"
            else self.ios_app_path
        )
        path = Path(raw).expanduser()
        return path if path.is_absolute() else MOBILE_ROOT / path

    def app_id(self, platform: str) -> str:
        """Bundle id (iOS) / package (Android) of the app under test."""
        if normalize_platform(platform) == "android":
            return self.android_app_package
        return self.ios_bundle_id

    def device_label(self, platform: str) -> str:
        """``iPhone 17 · iOS 26.5`` — the device configuration a verdict is limited to."""
        if normalize_platform(platform) == "android":
            return f"{self.android_device_name} · Android {self.android_platform_version}"
        return f"{self.ios_device_name} · iOS {self.ios_platform_version}"


settings = Settings()
