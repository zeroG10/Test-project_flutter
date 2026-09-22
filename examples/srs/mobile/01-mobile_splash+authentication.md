External Interface Requirements 
3.1 User Interfaces 

This section describes the User interface of the Acme Field Services Mobile application with related logic and interactions with users. 

3.1.0 Splash screen
The Splash Screen is displayed during application startup and serves to:
	•	Present the Acme Field Services brand identity;
	•	Mask application initialization and loading processes;
	•	Perform initial system checks (authentication, configuration, session validation);
	•	Provide a smooth transition to the next screen without exposing technical delays to the user.

UI Description

Visual Elements:
	•	Full-screen white background
	•	Centered Acme Field Services logo (static)
	•	No interactive elements (buttons, links, inputs)
	•	System status bar visible (time, network, battery)

Visual Requirements:
	•	Logo must be centered both vertically and horizontally
	•	No text labels, progress indicators, or user actions required

Functional Requirements

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
3.1.1 Authentication
3.1.1.1 Welcome screen
The Welcome Screen is the entry point to the mobile application for users who are not yet authenticated.

It is designed to:
	•	Introduce the application to new and returning users
	•	Provide clear navigation to account creation or login
	•	Serve as a gateway into the authentication flow

UI Description

Layout
	•	Full-screen, minimal layout
	•	Centered welcome message
	•	Two primary call-to-action buttons at the bottom
Content

Header Text:

Welcome to the Acme Field Services

Subtext:

Create an account or log in to get started.

Primary Actions

Button
Style
Function
Sign up
Primary (filled)
Navigate to account registration flow
Login
Secondary (outlined/neutral)
Navigate to login screen


System UI
	•	Device status bar visible
	•	No navigation bar or back button on this screen
Functional Requirements

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

Navigation & Flow Logic

Condition
Result
App opened, user not logged in
Welcome Screen displayed
User taps Sign up
Navigate to Sign Up
User taps Login
Navigate to Login
Valid session detected
Skip Welcome → Home


Error Handling

FR-WEL-05
If navigation to Login or Sign Up fails, the app shall display a generic error and allow retry.
3.1.1.2 Registration screen
The Registration Screen allows a new Field Technician to create an account in the mobile application by providing basic personal and contact information.

This screen is designed to:
	•	Collect required user identity details
	•	Validate input before proceeding
	•	Initiate the account creation process
UI Description

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

Good to see you! Let’s get you registered.

Input Fields

Field
Type
Required
Notes
First name
Text
Yes
Alphabetical characters only
(Minimum: 2 characters, Maximum: 100 characters)
Last name
Text
Yes
Alphabetical characters only 
(Minimum: 2 characters, Maximum: 100 characters)
Phone number
Phone
Yes
Must follow valid phone format
Email
Email
No
Optional but must be valid if provided


Primary Action

Button
State
Behavior
Continue
Disabled by default
Enabled only when required fields are valid



Legal Text

Displayed below the button:

By continuing, you accept the Acme Field Services Terms and Privacy Policy

	•	“Terms” and “Privacy Policy” are tappable links

Privacy Policy link: https://www.acme-field.example.com/mobile-privacy/
Terms and Conditions link: https://www.acme-field.example.com/sms-terms-and-conditions/

Functional Requirements

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

User Action
Result
Open Registration
Form displayed
Fill required fields correctly
Continue button enabled
Tap Continue
Registration request sent
Tap Terms / Privacy
Privacy Policy link: https://www.acme-field.example.com/mobile-privacy/
Terms and Conditions link: https://www.acme-field.example.com/sms-terms-and-conditions/
Registration success
Navigate to next onboarding step
Registration failure
Error message shown


Error Handling

FR-REG-10
If the registration request fails (e.g., network error), the app shall:
	•	Display an error message
	•	Allow the user to retry

FR-REG-11
If the phone number is already registered, the app shall display:

“This phone number is already associated with an account.”

3.1.1.1 Phone number verification screen
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

+1 415 555 2314 (example)

OTP Input
	•	4 individual input boxes
	•	Numeric keypad opens automatically
	•	Auto-focus moves to next box after digit entry
	•	Backspace moves to previous box

Primary Action

Button
State
Behavior
Verify
Disabled until 4 digits entered
Submits OTP for validation


Secondary Action

Resend Code Text:

Didn’t receive the code? You can request a new code in [timer]

	•	Countdown timer displayed
	•	When timer reaches zero, text changes to tappable:

Request a new code

Functional Requirements

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

Condition
Result
Screen opened
Timer starts, OTP awaited
Correct OTP entered
Proceed to next onboarding step
Incorrect OTP
Error shown, allow retry
Timer expires
Resend option enabled
New code requested
New OTP sent, timer restarts


Error Handling

FR-OTP-12
If OTP verification fails due to network issues, display a generic error and allow retry.

FR-OTP-13
If maximum retry attempts are exceeded, the user shall be temporarily blocked (2 minutes)  and informed.
3.1.1.1 Login screen
The Login Screen allows an existing Field Technician to authenticate using their registered phone number and begin the sign-in process.

This screen is designed to:
	•	Collect the user’s phone number
	•	Validate input format
	•	Initiate the authentication flow (OTP verification)

UI Description

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

Good to see you! Let’s get you log in.

Input Field

Field
Type
Required
Notes
Phone number
Phone
Yes
Must match valid phone format


	•	Numeric keypad displayed
	•	International format supported (e.g., +1 415 555 2314)
Primary Action
Button
State
Behavior
Log in
Disabled by default
Enabled when phone number is valid


Legal Text
Displayed below the button:
By continuing, you accept the Acme Field Services Terms and Privacy Policy
	•	Both are tappable links
Functional Requirements

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

User Action
Result
Open Login
Form displayed
Enter valid phone
Log in button enabled
Tap Log in
OTP requested and navigate to OTP screen
Tap Terms / Privacy
Legal document opens


Error Handling

FR-LOG-08
If the phone number is not associated with an account, display:

No account found with this phone number.

FR-LOG-09
If login request fails due to network issues, show a generic error and allow retry.
