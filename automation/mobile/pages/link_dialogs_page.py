"""Job-link dialogs — behaviour over screens/link_dialogs_map.py (module 03).

The mismatch dialog closes by itself ~0.6 s after it appears on the iOS simulator (recon 4, 4 of
4 — iOS simulator testing specific; on a device it stays, owner 2026-09-24). Its texts are
therefore read over its whole short life (``snapshot``): a read taken while it builds up can hold
the title alone (run 3), so every read that contains it adds to one picture of the dialog. If it
closes before that picture is complete, ``DialogMissed`` is raised — Blocked, never Passed.
"""

import time
import xml.etree.ElementTree as ET

import allure

from helpers import waits
from pages.base_page import BasePage, normalized
from screens.link_dialogs_map import LINK_EXPIRED, PHONE_MISMATCH

DIALOG_TITLES = ("Link expired", "Assigned to a different phone number")


def _visible_texts(page_source: str) -> tuple[list[str], list[str]]:
    texts, buttons = [], []
    for node in ET.fromstring(page_source).iter():
        a = node.attrib
        if a.get("visible") != "true" or not a.get("name"):
            continue
        if node.tag == "XCUIElementTypeStaticText":
            texts.append(normalized(a["name"]))
        elif node.tag == "XCUIElementTypeButton":
            buttons.append(normalized(a["name"]))
    return texts, buttons


class LinkExpiredDialog(BasePage):
    screen = LINK_EXPIRED


class DialogMissed(RuntimeError):
    """The dialog closed before a complete read of it was possible."""


class PhoneMismatchDialog(BasePage):
    screen = PHONE_MISMATCH

    def snapshot(self, timeout: float = 15) -> dict[str, list[str]]:
        """Texts and buttons of the dialog, gathered from every page-source read that contains
        it until it holds a title, a message and two buttons (the dialog's structure — the
        texts themselves are the test's to check)."""
        title = DIALOG_TITLES[1]
        found: dict[str, list[str]] = {"texts": [], "buttons": []}
        seen = [False]

        def complete(driver) -> bool:
            source = driver.page_source
            if title not in source:
                if seen[0]:
                    raise DialogMissed(f"the dialog closed after a partial read: {found}")
                return False
            seen[0] = True
            for key, values in zip(("texts", "buttons"), _visible_texts(source), strict=True):
                found[key] += [v for v in values if v not in found[key]]
            return len(found["texts"]) >= 2 and len(found["buttons"]) >= 2

        with allure.step("capture the mismatch dialog (every read while it is up)"):
            waits.wait_until(  # a fast poll: the dialog lives ~0.6 s on the simulator
                self.driver, complete, timeout, "the mismatch dialog did not appear", poll=0.1
            )
        return found


def expect_no_link_dialog(driver, seconds: float = 5) -> None:
    """No link dialog shows up during ``seconds`` — a documented hold (a dialog appears within
    ~1 s of the link, recon 4), polled on the page source."""
    with allure.step(f"expect no link dialog for {seconds}s"):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            source = driver.page_source
            shown = [t for t in DIALOG_TITLES if t in source]
            assert not shown, f"unexpected dialog: {shown}"
