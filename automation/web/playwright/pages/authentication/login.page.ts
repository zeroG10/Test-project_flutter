import { expect, type Page } from '@playwright/test';
import { login } from '../../screens/authentication/login.map';
import { resolveScreen, type ScreenLocators } from '../../screens/resolve';
import { fillInput } from '../actions';

/**
 * Login page object = behaviour only. Every locator comes from the screen map through
 * resolveScreen(); nothing here knows a selector. `el.<alias>` uses the exact alias a
 * test case writes (`login.email` → `loginPage.el.email`).
 *
 * Used by tests/auth.setup.ts (UI sign-in that produces the storageState) and by the
 * CHK-tagged login specs. Everything else authenticates by state.
 * Methods assert nothing except the `expect*` helpers, each of which names its oracle —
 * replace the `<oracle>` placeholders with the SRS section / Figma node of your product
 * (a fully cited version is in examples/automation/web/pages/authentication/).
 */
export class LoginPage {
  readonly el: ScreenLocators<typeof login>;

  constructor(private readonly page: Page) {
    this.el = resolveScreen(page, login);
  }

  async open(): Promise<void> {
    await this.page.goto(login.route);
  }

  /** `fill | login.email` — one field, so a test can assert between the two fills. '' clears it. */
  async fillEmail(email: string): Promise<void> {
    await fillInput(this.el.email, email);
  }

  /** `fill | login.password` — one field. '' clears it. */
  async fillPassword(password: string): Promise<void> {
    await fillInput(this.el.password, password);
  }

  /** Fills both fields, submits nothing — lets a test assert the button state first. */
  async fill(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
  }

  async submit(): Promise<void> {
    await this.el.submit.click();
  }

  /** fill + submit. Asserts nothing — the test states the expected outcome. */
  async signIn(email: string, password: string): Promise<void> {
    await this.fill(email, password);
    await this.submit();
  }

  /** Oracle: `<SRS §… / Figma node …>` — the login screen is on screen. */
  async expectOpen(): Promise<void> {
    await expect(this.el.root, 'oracle: <SRS §… / Figma node …> — login screen landmark present').toBeVisible();
    await expect(this.el.submit, 'oracle: <SRS §…> — login form present').toBeVisible();
  }

  /**
   * Oracle: `<SRS §…>` — a failed sign-in shows a server-side error that does not say
   * which credential was wrong. `login.error` is a `state` alias: it exists only after
   * the failed submit.
   */
  async expectError(message?: string | RegExp): Promise<void> {
    await expect(this.el.error, 'oracle: <SRS §…> — server error visible after failed sign-in').toBeVisible();
    if (message !== undefined) {
      await expect(this.el.error, 'oracle: <SRS §…> — server-defined message').toContainText(message);
    }
  }
}
