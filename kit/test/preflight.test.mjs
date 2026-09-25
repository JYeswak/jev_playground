import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { classifySizeBytes, optionsPreflight, offeredPreflight, PreflightError, sizePreflight, sizePreflightBytes } from '../src/preflight.ts';

const over = JSON.parse(await readFile(new URL('./fixtures/r112-over-limit.json', import.meta.url)));
const mini = JSON.parse(await readFile(new URL('./fixtures/miniwob-drag-items-grid-one-option.json', import.meta.url)));
const fits = JSON.parse(await readFile(new URL('./fixtures/fits-state.json', import.meta.url)));

test('R112 captured max_tokens_exceeded row is refused as OVER before spend', () => {
  assert.equal(classifySizeBytes(over.state_bytes, over.question_bytes), 'OVER');
  assert.throws(
    () => sizePreflightBytes(over.state_bytes, over.question_bytes),
    (error) => error instanceof PreflightError && error.code === 'size-over' && error.status === 'OVER',
  );
});

test('captured FITS OSWorld state passes the same compact-byte band', () => {
  const result = sizePreflight(fits.captured, fits.question);
  assert.equal(result.status, 'FITS');
  assert.ok(result.totalBytes < 32_768 * 1.4794769192690072);
});

test('captured drag-items-grid one-option observation is refused before Choice spend', () => {
  const question = { type: 'choice', criteria: Object.fromEntries(mini.observed_options.map((id) => [id, id])) };
  assert.throws(
    () => optionsPreflight(question),
    (error) => error instanceof PreflightError && error.code === 'choice-options',
  );
});

test('offeredPreflight refuses a solving option absent from the captured options', () => {
  const question = { type: 'choice', criteria: { none: 'do nothing', click: 'click' } };
  assert.throws(
    () => offeredPreflight(question, 'drag'),
    (error) => error instanceof PreflightError && error.code === 'offered-option',
  );
});

test('NEAR is fail-safe refusal unless allowNear is explicit', () => {
  const nearBytes = Math.ceil(32_768 * 1.6);
  assert.equal(classifySizeBytes(nearBytes, 0), 'NEAR');
  assert.throws(() => sizePreflightBytes(nearBytes, 0), /NEAR/);
  assert.equal(sizePreflightBytes(nearBytes, 0, { allowNear: true }).status, 'NEAR');
});
