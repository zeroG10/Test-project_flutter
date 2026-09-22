"""Redacted diagnostics only: never change the response that a test asserts on.

QA_REDACT_FIELDS adds comma-separated JSON/header field names (case/underscore/hyphen
insensitive). Non-JSON bodies are omitted because arbitrary text cannot be reliably
classified. Framework traces and arbitrary test prints are outside this helper.
"""

import json
import os
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

REDACTED = "[REDACTED]"
_FIELDS = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "password",
    "passwd",
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "api_key",
    "x-api-key",
    "secret",
    "client_secret",
    "session",
    "session_id",
    "csrf",
    "x-csrf-token",
}


def _normalise(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def _fields() -> set[str]:
    return _FIELDS | {s.strip() for s in os.getenv("QA_REDACT_FIELDS", "").split(",") if s.strip()}


def sensitive(key: str) -> bool:
    name = _normalise(key)
    return name in {_normalise(k) for k in _fields()} or name.endswith(
        ("token", "secret", "password", "apikey")
    )


def safe_text(value: str) -> str:
    """Mask common credentials embedded in otherwise useful diagnostic strings."""
    value = re.sub(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+", r"\1 [REDACTED]", value)
    keys = "|".join(re.escape(k) for k in sorted(_fields(), key=len, reverse=True))
    pattern = rf"(?i)([\"']?(?:{keys})[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;&}}]+)"
    return re.sub(pattern, lambda m: m[1] + REDACTED, value)


def redact(value: object) -> object:
    if isinstance(value, dict):
        return {k: REDACTED if sensitive(str(k)) else redact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    return safe_text(value) if isinstance(value, str) else value


def safe_url(value: str) -> str:
    """Keep route and query names, omit URL credentials, query values and fragments."""
    try:
        url = urlsplit(value)
        query = urlencode(
            [(key, REDACTED) for key, _ in parse_qsl(url.query, keep_blank_values=True)]
        )
        return safe_text(
            urlunsplit((url.scheme, url.netloc.rsplit("@", 1)[-1], url.path, query, ""))
        )
    except ValueError:
        return "[URL omitted]"


def response_summary(response: httpx.Response) -> str:
    try:
        body = response.json()
        rendered = (
            json.dumps(redact(body), ensure_ascii=False)
            if isinstance(body, (dict, list))
            else "[non-structured body omitted]"
        )
    except ValueError:
        rendered = "[non-JSON body omitted]"
    headers = {
        key: REDACTED
        if sensitive(key)
        else safe_url(value)
        if key.lower() == "location"
        else safe_text(value)
        for key, value in response.headers.items()
    }
    return f"status: {response.status_code}\nheaders: {headers}\nbody: {rendered[:2000]}"


def expect_status(response: httpx.Response, expected: int, operation: str) -> httpx.Response:
    """Exact, contract-derived status for tests or cleanup; negative tests can expect 403 etc."""
    if response.status_code != expected:
        raise AssertionError(
            f"{safe_url(operation)} expected {expected}\n{response_summary(response)}"
        )
    return response
