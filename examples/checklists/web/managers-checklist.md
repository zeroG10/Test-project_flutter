# QA Checklist: Managers

## Access and Permissions

1. [CHK-MGR-001] Check that the Managers list page is accessible to a user with the Root User role.
2. [CHK-MGR-002] Check that the Managers list page denies access to a user with the Manager User role and does not render the table.
3. [CHK-MGR-003] Check that the Add Manager page is accessible only to a user with the Root User role.
4. [CHK-MGR-004] Check that the Edit Manager page is accessible only to a user with the Root User role.
5. [CHK-MGR-005] Check that an unauthenticated user is redirected to the Login page when attempting to open the Managers list page directly via URL.
6. [CHK-MGR-006] Check that an unauthenticated user is redirected to the Login page when attempting to open the Add or Edit Manager page directly via URL.
7. [CHK-MGR-007] Check that a Manager User cannot see a Managers entry in the left-side navigation menu.
8. [CHK-MGR-008] Check that a Manager User attempting to open the Managers list page URL directly receives an access-denied response from the backend.
9. [CHK-MGR-009] Check that role checks for the Managers module are enforced on the backend independently of the frontend.

## Navigation

1. [CHK-MGR-010] Check that the Managers list page is reachable from the left-side navigation menu for a Root User.
2. [CHK-MGR-011] Check that clicking the Add button on the Managers list page navigates to the Add Manager page.
3. [CHK-MGR-012] Check that clicking the Edit action in a row on the Managers list page navigates to the Edit Manager page for the selected user.
4. [CHK-MGR-013] Check that after a Manager is successfully created on the Add Manager page the user is returned to the Managers list page.
5. [CHK-MGR-014] Check that after a Manager is successfully updated on the Edit Manager page the user remains on the Edit Manager page or is returned to the Managers list page per the configured flow.
6. [CHK-MGR-015] Check that after a Manager is successfully deleted from the Edit Manager page the user is returned to the Managers list page.
7. [CHK-MGR-016] Check that the browser Back button from the Add Manager page returns to the Managers list page without losing list state.
8. [CHK-MGR-017] Check that the browser Back button from the Edit Manager page returns to the Managers list page without losing list state.

## UI Layout

1. [CHK-MGR-018] Check that the Managers list page uses the standard Admin Panel layout with left-side navigation and top header.
2. [CHK-MGR-019] Check that the Managers list page displays the title "List of Managers" in the page header.
3. [CHK-MGR-020] Check that the Managers list page displays an Add button as the primary action in the page header.
4. [CHK-MGR-021] Check that the Managers list page displays the table columns Name, Email, Role, Created at, Last log in, Status, and Actions.
5. [CHK-MGR-022] Check that the Managers list page displays the Status column with both color indicator and label text.
6. [CHK-MGR-023] Check that the Managers list page displays pagination controls at the bottom of the table.
7. [CHK-MGR-024] Check that the Managers list page displays an items-per-page selector with options 10, 25, and 50.
8. [CHK-MGR-025] Check that the Managers list page displays the total items count near the pagination controls.
9. [CHK-MGR-026] Check that the Add Manager page displays the title "Add manager".
10. [CHK-MGR-027] Check that the Edit Manager page displays the title "Edit manager".
11. [CHK-MGR-028] Check that the Add Manager form displays the Name, Email, and Role fields.
12. [CHK-MGR-029] Check that the Add Manager form displays a "Save & send invitation" primary action button.
13. [CHK-MGR-030] Check that the Edit Manager form displays the Name, Email, Role, and Status fields.
14. [CHK-MGR-031] Check that the Edit Manager form displays the read-only system fields Created at and Last log in.
15. [CHK-MGR-032] Check that the Last log in field is hidden on the Edit Manager form if no value is available.
16. [CHK-MGR-033] Check that the Edit Manager form displays a Save primary action button.
17. [CHK-MGR-034] Check that the Edit Manager form displays a Delete icon or button for the destructive action.
18. [CHK-MGR-035] Check that the Delete Manager confirmation dialog displays the exact text "All data associated with manager [Name] will be deleted permanently." with the actual manager name substituted.

## Fields and Controls

1. [CHK-MGR-036] Check that the Name field on the Add Manager and Edit Manager forms is marked as required.
2. [CHK-MGR-037] Check that the Email field on the Add Manager and Edit Manager forms is marked as required.
3. [CHK-MGR-038] Check that the Role field on the Add Manager and Edit Manager forms is a dropdown with values "Manager" and "Admin".
4. [CHK-MGR-039] Check that the Role field on the Add Manager and Edit Manager forms is marked as required.
5. [CHK-MGR-040] Check that the Status field on the Edit Manager form is a dropdown with values "Pending", "Active", and "Inactive".
6. [CHK-MGR-041] Check that the Email field on the Edit Manager form is rendered as immutable (read-only or disabled).
7. [CHK-MGR-042] Check that the Resend invitation button is visible on the Edit Manager form only if the manager status is Pending.
8. [CHK-MGR-043] Check that the Resend invitation button is hidden on the Edit Manager form if the manager status is Active or Inactive.
9. [CHK-MGR-044] Check that the Save button on the Add Manager form is disabled while required fields are empty or invalid.
10. [CHK-MGR-045] Check that the Save button on the Edit Manager form is disabled while required fields are empty or invalid.
11. [CHK-MGR-046] Check that the Edit action is available in each row on the Managers list page.

## Positive Flow

1. [CHK-MGR-047] Check that a Root User can open the Managers list page and see the paginated list of all Manager and Root user accounts.
2. [CHK-MGR-048] Check that a Root User can open the Add Manager page from the Add button on the Managers list page.
3. [CHK-MGR-049] Check that submitting the Add Manager form with valid Name, Email, and Role creates a new user in Pending status.
4. [CHK-MGR-050] Check that submitting the Add Manager form with valid data triggers an invitation email containing a secure activation link.
5. [CHK-MGR-051] Check that a newly created Manager appears in the Managers list page immediately after creation.
6. [CHK-MGR-052] Check that the activation link from the invitation email opens the Set Password page for the new user.
7. [CHK-MGR-053] Check that opening the Edit Manager page preloads existing user data into the Name, Email, Role, and Status fields.
8. [CHK-MGR-054] Check that changing the Name on the Edit Manager form and clicking Save persists the new name.
9. [CHK-MGR-055] Check that changing the Role on the Edit Manager form and clicking Save persists the new role.
10. [CHK-MGR-056] Check that changing the Status on the Edit Manager form and clicking Save persists the new status.
11. [CHK-MGR-057] Check that clicking Resend invitation on a Pending manager triggers a new invitation email with a valid single-use activation link.
12. [CHK-MGR-058] Check that clicking Delete on the Edit Manager form opens the Delete Manager confirmation dialog.
13. [CHK-MGR-059] Check that confirming the Delete Manager dialog permanently removes the user account and returns the Root User to the Managers list page.
14. [CHK-MGR-060] Check that the deleted Manager no longer appears in the Managers list page after a successful deletion.

## Validation

1. [CHK-MGR-061] Check that the Add Manager form displays an inline required-field error for Name when submission is attempted with an empty Name.
2. [CHK-MGR-062] Check that the Add Manager form displays an inline required-field error for Email when submission is attempted with an empty Email.
3. [CHK-MGR-063] Check that the Add Manager form displays an inline required-field error for Role when submission is attempted without a Role selected.
4. [CHK-MGR-064] Check that the Add Manager form rejects an invalid email format with an inline error and prevents submission.
5. [CHK-MGR-065] Check that the Edit Manager form displays an inline required-field error for Name when submission is attempted with an empty Name.
6. [CHK-MGR-066] Check that the Add Manager form rejects a duplicate email already used by another Admin Panel user with a descriptive error.
7. [CHK-MGR-067] Check that invalid inputs on the Add and Edit Manager forms are highlighted with an error style.
8. [CHK-MGR-068] Check that the Save button on the Add Manager form remains disabled while any required field is empty or invalid.

## Negative Flow

1. [CHK-MGR-069] Check that the Managers list page is not rendered if the authenticated user has the Manager User role.
2. [CHK-MGR-070] Check that the Add Manager form preserves entered form data if creation fails due to a server-side error.
3. [CHK-MGR-071] Check that the Edit Manager form preserves entered changes if the update fails due to a server-side error.
4. [CHK-MGR-072] Check that cancelling or closing the Delete Manager confirmation dialog does not delete the user account.
5. [CHK-MGR-073] Check that attempting to change the Email field on the Edit Manager form does not modify the stored value.
6. [CHK-MGR-074] Check that the Resend invitation button is unavailable on the Edit Manager form for a non-Pending manager.

## Status Behavior

1. [CHK-MGR-075] Check that a newly created Manager has status Pending until the invitation activation link is used.
2. [CHK-MGR-076] Check that a Pending Manager transitions to Active after successfully setting a password via the activation link.
3. [CHK-MGR-077] Check that a Pending Manager cannot log in to the Admin Panel because no password has been set.
4. [CHK-MGR-078] Check that an Inactive Manager cannot log in to the Admin Panel.
5. [CHK-MGR-079] Check that changing status from Active to Inactive on the Edit Manager form immediately revokes the Manager's login access.
6. [CHK-MGR-080] Check that changing status from Inactive to Active on the Edit Manager form restores the Manager's login access.
7. [CHK-MGR-081] Check that the Status column on the Managers list page reflects status changes made on the Edit Manager form after save.
8. [CHK-MGR-082] Check that the Status indicator uses distinct colors for Active, Pending, and Inactive on the Managers list page.

## Notifications and Alerts

1. [CHK-MGR-083] Check that an invitation email is sent to the new Manager after successful creation on the Add Manager form.
2. [CHK-MGR-084] Check that the invitation email contains a single-use, time-limited activation link.
3. [CHK-MGR-085] Check that a new invitation email is sent when Resend invitation is clicked for a Pending Manager.
4. [CHK-MGR-086] Check that the previous activation link is invalidated when a new invitation email is sent via Resend invitation.
5. [CHK-MGR-087] Check that a success confirmation is shown after a Manager is successfully created on the Add Manager form.
6. [CHK-MGR-088] Check that a success confirmation is shown after changes are saved on the Edit Manager form.
7. [CHK-MGR-089] Check that a success confirmation is shown after a Manager is successfully deleted.

## Sorting, Filtering, and Pagination

1. [CHK-MGR-090] Check that the Name column on the Managers list page supports ascending and descending sort.
2. [CHK-MGR-091] Check that the Created at column on the Managers list page supports ascending and descending sort.
3. [CHK-MGR-092] Check that the Status column on the Managers list page supports ascending and descending sort.
4. [CHK-MGR-093] Check that the active sort column and direction are visually indicated in the column header on the Managers list page.
5. [CHK-MGR-094] Check that the column settings control on the Managers list page allows showing and hiding configurable columns.
6. [CHK-MGR-095] Check that pagination on the Managers list page uses server-side paging and fetches the next page when the page is changed.
7. [CHK-MGR-096] Check that changing the items-per-page selector on the Managers list page reloads the table with the new page size.
8. [CHK-MGR-097] Check that the selected page size on the Managers list page persists across navigations within the same session.
9. [CHK-MGR-098] Check that the selected page size on the Managers list page resets after the user logs out and back in.

## Data Saving and Persistence

1. [CHK-MGR-099] Check that a Manager created on the Add Manager form is persisted and visible on the Managers list page after a full page reload.
2. [CHK-MGR-100] Check that changes saved on the Edit Manager form are persisted and visible after a full page reload.
3. [CHK-MGR-101] Check that a deleted Manager is removed from persistence and does not reappear on the Managers list page after a full page reload.
4. [CHK-MGR-102] Check that column-settings visibility selections on the Managers list page persist for the duration of the session.
5. [CHK-MGR-103] Check that sort selection on the Managers list page persists while navigating between table pages within the same session.

## API and Backend Error Handling

1. [CHK-MGR-104] Check that the Managers list page displays an error message with a retry option if the managers data request fails.
2. [CHK-MGR-105] Check that the Managers list table continues to render available rows if the response contains partial data.
3. [CHK-MGR-106] Check that the Add Manager form displays a descriptive server error message if user creation fails due to a backend error.
4. [CHK-MGR-107] Check that the Edit Manager form displays a descriptive server error message if the update fails due to a backend error.
5. [CHK-MGR-108] Check that the Delete Manager confirmation dialog displays a descriptive error message and keeps the user account if the deletion request fails.
6. [CHK-MGR-109] Check that backend errors on the Managers pages do not expose stack traces or internal details to the user.
7. [CHK-MGR-110] Check that submission buttons on the Add and Edit Manager forms do not allow duplicate submissions while a request is in flight.

## Empty States

1. [CHK-MGR-111] Check that the Managers list page displays an empty-state illustration when no Managers exist.
2. [CHK-MGR-112] Check that the Managers list page displays the text "No managers have been added yet" when no Managers exist.
3. [CHK-MGR-113] Check that the Add button remains available on the Managers list page when the empty state is shown.

## Loading States

1. [CHK-MGR-114] Check that the Managers list page shows a table skeleton or loader while data is being fetched.
2. [CHK-MGR-115] Check that the Add Manager form shows a loading state on the "Save & send invitation" button while the create request is in flight.
3. [CHK-MGR-116] Check that the Edit Manager form shows a loading state on the Save button while the update request is in flight.
4. [CHK-MGR-117] Check that the Delete Manager confirmation dialog shows a loading state on the confirm button while the delete request is in flight.
5. [CHK-MGR-118] Check that the Edit Manager page shows a loading state while preloading existing user data on open.

## Cross-browser

1. [CHK-MGR-119] Check that the Managers list page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
2. [CHK-MGR-120] Check that the Add Manager page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
3. [CHK-MGR-121] Check that the Edit Manager page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
4. [CHK-MGR-122] Check that the Delete Manager confirmation dialog renders and functions identically on the latest versions of Chrome, Firefox, and Edge.
5. [CHK-MGR-123] Check that sorting and pagination controls on the Managers list page work on the latest versions of Chrome, Firefox, and Edge.

## Security

1. [CHK-MGR-124] Check that all Managers module requests are transmitted over HTTPS only.
2. [CHK-MGR-125] Check that role-based access for the Managers module is enforced on the backend regardless of frontend state.
3. [CHK-MGR-126] Check that a Manager User receives an authorization error from the backend when calling Managers list, create, update, or delete endpoints directly.
4. [CHK-MGR-127] Check that sensitive user fields are not returned to non-Root callers by the Managers endpoints.
5. [CHK-MGR-128] Check that the activation link generated for a new Manager is single-use and time-limited.
6. [CHK-MGR-129] Check that a deleted Manager's session and tokens are invalidated immediately after deletion.
7. [CHK-MGR-130] Check that pasting script payloads into the Name or Email fields on the Add or Edit Manager forms does not execute as code on the Managers list page or anywhere they are rendered.
8. [CHK-MGR-131] Check that an Inactive Manager's existing session is invalidated or denied access on the next protected action.
9. [CHK-MGR-132] Check that the Email field cannot be modified on the Edit Manager form via direct API call.

## Regression Checks

1. [CHK-MGR-133] Check that creating a new Manager does not affect existing Manager or Root user accounts on the Managers list page.
2. [CHK-MGR-134] Check that deleting a Manager does not affect other Manager or Root user accounts on the Managers list page.
3. [CHK-MGR-135] Check that changing a Manager's status does not affect other Managers' login access.
4. [CHK-MGR-136] Check that an existing active Root User session remains valid after another Manager is created, edited, or deleted.
5. [CHK-MGR-137] Check that the left-side navigation menu and role-based access for other modules remain intact after operations in the Managers module.

## Open Questions

- The SRS Search, Filters, and Sorting subsection (3.1.2.3) only defines sorting and column settings and does not mention a search box or filter controls — it is unclear whether a search input or status/role filters are in scope for the Managers list page, blocking related verification.
- The redirect target after a successful Save on the Edit Manager form is not specified — it is unclear whether the user stays on the Edit page or returns to the Managers list, affecting navigation checks.
- The redirect target after a successful "Save & send invitation" on the Add Manager form is not explicitly defined — it is unclear whether the user returns to the Managers list page or remains on the Add page.
- The activation link expiration window for the invitation email is not specified in the Managers SRS — testers cannot verify expiration boundary behavior.
- The Resend invitation behavior with regard to previously issued activation links (invalidation vs. coexistence) is not defined — testers cannot deterministically verify which link remains valid.
- The rules for editing a Root User's own account on the Edit Manager form (self-edit, self-deactivation, self-deletion) are not defined — it is unclear whether these are allowed.
- The behavior when the last Root User attempts to change their role to Manager or set Status to Inactive is not specified — this affects governance and lockout risk.
- The Status field on the Edit Manager form is not marked as required in the SRS — it is unclear whether Status can be cleared and what the default is.
- The maximum allowed length of the Name field and the rules for allowed characters and trimming are not specified.
- The Email field constraints (max length, normalization, case sensitivity for uniqueness) on the Add Manager form are not specified.
- The exact wording and channel (toast, banner, inline) of success and error notifications for Add, Edit, Delete, and Resend invitation are not defined in the SRS.
- The column settings persistence scope (per-session, per-user, across logins) is not specified — testers cannot verify persistence boundaries.
- Default sort column and direction for the Managers list page on first load are not specified.
- Whether deleting a Manager who owns or is referenced by other entities (e.g. surveys, templates) is allowed and what cascade behavior occurs is not defined.
- Whether the Last log in column reflects the user's local timezone or UTC and the display format are not specified.

**Coverage summary:** functional: 56 / UI: 25 / validation: 8 / permissions: 9 / edge cases: 39
