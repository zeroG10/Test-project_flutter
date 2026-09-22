# Mobile automation — Appium + Python

Stack: **Appium 2 + Appium-Python-Client + pytest + Allure**, dependencies managed by **uv**.
One product per clone: a native Android app, a native iOS app, or a Flutter app
(`mobile.kind` in `setup/project.yaml`). Conventions shared with the other stacks — layers,
CHK tags, screen maps, determinism rules — live in [`automation/README.md`](../README.md);
read it first.

Two independent axes, never mixed:

| Axis | Values | Set by |
|---|---|---|
| **Platform** — the OS the driver talks to | `android` \| `ios` | `pytest --platform=…` (default `PLATFORM` in `.env`) |
| **App kind** — what the build is | `native` \| `flutter` | `APP_KIND` in `.env` |

`--platform=flutter` is rejected on purpose (`platform must be android|ios; Flutter is
APP_KIND`): a Flutter app is tested through the Android / iOS drivers — see
[Flutter strategy](#flutter-strategy).

## Structure

```
automation/mobile/
├── conftest.py            # --platform, driver fixture, marker scoping, CHK-id validation
├── config/
│   ├── settings.py        # pydantic-settings: .env → settings (PLATFORM, APP_KIND, FLUTTER_DRIVER, …)
│   └── capabilities.py    # UiAutomator2Options / XCUITestOptions (+ FlutterIntegration when opted in)
├── screens/               # screen maps: alias → locator per platform — the ONLY place a locator lives
│   ├── __init__.py        # El, Screen, resolve()
│   ├── login_map.py       # example map (placeholder ids)
│   └── README.md          # format, alias rules, Flutter note
├── pages/                 # page objects: behaviour over a screen map, explicit waits only
│   ├── base_page.py       # tap / type / visible / wait_gone / assert_open … by alias
│   ├── login_page.py      # example page
│   └── {android,ios,flutter}/   # only for flows that differ structurally per OS (rare)
├── helpers/
│   ├── waits.py           # wait_visible / wait_gone / wait_clickable / wait_text on WebDriverWait
│   ├── gestures.py        # swipe / long-press
│   └── device.py          # adb, simctl, platform_of(driver)
├── fixtures/              # static test data ({{user.email}} placeholders resolve here)
├── tests/
│   ├── shared/            # run on every --platform (parametrised by the platform fixture)
│   ├── android/  ios/     # OS-specific (marker android / ios)
│   └── flutter/           # tests specific to a Flutter build (marker flutter)
├── builds/{android,ios,flutter}/   # .apk / .app / .ipa — gitignored, see builds/README.md
├── scripts/
│   ├── doctor.sh          # prerequisites table, exit 1 on a missing required item
│   ├── start_appium.sh    # Appium server
│   └── reset_simulator.sh # erase + boot an iOS simulator
├── allure-results/        # run output (gitignored) — input for automation/tools/trace_results.py
└── pyproject.toml         # deps + pytest markers
```

## Prerequisites

| Need | Android | iOS (macOS only) | Flutter app (either OS) |
|---|---|---|---|
| **uv** (Python 3.11+) | required | required | required |
| **Node.js ≥ 18 + Appium 2** (`npm i -g appium`) | required | required | required |
| Appium driver | `appium driver install uiautomator2` | `appium driver install xcuitest` | the OS driver above; optionally `appium driver install --source=npm appium-flutter-integration-driver` |
| **Java 17** (`brew install --cask temurin@17`) | required | – | as per OS |
| **Android SDK**: Android Studio *or* cmdline-tools + `platform-tools` + `emulator` + one AVD; `ANDROID_HOME` exported | required | – | as per OS |
| **Xcode** (full app, not just Command Line Tools) + one iOS simulator runtime | – | required | as per OS |
| **Flutter SDK** (`flutter doctor` green) | – | – | only to *build* the app; not needed to run tests against a build |
| Allure CLI (`brew install allure`) | optional | optional | optional |

### `scripts/doctor.sh`

Checks all of the above and prints a table with a fix hint per row; exits 1 if a required
item is missing (WARN rows — optional tools, missing `.env`, missing build — do not fail).

```bash
bash scripts/doctor.sh             # all on macOS, android on Linux
bash scripts/doctor.sh android     # one platform
bash scripts/doctor.sh ios
bash scripts/doctor.sh --with-mcp  # also probe the `mobile` MCP server (see below)
```

Flutter rows appear only when `.env` has `APP_KIND=flutter`; the integration driver becomes
required only with `FLUTTER_DRIVER=integration`.

## Setup

```bash
cd automation/mobile
uv sync                     # installs deps into .venv
cp .env.example .env        # then edit: device, app path, package / bundle id, APP_KIND
bash scripts/doctor.sh      # fix MISSING rows before the first run
```

Drop the build into `builds/<platform>/` (see [`builds/README.md`](builds/README.md)) and
point `ANDROID_APP_PATH` / `IOS_APP_PATH` at it. A missing build makes every test
`Blocked: build not found …` — it never passes and never disappears.

### `.env` keys

| Key | Values / default | Meaning |
|---|---|---|
| `APPIUM_HOST`, `APPIUM_PORT` | `127.0.0.1`, `4723` | Appium server |
| `PLATFORM` | `android` \| `ios` | default when `--platform` is not given |
| `APP_KIND` | `native` \| `flutter` (default `native`) | what the build is |
| `FLUTTER_DRIVER` | `native` \| `integration` (default `native`) | Flutter only; `integration` needs `APP_KIND=flutter` |
| `FLUTTER_ENABLED` | **deprecated** | alias for `APP_KIND=flutter`, honoured with a warning. The old Flutter driver it used to enable is *not* the default any more — set `FLUTTER_DRIVER=integration` explicitly if you need a widget driver |
| `DEFAULT_TIMEOUT` | `15` (seconds) | explicit-wait default; there is no implicit wait |
| `ANDROID_*` | device name, OS version, app path, package, activity | UiAutomator2 caps |
| `IOS_*` | device name, OS version, app path, bundle id | XCUITest caps |

## Run

Terminal 1 — Appium server:

```bash
bash scripts/start_appium.sh
```

Terminal 2 — tests:

```bash
uv run pytest --platform=android -m smoke
uv run pytest --platform=ios -m smoke
uv run pytest --platform=android tests/android/          # one folder
uv run pytest --platform=android -m "smoke and not flutter"
uv run pytest --collect-only -q --platform=android        # what would run, no device needed
allure serve allure-results                               # report
```

Every run prints its matrix in the header
(`mobile: platform=android app_kind=native flutter_driver=- appium=http://…`) so a report can
say exactly what ran. Two platforms in parallel = two Appium servers on different ports and
two pytest processes; one process talks to one device.

## Markers and tags

| Marker | Meaning | Effect |
|---|---|---|
| `smoke`, `regression` | suite tier | select with `-m` |
| `shared` | cross-platform test | runs on every `--platform` |
| `android`, `ios` | OS-specific test | **deselected** when `--platform` does not match |
| `flutter` | test specific to a Flutter build | **deselected** unless `APP_KIND=flutter` |
| `chk("CHK-AUTH-001", …)` | checklist item(s) this test proves | validated at collection against `CHK-[A-Z]{2,5}-\d{3,}`; exported to JUnit `<property name="chk">` |
| `quarantine` | parked flaky / defect-blocked test | reason MUST carry a `BUG-<CODE>-NNN` id + a row in the quarantine register (`.github/GATES.md`); CI runs `-m "smoke and not quarantine"` |

Deselection (not skip) is deliberate: a run where nothing remains exits 5 ("no tests
collected"), which CI treats as red — an empty run is not a passing run. Use plain `-m`
filters for narrower selections. A test that *is* collected and then skipped is Blocked:
with `CI` set (or `QA_STRICT_SKIPS=1`) the run exits 1 and lists the skips (`conftest.py`).

Each test carries its CHK ids twice — once for pytest, once for Allure — as in
[`tests/shared/test_smoke_example.py`](tests/shared/test_smoke_example.py):

```python
@pytest.mark.smoke
@pytest.mark.shared
@pytest.mark.chk("CHK-AUTH-001")
@allure.tag("CHK-AUTH-001")
@allure.title("CHK-AUTH-001 App launches and shows the login screen")
def test_app_launches_to_login(driver, platform):
    LoginPage(driver, platform).assert_open()
```

A malformed id (`CHK-auth-1`, a marker without an id) fails collection: an untraceable test
would otherwise report "not run" forever without anyone noticing.

## Flutter strategy

Flutter is an **app kind**, not a platform. Default (`APP_KIND=flutter`, `FLUTTER_DRIVER=native`):

- The app is driven by the **native drivers** (UiAutomator2 / XCUITest) exactly like a native
  app. Nothing else changes — same `--platform`, same caps, same screen maps.
- Developers wrap testable widgets in `Semantics(identifier: "login-email", child: …)`.
  Flutter ≥ 3.19 exposes the identifier as `resource-id` on Android and
  `accessibilityIdentifier` on iOS, so `El(android=(AppiumBy.ID, "login-email"), ios=(AppiumBy.ACCESSIBILITY_ID, "login-email"))` works on **release** builds.
  Missing identifiers are a testability defect, like missing test-ids on web.
- `flutter build apk` / `flutter build ios --simulator`, drop the result in
  `builds/android/` / `builds/ios/` (`builds/README.md`).

Opt-in fallback (`FLUTTER_DRIVER=integration`), for **debug** builds only:

- automationName becomes `FlutterIntegration` (`appium-flutter-integration-driver`, install
  with `appium driver install --source=npm appium-flutter-integration-driver`). The build must
  compile in the `appium_flutter_server` package.
- Screen maps may add a `flutter=(AppiumBy.FLUTTER_INTEGRATION_KEY, …)` locator per element;
  elements without one keep using their `android=` / `ios=` locator (the driver proxies
  native strategies). Keep these builds in `builds/flutter/`.
- `FLUTTER_DRIVER=integration` without `APP_KIND=flutter` is a configuration error and
  settings refuse to load.

Tests that only make sense on a Flutter build (widget-tree checks, semantics audits) go to
`tests/flutter/` with `@pytest.mark.flutter`.

## Reading real screens — the `mobile` MCP server

The web stack has a crawler (`npm run pw:recon`) that walks the app and harvests locators.
**Mobile has no crawler**: the equivalent is the `mobile` MCP server
(`@mobilenext/mobile-mcp`, configured in `.mcp.json`), which lets an agent drive a booted
simulator / emulator / real device and read its **accessibility tree** — the element ids as
the OS reports them, not a screenshot to guess from.

Use it for three things, none of which is running tests:

1. **Screen recon** — open the app, walk the flows, record what screens and elements exist.
2. **Harvesting ids for screen maps** — `mobile_list_elements_on_screen` returns each
   element with its accessibility id / text / coordinates. A Flutter `Semantics(identifier:)`
   shows up here, which is how you confirm the dev team actually shipped it
   (`screens/README.md` → "Harvesting ids from a real screen").
3. **Exploratory sessions** — SBTM charters from `qa/_templates/exploratory-session.md`;
   findings feed bugs and invariants back into the chain.

```bash
python3 ../../setup/check_mcp.py mobile   # verify the server answers (no device needed)
bash scripts/doctor.sh --with-mcp         # same check as a doctor row
```

Then boot a device (`xcrun simctl boot <name>` / `emulator -avd <name>`) — the server needs
one to report anything useful.

> **The MCP server is discovery only. The gate is always this pytest + Appium suite.**
> Same rule as web recon: what an agent explored by hand proves nothing until a tagged,
> repeatable test asserts it (`automation/README.md` → Determinism rules).

If the server fails to start with `MODULE_NOT_FOUND`, the npx cache is corrupt, not your
setup: `rm -rf ~/.npm/_npx` and re-verify (`setup/SETUP.md` §3).

## Screen maps and page objects

- `screens/<screen>_map.py` — alias → `(strategy, value)` per platform; rules in
  [`screens/README.md`](screens/README.md). Aliases match the web map for the same screen, so
  one test case in `qa/mobile/<NN-module>/<module>-test-cases.md` serves both stacks.
- `pages/<screen>_page.py` — behaviour only (`LoginPage(driver).login(email, pw)`); every
  action is an alias call on `BasePage` (`tap`, `type`, `visible`, `wait_gone`,
  `expect_text`, `assert_open`).
- `helpers/waits.py` — the only waits in the stack: `WebDriverWait` with
  `settings.default_timeout`. No `sleep`, no implicit wait (the driver fixture sets none, so
  explicit and implicit waits never stack).

## Builds folder

`builds/android/` (`.apk`), `builds/ios/` (`.app` simulator bundle or `.ipa` device build),
`builds/flutter/` (integration-driver debug builds only). Gitignored; details and the Flutter
build commands in [`builds/README.md`](builds/README.md).

## From run results to traceability

`automation/tools/trace_results.py` (shared with the API stack) closes the loop: it reads the
run output, extracts the CHK ids from the tags and writes the automated verdict per CHK id into
`qa/mobile/<NN-module>/<module>-traceability.md`. This stack produces two machine-readable sources for it:

- `allure-results/*-result.json` — `labels: [{"name": "tag", "value": "CHK-AUTH-001"}]` + status
  (from `@allure.tag`).
- `--junitxml=results.xml` — `<property name="chk" value="CHK-AUTH-001"/>` per test (from
  `@pytest.mark.chk`, written by `conftest.py`).

A CHK id with no tagged test is **not run**, never green; a deselected or errored test is
`Blocked`, never `Passed`.

## What this stack refuses to do (QA Doctrine, `CLAUDE.md`)

- Pass without an oracle: every action waits for a concrete element from the map; a missing
  anchor is a red `TimeoutException` with a screenshot and page source attached.
- Turn "could not run" into green: missing build, dead Appium server, wrong `--platform`,
  malformed CHK id, nothing selected — each is a loud failure with the reason in the message.
- Hide locators in tests or pages: they live in `screens/` only, and structural strategies
  (xpath / css / class-name) are rejected when the map is imported.

## CI

`.github/workflows/mobile-android-tests.yml` and `mobile-ios-tests.yml` run
`uv run pytest --platform=<os> -m smoke` after placing the build in `builds/`; gates and
their status are in `.github/GATES.md`. `lint.yml` runs `ruff check` + `ruff format --check`
on this folder.
