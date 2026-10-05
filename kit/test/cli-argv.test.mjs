import test from 'node:test';
import assert from 'node:assert/strict';
import { parseArgv } from '../src/cli/argv.mjs';
import { freshHome, runCli } from './cli-support.mjs';

test('one-edit typo offers an exact safe correction at the parser and CLI seams', async () => {
  const parsed = parseArgv(['--robto']);
  assert.equal(parsed.error?.correctedCommand, 'classifier --robot');

  const home = await freshHome('classifier-argv');
  const result = runCli(['--robto'], { home });
  assert.equal(result.status, 64, result.stderr);
  assert.equal(result.stdout, '');
  assert.ok(result.stderr.includes('Did you mean: classifier --robot'), result.stderr);
});

test('distant typos and destructive-flag typos are not suggested or applied', async () => {
  const distant = parseArgv(['--zzzz']);
  assert.equal(distant.error?.correctedCommand, undefined);
  const protectedFlag = parseArgv(['doctor', '--aply']);
  assert.equal(protectedFlag.error?.correctedCommand, undefined);

  const home = await freshHome('classifier-argv-negative');
  const noMatch = runCli(['--zzzz'], { home });
  assert.equal(noMatch.status, 64, noMatch.stderr);
  assert.ok(!noMatch.stderr.includes('Did you mean:'), noMatch.stderr);
  const destructive = runCli(['doctor', '--aply'], { home });
  assert.equal(destructive.status, 64, destructive.stderr);
  assert.ok(!destructive.stderr.includes('--apply'), destructive.stderr);
  assert.ok(!destructive.stderr.includes('Did you mean:'), destructive.stderr);
});
