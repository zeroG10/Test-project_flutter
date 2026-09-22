import type { Locator, Page } from '@playwright/test';
import { locate } from '../../screens/resolve';
import { camel, pascal } from './aliases';
import {
  MESSAGE_SELECTOR,
  OVERLAY_SELECTOR,
  extractAnchorsInBrowser,
  overlayCountInBrowser,
  validationMessagesInBrowser,
  type RawAnchor,
} from './browser-harvest';
import { collectRaw, countGaps, harvestScope, taggedLocator } from './harvest';
import type { Harvest, HarvestedElement, Log, SubStateRecord, ValidationProbe } from './types';

/** Never clicked, in any mode (except the explicit --probe-validation submit on an empty form). */
export const BLOCKLIST =
  /\b(delete|remove|logout|log out|sign out|signout|pay|purchase|send|submit|approve|reject|publish|archive|deactivate|disable|reset)\b/i;
/**
 * Names that usually open a dialog / menu / filter panel. `ellipsis` is Ant Design's
 * overflow "…" button — on Ant Design admin panels it usually hides delete / duplicate, and its
 * accessible name is the icon's, never the word "more". `preview` opens the read-only view
 * of whatever is being edited.
 */
export const OPENER_NAME =
  /^(add|create|new|filter|filters|edit|more|actions|columns|export|import|settings|ellipsis|preview|options)\b/i;
/** The openers that create something — tried first, because they are what coverage needs most. */
const PRIMARY_OPENER = /^(add|create|new)\b/i;
/** The same control repeated once per table row (10x "edit"): they all open the same thing. */
const MAX_SAME_OPENER = 2;
const CLOSE_NAME = /close|cancel/i;
const PROBE_PATH = /new|create|add/i;
const PROBE_BUTTON = /^(save|create|submit)\b/i;

const MAX_DISCOVERY_CLICKS = 25;
const MAX_OPENERS = 16;
/** Slow dev bundles are common; 2 s was not enough for Ant Design overlays on a real project. */
const OPENER_CLICK_TIMEOUT = 5_000;
const OVERLAY_WAIT = 3_000;
const MAX_TABS = 8;
const NAV_TIMEOUT = 15_000;
const IDLE_TIMEOUT = 5_000;

export interface ExploreContext {
  page: Page;
  deadline: number;
  /** Raw URL to navigate back to when a click leaves the page. */
  pageUrl: string;
  slug: string;
  log: Log;
}

export function errorMessage(e: unknown): string {
  const m = e instanceof Error ? e.message : String(e);
  return m.split('\n')[0].slice(0, 200);
}

/** Wait for the SPA to settle after a navigation: DOM ready, then network idle (bounded). */
export async function settle(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded', { timeout: IDLE_TIMEOUT }).catch(() => undefined);
  await page.waitForLoadState('networkidle', { timeout: IDLE_TIMEOUT }).catch(() => undefined);
  // One animation frame's worth of grace for client-side routers that render after idle.
  await page.waitForTimeout(250);
}

function isBlocked(el: HarvestedElement): boolean {
  return BLOCKLIST.test(el.name) || BLOCKLIST.test(el.text);
}

/** The locator a generated test would use; falls back to the temporary tag when nothing is unique. */
export function locatorFor(page: Page, el: HarvestedElement): Locator {
  if (el.spec && el.unique) return locate(page, el.spec);
  return taggedLocator(page, el.index);
}

async function restore(ctx: ExploreContext): Promise<void> {
  await ctx.page.goto(ctx.pageUrl, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT });
  await settle(ctx.page);
  await collectRaw(ctx.page, 'page'); // re-stamp tags after the reload
}

async function urlChanged(page: Page, before: string, timeout: number): Promise<boolean> {
  return page
    .waitForURL((u) => u.href !== before, { timeout })
    .then(() => true)
    .catch(() => page.url() !== before);
}

async function overlayCount(page: Page): Promise<number> {
  return page.evaluate(overlayCountInBrowser, OVERLAY_SELECTOR).catch(() => 0);
}

async function waitOverlayCount(page: Page, predicate: 'more' | 'back', n: number, timeout: number): Promise<boolean> {
  const until = Date.now() + timeout;
  for (;;) {
    const count = await overlayCount(page);
    if (predicate === 'more' ? count > n : count <= n) return true;
    if (Date.now() >= until) return false;
    await page.waitForTimeout(100);
  }
}

export interface DiscoveryResult {
  discovered: RawAnchor[];
  errors: string[];
}

/**
 * SPA navigation that `a[href]` extraction cannot see: role=link without an anchor,
 * `href="#"` / `javascript:` anchors, menu items without an inner link, buttons in
 * nav/header/sider. Click, watch the URL, record, go back.
 */
export async function discoverByClick(ctx: ExploreContext, harvest: Harvest): Promise<DiscoveryResult> {
  const { page } = ctx;
  const result: DiscoveryResult = { discovered: [], errors: [] };
  const candidates = harvest.elements.filter((el) => {
    if (el.disabled || el.flags.inOverlay || el.flags.hasPopup || el.flags.expanded === 'false' || isBlocked(el)) return false;
    if (el.kind === 'link') return el.flags.hrefKind === 'hash' || el.flags.hrefKind === 'js' || el.flags.hrefKind === 'none';
    if (el.kind === 'menuitem') return !el.flags.hasInnerRouteLink && el.flags.hrefKind !== 'route';
    if (el.kind === 'button') return el.flags.inNav && !OPENER_NAME.test(el.name);
    return false;
  });
  for (const el of candidates.slice(0, MAX_DISCOVERY_CLICKS)) {
    if (Date.now() > ctx.deadline) break;
    const before = page.url();
    try {
      await locatorFor(page, el).click({ timeout: 2000 });
    } catch (e) {
      result.errors.push(`discovery click '${el.alias}' failed: ${errorMessage(e)}`);
      continue;
    }
    if (await urlChanged(page, before, 1500)) {
      result.discovered.push({ href: page.url(), text: el.name || el.text || el.alias });
      try {
        await restore(ctx);
      } catch (e) {
        result.errors.push(`could not return to ${ctx.pageUrl} after clicking '${el.alias}': ${errorMessage(e)}`);
        break;
      }
    } else {
      await page.keyboard.press('Escape').catch(() => undefined);
    }
  }
  return result;
}

export interface ExploreResult {
  subStates: SubStateRecord[];
  discovered: RawAnchor[];
  errors: string[];
}

async function closeOverlay(ctx: ExploreContext, nBefore: number): Promise<SubStateRecord['closedBy']> {
  const { page } = ctx;
  await page.keyboard.press('Escape').catch(() => undefined);
  if (await waitOverlayCount(page, 'back', nBefore, 1500)) return 'escape';
  try {
    const btn = page.locator(OVERLAY_SELECTOR).filter({ visible: true }).last().getByRole('button', { name: CLOSE_NAME }).first();
    if ((await btn.count()) > 0) {
      await btn.click({ timeout: 1500 });
      if (await waitOverlayCount(page, 'back', nBefore, 1500)) return 'close-button';
    }
  } catch {
    /* fall through to reload */
  }
  await restore(ctx);
  return 'reload';
}

function subStateRecord(ctx: ExploreContext, opener: HarvestedElement, harvest: Harvest, kind: SubStateRecord['kind'], closedBy: SubStateRecord['closedBy']): SubStateRecord {
  return {
    id: `${ctx.slug}#${opener.alias}`,
    mapId: `${ctx.slug}-${opener.alias}`, // same prefix as the suggested test ids of this state
    constName: `${camel(ctx.slug)}${pascal(opener.alias)}${pascal(kind)}`,
    kind,
    opener: { alias: opener.alias, name: opener.name, kind: opener.kind },
    harvest,
    closedBy,
    gaps: countGaps(harvest),
  };
}

/**
 * The strings an opener may be recognised by. The accessible name can carry an icon's
 * label ("plus-circle Add" — observed on every list page of a real Ant Design admin
 * panel), which defeats a start-anchored match, so the visible text and the derived
 * alias (both already free of the icon label) are tried as well.
 */
function openerStrings(el: HarvestedElement): string[] {
  return [el.name, el.text, el.alias].filter((s): s is string => Boolean(s));
}

function isOpenerName(el: HarvestedElement): boolean {
  return openerStrings(el).some((s) => OPENER_NAME.test(s));
}

function isPrimaryOpener(el: HarvestedElement): boolean {
  return openerStrings(el).some((s) => PRIMARY_OPENER.test(s));
}

/**
 * Open every opener-looking element (aria-haspopup, aria-expanded=false, names like
 * add/create/filter/…), harvest what appears as a sub-state, close it. Then the same
 * for tabs whose panel is not the initially selected one.
 */
export async function exploreStates(ctx: ExploreContext, harvest: Harvest): Promise<ExploreResult> {
  const { page } = ctx;
  const result: ExploreResult = { subStates: [], discovered: [], errors: [] };
  const openerKinds = new Set(['button', 'link', 'menuitem', 'combobox', 'other']);
  const candidates = harvest.elements.filter((el) => {
    if (el.disabled || el.flags.inOverlay || isBlocked(el) || !openerKinds.has(el.kind)) return false;
    if (el.kind === 'link' && el.flags.hrefKind === 'route') return false;
    return el.flags.hasPopup || el.flags.expanded === 'false' || isOpenerName(el);
  });

  // A table with 10 rows yields 10 identical "edit" buttons. Without this, they fill
  // MAX_OPENERS and the page's real openers (Add, Filter) are never clicked.
  const seen = new Map<string, number>();
  const deduped = candidates.filter((el) => {
    const key = `${el.kind}|${(el.text || el.name).trim().toLowerCase()}`;
    const n = (seen.get(key) ?? 0) + 1;
    seen.set(key, n);
    return n <= MAX_SAME_OPENER;
  });

  // Creators first (they are what CRUD coverage needs), then the rest in document order,
  // comboboxes last: a select rarely hides anything a test case cannot reach otherwise.
  const rank = (el: HarvestedElement): number => (isPrimaryOpener(el) ? 0 : el.kind === 'combobox' ? 2 : 1);
  const openers = deduped
    .map((el, order) => ({ el, order }))
    .sort((a, b) => rank(a.el) - rank(b.el) || a.order - b.order)
    .map(({ el }) => el)
    .slice(0, MAX_OPENERS);

  const anchorsBefore = new Set((await page.evaluate(extractAnchorsInBrowser).catch(() => [] as RawAnchor[])).map((a) => a.href));

  for (const opener of openers) {
    if (Date.now() > ctx.deadline) break;
    const before = page.url();
    const nBefore = await overlayCount(page);
    try {
      await locatorFor(page, opener).click({ timeout: OPENER_CLICK_TIMEOUT });
    } catch (firstError) {
      // Ant Design wraps a Select's real hit target around an inner combobox that reports
      // itself as the control: the accessible element is there but never actionable
      // ('page-size' failed on every list page, 2026-09-21). One forced click through the
      // overlay is acceptable here — recon explores, it does not assert.
      try {
        await locatorFor(page, opener).click({ timeout: OPENER_CLICK_TIMEOUT, force: true });
        result.errors.push(`opener '${opener.alias}': normal click failed, opened with force (${errorMessage(firstError)})`);
      } catch (e) {
        result.errors.push(`opener '${opener.alias}': click failed (${errorMessage(e)})`);
        continue;
      }
    }
    const opened = await waitOverlayCount(page, 'more', nBefore, OVERLAY_WAIT);
    if (!opened) {
      if (page.url() !== before) {
        result.discovered.push({ href: page.url(), text: opener.name || opener.alias });
        try {
          await restore(ctx);
        } catch (e) {
          result.errors.push(`could not return to ${ctx.pageUrl} after '${opener.alias}': ${errorMessage(e)}`);
          break;
        }
        continue;
      }
      // Inline expansion (e.g. an inline sub-menu): pick up routes that appeared.
      const anchorsNow = await page.evaluate(extractAnchorsInBrowser).catch(() => [] as RawAnchor[]);
      for (const a of anchorsNow) {
        if (!anchorsBefore.has(a.href)) {
          anchorsBefore.add(a.href);
          result.discovered.push({ href: a.href, text: a.text || opener.alias });
        }
      }
      await page.keyboard.press('Escape').catch(() => undefined);
      continue;
    }
    const sub = await harvestScope(page, 'overlay', `${ctx.slug}-${opener.alias}`, { deadline: ctx.deadline });
    const kind = sub.container?.kind ?? 'popup';
    ctx.log(`    state ${ctx.slug}#${opener.alias} (${kind}): ${sub.elements.length} elements`);
    let closedBy: SubStateRecord['closedBy'];
    try {
      closedBy = await closeOverlay(ctx, nBefore);
    } catch (e) {
      result.errors.push(`could not close '${opener.alias}' (${kind}): ${errorMessage(e)}`);
      closedBy = 'n/a';
    }
    result.subStates.push(subStateRecord(ctx, opener, sub, kind, closedBy));
    if (closedBy !== 'reload') await collectRaw(page, 'page'); // restore base-state tags
  }

  // Tabs: a panel that is not the initially selected one is a sub-state too.
  const activeTab = harvest.elements.find((el) => el.kind === 'tab' && el.flags.selected);
  const tabs = harvest.elements
    .filter((el) => el.kind === 'tab' && !el.flags.selected && !el.disabled && !el.flags.inOverlay && !isBlocked(el))
    .slice(0, MAX_TABS);
  for (const tab of tabs) {
    if (Date.now() > ctx.deadline) break;
    const before = page.url();
    try {
      await locatorFor(page, tab).click({ timeout: 2000 });
    } catch (e) {
      result.errors.push(`tab '${tab.alias}': click failed (${errorMessage(e)})`);
      continue;
    }
    if (await urlChanged(page, before, 1000)) {
      result.discovered.push({ href: page.url(), text: tab.name || tab.alias });
      try {
        await restore(ctx);
      } catch (e) {
        result.errors.push(`could not return to ${ctx.pageUrl} after tab '${tab.alias}': ${errorMessage(e)}`);
        break;
      }
      continue;
    }
    await page
      .locator('[role="tab"][aria-selected="true"]')
      .filter({ hasText: tab.name })
      .first()
      .waitFor({ state: 'visible', timeout: 1500 })
      .catch(() => undefined);
    await settle(page);
    const sub = await harvestScope(page, 'tabpanel', `${ctx.slug}-${tab.alias}`, { deadline: ctx.deadline });
    if (sub.container) {
      ctx.log(`    state ${ctx.slug}#${tab.alias} (tabpanel): ${sub.elements.length} elements`);
      result.subStates.push(subStateRecord(ctx, tab, sub, 'tabpanel', 'tab-restore'));
    } else {
      result.errors.push(`tab '${tab.alias}': no [role=tabpanel] became visible — skipped`);
    }
    let restored = false;
    if (activeTab) {
      try {
        await locatorFor(page, activeTab).click({ timeout: 1500 });
        await settle(page);
        await collectRaw(page, 'page');
        restored = true;
      } catch {
        restored = false;
      }
    }
    if (!restored) {
      try {
        await restore(ctx);
      } catch (e) {
        result.errors.push(`could not restore page after tab '${tab.alias}': ${errorMessage(e)}`);
        break;
      }
    }
  }
  return result;
}

export interface ProbeResult {
  probe: ValidationProbe | null;
  /** Error/alert elements that only exist after the empty submit. */
  errorElements: HarvestedElement[];
  errors: string[];
}

/**
 * `--probe-validation`: on a /new|create|add page, click the primary save/create/submit
 * button of an EMPTY form once, record the validation messages, go back. Nothing is
 * filled in, so nothing can be created.
 */
export async function probeValidation(ctx: ExploreContext, harvest: Harvest, route: string): Promise<ProbeResult> {
  const { page } = ctx;
  const out: ProbeResult = { probe: null, errorElements: [], errors: [] };
  if (!PROBE_PATH.test(route)) return out;
  const form = harvest.forms.find((f) => f.empty && f.fields.length > 0);
  if (!form) {
    out.errors.push('validation probe skipped: no empty <form> with fields on this page');
    return out;
  }
  const formLoc = page.locator('form').nth(form.index);
  let btn = formLoc.getByRole('button', { name: PROBE_BUTTON }).first();
  if ((await btn.count()) === 0) btn = formLoc.locator('button[type="submit"], input[type="submit"]').first();
  if ((await btn.count()) === 0) {
    out.errors.push('validation probe skipped: no primary save/create/submit button in the empty form');
    return out;
  }
  const buttonName = (await btn.textContent().catch(() => null))?.replace(/\s+/g, ' ').trim() || 'submit';
  const before = page.url();
  try {
    await btn.click({ timeout: 2000 });
  } catch (e) {
    out.errors.push(`validation probe: click on '${buttonName}' failed (${errorMessage(e)})`);
    return out;
  }
  await page.waitForTimeout(1500);
  const messages = await page.evaluate(validationMessagesInBrowser, MESSAGE_SELECTOR).catch(() => []);
  const urlAfter = page.url();
  out.probe = { formIndex: form.index, button: buttonName, messages, urlAfter };
  if (urlAfter !== before) out.probe.note = 'URL changed after the empty submit — check nothing was created';
  const known = new Set(harvest.elements.map((e) => `${e.kind}|${e.name}|${e.text}`));
  const after = await harvestScope(page, 'page', ctx.slug, {
    deadline: ctx.deadline,
    reserved: new Set(harvest.elements.map((e) => e.alias)),
  });
  for (const el of after.elements) {
    if ((el.kind === 'alert' || el.kind === 'status') && !known.has(`${el.kind}|${el.name}|${el.text}`)) {
      el.state = 'after-empty-submit';
      out.errorElements.push(el);
    }
  }
  try {
    await restore(ctx);
  } catch (e) {
    out.errors.push(`validation probe: could not return to ${ctx.pageUrl} (${errorMessage(e)})`);
  }
  return out;
}
