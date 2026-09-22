Software Requirements  Specification 
for 
Acme Field Services Field services mobile application
Software Requirements Specification for Authentification module project

Table of Contents
Table of Contents	2
Revision History	3
1. Introduction	4
1.1 Purpose	4
1.2 Intended Audience and Reading Suggestions	4
1.3 Definitions, Acronyms, and Abbreviations	4
1.4 Product Scope	5
1.5 References	5
2. Overall Description	5
2.1 Product Perspective	5
2.2 Product Functions (High-Level)	6
2.3 User Classes and Characteristics	6
2.3.1 Field Technician (FT)	6
2.3.2 Project Facilitator (PF)	6
2.4 Operating Environment	6
2.5 Design and Implementation Constraints	7
2.6 Assumptions, Dependencies and Risks	7
3. External Interface Requirements	8
3.1 User Interfaces	8
3.1.0 Splash screen	8
3.1.1 Authentication	9
3.1.1.1 Welcome screen	9
3.1.1.2 Registration screen	11
3.1.1.1 Phone number verification screen	13
3.1.1.1 Login screen	16
3.1.2 Order list screen	19
3.1.2.1 List view	20
3.1.2.2 Calendar (Weekly) view	21
3.1.3 Order details screen	23
3.1.3.1 Details main screen	23
3.1.3.1.1 Location services pop-ups and logic	25
3.1.3.2 Attachments screen	27
3.1.3.2.1 Documents tab	28
3.1.3.2.2 Photos tab	29
3.1.3.3 Check in/Check out screens	29
3.1.3.4 In progress state	31
3.1.3.4.1 Submit deliverables pop-up	34
3.1.3.4.2 Survey screen	36
3.1.3.4.3 Photo report screen	39
3.1.3.4.4 Add photo flow	40
3.1.3.4.4 Delete photo pop-up	43
3.1.3.4.5 Notes screen	44
3.1.3.4.6 Add note screen	47
3.1.3.4.7 Delete note pop-up	49
3.1.4 Notifications screen	50
3.1.5 Profile screen	53
3.2 Software Interfaces	57
3.3 Communication Interfaces	57
3.3.1 Offline Functionality	57
3.3.2 Notifications and Alerts	57
4. System Features	58
5. Other Requirements	58
5.1 Performance	58
5.2 Security	58
5.3 Usability	58
5.4 Reliability	58
5.5 Scalability	58
5.6. Product backlog	58



Revision History 

Name
Date
Reason For Changes 
Version
SRS 
06.01.2026
-
0.9
SRS 
24.01.2026
Base version (Ready for dev team review)
0.9.1
SRS 
28.01.2026
Base version (Validated by dev team)
0.9.2
SRS 
02.02.2026
Base version 
1.0.0
SRS
15.04.2026
Added 3.4.1 SMS Consent & Notification Workflow
1.0.1
SRS
15.05.2026
Added Privacy Policy and
Terms and Conditions links to appropriate sections
1.0.2

1. Introduction 
1.1 Purpose  
This Software Requirements Specification (SRS) defines the functional and non-functional requirements for the Acme Field Services Mobile Application. The document is intended for stakeholders, project managers, developers, QA engineers, and third-party vendors involved in the design, development, testing, and deployment of the application.
This document describes system features, user interactions, constraints, assumptions, and acceptance criteria for the application.
1.2 Intended Audience and Reading Suggestions 
This document is intended for all the project stakeholders, the project management team, and the development team, including frontend developers and quality assurance engineers. 
The list of intended audiences may be expanded during the project development. The structure of this document is represented in the following chapters:
Introduction
Overall description
External interface requirements
System features
Other non-functional requirements
Other requirements
Proceedings through these sections are highly demanded to complete the overall vision of the product and detailed feature requirements.
1.3 Definitions, Acronyms, and Abbreviations
FT – Field Technician
PF – Project Facilitator
MVP – Minimum Viable Product
SOW – Statement of Work
COI – Certificate of Insurance
MFA – Multi-Factor Authentication
GPS – Global Positioning System

1.4 Product Scope 
The Acme Field Services Mobile Application is a mobile solution designed for the Field Services team, specifically Field Technicians (FTs) and Project Facilitators (PFs). The application will streamline communication, job management, and the submission of deliverables such as surveys and photos.
The application will replace existing third-party tools (e.g., GoCanvas and CompanyCam) and serve as a centralized platform for job execution, documentation, and reporting.

1.5 References 
This document refers to a list of artifacts (project materials) that fulfill the scope of outstanding requirements. The main artifacts influencing the requirements, scope, and time are part of the project plan.

Full list of references:
Mobile Application UI/UX wireframes 
Internal Acme Field Services workflow documentation
Acme Field Services Order Management API Reference (CTI-API)
Acme Field Services Order Management
Acme Field Services Mobile App API response model (Postman-based)
Any other documents related to the project have a minor influence and do not reference the Software requirements specification document.

2. Overall Description 
2.1 Product Perspective 
The application will be a standalone mobile app (iOS and Android) integrated with Acme Field Services’ backend systems. It will be used by external personnel: Field Technicians (FT).


2.2 Product Functions (High-Level)
The major functions of the application are determined within:
Secure user authentication via Phone number and OTP verification
Order assignment and scheduling
Order document management
Check-in / check-out with time and GPS tracking
Survey completion and photo submission
Two-way notifications
Offline data capture and synchronization

2.3 User Classes and Characteristics 
2.3.1 Field Technician (FT)
Field Technician at Acme Field Services installs, maintains, and supports technology infrastructure for large-scale, multi-site projects, managing everything from networks to specialized equipment, often deployed globally, requiring strong technical, communication, and problem-solving skills for onsite support in fast-paced, team-oriented environments. They work with diverse equipment and 
provide local technical expertise for major rollouts, ensuring high-quality deployment for clients.

The FT utilizes the Acme Field Services mobile application.
Mobile-first user
Completes jobs (orders) on-site
Requires offline functionality
Limited administrative access
2.3.2 Project Facilitator (PF)
Project Facilitator (PF) is a technical project management role responsible for coordinating the on-site deployment of technology rollouts. Unlike administrative dispatchers, PFs are expected to understand the technology being installed to provide direct support to field technicians.

The PF utilizes the Acme Field Services web application. This role is responsible for Order management and the necessary interaction with both the orders and the Field Technicians.
Assigns and manages jobs (orders)
Uploads and reviews documentation
Receives alerts and deliverables
Uses web or internal system (outside scope of mobile app UI unless specified)

2.4 Operating Environment 
The mobile application will be developed using Flutter, a cross-platform technology. This allows
for deployment on both major mobile operating systems, with the following minimum required
versions:
iOS: Version 16.0 and later
Android: Version 12.1 and later
The mobile application is designed to communicate with the Acme Field Services Order Management REST API. This API is built on the .NET framework.
The Mobile application is designed to communicate with the Survey Manager Web application via an REST API interface to retrieve Survey data. This API interface is built using Node.js technology.

 
2.5 Design and Implementation Constraints 
The Acme Field Services mobile application will be developed for both iOS and Android platforms.
Display and Design Specifications:
Resolution Width: The application must support a minimum width of 320px and a maximum width of 1440px.
Design Source: The primary source design file will be a Figma .fig file, which will contain:
Design Components
Project Wireframes
Project Prototype
Operational Requirements:
The application must maintain functionality even with intermittent or absent network connectivity.
2.6 Assumptions, Dependencies and Risks
Assumption:
A1: Project Facilitators (PFs) utilize the existing Acme Field Services system for job assignment and management.
Dependencies:
D1: Backend API Availability: Backend APIs must be available to support essential functions, including user authentication, job data retrieval, and document storage.
D2: Data Management System: The mobile application relies on data managed via a Acme Field Services web application. This requires dynamic data retrieval from a backend server connected to the DB content.
D3: Frontend Framework: A suitable frontend framework or library (e.g., Flutter) is required to build the mobile application. All necessary updates and modifications to this library must be applied to the application.
Risk Factors
R1: Design Changes: Alterations to the design of the actual products may necessitate significant application updates and require re-submission to mobile marketplaces (App Store, Google Play).
R2: Data Flexibility: Dependence on hardcoded data would limit the application's flexibility and demand manual updates whenever data changes occur.