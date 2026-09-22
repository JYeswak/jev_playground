/**
 * liveAsker wiring test: injected fake fetch only, no key, no network.
 * Proves each passage goes through askJevScore (typed guards) and the
 * expected-level reduction is unchanged. A fetch throw degrades to
 * {ok:false}, never throws.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { liveAsker } from '../src/live.ts';

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
  const prev = process.env.TYPESAFE_API_KEY;
  process.env.TYPESAFE_API_KEY = 'test-key';
  try {
    const r = await liveAsker({ query: 'q', passages: { p01: 'aaa', p02: 'bbb' } }, fakeFetch);
    assert.equal(r.ok, true);
    assert.deepEqual(Object.keys(r.scores).sort(), ['p01', 'p02']);
    for (const v of Object.values(r.scores)) assert.ok(v > 0.5 && v <= 1, `expected high level, got ${v}`);
  } finally {
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
  }
});

test('liveAsker degrades to ok:false when the transport throws', async () => {
  const prev = process.env.TYPESAFE_API_KEY;
  process.env.TYPESAFE_API_KEY = 'test-key';
  try {
    const r = await liveAsker({ query: 'q', passages: { p01: 'aaa' } }, async () => { throw new Error('down'); });
    assert.equal(r.ok, false);
  } finally {
    if (prev === undefined) delete process.env.TYPESAFE_API_KEY;
    else process.env.TYPESAFE_API_KEY = prev;
  }
});
