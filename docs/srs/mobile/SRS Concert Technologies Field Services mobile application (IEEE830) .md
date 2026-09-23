**Software Requirements  Specification** 

**for** 

**Concert Technologies Field services mobile application**

**Version  1.0.2**  
                              **Prepared by Alexander Moshenskiy**

**TRIARE  LLC**

**15/05/2026**

***Copyright © 1999 by Karl E. Wiegers. Permission is granted to use, modify, and distribute this document.***   
***Software Requirements Specification for Authentification module project***

# 

# **Table of Contents** {#table-of-contents}

[**Table of Contents	2**](#table-of-contents)

[Revision History	3](#revision-history)

[**1\. Introduction	4**](#1.-introduction)

[1.1 Purpose	4](#1.1-purpose)

[1.2 Intended Audience and Reading Suggestions	4](#1.2-intended-audience-and-reading-suggestions)

[1.3 Definitions, Acronyms, and Abbreviations	4](#1.3-definitions,-acronyms,-and-abbreviations)

[1.4 Product Scope	5](#1.4-product-scope)

[1.5 References	5](#1.5-references)

[**2\. Overall Description	5**](#2.-overall-description)

[**2.1 Product Perspective	5**](#2.1-product-perspective)

[2.2 Product Functions (High-Level)	6](#2.2-product-functions-\(high-level\))

[2.3 User Classes and Characteristics	6](#2.3-user-classes-and-characteristics)

[2.3.1 Field Technician (FT)	6](#2.3.1-field-technician-\(ft\))

[2.3.2 Project Facilitator (PF)	6](#2.3.2-project-facilitator-\(pf\))

[2.4 Operating Environment	6](#2.4-operating-environment)

[2.5 Design and Implementation Constraints	7](#2.5-design-and-implementation-constraints)

[2.6 Assumptions, Dependencies and Risks	7](#2.6-assumptions,-dependencies-and-risks)

[**3\. External Interface Requirements	8**](#3.-external-interface-requirements)

[3.1 User Interfaces	8](#3.1-user-interfaces)

[3.1.0 Splash screen	8](#3.1.0-splash-screen)

[3.1.1 Authentication	9](#3.1.1-authentication)

[3.1.1.1 Welcome screen	9](#3.1.1.1-welcome-screen)

[3.1.1.2 Registration screen	11](#3.1.1.2-registration-screen)

[3.1.1.1 Phone number verification screen	13](#3.1.1.1-phone-number-verification-screen)

[3.1.1.1 Login screen	16](#3.1.1.1-login-screen)

[3.1.2 Order list screen	19](#3.1.2-order-list-screen)

[3.1.2.1 List view	20](#3.1.2.1-list-view)

[3.1.2.2 Calendar (Weekly) view	21](#3.1.2.2-calendar-\(weekly\)-view)

[3.1.3 Order details screen	23](#3.1.3-order-details-screen)

[3.1.3.1 Details main screen	23](#3.1.3.1-details-main-screen)

[3.1.3.1.1 Location services pop-ups and logic	25](#3.1.3.1.1-location-services-pop-ups-and-logic)

[3.1.3.2 Attachments screen	27](#3.1.3.2-attachments-screen)

[3.1.3.2.1 Documents tab	28](#3.1.3.2.1-documents-tab)

[3.1.3.2.2 Photos tab	29](#3.1.3.2.2-photos-tab)

[3.1.3.3 Check in/Check out screens	29](#3.1.3.3-check-in/check-out-screens)

[3.1.3.4 In progress state	31](#3.1.3.4-in-progress-state)

[3.1.3.4.1 Submit deliverables pop-up	34](#3.1.3.4.1-submit-deliverables-pop-up-flow)

[3.1.3.4.2 Survey screen	36](#3.1.3.4.2-survey-screen)

[3.1.3.4.3 Photo report screen	39](#3.1.3.4.3-photo-report-screen)

[3.1.3.4.4 Add photo flow	40](#3.1.3.4.4-add-photo-flow)

[3.1.3.4.4 Delete photo pop-up	43](#3.1.3.4.4-delete-photo-pop-up)

[3.1.3.4.5 Notes screen	44](#3.1.3.4.5-notes-screen)

[3.1.3.4.6 Add note screen	47](#3.1.3.4.6-add-note-screen)

[3.1.3.4.7 Delete note pop-up	49](#3.1.3.4.7-delete-note-pop-up)

[3.1.4 Notifications screen	50](#3.1.4-notifications-screen)

[3.1.5 Profile screen	53](#3.1.5-profile-screen)

[3.2 Software Interfaces	57](#3.2-software-interfaces)

[3.3 Communication Interfaces	57](#3.3-communication-interfaces)

[3.3.1 Offline Functionality	57](#3.3.1-offline-functionality)

[3.3.2 Notifications and Alerts	57](#3.3.2-notifications-and-alerts)

[**4\. System Features	58**](#4.-system-features)

[**5\. Other Requirements	58**](#5.-other-requirements)

[5.1 Performance	58](#5.1-performance)

[5.2 Security	58](#5.2-security)

[5.3 Usability	58](#5.3-usability)

[5.4 Reliability	58](#5.4-reliability)

[5.5 Scalability	58](#5.5-scalability)

[5.6. Product backlog	58](#5.6.-product-backlog)

# 

## **Revision History**  {#revision-history}

| Name | Date | Reason For Changes  | Version |
| ----- | ----- | ----- | ----- |
| SRS  | 06.01.2026 | \- | 0.9 |
| SRS  | 24.01.2026 | Base version (Ready for dev team review) | 0.9.1 |
| SRS  | 28.01.2026 | Base version (Validated by dev team) | 0.9.2 |
| SRS  | 02.02.2026 | Base version  | 1.0.0 |
| SRS | 15.04.2026 | Added 3.4.1 SMS Consent & Notification Workflow | 1.0.1 |
| **SRS** | **15.05.2026** | **Added Privacy Policy and Terms and Conditions links to appropriate sections** | **1.0.2** |

# **1\. Introduction**  {#1.-introduction}

## **1.1 Purpose**   {#1.1-purpose}

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for the Concert Technologies Mobile Application. The document is intended for stakeholders, project managers, developers, QA engineers, and third-party vendors involved in the design, development, testing, and deployment of the application.

This document describes system features, user interactions, constraints, assumptions, and acceptance criteria for the application.

## **1.2 Intended Audience and Reading Suggestions**  {#1.2-intended-audience-and-reading-suggestions}

This document is intended for all the project stakeholders, the project management team, and the development team, including frontend developers and quality assurance engineers.   
The list of intended audiences may be expanded during the project development. The structure of this document is represented in the following chapters:

- Introduction  
- Overall description  
- External interface requirements  
- System features  
- Other non-functional requirements  
- Other requirements

Proceedings through these sections are highly demanded to complete the overall vision of the product and detailed feature requirements.

## **1.3 Definitions, Acronyms, and Abbreviations** {#1.3-definitions,-acronyms,-and-abbreviations}

* **FT** – Field Technician  
* **PF** – Project Facilitator  
* **MVP** – Minimum Viable Product  
* **SOW** – Statement of Work  
* **COI** – Certificate of Insurance  
* **MFA** – Multi-Factor Authentication  
* **GPS** – Global Positioning System

## **1.4 Product Scope**  {#1.4-product-scope}

The Concert Technologies Mobile Application is a mobile solution designed for the Field Services team, specifically Field Technicians (FTs) and Project Facilitators (PFs). The application will streamline communication, job management, and the submission of deliverables such as surveys and photos.

The application will replace existing third-party tools (e.g., GoCanvas and CompanyCam) and serve as a centralized platform for job execution, documentation, and reporting.

## **1.5 References**  {#1.5-references}

This document refers to a list of artifacts (project materials) that fulfill the scope of outstanding requirements. The main artifacts influencing the requirements, scope, and time are part of the project plan.

Full list of references:

1. [Mobile Application UI/UX wireframes](https://www.figma.com/design/eAb4RANWzBFgqiyiA5hUZ0/Concert-Technologies--Mobile-app--For-review-?node-id=66-5957&t=gXnuyevrhfbvb1w7-1)   
2. [Internal Concert Technologies workflow documentation](https://docs.google.com/document/d/1UQlNVnWlfzmZC9CmmibdeHlzm_7-Ebcc/edit)  
3. [Concert Technologies Order Management API Reference (CTI-API)](https://docs.google.com/document/d/1ltD5a1jXQpd65CPY1PZGG_r-p9lv2r2J/edit?usp=drive_link&ouid=102488952034084129081&rtpof=true&sd=true)  
4. [Concert Technologies Order Management](https://docs.google.com/document/d/1b8gf8jPilNfZeCqjIPOFdl-nQKu0oQbV/edit)  
5. [Concert Technologies Mobile App API response model (Postman-based)](https://documenter.getpostman.com/view/12140442/2sBXVhCqQB#1f5dcd6b-564d-4aea-8072-0bf0e696b469)

Any other documents related to the project have a minor influence and do not reference the Software requirements specification document.

# **2\. Overall Description**  {#2.-overall-description}

# **2.1 Product Perspective**  {#2.1-product-perspective}

The application will be a standalone mobile app (iOS and Android) integrated with Concert Technologies’ backend systems. It will be used by external personnel: Field Technicians (FT).

## **2.2 Product Functions (High-Level)** {#2.2-product-functions-(high-level)}

The major functions of the application are determined within:

* Secure user authentication via Phone number and OTP verification  
* Order assignment and scheduling  
* Order document management  
* Check-in / check-out with time and GPS tracking  
* Survey completion and photo submission  
* Two-way notifications  
* Offline data capture and synchronization

## **2.3 User Classes and Characteristics**  {#2.3-user-classes-and-characteristics}

#### **2.3.1 Field Technician (FT)** {#2.3.1-field-technician-(ft)}

Field Technician at Concert Technologies installs, maintains, and supports technology infrastructure for large-scale, multi-site projects, managing everything from networks to specialized equipment, often deployed globally, requiring strong technical, communication, and problem-solving skills for onsite support in fast-paced, team-oriented environments. They work with diverse equipment and   
provide local technical expertise for major rollouts, ensuring high-quality deployment for clients.

The **FT** utilizes the Concert Technologies mobile application.

* Mobile-first user  
* Completes jobs (orders) on-site  
* Requires offline functionality  
* Limited administrative access

#### **2.3.2 Project Facilitator (PF)** {#2.3.2-project-facilitator-(pf)}

Project Facilitator (PF) is a technical project management role responsible for coordinating the on-site deployment of technology rollouts. Unlike administrative dispatchers, PFs are expected to understand the technology being installed to provide direct support to field technicians.

The **PF** utilizes the Concert Technologies web application. This role is responsible for **Order management** and the necessary **interaction** with both the orders and the **Field Technicians**.

* Assigns and manages jobs (orders)  
* Uploads and reviews documentation  
* Receives alerts and deliverables  
* Uses web or internal system (outside scope of mobile app UI unless specified)

## **2.4 Operating Environment**  {#2.4-operating-environment}

The mobile application will be developed using Flutter, a cross-platform technology. This allows  
for deployment on both major mobile operating systems, with the following minimum required  
versions:

* **iOS:** Version 16.0 and later  
* **Android:** Version 12.1 and later

The mobile application is designed to communicate with the Concert Technologies Order Management REST API. This API is built on the .NET framework.

The Mobile application is designed to communicate with the Survey Manager Web application via an REST API interface to retrieve Survey data. This API interface is built using Node.js technology.

 

## **2.5 Design and Implementation Constraints**  {#2.5-design-and-implementation-constraints}

The Concert Technologies mobile application will be developed for both iOS and Android platforms.

**Display and Design Specifications:**

* **Resolution Width:** The application must support a minimum width of **320px** and a maximum width of **1440px**.  
* **Design Source:** The primary source design file will be a **Figma .fig file**, which will contain:  
  1. Design Components  
  2. Project Wireframes  
  3. Project Prototype

**Operational Requirements:**

* The application must maintain functionality even with intermittent or absent network connectivity.

## **2.6 Assumptions, Dependencies and Risks** {#2.6-assumptions,-dependencies-and-risks}

**Assumption:**

* **A1:** Project Facilitators (PFs) utilize the existing Concert Technologies system for job assignment and management.

**Dependencies:**

* **D1: Backend API Availability:** Backend APIs must be available to support essential functions, including user authentication, job data retrieval, and document storage.  
* **D2: Data Management System:** The mobile application relies on data managed via a Concert Technologies web application. This requires dynamic data retrieval from a backend server connected to the DB content.  
* **D3: Frontend Framework:** A suitable frontend framework or library (e.g., Flutter) is required to build the mobile application. All necessary updates and modifications to this library must be applied to the application.

**Risk Factors**

* **R1: Design Changes:** Alterations to the design of the actual products may necessitate significant application updates and require re-submission to mobile marketplaces (App Store, Google Play).  
* **R2: Data Flexibility:** Dependence on hardcoded data would limit the application's flexibility and demand manual updates whenever data changes occur.

# **3\. External Interface Requirements**  {#3.-external-interface-requirements}

## **3\.1 User Interfaces**  {#3.1-user-interfaces}

This section describes the User interface of the Concert Technologies Mobile application with related logic and interactions with users. 

### **3.1.0 Splash screen** {#3.1.0-splash-screen}

The Splash Screen is displayed during application startup and serves to:  
	•	Present the Concert Technologies brand identity;  
	•	Mask application initialization and loading processes;  
	•	Perform initial system checks (authentication, configuration, session validation);  
	•	Provide a smooth transition to the next screen without exposing technical delays to the user.

**UI Description**

Visual Elements:  
	•	Full-screen white background  
	•	Centered Concert Technologies logo (static)  
	•	No interactive elements (buttons, links, inputs)  
	•	System status bar visible (time, network, battery)

Visual Requirements:  
	•	Logo must be centered both vertically and horizontally  
	•	No text labels, progress indicators, or user actions required

**Functional Requirements**

FR-SPL-01  
The Splash Screen shall be displayed immediately upon application launch.

FR-SPL-02  
While the Splash Screen is displayed, the application shall perform the following background operations:  
	•	Validate existing user session (if any);  
	•	Verify authentication token status;  
	•	Load essential application configuration and metadata.

FR-SPL-03  
The Splash Screen shall not require or allow any user interaction.

FR-SPL-04  
Upon completion of initialization, the application shall automatically navigate to:  
	•	the Login Screen, if the user is not authenticated;  
	•	the Home / Jobs List or Calendar Screen, if a valid session exists.

### **3.1.1 Authentication** {#3.1.1-authentication}

#### **3.1.1.1 Welcome screen** {#3.1.1.1-welcome-screen}

The Welcome Screen is the entry point to the mobile application for users who are not yet authenticated.

It is designed to:  
	•	Introduce the application to new and returning users  
	•	Provide clear navigation to account creation or login  
	•	Serve as a gateway into the authentication flow

**UI Description**

Layout  
	•	Full-screen, minimal layout  
	•	Centered welcome message  
	•	Two primary call-to-action buttons at the bottom  
Content

Header Text:

Welcome to the Concert Technologies

Subtext:

Create an account or log in to get started.

Primary Actions

| Button | Style | Function |
| ----- | ----- | ----- |
| **Sign up** | Primary (filled) | Navigate to account registration flow |
| **Login** | Secondary (outlined/neutral) | Navigate to login screen |

System UI  
	•	Device status bar visible  
	•	No navigation bar or back button on this screen  
**Functional Requirements**

Navigation

FR-WEL-01  
Tapping Sign up shall navigate the user to the Account Registration / Sign Up screen.

FR-WEL-02  
Tapping Login shall navigate the user to the Login screen.

Access Logic

FR-WEL-03  
The Welcome Screen shall be shown only when:  
	•	The user is not authenticated  
	•	No valid session token exists

FR-WEL-04  
If a valid session exists, the app shall bypass the Welcome Screen and navigate directly to the Home / Jobs screen.

**Navigation & Flow Logic**

| Condition | Result |
| ----- | ----- |
| App opened, user not logged in | Welcome Screen displayed |
| User taps Sign up | Navigate to Sign Up |
| User taps Login | Navigate to Login |
| Valid session detected | Skip Welcome → Home |

**Error Handling**

FR-WEL-05  
If navigation to Login or Sign Up fails, the app shall display a generic error and allow retry.

#### **3.1.1.2 Registration screen** {#3.1.1.2-registration-screen}

The Registration Screen allows a new Field Technician to create an account in the mobile application by providing basic personal and contact information.

This screen is designed to:  
	•	Collect required user identity details  
	•	Validate input before proceeding  
	•	Initiate the account creation process  
**UI Description**

Layout  
	•	Full-screen form layout  
	•	Centered title and subtitle  
	•	Stacked input fields  
	•	Primary action button at the bottom  
	•	Legal acceptance text below the button

Header

Title:

Registration

Subtitle:

Good to see you\! Let’s get you registered.

Input Fields

| Field | Type | Required | Notes |
| ----- | ----- | ----- | ----- |
| First name | Text | Yes | Alphabetical characters only(Minimum: 2 characters, Maximum: 100 characters) |
| Last name | Text | Yes | Alphabetical characters only (Minimum: 2 characters, Maximum: 100 characters) |
| Phone number | Phone | Yes | Must follow valid phone format |
| Email | Email | No | Optional but must be valid if provided |

Primary Action

| Button | State | Behavior |
| ----- | ----- | ----- |
| Continue | Disabled by default | Enabled only when required fields are valid |

Legal Text

Displayed below the button:

By continuing, you accept the Concert Technologies Terms and Privacy Policy

	•	“Terms” and “Privacy Policy” are tappable links

Privacy Policy link: [https://www.concerttech.com/mobile-privacy/](https://www.concerttech.com/mobile-privacy/)  
Terms and Conditions link: [https://www.concerttech.com/sms-terms-and-conditions/](https://www.concerttech.com/sms-terms-and-conditions/)

**Functional Requirements**

Field Validation

FR-REG-01  
First name is required.

FR-REG-02  
Last name is required.

FR-REG-03  
Phone number is required and must match a valid phone number format.

FR-REG-04  
Email is optional, but if entered, must match valid email format.

FR-REG-05  
Invalid fields shall display inline error messages:  
	•	“Field is required.”  
	•	“Invalid phone number.”  
	•	“Invalid email address.”

Button Behavior

FR-REG-06  
The Continue button shall remain disabled until all required fields are valid.

FR-REG-07  
When tapped, Continue shall:  
	•	Submit registration data to the backend  
	•	Proceed to the next step in the onboarding/authentication flow

Legal Links

FR-REG-08  
Tapping Terms shall open the Terms & Conditions web page.

FR-REG-09  
Tapping Privacy Policy shall open the Privacy Policy web page.  
Navigation & Flow Logic

| User Action | Result |
| ----- | ----- |
| Open Registration | Form displayed |
| Fill required fields correctly | Continue button enabled |
| Tap Continue | Registration request sent |
| Tap Terms / Privacy | Privacy Policy link: [https://www.concerttech.com/mobile-privacy/](https://www.concerttech.com/mobile-privacy/) Terms and Conditions link: [https://www.concerttech.com/sms-terms-and-conditions/](https://www.concerttech.com/sms-terms-and-conditions/) |
| Registration success | Navigate to next onboarding step |
| Registration failure | Error message shown |

Error Handling

FR-REG-10  
If the registration request fails (e.g., network error), the app shall:  
	•	Display an error message  
	•	Allow the user to retry

FR-REG-11  
If the phone number is already registered, the app shall display:

“This phone number is already associated with an account.”

#### **3.1.1.1 Phone number verification screen** {#3.1.1.1-phone-number-verification-screen}

The Phone Number Verification screen allows a Field Technician to verify ownership of their phone number by entering a one-time password (OTP) sent via SMS.

This step is designed to:  
	•	Confirm user identity  
	•	Prevent fraudulent account creation  
	•	Complete the registration authentication step

UI Description

Layout  
	•	Back navigation arrow at top  
	•	Title and subtitle centered  
	•	Display of the phone number being verified  
	•	4-digit OTP input field  
	•	Primary action button  
	•	Resend code information

Header

Title:

Phone number verification

Instruction text:

Enter the 4-digit code sent to your number

Phone number display:

\+1 415 555 2314 (example)

OTP Input  
	•	4 individual input boxes  
	•	Numeric keypad opens automatically  
	•	Auto-focus moves to next box after digit entry  
	•	Backspace moves to previous box

Primary Action

| Button | State | Behavior |
| ----- | ----- | ----- |
| Verify | Disabled until 4 digits entered | Submits OTP for validation |

Secondary Action

Resend Code Text:

Didn’t receive the code? You can request a new code in \[timer\]

	•	Countdown timer displayed  
	•	When timer reaches zero, text changes to tappable:

Request a new code

**Functional Requirements**

OTP Entry

FR-OTP-01  
The screen shall accept a 4-digit numeric OTP.

FR-OTP-02  
OTP input shall automatically advance focus as digits are entered.

FR-OTP-03  
Deleting a digit shall move focus backward.

Button Behavior

FR-OTP-04  
The Verify button shall be disabled until all 4 digits are entered.

FR-OTP-05  
Tapping Verify shall send the OTP to the backend for validation.

OTP Validation

FR-OTP-06  
If the OTP is correct, the user shall proceed to the next step in onboarding.

FR-OTP-07  
If the OTP is incorrect, an inline error shall display:  
Incorrect code

Resend Code

FR-OTP-08  
A countdown timer shall start immediately when the screen loads.

FR-OTP-09  
The user shall not be able to request a new code until the timer expires.

FR-OTP-10  
After the timer expires, the user can tap Request a new code.

FR-OTP-11  
Requesting a new code shall trigger a new OTP SMS and restart the timer.

Navigation & Flow Logic

| Condition | Result |
| ----- | ----- |
| Screen opened | Timer starts, OTP awaited |
| Correct OTP entered | Proceed to next onboarding step |
| Incorrect OTP | Error shown, allow retry |
| Timer expires | Resend option enabled |
| New code requested | New OTP sent, timer restarts |

Error Handling

FR-OTP-12  
If OTP verification fails due to network issues, display a generic error and allow retry.

FR-OTP-13  
If maximum retry attempts are exceeded, the user shall be temporarily blocked (2 minutes)  and informed.

#### **3.1.1.1 Login screen** {#3.1.1.1-login-screen}

The Login Screen allows an existing Field Technician to authenticate using their registered phone number and begin the sign-in process.

This screen is designed to:  
	•	Collect the user’s phone number  
	•	Validate input format  
	•	Initiate the authentication flow (OTP verification)

**UI Description**

Layout  
	•	Full-screen form layout  
	•	Centered title and subtitle  
	•	Single input field  
	•	Primary action button  
	•	Legal acceptance text at bottom

Header

Title:

Log in

Subtitle:

Good to see you\! Let’s get you log in.

Input Field

| Field | Type | Required | Notes |
| ----- | ----- | ----- | ----- |
| Phone number | Phone | Yes | Must match valid phone format |

	•	Numeric keypad displayed

	•	International format supported (e.g., \+1 415 555 2314\)

Primary Action

| Button | State | Behavior |
| ----- | ----- | ----- |
| Log in | Disabled by default | Enabled when phone number is valid |

Legal Text

Displayed below the button:

By continuing, you accept the Concert Technologies Terms and Privacy Policy

	•	Both are tappable links

**Functional Requirements**

Field Validation

FR-LOG-01  
Phone number is required.

FR-LOG-02  
Phone number must match a valid format before enabling Log in.

FR-LOG-03  
Invalid or empty input shall show inline error:

Field is required.

Button Behavior

FR-LOG-04  
The Log in button shall remain disabled until a valid phone number is entered.

FR-LOG-05  
Tapping Log in shall:  
	•	Submit the phone number to the backend  
	•	Trigger OTP generation  
	•	Navigate to the Phone Number Verification (OTP) screen

Legal Links

FR-LOG-06  
Tapping Terms shall open the Terms & Conditions document.

FR-LOG-07  
Tapping Privacy Policy shall open the Privacy Policy document.

Navigation & Flow Logic

| User Action | Result |
| ----- | ----- |
| Open Login | Form displayed |
| Enter valid phone | Log in button enabled |
| Tap Log in | OTP requested and navigate to OTP screen |
| Tap Terms / Privacy | Legal document opens |

Error Handling

FR-LOG-08  
If the phone number is not associated with an account, display:

No account found with this phone number.

FR-LOG-09  
If login request fails due to network issues, show a generic error and allow retry.

### **3.1.2 Order list screen** {#3.1.2-order-list-screen}

The Orders List Screen provides Field Technicians with a centralized view of all assigned jobs (orders). It enables users to:  
	•	Quickly see currently assigned orders;  
	•	Identify order status and required actions;  
	•	Navigate to detailed order information;  
	•	Understand when no orders are currently assigned.

This screen serves as the primary landing screen after successful login.

**UI Description \- Main Layout**

Top app bar with:  
	•	Calendar icon (switches from List view to a Calendar weekly view)  
Status filter buttons:  
	•	New  
	•	In Progress  
Bottom navigation bar:  
	•	Orders (active)  
	•	Notifications  
	•	Profile

#### **3.1.2.0 Job Assignment Flow**

1. A unique link for a specific job is generated. This link will add the job to the technician's queue, which is associated with their phone number.  
2. The link is sent via SMS to the technician's phone number.  
3. The link is valid for 72 hours.  
4. Opening the link:  
   * If the mobile application is not downloaded, the user will be redirected to the relevant app marketplace page to download it.  
   * If the application is downloaded:  
     * If the user is not yet registered, the system will navigate them to the registration screen.  
     * If the user is registered, the link will open the job list screen within the mobile application.

Flow of getting Jobs by a FT :

* **A. Job ID Retrieval:** Our system will use a specific API endpoint to `GET` the Job ID (linked to a Field Technician and a Survey) by sending the FT's phone number. We need to decide on the optimal frequency/trigger for calling this endpoint with selected phone numbers.  
  * **B. SMS Generation:** After retrieving the associated Jobs, our system will generate a URL and send it to the Field Technician via SMS.  
  * **C. Authentication:** The Field Technician will use this URL to authenticate (which validates the phone number) and gain access to their Job list, which will be valid for the next 72 hours.

Error Handling:   
	  
The link can be reused within 72 hours. If the URL is used after 72 hours expired, system will deny access and display error: 

“Link expired. Your access link is no longer valid (72 hours passed).  
Please contact your Project Facilitator.”

5\. User sees Job List on Mobile App UI.

6\. In order to continuously synchronize job list on mobile app with COPS, we can use the same endpoint GET\_Jobs/phoneNumber OR you would need to prepare a new one, just for this specific reason.

#### **3.1.2.1 List view** {#3.1.2.1-list-view}

List view of the Order List displays Order cards.

**Order Card Elements**  
Each order card shall display:  
	•	Job ID (as the main bold line)   
•	Site Name  
•	City, State  
	•	Scheduled Date | Scheduled Time Date  
	•	Order status badge (New, In Progress )  
	•	Optional informational labels:  
		•	Unsubmitted  
	•	Updated  
**Empty State**  
When no orders are available:  
	•	Placeholder illustration/icon  
	•	Title text: “No orders”  
	•	Informational message explaining that: No orders are currently assigned  
**Functional Requirements**

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

**Data Requirements**

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

**Error Handling**

FR-ORD-08  
If orders fail to load due to a network error:  
	•	An error message shall be displayed;  
	•	The user shall be able to retry loading the list.  
FR-ORD-09  
Cached orders shall be displayed when offline, if available.

#### **3.1.2.2 Calendar (Weekly) view**  {#3.1.2.2-calendar-(weekly)-view}

Weekly View screen provides Field Technicians with a time-oriented view of assigned orders, organized by week and specific dates.  
It enables users to:  
	•	See which orders are scheduled on a given day;  
	•	Switch between list-based and calendar-based planning;  
	•	Quickly identify workload distribution within a week;  
	•	Navigate to order details directly from a selected date.

This screen complements the Orders List view and supports planning and daily execution.

**UI Description**

**Main Layout**  
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

**Empty State (Weekly View)**  
If no orders are scheduled for the selected day:  
	•	Display a “No orders” empty state  
	•	Show informational text explaining: No orders exist for the selected date  
	•	New orders will appear when assigned (after verification flow is passed)  
**Functional Requirements**

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

### **3.1.3 Order details screen** {#3.1.3-order-details-screen}

The Order Details Screen provides Field Technicians with a complete, read-only and action-oriented view of a single order.  
It enables users to:  
	•	Review job scope and instructions;  
	•	Access all relevant logistical information (vendor, location, schedule);  
	•	View updates and status indicators;  
	•	Navigate to related sub-features as an attachments;  
	•	Initiate job execution actions (e.g., Check-In).

This screen acts as the central hub for executing an assigned order.

#### **3.1.3.1 Details main screen** {#3.1.3.1-details-main-screen}

**UI Description**

Header  
	•	Order ID  
	•	Order title  
	•	Status  
•	Flags (Updated, Unsubmitted)  
Order Summary Section  
	•	Order name/Order ID  
	•	Order description / scope of work: Bullet-point or multi-line instructions  
	•	Clearly separated sections with visual dividers  
	•	PF Info: Name and phone number (with link to press and dial)  
•	Location: full address in the location. “On map” link to open location in a map view or   
external maps application)  
	•	Scheduled start date/time, Visual icons for date and time  
Attachments section  
•	Section navigates to Attachments screen  
Primary Action Button  
	•	Contextual primary action button displayed at the bottom:  
	•	Check In (for new or not-yet-started orders)  
	•	Button is prominent and always accessible  
**Functional Requirements**

Order Information Display  
FR-ORD-D-01  
The system shall display complete order details for the selected order.

FR-ORD-D-02  
Order details shall be read-only, except for explicitly interactive elements (links and actions).

Status & Indicators  
FR-ORD-D-03  
The current order status shall be clearly visible.

FR-ORD-D-04  
An “Updated” indicator shall be displayed if the order content has changed since received to a technician. Indicator disappears after a technician navigates outside a screen. Order should be possible to update until it’s submission. 

Location & Date Handling  
FR-ORD-D-05  
Selecting “On map” shall open the order location in:  
	•	an in-app map view, or  
	•	the device’s default map application.

FR-ORD-D-06  
Date and time information shall reflect the latest scheduled values provided by the system.

Navigation to Subsections

FR-ORD-D-07  
Selecting Attachments shall navigate to the Order Attachments screen.

Primary Action – Check In  
FR-ORD-D-08  
If the order status is New or not started, a Check In button shall be displayed.

FR-ORD-D-09  
Selecting Check In shall initiate the check-in workflow, including:  
	•	timestamp recording;  
	•	GPS capture (if enabled);  
	•	order status update to In Progress.  
Error Handling

FR-ORD-D-10  
If order details fail to load:  
	•	Display an error message;  
	•	Allow the user to retry.

FR-ORD-D-11  
When offline, previously cached order details shall be displayed if available.

	

##### **3.1.3.1.1 Location services pop-ups and logic** {#3.1.3.1.1-location-services-pop-ups-and-logic}

The Location Services feature supports accurate job site verification during check-in and check-out.  
It ensures transparency, user consent, and flexibility by:  
	•	Requesting location access only when required;  
	•	Clearly explaining why location data is used;  
	•	Allowing manual check-in when GPS is unavailable;  
	•	Validating proximity to the job site when GPS is enabled.  
**UI Components Description**

*Enable Location Services Prompt*  
Title: Enable Location Services  
Message:  
Explains that location is used for faster check-ins and accurate job site verification and is accessed only during active check-in or check-out actions.

Actions:  
	•	Enable – proceeds with system permission request  
	•	Cancel – dismisses the prompt and continues without GPS

*Location Disabled Prompt*

Title: Location Disabled  
Message:  
Informs the user that GPS check-in requires enabling location services in device settings, while manual check-in remains available.

Actions:  
	•	Go to settings – opens device location settings  
	•	Cancel – dismisses the prompt

*Check-in Location Mismatch Alert*

Title: Check-in Location Mismatch  
Message:  
Notifies the user that the current GPS location does not match the registered job site location.

Actions:  
	•	Got it – acknowledges the message and returns to the previous screen  
	•	Cancel – dismisses the alert

**Functional Requirements**

Location Permission Handling  
FR-LOC-01  
The system shall request location permission only when the user initiates a check-in or check-out action.

FR-LOC-02  
The system shall display the Enable Location Services prompt before triggering the operating system’s location permission dialog.

FR-LOC-03  
If the user selects Enable, the application shall request location access from the operating system.

FR-LOC-04  
If the user selects Cancel, the application shall proceed with manual (non-GPS) check-in, clearly flagging it as such.

Location Disabled Handling  
FR-LOC-05  
If location services are disabled at the device level, the system shall display the Location Disabled prompt.

FR-LOC-06  
Selecting Go to settings shall redirect the user to the device’s location settings screen.

FR-LOC-07  
Selecting Cancel shall return the user to the check-in flow without GPS validation.

GPS Validation Logic  
FR-LOC-08  
When GPS is enabled, the system shall capture the user’s current location at check-in and check-out.

FR-LOC-09  
The system shall compare the captured location with the registered job site location.

FR-LOC-10  
If the distance exceeds the allowed tolerance threshold (configurable), the system shall display the Check-in Location Mismatch alert. The system shall consider location limitations (bad GPS connection) and wait until it has stable connection. GPS approach should be \~50 meters minimum. GPS location logic should be implemented on a Client app side.

Manual Check-In Transparency  
FR-LOC-11  
All manual check-ins (with GPS enabled) shall be possible due to the necessity to track the GPS location of FT in cases when GPS coordinates are impossible to get technically. In such cases, the application will prompt a modal where the user enters the location manually and saves it to the order.

FR-LOC-12  
Manual check-ins shall not block job execution.

Error Handling

FR-LOC-13  
If location data cannot be retrieved due to system or sensor error, the system shall:  
	•	Notify the user;  
	•	System shall automatically take Order location and mark order with the tag (user did   
not confirmed GPS)

FR-LOC-14  
Location permission failures shall not prevent the user from continuing the job.

**Data Requirements**

The following data shall be recorded during check-in/check-out:  
	•	method (GPS/Manual)  
	•	coordinates  
	•	horizontal Accuracy (based on device)  
	•	 timestamp

#### **3.1.3.2 Attachments screen** {#3.1.3.2-attachments-screen}

Attachments screen allows Field Technicians to view, access, and manage all documents and photos associated with an order.  
It ensures that technicians can:  
	•	Review required documentation before and during the job;  
	•	View photos attached to the order for reference;  
	•	Open documents and images directly within the app;  
	•	Save files locally in cache data.

This screen supports job preparation, execution, and verification.

**Main Layout**  
	•	Header with: Back navigation control  
	•	Screen title: Attachments  
	•	Tab selector:  
		•	Documents  
		•	Photos  
Content area displaying attachments for the selected tab

**System Feedback**

	•	Toast or banner message displayed when:  
	•	A file is successfully saved to the device  
	•	An action completes successfully

**Functional Requirements**

Attachment Listing  
FR-ATT-01  
The system shall display all attachments associated with the selected order.

FR-ATT-02  
Attachments shall be separated into two categories:  
	•	Documents  
	•	Photos

FR-ATT-03  
The default selected tab shall be Documents.

**Offline Behavior**  
FR-ATT-04  
Previously downloaded attachments shall be accessible offline.

FR-ATT-05  
If an attachment is not available offline, the system shall notify the user when offline.

##### **3.1.3.2.1 Documents tab** {#3.1.3.2.1-documents-tab}

Each document item shall display:  
	•	File name (e.g., Safety instruction.pdf)  
	•	File type indicator (implicit via extension)  
	•	Tap action to open document in in-app viewer

Behavior:  
	•	Documents open in a full-screen document viewer  
	•	Vertical scrolling supported for multi-page documents  
	•	Zoom in/out scrolling supported  
	•	Close (X) control returns the user to the Attachments list

**Document Handling**  
FR-ATT-06  
Selecting a document shall open it in an in-app document viewer, but should require opening in a separate app that can handle it if interaction is required..

FR-ATT-07  
The document viewer shall support:  
	•	Multi-page documents  
	•	Vertical scrolling  
•	Zoom in/out scrolling supported  
	•	Read-only access

FR-ATT-08  
Users shall be able to save documents locally, when permitted by the operating system.

FR-ATT-09  
Supported formats: PDF, DOC, XLS

##### **3.1.3.2.2 Photos tab** {#3.1.3.2.2-photos-tab}

Screen shall display:  
	•	Grid layout of photo thumbnails  
	•	Consistent thumbnail sizing and spacing  
	•	Tap action opens photo in full-screen viewer

Photo Viewer:  
	•	Full-screen image display  
	•	Pinch-to-zoom and pan support  
	•	Close (X) control to return to the photo grid

**Photo Handling**  
FR-ATT-10  
Selecting a photo thumbnail shall open the image in a full-screen photo viewer.

FR-ATT-11  
The photo viewer shall support zoom and pan gestures.

#### **3.1.3.3 Check in/Check out screens** {#3.1.3.3-check-in/check-out-screens}

The Check-In and Check-Out Confirmation screens provide a clear, deliberate confirmation step before starting or finishing a job.  
They are designed to:  
	•	Prevent accidental check-ins or check-outs;  
	•	Clearly communicate the action being performed;  
	•	Ensure accurate time tracking and job state transitions;  
	•	Trigger GPS validation and time capture logic (if enabled).

These screens represent critical control points in the job lifecycle.

**UI Description** 

Shared Layout (Check-In & Check-Out)  
	•	Full-screen modal 	  
•	Header with: Close (X) icon to cancel the action  
	•	Screen title  
	•	Central visual placeholder (icon or illustration)  
	•	Primary message (action title)  
	•	Supporting explanatory text  
	•	Bottom action buttons:  
		•	Cancel  
		•	Confirm  
Check-In Actions:  
	•	Cancel – aborts the check-in process  
	•	Confirm – proceeds with job check-in, sends notification to a project facilitator  
Check-Out Actions:  
	•	Cancel – aborts the check-out process  
	•	Confirm – proceeds with job check-out, sends notification to a project facilitator

**Functional Requirements**

Check-In Logic

FR-CIO-01  
The system shall display the Check-In Confirmation screen when the user initiates a check-in action.

FR-CIO-02  
Selecting Confirm on the Check-In screen shall:  
	•	Record the check-in timestamp;  
	•	Capture GPS location if enabled;  
	•	Flag the check-in method (GPS or manual);  
	•	Update the order status to In Progress.  
•	Sends an email notification to a PF with a text “FT \*First name, Last name\*   
checked-in to Order ID \*number\*”

FR-CIO-03  
Selecting Cancel or closing the screen shall:  
	•	Abort the check-in;  
	•	Leave the order status unchanged.

Check-Out Logic

FR-CIO-04  
The system shall display the Check-Out Confirmation screen when the user has submitted deliverables successfully and initiates a check-out action.

FR-CIO-05  
Selecting Confirm on the Check-Out screen shall:  
	•	Record the check-out timestamp;  
	•	Capture GPS location if enabled; GPS coordinate should be accurate in about 100   
meters  
	•	Flag the check-out method (GPS or manual);  
	•	Mark the order as Completed or other status (per workflow rules).  
•	Sends an email notification to a PF with a text “FT \*First name, Last name\*   
checked-out of Order ID \*number\*”

FR-CIO-06  
Selecting Cancel or closing the screen shall:  
	•	Abort the check-out;  
	•	Leave the order status unchanged.

Location Integration

FR-CIO-07  
Check-In and Check-Out actions shall trigger location permission and validation logic as defined in the Location Services specification.

FR-CIO-08  
If GPS is unavailable or declined, the system shall allow manual check-in/check-out and flag it accordingly.

Error Handling

FR-CIO-09  
If the check-in or check-out operation fails:  
	•	Display an error message;  
	•	Allow the user to retry the action.

FR-CIO-10  
If the required data (e.g., timestamp) cannot be recorded, the action shall not complete.

**Data Requirements**

Each check-in/check-out event shall store:  
	•	Order ID  
	•	User ID  
	•	Action type (Check-In / Check-Out)  
	•	Timestamp  
	•	GPS coordinates (if enabled)  
	•	Method:  
		•	GPS-verified  
		•	Manual

#### **3.1.3.4 In progress state** {#3.1.3.4-in-progress-state}

The Order Details In-Progress state represents an order that has been successfully checked in and is actively being worked on.  
It enables Field Technicians to:  
	•	Track elapsed job time;  
	•	Complete required deliverables (survey, photo report, notes);  
	•	Review job details while on site;  
	•	Submit deliverables when work is complete;  
	•	Check out and finish the job.

This screen serves as the primary execution workspace during an active job.

**UI Description**

Header  
	•	Back navigation control  
	•	Order title (e.g., Tower Maintenance \#A-7)  
	•	Order status badge: In progress  
	•	Elapsed time counter (HH:MM:SS), running while the order is active

Deliverables Section

A grouped list of required deliverables:  
	•	Survey  
	•	Photo report  
	•	Notes

Each item:  
	•	Is tappable  
	•	Navigates to its respective data entry screen  
	•	Displays completion state (implicit or explicit)

Order Information Section

	•	Order description/scope of work  
	•	PF info   
	•	Full address location with “On map” link (opens external Maps application with   
pre-loaded location data)  
	•	Date and scheduled start time

Primary Action Area

Depending on the order state and connectivity:

Online & deliverables ready  
	•	Primary button: Submit deliverables

Offline  
	•	Disabled Submit Deliverables button  
	•	Informational message:  
“Offline. Data will sync when the connection is restored.”

Deliverables submitted  
	•	Primary button changes to: Check out

**Functional Requirements**

In-Progress State Behavior

FR-IP-01  
The system shall display the In-Progress Order State immediately after a successful check-in.

FR-IP-02  
The elapsed time counter shall start at check-in and update in real time.

Deliverables Access

FR-IP-03  
The user shall be able to access Survey, Photo Report, and Notes at any time while the order is in progress.

FR-IP-04  
Progress on deliverables shall be saved automatically locally on a device.

Submission Logic

FR-IP-05  
The Submit Deliverables button shall be enabled only when:  
	•	All required deliverables are completed (Survey);  
	•	The device is online.  
FR-IP-06  
If the device is offline, the system shall:  
	•	Disable submission;  
	•	Display a clear offline message;  
	•	Inform users once connectivity is restored, that order wasn’t submitted, so he can   
resubmit it  
•	Automatically submit data once connectivity is restored if the submission progress   
was interrupted.

Check-Out Transition

FR-IP-07  
After deliverables are successfully submitted, the primary action shall change to Check out.

FR-IP-08  
Selecting Check out shall initiate the Check-Out Confirmation flow.

Offline Behavior

FR-IP-09  
All deliverables created while offline shall be stored locally.

FR-IP-10  
Locally stored data shall automatically sync when network connectivity is restored (while submitting an order).

Error Handling

FR-IP-11  
If deliverable submission fails:  
	•	Display an error message;  
	•	Allow retry.

FR-IP-12  
If data cannot be synced due to connectivity issues:  
	•	Preserve data locally;  
	•	Retry automatically when possible.

##### **3.1.3.4.1 Submit deliverables pop-up flow** {#3.1.3.4.1-submit-deliverables-pop-up-flow}

The Submit Deliverables confirmation pop-up provides a final validation step before sending job deliverables to the Project Facilitator for review.  
It is designed to:  
	•	Prevent accidental submission of incomplete or incorrect data;  
	•	Clearly communicate that submission is final and irreversible;  
	•	Confirm successful transmission of deliverables: Survey (required) and Photos   
(optional) ;  
	•	Provide immediate user feedback upon completion.

This pop-up represents a critical transition point from execution to review.

**UI Description**

Confirmation Pop-up  
	•	Modal dialog displayed above the current screen  
	•	Semi-transparent background overlay  
	•	Visual confirmation icon (checkmark)  
	•	Title: Submit deliverables  
	•	Warning message:  
“You won’t be able to edit it after submission.”

Actions:  
	•	Cancel – closes the pop-up without submitting  
	•	Submit – confirms and proceeds with submission

Success Notification  
	•	Toast or banner message displayed after successful submission:  
“Deliverables sent to review successfully”

**Functional Requirements**

Submission Confirmation

FR-SUB-01  
The system shall display the Submit Deliverables confirmation pop-up when the user initiates a deliverables submission.

FR-SUB-02  
Selecting Cancel shall:  
	•	Close the pop-up;  
	•	Return the user to the In-Progress Order screen;  
	•	Leave all deliverables editable.

FR-SUB-03  
Selecting Submit shall:  
	•	Validate that all required deliverables are complete;  
	•	Lock deliverables from further editing;  
	•	Initiate deliverables upload to the backend system, which subsequently distribute   
deliverable to COPS system and Admin Panel.

Submission Execution

FR-SUB-04  
Upon successful submission, the system shall:  
	•	Receive and Display a success notification (after COPS system has successfully   
retrieved data)  
	•	Enable the Check out action.

FR-SUB-05  
Submitted deliverables shall be marked as read-only.

Offline Behavior

FR-SUB-06  
If the device is offline, the system shall:

	•	Prevent submission;  
	•	Display an appropriate offline message;  
	•	Automatically submit deliverables when connectivity is restored

Each submission event shall record:

	•	Order ID  
	•	FT ID  
	•	Submission timestamp  
	•	Location data (Check-in/Check-out)  
	•	Deliverables metadata (Survey response, Photo report, Notes)  
	•	Submission status (Success / Failed).

Error Handling

FR-SUB-07  
If submission fails:  
	•	Display an error message;  
	•	Allow the user to retry submission.  
•	If the survey is incomplete, display an error snackbar:   
“Complete the survey before job submission.”

FR-SUB-08  
Partial submissions shall not be allowed; submission is required.

##### **3.1.3.4.2 Survey screen** {#3.1.3.4.2-survey-screen}

The Survey Screen enables Field Technicians to capture structured job outcome data as part of order deliverables.  
It is designed to:  
	•	Collect standardized information required by Project Facilitators;  
	•	Ensure consistency and completeness of job reporting;  
	•	Support evidence attachment (photos);  
	•	Work reliably in both online and offline conditions.

The survey is a mandatory deliverable prior to submitting job results.

**UI Description**

Header  
	•	Back navigation control  
	•	Screen title (e.g., Fiber installation report)  
	•	Auto-save indicator (implicit)

Survey Structure

The survey is presented as a scrollable form composed of clearly numbered sections.

Typical Question Types:  
	1\.	Yes / No selection  
	2\.	Dropdown (single-select)  
	3\.	Date picker  
	4\.	Time picker  
	5\.	Checkbox list (multi-select)  
	6\.	Radio buttons (single-select)  
	7\.	Photo upload  
	8\.	Free-text input

Evidence & Notes Section  
	•	Photo thumbnail previews  
	•	Upload photo button  
	•	Ability to add multiple photos  
	•	Text area for comments, blockers, or additional work notes  
Primary Action  
	•	Save button at the bottom of the screen  
	•	Button state:  
		•	Disabled when required fields are incomplete  
		•	Enabled when validation passes

**Functional Requirements**

Survey Data Entry

FR-SUR-01  
The system shall display a predefined survey template associated with the order.

FR-SUR-02  
Survey questions shall support multiple input types:  
	•	Boolean (Yes/No)  
	•	Single-select  
	•	Multi-select  
	•	Date and time  
	•	Free-text (Max characters limit: 500\)  
	•	Photo attachments

Validation Rules

FR-SUR-03  
Required questions shall be clearly indicated.

FR-SUR-04  
The Save button shall be disabled until all required fields are completed.

FR-SUR-05  
Validation errors shall be displayed inline with the affected question.

Data Persistence

FR-SUR-06  
Survey responses shall be automatically saved locally as the user enters data.

FR-SUR-07  
Saved survey data shall persist across app restarts.

Photo Evidence Handling

FR-SUR-08  
The user shall be able to attach one or more photos as evidence.

FR-SUR-09  
Photo thumbnails shall be displayed within the survey.

FR-SUR-10  
Photos shall be compressed before upload while maintaining acceptable quality.

Save Behavior

FR-SUR-11  
Selecting Save shall:  
	•	Persist survey data locally;  
	•	Mark the survey as completed;  
	•	Return the user to the In-Progress Order screen.  
FR-SUR-11-1

Survey data must be automatically saved when the user navigates away or moves back, regardless of whether a manual "Save" action is performed.

Offline Behavior

FR-SUR-12  
The survey shall be fully functional offline.

FR-SUR-13  
Survey data and attached photos shall sync automatically when connectivity is restored.

Data Requirements

Each survey submission shall include:  
	•	Order ID  
	•	Survey template ID  
	•	Question IDs and responses  
	•	Attached photo references  
	•	Last modified timestamp  
	•	Completion status  
Error Handling

FR-SUR-14  
If survey data fails to save:  
	•	Display an error message;  
	•	Preserve entered data;  
	•	Allow retry.

FR-SUR-15  
If photo upload fails:  
	•	Notify the user;  
	•	Retain the photo locally for later sync.

##### **3.1.3.4.3 Photo report screen** {#3.1.3.4.3-photo-report-screen}

The Photo Report feature enables Field Technicians to capture, describe, organize, and manage photographic evidence related to an order.  
It is designed to:  
	•	Provide visual proof of work performed;  
	•	Allow contextual clarification through descriptions and tags;  
	•	Support photo editing and deletion before submission;  
	•	Function reliably in offline conditions.

The Photo Report is a mandatory or optional deliverable, depending on order configuration.

UI Description

3.1 Photo Report – Empty State  
	•	Header with back navigation and title: Photo report  
	•	Placeholder illustration  
	•	Informational text:  
“No photos have been added yet. Add photos to the report to get started.”  
	•	Primary action button:  
	•	Add photo

Photo Report – Populated State  
	•	Grid layout of photo thumbnails  
	•	Each photo displays:  
	•	Thumbnail preview  
	•	Short description snippet (if provided)  
	•	Floating or bottom Add photo button  
	•	Tap on photo opens photo actions

**Functional Requirements**

Photo Management

FR-PH-01  
The system shall allow users to add one or more photos to the Photo Report.

Editing & Deletion

FR-PH-02  
Users shall be able to edit photo metadata at any time before submission.

FR-PH-03  
Users shall be able to delete photos before submission.

FR-PH-04  
Deleting a photo shall require explicit confirmation.

Offline Behavior

FR-PH-05  
Photos shall be stored locally and automatically uploaded when connectivity is restored.

Error Handling

FR-PH-06  
If upload fails:  
	•	Retain photo locally;  
	•	Retry automatically when possible.

##### **3.1.3.4.4 Add photo flow** {#3.1.3.4.4-add-photo-flow}

The Add / Edit Photo screen allows Field Technicians to prepare photographic evidence before it becomes part of the Photo Report.  
It enables users to:  
	•	Crop and visually adjust photos;  
	•	Add visual markup/annotations for clarification;  
	•	Describe the photo with contextual text;  
	•	Tag photos for structured review;  
	•	Save changes locally before submission.

This screen ensures high-quality, well-explained visual deliverables.

**UI Description**

Header  
	•	Back navigation control  
	•	Contextual title:  
	•	Add photo (new photo)  
	•	Edit photo (existing photo)  
	•	Action icons:  
		•	Undo  
		•	Redo  
		•	Confirm  
Photo Preview Area  
	•	Full-width photo preview  
	•	Interactive canvas supporting:  
		•	Cropping  
		•	Markup (draw / annotate)  
	•	Safe margins to avoid accidental touches  
Photo Editing Tools

Crop Tool  
	•	Adjustable crop frame  
	•	Grid overlay for alignment  
	•	Apply / confirm crop action

Markup Tool  
	•	Freehand drawing on photo  
	•	Color palette selection  
	•	Adjustable stroke size  
	•	Undo / redo support  
Metadata Section

Photo Description  
	•	Multi-line text input  
	•	Character limit (e.g., 500 characters)  
	•	Optional field  
	•	Character counter displayed

Photo Tags  
	•	Multi-select chips  
	•	Example tags:  
		•	Before  
		•	After  
		•	Installation  
		•	Issue  
		•	Damage  
	•	Tags are sourced from an Admin Panel  
Primary Action  
	•	Save button  
	•	Button enabled only when:  
		•	Photo is present  
		•	Mandatory fields are valid

**Functional Requirements**

Photo Editing

FR-PH-M-01  
The system shall allow users to crop photos before saving.

FR-PH-M-02  
The system shall allow users to add visual markup to photos.

FR-PH-M-03  
Undo and redo actions shall be supported for photo edits.

Metadata Entry

FR-PH-M-04  
Users shall be able to add or edit a photo description.

FR-PH-M-05  
Users shall be able to assign one or more tags to a photo.

FR-PH-M-06  
Description length shall be limited and validated.

Save Behavior

FR-PH-M-07  
Selecting Save shall:  
	•	Persist photo edits and metadata locally;  
	•	Return the user to the Photo Report screen.

FR-PH-M-08  
Unsaved changes shall be discarded if the user navigates back without saving (with optional warning).

Edit vs Add Logic

FR-PH-M-09  
When editing an existing photo, previously saved data shall be preloaded.

FR-PH-M-10  
When adding a new photo, fields shall be empty by default.

Offline Behavior

FR-PH-M-11  
All photo editing and metadata entry shall be fully functional offline.

FR-PH-M-12  
Edited photos shall sync automatically when connectivity is restored.

Error Handling

FR-PH-M-13  
If photo editing fails:  
	•	Display an error message;  
	•	Preserve original photo.

FR-PH-M-14  
If save fails:  
	•	Notify the user;  
	•	Retain edits locally for retry.

##### **3.1.3.4.4 Delete photo pop-up** {#3.1.3.4.4-delete-photo-pop-up}

The Delete Photo confirmation pop-up provides a safety checkpoint before permanently removing a photo from the Photo Report.  
It is designed to:  
	•	Prevent accidental deletion of evidence;  
	•	Clearly communicate the irreversible nature of the action;  
	•	Ensure users explicitly confirm destructive operations;  
	•	Maintain data integrity and auditability during job execution.  
**UI Description**

Confirmation Pop-up  
	•	Modal dialog displayed above the current screen  
	•	Semi-transparent background overlay  
	•	Icon indicating destructive action (trash/delete icon)  
	•	Title: Delete photo  
	•	Warning message:  
“Are you sure you want delete this photo.  
All descriptions will be lost?”

Actions:  
	•	Cancel – dismisses the pop-up without deleting the photo  
	•	Delete – confirms deletion and removes the photo

Functional Requirements

Deletion Confirmation

FR-DEL-PH-01  
The system shall display the Delete Photo confirmation pop-up when the user initiates a delete action on a photo.

FR-DEL-PH-02  
Selecting Cancel shall:  
	•	Close the pop-up;  
	•	Preserve the photo and all associated metadata;  
	•	Return the user to the previous screen.

FR-DEL-PH-03  
Selecting Delete shall:  
	•	Permanently remove the photo from the Photo Report;  
	•	Remove all associated metadata (description, tags, markup);  
	•	Update the Photo Report view immediately.

State & Validation

FR-DEL-PH-04  
Deleted photos shall no longer be available for editing or submission.

FR-DEL-PH-05  
If the photo was marked as required evidence, deletion shall update the deliverables completion state accordingly.

Offline Behavior

FR-DEL-PH-06  
Photo deletion shall be supported while offline.

FR-DEL-PH-07  
If the photo has not yet been synced, deletion shall remove it from local storage.

FR-DEL-PH-08  
If the photo has already been synced, deletion shall be queued and synced when connectivity is restored.

Error Handling

FR-DEL-PH-09  
If photo deletion fails:  
	•	Display an error message;  
	•	Retain the photo;  
	•	Allow retry.

FR-DEL-PH-10  
Partial deletion (photo without metadata or vice versa) shall not be allowed.

##### **3.1.3.4.5 Notes screen** {#3.1.3.4.5-notes-screen}

The Notes screen allows Field Technicians to create, view, edit, and delete free-form notes associated with an order.  
It is intended to:  
	•	Capture contextual information that does not fit structured surveys;  
	•	Record observations, blockers, or additional work details;  
	•	Support iterative note-taking during job execution;  
	•	Maintain a chronological log of technician inputs.

Notes are considered a supporting deliverable and may be optional or required depending on order configuration.

**UI Description**

Empty State

When no notes exist for the order:  
	•	Header with back navigation and title: Notes  
	•	Placeholder illustration  
	•	Informational text:  
“No notes have been added yet.  
Add note to the report to get started”  
	•	Primary action button:  
		•	Add note  
Notes List (Populated State)  
	•	Scrollable vertical list of notes  
	•	Each note item displays:  
	•	Creation/Update date and time (e.g., 01 Aug 2026 11:52)  
	•	Note preview text (single or multi-line, truncated if long)  
	•	Context menu (⋮) for actions:   
		•	Edit  
		•	Delete  
	•	Floating or bottom-aligned Add note button  
Note Actions

From the context menu:  
	•	Edit note  
	•	Delete note  
System Feedback  
	•	Toast or banner notifications:  
		•	“Note added successfully”  
		•	“Note saved successfully”  
	•	“Note deleted successfully”

**Functional Requirements**

Notes Listing

FR-NOT-01  
The system shall display all notes associated with the selected order.

FR-NOT-02  
Notes shall be ordered chronologically by creation time (newest first by default).

Add Note

FR-NOT-03  
Selecting Add note shall navigate the user to the Add/Edit Note screen.

FR-NOT-04  
A new note shall be associated with the current order and user.

Edit Note

FR-NOT-05  
Users shall be able to edit existing notes until deliverables are submitted.

FR-NOT-06  
Edited notes shall retain last-modified timestamp.

Delete Note

FR-NOT-07  
Deleting a note shall require confirmation via a modal dialog.

FR-NOT-08  
Confirmed deletion shall permanently remove the note from the order.

Offline Behavior

FR-NOT-09  
Notes creation, editing, and deletion shall be fully supported offline.

FR-NOT-10  
Offline note changes shall sync automatically when connectivity is restored.

Error Handling

FR-NOT-11  
If a note fails to save:  
	•	Display an error message;  
	•	Preserve note content;  
	•	Allow retry.

FR-NOT-12  
If deletion fails:  
	•	Notify the user;  
	•	Retain the note;  
	•	Allow retry.

##### **3.1.3.4.6 Add note screen** {#3.1.3.4.6-add-note-screen}

The Add / Edit Note screen allows Field Technicians to create and maintain free-form textual notes related to an order.  
It is designed to:  
	•	Capture observations, clarifications, and additional work details;  
	•	Support quick note entry during active jobs;  
	•	Allow editing or deletion of notes prior to deliverable submission;  
	•	Work reliably in both online and offline conditions.

This screen supports both note creation and modification workflows.

**UI Description**

Header  
	•	Back navigation control  
	•	Screen title:  
	•	Add note (new note)  
	•	Edit note (existing note)  
	•	Optional action:  
		•	Delete note button (Edit mode only)

Note Input Area  
	•	Multi-line text input field  
	•	Placeholder text: Add note  
	•	Character counter displayed (e.g., 320 / 500\)  
	•	Maximum character limit enforced (e.g., 500 characters)

Primary Action  
	•	Save button at the bottom of the screen  
	•	Button state:  
		•	Disabled when note content is empty  
		•	Enabled when valid text is entered

**Functional Requirements**

Note Creation

FR-NOT-ADD-01  
The system shall allow users to create a new note associated with the current order.

FR-NOT-ADD-02  
A note shall not be saved if the text field is empty.

Note Editing

FR-NOT-ADD-03  
When editing an existing note, the system shall preload the previously saved note content.

FR-NOT-ADD-04  
Users shall be able to update note content until deliverables are submitted.

Save Behavior

FR-NOT-ADD-05  
Selecting Save shall:  
	•	Persist the note content locally;  
	•	Update the notes list;  
	•	Return the user to the Notes List screen.

FR-NOT-ADD-06  
The system shall display a success message after saving:  
	•	“Note added successfully” (new note)  
	•	“Note saved successfully” (edited note)

Delete Access (Edit Mode)

FR-NOT-ADD-07  
When editing a note, selecting Delete note shall trigger the Delete Note confirmation flow.

Offline Behavior

FR-NOT-ADD-08  
Notes shall be creatable and editable while offline.

FR-NOT-ADD-09  
Offline note changes shall sync automatically when connectivity is restored.

Error Handling

FR-NOT-ADD-10  
If saving a note fails:  
	•	Display an error message;  
	•	Preserve entered text;  
	•	Allow retry.

FR-NOT-ADD-11  
If character limit is exceeded:  
	•	Prevent further input;  
	•	Notify the user visually.

##### **3.1.3.4.7 Delete note pop-up** {#3.1.3.4.7-delete-note-pop-up}

The Delete Note confirmation pop-up provides a final safeguard before permanently removing a note from an order.  
It is designed to:  
	•	Prevent accidental deletion of important contextual information;  
	•	Clearly communicate that the action is irreversible;  
	•	Require explicit user confirmation for destructive actions;  
	•	Maintain data integrity during job execution.  
**UI Description**

Confirmation Pop-up  
	•	Modal dialog displayed above the current screen  
	•	Semi-transparent background overlay  
	•	Destructive-action icon (trash/delete)  
	•	Title: Delete note  
	•	Warning message:  
“Are you sure you want delete this note.  
All descriptions will be lost?”

Actions:  
	•	Cancel – dismisses the pop-up without deleting the note  
	•	Delete – confirms deletion and removes the note  
**Functional Requirements**

Deletion Confirmation

FR-DEL-NOT-01  
The system shall display the Delete Note confirmation pop-up when the user initiates a delete action on a note.

FR-DEL-NOT-02  
Selecting Cancel shall:  
	•	Close the pop-up;  
	•	Preserve the note and all associated content;  
	•	Return the user to the Notes List screen.

FR-DEL-NOT-03  
Selecting Delete shall:  
	•	Permanently remove the note from the order;  
	•	Remove all associated text content;  
	•	Update the Notes List immediately.

State & Validation

FR-DEL-NOT-04  
Deleted notes shall no longer be accessible for viewing or editing.

FR-DEL-NOT-05  
If notes are required to complete deliverables, deletion shall update the deliverables completion state accordingly.

Offline Behavior

FR-DEL-NOT-06  
Note deletion shall be supported while the device is offline.

FR-DEL-NOT-07  
If the note has not yet been synced, deletion shall remove it from local storage only.

FR-DEL-NOT-08  
If the note has already been synced, deletion shall be queued and synced when connectivity is restored.

Error Handling

FR-DEL-NOT-09  
If note deletion fails:  
	•	Display an error message;  
	•	Retain the note;  
	•	Allow retry.

FR-DEL-NOT-10  
Partial deletion (e.g., metadata without content) shall not be allowed.

### **3.1.4 Notifications screen** {#3.1.4-notifications-screen}

The Notifications Screen provides Field Technicians with a centralized list of job-related updates and alerts generated by the system or Project Facilitators. This screen displays all notifications within last week.

This screen is designed to:  
	•	Display recent activity related to assigned jobs  
	•	Keep users informed about schedule changes, new jobs, and updates  
	•	Encourage enabling push notifications  
**UI Description**

Layout  
	•	Top title: Notification list  
	•	Optional system banner for push notification settings  
	•	Scrollable list of notifications  
	•	Bottom navigation bar with Notifications tab selected  
Push Notification Banner

Displayed when push notifications are disabled.

Text:

Turn on push notifications  
Turn on push notifications to get alerts for job updates.

Action:  
	•	Go to Settings → Opens device notification settings

Notification List

Each notification item includes:

| Element | Description |
| ----- | ----- |
| Icon | Visual indicator of notification type |
| Title | Short summary (e.g., New job assigned) |
| Description | Details about the job update |
| Chevron | Indicates tap to open job details |

Notification Types

| Type | Example Text |
| ----- | ----- |
| New job assigned | “Tower Maintenance \#A-7 was assigned to you.” |
| Job starts today | “Tower Maintenance \#A-7 starts today at 14:00.” (sends daily at job day at 8 AM) |
| Job updated | “Tower Maintenance \#A-7 was updated by Project Facilitator.” |
| Job cancelled | “Tower Maintenance \#A-7 was removed from your list.” |

Empty State

If no notifications exist, display Text:

No notifications yet  
You’ll see updates about your jobs here.

**Functional Requirements**

Notification Display

FR-NOT-01  
The system shall display a chronological list of notifications (most recent first).

FR-NOT-02  
Each notification shall contain a type, title, description, and related job reference.

Navigation

FR-NOT-03  
Tapping a notification shall open the related Job Details screen If Job has been completed, rejected or cancelled user cannot be navigated in a Job Details.

Push Notification Banner

FR-NOT-04  
If push notifications are disabled, a banner shall be shown prompting the user to enable them.

FR-NOT-05  
Tapping Go to Settings shall open the device’s notification settings for the app.

State Management

FR-NOT-06  
Notifications shall be marked as read when opened.

FR-NOT-07  
Unread notifications shall be visually distinguishable (e.g., badge or highlight).

Navigation & Flow Logic

| Condition | Result |
| ----- | ----- |
| Screen opened | Notifications loaded |
| No notifications | Empty state shown |
| Push disabled | Settings banner shown |
| Notification tapped | Navigate to Job Details |

Error Handling

FR-NOT-08  
If notifications fail to load, display a retry option.

FR-NOT-09  
If related job is no longer available, display message:

This job is no longer available.

### **3.1.5 Profile screen** {#3.1.5-profile-screen}

The Profile Screen allows a Field Technician to view and manage their personal account information and access app-related settings.

This screen is designed to:  
	•	Display user identity details  
	•	Provide access to profile editing  
	•	Offer appearance and legal options  
	•	Allow the user to log out  
	•	Allow the user to delete account 

**UI Description**

Layout  
	•	Top section with user information card  
	•	Settings options list  
	•	App version and logout option at bottom  
	•	Bottom navigation bar with Profile tab selected

User Information Card

Displays:  
	•	Full name  
	•	Phone number  
	•	Email address

Action:  
	•	Edit button → opens Edit Profile screen

Settings Section

| Setting | Type | Description |
| ----- | ----- | ----- |
| Dark mode | Toggle switch | Enables/disables dark theme |
| Privacy Policy | Link | Privacy Policy link: [https://www.concerttech.com/mobile-privacy/](https://www.concerttech.com/mobile-privacy/) |

Footer

| Element | Description |
| ----- | ----- |
| App version | Display only |
| Log out | Opens logout confirmation dialog |

**Functional Requirements**

Profile Display

FR-PROF-01  
The system shall display the user’s first name, last name, phone number, and email.

Edit Profile Navigation

FR-PROF-02  
Tapping Edit shall navigate to the Edit Profile screen.

Dark Mode

FR-PROF-03  
Toggling Dark Mode shall change the app theme immediately.

FR-PROF-04  
Dark Mode preference shall persist across sessions.

Privacy Policy

FR-PROF-05  
Tapping Privacy Policy shall open the policy document in a web view or external browser.

Log Out

FR-PROF-06  
Tapping Log out shall open a confirmation dialog.

FR-PROF-07  
Confirming logout shall:  
	•	Clear user session  
	•	Return the user to the Welcome screen

FR-PROF-08  
Canceling logout shall close the dialog without action.

**Edit Profile state**

Purpose:

Allows the user to update personal account information.

Fields

| Field | Editable | Notes |
| ----- | ----- | ----- |
| First name | Yes | Required |
| Last name | Yes | Required |
| Phone number | No | Display only |
| Email | Yes | Optional |

Actions

| Button | Function |
| ----- | ----- |
| Save | Validates and saves changes |
| Back | Returns to Profile without saving |

**Functional Requirements**

FR-PROF-09  
First and last name are required fields.

FR-PROF-10  
Email must be valid format if entered.

FR-PROF-11  
Phone number is not editable.

FR-PROF-12  
Saving shall update profile information in backend and local state.

**Logout Confirmation Dialog**

Text:  
Are you sure you want to log out?

| Button | Behavior |
| ----- | ----- |
| Cancel | Close dialog |
| Log out | Complete logout process |

Navigation & Flow Logic

| User Action | Result |
| ----- | ----- |
| Tap Edit | Open Edit Profile |
| Save changes | Update profile and return |
| Toggle Dark Mode | Theme changes |
| Tap Privacy Policy | Open document |
| Tap Log out | Show confirmation dialog |
| Confirm logout | Return to Welcome |

Error Handling

FR-PROF-13  
If profile update fails, display an error message and allow retry.

FR-PROF-14  
If logout fails due to network issues, still clear local session.

Account deletion  
FR-PROF-15  
User shall be able to delete his account using confirmational pop-up (requires typing “Delete” prompt)

## **3.2 Software Interfaces**  {#3.2-software-interfaces}

The CLIENT application (Concet technologies mobile application) will be connected with a server by using REST API. The application’s data relies on the system database,PostgreSQL. 

The expected API Response model for the CT Mobile Application is described in the [CT Mobile API documentation](https://documenter.getpostman.com/view/12140442/2sBXVhCqQB#1f5dcd6b-564d-4aea-8072-0bf0e696b469) (a Postman-based documentation).

## **3.3 Communication Interfaces**  {#3.3-communication-interfaces}

The communication between the application and the server will be provided over the HTTPS protocol. 

### **3.3.1 Offline Functionality** {#3.3.1-offline-functionality}

**Description:** Ensure usability in low/no connectivity environments.

**Requirements:**

* Cache job data locally (Jobs should be stored locally at the moment they are retrieved)  
* Save in-progress surveys and photos  
* Automatic sync when connectivity is restored  
* Conflict handling and retry logic

If the communication between CLIENT and SERVER fails, the CLIENT will wait until a connection is restored and display a “No Internet connection” message.

### **3.3.2 Notifications and Alerts** {#3.3.2-notifications-and-alerts}

**Description:** Two-way communication triggers.

**Requirements:**

* Push notifications for:

  * Job starts today (Triggered in the morning at 8 AM of local FT’s time)  
  * Job cancelled  
  * Job updates   
    Note: Changes which are triggered by a Field Technician (Check-in/Check/out, Survey updated, Note/Photos added/removed, etc)  should not be included in notification logic)  
* Email notifications (for PF)  
  * FT check-in  
  * FT check-out  
  * Deliverables submitted

Contact email: [support@concerttech.com](mailto:support@concerttech.com)

## **3.4 Change requests**

### **3.4.1 CR-1: SMS Consent & Notification Workflow**

This section defines the requirements for implementing and enhancing the SMS-based communication workflow for technicians within the Concert Technologies platform, including consent management, job notifications, and OTP delivery logic.

The change introduces:

* SMS consent capture and tracking

* Conditional SMS notifications for job assignments

* Mobile app registration with consent management

* OTP delivery logic based on consent

* Error handling and system feedback to Project Facilitators (PF)

#### **High-Level Workflow**

1. Contractor onboarded (COPS side)

2. Technician added under contractor (COPS side)

3. Consent request sent via SMS (COPS side)

4. Technician responds (YES/NO) (COPS side)

5. Consent stored as system flag (COPS side)

6. Job assignment triggers conditional SMS (Field Services system side)

7. Technician may register via mobile app (Field Services system side)

8. Consent can be updated in app (Field Services system side)

9. OTP delivery depends on consent status (Field Services system side)

#### **Functional Requirements**

Technician Creation & Consent Request

FR-001

When a technician is created with a mobile number, the system shall send an SMS consent request which is sent from COPS system

FR-002

The SMS content shall be:

“Concert Technologies would like to send you job assignments, scheduling updates, and safety notifications by text. Messages may be recurring. Msg & data rates may apply. Reply YES to opt in or NO to decline. Reply STOP at any time to opt out.”

Consent Capture & Management

FR-003

The COPS system shall process incoming SMS replies:

	•	YES → set SMS\_Consent\_Flag \= TRUE

	•	NO → set SMS\_Consent\_Flag \= FALSE

	•	STOP → set SMS\_Consent\_Flag \= FALSE

FR-004

Consent status shall be stored per technician in COPS database.

Job Assignment Notification flow

FR-005

When a PF assigns a job, the system shall check SMS\_Consent\_Flag.

FR-006

If TRUE:

	•	System sends SMS with secure job access link, SMS body:

	“You have been assigned one or more new Jobs. Please click the link to check in via 

 the Field Services application.”

	•	PF receives confirmation: “SMS link sent to technician”

FR-007

If FALSE:

	•	No SMS is sent

	•	PF sees notification (delivered by email):

“Technician has not consented to SMS. Instruct tech to register for mobile app account, where they can update their consent if preferred.”

•	Email/SMS from PF to FT is sent, Email/SMS body:

“You have been assigned one or more new Jobs. Please click the link to check in via 

 the Field Services application.”

Mobile App Registration

FR-008

Technicians shall be able to register via Email or SMS (select manually OTP/Job link delivery method (SMS/Email).

FR-009

During registration, the system shall prompt for SMS consent (YES/NO). The application must present the user with an additional set of SMS terms of use. The user will be required to either **Accept** or **Decline** these terms.

FR-010

Consent updates shall override previous values:

	•	YES → set flag to TRUE

	•	NO → set flag to FALSE

OTP Delivery Logic

FR-011

System shall send OTP during registration.

FR-012

OTP delivery rules:

	•	If SMS\_Consent\_Flag \= TRUE → OTP via SMS

	•	If SMS\_Consent\_Flag \= FALSE → OTP via Email

#### **Non-Functional Requirements**

Security

	•	OTP must expire within configurable time (default: 5 minutes)

	•	SMS links must be time-bound (default: 72 hours)

	•	All consent actions must be logged

Reliability

	•	SMS delivery retries (configurable, e.g., 3 attempts)

	•	Graceful handling of SMS gateway failures

Compliance

	•	Must comply with SMS communication regulations (e.g., opt-in/opt-out tracking)

	•	STOP keyword must immediately revoke consent (configured on Twilio service)

#### **Error Handling**

SMS Link Usage

| Scenario | Expected Behavior |
| ----- | ----- |
| Link used second time | Allow access if within validity OR show “Link already used” (configurable) |
| Link expired (\>72h) | Show error: “Link expired. Request a new link.”  |

 Consent Edge Cases

| Scenario | Behavior |
| ----- | ----- |
| Invalid SMS reply | Ignore |
| No response | Default \= NO consent |
| Consent changed in app | Immediately reflected in system |

OTP Failures

| Scenario | Behavior |
| ----- | ----- |
| SMS OTP fails | Retry → fallback to email |
| Email OTP fails | Retry with alert |

#### **Notifications**

To Technician

* Consent request SMS (COPS side)

* Job assignment SMS/Email (Field Services system side)

* OTP (SMS or Email)

To PF

* Confirmation Job assignment SMS/Email sent (Field Services system side)

* Warning if no consent given (COPS/Field Services system sides)

### **3.4.2 CR-2: 01/07/2026	Repeatable Survey Sections** 

Feature requirements described in separate PRD document: 		

[Repeatable Survey Sections / Looping Functionality](https://docs.google.com/document/d/1nAp7MgzLPzyc502O7hcRx7_Gc4gHFFGJQzbntyaSSaU/edit?tab=t.0) 

# **4\. System Features**  {#4.-system-features}

All of the system features’ technical requirements are described in the following paragraph.   
Please check the appropriate screen section in paragraph 3 to see feature UI details and business logic requirements.

During the development, additional feature descriptions may be added to this document, and therefore to this paragraph.

# **5\. Other Requirements**  {#5.-other-requirements}

### **5.1 Performance** {#5.1-performance}

* App should load job list within 3 seconds under normal network conditions  
* Photo upload should be optimized for bandwidth

### **5.2 Security** {#5.2-security}

* Encrypted data at rest and in transit  
* Secure authentication mechanisms

### **5.3 Usability** {#5.3-usability}

* Intuitive, mobile-first UI  
* Minimal steps for job completion  
* Accessibility best practices

### **5.4 Reliability** {#5.4-reliability}

* Data persistence during app crashes or network loss  
* Graceful error handling

### **5.5 Scalability** {#5.5-scalability}

* Support growth in the number of users and jobs

### **5.6. Product backlog** {#5.6.-product-backlog}

The product backlog, which is a prioritized list of development work, is derived from the project's roadmap and its associated requirements. To guide the development team on what to deliver first, the most critical items are placed at the top of the backlog.

This product backlog is integrated into the project's roadmap and timelines document.

