3.1.2 Order list screen
The Orders List Screen provides Field Technicians with a centralized view of all assigned jobs (orders). It enables users to:
	•	Quickly see currently assigned orders;
	•	Identify order status and required actions;
	•	Navigate to detailed order information;
	•	Understand when no orders are currently assigned.

This screen serves as the primary landing screen after successful login.

UI Description - Main Layout

Top app bar with:
	•	Calendar icon (switches from List view to a Calendar weekly view)
Status filter buttons:
	•	New
	•	In Progress
Bottom navigation bar:
	•	Orders (active)
	•	Notifications
	•	Profile

3.1.2.0 Job Assignment Flow
A unique link for a specific job is generated. This link will add the job to the technician's queue, which is associated with their phone number.
The link is sent via SMS to the technician's phone number.
The link is valid for 72 hours.
Opening the link:
If the mobile application is not downloaded, the user will be redirected to the relevant app marketplace page to download it.
If the application is downloaded:
If the user is not yet registered, the system will navigate them to the registration screen.
If the user is registered, the link will open the job list screen within the mobile application.
Flow of getting Jobs by a FT :


A. Job ID Retrieval: Our system will use a specific API endpoint to GET the Job ID (linked to a Field Technician and a Survey) by sending the FT's phone number. We need to decide on the optimal frequency/trigger for calling this endpoint with selected phone numbers.
B. SMS Generation: After retrieving the associated Jobs, our system will generate a URL and send it to the Field Technician via SMS.
C. Authentication: The Field Technician will use this URL to authenticate (which validates the phone number) and gain access to their Job list, which will be valid for the next 72 hours.



Error Handling: 
	
The link can be reused within 72 hours. If the URL is used after 72 hours expired, system will deny access and display error: 

“Link expired. Your access link is no longer valid (72 hours passed).
Please contact your Project Facilitator.”
5. User sees Job List on Mobile App UI.
6. In order to continuously synchronize job list on mobile app with COPS, we can use the same endpoint GET_Jobs/phoneNumber OR you would need to prepare a new one, just for this specific reason.
3.1.2.1 List view
List view of the Order List displays Order cards.

Order Card Elements
Each order card shall display:
	•	Job ID (as the main bold line) 
•	Site Name
•	City, State
	•	Scheduled Date | Scheduled Time Date
	•	Order status badge (New, In Progress )
	•	Optional informational labels:
		•	Unsubmitted
	•	Updated
Empty State
When no orders are available:
	•	Placeholder illustration/icon
	•	Title text: “No orders”
	•	Informational message explaining that: No orders are currently assigned
Functional Requirements

FR-ORD-01
The system shall display a list of orders assigned to the authenticated user via access link.

FR-ORD-01-1
If a registered user attempts to access the application via a link, but the account is not linked to the phone number associated with that specific link, the application must display the error message: "Assigned to a Different Phone Number."

FR-ORD-02
Orders shall be grouped and filterable by status:
	•	New
	•	In Progress
Orders shall be sorted by a date and time (ascending order)
FR-ORD-03
Selecting an order card shall navigate the user to the Order Details Screen.

FR-ORD-04
The Orders List shall remain accessible via bottom navigation at all times.

FR-ORD-05
Order status badges shall be visually distinct and clearly readable.

FR-ORD-06
Special indicators (e.g., Updated) shall be displayed when applicable.

Data Requirements

FR-ORD-07 
Each order item shall include:
	•	Order ID
	•	Order title
	•	Status
	•	Site name 
•	City, State 
	•	Scheduled start date/time
	•	Actual start date/time (if started)
	•	Flags (Updated, Submitted/Unsubmitted)

Error Handling

FR-ORD-08
If orders fail to load due to a network error:
	•	An error message shall be displayed;
	•	The user shall be able to retry loading the list.
FR-ORD-09
Cached orders shall be displayed when offline, if available.
3.1.2.2 Calendar (Weekly) view 
Weekly View screen provides Field Technicians with a time-oriented view of assigned orders, organized by week and specific dates.
It enables users to:
	•	See which orders are scheduled on a given day;
	•	Switch between list-based and calendar-based planning;
	•	Quickly identify workload distribution within a week;
	•	Navigate to order details directly from a selected date.

This screen complements the Orders List view and supports planning and daily execution.

UI Description

Main Layout
Date selector section:
	•	Current month and year display
	•	Previous / Next week navigation arrows
	•	Days of the selected week (S–S)
	•	Visual indicator for: Selected day, Days containing scheduled orders
Status chips:
	•	New
	•	In Progress


Orders list for the selected day inherits Order card components from List view screen with a same Order Card Element: 
	•	Order ID
	•	Order title
	•	Status
	•	Site name 
•	City, State 
	•	Scheduled start date/time
	•	Actual start date/time (if started)
	•	Flags (Updated)

Empty State (Weekly View)
If no orders are scheduled for the selected day:
	•	Display a “No orders” empty state
	•	Show informational text explaining: No orders exist for the selected date
	•	New orders will appear when assigned (after verification flow is passed)
Functional Requirements

Calendar View Behavior


FR-CAL-W-01
The system shall display orders grouped by the selected calendar date within the current week.

FR-CAL-W-02
The default selected date shall be:
	•	Today, if today falls within the current week;
	•	Otherwise, the first day of the selected week.

FR-CAL-W-03
Users shall be able to navigate between weeks using previous and next controls.

FR-CAL-W-04
The user shall be able to switch between:
	•	Weekly calendar view
	•	Orders list view

FR-CAL-W-05
Orders shall be visible by status:
	•	New
	•	In Progress
Navigation


FR-CAL-W-06
Selecting a specific date shall update the order list to show only orders scheduled for that date.

FR-CAL-W-07
Selecting an order card shall navigate the user to the Order Details Screen.

Empty State Handling
FR-CAL-W-08
If no orders exist for the selected date, the system shall display the Empty State view instead of an empty list.

Error Handling

FR-CAL-W-09
If calendar or order data fails to load:
	•	Display an error message;
	•	Allow the user to retry.
FR-CAL-W-10
When offline, cached calendar and order data shall be displayed if available.
