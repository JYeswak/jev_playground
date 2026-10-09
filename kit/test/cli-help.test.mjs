import test from 'node:test';
import assert from 'node:assert/strict';
import { freshHome, runCli } from './cli-support.mjs';

test('bare invocation and help aliases exit successfully without ANSI styling', async () => {
  const home = await freshHome('classifier-help');
  for (const args of [[], ['--help'], ['-h'], ['help']]) {
    const result = runCli(args, { home, env: { CI: 'true', TERM: 'dumb', NO_COLOR: '1' } });
    assert.equal(result.status, 0, `${args.join(' ')}: ${result.stderr}`);
    assert.equal(result.stderr, '');
    assert.ok(!result.stdout.includes('\u001b['), 'help leaked ANSI styling');
  }
  const version = runCli(['--version'], { home });
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout, 'classifier 0.0.0\n');
  assert.equal(version.stderr, '');
});

test('topic and command help are successful and identify the requested command', async () => {
  const home = await freshHome('classifier-topic-help');
  const cases = [
    [['help', 'ask'], 'classifier ask choice|score|noul'],
    [['ask', '--help'], 'classifier ask choice|score|noul'],
    [['help', 'doctor'], 'classifier doctor [--quick|--deep]'],
    [['doctor', '--help'], 'classifier doctor [--quick|--deep]'],
    [['help', 'health'], 'classifier health [--json|--robot]'],
    [['health', '--help'], 'classifier health [--json|--robot]'],
  ];
  for (const [args, fragment] of cases) {
    const result = runCli(args, { home });
    assert.equal(result.status, 0, result.stderr);
    assert.ok(result.stdout.includes(fragment), result.stdout);
    if (args.includes('ask')) assert.ok(result.stdout.includes('Examples:'), result.stdout);
    assert.equal(result.stderr, '');
  }
});

test('health CLI returns keyless envelopes for JSON and robot modes', async () => {
  const home = await freshHome('classifier-health');
  for (const mode of ['--json', '--robot']) {
    const result = runCli(['health', mode], { home, env: { PATH: '', TYPESAFE_API_KEY: '' } });
    assert.equal(result.status, 1, result.stderr);
    const envelope = JSON.parse(result.stdout);
    assert.equal(envelope.schema, 'classifier.health.v1');
    assert.equal(envelope.status, 'FINDINGS');
    assert.equal(envelope.data.status, 'findings');
    assert.equal(envelope.data.key_source, 'none');
    assert.ok(envelope.data.findings.some(({ id }) => id === 'fm-secrets-no-key-source'));
    assert.equal(result.stderr, '');
  }
});
