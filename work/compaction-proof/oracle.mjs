// Does Jev's keep/drop survive contact with what the agent ACTUALLY needed next?
// Live decisions (not replayed), scored against the transcript's own future, vs 4 baselines.
import { readFileSync } from 'node:fs';
import { askJevBundle } from '../../kit/src/client.ts';
import { auc as kitAuc, field } from '../oracle-kit/index.mjs';

const WINDOW = 6;              // messages always pinned, matching the upstream default
const file = process.argv[2];
const rows = readFileSync(file, 'utf8').split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);

// Pair tool calls with their results using omp's own schema:
//   call   -> message.content[] part { type:'toolCall', id, name, arguments }
//   result -> a whole message with role:'toolResult', toolCallId, content[]
const calls = [];
const byId = new Map();
for (const [i, r] of rows.entries()) {
  const m = r.message;
  if (!m) continue;
  if (m.role === 'toolResult') {
    const txt = (m.content ?? []).map(p => p?.text ?? (typeof p === 'string' ? p : JSON.stringify(p ?? ''))).join('\n');
    const hit = byId.get(m.toolCallId);
    if (hit) { hit.result = txt.slice(0, 4000); hit.resultIdx = i; }
    continue;
  }
  for (const c of (m.content ?? [])) {
    if (c?.type === 'toolCall') {
      const rec = { idx: i, id: c.id, name: c.name, input: JSON.stringify(c.arguments ?? {}).slice(0, 400), result: null, resultIdx: i };
      calls.push(rec); byId.set(c.id, rec);
    }
  }
}

let scored = calls.filter(c => c.result && c.idx < rows.length - WINDOW);
// Cap the sample: a deterministic evenly-spaced draw, so cost stays bounded and the draw is
// reproducible. Reported as n, never as the whole session.
const CAP = Number(process.env.CAP ?? 120);
if (scored.length > CAP) {
  const step = scored.length / CAP;
  scored = Array.from({ length: CAP }, (_, k) => scored[Math.floor(k * step)]);
}
if (scored.length < 5) { console.log(`SKIP ${file}: only ${scored.length} eligible calls`); process.exit(0); }

// ORACLE: a call "was needed" if NOVEL tokens from its result reappear LATER in the transcript.
// Implemented with a token -> last-occurrence-row map and a token -> first-occurrence-row map:
// linear in time and memory. (Concatenating suffix strings is quadratic and OOMs a 14k-line file.)
const TOK = /[a-z][a-z0-9_./-]{5,}/g;
const firstSeen = new Map(), lastSeen = new Map();
for (let i = 0; i < rows.length; i++) {
  const s = JSON.stringify(rows[i].message ?? rows[i]).toLowerCase();
  for (const t of (s.match(TOK) ?? [])) {
    if (!firstSeen.has(t)) firstSeen.set(t, i);
    lastSeen.set(t, i);
  }
}
const STOP = new Set('the a an and or of to in is it for with on at by from this that not you your we as be are was'.split(' '));
const needed = scored.map(c => {
  const toks = [...new Set((c.result.toLowerCase().match(TOK) ?? []))].filter(t => !STOP.has(t));
  if (!toks.length) return false;
  // novel = first appears at or after this call, i.e. the result introduced it
  const novel = toks.filter(t => (firstSeen.get(t) ?? 0) >= c.idx);
  const probe = (novel.length ? novel : toks).slice(0, 60);
  return probe.some(t => (lastSeen.get(t) ?? -1) > c.resultIdx);
});

// LIVE Jev decisions, one call per tool call, batched.
if (!process.env.TYPESAFE_API_KEY) {
  console.error('unconfigured: TYPESAFE_API_KEY is not set — no network call made');
  process.exit(2);
}
const jev = [];
for (let i = 0; i < scored.length; i += 12) {
  const batch = scored.slice(i, i + 12);
  const qs = Object.fromEntries(batch.map((c, k) => [`keep_${k}`, { type: 'noul', instructions: `Will the FULL verbatim output of tool call "${c.name}" (input: ${c.input}) still be needed later in this session?` }]));
  const r = await askJevBundle({ state: { transcript_excerpt: batch.map(c => `${c.name}: ${c.result.slice(0, 600)}`).join('\n---\n') }, questions: qs, model: 'jev-1.13.0', timeoutMs: 10000, apiKey: process.env.TYPESAFE_API_KEY });
  if (!r.ok) throw new Error(`Invalid Jev answer: ${r.reason} ${r.error}`);
  batch.forEach((_, k) => jev.push(Number(field(r.answers[`keep_${k}`], 'noul'))));
  process.stderr.write(`.`);
}
const drops = { jev: jev.map(p => p < 0.5) };
// Baselines, same budget where meaningful.
const rate = drops.jev.filter(Boolean).length / scored.length;
drops.dropAll = scored.map(() => true);
drops.keepAll = scored.map(() => false);
drops.random = scored.map(() => Math.random() < rate);
drops.recency = scored.map((c, i) => i < scored.length * rate);   // drop the oldest, same budget

console.log(`\n${file.split('/').pop()}  calls=${scored.length}  needed_later=${needed.filter(Boolean).length}  jev_drop_rate=${(rate * 100).toFixed(1)}%`);
console.log('policy      dropped  dropped-but-needed  kept-but-never-needed  MISTAKES');
for (const [name, d] of Object.entries(drops)) {
  const bad = d.filter((x, i) => x && needed[i]).length;
  const waste = d.filter((x, i) => !x && !needed[i]).length;
  console.log(`${name.padEnd(11)} ${String(d.filter(Boolean).length).padStart(7)} ${String(bad).padStart(19)} ${String(waste).padStart(22)} ${String(bad + waste).padStart(9)}`);
}

// SEPARATION: can the keep-probability distinguish needed from unneeded AT ALL?
// P3's Python arm found none using call-local states; this arm passes result text plus a
// transcript excerpt, so it either confirms or refutes that on richer states.
{
  const A = jev.filter((_, i) => needed[i]);
  const B = jev.filter((_, i) => !needed[i]);
  const mean = (a) => a.reduce((x, y) => x + y, 0) / (a.length || 1);
  // kitAuc throws on a degenerate label rather than returning NaN, and reports constant=true
  // when every score is identical -- the shape that faked a clean 0.500 three times.
  const a = kitAuc(jev, needed);
  const auc = a.value;
  console.log(`SEPARATION  keep_p needed=${mean(A).toFixed(3)} (n=${A.length})  unneeded=${mean(B).toFixed(3)} (n=${B.length})  AUC=${auc.toFixed(3)}   0.5 = no signal`);
}
