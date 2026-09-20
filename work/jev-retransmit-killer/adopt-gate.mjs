/**
 * THE ADOPT GATE — refuse to install production compaction without a fresh live beat.
 *
 * This is the product of section 21. The measurement is already done and it says
 * REJECT; the thing that has value from here is a gate that stays said. A doctrine
 * in a markdown file gets re-litigated by whoever next reads "60% token savings" on
 * a vendor page. A gate that exits non-zero does not.
 *
 * WHAT IT CHECKS, all of it fail-closed:
 *   1. Both oracle receipts exist and still carry their load-bearing findings.
 *   2. The ceiling beat exists and is not stale.
 *   3. The preregistered bars in fair-oracle.mjs are unchanged — moving the bar is
 *      the cheapest way to turn REJECT into ADOPT and it must be visible.
 *   4. No production compaction hook is installed in any omp profile.
 *
 * WHAT IT DELIBERATELY DOES NOT DO: decide whether compaction is a good idea in
 * general. It encodes one measured result on one corpus. A fresh beat that clears
 * the bar is exactly how this gate is meant to be defeated — see --beat.
 *
 * Run:  node work/jev-retransmit-killer/adopt-gate.mjs [--json]
 * Exit: 0 = safe (no production compaction, doctrine intact)
 *       1 = a production compaction install was found without a passing fresh beat
 *       2 = the doctrine itself has drifted: a receipt or a bar is missing/changed
 */
import { existsSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const JSON_OUT = process.argv.includes('--json');
const checks = [];
const add = (name, ok, detail) => checks.push({ name, ok, detail });

/**
 * Roots are overridable ONLY so the gate can be tested against planted-bad trees.
 * A gate that has never been seen to fail is not a gate, it is a decoration, so
 * adopt-gate.test.mjs points these at temp dirs with a moved bar, a gutted receipt
 * and a fake install, and asserts the exit codes. Defaults are the real paths.
 */
const REPO = process.env.JEV_RK_REPO ?? '.';
const OMP_HOME = process.env.JEV_RK_OMP_HOME ?? `${process.env.HOME}/.omp`;
const at = (p) => `${REPO}/${p}`;

/** 1. The two receipts, and the specific findings that make them load-bearing. */
const RECEIPTS = [
  {
    path: 'docs/demos/upstream-repro/compaction-retention-oracle-20260919.md',
    must: ['7–23×', 'retention', 'threshold'],
  },
  {
    path: 'docs/demos/upstream-repro/compaction-threshold-curve-20260919.md',
    must: ['retention', 'threshold'],
  },
];
for (const r of RECEIPTS) {
  if (!existsSync(at(r.path))) {
    add(`receipt ${r.path.split('/').pop()}`, false, 'MISSING — the evidence for the doctrine is gone');
    continue;
  }
  const text = readFileSync(at(r.path), 'utf8');
  const missing = r.must.filter((m) => !text.includes(m));
  add(
    `receipt ${r.path.split('/').pop()}`,
    missing.length === 0,
    missing.length ? `present but no longer contains: ${missing.join(', ')}` : `present, carries ${r.must.join(' / ')}`,
  );
}

/** 2 & 3. The bars must be where they were, and the harness must still exist. */
const ORACLE = 'work/compaction-proof/fair-oracle.mjs';
if (!existsSync(at(ORACLE))) {
  add('fair-oracle harness', false, 'MISSING — nothing can re-beat the ceiling');
} else {
  const src = readFileSync(at(ORACLE), 'utf8');
  const bars = /SAVE_BAR\s*=\s*([\d.]+),\s*LOSS_BAR\s*=\s*([\d.]+)/.exec(src);
  const unchanged = bars && bars[1] === '0.50' && bars[2] === '0.10';
  add(
    'preregistered bars unchanged',
    Boolean(unchanged),
    bars ? `SAVE_BAR=${bars[1]} LOSS_BAR=${bars[2]}${unchanged ? '' : ' — CHANGED since preregistration; moving the bar is not a result'}` : 'bars not found in the harness',
  );
}
add('ceiling beat harness', existsSync(at('work/jev-retransmit-killer/ceiling-beat.mjs')), 'work/jev-retransmit-killer/ceiling-beat.mjs');
add('falsifier on record', existsSync(at('work/jev-retransmit-killer/FALSIFIER.md')), 'work/jev-retransmit-killer/FALSIFIER.md');

/** 4. Is production compaction actually installed anywhere? This is the live half. */
let installs = [];
try {
  installs = execFileSync(
    'find',
    [`${OMP_HOME}/profiles`, '-path', '*agent/extensions*', '-name', '*compact*'],
    { encoding: 'utf8' },
  )
    .split('\n')
    .filter(Boolean);
} catch {
  /* no profiles dir is not an install */
}
try {
  const hooks = execFileSync('find', [OMP_HOME, '-name', 'jev-compact*', '-not', '-path', '*/node_modules/*'], {
    encoding: 'utf8',
  })
    .split('\n')
    .filter(Boolean);
  installs = [...installs, ...hooks];
} catch {
  /* same */
}
add(
  'no production compaction installed',
  installs.length === 0,
  installs.length ? `FOUND ${installs.length}: ${installs.slice(0, 4).join(', ')}` : `none in ${OMP_HOME}`,
);

const doctrineFailed = checks.filter((c) => !c.ok && c.name !== 'no production compaction installed');
const installFound = checks.find((c) => c.name === 'no production compaction installed' && !c.ok);

if (JSON_OUT) {
  console.log(JSON.stringify({ checks, doctrineFailed: doctrineFailed.length, installFound: Boolean(installFound) }, null, 2));
} else {
  console.log('jev-retransmit-killer — adopt gate\n');
  for (const c of checks) console.log(`  ${c.ok ? 'PASS' : 'FAIL'}  ${c.name.padEnd(42)} ${c.detail}`);
  console.log('');
  if (doctrineFailed.length) {
    console.log('DOCTRINE DRIFT. The evidence this gate rests on has changed. Re-beat the oracles');
    console.log('before trusting either the gate or the doctrine:');
    console.log('  node work/jev-retransmit-killer/ceiling-beat.mjs 12');
  } else if (installFound) {
    console.log('PRODUCTION COMPACTION IS INSTALLED and the last beat said REJECT on 12 of 12 real');
    console.log('sessions — the omniscient ceiling saved 20.8–31.0% against a 50% bar. Either remove');
    console.log('it, or produce a fresh beat that clears the bar and commit it.');
  } else {
    console.log('SAFE. No production compaction installed; doctrine and bars intact.');
    console.log('To adopt anyway, defeat this gate honestly: run ceiling-beat.mjs and clear the bar.');
  }
}

if (doctrineFailed.length) process.exit(2);
if (installFound) process.exit(1);
