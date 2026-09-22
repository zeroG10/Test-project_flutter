/**
 * Authentication WEB QA checklist generator — Vadym's v5 web template (25 cols).
 * Hierarchy: Page -> Section -> Check.  Variant B: 1 feature = 1 page band,
 * screens become sections.
 *
 * Content = the project's reviewed checklist
 *   qa/checklists/web/authentication-checklist.md (CHK-AUTH ids preserved in B).
 * Single "Authentication" page band; each screen (Login / Forgot password /
 * Set password / All authentication pages) is a section holding that screen's
 * checks in source order. addSection() auto-prepends the VISUAL design check.
 *
 * Executed by automation/checklist-gen/web/generate_via_api.mjs (service account).
 */
function createAuthenticationChecklist() {
  var FOLDER_PATH = ['Projects', 'Acme Field Services', 'QA Documentation']; // ignored by service-account adapter
  var FILE_NAME   = 'Acme Field Services - Authentication checklist';
  var SHEET_NAME  = 'Checklist';
  var AUTHOR      = 'QA';

  // ── Drive: find/create folder chain and spreadsheet ─────────────────
  var folder = DriveApp.getRootFolder();
  FOLDER_PATH.forEach(function (name) {
    var it = folder.getFoldersByName(name);
    folder = it.hasNext() ? it.next() : folder.createFolder(name);
  });

  var ss;
  var files = folder.getFilesByName(FILE_NAME);
  if (files.hasNext()) {
    ss = SpreadsheetApp.open(files.next());
  } else {
    ss = SpreadsheetApp.create(FILE_NAME);
    DriveApp.getFileById(ss.getId()).moveTo(folder);
  }

  var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  ['Sheet1', 'Аркуш1'].forEach(function (n) {
    var sh = ss.getSheetByName(n);
    if (sh && ss.getSheets().length > 1 && n !== SHEET_NAME) ss.deleteSheet(sh);
  });

  // ── Cleanup ─────────────────────────────────────────────────────────
  var full = sheet.getRange(1, 1, sheet.getMaxRows(), sheet.getMaxColumns());
  full.breakApart();
  full.clear();
  full.clearDataValidations();
  sheet.setConditionalFormatRules([]);

  // ── Layout constants (web variant: 25 columns A..Y) ─────────────────
  var NCOLS = 25;
  var COLORS = {
    teal:    '#134f5c', tealFg:  '#f3f3f3', blue:    '#699ebf',
    passBg:  '#d2ebda', passFg:  '#135522',
    failBg:  '#f8d5da', failFg:  '#701c22',
    gray:    '#d9d9d9', grayFg:  '#434343',
    cntPass: '#b6d7a8', cntFail: '#f4cccc',
    pageBg:  '#b7b7b7', statusBg:'#efefef', resultBg:'#f3f3f3',
    purple:  '#8E7BC3', white:   '#ffffff'
  };
  var WIDTHS = [150, 530, 185, 110, 110, 110, 19, 82, 84, 18,
                185, 110, 110, 110, 19, 82, 84, 18,
                185, 102, 102, 102, 23, 78, 79];
  var BLOCKS = [
    { s: 3,  c1: 4,  c3: 6,  rA: 8,  rB: 9  },
    { s: 11, c1: 12, c3: 14, rA: 16, rB: 17 },
    { s: 19, c1: 20, c3: 22, rA: 24, rB: 25 }
  ];
  var SPACERS = [7, 10, 15, 18, 23];

  function cl(n) { return String.fromCharCode(64 + n); }

  // ── Pages / sections / checks ───────────────────────────────────────
  var VISUAL = 'Check that the fonts, sizes, colors and spacing in this section match the Figma design';
  var PAGES = [];
  var _curPage = null, _curSection = null;
  function addPage(name) {
    _curPage = { name: name, sections: [] };
    PAGES.push(_curPage);
    _curSection = null;
  }
  function addSection(name) {
    if (!_curPage) throw new Error('Call addPage(...) before addSection(...)');
    _curSection = { name: name, checks: [VISUAL] };
    _curPage.sections.push(_curSection);
  }
  function item(text) {
    if (!_curSection) throw new Error('Call addSection(...) before item(...)');
    _curSection.checks.push(text);
  }

  // ── Content (from authentication-checklist.md, Variant B: feature = page,
  //    screens = sections; checks kept in source order within each screen) ─
  var PAGE_NAME = 'Authentication';
  var SCREENS = [
    { name: 'Login page', checks: [
      '[CHK-AUTH-005] Check that the Login page is reachable without an authenticated session.',
      '[CHK-AUTH-006] Check that the Login page redirects an already authenticated user away from the form.',
      '[CHK-AUTH-007] Check that the Login page denies access when credentials belong to a non-activated account.',
      '[CHK-AUTH-008] Check that the Login page denies access when credentials belong to a disabled account.',
      '[CHK-AUTH-009] Check that after successful login as Root User the system grants access to the Admin Panel landing page.',
      '[CHK-AUTH-010] Check that after successful login as Manager User the system grants access to the Admin Panel landing page.',
      '[CHK-AUTH-011] Check that after successful login as Manager User the Managers list page is not accessible.',
      '[CHK-AUTH-014] Check that the Login page exposes a Forgot Password link that navigates to the Forgot Password page.',
      '[CHK-AUTH-017] Check that after successful login the user is redirected to the Admin Panel landing page.',
      '[CHK-AUTH-021] Check that using the browser Back button after a successful login does not return the user to the Login page in an authenticated state.',
      '[CHK-AUTH-023] Check that the Login page displays a centered card layout on a neutral background.',
      '[CHK-AUTH-026] Check that the Acme Field Services logo is displayed above the form on the Login page.',
      '[CHK-AUTH-029] Check that the Login page shows the title "Log in using your credentials".',
      '[CHK-AUTH-039] Check that the Login page contains an Email field with placeholder "Please enter".',
      '[CHK-AUTH-040] Check that the Login page contains a Password field with masked input by default.',
      '[CHK-AUTH-041] Check that the Password field on the Login page provides a visibility toggle to show or hide the password.',
      '[CHK-AUTH-042] Check that the Login page contains a Remember Me checkbox.',
      '[CHK-AUTH-043] Check that the Login page contains a Forgot Password link.',
      '[CHK-AUTH-044] Check that the Login page contains a primary "Log in" button disabled when required fields are empty or invalid.',
      '[CHK-AUTH-129] Check that the Remember Me checkbox on the Login page is selected by default when the page loads.',
      '[CHK-AUTH-130] Check that the Forgot Password link on the Login page reads "Forgot password?" and is right-aligned on the same row as the Remember Me checkbox.',
      '[CHK-AUTH-131] Check that the Log in button spans the full width of the Login form card.',
      '[CHK-AUTH-132] Check that the Password field on the Login page shows the visibility toggle as an eye icon at the right edge of the field.',
      '[CHK-AUTH-052] Check that entering a valid email and a non-empty password on the Login page enables the "Log in" button.',
      '[CHK-AUTH-053] Check that submitting valid credentials on the Login page creates an authenticated session and redirects to the landing page.',
      '[CHK-AUTH-054] Check that selecting Remember Me on the Login page persists the session beyond the default expiration according to the security configuration.',
      '[CHK-AUTH-055] Check that not selecting Remember Me on the Login page limits session persistence to the default expiration window.',
      '[CHK-AUTH-069] Check that the Login page rejects an invalid email format with an inline error and prevents submission.',
      '[CHK-AUTH-070] Check that the "Log in" button stays disabled when the email field is empty.',
      '[CHK-AUTH-071] Check that the "Log in" button stays disabled when the password field is empty.',
      '[CHK-AUTH-072] Check that the "Log in" button stays disabled when the email field contains an invalid format.',
      '[CHK-AUTH-133] Check that entering an email in an invalid format on the Login page shows the inline error "Please enter a valid email address." below the Email field.',
      '[CHK-AUTH-134] Check that the Email field on the Login page shows a red border and a red error icon inside the field when the entered email format is invalid.',
      '[CHK-AUTH-078] Check that submitting incorrect credentials on the Login page displays a generic "Incorrect email or password" error.',
      '[CHK-AUTH-079] Check that the Login error message does not reveal whether the email or the password was incorrect.',
      '[CHK-AUTH-080] Check that submitting credentials for a disabled account on the Login page displays an authentication error without disclosing account state.',
      '[CHK-AUTH-081] Check that submitting credentials for a non-activated account on the Login page displays an authentication error.',
      '[CHK-AUTH-083] Check that submitting the Login form with leading or trailing whitespace in the email is treated according to backend trimming rules.',
      '[CHK-AUTH-135] Check that submitting incorrect credentials on the Login page shows the banner "Incorrect email or password." at the top of the form card.',
      '[CHK-AUTH-087] Check that a Remember Me session ends at the configured expiration time even if the browser remains open.',
      '[CHK-AUTH-094] Check that an authenticated session created at login persists across page reloads within its configured lifetime.',
      '[CHK-AUTH-095] Check that Remember Me persists the session across browser restarts according to the configured expiration.',
      '[CHK-AUTH-096] Check that without Remember Me the session does not persist beyond the default session expiration.',
      '[CHK-AUTH-099] Check that the Login page displays a generic error message and allows retry when the authentication service is unavailable.',
      '[CHK-AUTH-104] Check that the Login page shows a loading state on the "Log in" button while the authentication request is in flight.',
      '[CHK-AUTH-108] Check that the Login page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-AUTH-111] Check that browser password autofill on the Login page does not break the enabled/disabled state of the "Log in" button.',
      '[CHK-AUTH-122] Check that role-based access enforced after login restricts Manager Users from Root-only areas such as the Managers list.',
      '[CHK-AUTH-126] Check that after a successful login the role-based navigation menu reflects the user\'s role on the landing page.',
      '[CHK-AUTH-128] Check that the activation flow does not interfere with previously activated accounts attempting to log in.' ] },

    { name: 'Forgot password page', checks: [
      '[CHK-AUTH-012] Check that the Forgot Password page is reachable from the Login page without authentication.',
      '[CHK-AUTH-015] Check that the Forgot Password page exposes a Back to Login link that navigates to the Login page.',
      '[CHK-AUTH-019] Check that the Back to Login link on the Forgot Password page remains available after the success confirmation is shown.',
      '[CHK-AUTH-024] Check that the Forgot Password page displays a centered card layout on a neutral background.',
      '[CHK-AUTH-027] Check that the Acme Field Services logo is displayed above the form on the Forgot Password page.',
      '[CHK-AUTH-030] Check that the Forgot Password page shows the title "Forgot your password?".',
      '[CHK-AUTH-032] Check that the Forgot Password page shows instructional text describing the reset process.',
      '[CHK-AUTH-045] Check that the Forgot Password page contains an Email field with placeholder "Please enter".',
      '[CHK-AUTH-046] Check that the Forgot Password page contains a primary "Request password reset" button disabled by default.',
      '[CHK-AUTH-047] Check that the Forgot Password page contains a Back to Login link.',
      '[CHK-AUTH-056] Check that entering a valid email format on the Forgot Password page enables the "Request password reset" button.',
      '[CHK-AUTH-057] Check that submitting a valid email on the Forgot Password page replaces the form with the success confirmation message.',
      '[CHK-AUTH-058] Check that submitting a valid email associated with an existing account on the Forgot Password page triggers a password reset email containing a single-use reset link.',
      '[CHK-AUTH-073] Check that the Forgot Password page rejects an invalid email format with an inline error.',
      '[CHK-AUTH-074] Check that the "Request password reset" button stays disabled when the email field is empty or invalid.',
      '[CHK-AUTH-082] Check that submitting a non-existent email on the Forgot Password page still displays the same success confirmation message to prevent account enumeration.',
      '[CHK-AUTH-086] Check that a previously issued password reset token becomes invalid after being used once.',
      '[CHK-AUTH-088] Check that a password reset email is sent when a valid email is submitted on the Forgot Password page and an account exists.',
      '[CHK-AUTH-089] Check that the password reset email contains a single-use, time-limited reset link.',
      '[CHK-AUTH-090] Check that the success confirmation message on the Forgot Password page reads "Please check your email. If an account is associated with this address, we\'ve sent a reset link."',
      '[CHK-AUTH-091] Check that no password reset email is sent when the submitted email does not match any account.',
      '[CHK-AUTH-100] Check that the Forgot Password page displays a generic error message and allows retry when the password reset service is unavailable.',
      '[CHK-AUTH-105] Check that the Forgot Password page shows a loading state on the "Request password reset" button while the request is in flight.',
      '[CHK-AUTH-109] Check that the Forgot Password page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-AUTH-116] Check that password reset tokens on the Forgot Password flow are single-use and expire after the configured time.',
      '[CHK-AUTH-117] Check that the Forgot Password response is identical regardless of whether the email is registered to prevent account enumeration.' ] },

    { name: 'Set password page', checks: [
      '[CHK-AUTH-001] Check that the Set Password page is accessible only via a valid activation link sent by email.',
      '[CHK-AUTH-002] Check that the Set Password page blocks access and shows an error if the activation token is invalid.',
      '[CHK-AUTH-003] Check that the Set Password page blocks access and shows an error if the activation token is expired.',
      '[CHK-AUTH-004] Check that the Set Password page blocks access and shows an error if the activation token was already used.',
      '[CHK-AUTH-016] Check that after successful password creation on the Set Password page the user is redirected to the Login page (or auto-logged in, if configured).',
      '[CHK-AUTH-018] Check that the password reset email link navigates the user to the Set Password page.',
      '[CHK-AUTH-020] Check that using the browser Back button after a successful Set Password submission does not return the user to a usable form state.',
      '[CHK-AUTH-022] Check that the Set Password page displays a centered card layout on a neutral background.',
      '[CHK-AUTH-025] Check that the Acme Field Services logo is displayed above the form on the Set Password page.',
      '[CHK-AUTH-028] Check that the Set Password page shows the title "Set password".',
      '[CHK-AUTH-031] Check that the Set Password page shows instructional text describing the password requirements.',
      '[CHK-AUTH-034] Check that the Set Password page contains a New Password field with masked input by default.',
      '[CHK-AUTH-035] Check that the Set Password page contains a Confirm Password field with masked input by default.',
      '[CHK-AUTH-036] Check that the New Password field on the Set Password page provides a visibility toggle to show or hide the password.',
      '[CHK-AUTH-037] Check that the Confirm Password field on the Set Password page provides a visibility toggle to show or hide the password.',
      '[CHK-AUTH-038] Check that the Set Password page contains a primary "Set password" button disabled by default.',
      '[CHK-AUTH-048] Check that opening a valid activation link loads the Set Password page without errors.',
      '[CHK-AUTH-049] Check that entering a New Password that satisfies all rules and a matching Confirm Password enables the "Set password" button on the Set Password page.',
      '[CHK-AUTH-050] Check that clicking "Set password" with valid matching passwords activates the account and persists the password securely.',
      '[CHK-AUTH-051] Check that after successful password creation on the Set Password page the activation token is invalidated and cannot be reused.',
      '[CHK-AUTH-059] Check that opening the reset link from the password reset email loads the Set Password page with a valid token.',
      '[CHK-AUTH-060] Check that the Set Password page rejects a New Password shorter than 12 characters with an inline error.',
      '[CHK-AUTH-061] Check that the Set Password page rejects a New Password without at least one digit with an inline error.',
      '[CHK-AUTH-062] Check that the Set Password page rejects a New Password without at least one letter with an inline error.',
      '[CHK-AUTH-063] Check that the Set Password page rejects a New Password without at least one special character or one uppercase letter with an inline error.',
      '[CHK-AUTH-064] Check that the Set Password page shows inline validation errors in real time as the user types.',
      '[CHK-AUTH-065] Check that the Set Password page rejects submission when Confirm Password does not exactly match New Password.',
      '[CHK-AUTH-066] Check that the "Set password" button remains disabled while any password rule is unmet.',
      '[CHK-AUTH-067] Check that the "Set password" button remains disabled while New Password and Confirm Password do not match.',
      '[CHK-AUTH-068] Check that invalid inputs on the Set Password page are highlighted with an error style.',
      '[CHK-AUTH-075] Check that opening an invalid activation link on the Set Password page shows an error state and blocks the form.',
      '[CHK-AUTH-076] Check that opening an expired activation link on the Set Password page shows an error state and blocks the form.',
      '[CHK-AUTH-077] Check that opening a previously used activation link on the Set Password page shows an error state and blocks the form.',
      '[CHK-AUTH-084] Check that the account status changes to active only after a successful password creation on the Set Password page.',
      '[CHK-AUTH-085] Check that the activation token is marked as used immediately after successful password submission.',
      '[CHK-AUTH-092] Check that the activation email sent after Root User creates a new account contains a single-use, time-limited activation link.',
      '[CHK-AUTH-093] Check that a password set on the Set Password page is persisted and usable to log in on the Login page.',
      '[CHK-AUTH-097] Check that input entered in the Set Password form is preserved when a server error occurs during submission.',
      '[CHK-AUTH-098] Check that the Set Password page displays a generic error message and allows retry when the password submission fails due to a server error.',
      '[CHK-AUTH-103] Check that the Set Password page shows a loading state on the "Set password" button while the submission request is in flight.',
      '[CHK-AUTH-106] Check that the Set Password page shows a loading state while validating the activation token on page load.',
      '[CHK-AUTH-107] Check that the Set Password page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-AUTH-112] Check that browser password manager prompts to save the new password after a successful Set Password submission.',
      '[CHK-AUTH-115] Check that activation links on the Set Password page are single-use and become invalid after a successful submission.' ] },

    { name: 'All authentication pages', checks: [
      '[CHK-AUTH-013] Check that the Set Password, Login, and Forgot Password pages are not accessible while a valid session is already active unless explicitly allowed.',
      '[CHK-AUTH-033] Check that each authentication page uses a single-column form optimized for desktop and tablet.',
      '[CHK-AUTH-101] Check that backend errors on any authentication page do not expose stack traces or internal details to the user.',
      '[CHK-AUTH-102] Check that submission buttons on all authentication pages do not allow duplicate submissions while a request is in flight.',
      '[CHK-AUTH-110] Check that the password visibility toggle works on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-AUTH-113] Check that all authentication page requests are transmitted over HTTPS only.',
      '[CHK-AUTH-114] Check that passwords are never sent or displayed in plaintext in network logs or browser dev tools.',
      '[CHK-AUTH-118] Check that session tokens are stored in a manner that protects against XSS access.',
      '[CHK-AUTH-119] Check that authenticated requests include CSRF protection where applicable.',
      '[CHK-AUTH-120] Check that pasting script payloads into the email or password fields does not execute as code.',
      '[CHK-AUTH-121] Check that the password visibility toggle does not reveal the password value in the DOM in a way that persists after toggle-off.',
      '[CHK-AUTH-123] Check that logout invalidates the session token on the server side and prevents reuse.',
      '[CHK-AUTH-124] Check that an expired session redirects the user back to the Login page on the next protected action.',
      '[CHK-AUTH-125] Check that after a password reset the previous password can no longer be used to log in on the Login page.',
      '[CHK-AUTH-127] Check that existing active sessions remain valid after a different user resets their password.' ] }
  ];

  // ── Managers (from managers-checklist.md, Variant B: feature = page,
  //    screens = sections) ────────────────────────────────────────────────
  var SCREENS_MGR = [
    { name: 'Managers list page', checks: [
      '[CHK-MGR-001] Check that the Managers list page is accessible to a user with the Root User role.',
      '[CHK-MGR-002] Check that the Managers list page denies access to a user with the Manager User role and does not render the table.',
      '[CHK-MGR-005] Check that an unauthenticated user is redirected to the Login page when attempting to open the Managers list page directly via URL.',
      '[CHK-MGR-007] Check that a Manager User cannot see a Managers entry in the left-side navigation menu.',
      '[CHK-MGR-008] Check that a Manager User attempting to open the Managers list page URL directly receives an access-denied response from the backend.',
      '[CHK-MGR-010] Check that the Managers list page is reachable from the left-side navigation menu for a Root User.',
      '[CHK-MGR-011] Check that clicking the Add button on the Managers list page navigates to the Add Manager page.',
      '[CHK-MGR-012] Check that clicking the Edit action in a row on the Managers list page navigates to the Edit Manager page for the selected user.',
      '[CHK-MGR-018] Check that the Managers list page uses the standard Admin Panel layout with left-side navigation and top header.',
      '[CHK-MGR-019] Check that the Managers list page displays the title "List of Managers" in the page header.',
      '[CHK-MGR-020] Check that the Managers list page displays an Add button as the primary action in the page header.',
      '[CHK-MGR-021] Check that the Managers list page displays the table columns Name, Email, Role, Created at, Last log in, Status, and Actions.',
      '[CHK-MGR-022] Check that the Managers list page displays the Status column with both color indicator and label text.',
      '[CHK-MGR-023] Check that the Managers list page displays pagination controls at the bottom of the table.',
      '[CHK-MGR-024] Check that the Managers list page displays an items-per-page selector with options 10, 25, and 50.',
      '[CHK-MGR-025] Check that the Managers list page displays the total items count near the pagination controls.',
      '[CHK-MGR-046] Check that the Edit action is available in each row on the Managers list page.',
      '[CHK-MGR-047] Check that a Root User can open the Managers list page and see the paginated list of all Manager and Root user accounts.',
      '[CHK-MGR-051] Check that a newly created Manager appears in the Managers list page immediately after creation.',
      '[CHK-MGR-060] Check that the deleted Manager no longer appears in the Managers list page after a successful deletion.',
      '[CHK-MGR-069] Check that the Managers list page is not rendered if the authenticated user has the Manager User role.',
      '[CHK-MGR-081] Check that the Status column on the Managers list page reflects status changes made on the Edit Manager form after save.',
      '[CHK-MGR-082] Check that the Status indicator uses distinct colors for Active, Pending, and Inactive on the Managers list page.',
      '[CHK-MGR-090] Check that the Name column on the Managers list page supports ascending and descending sort.',
      '[CHK-MGR-091] Check that the Created at column on the Managers list page supports ascending and descending sort.',
      '[CHK-MGR-092] Check that the Status column on the Managers list page supports ascending and descending sort.',
      '[CHK-MGR-093] Check that the active sort column and direction are visually indicated in the column header on the Managers list page.',
      '[CHK-MGR-094] Check that the column settings control on the Managers list page allows showing and hiding configurable columns.',
      '[CHK-MGR-095] Check that pagination on the Managers list page uses server-side paging and fetches the next page when the page is changed.',
      '[CHK-MGR-096] Check that changing the items-per-page selector on the Managers list page reloads the table with the new page size.',
      '[CHK-MGR-097] Check that the selected page size on the Managers list page persists across navigations within the same session.',
      '[CHK-MGR-098] Check that the selected page size on the Managers list page resets after the user logs out and back in.',
      '[CHK-MGR-099] Check that a Manager created on the Add Manager form is persisted and visible on the Managers list page after a full page reload.',
      '[CHK-MGR-101] Check that a deleted Manager is removed from persistence and does not reappear on the Managers list page after a full page reload.',
      '[CHK-MGR-102] Check that column-settings visibility selections on the Managers list page persist for the duration of the session.',
      '[CHK-MGR-103] Check that sort selection on the Managers list page persists while navigating between table pages within the same session.',
      '[CHK-MGR-104] Check that the Managers list page displays an error message with a retry option if the managers data request fails.',
      '[CHK-MGR-105] Check that the Managers list table continues to render available rows if the response contains partial data.',
      '[CHK-MGR-111] Check that the Managers list page displays an empty-state illustration when no Managers exist.',
      '[CHK-MGR-112] Check that the Managers list page displays the text "No managers have been added yet" when no Managers exist.',
      '[CHK-MGR-113] Check that the Add button remains available on the Managers list page when the empty state is shown.',
      '[CHK-MGR-114] Check that the Managers list page shows a table skeleton or loader while data is being fetched.',
      '[CHK-MGR-119] Check that the Managers list page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-MGR-123] Check that sorting and pagination controls on the Managers list page work on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-MGR-133] Check that creating a new Manager does not affect existing Manager or Root user accounts on the Managers list page.',
      '[CHK-MGR-134] Check that deleting a Manager does not affect other Manager or Root user accounts on the Managers list page.' ] },

    { name: 'Add Manager page', checks: [
      '[CHK-MGR-003] Check that the Add Manager page is accessible only to a user with the Root User role.',
      '[CHK-MGR-013] Check that after a Manager is successfully created on the Add Manager page the user is returned to the Managers list page.',
      '[CHK-MGR-016] Check that the browser Back button from the Add Manager page returns to the Managers list page without losing list state.',
      '[CHK-MGR-026] Check that the Add Manager page displays the title "Add manager".',
      '[CHK-MGR-028] Check that the Add Manager form displays the Name, Email, and Role fields.',
      '[CHK-MGR-029] Check that the Add Manager form displays a "Save & send invitation" primary action button.',
      '[CHK-MGR-044] Check that the Save button on the Add Manager form is disabled while required fields are empty or invalid.',
      '[CHK-MGR-048] Check that a Root User can open the Add Manager page from the Add button on the Managers list page.',
      '[CHK-MGR-049] Check that submitting the Add Manager form with valid Name, Email, and Role creates a new user in Pending status.',
      '[CHK-MGR-050] Check that submitting the Add Manager form with valid data triggers an invitation email containing a secure activation link.',
      '[CHK-MGR-052] Check that the activation link from the invitation email opens the Set Password page for the new user.',
      '[CHK-MGR-061] Check that the Add Manager form displays an inline required-field error for Name when submission is attempted with an empty Name.',
      '[CHK-MGR-062] Check that the Add Manager form displays an inline required-field error for Email when submission is attempted with an empty Email.',
      '[CHK-MGR-063] Check that the Add Manager form displays an inline required-field error for Role when submission is attempted without a Role selected.',
      '[CHK-MGR-064] Check that the Add Manager form rejects an invalid email format with an inline error and prevents submission.',
      '[CHK-MGR-066] Check that the Add Manager form rejects a duplicate email already used by another Admin Panel user with a descriptive error.',
      '[CHK-MGR-068] Check that the Save button on the Add Manager form remains disabled while any required field is empty or invalid.',
      '[CHK-MGR-070] Check that the Add Manager form preserves entered form data if creation fails due to a server-side error.',
      '[CHK-MGR-075] Check that a newly created Manager has status Pending until the invitation activation link is used.',
      '[CHK-MGR-083] Check that an invitation email is sent to the new Manager after successful creation on the Add Manager form.',
      '[CHK-MGR-084] Check that the invitation email contains a single-use, time-limited activation link.',
      '[CHK-MGR-087] Check that a success confirmation is shown after a Manager is successfully created on the Add Manager form.',
      '[CHK-MGR-106] Check that the Add Manager form displays a descriptive server error message if user creation fails due to a backend error.',
      '[CHK-MGR-115] Check that the Add Manager form shows a loading state on the "Save & send invitation" button while the create request is in flight.',
      '[CHK-MGR-120] Check that the Add Manager page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-MGR-128] Check that the activation link generated for a new Manager is single-use and time-limited.' ] },

    { name: 'Edit Manager page', checks: [
      '[CHK-MGR-004] Check that the Edit Manager page is accessible only to a user with the Root User role.',
      '[CHK-MGR-014] Check that after a Manager is successfully updated on the Edit Manager page the user remains on the Edit Manager page or is returned to the Managers list page per the configured flow.',
      '[CHK-MGR-015] Check that after a Manager is successfully deleted from the Edit Manager page the user is returned to the Managers list page.',
      '[CHK-MGR-017] Check that the browser Back button from the Edit Manager page returns to the Managers list page without losing list state.',
      '[CHK-MGR-027] Check that the Edit Manager page displays the title "Edit manager".',
      '[CHK-MGR-030] Check that the Edit Manager form displays the Name, Email, Role, and Status fields.',
      '[CHK-MGR-031] Check that the Edit Manager form displays the read-only system fields Created at and Last log in.',
      '[CHK-MGR-032] Check that the Last log in field is hidden on the Edit Manager form if no value is available.',
      '[CHK-MGR-033] Check that the Edit Manager form displays a Save primary action button.',
      '[CHK-MGR-034] Check that the Edit Manager form displays a Delete icon or button for the destructive action.',
      '[CHK-MGR-040] Check that the Status field on the Edit Manager form is a dropdown with values "Pending", "Active", and "Inactive".',
      '[CHK-MGR-041] Check that the Email field on the Edit Manager form is rendered as immutable (read-only or disabled).',
      '[CHK-MGR-042] Check that the Resend invitation button is visible on the Edit Manager form only if the manager status is Pending.',
      '[CHK-MGR-043] Check that the Resend invitation button is hidden on the Edit Manager form if the manager status is Active or Inactive.',
      '[CHK-MGR-045] Check that the Save button on the Edit Manager form is disabled while required fields are empty or invalid.',
      '[CHK-MGR-053] Check that opening the Edit Manager page preloads existing user data into the Name, Email, Role, and Status fields.',
      '[CHK-MGR-054] Check that changing the Name on the Edit Manager form and clicking Save persists the new name.',
      '[CHK-MGR-055] Check that changing the Role on the Edit Manager form and clicking Save persists the new role.',
      '[CHK-MGR-056] Check that changing the Status on the Edit Manager form and clicking Save persists the new status.',
      '[CHK-MGR-057] Check that clicking Resend invitation on a Pending manager triggers a new invitation email with a valid single-use activation link.',
      '[CHK-MGR-058] Check that clicking Delete on the Edit Manager form opens the Delete Manager confirmation dialog.',
      '[CHK-MGR-065] Check that the Edit Manager form displays an inline required-field error for Name when submission is attempted with an empty Name.',
      '[CHK-MGR-071] Check that the Edit Manager form preserves entered changes if the update fails due to a server-side error.',
      '[CHK-MGR-073] Check that attempting to change the Email field on the Edit Manager form does not modify the stored value.',
      '[CHK-MGR-074] Check that the Resend invitation button is unavailable on the Edit Manager form for a non-Pending manager.',
      '[CHK-MGR-079] Check that changing status from Active to Inactive on the Edit Manager form immediately revokes the Manager\'s login access.',
      '[CHK-MGR-080] Check that changing status from Inactive to Active on the Edit Manager form restores the Manager\'s login access.',
      '[CHK-MGR-085] Check that a new invitation email is sent when Resend invitation is clicked for a Pending Manager.',
      '[CHK-MGR-086] Check that the previous activation link is invalidated when a new invitation email is sent via Resend invitation.',
      '[CHK-MGR-088] Check that a success confirmation is shown after changes are saved on the Edit Manager form.',
      '[CHK-MGR-100] Check that changes saved on the Edit Manager form are persisted and visible after a full page reload.',
      '[CHK-MGR-107] Check that the Edit Manager form displays a descriptive server error message if the update fails due to a backend error.',
      '[CHK-MGR-116] Check that the Edit Manager form shows a loading state on the Save button while the update request is in flight.',
      '[CHK-MGR-118] Check that the Edit Manager page shows a loading state while preloading existing user data on open.',
      '[CHK-MGR-121] Check that the Edit Manager page renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-MGR-132] Check that the Email field cannot be modified on the Edit Manager form via direct API call.' ] },

    { name: 'Delete Manager confirmation dialog', checks: [
      '[CHK-MGR-035] Check that the Delete Manager confirmation dialog displays the exact text "All data associated with manager [Name] will be deleted permanently." with the actual manager name substituted.',
      '[CHK-MGR-059] Check that confirming the Delete Manager dialog permanently removes the user account and returns the Root User to the Managers list page.',
      '[CHK-MGR-072] Check that cancelling or closing the Delete Manager confirmation dialog does not delete the user account.',
      '[CHK-MGR-089] Check that a success confirmation is shown after a Manager is successfully deleted.',
      '[CHK-MGR-108] Check that the Delete Manager confirmation dialog displays a descriptive error message and keeps the user account if the deletion request fails.',
      '[CHK-MGR-117] Check that the Delete Manager confirmation dialog shows a loading state on the confirm button while the delete request is in flight.',
      '[CHK-MGR-122] Check that the Delete Manager confirmation dialog renders and functions identically on the latest versions of Chrome, Firefox, and Edge.',
      '[CHK-MGR-129] Check that a deleted Manager\'s session and tokens are invalidated immediately after deletion.' ] },

    { name: 'All Managers pages', checks: [
      '[CHK-MGR-006] Check that an unauthenticated user is redirected to the Login page when attempting to open the Add or Edit Manager page directly via URL.',
      '[CHK-MGR-009] Check that role checks for the Managers module are enforced on the backend independently of the frontend.',
      '[CHK-MGR-036] Check that the Name field on the Add Manager and Edit Manager forms is marked as required.',
      '[CHK-MGR-037] Check that the Email field on the Add Manager and Edit Manager forms is marked as required.',
      '[CHK-MGR-038] Check that the Role field on the Add Manager and Edit Manager forms is a dropdown with values "Manager" and "Admin".',
      '[CHK-MGR-039] Check that the Role field on the Add Manager and Edit Manager forms is marked as required.',
      '[CHK-MGR-067] Check that invalid inputs on the Add and Edit Manager forms are highlighted with an error style.',
      '[CHK-MGR-076] Check that a Pending Manager transitions to Active after successfully setting a password via the activation link.',
      '[CHK-MGR-077] Check that a Pending Manager cannot log in to the Admin Panel because no password has been set.',
      '[CHK-MGR-078] Check that an Inactive Manager cannot log in to the Admin Panel.',
      '[CHK-MGR-109] Check that backend errors on the Managers pages do not expose stack traces or internal details to the user.',
      '[CHK-MGR-110] Check that submission buttons on the Add and Edit Manager forms do not allow duplicate submissions while a request is in flight.',
      '[CHK-MGR-124] Check that all Managers module requests are transmitted over HTTPS only.',
      '[CHK-MGR-125] Check that role-based access for the Managers module is enforced on the backend regardless of frontend state.',
      '[CHK-MGR-126] Check that a Manager User receives an authorization error from the backend when calling Managers list, create, update, or delete endpoints directly.',
      '[CHK-MGR-127] Check that sensitive user fields are not returned to non-Root callers by the Managers endpoints.',
      '[CHK-MGR-130] Check that pasting script payloads into the Name or Email fields on the Add or Edit Manager forms does not execute as code on the Managers list page or anywhere they are rendered.',
      '[CHK-MGR-131] Check that an Inactive Manager\'s existing session is invalidated or denied access on the next protected action.',
      '[CHK-MGR-135] Check that changing a Manager\'s status does not affect other Managers\' login access.',
      '[CHK-MGR-136] Check that an existing active Root User session remains valid after another Manager is created, edited, or deleted.',
      '[CHK-MGR-137] Check that the left-side navigation menu and role-based access for other modules remain intact after operations in the Managers module.' ] }
  ];

  // Strip any leading [CHK-...] id — the sheet shows only the check text.
  // IDs are kept in the source above purely for traceability/maintenance.
  function stripId(text) { return text.replace(/^\[CHK-[A-Z]+-\d+\]\s*/, ''); }

  var FEATURES = [
    { page: PAGE_NAME, screens: SCREENS },
    { page: 'Managers',  screens: SCREENS_MGR }
  ];
  FEATURES.forEach(function (f) {
    addPage(f.page);
    f.screens.forEach(function (screen) {
      addSection(screen.name);
      screen.checks.forEach(function (c) { item(stripId(c)); });
    });
  });

  // ── Build grid ──────────────────────────────────────────────────────
  var tz = ss.getSpreadsheetTimeZone() || Session.getScriptTimeZone();
  var monthYear = Utilities.formatDate(new Date(), tz, 'MMMM yyyy');
  var year      = Utilities.formatDate(new Date(), tz, 'yyyy');

  function er() { return new Array(NCOLS).fill(''); }
  var grid = [er(), er(), er(), er()];
  var merges = [];
  var heights = { 1: 50, 2: 59, 3: 25, 4: 36 };

  grid[0][0] = 'Module';
  grid[0][1] = 'Checklist\nUp to date according to ' + monthYear;
  grid[3][1] = 'created by ' + AUTHOR + ' =)';
  merges.push([1, 1, 4, 1]);
  merges.push([1, 2, 3, 1]);

  BLOCKS.forEach(function (b) {
    grid[0][b.s - 1]  = 'Platform';
    grid[1][b.s - 1]  = 'Web';
    grid[0][b.c1 - 1] = 'Available Statuses /\nSummary counter by all platforms';
    grid[1][b.c1 - 1] = 'Passed';
    grid[1][b.c1]     = 'Failed';
    grid[1][b.c3 - 1] = 'Skipped';
    var sL = cl(b.s);
    grid[2][b.c1 - 1] = '=COUNTIF(' + sL + ':' + sL + ';"Passed")';
    grid[2][b.c1]     = '=COUNTIF(' + sL + ':' + sL + ';"Failed")';
    grid[2][b.c3 - 1] = '=COUNTIF(' + sL + ':' + sL + ';"Skipped")';
    grid[3][b.c1 - 1] = 'Comments';
    grid[0][b.rA - 1] = 'Checked\nxx/xx/' + year;
    grid[1][b.rA - 1] = 'Total/\nCheck counter per item';
    grid[3][b.rA - 1] = 'Passed';
    grid[3][b.rB - 1] = 'Failed';
    merges.push([2, b.s, 3, 1]);
    merges.push([1, b.c1, 1, 3]);
    merges.push([4, b.c1, 1, 3]);
    merges.push([1, b.rA, 1, 2]);
    merges.push([2, b.rA, 1, 2]);
  });

  var pageLayout = [];

  PAGES.forEach(function (p) {
    var pageTop    = grid.length + 1;
    var counterRow = pageTop + 1;
    var firstCheck = pageTop + 2;
    var nTotal = p.sections.reduce(function (a, s) { return a + s.checks.length; }, 0);
    var lastCheck = firstCheck + nTotal - 1;

    var r1 = er(), r2 = er();
    r1[0] = p.name;
    BLOCKS.forEach(function (b) {
      var sL = cl(b.s), rAL = cl(b.rA);
      r1[b.s - 1]  = '=IF(COUNTIF(' + sL + firstCheck + ':' + sL + lastCheck + ';"Failed")>0;"Not all issues are resolved!";"")';
      r1[b.rA - 1] = '=A' + pageTop;
      r2[b.rA - 1] = '=COUNTIF(' + rAL + firstCheck + ':' + rAL + lastCheck + ';"Passed")';
      r2[b.rB - 1] = '=COUNTIF(' + rAL + firstCheck + ':' + rAL + lastCheck + ';"Failed")';
      merges.push([pageTop, b.s, 2, 1]);
      merges.push([pageTop, b.c1, 2, 3]);
      merges.push([pageTop, b.rA, 1, 2]);
    });
    merges.push([pageTop, 1, 2, 2]);
    heights[pageTop + 1] = 24;
    grid.push(r1, r2);

    var sectionLayouts = [];
    p.sections.forEach(function (s) {
      var sectionStart = grid.length + 1;
      s.checks.forEach(function (text) {
        var row = grid.length + 1;
        var r = er();
        r[1] = text;
        BLOCKS.forEach(function (b) {
          var sL = cl(b.s);
          r[b.rA - 1] = '=IF(COUNTIF(' + sL + row + ';"Failed")>0;"Failed";IF(COUNTIF(' + sL + row + ';"Passed")>0;"Passed";IF(COUNTIF(' + sL + row + ';"Skipped")>0;"Skipped";"")))';
          merges.push([row, b.c1, 1, 3]);
          merges.push([row, b.rA, 1, 2]);
        });
        grid.push(r);
      });
      var sectionEnd = grid.length;
      grid[sectionStart - 1][0] = s.name;
      if (sectionEnd > sectionStart) merges.push([sectionStart, 1, sectionEnd - sectionStart + 1, 1]);
      sectionLayouts.push({ start: sectionStart, end: sectionEnd });
    });

    pageLayout.push({
      pageTop: pageTop, counterRow: counterRow,
      firstCheck: firstCheck, lastCheck: lastCheck,
      sections: sectionLayouts
    });
  });

  BLOCKS.forEach(function (b) {
    var passCells = pageLayout.map(function (L) { return cl(b.rA) + L.counterRow; });
    var failCells = pageLayout.map(function (L) { return cl(b.rB) + L.counterRow; });
    grid[2][b.rA - 1] = '=SUM(' + passCells.join(';') + ')';
    grid[2][b.rB - 1] = '=SUM(' + failCells.join(';') + ')';
  });

  var LAST = grid.length;

  sheet.getRange(1, 1, LAST, NCOLS).setValues(grid);
  merges.forEach(function (m) { sheet.getRange(m[0], m[1], m[2], m[3]).merge(); });

  // ── Formatting ──────────────────────────────────────────────────────
  full.setFontFamily('Arial');

  var tealCells = ['A1', 'B1', 'B4'];
  BLOCKS.forEach(function (b) {
    tealCells.push(cl(b.s) + '1');
    tealCells.push(cl(b.c1) + '1');
    tealCells.push(cl(b.rA) + '1');
  });
  tealCells.forEach(function (a1) {
    sheet.getRange(a1).setBackground(COLORS.teal).setFontColor(COLORS.tealFg)
      .setFontWeight('bold').setFontSize(13)
      .setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
  });
  sheet.getRange('A4').setBackground(COLORS.teal);
  sheet.getRange('B4').setFontColor(COLORS.teal);

  BLOCKS.forEach(function (b) {
    sheet.getRange(2, b.s).setBackground(COLORS.blue).setFontWeight('bold').setFontSize(13)
      .setHorizontalAlignment('center').setVerticalAlignment('middle');
    sheet.getRange(2, b.rA).setBackground(COLORS.blue).setFontWeight('bold').setFontSize(11)
      .setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
    sheet.getRange(2, b.c1).setBackground(COLORS.passBg).setFontColor(COLORS.passFg).setFontWeight('bold').setFontSize(13).setHorizontalAlignment('center');
    sheet.getRange(2, b.c1 + 1).setBackground(COLORS.failBg).setFontColor(COLORS.failFg).setFontWeight('bold').setFontSize(13).setHorizontalAlignment('center');
    sheet.getRange(2, b.c3).setBackground(COLORS.gray).setFontColor(COLORS.grayFg).setFontWeight('bold').setFontSize(13).setHorizontalAlignment('center');
    sheet.getRange(3, b.c1).setBackground(COLORS.cntPass).setFontWeight('bold').setFontSize(12).setHorizontalAlignment('center');
    sheet.getRange(3, b.c1 + 1).setBackground(COLORS.cntFail).setFontWeight('bold').setFontSize(12).setHorizontalAlignment('center');
    sheet.getRange(3, b.c3).setBackground(COLORS.gray).setFontWeight('bold').setFontSize(12).setHorizontalAlignment('center');
    sheet.getRange(3, b.rA).setBackground(COLORS.cntPass).setFontWeight('bold').setFontSize(12).setHorizontalAlignment('center');
    sheet.getRange(3, b.rB).setBackground(COLORS.cntFail).setFontWeight('bold').setFontSize(12).setHorizontalAlignment('center');
    sheet.getRange(4, b.c1).setBackground(COLORS.gray).setFontWeight('bold').setFontSize(14).setHorizontalAlignment('center');
    sheet.getRange(4, b.rA).setBackground(COLORS.passBg).setFontColor(COLORS.passFg).setFontWeight('bold').setFontSize(11).setHorizontalAlignment('center');
    sheet.getRange(4, b.rB).setBackground(COLORS.failBg).setFontColor(COLORS.failFg).setFontWeight('bold').setFontSize(11).setHorizontalAlignment('center');
  });

  SPACERS.forEach(function (col) {
    sheet.getRange(1, col, LAST, 1).setBackground(COLORS.gray);
  });

  var validation = SpreadsheetApp.newDataValidation()
    .requireValueInList(['Passed', 'Failed', 'Skipped'], true)
    .setAllowInvalid(false).build();

  pageLayout.forEach(function (L, i) {
    var p = PAGES[i];

    sheet.getRange(L.pageTop, 1, 2, NCOLS).setBackground(COLORS.pageBg);
    sheet.getRange(L.pageTop, 1).setFontWeight('bold').setFontSize(13)
      .setHorizontalAlignment('left').setVerticalAlignment('middle').setWrap(true);
    BLOCKS.forEach(function (b) {
      sheet.getRange(L.pageTop, b.s).setFontWeight('bold').setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
      sheet.getRange(L.pageTop, b.rA).setFontWeight('bold').setFontSize(12)
        .setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
      sheet.getRange(L.counterRow, b.rA).setBackground(COLORS.cntPass).setFontWeight('bold').setHorizontalAlignment('center');
      sheet.getRange(L.counterRow, b.rB).setBackground(COLORS.cntFail).setFontWeight('bold').setHorizontalAlignment('center');
    });
    sheet.autoResizeRows(L.pageTop, 1);

    var n = L.lastCheck - L.firstCheck + 1;
    sheet.getRange(L.firstCheck, 1, n, 2).setBackground(COLORS.white);
    sheet.getRange(L.firstCheck, 2, n, 1).setWrap(true).setFontSize(10)
      .setVerticalAlignment('middle');
    BLOCKS.forEach(function (b) {
      sheet.getRange(L.firstCheck, b.s, n, 1).setBackground(COLORS.statusBg).setDataValidation(validation)
        .setHorizontalAlignment('center').setVerticalAlignment('middle');
      sheet.getRange(L.firstCheck, b.c1, n, 3).setBackground(COLORS.statusBg);
      sheet.getRange(L.firstCheck, b.rA, n, 2).setBackground(COLORS.resultBg)
        .setHorizontalAlignment('center').setVerticalAlignment('middle');
    });
    sheet.autoResizeRows(L.firstCheck, n);

    L.sections.forEach(function (s, idx) {
      var sn = s.end - s.start + 1;
      sheet.getRange(s.start, 1, sn, 1)
        .setFontWeight('bold').setFontSize(11)
        .setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
      sheet.getRange(s.start, 1, sn, NCOLS).shiftRowGroupDepth(1);

      var addTop = idx > 0;
      sheet.getRange(s.start, 1, sn, 1).setBorder(addTop || null, true, true, true, null, null);
      sheet.getRange(s.start, 2, sn, 1).setBorder(null, true, null, null, null, null);
      sheet.getRange(s.end, 2).setBorder(null, null, true, null, null, null);
      if (addTop) sheet.getRange(s.start, 2).setBorder(true, null, null, null, null, null);
    });
  });

  WIDTHS.forEach(function (w, i) { sheet.setColumnWidth(i + 1, w); });
  for (var r = 1; r <= LAST; r++) { if (heights[r]) sheet.setRowHeight(r, heights[r]); }
  sheet.setFrozenRows(4);
  sheet.setFrozenColumns(2);

  ['C1:G1', 'K1:O1', 'S1:W1'].forEach(function (a1) {
    sheet.getRange(a1).shiftColumnGroupDepth(1);
  });
  sheet.setColumnGroupControlAfter(true);

  function cfRanges(a1list) {
    return a1list.map(function (a1) { return sheet.getRange(a1); });
  }
  var statusRanges = cfRanges(['C1:C199', 'H1:I199', 'K1:K199', 'P1:Q199', 'S1:S199', 'X1:Y199', 'D2:F2', 'L2:N2', 'T2:V2']);
  var purpleRanges = cfRanges(['C1:C199', 'K1:K199', 'S1:S199', 'D2:F2', 'L2:N2', 'T2:V2']);
  var rules = [
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Skipped')
      .setBackground('#D9D9D9').setFontColor('#434343').setBold(true).setRanges(statusRanges).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Passed')
      .setBackground('#D2EBDA').setFontColor('#135522').setBold(true).setRanges(statusRanges).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Failed')
      .setBackground('#F8D5DA').setFontColor('#701C22').setBold(true).setRanges(statusRanges).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextContains('Not all issues are resolved!')
      .setBackground('#8E7BC3').setFontColor('#F3F3F3').setBold(true).setRanges(purpleRanges).build()
  ];
  sheet.setConditionalFormatRules(rules);

  var nSections = PAGES.reduce(function (a, p) { return a + p.sections.length; }, 0);
  var nChecks   = PAGES.reduce(function (a, p) { return a + p.sections.reduce(function (b, s) { return b + s.checks.length; }, 0); }, 0);
  Logger.log('Done: ' + PAGES.length + ' pages, ' + nSections + ' sections, ' + nChecks + ' checks, ' + LAST + ' rows.');
  Logger.log('URL: ' + ss.getUrl());
}
