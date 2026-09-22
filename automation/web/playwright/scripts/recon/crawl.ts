import fs from 'node:fs';
import path from 'node:path';
import { chromium, type Page } from '@playwright/test';
import { camel, slugFromPattern } from './aliases';
import type { ReconOptions } from './args';
import { TAG_ATTR, extractAnchorsInBrowser, untagInBrowser } from './browser-harvest';
import { discoverByClick, errorMessage, exploreStates, probeValidation, settle, type ExploreContext } from './explore';
import { countGaps, harvestScope } from './harvest';
import {
  INTERACTIVE_KINDS,
  type DiscoveredLink,
  type Log,
  type NotVisited,
  type PageCounts,
  type PageRecord,
  type ReconRun,
} from './types';
import { isAuthRoute, isBuiltinDenied, matchesFilters, normaliseUrl, routePath, routePattern } from './urls';

const NAV_TIMEOUT = 15_000;
const SCREENSHOT_TIMEOUT = 10_000;
const MAX_CONSOLE_ERRORS = 20;

interface QueueItem {
  url: string;
  pattern: string;
  navPath: string[];
  foundOn: string | null;
  /** Set after a page error: the item gets exactly one more attempt, in a fresh tab. */
  retried?: boolean;
}

function emptyCounts(): PageCounts {
  return { interactive: 0, forms: 0, tables: 0, dialogs: 0, gaps: 0, consoleErrors: 0 };
}

function computeCounts(rec: PageRecord): PageCounts {
  const h = rec.harvest;
  const subGaps = rec.subStates.reduce((n, s) => n + s.gaps, 0);
  return {
    interactive: h ? h.elements.filter((e) => INTERACTIVE_KINDS.has(e.kind)).length : 0,
    forms: h ? h.forms.length : 0,
    tables: h ? h.tables.length : 0,
    dialogs: rec.subStates.filter((s) => s.kind !== 'tabpanel').length,
    gaps: (h ? countGaps(h) : 0) + subGaps,
    consoleErrors: rec.consoleErrors.length,
  };
}

function newRecord(item: QueueItem, module: string): PageRecord {
  return {
    index: -1,
    pattern: item.pattern,
    slug: slugFromPattern(item.pattern),
    constName: camel(slugFromPattern(item.pattern)),
    requestedUrl: item.url,
    finalUrl: item.url,
    route: '',
    redirected: false,
    title: '',
    h1: null,
    navPath: item.navPath,
    module,
    harvest: null,
    subStates: [],
    discovered: [],
    consoleErrors: [],
    errors: [],
    notes: [],
    validationProbe: null,
    counts: emptyCounts(),
    durationMs: 0,
  };
}

async function detectHashRouting(page: Page): Promise<boolean> {
  if (new URL(page.url()).hash.startsWith('#/')) return true;
  return (await page.locator('a[href^="#/"]').count().catch(() => 0)) > 0;
}

export async function crawl(opts: ReconOptions, outDir: string, log: Log): Promise<ReconRun> {
  const startedAt = Date.now();
  const deadline = startedAt + opts.maxMinutes * 60_000;
  const base = new URL(opts.baseUrl);
  const startUrl = opts.start === '/' ? new URL(base.href) : new URL(opts.start, base);

  const run: ReconRun = {
    meta: {
      tool: 'recon.ts',
      baseUrl: base.href,
      startUrl: startUrl.href,
      storageState: !!opts.storageState,
      storageStateFile: opts.storageState ? path.basename(opts.storageState) : null,
      maxPages: opts.maxPages,
      maxMinutes: opts.maxMinutes,
      allow: opts.allow ? opts.allow.source : null,
      deny: opts.deny ? opts.deny.source : null,
      exploreStates: opts.exploreStates,
      probeValidation: opts.probeValidation,
      module: opts.module,
      headed: opts.headed,
      hashRouted: false,
      startedAt: new Date(startedAt).toISOString(),
      finishedAt: '',
      durationMs: 0,
      outDir,
    },
    pages: [],
    notVisited: [],
    instances: {},
    authRequired: false,
    notes: [],
    errors: [],
  };

  const pagesByPattern = new Map<string, PageRecord>();
  const queuedPatterns = new Set<string>();
  const instances = new Map<string, Set<string>>();
  const notVisitedKeys = new Set<string>();
  const fingerprints = new Map<string, string>();
  const queue: QueueItem[] = [];
  let hashRouted = false;

  const addNotVisited = (nv: NotVisited): void => {
    const key = `${nv.pattern}|${nv.reason}`;
    if (notVisitedKeys.has(key)) return;
    notVisitedKeys.add(key);
    run.notVisited.push(nv);
  };
  const addInstance = (pattern: string, url: string): void => {
    const set = instances.get(pattern) ?? new Set<string>();
    const known = pagesByPattern.get(pattern);
    if (known && known.finalUrl === url) return;
    set.add(url);
    instances.set(pattern, set);
  };

  /** Normalise, filter and queue a discovered URL. Returns the link record (null = off-origin / not http). */
  const enqueue = (rawHref: string, text: string, from: PageRecord | null, via: DiscoveredLink['via']): DiscoveredLink | null => {
    const u = normaliseUrl(rawHref, base, hashRouted);
    if (!u) return null;
    const pattern = routePattern(u);
    const link: DiscoveredLink = { url: u.href, pattern, text, via };
    const pathLike = routePath(u);
    if (isBuiltinDenied(pathLike)) {
      addNotVisited({ url: u.href, pattern, reason: 'built-in deny (logout / sign-out)', foundOn: from?.pattern ?? null });
      return link;
    }
    const verdict = matchesFilters(pathLike, opts.allow, opts.deny);
    if (verdict !== 'ok') {
      addNotVisited({ url: u.href, pattern, reason: verdict === 'deny' ? 'denied by --deny' : 'not matched by --allow', foundOn: from?.pattern ?? null });
      return link;
    }
    if (pagesByPattern.has(pattern) || queuedPatterns.has(pattern)) {
      addInstance(pattern, u.href);
      return link;
    }
    queuedPatterns.add(pattern);
    queue.push({ url: u.href, pattern, navPath: from ? [...from.navPath, text || '(no text)'] : [], foundOn: from?.pattern ?? null });
    return link;
  };

  const browser = await chromium.launch({ headless: !opts.headed });
  const context = await browser.newContext({
    storageState: opts.storageState,
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true,
    locale: 'en-US',
  });
  // tsx (esbuild keepNames) injects `__name(fn, "name")` helper calls into function
  // bodies; Playwright ships our in-browser functions by source, where that helper does
  // not exist. An identity shim in every document keeps page.evaluate() working under
  // tsx. Plain string on purpose: nothing to serialise, nothing to break.
  await context.addInitScript({ content: 'globalThis.__name = globalThis.__name || function (fn) { return fn; };' });
  let consoleBuf: string[] = [];
  const wirePage = (p: Page): void => {
    p.on('dialog', (d) => void d.dismiss().catch(() => undefined));
    p.on('console', (m) => {
      if (m.type() === 'error') consoleBuf.push(m.text().split('\n')[0].slice(0, 300));
    });
    p.on('pageerror', (e) => consoleBuf.push(`pageerror: ${e.message.split('\n')[0].slice(0, 300)}`));
  };
  // The 'page' event fires while `context.newPage()` is still awaiting, so a handler that
  // compares against `page` would close the very tab being created (observed 2026-09-21:
  // it killed the context and every later navigation). The flag marks our own creations.
  let creatingOwnPage = false;
  const newOwnPage = async (): Promise<Page> => {
    creatingOwnPage = true;
    try {
      return await context.newPage();
    } finally {
      creatingOwnPage = false;
    }
  };
  // A tab the app opened (a preview, a printable report). The crawler drives exactly one
  // tab, so the popup is closed — but its URL is a route worth visiting, and silently
  // dropping it would hide a whole screen.
  const popupUrls: string[] = [];
  context.on('page', (p) => {
    if (creatingOwnPage || p === page) return;
    void (async () => {
      await p.waitForLoadState('domcontentloaded', { timeout: 5_000 }).catch(() => undefined);
      const url = p.url();
      if (url && url !== 'about:blank') popupUrls.push(url);
      await p.close().catch(() => undefined);
    })();
  });
  let page = await newOwnPage();
  wirePage(page);
  /**
   * A wedged tab poisons every later navigation: on 2026-09-21 the survey editor left the
   * page in a state where every following `page.goto` failed with `net::ERR_ABORTED`, and
   * 8 routes were lost. A fresh tab in the SAME context keeps the session (storageState
   * lives on the context) and lets the crawl continue.
   */
  const recreatePage = async (): Promise<void> => {
    const old = page;
    page = await newOwnPage();
    wirePage(page);
    await old.close().catch(() => undefined);
  };

  const seedNorm = normaliseUrl(startUrl.href, base, false) ?? startUrl;
  const seedPattern = routePattern(seedNorm);
  queue.push({ url: startUrl.href, pattern: seedPattern, navPath: [], foundOn: null });
  queuedPatterns.add(seedPattern);

  let drainReason: string | null = null;
  try {
    while (queue.length > 0) {
      if (pagesByPattern.size >= opts.maxPages) {
        drainReason = 'limit reached (--max-pages)';
        break;
      }
      if (Date.now() > deadline) {
        drainReason = 'time limit reached (--max-minutes)';
        break;
      }
      const item = queue.shift();
      if (!item) break;
      if (pagesByPattern.has(item.pattern)) {
        // Harvested meanwhile under this pattern (a redirect landed on it) — one instance is enough.
        queuedPatterns.delete(item.pattern);
        addInstance(item.pattern, item.url);
        continue;
      }
      consoleBuf = [];
      const t0 = Date.now();
      const rec = newRecord(item, opts.module);
      let retryItem: QueueItem | null = null;
      log(`[${pagesByPattern.size + 1}/${opts.maxPages}] ${item.pattern}`);

      try {
        const response = await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: NAV_TIMEOUT });
        await settle(page);
        if (pagesByPattern.size === 0) {
          hashRouted = await detectHashRouting(page);
          run.meta.hashRouted = hashRouted;
        }
        const finalRaw = page.url();
        const finalNorm = normaliseUrl(finalRaw, base, hashRouted);
        if (!finalNorm) {
          addNotVisited({ url: item.url, pattern: item.pattern, reason: `navigated off-origin to ${finalRaw}`, foundOn: item.foundOn });
          continue;
        }
        const finalPattern = routePattern(finalNorm);
        if (finalPattern !== item.pattern) {
          const reqPath = routePath(normaliseUrl(item.url, base, hashRouted) ?? new URL(item.url));
          const finPath = routePath(finalNorm);
          if (!opts.storageState && isAuthRoute(finPath) && !isAuthRoute(reqPath)) {
            run.authRequired = true;
            addNotVisited({ url: item.url, pattern: item.pattern, reason: 'redirected to login — auth required (no --storage-state)', foundOn: item.foundOn });
          } else {
            addNotVisited({ url: item.url, pattern: item.pattern, reason: `redirects to ${finalPattern}`, foundOn: item.foundOn });
          }
          if (pagesByPattern.has(finalPattern)) {
            addInstance(finalPattern, finalNorm.href);
            continue;
          }
          rec.pattern = finalPattern;
          queuedPatterns.add(finalPattern); // links to it found on this very page must not re-queue it
          rec.slug = slugFromPattern(finalPattern);
          rec.constName = camel(rec.slug);
          rec.redirected = true;
          rec.notes.push(`reached via redirect from ${item.pattern}`);
        }
        rec.finalUrl = finalNorm.href;
        rec.route = routePath(finalNorm);
        if (response && response.status() >= 400) rec.notes.push(`HTTP ${response.status()}`);

        // 1. Base state.
        const harvest = await harvestScope(page, 'page', rec.slug, { deadline });
        rec.harvest = harvest;
        rec.title = harvest.title;
        rec.h1 = harvest.h1;
        if (harvest.truncated) rec.notes.push('element list truncated (250 max)');
        const fingerprint = `${harvest.title}|${harvest.h1 ?? ''}|${harvest.elements.map((e) => `${e.kind}:${e.name}`).join(',')}`;
        const twin = run.pages.find((p) => p.harvest && fingerprints.get(p.pattern) === fingerprint);
        if (twin) rec.notes.push(`same content as ${twin.pattern} (alias route?)`);
        fingerprints.set(rec.pattern, fingerprint);
        if (!opts.storageState && pagesByPattern.size === 0) {
          const passwordFields = await page.locator('input[type="password"]').count().catch(() => 0);
          if (passwordFields > 0 || isAuthRoute(rec.route)) {
            run.authRequired = true;
            rec.notes.push('login form present — no --storage-state given');
          }
        }
        log(`    ${harvest.elements.length} elements, ${harvest.forms.length} forms, ${harvest.tables.length} tables, ${countGaps(harvest)} gaps`);

        // 2. Aria snapshot + screenshot of the base state.
        try {
          const aria = await page.locator('body').ariaSnapshot({ timeout: 5000 });
          await fs.promises.writeFile(path.join(outDir, 'aria', `${rec.slug}.aria.yaml`), `${aria}\n`);
        } catch (e) {
          rec.errors.push(`aria snapshot failed: ${errorMessage(e)}`);
        }
        try {
          await page.screenshot({ path: path.join(outDir, 'screenshots', `${rec.slug}.png`), fullPage: true, timeout: SCREENSHOT_TIMEOUT });
        } catch (e) {
          rec.errors.push(`screenshot failed: ${errorMessage(e)}`);
        }

        // 3. Links from hrefs (hidden ones too — collapsed menus hold real routes).
        const anchors = await page.evaluate(extractAnchorsInBrowser).catch(() => []);
        for (const a of anchors) {
          const l = enqueue(a.href, a.text, rec, 'href');
          if (l) rec.discovered.push(l);
        }

        const ctx: ExploreContext = { page, deadline, pageUrl: finalRaw, slug: rec.slug, log };

        // 4. SPA navigation that hrefs cannot see.
        const clicks = await discoverByClick(ctx, harvest);
        rec.errors.push(...clicks.errors);
        for (const d of clicks.discovered) {
          const l = enqueue(d.href, d.text, rec, 'click');
          if (l) rec.discovered.push(l);
        }

        // 5. Empty-submit validation probe (opt-in, /new|create|add pages only).
        if (opts.probeValidation) {
          const probe = await probeValidation(ctx, harvest, rec.route);
          rec.validationProbe = probe.probe;
          rec.errors.push(...probe.errors);
          harvest.elements.push(...probe.errorElements);
        }

        // 6. Openers → dialogs / menus / drawers; tabs → panels.
        if (opts.exploreStates) {
          const ex = await exploreStates(ctx, harvest);
          rec.subStates = ex.subStates;
          rec.errors.push(...ex.errors);
          for (const d of ex.discovered) {
            const l = enqueue(d.href, d.text, rec, 'expand');
            if (l) rec.discovered.push(l);
          }
        }

        // Routes the app opened in its own tab while we were exploring this page.
        while (popupUrls.length > 0) {
          const url = popupUrls.shift();
          if (!url) break;
          const l = enqueue(url, 'popup', rec, 'expand');
          if (l) rec.discovered.push(l);
        }

        await page.evaluate(untagInBrowser, TAG_ATTR).catch(() => undefined);
      } catch (e) {
        rec.errors.push(`page error: ${errorMessage(e)}`);
        log(`    ERROR ${errorMessage(e)}`);
        await recreatePage().catch(() => undefined);
        if (!item.retried) retryItem = { ...item, retried: true };
      } finally {
        // Released only now: while the page was being processed, a nav link back to it
        // must not have been queued again (it is recorded in pagesByPattern right below).
        queuedPatterns.delete(item.pattern);
        queuedPatterns.delete(rec.pattern);
      }

      if (retryItem) {
        // Not recorded as a page: the retry produces the record. A second failure has
        // `retried` set, so it falls through to the record below — never a loop.
        queuedPatterns.add(retryItem.pattern);
        queue.unshift(retryItem);
        log(`    retrying ${item.pattern} in a fresh tab`);
        continue;
      }

      rec.consoleErrors = [...new Set(consoleBuf)].slice(0, MAX_CONSOLE_ERRORS);
      rec.counts = computeCounts(rec);
      rec.durationMs = Date.now() - t0;
      rec.index = run.pages.length;
      pagesByPattern.set(rec.pattern, rec);
      run.pages.push(rec);
    }
  } finally {
    await browser.close().catch(() => undefined);
  }

  if (drainReason) {
    for (const item of queue) addNotVisited({ url: item.url, pattern: item.pattern, reason: drainReason, foundOn: item.foundOn });
  }
  for (const [pattern, set] of instances) run.instances[pattern] = [...set];
  if (run.authRequired && !opts.storageState) {
    run.notes.push('Auth required for the rest: The crawl ran without --storage-state, so only unauthenticated routes were harvested. Re-run with --storage-state <file> for the app behind login.');
  }
  run.meta.finishedAt = new Date().toISOString();
  run.meta.durationMs = Date.now() - startedAt;
  return run;
}
