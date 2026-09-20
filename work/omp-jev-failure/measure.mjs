/**
 * Ground-truth measurement for the omp-jev-failure questions.
 *
 * The extension logs three confident-looking scores per errored tool. Nobody had ever checked
 * one of them against a known answer. This does that, the same way work/omp-jev-rerank/measure.mjs
 * did — and that measurement deleted 2 of 3 questions.
 *
 * Method: eleven hand-built tool failures whose cause WE know by construction, three classes:
 *   transient  — the environment/dependency flaked; the identical invocation can succeed on retry
 *   argument   — the invocation was wrong; it fails identically forever until the caller changes
 *   bug        — the code under edit is broken; the tool did its job and reported real breakage
 * Nine are plain (the class is legible in the error text). Two are ADVERSARIAL: the misleading
 * keyword leads, the disambiguating evidence follows, and both are answerable from `state` alone.
 * Classes are mutually exclusive, so each question is TRUE on 3-4 of 11 cases and FALSE on the
 * rest. That asymmetry is why the per-question block prints the always-no / always-yes constants:
 * a question must beat ITS OWN CONSTANT, not the pooled coin flip, to have said anything.
 *
 * The questions are copied here rather than imported from src/index.ts on purpose: this file has
 * to keep reproducing the finding after the degenerate questions are cut from the extension.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-failure/measure.mjs
 */
import { askJev } from '../jev-client/src/index.ts';
import { gradeQuestion } from '../jev-client/measure-kit.mjs';

const QUESTIONS = {
  transient: 'Is this failure most consistent with a transient environment or dependency failure?',
  argument: "Does this error tie to the invocation's own arguments, path, or command rather than the environment?",
  bug: 'Is this failure most consistent with a genuine bug in the code under edit?',
};

const T = { transient: true, argument: false, bug: false };
const A = { transient: false, argument: true, bug: false };
const B = { transient: false, argument: false, bug: true };

const CASES = [
  {
    name: 'econnreset-fetch',
    truth: T,
    // Socket died mid-response against a healthy URL. Same call succeeds on retry.
    toolName: 'bash',
    args: { command: 'curl -sS https://api.typesafe.ai/v1/systemone' },
    failure: 'curl: (56) Recv failure: Connection reset by peer\nread ECONNRESET\n    at TLSWrap.onStreamRead (node:internal/stream_base_commons:218:20)',
  },
  {
    name: 'rate-limit-429',
    truth: T,
    // Server explicitly says "later". Retry-After is the definition of transient.
    toolName: 'bash',
    args: { command: 'npm install' },
    failure: 'npm ERR! code E429\nnpm ERR! 429 Too Many Requests - GET https://registry.npmjs.org/typescript\nnpm ERR! Retry-After: 30',
  },
  {
    name: 'upstream-504',
    truth: T,
    // Gateway timeout from an upstream we do not own; our request was well-formed.
    toolName: 'bash',
    args: { command: 'git push origin main' },
    failure: 'fatal: unable to access https://github.com/zeststream/jev.git/: The requested URL returned error: 504 Gateway Timeout',
  },
  {
    name: 'enoent-mistyped-path',
    truth: A,
    // `wrok/` for `work/`. Deterministic, forever, until the caller fixes the string.
    toolName: 'read',
    args: { path: 'wrok/jev-client/src/index.ts' },
    failure: "ENOENT: no such file or directory, open 'wrok/jev-client/src/index.ts'",
  },
  {
    name: 'permission-denied-system-path',
    truth: A,
    // Defensible as `argument`: /usr/lib is the wrong target for a project write. It is not
    // transient (identical on every retry, no dependency flaked) and it is not a bug in the code
    // under edit (no code ran; the kernel refused the destination). The invocation named a path
    // the caller has no business writing to, which is exactly a wrong-argument failure.
    toolName: 'write',
    args: { path: '/usr/lib/jev-config.json' },
    failure: "EACCES: permission denied, open '/usr/lib/jev-config.json'",
  },
  {
    name: 'unknown-flag',
    truth: A,
    // The tool is fine; the caller passed a flag it does not have.
    toolName: 'bash',
    args: { command: 'node --experimental-strip-typs work/omp-jev-failure/measure.mjs' },
    failure: 'node: bad option: --experimental-strip-typs',
  },
  {
    name: 'type-error-under-edit',
    truth: B,
    // Stack frame lands inside the file being edited. Real breakage, reported correctly.
    toolName: 'bash',
    args: { command: 'node --experimental-strip-types work/omp-jev-failure/measure.mjs' },
    failure: 'TypeError: result.scores.map is not a function\n    at buildRow (work/omp-jev-failure/src/index.ts:71:31)\n    at handleToolExecutionEnd (work/omp-jev-failure/src/index.ts:83:11)',
  },
  {
    name: 'assertion-expected-actual',
    truth: B,
    // A test named an expected value and got another. The tool did its job.
    toolName: 'bash',
    args: { command: 'node --test work/omp-jev-failure/test/failure.test.mjs' },
    failure: "AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:\n\n'failure_error' !== 'failure_scored'\n\n    at TestContext.<anonymous> (work/omp-jev-failure/test/failure.test.mjs:16:10)\n  expected: 'failure_scored'\n  actual: 'failure_error'",
  },
  {
    name: 'undefined-property-under-edit',
    truth: B,
    // Reading through an unchecked optional in the module just changed.
    toolName: 'bash',
    args: { command: 'node --experimental-strip-types work/omp-jev-failure/live-probe.mjs' },
    failure: "TypeError: Cannot read properties of undefined (reading 'scores')\n    at work/omp-jev-failure/src/index.ts:81:20",
  },
  // --- ADVERSARIAL ARMS ---------------------------------------------------------------------
  // The nine above spell their class in the first token, so a perfect score on them would only
  // show the questions read English. These two put the misleading keyword up front and the real
  // evidence behind it. The evidence IS in `state` both times — this tests reading, not clairvoyance.
  {
    name: 'adv-econnrefused-is-a-bug',
    truth: B,
    // Reads "transient network". Is not: our own code computed an undefined port, and the frame
    // that did it is in the file under edit. Retrying forever will never connect to port undefined.
    toolName: 'bash',
    args: { command: 'node --experimental-strip-types work/omp-jev-failure/live-probe.mjs' },
    failure: 'Error: connect ECONNREFUSED 127.0.0.1:undefined\n    at buildEndpoint (work/omp-jev-failure/src/index.ts:20:18)\n    at probe (work/omp-jev-failure/live-probe.mjs:11:20)\n  port resolved to undefined from config.port',
  },
  {
    name: 'adv-typeerror-is-an-argument',
    truth: A,
    // Reads "bug in the code under edit". Is not: every frame is inside node_modules, none in our
    // source, and the invocation omits the option the library requires. Supplying --path fixes it.
    toolName: 'bash',
    args: { command: 'npx jev-tool run --verbose' },
    failure: "TypeError: Cannot read properties of undefined (reading 'split')\n    at Command._parseOptionValue (node_modules/commander/lib/command.js:1412:26)\n    at Command.parse (node_modules/commander/lib/command.js:988:12)\n    at Object.<anonymous> (node_modules/jev-tool/bin/cli.js:7:9)\n  (no frame in this repository; required option --path <p> was not supplied)",
  },
];

const THRESHOLD = 0.5;
const KEYS = Object.keys(QUESTIONS);
const perQuestion = Object.fromEntries(KEYS.map((key) => [key, { correct: 0, asked: 0, yes: 0, trueCount: 0, scores: [], truths: [] }]));
let correct = 0;
let total = 0;
let advCorrect = 0;
let advTotal = 0;
const thin = [];
const rows = [];

for (const testCase of CASES) {
  const result = await askJev({
    state: {
      toolName: testCase.toolName,
      toolCallId: `measure-${testCase.name}`,
      args: testCase.args,
      failure: testCase.failure,
    },
    questions: QUESTIONS,
    timeoutMs: 8000,
  });
  if (!result.ok) {
    rows.push(`${testCase.name.padEnd(30)} ERROR ${result.reason} ${result.error}`);
    continue;
  }
  for (const key of KEYS) {
    const score = result.scores[key];
    if (typeof score !== 'number') continue;
    const said = score >= THRESHOLD;
    const truth = testCase.truth[key];
    const hit = said === truth;
    const adversarial = testCase.name.startsWith('adv-');
    total += 1;
    if (hit) correct += 1;
    if (adversarial) { advTotal += 1; if (hit) advCorrect += 1; }
    // A verdict decided by 0.04 is a verdict the threshold made, not the model.
    if (Math.abs(score - THRESHOLD) < 0.1) thin.push(`${testCase.name}/${key} @ ${score.toFixed(2)}`);
    const stat = perQuestion[key];
    stat.asked += 1;
    stat.scores.push(score);
    stat.truths.push(truth);
    if (said) stat.yes += 1;
    if (truth) stat.trueCount += 1;
    if (hit) stat.correct += 1;
    rows.push(`${testCase.name.padEnd(30)} ${key.padEnd(10)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(truth).padEnd(5)} ${hit ? 'HIT' : 'MISS'}${adversarial ? ' (adversarial)' : ''}`);
  }
}

console.log(rows.join('\n'));
console.log(`\nagreement with ground truth: ${correct}/${total}`);
console.log(`a coin flip on ${total} items is ${(total / 2).toFixed(1)}`);
console.log(`of which the 2 adversarial cases (misleading keyword, evidence behind it): ${advCorrect}/${advTotal}`);
console.log(`verdicts decided within 0.10 of the ${THRESHOLD} threshold: ${thin.length ? thin.join(', ') : 'none'}`);

console.log('\nper question (a question must beat its own constant, not the coin flip):');
for (const key of KEYS) {
  const stat = perQuestion[key];
  if (stat.asked === 0) { console.log(`${key.padEnd(10)} never answered`); continue; }
  const g = gradeQuestion(stat.scores.map((s, i) => ({ score: s, truth: stat.truths[i] })), THRESHOLD);
  console.log(
    `${key.padEnd(10)} ${g.correct}/${g.asked} correct | said-yes ${g.yes}/${g.asked} | ` +
    `always-no would score ${g.alwaysNo}/${g.asked}, always-yes ${g.alwaysYes}/${g.asked} | ` +
    `score spread ${g.spread.toFixed(2)} | near ${g.near} | ${g.verdict}`,
  );
  console.log(`${' '.repeat(10)} scores: ${g.scores.map((s) => s.toFixed(2)).join(' ')}`);
}

console.log('\nNO-CLAIM: 11 hand-built failures I wrote knowing the answer. Cases I author cannot');
console.log('establish accuracy on real tool traffic; cannot rule out that I wrote failures whose');
console.log('class my own phrasing made legible; and cannot settle genuinely mixed causes (a flaky');
console.log('dependency exposed by a real bug) because none are in the set. Two adversarial arms');
console.log('are two, not a distribution. This shows the questions are not constants. It does not');
console.log('show they are right about a failure nobody constructed for them.');
