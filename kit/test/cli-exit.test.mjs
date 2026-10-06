import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { EXIT_CODES, exitCodeForFailure, statusForFailure } from '../src/cli/exit.mjs';
import { rewriteCliError } from '../dist/cli/errors.js';
import { examplePath, freshHome, runCli } from './cli-support.mjs';

test('the shared exit dictionary and failure classes are stable', () => {
  assert.deepEqual({ ...EXIT_CODES }, {
    OK: 0,
    FINDINGS: 1,
    NOT_RUN: 2,
    REFUSED: 3,
    REFUSED_UNSAFE: 4,
    RETRYABLE: 5,
    ONLINE_REQUIRED: 6,
    USAGE: 64,
    NO_INPUT: 66,
    CANT_CREATE: 73,
    IO: 74,
  });
  assert.equal(exitCodeForFailure({ reason: 'unconfigured' }), 2);
  assert.equal(statusForFailure({ reason: 'unconfigured' }), 'NOT_RUN');
  assert.equal(exitCodeForFailure({ reason: 'no-answers' }), 3);
  assert.equal(statusForFailure({ reason: 'no-answers' }), 'REFUSED');
  assert.equal(exitCodeForFailure({ reason: 'refused-unsafe' }), 4);
  assert.equal(exitCodeForFailure({ reason: 'transport' }), 5);
  assert.equal(exitCodeForFailure({ reason: 'sdk-missing' }), 6);
  assert.equal(exitCodeForFailure({ reason: 'usage' }), 64);
  assert.equal(exitCodeForFailure({ reason: 'no-input' }), 66);
  assert.equal(exitCodeForFailure({ reason: 'cannot-create' }), 73);
  assert.equal(exitCodeForFailure({ reason: 'io' }), 74);
});

test('retryable and unsafe installer errors retain their typed exit envelopes', () => {
  const retryable = rewriteCliError({ reason: 'transport', message: 'installer is already running', command: 'classifier install' });
  assert.equal(retryable.code, 'RETRYABLE');
  assert.equal(retryable.exit_code, EXIT_CODES.RETRYABLE);

  const refused = rewriteCliError({ reason: 'refused-unsafe', message: 'invalid installer manifest', command: 'classifier install' });
  assert.equal(refused.code, 'REFUSED_UNSAFE');
  assert.equal(refused.exit_code, EXIT_CODES.REFUSED_UNSAFE);
});

test('missing credentials stay NOT_RUN with the same exit under JSON and robot modes', async () => {
  const home = await freshHome('classifier-no-key');
  const base = ['ask', 'choice', '--state', examplePath('state.json'), '--question', examplePath('question.json')];
  for (const mode of ['--json', '--robot']) {
    const result = runCli([...base, mode], { home });
    assert.equal(result.status, 2, result.stderr);
    const body = JSON.parse(result.stdout);
    assert.equal(body.schema, 'classifier.ask.v1');
    assert.equal(body.ok, false);
    assert.equal(body.status, 'NOT_RUN');
    assert.equal(body.errors[0].code, 'NOT_RUN');
    assert.equal(body.errors[0].exit_code, 2);
  }
});

test('doctor preserves its raw --json contract while --robot wraps it; both use no-key exit 2', async () => {
  const home = await freshHome('classifier-doctor-no-key');
  const raw = runCli(['doctor', '--json'], { home });
  assert.equal(raw.status, 2, raw.stderr);
  assert.equal(JSON.parse(raw.stdout).status, 'NOT_RUN');
  assert.equal(Object.hasOwn(JSON.parse(raw.stdout), 'schema'), false);
  const robot = runCli(['doctor', '--robot'], { home });
  assert.equal(robot.status, 2, robot.stderr);
  const body = JSON.parse(robot.stdout);
  assert.equal(body.schema, 'classifier.doctor.v1');
  assert.equal(body.status, 'NOT_RUN');
  assert.equal(body.data.status, 'NOT_RUN');
});

test('an unoffered recorded answer is REFUSED with exit 3, not NOT_RUN', async () => {
  const home = await freshHome('classifier-refused');
  const question = JSON.parse(await readFile(examplePath('question.json'), 'utf8'));
  delete question.criteria.c1;
  const questionPath = join(home, 'question.json');
  await writeFile(questionPath, JSON.stringify(question));
  const result = runCli([
    'ask', 'choice', '--state', examplePath('state.json'), '--question', questionPath, '--fake', '--robot',
  ], { home });
  assert.equal(result.status, 3, result.stderr);
  const body = JSON.parse(result.stdout);
  assert.equal(body.ok, false);
  assert.equal(body.status, 'REFUSED');
  assert.equal(body.errors[0].code, 'REFUSED');
});
