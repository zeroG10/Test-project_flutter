"""IDOR / broken-object-level-authorization matrix — the #1 QA-findable, high-impact
API security bug class.

For each protected resource owned by USER A, assert:
  - USER A (owner)      → can read it            (200)
  - USER B (other user) → CANNOT read it         (403/404, NEVER 200)
  - anonymous           → CANNOT read it         (401/403, NEVER 200)

A 200 for USER B on USER A's resource IS an IDOR — file it with severity S1
(severity tree branch 1: another user's data leaked). This test is read-only:
it proves the flaw by READING, never by mutating.

Config (in automation/api/.env, read through config/settings.py), skipped-loud until set:
  USER_A_TOKEN, USER_B_TOKEN
  IDOR_RESOURCES     = ';'-separated GET path templates with {id}, e.g. /orders/{id};/profile/{id}
  IDOR_RESOURCE_IDS  = ';'-separated ids owned by USER A, aligned with IDOR_RESOURCES
"""

import allure
import pytest

from clients.base_client import ApiClient
from config.settings import settings


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def _missing_config() -> list[str]:
    """Names of the .env variables that are still empty — quoted verbatim in the skip reason."""
    required = {
        "USER_A_TOKEN": settings.user_a_token,
        "USER_B_TOKEN": settings.user_b_token,
        "IDOR_RESOURCES": settings.idor_resources,
        "IDOR_RESOURCE_IDS": settings.idor_resource_ids,
    }
    return [name for name, value in required.items() if not value.strip()]


def _matrix() -> list[tuple[str, str]]:
    """Build (path_template, resource_id) pairs from settings, or [] while unconfigured."""
    if _MISSING:
        return []
    resources = _split(settings.idor_resources)
    ids = _split(settings.idor_resource_ids)
    # strict=True: a mismatched matrix is a config error that fails collection (red),
    # not a silently shorter test run (that would be a fabricated pass).
    return list(zip(resources, ids, strict=True))


_MISSING = _missing_config()
_MATRIX = _matrix()

# A skip here is `Blocked`, not a pass — the reason names exactly what is missing.
pytestmark = pytest.mark.skipif(
    bool(_MISSING),
    reason=(
        "BLOCKED — IDOR matrix not configured: missing "
        + ", ".join(_MISSING)
        + " in automation/api/.env"
    ),
)


def _path(template: str, rid: str) -> str:
    return template.replace("{id}", rid)


@pytest.mark.security
@pytest.mark.parametrize("template,rid", _MATRIX)
@allure.title("Owner CAN read own resource: {template}")
def test_owner_can_read(template, rid):
    with ApiClient(token=settings.user_a_token) as owner:
        resp = owner.get(_path(template, rid))
    assert resp.status_code == 200, (
        f"Owner cannot read own resource {_path(template, rid)} "
        f"(got {resp.status_code}) — fix the fixture before trusting the IDOR result."
    )


@pytest.mark.security
@pytest.mark.parametrize("template,rid", _MATRIX)
@allure.title("Other user CANNOT read another user's resource: {template}")
def test_other_user_denied(template, rid):
    with ApiClient(token=settings.user_b_token) as other:
        resp = other.get(_path(template, rid))
    assert resp.status_code in (403, 404), (
        f"IDOR: USER B got {resp.status_code} on USER A's {_path(template, rid)} "
        "(expected 403/404). A 200 here leaks another user's data — severity S1."
    )


@pytest.mark.security
@pytest.mark.parametrize("template,rid", _MATRIX)
@allure.title("Anonymous CANNOT read a protected resource: {template}")
def test_anonymous_denied(template, rid):
    with ApiClient(token="") as anon:
        resp = anon.get(_path(template, rid))
    assert resp.status_code in (401, 403), (
        f"Unauthenticated request got {resp.status_code} on {_path(template, rid)} "
        "(expected 401/403). A 200 here is a broken auth gate."
    )
