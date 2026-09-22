import type { Locator, Page } from '@playwright/test';

/**
 * Shared low-level actions for page objects. Locators still come from the screen maps;
 * this file only knows HOW the app's widgets need to be driven. `fillInput` is generic;
 * the Select / form-item helpers below are documented workarounds for Ant Design widgets
 * (a common base for admin panels) — delete them if the product uses another UI kit, and
 * add the equivalent for that kit here, never inline in a test.
 */

/**
 * Type into an input that may be `readonly` until focused (an anti-autofill pattern seen
 * on Ant Design login forms: the attribute is dropped on focus). Playwright's fill()
 * waits for an editable element BEFORE focusing, so on such a field it times out.
 * click() first lifts the attribute; then fill() behaves normally. Harmless on inputs
 * that are editable from the start.
 */
export async function fillInput(input: Locator, value: string): Promise<void> {
  await input.click();
  await input.fill(value);
}

/**
 * Choose a value in a customised Ant Design Select. Three of its details defeat the usual
 * approach (all observed on a real project):
 *
 *  1. the input is `readonly`, so there is no type-to-search;
 *  2. `getByRole('option', …)` resolves to a **zero-width, unclickable** element in the
 *     widget's accessibility layer, whose text is the raw value while its `aria-label`
 *     is the display label — clicking it times out, and a screen reader announces the
 *     wrong word. When you see this, record it as an accessibility defect against
 *     `docs/requirements/shared/testability-contract.md`;
 *  3. the clickable item is `.ant-select-item-option[title="<label>"]`, and the chosen
 *     value lands in `.ant-select-content-value`, not the standard `-selection-item`.
 *
 * The CSS below is deliberate and confined to this function: it drives a third-party
 * widget, it is not a screen locator. Screen maps stay CSS-free — they address the
 * combobox by role and name, and this helper opens it and picks inside it. When the dev
 * team ships ids for the options, this collapses to a `getByTestId`.
 */
export async function selectOption(combo: Locator, optionLabel: string): Promise<void> {
  const page = combo.page();
  await openSelect(combo);
  // Ant keeps closed dropdowns mounted and marks them `-hidden`; the newest one is last.
  const dropdown = page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden)').last();
  await dropdown.waitFor({ state: 'visible' });
  await dropdown.locator(`.ant-select-item-option[title=${JSON.stringify(optionLabel)}]`).click();
  await dropdown.waitFor({ state: 'hidden' });
}

/**
 * Open a Select. The combobox Playwright finds is an inner `<input>`; the element that
 * actually receives the click is the `.ant-select-selector` wrapper around it. Clicking
 * the input directly is intercepted by whatever sits above it in the layout (observed on
 * the page-size selector, where a table cell's text swallows the click), so the wrapper is
 * the right target — and it is what a user clicks.
 */
async function openSelect(combo: Locator): Promise<void> {
  const page = combo.page();
  await combo.waitFor({ state: 'attached' });
  const wrapper = combo.locator('xpath=ancestor-or-self::*[contains(@class,"ant-select")][1]');
  const target = (await wrapper.count()) > 0 ? wrapper.first() : combo;
  await target.scrollIntoViewIfNeeded();
  try {
    await target.click({ timeout: 8_000 });
  } catch {
    // Something above it swallowed the click (a table cell overlaps the page-size selector
    // at the bottom of the list). The widget is there and a user can reach it by scrolling.
    await target.click({ force: true });
  }
  await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden)').last().waitFor({ state: 'visible' });
}

/**
 * The label currently shown by such a Select, or null when nothing is chosen. Reads the
 * widget's own value node (see selectOption) rather than the input, which stays empty.
 */
export async function selectedOption(combo: Locator): Promise<string | null> {
  return combo.evaluate((el) => el.closest('.ant-select')?.querySelector('.ant-select-content-value')?.getAttribute('title') ?? null);
}

/**
 * The options a Select offers, by their visible labels, with the dropdown left closed.
 * Used by the checks that pin down an allowed value set (e.g. a Role dropdown).
 */
export async function optionLabels(combo: Locator): Promise<string[]> {
  const page = combo.page();
  await openSelect(combo);
  const dropdown = page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden)').last();
  await dropdown.waitFor({ state: 'visible' });
  const labels = await dropdown.locator('.ant-select-item-option').evaluateAll((els) => els.map((e) => e.getAttribute('title') ?? (e as HTMLElement).innerText.trim()));
  await page.keyboard.press('Escape');
  await dropdown.waitFor({ state: 'hidden' });
  return labels;
}

/**
 * The value of a form control that has no accessible name and no id, found through the
 * label of its Ant Design form item — typically disabled, display-only boxes such as
 * "Created at" that ship with neither (recorded in the recon `gaps.md`).
 *
 * Like selectOption, this is a documented workaround for a missing id, confined to one
 * place: the screen map keeps `<…>` placeholders for those aliases so the gap stays
 * visible, and both collapse to `getByTestId` the day the ids ship
 * (docs/requirements/shared/testability-contract.md §2.5).
 */
export async function fieldValueByLabel(page: Page, label: string): Promise<string | null> {
  const item = page.locator('.ant-form-item').filter({ has: page.locator(`label:text-is(${JSON.stringify(label)})`) });
  const input = item.locator('input');
  if ((await input.count()) === 0) return null;
  return input.first().inputValue();
}

/** Whether that same control is disabled — the "read-only" half of the checks above. */
export async function fieldDisabledByLabel(page: Page, label: string): Promise<boolean> {
  const item = page.locator('.ant-form-item').filter({ has: page.locator(`label:text-is(${JSON.stringify(label)})`) });
  return item.locator('input').first().isDisabled();
}
