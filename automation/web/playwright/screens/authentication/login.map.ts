import type { ScreenMap } from '../resolve';

/**
 * Login screen — SCAFFOLD with `<…>` placeholders. The harness needs this map before any
 * credential exists: `tests/auth.setup.ts` signs in through it once per role, and
 * `map-health` lists its placeholders as Blocked until they are curated.
 *
 * Curate it from a recon draft (`npm run pw:recon` → `scripts/recon-out/<name>/screens/`),
 * the ids owed by docs/requirements/shared/testability-contract.md and the Figma node in
 * docs/designs/web/figma-sources.md. One strategy per alias (screens/README.md:
 * role/label → test-id → text, never CSS/XPath). A placeholder never matches, so an
 * unobserved element fails loudly instead of matching something by accident.
 *
 * A fully curated version of this map — observed vs placeholder aliases, an oracle per
 * alias, the ids to request from the dev team — is in
 * examples/automation/web/screens/authentication/login.map.ts.
 *
 * Test-case steps address these as `login.email`, `login.submit`, … (same alias, no renaming).
 */
export const login = {
  id: 'login',
  route: '/<sign-in-route>',
  elements: {
    // Landmark unique to THIS screen (contract §2.3): expectOpen() and auth.setup rely on it.
    root: { testId: '<login-root>' },
    email: { testId: '<login-email>' },
    password: { testId: '<login-password>' },
    submit: { testId: '<login-submit>' },
    'forgot-password': { testId: '<login-forgot-password>' },
    // Exists only after a failed sign-in (contract §2.5). `state` tells map-health not to
    // expect it on first paint.
    error: { testId: '<login-error>', state: 'failed-sign-in' },
  },
} as const satisfies ScreenMap;
