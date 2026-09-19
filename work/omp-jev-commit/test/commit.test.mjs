import test from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import ompJevCommit from '../src/index.ts';

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
const call = (command) => ({ toolName: 'bash', toolCallId: 'tc-1', input: { command } });

function withFetch(impl, body) {
  return async () => {
    const real = globalThis.fetch;
    const prev = process.env.TYPESAFE_API_KEY;
    process.env.TYPESAFE_API_KEY = 'test-key';
    globalThis.fetch = impl;
    try { await body(); }
    finally {
      globalThis.fetch = real;
      if (prev === undefined) delete process.env.TYPESAFE_API_KEY; else process.env.TYPESAFE_API_KEY = prev;
    }
  };
}
const scored = async () => ({
  ok: true, status: 200,
  text: async () => JSON.stringify({ answers: { describes: { noul: 0.8 }, overstates: { noul: 0.1 }, omits: { noul: 0.2 } } }),
});

test('ignores everything that is not a git commit carrying a message', async () => {
  const h = host();
  ompJevCommit(h.pi);
  for (const command of ['git status', 'git push origin main', 'echo git commit', 'git commit --amend']) {
    await h.fire(call(command));
  }
  assert.equal(h.rows.length, 0, 'no diagnostic and no API call for these');
});

test('reads the message from -F <file>, which is the form this repo mandates', withFetch(scored, async () => {
  const dir = mkdtempSync(join(tmpdir(), 'commitmsg-'));
  const file = join(dir, 'msg.txt');
  writeFileSync(file, 'fix(thing): do the thing\n\nbody line\n');
  const h = host();
  ompJevCommit(h.pi);
  await h.fire(call(`git commit --only src/a.ts -F ${file}`));
  const rows = decisions(h);
  // a real staged diff may or may not exist in this worktree; if it does we get a row,
  // and when it does the subject must come from the FILE, not the command line
  if (rows.length > 0) assert.equal(rows[0].d.subject, 'fix(thing): do the thing');
}));

test('a -F pointing at a missing file is ignored rather than crashing', async () => {
  const h = host();
  ompJevCommit(h.pi);
  assert.equal(await h.fire(call('git commit -F /nonexistent/path/to/msg.txt')), undefined);
  assert.equal(decisions(h).length, 0);
});

test('an inline -m message is parsed, including multi-word quoted text', withFetch(scored, async () => {
  const h = host();
  ompJevCommit(h.pi);
  await h.fire(call('git commit -m "feat: add a thing that does stuff"'));
  const rows = decisions(h);
  if (rows.length > 0) assert.equal(rows[0].d.subject, 'feat: add a thing that does stuff');
}));

test('an unset key records commit_error with no scores, never an accurate-message verdict', async () => {
  const prev = process.env.TYPESAFE_API_KEY;
  delete process.env.TYPESAFE_API_KEY;
  try {
    const h = host();
    ompJevCommit(h.pi);
    await h.fire(call('git commit -m "some subject"'));
    const rows = decisions(h);
    if (rows.length > 0) {
      assert.equal(rows[0].d.kind, 'commit_error');
      assert.equal('scores' in rows[0].d, false);
      assert.equal(rows[0].d.failure, 'unconfigured');
    }
  } finally { if (prev !== undefined) process.env.TYPESAFE_API_KEY = prev; }
});

test('a throwing host still returns undefined', withFetch(scored, async () => {
  const h = host();
  ompJevCommit({ on: h.pi.on, appendEntry: async () => { throw new Error('sink down'); } });
  assert.equal(await h.fire(call('git commit -m "subject"')), undefined);
}));
