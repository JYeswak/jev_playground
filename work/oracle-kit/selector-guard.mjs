#!/usr/bin/env node
// Fail if a scorer *reads* the two SDK-SURFACE trap names as fields.
// Mentions in comments, tests, or throw-strings that refuse those names are allowed.
// Names are assembled at runtime so this file is not a self-hit (30-no-secrets lesson).
// ACCEPTANCE companion to node work/oracle-kit/test.mjs (the planted {noul} as probabilities throw).
import { readFileSync, readdirSync, statSync, writeFileSync, mkdtempSync } from 'node:fs';
import { join, relative } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const here = fileURLToPath(new URL('.', import.meta.url));
const root = join(here, '..', '..');

const TRAP_A = 'dis' + 'tribution';
const TRAP_B = 'prob' + 'ability';
const CODE = /\.(mjs|js|ts)$/;
const SKIP_DIR = new Set(['node_modules', '.git', 'dist', '.venv']);
const TEST_FILE = /\.test\.[tj]s$|\/test\//;

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP_DIR.has(name)) continue;
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (CODE.test(name)) out.push(p);
  }
  return out;
}

function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1');
}

function silentReaders(src) {
  const hits = [];
  const body = stripComments(src);
  const re = new RegExp(
    String.raw`(?:\.\s*(` + TRAP_A + '|' + TRAP_B + String.raw`)\b|\[["'](` + TRAP_A + '|' + TRAP_B + String.raw`)["']\])`,
    'g',
  );
  let m;
  while ((m = re.exec(body))) {
    const start = Math.max(0, m.index - 80);
    const ctx = body.slice(start, m.index + m[0].length + 40).replace(/\s+/g, ' ');
    if (/throw|there is no|FORBIDDEN|assertSdkSelector|refuses|not a field|not in the SDK|not accepted/i.test(ctx)) {
      continue;
    }
    hits.push({ field: m[1] || m[2], ctx });
  }
  return hits;
}

function scan(dir) {
  const files = walk(dir).filter((f) => !TEST_FILE.test(f.replaceAll('\\', '/')));
  const bad = [];
  for (const f of files) {
    if (f.endsWith('selector-guard.mjs')) continue;
    const hits = silentReaders(readFileSync(f, 'utf8'));
    for (const h of hits) bad.push({ file: relative(root, f), ...h });
  }
  return bad;
}

function selftest() {
  const dir = mkdtempSync(join(tmpdir(), 'selector-guard-'));
  const plant = join(dir, 'plant.mjs');
  writeFileSync(plant, `export const p = answer.${TRAP_A};\n`);
  const hits = silentReaders(readFileSync(plant, 'utf8'));
  if (hits.length === 0) {
    console.error('selector-guard --selftest FAIL: planted silent reader was not caught');
    return 2;
  }
  const clean = silentReaders(`throw new Error('there is no .${TRAP_A} in this SDK');\n`);
  if (clean.length !== 0) {
    console.error('selector-guard --selftest FAIL: refusal string counted as a reader');
    return 2;
  }
  console.log('selector-guard --selftest: PASS (planted silent reader caught; refusal string ignored)');
  return 0;
}

if (process.argv.includes('--selftest')) process.exit(selftest());

const targets = [join(root, 'work'), join(root, 'scripts')];
const bad = targets.flatMap(scan);
if (bad.length) {
  for (const h of bad) console.error(`SILENT_SELECTOR  ${h.file}  .${h.field}  ${h.ctx}`);
  process.exit(2);
}
console.log(`selector-guard: no silent .${TRAP_A} / .${TRAP_B} readers under work/ scripts/ (tests excluded)`);

const rg = spawnSync('rg', ['-n', String.raw`\.` + TRAP_A + String.raw`|\.` + TRAP_B + String.raw`\b`, 'work', 'docs/demos', '--glob', '!**/node_modules/**'], {
  cwd: root,
  encoding: 'utf8',
});
const lines = (rg.stdout || '').trim().split('\n').filter(Boolean);
console.log(`rg hunt (informational): ${lines.length} mention(s) — documentation of the trap is not a fail`);
process.exit(0);
