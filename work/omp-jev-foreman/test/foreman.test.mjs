import test from 'node:test';
import assert from 'node:assert/strict';
import { createForeman } from '../src/index.ts';

const askScore = async () => ({ ok: true, scores: { repeating: 0.9, progress: 0.1, stuck: 0.85 }, latencyMs: 11, model: 'fixture-jev' });
const event = (n, command = `echo ${n}`) => ({ type: 'tool_execution_end', toolCallId: `tc-${n}`, toolName: 'bash', args: { command }, result: { content: [] }, isError: false });

function harness(ask = askScore) {
  const rows = [];
  const observe = createForeman({ ask, append: async (type, data) => rows.push({ type, data }) });
  return { rows, observe };
}

test('healthy varied window does not trigger Jev', async () => {
  const h = harness();
  for (let i = 0; i < 7; i++) await h.observe(event(i, `read file-${i}.ts`));
  assert.equal(h.rows.length, 0);
});

test('repeated-command window triggers one scored decision', async () => {
  const h = harness();
  for (let i = 0; i < 3; i++) await h.observe(event(i, 'npm test'));
  const decisions = h.rows.filter((row) => row.data.kind === 'foreman_scored');
  assert.equal(decisions.length, 1);
  assert.equal(decisions[0].data.trigger, 'repeated_command');
  assert.deepEqual(decisions[0].data.scores, { repeating: 0.9, progress: 0.1, stuck: 0.85 });
});

test('throwing classifier emits foreman_error without scores', async () => {
  const h = harness(async () => { throw new Error('fixture transport'); });
  for (let i = 0; i < 3; i++) await h.observe(event(i, 'git status'));
  const decision = h.rows.find((row) => row.data.kind === 'foreman_error');
  assert.ok(decision);
  assert.equal('scores' in decision.data, false);
  assert.equal(decision.data.failureReason, 'transport');
});

test('throwing host remains fail-open', async () => {
  const observe = createForeman({ ask: askScore, append: async () => { throw new Error('fixture host'); } });
  for (let i = 0; i < 3; i++) assert.equal(await observe(event(i, 'git diff')), undefined);
});
