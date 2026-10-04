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

test('first read passes silent with no row', async () => {
  const rows = [];
  const handler = makeReadDedupHandler({
    append: async (_path, line) => rows.push(parseLine(line)),
    now: () => '2026-10-02T00:00:00.000Z',
  });
  const out = await handler({ toolName: 'read', content: [{ type: 'text', text: 'file content v1' }] });
  assert.equal(out, undefined);
  assert.equal(rows.length, 0);
});

test('identical second read logs would-skip and keeps content', async () => {
  const rows = [];
  const handler = makeReadDedupHandler({
    append: async (_path, line) => rows.push(parseLine(line)),
    now: () => '2026-10-02T00:00:00.000Z',
  });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'same bytes' }] });
  const out = await handler({ toolName: 'read', content: [{ type: 'text', text: 'same bytes' }] });
  assert.equal(out, undefined);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'would-skip');
  assert.equal(rows[0].repeats, 1);
  assert.match(rows[0].outputSha256, /^[0-9a-f]{64}$/);
  assert.doesNotMatch(JSON.stringify(rows), /same bytes/);
});

test('changed content replaces without a row', async () => {
  const rows = [];
  const handler = makeReadDedupHandler({
    append: async (_path, line) => rows.push(parseLine(line)),
  });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'v1' }] });
  const out = await handler({ toolName: 'read', content: [{ type: 'text', text: 'v2' }] });
  assert.equal(out, undefined);
  assert.equal(rows.length, 0);
});

test('non-read tools and errors are ignored', async () => {
  const rows = [];
  let logged = 0;
  const handler = makeReadDedupHandler({
    append: async () => { logged++; },
  });
  await handler({ toolName: 'bash', content: [{ type: 'text', text: 'x' }] });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'x' }] });
  await handler({ toolName: 'bash', content: [{ type: 'text', text: 'x' }] });
  await handler({ toolName: 'read', isError: true, content: [{ type: 'text', text: 'y' }] });
  await handler({ toolName: 'read', content: [{ type: 'text', text: '' }] });
  assert.equal(logged, 0);
  assert.equal(rows.length, 0);
});

test('map cap evicts oldest', async () => {
  const rows = [];
  const handler = makeReadDedupHandler({
    maxEntries: 2,
    append: async (_path, line) => rows.push(parseLine(line)),
  });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'a' }] });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'b' }] });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'c' }] });
  await handler({ toolName: 'read', content: [{ type: 'text', text: 'a' }] });
  assert.equal(rows.length, 0);
});

test('dedup subscribes to tool_result only', () => {
  const subscribed = [];
  jevReadDedupHook({ on: (event) => subscribed.push(event) }, { append: async () => {} });
  assert.deepEqual(subscribed, ['tool_result']);
});
