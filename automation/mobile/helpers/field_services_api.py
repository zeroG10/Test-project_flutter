"""Field Services API — test-data setup and cleanup for the UI suites, nothing else.

Operations are taken verbatim from docs/api/openapi.json; the recipe and its live check are
in docs/api/dev-test-data.md. DEV-friendly (decision 2026-09-23): one admin sign-in per run,
only the calls a fixture needs, no retries.

Safety: the only destructive call, ``DELETE /user/full-delete/{id}``, is refused unless the
user's email is a test-owned address (``qa-auto+…@example.com``, fixtures/test_data.py) and
the record found by the API carries exactly that email. Shared data is never touched.
"""

import allure
import requests

from config.settings import settings
from fixtures.test_data import TEST_EMAIL_RE


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
                f"HTTP {resp.status_code}\n{resp.text[:1000]}",
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
