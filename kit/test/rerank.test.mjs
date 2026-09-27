import test from 'node:test';
import assert from 'node:assert/strict';
import { rerankTop1 } from '../src/rerank.ts';

const candidates = [
  { id: 'c0', text: 'first passage' },
  { id: 'c1', text: 'selected passage' },
  { id: 'none', text: 'abstain passage' },
];

function answer(choice) {
  return async () => ({
    ok: true,
    choice,
    confidence: 0.9,
    probabilities: { c0: 0.05, c1: 0.9, none: 0.05 },
    latencyMs: 1,
    model: 'jev-1.13.0',
  });
}

test('rerank puts the selected candidate first and preserves input order after it', async () => {
  const result = await rerankTop1({ query: 'q', candidates, ask: answer('c1') });
  assert.deepEqual(result.orderedCandidates.map((candidate) => candidate.id), ['c1', 'c0', 'none']);
});

test('rerank refuses more than twenty candidates before asking', async () => {
  let calls = 0;
  const tooMany = Array.from({ length: 21 }, (_, i) => ({ id: `c${i}`, text: 'x' }));
  await assert.rejects(
    rerankTop1({ query: 'q', candidates: tooMany, ask: async () => { calls += 1; return answer('c0')(); } }),
    /at most 20/,
  );
  assert.equal(calls, 0);
});

test('rerank refuses an unoffered answer', async () => {
  await assert.rejects(rerankTop1({ query: 'q', candidates, ask: answer('missing') }), /unoffered candidate/);
});

test('rerank refuses an OVER state before asking', async () => {
  let calls = 0;
  const over = candidates.map((candidate) => ({ ...candidate, text: 'x'.repeat(100_000) }));
  await assert.rejects(
    rerankTop1({ query: 'q', candidates: over, ask: async () => { calls += 1; return answer('c0')(); } }),
    /OVER/,
  );
  assert.equal(calls, 0);
});
