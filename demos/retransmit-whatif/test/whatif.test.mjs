import test from 'node:test';
import assert from 'node:assert/strict';
import { readUsageFiles } from '../src/reader.mjs';
import { aggregate, measureTurn, shares } from '../src/whatif-core.mjs';

const fixture = new URL('../fixtures/known-shape.jsonl', import.meta.url).pathname;

test('known shape recovers all four token fields and denominator', async () => {
  const result = await readUsageFiles([fixture]);
  assert.equal(result.denominator.assistantTurns, 2);
  assert.equal(result.denominator.turnsWithUsage, 2);
  assert.equal(result.denominator.nonTurnRecords, 1);
  const total = aggregate(result.sessions[0].turns);
  assert.deepEqual(total, { cacheRead: 1000, cacheWrite: 50, input: 300, output: 100, total: 1450 });
  assert.equal(measureTurn(result.sessions[0].turns[0], 0.5).saved, 450);
  assert.equal(shares(total).cacheRead, 1000 / 1450);
});

test('malformed and negative usage are recorded as failures', async () => {
  const result = await readUsageFiles([new URL('../fixtures/malformed.jsonl', import.meta.url).pathname]);
  assert.equal(result.failures.length, 2);
  assert.deepEqual(result.failures.map((x) => x.code).sort(), ['INVALID_USAGE', 'MALFORMED_JSONL']);
});
