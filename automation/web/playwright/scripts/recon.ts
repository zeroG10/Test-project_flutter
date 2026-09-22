/**
 * recon — logged-in crawler + locator harvester for the web stack.
 *
 * Produces the raw material for screen maps (`screens/<screen>.map.draft.ts`),
 * checklists (`inventory.md`) and the testability hand-over (`gaps.md`).
 * Read automation/web/playwright/scripts/README.md before running it against a
 * shared environment: it clicks openers and tabs, never anything destructive.
 *
 *   npx tsx automation/web/playwright/scripts/recon.ts --max-pages 5 --module authentication
 *   npm run pw:recon -- --storage-state automation/web/playwright/.auth/user.json
 */
import fs from 'node:fs';
import path from 'node:path';
import { config as loadEnv } from 'dotenv';
import { HELP, UsageError, parseCliArgs } from './recon/args';
import { crawl } from './recon/crawl';
import { writeOutputs } from './recon/render';
import type { Log } from './recon/types';

// Same rule as playwright.config.ts: automation/web/.env for local runs, an exported
// BASE_URL wins, and no target means no run.
loadEnv({ path: path.resolve(__dirname, '..', '..', '.env'), quiet: true });

const log: Log = (message) => console.log(message);

async function main(): Promise<number> {
  const parsed = parseCliArgs(process.argv.slice(2), {
    baseUrl: process.env.BASE_URL,
    outRoot: path.resolve(__dirname, 'recon-out'),
  });
  if (parsed === 'help') {
    console.log(HELP);
    return 0;
  }
  const opts = parsed;
  for (const sub of ['screens', 'aria', 'screenshots']) fs.mkdirSync(path.join(opts.out, sub), { recursive: true });

  log(`recon: ${opts.baseUrl} (start ${opts.start}) → ${opts.out}`);
  log(
    `       module=${opts.module} max-pages=${opts.maxPages} max-minutes=${opts.maxMinutes} ` +
      `storage-state=${opts.storageState ? 'yes' : 'no'} explore-states=${opts.exploreStates ? 'on' : 'off'} ` +
      `probe-validation=${opts.probeValidation ? 'on' : 'off'}${opts.allow ? ` allow=/${opts.allow.source}/` : ''}${opts.deny ? ` deny=/${opts.deny.source}/` : ''}`,
  );

  const run = await crawl(opts, opts.out, log);
  const written = writeOutputs(run, opts.out);

  const harvested = run.pages.filter((p) => p.harvest !== null).length;
  const subStates = run.pages.reduce((n, p) => n + p.subStates.length, 0);
  const gaps = run.pages.reduce((n, p) => n + p.counts.gaps, 0);
  const errors = run.pages.reduce((n, p) => n + p.errors.length, 0);

  log('');
  log(`done in ${Math.round(run.meta.durationMs / 1000)}s: ${harvested} page(s) harvested, ${subStates} sub-state(s), ${gaps} gap(s), ${run.notVisited.length} route(s) not visited, ${errors} tool error(s)`);
  for (const n of run.notes) log(`note: ${n}`);
  log(`inventory: ${written.inventory}`);
  log(`gaps:      ${written.gaps}`);
  log(`drafts:    ${written.drafts.length} file(s) in ${path.join(opts.out, 'screens')}`);
  log(`summary:   ${written.summary}`);

  if (harvested === 0) {
    // Doctrine rule 3: an empty run is not a passing run.
    console.error('recon: zero pages harvested — the run is Blocked, not green. See inventory.md → Errors.');
    return 1;
  }
  return 0;
}

main()
  .then((code) => process.exit(code))
  .catch((e: unknown) => {
    if (e instanceof UsageError) {
      console.error(`recon: ${e.message}`);
      process.exit(2);
    }
    console.error(`recon: ${e instanceof Error ? e.stack ?? e.message : String(e)}`);
    process.exit(1);
  });
