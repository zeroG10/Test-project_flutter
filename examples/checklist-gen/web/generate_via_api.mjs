// Web QA checklist generator — SERVICE-ACCOUNT variant of Vadym's adapter.
//
// Difference from the original colleague's kit adapter (kit removed from the template 2026-09-16):
//   1. Auth: Google **service account** (reuses automation/tools/.secrets/credentials.json)
//      instead of OAuth user flow + token.json. No browser, no 7-day expiry.
//   2. Target: writes into an EXISTING spreadsheet by ID (service accounts have no
//      visible Drive, so we never create a new file). The sheet must be shared with
//      the service-account email as Editor.
//
// Everything else — the Apps-Script-to-Sheets-API adapter (mock SpreadsheetApp /
// DriveApp / etc.), the reset logic, the flush, and the STEP-5 self-test — is
// carried over from Vadym's web template unchanged, so the .gs runs identically.
//
// Run:  node automation/checklist-gen/web/generate_via_api.mjs
import { readFileSync, existsSync } from 'fs';
import { dirname, resolve } from 'path';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '../../..');

// ── EDIT FOR EACH PROJECT ───────────────────────────────────────────────
// SAFETY: this generator does a FULL SHEET REBUILD. Never point it at a live
// team sheet. Set the ID explicitly per run; it fails fast while unset.
const SPREADSHEET_ID = '<YOUR_SPREADSHEET_ID>';
if (SPREADSHEET_ID.startsWith('<')) {
  console.error('SPREADSHEET_ID is not configured — edit the constants block first.');
  process.exit(1);
}
const SHEET_NAME     = 'Checklist';
const GS_PATH        = resolve(__dirname, 'checklist_generator.gs');
const GENERATOR_FN   = 'createAuthenticationChecklist';
const SA_KEY_FILE    = resolve(REPO_ROOT, 'automation/tools/.secrets/credentials.json');
const NCOLS          = 25; // web variant (A..Y)
// ────────────────────────────────────────────────────────────────────────

// googleapis is installed next to this example (npm install --prefix examples/checklist-gen googleapis).
const MCP_DIR = resolve(REPO_ROOT, 'examples/checklist-gen');
if (!existsSync(MCP_DIR + '/node_modules/googleapis')) {
  console.error('googleapis not installed. Run: npm install --prefix ' + MCP_DIR + ' googleapis');
  process.exit(1);
}
if (!existsSync(SA_KEY_FILE)) {
  console.error('Service-account key not found at ' + SA_KEY_FILE);
  process.exit(1);
}
const require = createRequire(MCP_DIR + '/');
const { google } = require('googleapis');

// ── Auth: service account ────────────────────────────────────────────────
const auth = new google.auth.GoogleAuth({
  keyFile: SA_KEY_FILE,
  scopes: ['https://www.googleapis.com/auth/spreadsheets'],
});
const authClient = await auth.getClient();
const api = google.sheets({ version: 'v4', auth: authClient });
console.log('Auth: service account', JSON.parse(readFileSync(SA_KEY_FILE)).client_email);
console.log('Target spreadsheet:', SPREADSHEET_ID);

// ── Resolve the 'Checklist' sheet (create if missing) + full reset ───────
let sheetId;
const meta = await api.spreadsheets.get({ spreadsheetId: SPREADSHEET_ID });
let sh = meta.data.sheets.find(s => s.properties.title === SHEET_NAME);
if (!sh) {
  const r = await api.spreadsheets.batchUpdate({ spreadsheetId: SPREADSHEET_ID, requestBody: { requests: [
    { addSheet: { properties: { title: SHEET_NAME, gridProperties: { rowCount: 200, columnCount: NCOLS } } } }
  ] } });
  sheetId = r.data.replies[0].addSheet.properties.sheetId;
} else {
  sheetId = sh.properties.sheetId;
  const nCf = (sh.conditionalFormats || []).length;
  const reqs = [
    { unmergeCells: { range: { sheetId } } },
    { updateCells: { range: { sheetId }, fields: 'userEnteredValue,userEnteredFormat,dataValidation' } },
  ];
  for (let i = nCf - 1; i >= 0; i--) reqs.push({ deleteConditionalFormatRule: { sheetId, index: i } });
  for (const g of (sh.columnGroups || [])) {
    for (let d = 0; d < (g.depth || 1); d++) {
      reqs.push({ deleteDimensionGroup: { range: { sheetId, dimension: 'COLUMNS', startIndex: g.range.startIndex, endIndex: g.range.endIndex } } });
    }
  }
  for (const g of (sh.rowGroups || [])) {
    for (let d = 0; d < (g.depth || 1); d++) {
      reqs.push({ deleteDimensionGroup: { range: { sheetId, dimension: 'ROWS', startIndex: g.range.startIndex, endIndex: g.range.endIndex } } });
    }
  }
  const none = { style: 'NONE' };
  reqs.push({ updateBorders: {
    range: { sheetId, startRowIndex: 0, endRowIndex: 200, startColumnIndex: 0, endColumnIndex: NCOLS },
    top: none, bottom: none, left: none, right: none, innerHorizontal: none, innerVertical: none,
  } });
  await api.spreadsheets.batchUpdate({ spreadsheetId: SPREADSHEET_ID, requestBody: { requests: reqs } });
}
const ssUrl = 'https://docs.google.com/spreadsheets/d/' + SPREADSHEET_ID + '/edit';

// ── Apps-Script-to-API adapter (verbatim from Vadym's web template) ──────
const hex = h => {
  const m = h.replace('#', '');
  return { red: parseInt(m.slice(0, 2), 16) / 255, green: parseInt(m.slice(2, 4), 16) / 255, blue: parseInt(m.slice(4, 6), 16) / 255 };
};
const HA = { left: 'LEFT', center: 'CENTER', right: 'RIGHT' };
const VA = { top: 'TOP', middle: 'MIDDLE', bottom: 'BOTTOM' };

const fmtRequests = [];
const mergeRequests = [];
const dimRequests = [];
const dvRequests = [];
let cfRequests = [];
let gridValues = null;
const logs = [];

function gridRange(row, col, nr, nc) {
  return { sheetId, startRowIndex: row - 1, endRowIndex: row - 1 + nr, startColumnIndex: col - 1, endColumnIndex: col - 1 + nc };
}
function parseA1(a1) {
  const m = a1.match(/^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$/);
  const colN = s => s.split('').reduce((a, c) => a * 26 + c.charCodeAt(0) - 64, 0);
  const c1 = colN(m[1]), r1 = +m[2];
  const c2 = m[3] ? colN(m[3]) : c1, r2 = m[4] ? +m[4] : r1;
  return [r1, c1, r2 - r1 + 1, c2 - c1 + 1];
}
function fmt(range, cell, fields) {
  fmtRequests.push({ repeatCell: { range, cell: { userEnteredFormat: cell }, fields: 'userEnteredFormat.' + fields } });
}
function mkRange(row, col, nr, nc) {
  const range = gridRange(row, col, nr, nc);
  const self = {
    _grid: range,
    merge() { mergeRequests.push({ mergeCells: { range, mergeType: 'MERGE_ALL' } }); return self; },
    breakApart() { return self; }, clear() { return self; }, clearDataValidations() { return self; },
    setValues(v) { gridValues = v; return self; },
    setBackground(c) { fmt(range, { backgroundColor: hex(c) }, 'backgroundColor'); return self; },
    setFontColor(c) { fmt(range, { textFormat: { foregroundColor: hex(c) } }, 'textFormat.foregroundColor'); return self; },
    setFontWeight(w) { fmt(range, { textFormat: { bold: w === 'bold' } }, 'textFormat.bold'); return self; },
    setFontSize(s) { fmt(range, { textFormat: { fontSize: s } }, 'textFormat.fontSize'); return self; },
    setFontFamily(f) { fmt(range, { textFormat: { fontFamily: f } }, 'textFormat.fontFamily'); return self; },
    setHorizontalAlignment(a) { fmt(range, { horizontalAlignment: HA[a] }, 'horizontalAlignment'); return self; },
    setVerticalAlignment(a) { fmt(range, { verticalAlignment: VA[a] }, 'verticalAlignment'); return self; },
    setWrap(w) { fmt(range, { wrapStrategy: w ? 'WRAP' : 'OVERFLOW_CELL' }, 'wrapStrategy'); return self; },
    setDataValidation(rule) { dvRequests.push({ setDataValidation: { range, rule } }); return self; },
    shiftColumnGroupDepth(delta) {
      const r = { sheetId, dimension: 'COLUMNS', startIndex: range.startColumnIndex, endIndex: range.endColumnIndex };
      dimRequests.push(delta > 0 ? { addDimensionGroup: { range: r } } : { deleteDimensionGroup: { range: r } });
      return self;
    },
    shiftRowGroupDepth(delta) {
      const r = { sheetId, dimension: 'ROWS', startIndex: range.startRowIndex, endIndex: range.endRowIndex };
      dimRequests.push(delta > 0 ? { addDimensionGroup: { range: r } } : { deleteDimensionGroup: { range: r } });
      return self;
    },
    setBorder(top, left, bottom, right, vertical, horizontal) {
      const border = { style: 'SOLID', color: { red: 0, green: 0, blue: 0 } };
      const req = { updateBorders: { range } };
      if (top)        req.updateBorders.top = border;
      if (bottom)     req.updateBorders.bottom = border;
      if (left)       req.updateBorders.left = border;
      if (right)      req.updateBorders.right = border;
      if (vertical)   req.updateBorders.innerVertical = border;
      if (horizontal) req.updateBorders.innerHorizontal = border;
      fmtRequests.push(req);
      return self;
    },
  };
  return self;
}

const sheetObj = {
  getMaxRows: () => 200, getMaxColumns: () => NCOLS,
  getRange(...args) {
    if (args.length === 1 && typeof args[0] === 'string') return mkRange(...parseA1(args[0]));
    return mkRange(args[0], args[1], args[2] || 1, args[3] || 1);
  },
  setConditionalFormatRules(rules) {
    cfRequests = rules.map((rule, index) => ({ addConditionalFormatRule: { rule, index } }));
  },
  setColumnWidth(c, w) {
    dimRequests.push({ updateDimensionProperties: {
      range: { sheetId, dimension: 'COLUMNS', startIndex: c - 1, endIndex: c },
      properties: { pixelSize: w }, fields: 'pixelSize' } });
  },
  setRowHeight(r, h) {
    dimRequests.push({ updateDimensionProperties: {
      range: { sheetId, dimension: 'ROWS', startIndex: r - 1, endIndex: r },
      properties: { pixelSize: h }, fields: 'pixelSize' } });
  },
  setFrozenRows(n) {
    dimRequests.push({ updateSheetProperties: { properties: { sheetId, gridProperties: { frozenRowCount: n } }, fields: 'gridProperties.frozenRowCount' } });
  },
  setFrozenColumns(n) {
    dimRequests.push({ updateSheetProperties: { properties: { sheetId, gridProperties: { frozenColumnCount: n } }, fields: 'gridProperties.frozenColumnCount' } });
  },
  setColumnGroupControlAfter(after) {
    dimRequests.push({ updateSheetProperties: { properties: { sheetId, gridProperties: { columnGroupControlAfter: !!after } }, fields: 'gridProperties.columnGroupControlAfter' } });
  },
  setRowGroupControlAfter(after) {
    dimRequests.push({ updateSheetProperties: { properties: { sheetId, gridProperties: { rowGroupControlAfter: !!after } }, fields: 'gridProperties.rowGroupControlAfter' } });
  },
  autoResizeRows(start, count) {
    dimRequests.push({ autoResizeDimensions: {
      dimensions: { sheetId, dimension: 'ROWS', startIndex: start - 1, endIndex: start - 1 + count }
    } });
  },
};

const ssObj = {
  getSheetByName: n => n === SHEET_NAME ? sheetObj : null,
  insertSheet: () => sheetObj,
  getSheets: () => [sheetObj],
  deleteSheet: () => {},
  getSpreadsheetTimeZone: () => 'Europe/Kyiv',
  getUrl: () => ssUrl,
  getId: () => SPREADSHEET_ID,
};
const folderObj = {
  getFoldersByName: () => ({ hasNext: () => true, next: () => folderObj }),
  getFilesByName: () => ({ hasNext: () => true, next: () => ({}) }),
};
const SpreadsheetApp = {
  open: () => ssObj, create: () => ssObj,
  newDataValidation: () => {
    const rule = { condition: { type: 'ONE_OF_LIST', values: [] }, strict: false, showCustomUi: false };
    const b = {
      requireValueInList(list, dropdown) {
        rule.condition.values = list.map(v => ({ userEnteredValue: v }));
        rule.showCustomUi = !!dropdown; return b;
      },
      setAllowInvalid(allow) { rule.strict = !allow; return b; },
      build: () => rule,
    };
    return b;
  },
  newConditionalFormatRule: () => {
    const rule = { ranges: [], booleanRule: { condition: {}, format: {} } };
    const b = {
      whenTextEqualTo(t) { rule.booleanRule.condition = { type: 'TEXT_EQ', values: [{ userEnteredValue: t }] }; return b; },
      whenTextContains(t) { rule.booleanRule.condition = { type: 'TEXT_CONTAINS', values: [{ userEnteredValue: t }] }; return b; },
      setBackground(c) { rule.booleanRule.format.backgroundColor = hex(c); return b; },
      setFontColor(c) { (rule.booleanRule.format.textFormat ||= {}).foregroundColor = hex(c); return b; },
      setBold(v) { (rule.booleanRule.format.textFormat ||= {}).bold = v; return b; },
      setRanges(ranges) { rule.ranges = ranges.map(r => r._grid); return b; },
      build: () => rule,
    };
    return b;
  },
};
const DriveApp = { getRootFolder: () => folderObj, getFileById: () => ({ moveTo: () => {} }) };
const Session = { getScriptTimeZone: () => 'Europe/Kyiv' };
const Utilities = {
  formatDate: (d, tz, f) => f === 'yyyy'
    ? String(d.getFullYear())
    : d.toLocaleString('en-US', { month: 'long' }) + ' ' + d.getFullYear(),
};
const Logger = { log: s => logs.push(String(s)) };

// ── Execute the generator ───────────────────────────────────────────────
Object.assign(globalThis, { SpreadsheetApp, DriveApp, Session, Utilities, Logger });
const gsCode = readFileSync(GS_PATH, 'utf8');
(0, eval)(gsCode);
globalThis[GENERATOR_FN]();

// ── Flush to the API ──────────────────────────────────────────────────────
await api.spreadsheets.values.update({
  spreadsheetId: SPREADSHEET_ID, range: `${SHEET_NAME}!A1`, valueInputOption: 'USER_ENTERED',
  requestBody: { values: gridValues },
});
console.log('Values written:', gridValues.length, 'rows');

const allRequests = [...mergeRequests, ...fmtRequests, ...dimRequests, ...dvRequests, ...cfRequests];
for (let i = 0; i < allRequests.length; i += 500) {
  await api.spreadsheets.batchUpdate({
    spreadsheetId: SPREADSHEET_ID,
    requestBody: { requests: allRequests.slice(i, i + 500) },
  });
  console.log('Batch', 1 + i / 500, 'of', Math.ceil(allRequests.length / 500), 'applied');
}
console.log(logs.join('\n'));

// ── STEP 5 functional verification (first module band = rows 5..6) ─────────
async function readCells(ranges) {
  const r = await api.spreadsheets.values.batchGet({ spreadsheetId: SPREADSHEET_ID, ranges });
  return r.data.valueRanges.map(v => (v.values && v.values[0] && v.values[0][0]) || '');
}
await api.spreadsheets.values.update({
  spreadsheetId: SPREADSHEET_ID, range: `${SHEET_NAME}!C7`, valueInputOption: 'USER_ENTERED',
  requestBody: { values: [['Failed']] },
});
const probes = [`${SHEET_NAME}!H7`, `${SHEET_NAME}!I6`, `${SHEET_NAME}!I3`, `${SHEET_NAME}!C5`, `${SHEET_NAME}!E3`];
const [h7, i6, i3, c5, e3] = await readCells(probes);
const ok = h7 === 'Failed' && i6 === '1' && i3 === '1'
  && c5 === 'Not all issues are resolved!' && e3 === '1';
console.log('STEP 5 test:', ok ? 'PASSED' : 'FAILED', JSON.stringify({ h7, i6, i3, c5, e3 }));
await api.spreadsheets.values.update({
  spreadsheetId: SPREADSHEET_ID, range: `${SHEET_NAME}!C7`, valueInputOption: 'USER_ENTERED',
  requestBody: { values: [['']] },
});
console.log('URL:', ssUrl);
