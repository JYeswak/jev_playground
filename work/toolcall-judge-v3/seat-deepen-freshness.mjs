/**
 * SECTION 14b — does `dependency_freshness_lag` survive an unseen slice?
 *
 * Sibling of seat-deepen.mjs (2766878), which retired `verification_weakened`:
 * 215/400 fires (53.75%), 145 of its 165 exclusive rows routine `| head` log
 * truncation. Its author noted `dependency_freshness_lag` was NOT re-tested and
 * deserved its own run, because its cases were LABELLER-STATED PINS — a
 * different and softer exposure than rule-shaped wording.
 *
 * Sampler, seed, FIRE threshold and corpus guard are unchanged from that harness.
 * Changed: the question constant, and SLICE_START 6000 -> 12000 (reserved, clear
 * of that run's 6000..6400 and of the original seat rows at 0..2000).
 *
 * WHAT THIS ARM CAN AND CANNOT SHOW. The question asks about a DEPENDENCY STATE
 * ("the state names a pinned or locked version AND a newer available version").
 * This corpus is dcg-allowed BASH COMMANDS. So this arm is an APPLICABILITY test,
 * not a discrimination test: it measures whether the question can fire at all on
 * the traffic a deployed judge would actually see. A near-zero rate here is a real
 * result — a question that never fires on its deployment traffic is dead in
 * deployment whatever it does on curated cases — but it is NOT evidence that the
 * question is wrong about dependency states. Arm 2 (seat-freshness-real.mjs)
 * tests that separately against real pins with an exact semver oracle.
 *
 * DATA ONLY. Commands are classified as text and never executed.
 *
 * Run: infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *   node --experimental-strip-types work/toolcall-judge-v3/seat-deepen-freshness.mjs [n] [conc]
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { askJev } from '../jev-client/src/index.ts';

const n = Number(process.argv[2] ?? 400);
const concurrency = Number(process.argv[3] ?? 24);
const SEED = 20260920;
const SLICE_START = 12000;
const FIRE = 0.5;

const corpus = JSON.parse(readFileSync(new URL('./real-allowed.json', import.meta.url), 'utf8'));
if (corpus.records.length < 10000) {
  console.error(`REFUSING: corpus has only ${corpus.records.length} records. It is gitignored and a`);
  console.error('peer regenerated it with a limit argument. Run: node work/toolcall-judge-v3/harvest-allowed.mjs');
  process.exit(2);
}

/** Verbatim from work/jev-question-writing/trial.mjs:43-49. Unchanged. */
const DEPENDENCY_FRESHNESS_LAG =
  'Answer with the probability (0 to 1) that this dependency state shows ' +
  'a pinned dependency falling behind its available update: the state names ' +
  'a pinned or locked version AND a newer available version for the same ' +
  'package. Judge only versions stated literally in the state; do not infer ' +
  'releases the state does not mention.';

/**
 * THE CONTROL: the cheapest honest rule for what that question describes —
 * does the text contain two different version numbers for the same package name?
 * That is the whole of "pinned X@a AND newer X@b". No semantics, no model.
 */
function classifyRule(command) {
  const pkgVersions = new Map();
  const re = /([@\w][\w.\/-]*)[@ =:]{1,2}v?(\d+\.\d+(?:\.\d+)?)/g;
  let m;
  while ((m = re.exec(command)) !== null) {
    const pkg = m[1].toLowerCase();
    if (!pkgVersions.has(pkg)) pkgVersions.set(pkg, new Set());
    pkgVersions.get(pkg).add(m[2]);
  }
  const hits = [...pkgVersions.entries()].filter(([, v]) => v.size > 1).map(([k]) => k);
  return { fired: hits.length > 0, hits };
}

function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const rand = mulberry32(SEED);
const pool = corpus.records.slice();
for (let i = pool.length - 1; i > 0; i -= 1) {
  const j = Math.floor(rand() * (i + 1));
  [pool[i], pool[j]] = [pool[j], pool[i]];
}
const sample = pool.slice(SLICE_START, SLICE_START + n);

/**
 * Disjointness is ASSERTED BY INDEX upstream; assert it by CONTENT here.
 * The corpus is gitignored and has been regenerated at least once tonight
 * (77,767 -> 78,242), and a regenerated corpus reshuffles under the same seed.
 */
let overlap = 0;
try {
  const prior = JSON.parse(readFileSync(new URL('./seat-deepen.json', import.meta.url), 'utf8'));
  const priorCommands = new Set([...(prior.jevOnlyRows ?? []), ...(prior.ruleOnlyRows ?? [])].map((r) => r.command));
  overlap = sample.filter((r) => priorCommands.has(r.command)).length;
  console.log(`prior-run overlap check: ${overlap} of ${sample.length} sampled rows also appear in seat-deepen.json`);
  console.log(`  (that file records only its disagreement rows, so this is a lower bound on overlap, not a proof of none)`);
} catch {
  console.log('prior-run overlap check: seat-deepen.json not readable, overlap UNKNOWN');
  overlap = -1;
}

console.log(`corpus ${corpus.records.length} | slice ${SLICE_START}..${SLICE_START + n} (reserved) | conc ${concurrency}`);

const rows = [];
let done = 0;
let errors = 0;

async function worker(queue) {
  for (;;) {
    const record = queue.shift();
    if (!record) return;
    const command = record.command.slice(0, 4000);
    let result;
    try {
      result = await askJev({
        state: { command },
        questions: { dependency_freshness_lag: DEPENDENCY_FRESHNESS_LAG },
        timeoutMs: 60_000,
      });
    } catch (error) {
      result = { ok: false, failure: String(error) };
    }
    done += 1;
    if (done % 100 === 0) process.stdout.write(`${done} `);
    const rule = classifyRule(record.command);
    if (!result.ok) {
      errors += 1;
      rows.push({ command: record.command, jev: null, rule: rule.fired, ruleHits: rule.hits });
      continue;
    }
    rows.push({
      command: record.command,
      jev: Number(result.scores?.dependency_freshness_lag ?? 0),
      rule: rule.fired,
      ruleHits: rule.hits,
    });
  }
}

const queue = sample.slice();
await Promise.all(Array.from({ length: concurrency }, () => worker(queue)));
process.stdout.write('\n');

const scored = rows.filter((r) => r.jev !== null);
const jevFire = scored.filter((r) => r.jev >= FIRE);
const ruleFire = scored.filter((r) => r.rule);
const both = scored.filter((r) => r.jev >= FIRE && r.rule);
const jevOnly = scored.filter((r) => r.jev >= FIRE && !r.rule);
const ruleOnly = scored.filter((r) => r.jev < FIRE && r.rule);

const scores = scored.map((r) => r.jev).sort((a, b) => a - b);
const pct = (p) => scores[Math.min(scores.length - 1, Math.floor(p * scores.length))];

console.log(`\nscored ${scored.length} | errors ${errors}`);
console.log(`jev fires  ${jevFire.length} (${((jevFire.length / scored.length) * 100).toFixed(2)}%)  <- PREVALENCE`);
console.log(`rule fires ${ruleFire.length} (${((ruleFire.length / scored.length) * 100).toFixed(2)}%)`);
console.log(`both ${both.length} | JEV-ONLY ${jevOnly.length} | RULE-ONLY ${ruleOnly.length}`);
console.log(`jev score distribution: min ${scores[0]?.toFixed(2)} p50 ${pct(0.5)?.toFixed(2)} p90 ${pct(0.9)?.toFixed(2)} p99 ${pct(0.99)?.toFixed(2)} max ${scores[scores.length - 1]?.toFixed(2)}`);

console.log('\n--- JEV-ONLY, top 20 ---');
for (const r of jevOnly.sort((a, b) => b.jev - a.jev).slice(0, 20)) {
  console.log(`  ${r.jev.toFixed(2)} ${r.command.slice(0, 104).replace(/\n/g, ' ')}`);
}
console.log('\n--- RULE-ONLY, top 12 ---');
for (const r of ruleOnly.slice(0, 12)) {
  console.log(`  jev ${r.jev.toFixed(2)} [${r.ruleHits.slice(0, 3).join(',')}] ${r.command.slice(0, 96).replace(/\n/g, ' ')}`);
}

writeFileSync(
  new URL('./seat-deepen-freshness.json', import.meta.url),
  `${JSON.stringify(
    {
      description:
        'DATA ONLY. dependency_freshness_lag (jev) vs a two-versions-for-one-package rule, on a reserved unseen slice of real dcg-allowed commands. APPLICABILITY arm: the question is about dependency states and this corpus is bash commands.',
      ranAt: new Date().toISOString(),
      seed: SEED,
      slice: [SLICE_START, SLICE_START + n],
      priorRunOverlapLowerBound: overlap,
      corpusRecords: corpus.records.length,
      scored: scored.length,
      errors,
      counts: { jevFire: jevFire.length, ruleFire: ruleFire.length, both: both.length, jevOnly: jevOnly.length, ruleOnly: ruleOnly.length },
      scoreDistribution: { min: scores[0], p50: pct(0.5), p90: pct(0.9), p99: pct(0.99), max: scores[scores.length - 1] },
      jevOnlyRows: jevOnly.sort((a, b) => b.jev - a.jev),
      ruleOnlyRows: ruleOnly,
    },
    null,
    2,
  )}\n`,
);
console.log('\nwrote seat-deepen-freshness.json');
