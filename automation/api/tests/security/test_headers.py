"""Passive header / cookie / CORS checks — the fast automatable security win.

Read-only, safe to run repeatedly. Adjust the endpoint and the expected policy to
the project; the defaults are conservative starting points, not a universal spec.
A finding here is usually S3 (severity tree branch 3); a missing auth-related header
on an authenticated endpoint can be higher — judge per the severity tree.
"""

import allure
import pytest

# Headers whose ABSENCE is a finding on a browser-facing response.
EXPECTED_SECURITY_HEADERS = {
    "strict-transport-security",
    "x-content-type-options",
    "content-security-policy",
}


@pytest.mark.security
@allure.title("Security response headers are present")
def test_security_headers_present(api):
    # TODO: point at a real browser-facing endpoint of the API.
    resp = api.get("/health")
    present = {h.lower() for h in resp.headers}
    missing = sorted(EXPECTED_SECURITY_HEADERS - present)
    assert not missing, (
        f"Missing security headers: {missing}. "
        f"Oracle: OWASP Secure Headers project. Present headers: {sorted(present)}"
    )


@pytest.mark.security
@allure.title("x-content-type-options is nosniff")
def test_nosniff(api):
    resp = api.get("/health")
    value = resp.headers.get("x-content-type-options", "").lower()
    assert value == "nosniff", f"expected 'nosniff', got '{value or '(absent)'}'"


@pytest.mark.security
@allure.title("CORS does not reflect an arbitrary Origin with credentials")
def test_cors_not_wildcard_with_credentials(api):
    # A server that reflects any Origin AND allows credentials is an open door.
    resp = api.get("/health", headers={"Origin": "https://evil.example.com"})
    acao = resp.headers.get("access-control-allow-origin", "")
    acac = resp.headers.get("access-control-allow-credentials", "").lower()
    reflects_evil = acao == "https://evil.example.com" or acao == "*"
    assert not (reflects_evil and acac == "true"), (
        f"CORS reflects Origin '{acao}' with credentials allowed — "
        "any site could make authenticated cross-origin requests."
    )
