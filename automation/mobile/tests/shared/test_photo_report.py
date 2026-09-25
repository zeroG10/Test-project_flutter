"""Photo report (module 09) — TC-PHR-001…008.

Source of every step and expectation: qa/mobile/09-photo-report/photo-report-test-cases.md (recon 9;
the owner's decisions 2026-09-25). Data: fixtures/survey.py — one job per test, directly In
progress, deleted after it; photos from the simulator gallery (``gallery_photos``: cell 1 = a small
photo). The server copy is ``GET /job/{id}`` → ``photos``.

TC-PHR-008 asserts what the SRS requires of a deleted photo on the server; it is expected to fail
while BUG-PHR-001 (draft, the owner validates) stands. Camera, crop / markup, offline and failures
are not here (owner, Q-PHR-2…4). Every expected value goes through ``expected(...)``.
"""

import contextlib

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from helpers import waits
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.photo_report_page import (
    PhotoAddSheet,
    PhotoDeleteDialog,
    PhotoEditor,
    PhotoMetadata,
    PhotoReportPage,
    PhotoUnsavedDialog,
)

SERVER = 30.0
LIST_REFRESHES = 3
DELETE_MESSAGE = "Are you sure you want to delete this photo.\nAll descriptions will be lost?"
EDITED = "QA-AUTO photo one-edited"


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        report = PhotoReportPage(driver, platform)
        sheet = PhotoAddSheet(driver, platform)
        editor = PhotoEditor(driver, platform)
        meta = PhotoMetadata(driver, platform)
        delete = PhotoDeleteDialog(driver, platform)
        unsaved = PhotoUnsavedDialog(driver, platform)

    return Pages


def open_report(pages, job, expected) -> None:
    """Refresh until DEV lists the new job, open it, tap Photo report."""
    locator = pages.jobs.locator("card", text=job.job_id)
    for _ in range(LIST_REFRESHES):
        pages.jobs.pull_to_refresh()
        if pages.jobs.driver.find_elements(*locator):
            break
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)
    pages.details.tap("deliverable", text="Photo report")
    pages.report.assert_open(SERVER)


def server_photos(api, job, driver, until) -> list[dict]:
    """The job's photos on the server, read until ``until(photos)`` holds or SERVER seconds pass —
    the last read is returned either way and the test asserts on it."""
    last: list[list[dict]] = []

    def ready(_d) -> bool:
        last.append(api.job(job.id).get("photos") or [])
        return bool(until(last[-1]))

    with allure.step("server: the job's photos"), contextlib.suppress(TimeoutException):
        waits.wait_until(driver, ready, SERVER, poll=2)
    return last[-1]


ADD_CHKS = ("CHK-PHR-001", "CHK-PHR-002", "CHK-PHR-003", "CHK-PHR-004", "CHK-PHR-005",
            "CHK-PHR-006", "CHK-PHR-007", "CHK-PHR-009", "CHK-PHR-011", "CHK-PHR-013",
            "CHK-PHR-014", "CHK-PHR-033", "CHK-PHR-034", "CHK-PHR-035")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-001")
@pytest.mark.chk(*ADD_CHKS)
@allure.tag(*ADD_CHKS)
@allure.title(
    "TC-PHR-001 The empty Photo report leads through the gallery to a saved photo with its "
    "description"
)
def test_add_photo(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, r, meta = survey_job("short"), pages.report, pages.meta
    open_report(pages, job, expected)
    r.visible("back")
    r.visible("empty-title", 5)
    r.visible("empty-text")
    evidence.checkpoint("photo-report-empty")
    r.start_add_photo()
    pages.sheet.visible("camera")
    pages.sheet.visible("gallery")
    r.pick_from_gallery(1)
    pages.editor.tap("done")
    meta.assert_open(15)
    with allure.step("expect 'Add photo' with empty fields"):
        assert meta.description() == "", f"description {meta.description()!r}"
        assert meta.counter() == expected("0 / 500"), meta.counter()
    meta.fill_description("QA-AUTO photo one")
    meta.tap("save")
    r.assert_open(SERVER)
    r.visible("photo", 10, text=expected("QA-AUTO photo one"))
    evidence.checkpoint("photo-report-one")
    photos = server_photos(field_services_api, job, driver, until=lambda p: len(p) == 1)
    with allure.step("expect the photo on the job on the server, with its description"):
        assert [p.get("note") for p in photos] == [expected("QA-AUTO photo one")], photos


META_CHKS = ("CHK-PHR-025", "CHK-PHR-026", "CHK-PHR-027", "CHK-PHR-028", "CHK-PHR-029",
             "CHK-PHR-030", "CHK-PHR-031", "CHK-PHR-032")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-002")
@pytest.mark.chk(*META_CHKS)
@allure.tag(*META_CHKS)
@allure.title(
    "TC-PHR-002 Description up to 500 characters with a counter; tags are chosen and unchosen"
)
def test_description_and_tags(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected
):
    job, r, meta = survey_job("short"), pages.report, pages.meta
    text = ("QA-AUTO photo description " * 25)[:501]
    open_report(pages, job, expected)
    r.start_add_photo()
    r.pick_from_gallery(1)
    pages.editor.tap("done")
    meta.assert_open(15)
    meta.expect_enabled("save")  # the description is optional
    meta.fill_description(text)
    with allure.step("expect the first 500 characters and '500 / 500'"):
        assert meta.description() == text[:500], f"{len(meta.description())} characters kept"
        assert meta.counter() == expected("500 / 500"), meta.counter()
    for tag, selected in (("Undamaged", True), ("tag1", True), ("Undamaged", False)):
        meta.tap("tag", text=tag)
        meta.expect_tag(expected(tag), selected)
    meta.expect_tag("tag1")
    meta.tap("save")
    r.assert_open(SERVER)
    photos = server_photos(field_services_api, job, driver, until=lambda p: len(p) == 1)
    with allure.step("expect the 500-character note and one tag, tag1"):
        assert len(photos) == 1, photos
        assert photos[0].get("note") == text[:500], (
            f"note of {len(photos[0].get('note') or '')} characters"
        )
        assert [t.get("name") for t in photos[0].get("tags") or []] == [expected("tag1")], photos[0]


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-003")
@pytest.mark.chk("CHK-PHR-006", "CHK-PHR-008")
@allure.tag("CHK-PHR-006", "CHK-PHR-008")
@allure.title("TC-PHR-003 Several photos show as a grid, and Add photo stays available")
def test_several_photos(survey_job, gallery_photos, ui_login, pages, expected, evidence):
    job, r = survey_job("short"), pages.report
    open_report(pages, job, expected)
    for description in ("", "QA-AUTO second", "QA-AUTO third"):
        r.add_photo(1, description)
    r.expect_photo_count(3)
    with allure.step("expect the descriptions in the grid, and Add photo"):
        assert r.descriptions() == ["", expected("QA-AUTO second"), expected("QA-AUTO third")], (
            r.descriptions()
        )
        r.visible("add-photo")
    evidence.checkpoint("photo-report-three")


EDIT_CHKS = ("CHK-PHR-013", "CHK-PHR-015", "CHK-PHR-036", "CHK-PHR-037", "CHK-PHR-038")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-004")
@pytest.mark.chk(*EDIT_CHKS)
@allure.tag(*EDIT_CHKS)
@allure.title(
    "TC-PHR-004 Editing: 'Edit photo' preloads the photo's data; Save updates it; leaving without "
    "Save warns and keeps it"
)
def test_edit_photo(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, r, meta = survey_job("short"), pages.report, pages.meta
    open_report(pages, job, expected)
    r.add_photo(1, "QA-AUTO photo one", ("tag1",))
    r.open_photo(0)
    with allure.step("expect 'Edit photo' with the saved description and tag"):
        assert meta.description() == expected("QA-AUTO photo one"), meta.description()
        meta.expect_tag("tag1")
    meta.fill_description("-edited")
    meta.tap("back")
    pages.unsaved.visible("title", 5)
    pages.unsaved.visible("message")
    evidence.checkpoint("unsaved-changes")
    pages.unsaved.tap("leave")
    r.assert_open(SERVER)
    assert r.descriptions() == [expected("QA-AUTO photo one")], r.descriptions()
    r.open_photo(0)
    meta.fill_description("-edited")
    meta.tap("save")
    r.assert_open(SERVER)
    r.visible("photo", 10, text=expected("QA-AUTO photo one-edited"))
    photos = server_photos(field_services_api, job, driver,
                           until=lambda p: [x.get("note") for x in p] == [EDITED])  # fmt: skip
    with allure.step("expect one photo on the server, edited, with its tag"):
        assert [p.get("note") for p in photos] == [expected("QA-AUTO photo one-edited")], photos
        assert [t.get("name") for t in photos[0].get("tags") or []] == [expected("tag1")], photos[0]


DELETE_CHKS = ("CHK-PHR-039", "CHK-PHR-040", "CHK-PHR-041", "CHK-PHR-042", "CHK-PHR-044")


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-005")
@pytest.mark.chk(*DELETE_CHKS)
@allure.tag(*DELETE_CHKS)
@allure.title(
    "TC-PHR-005 Deleting: the dialog; Cancel keeps the photo; Delete removes it and the grid "
    "updates"
)
def test_delete_photo(survey_job, gallery_photos, ui_login, pages, expected, evidence):
    job, r, dialog = survey_job("short"), pages.report, pages.delete
    open_report(pages, job, expected)
    r.add_photo(1, "QA-AUTO first")
    r.add_photo(1, "QA-AUTO second")
    r.expect_photo_count(2)
    r.tap_delete(0)
    dialog.visible("title", 5)
    dialog.expect_text("message", expected(DELETE_MESSAGE))
    dialog.visible("cancel")
    evidence.checkpoint("delete-photo-dialog")
    dialog.tap("cancel")
    dialog.wait_gone("title", 5)
    r.expect_photo_count(2)
    r.delete_photo(0)
    r.expect_photo_count(1)
    r.delete_photo(0)
    r.visible("empty-title", 10)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-006")
@pytest.mark.chk("CHK-PHR-033")
@allure.tag("CHK-PHR-033")
@allure.title("TC-PHR-006 Photos and descriptions survive an app restart")
def test_photos_after_restart(survey_job, gallery_photos, ui_login, pages, expected):
    job, r = survey_job("short"), pages.report
    open_report(pages, job, expected)
    r.add_photo(1, "QA-AUTO keep")
    ui_login.relaunch()
    pages.jobs.assert_open(SERVER)
    open_report(pages, job, expected)
    r.visible("photo", 10, text=expected("QA-AUTO keep"))


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-007")
@pytest.mark.chk("CHK-PHR-012")
@allure.tag("CHK-PHR-012")
@allure.title("TC-PHR-007 The photo editor opens with Crop and Markup, and ✓ leads to 'Add photo'")
def test_editor_opens(survey_job, gallery_photos, ui_login, pages, expected, evidence):
    job, r = survey_job("short"), pages.report
    open_report(pages, job, expected)
    r.start_add_photo()
    r.pick_from_gallery(1)
    pages.editor.visible("crop", 5)
    pages.editor.visible("markup")
    evidence.checkpoint("photo-editor")
    pages.editor.tap("done")
    pages.meta.assert_open(15)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-PHR-008")
@pytest.mark.chk("CHK-PHR-043")
@allure.tag("CHK-PHR-043")
@allure.title("TC-PHR-008 A deleted photo is removed from the job on the server")
def test_deleted_photo_leaves_the_server(
    survey_job, gallery_photos, ui_login, field_services_api, driver, pages, expected, evidence
):
    job, r = survey_job("short"), pages.report
    open_report(pages, job, expected)
    r.add_photo(1, "QA-AUTO to delete")
    before = server_photos(field_services_api, job, driver, until=lambda p: len(p) == 1)
    assert [p.get("note") for p in before] == [expected("QA-AUTO to delete")], before
    r.delete_photo(0)
    r.visible("empty-title", 10)
    evidence.checkpoint("photo-report-empty-after-delete")
    after = server_photos(field_services_api, job, driver, until=lambda p: not p)
    with allure.step(
        "expect no photo on the job on the server (SRS FR-DEL-PH-03/-04/-08; BUG-PHR-001)"
    ):
        assert after == [], f"the deleted photo is still on the job: {[p.get('id') for p in after]}"
