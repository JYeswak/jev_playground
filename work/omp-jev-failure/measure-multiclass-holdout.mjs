/**
 * Hold-out for the multiclass failure framing: binary vs multiclass on FRESH failures.
 *
 * WHAT THE TUNED RUN CLAIMED (measure-multiclass.mjs): one multiclass question scores 11/11
 * x3 with zero drift where three binary questions score 9,10,9,9 with moving misses — on the
 * SAME 11 hand-built cases the framing was shaped against. Same flaw as the rephrase rescues.
 *
 * THIS FILE: nine fresh failures nobody shaped anything against. Six mined from a DIFFERENT
 * session log (clutterfreespaces.ios 2026-08-29, not the omp-orchestrator log the P3-32 cases
 * came from), toolName + full arguments + failure text verbatim: four wrong paths, two
 * infrastructure timeouts. Three produced on purpose in /tmp/mc-holdout (throwaway): a bad
 * node flag, a failing assertion, a TypeError on undefined. Ground truth by reading the
 * actual error. dcg-denial rows excluded (policy refusal is a fourth class).
 *
 * Framings: BINARY = the three shipped question strings, verbatim (the same strings
 * measure-multiclass.mjs reads out of measure.mjs at runtime — copied here with that
 * provenance; a wording drift between the two files would show as a SOURCE mismatch, stated).
 * MULTI = FAILURE_QUESTION + FAILURE_CLASSES imported from ./src/index.ts, so the tested
 * framing is the shipped one by construction, not by copying.
 * Case-level scoring exactly as in measure-multiclass.mjs: binary counts only if ALL THREE
 * verdicts match (incoherent yes-counts fail); multiclass counts on top-1 choice.
 *
 * 9 cases x 2 framings x 3 runs = 54 calls.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node --experimental-strip-types work/omp-jev-failure/measure-multiclass-holdout.mjs
 */
import { askJev, askJevChoice } from '../jev-client/src/index.ts';
import { FAILURE_QUESTION, FAILURE_CLASSES } from './src/index.ts';

const BINARY = {
  transient: 'Is this failure most consistent with a transient environment or dependency failure?',
  argument: 'Is this failure most consistent with a wrong argument, path, or invocation?',
  bug: 'Is this failure most consistent with a genuine bug in the code under edit?',
};
const LABELS = ['transient', 'argument', 'bug'];
const THRESHOLD = 0.5;
const THIN_MARGIN = 0.1;

const CASES = [
  { name: 'ho-arg-outbox-path', expected: 'argument', toolName: 'eval',
    args: { language: 'js', code: 'const results = await parallel([\n  () => tool.grep({pattern:"cronDependencyRequirements", path:"apps/cfs-console/src"}),\n  () => tool.read({path:"apps/cfs-console/src/proxy.ts"}),\n  () => tool.read({path:"apps/cfs-console/src/server/intake-ack-outbox.ts"}),\n  () => tool.read({path:"apps/cfs-console/vercel.json"})\n]);\ndisplay(results);' },
    failure: "Error: Path 'apps/cfs-console/src/server/intake-ack-outbox.ts' not found" },
  { name: 'ho-arg-schema-path', expected: 'argument', toolName: 'eval',
    args: { language: 'js', code: 'const results=await parallel([\n  () => tool.read({path:"supabase/migrations/20260515020200_cfs_contacts_lifecycle.sql:1-140"}),\n  () => tool.grep({pattern:"cfs_contacts",path:"supabase/schema.sql"})\n]); display(results);' },
    failure: 'Error: Path not found: supabase/schema.sql' },
  { name: 'ho-arg-route-test-path', expected: 'argument', toolName: 'eval',
    args: { language: 'js', code: 'const results=await parallel([\n  () => tool.grep({pattern:"it\\(",path:"apps/cfs-console/src/server/auth/member-management-route.vitest.test.ts"}),\n  () => tool.grep({pattern:"it\\(",path:"apps/cfs-console/src/server/auth/route-access.vitest.test.ts"})\n]); display(results);' },
    failure: 'Error: Path not found: apps/cfs-console/src/server/auth/route-access.vitest.test.ts' },
  { name: 'ho-arg-queue-doc-path', expected: 'argument', toolName: 'eval',
    args: { language: 'js', code: 'const results=await parallel([\n  () => tool.grep({pattern:"photo-approval|photo_review",path:"apps/cfs-console/src/server/cfs"}),\n  () => tool.grep({pattern:"20260720005000",path:"MIGRATION-READY-QUEUE.md"})\n]); display(results);' },
    failure: 'Error: Path not found: MIGRATION-READY-QUEUE.md' },
  { name: 'ho-arg-bad-flag', expected: 'argument', toolName: 'bash',
    args: { command: 'node --experimental-strip-flagg' },
    failure: 'node: bad option: --experimental-strip-flagg' },
  { name: 'ho-trans-grep-timeout', expected: 'transient', toolName: 'eval',
    args: { language: 'js', code: 'const out=await parallel([\n  ()=>tool.glob({path:"apps/cfs-mobile/__tests__",limit:300}),\n  ()=>tool.grep({pattern:"classifySessionRefreshFailure|failClosedToSignedOut",path:"apps/cfs-mobile",case:false,gitignore:true})\n]); display(out);' },
    failure: 'Error: Grep timed out after 30s; narrow paths or pattern, or scope with `glob` first' },
  { name: 'ho-trans-slb-timeout', expected: 'transient', toolName: 'eval',
    args: { language: 'js', code: 'const r=await tool.bash({command:"set +e; pnpm --dir apps/cfs-console exec tsc --noEmit",cwd:"/Users/josh/Developer/clutterfreespaces.ios",timeout:300}); display(r);' },
    failure: 'Error: SLB guard timed out; refusing the Bash call' },
  { name: 'ho-bug-assert', expected: 'bug', toolName: 'bash',
    args: { command: 'node --test /tmp/mc-holdout/bug-assert.test.mjs' },
    failure: "not ok 1 - sums\n  error: |-\n    Expected values to be strictly equal:\n\n    2 !== 3\n\n  code: 'ERR_ASSERTION'" },
  { name: 'ho-bug-undef-map', expected: 'bug', toolName: 'bash',
    args: { command: 'node /tmp/mc-holdout/bug-undef.mjs' },
    failure: "TypeError: Cannot read properties of undefined (reading 'map')" },
];

const RUNS = 3;
const binaryRows = [];
const multiRows = [];
const binaryDrift = {};
const multiDrift = {};
let errors = 0;

for (let run = 1; run <= RUNS; run++) {
  for (const c of CASES) {
    const state = { toolName: c.toolName, toolCallId: `mcholdout-${c.name}`, args: c.args, failure: c.failure };
    const b = await askJev({ state, questions: BINARY, timeoutMs: 8000 });
    if (!b.ok) { binaryRows.push(`${c.name}: ERROR ${b.reason}`); errors += 1; }
    else {
      const said = Object.fromEntries(LABELS.map((l) => [l, b.scores[l] >= THRESHOLD]));
      const yes = LABELS.filter((l) => said[l]);
      const exp = { transient: c.expected === 'transient', argument: c.expected === 'argument', bug: c.expected === 'bug' };
      const hit = LABELS.every((l) => said[l] === exp[l]);
      binaryDrift[c.name] ??= [];
      binaryDrift[c.name].push(yes.length === 1 ? yes[0] : `${yes.length}-yes`);
      if (run === 1) binaryRows.push(`${c.name.padEnd(24)} binary got=${(yes.length === 1 ? yes[0] : `${yes.length}-yes[${yes.join('+') || 'none'}]`).padEnd(16)} expected=${c.expected.padEnd(10)} ${hit ? 'HIT' : 'MISS'}${yes.length !== 1 ? ' (incoherent)' : ''}`);
    }
    const mc = await askJevChoice({ state, instructions: FAILURE_QUESTION, classes: FAILURE_CLASSES, timeoutMs: 8000 });
    if (!mc.ok) { multiRows.push(`${c.name}: ERROR ${mc.reason}`); errors += 1; }
    else {
      const ordered = [...LABELS].sort((a, b2) => mc.probabilities[b2] - mc.probabilities[a]);
      const hit = mc.choice === c.expected;
      multiDrift[c.name] ??= [];
      multiDrift[c.name].push(mc.choice);
      if (run === 1) multiRows.push(`${c.name.padEnd(24)} multi  got=${String(mc.choice).padEnd(16)} expected=${c.expected.padEnd(10)} ${hit ? 'HIT' : 'MISS'} margin=${(mc.probabilities[ordered[0]] - mc.probabilities[ordered[1]]).toFixed(2)}`);
    }
  }
}

console.log('BINARY (all-three-must-match):\n' + binaryRows.join('\n'));
console.log('\nMULTICLASS (top-1 choice):\n' + multiRows.join('\n'));

const tally = (drift) => {
  let hits = 0, total = 0;
  const flips = [];
  for (const [name, vals] of Object.entries(drift)) {
    if (vals.length < 2) continue;
    total += 1;
    if (new Set(vals).size > 1) flips.push(`${name}: ${vals.join(' ')}`);
  }
  return { flips };
};
console.log('\nbinary drift:', JSON.stringify(tally(binaryDrift)));
console.log('multiclass drift:', JSON.stringify(tally(multiDrift)));

const countHits = (rows) => rows.filter((r) => r.includes(' HIT')).length;
console.log(`\nbinary run-1: ${countHits(binaryRows)}/${CASES.length}  multiclass run-1: ${countHits(multiRows)}/${CASES.length}`);
console.log(`tuned: binary case-level 9,10,9/11 per run (misses moving), multiclass 11/11 x3`);
console.log(`transport errors: ${errors}`);

console.log('\nNO-CLAIM: nine fresh failures, but six are mined for legibility (selection, not');
console.log('sampling) and three are produced by me in /tmp knowing the answer. Contains no mixed');
console.log('causes — a flaky dependency exposed by a real bug appears in neither framing, by');
console.log('anybody. A hold-out of nine earns the conversion consideration, not the conversion.');
