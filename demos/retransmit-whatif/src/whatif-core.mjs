export const REDUCTIONS = [0.25, 0.5, 0.75];

export function validateUsage(usage, source, line) {
  for (const field of ['input', 'cacheRead', 'cacheWrite', 'output']) {
    if (usage[field] === undefined) throw new Error(`missing usage.${field} at ${source}:${line}`);
    if (!Number.isFinite(Number(usage[field])) || Number(usage[field]) < 0) throw new Error(`invalid usage.${field} at ${source}:${line}`);
  }
}

export function measureTurn(turn, reduction = null) {
  const cacheRead = Number(turn.cacheRead);
  const cacheWrite = Number(turn.cacheWrite);
  const input = Number(turn.input);
  const output = Number(turn.output);
  const total = cacheRead + cacheWrite + input + output;
  const saved = reduction === null ? 0 : cacheRead * reduction;
  return { cacheRead, cacheWrite, input, output, total, reduction, saved, remaining: total - saved };
}

export function aggregate(turns) {
  return turns.reduce((sum, turn) => ({
    cacheRead: sum.cacheRead + turn.cacheRead,
    cacheWrite: sum.cacheWrite + turn.cacheWrite,
    input: sum.input + turn.input,
    output: sum.output + turn.output,
    total: sum.total + turn.total,
  }), { cacheRead: 0, cacheWrite: 0, input: 0, output: 0, total: 0 });
}

export function shares(values) {
  return Object.fromEntries(Object.entries(values).map(([key, value]) => [key, values.total ? value / values.total : null]));
}
