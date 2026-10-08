import test from 'node:test';
import assert from 'node:assert/strict';
import { makeReadDedupHandler, default as jevReadDedupHook } from './jev-read-dedup.ts';

function parseLine(line) {
  try {
    return JSON.parse(line);
  } catch {
    assert.fail('shadow record must be valid JSON');
  }
}

function driver(opts = {}) {
  const rows = [];
  const handler = makeReadDedupHandler({
    append: async (_path, line) => rows.push(parseLine(line)),
    now: () => '2026-10-02T00:00:00.000Z',
    ...opts,
  });
  let n = 0;
  const call = (toolName, extra = {}) => handler.onCall({ toolName, toolCallId: `c${++n}`, arguments: extra });
  const result = (toolName, text, id) => handler.onResult({ toolName, toolCallId: id, content: [{ type: 'text', text }] });
  return { rows, handler, call, result };
}

test('first read passes silent with no row', async () => {
  const { rows, call, result } = driver();
  await call('read', { path: 'a.txt' });
  const out = await result('read', 'file content v1', 'c1');
  assert.equal(out, undefined);
  assert.equal(rows.length, 0);
});

test('identical second read logs would-skip and keeps content', async () => {
  const { rows, call, result } = driver();
  await call('read', { path: 'a.txt' });
  await result('read', 'same bytes', 'c1');
  await call('read', { path: 'a.txt' });
  const out = await result('read', 'same bytes', 'c2');
  assert.equal(out, undefined);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'would-skip');
  assert.equal(rows[0].repeats, 1);
  assert.equal(rows[0].path, 'a.txt');
  assert.match(rows[0].outputSha256, /^[0-9a-f]{64}$/);
  assert.doesNotMatch(JSON.stringify(rows), /same bytes/);
});

test('edited path logs repeat-kept, never would-skip', async () => {
  const { rows, call, result } = driver();
  await call('read', { path: 'a.txt' });
  await result('read', 'same bytes', 'c1');
  await call('edit', { path: 'a.txt' });
  await call('read', { path: 'a.txt' });
  await result('read', 'same bytes', 'c3');
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'repeat-kept');
  assert.equal(rows[0].reason, 'edited-since-first-read');
});

test('beyond turn bound logs repeat-kept', async () => {
  const { rows, call, result } = driver({ turnBoundCalls: 1 });
  await call('read', { path: 'a.txt' });
  await result('read', 'same bytes', 'c1');
  await call('bash', { command: 'echo hi' });
  await call('bash', { command: 'echo ho' });
  await call('read', { path: 'a.txt' });
  await result('read', 'same bytes', 'c4');
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'repeat-kept');
  assert.equal(rows[0].reason, 'beyond-turn-bound');
});

test('changed content replaces without a row', async () => {
  const { rows, call, result } = driver();
  await call('read', { path: 'a.txt' });
  await result('read', 'v1', 'c1');
  await call('read', { path: 'a.txt' });
  const out = await result('read', 'v2', 'c2');
  assert.equal(out, undefined);
  assert.equal(rows.length, 0);
});

test('non-read tools and errors are ignored', async () => {
  const { rows, call, result } = driver();
  await call('bash', { command: 'x' });
  await result('bash', 'x', 'c1');
  await call('read', { path: 'a.txt' });
  await result('read', 'x', 'c2');
  await call('bash', { command: 'x' });
  await result('bash', 'x', 'c3');
  await result('read', 'y', 'cX');
  assert.equal(rows.length, 0);
});

test('map cap evicts oldest', async () => {
  const { rows, call, result } = driver({ maxEntries: 2 });
  let n = 10;
  for (const t of ['a', 'b', 'c']) {
    await call('read', { path: `${t}.txt` });
    await result('read', t, `c${++n}`);
  }
  await call('read', { path: 'a.txt' });
  await result('read', 'a', `c${++n}`);
  assert.equal(rows.length, 0);
});

test('dedup subscribes to tool_call and tool_result', () => {
  const subscribed = [];
  jevReadDedupHook({ on: (event) => subscribed.push(event) }, { append: async () => {} });
  assert.deepEqual(subscribed, ['tool_call', 'tool_result']);
});
