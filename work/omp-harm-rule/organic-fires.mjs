/**
 * §17 organic precision: score a large systematic sample of REAL allow commands
 * through the SHIPPED extension (never a reimplementation) and print EVERY fire
 * for hand adjudication. The 14 known fires are all self-generated probes; the
 * 0/500 sample had zero fires. This run supplies the denominator organic traffic
 * has lacked.
 *
 * Join: bridge allow rows -> message toolCall parts by toolCallId (same three-way
 * join as dcg-recall.mjs). Sample: every 10th joined allow, deterministic.
 * No network. No model. Read-only over session logs.
 *
 * Run: node work/omp-harm-rule/organic-fires.mjs
 */
import { execSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';

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

const want = [];
const files = [];
for (const f of glob) {
  let text;
  try { text = readFileSync(f, 'utf8'); } catch { continue; }
  if (!text.includes('omp-dcg-bridge')) continue;
  files.push(f);
  for (const line of text.split('\n')) {
    if (!line.startsWith('{') || !line.includes('omp-dcg-bridge')) continue;
    const row = readRow(line);
    if (row && row.data.kind === 'dcg_allow' && row.data.toolCallId) want.push([f, row.data.toolCallId]);
  }
}

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
      if (part && typeof part === 'object' && part.type === 'toolCall') {
        const a = part.arguments || part.input || {};
        cmds.set(part.id, { tool: part.name, command: a && typeof a === 'object' ? a.command : undefined });
      }
    }
  }
}

const allows = [];
for (const [f, tid] of want) {
  const c = cmds.get(tid);
  if (c && c.tool === 'bash' && typeof c.command === 'string') allows.push(c.command);
}
// Full census: every joined allow command (deterministic; no sampling ambiguity
// as logs grow — the every-10th slice shifted between runs).
const sample = allows;
async function fire(command) {
  const rows = [];
  const pi = { on: (ev, h) => { pi._h = h; }, appendEntry: async (t, d) => rows.push({ t, d }) };
  harmRule(pi);
  await pi._h({ toolName: 'bash', toolCallId: 'organic-probe', input: { command } });
  const dec = rows.find((r) => r.t.endsWith('decision.v1'));
  if (!dec) return { fired: false, score: 0 };
  return { fired: dec.d.kind === 'harm_fire', score: dec.d.score ?? 0 };
}

// The distinguisher lives INSIDE the shipped rule now (harm-rule.ts classify:
// stripQuotedPayload, then blankDataLiterals) — no filter here, so this census
// testifies about what ships. (An earlier revision filtered here; removed when
// the rule absorbed the mechanism.)
const fires = [];
let n = 0;
for (const cmd of sample) {
  n += 1;
  const r = await fire(cmd);
  if (!r.fired) continue;
  fires.push({ score: r.score, command: cmd });
}
console.log(`allow commands joined: ${allows.length} | scored: ${sample.length} | fires: ${fires.length}`);
console.log(`\nFIRES (all ${fires.length}, for hand adjudication):`);
for (const f of fires) console.log(`--- score=${f.score}\n${f.command.slice(0, 600)}`);
writeFileSync('/tmp/organic-fires-full.json', JSON.stringify(fires.map((f) => ({ score: f.score, command: f.command })), null, 1));
