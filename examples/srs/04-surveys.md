3.1.4 Surveys 
3.1.4.1 Surveys list page
The Surveys List page provides Admin Panel users with a centralized overview of all surveys created in the system, including their lifecycle status and association with orders.

The screen is designed to:
	•	Display all surveys created from survey templates;
	•	Allow filtering, searching, and sorting of surveys;
	•	Show survey publication and draft states;
	•	Provide entry points for viewing, editing, publishing, or deleting surveys;
	•	Support operational review of survey configurations sent to the Mobile Application.

Entry Conditions & Preconditions
	•	User is authenticated.
	•	User has Root or Manager role.
	•	Survey module is enabled.

UI Description

Layout
	•	Standard Admin Panel layout:
	•	Left-side navigation menu
	•	Top header with user profile and settings
	•	Main content area displaying filters and surveys table

Page Header

Title:
Surveys

Primary Action:
	•	Add button
	•	Navigates to Create Survey flow

Filters Panel

A collapsible filters section is displayed above the table.

Available Filters:
	•	Created by:
	•		Dropdown list of Admin users
	•	Status:
	•	Draft
	•	Published
	•	Created at:
	•		Date picker
	•	Last updated:
	•		Date picker

Filter Controls:
	•	Filter – apply selected filters
	•	Clear – reset all filters
	•	Expand / Collapse – toggle advanced filters visibility

Surveys Table

The Surveys List is displayed as a data table.

Table Columns:
	•	ID
	•	Title
	•	Order ID
	•	Created by
	•	Created at
	•	Last updated
	•	Status
	•	Actions

Status Indicators

Survey status is visually indicated:
	•	Draft – survey not available in Mobile App
	•	Published – survey available to Field Technicians
	•	Archived (technical status which is not visible on UI)

Row Actions

Each survey row provides:
	•	View / Edit – open Survey Details page
	•	Download PDF - downloading survey pdf file

Empty & No Results States

Empty State (No Surveys)
	•	Illustration
	•	Text:
“No surveys have been added yet”

No Results State (Filters Applied)
	•	Illustration
	•	Text:
“No results found”

Loading State
	•	Table skeleton or loader displayed while surveys data is being fetched

Pagination & Table Controls
	•	Pagination controls at the bottom:
	•	Page navigation
	•	Items per page selector (e.g., 10 / 25 / 50)
	•	Total surveys count displayed

Functional Requirements

Access Control

FR-SUR-LIST-01
The system shall allow Root Users and Manager Users to access the Surveys List page.

Data Display

FR-SUR-LIST-02
The system shall display a paginated list of all surveys.

FR-SUR-LIST-03
Each row shall display accurate survey metadata for all defined columns.

Survey Creation

FR-SUR-LIST-04
Selecting Add shall navigate the user to the Create Survey page.

Filtering

FR-SUR-LIST-05
The system shall allow filtering surveys by:
	•	Created by
	•	Status
	•	Created date
	•	Last updated date

FR-SUR-LIST-06
Multiple filters may be applied simultaneously.

FR-SUR-LIST-07
Selecting Clear shall reset all filters.

Sorting

FR-SUR-LIST-08
The system shall allow column-based sorting (e.g., Created at, Status).

Actions

FR-SUR-LIST-09
Selecting View/Edit shall navigate to the Survey Details page.

FR-SUR-LIST-10
Deleting a survey shall require confirmation.

Pagination

FR-SUR-LIST-11
The system shall support server-side pagination.

3.1.4.2 Add/Edit survey page / Survey Editor
The Survey Editor allows Administrators and Managers to design, configure, and publish surveys that will be completed by Field Technicians in the Mobile Application.

This screen is designed to:
	•	Build surveys from scratch or from a template
	•	Add, edit, and organize questions
	•	Group questions into sections
	•	Define conditional logic (skip rules)
	•	Preview the survey as seen by a technician
	•	Save drafts, publish surveys, and export to PDF
Key Features:
Question Types: Surveys support various question formats, including:
Yes/No
Checkbox (multiple selection)
Radio (single selection)
Text Input
Photo Upload
Date Picker
Time Picker
Structure: Questions, which can be logically grouped into sections.
Conditional Logic (Skip Logic): For Yes/No and Radio question types, the editor allows Managers to define extra logic to skip certain subsequent questions and jump directly to a specified question.
Preview: A Preview option is available to visualize how the survey will appear on the Field Technician's Mobile App.
Export: Surveys can be downloaded as a PDF file.
Save and Publishing: Surveys can be saved as drafts, and publishited. 

Entry Conditions & Preconditions
	•	User is authenticated
	•	User navigates to Surveys → Add Survey or opens an existing draft
	•	Survey must have a title before publishing



UI Description

Top Action Bar

Button
Description
Create
Switch to editing mode
Preview
Switch to mobile preview mode
Save as template
Save current survey structure as reusable template
Save
Save survey as draft
Publish
Make survey active and assignable to jobs


Survey Metadata Section

Field
Type
Required
Template
Dropdown
No
Survey title
Text
Yes


Survey Structure

A survey consists of:
	•	Sections (optional groupings)
	•	Questions within sections or root level

Each question is displayed in a collapsible card.

Question Types Supported

Type
Description
Yes / No
Binary selection
Checkbox
Multiple choice
Radio
Single choice
Text
Free text input
Photo
Photo upload
Date
Date picker
Time
Time picker


Question Editor
Each question contains:

Element
Description
Question title
Editable text
Question type
Dropdown selector
Answers (if applicable)
Options list
Add answer
Adds option
Custom answer toggle
Allows “Other” option
Logic link
Configure skip logic
Duplicate
Copy question
Delete
Remove question
Drag handle
Reorder question


Section Management

FR-SURV-SEC-01
Users can add sections to group related questions.

FR-SURV-SEC-02
Sections can be reordered via drag-and-drop.

FR-SURV-SEC-03
Sections can be renamed or deleted.

Conditional Logic (Skip Logic)
Available for Yes/No and Radio questions only.
Logic Definition
For each answer option, the user may define:
If this answer is selected → Go to [Target Question]

Functional Requirements

FR-SURV-LOG-01
Logic can only point to a question that appears later in the survey.

FR-SURV-LOG-02
Multiple logic rules may exist for a question.

FR-SURV-LOG-03
Logic rules must not create circular navigation.

FR-SURV-LOG-04
Removing a target question shall remove associated logic rules.

Preview Mode

Preview renders the survey exactly as seen in the Mobile App.

FR-SURV-PREV-01
Preview must simulate:
	•	Question order
	•	Question types
	•	Section grouping
	•	Skip logic behavior

Save & Publish

Save Draft

FR-SURV-SAVE-01
Saving stores survey as editable draft.

Publish

FR-SURV-PUB-01
Published surveys become assignable to jobs.

FR-SURV-PUB-02
Published surveys cannot be structurally edited; changes require versioning.

Export

FR-SURV-PDF-01
Users can download survey structure as a PDF document.

Navigation Flow


Action
Result
Add question
Question card added
Change type
Fields update dynamically
Add logic
Logic configuration opens
Preview
Mobile preview opens
Save
Draft stored
Publish
Survey activated


Error Handling

FR-SURV-ERR-01
Survey cannot be published without a title.

FR-SURV-ERR-02
Invalid logic configurations shall show error.

FR-SURV-ERR-03
Deleting a question used in logic prompts confirmation.

Acceptance Criteria for Survey Editor:


	•	Questions can be added, edited, reordered
	•	Sections group questions correctly
	•	Logic navigation works
	•	Preview matches Mobile App layout
	•	Survey can be saved and published
	•	PDF export works


3.1.4.3 Search, Filters, and Sorting
Filters Panel

A collapsible filters section is displayed above the table.

Available Filters:
	•	Created by
	•	Dropdown list of Admin users
	•	Status
	•	Draft
	•	Published
	•	Created at
	•	Date picker
	•	Last updated
	•	Date picker

Filter Controls:
	•	Filter – apply selected filters
	•	Clear – reset all filters
	•	Expand / Collapse – toggle advanced filters visibility

Filtering

FR-SUR-LIST-05
The system shall allow filtering surveys by:
	•	Created by
	•	Status
	•	Created date
	•	Last updated date

FR-SUR-LIST-06
Multiple filters may be applied simultaneously.

FR-SUR-LIST-07
Selecting Clear shall reset all filters.

Sorting

FR-SUR-LIST-08
The system shall allow column-based sorting (e.g., Created at, Status).

Search
FR-SUR-LIST-09
The system shall allow sorting based on Order ID, and a Title 
