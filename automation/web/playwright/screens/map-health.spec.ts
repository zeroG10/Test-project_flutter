import fs from 'node:fs';
import path from 'node:path';
import type { Page, TestInfo } from '@playwright/test';
import { test, expect } from '../fixtures/test-fixtures';
import { appScreens, publicScreens } from './index';
import { isPlaceholder, locate, specValue, type ElementSpec, type ScreenMap } from './resolve';

/*
 * Screen-map health check — harness health for layer 2 (the alias → locator maps),
 * NOT feature coverage. It closes no checklist item and carries no CHK tag.
 *
 * Claim it proves, per curated screen: every alias that has been observed on the
 * page resolves to EXACTLY ONE element right after navigation. One run after a
 * markup change on DEV says which aliases broke (missing) or became ambiguous
 * (strict mode would throw in every test that uses them) — before the functional
 * suite turns red for a less obvious reason.
 *
 * Oracle: the curated map itself (screens/<module>/<screen>.map.ts, each entry dated
 * "observed …") + Playwright strict mode. Outside the claim, listed but never counted
 * as a pass: `<…>` placeholders (unobserved, owed by the testability contract) and
 * `state:` aliases (exist only after an interaction — an error alert, a revealed
 * password). Routes with a parameter and screens with nothing observed are Blocked.
 *
 * Project `map-health` (playwright.config.ts): Chromium, Root storageState; the public
 * describe below overrides the state with a clean context. Run: npm run pw:map-health
 */

type Verdict = 'ok' | 'missing' | 'ambiguous' | 'hidden' | 'placeholder' | 'conditional';

interface AliasRow {
  alias: string;
  strategy: string;
  count: number | null;
  verdict: Verdict;
  note: string;
}

/** Human form of a spec for the report: `role button "Log in" exact`. */
function strategyOf(el: ElementSpec): string {
  const value = specValue(el);
  const shown = value instanceof RegExp ? value.toString() : value === undefined ? '' : JSON.stringify(value);
  const exact = 'exact' in el && el.exact ? ' exact' : '';
  if ('testId' in el) return `testId ${shown}`;
  if ('role' in el) return `role ${el.role}${shown ? ` ${shown}` : ''}${exact}`;
  if ('label' in el) return `label ${shown}${exact}`;
  return `text ${shown}${exact}`;
}

/** expect-url <screen> → the route, optionally followed by /, ? or end of string. */
const atRoute = (route: string): RegExp => new RegExp(`${route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(/|\\?|$)`);

function renderTable(rows: AliasRow[]): string {
  const lines = ['| alias | strategy | count | verdict | note |', '|---|---|---|---|---|'];
  for (const r of rows) {
    lines.push(`| ${r.alias} | ${r.strategy.replace(/\|/g, '\\|')} | ${r.count ?? '—'} | ${r.verdict} | ${r.note} |`);
  }
  return lines.join('\n');
}

async function checkScreen(page: Page, screen: ScreenMap, testInfo: TestInfo): Promise<void> {
  const entries = Object.entries(screen.elements);
  const observed = entries.filter(([, el]) => !isPlaceholder(el) && !el.state);

  // Blocked, not green: a parametrised route cannot be opened without a real value
  // (set-password needs the emailed secret key); an all-placeholder map has nothing
  // observed to check yet. Both stay owed and show up as skipped in the report.
  test.skip(
    screen.route.includes('/:'),
    `Blocked: ${screen.id} route ${screen.route} needs a parameter — open it from a real link (mailbox flow), then check`,
  );
  test.skip(
    observed.length === 0,
    `Blocked: ${screen.id} has no observed alias yet (placeholders only) — fill the map from recon, then check`,
  );

  await page.goto(screen.route);

  // Readiness = the screen's own anchor (`root` when it exists, else the first observed
  // alias) within the navigation budget: the DEV bundle is slow (playwright.config.ts).
  const anchor = observed.find(([alias]) => alias === 'root') ?? observed[0];
  await expect(
    locate(page, anchor[1]),
    `${screen.id}.${anchor[0]} — screen anchor not visible after opening ${screen.route}: wrong page, redirect, or the anchor itself broke`,
  ).toBeVisible({ timeout: testInfo.project.use.navigationTimeout ?? 45_000 });
  await expect
    .soft(page, `${screen.id}: opened ${screen.route} but the URL moved away (redirect / session state)`)
    .toHaveURL(atRoute(screen.route));
  // Let late renders (icons, lazy widgets) settle, but never hang on a polling app.
  await page.waitForLoadState('networkidle', { timeout: 5_000 }).catch(() => undefined);

  const rows: AliasRow[] = [];
  for (const [alias, el] of entries) {
    const strategy = strategyOf(el);
    if (isPlaceholder(el)) {
      rows.push({ alias, strategy, count: null, verdict: 'placeholder', note: 'not observed yet — testability contract' });
      continue;
    }
    const locator = locate(page, el);
    let count = await locator.count();
    if (el.state) {
      rows.push({
        alias,
        strategy,
        count,
        verdict: count > 1 ? 'ambiguous' : 'conditional',
        note: `only after state "${el.state}" — not expected on load`,
      });
      continue;
    }
    if (count === 0) {
      // One bounded second chance for an element that renders after the anchor.
      await locator.first().waitFor({ state: 'attached', timeout: 3_000 }).catch(() => undefined);
      count = await locator.count();
    }
    if (count === 1) {
      const visible = await locator.isVisible();
      rows.push({ alias, strategy, count, verdict: visible ? 'ok' : 'hidden', note: visible ? '' : 'attached but not visible on load' });
    } else {
      rows.push({ alias, strategy, count, verdict: count === 0 ? 'missing' : 'ambiguous', note: '' });
    }
  }

  const table = renderTable(rows);
  await testInfo.attach(`${screen.id}.map-health.md`, { body: table, contentType: 'text/markdown' });
  console.log(`\n${screen.id} (${screen.route})\n${table}\n`);
  for (const r of rows) {
    if (r.verdict === 'placeholder' || r.verdict === 'conditional' || r.verdict === 'hidden') {
      testInfo.annotations.push({ type: r.verdict, description: `${screen.id}.${r.alias} — ${r.strategy} — ${r.note}` });
    }
  }

  // Soft, so one run reports every broken alias of the screen, not just the first.
  for (const r of rows) {
    if (r.verdict === 'missing') {
      expect
        .soft(r.count, `${screen.id}.${r.alias} MISSING — ${r.strategy} matched nothing on ${screen.route}: the page changed or the map is stale`)
        .toBe(1);
    }
    if (r.verdict === 'ambiguous') {
      expect
        .soft(r.count, `${screen.id}.${r.alias} AMBIGUOUS — ${r.strategy} matched ${r.count} elements: strict mode throws in every test that uses it`)
        .toBe(1);
    }
  }
}

function mapFiles(dir: string): string[] {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) return mapFiles(full);
    return entry.name.endsWith('.map.ts') ? [full] : [];
  });
}

test.describe('screen-map registry', () => {
  test('every screens/**/*.map.ts is registered in screens/index.ts, and ids match file names', { tag: ['@map-health'] }, async () => {
    const onDisk = mapFiles(__dirname).map((f) => path.basename(f, '.map.ts'));
    const registered = [...publicScreens, ...appScreens].map((s) => s.id);

    const duplicates = registered.filter((id, i) => registered.indexOf(id) !== i);
    expect(duplicates, `screen ids registered twice: ${duplicates.join(', ')}`).toEqual([]);

    const unregistered = onDisk.filter((id) => !registered.includes(id));
    expect(unregistered, `maps on disk missing from screens/index.ts: ${unregistered.join(', ')}`).toEqual([]);

    const orphans = registered.filter((id) => !onDisk.includes(id));
    expect(orphans, `registered ids without a <id>.map.ts file (id must equal the file name): ${orphans.join(', ')}`).toEqual([]);
  });
});

test.describe('public screens (clean context)', () => {
  test.use({ storageState: { cookies: [], origins: [] } });
  for (const screen of publicScreens) {
    test(`${screen.id} (${screen.route}) — every observed alias resolves to exactly one element`, { tag: ['@map-health'] }, async ({ page }, testInfo) => {
      await checkScreen(page, screen, testInfo);
    });
  }
});

test.describe('signed-in screens (Root state)', () => {
  if (appScreens.length === 0) {
    test('no signed-in screen map curated yet', { tag: ['@map-health'] }, async () => {
      test.skip(true, 'Blocked: appScreens in screens/index.ts is empty — nothing to check yet, which is not a pass');
    });
  }
  for (const screen of appScreens) {
    test(`${screen.id} (${screen.route}) — every observed alias resolves to exactly one element`, { tag: ['@map-health'] }, async ({ page }, testInfo) => {
      await checkScreen(page, screen, testInfo);
    });
  }
});
