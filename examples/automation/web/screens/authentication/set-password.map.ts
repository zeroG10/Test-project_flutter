import type { ScreenMap } from '../resolve';

/**
 * Set-password screen — PLACEHOLDER map. The page is reachable only through the
 * single-use link emailed after a Root creates a user (SRS 3.1.1.1) or after a
 * forgot-password request (3.1.1.3, FR-AUTH-FP-06); recon has not reached it.
 * Every entry is a `<…>` placeholder and fails loudly until observed — fill it from a
 * real emailed link (utils/mailbox.ts → SetPasswordPage.openFromLink) and re-run recon
 * with that URL as `--start`.
 *
 * Oracles: SRS 3.1.1.1 "Set password page" (FR-AUTH-SP-01…10); Figma 31:20046.
 * Route: the SPA route table (bundle) registers `reset-password/:secretKey`, and
 * `POST /auth/reset-password` takes `{ secretKey, password }` (docs/api/openapi.json,
 * ResetPasswordDto) — so `route` is a pattern, never navigated to directly.
 * Copy known from SRS + bundle: button "Set password"; hint "Password must be longer
 * than 12 characters, contain at least 1 digit, 1 letter, and either 1 special symbol
 * or 1 uppercase letter."
 */
export const setPassword = {
  id: 'set-password',
  route: '/reset-password/:secretKey',
  elements: {
    password: { testId: '<set-password-password>' },
    'confirm-password': { testId: '<set-password-confirm-password>' },
    // expected: { role: 'button', name: 'Set password', exact: true } — unobserved, kept as placeholder
    submit: { role: 'button', name: '<Set password>', exact: true },
    // FR-AUTH-SP-02 (invalid/expired token) and FR-AUTH-SP-09 (server error). Contract §2.5.
    error: { testId: '<set-password-error>', state: 'invalid-token-or-server-error' },
    // FR-AUTH-SP-08: on success the app redirects to Login (or auto-logs in). If a
    // confirmation message exists it needs this id; otherwise the oracle is the redirect.
    success: { testId: '<set-password-success>', state: 'password-set' },
  },
} as const satisfies ScreenMap;
