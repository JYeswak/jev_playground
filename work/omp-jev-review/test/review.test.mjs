import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevReview, { setDiffRunner, isThinDiff, touchesCodeFile } from '../src/index.ts';
import { requireSdkInstalled } from '../../sdk/require-installed.mjs';

requireSdkInstalled();

function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (event) => handler(event),
    pi: {
      on: (_e, cb) => { handler = cb; },
      appendEntry: async (type, data) => { rows.push({ type, data }); },
    },
  };
}
const decisions = (h) => h.rows.filter((r) => r.type.endsWith('decision.v1'));
const diffCall = (command) => ({ toolName: 'bash', toolCallId: 'tc-1', input: { command } });
const stubDiff = (body = 'diff --git a/a b/a\n+changed\n') => setDiffRunner(async () => body);
// A diff the gate must let through: @@ hunks with 12 changed lines.
const SUBSTANTIAL = 'diff --git a/a.ts b/a.ts\n@@ -1,6 +1,6 @@\n' +
  Array.from({ length: 12 }, (_, i) => `+added line ${i}`).join('\n') + '\n';
// The bar's planted negative: >100 changed lines must still score.
const BIG = 'diff --git a/big.ts b/big.ts\n@@ -1,60 +1,60 @@\n' +
  Array.from({ length: 120 }, (_, i) => `+added line ${i}`).join('\n') + '\n';
// One fetch stub serving both calls: the gate reads `applicability`, the
// scorer reads the rest. Omit a key to simulate that answer missing.
// Responses are clone()-capable: the SDK buffers via response.clone().body
// (same requirement work/jev-client/test documents for its fakes).
const answersFetch = (answers) => {
  const mk = () => ({
    ok: true,
    status: 200,
    headers: { get: () => 'application/json' },
    text: async () => JSON.stringify({ answers }),
    clone: () => mk(),
  });
  return async () => mk();
};

test('ignores every tool call that is not a git diff or show', async () => {
  const h = host();
  ompJevReview(h.pi);
  for (const event of [
    diffCall('echo hello'),
    { toolName: 'read', toolCallId: 'x', input: { command: 'git diff' } },
    { toolName: 'bash', toolCallId: 'y', input: {} },
  ]) assert.equal(await h.fire(event), undefined);
  assert.equal(h.rows.length, 0, 'a non-diff call must not even emit a diagnostic');
});

test('an unset API key records review_error, never a scored pass', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    stubDiff(SUBSTANTIAL);
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff HEAD~1'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.equal('probabilities' in row.data, false);   // RED if a default ever reappears
    assert.match(row.data.error, /unconfigured: TYPESAFE_API_KEY is not set/);
    assert.equal(row.data.failure, 'unconfigured');
  } finally {
    if (previous !== undefined) process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a throwing transport records review_error and never breaks the session', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = async () => { throw new Error('connection reset'); };
  try {
    stubDiff(SUBSTANTIAL);
    const h = host();
    ompJevReview(h.pi);
    assert.equal(await h.fire(diffCall('git show abc123')), undefined);
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.equal('probabilities' in row.data, false);
    assert.match(row.data.error, /connection reset/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a real score is recorded as review_scored with its probabilities', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = answersFetch({ behaviour: { noul: 0.82 }, boundary: { noul: 0.18 } });
  try {
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff --cached'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_scored');
    assert.deepEqual(row.data.probabilities, { behaviour: 0.82, boundary: 0.18 });
    assert.equal('error' in row.data, false);
    assert.equal(row.data.model, 'jev-1.13.0');
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a 200 with no probabilities is an error, not a silent pass', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  const mk = (body) => ({
    ok: true, status: 200, headers: { get: () => 'application/json' },
    text: async () => JSON.stringify(body), clone: () => mk(body),
  });
  globalThis.fetch = async () => mk({ unexpected: true });
  try {
    stubDiff(SUBSTANTIAL);
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.match(row.data.error, /no-answers/);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a host whose appendEntry throws still returns undefined', async () => {
  const h = host();
  ompJevReview({ on: h.pi.on, appendEntry: async () => { throw new Error('log sink down'); } });
  assert.equal(await h.fire(diffCall('git diff')), undefined);
});

// `scope` was cut after measure.mjs found it constant-false on all seven ground-truth diffs,
// including the 400-line "tidy up" it existed to catch. This pins the cut: re-adding a question
// puts it back on the wire, and that must fail here rather than quietly resume logging a score
// nobody has measured.
test('asks exactly the two measured questions and no more', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  const calls = [];
  const mk = (answers) => ({
    ok: true, status: 200, headers: { get: () => 'application/json' },
    text: async () => JSON.stringify({ answers }), clone: () => mk(answers),
  });
  globalThis.fetch = async (_url, init) => {
    const sent = JSON.parse(init.body);
    calls.push(sent);
    return mk({ behaviour: { noul: 0.5 }, boundary: { noul: 0.5 } });
  };
  try {
    stubDiff(SUBSTANTIAL);
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff'));
    assert.equal(calls.length, 1, 'one scoring call, no gate call');
    assert.deepEqual(Object.keys(calls[0].questions).sort(), ['behaviour', 'boundary']);
    assert.equal(calls[0].state.diff.includes('added line 0'), true);
    assert.equal(calls[0].state.diff.includes('git diff'), false);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('an empty diff is an error and does not call Jev', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  globalThis.fetch = async () => { called += 1; return { ok: true, status: 200, text: async () => '{}' }; };
  try {
    stubDiff('   \n');
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.failure, 'empty-diff');
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a shell metacharacter is not executed and not scored', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  let ran = 0;
  globalThis.fetch = async () => { called += 1; return { ok: true, status: 200, text: async () => '{}' }; };
  try {
    setDiffRunner(async () => { ran += 1; return 'should not run'; });
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff; echo pwned'));
    const [row] = decisions(h);
    assert.equal(row.data.failure, 'unsafe-command');
    assert.equal(ran, 0);
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('isThinDiff boundary: hunks, line counts, headers', () => {
  assert.equal(isThinDiff('diff --git a/a b/a\n+one\n'), true, 'no hunks is thin');
  assert.equal(isThinDiff(''), true, 'empty is thin');
  const hunk = (n) =>
    'diff --git a/a b/a\n@@ -1 +1 @@\n' + '+x\n'.repeat(n) + '-y\n'.repeat(n);
  assert.equal(isThinDiff(hunk(4)), true, '8 changed lines is thin');
  assert.equal(isThinDiff(hunk(5)), false, '10 changed lines scores');
  assert.equal(
    isThinDiff('diff --git a/a b/a\n--- a/a\n+++ b/a\n@@ -1 +1 @@\n context\n'),
    true,
    'headers and context never count; 0 changed lines is thin',
  );
});

test('a thin diff records applicable:false and never calls Jev', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  globalThis.fetch = async () => { called += 1; throw new Error('must not be called'); };
  try {
    stubDiff('diff --git a/a.ts b/a.ts\n+one line\n');
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_not_applicable');
    assert.equal(row.data.applicable, false);
    assert.equal(row.data.reason, 'thin-diff');
    assert.equal(called, 0, 'thin path spends zero Jev calls');
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a docs-only diff records applicable:false and never calls Jev', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  globalThis.fetch = async () => { called += 1; throw new Error('must not be called'); };
  try {
    stubDiff(
      'diff --git a/README.md b/README.md\n@@ -1,6 +1,6 @@\n' +
        Array.from({ length: 12 }, (_, i) => `+doc line ${i}`).join('\n') + '\n',
    );
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_not_applicable');
    assert.equal(row.data.applicable, false);
    assert.equal(row.data.reason, 'non-code-diff');
    assert.equal(called, 0, 'deterministic refusal spends zero Jev calls');
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('planted negative: a >100-line code diff still scores', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = answersFetch({ behaviour: { noul: 0.7 }, boundary: { noul: 0.2 } });
  try {
    stubDiff(BIG);
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff --stat'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_scored');
    assert.deepEqual(row.data.probabilities, { behaviour: 0.7, boundary: 0.2 });
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('touchesCodeFile: draw-derived extensions only', () => {
  const f = (name) => `diff --git a/${name} b/${name}\n@@ -1 +1 @@\n+x\n`;
  assert.equal(touchesCodeFile(f('a.ts')), true);
  assert.equal(touchesCodeFile(f('dir/b.mjs')), true);
  assert.equal(touchesCodeFile(f('c.py')), true);
  assert.equal(touchesCodeFile(f('bin/run.sh')), true);
  assert.equal(touchesCodeFile(f('README.md')), false);
  assert.equal(touchesCodeFile(f('data.json')), false);
  assert.equal(touchesCodeFile(f('githooks/pre-commit')), false, 'extensionless is not code by extension');
  assert.equal(touchesCodeFile(f('pkg/package.json')), false);
  assert.equal(touchesCodeFile('no diff headers at all'), false);
  assert.equal(
    touchesCodeFile(f('doc.md') + f('src/x.ts')),
    true,
    'one code file among docs is applicable',
  );
});
