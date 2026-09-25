import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const root = new URL('../..', import.meta.url);
const cli = new URL('../bin/jev.mjs', import.meta.url);

function runCli(args, env = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [cli.pathname, ...args], {
      cwd: root,
      env: { ...process.env, TYPESAFE_API_KEY: undefined, ...env },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('doctor --robot is explicit NOT_RUN without a key', async () => {
  const result = await runCli(['doctor', '--robot']);
  assert.equal(result.code, 2);
  const body = JSON.parse(result.stdout);
  assert.equal(body.status, 'NOT_RUN');
  assert.equal(body.reason, 'no key');
  assert.equal(body.model, 'jev-1.13.0');
  assert.equal(body.omp.repo, process.cwd());
  assert.equal(body.omp.tools.length, 4);
  assert.equal(body.omp.hooks.length, 1);
});

test('ask --fake produces an offline typed decision', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'jev-kit-cli-'));
  const state = join(directory, 'state.json');
  const question = join(directory, 'question.json');
  await writeFile(state, JSON.stringify({ task: 'captured' }));
  await writeFile(question, JSON.stringify({ instructions: 'Which candidate?', criteria: { c0: 'Candidate 1', c1: 'Candidate 2', none: 'Abstain' } }));
  const result = await runCli(['ask', 'choice', '--state', state, '--question', question, '--fake', '--robot']);
  assert.equal(result.code, 0);
  const body = JSON.parse(result.stdout);
  assert.equal(body.ok, true);
  assert.equal(body.model, 'jev-1.13.0');
});

test('invalid command is a robot error, not a successful empty result', async () => {
  const result = await runCli(['ask', 'choice', '--robot']);
  assert.equal(result.code, 1);
  assert.equal(JSON.parse(result.stdout).reason, 'usage');
});
