"""Job data for module 03 onwards (pytest plugin, registered in conftest.py).

| Test-case placeholder                              | Fixture          |
|----------------------------------------------------|------------------|
| ``{{job.<kind>}}``, ``{{day.*}}``                  | ``jobs_seed``    |
| the technician has no active job                   | ``no_active_jobs`` |
| a job created after the Jobs screen loaded         | ``late_job``     |
| ``{{link.invalid}}``, ``{{link.other_phone}}``, ``{{link.own_phone}}`` | ``job_links`` |

Recipe (docs/api/dev-test-data.md, verified 2026-09-22; recon 4 2026-09-24): ``POST /job`` with the
technician's ``userId`` and a read-only published survey → the test → ``DELETE /job/{id}`` in
``finally`` (verified gone). Only ``QA-AUTO-*`` jobs are ever deleted. Dates are device-local
(the simulator uses the host time zone). The seed is created **out of date order** (other day →
yesterday → today) so an order by creation time and an order by date differ (TC-ORDL-014).
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import allure
import pytest

from config.settings import settings
from fixtures import test_data
from helpers.field_services_api import ApiBlocked

SHORT_SURVEY = "2964b433-b734-4505-a8c5-6fb42c30fc33"  # "Short Survey", published, read-only
ADDRESS = "QA test site, 350 5th Ave, New York, NY 10118"
COORDINATES = {"latitude": "40.748440", "longitude": "-73.985664"}
LINK_BASE = "https://copsfieldservices.dev.concerttech.com/redirect/"
ACTIVE = ("new", "in_progress", "submitted", "reopened")


@dataclass(frozen=True)
class SeedJob:
    kind: str
    id: str
    job_id: str
    title: str
    when: datetime
    status: str

    @property
    def title_line(self) -> str:
        """``<jobId> - <title>`` — the bold line of the card and the details header."""
        return f"{self.job_id} - {self.title}"

    @property
    def date_text(self) -> str:
        """Card date, ``d MMM y`` (e.g. ``24 Sep 2026``)."""
        return f"{self.when.day} {self.when:%b %Y}"

    @property
    def time_text(self) -> str:
        return f"{self.when:%H:%M}"

    @property
    def address(self) -> str:
        return ADDRESS


@dataclass
class Seed:
    user_id: str
    today: date
    other_day: date  # another day of the current Sunday–Saturday week, with a job
    yesterday: date
    empty_day: date  # a day of the current week with no job
    jobs: dict[str, SeedJob] = field(default_factory=dict)

    def __getitem__(self, kind: str) -> SeedJob:
        return self.jobs[kind]


def week_of(day: date) -> list[date]:
    """Sunday … Saturday of ``day``'s week (the calendar's week, table_calendar default)."""
    sunday = day - timedelta(days=(day.weekday() + 1) % 7)
    return [sunday + timedelta(days=i) for i in range(7)]


def plan_days(today: date) -> tuple[date, date, date]:
    """(other_day, yesterday, empty_day) for a seed made on ``today``."""
    week = week_of(today)
    other_day = today + timedelta(days=1) if today != week[-1] else today - timedelta(days=1)
    yesterday = today - timedelta(days=1)
    empty_day = next(d for d in week if d not in (today, other_day, yesterday))
    return other_day, yesterday, empty_day


# kind, day key, hour, status, isViewed — in CREATION order (not date order, TC-ORDL-014)
SEED_PLAN = (
    ("otherday", "other_day", 12, "new", None),
    ("yesterday", "yesterday", 12, "new", None),
    ("new", "today", 9, "new", None),
    ("inprog", "today", 10, "in_progress", None),
    ("submitted", "today", 11, "submitted", None),
    ("completed", "today", 12, "completed", None),
    ("canceled", "today", 13, "canceled", None),
    ("expired", "today", 14, "expired", None),
    ("unviewed", "today", 15, "new", False),
)


def _create(api, user_id: str, run: str, kind: str, day: date, hour: int, status: str,
            viewed: bool | None) -> SeedJob:  # fmt: skip
    when = datetime(day.year, day.month, day.day, hour, 0)
    job_id = f"QA-AUTO-{run}-{kind.upper()}"
    title = f"QA-AUTO {kind}"
    created = api.create_job(
        user_id=user_id, job_id=job_id, title=title, when=when, status=status,
        survey_id=SHORT_SURVEY, address=ADDRESS, coordinates=COORDINATES, is_viewed=viewed,
    )  # fmt: skip
    return SeedJob(kind, str(created["id"]), job_id, title, when, status)


def _run_stamp() -> str:
    """``1002I201937`` — month-day, the platform's letter, the time: the id of every job and file
    a test seeds. The letter (``-`` outside a run) keeps an iOS and an Android run that seed in the
    same second apart (PARALLEL-RUNS.md); the length is the one the ids always had."""
    return datetime.now().strftime(f"%m%d{settings.run_tag}%H%M%S")


@pytest.fixture(scope="session")
def tech_user_id(field_services_api, tech) -> str:
    try:
        return field_services_api.technician_user_id(tech.email)
    except ApiBlocked as exc:
        pytest.skip(str(exc))


@pytest.fixture
def no_active_jobs(field_services_api, tech_user_id) -> None:
    """The technician has no active job: leftovers of an interrupted run (``QA-AUTO-*``) are
    deleted; a job somebody else assigned makes the precondition fail → Blocked."""
    with allure.step("precondition: the technician has no active job"):
        swept = field_services_api.sweep_test_jobs(tech_user_id)
        if swept:
            allure.attach("\n".join(swept), name="leftover test jobs deleted",
                          attachment_type=allure.attachment_type.TEXT)  # fmt: skip
        foreign = [
            str(j.get("jobId"))
            for j in field_services_api.jobs_of_user(tech_user_id)
            if j.get("statusType") in ACTIVE
        ]
        if foreign:
            pytest.skip(f"Blocked: the technician has active jobs not created by tests: {foreign}")


@pytest.fixture(scope="module")
def jobs_seed(field_services_api, tech_user_id):
    """``{{job.<kind>}}`` — 9 jobs for the module (plan, Step 9), deleted after it."""
    today = date.today()
    other_day, yesterday, empty_day = plan_days(today)
    seed = Seed(tech_user_id, today, other_day, yesterday, empty_day)
    days = {"today": today, "other_day": other_day, "yesterday": yesterday}
    run = _run_stamp()
    try:
        with allure.step(f"seed: {len(SEED_PLAN)} jobs (run {run})"):
            field_services_api.sweep_test_jobs(tech_user_id)
            for kind, day_key, hour, status, viewed in SEED_PLAN:
                seed.jobs[kind] = _create(field_services_api, tech_user_id, run, kind,
                                          days[day_key], hour, status, viewed)  # fmt: skip
        yield seed
    finally:
        errors = []
        for job in seed.jobs.values():
            try:
                field_services_api.delete_job({"id": job.id, "jobId": job.job_id})
            except (ApiBlocked, ValueError) as exc:
                errors.append(str(exc))
        if errors:
            raise ApiBlocked("seed cleanup failed:\n" + "\n".join(errors))


@pytest.fixture
def late_job(field_services_api, tech_user_id):
    """One job created INSIDE the test, after the Jobs screen has loaded (TC-ORDL-015)."""
    created: list[SeedJob] = []

    def make() -> SeedJob:
        job = _create(field_services_api, tech_user_id, _run_stamp(), "late", date.today(), 16,
                      "new", None)  # fmt: skip
        created.append(job)
        return job

    try:
        yield make
    finally:
        for job in created:
            field_services_api.delete_job({"id": job.id, "jobId": job.job_id})


@dataclass(frozen=True)
class JobLinks:
    invalid: str
    other_phone: str
    own_phone: str


@pytest.fixture(scope="module")
def job_links(field_services_api, tech) -> JobLinks:
    """https job links from ``POST /job/assign/{phone}`` (owner go 2026-09-24): one for a reserved
    555-01xx number without an account, one for the test account's (not real) phone, and a key
    that was never issued. Links expire by themselves (72 h) — nothing to clean."""
    other = "+1" + test_data.free_fictional_national(
        field_services_api, avoid=(tech.phone_national,)
    )
    try:
        return JobLinks(
            invalid=f"{LINK_BASE}QA-AUTO-INVALID-{_run_stamp()}",
            other_phone=field_services_api.job_link(other),
            own_phone=field_services_api.job_link(tech.phone),
        )
    except ApiBlocked as exc:
        pytest.skip(str(exc))


@pytest.fixture
def job_new(field_services_api, tech_user_id):
    """``{{job.new}}`` (TC-ORDL-016, -017, -019) — one job, status ``new``, today, created
    through the API while the device is online; deleted after the test (as the online file's
    ``jobs_seed``, one job at a time — convention of the offline test-case file;
    Android offline tests, step 5)."""
    job = _create(
        field_services_api, tech_user_id, _run_stamp(), "new", date.today(), 9, "new", None
    )
    try:
        yield job
    finally:
        field_services_api.delete_job({"id": job.id, "jobId": job.job_id})


@pytest.fixture
def job_offline_creator(field_services_api, tech_user_id):
    """``{{job.offline_created}}`` (TC-ORDL-018) — created mid-test through ``POST /job`` while
    the device stays offline; deleted after the test. A callable, as ``late_job`` (fixtures/jobs.py)
    is for the online file: the job does not exist until the test creates it."""
    made: list = []

    def make():
        job = _create(
            field_services_api, tech_user_id, _run_stamp(), "offline", date.today(), 9, "new", None
        )
        made.append(job)
        return job

    try:
        yield make
    finally:
        for job in made:
            field_services_api.delete_job({"id": job.id, "jobId": job.job_id})
