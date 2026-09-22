# QA Checklist: Mobile Order List (Jobs List)

> Feature: Orders List screen (List view + Calendar/Weekly view) for Field Technicians.
> Platform: Mobile — cross-platform Flutter app.
> Sources: [docs/srs/mobile/02-order-list.md](../../../../docs/srs/mobile/02-order-list.md),
> Figma "Jobs" (fileKey `EXAMPLEmobileFileKey00`, nodes `635:4219` list, `645:4380` calendar,
> `644:23181` list-empty, `648:4434` calendar-empty, `930:5278` no-internet),
> rendered screens in [docs/designs/mobile/screens/](../../../../docs/designs/mobile/screens/).
> Checks are written to match the **design**; SRS↔design disagreements are parked in Open Questions.

## Functional — List view

1. [CHK-ORDE-001] Check that after successful authentication the Orders List (Jobs list) is shown as the primary landing screen with the user's assigned orders.
2. [CHK-ORDE-002] Check that the top app bar headline reads exactly "Jobs list".
3. [CHK-ORDE-003] Check that the list displays one Order card per assigned order, each showing date · time, status badge, job title, and location row.
4. [CHK-ORDE-004] Check that each Order card shows the scheduled date and time as "14 Aug 2026 | 10:00" with a vertical divider between date and time.
5. [CHK-ORDE-005] Check that the job title renders as "<Job ID> - <name>" (e.g. "4567 - Cable installation").
6. [CHK-ORDE-006] Check that the location row shows a location-pin icon, then "<address, city>", a vertical divider, then "<State>" (e.g. "128 Oak Lane, Austin | Texas").
7. [CHK-ORDE-007] Check that orders are sorted by scheduled date and time in ascending order (FR-ORD-02).
8. [CHK-ORDE-008] Check that tapping an Order card navigates to the Order Details screen (FR-ORD-03).
9. [CHK-ORDE-009] Check that a "New" status badge renders as a pill with a red dot and light-red (#F9DEDC) background.
10. [CHK-ORDE-010] Check that an "In progress" status badge renders as a pill with an amber dot and light-amber (#FFF0CE) background.
11. [CHK-ORDE-011] Check that an updated order displays a full-width dark-red (#B80B22) banner across the card top with an alert-circle icon and the label "Updated" (FR-ORD-06).
12. [CHK-ORDE-012] Check that status badges are visually distinct and clearly readable against the white card (FR-ORD-05).
13. [CHK-ORDE-013] Check that the bottom navigation bar with "Jobs" (selected), "Notifications", and "Profile" remains visible on the Orders List at all times (FR-ORD-04).
14. [CHK-ORDE-014] Check that the "Jobs" bottom-nav item shows the selected/active state (maroon label + selection indicator) while on the Orders List.
15. [CHK-ORDE-015] Check that the order count and content match the orders returned for the authenticated user's phone number (FR-ORD-01).

## Functional — Empty state

16. [CHK-ORDE-016] Check that when no orders are assigned the screen shows the empty illustration, the title "No jobs", and the body "Your list of jobs is currently empty. New jobs from your Project Facilitator will appear here.".
17. [CHK-ORDE-017] Check that the empty state renders no Order cards and no error UI.
18. [CHK-ORDE-018] Check that the bottom navigation and the list/calendar toggle remain accessible in the empty state.

## Functional — Calendar (Weekly) view

19. [CHK-ORDE-019] Check that tapping the calendar icon in the app bar switches the List view to the Calendar (Weekly) view (FR-CAL-W-04).
20. [CHK-ORDE-020] Check that in Calendar view the app bar trailing icon changes to a list icon and tapping it switches back to List view.
21. [CHK-ORDE-021] Check that the weekly strip shows the day-of-week row "Sun Mon Tue Wed Thu Fri Sat" with the dates for the current week.
22. [CHK-ORDE-022] Check that the current day (today) is shown with a maroon (#782A2A) outline indicator.
23. [CHK-ORDE-023] Check that the selected day is shown with a filled maroon (#782A2A) circle and white date text.
24. [CHK-ORDE-024] Check that days that contain scheduled orders show a small red (#B80B22) dot indicator, and days without orders show none.
25. [CHK-ORDE-025] Check that the selected-day subheading below the week strip shows the weekday and date (e.g. "Wednesday, 9 February").
26. [CHK-ORDE-026] Check that selecting a day updates the list below to show only orders scheduled for that date (FR-CAL-W-06).
27. [CHK-ORDE-027] Check that the default selected date is today when today falls within the current week, otherwise the first day of the week (FR-CAL-W-02).
28. [CHK-ORDE-028] Check that the Order cards shown in Calendar view use the same component and fields as the List view.
29. [CHK-ORDE-029] Check that tapping an Order card in Calendar view navigates to the Order Details screen (FR-CAL-W-07).
30. [CHK-ORDE-030] Check that when no orders exist for the selected day the Calendar view shows the "No jobs" empty state (with the week strip still visible) instead of an empty list (FR-CAL-W-08).

## Permissions

> N/A for the Orders List feature itself — the list/calendar screen requests no runtime
> permissions. Location/GPS and notification permission prompts belong to the check-in flow
> (Order Details) and the Notifications tab respectively, and are covered by their own checklists.

## UI / Visual

31. [CHK-ORDE-031] Check that the List view matches the Figma design [docs/designs/mobile/screens/order-list_list-view.png](../../../../docs/designs/mobile/screens/order-list_list-view.png).
32. [CHK-ORDE-032] Check that the Calendar view matches the Figma design [docs/designs/mobile/screens/order-list_calendar-view.png](../../../../docs/designs/mobile/screens/order-list_calendar-view.png).
33. [CHK-ORDE-033] Check that the screen background is light gray (#F8F8FA) and Order cards are white with a 12px corner radius and a subtle elevation shadow.
34. [CHK-ORDE-034] Check that the screen respects the device safe area on iOS (notch, Dynamic Island, home indicator) without clipping the app bar, cards, or bottom navigation.
35. [CHK-ORDE-035] Check that the system status bar (time, network, battery) is shown with a consistent style above the app bar.
36. [CHK-ORDE-036] Check that text scales correctly with iOS Dynamic Type and Android font scale up to 200% without truncation or layout breakage on cards, badges, and the calendar strip.
37. [CHK-ORDE-037] Check that the Orders List and Calendar view render without truncation or overflow on the smallest supported screen (iPhone SE 4.7" / Pixel 4a 5.8").
38. [CHK-ORDE-038] Check that the Orders List and Calendar view render without overstretched controls on the largest supported screen (iPhone 15 Pro Max 6.7").
39. [CHK-ORDE-039] Check that the "Updated" card-top banner text is fully visible and not truncated regardless of title length.
40. [CHK-ORDE-040] Check that a long job title and a long address each wrap or truncate gracefully within the card without overlapping the status badge.

## Gestures & navigation

41. [CHK-ORDE-041] Check that tapping anywhere on an Order card (not only the title) activates navigation to Order Details.
42. [CHK-ORDE-042] Check that on Android the system back button on the Orders List (root tab) exits the app rather than navigating to a blank back stack.
43. [CHK-ORDE-043] Check that on Android 14+ the predictive back gesture on the Orders List behaves consistently with the system back button.
44. [CHK-ORDE-044] Check that the order list scrolls smoothly when the number of orders exceeds the viewport, with the bottom navigation remaining fixed.
45. [CHK-ORDE-045] Check that switching between List and Calendar views preserves scroll position / selected day expectations and does not reset the screen unexpectedly.

## Lifecycle & state

46. [CHK-ORDE-046] Check that a cold start with a valid session lands directly on the Orders List screen.
47. [CHK-ORDE-047] Check that a warm start (return from background) restores the Orders List with the previously selected view (List/Calendar) and selected day.
48. [CHK-ORDE-048] Check that after the app is killed by the OS under memory pressure, resuming reloads the Orders List without crashing or losing the session.
49. [CHK-ORDE-049] Check that after an app update a valid session is preserved and the user lands on the Orders List with current data.
50. [CHK-ORDE-050] Check that changing the device locale while the app is suspended re-renders the Orders List labels (and date formats) in the new locale on next launch.

## Network

51. [CHK-ORDE-051] Check that with connectivity (Wi-Fi or cellular) the Orders List loads the current orders for the authenticated user.
52. [CHK-ORDE-052] Check that when offline, previously cached orders are displayed if available (FR-ORD-09, FR-CAL-W-10).
53. [CHK-ORDE-053] Check that if orders fail to load due to a network error, an error message is shown and the user can retry loading the list (FR-ORD-08, FR-CAL-W-09).
54. [CHK-ORDE-054] Check that the dedicated "No internet connection" screen shows the body "Slow or no internet connection. Check the Internet settings and try again" with a working "Try again" button.
55. [CHK-ORDE-055] Check that on a slow / flaky network a loading indicator is shown and the list populates once data arrives (no indefinite hang).
56. [CHK-ORDE-056] Check that switching between Wi-Fi and cellular mid-load completes the request or recovers via retry without duplicate cards.
57. [CHK-ORDE-057] Check that toggling airplane mode while on the Orders List transitions to cached/offline behavior and recovers when connectivity returns.
58. [CHK-ORDE-058] Check that when the access token expires the app silently refreshes or prompts re-authentication rather than showing a broken/empty list.
59. [CHK-ORDE-059] Check that the order list stays in sync with the backend (GET jobs by phone number) and reflects newly assigned or updated orders after a refresh/relaunch.

## Notifications

> N/A for the Orders List screen itself — it does not raise or react to push notifications.
> The order-assignment trigger is an SMS deep link (see Deep links). The "Notifications" bottom-nav
> destination is a separate feature with its own checklist.

## Deep links / Universal Links / App Links

60. [CHK-ORDE-060] Check that opening the SMS access link on a device where the app is NOT installed redirects the user to the correct app marketplace page.
61. [CHK-ORDE-061] Check that opening the link when the app is installed but the user is not yet registered navigates to the Registration screen.
62. [CHK-ORDE-062] Check that opening the link when the user is registered and authenticated opens the Orders List (Jobs list) screen.
63. [CHK-ORDE-063] Check that the access link can be reused within 72 hours and continues to grant access to the order list.
64. [CHK-ORDE-064] Check that using the link after 72 hours denies access and displays: "Link expired. Your access link is no longer valid (72 hours passed). Please contact your Project Facilitator.".
65. [CHK-ORDE-065] Check that when a registered user opens a link whose job is associated with a different phone number, the app displays the "Assigned to a different phone number" dialog with the message about logging out and signing in with the linked phone number (FR-ORD-01-1).
66. [CHK-ORDE-066] Check cold-start vs warm-start entry from the link both land on the correct screen for the user's auth state.

## Accessibility

67. [CHK-ORDE-067] Check that on iOS VoiceOver announces each Order card with its job title, status, date/time, and location, and announces the app-bar toggle and bottom-nav items with descriptive labels.
68. [CHK-ORDE-068] Check that on Android TalkBack announces the same Order card content, the list/calendar toggle, and bottom-nav items with descriptive labels.
69. [CHK-ORDE-069] Check that the reading/focus order follows a logical top-to-bottom, card-by-card flow.
70. [CHK-ORDE-070] Check that order status is conveyed by text ("New" / "In progress" / "Updated"), not by color alone.
71. [CHK-ORDE-071] Check that card text, status badges, and the "Updated" banner meet WCAG AA contrast.
72. [CHK-ORDE-072] Check that calendar day cells announce their state (today, selected, has-orders) to screen readers, not only via color/dot.

## Performance

73. [CHK-ORDE-073] Check that the Orders List cold-start to first meaningful render meets the target time on a P0 device.
74. [CHK-ORDE-074] Check that scrolling a long order list and toggling List↔Calendar stays smooth (~60fps) with no visible jank.
75. [CHK-ORDE-075] Check that repeatedly opening, refreshing, and toggling the screen does not grow memory unbounded.

## Security

76. [CHK-ORDE-076] Check that no sensitive data (tokens, phone number, job payloads) is written to device logs (`adb logcat`, Console.app).
77. [CHK-ORDE-077] Check that the session/access token is stored only in the Keychain (iOS) / EncryptedSharedPreferences (Android), never in plain UserDefaults / SharedPreferences.
78. [CHK-ORDE-078] Check that all order-list network requests are sent over HTTPS only.
79. [CHK-ORDE-079] Check that the app-switcher snapshot does not expose order data if a privacy-blur policy applies.

## Localization & RTL

80. [CHK-ORDE-080] Check that all static strings (app bar, empty state, status labels, error messages) are localized with no hardcoded literals.
81. [CHK-ORDE-081] Check that scheduled date, time, and weekday formats render per the device locale.
82. [CHK-ORDE-082] Check that, where RTL locales are supported, the list, card layout, and calendar strip mirror correctly.

## Device-class coverage

83. [CHK-ORDE-083] Check the Orders List on a P0 iOS device (iPhone 15, iOS 17.4).
84. [CHK-ORDE-084] Check the Orders List on P0 Android devices (Pixel 7 and Samsung Galaxy S23, Android 14).
85. [CHK-ORDE-085] Check on the smallest supported screen (iPhone SE 3rd gen / Pixel 4a).
86. [CHK-ORDE-086] Check on the largest supported screen (iPhone 15 Pro Max).
87. [CHK-ORDE-087] Check on the lowest supported OS version (iOS 16.7 / Android 13).

## Crash / ANR

88. [CHK-ORDE-088] Check that loading and navigating the Orders List 10× in a row produces no crashes.
89. [CHK-ORDE-089] Check that rapidly toggling List↔Calendar and spamming day selection produces no ANR or frozen UI.
90. [CHK-ORDE-090] Check that rapid repeated taps on an Order card open Order Details exactly once (no double-navigation).
91. [CHK-ORDE-091] Check that the crash reporter (Crashlytics / Sentry) shows no new issues after a smoke run of the Orders List.

## Open Questions

1. **Status filtering (FR-ORD-02 vs design).** The SRS describes status filter buttons ("New", "In Progress") in the top app bar and that orders are "grouped and filterable by status". The design shows **no top-level filter control** — status appears only as per-card badges. Confirm whether status filtering is in scope and how it is triggered. (Checks written to the design: no filter control.)
2. **Calendar week navigation (FR-CAL-W-03 vs design).** The SRS specifies a current month/year display and previous/next week navigation arrows. The design's Calendar view shows a **single week with no month/year header and no prev/next arrows**. Confirm how week navigation is performed.
3. **Date inconsistency in design.** Card dates read "14 Aug 2026" while the calendar selected-day subhead reads "Wednesday, 9 February" (no year) — likely placeholder data. Confirm the production date/time format and whether the year is shown.
4. **"Unsubmitted" label.** The SRS lists "Unsubmitted" (and "Submitted/Unsubmitted" flags) as optional card labels; this label is **not present in the design**. Confirm whether it exists and how it renders.
5. **Site Name field.** The SRS lists "Site Name" separately from "City, State". The design's card location row shows only "<address, city> | <State>" with no distinct Site Name line. Confirm whether Site Name should be displayed and where.
6. **Screen naming.** App bar reads "Jobs list", bottom-nav reads "Jobs", and the SRS titles it "Orders List". Confirm the canonical user-facing names.
7. **Pull-to-refresh / manual refresh.** No refresh affordance is shown in the design and the SRS does not define a manual refresh; sync frequency/trigger (SRS section A) is explicitly undecided. Confirm refresh and background-sync behavior.
8. **Loading / skeleton state.** No loading or skeleton frame exists in the design for the list. Confirm the expected loading indicator while orders are fetched.
9. **Dark mode.** Dark-theme parity for the Orders List and Calendar view is not specified.
10. **RTL support.** RTL layout support (Arabic, Hebrew) is not specified for this screen.

**Coverage summary:** functional: 30 / UI: 10 / network & offline: 9 / deep links: 7 / accessibility: 6 / lifecycle: 5 / device-class: 5 / crash & ANR: 4 / security: 4 / performance: 3 / localization: 3 / gestures: 5
