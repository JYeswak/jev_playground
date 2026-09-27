import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp } from 'node:fs/promises';
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

test('installed omp rerank calls the measured top-1 Choice design', async () => {
  const { default: rerankTool } = await installedTool('jev-rerank.ts');
  let seen;
  const tool = rerankTool(pi, async (options) => {
    seen = options;
    return { ok: true, choice: '1', confidence: 0.91, probabilities: { '0': 0.09, '1': 0.91 }, latencyMs: 3, model: 'fake' };
  });
  const result = await tool.execute('id', { query: 'q', passages: ['first', 'selected'] });
  assert.deepEqual(Object.keys(seen.classes), ['0', '1']);
  assert.equal(result.details.choice, '1');
  assert.equal(result.details.selectedIndex, 1);
  assert.match(result.content[0].text, /top1=true/);
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
