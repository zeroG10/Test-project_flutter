# Test cases — Profile (mobile)

> Structured, alias-based test cases for the CHK IDs selected in [profile-automation-plan.md](profile-automation-plan.md).
> Format: [qa/_templates/test-case-format.md](../../_templates/test-case-format.md) · prompt `prompts/mobile/03`.
> **Status: automated and traced on iOS (run 3, 2026-09-27: 8 of 8 passed); the owner sees them with the results.
> Written after recon 13 ([qa/shared/recon-2026-09-24-ios.md](../../shared/recon-2026-09-24-ios.md)) and the
> owner's decisions of 2026-09-27: D-PRF-1…6, Q-PRF-1…5 — [profile-questions.md](profile-questions.md).**

| Field | Value |
|---|---|
| Feature | The Profile tab: the user card, Edit profile (fields, Save rules, saving, leaving without saving), App theme, Privacy Policy, log out, the delete-account dialog, deleting a throwaway account |
| Source checklist | `qa/mobile/12-profile/profile-checklist.md` (CHK-PRF-001…035) |
| Devices / build | iPhone 17 · iOS 26.5 (simulator) · `[DEV] CT Mobile` 1.1.1 (178), `CLIENT_BUILD=true` · online |
| Owner | @mykola.zhuchenko · Last updated 2026-09-27 |

**Conventions**

- **The main test account** (`{{tech.*}}`): its phone and email come from `.env`; its first and last name come from
  the server (`GET /user/{id}`, `api.user`).
  - TC-PRF-003 changes the name and puts it back through the app. If the test fails, the name is put back through
    `PATCH /user/{id}` (owner, Q-PRF-1).
- **The card** (`profile.card`) is one element named `<first last>\n<phone>\n<email>`. The Edit button has no name: it is
  the unnamed button at the card's top right (`profile.edit`).
- **App theme** is decided by the screenshot's mean brightness. Recon 13: 246 in the light theme, 39 in the dark one.
  Dark < 100, light > 180. Every test that changes the theme puts Auto back.
- **A throwaway technician** (`{{new_user.*}}`, as module 02) is used in TC-PRF-008 only.
  - It is registered in the app with the Email channel and the DEV code.
  - Its user id is kept right after registration.
  - Whatever is left of it is removed through the API after the test (owner, Q-PRF-2).
- After a log out or a deletion the next test signs in again (`ui_login`; owner, Q-PRF-3).

---

## TC-PRF-001 — The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-001, -002, -003, -004, -005, -006, -007, -008 |
| Priority | P0 · smoke |
| Preconditions | signed in as `{{tech}}` |
| Oracle | spec — SRS §3.1.5 (layout, FR-PROF-01); the account on the server (name) and `.env` (phone, email) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.profile | — | profile.root "Profile"; the tab selected |
| 2 | expect-text | profile.card | — | `<first> <last>` (server), `{{tech.phone}}`, `{{tech.email}}` |
| 3 | expect-enabled | profile.edit | — | at the card's top right |
| 4 | expect-visible | profile.theme | — | App theme (…) |
| 5 | expect-visible | profile.privacy | — | — |
| 6 | expect-visible | profile.logout | — | — |
| 7 | expect-text | profile.version | — | `v1.1.1 (178)` (the build under test) |
| 8 | open | app | terminate + launch → tabbar.profile | steps 2–7 again |

## TC-PRF-002 — Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-009, -010, -011, -012, -013, -014, -016, -019, -020 |
| Priority | P0 |
| Preconditions | Profile open |
| Oracle | spec — FR-PROF-02, -09, -11; D-PRF-1 (email disabled), D-PRF-2 (Unsaved Changes), D-PRF-5 (Save disabled, no message) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | profile.edit | — | edit-profile.title "Edit profile" |
| 2 | expect-visible | edit-profile.back | — | — |
| 3 | expect-enabled | edit-profile.save | — | the names are valid |
| 4 | expect-text | edit-profile.first-name | — | the server's first name |
| 5 | expect-text | edit-profile.last-name | — | the server's last name |
| 6 | expect-disabled | edit-profile.phone | — | the national number of `{{tech.phone}}` |
| 7 | expect-disabled | edit-profile.email | — | `{{tech.email}}` |
| 8 | clear | edit-profile.first-name | — | edit-profile.save disabled |
| 9 | fill | edit-profile.first-name | `QA` | edit-profile.save enabled |
| 10 | clear | edit-profile.last-name | — | edit-profile.save disabled |
| 11 | click | edit-profile.back | — | unsaved-dialog "Unsaved Changes" |
| 12 | click | unsaved-dialog.leave | — | profile.card with the old name; the server unchanged |

## TC-PRF-003 — A changed name is saved: Profile shows it at once, the server has it; the name is put back

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-017, -018 |
| Priority | P0 |
| Preconditions | Profile open; the account's name read from the server |
| Oracle | spec — FR-PROF-12 (backend and local state); the server copy (`api.user`) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | profile.edit | — | — |
| 2 | fill | edit-profile.first-name | `Qaedit` | — |
| 3 | click | edit-profile.save | — | profile.root; profile.card `Qaedit <last>` at once |
| 4 | expect-text | api.user | — | firstName `Qaedit` |
| 5 | click | profile.edit | then the old first name, Save | profile.card with the old name; the server has it back |

## TC-PRF-004 — App theme: Dark turns the app dark at once and stays after a restart; Auto again

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-021, -022, -023 |
| Priority | P2 |
| Preconditions | Profile open, App theme (Auto) in the light system appearance |
| Oracle | spec — FR-PROF-03, -04; D-PRF-3 (Auto / Light / Dark); Q-PRF-5 (the background by pixels, the rest on the screenshot) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | profile.theme-menu | then theme-menu.dark | profile.theme "App theme (Dark)"; the screen dark at once |
| 2 | open | app | terminate + launch → tabbar.profile | still "App theme (Dark)", dark |
| 3 | click | profile.theme-menu | then theme-menu.auto | "App theme (Auto)"; the screen light |

## TC-PRF-005 — Privacy Policy opens in the app's browser; Close returns to Profile

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-024, -025 |
| Priority | P1 |
| Preconditions | Profile open |
| Oracle | spec — FR-PROF-05 (web view or browser; the link `https://www.concerttech.com/mobile-privacy/`) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | profile.privacy | — | in-app-browser.url `concerttech.com` |
| 2 | click | in-app-browser.close | — | profile.root |

## TC-PRF-006 — Log out: the dialog; Cancel stays signed in; Log out goes to Welcome and a relaunch stays there

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-026, -027, -028, -029 |
| Priority | P0 |
| Preconditions | Profile open |
| Oracle | spec — FR-PROF-06…08, SRS §3.1.5 (dialog text) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | profile.logout | — | logout-dialog: "Log out", "Are you sure you want to log out?", Cancel, Log out |
| 2 | click | logout-dialog.cancel | — | profile.root |
| 3 | click | profile.logout | then logout-dialog.confirm | welcome.root |
| 4 | open | app | terminate + launch | welcome.root — no Jobs list |

## TC-PRF-007 — The delete-account dialog as the app has it; Cancel changes nothing

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-031, -032, -033 |
| Priority | P1 |
| Preconditions | Profile open |
| Oracle | FR-PROF-15; D-PRF-4 (accepted: on Edit profile, no typed "Delete") |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | profile.edit | then edit-profile.delete-account | delete-dialog: "Delete account", "Are you sure you want to delete account?", Cancel, Delete; no text field |
| 2 | click | delete-dialog.cancel | — | edit-profile.title; the account still on the server |

## TC-PRF-008 — A throwaway account deleted in the app: Welcome; the same email cannot sign in; gone on the server

| Field | Value |
|---|---|
| Source CHK IDs | CHK-PRF-034, -035 |
| Priority | P1 |
| Preconditions | signed out; `{{new_user}}` registered in the app (Email channel, DEV code) → Jobs list |
| Oracle | spec — FR-PROF-15; the login message of an unregistered email (module 02); the server (`GET /technician?search=`) |

| # | Action | Target (alias) | Data | Expected |
|---|---|---|---|---|
| 1 | click | tabbar.profile | then profile.edit, edit-profile.delete-account | — |
| 2 | click | delete-dialog.delete | — | welcome.root |
| 3 | expect-text | api.technicians | — | no technician with `{{new_user.email}}` |
| 4 | click | welcome.login | then `{{new_user.email}}`, Continue | login.error "This email is not registered yet. Create an account to get started." |

## Aliases used

| Alias | ios map |
|---|---|
| tabbar.profile | yes |
| profile.* | `screens/profile_map.py` (recon 13) |
| edit-profile.*, unsaved-dialog.*, delete-dialog.* | `screens/edit_profile_map.py` (recon 13) |
| theme-menu.*, logout-dialog.* | `screens/profile_map.py` (recon 13) |
| in-app-browser.url, .close | yes (module 04) |
| welcome.root, welcome.login, login.error | yes (module 02) |
| api.user, api.technicians | not elements — `GET /user/{id}`, `GET /technician?search=` (admin, read-only) |

## Coverage

| CHK ID | TC | Note |
|---|---|---|
| CHK-PRF-001…-008 | TC-PRF-001 | |
| CHK-PRF-009…-014, -016, -019, -020 | TC-PRF-002 | D-PRF-1, -2, -5 |
| CHK-PRF-017, -018 | TC-PRF-003 | the main account's name, put back (Q-PRF-1) |
| CHK-PRF-021…-023 | TC-PRF-004 | -023: the background by pixels (Q-PRF-5) |
| CHK-PRF-024, -025 | TC-PRF-005 | |
| CHK-PRF-026…-029 | TC-PRF-006 | |
| CHK-PRF-031…-033 | TC-PRF-007 | -032: the dialog as it is (D-PRF-4) |
| CHK-PRF-034, -035 | TC-PRF-008 | a throwaway technician (Q-PRF-2) |

**Not here:**
- CHK-PRF-015 — skipped with a comment: the email is not editable (D-PRF-1).
- CHK-PRF-030 — offline, Android stage (Q-PRF-4).
