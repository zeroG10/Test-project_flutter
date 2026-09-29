# Automated traceability — mobile

Generated: 2026-09-27 09:36 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/12-profile/profile-checklist.md` — 35 items
- Results (allure): `automation/mobile/allure-results-12` — 8 tests (8 passed, 0 failed, 0 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `31f982c`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_profile.py (module 12 run 3, 2026-09-27; the main account's name changed and put back; a throwaway technician registered and deleted)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-PRF-001 | Check that the Profile screen is opened when the user taps the Profile tab in t… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-002 | Check that the Profile tab is visually highlighted as active when the Profile s… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-003 | Check that the Profile screen contains a user information card, settings sectio… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-004 | Check that all Profile screen elements are displayed correctly after app relaun… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-005 | Check that the user’s first name and last name are displayed correctly in the u… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-006 | Check that the phone number is displayed in read-only mode in the user informat… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-007 | Check that the email address is displayed correctly in the user information car… | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-008 | Check that the Edit button is visible and enabled in the user information card. | 1 — `tests.shared.test_profile#test_profile_card (TC-PRF-001 The Profile tab: the card with the account's name, phone and email, Edit, the settings and the footer; the same after a restart)` | Passed | allure: passed |
| CHK-PRF-009 | Check that tapping the Edit button navigates the user to the Edit Profile scree… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-010 | Check that the Edit Profile screen header contains a Back button and a Save but… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-011 | Check that First name, Last name, Phone number, and Email fields are pre-filled… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-012 | Check that the Phone number field is disabled and not editable on the Edit Prof… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-013 | Check that the Save button is disabled when the First name field is empty. | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-014 | Check that the Save button is disabled when the Last name field is empty. | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-015 | Check that an error is shown when an invalid email format is entered and the Sa… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PRF-016 | Check that the Save button is enabled when all required fields contain valid va… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-017 | Check that tapping Save updates the user profile data and returns the user to t… | 1 — `tests.shared.test_profile#test_edit_name_saved (TC-PRF-003 A changed name is saved: Profile shows it at once, the server has it; the name is put back)` | Passed | allure: passed |
| CHK-PRF-018 | Check that updated profile data is immediately reflected on the Profile screen… | 1 — `tests.shared.test_profile#test_edit_name_saved (TC-PRF-003 A changed name is saved: Profile shows it at once, the server has it; the name is put back)` | Passed | allure: passed |
| CHK-PRF-019 | Check that tapping the Back button returns the user to the Profile screen witho… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-020 | Check that unsaved changes are discarded when the user navigates back from Edit… | 1 — `tests.shared.test_profile#test_edit_profile_rules (TC-PRF-002 Edit profile: the fields and their state, the Save rules; Back with changes asks, Leave saves nothing)` | Passed | allure: passed |
| CHK-PRF-021 | Check that toggling the Dark mode switch changes the app theme immediately. | 1 — `tests.shared.test_profile#test_app_theme (TC-PRF-004 App theme: Dark turns the app dark at once and stays after a restart; Auto again)` | Passed | allure: passed |
| CHK-PRF-022 | Check that the Dark mode toggle state is preserved after app restart. | 1 — `tests.shared.test_profile#test_app_theme (TC-PRF-004 App theme: Dark turns the app dark at once and stays after a restart; Auto again)` | Passed | allure: passed |
| CHK-PRF-023 | Check that all Profile screen elements adapt correctly to Dark mode. | 1 — `tests.shared.test_profile#test_app_theme (TC-PRF-004 App theme: Dark turns the app dark at once and stays after a restart; Auto again)` | Passed | allure: passed |
| CHK-PRF-024 | Check that tapping Privacy Policy opens the policy document in a web view or ex… | 1 — `tests.shared.test_profile#test_privacy_policy (TC-PRF-005 Privacy Policy opens in the app's browser; Close returns to Profile)` | Passed | allure: passed |
| CHK-PRF-025 | Check that the user can return to the app after viewing the Privacy Policy. | 1 — `tests.shared.test_profile#test_privacy_policy (TC-PRF-005 Privacy Policy opens in the app's browser; Close returns to Profile)` | Passed | allure: passed |
| CHK-PRF-026 | Check that tapping Log out opens the logout confirmation dialog. | 1 — `tests.shared.test_profile#test_log_out (TC-PRF-006 Log out: the dialog; Cancel stays signed in; Log out goes to Welcome and a relaunch stays there)` | Passed | allure: passed |
| CHK-PRF-027 | Check that tapping Cancel closes the logout dialog without logging the user out. | 1 — `tests.shared.test_profile#test_log_out (TC-PRF-006 Log out: the dialog; Cancel stays signed in; Log out goes to Welcome and a relaunch stays there)` | Passed | allure: passed |
| CHK-PRF-028 | Check that tapping Log out clears the user session and navigates to the Welcome… | 1 — `tests.shared.test_profile#test_log_out (TC-PRF-006 Log out: the dialog; Cancel stays signed in; Log out goes to Welcome and a relaunch stays there)` | Passed | allure: passed |
| CHK-PRF-029 | Check that the user cannot access authenticated screens after logging out. | 1 — `tests.shared.test_profile#test_log_out (TC-PRF-006 Log out: the dialog; Cancel stays signed in; Log out goes to Welcome and a relaunch stays there)` | Passed | allure: passed |
| CHK-PRF-030 | Check that logout clears local user data even when the device is offline. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-PRF-031 | Check that tapping Delete account opens the account deletion confirmation pop-u… | 1 — `tests.shared.test_profile#test_delete_account_dialog (TC-PRF-007 The delete-account dialog as the app has it; Cancel changes nothing)` | Passed | allure: passed |
| CHK-PRF-032 | Check that account deletion is blocked until the user types the required “Delet… | 1 — `tests.shared.test_profile#test_delete_account_dialog (TC-PRF-007 The delete-account dialog as the app has it; Cancel changes nothing)` | Passed | allure: passed |
| CHK-PRF-033 | Check that tapping Cancel closes the delete account dialog without any changes. | 1 — `tests.shared.test_profile#test_delete_account_dialog (TC-PRF-007 The delete-account dialog as the app has it; Cancel changes nothing)` | Passed | allure: passed |
| CHK-PRF-034 | Check that confirming account deletion removes the user account and logs the us… | 1 — `tests.shared.test_profile#test_delete_throwaway_account (TC-PRF-008 A throwaway account deleted in the app: Welcome; the same email cannot sign in; gone on the server)` | Passed | allure: passed |
| CHK-PRF-035 | Check that deleted accounts cannot log in again using the same credentials. | 1 — `tests.shared.test_profile#test_delete_throwaway_account (TC-PRF-008 A throwaway account deleted in the app: Welcome; the same email cannot sign in; gone on the server)` | Passed | allure: passed |

**Summary:** total 35 · automated 33 · Passed 33 · Failed 0 · Blocked 0 · Not run 2 (= total − Passed − Failed − Blocked)

## Notes on this run

- **Not run (2), by the owner's decisions of 2026-09-27:**
  - CHK-PRF-015: the email is not editable on Edit profile, so no format error can appear. Skipped with a comment
    (D-PRF-1).
  - CHK-PRF-030: log out offline, Android stage (Q-PRF-4).
- **Accepted baseline (D-PRF-1…6):**
  - Back with changes asks "Unsaved Changes";
  - the theme is a menu Auto / Light / Dark;
  - Delete account sits on Edit profile and asks for no typed word — CHK-PRF-032 checks the dialog as it is;
  - Save is disabled for a bad name, without a message.
- **Data (owner, Q-PRF-1…3):**
  - TC-PRF-003 changes the main account's first name and puts it back through the app; the fixture would put it back
    through `PATCH /user/{id}`.
  - TC-PRF-008 deletes only a throwaway technician it registers itself. After the app deletes it, the user record stays
    with its email emptied; the harness removes it by id.
  - After the runs the main account's name is unchanged, and no throwaway user is left.
- **How the checks decide:**
  - the theme by the screenshot's mean brightness (dark < 100, light > 180);
  - the name on the server by `GET /user/{id}`;
  - the deletion by `GET /technician?search=` and by the login message for an unregistered email.
- **Run history:**
  - Run 1: 7 passed, 1 broken by the harness, and a cleanup error. TC-PRF-005: Close tapped while the page loaded. The
    cleanup guard refused the user whose email the app had emptied — that record from run 1 is anonymised and cannot
    be found by the list API, so it stays on DEV.
  - Run 2: 7 passed, 1 broken by the harness (TC-PRF-005: an element click on the browser's Close does not close it;
    now a tap at its centre).
  - Run 3: 8 passed.
  - Prove-red (`--prove-red`): 7 of 7 failed in the full run. TC-PRF-008 was Blocked there, because the registration
    precondition did not reach the code screen. Run alone, it failed at its own check (the card's email). 8 of 8 in all.
