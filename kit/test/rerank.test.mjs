import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { rerankTop1 } from '../src/rerank.ts';

const fiqa = JSON.parse(readFileSync(new URL('../../work/rerank-scifact/candidates-fiqa-fits.jsonl', import.meta.url), 'utf8').split('\n', 1)[0]);
const choice = JSON.parse(readFileSync(new URL('./fixtures/rerank-fiqa-answer.json', import.meta.url), 'utf8'))[0].answers.choice;
const recordedCandidates = fiqa.cands.map(([id]) => ({ id, text: id }));

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

test('rerank accepts projected two and recorded twenty FiQA candidate IDs with a Choice answer', async () => {
  assert.equal(fiqa.qid, '10034');
  assert.equal(recordedCandidates.length, 20);
  assert.equal(choice.choice, '181942');
  const two = [recordedCandidates[0], recordedCandidates.find((candidate) => candidate.id === choice.choice)];
  for (const input of [two, recordedCandidates]) {
    let calls = 0;
    const result = await rerankTop1({
      query: fiqa.qid,
      candidates: input,
      ask: async (options) => {
        calls++;
        assert.deepEqual(new Set(Object.keys(options.classes)), new Set(input.map(({ id }) => id)));
        assert.deepEqual(options.state.candidates.map(({ id }) => id), input.map(({ id }) => id));
        return { ok: true, ...choice, latencyMs: 1, model: 'fake' };
      },
    });
    assert.equal(calls, 1);
    assert.deepEqual(result.orderedCandidates.map(({ id }) => id), [choice.choice, ...input.map(({ id }) => id).filter((id) => id !== choice.choice)]);
  }
});

test('rerank sends passage text to Choice and returns the selected passage verbatim', async () => {
  const passages = [
    { id: 'doc-a', text: 'A bond matures in 2034.' },
    { id: 'doc-b', text: '  Stocks fell 2%.\nSecond line stays.  ' },
  ];
  const result = await rerankTop1({
    query: 'Which passage discusses stocks?',
    candidates: passages,
    ask: async (options) => {
      assert.deepEqual(options.state.candidates, passages);
      return {
        ok: true,
        choice: 'doc-b',
        confidence: 0.9,
        probabilities: { 'doc-a': 0.1, 'doc-b': 0.9 },
        latencyMs: 1,
        model: 'fake',
      };
    },
  });
  assert.strictEqual(result.orderedCandidates[0], passages[1]);
  assert.equal(result.orderedCandidates[0].text, passages[1].text);
});

test('rerank refuses one captured candidate before calling asker', async () => {
  let calls = 0;
  await assert.rejects(
    rerankTop1({ query: fiqa.qid, candidates: recordedCandidates.slice(0, 1), ask: async () => { calls++; return { ok: true, ...choice, latencyMs: 1, model: 'fake' }; } }),
    /at least 2/,
  );
  assert.equal(calls, 0);
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
