/**
 * Does ONE multiclass question beat THREE binary questions on the same eleven failures?
 *
 * The receipt at docs/demos/upstream-repro/jev-align-20260919.md claims it does: 11/11 across
 * four repeats, on the same cases where the binary `argument` question flipped HIT->MISS->MISS on
 * byte-identical input. That claim was produced through jev-align's saved AI Function. Until it is
 * re-run through OUR client it is a claim, not evidence. This re-runs it.
 *
 * What is held fixed, and why:
 *   - The CASES are lifted out of the committed measure.mjs by the same literal-slice trick
 *     work/jev-align-probe/export-failure-gold.mjs uses. Not copied, not re-typed, not relabeled:
 *     a duplicated gold table drifts, and a drifted gold table proves whatever you want.
 *   - `state` is byte-identical to what measure.mjs sends, so the ONLY difference between the two
 *     measurements is the shape of the question.
 *
 * Three arms, all in ONE command and ONE session, because a comparison against numbers recorded
 * hours earlier is a comparison against the weather:
 *   binary   — the three independent binary questions the extension ships today. The baseline.
 *   ours     — our three binary question strings, VERBATIM, used as the three class descriptions.
 *   receipt  — the declarative rewrites the receipt actually passed to `jeva --class`.
 * Running both multiclass wordings answers the obvious objection: if `ours` and `receipt` disagree
 * the finding is about phrasing, not about task shape. Each arm prints the exact strings it used.
 *
 * Scoring is CASE-LEVEL for every arm — a binary case counts as correct only if all three of its
 * verdicts match — because one multiclass label is comparable to three binary verdicts only that
 * way. The binary arm additionally counts answers that are structurally impossible: three
 * independent questions over three mutually-exclusive classes can say yes twice or no three times.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-failure/measure-multiclass.mjs
 *
 *   --runs N   repeats per arm (default 3)
 *   --arm X    'binary' | 'ours' | 'receipt' | 'both' (default both = all three)
 */
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { askJev, askJevChoice } from '../jev-client/src/index.ts';

const argv = process.argv.slice(2);
const argOf = (name, fallback) => {
  const index = argv.indexOf(name);
  return index >= 0 && argv[index + 1] !== undefined ? argv[index + 1] : fallback;
};
const RUNS = Number(argOf('--runs', '3'));
const ARM = argOf('--arm', 'both');
if (!Number.isInteger(RUNS) || RUNS < 1) throw new Error('--runs must be a positive integer');
if (!['binary', 'ours', 'receipt', 'both'].includes(ARM)) throw new Error('--arm must be binary|ours|receipt|both');

// ---- the committed gold set, read out of measure.mjs rather than duplicated -------------------
const source = readFileSync(new URL('./measure.mjs', import.meta.url), 'utf8');
const sliceLiteral = (name, open, close) => {
  const start = source.indexOf(`const ${name} = ${open}`);
  const end = source.indexOf(`\n${close};`, start) + close.length + 2;
  if (start < 0 || end < close.length + 2) throw new Error(`could not locate ${name} in measure.mjs`);
  return source.slice(start, end);
};
const T = { transient: true, argument: false, bug: false };
const A = { transient: false, argument: true, bug: false };
const B = { transient: false, argument: false, bug: true };
const CASES = new Function('T', 'A', 'B', `${sliceLiteral('CASES', '[', ']')}\nreturn CASES;`)(T, A, B);
const BINARY_QUESTIONS = new Function(`${sliceLiteral('QUESTIONS', '{', '}')}\nreturn QUESTIONS;`)();
// measure.mjs moves: it was reworded mid-session on 2026-09-19 while this harness was running.
// Stamp what was actually read, so a run's numbers can never be attributed to the wrong wording.
const SOURCE_SHA = createHash('sha256').update(source).digest('hex').slice(0, 12);

const LABELS = ['transient', 'argument', 'bug'];
if (CASES.length !== 11) throw new Error(`expected the committed 11 cases, got ${CASES.length}`);
for (const label of LABELS) {
  if (typeof BINARY_QUESTIONS[label] !== 'string') throw new Error(`no binary question for ${label}`);
}
const classOf = (truth) => {
  const hit = LABELS.filter((label) => truth[label]);
  if (hit.length !== 1) throw new Error('a case must have exactly one true class');
  return hit[0];
};

const INSTRUCTIONS = 'Which failure class best fits this tool failure?';
const ARMS = {
  // Our three existing question strings, verbatim. They are phrased as questions; that is what
  // they say in the extension today, and substituting a nicer sentence would measure the sentence.
  ours: BINARY_QUESTIONS,
  // Exactly the three --class descriptions in the receipt whose 11/11 is under test.
  receipt: {
    transient: 'The failure is most consistent with a transient environment or dependency failure.',
    argument: 'The failure is most consistent with a wrong argument, path, or invocation.',
    bug: 'The failure is most consistent with a genuine bug in the code under edit.',
  },
};

// A multiclass verdict has no 0.5 threshold; the analogous "the harness decided this, not the
// model" case is a top-1 that barely clears top-2. Same spirit as measure.mjs's `thin` list.
const THIN_MARGIN = 0.1;

async function runOnce(classes) {
  const rows = [];
  for (const testCase of CASES) {
    const expected = classOf(testCase.truth);
    const result = await askJevChoice({
      state: {
        toolName: testCase.toolName,
        toolCallId: `measure-${testCase.name}`,
        args: testCase.args,
        failure: testCase.failure,
      },
      instructions: INSTRUCTIONS,
      classes,
      timeoutMs: 8000,
    });
    if (!result.ok) {
      rows.push({ name: testCase.name, expected, error: `${result.reason}: ${result.error}` });
      continue;
    }
    const ordered = [...LABELS].sort((a, b) => result.probabilities[b] - result.probabilities[a]);
    rows.push({
      name: testCase.name,
      expected,
      got: result.choice,
      hit: result.choice === expected,
      confidence: result.confidence,
      margin: result.probabilities[ordered[0]] - result.probabilities[ordered[1]],
      adversarial: testCase.name.startsWith('adv-'),
    });
  }
  return rows;
}

/**
 * The baseline, run in the SAME command and the SAME session as the multiclass arms, because a
 * comparison against numbers recorded hours earlier is a comparison against the weather.
 * A case counts as correct only if ALL THREE binary verdicts match — that is the case-level
 * question, and it is the only thing comparable to a single multiclass label.
 * `yesCount` is the structural part: three independent questions over three mutually-exclusive
 * classes can answer yes twice, or no three times. A choice question cannot.
 */
async function runBinaryOnce() {
  const rows = [];
  for (const testCase of CASES) {
    const expected = classOf(testCase.truth);
    const result = await askJev({
      state: {
        toolName: testCase.toolName,
        toolCallId: `measure-${testCase.name}`,
        args: testCase.args,
        failure: testCase.failure,
      },
      questions: BINARY_QUESTIONS,
      timeoutMs: 8000,
    });
    if (!result.ok) {
      rows.push({ name: testCase.name, expected, error: `${result.reason}: ${result.error}` });
      continue;
    }
    const said = Object.fromEntries(LABELS.map((label) => [label, result.scores[label] >= 0.5]));
    const wrong = LABELS.filter((label) => said[label] !== testCase.truth[label]);
    const yes = LABELS.filter((label) => said[label]);
    rows.push({
      name: testCase.name,
      expected,
      got: yes.length === 1 ? yes[0] : `${yes.length}-yes[${yes.join('+') || 'none'}]`,
      hit: wrong.length === 0,
      incoherent: yes.length !== 1,
      wrong: wrong.map((label) => `${label}=${result.scores[label].toFixed(2)}`),
      margin: Math.min(...LABELS.map((label) => Math.abs(result.scores[label] - 0.5))),
      confidence: Number.NaN,
      adversarial: testCase.name.startsWith('adv-'),
    });
  }
  return rows;
}

const report = {};
const plan = ARM === 'both' ? ['binary', 'ours', 'receipt'] : [ARM];
console.log(`gold + question strings read from measure.mjs sha256:${SOURCE_SHA} (11 cases)`);
for (const arm of plan) {
  const classes = ARMS[arm];
  console.log(`\n================ ARM: ${arm} ================`);
  if (arm === 'binary') {
    console.log('  three INDEPENDENT binary questions, the shape the extension ships today:');
    for (const label of LABELS) console.log(`  ${label.padEnd(10)} ${BINARY_QUESTIONS[label]}`);
  } else {
    console.log(`  one multiclass question: "${INSTRUCTIONS}"`);
    for (const label of LABELS) console.log(`  ${label.padEnd(10)} ${classes[label]}`);
  }

  const runs = [];
  for (let run = 1; run <= RUNS; run += 1) {
    const rows = arm === 'binary' ? await runBinaryOnce() : await runOnce(classes);
    runs.push(rows);
    const errors = rows.filter((row) => row.error);
    const hits = rows.filter((row) => row.hit).length;
    const advHits = rows.filter((row) => row.adversarial && row.hit).length;
    const advTotal = rows.filter((row) => row.adversarial).length;
    console.log(`\n-- run ${run} --`);
    for (const row of rows) {
      if (row.error) { console.log(`ERROR ${row.name.padEnd(32)} ${row.error}`); continue; }
      const detail = arm === 'binary'
        ? `said=${row.got.padEnd(16)}${row.wrong.length ? ` wrong: ${row.wrong.join(', ')}` : ''}` +
          `${row.incoherent ? '  INCOHERENT (not exactly one class)' : ''}`
        : `got=${row.got.padEnd(9)} confidence=${row.confidence.toFixed(3)} margin=${row.margin.toFixed(3)}`;
      console.log(
        `${row.hit ? 'HIT ' : 'MISS'}  ${row.name.padEnd(32)} expected=${row.expected.padEnd(9)} ${detail}` +
        `${row.adversarial ? '  (adversarial)' : ''}`,
      );
    }
    console.log(`run ${run}: ${hits}/${rows.length}   adversarial ${advHits}/${advTotal}` +
      `${errors.length ? `   errors ${errors.length}` : ''}`);
    const thin = rows.filter((row) => !row.error && row.margin < THIN_MARGIN);
    console.log(arm === 'binary'
      ? `  cases with a verdict within ${THIN_MARGIN} of the 0.5 threshold: ` +
        `${thin.length ? thin.map((row) => row.name).join(', ') : 'none'}`
      : `  verdicts decided by a top-1/top-2 margin under ${THIN_MARGIN}: ` +
        `${thin.length ? thin.map((row) => `${row.name} @ ${row.margin.toFixed(3)}`).join(', ') : 'none'}`);
  }

  // Drift is the thing the binary `argument` question failed at: same input, different answer.
  const drift = [];
  for (let index = 0; index < CASES.length; index += 1) {
    const answers = runs.map((rows) => rows[index].got ?? `ERROR`);
    if (new Set(answers).size > 1) drift.push(`${CASES[index].name}: ${answers.join(' -> ')}`);
  }
  const totals = runs.map((rows) => rows.filter((row) => row.hit).length);
  const incoherent = runs.map((rows) => rows.filter((row) => row.incoherent).length);
  report[arm] = { totals, drift, incoherent, runs };
  console.log(`\nARM ${arm} case-level totals across ${RUNS} runs: ${totals.map((n) => `${n}/11`).join(', ')}`);
  console.log(`ARM ${arm} drift (same input, different answer): ${drift.length ? drift.join(' | ') : 'none'}`);
  if (arm === 'binary') {
    console.log(`ARM binary structurally impossible answers per run (not exactly one class true): ${incoherent.join(', ')}`);
  }
}

console.log('\n================ SIDE BY SIDE ================');
for (const [arm, data] of Object.entries(report)) {
  const stable = data.drift.length === 0;
  const perfect = data.totals.every((n) => n === 11);
  const verdict = arm === 'binary'
    ? 'baseline (the shape shipping today)'
    : perfect && stable ? 'reproduces 11/11 with no drift' : 'DOES NOT reproduce a stable 11/11';
  console.log(`${arm.padEnd(8)} case-level=${data.totals.map((n) => `${n}/11`).join(',')}  ` +
    `drifted-cases=${stable ? 0 : data.drift.length}  incoherent=${data.incoherent.join(',')}  -> ${verdict}`);
}
console.log('\nThe comparison IS the finding. An 11/11 with no baseline beside it is just a number.');

console.log('\nNO-CLAIM: this is the same 11 hand-built failures, scored against the same gold table');
console.log('that defined them, by the person who benefits from the answer. It can show that one');
console.log('multiclass question is more stable than three binary ones ON THESE ELEVEN, and nothing');
console.log('else. It cannot estimate accuracy on real tool traffic, cannot rule out that the case');
console.log('text makes its own class legible, and cannot speak to mixed causes (a flaky dependency');
console.log('exposed by a real bug) because the set contains none. Three repeats bound drift at this');
console.log('sample size only; a label that is stable across three calls can still move on the fourth.');
console.log('');
console.log('And the limit that bit the question-rescue lane tonight applies here unchanged: these');
console.log('eleven cases are the cases the classes were SHAPED against. One rescued question there');
console.log('scored 6/7 on a hold-out while answering no to all seven — a perfect-looking number from');
console.log('a degenerate answer. Nothing in this file is a hold-out. Until this same multiclass');
console.log('question is run on failures nobody wrote for it, the honest claim is stability on a');
console.log('fixed set, not accuracy. That hold-out is the next unit, and it is not this one.');
