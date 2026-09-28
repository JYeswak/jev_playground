import test from 'node:test';
import assert from 'node:assert/strict';
import { makeInjectionShadowHandler } from './jev-injection-shadow.ts';
import { spawnSync } from 'node:child_process';

test('detached worker refuses an unadmitted job before reading state or acquiring credentials', () => {
  const result = spawnSync(process.execPath, ['--experimental-strip-types', '.omp/hooks/jev-shadow-worker.ts'], {
    cwd: process.cwd(),
    input: JSON.stringify({ kind: 'injection', text: 'PRIVATE_WORKER_STATE_7d03', path: '/nonexistent/jev-row.jsonl', row: {} }),
    env: { ...process.env, TYPESAFE_API_KEY: 'synthetic-never-send' },
    encoding: 'utf8',
    timeout: 10_000,
  });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /permission-required/);
  assert.doesNotMatch(result.stdout + result.stderr, /PRIVATE_WORKER_STATE_7d03|synthetic-never-send/);
});

test('injection shadow cap row is hash-only and fail-open', async () => {
  const rows = [];
  const handler = makeInjectionShadowHandler({ cap: 0, append: async (_path, line) => rows.push(JSON.parse(line)), now: () => '2026-09-27T00:00:00.000Z' });
  await handler({ toolName: 'bash', toolCallId: 'x', content: [{ type: 'text', text: 'secret command output' }] });
  assert.equal(rows[0].status, 'cap');
  assert.equal(rows[0].outputSha256.length, 64);
  assert.equal(JSON.stringify(rows[0]).includes('secret command output'), false);
});

test('unapproved injection callback records a hash-only refusal and leaves the tool result unchanged', async () => {
  const rows = [];
  const handler = makeInjectionShadowHandler({ append: async (_path, line) => rows.push(JSON.parse(line)), now: () => '2026-09-27T00:00:00.000Z' });
  const result = await handler({ toolName: 'bash', toolCallId: 'unapproved', content: [{ type: 'text', text: 'private tool output' }] });
  assert.equal(result, undefined);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].status, 'not-run');
  assert.equal(rows[0].reason, 'recipient-and-data-class-approval-required');
  assert.match(rows[0].outputSha256, /^[0-9a-f]{64}$/);
  assert.doesNotMatch(JSON.stringify(rows[0]), /private tool output/);
});

test('injection shadow ignores failed tool results', async () => {
  const rows = [];
  const handler = makeInjectionShadowHandler({ cap: 1, append: async (_path, line) => rows.push(JSON.parse(line)) });
  await handler({ toolName: 'bash', isError: true, content: [{ type: 'text', text: 'failed output' }] });
  assert.equal(rows.length, 0);
});
