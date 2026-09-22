/**
 * Environment access for the harness. One rule: a missing value is Blocked and says
 * which variable — never a silent default, never a fallback that turns a run green.
 */
export function requireEnv(name: string, purpose: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(
      `${name} is not set — ${purpose}. Add it to automation/web/.env (see .env.example) or export it. ` +
        'Blocked, not green: a run without it is not a run.',
    );
  }
  return value;
}
