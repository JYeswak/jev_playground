/**
 * Recall of the shipped harm rule against REAL dcg blocks (not probes).
 *
 * Source and truth notes: see receipt. Scoring uses the SHIPPED extension via
 * dynamic import (plain-node static resolution refuses the .ts path that the
 * shipped verify-claim.mjs loads fine this way — same module, no copy).
 *
 * Run: node work/omp-jev-harm-rule/dcg-recall.mjs
 */
import { execSync } from 'node:child_process';
import { gradeQuestion } from '../jev-client/measure-kit.mjs';
const { default: harmRule } = await import(new URL('./harm-rule.ts', import.meta.url));

const glob = execSync(`find $HOME/.omp/profiles -path '*agent/sessions*' -name '*.jsonl'`,
  { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }).split('\n').filter(Boolean);

function readRow(line) {
  let parsed;
  try { parsed = JSON.parse(line); } catch { return undefined; }
  if (!parsed || typeof parsed !== 'object' || !('customType' in parsed)) return undefined;
  const custom = parsed.customType;
  if (typeof custom === 'string') {
    if (!custom.includes('omp-dcg-bridge')) return undefined;
    const data = parsed.data;
    if (!data || typeof data !== 'object') return undefined;
    return { type: custom, data };
  }
  if (custom && typeof custom === 'object' && typeof custom.type === 'string') {
    if (!custom.type.includes('omp-dcg-bridge')) return undefined;
    if (!custom.data || typeof custom.data !== 'object') return undefined;
    return { type: custom.type, data: { ...custom.data } };
  }
  return undefined;
}

const { readFileSync } = await import('node:fs');
let blockRows = 0, allowRows = 0;
const want = new Map(); // toolCallId -> kind (first verdict wins)
const files = [];
for (const f of glob) {
  let text;
  try { text = readFileSync(f, 'utf8'); } catch { continue; }
  if (!text.includes('omp-dcg-bridge')) continue;
  files.push(f);
  for (const line of text.split('\n')) {
    if (!line.startsWith('{') || !line.includes('omp-dcg-bridge')) continue;
    const row = readRow(line);
    if (!row) continue;
    const kind = row.data.kind;
    const tid = row.data.toolCallId;
    if (kind === 'dcg_block') { blockRows += 1; if (!want.has(tid)) want.set(tid, 'block'); }
    else if (kind === 'dcg_allow') { allowRows += 1; if (!want.has(tid)) want.set(tid, 'allow'); }
  }
}

// Join: toolCall parts by id, same-file pass over files that had bridge rows.
const cmds = new Map();
for (const f of files) {
  let text;
  try { text = readFileSync(f, 'utf8'); } catch { continue; }
  if (!text.includes('toolCall')) continue;
  for (const line of text.split('\n')) {
    if (!line.startsWith('{') || !line.includes('toolCall')) continue;
    let r;
    try { r = JSON.parse(line); } catch { continue; }
    if (r.type !== 'message') continue;
    const m = r.message || {};
    for (const part of m.content || []) {
      if (part && typeof part === 'object' && part.type === 'toolCall' && want.has(part.id)) {
        const a = part.arguments || part.input || {};
        cmds.set(part.id, { tool: part.name, command: a && typeof a === 'object' ? a.command : undefined });
      }
    }
  }
}

const blocks = [], allows = [];
for (const [tid, kind] of want) {
  const c = cmds.get(tid);
  if (!c) continue;
  (kind === 'block' ? blocks : allows).push({ id: tid, tool: c.tool, command: c.command });
}
// Deterministic FP sample: every 100th joined allow (spread across the whole corpus).
const allowSample = allows.filter((_, i) => i % 100 === 0).slice(0, 500);

async function fire(command) {
  const rows = [];
  const pi = { on: (ev, h) => { pi._h = h; }, appendEntry: async (t, d) => rows.push({ t, d }) };
  harmRule(pi);
  await pi._h({ toolName: 'bash', toolCallId: 'recall-probe', input: { command } });
  const dec = rows.find((r) => r.t.endsWith('decision.v1'));
  if (!dec) return { fired: false, score: 0, error: 'no-decision-row' };
  return { fired: dec.d.kind === 'harm_fire', score: dec.d.score ?? 0, kind: dec.d.kind };
}

const samples = [];
const misses = [];
for (const b of blocks) {
  if (b.tool !== 'bash' || typeof b.command !== 'string') { samples.push({ skip: b.id }); continue; }
  const r = await fire(b.command);
  samples.push({ score: r.score, truth: true });
  if (!r.fired) misses.push(b.command);
}
const fps = [];
const allowSamples = [];
for (const a of allowSample) {
  if (a.tool !== 'bash' || typeof a.command !== 'string') continue;
  const r = await fire(a.command);
  allowSamples.push({ score: r.score, truth: false });
  if (r.fired) fps.push(a.command);
}

const recall = samples.length ? (samples.length - misses.length) / samples.length : NaN;
console.log(`bridge rows scanned: block=${blockRows} allow=${allowRows} (files with bridge rows: ${files.length})`);
console.log(`joined with command text: block=${blocks.length}/${blockRows} allow-sample=${allowSample.length}`);
console.log(`RECALL vs real dcg blocks: ${samples.length - misses.length}/${samples.length} = ${Number.isNaN(recall) ? 'n/a' : recall.toFixed(3)}`);
console.log(`\nMISSES (blocked by dcg, silent under harm-rule), all ${misses.length}:`);
for (const m of misses) console.log(`  - ${JSON.stringify(m.slice(0, 300))}`);
console.log(`\nFP CANDIDATES (dcg_allow, harm_rule fires), ${fps.length}/${allowSample.length} sampled:`);
for (const f of fps.slice(0, 20)) console.log(`  - ${JSON.stringify(f.slice(0, 300))}`);

const g = gradeQuestion([
  ...samples.filter((s) => !s.skip).map((s) => ({ score: s.score, truth: true })),
  ...allowSamples.map((s) => ({ score: s.score, truth: false })),
]);
console.log(`\nkit verdict on block+allow sample: ${g.correct}/${g.asked} | yes ${g.yes}/${g.asked} | best-const ${g.best}/${g.asked} | near ${g.near} | ${g.verdict}`);
