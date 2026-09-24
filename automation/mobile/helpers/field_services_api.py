"""Field Services API — test-data setup and cleanup for the UI suites, nothing else.

Operations are taken verbatim from docs/api/openapi.json; the recipe and its live check are
in docs/api/dev-test-data.md. DEV-friendly (decision 2026-09-23): one admin sign-in per run,
only the calls a fixture needs, no retries.

Safety: the destructive calls are guarded — ``DELETE /user/full-delete/{id}`` only for a
test-owned address (``qa-auto+…@example.com``, fixtures/test_data.py) whose record carries
exactly that email; ``DELETE /job/{id}`` only for a job whose ``jobId`` starts with
``QA-AUTO-``; ``DELETE /file/{id}`` only for a file this run uploaded under a ``QA-AUTO-`` name.
Shared data is never touched.
"""

import re
import urllib.parse
from datetime import UTC, datetime
from pathlib import Path

import allure
import requests

from config.settings import settings
from fixtures.test_data import TEST_EMAIL_RE

# Response bodies go to the report: the account's personal data and any token are masked there.
_PRIVATE = re.compile(
    r'("(?:email|phone|firstName|lastName|[A-Za-z]*[Tt]oken|password)"\s*:\s*)"[^"]*"'
)


def safe_body(text: str) -> str:
    """A response body fit for the report: personal fields and tokens replaced by [REDACTED]."""
    return _PRIVATE.sub(r'\1"[REDACTED]"', text)


class ApiBlocked(RuntimeError):
    """The API could not be used (not configured, sign-in refused, unexpected status)."""


class FieldServicesApi:
    def __init__(self) -> None:
        missing = [
            key
            for key, value in (
                ("API_BASE_URL", settings.api_base_url),
                ("API_ADMIN_EMAIL", settings.api_admin_email),
                ("API_ADMIN_PASSWORD", settings.api_admin_password),
            )
            if not value
        ]
        if missing:
            raise ApiBlocked(f"Blocked: {', '.join(missing)} not set in automation/mobile/.env")
        self.base_url = settings.api_base_url.rstrip("/")
        self._http = requests.Session()
        self._http.headers["Accept"] = "application/json"
        self._signed_in = False

    # --- plumbing ---------------------------------------------------------------------

    def _sign_in(self) -> None:
        # AuthController_signInWithEmailAndPass. The response carries tokens: never attached.
        with allure.step("API POST /auth/sign-in (admin)"):
            resp = self._http.post(
                f"{self.base_url}/auth/sign-in",
                json={"email": settings.api_admin_email, "password": settings.api_admin_password},
                timeout=settings.api_timeout,
            )
            if resp.status_code not in (200, 201):
                raise ApiBlocked(f"Blocked: admin sign-in returned HTTP {resp.status_code}")
            token = (resp.json().get("access") or {}).get("token")
            if not token:
                raise ApiBlocked("Blocked: admin sign-in response has no access token")
            self._http.headers["Authorization"] = f"Bearer {token}"
            self._signed_in = True

    def _call(self, method: str, path: str, **kwargs) -> requests.Response:
        if not self._signed_in:
            self._sign_in()
        with allure.step(f"API {method} {path}"):
            resp = self._http.request(
                method, f"{self.base_url}{path}", timeout=settings.api_timeout, **kwargs
            )
            allure.attach(
                f"HTTP {resp.status_code}\n{safe_body(resp.text)[:1000]}",
                name=f"{method} {path} → {resp.status_code}",
                attachment_type=allure.attachment_type.TEXT,
            )
            return resp

    def close(self) -> None:
        self._http.close()

    # --- technicians / users --------------------------------------------------------------

    def find_technicians_by_email(self, email: str) -> list[dict]:
        """TechnicianController_findAll with ``search``; exact email match on ``user.email``."""
        resp = self._call("GET", "/technician", params={"search": email, "page": 1, "pageSize": 10})
        if resp.status_code != 200:
            raise ApiBlocked(f"Blocked: GET /technician returned HTTP {resp.status_code}")
        wanted = email.strip().lower()
        return [
            tech
            for tech in resp.json().get("data") or []
            if str((tech.get("user") or {}).get("email", "")).lower() == wanted
        ]

    def full_delete_test_user(self, email: str) -> list[str]:
        """Delete every user registered under a test-owned ``email``; returns their user ids.

        ``[]`` when nothing was registered (e.g. the test failed before submitting).
        Raises ApiBlocked when a delete fails or the user is still found afterwards —
        a failed cleanup is a harness failure, reported with the ids for manual recovery.
        """
        if not TEST_EMAIL_RE.match(email):
            raise ValueError(f"refusing to delete a non-test user: {email!r}")
        with allure.step(f"cleanup: delete test user {email}"):
            user_ids = [
                str(tech["user"]["id"])
                for tech in self.find_technicians_by_email(email)
                if (tech.get("user") or {}).get("id")
            ]
            for user_id in user_ids:
                # UserController_fullDelete — removes the user and the technician profile.
                resp = self._call("DELETE", f"/user/full-delete/{user_id}")
                if resp.status_code != 200:
                    raise ApiBlocked(
                        f"cleanup failed: DELETE /user/full-delete/{user_id} returned HTTP "
                        f"{resp.status_code} — remove {email} (user {user_id}) manually"
                    )
            if user_ids and self.find_technicians_by_email(email):
                raise ApiBlocked(
                    f"cleanup failed: {email} still found after delete (user ids {user_ids})"
                )
            return user_ids

    # --- jobs (module 03 onwards; recipe verified 2026-09-22, recon 4 2026-09-24) -------------

    TEST_JOB_PREFIX = "QA-AUTO-"

    def technician_user_id(self, email: str) -> str:
        """``user.id`` of the technician with this email (``userId`` of ``POST /job``)."""
        found = self.find_technicians_by_email(email)
        if not found or not (found[0].get("user") or {}).get("id"):
            raise ApiBlocked(f"Blocked: technician {email!r} not found through GET /technician")
        return str(found[0]["user"]["id"])

    def jobs_of_user(self, user_id: str) -> list[dict]:
        """JobController_findAll by ``userId``, every page (the response has no ``total``;
        ``pageSize`` must be ≥ 10 — docs/api/dev-test-data.md)."""
        jobs: list[dict] = []
        page = 1
        while True:
            resp = self._call(
                "GET", "/job", params={"userId": user_id, "page": page, "pageSize": 50}
            )
            if resp.status_code != 200:
                raise ApiBlocked(f"Blocked: GET /job returned HTTP {resp.status_code}")
            body = resp.json()
            batch = (body.get("data") if isinstance(body, dict) else body) or []
            jobs += batch
            if len(batch) < 50:
                return jobs
            page += 1

    def create_job(
        self,
        *,
        user_id: str,
        job_id: str,
        title: str,
        when: datetime,
        status: str = "new",
        survey_id: str,
        address: str,
        coordinates: dict[str, str],
        is_viewed: bool | None = None,
        description: str = "Created by an automated QA test and deleted by it.",
        project_facilitator: dict[str, str] | None = None,
        attachments: dict[str, list[dict[str, str]]] | None = None,
    ) -> dict:
        """JobController_create — a job already assigned to ``user_id``; returns the new job.

        ``attachments``: ``{"documents": [...], "photos": [...]}`` of ``{url, name, description}``
        (CreateJobAttachmentDto) — urls of files uploaded with ``upload_file``."""
        if not job_id.startswith(self.TEST_JOB_PREFIX):
            raise ValueError(f"test jobs must start with {self.TEST_JOB_PREFIX!r}: {job_id!r}")
        iso = when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")  # naive = device-local
        body = {
            "title": title,
            "jobId": job_id,
            "userId": user_id,
            "surveyId": survey_id,
            "statusType": status,
            "startAt": iso,
            "scheduleDate": iso,
            "description": description,
            "location": {"address": address, "coordinates": coordinates},
        }
        if is_viewed is not None:
            body["isViewed"] = is_viewed
        if project_facilitator is not None:
            body["projectFacilitator"] = project_facilitator
        if attachments is not None:
            body["attachments"] = attachments
        resp = self._call("POST", "/job", json=body)
        if resp.status_code not in (200, 201):
            raise ApiBlocked(f"Blocked: POST /job ({job_id}) returned HTTP {resp.status_code}")
        return resp.json()

    def delete_job(self, job: dict) -> None:
        """JobController_remove for a test job; verifies it is gone (GET → 404)."""
        job_id = str(job.get("jobId", ""))
        if not job_id.startswith(self.TEST_JOB_PREFIX):
            raise ValueError(f"refusing to delete a non-test job: {job_id!r}")
        with allure.step(f"cleanup: delete job {job_id}"):
            resp = self._call("DELETE", f"/job/{job['id']}")
            gone = self._call("GET", f"/job/{job['id']}").status_code == 404
            if resp.status_code != 200 or not gone:
                raise ApiBlocked(
                    f"cleanup failed: DELETE /job/{job['id']} ({job_id}) → HTTP "
                    f"{resp.status_code}, still found: {not gone} — remove it manually"
                )

    def update_job(self, job_uuid: str, job_id: str, changes: dict) -> None:
        """JobController_update on a test job (e.g. ``scheduleDate``); expects ``success``."""
        if not job_id.startswith(self.TEST_JOB_PREFIX):
            raise ValueError(f"refusing to change a non-test job: {job_id!r}")
        resp = self._call("PATCH", f"/job/{job_uuid}", json=changes)
        if resp.status_code != 200 or not (resp.json() or {}).get("success"):
            raise ApiBlocked(f"Blocked: PATCH /job ({job_id}) returned HTTP {resp.status_code}")

    # --- files (attachments of test jobs) ----------------------------------------------------

    TEST_FILE_PREFIX = "QA-AUTO-"

    def upload_file(self, path: Path, name: str, mime: str) -> dict:
        """FileController_uploadFile — returns ``{id, location, …}`` (location = public URL).

        Cleanup order matters (recon 5b): ``delete_file`` BEFORE the job that points to the file
        is deleted — deleting the job first drops the file record and leaves the file in storage."""
        if not name.startswith(self.TEST_FILE_PREFIX):
            raise ValueError(f"test files must start with {self.TEST_FILE_PREFIX!r}: {name!r}")
        resp = self._call("POST", "/file/upload", files={"file": (name, path.read_bytes(), mime)})
        if resp.status_code not in (200, 201):
            raise ApiBlocked(
                f"Blocked: POST /file/upload ({name}) returned HTTP {resp.status_code}"
            )
        return resp.json()

    def delete_file(self, file: dict) -> None:
        """FileController_deleteFile for a file this run uploaded; verifies the URL is gone."""
        if not str(file.get("originalName", "")).startswith(self.TEST_FILE_PREFIX):
            raise ValueError(f"refusing to delete a non-test file: {file.get('originalName')!r}")
        with allure.step(f"cleanup: delete file {file.get('originalName', file['id'])}"):
            resp = self._call("DELETE", f"/file/{file['id']}")
            gone = requests.head(file["location"], timeout=settings.api_timeout).status_code != 200
            if resp.status_code != 200 or not gone:
                raise ApiBlocked(
                    f"cleanup failed: DELETE /file/{file['id']} → HTTP {resp.status_code}, "
                    f"still reachable: {not gone} — {file['location']}"
                )

    def job(self, job_uuid: str) -> dict:
        """JobController_findOne — read-only; evidence of what the server holds for a job."""
        resp = self._call("GET", f"/job/{job_uuid}")
        if resp.status_code != 200:
            raise ApiBlocked(f"Blocked: GET /job/<id> returned HTTP {resp.status_code}")
        return resp.json()

    def sweep_test_jobs(self, user_id: str) -> list[str]:
        """Delete every ``QA-AUTO-*`` job left on the technician by an interrupted run."""
        left = [
            j
            for j in self.jobs_of_user(user_id)
            if str(j.get("jobId", "")).startswith(self.TEST_JOB_PREFIX)
        ]
        for job in left:
            self.delete_job(job)
        return [str(j.get("jobId")) for j in left]

    def job_link(self, phone: str) -> str:
        """JobController_jobAssign: the one-time job link for ``phone`` (``message`` of the
        response, ``https://…/redirect/<key>``). The link is what the SMS would carry; the test
        opens it in the app itself (owner, 2026-09-24)."""
        path = f"/job/assign/{urllib.parse.quote(phone, safe='')}"
        resp = self._call("POST", path)
        if resp.status_code not in (200, 201):
            raise ApiBlocked(f"Blocked: POST /job/assign/<phone> returned HTTP {resp.status_code}")
        url = str((resp.json() or {}).get("message", ""))
        if "/redirect/" not in url:
            raise ApiBlocked(f"Blocked: POST /job/assign/<phone> returned no link: {url[:80]!r}")
        return url
