#!/usr/bin/env node
/**
 * Every report of the shared copy as PDF — A4, light theme, backgrounds printed, the footer
 * "TRIARE · <report> · run of <date> · Page n of N" (the same as the web project's reports):
 *
 *   reports/<slice>/internal/index.html                → reports/<slice>/pdf/<prefix>_TestCompletionReport_INTERNAL_<run date>.pdf
 *   reports/<slice>/client/test-completion-report.html → reports/<slice>/pdf/<prefix>_TestCompletionReport_<run date>.pdf
 *
 * The date is the date of the run the report describes, never the day the PDF was made; date, prefix and company come
 * from reports/<slice>/run.json, written by build_reports.py from setup/project.yaml → report. A PDF named by the wrong
 * run is worse than none: without run.json it refuses.
 *
 * No packages: Node's own WebSocket drives a headless Chromium over the DevTools protocol — the one Playwright keeps in
 * its cache, or Google Chrome, or CHROME_BIN.
 *
 *   node automation/tools/export_pdf.mjs [reports-root]
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root = path.resolve(process.argv[2] ?? path.join(import.meta.dirname, '../../reports'));
const SLICES = ['ios', 'android', 'mobile'];
const DOCS = [
  { page: 'internal/index.html', report: 'TestCompletionReport_INTERNAL', label: 'Test completion report (internal)' },
  { page: 'client/test-completion-report.html', report: 'TestCompletionReport', label: 'Test completion report' },
];

function chrome() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  const cache = path.join(homedir(), 'Library/Caches/ms-playwright');
  if (existsSync(cache)) {
    const shells = readdirSync(cache).filter((d) => d.startsWith('chromium_headless_shell-')).sort().reverse();
    for (const dir of shells) {
      for (const arch of ['chrome-headless-shell-mac-arm64', 'chrome-headless-shell-mac-x64', 'chrome-headless-shell-linux64']) {
        const bin = path.join(cache, dir, arch, 'chrome-headless-shell');
        if (existsSync(bin)) return bin;
      }
    }
  }
  const app = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if (existsSync(app)) return app;
  throw new Error('Blocked: no Chromium found — set CHROME_BIN');
}

async function launch() {
  const profile = mkdtempSync(path.join(tmpdir(), 'qa-pdf-'));
  const proc = spawn(chrome(), ['--headless', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run', 'about:blank'], {
    stdio: ['ignore', 'ignore', 'pipe'],
  });
  const url = await new Promise((resolve, reject) => {
    let err = '';
    proc.stderr.on('data', (chunk) => {
      err += chunk;
      const m = err.match(/DevTools listening on (ws:\/\/\S+)/);
      if (m) resolve(m[1]);
    });
    proc.on('exit', () => reject(new Error(`Chromium exited: ${err.slice(0, 400)}`)));
    setTimeout(() => reject(new Error('Chromium did not start in 20 s')), 20000);
  });
  const ws = new WebSocket(url);
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });
  let id = 0;
  const pending = new Map();
  const waiters = [];
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(new Error(msg.error.message));
      else resolve(msg.result);
    } else if (msg.method) {
      for (const w of waiters.splice(0)) {
        if (w.method === msg.method && w.sessionId === msg.sessionId) w.resolve(msg.params);
        else waiters.push(w);
      }
    }
  };
  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const n = ++id;
      pending.set(n, { resolve, reject });
      ws.send(JSON.stringify({ id: n, method, params, ...(sessionId ? { sessionId } : {}) }));
    });
  const once = (method, sessionId) => new Promise((resolve) => waiters.push({ method, sessionId, resolve }));
  const close = async () => {
    ws.close();
    const exited = new Promise((resolve) => proc.once('exit', resolve));
    proc.kill();
    await exited;
    try {
      rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
    } catch {
      // a temp profile left behind is harmless
    }
  };
  return { send, once, close };
}

async function print(cdp, file, footer, out) {
  const { targetId } = await cdp.send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await cdp.send('Target.attachToTarget', { targetId, flatten: true });
  await cdp.send('Page.enable', {}, sessionId);
  await cdp.send('Emulation.setEmulatedMedia', { media: 'print', features: [{ name: 'prefers-color-scheme', value: 'light' }] }, sessionId);
  const loaded = cdp.once('Page.loadEventFired', sessionId);
  await cdp.send('Page.navigate', { url: pathToFileURL(file).href }, sessionId);
  await loaded;
  await cdp.send('Runtime.evaluate', { expression: 'document.fonts.ready.then(() => true)', awaitPromise: true }, sessionId);
  const mm = (v) => v / 25.4;
  const { data } = await cdp.send(
    'Page.printToPDF',
    {
      paperWidth: mm(210),
      paperHeight: mm(297),
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate:
        '<div style="width:100%;font:9px Manrope,Arial,sans-serif;color:#5B6B85;padding:0 12mm;display:flex;justify-content:space-between">' +
        `<span>${footer}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`,
      marginTop: mm(14),
      marginBottom: mm(18),
      marginLeft: mm(12),
      marginRight: mm(12),
    },
    sessionId,
  );
  writeFileSync(out, Buffer.from(data, 'base64'));
  await cdp.send('Target.closeTarget', { targetId });
}

const cdp = await launch();
try {
  for (const slice of SLICES) {
    const runFile = path.join(root, slice, 'run.json');
    if (!existsSync(runFile)) throw new Error(`Blocked: no ${runFile} — run "build_reports.py --share" first`);
    const run = JSON.parse(readFileSync(runFile, 'utf8'));
    if (!run.date || !run.file_prefix || !run.company) throw new Error(`${runFile} lacks date / file_prefix / company`);
    const outDir = path.join(root, slice, 'pdf');
    mkdirSync(outDir, { recursive: true });
    for (const doc of DOCS) {
      const page = path.join(root, slice, doc.page);
      if (!existsSync(page)) throw new Error(`Blocked: no ${page}`);
      const out = path.join(outDir, `${run.file_prefix}_${doc.report}_${run.date}.pdf`);
      await print(cdp, page, `${run.company} · ${doc.label} · run of ${run.date}`, out);
      console.log(`pdf: ${path.relative(process.cwd(), out)}`);
    }
  }
} finally {
  await cdp.close();
}
