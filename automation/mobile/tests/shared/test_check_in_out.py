"""Check-in / Check-out (module 05) — TC-CHIO-001…009.

Source of every step and expectation: qa/mobile/05-check-in-out/check-in-out-test-cases.md
(recon 6 / 6b / 6c; D-CHIO-1…5 accepted by the owner 2026-09-24). Data: fixtures/check.py — 8 jobs
through the API, removed after the module; device location and permission set per test.

The iOS simulator's location is always refused as mocked (recon 6 / 6b), so every test that
completes a location step runs with the app's own mock-location switch ON (``on_site`` /
``away``; owner, Q-CHIO-5) — and TC-CHIO-008 proves the guard with it OFF (``guarded``). Manual
location entry is unreachable on the simulator; the owner verified it on a real device.

The stored result is read back through ``GET /job/{id}``. Order of the functions = order of the
run: TC-CHIO-008 → 009 use the job `guard`; TC-CHIO-006 reads `far` (after 003) and
`kept` (after 005). Every expected value goes through ``expected(...)``.
"""

from datetime import UTC, datetime

import allure
import pytest

from helpers import waits
from pages.confirm_check_page import ConfirmCheckPage
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.location_dialogs_page import (
    LocationDisabledDialog,
    LocationPromptPage,
    MockLocationDialog,
    NotAtSiteDialog,
    system_alerts,
)
from screens.location_dialogs_map import MOCK_LOCATION_MESSAGE, NOT_AT_SITE_MESSAGE

SERVER = 20.0
RECORD_WINDOW = 60  # seconds between the tap on Confirm and the stored date (recon 6c: 0.6–0.7 s)
SETTINGS_APPS = {"ios": "com.apple.Preferences", "android": "com.android.settings"}

CHECK_IN = ("Confirm check in", "Check in and start", "Confirm you are on site to begin the job.")
CHECK_OUT = (
    "Confirm check out",
    "Check out and finish",
    "Confirm you are ready to finish the job.",
)


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        confirm = ConfirmCheckPage(driver, platform)
        not_at_site = NotAtSiteDialog(driver, platform)
        mock = MockLocationDialog(driver, platform)
        prompt = LocationPromptPage(driver, platform)
        disabled = LocationDisabledDialog(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    pages.jobs.pull_to_refresh()
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def server_job(api, job) -> dict:
    return api.job(job.id)


def expect_record(record: dict, where: tuple[float, float], expected) -> None:
    """A GPS record of check-in / check-out: method gps, the device's coordinates, an accuracy."""
    with allure.step(f"expect a GPS record at {where}"):
        assert record.get("method") == expected("gps"), f"record: {record}"
        coords = record.get("coordinates") or {}
        got = (float(coords.get("latitude", "nan")), float(coords.get("longitude", "nan")))
        assert abs(got[0] - where[0]) < 1e-5 and abs(got[1] - where[1]) < 1e-5, f"record: {record}"
        assert record.get("horizontalAccuracyM"), f"no accuracy in the record: {record}"


def expect_recent(stamp: str | None, tapped: datetime, what: str) -> None:
    with allure.step(f"expect {what} within {RECORD_WINDOW}s of the tap"):
        assert stamp, f"no {what} stored"
        stored = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        delta = abs((stored - tapped).total_seconds())
        assert delta <= RECORD_WINDOW, (
            f"{what} {stamp} is {delta:.1f}s from the tap {tapped:%H:%M:%S}"
        )


# --------------------------------------------------------------------------------------
# The guard first (switch OFF), then the flows with the switch ON
# --------------------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-008")
@pytest.mark.chk("CHK-CHIO-041")
@allure.tag("CHK-CHIO-041")
@allure.title(
    "TC-CHIO-008 Without the switch, a simulated location is refused with 'Location could not "
    "be trusted' and the job stays New"
)
def test_mock_location_refused(
    check_seed, guarded, ui_login, field_services_api, pages, expected, evidence
):
    job = check_seed["guard"]
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-in")
        pages.mock.expect_text("title", expected("Location could not be trusted"), SERVER)
        pages.mock.expect_text("message", expected(MOCK_LOCATION_MESSAGE))
        evidence.checkpoint("mock-location-refused")
        pages.mock.tap("got-it")
    pages.details.expect_enabled("check-in", timeout=SERVER)
    status = server_job(field_services_api, job).get("statusType")
    assert status == expected("new"), f"job status on the server: {status!r}"


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-009")
@pytest.mark.chk("CHK-ORDD-028")
@allure.tag("CHK-ORDD-028")
@allure.title("TC-CHIO-009 After refusing location, 'Go to settings' opens the device settings")
def test_go_to_settings(check_seed, guarded, ui_login, driver, platform, pages, expected):
    job = check_seed["guard"]
    ui_login.reset_location_permission()  # "not determined" → the system prompt appears
    ui_login.launch()
    pages.jobs.assert_open(SERVER)
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-in")
        with system_alerts(driver, platform):
            pages.prompt.visible("title", SERVER)
            pages.prompt.tap("dont-allow")
        pages.disabled.expect_text("title", expected("Location disabled"), SERVER)
        pages.disabled.tap("go-to-settings")
    with allure.step("expect the Settings app in the foreground"):
        settings_app = expected(SETTINGS_APPS[platform])
        waits.wait_until(driver, lambda _d: ui_login.in_foreground(settings_app), SERVER,
                         "the Settings app did not open")  # fmt: skip
    ui_login.launch()
    ui_login.grant_location_permission()


CHECK_IN_CHKS = (
    "CHK-CHIO-001", "CHK-CHIO-004", "CHK-CHIO-005", "CHK-CHIO-006", "CHK-CHIO-010",
    "CHK-CHIO-011", "CHK-CHIO-012", "CHK-CHIO-014", "CHK-CHIO-022", "CHK-CHIO-035",
    "CHK-CHIO-036", "CHK-CHIO-037", "CHK-ORDD-030", "CHK-ORDD-044", "CHK-ORDD-045",
    "CHK-ORDD-046", "CHK-ORDD-047",
)  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-001")
@pytest.mark.chk(*CHECK_IN_CHKS)
@allure.tag(*CHECK_IN_CHKS)
@allure.title(
    "TC-CHIO-001 On site, check-in shows the confirmation screen, and Confirm starts the job "
    "with a GPS record"
)
def test_check_in_on_site(
    check_seed, on_site, ui_login, field_services_api, pages, expected, evidence
):
    job = check_seed["gps"]
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-in")
        pages.confirm.expect_screen(*(expected(t) for t in CHECK_IN), timeout=SERVER)
        evidence.checkpoint("confirm-check-in")
        tapped = datetime.now(UTC)
        pages.confirm.tap("confirm")
    pages.details.expect_field("status", expected("In progress"), SERVER)
    stored = server_job(field_services_api, job)
    assert stored.get("statusType") == expected("in_progress"), (
        f"status: {stored.get('statusType')}"
    )
    expect_recent(stored.get("checkInDate"), tapped, "checkInDate")
    expect_record(stored.get("userLocation") or {}, on_site, expected)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-002")
@pytest.mark.chk("CHK-CHIO-003", "CHK-CHIO-007", "CHK-CHIO-009")
@allure.tag("CHK-CHIO-003", "CHK-CHIO-007", "CHK-CHIO-009")
@allure.title("TC-CHIO-002 X and Cancel on the check-in confirmation leave the job New")
def test_check_in_cancelled(check_seed, on_site, ui_login, field_services_api, pages, expected):
    job = check_seed["cancel"]
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-in")
        pages.confirm.visible("title", SERVER, text=expected(CHECK_IN[0]))
        pages.confirm.tap("close")
        pages.details.expect_enabled("check-in", timeout=SERVER)
        pages.details.tap("check-in")
        pages.confirm.visible("title", SERVER, text=expected(CHECK_IN[0]))
        pages.confirm.tap("cancel")
    pages.details.expect_field("status", expected("New"), SERVER)
    stored = server_job(field_services_api, job)
    assert stored.get("statusType") == "new" and not stored.get("checkInDate"), f"stored: {stored}"


AWAY_CHKS = ("CHK-ORDD-031", "CHK-ORDD-032", "CHK-ORDD-033", "CHK-ORDD-034", "CHK-ORDD-035")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-003")
@pytest.mark.chk(*AWAY_CHKS)
@allure.tag(*AWAY_CHKS)
@allure.title(
    "TC-CHIO-003 Away from the site, check-in is stopped with 'You are not at the job site'; "
    "Got it and Cancel leave the job New"
)
def test_check_in_away(check_seed, away, ui_login, field_services_api, pages, expected, evidence):
    job, alert = check_seed["far"], pages.not_at_site
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-in")
        alert.expect_text("title", expected("You are not at the job site"), SERVER)
        alert.expect_text("message", expected(NOT_AT_SITE_MESSAGE))
        evidence.checkpoint("not-at-the-job-site")
        alert.tap("got-it")
        pages.details.expect_field("status", expected("New"), SERVER)
        pages.details.tap("check-in")
        alert.visible("title", SERVER)
        alert.tap("cancel")
    pages.details.expect_enabled("check-in", timeout=SERVER)
    status = server_job(field_services_api, job).get("statusType")
    assert status == expected("new"), f"job status on the server: {status!r}"


CHECK_OUT_CHKS = (
    "CHK-CHIO-002", "CHK-CHIO-016", "CHK-CHIO-017", "CHK-CHIO-018", "CHK-CHIO-020", "CHK-CHIO-023",
)  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-004")
@pytest.mark.chk(*CHECK_OUT_CHKS)
@allure.tag(*CHECK_OUT_CHKS)
@allure.title(
    "TC-CHIO-004 On site, check-out from a Submitted job shows its confirmation, and Confirm "
    "completes the job with a GPS record"
)
def test_check_out_on_site(
    check_seed, on_site, ui_login, field_services_api, pages, expected, evidence
):
    job = check_seed["submitted"]
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-out")
        pages.confirm.expect_screen(*(expected(t) for t in CHECK_OUT), timeout=SERVER)
        evidence.checkpoint("confirm-check-out")
        tapped = datetime.now(UTC)
        pages.confirm.tap("confirm")
    pages.jobs.assert_open(SERVER)
    stored = server_job(field_services_api, job)
    assert stored.get("statusType") == expected("completed"), f"status: {stored.get('statusType')}"
    expect_recent(stored.get("checkOutDate"), tapped, "checkOutDate")
    expect_record(stored.get("checkOutLocation") or {}, on_site, expected)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-005")
@pytest.mark.chk("CHK-CHIO-008")
@allure.tag("CHK-CHIO-008")
@allure.title("TC-CHIO-005 Cancel on the check-out confirmation keeps the job Submitted")
def test_check_out_cancelled(check_seed, on_site, ui_login, field_services_api, pages, expected):
    job = check_seed["kept"]
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-out")
        pages.confirm.visible("title", SERVER, text=expected(CHECK_OUT[0]))
        pages.confirm.tap("cancel")
    pages.details.expect_enabled("check-out", timeout=SERVER)
    stored = server_job(field_services_api, job)
    assert stored.get("statusType") == expected("submitted") and not stored.get("checkOutDate"), (
        f"stored: {stored.get('statusType')}, {stored.get('checkOutDate')}"
    )


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-006")
@pytest.mark.chk("CHK-CHIO-040")
@allure.tag("CHK-CHIO-040")
@allure.title(
    "TC-CHIO-006 Each status offers only its own action: New → Check in, In progress → none, "
    "Submitted → Check out"
)
def test_actions_per_status(check_seed, ui_login, pages, expected):
    d = pages.details
    for kind, offered, absent in (
        ("far", "check-in", ("check-out",)),
        ("in_progress", "submit-deliverables", ("check-in", "check-out")),
        ("kept", "check-out", ("check-in",)),
    ):
        job = check_seed[kind]
        open_job(pages, job, expected)
        with allure.step(f"{kind}: {offered} offered, {', '.join(absent)} not"):
            d.visible(offered, SERVER)
            for alias in absent:
                d.wait_gone(alias, 1)
        d.go_back()
        pages.jobs.assert_open(SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-CHIO-007")
@pytest.mark.chk("CHK-CHIO-039")
@allure.tag("CHK-CHIO-039")
@allure.title("TC-CHIO-007 Two quick taps on Confirm start the job once")
def test_confirm_double_tap(check_seed, on_site, ui_login, field_services_api, pages, expected):
    job = check_seed["double"]
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # WDA may press a dialog button
        pages.details.tap("check-in")
        pages.confirm.visible("title", SERVER, text=expected(CHECK_IN[0]))
        pages.confirm.double_tap_confirm()
    pages.details.expect_field("status", expected("In progress"), SERVER)
    pages.details.expect_header(expected(job.title_line), SERVER)
    stored = server_job(field_services_api, job)
    assert stored.get("statusType") == "in_progress", f"status: {stored.get('statusType')}"
    assert stored.get("checkInDate") and (stored.get("userLocation") or {}).get("method"), (
        f"one check-in expected: {stored}"
    )
