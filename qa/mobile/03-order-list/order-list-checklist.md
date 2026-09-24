# QA Checklist: Order list screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-23 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## List view / General & Entry Logic

1. [CHK-ORDL-001] Check that the Orders List screen is displayed as the primary landing screen after successful login and authentication.
2. [CHK-ORDL-002] Check that the Orders List screen is opened when a registered user accesses the app via a valid job access link.
3. [CHK-ORDL-003] Check that the Orders List screen is not displayed for unauthenticated users and authentication flow is triggered instead.

## List view / Assigned to a Different Phone Number — Error Modal

1. [CHK-ORDL-004] Check that an error modal with the title “Assigned to a Different Phone Number” is displayed when a user opens a job link not linked to their phone number.
2. [CHK-ORDL-005] Check that the error modal displays explanatory text instructing the user to log out and sign in with the correct phone number.
3. [CHK-ORDL-006] Check that the error modal displays both “Cancel” and “Log out” action buttons.
4. [CHK-ORDL-007] Check that tapping “Cancel” closes the modal without logging the user out.
5. [CHK-ORDL-008] Check that tapping “Log out” logs the user out and navigates them to the authentication flow.

## List view / Layout & Navigation

1. [CHK-ORDL-009] Check that the top app bar is displayed on the Orders List screen with a calendar icon.
2. [CHK-ORDL-010] Check that tapping the calendar icon switches the view from List view to Calendar weekly view. (placeholder if Calendar view is implemented later)
3. [CHK-ORDL-011] Check that the bottom navigation bar is displayed on the Orders List screen.
4. [CHK-ORDL-012] Check that the Orders tab is highlighted as active in the bottom navigation bar.
5. [CHK-ORDL-013] Check that the Orders List screen remains accessible at all times via the bottom navigation bar.
6. [CHK-ORDL-014] Check that status filter buttons “New”, “In Progress”, and “Completed” are displayed on the Orders List screen.

## List view / Order List & Cards

1. [CHK-ORDL-015] Check that a list of order cards is displayed when orders are available for the authenticated user.
2. [CHK-ORDL-016] Check that each order card displays the Job ID as the primary bold element.
3. [CHK-ORDL-017] Check that each order card displays the Site Name for the order.
4. [CHK-ORDL-018] Check that each order card displays the City and State location information.
5. [CHK-ORDL-019] Check that each order card displays the scheduled date and scheduled time.
6. [CHK-ORDL-020] Check that each order card displays a visually distinct order status badge (e.g., New, In Progress).
7. [CHK-ORDL-021] Check that special indicators such as “Unsubmitted” are displayed on the order card when applicable.
8. [CHK-ORDL-022] Check that special indicators such as “Updated” are displayed on the order card when applicable.
9. [CHK-ORDL-023] Check that order status badges and indicators remain readable across different screen sizes.
10. [CHK-ORDL-024] Check that tapping an order card navigates the user to the corresponding Order Details screen.
11. [CHK-ORDL-025] Check that only a single navigation event is triggered when an order card is tapped multiple times rapidly.
12. [CHK-ORDL-069] Check that order cards on the Orders List screen are sorted by scheduled date and time in ascending order.

> CHK-ORDL-069 added 2026-09-24 on the owner's decision (SRS FR-ORD-02; Q-ORDL-4) — not in the team Sheet yet; the
> Sheet gets it only through `qa-sheets-sync` (dry-run first, owner confirms).

## List view / Empty State

1. [CHK-ORDL-026] Check that an empty state is displayed when no orders are assigned to the user.
2. [CHK-ORDL-027] Check that the empty state displays a placeholder illustration or icon.
3. [CHK-ORDL-028] Check that the empty state displays the title text “No orders”.
4. [CHK-ORDL-029] Check that the empty state displays an informational message explaining that no orders are currently assigned.
5. [CHK-ORDL-030] Check that orders assigned via a valid access link appear in the Orders List after synchronization.
6. [CHK-ORDL-031] Check that cached orders are displayed on the Orders List screen when the device is offline and cached data exists.
7. [CHK-ORDL-032] Check that the Orders List screen displays an appropriate message or indicator when no cached data is available offline. (placeholder for UX decision)
8. [CHK-ORDL-033] Check that an error message is displayed when the orders list fails to load due to a network error.
9. [CHK-ORDL-034] Check that the user is able to retry loading the Orders List after a network error occurs.
10. [CHK-ORDL-035] Check that the Orders List screen recovers correctly after connectivity is restored.
11. [CHK-ORDL-036] Check that the Orders List screen does not display duplicate orders after refresh or navigation events.

## Calendar (Weekly) View / General & Navigation

> Heading corrected after import: in the Sheet "Calendar (Weekly) View" sits in column B (row 205), so the parser
> read it as an empty group and kept "List view". Only the heading changed — IDs and texts are as imported.


1. [CHK-ORDL-037] Check that the Calendar (Weekly) view is displayed when the user switches from the Orders List view using the calendar control.
2. [CHK-ORDL-038] Check that the Calendar (Weekly) view is accessible only to authenticated users.
3. [CHK-ORDL-039] Check that the bottom navigation bar remains visible with the Orders tab highlighted while the Calendar view is active.
4. [CHK-ORDL-040] Check that the user can switch back from the Calendar (Weekly) view to the Orders List view using the list control.
5. [CHK-ORDL-041] Check that the current month and year are displayed in the date selector section of the Calendar view.
6. [CHK-ORDL-042] Check that the default selected date is today when today falls within the current displayed week.
7. [CHK-ORDL-043] Check that the first day of the week is selected by default when today does not fall within the current week.
8. [CHK-ORDL-044] Check that the days of the selected week (Sunday to Saturday) are displayed in the date selector.
9. [CHK-ORDL-045] Check that the selected date is visually highlighted in the week selector.
10. [CHK-ORDL-046] Check that days containing scheduled orders are visually indicated in the week selector.
11. [CHK-ORDL-047] Check that tapping the previous week arrow navigates to the previous calendar week.
12. [CHK-ORDL-048] Check that tapping the next week arrow navigates to the next calendar week.
13. [CHK-ORDL-049] Check that orders are displayed only for the currently selected date in the Calendar (Weekly) view.
14. [CHK-ORDL-050] Check that the order list updates immediately when a different date is selected.
15. [CHK-ORDL-051] Check that the Calendar view displays order cards using the same layout and elements as the Orders List view.
16. [CHK-ORDL-052] Check that each order card displays the Job ID as the primary identifier.
17. [CHK-ORDL-053] Check that each order card displays the Site Name and City, State information.
18. [CHK-ORDL-054] Check that each order card displays the scheduled start date and time.
19. [CHK-ORDL-055] Check that each order card displays the order status badge (New or In Progress).
20. [CHK-ORDL-056] Check that special flags such as “Updated” or “Unsubmitted” are displayed on order cards when applicable.
21. [CHK-ORDL-057] Check that only orders with status New or In Progress are displayed in the Calendar (Weekly) view.
22. [CHK-ORDL-058] Check that tapping an order card in the Calendar view navigates the user to the corresponding Order Details screen.
23. [CHK-ORDL-059] Check that multiple rapid taps on an order card do not trigger duplicate navigation events.
24. [CHK-ORDL-060] Check that an empty state is displayed when no orders are scheduled for the selected date.
25. [CHK-ORDL-061] Check that the empty state displays the title text “No orders”.
26. [CHK-ORDL-062] Check that the empty state displays informational text explaining that no orders exist for the selected date.
27. [CHK-ORDL-063] Check that the empty state is shown instead of an empty list when no orders are available for the selected date.
28. [CHK-ORDL-064] Check that cached calendar and order data is displayed when the device is offline and cached data exists.
29. [CHK-ORDL-065] Check that the Calendar (Weekly) view displays an appropriate state when offline and no cached data is available. (placeholder for UX decision)
30. [CHK-ORDL-066] Check that switching between weeks does not cause UI flickering or layout shifts.
31. [CHK-ORDL-067] Check that the Calendar (Weekly) view handles a large number of orders without performance degradation.
32. [CHK-ORDL-068] Check that the selected date and order list state are preserved when switching between Calendar and List views.
33. [CHK-ORDL-070] Check that jobs shown in the Orders List after a refresh are also shown in the Calendar (Weekly) view on their scheduled dates.

> CHK-ORDL-070 added 2026-09-24 on the owner's decision — the regression check for BUG-ORDL-001; not in the team Sheet
> yet (only through `qa-sheets-sync`, dry-run first, owner confirms).
