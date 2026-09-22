3.1.3 Field Technicians  
3.1.3.1 FT list page


The Field Technicians List page provides Admin Panel users with a centralized view of all Field Technicians using the Mobile Application.

The screen is designed to:
	•	Display key identification and activity data for Field Technicians;
	•	Allow filtering and searching across technician attributes;
	•	Indicate account and integration status (e.g., COPS match);
	•	Serve as the entry point to Field Technician Details;
	•	Support operational monitoring without modifying technician accounts.

Entry Conditions & Preconditions
	•	User is authenticated.
	•	User has Root or Manager role.
	•	Field Technician records exist in the system (or empty state is shown).
UI Description

Layout
	•	Standard Admin Panel layout:
	•	Left-side navigation menu
	•	Top header with user profile menu
	•	Main content area displaying filters and the technicians table

Page Header

Title:
List of Field Technicians

Filters Panel

A filter bar is displayed above the table.

Available Filters:
	•	COPS match
	•	Select
	•	Matched
	•	Not found
	•	Status
	•	Active
	•	Inactive
	•	Last activity
	•	Date picker (single date or range)

Filter Controls:
	•	Filter button – applies selected filters
	•	Clear button – resets filters
	•	Expand / Collapse – toggles filter visibility

Field Technicians Table

The Field Technicians List is displayed as a data table.

Table Columns:
	•	Name
	•	Phone number
	•	Email
	•	COPS match
	•	Last activity
	•	Status
	•	Actions

Row Actions

Each row provides:
	•	Edit / View action
	•	Navigates to Field Technician Details page

Status Indicators
	Status
	•	Active
	•	Inactive
	•	Archived (technical status which is not visible on UI)
	•	Status is visually indicated with text and color.

Empty & No Results States

Empty State (No Technicians)
	•	Illustration
	•	Text:
“No field technicians have been added yet”

No Results State (Filters Applied)
	•	Illustration
	•	Text:
“No results found”

Loading State
	•	Skeleton rows or loader displayed while fetching data

Pagination & Table Controls
	•	Pagination controls at bottom:
	•	Page number navigation
	•	Items per page selector (e.g., 10 / 25 / 50)
	•	Total items count displayed
Functional Requirements

Access Control

FR-FT-LIST-01
The system shall allow Root Users and Manager Users to access the Field Technicians List page.

Data Display

FR-FT-LIST-02
The system shall display a paginated list of all Field Technicians.

FR-FT-LIST-03
Each table row shall display accurate technician data for all defined columns.

Search (Optional / If Enabled)

FR-FT-LIST-07
The system may support free-text search across Name, Email, and Phone number.



Navigation

FR-FT-LIST-08
Selecting the row action shall navigate to the Field Technician Details page.

Navigation & Flow Logic

User Action
Result
Open Field Technicians
Table displayed
Apply filters
Filtered results shown
Clear filters
Full list restored
No matching data
No Results state shown
Click row action
Navigate to Technician Details
Change page
Fetch next page


Error Handling

FR-FT-LIST-11
If Field Technician data fails to load:
	•	Display an error message;
	•	Provide a retry option.

FR-FT-LIST-12
Filter errors shall not break table rendering.

Security Requirements

NFR-FT-LIST-01
Field Technician data shall be read-only in this screen.

NFR-FT-LIST-02
Access to technician data shall be restricted to authorized roles.
3.1.3.2 FT details page
The Field Technician Details page allows Admin Panel users to view and manage detailed information about a specific Field Technician registered in the Mobile Application.

The screen is designed to:
	•	Display core identification and contact information;
	•	Show system and integration-related metadata (e.g., COPS match);
	•	Manage technician account status;
	•	Provide administrative control such as disabling or deleting a technician;
	•	Serve as a reference point for operational monitoring and troubleshooting.
Entry Conditions & Preconditions
	•	User is authenticated.
	•	User has Root or Manager role.
	•	User navigates from Field Technicians List by selecting a technician.
UI Description

Layout
	•	Standard Admin Panel layout:
	•	Left-side navigation menu
	•	Top header with breadcrumb navigation
	•	Main content area displaying technician details form

Page Header

Title:
Edit Field Technician

Primary Actions:
	•	Save button – persists changes
	•	Delete icon/button – opens delete confirmation dialog

Technician Information Form

Identification Fields

First Name
	•	Text input
	•	Required

Last Name
	•	Text input
	•	Required

Contact & Account Fields

Email
	•	Text input
	•	Read-only (email is controlled by Mobile App registration)

Phone Number
	•	Text input
	•	Required
	•	Displayed in international format

Status & System Fields

Status
	•	Dropdown selector
	•	Required
	•	Available values:
	•	Active
	•	Inactive

Behavior:
	•	Active → Technician can log in and use the Mobile App
	•	Inactive → Technician access to Mobile App is blocked

COPS Match
	•	Read-only field
	•	Possible values:
	•	Matched
	•	Not matched
	•	Indicates external system (COPS) integration status

Last Activity
	•	Read-only timestamp
	•	Indicates last known interaction with the Mobile App

Delete Field Technician
	•	Destructive action available via delete button
	•	Opens confirmation modal:

Confirmation Message:

“Delete field technician?
All data associated with this technician will be deleted permanently.”

Actions:
	•	Cancel
	•	Delete

Functional Requirements

Data Display

FR-FT-DET-01
The system shall display complete and accurate Field Technician information.

FR-FT-DET-02
Read-only fields (Email, COPS match, Last activity) shall not be editable.

Edit Behavior

FR-FT-DET-03
Users shall be able to update editable fields:
	•	First name
	•	Last name
	•	Phone number
	•	Status

FR-FT-DET-04
Changes shall not be persisted until Save is selected.

Status Handling

FR-FT-DET-05
Changing status to Inactive shall immediately prevent Mobile App access.

FR-FT-DET-06
Changing status to Active shall restore Mobile App access.

Save Behavior

FR-FT-DET-07
Selecting Save shall:
	•	Validate required fields;
	•	Persist changes to the backend;
	•	Display a success notification.

Delete Behavior

FR-FT-DET-08
Deleting a Field Technician shall permanently remove the technician record.

FR-FT-DET-09
Deletion shall require explicit confirmation.

FR-FT-DET-10
After deletion, the user shall be redirected to the Field Technicians List page.

Validation & Error Handling

Client-Side Validation

FR-FT-DET-11
Required fields shall display inline validation errors when empty.

FR-FT-DET-12
Invalid phone number formats shall be rejected before submission.

Server-Side Errors

FR-FT-DET-13
If saving or deleting fails:
	•	Display an error message;
	•	Preserve current form state.


Navigation & Flow Logic

User Action
Result
Open Technician Details
Details form displayed
Modify fields
Save enabled
Click Save
Changes persisted
Change status
Status updated
Click Delete
Confirmation dialog
Confirm delete
Technician removed
Cancel delete
Return to details


Security Requirements

NFR-FT-DET-01
Only authorized users (Root, Manager) may access this page.

NFR-FT-DET-02
Deletion and status changes shall be logged for audit purposes (recommended).



3.1.3.3 Search, Filters, and Sorting
Filters Panel

A filter bar is displayed above the table.

Available Filters:
	•	COPS match
	•	Select:
	•		Matched
	•		Not found
	•	Status:
	•		Active
	•		Inactive
	•	Last activity:
	•		Date picker (single date or range)

Filter Controls:
	•	Filter button – applies selected filters
	•	Clear button – resets filters
	•	Expand / Collapse – toggles filter visibility

Filtering functional requirements

FR-FT-LIST-04
The system shall allow filtering by:
	•	COPS match
	•	Status
	•	Last activity date

FR-FT-LIST-05
Multiple filters may be applied simultaneously.

FR-FT-LIST-06
Selecting Clear shall reset all filters to default values.

Search (Optional / If Enabled)

FR-FT-LIST-07
The system may support free-text search across Name, Email, and Phone number.

Pagination & Sorting
FR-FT-LIST-09
The system shall support server-side pagination.

FR-FT-LIST-10
The system shall support column-based sorting (e.g., Name, Last activity).
