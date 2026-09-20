/**
 * pipe-exit fire-rate measurement, independent re-derivation.
 *
 * Settles three numbers that all live in the tree and disagree:
 *   R51                     55.2% (43,185 / 78,242 distinct allow-commands)
 *   R51 parenthetical       18.4% ("conductor measured on a 4,000 subset")
 *   guard-fp-rate receipt   57%   (57 fires / 100 seeded sample)
 *
 * Two predicates are measured separately, because they are NOT the same:
 *   HOOK  — the shipped glob, `*"| head"*|*"| tail"*` (substring, space required)
 *   R51   — /\|\s*(head|tail)\b/ (also matches `|head`, no space)
 *
 * Also attributes every command to its session file's mtime, so "which
 * population was measured" is answerable rather than guessed at.
 *
 * DATA ONLY. Commands are read as text and never executed.
 * Run: node work/pipe-exit-reconciliation/measure.mjs
 */
import { execSync } from 'node:child_process';
import { readFileSync, statSync } from 'node:fs';

const HOOK = (c) => c.includes('| head') || c.includes('| tail');
const R51 = (c) => /\|\s*(head|tail)\b/.test(c);

const files = execSync(`find $HOME/.omp/profiles -path '*agent/sessions*' -name '*.jsonl'`, {
  encoding: 'utf8',
  maxBuffer: 64 * 1024 * 1024,
})
  .split('\n')
  .filter(Boolean);

function bridgeData(parsed) {
  const custom = parsed.customType;
  if (typeof custom === 'string') {
    if (!custom.includes('omp-dcg-bridge')) return undefined;
    return parsed.data && typeof parsed.data === 'object' ? parsed.data : undefined;
  }
  if (custom && typeof custom === 'object' && typeof custom.type === 'string') {
    if (!custom.type.includes('omp-dcg-bridge')) return undefined;
    return custom.data && typeof custom.data === 'object' ? custom.data : undefined;
  }
  return undefined;
}

/** id -> {verdict, file}; and id -> command, both scoped per file. */
const rows = []; // {file, mtime, command}
let allowRows = 0;
let joined = 0;

for (const file of files) {
  let text;
  try {
    text = readFileSync(file, 'utf8');
  } catch {
    continue;
  }
  if (!text.includes('omp-dcg-bridge')) continue;
  const mtime = statSync(file).mtime.toISOString();
  const allow = new Set();
  const cmds = new Map();
  for (const line of text.split('\n')) {
    if (!line.startsWith('{')) continue;
    let parsed;
    try {
      parsed = JSON.parse(line);
    } catch {
      continue;
    }
    if ('customType' in parsed) {
      const data = bridgeData(parsed);
      if (data && data.kind === 'dcg_allow') {
        allow.add(data.toolCallId);
        allowRows += 1;
      }
      continue;
    }
    if (parsed.type !== 'message') continue;
    const content = parsed.message && Array.isArray(parsed.message.content) ? parsed.message.content : [];
    for (const part of content) {
      if (!part || part.type !== 'toolCall') continue;
      const args = part.arguments || part.input || {};
      const command = args && typeof args === 'object' ? args.command : undefined;
      if (typeof command === 'string' && command.trim()) cmds.set(part.id, command);
    }
  }
  for (const id of allow) {
    const command = cmds.get(id);
    if (typeof command !== 'string') continue;
    joined += 1;
    rows.push({ file, mtime, command });
  }
}

rows.sort((a, b) => (a.mtime < b.mtime ? -1 : a.mtime > b.mtime ? 1 : 0));

const pct = (n, d) => (d === 0 ? 'n/a' : `${((100 * n) / d).toFixed(1)}%`);
const rate = (set, f) => {
  const fired = set.filter((r) => f(r.command)).length;
  return `${fired}/${set.length} = ${pct(fired, set.length)}`;
};

// deduped-distinct view, the population R51 used
const distinct = [...new Map(rows.map((r) => [r.command, r])).values()];

console.log('session files with bridge rows :', new Set(rows.map((r) => r.file)).size);
console.log('dcg_allow rows                 :', allowRows);
console.log('joined to a command string     :', joined);
console.log('distinct commands              :', distinct.length);
console.log('');
console.log('ALL OCCURRENCES  hook-glob :', rate(rows, HOOK));
console.log('ALL OCCURRENCES  R51-regex :', rate(rows, R51));
console.log('DISTINCT         hook-glob :', rate(distinct, HOOK));
console.log('DISTINCT         R51-regex :', rate(distinct, R51));
console.log('');
console.log('-- chronological quartiles of DISTINCT commands (R51-regex) --');
const q = Math.ceil(distinct.length / 4);
for (let i = 0; i < 4; i += 1) {
  const slice = distinct.slice(i * q, (i + 1) * q);
  if (slice.length === 0) continue;
  console.log(
    `Q${i + 1} ${slice[0].mtime.slice(0, 16)} .. ${slice[slice.length - 1].mtime.slice(0, 16)} : ${rate(slice, R51)}`,
  );
}
console.log('');
console.log('-- oldest 4,000 vs newest 4,000 DISTINCT (R51-regex) --');
console.log('oldest 4000 :', rate(distinct.slice(0, 4000), R51));
console.log('newest 4000 :', rate(distinct.slice(-4000), R51));
console.log('');
console.log('-- top 12 session files by distinct firing commands --');
const byFile = new Map();
for (const r of distinct) {
  const e = byFile.get(r.file) ?? { n: 0, fired: 0, mtime: r.mtime };
  e.n += 1;
  if (R51(r.command)) e.fired += 1;
  byFile.set(r.file, e);
}
[...byFile.entries()]
  .sort((a, b) => b[1].fired - a[1].fired)
  .slice(0, 12)
  .forEach(([file, e]) => {
    console.log(`${e.fired.toString().padStart(6)} / ${e.n.toString().padStart(6)} (${pct(e.fired, e.n).padStart(6)})  ${e.mtime.slice(0, 16)}  ${file.replace(process.env.HOME, '~')}`);
  });
