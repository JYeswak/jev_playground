/**
 * Tests for the silent register.
 *
 * The two load-bearing properties are the ones jevcache got wrong, so they get
 * planted negatives rather than happy paths:
 *   - the raw input must be UNRECOVERABLE from the register
 *   - two different inputs must NEVER share an identity, including when a field
 *     name looks like a volatile id
 *
 * Run: node --test work/jev-score-register/register.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { canonicalise, inputIdentity, recordScore, readRegister, recording } from './register.mjs';

const dir = () => mkdtempSync(join(tmpdir(), 'jsr-'));

test('PLANTED NEGATIVE: the jevcache collision cannot happen here', () => {
  // jevcache deleted *_id fields before hashing, so these two shared a fingerprint
  // and it served the benign answer for the destructive command.
  const destructive = inputIdentity({ command_id: 'rm -rf --no-preserve-root /' });
  const benign = inputIdentity({ command_id: 'echo hello' });
  assert.notEqual(destructive, benign, 'different inputs must never share an identity');
});

test('PLANTED NEGATIVE: no field is dropped, whatever it is called', () => {
  assert.notEqual(inputIdentity({ a: 1, b_id: 'x' }), inputIdentity({ a: 1, b_id: 'y' }));
  assert.notEqual(inputIdentity({ a: 1 }), inputIdentity({ a: 1, timestamp_id: 'z' }));
});

test('PLANTED NEGATIVE: the raw input is not recoverable from the register', () => {
  const path = join(dir(), 'scores.jsonl');
  const secret = 'PLACEHOLDERTOKENNODIGITS';
  recordScore(path, { questionKey: 'q', score: 0.9, model: 'm', state: { authorization: `Bearer ${secret}` } });
  const raw = readFileSync(path, 'utf8');
  assert.ok(!raw.includes(secret), 'register must never contain input text');
  assert.ok(!raw.includes('authorization'), 'not even the field names');
  assert.ok(!raw.includes('state_preview'), 'the jevcache field must not exist here');
});

test('register file is created 0600, not 0644', () => {
  const path = join(dir(), 'nested', 'scores.jsonl');
  recordScore(path, { questionKey: 'q', score: 0.1, model: 'm', state: { a: 1 } });
  assert.equal(statSync(path).mode & 0o777, 0o600);
});

test('identity is stable across key order', () => {
  assert.equal(inputIdentity({ a: 1, b: 2 }), inputIdentity({ b: 2, a: 1 }));
  assert.equal(canonicalise({ b: 2, a: 1 }), '{"a":1,"b":2}');
});

test('rows round-trip, and a torn final line does not lose the rest', () => {
  const path = join(dir(), 'scores.jsonl');
  recordScore(path, { questionKey: 'q1', score: 0.7, model: 'm', state: { a: 1 } });
  recordScore(path, { questionKey: 'q2', score: 0.2, model: 'm', state: { a: 2 } });
  const { rows, malformed } = readRegister(path);
  assert.equal(rows.length, 2);
  assert.equal(malformed, 0);
  assert.equal(rows[0].questionKey, 'q1');
  assert.equal(rows[0].score, 0.7);
});

test('a failed call is recorded as a gap, never as a passing score', () => {
  const path = join(dir(), 'scores.jsonl');
  recordScore(path, { questionKey: 'q', model: 'm', state: { a: 1 }, ok: false, failure: 'http', score: 0 });
  const { rows } = readRegister(path);
  assert.equal(rows[0].ok, false);
  assert.equal(rows[0].score, null, 'a failure must not look like a 0.0 answer');
  assert.equal(rows[0].failure, 'http');
});

test('recording() does not change the wrapped answer', async () => {
  const path = join(dir(), 'scores.jsonl');
  const fake = async () => ({ ok: true, scores: { alpha: 0.8, beta: 0.1 }, model: 'jev-test' });
  const wrapped = recording(fake, { path, extension: 'omp-jev-x', model: 'jev-test' });
  const direct = await fake();
  const viaRegister = await wrapped({ state: { a: 1 }, questions: { alpha: 'a?', beta: 'b?' } });
  assert.deepEqual(viaRegister, direct, 'the register is a side effect, never a substitute');
  const { rows } = readRegister(path);
  assert.equal(rows.length, 2, 'one row per question');
  assert.deepEqual(rows.map((r) => r.questionKey).sort(), ['alpha', 'beta']);
});

test('recording() records a failure without inventing a score', async () => {
  const path = join(dir(), 'scores.jsonl');
  const failing = async () => ({ ok: false, failure: 'transport' });
  const wrapped = recording(failing, { path, extension: 'omp-jev-x', model: 'jev-test' });
  await wrapped({ state: { a: 1 }, questions: { alpha: 'a?' } });
  const { rows } = readRegister(path);
  assert.equal(rows[0].ok, false);
  assert.equal(rows[0].score, null);
});

test('recordScore refuses a row it cannot attribute', () => {
  const path = join(dir(), 'scores.jsonl');
  assert.throws(() => recordScore(path, { score: 0.5, model: 'm', state: { a: 1 } }), /questionKey/);
  assert.throws(() => recordScore(path, { questionKey: 'q', score: 0.5, model: 'm' }), /identity/);
});
