import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { main, addedBlocks, askLocal, isScoredPath, scoreCommit, VENDOR_CUT } from './vendor-shadow.mjs';

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

test('jev-517o: local verdict is logged beside Jev, Platt-mapped; a down server logs NOT_RUN and Jev row still lands', async () => {
  const { plattMap } = await import('./vendor-shadow.mjs');
  const previous = process.env.JEV_VENDOR_LOCAL_URL;
  process.env.JEV_VENDOR_LOCAL_URL = 'http://x';
  try {
    const diff = diffOf('work/pasted-lib/index.js', MIT_BLOCK.split('\n'));
    const ok = async () => ({ ok: true, json: async () => ({ answers: { vendored: { noul: 0.2 } } }) });
    const available = async () => ({ available: true });
    const rows = [];
    await scoreCommit({ commit: 'l1', diff, ask: noulAnswer(0.91), log: async (r) => rows.push(r), count: async () => 0, local: (code) => askLocal(code, 'http://x', ok, available) });
    const s = rows.find((r) => r.status === 'scored');
    assert.equal(s.noul, 0.91);
    assert.equal(s.local_status, 'scored');
    assert.equal(s.local_raw, 0.2);
    assert.ok(Math.abs(s.local_noul - plattMap(0.2)) < 1e-12);
    assert.ok(s.local_noul > 0.2, 'Platt b>0 lifts low raw scores (fitted on vendor dev)');
    const down = async () => { throw Object.assign(new Error('refused'), { name: 'TypeError' }); };
    const rows2 = [];
    const r = await scoreCommit({ commit: 'l2', diff, ask: noulAnswer(0.91), log: async (x) => rows2.push(x), count: async () => 0, local: (code) => askLocal(code, 'http://x', down, available) });
    assert.equal(r.scored, 1);
    const s2 = rows2.find((x) => x.status === 'scored');
    assert.equal(s2.noul, 0.91);
    assert.equal(s2.local_status, 'NOT_RUN');
  } finally {
    if (previous === undefined) delete process.env.JEV_VENDOR_LOCAL_URL;
    else process.env.JEV_VENDOR_LOCAL_URL = previous;
  }
});
test('local leg is disabled before fetch or guard when its opt-in URL is unset', async () => {
  const previous = process.env.JEV_VENDOR_LOCAL_URL;
  delete process.env.JEV_VENDOR_LOCAL_URL;
  let fetchCalls = 0;
  let guardCalls = 0;
  try {
    const result = await askLocal('code', undefined, async () => {
      fetchCalls += 1;
      throw new Error('fetch must not run');
    }, async () => {
      guardCalls += 1;
      return { available: true };
    });
    assert.equal(result.local_status, 'NOT_RUN');
    assert.equal(fetchCalls, 0);
    assert.equal(guardCalls, 0);
  } finally {
    if (previous === undefined) delete process.env.JEV_VENDOR_LOCAL_URL;
    else process.env.JEV_VENDOR_LOCAL_URL = previous;
  }
});

test('local guard timeout bounds the post-commit runner under two seconds', async () => {
  const scratch = await mkdtemp(join(process.cwd(), 'var/agent-tmp/jev-a5ny.'));
  await writeFile(join(scratch, '.owner'), `pid=${process.pid}\nlabel=jev-a5ny-test\nrepo=${process.cwd()}\ncreated=${new Date().toISOString()}\n`);
  const stub = join(scratch, 'localbench-sleeps.sh');
  await writeFile(stub, '#!/bin/sh\nexec /bin/sleep 30\n', { mode: 0o755 });

  const prior = {
    url: process.env.JEV_VENDOR_LOCAL_URL,
    bin: process.env.LOCALBENCH_BIN,
    hold: process.env.JEV_GPU_HOLD_FILE,
  };
  process.env.JEV_VENDOR_LOCAL_URL = 'http://127.0.0.1:8010/v1/systemone';
  process.env.LOCALBENCH_BIN = stub;
  process.env.JEV_GPU_HOLD_FILE = join(scratch, 'missing-hold-file');
  const rows = [];
  const diff = diffOf('work/pasted-lib/index.js', MIT_BLOCK.split('\n'));
  const git = (args) => {
    if (args.join(' ') === 'rev-parse HEAD') return 'commit-a5ny';
    if (args.join(' ') === 'rev-parse HEAD^') return 'parent-a5ny';
    if (args[0] === 'show') return diff;
    throw new Error(`unexpected git args: ${args.join(' ')}`);
  };
  const started = Date.now();
  try {
    const result = await main([], {
      ask: noulAnswer(0.91),
      git,
      log: async (row) => rows.push(row),
      count: async () => 0,
      local: (code) => askLocal(code, undefined, async () => {
        throw new Error('fetch must not run after guard timeout');
      }),
    });
    assert.equal(result, 0);
    assert.ok(Date.now() - started < 2000, `runner took ${Date.now() - started}ms`);
    const row = rows.find((x) => x.status === 'scored');
    assert.equal(row?.local_status, 'NOT_RUN');
  } finally {
    for (const [name, value] of Object.entries({
      JEV_VENDOR_LOCAL_URL: prior.url,
      LOCALBENCH_BIN: prior.bin,
      JEV_GPU_HOLD_FILE: prior.hold,
    })) {
      if (value === undefined) delete process.env[name];
      else process.env[name] = value;
    }
  }
});

test('slow local endpoint shares one two-second deadline across commit hunks', async () => {
  let requests = 0;
  const server = createServer((_req, res) => {
    requests += 1;
    const timer = setTimeout(() => {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ answers: { vendored: { noul: 0.2 } } }));
    }, 3000);
    res.once('close', () => clearTimeout(timer));
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const endpoint = `http://127.0.0.1:${server.address().port}/v1/systemone`;
  const previous = process.env.JEV_VENDOR_LOCAL_URL;
  process.env.JEV_VENDOR_LOCAL_URL = endpoint;
  const rows = [];
  const diff = [
    diffOf('work/pasted-lib/a.js', ['a', 'b', 'c']),
    diffOf('work/pasted-lib/b.js', ['d', 'e', 'f']),
  ].join('\n');
  const started = Date.now();
  try {
    await scoreCommit({
      commit: 'slow-local',
      diff,
      ask: noulAnswer(0.91),
      log: async (row) => rows.push(row),
      count: async () => 0,
      local: (code, deadline) => askLocal(
        code,
        endpoint,
        fetch,
        async () => ({ available: true }),
        deadline,
      ),
    });
    const elapsed = Date.now() - started;
    assert.ok(elapsed < 2500, `shared local leg took ${elapsed}ms`);
    assert.equal(requests, 1, 'expired shared deadline must skip the next hunk');
    assert.equal(rows.filter((row) => row.status === 'scored').length, 2);
    assert.equal(rows[0].local_status, 'NOT_RUN');
    assert.equal(rows[1].local_status, 'NOT_RUN');
  } finally {
    if (previous === undefined) delete process.env.JEV_VENDOR_LOCAL_URL;
    else process.env.JEV_VENDOR_LOCAL_URL = previous;
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close((err) => err ? reject(err) : resolve()));
  }
});
test('main shares its local deadline across hunks through the production askLocal adapter', async () => {
  const scratch = await mkdtemp(join(process.cwd(), 'var/agent-tmp/jev-a5ny-main.'));
  await writeFile(join(scratch, '.owner'), `pid=${process.pid}\nlabel=jev-a5ny-main-test\nrepo=${process.cwd()}\ncreated=${new Date().toISOString()}\n`);
  const localbench = join(scratch, 'localbench-free.sh');
  await writeFile(localbench, '#!/bin/sh\nprintf \'{"parked":[]}\\n\'\n', { mode: 0o755 });
  let requests = 0;
  const server = createServer((_req, res) => {
    requests += 1;
    const timer = setTimeout(() => {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ answers: { vendored: { noul: 0.2 } } }));
    }, 3000);
    res.once('close', () => clearTimeout(timer));
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const previous = {
    url: process.env.JEV_VENDOR_LOCAL_URL,
    bin: process.env.LOCALBENCH_BIN,
    hold: process.env.JEV_GPU_HOLD_FILE,
  };
  process.env.JEV_VENDOR_LOCAL_URL = `http://127.0.0.1:${server.address().port}/v1/systemone`;
  process.env.LOCALBENCH_BIN = localbench;
  process.env.JEV_GPU_HOLD_FILE = join(scratch, 'missing-hold-file');
  const rows = [];
  const diff = [
    diffOf('work/pasted-lib/a.js', ['a', 'b', 'c']),
    diffOf('work/pasted-lib/b.js', ['d', 'e', 'f']),
  ].join('\n');
  const git = (args) => {
    if (args.join(' ') === 'rev-parse HEAD') return 'commit-a5ny-main';
    if (args.join(' ') === 'rev-parse HEAD^') return 'parent-a5ny-main';
    if (args[0] === 'show') return diff;
    throw new Error(`unexpected git args: ${args.join(' ')}`);
  };
  const started = Date.now();
  try {
    await main([], {
      ask: noulAnswer(0.91),
      git,
      log: async (row) => rows.push(row),
      count: async () => 0,
    });
    const elapsed = Date.now() - started;
    assert.ok(elapsed < 2500, `production main local leg took ${elapsed}ms`);
    assert.equal(requests, 1, 'expired shared deadline must skip the next hunk');
    assert.equal(rows.filter((row) => row.status === 'scored').length, 2);
    assert.equal(rows[0].local_status, 'NOT_RUN');
    assert.equal(rows[1].local_status, 'NOT_RUN');
  } finally {
    for (const [name, value] of Object.entries({
      JEV_VENDOR_LOCAL_URL: previous.url,
      LOCALBENCH_BIN: previous.bin,
      JEV_GPU_HOLD_FILE: previous.hold,
    })) {
      if (value === undefined) delete process.env[name];
      else process.env[name] = value;
    }
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close((err) => err ? reject(err) : resolve()));
  }
});


test('local endpoint has no baked-in loopback default', async () => {
  const source = await readFile(new URL('./vendor-shadow.mjs', import.meta.url), 'utf8');
  assert.equal(source.includes('127.0.0.1:8010'), false);
});
