import test from 'node:test';
import assert from 'node:assert/strict';
import { parseArgv } from '../src/cli/argv.mjs';
import { freshHome, runCli } from './cli-support.mjs';

test('one-edit flag typo is interpreted with a warning at the CLI seam', async () => {
  const parsed = parseArgv(['--robto']);
  assert.equal(parsed.error?.correctedCommand, 'classifier --robot');

  const home = await freshHome('classifier-argv');
  const result = runCli(['doctor', '--robto'], { home });
  assert.equal(result.status, 2, result.stderr);
  assert.equal(JSON.parse(result.stdout).schema, 'classifier.doctor.v1');
  assert.ok(result.stderr.includes("interpreted as '--robot'"), result.stderr);
});

test('distant typos and destructive-flag typos are not suggested or applied', async () => {
  const distant = parseArgv(['--zzzz']);
  assert.equal(distant.error?.correctedCommand, undefined);
  const protectedFlag = parseArgv(['doctor', '--aply']);
  assert.equal(protectedFlag.error?.correctedCommand, undefined);

  const home = await freshHome('classifier-argv-negative');
  const noMatch = runCli(['doctor', '--zzzz'], { home });
  assert.equal(noMatch.status, 2, noMatch.stderr);
  assert.ok(noMatch.stderr.includes("unknown flag '--zzzz' ignored"), noMatch.stderr);
  assert.ok(!noMatch.stderr.includes('Did you mean:'), noMatch.stderr);
  const destructive = runCli(['doctor', '--aply'], { home });
  assert.equal(destructive.status, 2, destructive.stderr);
  assert.ok(destructive.stderr.includes("unknown flag '--aply' ignored"), destructive.stderr);
  assert.ok(!destructive.stderr.includes('--apply'), destructive.stderr);
  assert.ok(!destructive.stderr.includes('Did you mean:'), destructive.stderr);
});
