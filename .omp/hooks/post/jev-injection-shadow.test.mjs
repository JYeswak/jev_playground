import test from 'node:test';
import assert from 'node:assert/strict';
import { makeInjectionShadowHandler } from './jev-injection-shadow.ts';

test('injection shadow cap row is hash-only and fail-open', async () => {
  const rows = [];
  const handler = makeInjectionShadowHandler({ cap: 0, append: async (_path, line) => rows.push(JSON.parse(line)), now: () => '2026-09-27T00:00:00.000Z' });
  await handler({ toolName: 'bash', toolCallId: 'x', content: [{ type: 'text', text: 'secret command output' }] });
  assert.equal(rows[0].status, 'cap');
  assert.equal(rows[0].outputSha256.length, 64);
  assert.equal(JSON.stringify(rows[0]).includes('secret command output'), false);
});

test('injection shadow ignores failed tool results', async () => {
  const rows = [];
  const handler = makeInjectionShadowHandler({ cap: 1, append: async (_path, line) => rows.push(JSON.parse(line)) });
  await handler({ toolName: 'bash', isError: true, content: [{ type: 'text', text: 'failed output' }] });
  assert.equal(rows.length, 0);
});
