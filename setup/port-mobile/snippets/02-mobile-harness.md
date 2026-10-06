# The mobile harness — files the template already has (merge by hand)

The template has its own (older) versions of these files. For each: take what the middle column names from this
project's file, keep what the right column names from the template's. Paths are relative to `automation/mobile/`.

| File | Take from this project | Keep / re-apply in the template |
|---|---|---|
| `conftest.py` | all of it: `--prove-red` + `expected`, `apply_platform()` in `pytest_configure`, the account fingerprint in the header, a session per module on Android and its revival, `AnrBlocked`, `chk_skipped_on`, screen video, Allure context, run files | **`pytest_plugins = ["fixtures.network"]`** — this project's list names its app's fixture modules |
| `config/settings.py` | all of it: an account and an Appium port per platform (`IOS_USER_*`, `ANDROID_USER_*`, `IOS_APPIUM_PORT`, `ANDROID_APPIUM_PORT`), `apply_platform()`, `run_tag`, `account_key()`, `can_run_in_parallel()`, `android_emulator_args`, `app_link_domain`, `evidence_video` | the template's example defaults (device names, OS versions) |
| `config/capabilities.py` | all of it (`ANDROID_SERIAL` → `udid`, the install / server timeouts, `waitForIdleTimeout`) | — |
| `.env.example` | the per-platform account block, the parallel-run block, `APP_LINK_DOMAIN`, `EVIDENCE_VIDEO` | the template's example values |
| `helpers/device.py`, `helpers/waits.py`, `pages/base_page.py` | all of it (section 1 of PORT-MOBILE.md) | — |
| `screens/__init__.py`, `screens/README.md` | all of it (the Android column, `InAppBar`, `EditTextByHint`, the app-bar bound) | — |
| `scripts/start_appium.sh` | all of it (a server per platform) | — |
| `scripts/doctor.sh` | — (this project did not change it) | the template's version |
| `pyproject.toml` | dependencies: `pillow` (pixel oracles), `python-dotenv`; the `chk_skipped_on`, `e2e` markers | the template's other entries |
| `README.md` | the sections **Session model and app-state fixtures**, **Evidence**, **Allure report**, **Test completion reports**, **Prove red**, **Android specifics**, **Offline self-test**; the *Run* section's "One command" block; the new rows of the `.env` keys table | the template's folder tree and examples (this project's tree names its app's maps) |
| `helpers/app.py` (new to the template) | app control: cold start, clear data (+ permissions again on Android), location (simulator / emulator), media into the gallery, theme, links | **adapt**: `MOCK_SWITCH` / `THEME_KEY` are this app's preference keys and the first-screen text check is this app's — make them settings or remove |
| `fixtures/test_data.py` | the generated-data rules (reserved ranges, the `qa-auto+` marker, `_stamp()`), `Tech` from `settings.account()` | **adapt**: `free_fictional_national()` needs the product's API (`phone_in_use`) |
| `fixtures/app_state.py` | — the pattern only (README *Session model*): a fixture per test-case precondition | it is this app's sign-in flow |
| `unit_tests/test_harness.py`, `test_screen_maps.py`, `test_android_maps.py` | the checks | the maps, modules and dumps they name are this project's — keep them pointing at the template's example map |

New, project-side hook the template only documents: `helpers/account_names.py` (`account_names() -> list[str]`) —
the test accounts' names for the reports' privacy check when they are not in `.env` (`*_USER_NAME`).
