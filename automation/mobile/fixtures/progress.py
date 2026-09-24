"""Jobs for module 06 Order progress (pytest plugin, registered in conftest.py).

| Test-case placeholder / precondition                 | Fixture           |
|------------------------------------------------------|-------------------|
| ``{{job.progress}}``, ``{{job.done}}``, ``{{pf.*}}`` | ``progress_seed`` |
| ``{{job.progress}}`` checked in, Jobs list on screen | ``in_progress_job`` |

Recipe (recon 7, 2026-09-24): ``progress`` is created New with a description and a PF and is
checked in **through the UI on this device** by the first test that needs it (the steps of
TC-CHIO-001, mock-location switch ON as in module 05). A job created In progress through the API
has no check-in time the app reads: its timer counts from the job's last change and restarts
with every update (Q-ORDP-4). ``done`` is created Submitted. Nothing is filled or submitted; both
jobs are deleted after the module.
"""

from dataclasses import dataclass, field
from datetime import date, datetime

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from fixtures.details import DESCRIPTION, PF, DetailsJob
from fixtures.jobs import ADDRESS, COORDINATES, SHORT_SURVEY, _run_stamp
from helpers.field_services_api import ApiBlocked
from pages.confirm_check_page import ConfirmCheckPage
from pages.job_details_page import JobDetailsPage
from pages.jobs_list_page import JobsListPage

SERVER = 20.0
PLAN = (("progress", "new", 9), ("done", "submitted", 10))  # kind, status, hour


@dataclass
class ProgressSeed:
    jobs: dict[str, DetailsJob] = field(default_factory=dict)
    pf: dict[str, str] = field(default_factory=lambda: dict(PF))
    survey_name: str = "Short Survey"  # the name of SHORT_SURVEY (recon 7)

    def __getitem__(self, kind: str) -> DetailsJob:
        return self.jobs[kind]


@pytest.fixture(scope="module")
def progress_seed(field_services_api, tech_user_id):
    """2 jobs for module 06 (plan, Step 9), deleted after it."""
    api, seed, run, today = field_services_api, ProgressSeed(), _run_stamp(), date.today()
    try:
        with allure.step(f"seed: {len(PLAN)} jobs (run {run})"):
            api.sweep_test_jobs(tech_user_id)
            for kind, status, hour in PLAN:
                when = datetime(today.year, today.month, today.day, hour, 0)
                job_id, title = f"QA-AUTO-{run}-{kind.upper()}", f"QA-AUTO {kind}"
                created = api.create_job(
                    user_id=tech_user_id, job_id=job_id, title=title, when=when, status=status,
                    survey_id=SHORT_SURVEY, address=ADDRESS, coordinates=COORDINATES,
                    description=DESCRIPTION, project_facilitator=PF,
                )  # fmt: skip
                seed.jobs[kind] = DetailsJob(kind, str(created["id"]), job_id, title, when, status)
        yield seed
    finally:
        errors = []
        for job in seed.jobs.values():
            try:
                api.delete_job({"id": job.id, "jobId": job.job_id})
            except (ApiBlocked, ValueError) as exc:
                errors.append(str(exc))
        if errors:
            raise ApiBlocked("progress seed cleanup failed:\n" + "\n".join(errors))


def _check_in(app, driver, platform, job) -> None:
    """The steps of TC-CHIO-001 (which proves them) as a precondition; back on the Jobs list."""
    jobs, details = JobsListPage(driver, platform), JobDetailsPage(driver, platform)
    confirm = ConfirmCheckPage(driver, platform)
    try:
        with allure.step(f"precondition: check in {job.job_id} through the UI"):
            jobs.pull_to_refresh()
            jobs.open_card(job.job_id)
            details.expect_header(job.title_line, SERVER)
            with app.alerts_left_alone():  # WDA may press a dialog button
                details.tap("check-in")
                confirm.visible("confirm", SERVER)
                confirm.tap("confirm")
            details.expect_field("status", "In progress", SERVER)
            details.go_back()
            jobs.assert_open(SERVER)
    except (TimeoutException, AssertionError) as exc:
        reason = getattr(exc, "msg", None) or str(exc).splitlines()[0]
        pytest.skip(f"Blocked: the check-in precondition failed ({reason}); TC-CHIO-001 owns it")


@pytest.fixture
def in_progress_job(progress_seed, field_services_api, driver, platform, request):
    """``{{job.progress}}`` In progress, checked in on this device; signed in, Jobs list on screen.

    Request it INSTEAD of listing ``ui_login`` first: when the job is still New it sets the device
    on site with the switch ON (``on_site``, which must run before ``ui_login``), then signs in and
    checks in. The switch goes back OFF when the test ends.
    """
    job = progress_seed["progress"]
    status = field_services_api.job(job.id).get("statusType")
    if status not in ("new", "in_progress"):
        pytest.skip(f"Blocked: {{{{job.progress}}}} is {status!r} on the server, not in_progress")
    if status == "new":
        request.getfixturevalue("on_site")
    app = request.getfixturevalue("ui_login")
    if status == "new":
        _check_in(app, driver, platform, job)
    return job
