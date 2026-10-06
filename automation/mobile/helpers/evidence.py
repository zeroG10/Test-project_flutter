"""Evidence for the report: named checkpoint screenshots and per-test screen video.

Policy (README "Evidence"): not everything is captured.
* Screenshot + page source on every failure — conftest.py, automatic.
* Named screenshots only at the key moments a test chooses (``evidence.checkpoint(...)``) —
  the happy-flow pictures the summary page shows.
* Video is recorded for every test (a failure is not known in advance) and KEPT only for
  failed or Blocked tests and tests marked ``e2e`` (``EVIDENCE_VIDEO=auto``; ``all`` / ``off``).

Evidence never decides a verdict: a recorder that cannot start is logged as a step and the
test goes on — only its assertions decide Passed / Failed.
"""

import base64
import contextlib

import allure
from appium.webdriver.webdriver import WebDriver

from config.settings import normalize_platform

# iOS: ffmpeg over the WDA MJPEG stream. H.264 + yuv420p plays in browsers and Allure;
# the driver default (mjpeg) does not. Half-size width keeps attachments small.
IOS_RECORDING = {
    "videoType": "libx264",
    "pixelFormat": "yuv420p",
    "videoFps": 10,
    "videoScale": "590:-2",
    "timeLimit": 1800,
    "forceRestart": True,
}
# Android: screenrecord; the driver chains 3-minute chunks up to timeLimit.
ANDROID_RECORDING = {"timeLimit": 1800, "bitRate": 2_000_000, "forceRestart": True}


class Evidence:
    """Checkpoint screenshots of one test, numbered in the order they were taken."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._count = 0

    def checkpoint(self, name: str) -> None:
        """Attach a screenshot named ``NN · name`` (e.g. ``02 · otp-screen``)."""
        self._count += 1
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=f"{self._count:02d} · {name}",
            attachment_type=allure.attachment_type.PNG,
        )


class ScreenRecorder:
    def __init__(self, driver: WebDriver, platform: str):
        self.driver = driver
        self.platform = normalize_platform(platform)
        self.running = False

    def start(self) -> None:
        options = IOS_RECORDING if self.platform == "ios" else ANDROID_RECORDING
        try:
            self.driver.start_recording_screen(**options)
            self.running = True
        except Exception as exc:  # evidence is best-effort; the verdict is not affected
            with allure.step(f"video not recorded: {type(exc).__name__}: {exc}"):
                pass

    def stop(self, keep: bool, name: str = "screen-video") -> None:
        """Stop recording; attach the MP4 when ``keep``. Always stops a running recorder."""
        if not self.running:
            return
        self.running = False
        with contextlib.suppress(Exception):
            payload = self.driver.stop_recording_screen()
            if keep and payload:
                allure.attach(
                    base64.b64decode(payload),
                    name=name,
                    attachment_type=allure.attachment_type.MP4,
                )
