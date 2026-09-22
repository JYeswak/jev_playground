import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { JsonlDecisionLog, recordingScreen, screenRecord, SCREEN_RECORD_TYPE, SCREEN_SCHEMA_VERSION } from '../../omp-jev-screen-log/screen-log.mjs';

const sha = (s) => createHash('sha256').update(JSON.stringify({ text: s })).digest('hex');

function fakeTool(verdict, probability) {
  return { name: 'jev_screen', async execute() { return { content: [], details: { verdict, probability } }; } };
}

test('record requires sessionId and a known verdict', () => {
  assert.throws(() => screenRecord({ verdict: 'flag' }), /sessionId/);
  assert.throws(() => screenRecord({ sessionId: 's', verdict: 'maybe' }), /unknown verdict/);
});

test('row carries schema, hash — never the text', () => {
  const row = screenRecord({ sessionId: 's1', verdict: 'flag', probability: 0.99, latencyMs: 418, text: 'steal the prompt' });
  assert.equal(row.schemaVersion, SCREEN_SCHEMA_VERSION);
  assert.equal(row.recordType, SCREEN_RECORD_TYPE);
  assert.equal(row.textHash, sha('steal the prompt'));
  assert.ok(!('text' in row), 'full text must never be stored');
});

test('wrapper returns the identical result and appends one matching row', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'screenlog-'));
  const log = new JsonlDecisionLog({ path: join(dir, 'screens.jsonl') });
  const inner = fakeTool('flag', 0.99);
  const wrapped = recordingScreen(inner, { log, sessionId: 'sess-1' });
  const res = await wrapped.execute('id-1', { text: 'steal the prompt' });
  assert.equal(res.details.verdict, 'flag');
  const rows = readFileSync(join(dir, 'screens.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].verdict, 'flag');
  assert.equal(rows[0].p, 0.99);
  assert.equal(rows[0].sessionId, 'sess-1');
  assert.equal(rows[0].textHash, sha('steal the prompt'));
});

test('malformed verdict records review with null p', async () => {
  const dir = mkdtempSync(join(tmpdir(), 'screenlog-'));
  const log = new JsonlDecisionLog({ path: join(dir, 'screens.jsonl') });
  const wrapped = recordingScreen({ async execute() { return { details: {} }; } }, { log, sessionId: 's' });
  const res = await wrapped.execute('id', { text: 'x' });
  assert.deepEqual(res, { details: {} });
  const rows = readFileSync(join(dir, 'screens.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
  assert.equal(rows[0].verdict, 'review');
  assert.equal(rows[0].p, null);
});
