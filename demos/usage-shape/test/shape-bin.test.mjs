import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const bin = new URL('../bin/shape.mjs', import.meta.url).pathname;
async function run(args) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [bin, ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = ''; let stderr = '';
    child.stdout.on('data', (data) => { stdout += data; });
    child.stderr.on('data', (data) => { stderr += data; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('directory input walks JSONL and reports exact denominator/share/residual', async () => {
  const root = await mkdtemp(join(tmpdir(), 'shape-bin-'));
  await writeFile(join(root, 'a.jsonl'), [
    JSON.stringify({ type: 'session', id: 's' }),
    JSON.stringify({ type: 'message', message: { role: 'assistant', model: 'm', usage: { cache_read_input_tokens: 100, cache_creation_input_tokens: 20, input_tokens: 10, output_tokens: 5, total_tokens: 150 } } }),
    JSON.stringify({ type: 'message', message: { role: 'user', content: [] } }),
  ].join('\n') + '\n');
  const result = await run([root, '--json']);
  assert.equal(result.code, 0, result.stderr);
  const receipt = JSON.parse(result.stdout);
  assert.deepEqual(receipt.denominator, { sessions: 1, turns: 1, files: 1, unparsable_lines: 0, records_without_usage: 2 });
  assert.equal(receipt.totals.cacheRead, 100);
  assert.equal(receipt.totals.unreconciled, 15);
  assert.equal(receipt.levers[0].share_pct, 66.6667);
});

test('empty directory fails closed instead of emitting a green empty result', async () => {
  const root = await mkdtemp(join(tmpdir(), 'shape-empty-'));
  const result = await run([root, '--json']);
  assert.equal(result.code, 3);
  assert.match(result.stdout, /EMPTY_SCAN_SET/);
});
