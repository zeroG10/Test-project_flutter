import type { ScreenMap } from '../resolve';

/**
 * Forgot-password screen — curated 2026-09-21 from the recon draft
 * `scripts/recon-out/cops-auth/screens/forgot-password.map.draft.ts` (DEV, 2026-09-17)
 * plus a headless pass on 2026-09-21 (invalid input, one request for a non-existent
 * account) that observed the error states.
 *
 * Oracles: SRS 3.1.1.3 "Forgot password page" (FR-AUTH-FP-01…08); Figma 31:19987;
 * the real page for what exists today. No `data-testid` shipped (gaps.md: no
 * `forgot-password-root`).
 */
export const forgotPassword = {
  id: 'forgot-password',
  route: '/forgot-password',
  elements: {
    // observed — unique (role+name); note the label has no "*" unlike the login screen
    email: { role: 'textbox', name: 'Email', exact: true },
    // observed — disabled until a valid email is entered (FR-AUTH-FP-03)
    submit: { role: 'button', name: 'Request password reset', exact: true },
    // observed — a link (→ /sign-in) wrapping a button; the accessible name is
    // "left Back to Login" because the arrow icon's aria-label leaks into it.
    // Non-exact match on the visible copy keeps the locator valid if the icon changes.
    'back-to-login': { role: 'link', name: 'Back to Login' },
    // NOT observed yet (needs an existing account). SRS success state replaces the form
    // with "Please check your email. If an account is associated with this address, we've
    // sent a reset link." — copy "Please check your email" exists in the SPA bundle.
    // Contract §2.5: `forgot-password-success` (a message must be locatable to be asserted).
    success: { testId: '<forgot-password-success>', state: 'request-sent' },
    // observed — inline validation "Invalid email" (.ant-form-item-explain-error, no role,
    // no id). WEAK, by copy. Checklist CHK-AUTH-031 expects "Please enter a valid email
    // address" — the real copy differs (checklist defect, not an app bug).
    // Fix = data-testid="forgot-password-email-error" (contract §2.5).
    'email-error': { text: 'Invalid email', exact: true, state: 'invalid-email' },
    // observed — Ant Design alert (role=alert) above the form. For an unknown email the
    // API answers 404 and the UI shows "User is not found": the UI enumerates accounts,
    // contradicting SRS FR-AUTH-FP-05/08 → question for authentication-questions.md, not
    // a map choice. Unique: one alert on the page.
    error: { role: 'alert', state: 'request-failed' },

    // --- added 2026-09-21 (prompt 07, headless pass on DEV) for TC-AUTH-002/010 ---
    // observed 2026-09-21 — no landmark of its own (unnamed <form>, no heading; `main` is
    // shared with Login), so `root` is anchored on the title copy, unique to this screen,
    // until `forgot-password-root` ships (contract §2.3, gaps.md). weak: by copy.
    root: { text: 'Forgot your password?', exact: true },
    // observed 2026-09-21 — <strong>, unique (CHK-AUTH-025)
    title: { text: 'Forgot your password?', exact: true },
    // observed 2026-09-21 — <img alt="Triare">, unique
    logo: { role: 'img', name: 'Triare', exact: true },
    // observed 2026-09-21 — <div class="ant-typography">, unique; straight apostrophe in
    // "we'll". The SRS instruction text speaks of a "verification code" (Q-01) — the real
    // page says "link" and wins for what exists today.
    description: {
      text: "Please enter the email address associated with your account, and we'll send you a link to reset your password.",
      exact: true,
    },
    // observed 2026-09-21 — <label> "Email", no asterisk (CHK-AUTH-026 "marked as required" — Q-20)
    'email-label': { text: 'Email', exact: true },
  },
} as const satisfies ScreenMap;
