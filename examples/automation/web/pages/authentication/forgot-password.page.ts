import { expect, type Page } from '@playwright/test';
import { forgotPassword } from '../../screens/authentication/forgot-password.map';
import { resolveScreen, type ScreenLocators } from '../../screens/resolve';
import { fillInput } from '../actions';

/** Forgot-password page object — behaviour only, locators via the screen map. */
export class ForgotPasswordPage {
  readonly el: ScreenLocators<typeof forgotPassword>;

  constructor(private readonly page: Page) {
    this.el = resolveScreen(page, forgotPassword);
  }

  async open(): Promise<void> {
    await this.page.goto(forgotPassword.route);
  }

  /** `fill | forgot-password.email` — one field, submits nothing. '' clears it. */
  async fillEmail(email: string): Promise<void> {
    await fillInput(this.el.email, email);
  }

  /** Enter the email and submit. Asserts nothing. */
  async requestReset(email: string): Promise<void> {
    await this.fillEmail(email);
    await this.el.submit.click();
  }

  /**
   * Oracle: SRS 3.1.1.3 "Success State" + FR-AUTH-FP-05 — after submission the form is
   * replaced by "Please check your email. If an account is associated with this address,
   * we've sent a reset link." `forgot-password.success` is a placeholder id until observed.
   */
  async expectSuccess(): Promise<void> {
    await expect(this.el.success, 'oracle: SRS FR-AUTH-FP-05 — confirmation shown after request').toBeVisible();
  }

  /**
   * Oracle: SRS 3.1.1.3 FR-AUTH-FP-02 (inline email-format error, checklist CHK-AUTH-031
   * "Please enter a valid email address") for `field: 'email'`; FR-AUTH-FP-07 (generic
   * service error) for the page-level error. Both ids are placeholders until observed.
   */
  async expectError(message?: string | RegExp, field?: 'email'): Promise<void> {
    const target = field === 'email' ? this.el['email-error'] : this.el.error;
    const oracle = field === 'email' ? 'SRS FR-AUTH-FP-02 — inline email error' : 'SRS FR-AUTH-FP-07 — request error visible';
    await expect(target, `oracle: ${oracle}`).toBeVisible();
    if (message !== undefined) await expect(target, `oracle: ${oracle}`).toContainText(message);
  }
}
