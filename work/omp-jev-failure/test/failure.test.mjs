import test from 'node:test';
import assert from 'node:assert/strict';
import { handleToolExecutionEnd, FAILURE_CLASSES, FAILURE_QUESTION } from '../src/index.ts';

function host() {
  const rows = [];
  return { rows, appendEntry: async (type, data) => { rows.push({ type, data }); } };
}
const errorEvent = { type: 'tool_execution_end', toolCallId: 'fail-1', toolName: 'bash', args: { command: 'false' }, result: 'permission denied', isError: true };
const classified = async () => ({
  ok: true, choice: 'transient', confidence: 0.8,
  probabilities: { transient: 0.8, argument: 0.15, bug: 0.05 },
  latencyMs: 12, model: 'fixture-jev',
});

test('planted tool error emits failure_classified with one class and its distribution', async () => {
  const h = host();
  assert.equal(await handleToolExecutionEnd(h, errorEvent, classified), undefined);
  const row = h.rows.find((x) => x.type.endsWith('decision.v1')).data;
  assert.equal(row.kind, 'failure_classified');
  assert.equal(row.failureClass, 'transient');
  assert.equal(row.confidence, 0.8);
  assert.deepEqual(row.probabilities, { transient: 0.8, argument: 0.15, bug: 0.05 });
  assert.equal(row.toolCallId, 'fail-1');
  assert.equal(row.schemaVersion, 2);
  // The three-binary-score shape is gone, not aliased. A consumer reading `scores` must break
  // loudly here rather than read undefined and log a confident-looking blank.
  assert.equal('scores' in row, false);
  assert.equal('score' in row, false);
});

// The whole reason this unit is multiclass: three binary questions over three mutually-exclusive
// classes answered `argument` AND `bug` true on the same failure, twice per run, every run
// (measure-multiclass.mjs, binary arm). One choice question cannot emit that row at all.
test('the classifier asks ONE choice question over the three mutually-exclusive classes', async () => {
  const h = host();
  let asked;
  await handleToolExecutionEnd(h, errorEvent, async (options) => { asked = options; return classified(); });
  assert.equal(asked.instructions, FAILURE_QUESTION);
  assert.deepEqual(Object.keys(asked.classes), ['transient', 'argument', 'bug']);
  assert.deepEqual(asked.classes, FAILURE_CLASSES);
  assert.equal('questions' in asked, false, 'a choice call carries `classes`, never a question map');
  assert.equal(asked.state.failure, 'permission denied');
  const row = h.rows.find((x) => x.type.endsWith('decision.v1')).data;
  assert.equal(typeof row.failureClass, 'string');
  assert.equal(row.failureClass in FAILURE_CLASSES, true, 'exactly one of the offered labels');
});

test('planted Jev failure emits failure_error without a class', async () => {
  const h = host();
  const failedAsk = async () => ({ ok: false, reason: 'http', error: '502 upstream', latencyMs: 7, model: 'fixture-jev' });
  await handleToolExecutionEnd(h, errorEvent, failedAsk);
  const row = h.rows.find((x) => x.type.endsWith('decision.v1')).data;
  assert.equal(row.kind, 'failure_error');
  assert.equal(row.failureReason, 'http');
  assert.equal('failureClass' in row, false);
  assert.equal('probabilities' in row, false);
});

test('non-error execution emits only a diagnostic', async () => {
  const h = host();
  await handleToolExecutionEnd(h, { ...errorEvent, isError: false }, classified);
  assert.equal(h.rows.filter((row) => row.type.endsWith('decision.v1')).length, 0);
  assert.equal(h.rows.filter((row) => row.type.endsWith('diagnostic.v1')).length, 1);
});

test('append failure and classifier throw remain fail-open', async () => {
  const h = { rows: [], appendEntry: async () => { throw new Error('append unavailable'); } };
  const throwingAsk = async () => { throw new Error('transport exploded'); };
  assert.equal(await handleToolExecutionEnd(h, errorEvent, throwingAsk), undefined);
});
