# API Automation — Python + pytest + httpx

Stack: **httpx + pytest + Allure**, dependencies managed by **uv**.

Shared between Web and Mobile — your backend API is the same surface from both clients.

## Setup

```bash
cd automation/api
uv sync
cp .env.example .env       # set API_BASE_URL (required — the session refuses to start without it), tokens, etc.
```

`.env` is loaded by `conftest.py` (`load_dotenv`) before `config.settings` is imported,
so both `settings.*` and any direct `os.getenv(...)` in a test see the same values.
A real environment variable (e.g. a CI secret) always wins over the file.

## Run

```bash
# All tests
uv run pytest

# Smoke only
uv run pytest -m smoke

# Security module (headers/CORS + IDOR matrix) — see tests/security/README.md
uv run pytest -m security

# Contract / schema tests — see note below
uv run pytest -m contract

# Against a different environment (dev/staging only — production is never a target)
API_ENV=dev API_BASE_URL=https://api.dev.example.com uv run pytest -m smoke
```

`API_BASE_URL` is fail-closed like `BASE_URL` in the web stack: empty or still the `<…>`
placeholder → `conftest.py` stops the session before any test with a `Blocked` message
(exit 4). A run without a target is not a run.

> **`tests/contract/` ships empty** (only `__init__.py`). Until you add JSON Schemas to
> `schemas/` and tests to `tests/contract/`, `uv run pytest -m contract` collects nothing
> and exits with code **5** — that is red, not green: an empty run is not a passing run
> (doctrine rule 3). Do not wire `-m contract` into CI as a required check before it has
> at least one real test.

## Reports

```bash
allure serve allure-results
```

## Structure

```
automation/api/
├── pyproject.toml         # deps + pytest config (markers, --strict-markers)
├── .env.example           # API_BASE_URL, tokens, env label, security-module vars
├── conftest.py            # loads .env, shared fixtures (api client, allure labels)
├── config/                # pydantic-settings (settings.py — incl. security-module fields)
├── clients/               # ApiClient (httpx wrapper) — extend with resource-specific clients
├── tests/
│   ├── smoke/             # critical happy-path
│   ├── contract/          # schema validation against OpenAPI (ships empty — see Run)
│   └── security/          # [module] headers/CORS + IDOR access-control matrix (-m security)
├── schemas/               # JSON Schemas (or pydantic models) for contract tests
├── helpers/
│   ├── schema_validator.py  # validate_schema(payload, schema) → AssertionError + Allure attach
│   └── retry.py             # retry_on_transport_error — transport/timeout only, never verdicts
└── fixtures/              # static test data (no secrets)
```

## Markers

All markers are registered in `pyproject.toml` and enforced by `--strict-markers` —
an unregistered marker fails the run instead of silently doing nothing.

- `smoke` — run on every PR
- `regression` — full suite
- `contract` — validates responses against OpenAPI/JSON Schema (folder ships empty)
- `auth` — requires valid token
- `security` — grey-box security checks (headers, CORS, IDOR/access-control); optional module
- `slow` — > 5s tests
- `chk(id)` — checklist item this test proves, e.g. `CHK-AUTH-001` (see Tagging). Validated at
  collection against the canonical `CHK-[A-Z]{2,5}-\d{3,}` — a malformed id fails the run
  instead of silently never being traced
- `quarantine` — parked flaky / defect-blocked test; the reason MUST carry a `BUG-<CODE>-NNN`
  id and the test a row in the quarantine register of `.github/GATES.md`. CI runs
  `-m "smoke and not quarantine"`; locally the test still runs

**CI strict-skip.** With `CI` set (GitHub sets it) or `QA_STRICT_SKIPS=1`, a run that
skipped any test exits 1 and lists the skips: a skip is Blocked, never green
(`conftest.py`, GATES.md rule 2). Locally the same block prints as advisory.

## Tagging (CHK IDs — the contract between checklist and code)

Per [automation/README.md](../README.md), every test carries the checklist IDs it proves
in a machine-readable place. For pytest that is **both** a marker (filtering, traceability)
and an Allure tag (report):

```python
import allure
import pytest


@pytest.mark.smoke
@pytest.mark.chk("CHK-AUTH-001")
@allure.tag("CHK-AUTH-001")
@allure.title("Login with valid credentials returns a token")
def test_login_ok(api):
    ...
```

- One test may prove several IDs — stack the decorators (`@pytest.mark.chk("CHK-AUTH-001")`,
  `@pytest.mark.chk("CHK-AUTH-002")`, and matching `@allure.tag(...)` calls).
- Filter by tag: `uv run pytest -m chk` runs everything that proves a checklist item.
- The traceability step reads these tags from the run output and writes the automated
  verdict per CHK ID. A CHK ID with **no tagged test is "not run", never green**.
- Example in place: [tests/smoke/test_health_example.py](tests/smoke/test_health_example.py)
  (uses the placeholder `CHK-API-001` — replace with the real ID from the module checklist, `qa/{web,mobile}/<NN-module>/<module>-checklist.md`, or a shared one in `qa/shared/checklists/`).

## Patterns

### Adding a new resource client

Create `clients/users_client.py`:

```python
from clients.base_client import ApiClient

class UsersClient(ApiClient):
    def get_user(self, user_id: str):
        return self.get(f"/users/{user_id}")

    def create_user(self, payload: dict):
        return self.post("/users", json=payload)
```

### Contract test against OpenAPI

Drop the JSON Schema in `schemas/users_get.json`, then:

```python
import json
from pathlib import Path
from helpers.schema_validator import validate_schema

def test_user_response_matches_schema(api):
    response = api.get("/users/123")
    schema = json.loads((Path(__file__).parent.parent.parent / "schemas/users_get.json").read_text())
    validate_schema(response.json(), schema)
```

### Retrying a flaky transport (not a flaky verdict)

`helpers/retry.py` exposes `retry_on_transport_error` (tenacity, max 3 attempts,
exponential backoff). It retries **only** `httpx.TransportError` / `httpx.TimeoutException`
— never an assertion failure and never a 4xx/5xx response, because a retry that hides a
failure is a fabricated pass. Wrap the request, keep the assertion outside:

```python
from helpers.retry import retry_on_transport_error

@retry_on_transport_error
def get_health(api):
    return api.get("/health")

def test_health(api):
    assert get_health(api).status_code == 200
```

If every attempt fails, the original httpx exception is re-raised — the test errors
(Blocked), it does not pass.

## Source of API spec

Place OpenAPI / Swagger / Postman collections in [docs/api/](../../docs/api/) — that's the contract this test suite validates against.

## Diagnostic data

`helpers/reporting.py`: `response_summary()` and `expect_status()` redact sensitive fields before reporting.
Tokens, cookies, passwords and common secret fields are masked recursively; add product
fields through `QA_REDACT_FIELDS` (comma-separated names, including personal-data fields
where needed). Request URL query values and credentials are hidden. Unstructured bodies
are omitted; JSON is redacted before truncation. Assertions receive the original response.
Use these helpers instead of printing raw response bodies in assertion messages.
This does not sanitise arbitrary test prints, framework exception introspection, browser
traces, screenshots or videos; handle those artifacts according to the project data policy.

Offline helper checks (from `automation/api`, after `uv sync`; no product requests, no
report files, no target needed). `unittest`, not pytest: `conftest.py` refuses a pytest
session without `API_BASE_URL`, and these tests exercise pure helpers. They run in CI as
part of gate G-5 (`.github/workflows/lint.yml`), so a helper that starts leaking a secret
turns the gate red.

```bash
uv run python -m unittest discover -s unit_tests -v
```
