import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { askJevChoice } from '../src/client.ts';
import { RecordedFakeAsker } from '../src/fake.ts';

const rows = JSON.parse(await readFile(new URL('./fixtures/recorded-answer-rows.json', import.meta.url)));

test('recorded answer rows drive a deterministic offline Choice response', async () => {
  const asker = new RecordedFakeAsker(rows);
  const result = await askJevChoice({
    state: { task: rows[0].id },
    instructions: 'Which candidate?',
    classes: { c0: 'Candidate 1', c1: 'Candidate 2', none: 'Abstain' },
    apiKey: ['fixture', 'key'].join('-'),
    fetchImpl: asker.fetch,
  });
  assert.equal(result.ok, true);
  assert.equal(result.choice, rows[0].answers.choice.choice);
  assert.deepEqual(result.probabilities, rows[0].answers.choice.probabilities);
});

test('fake asker exhausts recorded rows rather than inventing a fallback', async () => {
  const asker = new RecordedFakeAsker(rows.slice(0, 1));
  const options = { state: { task: 'captured' }, instructions: 'q', classes: { c0: 'a', c1: 'b', none: 'none' }, apiKey: ['fixture', 'key'].join('-'), fetchImpl: asker.fetch };
  const first = await askJevChoice(options);
  assert.equal(first.ok, true);
  const second = await askJevChoice(options);
  assert.equal(second.ok, false);
  assert.equal(second.reason, 'transport');
});
