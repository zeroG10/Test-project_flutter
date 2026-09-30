"""Splash — behaviour over screens/splash_map.py (module 01-splash).

The splash has no labelled element (recon 4): "the splash is shown" is decided by the pixels of a
screenshot — the brand colour fills the screen (Figma `Spalsh` 2451:82537: #782A2A) — and the logo
by the centre of the light pixels on it (helpers/pixels.py). The tree is used for the one thing it
can say here: no text, button or field exists while the splash is up.

A check that can no longer be observed because the splash has already gone raises
``SplashMissed`` — the test turns it into Blocked (timing), never into Passed.
"""

import time
import xml.etree.ElementTree as ET

import allure

from config.settings import settings
from helpers import pixels, waits
from pages.base_page import BasePage
from screens.splash_map import SPLASH
from screens.welcome_map import WELCOME

SPLASH_SHARE = 0.9  # recon 4: 0.998 of the screen is the brand colour on every splash frame
LOGO_TOLERANCE = 0.02  # test-case convention: centred within 2 % of the screen
LOGO_TIMEOUT = 20.0  # debug build: the logo appears ~8 s after launch (recon 4)
# Android: the system splash lasts until Flutter draws — the first brand frame came after 4.0 s,
# 5.6 s, over 10 s (module 01+03 Android runs 1–3, 2026-09-29); a cold debug start takes over 30 s
# on this host (LANDING_TIMEOUT_ANDROID). The wait ends at the first brand frame.
SYSTEM_SPLASH_TIMEOUT_ANDROID = 60.0


class SplashMissed(RuntimeError):
    """The splash was already gone when a splash-only check was due."""


class SplashPage(BasePage):
    screen = SPLASH

    def _frame(self) -> tuple[bytes, float]:
        png = self.driver.get_screenshot_as_png()
        return png, pixels.colour_share(png, self.rgb)

    def use_colour(self, rgb: tuple[int, int, int]) -> "SplashPage":
        self.rgb = rgb
        return self

    def expect_shown(self, label: str = "splash frame") -> bytes:
        """The current screenshot is the splash: ≥ 90 % brand colour."""
        png, share = self._frame()
        allure.attach(png, name=f"{label} (brand colour {share:.3f})",
                      attachment_type=allure.attachment_type.PNG)  # fmt: skip
        if share < SPLASH_SHARE:
            raise SplashMissed(f"{label}: brand colour covers {share:.3f} of the screen")
        return png

    def expect_shown_after_system_splash(
        self, timeout: float = SYSTEM_SPLASH_TIMEOUT_ANDROID
    ) -> bytes:
        """Android 12+ first shows the SYSTEM splash (white, the app icon, ~3 s — recon A1), then
        the app's own brand-colour splash (owner, Q-SPL-A1: the check is the brand splash after
        the system one). Waits for the first brand frame; iOS: the first captured frame."""
        if self.platform != "android":
            return self.expect_shown("first frame after launch")
        start = time.monotonic()
        while True:
            png, share = self._frame()
            if share >= SPLASH_SHARE:
                waited = time.monotonic() - start
                allure.attach(png, name=f"first brand-colour frame after {waited:.1f}s of the "
                              f"system splash (brand colour {share:.3f})",
                              attachment_type=allure.attachment_type.PNG)  # fmt: skip
                return png
            if time.monotonic() - start > timeout:
                allure.attach(png, name=f"no brand-colour frame within {timeout:.0f}s "
                              f"(brand colour {share:.3f})",
                              attachment_type=allure.attachment_type.PNG)  # fmt: skip
                raise SplashMissed(f"no brand-colour frame within {timeout:.0f}s of the launch")
            time.sleep(0.2)

    def expect_no_interactive_elements(self) -> None:
        """No text, button, link, field or switch in the tree — and the splash still on screen
        afterwards, so the tree was read during the splash (iOS)."""
        with allure.step("expect no interactive element in the tree during the splash"):
            if self.platform == "android":
                self._expect_bare_tree_android()
                return
            count = self.count_visible("interactive")
            self.expect_shown("splash after the tree read")
            assert count == 0, f"{count} text / button / field element(s) during the splash"

    def _expect_bare_tree_android(self) -> None:
        """Android: the tree itself proves when it was read. The brand splash is up for about a
        second after the system splash on this host — gone before a screenshot after the read
        (module 01+03 Android run 5 and the check after it) — but the splash has no text at all:
        a tree that holds the Welcome title was read after it (SplashMissed → Blocked), and any
        other labelled or clickable node of the app is on the splash (a failure)."""
        package = settings.app_id("android")
        nodes = [
            n.attrib
            for n in ET.fromstring(self.driver.page_source).iter()
            if n.attrib.get("package") == package
        ]
        labels = [a.get("content-desc") or a.get("text") for a in nodes]
        labels = [label for label in labels if label]
        clickable = sum(1 for a in nodes if a.get("clickable") == "true")
        allure.attach("\n".join(labels) or "(none)", name="labelled nodes of the app in the tree",
                      attachment_type=allure.attachment_type.TEXT)  # fmt: skip
        if WELCOME.locator("android", "root")[1] in labels:
            raise SplashMissed("the tree was read after the splash (the Welcome title is in it)")
        assert not labels and not clickable, (
            f"{len(labels)} labelled / {clickable} clickable element(s) during the splash: "
            f"{labels[:5]}"
        )

    def tap_centre(self) -> None:
        size = self.driver.get_window_size()
        with allure.step("tap the centre of the splash"):
            self.driver.tap([(size["width"] // 2, size["height"] // 2)])

    def expect_logo_centred(
        self, frame: bytes | None = None, tolerance: float = LOGO_TOLERANCE
    ) -> None:
        """Wait for the logo (light pixels on the brand colour), then check its centre.

        ``frame``: a screenshot already proven to be the splash (``expect_shown``) — judged first,
        so a splash that ends a moment later is still judged (Android: the logo is drawn from the
        first brand frame; module 01+03 Android run 1 took a new screenshot after the splash had
        gone). Without a logo in it, the page waits for one as before (iOS draws it late)."""
        width = self.driver.get_window_size()["width"]
        seen: list[tuple[float, float]] = []
        # Android works in pixels: skip the status bar with the DEBUG ribbon (~150 px) and the
        # gesture bar (last ~65 px) — their glyphs are light too (recon A1 frames).
        skips = (300, 100) if self.platform == "android" else ()

        def logo_in(png: bytes) -> bool:
            offset = pixels.light_blob_offset(png, width, *skips)
            if offset is None:
                return False
            seen.append(offset)
            allure.attach(png, name="splash with the logo",
                          attachment_type=allure.attachment_type.PNG)  # fmt: skip
            return True

        def logo_drawn(_driver) -> bool:
            png, share = self._frame()
            if share < SPLASH_SHARE - 0.1:  # the logo itself takes ~2 % of the screen
                raise SplashMissed(f"splash gone before the logo appeared (brand {share:.3f})")
            return logo_in(png)

        with allure.step("expect the logo centred on the splash"):
            if frame is None or not logo_in(frame):
                waits.wait_until(self.driver, logo_drawn, LOGO_TIMEOUT, "the logo never appeared")
            dx, dy = seen[-1]
            assert abs(dx) <= tolerance and abs(dy) <= tolerance, (
                f"logo centre off by {dx:+.1%} / {dy:+.1%} of the screen "
                f"(tolerance {tolerance:.0%})"
            )
