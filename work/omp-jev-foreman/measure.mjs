/**
 * Ground-truth measurement for omp-jev-foreman questions.
 *
 * Three byte-identical runs, eight constructed windows, per-question constant baselines and every
 * near-threshold score. This is a measurement of hand-built cases, not a production accuracy claim.
 */
import { askJev } from '../../work/jev-client/src/index.ts';

const QUESTIONS = {
  repeating: 'Is the agent repeating itself or retrying the same obstacle?',
  progress: 'Is the agent making meaningful progress toward its task?',
  stuck: 'Is the agent stuck on one obstacle rather than progressing?',
};

const CASES = [
  { name: 'same-failing-command', truth: { repeating: true, progress: false, stuck: true }, window: ['npm test', 'npm test', 'npm test'].map((command) => ({ toolName: 'bash', command, isError: true })) },
  { name: 'varied-edits', truth: { repeating: false, progress: true, stuck: false }, window: ['read a.ts', 'edit a.ts', 'write b.ts', 'run test'].map((command) => ({ toolName: 'bash', command, isError: false })) },
  { name: 'twenty-reads-no-writes', truth: { repeating: false, progress: false, stuck: true }, window: Array.from({ length: 20 }, (_, i) => ({ toolName: 'read', command: `read file-${i}.ts`, isError: false })) },
  { name: 'build-test-commit', truth: { repeating: false, progress: true, stuck: false }, window: ['edit src/index.ts', 'npm test', 'git diff', 'git commit -am fix'].map((command) => ({ toolName: 'bash', command, isError: false })) },
  { name: 'retry-then-move-on', truth: { repeating: false, progress: true, stuck: false }, window: ['npm test', 'npm test', 'edit src/fix.ts', 'npm test', 'git diff'].map((command) => ({ toolName: 'bash', command, isError: command === 'npm test' })) },
  { name: 'same-permission-failure', truth: { repeating: true, progress: false, stuck: true }, window: ['chmod -R 777 /etc', 'chmod -R 777 /etc', 'chmod -R 777 /etc'].map((command) => ({ toolName: 'bash', command, isError: true })) },
  { name: 'multi-file-refactor', truth: { repeating: false, progress: true, stuck: false }, window: ['read a.ts', 'edit a.ts', 'edit b.ts', 'write test.ts', 'npm test'].map((command) => ({ toolName: 'bash', command, isError: false })) },
  { name: 'test-fix-commit', truth: { repeating: false, progress: true, stuck: false }, window: ['npm test', 'edit fix.ts', 'npm test', 'git commit -am fix'].map((command) => ({ toolName: 'bash', command, isError: false })) },
];

const run = Number(process.env.FOREMAN_RUN ?? 1);
const rows = [];
for (const item of CASES) {
  const result = await askJev({ state: { window: item.window, trigger: 'measurement' }, questions: QUESTIONS, timeoutMs: 6000 });
  if (!result.ok) {
    console.log(JSON.stringify({ run, case: item.name, kind: 'error', reason: result.reason, error: result.error, latencyMs: result.latencyMs }));
    continue;
  }
  for (const key of Object.keys(QUESTIONS)) {
    const score = result.scores[key];
    const truth = item.truth[key];
    const said = score >= 0.5;
    const near = score >= 0.4 && score <= 0.6;
    const row = { run, case: item.name, question: key, score, truth, said, verdict: said === truth ? 'HIT' : 'MISS', near, latencyMs: result.latencyMs };
    rows.push(row);
    console.log(JSON.stringify(row));
  }
}

for (const key of Object.keys(QUESTIONS)) {
  const questionRows = rows.filter((row) => row.question === key);
  const positives = questionRows.filter((row) => row.truth).length;
  const alwaysNo = questionRows.filter((row) => !row.truth).length / CASES.length;
  const alwaysYes = positives / CASES.length;
  const hits = questionRows.filter((row) => row.verdict === 'HIT').length;
  const near = questionRows.filter((row) => row.near).length;
  const scores = questionRows.map((row) => row.score);
  console.log(JSON.stringify({ run, summary: key, hits, denominator: questionRows.length, alwaysNo, alwaysYes, coinFlip: 0.5, nearThreshold: near, min: Math.min(...scores), max: Math.max(...scores) }));
}
