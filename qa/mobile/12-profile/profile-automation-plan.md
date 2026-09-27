# Automation plan — Profile (mobile)

> Output of `prompts/06-select-automation-candidates.md` for `qa/mobile/12-profile/profile-checklist.md` (35 items,
> `CHK-PRF-001…035`, imported 2026-09-27). Date: 2026-09-27. Owner: mykola.zhuchenko.
> **Status: accepted by the owner 2026-09-27 (D-PRF-1…6, Q-PRF-1…5: «все ок») — [profile-questions.md](profile-questions.md).**

| Field | Value |
|---|---|
| Platform / stack | mobile — iOS first, then Android · Appium 3 + XCUITest / UiAutomator2 · Python + pytest |
| Feature code | `PRF` |
| Scope decision (proposed) | the Profile tab: the card, Edit profile (fields, Save rules, saving, leaving without saving), the app theme, Privacy Policy, log out, the delete-account dialog; deleting an account only on a throwaway technician (Q-PRF-2); offline → Android stage |
| Oracle model | accepted production baseline; SRS §3.1.5 (FR-PROF-01…15); the technician on the server (`GET /user/{id}`, `GET /technician`) and the test account's data (`APP_USER_*`) |
| App code read | `profile_page.dart`, `edit_profile_page.dart`, `app_validators.dart`, `theme_cubit.dart`, `auth_bloc.dart`, `auth_repository_impl.dart`, `url_launcher_helper.dart` (read only, `development` @ 85a84f3) |

## Step 3–4 — Candidate matrix (35 items)

| CHK ID | Scenario (short) | Level | Status | Priority | TC | Reason / blocker |
|---|---|---|---|---|---|---|
| CHK-PRF-001…-003, -005…-008 | the tab; highlighted; card, settings, footer, tab bar; name, phone, email as the account; Edit shown | E2E UI | Good Candidate | P0 | TC-PRF-001 | Edit has no name — by its place on the card |
| CHK-PRF-004 | the same after an app restart | E2E UI | Good Candidate | P1 | TC-PRF-001 | |
| CHK-PRF-009…-014, -016 | Edit profile: Back, Save, pre-filled, phone and email disabled, Save disabled for an empty first / last name, enabled when valid | E2E UI | Good Candidate | P0 | TC-PRF-002 | |
| CHK-PRF-019, -020 | Back with changes: "Unsaved Changes" → Leave → nothing saved | E2E UI + API | Good Candidate | P1 | TC-PRF-002 | D-PRF-2 |
| CHK-PRF-015 | invalid email error | — | Skipped (D-PRF-1) | – | — | email not editable |
| CHK-PRF-017, -018 | Save → Profile shows the new name at once; the server has it; restored after | E2E UI + API | Good Candidate | P0 | TC-PRF-003 | Q-PRF-1 (the main test account) |
| CHK-PRF-021, -022 | App theme → Dark at once (pixels) and after a restart; back to Auto | E2E UI | Good Candidate | P2 | TC-PRF-004 | D-PRF-3 |
| CHK-PRF-023 | every element in dark | E2E UI | Partial | P3 | TC-PRF-004 | Q-PRF-5: background by pixels, the rest on the screenshot |
| CHK-PRF-024, -025 | Privacy Policy → the in-app browser at concerttech.com → Close → Profile | E2E UI | Good Candidate | P1 | TC-PRF-005 | the browser's Close, not the site's |
| CHK-PRF-026…-029 | log out: the dialog, Cancel stays; Log out → Welcome; after a relaunch still Welcome | E2E UI | Good Candidate | P0 | TC-PRF-006 | Q-PRF-3 |
| CHK-PRF-031, -033 | Delete account dialog; Cancel changes nothing | E2E UI | Good Candidate | P1 | TC-PRF-007 | D-PRF-4 |
| CHK-PRF-032 | typing "Delete" required | E2E UI | Baseline (D-PRF-4) | P2 | TC-PRF-007 | the dialog as the app has it |
| CHK-PRF-034, -035 | deleting removes the account and logs out; the email cannot sign in again | E2E UI + API | Good Candidate | P1 | TC-PRF-008 | Q-PRF-2: a throwaway technician only |
| CHK-PRF-030 | log out offline | Manual (Android stage) | Needs Device | P2 | — | Q-PRF-4 |

## Step 5b — Selected (draft)

**Up to 33 of 35 → 8 TCs** (TC-PRF-003 and -008 depend on Q-PRF-1 / -2).

| TC | Covers |
|---|---|
| TC-PRF-001 | the tab, the card with the account's data, the settings and footer; again after a restart |
| TC-PRF-002 | Edit profile: fields and their state, Save rules, Back with changes → "Unsaved Changes" → Leave, nothing saved |
| TC-PRF-003 | a changed name saved → Profile at once and the server; restored |
| TC-PRF-004 | App theme Dark → dark at once, after a restart; Auto again |
| TC-PRF-005 | Privacy Policy → in-app browser → Close |
| TC-PRF-006 | Log out: dialog, Cancel; Log out → Welcome; relaunch → still Welcome; signed in again by the next test |
| TC-PRF-007 | Delete account dialog as it is; Cancel → nothing changes |
| TC-PRF-008 | a throwaway technician registered in the app → Delete account → Welcome → the same email cannot sign in |

**The rest:** CHK-PRF-015 (email not editable), CHK-PRF-030 (offline, Android stage).

## Step 9 — Test data

- The main test account (`APP_USER_*`): its data is read, and in TC-PRF-003 its name is changed and restored — through
  the app, and through `PATCH /user/{id}` on failure.
- TC-PRF-008: a throwaway technician (`new_user`, as module 02), removed through the API if anything is left.
- The app theme and the session are put back after each test.

## Step 16 — Recommendation

The owner's word on the questions → test cases → harness.
