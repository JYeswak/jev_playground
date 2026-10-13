export type SystemOneUsage = {
  input_tokens: number;
  output_tokens: number;
  billing_units: number | null;
  extra: Record<string, number>;
};

/** Preserve only finite server-reported usage; missing totals keep the whole object absent. */
export function readSystemOneUsage(raw: unknown): SystemOneUsage | undefined {
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) return undefined;
  const usage = raw as Record<string, unknown>;
  const finite = (key: string): number | null => {
    const value = Reflect.get(usage, key);
    return typeof value === "number" && Number.isFinite(value) ? value : null;
  };
  const input_tokens = finite("input_tokens");
  const output_tokens = finite("output_tokens");
  if (input_tokens === null || output_tokens === null) return undefined;
  const extra: Record<string, number> = {};
  for (const key of Object.keys(usage)) {
    if (key === "input_tokens" || key === "output_tokens" || key === "billing_units") continue;
    const value = finite(key);
    if (value !== null) extra[key] = value;
  }
  return { input_tokens, output_tokens, billing_units: finite("billing_units"), extra };
}
