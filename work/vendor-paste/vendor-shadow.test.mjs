import test from 'node:test';
import assert from 'node:assert/strict';
import { addedBlocks, isScoredPath, scoreCommit, VENDOR_CUT } from './vendor-shadow.mjs';

const MIT_BLOCK = `/*
Copyright (c) 2024 Example Corp. All rights reserved.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0
*/`;
const OWN_CODE = `export function decideVendor(noul) {
  return Number.isFinite(noul) && noul >= VENDOR_CUT;
}`;

const diffOf = (file, lines) =>
  `+++ b/${file}\n@@ -0,0 +1,${lines.length} @@\n` + lines.map((l) => `+${l}`).join('\n');

const noulAnswer = (noul) => async () => ({
  ok: true, scores: { vendored: noul }, latencyMs: 300, model: 'jev-1.13.0',
  usage: { input_tokens: 500, output_tokens: 20 },
});

test('addedBlocks splits per file, skips vendored/dep/non-source paths, needs 3 added lines', () => {
  const diff = [
    diffOf('upstream/acme/lib.js', ['a', 'b', 'c', 'd']),
    diffOf('kit/src/mine.ts', ['x', 'y']),
    diffOf('work/x/node_modules/dep/index.js', ['a', 'b', 'c', 'd']),
    diffOf('kit/src/real.ts', ['l1', 'l2', 'l3', 'l4', 'l5']),
    diffOf('.gitignore', ['a', 'b', 'c']),
    diffOf('docs/guide.txt', ['a', 'b', 'c']),
    diffOf('bun.lock', ['a', 'b', 'c']),
  ].join('\n');
  const { scored, skipped } = addedBlocks(diff);
  assert.deepEqual(scored.map((b) => b.file), ['kit/src/real.ts']);
  assert.deepEqual(new Map(skipped.map((s) => [s.file, s.reason])), new Map([
    ['upstream/acme/lib.js', 'excluded-path'],
    ['work/x/node_modules/dep/index.js', 'excluded-path'],
    ['.gitignore', 'dotfile'],
    ['docs/guide.txt', 'non-source-extension'],
    ['bun.lock', 'lockfile'],
  ]));
  assert.equal(isScoredPath('upstream/acme/lib.js'), false);
  assert.equal(isScoredPath('work/x/node_modules/dep/index.js'), false);
  assert.equal(isScoredPath('kit/src/real.ts'), true);
  assert.equal(isScoredPath('kit/src/real.md'), false);
});

test('.gitignore and .txt are skipped without a call; pasted MIT .js is scored', async () => {
  const rows = [];
  let asked = 0;
  const diff = [diffOf('.gitignore', ['a', 'b', 'c']), diffOf('notes.txt', ['a', 'b', 'c']), diffOf('lib/pasted.js', MIT_BLOCK.split('\n'))].join('\n');
  const r = await scoreCommit({ commit: 's1', diff, ask: async (o) => { asked += 1; return noulAnswer(0.91)(o); }, log: async (row) => rows.push(row), count: async () => 0 });
  assert.equal(asked, 1);
  assert.equal(r.scored, 1);
  assert.deepEqual(rows.filter((x) => x.status === 'skipped').map((x) => [x.file, x.reason]), [['.gitignore', 'dotfile'], ['notes.txt', 'non-source-extension']]);
  assert.equal(rows.find((x) => x.file === 'lib/pasted.js').would_flag, true);
});

test('planted MIT block is flagged, own code is not; rows carry commit/file/hash', async () => {
  const rows = [];
  const diff = [diffOf('work/pasted-lib/index.js', MIT_BLOCK.split('\n')), diffOf('kit/src/mine.ts', OWN_CODE.split('\n'))].join('\n');
  const ask = async (o) => {
    const code = o.state.code;
    return noulAnswer(code.includes('Apache License') ? 0.91 : 0.07)(o);
  };
  const r = await scoreCommit({ commit: 'abc123', diff, ask, log: async (row) => rows.push(row), count: async () => 0 });
  assert.equal(r.scored, 2);
  const flagged = rows.find((x) => x.file === 'work/pasted-lib/index.js');
  const allowed = rows.find((x) => x.file === 'kit/src/mine.ts');
  assert.equal(flagged.status, 'scored');
  assert.equal(flagged.would_flag, true);
  assert.equal(flagged.noul, 0.91);
  assert.equal(flagged.commit, 'abc123');
  assert.equal(typeof flagged.hunk_sha, 'string');
  assert.equal(allowed.would_flag, false);
});

test('refused asker and cap both log fail-open rows and never throw', async () => {
  const rows = [];
  const diff = diffOf('kit/src/a.ts', ['a', 'b', 'c']);
  const dead = async () => ({ ok: false, reason: 'unconfigured', latencyMs: 0, model: 'jev-1.13.0' });
  const r1 = await scoreCommit({ commit: 'c1', diff, ask: dead, log: async (row) => rows.push(row), count: async () => 0 });
  assert.equal(r1.scored, 0);
  assert.match(rows[0].status, /fail_open/);
  const rows2 = [];
  let asked = 0;
  await scoreCommit({ commit: 'c2', diff, ask: async (o) => { asked += 1; return noulAnswer(0.99)(o); }, log: async (row) => rows2.push(row), count: async () => 100 });
  assert.equal(asked, 0);
  assert.equal(rows2[0].reason, 'cap');
});

test('cut 0.35 is the frozen 30hi operating point', () => {
  assert.equal(VENDOR_CUT, 0.35);
});
