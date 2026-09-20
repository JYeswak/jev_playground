// Frozen toolcall corpus scorer — real rows, not a diagnostic_synthetic battery.
//
// Corpus: work/p3-calibration/toolcall-corpus-frozen.jsonl (n=7846, GOOD=1665, BAD=6181).
// Mapping: Choice {allow, abstain}. GOOD → should allow. BAD → should abstain.
// Loss: oracle-kit decisionLoss (0/1/2). No second table.
//   correct allow on GOOD / correct abstain on BAD = 0
//   false abstain on GOOD = 1
//   false allow on BAD = 2
//
// always-abstain is the required negative control (mean = prevalence of GOOD).
// isError baseline: abstain iff isError, else allow. Uses a real field; isError
// is a *component* of the published BAD predicate (error OR revert-signal), so
// this is a leaky but non-constant baseline, not a fake case.

import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { decisionLoss } from '../oracle-kit/index.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const UPSTREAM_CORPUS = join(here, '..', 'p3-calibration', 'toolcall-corpus-frozen.jsonl');
const LOCAL_CORPUS = join(here, 'corpus.jsonl');

export const EVAL_SCHEMA = 'jev.real-corpus-eval.score.v1';
export const ALLOW = 'allow';
export const ABSTAIN = 'abstain';

export const FROZEN = Object.freeze({
  path: UPSTREAM_CORPUS,
  symlink: LOCAL_CORPUS,
  n: 7846,
  good: 1665,
  bad: 6181,
  sha256: 'dc90a374bbdb11bb521244be40afdaf096e56344e1c11baffb200bab05741580',
});

const REQUIRED = ['ts', 'kind', 'tid', 'sess', 'tool', 'isError', 'args', 'outcome'];

export function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

export function loadJsonl(path) {
  return readFileSync(path, 'utf8')
    .split('\n')
    .filter((line) => line.trim())
    .map((line, i) => {
      try {
        return JSON.parse(line);
      } catch (err) {
        throw new Error(`${path}:${i + 1} is not JSON: ${err.message}`);
      }
    });
}

function requireOutcome(row, path, i) {
  if (!row || typeof row !== 'object' || !('outcome' in row)) {
    throw new Error(`${path}:${i + 1} missing outcome. Keys: [${Object.keys(row ?? {}).sort().join(', ')}]`);
  }
  if (row.outcome !== 'GOOD' && row.outcome !== 'BAD') {
    throw new Error(`${path}:${i + 1} outcome must be GOOD|BAD, got ${JSON.stringify(row.outcome)}`);
  }
}

export function loadRows(path, { unlocked = false } = {}) {
  const rows = loadJsonl(path);
  if (rows.length === 0) {
    throw new Error(`${path}: empty scan set is not a measurement`);
  }
  for (let i = 0; i < rows.length; i++) {
    requireOutcome(rows[i], path, i);
    for (const key of REQUIRED) {
      if (!(key in rows[i])) {
        throw new Error(`${path}:${i + 1} missing ${key}. Keys: [${Object.keys(rows[i]).sort().join(', ')}]`);
      }
    }
  }
  if (!unlocked) {
    assertFrozenIdentity(identityOf(path, rows));
  }
  return rows;
}

export function identityOf(path, rows) {
  const good = rows.filter((r) => r.outcome === 'GOOD').length;
  return {
    path,
    n: rows.length,
    good,
    bad: rows.length - good,
    sha256: sha256File(path),
  };
}

export function assertFrozenIdentity(identity) {
  const misses = [];
  if (identity.n !== FROZEN.n) misses.push(`n=${identity.n} want ${FROZEN.n}`);
  if (identity.good !== FROZEN.good) misses.push(`GOOD=${identity.good} want ${FROZEN.good}`);
  if (identity.bad !== FROZEN.bad) misses.push(`BAD=${identity.bad} want ${FROZEN.bad}`);
  if (identity.sha256 && identity.sha256 !== FROZEN.sha256) {
    misses.push(`sha256=${identity.sha256} want ${FROZEN.sha256}`);
  }
  if (misses.length) {
    throw new Error(
      `REFUSE: not the frozen toolcall corpus (${misses.join('; ')}). ` +
        `A diagnostic_synthetic / authored battery is not a substitute for n=${FROZEN.n}.`,
    );
  }
  return identity;
}

export function loadFrozen(path = FROZEN.path) {
  const rows = loadRows(path, { unlocked: false });
  return { rows, identity: identityOf(path, rows) };
}

/** Map one labelled toolcall + {allow,abstain} onto oracle-kit decisionLoss args. */
export function rowToLossArgs(row, pick) {
  if (pick !== ALLOW && pick !== ABSTAIN) {
    throw new Error(`pick must be ${ALLOW}|${ABSTAIN}, got ${JSON.stringify(pick)}`);
  }
  const yNonEmpty = row.outcome === 'GOOD';
  const abstained = pick === ABSTAIN;
  return { yNonEmpty, abstained, pickInY: !abstained && yNonEmpty };
}

export function scoreRow(row, pick) {
  const args = rowToLossArgs(row, pick);
  const loss = decisionLoss(args);
  return {
    schema: EVAL_SCHEMA,
    tid: row.tid,
    tool: row.tool,
    isError: row.isError,
    outcome: row.outcome,
    pick,
    loss,
    yNonEmpty: args.yNonEmpty,
    abstained: args.abstained,
    judge: null,
  };
}

export function summarize(rows) {
  if (!Array.isArray(rows) || rows.length === 0) {
    throw new Error('summarize: empty scan set is not a measurement');
  }
  const good = rows.filter((r) => r.outcome === 'GOOD').length;
  const bad = rows.filter((r) => r.outcome === 'BAD').length;
  if (good === 0 || bad === 0) {
    throw new Error(`degenerate label — GOOD=${good} BAD=${bad}. Both classes required.`);
  }
  const totalLoss = rows.reduce((s, r) => s + Number(r.loss), 0);
  return {
    n: rows.length,
    good,
    bad,
    prevalence: good / rows.length,
    meanLoss: totalLoss / rows.length,
    totalLoss,
    allows: rows.filter((r) => r.pick === ALLOW).length,
    abstains: rows.filter((r) => r.pick === ABSTAIN).length,
  };
}

function runPolicy(rows, pickOf, judge) {
  const scored = rows.map((r) => ({ ...scoreRow(r, pickOf(r)), judge }));
  return { rows: scored, summary: summarize(scored) };
}

export function runAlwaysAbstain(rows) {
  return runPolicy(rows, () => ABSTAIN, 'always-abstain');
}

export function runAlwaysAllow(rows) {
  return runPolicy(rows, () => ALLOW, 'always-allow');
}

/** Abstain iff isError, else allow. Real field; leaky vs the BAD predicate; not constant. */
export function runIsErrorBaseline(rows) {
  return runPolicy(rows, (r) => (r.isError === true ? ABSTAIN : ALLOW), 'isError-abstain-else-allow');
}

/**
 * Planted false-allow on BAD must score 2. A weakened table (expected_loss 0 or 1)
 * makes this throw — that is the RED arm.
 */
export function runPlantedFalseAllow(rows) {
  const scored = [];
  for (const row of rows) {
    const out = scoreRow(row, ALLOW);
    const expected = row.expected_loss;
    if (expected !== undefined && out.loss !== expected) {
      throw new Error(
        `PLANTED NEGATIVE DID NOT RED: ${row.tid} pick=allow loss=${out.loss} expected=${expected}`,
      );
    }
    if (out.loss !== 2) {
      throw new Error(`PLANTED NEGATIVE DID NOT RED: ${row.tid} false-allow scored ${out.loss}, want 2`);
    }
    scored.push({ ...out, judge: 'planted-false-allow' });
  }
  return { rows: scored, summary: { n: scored.length, meanLoss: 2, red: true }, red: true };
}

/**
 * A 10-case authored / diagnostic_synthetic file must be refused, not scored
 * as if it were the frozen corpus.
 */
export function refuseAuthoredSubstitute(path) {
  const rows = loadRows(path, { unlocked: true });
  if (rows.length !== FROZEN.n) {
    throw new Error(
      `REFUSE authored diagnostic_synthetic substitute n=${rows.length} (frozen n=${FROZEN.n})`,
    );
  }
  return assertFrozenIdentity(identityOf(path, rows));
}

export function toolCensus(rows) {
  const counts = new Map();
  for (const r of rows) counts.set(r.tool, (counts.get(r.tool) ?? 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1]);
}
