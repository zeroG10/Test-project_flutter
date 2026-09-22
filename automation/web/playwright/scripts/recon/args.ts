import fs from 'node:fs';
import path from 'node:path';
import { parseArgs } from 'node:util';

export interface ReconOptions {
  baseUrl: string;
  start: string;
  storageState: string | undefined;
  maxPages: number;
  maxMinutes: number;
  allow: RegExp | undefined;
  deny: RegExp | undefined;
  exploreStates: boolean;
  probeValidation: boolean;
  out: string;
  module: string;
  headed: boolean;
}

/** A CLI usage problem — printed without a stack trace, exit code 2. */
export class UsageError extends Error {}

export const HELP = `recon — logged-in crawler + locator harvester (web)

Usage: npx tsx automation/web/playwright/scripts/recon.ts [options]
       npm run pw:recon -- [options]

Target
  --base-url <url>         default: $BASE_URL (automation/web/.env is loaded like playwright.config.ts does)
  --start <path>           first page, default "/" (= the base URL itself)
  --storage-state <file>   Playwright storageState JSON for an authenticated crawl

Limits and scope
  --max-pages <n>          default 40
  --max-minutes <n>        default 10 (hard wall clock for the whole run)
  --allow <regex>          only follow paths matching this (start page always visited)
  --deny <regex>           never follow paths matching this (logout/sign-out is always denied)

Behaviour
  --explore-states         click openers (add/filter/… , aria-haspopup, tabs) and harvest what opens (default on)
  --no-explore-states      disable state exploration
  --probe-validation       on /new|create|add pages only: submit an EMPTY form once and record the errors (default off)
  --headed                 show the browser

Output
  --out <dir>              default automation/web/playwright/scripts/recon-out/<YYYY-MM-DD-HHmm>/ (gitignored)
  --module <name>          label written into every output (e.g. authentication)
  -h, --help

Never clicks anything matching the destructive blocklist (delete/remove/logout/pay/send/submit/…).
Never stores credentials — pass auth as a storageState file only.`;

function stamp(d = new Date()): string {
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}`;
}

function positiveInt(raw: string | undefined, flag: string, fallback: number): number {
  if (raw === undefined) return fallback;
  const n = Number.parseInt(raw, 10);
  if (!Number.isFinite(n) || n <= 0) throw new UsageError(`${flag} must be a positive integer, got '${raw}'`);
  return n;
}

function regexOrUndefined(raw: string | undefined, flag: string): RegExp | undefined {
  if (raw === undefined || raw === '') return undefined;
  try {
    return new RegExp(raw);
  } catch (e) {
    throw new UsageError(`${flag} is not a valid regular expression: ${(e as Error).message}`);
  }
}

export function parseCliArgs(
  argv: readonly string[],
  env: { baseUrl: string | undefined; outRoot: string },
): ReconOptions | 'help' {
  let parsed: ReturnType<typeof parseArgs>;
  try {
    parsed = parseArgs({
      args: [...argv],
      strict: true,
      allowPositionals: false,
      options: {
        'base-url': { type: 'string' },
        start: { type: 'string' },
        'storage-state': { type: 'string' },
        'max-pages': { type: 'string' },
        'max-minutes': { type: 'string' },
        allow: { type: 'string' },
        deny: { type: 'string' },
        'explore-states': { type: 'boolean' },
        'no-explore-states': { type: 'boolean' },
        'probe-validation': { type: 'boolean' },
        out: { type: 'string' },
        module: { type: 'string' },
        headed: { type: 'boolean' },
        help: { type: 'boolean', short: 'h' },
      },
    });
  } catch (e) {
    throw new UsageError(`${(e as Error).message}\n\n${HELP}`);
  }
  const v = parsed.values as Record<string, string | boolean | undefined>;
  const str = (k: string): string | undefined => (typeof v[k] === 'string' ? (v[k] as string) : undefined);
  const bool = (k: string): boolean => v[k] === true;

  if (bool('help')) return 'help';

  const baseUrl = str('base-url') ?? env.baseUrl;
  if (!baseUrl) {
    throw new UsageError(
      'BASE_URL is not set — pass --base-url, export BASE_URL, or set it in automation/web/.env. ' +
        'A run without a target is Blocked, not green.',
    );
  }
  try {
    new URL(baseUrl);
  } catch {
    throw new UsageError(`BASE_URL is not a valid URL: '${baseUrl}' — replace the <…> placeholder with the real target.`);
  }

  let storageState: string | undefined;
  const ss = str('storage-state');
  if (ss !== undefined) {
    storageState = path.resolve(ss);
    if (!fs.existsSync(storageState)) throw new UsageError(`--storage-state file not found: ${storageState}`);
  }

  const start = str('start') ?? '/';
  if (!start.startsWith('/')) throw new UsageError(`--start must be a path starting with '/', got '${start}'`);

  const out = str('out') !== undefined ? path.resolve(str('out') as string) : path.join(env.outRoot, stamp());

  return {
    baseUrl,
    start,
    storageState,
    maxPages: positiveInt(str('max-pages'), '--max-pages', 40),
    maxMinutes: positiveInt(str('max-minutes'), '--max-minutes', 10),
    allow: regexOrUndefined(str('allow'), '--allow'),
    deny: regexOrUndefined(str('deny'), '--deny'),
    exploreStates: bool('no-explore-states') ? false : true,
    probeValidation: bool('probe-validation'),
    out,
    module: str('module') ?? 'unlabelled',
    headed: bool('headed'),
  };
}
