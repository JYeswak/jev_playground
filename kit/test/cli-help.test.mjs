import test from 'node:test';
import assert from 'node:assert/strict';
import { freshHome, runCli } from './cli-support.mjs';

const EXPECTED_HELP = `classifier — model-neutral decision CLI
Usage:
  classifier
  classifier <command> [options]
  classifier <command> --help

Commands:
  doctor                 Check local readiness
  ask choice|score|noul  Judge a typed question
  rerank                 Select a top candidate
  classify               Choose a label
  verify                 Check evidence for a claim
  score                  Rate text on a rubric
  gate                   Judge command risk
  omp install|uninstall  Manage project-scoped omp files

Global options:
  --json                 Emit command JSON (doctor keeps its raw report)
  --robot                Emit the versioned machine envelope
  --no-color             Disable styling
  -h, --help             Show help and exit
  --version              Print version and exit

Fixture option:
  --fake                 Use captured data; available on ask, rerank, classify, verify, score, and gate

Exit codes:
  0 success; 1 findings/NOT_RUN; 3 refused; 4 refused_unsafe
  5 retryable; 6 online_required; 64 usage; 66 no_input
  73 cannot_create; 74 I/O

Examples:
  classifier doctor --robot
  classifier ask choice --state kit/examples/state.json --question kit/examples/question.json --fake --robot
`;

test('bare invocation and every help spelling exit 0 with the pinned overview', async () => {
  const home = await freshHome('classifier-help');
  for (const args of [[], ['--help'], ['-h'], ['help']]) {
    const result = runCli(args, { home, env: { CI: 'true', TERM: 'dumb', NO_COLOR: '1' } });
    assert.equal(result.status, 0, `${args.join(' ')}: ${result.stderr}`);
    assert.equal(result.stdout, EXPECTED_HELP);
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
  for (const args of [['help', 'ask'], ['ask', '--help']]) {
    const result = runCli(args, { home });
    assert.equal(result.status, 0, result.stderr);
    assert.ok(result.stdout.includes('classifier ask choice|score|noul'), result.stdout);
    assert.ok(result.stdout.includes('Examples:'), result.stdout);
    assert.equal(result.stderr, '');
  }
});
