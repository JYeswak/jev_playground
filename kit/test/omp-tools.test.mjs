import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const pi = {
  zod: {
    object: (shape) => shape,
    string: () => ({ min: () => ({}) }),
    array: () => ({ min: () => ({ max: () => ({}) }) }),
  },
};

async function installedTool(name) {
  const repo = await mkdtemp(join(tmpdir(), 'jev-omp-tool-'));
  const { installOmp } = await import('../dist/install.js');
  await installOmp(repo);
  return import(pathToFileURL(join(repo, '.omp/tools', name)).href);
}

test('installed omp gate refuses the measured RISK hit without executing', async () => {
  const { default: gateTool } = await installedTool('jev-gate.ts');
  let seen;
  const tool = gateTool(pi, async (options) => {
    seen = options;
    return { ok: true, answers: { destructive: { noul: 0.89 } }, latencyMs: 4, resolvedModel: 'fake' };
  });
  const result = await tool.execute('id', { command: 'rm -rf /important' });
  assert.equal(seen.state.command, 'rm -rf /important');
  assert.equal(result.details.verdict, 'refuse');
  assert.equal(result.details.flag, true);
  assert.match(result.content[0].text, /verdict=refuse/);
});

test('installed omp rerank refuses 1/21 and selects projected 2 or recorded 20 FiQA IDs', async () => {
  const { default: rerankTool } = await installedTool('jev-rerank.ts');
  const fiqa = JSON.parse((await readFile(new URL('../../work/rerank-scifact/candidates-fiqa-fits.jsonl', import.meta.url), 'utf8')).split('\n', 1)[0]);
  const answer = JSON.parse(await readFile(new URL('./fixtures/rerank-fiqa-answer.json', import.meta.url), 'utf8'))[0].answers.choice;
  const ids = fiqa.cands.map(([id]) => id);
  assert.equal(fiqa.qid, '10034');
  assert.equal(ids.length, 20);
  assert.equal(answer.choice, '181942');
  let calls = 0;
  let offered = [];
  const tool = rerankTool(pi, async (options) => {
    calls++;
    assert.deepEqual(Object.keys(options.classes), offered.map((_, i) => String(i)));
    return {
      ok: true,
      choice: String(offered.indexOf(answer.choice)),
      confidence: answer.confidence,
      probabilities: Object.fromEntries(offered.map((id, i) => [String(i), answer.probabilities[id]])),
      latencyMs: 3,
      model: 'fake',
    };
  });
  for (const invalid of [ids.slice(0, 1), [...ids, ids[0]]]) {
    const result = await tool.execute('id', { query: fiqa.qid, passages: invalid });
    assert.equal(result.details.verdict, 'not_run');
    assert.match(result.content[0].text, /NOT_RUN/);
    assert.equal(calls, 0);
  }
  for (const valid of [[ids[0], answer.choice], ids]) {
    offered = valid;
    const result = await tool.execute('id', { query: fiqa.qid, passages: valid });
    assert.equal(result.details.verdict, 'selected');
    assert.equal(result.details.selectedIndex, valid.indexOf(answer.choice));
    assert.equal(result.details.passage, answer.choice);
    assert.match(result.content[0].text, /top1=true/);
  }
  assert.equal(calls, 2);
});

test('installed omp rerank sends distinct passage text and returns selected text verbatim', async () => {
  const { default: rerankTool } = await installedTool('jev-rerank.ts');
  const passages = ['Bonds mature in 2034.', '  Stocks fell 2%.\nSecond line stays.  '];
  const tool = rerankTool(pi, async (options) => {
    assert.equal(options.state.query, 'Which passage discusses stocks?');
    assert.deepEqual(options.state.candidates, [
      { id: '0', text: passages[0] },
      { id: '1', text: passages[1] },
    ]);
    return {
      ok: true,
      choice: '1',
      confidence: 0.9,
      probabilities: { '0': 0.1, '1': 0.9 },
      latencyMs: 3,
      model: 'fake',
    };
  });
  const result = await tool.execute('id', { query: 'Which passage discusses stocks?', passages });
  assert.equal(result.details.verdict, 'selected');
  assert.equal(result.details.selectedIndex, 1);
  assert.equal(result.details.passage, passages[1]);
  assert.equal(result.content[0].text.split('\n').slice(1).join('\n'), passages[1]);
});

test('installed omp claim check uses the SciFact 0.5 cut', async () => {
  const { default: claimCheckTool } = await installedTool('jev-claim-check.ts');
  let seen;
  const tool = claimCheckTool(pi, async (options) => {
    seen = options;
    return { ok: true, scores: { value: 0.6 }, latencyMs: 4, model: 'fake' };
  });
  const result = await tool.execute('id', { claim: 'A qualitative claim', evidence: 'Evidence text.' });
  assert.deepEqual(seen.questions.value.criteria, {
    true: 'The evidence states the claim or directly implies that it is true',
    false: 'The evidence contradicts the claim, or does not address what the claim asserts',
  });
  assert.equal(result.details.label, 'supported');
  assert.equal(result.details.threshold, 0.5);
});

test('installed omp claim check refuses numeric claims without asking', async () => {
  const { default: claimCheckTool } = await installedTool('jev-claim-check.ts');
  let calls = 0;
  const tool = claimCheckTool(pi, async () => {
    calls++;
    throw new Error('numeric claim reached the asker');
  });
  const result = await tool.execute('id', { claim: 'The result improved by 3%.', evidence: 'Evidence text.' });
  assert.equal(result.details.verdict, 'refused');
  assert.equal(result.details.reason, 'numeric-out-of-scope');
  assert.equal(result.details.calledModel, false);
  assert.equal(calls, 0);
});

test('installed omp classify calls the measured Banking77 Choice design', async () => {
  const { default: classifyTool } = await installedTool('jev-classify.ts');
  let seen;
  const tool = classifyTool(pi, async (options) => {
    seen = options;
    return { ok: true, choice: 'card arrival', confidence: 0.98, probabilities: { 'card arrival': 0.98, 'cash withdrawal': 0.02 }, latencyMs: 5, model: 'fake' };
  });
  const result = await tool.execute('id', { text: 'My card is late.', labels: ['card arrival', 'cash withdrawal'] });
  assert.deepEqual(seen.state, { customer_message: 'My card is late.' });
  assert.equal(seen.classes['card arrival'], null);
  assert.equal(result.details.label, 'card arrival');
  assert.equal(result.details.confidence, 0.98);
});
