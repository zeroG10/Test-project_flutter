"""Job data for module 04 Order details (pytest plugin, registered in conftest.py).

| Test-case placeholder                                   | Fixture         |
|---------------------------------------------------------|-----------------|
| ``{{job.full}}``, ``{{pf.*}}``, ``{{doc.*}}``, ``{{photo.*}}`` | ``details_seed`` |
| ``{{job.reschedule}}``, ``{{job.unviewed}}``             | ``details_seed`` |

Recipe (recon 5 / 5b, 2026-09-24; owner's decisions Q-ORDD-2 and 2026-09-24): our own files go up
through ``POST /file/upload``, the jobs point to them; cleanup deletes **the files first, then the
jobs** — deleting a job first drops the file records and leaves the files in storage. Only
``QA-AUTO-*`` jobs and files are ever deleted.
"""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import allure
import pytest

from fixtures.jobs import ADDRESS, COORDINATES, SHORT_SURVEY, SeedJob, _run_stamp
from helpers.field_services_api import ApiBlocked

MEDIA = Path(__file__).parent / "media"
DESCRIPTION = "\n".join(  # as Figma `Jobs details_New` 2451:82657
    ("Inspect and secure antenna mounts.", "Replace cable entry seals.",
     "Test signal transmission levels.")
)  # fmt: skip
LONG_DESCRIPTION = "\n".join(
    f"QA-AUTO step {i}: check the item and write the result." for i in range(1, 19)
)
PF = {"name": "QA-AUTO PF Olive", "phone": "+1 202 555 0147", "email": "qa-auto+pf@example.com"}
DOCUMENTS = (("safety", "QA-AUTO safety.pdf"), ("power", "QA-AUTO power.pdf"))
PHOTOS = (("1", "QA-AUTO site 1.jpg"), ("2", "QA-AUTO site 2.jpg"))
FILES = (  # key, media file, mime
    ("pdf", "qa_auto_2_pages.pdf", "application/pdf"),
    ("photo1", "site_photo.jpg", "image/jpeg"),
    ("photo2", "site_photo_2.jpg", "image/jpeg"),
)


@dataclass(frozen=True)
class DetailsJob(SeedJob):
    description: str = DESCRIPTION


@dataclass
class DetailsSeed:
    jobs: dict[str, DetailsJob] = field(default_factory=dict)
    files: dict[str, dict] = field(default_factory=dict)
    pf: dict[str, str] = field(default_factory=lambda: dict(PF))
    documents: tuple[tuple[str, str], ...] = DOCUMENTS
    photos: tuple[tuple[str, str], ...] = PHOTOS

    def __getitem__(self, kind: str) -> DetailsJob:
        return self.jobs[kind]

    @property
    def attachment_count(self) -> int:
        return len(self.documents) + len(self.photos)


def _attachments(files: dict[str, dict]) -> dict[str, list[dict[str, str]]]:
    pdf, photo1, photo2 = (files[k]["location"] for k in ("pdf", "photo1", "photo2"))
    return {
        "documents": [
            {"url": pdf, "name": DOCUMENTS[0][1], "description": "2 pages"},
            {"url": pdf, "name": DOCUMENTS[1][1], "description": "the same file, second entry"},
        ],
        "photos": [
            {"url": photo1, "name": PHOTOS[0][1], "description": "photo 1"},
            {"url": photo2, "name": PHOTOS[1][1], "description": "photo 2"},
        ],
    }


@pytest.fixture(scope="module")
def details_seed(field_services_api, tech_user_id):
    """3 files + 3 jobs for module 04 (plan, Step 9), all deleted after it — files first."""
    api = field_services_api
    seed = DetailsSeed()
    run = _run_stamp()
    today = date.today()
    plans = {  # kind: (hour, description, extra fields)
        "full": (12, DESCRIPTION, {"project_facilitator": PF}),
        "unviewed": (13, DESCRIPTION, {"is_viewed": False}),
        "reschedule": (10, LONG_DESCRIPTION, {}),
    }
    try:
        with allure.step(f"seed: {len(FILES)} files + {len(plans)} jobs (run {run})"):
            api.sweep_test_jobs(tech_user_id)
            for key, name, mime in FILES:
                seed.files[key] = api.upload_file(MEDIA / name, f"QA-AUTO-{run}-{name}", mime)
            for kind, (hour, description, extra) in plans.items():
                when = datetime(today.year, today.month, today.day, hour, 0)
                job_id, title = f"QA-AUTO-{run}-{kind.upper()}", f"QA-AUTO {kind}"
                if kind == "full":
                    extra = {**extra, "attachments": _attachments(seed.files)}
                created = api.create_job(
                    user_id=tech_user_id, job_id=job_id, title=title, when=when, status="new",
                    survey_id=SHORT_SURVEY, address=ADDRESS, coordinates=COORDINATES,
                    description=description, **extra,
                )  # fmt: skip
                seed.jobs[kind] = DetailsJob(kind, str(created["id"]), job_id, title, when, "new",
                                             description)  # fmt: skip
        yield seed
    finally:
        errors = []
        for f in seed.files.values():  # files BEFORE the jobs that point to them (recon 5b)
            try:
                api.delete_file(f)
            except (ApiBlocked, ValueError) as exc:
                errors.append(str(exc))
        for job in seed.jobs.values():
            try:
                api.delete_job({"id": job.id, "jobId": job.job_id})
            except (ApiBlocked, ValueError) as exc:
                errors.append(str(exc))
        if errors:
            raise ApiBlocked("details seed cleanup failed:\n" + "\n".join(errors))


def moved(when: datetime) -> datetime:
    """The new schedule TC-ORDD-002 sends: +1 day, +2 hours."""
    return when + timedelta(days=1, hours=2)


def schedule_change(when: datetime) -> dict[str, str]:
    """``PATCH /job/{id}`` body moving the job to ``when`` (device-local; sent as UTC)."""
    iso = when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return {"scheduleDate": iso, "startAt": iso}
