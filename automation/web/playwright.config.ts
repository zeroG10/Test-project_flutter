import path from 'node:path';
import { defineConfig, devices } from '@playwright/test';
import { config as loadEnv } from 'dotenv';

// Local runs read automation/web/.env (gitignored — copy .env.example). CI sets
// BASE_URL directly from the WEB_BASE_URL repository variable. dotenv never
// overrides an already-exported variable, so `BASE_URL=… npm run pw:test` wins.
loadEnv({ path: path.resolve(__dirname, '.env'), quiet: true });

// Fail closed. A run with no target would "pass" against nothing or against a
// placeholder site — an empty run that reads as green (doctrine rule 3).
const baseURL = process.env.BASE_URL;
if (!baseURL) {
  throw new Error(
    'BASE_URL is not set — copy automation/web/.env.example to .env or export it. ' +
      'A run without a target is Blocked, not green.',
  );
}
// A left-over `<https://…>` placeholder is the same problem with a worse error
// message (Playwright would try to navigate to the literal path). Refuse it here.
try {
  new URL(baseURL);
} catch {
  throw new Error(`BASE_URL is not a valid URL: '${baseURL}' — replace the <…> placeholder with the real target.`);
}

// Auth by state: the `setup` project writes these, the browser projects read them.
// Absolute on purpose — `npm run pw:*` runs from the repo root with --config, and a
// relative storageState would resolve against the cwd, not this file.
const ROOT_STATE = path.resolve(__dirname, 'playwright/.auth/root.json');
// Specs for pages reachable without a session (login, forgot-password, smoke) end in
// `.public.spec.ts` and run only in the *-public projects.
const PUBLIC_SPEC = /.*\.public\.spec\.ts/;

export default defineConfig({
  testDir: './playwright/tests',
  // Budgets, not waits: every assertion polls, so a passing test still finishes as fast as
  // the app allows. Tune them to the target environment once observed (a slow bundle, a
  // rate-limited dev proxy) and record the observation in docs/environments.md — never
  // compensate with retries (retries stay 0 by policy, .github/GATES.md rule 3).
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  // Shared dev environments often misbehave under parallel browsers (rate limits, shared
  // data). Serial in CI by default; raise `workers` once the environment is known to cope.
  workers: process.env.CI ? 1 : undefined,
  fullyParallel: false,
  // A stray test.only would silently shrink the suite to one test — an "empty run"
  // that reads as green. Refuse it in CI.
  forbidOnly: !!process.env.CI,
  retries: 0,
  // Artifacts (traces, screenshots, videos) land here. Must match the path the
  // CI workflow uploads.
  outputDir: './playwright/test-results',
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright/playwright-report', open: 'never' }],
    // Machine-readable run output: automation/tools/trace_results.py reads it,
    // extracts @CHK-… tags and writes the automated verdict per checklist item.
    ['json', { outputFile: 'playwright/test-results/results.json' }],
  ],
  use: {
    baseURL,
    navigationTimeout: 30_000,
    actionTimeout: 15_000,
    // NOT 'on-first-retry': retries are 0 by policy (GATES.md rule 3), so that
    // setting would never capture anything.
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    // 1. UI sign-in once per role → playwright/.auth/*.json (tests/auth.setup.ts).
    //    Primary role is required (APP_USER_*), the second role optional (APP_MANAGER_*).
    //    Runs on Chromium only: the state is cookies + localStorage, browser-neutral.
    {
      name: 'setup',
      testMatch: '**/*.setup.ts',
      use: { ...devices['Desktop Chrome'] },
    },
    // 2. Gate browsers — match the browsers the product's SRS names (Edge is Chromium) and
    //    record the choice in docs/notes/decisions.md. Start signed in as the primary role;
    //    skip the public specs, which have their own projects below.
    {
      name: 'chromium',
      dependencies: ['setup'],
      testIgnore: PUBLIC_SPEC,
      use: { ...devices['Desktop Chrome'], storageState: ROOT_STATE },
    },
    {
      name: 'firefox',
      dependencies: ['setup'],
      testIgnore: PUBLIC_SPEC,
      use: { ...devices['Desktop Firefox'], storageState: ROOT_STATE },
    },
    // 3. Public pages (login, forgot-password, smoke): no storageState and no dependency
    //    on setup, so they run before any credential exists.
    {
      name: 'chromium-public',
      testMatch: PUBLIC_SPEC,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox-public',
      testMatch: PUBLIC_SPEC,
      use: { ...devices['Desktop Firefox'] },
    },
    // 4. WebKit is OUTSIDE the gate by default. Move it into the gate (and the CI matrix)
    //    when the SRS names Safari. Kept for optional runs: --project=webkit
    {
      name: 'webkit',
      dependencies: ['setup'],
      testIgnore: PUBLIC_SPEC,
      use: { ...devices['Desktop Safari'], storageState: ROOT_STATE },
    },
    // 5. Screen-map health (playwright/screens/map-health.spec.ts): every curated alias
    //    still resolves to exactly one element. Lives next to the maps, so it is its own
    //    project like `visual`. Chromium only — accessible names are browser-neutral and
    //    the gate browsers cover the functional differences. Signed-in maps use the primary
    //    state (hence `setup`); public maps override it with a clean context in the spec.
    //    Run alone: npm run pw:map-health
    {
      name: 'map-health',
      testDir: './playwright/screens',
      testMatch: '**/map-health.spec.ts',
      dependencies: ['setup'],
      use: { ...devices['Desktop Chrome'], storageState: ROOT_STATE },
    },
    // Optional module `visual_regression`. Lives outside the default testDir on
    // purpose: it is a separate discipline with its own baseline governance
    // (see playwright/visual/README.md) and is NOT part of gate G-1.
    // Run it explicitly: npx playwright test --project=visual
    // If the module is disabled, delete this entry together with the folder.
    {
      name: 'visual',
      testDir: './playwright/visual',
      use: { ...devices['Desktop Chrome'], deviceScaleFactor: 1 },
    },
  ],
});
