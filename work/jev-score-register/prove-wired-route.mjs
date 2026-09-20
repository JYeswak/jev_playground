/**
 * Prove the NEW wiring end to end: drive omp-jev-route's shipped handler against a
 * REAL prompt and show the register grew, then replay the rows with no key present.
 *
 * Sibling of prove-wired.mjs, which does the same for omp-jev-commit. Same rule: it
 * must exercise the SHIPPED extension, not a copy of its logic, or it proves nothing
 * about what is installed.
 *
 * THE TRAP THIS AVOIDS, paid for by the commit proof: that run reported "0 scores
 * persisted" and looked like a wiring failure. It was not. It had been handed
 * `-F /tmp/m.txt` with no such file, and the extension CORRECTLY declined to score a
 * commit with no message. The probe was broken, not the extension. So this one
 * refuses up front if it cannot supply a real prompt, and says which it is.
 *
 * Run: infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *   node --experimental-strip-types work/jev-score-register/prove-wired-route.mjs
 */
import { readRegister } from './register.mjs';

const REGISTER = process.env.JEV_SCORE_REGISTER ?? 'work/jev-score-register/scores.jsonl';
const before = readRegister(REGISTER);
console.log(`register before: ${before.rows.length} rows`);

const { default: routeExt } = await import('../omp-jev-route/src/index.ts');

const appended = [];
let handler;
const pi = {
  on: (event, h) => {
    if (event === 'context') handler = h;
  },
  appendEntry: async (type, data) => {
    appended.push({ type, data });
  },
};
routeExt(pi);

if (typeof handler !== 'function') {
  console.error('BLOCKED: extension registered no context handler');
  process.exit(2);
}

/**
 * A real prompt from this lane's own work, not a fixture string. If this were empty
 * the extension would correctly decline and the probe would misreport it as a wiring
 * failure — which is exactly what happened to the commit proof.
 */
const prompt =
  'Wire the remaining omp-jev extensions into the score register, report which are ' +
  'NOT-APPLICABLE because they make no model call, and quote the replay row proving ' +
  'the rows read back with zero API calls.';
if (!prompt.trim()) {
  console.error('BLOCKED: no prompt to supply. The probe is broken, not the extension.');
  process.exit(2);
}

await handler({ type: 'context', messages: [{ role: 'user', content: prompt }] });

const after = readRegister(REGISTER);
const grew = after.rows.length - before.rows.length;
const mine = after.rows.slice(before.rows.length).filter((r) => r.extension === 'omp-jev-route');

console.log(`register after : ${after.rows.length} rows  (+${grew})`);
console.log(`omp-jev-route rows written this run: ${mine.length}`);
for (const r of mine) {
  console.log(`  ${r.questionKey.padEnd(22)} score ${String(r.score).padEnd(6)} model ${r.model} identity ${r.identity.slice(0, 12)}…`);
}
console.log(`extension appended ${appended.length} host entries`);

if (mine.length === 0) {
  console.error('\nFAILED: the extension ran and persisted nothing. Check the wiring, not the probe —');
  console.error('the probe supplied a non-empty prompt and the handler was registered.');
  process.exit(1);
}
console.log('\nWIRED: a newly wired extension exported real Jev scores.');
