/**
 * Ground-truth measurement for the omp-jev-review questions.
 *
 * The extension logs three confident-looking scores per `git diff` and NOBODY HAS EVER CHECKED
 * them against a known answer. This checks them, the way work/omp-jev-rerank/measure.mjs did —
 * that measurement found 2 of 3 questions were constants and they were cut.
 *
 * Method: seven hand-built diffs whose answers we know BY CONSTRUCTION (we wrote the diff to
 * have the property). Each question is scored on each case at threshold 0.5, so every question
 * has a right answer on every case. The per-question split is the load-bearing output: a
 * question that returns the same verdict on all seven cases is DEGENERATE — its contribution to
 * any total is base rate, not judgement.
 *
 * NOTE ON WHAT IS MEASURED. This measures the QUESTIONS against real diff TEXT. The shipped
 * extension passes `state: { diff: command }` — the command string (`git diff HEAD~1`), not the
 * diff body. So these numbers are an UPPER BOUND on the extension: they score the questions on
 * the richest input they could ever get. Measuring first, changing behaviour later.
 *
 * Run:
 *   infisical run --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
 *     node --experimental-strip-types work/omp-jev-review/measure.mjs
 */
import { askJev } from '../jev-client/src/index.ts';

/**
 * The THREE questions the extension shipped with. `scope` is kept here on purpose after being
 * cut from src/index.ts: the measurement is the evidence for the cut, so it has to stay
 * reproducible. `behaviour` and `boundary` are verbatim from src/index.ts; if they drift from
 * these, the measurement is measuring something the extension no longer asks.
 */
const QUESTIONS = {
  behaviour: 'Does this diff alter behaviour that an existing caller depends on?',
  boundary: 'Does this diff touch a security, permission, or authentication boundary?',
  scope: 'Is this diff larger or more invasive than a routine change of its kind?',
};

const COMMENT_ONLY = `commit a1b2c3d
    docs: fix typo in the retry comment

diff --git a/src/retry.ts b/src/retry.ts
index 1111111..2222222 100644
--- a/src/retry.ts
+++ b/src/retry.ts
@@ -3,7 +3,7 @@ export function retry(fn: () => Promise<void>, attempts = 3) {
-  // retry the funciton up to \`attempts\` times
+  // Retry the function up to \`attempts\` times.
   let last: unknown;
   for (let i = 0; i < attempts; i += 1) {
     try {
`;

const DEFAULT_CHANGED = `commit b2c3d4e
    chore: adjust retry default

diff --git a/src/retry.ts b/src/retry.ts
index 2222222..3333333 100644
--- a/src/retry.ts
+++ b/src/retry.ts
@@ -1,4 +1,4 @@
-export function retry(fn: () => Promise<void>, attempts = 3) {
+export function retry(fn: () => Promise<void>, attempts = 1) {
   let last: unknown;
   for (let i = 0; i < attempts; i += 1) {
     try {
`;

const AUTH_DELETED = `commit c3d4e5f
    fix: unblock the staging dashboard

diff --git a/src/server/dashboard.ts b/src/server/dashboard.ts
index 4444444..5555555 100644
--- a/src/server/dashboard.ts
+++ b/src/server/dashboard.ts
@@ -12,9 +12,6 @@ export async function handleDashboard(req: Request): Promise<Response> {
   const session = await readSession(req);
-  if (!session || !session.roles.includes('admin')) {
-    return new Response('forbidden', { status: 403 });
-  }
   const rows = await db.query('select * from tenants');
   return Response.json(rows);
 }
`;

const PERM_WIDENED = `commit d4e5f60
    chore: cors tweak so the preview build works

diff --git a/src/server/cors.ts b/src/server/cors.ts
index 6666666..7777777 100644
--- a/src/server/cors.ts
+++ b/src/server/cors.ts
@@ -1,5 +1,5 @@
 export const corsOptions = {
-  allowedOrigins: ['https://app.example.com'],
-  credentials: true,
+  allowedOrigins: ['*'],
+  credentials: true,
 };
`;

/** 400 changed lines of a mechanical internal rename, sold as "tidy up". */
const BIG_REFACTOR = (() => {
  const body = [];
  for (let i = 0; i < 200; i += 1) {
    body.push(`-  const tmp${i} = mkNode(${i});`);
    body.push(`+  const node${i} = makeNode(${i});`);
  }
  return `commit e5f6071
    tidy up

diff --git a/src/graph/build.ts b/src/graph/build.ts
index 8888888..9999999 100644
--- a/src/graph/build.ts
+++ b/src/graph/build.ts
@@ -20,400 +20,400 @@ export function buildGraph(): Graph {
${body.join('\n')}
   return graph;
 }
`;
})();

const NEW_TEST_FILE = `commit f607182
    test: cover the empty-input path

diff --git a/test/slug.test.mjs b/test/slug.test.mjs
new file mode 100644
index 0000000..aaaaaaa
--- /dev/null
+++ b/test/slug.test.mjs
@@ -0,0 +1,9 @@
+import test from 'node:test';
+import assert from 'node:assert/strict';
+import { slug } from '../src/slug.ts';
+
+test('an empty string slugs to an empty string', () => {
+  assert.equal(slug(''), '');
+});
+test('spaces become hyphens', () => {
+  assert.equal(slug('a b'), 'a-b');
+});
`;

const DEP_BUMP = `commit 0718293
    build(deps): bump undici 6.19.2 -> 6.21.0

diff --git a/package.json b/package.json
index bbbbbbb..ccccccc 100644
--- a/package.json
+++ b/package.json
@@ -8,7 +8,7 @@
   "dependencies": {
-    "undici": "6.19.2"
+    "undici": "6.21.0"
   }
 }
diff --git a/package-lock.json b/package-lock.json
index ddddddd..eeeeeee 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -44,8 +44,8 @@
     "node_modules/undici": {
-      "version": "6.19.2",
-      "resolved": "https://registry.npmjs.org/undici/-/undici-6.19.2.tgz",
-      "integrity": "sha512-oldoldoldoldoldoldoldoldoldoldoldoldoldoldoldold=="
+      "version": "6.21.0",
+      "resolved": "https://registry.npmjs.org/undici/-/undici-6.21.0.tgz",
+      "integrity": "sha512-newnewnewnewnewnewnewnewnewnewnewnewnewnewnewnew=="
     }
 }
`;

/**
 * `truth` is known by construction — we wrote each diff to have exactly these properties.
 * `why` is the defence, recorded so a reader can disagree with a specific label rather than
 * with the total. The dep-bump row is the only judgement call; see its note.
 */
const CASES = [
  {
    name: 'comment-only',
    diff: COMMENT_ONLY,
    truth: { behaviour: false, boundary: false, scope: false },
    why: 'one comment line; no token of executable code changes',
  },
  {
    name: 'default-changed',
    diff: DEFAULT_CHANGED,
    truth: { behaviour: true, boundary: false, scope: false },
    why: 'exported default attempts 3 -> 1: every caller that omitted the arg now retries less',
  },
  {
    name: 'auth-check-deleted',
    diff: AUTH_DELETED,
    truth: { behaviour: true, boundary: true, scope: false },
    why: 'an admin-role gate is removed: authentication boundary, and 403 becomes 200',
  },
  {
    name: 'cors-widened',
    diff: PERM_WIDENED,
    truth: { behaviour: true, boundary: true, scope: false },
    why: 'origin allowlist -> "*": permission boundary, and previously-rejected origins now pass',
  },
  {
    name: 'big-refactor-tidy',
    diff: BIG_REFACTOR,
    truth: { behaviour: false, boundary: false, scope: true },
    why: '400 changed lines under the message "tidy up"; rename is mechanical and local',
  },
  {
    name: 'new-test-file',
    diff: NEW_TEST_FILE,
    truth: { behaviour: false, boundary: false, scope: false },
    why: 'a new isolated test file; no shipped code path is reachable differently',
  },
  {
    name: 'dep-bump-lockfile',
    diff: DEP_BUMP,
    // JUDGEMENT CALL, stated so it can be argued with: behaviour=true. The question is whether
    // behaviour a CALLER DEPENDS ON changes, not whether the local source changed. A runtime
    // HTTP client moving 6.19.2 -> 6.21.0 swaps executed code under every caller with no
    // call-site edit to notice — that is precisely the class this extension exists to flag.
    // If you score it false, subtract 1 from `behaviour` below; it does not change any verdict.
    truth: { behaviour: true, boundary: false, scope: false },
    why: 'runtime dependency upgrade: executed code changes under unchanged call sites',
  },
];

const THRESHOLD = 0.5;
const KEYS = Object.keys(QUESTIONS);

/** per-question tallies, so degeneracy is visible rather than averaged away */
const perQuestion = Object.fromEntries(KEYS.map((k) => [k, { correct: 0, total: 0, saids: [], scores: [] }]));
const rows = [];
const errors = [];
let correct = 0;
let total = 0;

for (const testCase of CASES) {
  const result = await askJev({
    state: { diff: testCase.diff.slice(0, 12000) },
    questions: QUESTIONS,
    timeoutMs: 30000,
  });
  if (!result.ok) {
    const line = `${testCase.name.padEnd(18)} ERROR ${result.reason}: ${result.error}`;
    rows.push(line);
    errors.push(line);
    continue;
  }
  for (const key of KEYS) {
    const score = result.scores[key];
    if (typeof score !== 'number') {
      rows.push(`${testCase.name.padEnd(18)} ${key.padEnd(10)} MISSING SCORE`);
      continue;
    }
    const said = score >= THRESHOLD;
    const truth = testCase.truth[key];
    const hit = said === truth;
    total += 1;
    if (hit) correct += 1;
    perQuestion[key].total += 1;
    if (hit) perQuestion[key].correct += 1;
    perQuestion[key].saids.push(said);
    perQuestion[key].scores.push(score);
    rows.push(
      `${testCase.name.padEnd(18)} ${key.padEnd(10)} score=${score.toFixed(2)} said=${String(said).padEnd(5)} truth=${String(truth).padEnd(5)} ${hit ? 'HIT' : 'MISS'}`,
    );
  }
}

console.log('per-case:\n');
console.log(rows.join('\n'));

console.log('\nper-question:\n');
const degenerate = [];
for (const key of KEYS) {
  const q = perQuestion[key];
  if (q.total === 0) {
    console.log(`${key.padEnd(10)} no scores returned`);
    continue;
  }
  const allSame = q.saids.every((s) => s === q.saids[0]);
  const spread = Math.max(...q.scores) - Math.min(...q.scores);
  if (allSame) degenerate.push(key);
  console.log(
    `${key.padEnd(10)} ${q.correct}/${q.total}  said=[${q.saids.map((s) => (s ? 'Y' : 'n')).join('')}]  scores=[${q.scores.map((s) => s.toFixed(2)).join(' ')}]  spread=${spread.toFixed(2)}  ${allSame ? `DEGENERATE (constant ${q.saids[0]})` : 'discriminates'}`,
  );
}

console.log(`\nagreement with ground truth: ${correct}/${total}`);
console.log(`a coin flip on ${total} items is ${(total / 2).toFixed(1)}`);
if (degenerate.length > 0) {
  console.log(`DEGENERATE questions (same verdict on every case): ${degenerate.join(', ')}`);
  console.log('Their contribution to the total is base rate, not judgement.');
}
if (errors.length > 0) {
  console.log(`\n${errors.length} case(s) errored — the total above is over the cases that answered.`);
}
console.log(
  `NO-CLAIM: ${CASES.length} hand-built diffs, written by the same person who labelled them, scored once at threshold 0.5.\n` +
    'This bounds nothing about real review traffic, says nothing about calibration between 0.4 and 0.6,\n' +
    'and cannot detect a question that is right here and wrong on diffs nobody thought to write.',
);
