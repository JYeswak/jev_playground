import test from 'node:test';
import assert from 'node:assert/strict';
import { chmod, stat, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { doctorFixture, snapshot } from './doctor-support.mjs';
import { runCli } from './cli-support.mjs';

function runRepair(args, fixture) {
  const doctorDir = join(fixture.home, '.local/state/classifier/doctor');
  return runCli(['repair', ...args], {
    home: fixture.home,
    cwd: fixture.repo,
    env: {
      CI: '1',
      JEV_STATE_DIR: fixture.stateDir,
      JEV_DOCTOR_DIR: doctorDir,
      NO_COLOR: '1',
      PATH: '',
    },
  });
}

test('repair defaults to a zero-write plan and names apply plus rollback commands', async () => {
  const fixture = await doctorFixture('classifier-repair-plan', { tier: 'deep' });
  const log = join(fixture.stateDir, 'mode-check.jsonl');
  await writeFile(log, '');
  await chmod(log, 0o644);
  const before = await snapshot(fixture.home);
  const beforeMode = (await stat(log)).mode & 0o777;

  const result = runRepair(['--json', '--only', 'fm-logs-mode-too-open'], fixture);

  assert.equal(result.status, 0, result.stderr || result.stdout);
  const envelope = JSON.parse(result.stdout);
  assert.equal(envelope.schema, 'classifier.repair.v1');
  assert.equal(envelope.status, 'OK');
  assert.equal(envelope.data.mode, 'plan');
  const commands = JSON.stringify(envelope.data);
  assert.ok(commands.includes('--apply'));
  assert.ok(commands.includes('undo latest'));
  assert.deepEqual(await snapshot(fixture.home), before);
  assert.equal((await stat(log)).mode & 0o777, beforeMode);
});

test('unknown repair option typo returns usage status and exact corrected command', async () => {
  const fixture = await doctorFixture('classifier-repair-option-typo', { tier: 'deep' });

  const result = runRepair(['--jso'], fixture);

  assert.equal(result.status, 64, result.stderr || result.stdout);
  assert.ok(result.stderr.includes("error: unknown option '--jso'"), result.stderr);
  assert.ok(result.stderr.includes('did you mean: classifier repair --json'), result.stderr);
});
