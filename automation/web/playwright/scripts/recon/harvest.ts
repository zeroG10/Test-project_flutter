import type { Locator, Page } from '@playwright/test';
import type { ElementSpec } from '../../screens/resolve';
import { assignAliases } from './aliases';
import {
  EMPTY_STATE_SELECTOR,
  HARVEST_SELECTOR,
  ICON_SELECTOR,
  INTERACTIVE_ANCESTOR,
  MESSAGE_SELECTOR,
  OVERLAY_SELECTOR,
  TAG_ATTR,
  collectInBrowser,
  type RawElement,
  type RawHarvest,
} from './browser-harvest';
import type {
  Alternative,
  ElementKind,
  Gap,
  Harvest,
  HarvestedElement,
  NameSource,
  Scope,
  Strategy,
  TableInfo,
} from './types';

type AriaRole = Parameters<Page['getByRole']>[0];

/** Every role `page.getByRole()` accepts — typed so tsc rejects a typo. */
const ARIA_ROLES: readonly AriaRole[] = [
  'alert', 'alertdialog', 'application', 'article', 'banner', 'blockquote', 'button', 'caption', 'cell',
  'checkbox', 'code', 'columnheader', 'combobox', 'complementary', 'contentinfo', 'definition', 'deletion',
  'dialog', 'directory', 'document', 'emphasis', 'feed', 'figure', 'form', 'generic', 'grid', 'gridcell',
  'group', 'heading', 'img', 'insertion', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee',
  'math', 'meter', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation', 'none',
  'note', 'option', 'paragraph', 'presentation', 'progressbar', 'radio', 'radiogroup', 'region', 'row',
  'rowgroup', 'rowheader', 'scrollbar', 'search', 'searchbox', 'separator', 'slider', 'spinbutton', 'status',
  'strong', 'subscript', 'superscript', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox',
  'time', 'timer', 'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem',
];
const ROLE_SET = new Set<string>(ARIA_ROLES);
const MEANINGLESS_ROLES = new Set(['generic', 'none', 'presentation']);
/** Roles that are a sensible locator even without an accessible name (when unique on the page). */
const UNNAMED_ROLE_OK = new Set(['alert', 'status', 'table', 'dialog', 'alertdialog', 'searchbox', 'tabpanel']);

const MAX_ELEMENTS = 250;
const MAX_NAME_LENGTH = 150;
const MAX_TEXT_LENGTH = 80;

export function isAriaRole(role: string): role is AriaRole {
  return ROLE_SET.has(role);
}

export function taggedLocator(page: Page, index: number): Locator {
  return page.locator(`[${TAG_ATTR}="${index}"]`);
}

/** Runs the in-browser collector (also re-stamps the tag attribute — call it to "retag" after a reload). */
export async function collectRaw(page: Page, scope: Scope): Promise<RawHarvest> {
  return page.evaluate(collectInBrowser, {
    harvestSelector: HARVEST_SELECTOR,
    overlaySelector: OVERLAY_SELECTOR,
    messageSelector: MESSAGE_SELECTOR,
    emptySelector: EMPTY_STATE_SELECTOR,
    iconSelector: ICON_SELECTOR,
    interactiveAncestor: INTERACTIVE_ANCESTOR,
    tagAttr: TAG_ATTR,
    scope,
    maxElements: MAX_ELEMENTS,
  });
}

const SNAPSHOT_LINE = /^- ([a-z]+)(?: "((?:[^"\\]|\\.)*)")?/;

/**
 * Role + accessible name exactly as Playwright computes them: the first line of the
 * element's own aria snapshot (`- button "Sign in"`). Null when the element has no
 * role of its own (the snapshot would start with a descendant).
 */
async function playwrightRoleName(page: Page, raw: RawElement): Promise<{ role: string; name: string } | null> {
  if (!raw.explicitRole && !raw.implicitRole) return null;
  try {
    const yaml = await taggedLocator(page, raw.index).ariaSnapshot({ timeout: 2000 });
    const first = yaml.split('\n').find((l) => l.trim().length > 0) ?? '';
    const m = SNAPSHOT_LINE.exec(first.trim());
    if (!m) return null;
    const role = m[1];
    if (role === 'text' || MEANINGLESS_ROLES.has(role)) return null;
    const name = (m[2] ?? '').replace(/\\(["\\])/g, '$1');
    return { role, name };
  } catch {
    return null;
  }
}

function resolveName(raw: RawElement, pwName: string | null): { name: string; source: NameSource } {
  const candidates: [NameSource, string][] = [
    ['aria-labelledby', raw.labelledBy],
    ['aria-label', raw.ariaLabel],
    ['label', raw.labels],
    ['value', raw.value ?? ''],
    ['alt', raw.alt],
    ['content', raw.contentText],
    ['title', raw.title],
    ['placeholder', raw.placeholder],
  ];
  if (pwName !== null) {
    if (!pwName) return { name: '', source: 'none' };
    const hit = candidates.find(([, v]) => v && v === pwName);
    return { name: pwName, source: hit ? hit[0] : 'content' };
  }
  const first = candidates.find(([, v]) => v.length > 0);
  return first ? { name: first[1], source: first[0] } : { name: '', source: 'none' };
}

function kindOf(raw: RawElement, role: string | null): ElementKind {
  switch (role) {
    case 'button':
      return 'button';
    case 'link':
      return 'link';
    case 'textbox':
    case 'searchbox':
    case 'spinbutton':
      return 'textbox';
    case 'checkbox':
      return 'checkbox';
    case 'radio':
      return 'radio';
    case 'switch':
      return 'switch';
    case 'tab':
      return 'tab';
    case 'menuitem':
    case 'menuitemcheckbox':
    case 'menuitemradio':
      return 'menuitem';
    case 'combobox':
      return 'combobox';
    case 'listbox':
      return 'listbox';
    case 'option':
      return 'option';
    case 'columnheader':
    case 'rowheader':
      return 'columnheader';
    case 'heading':
      return 'heading';
    case 'alert':
    case 'alertdialog':
      return 'alert';
    case 'status':
    case 'log':
      return 'status';
    case 'table':
    case 'grid':
    case 'treegrid':
      return 'table';
    default:
      break;
  }
  if (raw.isClickableIcon) return 'icon';
  if (raw.isEmptyState) return 'empty-state';
  if (raw.isMessage) return 'alert';
  if (raw.editable) return 'editable';
  if (raw.tag === 'input') return raw.inputType === 'checkbox' ? 'checkbox' : raw.inputType === 'radio' ? 'radio' : 'textbox';
  if (raw.tag === 'select') return 'combobox';
  if (raw.tag === 'textarea') return 'textbox';
  if (raw.tag === 'th') return 'columnheader';
  if (raw.tag === 'h1' || raw.tag === 'h2') return 'heading';
  if (raw.tag === 'table') return 'table';
  return 'other';
}

interface SpecResult {
  spec: ElementSpec | null;
  via: string | null;
  unique: boolean;
  alternatives: Alternative[];
}

/**
 * Locator priority: data-testid → role + accessible name → label → (placeholder,
 * recorded only) → visible text. Each candidate is verified for uniqueness with the
 * same Playwright call `locate()` will make; the first unique one wins.
 */
async function bestSpec(page: Page, raw: RawElement, role: string | null, name: string, source: NameSource, kind: ElementKind): Promise<SpecResult> {
  const alternatives: Alternative[] = [];
  const tryCount = async (strategy: Strategy, value: string, loc: Locator, note?: string): Promise<number> => {
    let count = -1;
    try {
      count = await loc.count();
    } catch {
      count = -1;
    }
    alternatives.push(note ? { strategy, value, count, note } : { strategy, value, count });
    return count;
  };
  const done = (spec: ElementSpec, via: string): SpecResult => ({ spec, via, unique: true, alternatives });

  if (raw.testId) {
    const c = await tryCount('testId', raw.testId, page.getByTestId(raw.testId));
    if (c === 1) return done({ testId: raw.testId }, 'testId');
  }
  const roleOk = role !== null && isAriaRole(role) && !MEANINGLESS_ROLES.has(role);
  if (roleOk && name && name.length <= MAX_NAME_LENGTH) {
    const c = await tryCount('role', `${role} "${name}"`, page.getByRole(role, { name, exact: true }));
    if (c === 1) return done({ role, name, exact: true }, source === 'placeholder' ? 'role+name(placeholder)' : 'role+name');
    if (c === 0) {
      const loose = await tryCount('role', `${role} ~"${name}"`, page.getByRole(role, { name }), 'exact name did not match — substring, case-insensitive');
      if (loose === 1) return done({ role, name, exact: false }, 'role+name(loose)');
    }
  } else if (roleOk && !name && UNNAMED_ROLE_OK.has(role)) {
    const c = await tryCount('role', role, page.getByRole(role));
    if (c === 1) return done({ role }, 'role');
  }
  const label = raw.labels || raw.ariaLabel || raw.labelledBy;
  if (label) {
    const c = await tryCount('label', label, page.getByLabel(label, { exact: true }));
    if (c === 1) return done({ label, exact: true }, 'label');
  }
  if (raw.placeholder) {
    await tryCount('placeholder', raw.placeholder, page.getByPlaceholder(raw.placeholder, { exact: true }), 'no ElementSpec shape for placeholder — recorded only');
  }
  const text = raw.text;
  if (text && text.length <= MAX_TEXT_LENGTH && kind !== 'textbox' && kind !== 'combobox' && kind !== 'listbox' && kind !== 'table') {
    const c = await tryCount('text', text, page.getByText(text, { exact: true }));
    if (c === 1) return done({ text, exact: true }, 'text');
  }
  return { spec: null, via: null, unique: false, alternatives };
}

const WEAK_TEXT_KINDS = new Set<ElementKind>(['alert', 'status', 'empty-state', 'other', 'editable', 'option', 'menuitem', 'tab']);

function classifyGap(el: HarvestedElement, screenSlug: string): Gap | null {
  const suggestedTestId = `${screenSlug}-${el.alias}`;
  if (el.kind === 'icon') {
    return el.spec
      ? { severity: 'weak', reason: 'clickable icon exposed as role=img — needs role="button" + an id (contract §2.7)', suggestedTestId }
      : { severity: 'blocking', reason: 'clickable icon with no role, name or id', suggestedTestId };
  }
  if (!el.spec) {
    const dup = el.alternatives.find((a) => a.count > 1);
    let reason: string;
    if (dup && dup.strategy === 'testId') reason = `data-testid="${dup.value}" is shared by ${dup.count} elements — ids must be unique per screen`;
    else if (dup) reason = `${dup.strategy === 'role' ? 'role+name' : dup.strategy} matches ${dup.count} elements`;
    else if (!el.name && !el.text) reason = 'no accessible name and no text';
    else if (!el.role || MEANINGLESS_ROLES.has(el.role)) reason = 'no role — only text, and the text is not unique';
    else reason = 'no strategy resolved to exactly one element';
    if (el.flags.inRow) {
      const action = el.alias.replace(/-\d+$/, '');
      return {
        severity: 'blocking',
        reason: `${reason} — inside a table row, non-unique by design; needs a row-scoped id (contract §2.4)`,
        suggestedTestId: `${screenSlug}-row-<entityId>-${action}`,
      };
    }
    return { severity: 'blocking', reason, suggestedTestId };
  }
  if (el.via === 'text' && WEAK_TEXT_KINDS.has(el.kind)) {
    return { severity: 'weak', reason: 'text-only locator (contract §2.5/§2.7: needs an id)', suggestedTestId };
  }
  if (el.via === 'text') return { severity: 'weak', reason: 'text-only locator (copy-fragile)', suggestedTestId };
  if (el.via === 'role+name(placeholder)') return { severity: 'weak', reason: 'name comes from the placeholder (copy-fragile)', suggestedTestId };
  if (el.via === 'role+name(loose)') return { severity: 'weak', reason: 'exact accessible name did not match — locator uses a substring', suggestedTestId };
  if ((el.kind === 'alert' || el.kind === 'status' || el.kind === 'empty-state') && el.via !== 'testId') {
    return { severity: 'weak', reason: 'message/empty state without data-testid (contract §2.5)', suggestedTestId };
  }
  return null;
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function toTableInfo(raw: RawHarvest['tables'][number]): TableInfo {
  const entity = raw.firstCellText ? escapeRegex(raw.firstCellText.slice(0, 40)) : '<entity text>';
  return {
    index: raw.index,
    hint: raw.hint,
    name: raw.name,
    headers: raw.headers,
    rowCount: raw.rowCount,
    firstRowText: raw.firstRowText,
    empty: raw.empty,
    rowTemplate: `page.getByRole('row', { name: /${entity}/ })`,
  };
}

export interface HarvestOptions {
  deadline: number;
  /** Aliases already taken (when merging into an existing harvest). */
  reserved?: ReadonlySet<string>;
}

/**
 * Harvest one state of the page: collect candidates in the browser, ask Playwright for
 * the true role/name of each, rank locators, verify uniqueness, assign aliases, flag gaps.
 * `screenSlug` is the `<screen>` prefix of suggested test ids.
 */
export async function harvestScope(page: Page, scope: Scope, screenSlug: string, opts: HarvestOptions): Promise<Harvest> {
  const raw = await collectRaw(page, scope);
  const elements: HarvestedElement[] = [];
  for (const r of raw.elements) {
    if (Date.now() > opts.deadline) break;
    const pw = await playwrightRoleName(page, r);
    const role = pw?.role ?? r.explicitRole ?? r.implicitRole;
    const kind = kindOf(r, role);
    const { name, source } = resolveName(r, pw ? pw.name : null);
    const ranked = await bestSpec(page, r, role, name, source, kind);
    const notes: string[] = [];
    if (name && r.text && name !== r.text && name.includes(r.text)) notes.push(`name includes icon label(s); visible text is "${r.text}"`);
    if (r.otherTestAttrs['data-test-id'] || r.otherTestAttrs['data-test'] || r.otherTestAttrs['data-qa'] || r.otherTestAttrs['data-cy']) {
      notes.push(`has ${Object.keys(r.otherTestAttrs).join('/')} but no data-testid`);
    }
    elements.push({
      index: r.index,
      kind,
      tag: r.tag,
      inputType: r.inputType,
      role,
      name,
      nameSource: source,
      testId: r.testId,
      otherTestAttrs: r.otherTestAttrs,
      label: r.labels || r.labelledBy || r.ariaLabel || null,
      placeholder: r.placeholder || null,
      text: r.text,
      disabled: r.disabled,
      hint: r.hint,
      href: r.href,
      flags: {
        inNav: r.inNav,
        inOverlay: r.inOverlay,
        hrefKind: r.hrefKind,
        hasPopup: r.hasPopup,
        expanded: r.expanded,
        selected: r.selected,
        hasInnerRouteLink: r.hasInnerRouteLink,
        inRow: r.inTableRow,
      },
      alias: '',
      spec: ranked.spec,
      via: ranked.via,
      unique: ranked.unique,
      alternatives: ranked.alternatives,
      gap: null,
      notes,
    });
  }
  assignAliases(elements, screenSlug, opts.reserved);
  for (const el of elements) el.gap = classifyGap(el, screenSlug);
  return {
    url: raw.url,
    title: raw.title,
    h1: raw.h1,
    hasRootTestId: raw.hasRootTestId,
    elements,
    tables: raw.tables.map(toTableInfo),
    forms: raw.forms.map((f) => ({ index: f.index, hint: f.hint, fields: f.fields, submitText: f.submitText, empty: f.empty })),
    truncated: raw.truncated,
    container: raw.container,
  };
}

export function countGaps(h: Harvest): number {
  return h.elements.filter((e) => e.gap !== null).length;
}
