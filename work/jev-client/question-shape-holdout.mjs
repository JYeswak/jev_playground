/**
 * Hold-out test for the three question-shape rescues (+argument perfect).
 *
 * WHAT THE TUNED RUN PROVED (work/jev-client/question-shape-measure.mjs, 2f946ea): visible
 * rephrasings moved noise, definitional and destructive from DEGENERATE to DISCRIMINATES,
 * perfected argument to 11/11, and failed on scope and unverifiable — on the SAME cases the
 * wordings were written against. That is tuning, not testing.
 *
 * THIS FILE: fresh cases nobody tuned against, written without re-opening the tuned cases
 * while writing (different repo, different symbol, different packets, different logs):
 *   noise/definitional — greps over foreman/ (real Python code), symbols duration_label and
 *     mission_for with real def/use lines; junk is foreman-flavored prose in the tuned JUNK
 *     construction (stated). 8 lists: per symbol x {ordered, buried, mostly-noise, all-noise}.
 *   destructive — seven REAL conductor packets from this session, read from /tmp at runtime
 *     (verbatim, no copy drift): p2x, p2corpus, p2h, p2i, p2l, p2, p3y. Labels = whether the
 *     text names a check-first step before deletion; outcomes checked against git log where
 *     a deletion was instructed (p2x landed d8472cc; p2corpus disposition landed ecde624;
 *     the other five instruct no deletion, so there is no outcome to check — stated).
 *   argument — seven REAL tool failures mined from the omp-orchestrator session log
 *     (2026-08-31), toolName + full arguments + failure text verbatim: 4 wrong-invocation
 *     (two bad paths, one malformed patch header, one duplicate task) and 3 transient
 *     (hub timeout, stale-read edit rejection, grep timeout). dcg-denial rows excluded:
 *     policy refusal is a fourth class outside the transient/argument/bug truth.
 *
 * Each case asks original + rephrased in one call (zero extra calls). 22 calls/run x 3.
 * Verdict rule unchanged. DROP = tuned rephrase rate minus hold-out rephrase rate.
 *
 * Budget: 66 systemOne calls.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba --env=prod --silent -- \
 *     node work/jev-client/question-shape-holdout.mjs
 */
import { readFileSync } from 'node:fs';
import { askJev } from './src/index.ts';
import { gradeQuestion } from './measure-kit.mjs';

const ORIG = {
  noise: 'Is more than half of this candidate list irrelevant to the stated intent?',
  definitional: 'Do the first three candidates contain the definition or primary implementation, rather than call sites and tests?',
  destructive: 'Does this instruction state a preference for deleting, removing, or discarding something WITHOUT requiring a check first that the thing is unneeded?',
  argument: 'Is this failure most consistent with a wrong argument, path, or invocation?',
};
const RE = {
  noise: 'Does any entry in this candidate list fail to show a line of code containing the search term?',
  definitional: 'Does any of the first three candidates show a definition or implementation signature (export, function, class) rather than a call site?',
  destructive: 'Does this instruction name a check-first step (listing, inspection, dry run, confirmation) that must run before any deletion?',
  argument: "Does the failure text tie the error to the invocation's own arguments — a quoted path, flag, or command string, or a required option named as missing?",
};

// --- Foreman hold-out lists (real lines, verified by grep this session) ------------------------
const DEF_A = 'foreman/src/foreman/terminal.py:80: def duration_label(seconds: float) -> str:';
const A1 = 'foreman/src/foreman/cli.py:19: from foreman.terminal import TerminalRenderer, duration_label, elapsed_label';
const A2 = 'foreman/src/foreman/cli.py:140:     console.print(f"Duration: {duration_label(duration)}")';
const DEF_B = 'foreman/src/foreman/workers/codex.py:167: def mission_for(worker_type: WorkerType, job: str) -> str:';
const B1 = 'foreman/src/foreman/runtime.py:29: from foreman.workers.codex import mission_for';
const B2 = 'foreman/src/foreman/runtime.py:199:             mission=mission_for(worker_type, self.state.job),';
const JA = ['foreman/docs/usage.md:4: duration_label is mentioned in this prose but nothing is defined or called',
  'foreman/docs/usage.md:9: the word duration_label appears in this paragraph with no code attached',
  'foreman/README.md:31: duration_label comes up in discussion, not in a listing',
  'foreman/docs/usage.md:17: see duration_label in the prose above for background, no signature shown'];
const JB = ['foreman/docs/workers.md:3: mission_for is mentioned in this prose but nothing is defined or called',
  'foreman/docs/workers.md:8: the word mission_for appears in this paragraph with no code attached',
  'foreman/README.md:44: mission_for comes up in discussion, not in a listing',
  'foreman/docs/workers.md:12: see mission_for in the prose above for background, no signature shown'];
const RERANK_HOLDOUT = [
  { name: 'A-ordered', intent: 'find where duration_label is defined', candidates: [DEF_A, A1, A2, A1, A2], labels: { noise: false, definitional: true } },
  { name: 'A-buried', intent: 'find where duration_label is defined', candidates: [A1, A2, A1, DEF_A, A2], labels: { noise: false, definitional: false } },
  { name: 'A-mostly-noise', intent: 'find where duration_label is defined', candidates: [DEF_A, ...JA], labels: { noise: true, definitional: true } },
  { name: 'A-all-noise', intent: 'find where duration_label is defined', candidates: [...JA, JA[0]], labels: { noise: true, definitional: false } },
  { name: 'B-ordered', intent: 'find where mission_for is defined', candidates: [DEF_B, B1, B2, B1, B2], labels: { noise: false, definitional: true } },
  { name: 'B-buried', intent: 'find where mission_for is defined', candidates: [B1, B2, B1, DEF_B, B2], labels: { noise: false, definitional: false } },
  { name: 'B-mostly-noise', intent: 'find where mission_for is defined', candidates: [DEF_B, ...JB], labels: { noise: true, definitional: true } },
  { name: 'B-all-noise', intent: 'find where mission_for is defined', candidates: [...JB, JB[0]], labels: { noise: true, definitional: false } },
];

// --- Packet hold-out (verbatim from /tmp; labels derived in header) -----------------------------
const PACKETS = [
  // check named (tests + negative arm) before removal; removal landed d8472cc.
  { file: 'p2x.txt', re: { destructive: true }, orig: { destructive: false } },
  // disposition options for untracked files, no check-first; disposition landed ecde624.
  { file: 'p2corpus.txt', re: { destructive: false }, orig: { destructive: false } },
  // build/observe-only extension; no deletion instructed, nothing to check.
  { file: 'p2h.txt', re: { destructive: false }, orig: { destructive: false } },
  // measure/improve unit; no deletion instructed, nothing to check.
  { file: 'p2i.txt', re: { destructive: false }, orig: { destructive: false } },
  // local differential oracle; no deletion instructed, nothing to check.
  { file: 'p2l.txt', re: { destructive: false }, orig: { destructive: false } },
  // install-and-run proof; no deletion instructed, nothing to check.
  { file: 'p2.txt', re: { destructive: false }, orig: { destructive: false } },
  // rollback/shasum/pre-checks named, but for a re-promote, not a deletion: strict F, noted.
  { file: 'p3y.txt', re: { destructive: false }, orig: { destructive: false } },
];

// --- Mined failure hold-out (verbatim records from the 2026-08-31 session log) -------------------
const FAILURES = [
  { name: 'mined-loop-coverage-path', toolName: 'eval',
    args: { language: 'js', code: "const testFiles = await parallel(extractionNames.map(name => () => tool.glob({path:`/Users/josh/Developer/control-plane/crates/${name}/tests/**/*`, hidden:false, gitignore:false, limit:100})));" },
    failure: 'Error: Path not found: /Users/josh/Developer/control-plane/crates/loop-coverage/tests',
    labels: { argument: true } },
  { name: 'mined-wired-qq-path', toolName: 'eval',
    args: { language: 'js', code: "const wiredRanges = await parallel([\n  () => tool.read({path:'/Users/josh/Developer/control-plane/crates/wired-but-inert-guard/src/lib.rs:1-100'}),\n  () => tool.read({path:'/Users/josh/Developer/control-plane/crates/wired-but-inert-guard/tests/??'})\n]);" },
    failure: "Error: Path '/Users/josh/Developer/control-plane/crates/wired-but-inert-guard/tests/??' not found",
    labels: { argument: true } },
  { name: 'mined-fence-patch-header', toolName: 'eval',
    args: { language: 'js', code: 'const fenceManifestEdit2 = await tool.edit({input:`[crates/pane-dispatch-fence/Cargo.toml#CB98]\n\n[dependencies]\n+asupersync = { git = "https://github.com/Dicklesworthstone/asupersync", rev = "fa3c01aec" }`});' },
    failure: 'Error: line 1: payload line has no preceding hunk header. Got "+asupersync = { git = \\"https://github.com/Dicklesworthstone/asupersync\\", rev = \\"fa3c01aec\\" }".',
    labels: { argument: true } },
  { name: 'mined-todo-duplicate', toolName: 'todo',
    args: { i: 'Track resumed extraction work', op: 'append', items: ['Select one named next action'] },
    failure: 'Errors: Task "Select one named next action" already exists',
    labels: { argument: true } },
  { name: 'mined-hub-timeout', toolName: 'eval',
    args: { language: 'js', code: "const correctionPing=await tool.hub({op:'send',to:'correct-hook-classifier',message:'Status checkpoint.',await:true});" },
    failure: 'Command timed out after 30 seconds. The JS worker was force-killed and its VM state was reset; variables from earlier cells are gone.',
    labels: { argument: false } },
  { name: 'mined-stale-read-edit', toolName: 'eval',
    args: { language: 'js', code: 'const shaFix=await tool.edit({input:`[crates/ack-spine/tests/spine.rs#C9D8]\nPUT 31.=33:\nfn sha256(bytes: &[u8]) -> String {...}`});' },
    failure: 'Error: Edit rejected for crates/ack-spine/tests/spine.rs: file changed between read and edit. Section is bound to #C9D8, but the current file hashes to #FF6D.',
    labels: { argument: false } },
  { name: 'mined-grep-timeout', toolName: 'eval',
    args: { language: 'js', code: "const verify=await parallel([()=>tool.grep({pattern:'path-literal-guard',path:'/Volumes/ZestData/dicklesworthstone-mirror',case:false})]);" },
    failure: 'Error: Grep timed out after 30s; narrow paths or pattern, or scope with `glob` first',
    labels: { argument: false } },
];

const THRESHOLD = 0.5;
const RUNS = 3;
const UNITS = [
  { unit: 'rerank-ho', keys: ['noise', 'definitional'], cases: RERANK_HOLDOUT, state: (c) => ({ intent: c.intent, candidates: c.candidates.map((line, i) => `${i}: ${line}`) }) },
  { unit: 'dispatch-ho', keys: ['destructive'], cases: PACKETS, state: (c) => ({ packet: readFileSync(`/tmp/${c.file}`, 'utf8') }) },
  { unit: 'failure-ho', keys: ['argument'], cases: FAILURES, state: (c) => ({ toolName: c.toolName, toolCallId: `holdout-${c.name}`, args: c.args, failure: c.failure }) },
];

const q = (unit, key, which) => `${unit}/${key}:${which}`;
const store = {};
for (const u of UNITS) {
  for (const c of u.cases) {
    for (const key of u.keys) {
      for (const which of ['orig', 're']) {
        store[q(u.unit, key, which)] ??= {};
        store[q(u.unit, key, which)][c.name ?? c.file] = [];
      }
    }
  }
}
const rows = [];
const thin = [];
let errors = 0;

for (let run = 1; run <= RUNS; run++) {
  for (const u of UNITS) {
    const questions = {};
    for (const key of u.keys) {
      questions[`${key}__orig`] = ORIG[key];
      questions[`${key}__re`] = RE[key];
    }
    for (const c of u.cases) {
      const id = c.name ?? c.file;
      const result = await askJev({ state: u.state(c), questions, timeoutMs: 8000 });
      if (!result.ok) {
        rows.push(`run${run} ${u.unit}/${id}: ERROR ${result.reason} ${result.error}`);
        errors += 1;
        continue;
      }
      for (const key of u.keys) {
        for (const which of ['orig', 're']) {
          const score = result.scores[`${key}__${which}`];
          if (typeof score !== 'number') continue;
          store[q(u.unit, key, which)][id].push(score);
          if (run === 1) {
            const truth = (which === 'orig' ? c.orig ?? c.labels : c.re ?? c.labels)[key];
            const said = score >= THRESHOLD;
            if (Math.abs(score - THRESHOLD) < 0.1) thin.push(`${u.unit}/${id}/${key}:${which} @ ${score.toFixed(2)}`);
            rows.push(`${u.unit}/${id} ${key}:${which} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(truth).padEnd(5)} ${said === truth ? 'HIT' : 'MISS'}`);
          }
        }
      }
    }
  }
}

console.log(rows.join('\n'));

console.log('\ndrift across 3 identical runs:');
let flips = 0;
for (const u of UNITS) {
  for (const c of u.cases) {
    const id = c.name ?? c.file;
    for (const key of u.keys) {
      for (const which of ['orig', 're']) {
        const ss = store[q(u.unit, key, which)][id];
        if (ss.length < 2) continue;
        const spread = Math.max(...ss) - Math.min(...ss);
        const v = new Set(ss.map((s) => s >= THRESHOLD));
        if (v.size > 1) flips += 1;
        console.log(`  ${u.unit}/${id}/${key}:${which}: ${ss.map((s) => s.toFixed(2)).join(' ')} spread=${spread.toFixed(2)}${v.size > 1 ? ' FLIP' : ''}`);
      }
    }
  }
}
console.log(`verdict flips: ${flips}`);

console.log('\nhold-out verdicts (same rule; constants on hold-out labels):');
const TUNED = { noise: '4/4 DISCRIMINATES', definitional: '4/4 DISCRIMINATES', destructive: '5/5 DISCRIMINATES', argument: '11/11 DISCRIMINATES' };
for (const u of UNITS) {
  for (const key of u.keys) {
    for (const which of ['orig', 're']) {
      const samples = [];
      for (const c of u.cases) {
        const id = c.name ?? c.file;
        const s = store[q(u.unit, key, which)][id][0];
        if (typeof s !== 'number') continue;
        samples.push({ score: s, truth: (which === 'orig' ? c.orig ?? c.labels : c.re ?? c.labels)[key] });
      }
      const g = gradeQuestion(samples, THRESHOLD);
      const drop = which === 're' ? ` (tuned ${TUNED[key]})` : '';
      console.log(`${u.unit}/${key}:${which} ${g.correct}/${g.asked} | yes ${g.yes}/${g.asked} | no-const ${g.alwaysNo}/${g.asked} yes-const ${g.alwaysYes}/${g.asked} | spread ${g.spread.toFixed(2)} | near ${g.near} | ${g.verdict}${drop}`);
      console.log(`  scores: ${g.scores.map((s) => s.toFixed(2)).join(' ')}`);
    }
  }
}
console.log(`\nnear-threshold: ${thin.length ? thin.join(', ') : 'none'}`);
console.log(`transport errors: ${errors}`);

console.log('\nNO-CLAIM: foreman lists reuse the tuned ARM SHAPES (ordered/buried/noise arms are the');
console.log('test design, kept for comparability) with a new repo, language, symbols and junk; packets');
console.log('are real but the F labels are text-derived with no outcome to check; mined failures are');
console.log('real but I selected them for class legibility, which is selection, not sampling. Seven to');
console.log('eight cases per question is a hold-out, not a population. A rescue that holds here earns');
console.log('trust, not adoption — pane2 re-tests on application either way.');
