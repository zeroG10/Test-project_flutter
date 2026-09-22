3.1.2 Managers 
3.1.2.1 Managers list page


The Managers List page allows Root Users (Super Admins) to view, manage, and administer Manager and Root user accounts within the Admin Panel.

The screen is designed to:
	•	Provide an overview of all admin users (Managers and Root users);
	•	Display key account information and status;
	•	Enable creation of new users;
	•	Support basic account management actions (view/edit);
	•	Serve as the entry point to Manager Details.

Entry Conditions & Preconditions

	•	The user is authenticated.
	•	The authenticated user has the Root User role.
	•	The Managers module is enabled in system configuration.

UI Description

Layout
	•	Standard Admin Panel layout with:
	•	Left-side navigation menu
	•	Top header with user profile and settings
	•	Main content area displaying the Managers list


Page Header

Title:
List of Managers

Primary Action:
	•	Add button
	•	Opens the Add Manager flow (user creation)

Managers Table

The Managers List is displayed as a data table.

Table Columns:
	•	Name
	•	Email
	•	Role:
	•	Manager
	•	Admin (Root)
	•	Created at
	•	Last log in
	•	Status
	•	Active
	•	Pending
	•	Inactive
•	Actions

Row Actions

Each row provides contextual actions:
	•	Edit (navigate to Manager Details page)

Status Indicators
	•	Status is visually indicated using:
	•	Color
	•	Label text
	•	Status definitions:
	•	Active – account activated and usable
	•	Pending – invitation sent, password not set
	•	Inactive – account disabled

Empty State

When no Managers exist:
	•	Empty-state illustration
	•	Informational text:
“No managers have been added yet”
	•	Add button remains available

Loading State
	•	Table skeleton or loader displayed while data is being fetched


Pagination & Controls
	•	Pagination controls at the bottom of the table
	•	Items per page selector (e.g., 10 / 25 / 50)
	•	Total items count displayed

Functional Requirements

Access Control

FR-MAN-LIST-01
The system shall restrict access to the Managers List page to Root Users only.

FR-MAN-LIST-02
Manager users attempting to access this page shall be denied access.

Data Display

FR-MAN-LIST-03
The system shall display a paginated list of all Manager and Root user accounts.

FR-MAN-LIST-04
Each row shall display accurate user metadata as defined in the table columns.

Add Manager

FR-MAN-LIST-05
Selecting Add shall navigate the user to the Add Manager screen.

FR-MAN-LIST-06
Newly added Managers shall appear in the list immediately after creation.

Row Actions

FR-MAN-LIST-07
Selecting the Edit action shall navigate to the Manager Details page.

Sorting & Column Settings

FR-MAN-LIST-08
The system shall allow column-based sorting (e.g., Name, Created at, Status).

FR-MAN-LIST-09
Users may configure visible columns via a column settings control.

Pagination

FR-MAN-LIST-10
The system shall support server-side pagination.

FR-MAN-LIST-11
The selected page size shall persist during the session.

Navigation & Flow Logic



User Action
Result
Open Managers List
Table displayed
Click Add
Navigate to Add Manager
Click Edit
Navigate to Manager Details
No managers exist
Empty state shown
Change page
Fetch next page data
Sort column
Table sorted accordingly


Error Handling

FR-MAN-LIST-12
If managers data fails to load:
	•	Display an error message;
	•	Provide retry option.

FR-MAN-LIST-13
Partial data loads shall not break table rendering.

Security Requirements

NFR-MAN-LIST-01
User role checks shall be enforced on both frontend and backend.

NFR-MAN-LIST-02
Sensitive user data shall not be exposed beyond authorized roles.

3.1.2.2 Add/Edit Manager page

The Add / Edit Manager page allows Root Users (Super Admins) to create new admin users (Managers or Root users) and manage existing admin accounts.

This screen is designed to:
	•	Create new Manager or Root user accounts;
	•	Send invitation emails for account activation;
	•	View and update existing Manager details;
	•	Manage account status (Active / Pending / Inactive);
	•	Support administrative lifecycle management of Admin Panel users.

Entry Conditions & Preconditions

Add Mode
	•	User is authenticated as Root User
	•	User navigates from Managers List → Add

Edit Mode
	•	User is authenticated as Root User
	•	User selects an existing Manager from Managers List
UI Description

Layout
	•	Standard Admin Panel layout with:
	•	Left-side navigation menu
	•	Top header with user profile controls
	•	Main content area displaying the form

Page Title
	•	Add manager (Add mode)
	•	Edit manager (Edit mode)

Form Fields

Name
	•	Text input field
	•	Required
	•	Used as display name in Admin Panel

Email
	•	Text input field
	•	Required
	•	Must be a valid email format
	•	Immutable after account creation (Edit mode)

Role
	•	Dropdown selector
	•	Required
	•	Available values:
	•	Manager
	•	Admin (Root user)

Status (Edit Mode Only)
	•	Dropdown selector
	•	Available values:
	•	Pending
	•	Active
	•	Inactive
	•	Status behavior:
		•	Pending – invitation sent, password not set
	•	Active – account enabled
	•	Inactive – account disabled

System Fields (Read-only, Edit Mode)
	•	Created at
	•	Last log in (only visible when available)

Primary Actions

Add Mode
	•	Save & send invitation button

Edit Mode
	•	Save button
	•	Resend invitation button (Pending status only)

Secondary / Destructive Actions

Delete Manager
	•	Delete icon/button (Edit mode)
	•	Opens Delete Manager confirmation dialog:
“All data associated with manager [Name] will be deleted permanently.”

Functional Requirements

User Creation

FR-MAN-ADD-01
The system shall allow Root Users to create new Manager or Admin accounts.

FR-MAN-ADD-02
All required fields (Name, Email, Role) must be completed before submission.

FR-MAN-ADD-03
Email addresses must be unique across Admin Panel users.

Invitation Flow

FR-MAN-ADD-04
Upon successful creation, the system shall:
	•	Create the user in Pending status;
	•	Generate a secure activation link;
	•	Send an invitation email to the user.

FR-MAN-ADD-05
The activation link shall redirect the user to the Set Password page.

Edit Behavior

FR-MAN-ADD-06
The system shall preload existing user data in Edit mode.

FR-MAN-ADD-07
Changes to Name, Role, or Status shall be persisted upon Save.

Status Handling

FR-MAN-ADD-08
Changing status to Inactive shall prevent login access.

FR-MAN-ADD-09
Changing status to Active shall restore login access.

Resend Invitation

FR-MAN-ADD-10
For users in Pending status, the system shall allow resending the invitation email.

Delete Manager

FR-MAN-ADD-11
Deleting a Manager shall permanently remove the user account.

FR-MAN-ADD-12
Deletion shall require explicit confirmation.

Validation & Error Handling

Client-Side Validation

FR-MAN-ADD-13
Required fields shall display inline validation errors when empty.

FR-MAN-ADD-14
Invalid email formats shall be rejected before submission.

Server-Side Errors

FR-MAN-ADD-15
If creation or update fails:
	•	Display a descriptive error message;
	•	Preserve entered form data.

Navigation & Flow Logic

User Action
Result
Click Add
Open Add Manager page
Fill form correctly
Save enabled
Save & send invitation
Manager created
Edit existing manager
Open Edit Manager
Change status
Status updated
Resend invitation
Email resent
Delete manager
Confirmation dialog
Confirm delete
Manager removed


Security Requirements

NFR-MAN-ADD-01
Only Root Users shall access this screen.

NFR-MAN-ADD-02
Invitation links shall be single-use and time-limited.

NFR-MAN-ADD-03
Deleted users shall immediately lose system access.
3.1.2.3 Search, Filters, and Sorting

Sorting & Column Settings

FR-MAN-LIST-08
The system shall allow column-based sorting (e.g., Name, Created at, Status).

FR-MAN-LIST-09
Users may configure visible columns via a column settings control.
