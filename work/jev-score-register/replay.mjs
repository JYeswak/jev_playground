/**
 * Replay — reproduce a verdict table from the register with ZERO new Jev calls.
 *
 * This is the acceptance command for jev-vbh.7. It proves the register closes the
 * export hole: a second measurement reads scores a live extension run already paid
 * for, instead of re-calling the API. The commit-judge measurement re-scored 31
 * commits that extensions had already seen; that is the waste this removes.
 *
 * HONESTY PROPERTY, deliberate: this script cannot call Jev. It does not import the
 * client. If a row is missing it reports the gap and exits non-zero — it never
 * silently falls back to the network, because a replay that can call the API is not
 * a replay, and "0 API calls" would stop being checkable.
 *
 * Run: node --experimental-strip-types work/jev-score-register/replay.mjs [registerPath]
 *   (no API key needed, and that is the point — if it needs one, it is broken)
 */
import { createHash } from 'node:crypto';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { readRegister } from './register.mjs';

const path = process.argv[2] ?? 'work/jev-score-register/scores.jsonl';
const { rows, malformed } = readRegister(path);

if (rows.length === 0) {
  console.error(`REPLAY GAP: no rows in ${path}. Nothing to replay; run a recorded extension first.`);
  process.exit(2);
}

const byQuestion = new Map();
for (const row of rows) {
  if (!byQuestion.has(row.questionKey)) byQuestion.set(row.questionKey, []);
  byQuestion.get(row.questionKey).push(row);
}

/**
 * PIN THE INPUT AT QUOTE TIME. Four times tonight a live number was quoted without
 * its input pinned, and a later reader could not tell whether they were looking at
 * the same data: real-allowed.json grew 77,767 -> 78,242 between two runs of one
 * harness; a matched= denominator moved 15,525 -> 15,557 -> 15,618 mid-session;
 * c6eb7ab's corpus drifted under a committed receipt; and this register is
 * gitignored, so a quoted replay is not reproducible from a fresh clone.
 *
 * The fix is NOT to commit the log — a growing append log does not belong in git.
 * The fix is that every quoted table carries the identity of the log it came from,
 * so "is this the same data?" is decided by comparing one line instead of guessing.
 */
const digest = existsSync(path) ? createHash('sha256').update(readFileSync(path)).digest('hex') : null;
const bytes = existsSync(path) ? statSync(path).size : 0;

const FIRE = 0.5;
console.log(`register        : ${path}`);
console.log(`register sha256 : ${digest ?? 'ABSENT'}`);
console.log(`register bytes  : ${bytes}`);
console.log(`rows            : ${rows.length}${malformed ? ` (${malformed} malformed, skipped)` : ''}`);
console.log(`api calls made  : 0   <- this script cannot call Jev; it does not import the client`);
console.log(`models seen     : ${[...new Set(rows.map((r) => r.model).filter(Boolean))].join(', ') || 'none recorded'}`);
console.log(`extensions      : ${[...new Set(rows.map((r) => r.extension).filter(Boolean))].join(', ') || 'none recorded'}`);
console.log(`distinct inputs : ${new Set(rows.map((r) => r.identity)).size}`);
console.log('');
console.log('QUOTE THIS TABLE ONLY WITH THE sha256 AND ROW COUNT ABOVE. The register is an append');
console.log('log and is gitignored: without them a later reader cannot tell it is the same data.');
console.log('');
console.log('question                       n    fired   fire%   mean   errors');

for (const [questionKey, group] of [...byQuestion].sort()) {
  const ok = group.filter((r) => r.ok);
  const errors = group.length - ok.length;
  const fired = ok.filter((r) => r.score >= FIRE).length;
  const mean = ok.length ? ok.reduce((a, r) => a + r.score, 0) / ok.length : 0;
  const pct = ok.length ? ((fired / ok.length) * 100).toFixed(1) : '0.0';
  console.log(
    `${questionKey.padEnd(30)} ${String(ok.length).padStart(4)} ${String(fired).padStart(7)} ${pct.padStart(6)}% ${mean.toFixed(3).padStart(7)} ${String(errors).padStart(7)}`,
  );
}

const duplicates = rows.length - new Set(rows.map((r) => `${r.identity}|${r.questionKey}|${r.model}`)).size;
console.log('');
console.log(`repeat scorings of an identical (input, question, model): ${duplicates}`);
console.log(
  duplicates > 0
    ? '  ^ each of these was an API call we had already paid for once.'
    : '  ^ no redundant calls in this register.',
);
