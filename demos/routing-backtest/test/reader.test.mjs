import assert from 'node:assert/strict';
import test from 'node:test';
import { parseSessionText, readSessionLogs, requireClassifiable } from '../src/transcript-reader.mjs';

const session = (messages, model = 'cheap-1') =>
  [
    { type: 'session', version: 3, id: 'session-test' },
    { type: 'model_change', model },
    ...messages,
  ]
    .map((row) => JSON.stringify(row))
    .join('\n');

test('extracts model and token counts per classifiable turn', () => {
  const parsed = parseSessionText(
    session([
      { type: 'message', message: { role: 'user', content: [{ type: 'text', text: 'one' }] } },
      {
        type: 'message',
        message: {
          role: 'assistant',
          model: 'cheap-1',
          usage: { input: 11, output: 7 },
          content: [{ type: 'text', text: 'done' }],
        },
      },
    ]),
  );
  assert.deepEqual(parsed.totals, { turns: 1, classifiableTurns: 1, skippedTurns: 0 });
  assert.deepEqual(parsed.turns[0], {
    sessionId: 'session-test',
    turnIndex: 1,
    model: 'cheap-1',
    models: ['cheap-1'],
    promptTokens: 11,
    completionTokens: 7,
    assistantMessages: 1,
    classifiable: true,
    skipReason: null,
  });
});

test('uses model_change when assistant message omits model', () => {
  const parsed = parseSessionText(
    session([
      { type: 'message', message: { role: 'user', content: [{ type: 'text', text: 'one' }] } },
      { type: 'message', message: { role: 'assistant', usage: { input: 1, output: 2 }, content: [] } },
    ], 'model-from-change'),
  );
  assert.equal(parsed.turns[0].model, 'model-from-change');
});

test('records a skipped turn when the served model is absent', () => {
  const parsed = parseSessionText(
    [
      { type: 'session', id: 'unclassified' },
      { type: 'message', message: { role: 'user', content: [{ type: 'text', text: 'one' }] } },
      { type: 'message', message: { role: 'assistant', content: [] } },
    ]
      .map((row) => JSON.stringify(row))
      .join('\n'),
  );
  assert.equal(parsed.totals.classifiableTurns, 0);
  assert.equal(parsed.turns[0].skipReason, 'served model not recorded');
});

test('empty classifiable set is an error, never an empty green run', () => {
  const parsed = parseSessionText(
    JSON.stringify({ type: 'session', id: 'empty' }) + '\n' +
      JSON.stringify({ type: 'message', message: { role: 'user', content: [{ type: 'text', text: 'only prompt' }] } }),
    'empty.jsonl',
  );
  assert.throws(
    () => requireClassifiable({
      sessions: [parsed],
      turns: parsed.turns,
      totals: {
        sessions: 1,
        turns: parsed.totals.turns,
        classifiableTurns: parsed.totals.classifiableTurns,
        skippedTurns: parsed.totals.skippedTurns,
      },
    }),
    (error) => error?.code === 'EMPTY_CLASSIFIABLE_SET',
  );
});
