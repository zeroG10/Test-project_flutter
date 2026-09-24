# Automated traceability — mobile

Generated: 2026-09-24 10:48 UTC by `automation/tools/trace_results.py` (read-only: nothing written to Sheets or checklists).

- Platform: **mobile**
- Checklist: `qa/mobile/04-order-details/order-details-checklist.md` — 89 items
- Results (allure): `automation/mobile/allure-results-04` — 10 tests (9 passed, 0 failed, 1 skipped)

## Run context — the limits of every verdict below

- Target: `iOS simulator iPhone 17 · iOS 26.5 · DEV API`
- Product build / version: `1.1.1 (178), development @ 85a84f3, CLIENT_BUILD=true`
- Harness commit (this repo): `04c80ec`
- Environment label (pytest): `iOS · iPhone 17 · iOS 26.5 · build 1.1.1 (178)`
- Run label (suite / filter): `pytest --platform=ios tests/shared/test_order_details.py tests/shared/test_order_list.py::test_calendar_selection_kept_and_card_opens (run 2, 2026-09-24)`
- Not covered by this run: every browser, device, environment, role and quarantined test not listed above. A Passed here says nothing about them.

> Verdict rules: **Passed** only if ALL tagged tests passed; **Failed** if any failed; **Blocked** if any was skipped / did not execute and none failed (a skip is Blocked, never a pass); empty = no tagged test → not run, never green. Manual and exploratory verdicts live in the checklist Sheet, not here.

| CHK ID | Check | Tests | Automated verdict | Evidence |
|---|---|---|---|---|
| CHK-ORDD-001 | Check that the Order Details screen is displayed when the user selects an order… | 2 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)`; `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed<br>allure: passed |
| CHK-ORDD-002 | Check that the back navigation arrow returns the user to the previous screen wi… | 2 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)`; `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed<br>allure: passed |
| CHK-ORDD-003 | Check that the Order ID is displayed prominently in the header of the Order Det… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-004 | Check that the order title is displayed below the Order ID. | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-005 | Check that the current order status badge (e.g., New, In Progress) is clearly v… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-006 | Check that the “Updated” indicator is displayed when the order content has chan… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-007 | Check that the “Updated” indicator disappears after the user navigates away fro… | 1 — `tests.shared.test_order_details#test_updated_gone_after_viewing (TC-ORDD-009 After the details of an unviewed job were opened, the details no longer show 'Updated')` | Passed | allure: passed |
| CHK-ORDD-008 | Check that the order description and scope of work are displayed as readable mu… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-009 | Check that all order information sections are visually separated by dividers. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-010 | Check that all order information fields are read-only and cannot be edited by t… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-011 | Check that the full job site address is displayed in the Location section. | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-012 | Check that tapping the “On map” link opens the job location in an in-app map vi… | 1 — `tests.shared.test_order_details#test_on_map_opens_browser (TC-ORDD-003 'On map' opens the job's location in the in-app browser, and Close returns to the details)` | Passed | allure: passed |
| CHK-ORDD-013 | Check that the map opens with the correct job site coordinates. | 1 — `tests.shared.test_order_details#test_on_map_opens_browser (TC-ORDD-003 'On map' opens the job's location in the in-app browser, and Close returns to the details)` | Passed | allure: passed |
| CHK-ORDD-014 | Check that the scheduled start date and time are displayed with visual date and… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-015 | Check that the displayed date and time reflect the latest scheduled values rece… | 1 — `tests.shared.test_order_details#test_schedule_follows_backend (TC-ORDD-002 A schedule change made on the backend appears on the open details after a refresh)` | Passed | allure: passed |
| CHK-ORDD-016 | Check that the PF name is displayed in the PF Info section. | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-017 | Check that tapping the PF phone number opens the device dialer with the number… | 1 — `tests.shared.test_order_details#test_pf_phone_opens_dialer (TC-ORDD-004 Tapping the PF phone opens the dialer with the number)` | Blocked | allure: skipped — Skipped: Blocked: iOS simulator limitation — there is no Phone app, the tap cannot open a dialer (owner, 2026-09-24, Q-ORDD-3). Runs in full on the Android emu… |
| CHK-ORDD-018 | Check that the Attachments section is displayed on the Order Details screen. | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-019 | Check that tapping the Attachments section navigates the user to the Order Atta… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-020 | Check that the Check In button is displayed at the bottom of the screen when th… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-021 | Check that the Check In button is always visible and accessible without scrolli… | 1 — `tests.shared.test_order_details#test_new_job_details (TC-ORDD-001 A New job shows every part of its details and the Check in button; back returns to the list)` | Passed | allure: passed |
| CHK-ORDD-022 | Check that tapping the Check In button initiates the check-in workflow. | 1 — `tests.shared.test_order_details#test_check_in_starts_flow (TC-ORDD-005 Check in starts the check-in flow; refusing location and cancelling leaves the job New)` | Passed | allure: passed |
| CHK-ORDD-023 | Check that the Enable Location Services prompt is displayed before requesting O… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-024 | Check that the prompt clearly explains why location access is required. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-025 | Check that tapping Enable triggers the operating system location permission dia… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-026 | Check that tapping Cancel dismisses the prompt and continues the check-in flow… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-027 | Check that the Location Disabled prompt is displayed when device-level location… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-028 | Check that tapping Go to settings opens the device location settings screen. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-029 | Check that tapping Cancel returns the user to the check-in flow without GPS val… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-030 | Check that the system captures the user’s GPS location when GPS is enabled duri… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-031 | Check that the system compares the captured GPS location with the registered jo… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-032 | Check that a Check-in Location Mismatch alert is displayed when the distance ex… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-033 | Check that the Check-in Location Mismatch alert explains that the user is not a… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-034 | Check that tapping Got it closes the alert and returns the user to the previous… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-035 | Check that tapping Cancel dismisses the alert without completing check-in. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-036 | Check that a manual location entry prompt is displayed when GPS coordinates can… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-037 | Check that the manual location input field allows the user to enter a textual l… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-038 | Check that tapping Confirm saves the manually entered location to the order. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-039 | Check that manual check-ins are clearly marked as manual in order data. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-040 | Check that manual check-ins do not block job execution. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-041 | Check that a notification is displayed when location data cannot be retrieved d… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-042 | Check that the order is marked with a flag indicating GPS was not confirmed whe… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-043 | Check that location permission failures do not prevent the user from continuing… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-044 | Check that the check-in records include the method used (GPS or Manual). | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-045 | Check that the check-in records include captured coordinates when GPS is availa… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-046 | Check that the check-in records include horizontal accuracy values when GPS is… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-047 | Check that the check-in records include an accurate timestamp of the action. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-048 | Check that cached order details are displayed when the device is offline. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-049 | Check that the Check In flow can be initiated offline and synchronized later wh… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-050 | Check that the Order Details screen remains responsive during slow GPS or netwo… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-051 | Check that the Attachments screen is displayed when the user selects the Attach… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-052 | Check that the Attachments screen header displays a back navigation control tha… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-053 | Check that the screen title “Attachments” is displayed at the top of the Attach… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-054 | Check that the tab selector displays two tabs: Documents and Photos. | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-055 | Check that the Documents tab is selected by default when the Attachments screen… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-056 | Check that all attachments associated with the selected order are displayed on… | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-057 | Check that document files are displayed only under the Documents tab. | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-058 | Check that photo files are displayed only under the Photos tab. | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-059 | Check that switching between Documents and Photos tabs updates the content area… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-060 | Check that each document item displays the file name including its extension (e… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-061 | Check that the document file type is visually identifiable via the file extensi… | 1 — `tests.shared.test_order_details#test_attachments_screen (TC-ORDD-006 Attachments opens with Documents selected and lists the job's documents; Photos switches the tab)` | Passed | allure: passed |
| CHK-ORDD-062 | Check that tapping a document item opens the document in an in-app document vie… | 1 — `tests.shared.test_order_details#test_pdf_viewer (TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents)` | Passed | allure: passed |
| CHK-ORDD-063 | Check that the document opens in a full-screen document viewer. | 1 — `tests.shared.test_order_details#test_pdf_viewer (TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents)` | Passed | allure: passed |
| CHK-ORDD-064 | Check that the document viewer supports vertical scrolling for multi-page docum… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-065 | Check that the document viewer supports zoom in and zoom out gestures. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-066 | Check that the document viewer provides read-only access to the document conten… | 1 — `tests.shared.test_order_details#test_pdf_viewer (TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents)` | Passed | allure: passed |
| CHK-ORDD-067 | Check that a Close (X) control is displayed in the document viewer. | 1 — `tests.shared.test_order_details#test_pdf_viewer (TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents)` | Passed | allure: passed |
| CHK-ORDD-068 | Check that tapping the Close (X) control returns the user to the Documents list. | 1 — `tests.shared.test_order_details#test_pdf_viewer (TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents)` | Passed | allure: passed |
| CHK-ORDD-069 | Check that the user is able to save a document locally when permitted by the op… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-070 | Check that a success toast or banner is displayed when a document is successful… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-071 | Check that supported document formats include PDF, DOC, and XLS. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-072 | Check that unsupported document formats are handled gracefully with an appropri… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-073 | Check that the Photos tab displays a grid layout of photo thumbnails. | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-074 | Check that all photo thumbnails have consistent sizing and spacing in the grid. | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-075 | Check that tapping a photo thumbnail opens the photo in a full-screen photo vie… | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-076 | Check that the selected photo is displayed in full-screen mode in the photo vie… | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-077 | Check that the photo viewer supports pinch-to-zoom gestures. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-078 | Check that the photo viewer supports panning gestures when zoomed. | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-079 | Check that a Close (X) control is displayed in the photo viewer. | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-080 | Check that tapping the Close (X) control returns the user to the Photos grid. | 1 — `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed |
| CHK-ORDD-081 | Check that previously downloaded documents are accessible when the device is of… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-082 | Check that previously downloaded photos are accessible when the device is offli… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-083 | Check that the system notifies the user when attempting to open an attachment t… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-084 | Check that the Attachments screen displays an appropriate message when attachme… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-085 | Check that the user is able to retry loading attachments after a network failur… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-086 | Check that switching between Documents and Photos tabs does not cause UI flicke… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-087 | Check that opening and closing attachments does not reset the selected tab unex… | 2 — `tests.shared.test_order_details#test_pdf_viewer (TC-ORDD-007 A PDF opens in the in-app viewer with its first page drawn, read-only, and X returns to Documents)`; `tests.shared.test_order_details#test_photos_grid_and_viewer (TC-ORDD-008 Photos shows a grid of thumbnails; a thumbnail opens the photo full screen; back returns to Photos)` | Passed | allure: passed<br>allure: passed |
| CHK-ORDD-088 | Check that the Attachments screen remains responsive when a large number of doc… | 0 |  | no tagged test — not run (manual / exploratory), never green |
| CHK-ORDD-089 | Check that attachment content is cached for subsequent access according to offl… | 0 |  | no tagged test — not run (manual / exploratory), never green |

**Summary:** total 89 · automated 43 · Passed 42 · Failed 0 · Blocked 1 · Not run 46 (= total − Passed − Failed − Blocked)

## Tagged tests with no checklist item

These CHK IDs appear in test tags but in none of the checklists above — a stale tag, a typo, or a missing `--checklist`. They count for nothing until resolved.

| CHK ID | Tests | Statuses |
|---|---|---|
| CHK-ORDL-058 | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | passed |
| CHK-ORDL-068 | 1 — `tests.shared.test_order_list#test_calendar_selection_kept_and_card_opens (TC-ORDL-008 The selected date survives a switch to the list and back, and a calendar card opens its job)` | passed |
