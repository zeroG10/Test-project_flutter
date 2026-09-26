# QA Checklist: Notifications screen

> Source: Google Sheet `Check-list (CSV export)` (copy of "checklist-concert-technologies-flutter.csv"), spreadsheet id `csv-export` gid `0`, imported 2026-09-26 by automation/tools/import_checklist_from_sheets.py. IDs assigned at import; they are now the contract — never renumber.

## Screen entry & layout

1. [CHK-NOTIF-001] Check that the Notifications screen opens from the bottom navigation when the user taps the Notifications tab.
2. [CHK-NOTIF-002] Check that the Notifications screen displays the title “Notification list” at the top.
3. [CHK-NOTIF-003] Check that the Notifications bottom tab is visually selected when the Notifications screen is open.
4. [CHK-NOTIF-004] Check that the Notifications list is scrollable when the number of notifications exceeds the visible area.
5. [CHK-NOTIF-005] Check that the push notifications banner is displayed at the top of the Notifications screen when app push notifications are disabled in device settings.
6. [CHK-NOTIF-006] Check that the push notifications banner displays the text “Turn on push notifications” and the supporting message about job updates.
7. [CHK-NOTIF-007] Check that the banner displays the action “Go to Settings” as a tappable control.
8. [CHK-NOTIF-008] Check that tapping “Go to Settings” opens the device notification settings page for the app.
9. [CHK-NOTIF-009] Check that the push notifications banner is not displayed when push notifications are enabled for the app.

## Notification item content & UI

1. [CHK-NOTIF-010] Check that each notification item displays an icon that matches the notification type.
2. [CHK-NOTIF-011] Check that each notification item displays a title (e.g., “New job assigned”, “Job starts today”, “Job updated”, “Job cancelled”).
3. [CHK-NOTIF-012] Check that each notification item displays a description containing the related job reference (e.g., “Tower Maintenance #A-7 …”).
4. [CHK-NOTIF-013] Check that each notification item displays a chevron indicating it can be opened.
5. [CHK-NOTIF-014] Check that notification titles and descriptions are readable and do not overlap or truncate incorrectly on smaller screens.

## Ordering & data rules

1. [CHK-NOTIF-015] Check that notifications are displayed in reverse chronological order with the most recent notification shown first.
2. [CHK-NOTIF-016] Check that each notification item contains a valid type, title, description, and related job reference as returned by backend.
3. [CHK-NOTIF-017] Check that “Job starts today” notifications are generated only for jobs scheduled for the current day and are not shown for other dates.
4. [CHK-NOTIF-018] Check that “Job starts today” notifications appear at the expected time logic (daily on job day at 8 AM) when the device time/timezone matches the schedule rules.

## Navigation to Job Details

1. [CHK-NOTIF-019] Check that tapping a notification item opens the related Job Details screen for that notification’s job reference.
2. [CHK-NOTIF-020] Check that opening a notification keeps the bottom navigation available after returning back to Notifications.
3. [CHK-NOTIF-021] Check that if the related job is no longer available, tapping the notification shows the message “This job is no longer available.” and does not navigate to Job Details.

## Read/unread state & badges

1. [CHK-NOTIF-022] Check that unread notifications are visually distinguishable from read notifications using a badge or highlight.
2. [CHK-NOTIF-023] Check that a notification is marked as read immediately after it is opened from the Notifications list.
3. [CHK-NOTIF-024] Check that returning to the Notifications list shows the previously opened notification in the read state.
4. [CHK-NOTIF-025] Check that the unread indicator count (badge dot on the Notifications tab, if implemented) decreases when notifications are marked as read.

## Empty state

1. [CHK-NOTIF-026] Check that the empty state is displayed when no notifications exist for the user.
2. [CHK-NOTIF-027] Check that the empty state displays the text “No notifications yet” and “You’ll see updates about your jobs here.”
3. [CHK-NOTIF-028] Check that the push notifications banner (if push disabled) can still be shown together with the empty state without layout overlap.
4. [CHK-NOTIF-029] Check that if the device is offline, the screen shows cached notifications if available and displays an appropriate offline indicator/message if implemented.
5. [CHK-NOTIF-030] Check that if the device is offline, the screen shows cached notifications if available and displays an appropriate offline indicator/message if implemented.
6. [CHK-NOTIF-031] Check that long job names in notification descriptions are truncated gracefully without breaking layout.
