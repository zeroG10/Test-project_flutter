# Test cases — Splash (mobile)

> Structured, alias-based test cases for the CHK IDs selected in
> [splash-automation-plan.md](splash-automation-plan.md). Format:
> [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) ·
> [qa/_templates/test-cases-mobile.md](../../_templates/test-cases-mobile.md) · prompt `prompts/mobile/03`.
> **Status: draft for the owner's validation — not automated yet.**

| Field | Value |
|---|---|
| Feature | Splash — the start-up screen and where it hands over |
| Platform | cross-platform (Flutter app driven by native drivers) — iOS first, then Android |
| Source checklist | `qa/mobile/01-splash/splash-checklist.md` (CHK-SPL-001…015) |
| Selection | `qa/mobile/01-splash/splash-automation-plan.md` → Selected CHK IDs (9) |
| Min OS | iOS 16.0 / Android 12.1 (SRS §2.4) — not run by decision; see [supported-devices.md](../../../docs/platform-specs/supported-devices.md) |
| Devices | iPhone 17 · iOS 26.5 (simulator); Pixel 7 · Android 15 / API 35 (emulator) — [device matrix](../../shared/device-matrix/device-matrix.md) |
| Build | `[DEV] CT Mobile` 1.1.1 (178), flavor `development`, `CLIENT_BUILD=true` |
| Owner | @mykola.zhuchenko |
| Last updated | 2026-09-23 |

Execution statuses: **Passed / Failed / Skipped / Blocked / (empty)** — results go to `ios/` / `android/splash-traceability.md`
(via `trace_results.py`), never into this file.

**Conventions used in this file** (as in the Auth test cases)

- **Priority:** P0 = smoke, every run · P1 = release regression · P2 = full suite · P3 = edge / scheduled.
- **Oracle model:** accepted production baseline (`docs/notes/decisions.md`, 2026-09-23). Where the SRS / checklist and
  the app disagree, the TC asserts the app — D-SPL-1…4 accepted by the owner on 2026-09-23
  ([splash-questions.md](splash-questions.md)).
- **The splash has no labelled element.** `splash.root` and `splash.logo` are decided by **pixels** of a screenshot
  (brand colour `#782A2A` from Figma `Spalsh` 2451:82537 and the app theme); `splash.interactive` is decided by the
  **tree** (no text, button or field). A splash check that cannot be observed inside the splash window is
  **Blocked** — never Passed.

---

## TC-SPL-001 — Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself

| Field | Value |
|---|---|
| ID | TC-SPL-001 |
| Title | Without a session, a cold start shows the brand splash with a centred logo and nothing to interact with, then opens Welcome by itself |
| Source CHK IDs | CHK-SPL-001, CHK-SPL-002, CHK-SPL-003, CHK-SPL-005, CHK-SPL-011 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted (system alert auto-accepted) |
| Network | online Wi-Fi |
| Preconditions | no session; the app is terminated |
| Oracle | spec — SRS §3.1.0 UI Description, FR-SPL-01, FR-SPL-03, FR-SPL-04; spec — figma:2451:82537 (`Spalsh`: fill `#782A2A`, logo 128×128 centred), figma:2451:83867 (`Spalsh animation`); spec — SRS §3.1.1.1 FR-WEL-03 (Welcome when not authenticated); accepted baseline D-SPL-2, D-SPL-3 (owner, 2026-09-23) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | — |
| 2 | expect-visible | splash.root | — | the first captured frame: ≥ 90 % of the screen is the brand colour `#782A2A` (D-SPL-2) |
| 3 | expect-hidden | splash.interactive | — | no text, button, link or input in the tree |
| 4 | expect-visible | splash.logo | — | the logo appears (debug build: ~8 s after launch); its centre within 2 % of the screen centre (both axes) |
| 5 | wait-for | welcome.root | — | appears without any input |
| 6 | expect-visible | welcome.root | — | visible — Welcome, not Login (D-SPL-3) |
| 7 | expect-hidden | login.root | — | hidden |

**Postconditions / cleanup:** nothing to clean.
**Notes:** recon 4 (2026-09-24, debug build): the first screenshot comes 2.2–3.4 s after launch and is already 99.8 %
brand colour; the logo appears at ~8 s (centre within 0.5 %); Welcome after ~9 s; the tree holds no text / button /
field during the splash. The debug build starts far slower than the code's 2.0 s + 0.8 s — step 3 waits for the logo.
If a step cannot be observed inside the splash, the TC is **Blocked (timing)**, never Passed. The logo step comes
after the interactions because in the debug build the logo is drawn only at the end of the splash (recon 4). The long press on the logo is **not** used: in the `development`
flavour it opens the debug screen by design (D-SPL-4). The logo animates while it grows (fade, scale, a half turn);
its centre does not move, so step 3 holds at any moment of the animation.
**Android (step 4 of the Android stage, 2026-09-29):** step 2 is the first brand frame **after** the system splash
(Q-SPL-A1); step 5 is the **system Back**, and "nothing happens" also means "the app stays in the foreground" — checked
over a 1.5 s window after step 7, because the frame right after Back still shows the splash while Android is already
leaving the app (Q-SPL-A2 → BUG-SPL-002). After a system splash of 4–32 s the brand splash is up for only about a second on the test
host — less than a tree read plus a screenshot — so on Android the steps run over two cold starts: start 1 — step 2,
step 7 on that first brand frame (the logo is drawn from it), step 4, then step 3, where the tree proves by itself that
it was read during the splash (no text at all; the Welcome title in it → Blocked, timing); start 2 — step 2, then step 5
(the system Back) at once, then the 1.5 s window of step 6 and steps 8–10.
**Split (owner «ок», 2026-10-01):** the interaction steps (old 4–6, CHK-SPL-007) moved to **TC-SPL-005**, so the one red
item on Android (the system Back — BUG-SPL-002) no longer turns the other five red. The notes above keep the old step
numbers; on Android this TC is now start 1 without the tap: the first brand frame, the logo on it, the tree.

---

## TC-SPL-005 — A tap and a back on the splash change nothing; the app goes on to Welcome by itself

| Field | Value |
|---|---|
| ID | TC-SPL-005 |
| Title | A tap and a back on the splash change nothing; the app goes on to Welcome by itself |
| Source CHK IDs | CHK-SPL-007 |
| Platforms | ios, android |
| Priority | P0 |
| Automation | automated(ios, android) — `tests/shared/test_splash.py::test_splash_ignores_interaction` |
| Device / OS | P0 devices from the matrix |
| App state | cold start; app data reset (logged out) |
| Permissions | notifications: granted (system alert auto-accepted) |
| Network | online Wi-Fi |
| Preconditions | no session; the app is terminated |
| Oracle | spec — SRS §3.1.0 FR-SPL-03 ("The Splash Screen shall not require or allow any user interaction."); spec — checklist CHK-SPL-007 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | — |
| 2 | expect-visible | splash.root | — | the brand splash (Android: the first brand frame after the system splash) |
| 3 | click | splash.root | screen centre | nothing happens |
| 4 | back | — | edge swipe (iOS) / the system Back (Android) | nothing happens; the app stays in the foreground |
| 5 | expect-visible | splash.root | — | still the splash — steps 3–4 changed nothing |
| 6 | wait-for | welcome.root | — | Welcome by itself, no input |

**Postconditions / cleanup:** nothing to clean.
**Notes:** split from TC-SPL-001 on the owner's word (2026-10-01) — its old steps 4–6. On Android the steps run over two
cold starts: start 1 — step 2, then step 4 (the system Back) at once; step 5 becomes "the app stays in the foreground"
over a 1.5 s window (the frame right after Back can still show the splash while Android leaves the app); start 2 — step 2,
step 3, then the tree (no text at all: still the splash, the tap opened nothing). The Back goes first: it does not
depend on how fast the tree is read (run 01-split-r1: a late tree read Blocked the TC before the Back was tried). **Red on Android
against BUG-SPL-002.**

---

## TC-SPL-002 — With a valid session, the splash hands over to the Jobs list and Welcome never appears

| Field | Value |
|---|---|
| ID | TC-SPL-002 |
| Title | With a valid session, the splash hands over to the Jobs list and Welcome never appears |
| Source CHK IDs | CHK-SPL-008, CHK-SPL-012 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | terminated after sign-in → cold start |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | signed in as `{{tech.email}}` (session created by the `ui_login` fixture) |
| Oracle | spec — SRS §3.1.0 FR-SPL-02, FR-SPL-04; spec — SRS §3.1.1.1 FR-WEL-04 |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | expect-visible | jobs-list.root | — | visible (session active) |
| 2 | open | app | terminate, then cold start | — |
| 3 | wait-for | jobs-list.root | — | appears without any input; the screen is polled from the launch on |
| 4 | expect-hidden | welcome.root | — | never seen while waiting in step 3 |
| 5 | expect-visible | tabbar.jobs | — | the signed-in shell (bottom navigation) is shown |

**Postconditions / cleanup:** reset app data (sign out) unless the next test needs the session.
**Notes:** with a session the app leaves the splash after ~0.8 s — too short to assert the splash itself reliably; the
splash's own look is proven by TC-SPL-001. Overlaps TC-AUTH-003 by design (plan, Step 11).

---

## TC-SPL-003 — A session whose account was deleted on the server ends on Welcome after a cold start

| Field | Value |
|---|---|
| ID | TC-SPL-003 |
| Title | A session whose account was deleted on the server ends on Welcome after a cold start |
| Source CHK IDs | CHK-SPL-009 |
| Platforms | ios, android |
| Priority | P1 |
| Automation | candidate |
| Device / OS | P0 devices from the matrix |
| App state | terminated after sign-in → cold start |
| Permissions | notifications: granted |
| Network | online Wi-Fi |
| Preconditions | `{{new_user}}` registered through the UI (Email channel, DEV code — the TC-AUTH-013 flow) and signed in; the app terminated; then the account deleted through the API: `GET /technician` (`TechnicianController_findAll`, `search={{new_user.email}}`) → `DELETE /user/full-delete/{id}` (`UserController_fullDelete`) |
| Oracle | spec — SRS §3.1.0 FR-SPL-02 (verify authentication token status); spec — SRS §3.1.1.1 FR-WEL-03 (Welcome only without a valid session) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | open | app | cold start | — |
| 2 | wait-for | welcome.root | — | within 30 s (the debug build needs ~10 s to its first screen) |
| 3 | expect-visible | welcome.root | — | signed out |
| 4 | expect-hidden | jobs-list.root | — | the Jobs list is not shown |
| 5 | open | app | terminate, then cold start | — |
| 6 | expect-visible | welcome.root | — | stays signed out on the next launch |

**Postconditions / cleanup:** the account is already deleted; teardown re-checks it is gone (`GET /technician` → 0) and
deletes it if a failure left it behind; reset app data.
**Known issue:** [BUG-SPL-001](bugs/BUG-SPL-001.md) — recon 4 (2 of 2): the deleted account stays signed in (Jobs list
"No jobs", Profile of the deleted account, the next launch the same). The TC keeps the SRS expectation and **stays red**
as the regression check for that bug (owner, 2026-09-24). Also closes MISS-10 of the Auth coverage review.

---

## Aliases used

Screen maps come in step 5 of the module; `MISSING` = to be added from the recon of this module.

| Alias | Screen | android map | ios map |
|---|---|---|---|
| app | — (launch / relaunch) | n/a | n/a (`helpers/app.py`) |
| splash.root | splash | step 7 | **MISSING** — page method: brand-colour share of a screenshot (pixels) |
| splash.logo | splash | step 7 | **MISSING** — page method: centre of the light blob (pixels) |
| splash.interactive | splash | step 7 | **MISSING** — page method: count of text / button / field elements in the tree |
| welcome.root, login.root | welcome, login | step 7 | yes |
| jobs-list.root | jobs-list | step 7 | yes |
| tabbar.jobs | tab bar (shared) | step 7 | **MISSING** as `tabbar.*` — today `jobs-list.tab-jobs`; moves to a shared tab-bar map in module 03 |

## Fixtures used

| Placeholder | Source | Notes |
|---|---|---|
| {{tech.email}}, {{tech.otp}} | `automation/mobile/.env` → `APP_USER_EMAIL`, `APP_USER_OTP` | existing test technician, read-only |
| {{new_user.*}} | generated at runtime (`fixtures/test_data.py`) | `qa-auto+<ts>@example.com`, `+1 202 555 01xx`; deleted by the test |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-SPL-001, -003, -005 | TC-SPL-001 | pixels / tree; Blocked (timing) if the splash window is missed |
| CHK-SPL-007 | TC-SPL-005 | split from TC-SPL-001 (owner, 2026-10-01); Android: red against BUG-SPL-002 |
| CHK-SPL-002 | TC-SPL-001 | brand colour instead of white — D-SPL-2 (accepted) |
| CHK-SPL-011 | TC-SPL-001 | Welcome instead of Login — D-SPL-3 (accepted) |
| CHK-SPL-008, -012 | TC-SPL-002 | -008 proven by the outcome (session honoured) |
| CHK-SPL-009 | TC-SPL-003 | proven by the outcome — currently red: BUG-SPL-001 |
| CHK-SPL-004 | — | **Skipped** — the logo is animated by design (D-SPL-1, owner 2026-09-23) |
| CHK-SPL-006, -013 | — | manual (plan, Step 6) |
| CHK-SPL-010, -015 | — | not recommended (plan) |
| CHK-SPL-014 | — | manual (owner, 2026-09-24); the measured duration is reported as information |

**Total: 9 CHK IDs in 3 TCs.**

## Open questions

- D-SPL-1…4 — accepted (owner, 2026-09-23). Q-SPL-1 — CHK-SPL-014 stays manual; Q-SPL-2 — one user per run OK;
  Q-SPL-3 — bug BUG-SPL-001 (owner, 2026-09-24). [splash-questions.md](splash-questions.md).
