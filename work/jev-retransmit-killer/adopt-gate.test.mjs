/**
 * Tests for the adopt gate.
 *
 * A gate nobody has seen fail is a decoration. Every test here is a PLANTED BAD
 * TREE: the gate is pointed at a temp repo where exactly one thing is wrong, and
 * the exit code is asserted. The happy path gets one test; the four ways the
 * doctrine can rot get the rest.
 *
 * Run: node --test work/jev-retransmit-killer/adopt-gate.test.mjs  (no API key)
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, cpSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { execFileSync } from 'node:child_process';

const GATE = 'work/jev-retransmit-killer/adopt-gate.mjs';

/** A temp repo that PASSES, so each test can break exactly one thing. */
function goodRepo() {
  const root = mkdtempSync(join(tmpdir(), 'rk-'));
  const write = (p, body) => {
    mkdirSync(dirname(join(root, p)), { recursive: true });
    writeFileSync(join(root, p), body);
  };
  write('docs/demos/upstream-repro/compaction-retention-oracle-20260919.md', 'it is 7–23× worse; retention oracle; threshold 0.5\n');
  write('docs/demos/upstream-repro/compaction-threshold-curve-20260919.md', 'retention need; threshold sweep\n');
  write('work/compaction-proof/fair-oracle.mjs', 'const SAVE_BAR = 0.50, LOSS_BAR = 0.10;\n');
  write('work/jev-retransmit-killer/ceiling-beat.mjs', '// harness\n');
  write('work/jev-retransmit-killer/FALSIFIER.md', '# falsifier\n');
  const omp = mkdtempSync(join(tmpdir(), 'rk-omp-'));
  mkdirSync(join(omp, 'profiles', 'x', 'agent', 'extensions'), { recursive: true });
  return { root, omp, write };
}

function run({ root, omp }) {
  try {
    const stdout = execFileSync('node', [GATE, '--json'], {
      encoding: 'utf8',
      env: { ...process.env, JEV_RK_REPO: root, JEV_RK_OMP_HOME: omp },
    });
    return { code: 0, out: JSON.parse(stdout) };
  } catch (error) {
    return { code: error.status, out: JSON.parse(error.stdout) };
  }
}

test('a clean tree passes with exit 0', () => {
  const r = run(goodRepo());
  assert.equal(r.code, 0);
  assert.equal(r.out.doctrineFailed, 0);
  assert.equal(r.out.installFound, false);
});

test('PLANTED: moving the preregistered bar is caught, not silently honoured', () => {
  // The cheapest way to turn REJECT into ADOPT is to lower the bar. It must be visible.
  const repo = goodRepo();
  repo.write('work/compaction-proof/fair-oracle.mjs', 'const SAVE_BAR = 0.20, LOSS_BAR = 0.40;\n');
  const r = run(repo);
  assert.equal(r.code, 2, 'doctrine drift must exit 2');
  const bar = r.out.checks.find((c) => c.name === 'preregistered bars unchanged');
  assert.equal(bar.ok, false);
  assert.match(bar.detail, /CHANGED/);
});

test('PLANTED: a receipt gutted of its finding is caught, not just its presence', () => {
  const repo = goodRepo();
  repo.write('docs/demos/upstream-repro/compaction-retention-oracle-20260919.md', 'compaction is great, ship it\n');
  const r = run(repo);
  assert.equal(r.code, 2);
  const rc = r.out.checks.find((c) => c.name.startsWith('receipt compaction-retention'));
  assert.equal(rc.ok, false);
  assert.match(rc.detail, /no longer contains/);
});

test('PLANTED: a missing receipt is caught', () => {
  const repo = goodRepo();
  const bare = mkdtempSync(join(tmpdir(), 'rk-bare-'));
  cpSync(join(repo.root, 'work'), join(bare, 'work'), { recursive: true });
  const r = run({ root: bare, omp: repo.omp });
  assert.equal(r.code, 2);
  assert.ok(r.out.checks.some((c) => c.name.startsWith('receipt') && /MISSING/.test(c.detail)));
});

test('PLANTED: an installed production compaction hook is caught and exits 1, not 2', () => {
  // Exit code carries meaning: 1 = a real install to remove, 2 = the evidence rotted.
  const repo = goodRepo();
  writeFileSync(join(repo.omp, 'profiles', 'x', 'agent', 'extensions', 'jev-compact.ts'), '// installed\n');
  const r = run(repo);
  assert.equal(r.code, 1, 'an install is exit 1');
  assert.equal(r.out.doctrineFailed, 0, 'the doctrine is intact; only the install is wrong');
  assert.equal(r.out.installFound, true);
});
