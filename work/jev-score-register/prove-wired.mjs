/**
 * Prove the wiring end to end: drive omp-jev-commit's real handler against a REAL
 * staged diff and show the register grew.
 *
 * This is the retirement condition for jev-vbh.7 — ">=1 package exports scores a
 * second measurement reads" — so it must exercise the shipped extension, not a copy
 * of its logic.
 *
 * Run: infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *   node --experimental-strip-types work/jev-score-register/prove-wired.mjs
 */
import { execSync } from 'node:child_process';
import { readRegister } from './register.mjs';

const REGISTER = 'work/jev-score-register/scores.jsonl';
const before = readRegister(REGISTER).rows.length;

const { default: commitExt } = await import('../omp-jev-commit/src/index.ts');

// Minimal host stand-in: capture rows, expose the registered handler.
const rows = [];
let handler;
const pi = {
  on: (_event, h) => {
    handler = h;
  },
  appendEntry: async (type, data) => {
    rows.push({ type, data });
  },
};
commitExt(pi);

if (typeof handler !== 'function') {
  console.error('BLOCKED: extension registered no handler');
  process.exit(2);
}

const staged = execSync('git diff --cached --stat', { encoding: 'utf8' }).trim();
if (!staged) {
  console.error('BLOCKED: nothing staged. Stage a real change first; this proof refuses a fixture.');
  process.exit(2);
}
console.log('staged diff present:\n' + staged.split('\n').slice(-1)[0]);

await handler({
  toolName: 'bash',
  toolCallId: 'prove-wired',
  input: { command: 'git commit -F /tmp/m.txt' },
});

const after = readRegister(REGISTER).rows.length;
const decision = rows.find((r) => r.type.endsWith('decision.v1'));

console.log(`\nextension rows emitted : ${rows.length} (kind=${decision?.data?.kind ?? 'none'})`);
console.log(`register rows before   : ${before}`);
console.log(`register rows after    : ${after}`);
console.log(`NEW SCORES PERSISTED   : ${after - before}`);

if (after > before) {
  const fresh = readRegister(REGISTER).rows.slice(before);
  for (const r of fresh) {
    console.log(`  ${r.questionKey.padEnd(12)} score=${r.score} model=${r.model} identity=${r.identity.slice(0, 12)}…`);
  }
  console.log('\nRETIREMENT CONDITION MET: a shipped package exported Jev-derived scores.');
} else {
  console.log('\nNOT MET: the extension ran but persisted nothing.');
  process.exit(1);
}
