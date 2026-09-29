"""The "Submit deliverables" dialog and what a submission shows (module 07, recon 11).

The submission's states are brief ("Submitting deliverables" ~0.3–3 s, "Successful" 1.5 s, the
snackbar ~4 s), so ``watch_submission`` reads the page source many times a second from the tap on
Submit until a message has stayed on screen for ``settle`` seconds, and records everything it saw.
"""

import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import UTC, datetime

import allure

from helpers.device import platform_of
from pages.base_page import BasePage, page_nodes
from screens.job_details_map import MESSAGE_MIN_Y, SUBMIT_STATES
from screens.submit_dialog_map import SUBMIT_DIALOG

SUBMIT_WAIT = 30.0  # seconds a submission may take to show its result (recon 11: 0.5–3 s)
SETTLE = 2.0  # seconds watched after the first message ("Successful" follows a success message)
# Android: the snackbar is a View at the bottom — y 2127 px of 2400 in recon A1 (details scroll
# area ends there); MESSAGE_MIN_Y of the map is in iOS points.
MESSAGE_MIN_Y_ANDROID = 2100


@dataclass
class Submission:
    """What the job's details showed from the tap on Submit until the result settled."""

    tapped_at: datetime  # UTC, just before the tap
    submitting_disabled: bool = False  # "Submitting deliverables" seen, and disabled
    submitting_enabled: bool = False  # "Submitting deliverables" seen enabled — must stay False
    successful: bool = False
    check_out: bool = False
    retry: bool = False
    messages: list[str] = field(default_factory=list)  # snackbar texts, in order

    def summary(self) -> str:
        return (
            f"tapped at {self.tapped_at:%H:%M:%S.%f} UTC; submitting (disabled) "
            f"{self.submitting_disabled}; submitting enabled {self.submitting_enabled}; "
            f"successful {self.successful}; check out {self.check_out}; retry {self.retry}; "
            f"messages {self.messages}"
        )


def _observe_android(source: str, seen: Submission) -> None:
    for n in page_nodes(source, "android"):
        if not n.visible:
            continue
        if n.kind == "Button" and n.label == SUBMIT_STATES["submitting"]:
            if n.enabled:
                seen.submitting_enabled = True
            else:
                seen.submitting_disabled = True
        elif n.kind == "Button" and n.label == SUBMIT_STATES["successful"]:
            seen.successful = True
        elif n.kind == "Button" and n.label == SUBMIT_STATES["check-out"]:
            seen.check_out = True
        elif n.kind == "Button" and n.label == SUBMIT_STATES["retry"]:
            seen.retry = True
        elif (
            n.kind == "View"
            and n.label
            and n.y > MESSAGE_MIN_Y_ANDROID
            and n.label not in seen.messages
        ):
            seen.messages.append(n.label)


def observe(source: str, seen: Submission, platform: str = "ios") -> None:
    """Add what one page source shows to ``seen``."""
    if platform == "android":
        _observe_android(source, seen)
        return
    for node in ET.fromstring(source).iter():
        attrs = node.attrib
        if attrs.get("visible") != "true":
            continue
        kind, name = node.tag.replace("XCUIElementType", ""), attrs.get("name") or ""
        if kind == "Button" and name == SUBMIT_STATES["submitting"]:
            if attrs.get("enabled") == "false":
                seen.submitting_disabled = True
            else:
                seen.submitting_enabled = True
        elif kind == "Button" and name == SUBMIT_STATES["successful"]:
            seen.successful = True
        elif kind == "Button" and name == SUBMIT_STATES["check-out"]:
            seen.check_out = True
        elif kind == "Button" and name == SUBMIT_STATES["retry"]:
            seen.retry = True
        elif (
            kind == "Other"
            and name
            and int(attrs.get("y", "0")) > MESSAGE_MIN_Y
            and name not in seen.messages
        ):
            seen.messages.append(name)


def snackbars(source: str, platform: str = "ios") -> list[str]:
    """The names of the snackbars on screen (a visible Other at the bottom)."""
    if platform == "android":
        return [
            n.label
            for n in page_nodes(source, platform)
            if n.kind == "View" and n.visible and n.label and n.y > MESSAGE_MIN_Y_ANDROID
        ]
    return [
        node.attrib.get("name", "")
        for node in ET.fromstring(source).iter()
        if node.tag.endswith("Other")
        and node.attrib.get("visible") == "true"
        and node.attrib.get("name")
        and int(node.attrib.get("y", "0")) > MESSAGE_MIN_Y
    ]


class SubmitDialog(BasePage):
    screen = SUBMIT_DIALOG

    def expect_modal(self, hidden_name: str) -> None:
        """The dialog's layer covers the whole window and ``hidden_name`` (the details' header)
        is out of the tree while the dialog is open."""
        with allure.step("expect submit-dialog.layer over the whole window, the details hidden"):
            size, layer = self.driver.get_window_size(), self.rect("layer")
            assert layer["width"] >= size["width"] and layer["height"] >= size["height"], (
                f"layer {layer}, window {size}"
            )
            shown = [n.label for n in self.nodes() if n.visible]
            assert hidden_name not in shown, f"{hidden_name!r} still reachable under the dialog"

    def submit(self, settle: float = SETTLE) -> Submission:
        """Tap Submit, then watch the details until the result settles. A short ``settle`` leaves
        time to act on the snackbar (its Retry lives ~4 s)."""
        with allure.step("tap submit-dialog.submit and watch the submission"):
            seen = Submission(tapped_at=datetime.now(UTC))
            self.tap("submit")
            watch_submission(self.driver, seen, settle=settle)
            allure.attach(seen.summary(), name="what the submission showed",
                          attachment_type=allure.attachment_type.TEXT)  # fmt: skip
            return seen


def watch_submission(driver, seen: Submission, timeout: float = SUBMIT_WAIT,
                     settle: float = SETTLE) -> Submission:  # fmt: skip
    """Read the page source until a message has been on screen for ``settle`` seconds."""
    end, first_message = time.monotonic() + timeout, None
    platform = platform_of(driver)
    while time.monotonic() < end:
        observe(driver.page_source, seen, platform)
        if seen.messages and first_message is None:
            first_message = time.monotonic()
        if first_message is not None and time.monotonic() - first_message >= settle:
            break
    return seen
