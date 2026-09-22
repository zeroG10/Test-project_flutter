/// <reference lib="dom" />
/**
 * In-browser side of the harvester. Every function exported here is passed to
 * `page.evaluate()` / `page.waitForFunction()`, so it MUST be self-contained:
 * no imports used inside the body, no closures over module scope (Playwright
 * serialises the function source and runs it in the page). Selectors are
 * passed in as arguments for the same reason.
 */
import type { HrefKind, Scope, SubStateKind } from './types';

/** Temporary attribute stamped on harvested elements so Node can re-locate them by index. */
export const TAG_ATTR = 'data-recon-i';

export const MESSAGE_SELECTOR = [
  '[role="alert"]',
  '[role="status"]',
  '.ant-message-notice',
  '.ant-notification-notice',
  '.ant-alert',
  '.ant-form-item-explain-error',
  '.ant-result',
].join(', ');

export const EMPTY_STATE_SELECTOR = [
  '.ant-empty',
  '[class*="empty-state" i]',
  '[class*="EmptyState"]',
  '[class*="no-data" i]',
  '[data-testid*="empty" i]',
].join(', ');

/** Icon candidates — kept only when clickable (cursor: pointer) and outside any interactive element. */
export const ICON_SELECTOR = '[role="img"], .anticon, svg';
export const INTERACTIVE_ANCESTOR =
  'button, a[href], label, th, [role="button"], [role="link"], [role="tab"], [role="menuitem"], [role="checkbox"], [role="radio"], [role="switch"], [role="option"], [role="combobox"]';

export const HARVEST_SELECTOR = [
  'button',
  'a[href]',
  'input:not([type="hidden"])',
  'select',
  'textarea',
  '[role="button"]',
  '[role="link"]',
  '[role="tab"]',
  '[role="menuitem"]',
  '[role="menuitemcheckbox"]',
  '[role="menuitemradio"]',
  '[role="checkbox"]',
  '[role="radio"]',
  '[role="switch"]',
  '[role="combobox"]',
  '[role="textbox"]',
  '[role="searchbox"]',
  '[role="option"]',
  '[contenteditable=""]',
  '[contenteditable="true"]',
  '[contenteditable="plaintext-only"]',
  'th',
  'h1',
  'h2',
  'table',
  MESSAGE_SELECTOR,
  EMPTY_STATE_SELECTOR,
  ICON_SELECTOR,
].join(', ');

/** Containers that count as an "open state" (dialog / menu / listbox / drawer …). */
export const OVERLAY_SELECTOR = [
  '[role="dialog"]',
  '[role="alertdialog"]',
  'dialog[open]',
  '[role="menu"]',
  '[role="listbox"]',
  '.ant-modal-wrap',
  '.ant-modal',
  '.ant-drawer',
  '.ant-dropdown',
  '.ant-popover',
  '.ant-popconfirm',
  '.ant-select-dropdown',
  '.ant-picker-dropdown',
].join(', ');

export interface CollectArgs {
  harvestSelector: string;
  overlaySelector: string;
  messageSelector: string;
  emptySelector: string;
  iconSelector: string;
  interactiveAncestor: string;
  tagAttr: string;
  scope: Scope;
  maxElements: number;
}

export interface RawElement {
  index: number;
  tag: string;
  inputType: string | null;
  explicitRole: string | null;
  implicitRole: string | null;
  id: string | null;
  classes: string;
  testId: string | null;
  otherTestAttrs: Record<string, string>;
  ariaLabel: string;
  labelledBy: string;
  labels: string;
  placeholder: string;
  title: string;
  alt: string;
  value: string | null;
  contentText: string;
  text: string;
  disabled: boolean;
  required: boolean;
  editable: boolean;
  isMessage: boolean;
  isEmptyState: boolean;
  isClickableIcon: boolean;
  href: string | null;
  hrefKind: HrefKind;
  hasPopup: boolean;
  expanded: 'true' | 'false' | null;
  selected: boolean;
  inNav: boolean;
  inOverlay: boolean;
  hasInnerRouteLink: boolean;
  inTableRow: boolean;
  formIndex: number | null;
  hint: string;
}

export interface RawFormField {
  tag: string;
  type: string;
  name: string | null;
  label: string | null;
  required: boolean;
}

export interface RawForm {
  index: number;
  hint: string;
  fields: RawFormField[];
  submitText: string | null;
  empty: boolean;
}

export interface RawTable {
  index: number;
  hint: string;
  name: string | null;
  headers: string[];
  rowCount: number;
  firstRowText: string | null;
  firstCellText: string | null;
  empty: boolean;
}

export interface RawHarvest {
  url: string;
  title: string;
  h1: string | null;
  hasRootTestId: boolean;
  elements: RawElement[];
  tables: RawTable[];
  forms: RawForm[];
  truncated: boolean;
  container: { kind: SubStateKind; hint: string } | null;
}

export interface RawAnchor {
  href: string;
  text: string;
}

export interface RawValidationMessage {
  field: string | null;
  message: string;
}

/** Runs in the page. Collects every visible candidate element in `scope` and stamps it with `tagAttr`. */
export function collectInBrowser(args: CollectArgs): RawHarvest {
  const norm = (s: string | null | undefined): string => (s ?? '').replace(/\s+/g, ' ').trim();
  const cap = (s: string, n: number): string => (s.length > n ? `${s.slice(0, n - 1)}…` : s);
  const classesOf = (e: Element): string => e.getAttribute('class') ?? '';
  const hasClass = (e: Element, c: string): boolean => new RegExp(`(^|\\s)${c}(\\s|$)`).test(classesOf(e));

  const isVisible = (el: Element): boolean => {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return false;
    return !el.closest('[aria-hidden="true"]');
  };

  // --- overlays -----------------------------------------------------------
  const isOverlay = (el: Element): boolean => {
    const role = el.getAttribute('role');
    if (role === 'dialog' || role === 'alertdialog' || el.tagName.toLowerCase() === 'dialog') return true;
    if (/(^|\s)ant-(modal-wrap|modal|drawer|dropdown|popover|popconfirm|select-dropdown|picker-dropdown)(\s|$)/.test(classesOf(el)))
      return true;
    if (role === 'menu' || role === 'listbox') {
      const pos = getComputedStyle(el).position;
      const ppos = el.parentElement ? getComputedStyle(el.parentElement).position : 'static';
      return pos === 'absolute' || pos === 'fixed' || ppos === 'absolute' || ppos === 'fixed';
    }
    return false;
  };
  const overlays = Array.from(document.querySelectorAll(args.overlaySelector)).filter((o) => isOverlay(o) && isVisible(o));
  const topOverlays = overlays.filter((o) => !overlays.some((p) => p !== o && p.contains(o)));

  const kindOfContainer = (c: Element): SubStateKind => {
    const role = c.getAttribute('role');
    const cls = classesOf(c);
    if (/(^|\s)ant-drawer(\s|$)/.test(cls)) return 'drawer';
    if (role === 'dialog' || role === 'alertdialog' || c.tagName.toLowerCase() === 'dialog' || /(^|\s)ant-modal(-wrap)?(\s|$)/.test(cls)) return 'dialog';
    if (role === 'menu' || /(^|\s)ant-dropdown(\s|$)/.test(cls)) return 'menu';
    if (role === 'listbox' || /(^|\s)ant-select-dropdown(\s|$)/.test(cls)) return 'listbox';
    if (/(^|\s)ant-(popover|popconfirm|picker-dropdown)(\s|$)/.test(cls)) return 'popover';
    return 'popup';
  };

  // --- hints ----------------------------------------------------------------
  const desc = (e: Element): string => {
    const tag = e.tagName.toLowerCase();
    const id = e.id && !/\d{3,}/.test(e.id) ? `#${e.id}` : '';
    const cls = classesOf(e)
      .split(/\s+/)
      .filter((c) => c && c.length <= 40 && !/^(css-|sc-|jsx-|_)/.test(c) && !/[0-9a-f]{6,}/i.test(c))
      .slice(0, 2)
      .map((c) => `.${c}`)
      .join('');
    return `${tag}${id}${cls}`;
  };
  const LANDMARK =
    'form, table, nav, header, main, aside, footer, section, [role="dialog"], .ant-modal, .ant-drawer, .ant-dropdown, .ant-card, .ant-form-item, .ant-table';
  const hintOf = (el: Element): string => {
    const parts: string[] = [];
    const parent = el.parentElement;
    const landmark = parent ? parent.closest(LANDMARK) : null;
    if (landmark && landmark !== parent) parts.push(`${desc(landmark)} …`);
    if (parent) parts.push(desc(parent));
    parts.push(desc(el));
    return parts.join(' > ');
  };

  // --- scope ------------------------------------------------------------------
  let container: Element | null = null;
  let containerKind: SubStateKind = 'popup';
  if (args.scope === 'overlay') {
    container = topOverlays.length ? topOverlays[topOverlays.length - 1] : null;
    if (container) containerKind = kindOfContainer(container);
  } else if (args.scope === 'tabpanel') {
    const panels = Array.from(document.querySelectorAll('[role="tabpanel"]')).filter(isVisible);
    container = panels.length ? panels[panels.length - 1] : null;
    containerKind = 'tabpanel';
  }
  const empty: RawHarvest = {
    url: location.href,
    title: document.title,
    h1: null,
    hasRootTestId: false,
    elements: [],
    tables: [],
    forms: [],
    truncated: false,
    container: null,
  };
  if (args.scope !== 'page' && !container) return empty;
  const inScope = (el: Element): boolean =>
    container ? container.contains(el) : !overlays.some((o) => o.contains(el));

  // --- name pieces -----------------------------------------------------------
  const NAME_FROM_CONTENT = new Set([
    'button',
    'cell',
    'checkbox',
    'columnheader',
    'gridcell',
    'heading',
    'link',
    'menuitem',
    'menuitemcheckbox',
    'menuitemradio',
    'option',
    'radio',
    'row',
    'rowheader',
    'switch',
    'tab',
    'tooltip',
    'treeitem',
  ]);
  const textOf = (n: Node): string => {
    if (n.nodeType === Node.TEXT_NODE) return n.textContent ?? '';
    if (n.nodeType !== Node.ELEMENT_NODE) return '';
    const e = n as Element;
    if (getComputedStyle(e).display === 'none') return '';
    const al = e.getAttribute('aria-label');
    if (al) return ` ${al} `;
    const tag = e.tagName.toLowerCase();
    if (tag === 'img') return ` ${e.getAttribute('alt') ?? ''} `;
    if (tag === 'svg') {
      const t = e.querySelector('title');
      return t ? ` ${t.textContent ?? ''} ` : '';
    }
    return Array.from(e.childNodes).map(textOf).join('');
  };
  const labelsOf = (el: Element): string => {
    const withLabels = el as HTMLInputElement;
    if ('labels' in withLabels && withLabels.labels) {
      const t = Array.from(withLabels.labels)
        .map((l) => norm(l.textContent))
        .filter(Boolean)
        .join(' ');
      if (t) return t;
    }
    if (el.id) {
      return Array.from(document.querySelectorAll(`label[for="${CSS.escape(el.id)}"]`))
        .map((l) => norm(l.textContent))
        .filter(Boolean)
        .join(' ');
    }
    return '';
  };
  const labelledByOf = (el: Element): string =>
    (el.getAttribute('aria-labelledby') ?? '')
      .split(/\s+/)
      .filter(Boolean)
      .map((id) => norm(document.getElementById(id)?.textContent))
      .filter(Boolean)
      .join(' ');

  const implicitRoleOf = (el: Element, tag: string, inputType: string | null): string | null => {
    switch (tag) {
      case 'button':
        return 'button';
      case 'a':
        return el.hasAttribute('href') ? 'link' : null;
      case 'select': {
        const s = el as HTMLSelectElement;
        return s.multiple || s.size > 1 ? 'listbox' : 'combobox';
      }
      case 'textarea':
        return 'textbox';
      case 'th':
        return el.getAttribute('scope') === 'row' ? 'rowheader' : 'columnheader';
      case 'h1':
      case 'h2':
      case 'h3':
      case 'h4':
      case 'h5':
      case 'h6':
        return 'heading';
      case 'table':
        return 'table';
      case 'input': {
        const list = el.hasAttribute('list');
        switch (inputType) {
          case 'checkbox':
            return 'checkbox';
          case 'radio':
            return 'radio';
          case 'button':
          case 'submit':
          case 'reset':
          case 'image':
            return 'button';
          case 'number':
            return 'spinbutton';
          case 'range':
            return 'slider';
          case 'search':
            return list ? 'combobox' : 'searchbox';
          case 'email':
          case 'tel':
          case 'text':
          case 'url':
          case 'password':
            return list ? 'combobox' : 'textbox';
          default:
            return null;
        }
      }
      default:
        return null;
    }
  };

  const allForms = Array.from(document.querySelectorAll('form'));

  // --- elements ---------------------------------------------------------------
  const all = Array.from(document.querySelectorAll(args.harvestSelector));
  const elements: RawElement[] = [];
  let truncated = false;
  const isIconCandidate = (el: Element): boolean => el.matches(args.iconSelector);
  const isClickableIcon = (el: Element): boolean => {
    if (el.closest(args.interactiveAncestor)) return false;
    if (el.parentElement && isIconCandidate(el.parentElement)) return false; // svg inside the icon span: count the span once
    const cursor = getComputedStyle(el).cursor;
    const parentCursor = el.parentElement ? getComputedStyle(el.parentElement).cursor : '';
    return cursor === 'pointer' || parentCursor === 'pointer';
  };
  all.forEach((el, index) => {
    if (truncated) return;
    if (!inScope(el) || !isVisible(el)) return;
    const iconCandidate = isIconCandidate(el);
    if (iconCandidate && !isClickableIcon(el)) return; // decorative icon, or part of a button/link
    if (elements.length >= args.maxElements) {
      truncated = true;
      return;
    }
    el.setAttribute(args.tagAttr, String(index));

    const tag = el.tagName.toLowerCase();
    const input = el as HTMLInputElement;
    const inputType = tag === 'input' ? (input.type || 'text').toLowerCase() : null;
    const explicitRole = el.getAttribute('role');
    const implicitRole = implicitRoleOf(el, tag, inputType);
    const role = explicitRole ?? implicitRole;
    const otherTestAttrs: Record<string, string> = {};
    for (const a of ['data-test-id', 'data-test', 'data-qa', 'data-cy', 'data-automation-id', 'data-e2e']) {
      const v = el.getAttribute(a);
      if (v) otherTestAttrs[a] = v;
    }
    const isButtonInput = tag === 'input' && (inputType === 'button' || inputType === 'submit' || inputType === 'reset');
    const isFieldLike = tag === 'input' || tag === 'select' || tag === 'textarea';
    const hrefAttr = tag === 'a' ? el.getAttribute('href') : null;
    let hrefKind: HrefKind = 'none';
    if (hrefAttr !== null) {
      if (/^javascript:/i.test(hrefAttr)) hrefKind = 'js';
      else if (/^#(?!\/)/.test(hrefAttr) || hrefAttr === '') hrefKind = 'hash';
      else if (/^(mailto|tel|sms):/i.test(hrefAttr)) hrefKind = 'external';
      else hrefKind = 'route';
    }
    const popup = el.getAttribute('aria-haspopup');
    const expandedAttr = el.getAttribute('aria-expanded');
    const formEl = el.closest('form');
    const editable = el.hasAttribute('contenteditable') && el.getAttribute('contenteditable') !== 'false';
    const contentText = role && NAME_FROM_CONTENT.has(role) ? norm(textOf(el)) : '';
    const innerText = (el as HTMLElement).innerText;
    elements.push({
      index,
      tag,
      inputType,
      explicitRole,
      implicitRole,
      id: el.id || null,
      classes: classesOf(el),
      testId: el.getAttribute('data-testid'),
      otherTestAttrs,
      ariaLabel: norm(el.getAttribute('aria-label')),
      labelledBy: labelledByOf(el),
      labels: labelsOf(el),
      placeholder: norm(el.getAttribute('placeholder')),
      title: norm(el.getAttribute('title')),
      alt: norm(el.getAttribute('alt')),
      value: isButtonInput ? norm(input.value) : null,
      contentText,
      text: isFieldLike || tag === 'table' ? '' : cap(norm(typeof innerText === 'string' ? innerText : el.textContent), 120),
      disabled:
        (el as HTMLButtonElement).disabled === true ||
        el.getAttribute('aria-disabled') === 'true' ||
        !!el.closest('fieldset:disabled'),
      required: input.required === true || el.getAttribute('aria-required') === 'true',
      editable,
      isMessage: el.matches(args.messageSelector),
      isEmptyState: el.matches(args.emptySelector),
      isClickableIcon: iconCandidate,
      href: tag === 'a' ? (el as HTMLAnchorElement).href : null,
      hrefKind,
      hasPopup: !!popup && popup !== 'false',
      expanded: expandedAttr === 'true' ? 'true' : expandedAttr === 'false' ? 'false' : null,
      selected: el.getAttribute('aria-selected') === 'true',
      inNav: !!el.closest(
        'nav, header, aside, [role="navigation"], [role="menubar"], .ant-menu, .ant-layout-sider, .ant-layout-header',
      ),
      inOverlay: overlays.some((o) => o.contains(el)),
      hasInnerRouteLink: tag !== 'a' && !!el.querySelector('a[href]:not([href^="#"]):not([href^="javascript:"])'),
      inTableRow: !!el.closest('tbody tr'),
      formIndex: formEl ? allForms.indexOf(formEl) : null,
      hint: hintOf(el),
    });
  });

  // --- forms ------------------------------------------------------------------
  const forms: RawForm[] = [];
  allForms.forEach((form, index) => {
    if (!inScope(form) || !isVisible(form)) return;
    const fieldEls = Array.from(
      form.querySelectorAll(
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]), select, textarea',
      ),
    ).filter(isVisible);
    const fields: RawFormField[] = fieldEls.map((f) => {
      const fi = f as HTMLInputElement;
      const ftag = f.tagName.toLowerCase();
      return {
        tag: ftag,
        type: ftag === 'input' ? (fi.type || 'text').toLowerCase() : ftag,
        name: f.getAttribute('name'),
        label: labelsOf(f) || norm(f.getAttribute('aria-label')) || norm(f.getAttribute('placeholder')) || null,
        required: fi.required === true || f.getAttribute('aria-required') === 'true',
      };
    });
    const isEmpty = fieldEls.every((f) => {
      const fi = f as HTMLInputElement;
      const ftag = f.tagName.toLowerCase();
      if (ftag === 'input' && (fi.type === 'checkbox' || fi.type === 'radio')) return !fi.checked;
      if (ftag === 'select') return (f as HTMLSelectElement).selectedIndex <= 0;
      return norm(fi.value) === '';
    });
    const submit =
      Array.from(form.querySelectorAll('button[type="submit"], input[type="submit"]')).find(isVisible) ??
      Array.from(form.querySelectorAll('.ant-btn-primary, button')).find(isVisible) ??
      null;
    forms.push({
      index,
      hint: hintOf(form),
      fields,
      submitText: submit ? norm(textOf(submit)) || norm((submit as HTMLInputElement).value) || null : null,
      empty: isEmpty,
    });
  });

  // --- tables -----------------------------------------------------------------
  const tables: RawTable[] = [];
  Array.from(document.querySelectorAll('table')).forEach((t, index) => {
    if (!inScope(t) || !isVisible(t)) return;
    let headers = Array.from(t.querySelectorAll('thead th')).map((th) => norm(th.textContent));
    if (headers.length === 0) {
      const first = t.querySelector('tr');
      headers = first ? Array.from(first.querySelectorAll('th, td')).map((c) => norm(c.textContent)) : [];
    }
    const rows = Array.from(t.querySelectorAll('tbody tr')).filter(
      (tr) => !hasClass(tr, 'ant-table-measure-row') && !hasClass(tr, 'ant-table-placeholder') && isVisible(tr),
    );
    const firstCells = rows.length ? Array.from(rows[0].querySelectorAll('td, th')).map((c) => norm(c.textContent)) : [];
    const caption = t.querySelector('caption');
    tables.push({
      index,
      hint: hintOf(t),
      name: norm(caption?.textContent) || norm(t.getAttribute('aria-label')) || labelledByOf(t) || null,
      headers,
      rowCount: rows.length,
      firstRowText: firstCells.length ? cap(firstCells.slice(0, 3).join(' | '), 120) : null,
      firstCellText: firstCells.find((c) => c.length > 0) ?? null,
      empty: rows.length === 0 || !!t.querySelector('.ant-empty'),
    });
  });

  const h1 = Array.from(document.querySelectorAll('h1, [role="heading"][aria-level="1"]')).find(isVisible);
  return {
    url: location.href,
    title: document.title,
    h1: h1 ? norm((h1 as HTMLElement).innerText ?? h1.textContent) || null : null,
    hasRootTestId: !!document.querySelector('[data-testid$="-root"]'),
    elements,
    tables,
    forms,
    truncated,
    container: container ? { kind: containerKind, hint: hintOf(container) } : null,
  };
}

/** Runs in the page. Every anchor (visible or not — collapsed menus still hold real routes). */
export function extractAnchorsInBrowser(): RawAnchor[] {
  return Array.from(document.querySelectorAll('a[href]')).map((a) => ({
    href: (a as HTMLAnchorElement).href,
    text: (a.getAttribute('aria-label') ?? a.textContent ?? '').replace(/\s+/g, ' ').trim().slice(0, 60),
  }));
}

/** Runs in the page. Number of visible overlay containers (dialog/menu/listbox/drawer …). */
export function overlayCountInBrowser(overlaySelector: string): number {
  const classesOf = (e: Element): string => e.getAttribute('class') ?? '';
  const isVisible = (el: Element): boolean => {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return false;
    return !el.closest('[aria-hidden="true"]');
  };
  const isOverlay = (el: Element): boolean => {
    const role = el.getAttribute('role');
    if (role === 'dialog' || role === 'alertdialog' || el.tagName.toLowerCase() === 'dialog') return true;
    if (/(^|\s)ant-(modal-wrap|modal|drawer|dropdown|popover|popconfirm|select-dropdown|picker-dropdown)(\s|$)/.test(classesOf(el)))
      return true;
    if (role === 'menu' || role === 'listbox') {
      const pos = getComputedStyle(el).position;
      const ppos = el.parentElement ? getComputedStyle(el.parentElement).position : 'static';
      return pos === 'absolute' || pos === 'fixed' || ppos === 'absolute' || ppos === 'fixed';
    }
    return false;
  };
  const overlays = Array.from(document.querySelectorAll(overlaySelector)).filter((o) => isOverlay(o) && isVisible(o));
  return overlays.filter((o) => !overlays.some((p) => p !== o && p.contains(o))).length;
}

/** Runs in the page. Visible validation / alert messages with the field they belong to. */
export function validationMessagesInBrowser(messageSelector: string): RawValidationMessage[] {
  const norm = (s: string | null | undefined): string => (s ?? '').replace(/\s+/g, ' ').trim();
  const isVisible = (el: Element): boolean => {
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const out: RawValidationMessage[] = [];
  const seen = new Set<string>();
  for (const el of Array.from(document.querySelectorAll(messageSelector)).filter(isVisible)) {
    const message = norm(el.textContent);
    if (!message) continue;
    const item = el.closest('.ant-form-item');
    const label = item ? norm(item.querySelector('label')?.textContent) : '';
    const key = `${label}|${message}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ field: label || null, message });
  }
  for (const f of Array.from(document.querySelectorAll('[aria-invalid="true"]')).filter(isVisible)) {
    const described = (f.getAttribute('aria-describedby') ?? '')
      .split(/\s+/)
      .map((id) => norm(document.getElementById(id)?.textContent))
      .filter(Boolean)
      .join(' ');
    if (!described) continue;
    const withLabels = f as HTMLInputElement;
    const label =
      'labels' in withLabels && withLabels.labels
        ? Array.from(withLabels.labels)
            .map((l) => norm(l.textContent))
            .join(' ')
        : '';
    const key = `${label}|${described}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ field: label || null, message: described });
  }
  // Native constraint validation (required / pattern / type): the browser shows a tooltip
  // that never reaches the DOM — read the message off the field instead.
  for (const f of Array.from(document.querySelectorAll('form :invalid')).filter(isVisible)) {
    const fi = f as HTMLInputElement;
    const message = norm(fi.validationMessage);
    if (!message) continue;
    const label =
      'labels' in fi && fi.labels
        ? Array.from(fi.labels)
            .map((l) => norm(l.textContent))
            .join(' ')
        : '';
    const key = `${label}|${message}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ field: label || fi.name || null, message: `${message} (native constraint validation, not in the DOM)` });
  }
  return out;
}

/** Runs in the page. Removes the temporary tag attribute. */
export function untagInBrowser(tagAttr: string): void {
  document.querySelectorAll(`[${tagAttr}]`).forEach((e) => e.removeAttribute(tagAttr));
}
