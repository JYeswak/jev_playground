import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// jev-6smc. A demo run with --live and no key measured nothing, so it must say NOT_RUN (or name the
// missing key) and exit 2: an exit 0 reads as success to any wrapper. The recorded lane of the same
// demo must still exit 0. Every demo whose source parses `--live` is covered, so a new demo is
// checked without editing this file. No network: with no key the client refuses before any call.
const DEMOS = join(dirname(fileURLToPath(import.meta.url)), '..');
const KEY_VARS = ['TYPESAFE_API_KEY', 'TYPE_SAFE_AI_KEY', 'JEV_API_KEY'];
const env = Object.fromEntries(Object.entries(process.env).filter(([k]) => !KEY_VARS.includes(k)));

const liveDemos = readdirSync(DEMOS, { withFileTypes: true })
  .filter((d) => d.isDirectory() && existsSync(join(DEMOS, d.name, 'demo.mjs')))
  .map((d) => d.name)
  .filter((name) => /argv\.includes\(["']--live["']\)/.test(readFileSync(join(DEMOS, name, 'demo.mjs'), 'utf8')))
  .sort();

// compact imports the fast-jev-compaction sibling, which ./scripts/bootstrap-compaction.sh builds.
const needsBootstrap = { compact: join(DEMOS, '..', 'fast-jev-compaction', 'dist', 'index.js') };

test('every demo with a --live lane is discovered', () => {
  assert.ok(liveDemos.length >= 17, `found ${liveDemos.length}: ${liveDemos.join(', ')}`);
});

for (const name of liveDemos) {
  const prereq = needsBootstrap[name];
  const skip = prereq && !existsSync(prereq) ? `needs ./scripts/bootstrap-compaction.sh (${prereq})` : false;
  test(`${name}: keyless --live refuses with exit 2; the recorded lane exits 0`, { skip }, () => {
    const demo = join(DEMOS, name, 'demo.mjs');
    const live = spawnSync(process.execPath, [demo, '--live'], { env, encoding: 'utf8', timeout: 30000 });
    const out = `${live.stdout}\n${live.stderr}`;
    assert.equal(live.status, 2, `${name} --live exited ${live.status}:\n${out.slice(-600)}`);
    assert.match(out, /NOT_RUN|unconfigured|TYPESAFE_API_KEY/, `${name} --live did not say why:\n${out.slice(-600)}`);
    const recorded = spawnSync(process.execPath, [demo], { env, encoding: 'utf8', timeout: 30000 });
    assert.equal(recorded.status, 0, `${name} recorded lane exited ${recorded.status}:\n${recorded.stderr.slice(-600)}`);
  });
}
