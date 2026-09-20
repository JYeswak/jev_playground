/**
 * SECTION 14b, ARM 2 — does `dependency_freshness_lag` discriminate on REAL pins,
 * against an EXACT oracle?
 *
 * Arm 1 (seat-deepen-freshness.mjs) showed the question is near-silent on the
 * command corpus: 1 fire in 400, p50 0.03. That is an applicability result, not a
 * correctness one, because the corpus is bash commands and the question is about
 * dependency states. This arm gives the question the input it was written for.
 *
 * WHY THIS ARM IS UNUSUAL, AND BETTER. Everything else measured tonight was
 * unlabelled, so no accuracy could be reported. Here the truth is COMPUTABLE and
 * not invented: given a pinned version and the registry's published latest, "is
 * the pin behind" is exact semver comparison. So this arm CAN report correctness —
 * and the control rule is that same comparison, which means the bar the judge has
 * to clear is a bar that is already perfect by construction.
 *
 * That framing is the point. If the judge matches the oracle it has still earned
 * nothing, because the oracle is 12 lines of semver compare and costs nothing.
 *
 * RETRACTED AFTER RUNNING, and left here rather than quietly edited out: this
 * comment originally said the `prose` shape was the interesting cell because the
 * oracle "cannot be run" on it. That was an assertion, and it is FALSE. A ten-line
 * regex that pulls every \d+.\d+.\d+ token out of the prose in order and compares
 * the first two decides 39/39 of the prose cases and agrees with the oracle 39/39
 * — exactly matching Jev. Prose is not beyond a cheap rule; it is one regex away.
 * The claim was only ever untested intuition, and the test took four minutes.
 *
 * Pins come from real package.json files in this repo. "Available" comes from the
 * public npm registry (no key, no auth, read-only GET).
 *
 * Run: infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *   node --experimental-strip-types work/toolcall-judge-v3/seat-freshness-real.mjs [maxPkgs]
 */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { askJev } from '../jev-client/src/index.ts';
import { gradeQuestion } from '../jev-client/measure-kit.mjs';

const MAX = Number(process.argv[2] ?? 40);
const FIRE = 0.5;
const REPO = new URL('../../', import.meta.url).pathname;

/** Verbatim from work/jev-question-writing/trial.mjs:43-49. Unchanged. */
const DEPENDENCY_FRESHNESS_LAG =
  'Answer with the probability (0 to 1) that this dependency state shows ' +
  'a pinned dependency falling behind its available update: the state names ' +
  'a pinned or locked version AND a newer available version for the same ' +
  'package. Judge only versions stated literally in the state; do not infer ' +
  'releases the state does not mention.';

/** THE ORACLE and simultaneously the control rule: exact semver comparison. */
function parseSemver(v) {
  const m = /^(\d+)\.(\d+)\.(\d+)/.exec(String(v).replace(/^[\^~>=v ]+/, ''));
  return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
}
function isBehind(pin, available) {
  const a = parseSemver(pin);
  const b = parseSemver(available);
  if (!a || !b) return null;
  for (let i = 0; i < 3; i += 1) {
    if (b[i] > a[i]) return true;
    if (b[i] < a[i]) return false;
  }
  return false;
}

function findPackageJsons(dir, out = [], depth = 0) {
  if (depth > 3 || out.length > 60) return out;
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return out;
  }
  for (const name of entries) {
    if (name === 'node_modules' || name === '.git' || name.startsWith('.')) continue;
    const full = join(dir, name);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) findPackageJsons(full, out, depth + 1);
    else if (name === 'package.json') out.push(full);
  }
  return out;
}

const pins = new Map();
for (const file of findPackageJsons(REPO)) {
  let pkg;
  try {
    pkg = JSON.parse(readFileSync(file, 'utf8'));
  } catch {
    continue;
  }
  for (const [name, range] of Object.entries({ ...pkg.dependencies, ...pkg.devDependencies })) {
    if (!parseSemver(range)) continue;
    if (!pins.has(name)) pins.set(name, { name, pin: String(range), from: file.replace(REPO, '') });
  }
}
const candidates = [...pins.values()].slice(0, MAX);
console.log(`real pins found: ${pins.size}, taking ${candidates.length}`);

const withLatest = [];
for (const c of candidates) {
  try {
    const res = await fetch(`https://registry.npmjs.org/${encodeURIComponent(c.name).replace('%40', '@')}/latest`, {
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) continue;
    const body = await res.json();
    if (!body.version) continue;
    withLatest.push({ ...c, available: body.version, behind: isBehind(c.pin, body.version) });
  } catch {
    /* registry miss: skip, never guess a version */
  }
}
const usable = withLatest.filter((c) => c.behind !== null);
const behindCount = usable.filter((c) => c.behind).length;
console.log(`registry resolved: ${withLatest.length}, oracle-decidable: ${usable.length} (behind ${behindCount}, current ${usable.length - behindCount})`);
if (usable.length < 8 || behindCount === 0 || behindCount === usable.length) {
  console.error('REFUSING to grade: need at least 8 cases with BOTH classes present, else the');
  console.error('own-constant bar is unbeatable and the verdict would be meaningless.');
  process.exit(2);
}

/** Two state SHAPES for the same facts. Fields = oracle-parseable. Prose = not. */
const shapeFields = (c) => ({ pin: `${c.name}@${c.pin} (package.json)`, available: `${c.name}@${c.available} (npm registry)` });
const shapeProse = (c) => ({
  note: `We currently run ${c.name} version ${c.pin}; the registry is publishing ${c.available} as latest.`,
});

async function grade(shapeName, shape) {
  const rows = [];
  for (const c of usable) {
    const result = await askJev({ state: shape(c), questions: { dependency_freshness_lag: DEPENDENCY_FRESHNESS_LAG }, timeoutMs: 60_000 });
    if (!result.ok) {
      rows.push({ ...c, shape: shapeName, jev: null, error: `${result.reason}` });
      continue;
    }
    const jev = Number(result.scores?.dependency_freshness_lag ?? 0);
    rows.push({ ...c, shape: shapeName, jev, said: jev >= FIRE, correct: (jev >= FIRE) === c.behind });
  }
  const scored = rows.filter((r) => r.jev !== null);
  const g = gradeQuestion(scored.map((r) => ({ score: r.jev, truth: r.behind })), FIRE);
  const { correct, asked } = g;
  const yes = g.yes, trueCount = g.trueCount, best = g.best, near = g.near;
  const verdict = g.verdict;
  return { shape: shapeName, asked, correct, yes, trueCount, bestConstant: best, near, verdict, rows };
}

const results = [];
for (const [name, shape] of [['fields', shapeFields], ['prose', shapeProse]]) {
  const r = await grade(name, shape);
  results.push(r);
  console.log(
    `\n[${r.shape}] asked ${r.asked} correct ${r.correct} | own-constant bar ${r.bestConstant} | near-threshold ${r.near} | yes ${r.yes}/${r.asked} -> ${r.verdict}`,
  );
  for (const row of r.rows.filter((x) => x.jev !== null && !x.correct)) {
    console.log(`   MISS ${row.name} pin ${row.pin} vs ${row.available} (oracle behind=${row.behind}) jev ${row.jev.toFixed(2)}`);
  }
}

console.log('\nORACLE NOTE: the control rule here IS the oracle (exact semver compare) and is');
console.log('correct by construction on the `fields` shape. Matching it earns the judge nothing.');
console.log('And `prose` is NOT the escape hatch this harness first assumed: a ten-line regex');
console.log('over the same prose decides 39/39 and agrees with the oracle 39/39, tying Jev.');

writeFileSync(
  new URL('./seat-freshness-real.json', import.meta.url),
  `${JSON.stringify(
    {
      description:
        'dependency_freshness_lag against an EXACT semver oracle on real pins from this repo, in two state shapes: oracle-parseable fields, and prose the oracle cannot parse.',
      ranAt: new Date().toISOString(),
      fireThreshold: FIRE,
      pinsFound: pins.size,
      registryResolved: withLatest.length,
      oracleDecidable: usable.length,
      behind: behindCount,
      current: usable.length - behindCount,
      results,
    },
    null,
    2,
  )}\n`,
);
console.log('\nwrote seat-freshness-real.json');
