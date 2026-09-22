import type { ScreenMap } from './resolve';
import { login } from './authentication/login.map';

/**
 * Registry of every curated screen map, by access level. `map-health.spec.ts` walks it,
 * and its "registry is complete" test fails when a `*.map.ts` on disk is missing here —
 * so curating a new map ends with one line in this file (README.md → "Registry").
 *
 * - `publicScreens` — reachable without a session; the health check opens them in a
 *   clean browser context so a leftover signed-in session cannot redirect them away.
 * - `appScreens`    — need the primary-role session (`storageState` written by the setup project).
 */
export const publicScreens: readonly ScreenMap[] = [login];

/** Signed-in screens — filled module by module: one import + one entry per curated map. */
export const appScreens: readonly ScreenMap[] = [];
