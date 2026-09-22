import { expect, type Page } from '@playwright/test';
import { login } from '../../screens/authentication/login.map';
import { resolveScreen, type ScreenLocators } from '../../screens/resolve';
import { fillInput } from '../actions';

/**
 * Login page object = behaviour only. Every locator comes from the screen map through
 * resolveScreen(); nothing here knows a selector. `el.<alias>` uses the exact alias a
 * test case writes (`login.email` → `loginPage.el.email`).
 *
 * Used by auth.setup.ts (UI sign-in that produces the storageState) and by the smoke /
 * CHK-tagged login specs. Everything else authenticates by state.
 * Methods assert nothing except the `expect*` helpers, each of which names its oracle.
 */
export class LoginPage {
  readonly el: ScreenLocators<typeof login>;

  constructor(private readonly page: Page) {
    this.el = resolveScreen(page, login);
  }

  async open(): Promise<void> {
    await this.page.goto(login.route);
  }

  /** Fills both fields, submits nothing — lets a test assert button state (FR-AUTH-LG-04). */
  async fill(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
  }

  /** `fill | login.email` — one field, so a test can assert between the two fills. '' clears it. */
  async fillEmail(email: string): Promise<void> {
    await fillInput(this.el.email, email);
  }

  /** `fill | login.password` — one field. '' clears it. */
  async fillPassword(password: string): Promise<void> {
    await fillInput(this.el.password, password);
  }

  async submit(): Promise<void> {
    await this.el.submit.click();
  }

  /** fill + submit. Asserts nothing — the test states the expected outcome. */
  async signIn(email: string, password: string): Promise<void> {
    await this.fill(email, password);
    await this.submit();
  }

  /**
   * Oracle: SRS 3.1.1.2 FR-AUTH-LG-06/07 — a failed sign-in shows a server-side error
   * (e.g. "Incorrect email or password") that does not say which credential was wrong.
   * `login.error` is still a placeholder id (contract §2.5) → this fails loudly until
   * the element is observed and mapped.
   */
  async expectError(message?: string | RegExp): Promise<void> {
    await expect(this.el.error, 'oracle: SRS FR-AUTH-LG-06 — server error visible after failed sign-in').toBeVisible();
    if (message !== undefined) {
      await expect(this.el.error, 'oracle: SRS FR-AUTH-LG-06 — server-defined message').toContainText(message);
    }
  }

  /** Oracle: real page (recon 2026-09-17) + SRS 3.1.1.2 layout — the form is on screen. */
  async expectOpen(): Promise<void> {
    await expect(this.el.email, 'oracle: login form present (recon + SRS 3.1.1.2)').toBeVisible();
    await expect(this.el.submit, 'oracle: login form present (recon + SRS 3.1.1.2)').toBeVisible();
  }
}
