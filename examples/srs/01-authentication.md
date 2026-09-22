3.1.1 Authentication
3.1.1.1 Set password page
The Set Password page allows newly created Admin Panel users to activate their account and set an initial password.
This page is accessed via a secure, single-use link sent by email after a Super Admin creates a new user (Root or Manager).

The screen is designed to:


	•	Securely validate the user’s identity;
	•	Enforce password complexity and security standards;
	•	Complete account activation;
	•	Enable the user to access the Admin Panel.


Entry Conditions & Preconditions


	•	The user account has been created by a Root User.
	•	The user has received an email containing a unique, time-limited activation link.
	•	The activation token embedded in the link is:
		•	Valid
		•	Not expired
		•	Not previously used
UI Description

Layout
	•	Centered card layout on a neutral background
	•	Acme Field Services logo displayed above the form
	•	Single-column form optimized for desktop and tablet

Page Content

Title:
Set password

Instructional text:
Describes password requirements, e.g.:

“Password must be longer than 12 characters, contain at least 1 digit, 1 letter and either 1 special symbol or 1 uppercase letter.”

Form Fields

New Password
	•	Password input field
	•	Masked input by default
	•	Visibility toggle (show / hide password)

Confirm Password
	•	Password input field
	•	Masked input by default
	•	Visibility toggle (show / hide password)

Primary Action
	•	Set password button
	•	Button states:
	•	Disabled by default
	•	Enabled only when all validations pass

Validation Feedback
	•	Inline validation messages below fields
	•	Error highlighting on invalid inputs
	•	Client-side validation before submission

Functional Requirements

Account Activation Flow

FR-AUTH-SP-01
The system shall validate the activation token upon page load.

FR-AUTH-SP-02
If the activation token is invalid or expired, the system shall block password setup and display an appropriate error message.

FR-AUTH-SP-03
The account shall be marked as active only after successful password creation.

Password Rules & Validation

FR-AUTH-SP-04
The system shall enforce the following password rules:
	•	Minimum length (e.g., ≥ 12 characters)
	•	At least one digit
	•	At least one letter
	•	At least one special character or one uppercase letter

FR-AUTH-SP-05
The Confirm Password value must exactly match the New Password value.

FR-AUTH-SP-06
Validation errors shall be displayed inline and in real time.

Submission Behavior

FR-AUTH-SP-07
The Set password button shall remain disabled until:
	•	All password rules are satisfied;
	•	Password and confirmation match.

FR-AUTH-SP-08
Upon successful submission, the system shall:
	•	Persist the password securely (hashed);
	•	Invalidate the activation token;
	•	Redirect the user to the Login page (or auto-login, if configured).

Navigation & Flow Logic


User Action
Result
Open activation link
Set Password page loads
Invalid/expired token
Error state shown
Enter invalid password
Inline validation errors
Passwords match & valid
Set password enabled
Click Set password
Account activated
Activation complete
Redirect to Login


Error Handling

FR-AUTH-SP-09
If password submission fails due to server error:
	•	Display a generic error message;
	•	Allow the user to retry without losing input.

FR-AUTH-SP-10
The system shall prevent reuse of activation links.

Security Requirements

NFR-AUTH-SP-01
Passwords shall never be logged or stored in plain text.

NFR-AUTH-SP-02
Activation links shall:
	•	Be single-use;
	•	Have an expiration time (configurable).

NFR-AUTH-SP-03
All communication shall occur over HTTPS.

3.1.1.2 Login page
The Login page allows authorized Admin Panel users to authenticate using email and password in order to access the Admin Panel system.
It serves as the primary entry point for both Root Users and Manager Users after account activation.

The screen is designed to:
	•	Securely authenticate users;
	•	Enforce input validation before submission;
	•	Provide clear feedback for authentication errors;
	•	Support session persistence via “Remember me”.

Entry Conditions & Preconditions


	•	The user account exists in the system.
	•	The account has been activated via the Set Password flow.
	•	The user is not already authenticated (no valid active session).

UI Description

Layout
	•	Centered authentication card on a neutral background
	•	Acme Field Services logo displayed above the form
	•	Single-column layout optimized for desktop and tablet


Page Content

Title:
Log in using your credentials

Form Fields

Email
	•	Text input field
	•	Placeholder text: Please enter
	•	Client-side email format validation
	•	Inline error messaging for invalid email format

Password
	•	Password input field
	•	Masked input by default
	•	Visibility toggle (show / hide password)

Additional Controls

Remember Me
	•	Checkbox option
	•	Persists user session according to security configuration

Forgot Password
	•	Text link
	•	Navigates to Forgot / Reset Password flow

Primary Action
	•	Log in button
	•	Button states:
	•	Disabled when required fields are empty or invalid
	•	Enabled when email and password inputs are valid

Error Feedback

Client-Side Errors
	•	Invalid email format
	•	Required fields empty

Server-Side Errors
	•	Incorrect email or password
	•	Account disabled or not activated

Errors are displayed inline or as a banner within the form.

Functional Requirements

Authentication Flow

FR-AUTH-LG-01
The system shall authenticate users using email and password credentials.

FR-AUTH-LG-02
The system shall validate input fields on the client side before submission.

FR-AUTH-LG-03
Invalid email formats shall prevent form submission and display an inline error.

Submission Behavior

FR-AUTH-LG-04
The Log in button shall remain disabled until:
	•	Email field contains a valid email format;
	•	Password field is not empty.

FR-AUTH-LG-05
Upon successful authentication, the system shall:
	•	Create an authenticated session;
	•	Redirect the user to the Admin Panel landing page (Dashboard or default page).

Error Handling

FR-AUTH-LG-06
If authentication fails due to incorrect credentials:
	•	Display a server-side error message (e.g., “Incorrect email or password”).

FR-AUTH-LG-07
Error messages shall not reveal which credential was incorrect.

Remember Me

FR-AUTH-LG-08
If “Remember me” is selected, the system shall persist the user session based on configured expiration rules.

Access Control

FR-AUTH-LG-09
After login, user access shall be restricted based on assigned role:
	•	Root User
	•	Manager User
Error Handling

FR-AUTH-LG-10
If the authentication service is unavailable:
	•	Display a generic error message;
	•	Allow the user to retry.

FR-AUTH-LG-11
Repeated failed login attempts may be rate-limited (recommended).

Security Requirements

NFR-AUTH-LG-01
Passwords shall never be logged or exposed in plaintext.

NFR-AUTH-LG-02
Authentication requests shall be transmitted over HTTPS only.

NFR-AUTH-LG-03
Session tokens shall be securely stored and protected against XSS and CSRF.

3.1.1.3 Forgot password page

The Forgot Password page allows Admin Panel users to initiate a secure password reset process when they have forgotten their password.

The screen is designed to:
	•	Collect the user’s registered email address;
	•	Validate the email format and existence;
	•	Trigger a secure password reset email;
	•	Guide the user back to authentication once the request is complete.

Entry Conditions & Preconditions
	•	The user is not authenticated.
	•	The user navigates to the Forgot Password page via the Login screen.
	•	The user has an existing account in the system.

UI Description

Layout
	•	Centered card layout on a neutral background
	•	Acme Field Services logo displayed above the form
	•	Single-column layout optimized for desktop and tablet

Page Content

Title:
Forgot your password?

Instructional text:
Explains the process, e.g.:

“Please enter the email address associated with your account, and we’ll send you a verification code to reset your password.”

Form Fields

Email
	•	Text input field
	•	Placeholder text: Please enter
	•	Client-side email format validation
	•	Inline error message for invalid email format

Primary Action
	•	Request password reset button
	•	Button states:
	•	Disabled when email field is empty or invalid
	•	Enabled when a valid email format is entered

Secondary Action
	•	Back to Login link
	•	Navigates the user back to the Login page

Success State

After a successful request:
	•	The form is replaced with a confirmation message:
“Please check your email.
If an account is associated with this address, we’ve sent a reset link.”
	•	Back to Login link remains available

Functional Requirements

Password Reset Request

FR-AUTH-FP-01
The system shall allow users to request a password reset by providing their email address.

FR-AUTH-FP-02
The system shall validate the email format on the client side before submission.

FR-AUTH-FP-03
The Request password reset button shall remain disabled until a valid email format is entered.


Submission Behavior

FR-AUTH-FP-04
Upon submission, the system shall:
	•	Verify whether the email exists in the system;
	•	Generate a secure, time-limited password reset token;
	•	Send a password reset email containing a reset link.

FR-AUTH-FP-05
The system shall display a success confirmation message regardless of whether the email exists (to prevent account enumeration).

Reset Link Behavior

FR-AUTH-FP-06
The password reset email shall contain a single-use, time-limited link that directs the user to the Set Password page.

Navigation & Flow Logic


User Action
Result
Open Forgot Password
Forgot Password form displayed
Enter invalid email
Client-side validation error
Enter valid email
Request button enabled
Submit request
Confirmation message shown
Click Back to Login
Navigate to Login page
Click reset link from email
Navigate to Set Password page


Error Handling

FR-AUTH-FP-07
If the password reset service is unavailable:
	•	Display a generic error message;
	•	Allow the user to retry.

FR-AUTH-FP-08
The system shall not disclose whether an email is registered or not.

Security Requirements

NFR-AUTH-FP-01
Password reset tokens shall:
	•	Be single-use;
	•	Expire after a configurable time period.

NFR-AUTH-FP-02
Reset requests shall be rate-limited to prevent abuse.

NFR-AUTH-FP-03
All password reset communications shall occur over HTTPS.
