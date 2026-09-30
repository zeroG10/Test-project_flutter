"""Order details (module 04) — TC-ORDD-001…009.

Source of every step and expectation: qa/mobile/04-order-details/order-details-test-cases.md
(D-ORDD-1…9 accepted by the owner 2026-09-24; recon 5 / 5b). Data: fixtures/details.py — 3 of our
own files and 3 jobs through the API, removed after the module (files first).

TC-ORDD-004 (PF phone → dialer) is Blocked on iOS: the simulator has no Phone app (owner,
Q-ORDD-3). TC-ORDD-007 / -008 need the attachments to load in the app — they did not on the
simulator in recon 5b (Q-ORDD-6; they open on the owner's device): the tests decide it by pixels.
The calendar path of CHK-ORDD-001 / -002 is TC-ORDL-008 (test_order_list.py).

Order of the functions = order of the run (plan, Step 12): TC-ORDD-005 (Check in) is the last
test on the job `full` — if the flow ever completed, the job would be In progress. Every expected
value goes through ``expected(...)``.
"""

import allure
import pytest

from fixtures.details import moved, schedule_change
from helpers import waits
from pages.android.system_pages import DialerPage
from pages.attachments_page import AttachmentsPage, PdfViewerPage, PhotoViewerPage
from pages.base_page import normalized
from pages.in_app_browser_page import InAppBrowserPage
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.location_dialogs_page import LocationDisabledDialog, LocationPromptPage, system_alerts
from screens.location_dialogs_map import (
    LOCATION_DISABLED_MESSAGE,
    LOCATION_DISABLED_MESSAGE_ANDROID,
    LOCATION_PROMPT_MESSAGE,
)

SERVER = 20.0
MAPS_PAGE = 40.0  # maps.apple.com loads slowly on the simulator (recon 5: blank at 4 s)


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        attachments = AttachmentsPage(driver, platform)
        pdf = PdfViewerPage(driver, platform)
        photo = PhotoViewerPage(driver, platform)
        browser = InAppBrowserPage(driver, platform)
        prompt = LocationPromptPage(driver, platform)
        disabled = LocationDisabledDialog(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    """The "open a job" convention: pull the list to refresh, tap the job's card."""
    pages.jobs.pull_to_refresh()
    pages.jobs.scroll_to("card", text=job.job_id)
    pages.jobs.tap("card", text=job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def open_attachments(pages, job, expected) -> None:
    open_job(pages, job, expected)
    pages.details.open_attachments()
    pages.attachments.assert_open(SERVER)


DETAILS_CHKS = (
    "CHK-ORDD-001", "CHK-ORDD-002", "CHK-ORDD-003", "CHK-ORDD-004", "CHK-ORDD-005",
    "CHK-ORDD-008", "CHK-ORDD-010", "CHK-ORDD-011", "CHK-ORDD-014", "CHK-ORDD-016",
    "CHK-ORDD-018", "CHK-ORDD-020", "CHK-ORDD-021",
)  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-001")
@pytest.mark.chk(*DETAILS_CHKS)
@allure.tag(*DETAILS_CHKS)
@allure.title(
    "TC-ORDD-001 A New job shows every part of its details and the Check in button; "
    "back returns to the list"
)
def test_new_job_details(details_seed, ui_login, pages, expected, evidence):
    job, pf, d = details_seed["full"], details_seed.pf, pages.details
    open_job(pages, job, expected)
    d.expect_field("status", expected("New"))
    d.expect_field("title-line", expected(job.title_line))
    d.expect_description(expected(job.description))
    d.visible("location-title")
    d.expect_field("address", expected(job.address))
    d.visible("schedule-title")
    d.expect_field("date", expected(job.date_text))
    d.expect_field("time", expected(job.time_text))
    d.visible("pf-title")
    d.expect_field("pf-name", expected(pf["name"]))
    d.visible("pf-phone", text=expected(pf["phone"]))
    d.expect_text("attachments", expected(f"Attachments ({details_seed.attachment_count})"))
    d.expect_check_in_on_screen()
    d.expect_read_only()
    evidence.checkpoint("job-details-full")
    d.go_back()
    pages.jobs.assert_open(SERVER)
    with allure.step("expect the job's card still in the list"):
        assert pages.jobs.card_count(job.job_id) == 1


ATTACHMENTS_CHKS = (
    "CHK-ORDD-019", "CHK-ORDD-051", "CHK-ORDD-052", "CHK-ORDD-053", "CHK-ORDD-054",
    "CHK-ORDD-055", "CHK-ORDD-057", "CHK-ORDD-059", "CHK-ORDD-060", "CHK-ORDD-061",
)  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-006")
@pytest.mark.chk(*ATTACHMENTS_CHKS)
@allure.tag(*ATTACHMENTS_CHKS)
@allure.title(
    "TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; "
    "Photos switches the tab"
)
def test_attachments_screen(details_seed, ui_login, pages, expected, evidence):
    job, a = details_seed["full"], pages.attachments
    docs = [name for _, name in details_seed.documents]
    open_attachments(pages, job, expected)
    a.visible("title")
    a.visible("back")
    with allure.step("expect two tabs: Documents, then Photos"):
        names = [name.split("\n")[0] for name in a.tab_names()]
        assert names == [expected("Documents"), expected("Photos")], f"tabs: {a.tab_names()}"
    a.expect_selected_tab(expected("Documents"))
    for name in docs:
        a.visible("document", SERVER, text=expected(name))
    evidence.checkpoint("attachments-documents")
    a.open_tab("Photos")
    a.wait_gone("document", 2, text=docs[0])
    a.open_tab("Documents")
    a.visible("document", SERVER, text=docs[0])
    a.tap("back")
    pages.details.expect_header(expected(job.title_line), SERVER)


PDF_CHKS = ("CHK-ORDD-062", "CHK-ORDD-063", "CHK-ORDD-066", "CHK-ORDD-067", "CHK-ORDD-068")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-007")
@pytest.mark.chk(*PDF_CHKS, "CHK-ORDD-087")
@allure.tag(*PDF_CHKS, "CHK-ORDD-087")
@allure.title(
    "TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, "
    "and X returns to Documents"
)
def test_pdf_viewer(details_seed, ui_login, pages, expected, evidence):
    job, a, pdf = details_seed["full"], pages.attachments, pages.pdf
    doc = details_seed.documents[0][1]
    open_attachments(pages, job, expected)
    a.tap("document", SERVER, text=doc)
    pdf.visible("title", SERVER, text=expected(doc))
    try:
        pdf.expect_page_drawn()
    finally:
        evidence.checkpoint("pdf-viewer")
    a.wait_gone("tab", 2, text="Documents")
    pdf.expect_read_only()
    pdf.visible("close")
    pdf.close()
    a.expect_selected_tab(expected("Documents"), SERVER)
    a.visible("document", SERVER, text=doc)


PHOTO_CHKS = (
    "CHK-ORDD-056", "CHK-ORDD-058", "CHK-ORDD-073", "CHK-ORDD-074", "CHK-ORDD-075",
    "CHK-ORDD-076", "CHK-ORDD-079", "CHK-ORDD-080", "CHK-ORDD-087",
)  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-008")
@pytest.mark.chk(*PHOTO_CHKS)
@allure.tag(*PHOTO_CHKS)
@allure.title(
    "TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; "
    "back returns to Photos"
)
def test_photos_grid_and_viewer(details_seed, ui_login, pages, expected, evidence):
    job, a, photo = details_seed["full"], pages.attachments, pages.photo
    open_attachments(pages, job, expected)
    a.open_tab(expected("Photos"))
    try:
        a.expect_thumbnails_drawn(len(details_seed.photos))
    finally:
        evidence.checkpoint("attachments-photos")
    a.tap_cell(0)
    photo.expect_photo_fills_width()
    a.wait_gone("tab", 2, text="Photos")
    photo.visible("back")
    photo.tap("back")
    a.expect_selected_tab(expected("Photos"), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-003")
@pytest.mark.chk("CHK-ORDD-012", "CHK-ORDD-013")
@allure.tag("CHK-ORDD-012", "CHK-ORDD-013")
@allure.title(
    "TC-ORDD-003 'On map' opens the job's location in the in-app browser, and Close returns "
    "to the details"
)
def test_on_map_opens_browser(details_seed, ui_login, pages, expected, evidence):
    job = details_seed["full"]
    open_job(pages, job, expected)
    pages.details.tap("on-map")
    street = job.address.split(", ")[1]  # "QA test site, 350 5th Ave, …" → "350 5th Ave"
    # iOS: the in-app browser on maps.apple.com; Android: Google Maps (D-ORDD-A1)
    pages.browser.expect_map(expected("maps.apple.com"), expected(street), SERVER, MAPS_PAGE)
    evidence.checkpoint("on-map-browser")
    pages.browser.close_map()
    pages.details.expect_header(expected(job.title_line), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-002")
@pytest.mark.chk("CHK-ORDD-015")
@allure.tag("CHK-ORDD-015")
@allure.title(
    "TC-ORDD-002 A schedule change made on the backend appears on the open details after a refresh"
)
def test_schedule_follows_backend(details_seed, ui_login, field_services_api, pages, expected):
    job, d = details_seed["reschedule"], pages.details
    open_job(pages, job, expected)
    d.expect_field("date", expected(job.date_text))
    d.expect_field("time", expected(job.time_text))
    new = moved(job.when)
    with allure.step(f"backend: move the job to {new:%d %b %Y %H:%M}"):
        field_services_api.update_job(job.id, job.job_id, schedule_change(new))
    d.pull_to_refresh()
    d.expect_field("date", expected(f"{new.day} {new:%b %Y}"), SERVER)
    d.expect_field("time", expected(f"{new:%H:%M}"), SERVER)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-009")
@pytest.mark.chk("CHK-ORDD-007")
@allure.tag("CHK-ORDD-007")
@allure.title(
    "TC-ORDD-009 After the details of an unviewed job were opened, the details no longer show "
    "'Updated'"
)
def test_updated_gone_after_viewing(details_seed, ui_login, field_services_api, pages, expected):
    job = details_seed["unviewed"]
    open_job(pages, job, expected)
    pages.details.go_back()
    pages.jobs.assert_open(SERVER)
    with allure.step("expect the server to record the viewing (isViewed = true)"):
        waits.wait_until(
            pages.jobs.driver,
            lambda _d: field_services_api.job(job.id).get("isViewed") is True,
            10,
            "the server did not record the viewing",
        )
    pages.jobs.tap("card", text=job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)
    pages.details.expect_no_updated_banner()


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-005")
# + CHK-CHIO-022, CHK-ORDD-024, -027 (module 05): flow starts; its explanation; refusal
@pytest.mark.chk("CHK-ORDD-022", "CHK-ORDD-024", "CHK-ORDD-027", "CHK-CHIO-022")
@allure.tag("CHK-ORDD-022", "CHK-ORDD-024", "CHK-ORDD-027", "CHK-CHIO-022")
@allure.title(
    "TC-ORDD-005 Check in starts the check-in flow; refusing location and cancelling leaves "
    "the job New"
)
def test_check_in_starts_flow(
    details_seed, ui_login, field_services_api, driver, platform, pages, expected, evidence
):
    job, d = details_seed["full"], pages.details
    ui_login.reset_location_permission()  # "not determined" → the system prompt appears
    ui_login.launch()
    pages.jobs.assert_open(SERVER)
    open_job(pages, job, expected)
    with ui_login.alerts_left_alone():  # the test answers the prompt and the dialog itself
        d.tap("check-in")
        d.wait_checking_in(SERVER)
        with system_alerts(driver, platform):  # the system prompt is readable only inside
            if platform == "android":  # one text in the system's own wording (D-CHIO-A2)
                pages.prompt.expect_text("title", expected("to access this device"), SERVER)
                shown = pages.prompt.label_of(pages.prompt.visible("title"))
                explained = normalized(expected(LOCATION_PROMPT_MESSAGE)) in normalized(shown)
            else:
                pages.prompt.expect_text("title", expected("to use your location"), SERVER)
                pages.prompt.expect_text("message", expected(LOCATION_PROMPT_MESSAGE))
                shown, explained = LOCATION_PROMPT_MESSAGE, True
            evidence.checkpoint("location-prompt")
            pages.prompt.tap("dont-allow")
        if platform == "android":  # the app's dialog after a denial differs (D-CHIO-A3, accepted)
            pages.disabled.expect_text("title", expected("Location access required"), SERVER)
            pages.disabled.expect_text("message", expected(LOCATION_DISABLED_MESSAGE_ANDROID))
        else:
            pages.disabled.expect_text("title", expected("Location disabled"), SERVER)
            pages.disabled.expect_text("message", expected(LOCATION_DISABLED_MESSAGE))
        pages.disabled.tap("cancel")
    d.expect_enabled("check-in", timeout=SERVER)
    d.expect_field("status", expected("New"))
    with allure.step("expect no check-in recorded on the server"):
        status = field_services_api.job(job.id).get("statusType")
        assert status == expected("new"), f"job status on the server: {status!r}"
    # CHK-ORDD-024 last, so that every other step of the flow gets its verdict first
    with allure.step("expect the prompt to explain why the location is needed (CHK-ORDD-024)"):
        assert explained, (
            f"the location prompt shows {shown!r}, without the explanation "
            f"{LOCATION_PROMPT_MESSAGE!r} (Android, Q-ORDD-A4)"
        )


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-ORDD-004")
@pytest.mark.chk("CHK-ORDD-017")
@allure.tag("CHK-ORDD-017")
@allure.title("TC-ORDD-004 Tapping the PF phone opens the dialer with the number")
def test_pf_phone_opens_dialer(details_seed, ui_login, driver, platform, pages, expected):
    if platform == "ios":
        pytest.skip(
            "Blocked: iOS simulator limitation — there is no Phone app, the tap cannot open a "
            "dialer (owner, 2026-09-24, Q-ORDD-3). Runs in full on the Android emulator."
        )
    job, phone = details_seed["full"], details_seed.pf["phone"]
    open_job(pages, job, expected)
    pages.details.tap("pf-phone", text=phone)
    digits = "".join(ch for ch in expected(phone) if ch.isdigit())
    with allure.step(f"expect the dialer with {digits}"):
        # the dialer's own number field (recon A1, dialer.xml) — not every digit of the page
        # source, where bounds and ids hold digits too
        shown = "".join(ch for ch in DialerPage(driver, platform).number(SERVER) if ch.isdigit())
        assert shown == digits, f"dialer shows {shown!r}, expected {digits!r}"
    driver.back()
