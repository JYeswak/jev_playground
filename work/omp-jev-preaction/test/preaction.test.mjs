import test from 'node:test';
import assert from 'node:assert/strict';
import ompJevPreaction from '../src/index.ts';

function host() {
  const rows = [];
  let handler;
  return {
    rows,
    fire: (event) => handler(event),
    pi: { on: (_e, cb) => { handler = cb; }, appendEntry: async (t, d) => { rows.push({ t, d }); } },
  };
}
const decisions = (h) => h.rows.filter((r) => r.t.endsWith('decision.v1'));
const bash = (command) => ({ toolName: 'bash', toolCallId: 'tc-1', input: { command } });

test('fires on every pattern in the pre-registered policy', async () => {
  const cases = [
    ['rm -rf /', 'wipe-root'],
    ['rm -rf /*', 'wipe-star'],
    ['mkfs.ext4 /dev/sda1', 'mkfs'],
    ['dd if=/dev/zero of=/dev/sda', 'dd-device'],
    [':(){ :|:& };:', 'forkbomb'],
    ['chmod -R / 777', 'chmod-root'],
  ];
  for (const [command, expected] of cases) {
    const h = host();
    ompJevPreaction(h.pi);
    await h.fire(bash(command));
    const [row] = decisions(h);
    assert.equal(row.d.kind, 'preaction_fire', `${command} must fire`);
    assert.ok(row.d.hits.some((hit) => hit.id === expected), `${command} must hit ${expected}, got ${JSON.stringify(row.d.hits)}`);
  }
});

test('ordinary daily commands do not fire — the false-positive arm', async () => {
  const benign = [
    'git status',
    'rm -rf node_modules',            // destructive but scoped, and routine
    'npm test',
    'chmod +x scripts/build.sh',      // chmod, but not on /
    'dd if=input.img of=output.img',  // dd, but not to a device
    'echo "rm -rf /" >> notes.txt',   // mentions the string in a quoted echo
  ];
  for (const command of benign) {
    const h = host();
    ompJevPreaction(h.pi);
    await h.fire(bash(command));
    const [row] = decisions(h);
    assert.equal(row.d.kind, 'preaction_pass', `${command} must NOT fire`);
  }
});

test('non-bash tools are ignored entirely', async () => {
  const h = host();
  ompJevPreaction(h.pi);
  await h.fire({ toolName: 'read', toolCallId: 'x', input: { command: 'rm -rf /' } });
  assert.equal(decisions(h).length, 0);
});

test('a missing or non-string command never throws', async () => {
  const h = host();
  ompJevPreaction(h.pi);
  for (const event of [{ toolName: 'bash', input: {} }, { toolName: 'bash' }, {}]) {
    assert.equal(await h.fire(event), undefined);
  }
});

test('it observes only: no block, no throw, undefined on every path', async () => {
  const h = host();
  ompJevPreaction({ on: h.pi.on, appendEntry: async () => { throw new Error('sink down'); } });
  assert.equal(await h.fire(bash('rm -rf /')), undefined, 'a firing case still returns undefined');
});

test('the decision row names what matched, so a fire is always explainable', async () => {
  const h = host();
  ompJevPreaction(h.pi);
  await h.fire(bash('mkfs.ext4 /dev/sdb'));
  const [row] = decisions(h);
  assert.equal(row.d.command.includes('mkfs'), true);
  assert.equal(typeof row.d.hits[0].reason, 'string');
  assert.ok(row.d.hits[0].reason.length > 0);
});
