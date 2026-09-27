import test from 'node:test';
import assert from 'node:assert/strict';
import { makeGateShadowHandler } from './jev-gate-shadow.ts';

const fakeScores = {
  exfiltration: 0.1,
  destructive: 0.2,
  privilege: 0.1,
  irreversible_publish: 0.05,
  secret_staging: 0.1,
};

function asker(scores = fakeScores) {
  let calls = 0;
  const ask = async () => {
    calls += 1;
    const answers = Object.fromEntries(Object.entries(scores).map(([key, noul]) => [key, { type: 'noul', noul }]));
    return { ok: true, answers, resolvedModel: 'fake', latencyMs: 7, usage: { input_tokens: 12, output_tokens: 8 } };
  };
  return { ask, calls: () => calls };
}

function event(command) {
  return { toolName: 'bash', input: { command }, details: { existingFlag: false } };
}

function parseRow(line) {
  try { return JSON.parse(line); } catch { throw new Error('invalid row'); }
}

async function waitFor(condition) {
  for (let i = 0; i < 100; i += 1) {
    if (condition()) return;
    await new Promise((resolve) => setImmediate(resolve));
  }
  throw new Error('condition timeout');
}

test('healthy bash command is shadow-scored, hash-only, and never blocked', async () => {
  const rows = [];
  const fake = asker();
  const handler = makeGateShadowHandler({ ask: fake.ask, append: async (_path, line) => rows.push(parseRow(line)), cap: 10, session: 's1', now: () => '2026-09-27T00:00:00.000Z' });
  assert.equal(await handler(event('printf hello')), undefined);
  await waitFor(() => rows.length === 1);
  assert.equal(fake.calls(), 1);
  assert.equal(rows[0].status, 'scored');
  assert.equal(rows[0].cmdSha.length, 64);
  assert.equal(rows[0].command, undefined);
  assert.equal(rows[0].maxScore, 0.2);
  assert.equal(rows[0].jevFlag, false);
});

test('non-bash tool is ignored without an asker call', async () => {
  const fake = asker();
  const handler = makeGateShadowHandler({ ask: fake.ask, append: async () => { throw new Error('must not append'); } });
  assert.equal(await handler({ toolName: 'read', input: { path: 'x' } }), undefined);
  assert.equal(fake.calls(), 0);
});

test('daily cap writes a cap row and does not call Jev again', async () => {
  const rows = [];
  const fake = asker();
  const handler = makeGateShadowHandler({ ask: fake.ask, append: async (_path, line) => rows.push(parseRow(line)), cap: 1, session: 's1', now: () => '2026-09-27T00:00:00.000Z' });
  await handler(event('printf one')); await waitFor(() => rows.length === 1);
  await handler(event('printf two')); await waitFor(() => rows.length === 2);
  assert.equal(fake.calls(), 1);
  assert.deepEqual(rows.map((row) => row.status), ['scored', 'cap']);
});

test('HTTP 402 pauses subsequent calls and remains fail-open', async () => {
  const rows = [];
  let calls = 0;
  const handler = makeGateShadowHandler({
    ask: async () => { calls += 1; return { ok: false, reason: 'http', error: 'systemOne HTTP 402: insufficient credits', latencyMs: 3 }; },
    append: async (_path, line) => rows.push(parseRow(line)),
    cap: 10,
    session: 's1',
    now: () => '2026-09-27T00:00:00.000Z',
  });
  assert.equal(await handler(event('printf one')), undefined); await waitFor(() => rows.length === 1);
  assert.equal(await handler(event('printf two')), undefined); await waitFor(() => rows.length === 2);
  assert.equal(calls, 1);
  assert.deepEqual(rows.map((row) => row.status), ['paused', 'paused']);
});

test('asker throw is logged as error and never escapes the hook', async () => {
  const rows = [];
  const handler = makeGateShadowHandler({ ask: async () => { throw new Error('transport'); }, append: async (_path, line) => rows.push(parseRow(line)) });
  assert.equal(await handler(event('printf hello')), undefined); await waitFor(() => rows.length === 1);
  assert.equal(rows[0].status, 'error');
});
