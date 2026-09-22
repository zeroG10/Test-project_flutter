import fs from 'node:fs';
import path from 'node:path';
import { test as base, type APIRequestContext } from '@playwright/test';
import { LoginPage } from '../pages/authentication/login.page';
import { loginByApi, newApiContext } from '../utils/api';
import { requireEnv } from '../utils/env';
import { cleanupRegistry, type Seed } from '../utils/cleanup';

export type { Seed } from '../utils/cleanup';

/*
 * Auth by state (automation/README.md → Determinism rules). UI sign-in runs ONCE per
 * role, in tests/auth.setup.ts (project `setup`); every spec in `chromium` / `firefox`
 * starts already signed in as the primary role through `storageState`. Public pages
 * (login, forgot-password, …) run in `chromium-public` / `firefox-public` with no state
 * and no dependency on setup — see playwright.config.ts.
 *
 * The state files are gitignored (automation/web/playwright/.auth/).
 */
export const AUTH_DIR = path.resolve(__dirname, '../.auth');
/** Primary role (`APP_USER_*`) — required; every authenticated project starts from it. */
export const ROOT_STATE = path.join(AUTH_DIR, 'root.json');
/** Optional second, lower-privilege role (`APP_MANAGER_*`) for permission checks. */
export const MANAGER_STATE = path.join(AUTH_DIR, 'manager.json');

/**
 * Registers the cleanup of data a test created. Every test owns its data
 * (automation/README.md → Determinism): create through the API, track the undo, and the
 * fixture removes it when the test ends — even on failure, in reverse order.
 */

/**
 * One fixture per page object. Add a line here for every page object you create
 * (automation/web/README.md → "Adding a module", step 4). Fixtures are lazy: a fixture
 * only runs when a test asks for it.
 *
 * Data fixtures — the pattern for CRUD modules:
 *
 *   test('CHK-ORD-010 …', { tag: ['@CHK-ORD-010'] }, async ({ apiContext, seed, page }) => {
 *     // POST /orders + body: docs/api/openapi.json → operationId createOrder (cite it here)
 *     const res = await apiContext.post('/orders', { data: { name: unique('qa-order') } });
 *     const order = await expectStatus<{ id: string }>(res, 201, 'POST /orders');
 *     seed.track(() => apiContext.delete(`/orders/${order.id}`), `order ${order.id}`, 204);
 *     // 204 is from this example contract; use the product's documented delete status.
 *     …the UI is what the test judges; API prepared this test's data; the assertions still exercise the UI.
 *   });
 *
 * Both fixtures are Blocked (throw, never skip) until utils/api.ts `loginByApi()` is
 * written from the product's OpenAPI spec — no token, no seeding.
 */
type Fixtures = {
  loginPage: LoginPage;
  /** API context signed in as the primary role (`APP_USER_*`) via utils/api.ts `loginByApi`. */
  apiContext: APIRequestContext;
  /** Cleanup registry for data the test created; runs LIFO at test end, even on failure. */
  seed: Seed;
};

/**
 * Project test object. Specs import { test, expect } from here — not from
 * '@playwright/test' — so every test gets the page-object fixtures.
 */
export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  // eslint-disable-next-line no-empty-pattern
  apiContext: async ({}, use) => {
    const email = requireEnv('APP_USER_EMAIL', 'primary account for login-by-API and seeding');
    const password = requireEnv('APP_USER_PASSWORD', 'primary account for login-by-API and seeding');
    const anonymous = await newApiContext();
    let token: string;
    try {
      token = await loginByApi(anonymous, email, password);
    } finally {
      await anonymous.dispose();
    }
    const context = await newApiContext(token);
    try {
      await use(context);
    } finally {
      await context.dispose();
    }
  },

  seed: async ({ apiContext }, use, testInfo) => {
    // Declare the dependency: the API context must remain open until cleanup completes.
    void apiContext;
    const registry = cleanupRegistry();
    try {
      await use(registry);
    } finally {
      try {
        await registry.finish();
      } catch (error) {
        testInfo.annotations.push({ type: 'cleanup-failed', description: String(error) });
        throw error;
      }
    }
  },
});

export { expect } from '@playwright/test';

/**
 * Run the enclosing file / describe block as the second role.
 *
 *   import { test, expect, asManager } from '../../fixtures/test-fixtures';
 *   asManager();
 *   test('CHK-<CODE>-NNN …', { tag: ['@CHK-<CODE>-NNN'] }, async ({ page }) => { … });
 *
 * The manager state is only produced by auth.setup.ts when APP_MANAGER_EMAIL /
 * APP_MANAGER_PASSWORD are set. Without it every test in the block throws
 * "Blocked: …" before a browser context is created — it never skips (a skip is
 * Blocked, not a pass; a silent primary-role run in a second-role block would be a fake result).
 */
export function asManager(): void {
  test.use({
    storageState: async ({}, use) => {
      if (!fs.existsSync(MANAGER_STATE)) {
        throw new Error(
          `Blocked: manager state missing — set APP_MANAGER_* and rerun setup (expected ${MANAGER_STATE})`,
        );
      }
      await use(MANAGER_STATE);
    },
  });
}
