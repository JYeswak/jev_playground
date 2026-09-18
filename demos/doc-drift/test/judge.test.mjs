import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { judgePair } from '../src/judge.mjs';

const policy = JSON.parse(readFileSync(new URL('../policy.json', import.meta.url), 'utf8'));
const canned = (p) => ({ async ask() { return { answers: { accurate: { noul: p } } }; } });
const failing = () => ({ async ask() { throw new Error('canned malformed'); } });
const pair = { doc: 'X does Y.', code: 'function X() { return Y(); }', anchor: 'src/x#X' };

describe('verdicts reachable', () => {
  it('accurate on high support', async () => {
    assert.equal((await judgePair({ ...pair, policy, asker: canned(0.9) })).verdict, 'accurate');
  });
  it('drifted on low support', async () => {
    assert.equal((await judgePair({ ...pair, policy, asker: canned(0.2) })).verdict, 'drifted');
  });
  it('uncertain in the open band (not accurate, not drifted)', async () => {
    assert.equal((await judgePair({ ...pair, policy, asker: canned(0.55) })).verdict, 'uncertain');
  });
});

describe('fail-safe directions', () => {
  it('malformed answer withholds (never coerces)', async () => {
    const v = await judgePair({ ...pair, policy, asker: failing() });
    assert.equal(v.verdict, 'uncertain');
    assert.equal(v.reason_code, 'asker-malformed');
  });
  it('unpaired input is uncertain without calling Jev', async () => {
    let calls = 0;
    const a = { async ask() { calls += 1; return { answers: { accurate: { noul: 1 } } }; } };
    const v = await judgePair({ doc: 'vague words', code: null, anchor: 'none', policy, asker: a });
    assert.equal(v.verdict, 'uncertain');
    assert.equal(v.reason_code, 'unpaired');
    assert.equal(calls, 0);
  });
  it('boundaries: 0.75 accurate, 0.40 uncertain, below drifted', async () => {
    assert.equal((await judgePair({ ...pair, policy, asker: canned(0.75) })).verdict, 'accurate');
    assert.equal((await judgePair({ ...pair, policy, asker: canned(0.4) })).verdict, 'uncertain');
    assert.equal((await judgePair({ ...pair, policy, asker: canned(0.39) })).verdict, 'drifted');
  });
});
