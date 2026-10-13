import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import { BANKING77_INSTRUCTIONS } from '../src/classify.ts';
import { fingerprintWeights, loadCalibrations, plattMap, questionSha } from '../src/calibration.ts';
import { plattMap as vendorPlattMap } from '../../work/vendor-paste/vendor-shadow.mjs';

const repoRoot = fileURLToPath(new URL('../..', import.meta.url));
const answerFixture = JSON.parse(await readFile(new URL('./fixtures/banking77-answer.json', import.meta.url), 'utf8'))[0];
const labels = Object.keys(answerFixture.answers.choice.probabilities);
const question = {
  type: 'choice',
  instructions: BANKING77_INSTRUCTIONS,
  criteria: Object.fromEntries(labels.map((label) => [label, null])),
};
const stateKeys = ['customer_message'];
const B77_PREREG = 'ca787540';
const B77_RESULT = '8b1bb513';
const B77_MAP = {
  kind: 'platt-logit',
  target: 'p_choice',
  a: 1.3526520145076346,
  b: 0.0002885751250081534,
  clip: 1e-4,
};

async function ownedScratch(label) {
  const root = join(repoRoot, 'var/agent-tmp');
  await mkdir(root, { recursive: true });
  const dir = await mkdtemp(join(root, `${label}.${process.pid}.`));
  await writeFile(join(dir, '.owner'), `pid=${process.pid} label=${label} repo=jev created=${new Date().toISOString()}\n`);
  return dir;
}

function b77Calibration(questionHash, model) {
  // Schema-only fixture: receipt identifiers and coefficients come from the recorded B77 experiment;
  // the temporary model bytes below are not that experiment's weights and make no quality claim.
  return {
    schema: 'jev.clef-calibration.v1',
    task_id: 'banking77-intent',
    version: 1,
    primitive: 'choice',
    question_key: 'intent',
    question_sha256: questionHash,
    model: { id: 'clef-flash', ...model },
    map: B77_MAP,
    fit: { split: 'dev', n: 200, steps: 2000, learning_rate: 0.1, initial_a: 1, initial_b: 0 },
    receipt: {
      prereg_commit: B77_PREREG,
      result_commit: B77_RESULT,
      verdict: 'PASS',
      held_rows: 600,
    },
  };
}

test('questionSha matches canonical question plus sorted state keys', () => {
  const digest = questionSha(question, stateKeys);
  const sortedCriteria = Object.fromEntries(Object.entries(question.criteria).sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0));
  const expectedQuestion = { criteria: sortedCriteria, instructions: question.instructions, type: question.type };
  const expected = createHash('sha256')
    .update(JSON.stringify({ question: expectedQuestion, state_keys: [...stateKeys].sort() }), 'utf8')
    .digest('hex');
  const reorderedQuestion = {
    criteria: Object.fromEntries(Object.entries(question.criteria).reverse()),
    instructions: question.instructions,
    type: question.type,
  };
  assert.equal(digest.length, 64);
  assert.equal(digest, expected);
  assert.equal(questionSha(reorderedQuestion, stateKeys), digest);
  assert.notEqual(questionSha({ ...question, instructions: `${question.instructions} ` }, stateKeys), digest);
});

test('fingerprintWeights hashes model file bytes, not file names', async () => {
  const dir = await ownedScratch('clef-fingerprint');
  await writeFile(join(dir, 'joint_head.safetensors'), 'abc');
  await writeFile(join(dir, 'model.safetensors.index.json'), 'abc');
  const expected = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad';
  assert.deepEqual(await fingerprintWeights(dir), {
    joint_head_sha256: expected,
    index_sha256: expected,
  });
  await writeFile(join(dir, 'joint_head.safetensors'), 'abd');
  const changed = await fingerprintWeights(dir);
  assert.notEqual(changed.joint_head_sha256, expected);
  assert.equal(changed.index_sha256, expected);
});

test('loadCalibrations accepts a structurally valid unit fixture and refuses missing commits or non-finite maps', async () => {
  const root = await ownedScratch('clef-calibration');
  const modelDir = join(root, 'weights');
  const calibrationDir = join(root, 'calibrations');
  await mkdir(modelDir);
  await mkdir(calibrationDir);
  await writeFile(join(modelDir, 'joint_head.safetensors'), 'abc');
  await writeFile(join(modelDir, 'model.safetensors.index.json'), 'abc');
  const model = await fingerprintWeights(modelDir);
  const valid = b77Calibration(questionSha(question, stateKeys), model);
  await writeFile(join(calibrationDir, 'banking77-intent.v1.json'), JSON.stringify(valid));

  const loaded = await loadCalibrations(calibrationDir);
  assert.equal(loaded.length, 1);
  assert.equal(loaded[0].task_id, 'banking77-intent');
  assert.equal(loaded[0].receipt.result_commit, B77_RESULT);

  const missingCommit = { ...valid, task_id: 'missing-result', receipt: { ...valid.receipt, result_commit: '' } };
  await writeFile(join(calibrationDir, 'missing-result.v1.json'), JSON.stringify(missingCommit));
  const nonFinite = JSON.stringify({ ...valid, task_id: 'non-finite' }).replace('1.3526520145076346', '1e9999');
  await writeFile(join(calibrationDir, 'non-finite.v1.json'), nonFinite);
  const filtered = await loadCalibrations(calibrationDir);
  assert.deepEqual(filtered.map((item) => item.task_id), ['banking77-intent']);
});

test('Platt mapping matches the vendored local-shadow implementation at the frozen probe values', () => {
  const map = { a: 1.239, b: 2.926, clip: 1e-4 };
  for (const p of [0.1, 0.5, 0.9]) {
    assert.ok(Math.abs(plattMap(p, map) - vendorPlattMap(p, map)) < 1e-3, `p=${p}`);
  }
  assert.equal(plattMap(0, map), plattMap(1e-4, map));
  assert.equal(plattMap(1, map), plattMap(1 - 1e-4, map));
});
