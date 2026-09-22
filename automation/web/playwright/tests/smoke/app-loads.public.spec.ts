import { test, expect } from '../../fixtures/test-fixtures';

// Harness health, NOT feature coverage. Runs in the *-public projects (no storageState,
// no dependency on setup) so it works before any credential exists. This proves the target answers and the
// config/browsers are wired; it closes no checklist item. Feature tests carry the
// [CHK-…] IDs they prove as tags — test('CHK-AUTH-001 …', { tag: ['@CHK-AUTH-001'] }, …)
// per automation/README.md — and that is what trace_results.py reads.
test('App loads: GET / answers below 400 and the page has a title', { tag: ['@smoke'] }, async ({ page }) => {
  const response = await page.goto('/');

  // goto() returns null only for same-document navigations; '/' is a real request,
  // so a null response is a harness defect, not something to pass over.
  expect(response, 'no HTTP response for GET /').not.toBeNull();
  expect(response!.status(), `GET / returned HTTP ${response!.status()}`).toBeLessThan(400);
  await expect(page, 'document <title> is empty').toHaveTitle(/\S/);
});
