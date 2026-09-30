"""Jobs that send notifications — module 11 Notifications (pytest plugin, see conftest.py).

| Test-case precondition                              | Fixture            |
|-----------------------------------------------------|--------------------|
| jobs New for the technician (each: "New job assigned") | ``notif_job``   |
| no notification for the technician                  | ``no_notifications`` |
| push allowed again after the test                   | ``push_restored``  |

Recipe (recon 12, 2026-09-26): ``POST /job`` for the technician sends "New job assigned"; a title
changed through ``PATCH /job`` sends "Job updated"; ``statusType`` ``canceled`` sends "Job
cancelled" (already read). Deleting the job deletes its notifications, so a test leaves none.
"""

import contextlib
import time
from collections.abc import Callable, Iterator
from datetime import date, datetime

import allure
import pytest
from selenium.common.exceptions import TimeoutException

from fixtures.jobs import ADDRESS, COORDINATES, SHORT_SURVEY, SeedJob, _run_stamp
from helpers import waits
from helpers.android.device import Adb
from helpers.field_services_api import ApiBlocked
from pages.settings_page import SystemSettingsPage

SERVER = 30.0
APART = 1.2  # seconds between two jobs: distinct createdAt, so the order is decidable


@pytest.fixture(scope="module")
def notif_sweep(field_services_api, tech_user_id) -> None:
    """Jobs left by an interrupted run are removed once per module — with their notifications."""
    with allure.step("sweep QA-AUTO jobs left on the technician"):
        field_services_api.sweep_test_jobs(tech_user_id)


@pytest.fixture
def notif_job(notif_sweep, field_services_api, tech_user_id) -> Iterator[Callable[..., SeedJob]]:
    """``notif_job(title=None)`` → a new job, status New, for the technician; deleted after the
    test with its notifications."""
    api, run, made = field_services_api, _run_stamp(), []

    def create(title: str | None = None) -> SeedJob:
        today = date.today()
        when = datetime(today.year, today.month, today.day, 9 + len(made) % 12, 0)
        job_id = f"QA-AUTO-{run}-N{len(made) + 1:02d}"
        title = title or f"QA-AUTO notif {len(made) + 1:02d}"
        if made:
            time.sleep(APART)
        with allure.step(f"seed: job {job_id} (new) → 'New job assigned'"):
            created = api.create_job(
                user_id=tech_user_id, job_id=job_id, title=title, when=when, status="new",
                survey_id=SHORT_SURVEY, address=ADDRESS, coordinates=COORDINATES,
            )  # fmt: skip
        job = SeedJob("notif", str(created["id"]), job_id, title, when, "new")
        made.append(job)
        return job

    try:
        yield create
    finally:
        errors = []
        for job in made:
            try:
                api.delete_job({"id": job.id, "jobId": job.job_id})
            except (ApiBlocked, ValueError) as exc:
                errors.append(str(exc))
        if errors:
            raise ApiBlocked("notification job cleanup failed:\n" + "\n".join(errors))


def server_notifications(api, user_id: str, driver, jobs: list[SeedJob], count: int) -> list[dict]:
    """The technician's notifications of ``jobs``, newest first, once ``count`` of them are on
    the server (or SERVER seconds pass — the last read is returned and the test asserts on it)."""
    ids = {j.job_id for j in jobs}
    last: list[list[dict]] = []

    def ready(_d) -> bool:
        mine = [n for n in api.notifications(user_id) if (n.get("job") or {}).get("jobId") in ids]
        last.append(mine)
        return len(mine) >= count

    with (
        allure.step(f"server: {count} notification(s) of the test's jobs"),
        contextlib.suppress(TimeoutException),
    ):
        waits.wait_until(driver, ready, SERVER, poll=2)
    return last[-1]


@pytest.fixture
def no_notifications(notif_sweep, field_services_api, tech_user_id) -> None:
    """The technician has no notification — else the empty state cannot be reached: Blocked."""
    left = field_services_api.notifications(tech_user_id)
    if left:
        pytest.skip(
            f"Blocked: the technician has {len(left)} notification(s) that no test made — the "
            "empty state cannot be reached"
        )


@pytest.fixture
def push_restored(app, driver) -> Iterator[SystemSettingsPage]:
    """The Settings app page; push is allowed again when the test ends, even after a failure."""
    settings_app = SystemSettingsPage(driver, app.platform)
    try:
        yield settings_app
    finally:
        settings_app.set_app_notifications(True, app.app_id)
        if app.platform == "android":
            # the "Don't allow" of the test (D-NOTIF-A4) is remembered — a second one would make
            # Android stop asking; every run starts from the same never-refused state
            Adb.of(driver).shell(
                f"pm clear-permission-flags {app.app_id} android.permission.POST_NOTIFICATIONS "
                "user-set user-fixed"
            )
