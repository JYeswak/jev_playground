import test from 'node:test';
import assert from 'node:assert/strict';
import { handleToolExecutionEnd } from '../src/index.ts';

function host() {
  const rows = [];
  return { rows, appendEntry: async (type, data) => { rows.push({ type, data }); } };
}
const errorEvent = { type: 'tool_execution_end', toolCallId: 'fail-1', toolName: 'bash', args: { command: 'false' }, result: 'permission denied', isError: true };
const scores = async () => ({ ok: true, scores: { transient: 0.8, argument: 0.1, bug: 0.2 }, latencyMs: 12, model: 'fixture-jev' });

test('planted tool error emits failure_scored with scores', async () => {
  const h = host();
  assert.equal(await handleToolExecutionEnd(h, errorEvent, scores), undefined);
  const row = h.rows.find((x) => x.type.endsWith('decision.v1')).data;
  assert.equal(row.kind, 'failure_scored');
  assert.deepEqual(row.scores, { transient: 0.8, argument: 0.1, bug: 0.2 });
  assert.equal(row.toolCallId, 'fail-1');
  assert.equal('score' in row, false);
});

test('planted Jev failure emits failure_error without scores', async () => {
  const h = host();
  const failedAsk = async () => ({ ok: false, reason: 'http', error: '502 upstream', latencyMs: 7, model: 'fixture-jev' });
  await handleToolExecutionEnd(h, errorEvent, failedAsk);
  const row = h.rows.find((x) => x.type.endsWith('decision.v1')).data;
  assert.equal(row.kind, 'failure_error');
  assert.equal(row.failureReason, 'http');
  assert.equal('scores' in row, false);
});

test('non-error execution emits only a diagnostic', async () => {
  const h = host();
  await handleToolExecutionEnd(h, { ...errorEvent, isError: false }, scores);
  assert.equal(h.rows.filter((row) => row.type.endsWith('decision.v1')).length, 0);
  assert.equal(h.rows.filter((row) => row.type.endsWith('diagnostic.v1')).length, 1);
});

test('append failure and classifier throw remain fail-open', async () => {
  const h = { rows: [], appendEntry: async () => { throw new Error('append unavailable'); } };
  const throwingAsk = async () => { throw new Error('transport exploded'); };
  assert.equal(await handleToolExecutionEnd(h, errorEvent, throwingAsk), undefined);
});
