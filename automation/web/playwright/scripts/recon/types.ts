import type { ElementSpec } from '../../screens/resolve';

/** Which part of the DOM a harvest looks at. */
export type Scope = 'page' | 'overlay' | 'tabpanel';

export type ElementKind =
  | 'button'
  | 'link'
  | 'textbox'
  | 'checkbox'
  | 'radio'
  | 'switch'
  | 'tab'
  | 'menuitem'
  | 'combobox'
  | 'listbox'
  | 'option'
  | 'editable'
  | 'columnheader'
  /** Clickable icon (cursor: pointer) with no interactive role — a testability gap by definition. */
  | 'icon'
  | 'heading'
  | 'alert'
  | 'status'
  | 'empty-state'
  | 'table'
  | 'other';

export const INTERACTIVE_KINDS: ReadonlySet<ElementKind> = new Set<ElementKind>([
  'button',
  'link',
  'textbox',
  'checkbox',
  'radio',
  'switch',
  'tab',
  'menuitem',
  'combobox',
  'listbox',
  'option',
  'editable',
  'icon',
]);

export type NameSource =
  | 'aria-labelledby'
  | 'aria-label'
  | 'label'
  | 'content'
  | 'title'
  | 'placeholder'
  | 'value'
  | 'alt'
  | 'none';

export type Strategy = 'testId' | 'role' | 'label' | 'placeholder' | 'text';

export interface Alternative {
  strategy: Strategy;
  value: string;
  count: number;
  note?: string;
}

export type GapSeverity = 'blocking' | 'weak';

export interface Gap {
  severity: GapSeverity;
  reason: string;
  suggestedTestId: string;
}

export type HrefKind = 'route' | 'hash' | 'js' | 'external' | 'none';

export interface ElementFlags {
  inNav: boolean;
  inOverlay: boolean;
  hrefKind: HrefKind;
  hasPopup: boolean;
  expanded: 'true' | 'false' | null;
  selected: boolean;
  hasInnerRouteLink: boolean;
  /** Inside a <tbody> row: non-unique by design → needs a row-scoped id (contract §2.4). */
  inRow: boolean;
}

export interface HarvestedElement {
  /** Position in the document-order harvest query; also the value of the temporary tag attribute. */
  index: number;
  kind: ElementKind;
  tag: string;
  inputType: string | null;
  /** Role as Playwright computes it (from ariaSnapshot) or the implicit role. */
  role: string | null;
  /** Accessible name as Playwright computes it. */
  name: string;
  nameSource: NameSource;
  testId: string | null;
  otherTestAttrs: Record<string, string>;
  label: string | null;
  placeholder: string | null;
  text: string;
  disabled: boolean;
  hint: string;
  href: string | null;
  flags: ElementFlags;
  alias: string;
  /** Best UNIQUE locator in the shape `locate()` understands, or null → gap. */
  spec: ElementSpec | null;
  via: string | null;
  unique: boolean;
  alternatives: Alternative[];
  gap: Gap | null;
  /** Human notes for the draft comment (icon labels in the name, nesting, …). */
  notes: string[];
  /** Set when the element only exists in a derived state (e.g. after an empty submit). */
  state?: string;
}

export interface FormField {
  tag: string;
  type: string;
  name: string | null;
  label: string | null;
  required: boolean;
}

export interface FormInfo {
  index: number;
  hint: string;
  fields: FormField[];
  submitText: string | null;
  empty: boolean;
}

export interface TableInfo {
  index: number;
  hint: string;
  name: string | null;
  headers: string[];
  rowCount: number;
  firstRowText: string | null;
  empty: boolean;
  rowTemplate: string;
}

export type SubStateKind = 'dialog' | 'drawer' | 'menu' | 'listbox' | 'popover' | 'popup' | 'tabpanel';

export interface Harvest {
  url: string;
  title: string;
  h1: string | null;
  hasRootTestId: boolean;
  elements: HarvestedElement[];
  tables: TableInfo[];
  forms: FormInfo[];
  truncated: boolean;
  container: { kind: SubStateKind; hint: string } | null;
}

export interface SubStateRecord {
  /** `<page-slug>#<opener-alias>` — the id used in inventory.md. */
  id: string;
  /** Map id (`<slug>-<opener>-<kind>`) and exported const name (`<slug><Opener><Kind>`). */
  mapId: string;
  constName: string;
  kind: SubStateKind;
  opener: { alias: string; name: string; kind: ElementKind };
  harvest: Harvest;
  closedBy: 'escape' | 'close-button' | 'reload' | 'tab-restore' | 'n/a';
  gaps: number;
}

export interface ValidationProbe {
  formIndex: number;
  button: string;
  messages: { field: string | null; message: string }[];
  urlAfter: string;
  note?: string;
}

export interface DiscoveredLink {
  url: string;
  pattern: string;
  text: string;
  via: 'href' | 'click' | 'expand';
}

export interface PageCounts {
  interactive: number;
  forms: number;
  tables: number;
  dialogs: number;
  gaps: number;
  consoleErrors: number;
}

export interface PageRecord {
  index: number;
  pattern: string;
  slug: string;
  constName: string;
  requestedUrl: string;
  finalUrl: string;
  route: string;
  redirected: boolean;
  title: string;
  h1: string | null;
  navPath: string[];
  module: string;
  harvest: Harvest | null;
  subStates: SubStateRecord[];
  discovered: DiscoveredLink[];
  consoleErrors: string[];
  errors: string[];
  notes: string[];
  validationProbe: ValidationProbe | null;
  counts: PageCounts;
  durationMs: number;
}

export interface NotVisited {
  url: string;
  pattern: string;
  reason: string;
  foundOn: string | null;
}

export interface RunMeta {
  tool: string;
  baseUrl: string;
  startUrl: string;
  storageState: boolean;
  storageStateFile: string | null;
  maxPages: number;
  maxMinutes: number;
  allow: string | null;
  deny: string | null;
  exploreStates: boolean;
  probeValidation: boolean;
  module: string;
  headed: boolean;
  hashRouted: boolean;
  startedAt: string;
  finishedAt: string;
  durationMs: number;
  outDir: string;
}

export interface ReconRun {
  meta: RunMeta;
  pages: PageRecord[];
  notVisited: NotVisited[];
  /** route pattern → other concrete URLs seen for it (only one instance is visited). */
  instances: Record<string, string[]>;
  authRequired: boolean;
  notes: string[];
  errors: string[];
}

export type Log = (message: string) => void;
