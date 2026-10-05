import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { classifyText, BANKING77_INSTRUCTIONS } from '../src/classify.ts';
import { PreflightError } from '../src/preflight.ts';

const labels = ['card arrival', 'cash withdrawal'];
const captured = {
  text: 'I still have not received my new card, I ordered over a week ago.',
  labels: ['card arrival', 'cash withdrawal'],
};

function answer(choice = 'card arrival') {
  return async () => ({
    ok: true,
    choice,
    confidence: 0.73,
    probabilities: { 'card arrival': 0.73, 'cash withdrawal': 0.27 },
    latencyMs: 4,
    model: 'jev-1.13.0',
  });
}

test('classify preserves the Banking77 question and passes confidence through', async () => {
  let seen;
  const result = await classifyText({
    text: captured.text,
    labels: captured.labels,
    ask: async (options) => {
      seen = options;
      return answer()();
    },
  });
  assert.equal(result.label, 'card arrival');
  assert.equal(result.confidence, 0.73);
  assert.equal(seen.instructions, BANKING77_INSTRUCTIONS);
  assert.deepEqual(seen.state, { customer_message: captured.text });
  assert.deepEqual(seen.classes, { 'card arrival': null, 'cash withdrawal': null });
});

test('classify refuses a label absent from the offered set', async () => {
  await assert.rejects(
    classifyText({ text: captured.text, labels, ask: answer('not offered') }),
    /unoffered label/,
  );
});

test('classify refuses an OVER request before asking Jev', async () => {
  let calls = 0;
  await assert.rejects(
    classifyText({
      text: 'x'.repeat(100_000),
      labels,
      ask: async () => {
        calls += 1;
        return answer()();
      },
    }),
    (error) => error instanceof PreflightError && error.code === 'size-over',
  );
  assert.equal(calls, 0);
});

test('classify refuses a malformed Jev answer', async () => {
  const fetchImpl = async () => ({
    ok: true,
    status: 200,
    headers: { get: () => 'application/json' },
    body: null,
    clone() { return this; },
    text: async () => JSON.stringify({
      answers: {
        choice: {
          type: 'choice',
          choice: 'card arrival',
          confidence: 0.9,
          probabilities: { 'card arrival': 0.2, 'cash withdrawal': 0.2 },
        },
      },
    }),
  });
  await assert.rejects(
    classifyText({ text: captured.text, labels, apiKey: 'fixture-key', fetchImpl }),
    /classify failed \(no-answers\)/,
  );
});

const cli = new URL('../bin/jev.mjs', import.meta.url);
const kitRoot = new URL('../..', import.meta.url);

function runCli(args) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [cli.pathname, ...args], {
      cwd: kitRoot,
      env: { ...process.env, TYPESAFE_API_KEY: undefined },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('CLI runs the captured Banking77 example with the keyless fake', async () => {
  const example = JSON.parse(await readFile(new URL('../examples/banking77-example.json', import.meta.url)));
  const labels = new URL('../examples/banking77-labels.json', import.meta.url).pathname;
  const result = await runCli(['classify', '--text', example.text, '--labels', labels, '--fake', '--robot']);
  assert.equal(result.code, 0, result.stderr);
  const body = JSON.parse(result.stdout);
  assert.equal(body.data.label, example.expected_label);
  assert.equal(body.meta.model, 'fake');
  assert.equal(body.data.confidence, 0.86);
});
