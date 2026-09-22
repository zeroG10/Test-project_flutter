import type { Locator, Page } from '@playwright/test';

/**
 * Presence note shared by every strategy. `state` marks an element that only exists
 * after the named state is reached (an error alert, a revealed password, a success
 * message); `map-health.spec.ts` does not expect it on first paint. An element
 * without `state` must be present — and unique — as soon as the screen is open.
 */
type Presence = { state?: string };

/** One screen-map element. Exactly one strategy per element (+ optional `state`). */
export type ElementSpec = (
  | { testId: string }
  | { role: Parameters<Page['getByRole']>[0]; name?: string | RegExp; exact?: boolean }
  | { label: string | RegExp; exact?: boolean }
  | { text: string | RegExp; exact?: boolean }
) &
  Presence;

/** Shape every `<screen>.map.ts` must satisfy (see README.md in this folder). */
export type ScreenMap = {
  readonly id: string;
  readonly route: string;
  readonly elements: Readonly<Record<string, ElementSpec>>;
};

/**
 * Resolve a screen-map element to a Locator. The map is the ONLY place a locator
 * lives (automation/README.md): page objects and generated tests call this instead
 * of writing selectors. Priority follows the doctrine — role/label → test-id → text.
 * No CSS, no XPath: a missing id is a testability defect, not a reason to reach for
 * a structural selector.
 */
export function locate(page: Page, el: ElementSpec): Locator {
  if ('testId' in el) return page.getByTestId(el.testId);
  if ('role' in el) return page.getByRole(el.role, { name: el.name, exact: el.exact });
  if ('label' in el) return page.getByLabel(el.label, { exact: el.exact });
  if ('text' in el) return page.getByText(el.text, { exact: el.exact });
  // Exhaustiveness guard: a new strategy is added HERE, never inlined in a test.
  const unreachable: never = el;
  throw new Error(`Unknown element spec: ${JSON.stringify(unreachable)}`);
}

/** Every alias of a screen map resolved to a Locator, keyed by the alias itself. */
export type ScreenLocators<M extends ScreenMap> = { readonly [K in keyof M['elements']]: Locator };

/**
 * Resolve a whole screen map at once. Locators are lazy, so this costs nothing until
 * a test touches one. Page objects expose the result as `el`, so a test-case step
 * `expect-visible | login.email` reads as `loginPage.el.email` — same alias, no renaming
 * layer in between.
 */
export function resolveScreen<M extends ScreenMap>(page: Page, map: M): ScreenLocators<M> {
  const out: Record<string, Locator> = {};
  for (const [alias, spec] of Object.entries(map.elements)) out[alias] = locate(page, spec);
  return out as ScreenLocators<M>;
}

/** The value a strategy matches on: the test id, the accessible name, the label or the copy. */
export function specValue(el: ElementSpec): string | RegExp | undefined {
  if ('testId' in el) return el.testId;
  if ('role' in el) return el.name;
  if ('label' in el) return el.label;
  return el.text;
}

/**
 * `<…>` marks a value nobody has observed yet (screens/README.md): the alias exists so
 * a test case can name it, and it fails loudly until the real value is filled in.
 * The health check lists placeholders instead of counting them.
 */
export function isPlaceholder(el: ElementSpec): boolean {
  const value = specValue(el);
  return typeof value === 'string' && /^<.+>$/.test(value);
}
