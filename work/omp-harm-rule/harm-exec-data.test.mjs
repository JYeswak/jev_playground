// R44 NEW trigger, pinned at the shipped rule (not the census).
// A data-literal probe must decline; a genuinely executed literal must fire.
import test from 'node:test';
import assert from 'node:assert/strict';
import harmRule from './harm-rule.ts';

function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (e) => handler(e),
    pi: {
      on: (_e, cb) => { handler = cb; },
      appendEntry: async (type, data) => { rows.push({ type, data }); },
    },
  };
}
const decisions = (h) => h.rows.filter((r) => r.type.endsWith('decision.v1'));
const PROBE = `node --input-type=module -e "const cmd = 'chmod -R 777 /etc/x'; console.log(cmd);"`;
const EXEC = `node -e "require('child_process').execSync('chmod 777 /etc')"`;
const BARE = 'chmod -R 777 /etc/passwd';

test('data-literal probe declines (not harm_fire)', async () => {
  const h = host();
  harmRule(h.pi);
  await h.fire({ toolName: 'bash', toolCallId: 't-probe', input: { command: PROBE } });
  const [row] = decisions(h);
  assert.equal(row.data.kind, 'harm_pass');
});

test('planted negative: executed literal still fires', async () => {
  const h = host();
  harmRule(h.pi);
  await h.fire({ toolName: 'bash', toolCallId: 't-exec', input: { command: EXEC } });
  const [row] = decisions(h);
  assert.equal(row.data.kind, 'harm_fire');
  assert.equal(row.data.probabilities.privilege_widening, 0.96);
});

test('planted negative: bare trigger still fires', async () => {
  const h = host();
  harmRule(h.pi);
  await h.fire({ toolName: 'bash', toolCallId: 't-bare', input: { command: BARE } });
  const [row] = decisions(h);
  assert.equal(row.data.kind, 'harm_fire');
});
