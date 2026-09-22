import type { ElementKind, HarvestedElement } from './types';

/** `Forgot password?` → `forgot-password`; strips diacritics, keeps ASCII a-z0-9. */
export function kebab(s: string): string {
  return s
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function camel(slug: string): string {
  const parts = kebab(slug).split('-').filter(Boolean);
  const out = parts.map((p, i) => (i === 0 ? p : p.charAt(0).toUpperCase() + p.slice(1))).join('');
  const safe = out.replace(/[^A-Za-z0-9_$]/g, '');
  if (!safe) return 'screen';
  return /^[0-9]/.test(safe) ? `s${safe}` : safe;
}

export function pascal(slug: string): string {
  const c = camel(slug);
  return c.charAt(0).toUpperCase() + c.slice(1);
}

/** `/surveys/:id/edit` → `surveys-id-edit`, `/` → `home`, `/todomvc/#/active` → `todomvc-active`. */
export function slugFromPattern(pattern: string): string {
  const s = kebab(pattern.replace(/:id/g, 'id').replace(/[?&=#]/g, ' '));
  return (s || 'home').slice(0, 60).replace(/-+$/, '');
}

const WIDGET_TAIL = new Set([
  'button',
  'btn',
  'input',
  'field',
  'link',
  'icon',
  'checkbox',
  'dropdown',
  'selector',
  'menu',
  'toggle',
  'textbox',
  'textarea',
  'box',
]);
// Deliberately short: prepositions stay ("Log in" → log-in, "Back to Login" → back-to-login).
const STOP_WORDS = new Set(['the', 'a', 'an', 'your', 'my', 'please']);
const INPUT_LEAD_VERBS = new Set(['enter', 'type', 'input', 'choose', 'select', 'pick', 'write', 'fill']);
const INPUT_KINDS = new Set<ElementKind>(['textbox', 'combobox', 'listbox', 'editable', 'checkbox', 'radio', 'switch']);

const KIND_SUFFIX: Record<ElementKind, string> = {
  button: 'button',
  link: 'link',
  textbox: 'input',
  checkbox: 'checkbox',
  radio: 'radio',
  switch: 'switch',
  tab: 'tab',
  menuitem: 'menu-item',
  combobox: 'select',
  listbox: 'list',
  option: 'option',
  editable: 'editor',
  columnheader: 'column',
  icon: 'icon',
  heading: 'heading',
  alert: 'alert',
  status: 'status',
  'empty-state': 'empty-state',
  table: 'table',
  other: 'element',
};

type AliasSource = Pick<HarvestedElement, 'kind' | 'testId' | 'name' | 'label' | 'placeholder' | 'text'>;

/** Purpose-word alias: `save-button` → `save`, `Enter your email` → `email`. */
export function aliasBase(el: AliasSource, screenSlug: string): string {
  let source: string;
  if (el.testId) {
    source = el.testId;
    const prefix = `${screenSlug}-`;
    if (source.startsWith(prefix) && source.length > prefix.length) source = source.slice(prefix.length);
  } else if (el.name && el.text && el.name !== el.text && el.name.includes(el.text) && el.text.length >= 3) {
    // The accessible name carries extra icon labels ("left Back to Login"); the visible
    // text is the purpose ("Back to Login"). The locator still uses the full name.
    source = el.text;
  } else {
    source = el.name || el.label || el.placeholder || el.text || '';
  }
  let tokens = kebab(source).split('-').filter(Boolean);
  if (!el.testId) {
    tokens = tokens.filter((t) => !STOP_WORDS.has(t));
    if (INPUT_KINDS.has(el.kind)) {
      while (tokens.length > 1 && INPUT_LEAD_VERBS.has(tokens[0])) tokens.shift();
    }
    while (tokens.length > 1 && WIDGET_TAIL.has(tokens[tokens.length - 1])) tokens.pop();
    tokens = tokens.slice(0, 5);
  }
  if (tokens.length === 0) return el.kind;
  let alias = tokens.join('-');
  if (alias.length > 40) alias = alias.slice(0, 40).replace(/-+$/, '');
  return /^[0-9]/.test(alias) ? `${KIND_SUFFIX[el.kind]}-${alias}` : alias;
}

/**
 * Assigns `el.alias` for every element: purpose word first, a kind suffix on
 * collision (`search-input` / `search-button`), a numeric suffix only when that
 * still collides. `reserved` seeds the taken set (e.g. aliases of the base state).
 */
export function assignAliases(elements: HarvestedElement[], screenSlug: string, reserved?: ReadonlySet<string>): void {
  const bases = elements.map((el) => aliasBase(el, screenSlug));
  const groups = new Map<string, number[]>();
  bases.forEach((b, i) => groups.set(b, [...(groups.get(b) ?? []), i]));
  const used = new Set<string>(reserved ?? []);
  const claim = (candidate: string): string | null => {
    if (used.has(candidate)) return null;
    used.add(candidate);
    return candidate;
  };
  elements.forEach((el, i) => {
    const base = bases[i];
    const group = groups.get(base) ?? [i];
    const kindsInGroup = new Set(group.map((j) => elements[j].kind));
    // Same purpose word, different widgets → kind suffix (search-input / search-button).
    // Same purpose word, same widget → numeric suffix (edit, edit-2): nothing else tells them apart.
    const suffix = KIND_SUFFIX[el.kind];
    const candidate = group.length > 1 && kindsInGroup.size > 1 && !base.endsWith(`-${suffix}`) ? `${base}-${suffix}` : base;
    let alias = claim(candidate);
    let n = 2;
    while (alias === null) alias = claim(`${candidate}-${n++}`);
    el.alias = alias;
  });
}
