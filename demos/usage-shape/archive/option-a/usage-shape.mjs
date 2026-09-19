const LEVER_ORDER = ['RETRANSMIT', 'FRESH', 'OUTPUT', 'CACHEWRITE', 'UNRECONCILED'];

function usageFor(turn) {
  return turn.usage && turn.usage.input !== null ? turn.usage : null;
}

function classify(turn) {
  const usage = usageFor(turn);
  if (!usage) return null;
  const billedTotal = usage.costTotal;
  const retransmit = usage.cacheRead ?? 0;
  const fresh = usage.input ?? 0;
  const output = usage.output ?? 0;
  const cacheWrite = usage.cacheWrite ?? 0;
  const known = retransmit + fresh + output + cacheWrite;
  const unreconciled = billedTotal === null ? null : billedTotal - known;
  return { RETRANSMIT: retransmit, FRESH: fresh, OUTPUT: output, CACHEWRITE: cacheWrite, UNRECONCILED: unreconciled, billedTotal };
}

function table(values) {
  const total = values.reduce((sum, value) => sum + (value.value ?? 0), 0);
  return LEVER_ORDER.map((lever) => {
    const value = values.find((entry) => entry.lever === lever)?.value ?? 0;
    return { lever, value, share: total ? value / total : null };
  }).sort((a, b) => Math.abs(b.value) - Math.abs(a.value) || a.lever.localeCompare(b.lever));
}

function summarize(turns) {
  const rows = turns.map((turn) => ({
    sessionId: turn.sessionId,
    turnIndex: turn.turnIndex,
    measured: Boolean(usageFor(turn)),
    usage: classify(turn),
  }));
  const measured = rows.filter((row) => row.measured);
  const aggregate = { RETRANSMIT: 0, FRESH: 0, OUTPUT: 0, CACHEWRITE: 0, UNRECONCILED: 0, billedTotal: 0 };
  for (const row of measured) for (const key of Object.keys(aggregate)) aggregate[key] += row.usage[key] ?? 0;
  return {
    rows,
    measured: measured.length,
    aggregate: {
      billedTotal: aggregate.billedTotal,
      table: table(LEVER_ORDER.map((lever) => ({ lever, value: aggregate[lever] }))),
      accounting: 'input-includes-cache: unknown; observed input is carried as provisional FRESH; UNRECONCILED remains explicit',
    },
  };
}

export function buildUsageShape(sessions) {
  const perSession = sessions.map((session) => {
    const summary = summarize(session.turns);
    return {
      source: session.source,
      sessionId: session.sessionId,
      denominator: { turns: session.turns.length, turnsWithUsage: summary.measured, turnsWithoutUsage: session.turns.length - summary.measured },
      levers: summary.aggregate.table,
      turns: summary.rows,
    };
  });
  const allTurns = sessions.flatMap((session) => session.turns);
  const summary = summarize(allTurns);
  return {
    denominator: { sessions: sessions.length, turns: allTurns.length, turnsWithUsage: summary.measured, turnsWithoutUsage: allTurns.length - summary.measured, tokensUnattributed: allTurns.length - summary.measured },
    accounting: { inputIncludesCache: 'unknown', rule: 'observed input is shown as provisional FRESH; UNRECONCILED is never absorbed' },
    levers: { perTurn: summary.rows, perSession, aggregate: summary.aggregate.table },
    failures: [],
  };
}
