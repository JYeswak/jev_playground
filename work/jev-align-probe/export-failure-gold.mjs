/**
 * Export the committed omp-jev-failure ground-truth table as a jev-align input CSV
 * plus a gold-label sidecar for drive.py's `--oracle gold`.
 *
 * The CASES array in work/omp-jev-failure/measure.mjs is the only source of truth
 * here; this script does not invent, relabel, or reorder a single case.
 *
 *   node work/jev-align-probe/export-failure-gold.mjs /tmp/jeva-ours
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.argv[2];
if (!outDir) throw new Error('usage: export-failure-gold.mjs OUTDIR');
mkdirSync(outDir, { recursive: true });

const source = readFileSync(
  new URL('../omp-jev-failure/measure.mjs', import.meta.url),
  'utf8',
);

// Evaluate only the literal CASES array from the committed file, with the T/A/B
// aliases bound exactly as the file defines them. No network, no side effects.
const start = source.indexOf('const CASES = [');
const end = source.indexOf('\n];', start) + 3;
if (start < 0 || end < 3) throw new Error('could not locate CASES array');
const T = { transient: true, argument: false, bug: false };
const A = { transient: false, argument: true, bug: false };
const B = { transient: false, argument: false, bug: true };
const CASES = new Function('T', 'A', 'B', `${source.slice(start, end)}\nreturn CASES;`)(T, A, B);

const classOf = (truth) => {
  if (truth.transient) return 'transient';
  if (truth.argument) return 'argument';
  if (truth.bug) return 'bug';
  throw new Error('case has no true class');
};

const csvCell = (value) => `"${String(value).replaceAll('"', '""')}"`;

// jev-align renders each row inside a box and soft-wraps long lines, so a needle
// must be matched against a NORMALIZED card: box glyphs stripped, whitespace
// collapsed. drive.py applies the identical normalization before matching.
const normalize = (value) =>
  String(value)
    .replaceAll(/[│┃╭╮╰╯━─┏┓┗┛┡┩╇┳┻╋]/gu, ' ')
    .replaceAll(/\s+/gu, ' ')
    .trim();

const rows = [['tool', 'invocation', 'failure'].join(',')];
const gold = [];
for (const testCase of CASES) {
  const invocation = JSON.stringify(testCase.args);
  rows.push([testCase.toolName, invocation, testCase.failure].map(csvCell).join(','));
  gold.push({
    name: testCase.name,
    normalized: normalize(testCase.failure),
    label: classOf(testCase.truth),
  });
}

// Grow each needle from the normalized failure text until it identifies exactly
// one case. A needle that can never be made unique is a hard error, not a guess.
for (const row of gold) {
  let length = 24;
  for (;;) {
    const candidate = row.normalized.slice(0, length);
    const matches = gold.filter((other) => other.normalized.includes(candidate));
    if (matches.length === 1) {
      row.needle = candidate;
      break;
    }
    if (length >= row.normalized.length) {
      throw new Error(`no unique needle for case ${row.name}`);
    }
    length = Math.min(length + 12, row.normalized.length);
  }
}
for (const row of gold) {
  delete row.normalized;
}

if (new Set(gold.map((row) => row.needle)).size !== gold.length) {
  throw new Error('needles are not unique');
}

writeFileSync(join(outDir, 'failure-cases.csv'), `${rows.join('\n')}\n`);
writeFileSync(join(outDir, 'gold.json'), `${JSON.stringify(gold, null, 1)}\n`);

const counts = {};
for (const row of gold) counts[row.label] = (counts[row.label] ?? 0) + 1;
console.log(`cases: ${CASES.length}`);
console.log(`class counts: ${JSON.stringify(counts)}`);
console.log(`wrote ${join(outDir, 'failure-cases.csv')}`);
console.log(`wrote ${join(outDir, 'gold.json')}`);
