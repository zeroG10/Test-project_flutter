import { expect, type Page } from '@playwright/test';
import { setPassword } from '../../screens/authentication/set-password.map';
import { resolveScreen, type ScreenLocators } from '../../screens/resolve';
import { fillInput } from '../actions';

/**
 * Set-password page object. The page has no direct route: it opens from the single-use
 * link in the activation / reset email (SRS 3.1.1.1, FR-AUTH-FP-06), so `openFromLink`
 * takes the absolute URL extracted by utils/mailbox.ts → extractLink().
 * The whole map is placeholders until the page is observed (see set-password.map.ts).
 */
export class SetPasswordPage {
  readonly el: ScreenLocators<typeof setPassword>;

  constructor(private readonly page: Page) {
    this.el = resolveScreen(page, setPassword);
  }

  /** Navigate to the emailed link as-is (absolute URL, includes the secret key). */
  async openFromLink(url: string): Promise<void> {
    if (!/^https?:\/\//.test(url)) {
      throw new Error(`SetPasswordPage.openFromLink expects the absolute URL from the email, got '${url}'`);
    }
    await this.page.goto(url);
  }

  /** Fill both fields and submit. `confirm` defaults to `password` (the happy path). */
  async setPassword(password: string, confirm: string = password): Promise<void> {
    await fillInput(this.el.password, password);
    await fillInput(this.el['confirm-password'], confirm);
    await this.el.submit.click();
  }

  /** Oracle: SRS FR-AUTH-SP-02 (invalid/expired token) or FR-AUTH-SP-09 (server error). */
  async expectError(message?: string | RegExp): Promise<void> {
    await expect(this.el.error, 'oracle: SRS FR-AUTH-SP-02/09 — error shown').toBeVisible();
    if (message !== undefined) await expect(this.el.error, 'oracle: SRS FR-AUTH-SP-02/09').toContainText(message);
  }

  /**
   * Oracle: SRS FR-AUTH-SP-08 — after a successful submission the user is redirected to
   * the Login page (URL leaves `/reset-password/…`). A success message, if the app shows
   * one, is `set-password.success` — kept separate so a redirect-only app still passes.
   */
  async expectRedirectedToLogin(): Promise<void> {
    await expect(this.page, 'oracle: SRS FR-AUTH-SP-08 — redirect to Login after set password').toHaveURL(/\/sign-in(\/|\?|$)/);
  }
}
