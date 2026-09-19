#!/usr/bin/env node
// Where does your agent spend actually go? Reads Claude Code / omp session JSONL and ranks the
// LEVERS by share of billed input, so you know which intervention could pay before you build one.
// Offline. No API key. No network. Read-only.
import { readdir, stat, open } from 'node:fs/promises';
import { join } from 'node:path';

function usage(msg) {
  if (msg) console.error(`ERROR ${msg}`);
  console.error('usage: node bin/shape.mjs <dir-or-file>... [--json]');
  console.error('');
  console.error('Ranks where your agent spend goes. Offline, no key, no network.');
  console.error('  node bin/shape.mjs ~/.claude/projects');
  process.exit(2);
}

const args = process.argv.slice(2);
const wantJson = args.includes('--json');
const roots = args.filter((a) => !a.startsWith('--'));
if (roots.length === 0) usage('at least one directory or .jsonl file is required');

async function* jsonlFiles(p) {
  const s = await stat(p).catch(() => null);
  if (!s) return;
  if (s.isFile()) { if (p.endsWith('.jsonl')) yield p; return; }
  for (const e of await readdir(p, { withFileTypes: true })) yield* jsonlFiles(join(p, e.name));
}

const t = { cacheRead: 0, cacheWrite: 0, input: 0, output: 0, unreconciled: 0, turns: 0, files: 0, sessions: 0, unparsable: 0, noUsage: 0 };
const byModel = new Map();
for (const root of roots) {
  for await (const f of jsonlFiles(root)) {
    t.files += 1;
    let sawTurn = false;
    const fh = await open(f, 'r');
    try {
      for await (const line of fh.readLines({ encoding: 'utf8' })) {
        if (!line.trim()) continue;
        let o;
        try { o = JSON.parse(line); } catch { t.unparsable += 1; continue; }
        const u = o?.message?.usage;
        if (!u) { t.noUsage += 1; continue; }
        const cr = u.cache_read_input_tokens ?? 0;
        const cw = u.cache_creation_input_tokens ?? 0;
        const inp = u.input_tokens ?? 0;
        const out = u.output_tokens ?? 0;
        t.cacheRead += cr; t.cacheWrite += cw; t.input += inp; t.output += out;
        const declaredTotal = u.total_tokens ?? u.totalTokens;
        if (declaredTotal !== undefined && declaredTotal !== null) t.unreconciled += Number(declaredTotal) - (cr + cw + inp + out);
        t.turns += 1; sawTurn = true;
        const m = o?.message?.model ?? 'unknown';
        const b = byModel.get(m) ?? { turns: 0, cacheRead: 0, output: 0 };
        b.turns += 1; b.cacheRead += cr; b.output += out; byModel.set(m, b);
      }
    } finally { await fh.close(); }
    if (sawTurn) t.sessions += 1;
  }
}

if (t.files === 0 || t.turns === 0) {
  const empty = { schema: 'jev.usage-shape.v1', generated_at: new Date().toISOString(), denominator: { sessions: t.sessions, turns: t.turns, files: t.files, unparsable_lines: t.unparsable, records_without_usage: t.noUsage }, failures: [{ code: 'EMPTY_SCAN_SET', message: 'no usage-bearing records found' }] };
  if (wantJson) console.log(JSON.stringify(empty, null, 2)); else console.error('ERROR EMPTY_SCAN_SET: no usage-bearing records found');
  process.exit(3);
}

const billedInput = t.cacheRead + t.cacheWrite + t.input;
const total = billedInput + t.output + t.unreconciled;
const pct = (n) => (total ? (n / total) * 100 : 0);
const levers = [
  ['retransmitted context (cache read)', t.cacheRead, 'fewer turns, or less parked in context'],
  ['context first-write (cache create)', t.cacheWrite, 'read less into context at all'],
  ['fresh input (uncached)', t.input, 'shorter prompts'],
  ['model output', t.output, 'ask for less output'],
  ['unreconciled residual', t.unreconciled, 'investigate provider accounting before pricing an intervention'],
].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

if (wantJson) {
  console.log(JSON.stringify({ schema: 'jev.usage-shape.v1', generated_at: new Date().toISOString(), denominator: { sessions: t.sessions, turns: t.turns, files: t.files, unparsable_lines: t.unparsable, records_without_usage: t.noUsage }, totals: { cacheRead: t.cacheRead, cacheWrite: t.cacheWrite, input: t.input, output: t.output, unreconciled: t.unreconciled, billedInput, total }, levers: levers.map(([name, v, fix]) => ({ lever: name, tokens: v, share_pct: +pct(v).toFixed(4), reduced_by: fix })), by_model: [...byModel].map(([model, b]) => ({ model, ...b })), no_claim: 'Token counts only. No prices, no dollar figures, and no claim any lever is worth intervening on.' }, null, 2));
  process.exit(0);
}

console.log('');
console.log('WHERE YOUR AGENT SPEND GOES');
console.log(`  ${t.sessions} sessions, ${t.turns} billed turns, ${t.files} files read`);
if (t.unparsable || t.noUsage) console.log(`  skipped: ${t.unparsable} unparsable lines, ${t.noUsage} records with no usage block`);
console.log('');
const width = 40;
for (const [name, v, fix] of levers) {
  const share = pct(v); const bar = '#'.repeat(Math.max(0, Math.round((share / 100) * width))).padEnd(width, '.');
  console.log(`  ${bar}  ${share.toFixed(1).padStart(5)}%  ${name}`);
  console.log(`  ${' '.repeat(width)}         reduce by: ${fix}`);
}
console.log('');
console.log(`  billed input ${billedInput} tokens, output ${t.output} tokens`);
console.log(`  mean retransmitted context per turn: ${t.turns ? Math.round(t.cacheRead / t.turns) : 0} tokens`);
console.log('');
console.log('  Token counts only. No prices here, and no claim that the top lever is worth');
console.log('  intervening on — that depends on what an intervention costs you.');
console.log('');
