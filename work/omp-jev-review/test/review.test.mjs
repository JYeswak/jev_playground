import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevReview, { setDiffRunner, isThinDiff, touchesCodeFile, isVendoredPath, reviewableDiff, BOUNDARY_COMMENT } from '../src/index.ts';
import { mkdir, unlink, writeFile } from 'node:fs/promises';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { requireSdkInstalled } from '../../sdk/require-installed.mjs';
import jevReviewExtension from '../../../.omp/extensions/jev-review.ts';
import { keyProviderInstalled, setKeyProvider } from '../../../kit/src/client.ts';

requireSdkInstalled();

const sessionContext = (sessionId = 'synthetic-session') => ({
  sessionManager: { getSessionId: () => sessionId },
});

function host() {
  const rows = [];
  const handlers = {};
  return {
    rows,
    fire: (event, context = sessionContext()) => handlers.tool_call(event, context),
    fireResult: (event, context = sessionContext()) => handlers.tool_result(event, context),
    pi: {
      on: (e, cb) => { handlers[e] = cb; },
      appendEntry: async (type, data) => { rows.push({ type, data }); },
    },
  };
}
const decisions = (h) => h.rows.filter((r) => r.type.endsWith('decision.v1'));
const diffCall = (command) => ({ toolName: 'bash', toolCallId: 'tc-1', input: { command } });

// Captured OMP tool call: P15 session 01a0f3a9-d58e-748c-83af-3a2661b433ca, call-p15-1.
const P15_RECORDED_SESSION = '01a0f3a9-d58e-748c-83af-3a2661b433ca';
const P15_RECORDED_CALL = {
  toolName: 'bash',
  toolCallId: 'call-p15-1',
  input: { command: 'git diff --cached -- src/eligible.ts' },
};

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
const syntheticApproval = () => ({ provider: true, localDiffExecution: true });

test('project extension loads without installing a global key provider before admission', async () => {
  setKeyProvider(undefined);
  try {
    const h = host();
    jevReviewExtension({ ...h.pi, zod: { object: () => ({}) }, registerTool: () => {} });
    assert.equal(keyProviderInstalled(), false);
    await h.fire(diffCall('git diff --cached'));
    assert.equal(decisions(h)[0].data.reason, 'permission-denied');
  } finally {
    setKeyProvider(undefined);
  }
});

test('unapproved automatic diff is recorded locally without re-running git or calling provider', async () => {
  let gitRuns = 0;
  let providerCalls = 0;
  setDiffRunner(async () => { gitRuns += 1; return SUBSTANTIAL; });
  const realFetch = globalThis.fetch;
  globalThis.fetch = async () => { providerCalls += 1; throw new Error('unapproved egress'); };
  try {
    const h = host();
    ompJevReview(h.pi);
    await h.fire(diffCall('git diff --cached'));
    assert.equal(gitRuns, 0);
    assert.equal(providerCalls, 0);
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_not_applicable');
    assert.equal(row.data.reason, 'permission-denied');
    assert.match(row.data.commandSha, /^[0-9a-f]{64}$/);
    assert.equal(row.data.command, undefined);
    assert.doesNotMatch(JSON.stringify(h.rows), /git diff --cached/);
  } finally {
    setDiffRunner(null);
    globalThis.fetch = realFetch;
  }
});

test('provider approval alone cannot spawn a second local git command', async () => {
  const realFetch = globalThis.fetch;
  let gitRuns = 0;
  let providerCalls = 0;
  setDiffRunner(async () => { gitRuns += 1; return SUBSTANTIAL; });
  globalThis.fetch = async () => { providerCalls += 1; throw new Error('unexpected provider request'); };
  try {
    const h = host();
    ompJevReview(h.pi, () => ({ provider: true, localDiffExecution: false }));
    await h.fire(diffCall('git diff --cached'));
    assert.equal(gitRuns, 0);
    assert.equal(providerCalls, 0);
    assert.equal(decisions(h)[0].data.reason, 'local-diff-denied');
  } finally {
    setDiffRunner(null);
    globalThis.fetch = realFetch;
  }
});

test('approved diff execution refuses external helpers, no-index and output files before spawning', async () => {
  let gitRuns = 0;
  setDiffRunner(async () => { gitRuns += 1; return SUBSTANTIAL; });
  try {
    const h = host();
    ompJevReview(h.pi, () => ({ provider: true, localDiffExecution: true }));
    for (const command of [
      'git diff --ext-diff',
      'git show --textconv HEAD',
      'git diff --no-index /etc/hosts ./file',
      'git diff --output=outside.patch',
    ]) {
      await h.fire(diffCall(command));
    }
    assert.equal(gitRuns, 0);
    assert.equal(decisions(h).length, 4);
    assert.equal(decisions(h).every((row) => row.data.reason === 'not-a-plain-diff-command'), true);
  } finally {
    setDiffRunner(null);
  }
});

test('locally approved ordinary diff explicitly disables external helpers', async () => {
  let argv;
  setDiffRunner(async (args) => { argv = args; return ''; });
  try {
    const h = host();
    ompJevReview(h.pi, () => ({ provider: true, localDiffExecution: true }));
    await h.fire(diffCall('git diff --cached'));
    assert.deepEqual(argv, ['git', 'diff', '--no-ext-diff', '--no-textconv', '--cached']);
    assert.equal(decisions(h)[0].data.reason, 'empty-diff');
  } finally {
    setDiffRunner(null);
  }
});

test('ignores every tool call that is not a git diff or show', async () => {
  const h = host();
  ompJevReview(h.pi, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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
  ompJevReview({ on: h.pi.on, appendEntry: async () => { throw new Error('log sink down'); } }, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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

test('an empty diff records applicable:false and does not call Jev', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  globalThis.fetch = async () => { called += 1; return { ok: true, status: 200, text: async () => '{}' }; };
  try {
    stubDiff('   \n');
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_not_applicable');
    assert.equal(row.data.applicable, false);
    assert.equal(row.data.reason, 'empty-diff');
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

// Bead jev-k9z.2 planted negative: a 10k-line vendored diff is not ours to review.
const VENDORED_10K = 'diff --git a/node_modules/lib/index.ts b/node_modules/lib/index.ts\n@@ -1,1 +1,10000 @@\n' +
  Array.from({ length: 10000 }, (_, i) => `+vendored line ${i}`).join('\n') + '\n';

test('a 10k-line vendored diff records applicable:false and never calls Jev', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  globalThis.fetch = async () => { called += 1; throw new Error('must not be called'); };
  try {
    stubDiff(VENDORED_10K + 'diff --git a/package-lock.json b/package-lock.json\n@@ -1 +1 @@\n+{}\n');
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_not_applicable');
    assert.equal(row.data.reason, 'vendored-diff');
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('vendored sections are cut before scoring; our own code in the same diff still scores', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  const sent = [];
  const mk = (answers) => ({
    ok: true, status: 200, headers: { get: () => 'application/json' },
    text: async () => JSON.stringify({ answers }), clone: () => mk(answers),
  });
  globalThis.fetch = async (_url, init) => { sent.push(JSON.parse(init.body)); return mk({ behaviour: { noul: 0.3 }, boundary: { noul: 0.2 } }); };
  try {
    stubDiff(VENDORED_10K + SUBSTANTIAL);
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire(diffCall('git diff'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_scored');
    assert.equal(row.data.vendoredFilesDropped, 1);
    assert.equal(sent.length, 1);
    assert.equal(sent[0].state.diff.includes('vendored line'), false, 'Jev never sees vendored text');
    assert.equal(sent[0].state.diff.includes('added line 0'), true);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('isVendoredPath: directory segments and lockfiles, not look-alike names', () => {
  assert.equal(isVendoredPath('node_modules/a/b.ts'), true);
  assert.equal(isVendoredPath('web/vendor/x.py'), true);
  assert.equal(isVendoredPath('uv.lock'), true);
  assert.equal(isVendoredPath('sub/package-lock.json'), true);
  assert.equal(isVendoredPath('src/vendor.ts'), false, 'a file named vendor is not a vendor dir');
  assert.equal(isVendoredPath('src/distance.ts'), false);
  assert.equal(reviewableDiff('commit abc\n\nmsg\n' + VENDORED_10K).diff.startsWith('commit abc'), true, 'the git show header is kept');
});

// The advisory line: one scored diff, the git output of that same call, nothing else.
async function scoredWithBoundary(boundary, id = 'tc-1', sessionId = 'synthetic-session', command = 'git show HEAD') {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  globalThis.fetch = answersFetch({ behaviour: { noul: 0.4 }, boundary: { noul: boundary } });
  try {
    stubDiff(SUBSTANTIAL);
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire({ toolName: 'bash', toolCallId: id, input: { command } }, sessionContext(sessionId));
    return h;
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
}
const gitOutput = [{ type: 'text', text: 'commit abc\n' }];

test('a boundary score at the threshold appends one advisory line to that call only', async () => {
  const h = await scoredWithBoundary(BOUNDARY_COMMENT);
  assert.equal(decisions(h)[0].data.comment, true);
  const out = await h.fireResult({ toolName: 'bash', toolCallId: 'tc-1', content: gitOutput });
  assert.equal(out.content.length, 2);
  assert.deepEqual(out.content[0], gitOutput[0], 'the git output is kept verbatim');
  assert.match(out.content[1].text, /jev-review advisory, no merge authority\] boundary 0\.90/);
  assert.equal(await h.fireResult({ toolName: 'bash', toolCallId: 'tc-1', content: gitOutput }), undefined, 'fires once');
});

test('below the threshold the result is silent', async () => {
  const h = await scoredWithBoundary(BOUNDARY_COMMENT - 0.01);
  assert.equal(decisions(h)[0].data.comment, false);
  assert.equal(await h.fireResult({ toolName: 'bash', toolCallId: 'tc-1', content: gitOutput }), undefined);
});

test('another call, or a failed git call, gets no advisory line', async () => {
  const h = await scoredWithBoundary(0.97);
  assert.equal(await h.fireResult({ toolName: 'bash', toolCallId: 'tc-other', content: gitOutput }), undefined);
  assert.equal(await h.fireResult({ toolName: 'bash', toolCallId: 'tc-1', isError: true, content: gitOutput }), undefined);
});

test('a compound or piped command is not executed, not scored, and recorded not-applicable rather than as an error', async () => {
  const previous = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  process.env.TYPESAFE_API_KEY = 'test-key';
  let called = 0;
  let ran = 0;
  globalThis.fetch = async () => { called += 1; return { ok: true, status: 200, text: async () => '{}' }; };
  try {
    setDiffRunner(async () => { ran += 1; return 'should not run'; });
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire(diffCall('git diff; echo pwned'));
    await h.fire(diffCall('git add -- a.py && git diff --cached --check'));
    await h.fire(diffCall('git show abc:work/x.py | python3 -'));
    const rows = decisions(h);
    assert.equal(rows.length, 3);
    for (const row of rows) {
      assert.equal(row.data.kind, 'review_not_applicable');
      assert.equal(row.data.reason, 'not-a-plain-diff-command');
    }
    assert.equal(ran, 0);
    assert.equal(called, 0);
  } finally {
    globalThis.fetch = realFetch;
    if (previous === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previous;
  }
});

test('a plain git diff that fails to run is still review_error, never not-applicable', async () => {
  setDiffRunner(async () => { throw new Error('fatal: bad revision'); });
  try {
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire(diffCall('git show deadbeef'));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_error');
    assert.equal(row.data.failure, 'diff-exec');
  } finally {
    setDiffRunner(null);
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
    ompJevReview(h.pi, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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
    ompJevReview(h.pi, syntheticApproval);
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

test('approved recorded OMP event score is bound to its source session and toolCallId', async () => {
  const previousKey = process.env.TYPESAFE_API_KEY;
  const realFetch = globalThis.fetch;
  delete process.env.TYPESAFE_API_KEY;
  let credentialCalls = 0;
  globalThis.fetch = answersFetch({ behaviour: { noul: 0.82 }, boundary: { noul: 0.18 } });
  stubDiff(SUBSTANTIAL);
  setKeyProvider(async () => { credentialCalls++; return 'synthetic-p15-key'; });
  try {
    const h = host();
    ompJevReview(h.pi, syntheticApproval);
    await h.fire(P15_RECORDED_CALL, sessionContext(P15_RECORDED_SESSION));
    const [row] = decisions(h);
    assert.equal(row.data.kind, 'review_scored');
    assert.equal(row.data.toolCallId, P15_RECORDED_CALL.toolCallId);
    assert.equal(row.data.sessionId, P15_RECORDED_SESSION);
    assert.equal(credentialCalls, 1);
  } finally {
    globalThis.fetch = realFetch;
    if (previousKey === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previousKey;
    setDiffRunner(null);
    setKeyProvider(undefined);
  }
});

test('unknown OMP session refuses before authorization, diff execution, or Jev', async () => {
  const previousKey = process.env.TYPESAFE_API_KEY;
  const previousFetch = globalThis.fetch;
  delete process.env.TYPESAFE_API_KEY;
  const calls = { authorization: 0, diff: 0, provider: 0, credential: 0 };
  const answer = answersFetch({ behaviour: { noul: 0.82 }, boundary: { noul: 0.18 } });
  globalThis.fetch = async (...args) => { calls.provider++; return answer(...args); };
  setDiffRunner(async () => { calls.diff++; return SUBSTANTIAL; });
  setKeyProvider(async () => { calls.credential++; return 'synthetic-p15-key'; });
  try {
    const h = host();
    ompJevReview(h.pi, () => {
      calls.authorization++;
      return { provider: true, localDiffExecution: true };
    });
    await h.fire(P15_RECORDED_CALL, sessionContext('unknown'));
    const [row] = decisions(h);
    assert.equal(row.data.reason, 'missing-session-id');
    assert.equal(row.data.sessionId, null);
    assert.deepEqual(calls, { authorization: 0, diff: 0, provider: 0, credential: 0 });
    assert.doesNotMatch(JSON.stringify(h.rows), /added line/);
  } finally {
    if (previousKey === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = previousKey;
    globalThis.fetch = previousFetch;
    setDiffRunner(null);
    setKeyProvider(undefined);
  }
});

test('tool-result advisory is scoped to both recorded session and toolCallId', async () => {
  const h = await scoredWithBoundary(
    BOUNDARY_COMMENT,
    P15_RECORDED_CALL.toolCallId,
    P15_RECORDED_SESSION,
    P15_RECORDED_CALL.input.command,
  );
  const otherSession = '01a0f39e-fcd4-7703-9b9a-e1255f733f6d';
  assert.equal(await h.fireResult({ toolName: 'bash', toolCallId: P15_RECORDED_CALL.toolCallId, content: gitOutput }, sessionContext(otherSession)), undefined);
  const original = await h.fireResult({ toolName: 'bash', toolCallId: P15_RECORDED_CALL.toolCallId, content: gitOutput }, sessionContext(P15_RECORDED_SESSION));
  assert.equal(original.content.length, 2);
  assert.deepEqual(original.content[0], gitOutput[0]);
});
test('presence-OFF skips review authorization, diff execution, and Jev', async () => {
  const stateDir = join(homedir(), '.local', 'state', 'jev');
  const marker = join(stateDir, 'jev-lab-review.off');
  await mkdir(stateDir, { recursive: true });
  await writeFile(marker, 'operator off');
  const previousFetch = globalThis.fetch;
  const calls = { authorization: 0, diff: 0, provider: 0 };
  globalThis.fetch = async () => { calls.provider += 1; throw new Error('unexpected Jev request'); };
  setDiffRunner(async () => { calls.diff += 1; return SUBSTANTIAL; });
  try {
    const h = host();
    ompJevReview(h.pi, () => {
      calls.authorization += 1;
      return { provider: true, localDiffExecution: true };
    });
    assert.equal(await h.fire(diffCall('git diff')), undefined);
    assert.deepEqual(calls, { authorization: 0, diff: 0, provider: 0 });
    assert.equal(decisions(h).length, 0);
  } finally {
    globalThis.fetch = previousFetch;
    setDiffRunner(null);
    await unlink(marker);
  }
});
