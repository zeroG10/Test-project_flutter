"""Notes (module 10) — TC-NOTE-001…007.

Source of every step and expectation: qa/mobile/10-notes/notes-test-cases.md (recon 10; the owner's
decisions 2026-09-25). Data: fixtures/survey.py — one job per test, directly In progress (Submitted
for TC-NOTE-007), deleted after it. The server copy is ``GET /job/{id}`` → ``notes``.

The job's notes on the server before submission are not an oracle (owner, 2026-09-26: editing and
deleting work on a real device; BUG-NOTE-001 not filed); the final server state is checked after
submission in module 07. Offline and failures are not here (owner, Q-NOTE-1); CHK-NOTE-041 is
skipped (Q-NOTE-2). Every expected value goes through ``expected(...)``.
"""

import contextlib
from datetime import datetime, timedelta

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from helpers import waits
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage
from pages.notes_page import NoteDeleteDialog, NoteEditor, NotesPage, NoteUnsavedDialog

SERVER = 30.0
LIST_REFRESHES = 3
READ_ONLY_WATCH = 3.0
DELETE_MESSAGE = "Are you sure you want delete this note. All descriptions will be lost?"


@pytest.fixture
def pages(driver, platform):
    class Pages:
        jobs = JobsListPage(driver, platform)
        details = JobDetailsPage(driver, platform)
        notes = NotesPage(driver, platform)
        editor = NoteEditor(driver, platform)
        delete = NoteDeleteDialog(driver, platform)
        unsaved = NoteUnsavedDialog(driver, platform)

    return Pages


def open_job(pages, job, expected) -> None:
    """Refresh until DEV lists the new job, then open it."""
    locator = pages.jobs.locator("card", text=job.job_id)
    for _ in range(LIST_REFRESHES):
        pages.jobs.pull_to_refresh()
        if pages.jobs.driver.find_elements(*locator):
            break
    pages.jobs.open_card(job.job_id)
    pages.details.expect_header(expected(job.title_line), SERVER)


def open_notes(pages, job, expected) -> None:
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text="Notes")
    pages.notes.assert_open(SERVER)


def server_notes(api, job, driver, until) -> list[str]:
    """The texts of the job's notes on the server, read until ``until(texts)`` holds or SERVER
    seconds pass — the last read is returned either way and the test asserts on it."""
    last: list[list[str]] = []

    def ready(_d) -> bool:
        last.append([n.get("text") for n in api.job(job.id).get("notes") or []])
        return bool(until(last[-1]))

    with allure.step("server: the job's notes"), contextlib.suppress(TimeoutException):
        waits.wait_until(driver, ready, SERVER, poll=2)
    return last[-1]


ADD_CHKS = ("CHK-NOTE-001", "CHK-NOTE-002", "CHK-NOTE-003", "CHK-NOTE-004", "CHK-NOTE-005",
            "CHK-NOTE-006", "CHK-NOTE-012", "CHK-NOTE-013", "CHK-NOTE-014", "CHK-NOTE-015",
            "CHK-NOTE-016", "CHK-NOTE-020", "CHK-NOTE-021", "CHK-NOTE-022",
            "CHK-NOTE-023")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-001")
@pytest.mark.chk(*ADD_CHKS)
@allure.tag(*ADD_CHKS)
@allure.title(
    "TC-NOTE-001 The empty Notes screen leads to a saved note, with the Save rules and the success "
    "message"
)
def test_add_note(survey_job, ui_login, field_services_api, driver, pages, expected, evidence):
    job, n, e = survey_job("short"), pages.notes, pages.editor
    text = "QA-AUTO note one\nline two"
    open_notes(pages, job, expected)
    n.visible("back")
    n.visible("empty-title", 5)
    n.visible("empty-text")
    evidence.checkpoint("notes-empty")
    n.start_add()
    with allure.step("expect 'Add note': the placeholder, 0/500, Save disabled"):
        assert e.find("field").get_attribute("name") == expected("Add note"), "no placeholder"
        assert e.counter() == expected("0/500"), e.counter()
    e.expect_disabled("save")
    e.type_text(text)
    e.expect_enabled("save")
    e.tap("save")
    n.assert_open(SERVER)
    n.visible("toast", 5)
    n.expect_text("toast", expected("Note added successfully"))
    evidence.checkpoint("note-added")
    n.expect_texts([expected(text)])
    notes = server_notes(field_services_api, job, driver, until=lambda t: t == [text])
    with allure.step("expect the note on the job on the server"):
        assert notes == [expected(text)], notes


LIST_CHKS = ("CHK-NOTE-007", "CHK-NOTE-008", "CHK-NOTE-009", "CHK-NOTE-010", "CHK-NOTE-011")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-002")
@pytest.mark.chk(*LIST_CHKS)
@allure.tag(*LIST_CHKS)
@allure.title("TC-NOTE-002 The list: newest first, date and time, preview, ⋮, Add note available")
def test_notes_list(survey_job, ui_login, pages, expected, evidence):
    job, n = survey_job("short"), pages.notes
    long = ("QA-AUTO long note " * 20)[:300]
    open_notes(pages, job, expected)
    for text in ("QA-AUTO first", "QA-AUTO second", long):
        n.add_note(text)
    n.expect_texts([expected(long), expected("QA-AUTO second"), expected("QA-AUTO first")])
    now = datetime.now()
    shown = {
        f"{t:%d %b %Y %H:%M}" for t in (now, now - timedelta(minutes=1), now - timedelta(minutes=2))
    }
    with allure.step("expect 'dd MMM yyyy HH:mm' of now on the newest note"):
        assert n.rows()[0].date in shown, (
            f"date {n.rows()[0].date!r}, expected one of {sorted(shown)}"
        )
    evidence.checkpoint("notes-list")
    menu = n.open_menu(0)
    menu.visible("edit")
    menu.visible("delete")
    menu.tap("edit")  # leave the menu the plain way: the edit page, then back unchanged
    pages.editor.visible("edit-title", 10)
    pages.editor.tap("back")
    n.assert_open(SERVER)
    n.visible("add-note")


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-003")
@pytest.mark.chk("CHK-NOTE-017", "CHK-NOTE-018", "CHK-NOTE-019")
@allure.tag("CHK-NOTE-017", "CHK-NOTE-018", "CHK-NOTE-019")
@allure.title("TC-NOTE-003 A note takes 500 characters; the 501st is refused; the counter follows")
def test_note_limit(survey_job, ui_login, pages, expected):
    job, n, e = survey_job("short"), pages.notes, pages.editor
    rest = ("QA-AUTO note limit " * 30)[:494]
    open_notes(pages, job, expected)
    n.start_add()
    e.type_text("QA-AUTO")
    assert e.counter() == expected("7/500"), e.counter()
    e.driver.switch_to.active_element.send_keys(rest)  # 7 + 494 = 501
    with allure.step("expect the first 500 characters and '500/500'"):
        assert e.text() == ("QA-AUTO" + rest)[:500], f"{len(e.text())} characters kept"
        assert e.counter() == expected("500/500"), e.counter()


EDIT_CHKS = ("CHK-NOTE-024", "CHK-NOTE-025", "CHK-NOTE-026", "CHK-NOTE-027", "CHK-NOTE-028",
             "CHK-NOTE-029")  # fmt: skip


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-004")
@pytest.mark.chk(*EDIT_CHKS)
@allure.tag(*EDIT_CHKS)
@allure.title(
    "TC-NOTE-004 Editing: 'Edit note' preloads the text; Save updates it in place with 'Note saved "
    "successfully'; leaving without Save warns"
)
def test_edit_note(survey_job, ui_login, pages, expected, evidence):
    job, n = survey_job("short"), pages.notes
    open_notes(pages, job, expected)
    n.add_note("QA-AUTO older")
    n.add_note("QA-AUTO newer")
    editor = n.edit(1)  # QA-AUTO older
    assert editor.text() == expected("QA-AUTO older"), editor.text()
    editor.type_text(" edited")
    editor.tap("back")
    pages.unsaved.visible("title", 5)
    evidence.checkpoint("note-unsaved-changes")
    pages.unsaved.tap("leave")
    n.assert_open(SERVER)
    n.expect_texts([expected("QA-AUTO newer"), expected("QA-AUTO older")])
    editor = n.edit(1)
    editor.type_text(" edited")
    editor.tap("save")
    n.assert_open(SERVER)
    n.visible("toast", 5)
    n.expect_text("toast", expected("Note saved successfully"))
    n.expect_texts([expected("QA-AUTO newer"), expected("QA-AUTO older edited")])  # order kept


DELETE_CHKS = ("CHK-NOTE-030", "CHK-NOTE-031", "CHK-NOTE-032", "CHK-NOTE-033", "CHK-NOTE-034",
               "CHK-NOTE-035", "CHK-NOTE-036", "CHK-NOTE-037", "CHK-NOTE-038",
               "CHK-NOTE-039", "CHK-NOTE-040")  # fmt: skip


@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-005")
@pytest.mark.chk(*DELETE_CHKS)
@allure.tag(*DELETE_CHKS)
@allure.title(
    "TC-NOTE-005 Deleting from ⋮ and from 'Edit note': the dialog, Cancel keeps, Delete removes "
    "with 'Note deleted successfully'"
)
def test_delete_note(survey_job, ui_login, pages, expected, evidence):
    job, n, dialog = survey_job("short"), pages.notes, pages.delete
    open_notes(pages, job, expected)
    n.add_note("QA-AUTO first")
    n.add_note("QA-AUTO second")
    n.open_menu(0).tap("delete")
    dialog.visible("title", 5)
    dialog.expect_text("message", expected(DELETE_MESSAGE))
    dialog.visible("cancel")
    evidence.checkpoint("delete-note-dialog")
    dialog.tap("cancel")
    dialog.wait_gone("title", 5)
    n.expect_texts([expected("QA-AUTO second"), expected("QA-AUTO first")])
    n.delete_from_menu(0, confirm=True)
    n.visible("toast", 5)
    n.expect_text("toast", expected("Note deleted successfully"))
    n.expect_texts([expected("QA-AUTO first")])
    editor = n.edit(0)
    editor.tap("delete-note")
    dialog.visible("title", 5)
    dialog.tap("delete")
    n.visible("empty-title", 10)


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-006")
@pytest.mark.chk("CHK-NOTE-020")
@allure.tag("CHK-NOTE-020")
@allure.title("TC-NOTE-006 Notes survive an app restart")
def test_notes_after_restart(survey_job, ui_login, pages, expected):
    job, n = survey_job("short"), pages.notes
    open_notes(pages, job, expected)
    n.add_note("QA-AUTO keep")
    ui_login.relaunch()
    pages.jobs.assert_open(SERVER)
    open_notes(pages, job, expected)
    n.expect_texts([expected("QA-AUTO keep")])


@pytest.mark.regression
@pytest.mark.shared
@pytest.mark.tc("TC-NOTE-007")
@pytest.mark.chk("CHK-NOTE-042")
@allure.tag("CHK-NOTE-042")
@allure.title("TC-NOTE-007 After the deliverables are submitted, Notes cannot be opened or changed")
def test_submitted_notes_read_only(survey_job, ui_login, pages, expected, evidence):
    job = survey_job("short", status="submitted")
    open_job(pages, job, expected)
    pages.details.tap("deliverable", text=expected("Notes"))
    with allure.step(f"expect no Notes screen for {READ_ONLY_WATCH:.0f}s (read-only)"):
        assert not pages.notes.is_visible("header", READ_ONLY_WATCH), "Notes opened"
    evidence.checkpoint("submitted-notes-read-only")
    pages.details.expect_header(expected(job.title_line))
