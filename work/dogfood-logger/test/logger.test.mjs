import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { JsonlDecisionLog, decisionRecord, outcomeRecord } from '../src/logger.mjs';
import { parseRecords, summarize } from '../src/replay.mjs';

function decision(id, flag = 0.9) {
  return decisionRecord({ sessionId: 's', tool: 'bash', args: { command: id }, dcgVerdict: 'allow', questionSet: ['flag'], probabilities: { flag, pass: 1 - flag }, decisionId: id });
}

test('joined decision/outcome computes fire and proceeded false-positive rates', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'dogfood-'));
  const path = join(dir, 'events.jsonl');
  const log = new JsonlDecisionLog({ path });
  await log.append(decision('a', 0.9));
  await log.append(outcomeRecord({ decisionId: 'a', status: 'proceeded', exitStatus: 0 }));
  await log.append(decision('b', 0.1));
  await log.append(outcomeRecord({ decisionId: 'b', status: 'cancelled', exitStatus: null }));
  const parsed = parseRecords(await readFile(path, 'utf8'));
  const summary = summarize(parsed.records, parsed.malformed);
  assert.equal(summary.decisionCount, 2);
  assert.equal(summary.joinedOutcomeCount, 2);
  assert.equal(summary.fireCount, 1);
  assert.equal(summary.falsePositiveRate, 1);
  await rm(dir, { recursive: true, force: true });
});

test('malformed and orphan records are reported, not fatal', () => {
  const parsed = parseRecords(`${JSON.stringify(decision('a'))}\nnot-json\n${JSON.stringify(outcomeRecord({ decisionId: 'missing', status: 'failed', exitStatus: 1 }))}\n`);
  const summary = summarize(parsed.records, parsed.malformed);
  assert.equal(summary.malformedCount, 1);
  assert.equal(summary.orphanOutcomeCount, 1);
  assert.equal(summary.unmatchedDecisionCount, 1);
});

test('concurrent appends preserve every JSONL record', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'dogfood-'));
  const path = join(dir, 'events.jsonl');
  const log = new JsonlDecisionLog({ path, rotateBytes: 1_000_000 });
  const writes = [];
  for (let i = 0; i < 100; i += 1) writes.push(log.append(decision(`d-${i}`, i % 2 ? 0.1 : 0.9)));
  assert.equal((await Promise.all(writes)).every(Boolean), true);
  const parsed = parseRecords(await readFile(path, 'utf8'));
  assert.equal(parsed.malformed.length, 0);
  assert.equal(parsed.records.length, 100);
  await rm(dir, { recursive: true, force: true });
});

test('rotation keeps both files readable', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'dogfood-'));
  const path = join(dir, 'events.jsonl');
  const log = new JsonlDecisionLog({ path, rotateBytes: 200 });
  await Promise.all(Array.from({ length: 20 }, (_, i) => log.append(decision(`r-${i}`, 0.9))));
  const files = (await import('node:fs/promises')).readdir(dir);
  assert.ok((await files).length >= 2);
  await rm(dir, { recursive: true, force: true });
});
