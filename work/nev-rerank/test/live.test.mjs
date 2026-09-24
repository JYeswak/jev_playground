/**
 * liveAsker wiring test: injected fake fetch only, no key, no network.
 * Proves each passage goes through askJevScore (typed guards) and the
 * expected-level reduction is unchanged. A fetch throw degrades to
 * {ok:false}, never throws. calledModel on a failure is true only when a
 * request reached the transport (jev-t7oq).
 */
import test, { mock } from 'node:test';
import assert from 'node:assert/strict';
import { liveAsker, LIVE_TIMEOUT_MS } from '../src/live.ts';
import { resetBillingHold } from '../../jev-client/src/index.ts';
import { requireSdkInstalled } from '../../sdk/require-installed.mjs';

requireSdkInstalled();

const ONE = { query: 'q', passages: { p01: 'aaa' } };

// Saves and restores the env var around fn. The comparisons below are with `undefined`
// (was the variable set), not with a secret; the only key used here is the fake 'test-key'.
async function withKey(key, fn) {
  const prev = process.env.TYPESAFE_API_KEY;
  if (key === undefined) delete process.env.TYPESAFE_API_KEY; // ubs:ignore — presence check, not a secret comparison
  else process.env.TYPESAFE_API_KEY = key;
  try {
    return await fn();
  } finally {
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY; // ubs:ignore — presence check, not a secret comparison
    else process.env.TYPESAFE_API_KEY = prev;
  }
}

const fakeHeaders = () => ({ get: (n) => String(n).toLowerCase() === 'content-type' ? 'application/json' : null });
const scoreAnswer = (top) => ({
  answers: { score: { type: 'score', score: top,
    confidence: 0.9,
    legend: { 0: 'off', 1: 'related', 2: 'partly', 3: 'fully' },
    probabilities: { 0: 0.05, 1: 0.05, 2: 0.1, 3: 0.8 } } },
});
const fakeFetch = async () => ({
  ok: true, status: 200, headers: fakeHeaders(), body: null,
  clone() { return this; },
  text: async () => JSON.stringify(scoreAnswer(3)),
});

test('liveAsker scores every passage through askJevScore, no network', async () => {
  const r = await withKey('test-key', () => liveAsker({ query: 'q', passages: { p01: 'aaa', p02: 'bbb' } }, fakeFetch));
  assert.equal(r.ok, true);
  assert.deepEqual(Object.keys(r.scores).sort(), ['p01', 'p02']);
  for (const v of Object.values(r.scores)) assert.ok(v > 0.5 && v <= 1, `expected high level, got ${v}`);
});

test('liveAsker degrades to ok:false when the transport throws; the request was sent', async () => {
  const r = await withKey('test-key', () => liveAsker(ONE, async () => { throw new Error('down'); }));
  assert.equal(r.ok, false);
  assert.equal(r.reason, 'transport');
  assert.equal(r.calledModel, true);
});

test('keyless: askJevScore stops before any request, so calledModel is false', async () => {
  let calls = 0;
  const r = await withKey(undefined, () => liveAsker({ query: 'q', passages: { p01: 'aaa', p02: 'bbb' } }, async () => {
    calls += 1;
    throw new Error('the transport must not be reached without a key');
  }));
  assert.equal(r.ok, false);
  assert.equal(r.reason, 'unconfigured');
  assert.equal(r.calledModel, false);
  assert.equal(calls, 0);
});

test('HTTP 402 is a sent request (calledModel true); the billing hold after it sends nothing (false)', async () => {
  let calls = 0;
  const refuse = async () => {
    calls += 1;
    return new Response(JSON.stringify({ error: 'insufficient credits' }), { status: 402, headers: { 'content-type': 'application/json' } });
  };
  try {
    const refused = await withKey('test-key', () => liveAsker(ONE, refuse));
    assert.equal(refused.ok, false);
    assert.equal(refused.reason, 'http');
    assert.equal(refused.calledModel, true);
    assert.equal(calls, 1);
    const held = await withKey('test-key', () => liveAsker(ONE, refuse));
    assert.equal(held.ok, false);
    assert.equal(held.reason, 'billing-hold');
    assert.equal(held.calledModel, false);
    assert.equal(calls, 1);
  } finally {
    resetBillingHold();
  }
});

test('a request that times out is a sent request: calledModel true', async () => {
  mock.timers.enable({ apis: ['setTimeout'] });
  let arrived;
  const reached = new Promise((resolve) => { arrived = resolve; });
  const hang = (_url, init) => new Promise((_resolve, reject) => {
    init.signal.addEventListener('abort', () => reject(init.signal.reason), { once: true }); // ubs:ignore — once:true removes it when the abort fires
    arrived();
  });
  try {
    const pending = withKey('test-key', () => liveAsker(ONE, hang));
    await reached;
    mock.timers.tick(LIVE_TIMEOUT_MS);
    const r = await pending;
    assert.equal(r.ok, false);
    assert.equal(r.reason, 'transport');
    assert.equal(r.calledModel, true);
  } finally {
    mock.timers.reset();
  }
});
