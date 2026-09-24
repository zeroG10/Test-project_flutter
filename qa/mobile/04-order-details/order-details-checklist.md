# QA Checklist: Order details screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-24 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Order details screen / Details main screen_General & Layout

1. [CHK-ORDD-001] Check that the Order Details screen is displayed when the user selects an order from the Orders List or Calendar view.
2. [CHK-ORDD-002] Check that the back navigation arrow returns the user to the previous screen without losing state.
3. [CHK-ORDD-003] Check that the Order ID is displayed prominently in the header of the Order Details screen.
4. [CHK-ORDD-004] Check that the order title is displayed below the Order ID.
5. [CHK-ORDD-005] Check that the current order status badge (e.g., New, In Progress) is clearly visible.
6. [CHK-ORDD-006] Check that the “Updated” indicator is displayed when the order content has changed since last viewed.
7. [CHK-ORDD-007] Check that the “Updated” indicator disappears after the user navigates away from the Order Details screen.
8. [CHK-ORDD-008] Check that the order description and scope of work are displayed as readable multi-line instructions.
9. [CHK-ORDD-009] Check that all order information sections are visually separated by dividers.
10. [CHK-ORDD-010] Check that all order information fields are read-only and cannot be edited by the user.

## Order details screen / Location & Map

1. [CHK-ORDD-011] Check that the full job site address is displayed in the Location section.
2. [CHK-ORDD-012] Check that tapping the “On map” link opens the job location in an in-app map view or external maps application.
3. [CHK-ORDD-013] Check that the map opens with the correct job site coordinates.

## Order details screen / Date & Time

1. [CHK-ORDD-014] Check that the scheduled start date and time are displayed with visual date and time icons.
2. [CHK-ORDD-015] Check that the displayed date and time reflect the latest scheduled values received from the backend.

## Order details screen / PF Information

1. [CHK-ORDD-016] Check that the PF name is displayed in the PF Info section.
2. [CHK-ORDD-017] Check that tapping the PF phone number opens the device dialer with the number prefilled.

## Order details screen / Attachments Navigation

1. [CHK-ORDD-018] Check that the Attachments section is displayed on the Order Details screen.
2. [CHK-ORDD-019] Check that tapping the Attachments section navigates the user to the Order Attachments screen.

## Order details screen / Primary Action — Check In

1. [CHK-ORDD-020] Check that the Check In button is displayed at the bottom of the screen when the order status is New or not started.
2. [CHK-ORDD-021] Check that the Check In button is always visible and accessible without scrolling.
3. [CHK-ORDD-022] Check that tapping the Check In button initiates the check-in workflow.

## Order details screen / Location Permissions & GPS Logic

1. [CHK-ORDD-023] Check that the Enable Location Services prompt is displayed before requesting OS-level location permission.
2. [CHK-ORDD-024] Check that the prompt clearly explains why location access is required.
3. [CHK-ORDD-025] Check that tapping Enable triggers the operating system location permission dialog.
4. [CHK-ORDD-026] Check that tapping Cancel dismisses the prompt and continues the check-in flow without GPS.
5. [CHK-ORDD-027] Check that the Location Disabled prompt is displayed when device-level location services are turned off.
6. [CHK-ORDD-028] Check that tapping Go to settings opens the device location settings screen.
7. [CHK-ORDD-029] Check that tapping Cancel returns the user to the check-in flow without GPS validation.
8. [CHK-ORDD-030] Check that the system captures the user’s GPS location when GPS is enabled during check-in.
9. [CHK-ORDD-031] Check that the system compares the captured GPS location with the registered job site location.
10. [CHK-ORDD-032] Check that a Check-in Location Mismatch alert is displayed when the distance exceeds the allowed tolerance threshold (~100 meters).
11. [CHK-ORDD-033] Check that the Check-in Location Mismatch alert explains that the user is not at the registered job site.
12. [CHK-ORDD-034] Check that tapping Got it closes the alert and returns the user to the previous screen.
13. [CHK-ORDD-035] Check that tapping Cancel dismisses the alert without completing check-in.

## Order details screen / Manual Check-In

1. [CHK-ORDD-036] Check that a manual location entry prompt is displayed when GPS coordinates cannot be obtained.
2. [CHK-ORDD-037] Check that the manual location input field allows the user to enter a textual location.
3. [CHK-ORDD-038] Check that tapping Confirm saves the manually entered location to the order.
4. [CHK-ORDD-039] Check that manual check-ins are clearly marked as manual in order data.
5. [CHK-ORDD-040] Check that manual check-ins do not block job execution.

## Order details screen / Data Recording

1. [CHK-ORDD-041] Check that a notification is displayed when location data cannot be retrieved due to system or sensor error.
2. [CHK-ORDD-042] Check that the order is marked with a flag indicating GPS was not confirmed when automatic location fails.
3. [CHK-ORDD-043] Check that location permission failures do not prevent the user from continuing the job.
4. [CHK-ORDD-044] Check that the check-in records include the method used (GPS or Manual).
5. [CHK-ORDD-045] Check that the check-in records include captured coordinates when GPS is available.
6. [CHK-ORDD-046] Check that the check-in records include horizontal accuracy values when GPS is used.
7. [CHK-ORDD-047] Check that the check-in records include an accurate timestamp of the action.
8. [CHK-ORDD-048] Check that cached order details are displayed when the device is offline.
9. [CHK-ORDD-049] Check that the Check In flow can be initiated offline and synchronized later when connectivity is restored. (placeholder if async sync is planned)
10. [CHK-ORDD-050] Check that the Order Details screen remains responsive during slow GPS or network conditions.

## Order details screen / General & Layout

1. [CHK-ORDD-051] Check that the Attachments screen is displayed when the user selects the Attachments section from the Order Details screen.
2. [CHK-ORDD-052] Check that the Attachments screen header displays a back navigation control that returns the user to the Order Details screen.
3. [CHK-ORDD-053] Check that the screen title “Attachments” is displayed at the top of the Attachments screen.
4. [CHK-ORDD-054] Check that the tab selector displays two tabs: Documents and Photos.
5. [CHK-ORDD-055] Check that the Documents tab is selected by default when the Attachments screen is opened.

## Order details screen / Attachment Listing

1. [CHK-ORDD-056] Check that all attachments associated with the selected order are displayed on the Attachments screen.
2. [CHK-ORDD-057] Check that document files are displayed only under the Documents tab.
3. [CHK-ORDD-058] Check that photo files are displayed only under the Photos tab.
4. [CHK-ORDD-059] Check that switching between Documents and Photos tabs updates the content area accordingly.

## Order details screen / Documents Tab

1. [CHK-ORDD-060] Check that each document item displays the file name including its extension (e.g., “Safety instruction.pdf”).
2. [CHK-ORDD-061] Check that the document file type is visually identifiable via the file extension or indicator.
3. [CHK-ORDD-062] Check that tapping a document item opens the document in an in-app document viewer.

## Order details screen / Document Viewer

1. [CHK-ORDD-063] Check that the document opens in a full-screen document viewer.
2. [CHK-ORDD-064] Check that the document viewer supports vertical scrolling for multi-page documents.
3. [CHK-ORDD-065] Check that the document viewer supports zoom in and zoom out gestures.
4. [CHK-ORDD-066] Check that the document viewer provides read-only access to the document content.
5. [CHK-ORDD-067] Check that a Close (X) control is displayed in the document viewer.
6. [CHK-ORDD-068] Check that tapping the Close (X) control returns the user to the Documents list.
7. [CHK-ORDD-069] Check that the user is able to save a document locally when permitted by the operating system.
8. [CHK-ORDD-070] Check that a success toast or banner is displayed when a document is successfully saved to the device.
9. [CHK-ORDD-071] Check that supported document formats include PDF, DOC, and XLS.
10. [CHK-ORDD-072] Check that unsupported document formats are handled gracefully with an appropriate message. (placeholder for future formats)

## Order details screen / Photos Tab

1. [CHK-ORDD-073] Check that the Photos tab displays a grid layout of photo thumbnails.
2. [CHK-ORDD-074] Check that all photo thumbnails have consistent sizing and spacing in the grid.
3. [CHK-ORDD-075] Check that tapping a photo thumbnail opens the photo in a full-screen photo viewer.

## Order details screen / Photo Viewer

1. [CHK-ORDD-076] Check that the selected photo is displayed in full-screen mode in the photo viewer.
2. [CHK-ORDD-077] Check that the photo viewer supports pinch-to-zoom gestures.
3. [CHK-ORDD-078] Check that the photo viewer supports panning gestures when zoomed.
4. [CHK-ORDD-079] Check that a Close (X) control is displayed in the photo viewer.
5. [CHK-ORDD-080] Check that tapping the Close (X) control returns the user to the Photos grid.
6. [CHK-ORDD-081] Check that previously downloaded documents are accessible when the device is offline.
7. [CHK-ORDD-082] Check that previously downloaded photos are accessible when the device is offline.
8. [CHK-ORDD-083] Check that the system notifies the user when attempting to open an attachment that is not available offline.
9. [CHK-ORDD-084] Check that the Attachments screen displays an appropriate message when attachment loading fails due to a network error.
10. [CHK-ORDD-085] Check that the user is able to retry loading attachments after a network failure.
11. [CHK-ORDD-086] Check that switching between Documents and Photos tabs does not cause UI flickering or layout shifts.
12. [CHK-ORDD-087] Check that opening and closing attachments does not reset the selected tab unexpectedly.
13. [CHK-ORDD-088] Check that the Attachments screen remains responsive when a large number of documents or photos are present.
14. [CHK-ORDD-089] Check that attachment content is cached for subsequent access according to offline behavior rules.
