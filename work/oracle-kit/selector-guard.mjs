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
// `[cm]?`: the old `\.test\.[tj]s$` missed every `.test.mjs`, so 6 test-file reads were scanned (jev-7xjv).
const TEST_FILE = /\.test\.[cm]?[tj]s$|\/test\//;
// A trap name read off an omp tool's own result is that tool's declared field, not the SDK trap:
// jev_claim_check and jev_screen put `probability` in `details` (.omp/tools/jev-claim-check.ts:178,
// .omp/tools/jev-screen.ts:88). omp returns tool output as `<result>.details`, and the xd device
// wraps it as `<details>.xdev.inner`. A receiver passes only when its chain ENDS in one of those.
const DETAILS_END = /\.(details|xdev\.inner)$/;

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

// Block comments keep their newlines so a hit's line number matches the file.
function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, (c) => c.replace(/[^\n]/g, '')).replace(/(^|[^:])\/\/.*$/gm, '$1');
}

// Skips a quoted string or template literal starting at i; returns the index after it.
function skipString(src, i) {
  const q = src[i];
  for (let j = i + 1; j < src.length; j += 1) {
    if (src[j] === '\\') j += 1;
    else if (src[j] === q) return j + 1;
  }
  return src.length;
}

// The receiver chain that ends right before index i: `res?.details?` for `res?.details?.x`.
function chainBefore(src, i) {
  let j = i - 1;
  while (j >= 0) {
    const ch = src[j];
    if (/[\w$.?]/.test(ch)) { j -= 1; continue; }
    if (ch === ')' || ch === ']') {
      const open = ch === ')' ? '(' : '[';
      let depth = 0;
      for (; j >= 0; j -= 1) {
        if (src[j] === ch) depth += 1;
        else if (src[j] === open && --depth === 0) break;
      }
      j -= 1;
      continue;
    }
    break;
  }
  return src.slice(j + 1, i);
}

const normalizeChain = (chain) => chain.replace(/\?\./g, '.').replace(/\?$/, '').trim();

// Splits at a top-level `??` or `||`, outside brackets and strings.
function alternatives(expr) {
  const out = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < expr.length; i += 1) {
    const ch = expr[i];
    if (ch === '"' || ch === "'" || ch === '`') { i = skipString(expr, i) - 1; continue; }
    if ('([{'.includes(ch)) depth += 1;
    else if (')]}'.includes(ch)) depth -= 1;
    else if (depth === 0 && (expr.startsWith('??', i) || expr.startsWith('||', i))) {
      out.push(expr.slice(start, i));
      start = i + 2;
      i += 1;
    }
  }
  out.push(expr.slice(start));
  return out.map((a) => a.trim());
}

// True when an object literal declares `field` at its own top level: `{ a, field: x }` or `{ field }`.
function literalDeclares(literal, field) {
  let depth = 0;
  let flat = '';
  for (let i = 0; i < literal.length; i += 1) {
    const ch = literal[i];
    if (ch === '"' || ch === "'" || ch === '`') {
      const end = skipString(literal, i);
      flat += ' '.repeat(end - i);
      i = end - 1;
      continue;
    }
    if ('([{'.includes(ch)) depth += 1;
    flat += depth === 1 ? ch : ' ';
    if (')]}'.includes(ch)) depth -= 1;
  }
  return new RegExp(String.raw`[{,]\s*` + field + String.raw`\s*[:,}]`).test(flat);
}

// The right-hand side of every `const|let|var <name> =` in the file, up to `;`, `,` or a newline at depth 0.
function bindingsOf(src, name) {
  const out = [];
  const re = new RegExp(String.raw`\b(?:const|let|var)\s+` + name.replace(/\$/g, '\\$') + String.raw`\s*=(?!=)`, 'g');
  let m;
  while ((m = re.exec(src))) {
    let depth = 0;
    let i = m.index + m[0].length;
    const start = i;
    for (; i < src.length; i += 1) {
      const ch = src[i];
      if (ch === '"' || ch === "'" || ch === '`') { i = skipString(src, i) - 1; continue; }
      if ('([{'.includes(ch)) depth += 1;
      else if (')]}'.includes(ch)) depth -= 1;
      else if (depth === 0 && (ch === ';' || ch === ',' || ch === '\n')) break;
    }
    out.push(src.slice(start, i).trim());
  }
  return out;
}

// A receiver is a tool's own result when its chain ends in DETAILS_END, or it is a name whose
// EVERY binding in the file is such a chain, another such name, a literal declaring `field`, or
// the empty fallback `{}` / `null`. A parameter or destructured name has no binding and fails closed.
function toolOwned(src, receiver, field, seen = new Set()) {
  const chain = normalizeChain(receiver);
  if (DETAILS_END.test(chain)) return true;
  if (!/^[A-Za-z_$][\w$]*$/.test(chain) || seen.has(chain)) return false;
  const bound = bindingsOf(src, chain);
  if (bound.length === 0) return false;
  const next = new Set(seen).add(chain);
  return bound.every((expr) => {
    let owned = false;
    for (const alt of alternatives(expr)) {
      if (alt === '{}' || alt === 'null' || alt === 'undefined') continue;
      if (alt.startsWith('{') && alt.endsWith('}')) {
        if (!literalDeclares(alt, field)) return false;
        owned = true;
        continue;
      }
      if (!toolOwned(src, alt, field, next)) return false;
      owned = true;
    }
    return owned;
  });
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
    const field = m[1] || m[2];
    if (toolOwned(body, chainBefore(body, m.index), field)) continue;
    hits.push({ field, line: body.slice(0, m.index).split('\n').length, ctx });
  }
  return hits;
}

function scan(dir) {
  const files = walk(dir).filter((f) => !TEST_FILE.test(f.replaceAll('\\', '/')));
  const bad = [];
  for (const f of files) {
    if (f.endsWith('selector-guard.mjs')) continue;
    const hits = silentReaders(readFileSync(f, 'utf8'));
    for (const h of hits) bad.push({ file: `${relative(root, f)}:${h.line}`, ...h });
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
  const B = TRAP_B;
  // Real reads of a Jev answer: each must still be caught.
  const red = {
    'answer bound from answers': `const answer = body.answers.harm;\nexport const p = answer.${B};\n`,
    'answers chain': `export const p = res.answers.harm.${B};\n`,
    'details prefix, answer tail': `const d = r.details.answers.harm;\nexport const p = d.${B};\n`,
    'literal without the field': `const row = { noul: 1 };\nexport const p = row.${B};\n`,
    'parameter, no binding': `export function f(d) { return d.${B}; }\n`,
    'ternary with an answer arm': `const d = ok ? r.details : answer;\nexport const p = d.${B};\n`,
  };
  for (const [name, src] of Object.entries(red)) {
    if (silentReaders(src).length === 0) {
      console.error(`selector-guard --selftest FAIL: real read not caught (${name})`);
      return 2;
    }
  }
  // A tool's own details: each must pass.
  const green = {
    'details chains': `const d = r.details;\nexport const a = d.${B};\nexport const b = r.details.${B};\nexport const c = res?.details?.${B};\n`,
    'xdev inner of details': `const d = f.result?.details ?? {};\nconst inner = d.xdev?.inner ?? d;\nexport const p = inner.${B};\n`,
    'literal declaring the field': `const row = { a: 1, ${B}: p };\nexport const q = row.${B};\n`,
    'awaited execute details': `const d = (await t.execute(id, { x: 1 })).details;\nexport const p = d.${B};\n`,
  };
  for (const [name, src] of Object.entries(green)) {
    const got = silentReaders(src);
    if (got.length !== 0) {
      console.error(`selector-guard --selftest FAIL: tool details read flagged (${name}): ${got[0].ctx}`);
      return 2;
    }
  }
  if (!TEST_FILE.test('work/x/claim-check.test.mjs') || TEST_FILE.test('work/x/run.mjs')) {
    console.error('selector-guard --selftest FAIL: .test.mjs is not excluded, or a plain .mjs is');
    return 2;
  }
  console.log(
    `selector-guard --selftest: PASS (${1 + Object.keys(red).length} planted real reads caught; refusal string, ` +
      `${Object.keys(green).length} tool-details reads and .test.mjs ignored)`,
  );
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
