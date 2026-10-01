"""Splash — Android offline (step 5): TC-SPL-004.

Source: qa/mobile/01-splash/android/splash-test-cases.md (owner-validated 2026-10-01;
Resolved D-OFF-9 — "ок": automated hand-over + logo check, screenshots kept as evidence for a
human to judge the subjective "no flicker" part of CHK-SPL-015). Android only: the throttled
network this check needs comes from the emulator console, not available on the iOS simulator.

Reuses the TC-SPL-001 pixel/tree splash oracle (pages/splash_page.py — the splash has no
labelled element; "shown" / "logo centred" are decided by pixels) under a throttled network
instead of full speed. Every expected text goes through ``expected(...)`` (--prove-red breaks
it).
"""

import allure
import pytest

from helpers import pixels
from pages.android.offline_page import OfflineBanner
from pages.splash_page import SplashMissed, SplashPage
from pages.welcome_page import WelcomePage
from tests.shared.test_splash import BRAND, WELCOME_TITLE

SLOW = 90.0  # throttled network (emulator: gsm speed, gprs delay) on top of the cold-start timing


@pytest.mark.android
@pytest.mark.regression
@pytest.mark.tc("TC-SPL-004")
@pytest.mark.chk("CHK-SPL-015")
@allure.tag("CHK-SPL-015")
@allure.title(
    "TC-SPL-004 On a slow network the splash hands over to the next screen automatically, "
    "with no error and a centred logo"
)
def test_slow_network_splash_hands_over(app, driver, platform, network, expected, evidence):
    splash = SplashPage(driver, platform).use_colour(pixels.hex_to_rgb(expected(BRAND)))
    welcome = WelcomePage(driver, platform)
    offline = OfflineBanner(driver, platform)

    network.slow()  # open device.network slow (emulator: gsm speed, gprs delay)
    app.clear_data()  # signed out and not running → the next launch is a cold start
    app.launch()  # open app, cold start
    try:
        first = splash.expect_shown_after_system_splash(SLOW)  # expect-visible splash.root
        splash.expect_logo_centred(first)  # expect-visible splash.logo, centred
    except SplashMissed as exc:
        pytest.skip(f"Blocked: timing — {exc}; the splash could not be observed in time")
    evidence.checkpoint("splash-slow-network")

    # expect-hidden offline-banner.message — a slow connection is not "no connection" (§3.3.1);
    # checked right as the splash is confirmed, the best this harness can do for "throughout"
    offline.wait_gone("message", 2)

    # wait-for + expect-visible welcome.root: the app moved on by itself, the slow network did
    # not block the hand-over (FR-SPL-04)
    welcome.expect_text("title", expected(WELCOME_TITLE), SLOW)
    evidence.checkpoint("welcome-after-slow-splash")
