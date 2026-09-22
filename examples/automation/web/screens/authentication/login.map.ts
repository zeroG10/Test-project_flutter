import type { ScreenMap } from '../resolve';

/**
 * Login screen — curated 2026-09-21 from the recon draft
 * `scripts/recon-out/cops-auth/screens/sign-in.map.draft.ts` (DEV, harvested 2026-09-17)
 * plus a headless pass on 2026-09-21 (invalid input, password toggle, one sign-in with a
 * non-existent account) that observed the error states.
 *
 * Oracles: SRS 3.1.1.2 "Login page" (FR-AUTH-LG-01…11); Figma 31:19824 (design wins over
 * SRS on conflict); the real page wins over both for what exists today.
 * `/` and `/sign-in` render the same form; `/sign-in` is canonical (the app's own
 * "Back to Login" link targets it).
 *
 * No `data-testid` has shipped yet (gaps.md: no `sign-in-root`, eye icon is `role=img`).
 * Role + accessible name is the strongest locator available today; the testability
 * contract (§1, §2.3, §2.5, §2.7) still requires ids — the `<…>` placeholders below are
 * exactly the ids to request. A placeholder never matches, so an unobserved element
 * fails loudly instead of matching something by accident (screens/README.md).
 */
export const login = {
  id: 'login',
  route: '/sign-in',
  elements: {
    // observed — unique (role+name)
    email: { role: 'textbox', name: 'Email *', exact: true },
    password: { role: 'textbox', name: 'Password *', exact: true },
    // observed: img "eye-invisible" while masked, "eye" once revealed (Ant Design
    // Input.Password) — matched as either. WEAK: clickable icon exposed as role=img,
    // tabindex=-1, no id (gaps.md, contract §2.7).
    'password-toggle': { role: 'img', name: /^eye(-invisible)?$/ },
    // observed — checked by default (SRS FR-AUTH-LG-08 "Remember me")
    'remember-me': { role: 'checkbox', name: 'Remember me', exact: true },
    // observed — link → /forgot-password
    'forgot-password': { role: 'link', name: 'Forgot password?', exact: true },
    // observed — disabled until the email has a valid format AND the password passes the
    // 12-character rule (FR-AUTH-LG-04 says "not empty"; the real page is stricter).
    submit: { role: 'button', name: 'Log in', exact: true },
    // observed — server-side error is an Ant Design alert (role=alert, .ant-alert-error)
    // above the form with the copy "Incorrect email or password" and a close button
    // (SRS FR-AUTH-LG-06/07; checklist CHK-AUTH-018 calls it a modal — it is a banner).
    // Unique: the page has one alert. Contract §2.5 still wants `login-error`.
    error: { role: 'alert', state: 'failed-sign-in' },
    // observed — inline validation under the field (.ant-form-item-explain-error, no role,
    // no id; the input gets aria-invalid=true). WEAK: by copy, and only for the format
    // rule seen so far. Fix = data-testid="login-email-error" (contract §2.5).
    'email-error': { text: 'Invalid email', exact: true, state: 'invalid-email' },
    // observed for the length rule (SRS FR-AUTH-LG-04 / CHK-AUTH-010). WEAK, by copy;
    // other password rules may carry other copy. Fix = data-testid="login-password-error".
    'password-error': { text: /^Password must be at least 12 characters/, state: 'short-password' },

    // --- added 2026-09-21 (prompt 07, headless pass on DEV) for TC-AUTH-001/002/005/006 ---
    // observed 2026-09-21 — the screen has no landmark of its own: `<form id="signInEmail">`
    // carries no accessible name (so no role=form), there is no heading, and `main` is the
    // same element on every public page. The only anchor unique to THIS screen is its title
    // copy, so `root` points there until `login-root` ships (contract §2.3, gaps.md).
    // weak: by copy — a title change reads as "not on Login".
    root: { text: 'Log in using your credentials', exact: true },
    // observed 2026-09-21 — <strong>, unique (CHK-AUTH-001)
    title: { text: 'Log in using your credentials', exact: true },
    // observed 2026-09-21 — <img alt="Triare">, unique (CHK-AUTH-002; alt is the vendor's name, Q-21)
    logo: { role: 'img', name: 'Triare', exact: true },
    // observed 2026-09-21 — <label> copy; the asterisk is the only "required" marking
    // (no `required` attribute on the inputs) — CHK-AUTH-003/004
    'email-label': { text: 'Email *', exact: true },
    'password-label': { text: 'Password *', exact: true },
    // observed 2026-09-21 — state aliases for TC-AUTH-005: the icon's accessible name is
    // "eye-invisible" while the input is type=password and "eye" once it is type=text;
    // exactly one of the two exists at any time. weak: role=img, no id (contract §2.7) —
    // the same gap as `password-toggle`; fix = data-testid="login-password-toggle" + aria-pressed.
    'password-toggle-masked': { role: 'img', name: 'eye-invisible', exact: true },
    'password-toggle-revealed': { role: 'img', name: 'eye', exact: true, state: 'password-revealed' },
  },
} as const satisfies ScreenMap;
