# QA Checklist: Field Technicians

## Access and Permissions

1. [CHK-FT-001] Check that a user with the Root role can open the Field Technicians List page from the left navigation.
2. [CHK-FT-002] Check that a user with the Manager role can open the Field Technicians List page from the left navigation.
3. [CHK-FT-003] Check that a user with the Root role can open the Field Technician Details page from a list row action.
4. [CHK-FT-004] Check that a user with the Manager role can open the Field Technician Details page from a list row action.
5. [CHK-FT-005] Check that an unauthenticated user is redirected to the Login page when navigating directly to the Field Technicians List URL.
6. [CHK-FT-006] Check that Field Technician data on the List page is read-only and offers no inline editing controls.
7. [CHK-FT-007] Check that the Field Technicians item in the left navigation is shown as active while the user is on a Field Technicians page.

## Navigation

1. [CHK-FT-008] Check that the left navigation displays a Field Technicians item with its team icon.
2. [CHK-FT-009] Check that the top header breadcrumb shows Home and Field Technicians on the List page.
3. [CHK-FT-010] Check that selecting the Edit row action on the List page navigates to the Field Technician Details page.
4. [CHK-FT-011] Check that the breadcrumb on the Details page navigates back to the Field Technicians List page.
5. [CHK-FT-012] Check that the user is redirected to the Field Technicians List page after a technician is deleted.

## UI Layout

1. [CHK-FT-013] Check that the List page header displays the title "List of Field Technicians".
2. [CHK-FT-014] Check that the List page uses the standard admin layout with left navigation, top header, and a main content area containing the filters and the technicians table.
3. [CHK-FT-015] Check that the filter bar is displayed above the technicians table.
4. [CHK-FT-016] Check that the table toolbar displays a search input with the placeholder "Search".
5. [CHK-FT-017] Check that the table toolbar displays the history, row-density, and column-settings icon buttons.
6. [CHK-FT-018] Check that the Details page header displays the title "Edit Field Technician".
7. [CHK-FT-019] Check that the Details page header displays a Save button and a Delete icon button.
8. [CHK-FT-020] Check that the layout renders without horizontal clipping at the minimum supported width of 1366px.
9. [CHK-FT-021] Check that the layout remains usable at tablet viewport width.
10. [CHK-FT-022] Check that the layout remains readable when the browser font scale is set between 75% and 150%.
11. [CHK-FT-023] Check that the top header displays the user menu with avatar, user name, and a dropdown chevron.
12. [CHK-FT-024] Check that the top header displays the language control.

## Fields and Controls

1. [CHK-FT-025] Check that the technicians table displays columns in the order Name, Phone number, Email, COPS match, Last activity, Status, Actions.
2. [CHK-FT-026] Check that each table row displays accurate technician data for every column.
3. [CHK-FT-027] Check that each table row displays an Edit action icon in the Actions column.
4. [CHK-FT-028] Check that the Status column displays a colored badge with a dot and a status label.
5. [CHK-FT-029] Check that the COPS match filter is a select control with the placeholder "Select" and the options Matched and Not found.
6. [CHK-FT-030] Check that the Status filter is a select control with the options Active, Inactive, and Pending.
7. [CHK-FT-031] Check that the Last activity filter is a date picker with the placeholder "Select date" that supports a single date or a date range.
8. [CHK-FT-032] Check that the filter bar displays the Filter, Clear, and Expand/Collapse controls.
9. [CHK-FT-033] Check that the First name field on the Details page is an editable text input marked as required.
10. [CHK-FT-034] Check that the Last name field on the Details page is an editable text input marked as required.
11. [CHK-FT-035] Check that the Status field on the Details page is an editable dropdown marked as required and displays the current status as a badge.
12. [CHK-FT-036] Check that the Email field on the Details page is an editable text input.
13. [CHK-FT-037] Check that the Phone number field on the Details page is displayed as read-only with a disabled appearance.
14. [CHK-FT-038] Check that the COPS match field on the Details page is read-only and shows Matched or Not matched.
15. [CHK-FT-039] Check that the Last activity field on the Details page is a read-only timestamp.
16. [CHK-FT-040] Check that the items-per-page selector on the List page displays "10 / page".

## Positive Flow

1. [CHK-FT-041] Check that the technicians table loads a paginated list of Field Technicians when the List page is opened.
2. [CHK-FT-042] Check that selecting filter values and pressing Filter displays only the matching technicians.
3. [CHK-FT-043] Check that pressing Clear resets all filters to their default values and restores the full technician list.
4. [CHK-FT-044] Check that pressing Expand reveals the Last activity filter and pressing Collapse hides it.
5. [CHK-FT-045] Check that entering a query in the search input returns technicians matching by Name, Email, or Phone number.
6. [CHK-FT-046] Check that opening a technician from the List page shows the Details form prefilled with that technician's data.
7. [CHK-FT-047] Check that editing First name, Last name, Status, or Email and pressing Save persists the changes and shows the success toast "Changes saved".
8. [CHK-FT-048] Check that changing the Status value and pressing Save updates the displayed status for the technician.
9. [CHK-FT-049] Check that pressing the Delete icon on the Details page opens the delete confirmation modal.
10. [CHK-FT-050] Check that confirming Delete removes the technician, redirects to the List page, and shows the success toast "Field Technician deleted".
11. [CHK-FT-051] Check that pressing Cancel in the delete confirmation modal closes it and leaves the technician unchanged.
12. [CHK-FT-052] Check that selecting a different page in the pagination control fetches and displays the next set of technicians.
13. [CHK-FT-053] Check that selecting a sortable column header reorders the table rows by that column.

## Validation

1. [CHK-FT-054] Check that the First name field displays an inline required-field error when it is empty on Save.
2. [CHK-FT-055] Check that the Last name field displays an inline required-field error when it is empty on Save.
3. [CHK-FT-056] Check that the Status field displays an inline required-field error when no value is selected on Save.
4. [CHK-FT-057] Check that Save validates all required fields before persisting changes.
5. [CHK-FT-058] Check that field edits are not persisted if the user leaves the Details page without pressing Save.

## Negative Flow

1. [CHK-FT-059] Check that the "No results found" state is shown when applied filters or a search return no technicians.
2. [CHK-FT-060] Check that the Phone number, COPS match, and Last activity fields cannot be edited on the Details page.
3. [CHK-FT-061] Check that a filter request error does not break rendering of the technicians table.

## Status Behavior

1. [CHK-FT-062] Check that an Active technician is shown with a green status badge.
2. [CHK-FT-063] Check that an Inactive technician is shown with a grey status badge.
3. [CHK-FT-064] Check that a Pending technician is shown with an orange status badge.
4. [CHK-FT-065] Check that setting a technician's status to Inactive blocks that technician's access to the Mobile App.
5. [CHK-FT-066] Check that setting a technician's status to Active restores that technician's access to the Mobile App.

## Notifications and Alerts

1. [CHK-FT-067] Check that a "Changes saved" success toast appears after a technician's changes are saved.
2. [CHK-FT-068] Check that a "Field Technician deleted" success toast appears after a technician is deleted.

## Sorting, Filtering, and Pagination

1. [CHK-FT-069] Check that the Name, Phone number, Email, COPS match, Last activity, and Status columns are sortable while the Actions column is not.
2. [CHK-FT-070] Check that multiple filters can be applied simultaneously and the results match all selected criteria.
3. [CHK-FT-071] Check that pagination is handled server-side so that only the current page of technicians is fetched.
4. [CHK-FT-072] Check that the total technician count is displayed with the pagination controls.
5. [CHK-FT-073] Check that the previous-page arrow is disabled while the first page is displayed.
6. [CHK-FT-074] Check that the Last activity filter returns technicians within the selected date range when a range is chosen.

## Data Saving and Persistence

1. [CHK-FT-075] Check that saved changes to a technician remain after the Details page is reloaded.
2. [CHK-FT-076] Check that a deleted technician no longer appears in the List page after deletion.
3. [CHK-FT-077] Check that a status change persists after the page is reloaded.

## API and Backend Error Handling

1. [CHK-FT-078] Check that an error message and a retry option are shown if the technician list fails to load.
2. [CHK-FT-079] Check that an error message is shown and the current form state is preserved if a Save request fails.
3. [CHK-FT-080] Check that an error message is shown and the technician is not removed if a Delete request fails.

## Empty States

1. [CHK-FT-081] Check that the empty state shows the illustration and the text "No field technicians have been added yet" when no technicians exist.

## Loading States

1. [CHK-FT-082] Check that a loading indicator is displayed while the technician list is being fetched.

## Cross-browser

1. [CHK-FT-083] Check that the List and Details pages render correctly in the latest Chrome.
2. [CHK-FT-084] Check that the List and Details pages render correctly in the latest Firefox.
3. [CHK-FT-085] Check that the List and Details pages render correctly in the latest Edge.

## Security

1. [CHK-FT-086] Check that a user without an authorized role cannot access the Field Technician Details page.
2. [CHK-FT-087] Check that navigating directly to a Field Technician Details URL without an active session is blocked or redirected to Login.
3. [CHK-FT-088] Check that no control allows modifying technician data from the List page.

## Regression Checks

1. [CHK-FT-089] Check that navigating from the Field Technicians pages to other modules such as Managers and Surveys still works.
2. [CHK-FT-090] Check that the global header and left navigation continue to function while on the Field Technicians pages.
3. [CHK-FT-091] Check that the shared data-table component still renders correctly on the Managers list after Field Technicians changes.

## Open Questions

- [Phone number editability — SRS FR-FT-DET-03/11/12 treat Phone number as an editable, required, validated field, but the design shows it read-only/disabled — confirm which is correct, because it changes whether edit and validation checks apply.]
- [Email editability — SRS marks Email read-only (controlled by Mobile App registration), but the design shows it editable and not required — confirm which wins, as it affects edit, validation, and persistence checks.]
- [Status value "Pending" — SRS defines only Active and Inactive (plus a hidden Archived), but the design shows a "Pending" badge in the table and as a Status filter option — confirm whether Pending is a valid status and whether it is selectable on the Edit dropdown.]
- [Delete modal copy — the design's modal body reads "All data associated with manager <name> will be deleted permanently" (says "manager", includes the name), while the SRS wording is "All data associated with this technician will be deleted permanently" — confirm the correct text.]
- [COPS match vocabulary — the filter option is "Not found", the table cell shows "-", and the Details read-only field shows "Matched"/"Not matched" — confirm a single consistent label for the no-match case.]
- [Items-per-page options — the design shows only "10 / page", while the SRS mentions e.g. 10/25/50 — confirm which page sizes are supported.]
- [Audit logging — NFR-FT-DET-02 lists logging of deletions and status changes as "recommended" — confirm whether it is in scope for this release and how QA can verify it.]
- [Status-to-Mobile-App effect — Active/Inactive status is stated to grant/block Mobile App access, a cross-system effect — confirm how QA should verify Mobile App login is blocked or restored from the Admin Panel.]

**Coverage summary:** functional: 37 / UI: 31 / validation: 5 / permissions: 10 / edge cases: 8
