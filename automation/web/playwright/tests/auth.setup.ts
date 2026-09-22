import fs from 'node:fs';
import type { Page } from '@playwright/test';
import { test as setup, expect, AUTH_DIR, ROOT_STATE, MANAGER_STATE } from '../fixtures/test-fixtures';
import { LoginPage } from '../pages/authentication/login.page';
import { login } from '../screens/authentication/login.map';
import { isPlaceholder } from '../screens/resolve';
import { requireEnv } from '../utils/env';

/*
 * Project `setup` (playwright.config.ts): signs in through the UI once per role and
 * saves the browser state that the authenticated projects reuse.
 *
 *   Primary role — required. APP_USER_EMAIL / APP_USER_PASSWORD → .auth/root.json
 *   Second role  — optional. APP_MANAGER_EMAIL / APP_MANAGER_PASSWORD → .auth/manager.json;
 *                  when unset the file is NOT created (and a stale one is removed), and every
 *                  spec that calls asManager() fails with "Blocked: manager state missing".
 *
 * A missing credential throws naming the variable — never test.skip(): a skip is
 * Blocked, not a pass (CLAUDE.md doctrine rule 3). Credentials come from
 * automation/web/.env (dotenv, loaded by the config) or the shell; never from code.
 *
 * Success oracle: after sign-in the URL has left the login route AND the login landmark
 * is gone. That is the weakest honest oracle, not the final one — once the landing page is
 * observed, assert its own landmark here and cite the SRS section / Figma node.
 */

/** Aliases a sign-in needs. `error` and the like may stay placeholders; these may not. */
const SIGN_IN_ALIASES = ['root', 'email', 'password', 'submit'] as const;

/** A scaffold map cannot sign anyone in — say so before a browser is opened. */
function requireCuratedLoginMap(): void {
  const owed = SIGN_IN_ALIASES.filter((alias) => isPlaceholder(login.elements[alias]));
  if (login.route.includes('<') || owed.length > 0) {
    throw new Error(
      `Blocked: screens/authentication/login.map.ts is still a scaffold (route '${login.route}'` +
        `${owed.length ? `, placeholder aliases: ${owed.join(', ')}` : ''}). ` +
        'Curate it from a recon draft before running the setup project (screens/README.md).',
    );
  }
}

const escapeRegExp = (s: string): string => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

async function signInAndSave(
  page: Page,
  role: string,
  email: string,
  password: string,
  file: string,
): Promise<void> {
  requireCuratedLoginMap();
  const loginPage = new LoginPage(page);
  await loginPage.open();
  await loginPage.expectOpen();
  await loginPage.signIn(email, password);

  const loginRoute = new RegExp(`${escapeRegExp(login.route)}(\\/|\\?|$)`);
  await expect(page, `oracle: after ${role} sign-in the URL leaves ${login.route}`).not.toHaveURL(loginRoute);
  await expect(loginPage.el.root, `oracle: login landmark gone after ${role} sign-in`).toBeHidden();
  // TODO(product): replace with the landing-page landmark once observed (cite SRS / Figma).

  fs.mkdirSync(AUTH_DIR, { recursive: true });
  await page.context().storageState({ path: file });
}

setup('Primary sign-in → .auth/root.json (APP_USER_EMAIL / APP_USER_PASSWORD)', async ({ page }) => {
  const email = requireEnv('APP_USER_EMAIL', 'primary account used for the authenticated projects');
  const password = requireEnv('APP_USER_PASSWORD', 'primary account used for the authenticated projects');
  await signInAndSave(page, 'primary role', email, password, ROOT_STATE);
});

setup('Second-role sign-in → .auth/manager.json (optional: APP_MANAGER_EMAIL / APP_MANAGER_PASSWORD)', async ({ page }) => {
  const email = process.env.APP_MANAGER_EMAIL;
  const password = process.env.APP_MANAGER_PASSWORD;

  if (!email && !password) {
    if (fs.existsSync(MANAGER_STATE)) fs.rmSync(MANAGER_STATE);
    const note = 'manager state NOT created: APP_MANAGER_EMAIL / APP_MANAGER_PASSWORD are unset — ' +
      'specs using asManager() will fail with "Blocked: manager state missing"';
    console.log(`[auth.setup] ${note}`);
    setup.info().annotations.push({ type: 'manager-state', description: note });
    return;
  }
  // Half-configured is a configuration error, not "optional": say which half.
  const e = requireEnv('APP_MANAGER_EMAIL', 'second-role account (both APP_MANAGER_* vars or neither)');
  const p = requireEnv('APP_MANAGER_PASSWORD', 'second-role account (both APP_MANAGER_* vars or neither)');
  await signInAndSave(page, 'second role', e, p, MANAGER_STATE);
});
