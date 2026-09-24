"""Jobs and device state for module 05 Check-in / Check-out (pytest plugin, see conftest.py).

| Test-case placeholder / precondition                  | Fixture              |
|-------------------------------------------------------|----------------------|
| ``{{job.<kind>}}`` — gps, cancel, far, double, guard, in_progress, submitted, … | ``check_seed`` |
| location granted, device on site, mock switch ON      | ``on_site``          |
| … device ~5.5 km away                                 | ``away``             |
| location granted, device on site, mock switch OFF     | ``guarded``          |

Every check-in / check-out changes its job, so each TC that completes one owns a job. The device
state is global: every fixture sets it before ``ui_login`` relaunches the app and puts the mock
switch back OFF afterwards (owner, Q-CHIO-5; recon 6 / 6c).
"""

from dataclasses import dataclass, field
from datetime import date, datetime

import allure
import pytest

from fixtures.jobs import ADDRESS, COORDINATES, SHORT_SURVEY, SeedJob, _run_stamp
from helpers.app import AppControl
from helpers.field_services_api import ApiBlocked

SITE = (float(COORDINATES["latitude"]), float(COORDINATES["longitude"]))
AWAY = (SITE[0] + 0.05, SITE[1])  # ~5.5 km north — far outside the app's 100 m radius
PLAN = (  # kind, status, hour
    ("gps", "new", 8), ("cancel", "new", 9), ("far", "new", 10), ("double", "new", 11),
    ("guard", "new", 12), ("in_progress", "in_progress", 13), ("submitted", "submitted", 14),
    ("submitted_keep", "submitted", 15),
)  # fmt: skip


@dataclass
class CheckSeed:
    jobs: dict[str, SeedJob] = field(default_factory=dict)

    def __getitem__(self, kind: str) -> SeedJob:
        return self.jobs[kind]


@pytest.fixture(scope="module")
def check_seed(field_services_api, tech_user_id):
    """8 jobs for module 05 (plan, Step 9), deleted after it."""
    api, seed, run, today = field_services_api, CheckSeed(), _run_stamp(), date.today()
    try:
        with allure.step(f"seed: {len(PLAN)} jobs (run {run})"):
            api.sweep_test_jobs(tech_user_id)
            for kind, status, hour in PLAN:
                when = datetime(today.year, today.month, today.day, hour, 0)
                job_id, title = f"QA-AUTO-{run}-{kind.upper()}", f"QA-AUTO {kind}"
                created = api.create_job(
                    user_id=tech_user_id, job_id=job_id, title=title, when=when, status=status,
                    survey_id=SHORT_SURVEY, address=ADDRESS, coordinates=COORDINATES,
                )  # fmt: skip
                seed.jobs[kind] = SeedJob(kind, str(created["id"]), job_id, title, when, status)
        yield seed
    finally:
        errors = []
        for job in seed.jobs.values():
            try:
                api.delete_job({"id": job.id, "jobId": job.job_id})
            except (ApiBlocked, ValueError) as exc:
                errors.append(str(exc))
        if errors:
            raise ApiBlocked("check seed cleanup failed:\n" + "\n".join(errors))


def _device(app: AppControl, where: tuple[float, float], mock_allowed: bool) -> None:
    app.set_mock_location_allowed(mock_allowed)  # terminates the app first
    app.grant_location_permission()
    app.set_location(*where)


@pytest.fixture
def on_site(app):
    """Location granted, device at the job site, mock switch ON — list it BEFORE ``ui_login``."""
    _device(app, SITE, mock_allowed=True)
    yield SITE
    app.set_mock_location_allowed(False)


@pytest.fixture
def away(app):
    """As ``on_site`` but ~5.5 km from the job."""
    _device(app, AWAY, mock_allowed=True)
    yield AWAY
    app.set_mock_location_allowed(False)
    app.set_location(*SITE)


@pytest.fixture
def guarded(app):
    """Location granted, device at the job site, mock switch OFF — the app's guard is active."""
    _device(app, SITE, mock_allowed=False)
    return SITE
