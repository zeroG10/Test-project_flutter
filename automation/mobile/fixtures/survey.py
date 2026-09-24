"""Jobs and photos for module 08 Survey (pytest plugin, registered in conftest.py).

| Test-case placeholder / precondition             | Fixture          |
|--------------------------------------------------|------------------|
| ``{{job.<survey>}}`` In progress, ``{{job.done}}`` | ``survey_job``   |
| the 4032×3024 photo newest in the gallery        | ``gallery_photos`` |

Recipe (recon 8, 2026-09-24): one job per test, created through ``POST /job`` **directly In
progress** with the survey under test (the timer is not asserted here, so no check-in), deleted when
the test ends — its saved survey goes with it. Survey photos are uploaded to DEV storage and may
stay there after the job is deleted (accepted by the owner, module 04). The surveys themselves are
published DEV surveys, read only.
"""

from collections.abc import Callable, Iterator
from datetime import date, datetime
from pathlib import Path

import allure
import pytest

from fixtures.jobs import ADDRESS, COORDINATES, SeedJob, _run_stamp
from helpers.field_services_api import ApiBlocked

MEDIA = Path(__file__).parent / "media"
SURVEYS = {  # kind: survey id — qa/mobile/08-survey/survey-definitions/
    "short": "2964b433-b734-4505-a8c5-6fb42c30fc33",
    "mo3": "accc4039-cc3d-455f-b617-f89026760768",
    "mo5": "2db0c23c-1f90-4ed9-bb13-fe18c13f9421",
    "t8": "3fa5b8f2-7813-4055-97dd-a1a303d284c5",
    "end": "5478a9d2-8786-491d-bc09-bcc3a66d71e5",
    "fiber": "cd20d2a6-a9e8-4269-991b-3a544655425e",
    "rep1": "4c694562-dae5-494c-a8f9-c7e99b016d0f",
    "two": "4044453f-6660-43c7-9c58-9499c63c2b45",
    "photo": "b4e9b124-0048-4be0-9e22-4db8f446af41",
    "empty": "553411d6-9a98-4e97-bd58-1b2b0a6d6e2c",
}
LARGE_PHOTO = MEDIA / "large_site_photo.jpg"  # 4032×3024 — gallery cell 0
OTHER_PHOTO = MEDIA / "site_photo_2.jpg"  # gallery cell 1


@pytest.fixture(scope="module")
def survey_sweep(field_services_api, tech_user_id) -> None:
    """Jobs left by an interrupted run are removed once per module."""
    with allure.step("sweep QA-AUTO jobs left on the technician"):
        field_services_api.sweep_test_jobs(tech_user_id)


@pytest.fixture
def survey_job(survey_sweep, field_services_api, tech_user_id) -> Iterator[Callable[..., SeedJob]]:
    """``survey_job(kind, status="in_progress")`` → a new job with that survey, deleted after
    the test."""
    api, run, made = field_services_api, _run_stamp(), []

    def create(kind: str, status: str = "in_progress") -> SeedJob:
        today = date.today()
        when = datetime(today.year, today.month, today.day, 9 + len(made), 0)
        job_id, title = f"QA-AUTO-{run}-S{len(made) + 1:02d}", f"QA-AUTO survey {kind}"
        with allure.step(f"seed: job {job_id} ({status}, survey {kind})"):
            created = api.create_job(
                user_id=tech_user_id, job_id=job_id, title=title, when=when, status=status,
                survey_id=SURVEYS[kind], address=ADDRESS, coordinates=COORDINATES,
            )  # fmt: skip
        job = SeedJob(kind, str(created["id"]), job_id, title, when, status)
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
            raise ApiBlocked("survey job cleanup failed:\n" + "\n".join(errors))


_GALLERY_READY: list[bool] = []  # once per run: each simctl addmedia adds new copies


@pytest.fixture
def gallery_photos(app) -> tuple[Path, Path]:
    """Two photos newest in the device gallery: cell 0 = the 4032×3024 photo, cell 1 = a small
    one."""
    if not _GALLERY_READY:
        app.add_media(OTHER_PHOTO, LARGE_PHOTO)
        _GALLERY_READY.append(True)
    return LARGE_PHOTO, OTHER_PHOTO
