"""Android-only device operations over adb (Android stage; recon A1 —
qa/shared/recon-2026-09-29-android.md).

Everything that changes the device is undone by its context manager, also on failure.

* ``gps_feed`` — the emulator GPS reports a point once per ``adb emu geo fix``; the app asks for a
  FRESH fix at check-in and, without one in time, shows "Enter location manually". The feed
  repeats the fix every second while a step runs. These fixes are NOT mocked for the app (unlike
  the iOS simulator), so check-in works without the app's debug switch (owner, Q-CHIO-A1).
* ``mock_location`` — a real mocked location (Appium Settings as the mock provider): the app's
  guard shows "Location could not be trusted". The mock permission is restored afterwards.
* ``offline`` — Wi-Fi and mobile data off, restored in ``finally``.
* ``push_media`` — photos into the gallery (adb push + media scan), the ``simctl addmedia`` twin.
* ``send_sms`` / ``app_links_allowed`` — a job link as an SMS in Google Messages and the user's
  "open supported links" choice for the app (owner, Q-ORDL-A1: model the SMS where possible).
"""

import contextlib
import subprocess
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import allure

APPIUM_SETTINGS = "io.appium.settings"
DEV_LINK_DOMAIN = "copsfieldservices.dev.concerttech.com"


class Adb:
    """adb bound to one device (the session's ``udid``)."""

    def __init__(self, udid: str | None):
        self.udid = udid

    def run(self, *args: str, timeout: float = 60, check: bool = True) -> str:
        cmd = ["adb", *(["-s", self.udid] if self.udid else []), *args]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if check and out.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} → {out.returncode}: {out.stderr.strip()[:300]}")
        return (out.stdout + out.stderr).strip()

    def shell(self, command: str, **kw) -> str:
        return self.run("shell", command, **kw)

    @classmethod
    def of(cls, driver) -> "Adb":
        caps = driver.capabilities
        return cls(caps.get("udid") or caps.get("appium:udid") or caps.get("deviceUDID"))

    # --- permissions ---------------------------------------------------------------------

    def grant(self, package: str, *permissions: str) -> None:
        for p in permissions:
            self.shell(f"pm grant {package} {p}")

    def revoke(self, package: str, *permissions: str) -> None:
        for p in permissions:
            self.shell(f"pm revoke {package} {p}")

    def granted(self, package: str, permission: str) -> bool:
        dump = self.shell(f"dumpsys package {package}", timeout=60)
        return f"{permission}: granted=true" in dump

    # --- location -------------------------------------------------------------------------

    def geo_fix(self, latitude: float, longitude: float) -> None:
        self.run("emu", "geo", "fix", f"{longitude:.6f}", f"{latitude:.6f}")

    @contextlib.contextmanager
    def gps_feed(self, latitude: float, longitude: float, every: float = 1.0) -> Iterator[None]:
        """Keep the emulator's GPS at a point while the block runs (a fix every ``every`` s)."""
        stop = threading.Event()

        def feed() -> None:
            while not stop.is_set():
                with contextlib.suppress(Exception):
                    self.geo_fix(latitude, longitude)
                stop.wait(every)

        with allure.step(f"device GPS feed → {latitude:.6f}, {longitude:.6f}"):
            self.geo_fix(latitude, longitude)
            thread = threading.Thread(target=feed, name="gps-feed", daemon=True)
            thread.start()
        try:
            yield
        finally:
            stop.set()
            thread.join(timeout=5)

    @contextlib.contextmanager
    def mock_location(self, latitude: float, longitude: float) -> Iterator[None]:
        """A MOCKED location (the app must refuse it): Appium Settings is made the mock
        provider for the block; its mock permission goes back to default afterwards."""
        where = f"{latitude:.6f}, {longitude:.6f}"
        with allure.step(f"device: MOCK location {where} (Appium Settings)"):
            self.shell(f"appops set {APPIUM_SETTINGS} android:mock_location allow")
            self.shell(
                f"am start-foreground-service --user 0 -n {APPIUM_SETTINGS}/.LocationService "
                f"--es longitude {longitude:.6f} --es latitude {latitude:.6f} --es altitude 20"
            )
            time.sleep(2)
        try:
            yield
        finally:
            with contextlib.suppress(Exception):
                self.shell(f"am stopservice {APPIUM_SETTINGS}/.LocationService")
            with contextlib.suppress(Exception):
                self.shell(f"appops set {APPIUM_SETTINGS} android:mock_location default")

    # --- network (offline checks, step 5) -------------------------------------------------

    @contextlib.contextmanager
    def offline(self) -> Iterator[None]:
        """Wi-Fi and mobile data off for the block; both back on in ``finally``."""
        with allure.step("device: network OFF (wifi + data)"):
            self.shell("svc wifi disable")
            self.shell("svc data disable")
        try:
            yield
        finally:
            with allure.step("device: network back ON"):
                self.shell("svc wifi enable", check=False)
                self.shell("svc data enable", check=False)

    # --- gallery ----------------------------------------------------------------------------

    def push_media(self, *paths: Path) -> None:
        """Photos into /sdcard/Pictures and the media store (the picker orders by date taken)."""
        for p in paths:
            target = f"/sdcard/Pictures/{p.name}"
            self.run("push", str(p), target)
            self.shell(
                f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{target}"
            )

    # --- SMS and links (module 03, Q-ORDL-A1) ---------------------------------------------

    def send_sms(self, sender: str, text: str) -> None:
        """An incoming SMS on the emulator (the carrier's side); it lands in Google Messages."""
        with allure.step(f"device: incoming SMS from {sender}"):
            self.run("emu", "sms", "send", sender, text)

    @contextlib.contextmanager
    def app_links_allowed(self, package: str, domain: str = DEV_LINK_DOMAIN) -> Iterator[None]:
        """The user's "open supported links" choice for ``domain``: our debug build is signed with
        a local key, so Android's own App Link verification fails (recon A1) and the link would
        open in Chrome. Restored in ``finally``."""
        with allure.step(f"device: links of {domain} open in the app (user selection)"):
            self.shell(
                f"pm set-app-links-user-selection --user 0 --package {package} true {domain}"
            )
        try:
            yield
        finally:
            with contextlib.suppress(Exception):
                self.shell(
                    f"pm set-app-links-user-selection --user 0 --package {package} false {domain}"
                )

    # --- system notifications ---------------------------------------------------------------

    @contextlib.contextmanager
    def heads_up_off(self) -> Iterator[None]:
        """No heads-up pop-ups for the block (notifications still land in the shade); the old
        value comes back afterwards. A job created through the API pushes "New job assigned",
        and its pop-up lies over the app bar for seconds — a tap on the calendar toggle landed on
        it (module 01+03 Android run 4, TC-ORDL-015). The iOS simulator shows no such pop-up."""
        key = "heads_up_notifications_enabled"
        before = self.shell(f"settings get global {key}", check=False).strip()
        self.shell(f"settings put global {key} 0")
        try:
            yield
        finally:
            with contextlib.suppress(Exception):
                if before in ("0", "1"):
                    self.shell(f"settings put global {key} {before}")
                else:
                    self.shell(f"settings delete global {key}")

    # --- app state ------------------------------------------------------------------------

    def run_as(self, package: str, command: str) -> str:
        """A command in the app's sandbox (debuggable build only — ours is debug)."""
        return self.shell(f"run-as {package} {command}")

    def anr_on_screen(self) -> bool:
        """Whether the system "… isn't responding" dialog is up (an emulator starved of CPU —
        recon A1, Fable's analysis: environment, Blocked, never Failed)."""
        out = self.shell("dumpsys window windows", check=False, timeout=20)
        return "Application Not Responding" in out
