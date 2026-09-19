// A FAIR compaction oracle: one that can return YES.
//
// The previous oracle (oracle.mjs) scored a drop as a mistake if ANY novel token from the result
// reappeared later. Keep-everything therefore wins by construction: it makes zero drop-mistakes by
// definition, and the only cost it pays -- "kept but never needed" -- is counted per CALL, not per
// BYTE, so hoarding megabytes is free. That oracle cannot adopt compaction no matter how good it is.
//
// WIN CONDITION, PREREGISTERED BEFORE THIS WAS RUN (2026-09-19, committed in this file):
//   A compaction policy is ADOPTED if, versus keep-everything, it
//     (a) saves >= 50% of tool-result bytes, AND
//     (b) loses <= 10% of SUBSTANTIVE reuse events.
//   Anything else is REJECTED. Both numbers are declared here so the threshold cannot be chosen
//   after seeing the data.
//
// Two fairness fixes over the old oracle:
//   1. SUBSTANTIVE reuse: a single recurring token (a path, a flag, an id) is not evidence the
//      result mattered. Require >= MIN_TOKENS distinct novel tokens to reappear.
//   2. BYTES are the benefit and they are counted. The old scorer only counted calls.
import { readFileSync } from 'node:fs';

const MIN_TOKENS = Number(process.env.MIN_TOKENS ?? 3);
const SAVE_BAR = 0.50, LOSS_BAR = 0.10;
const rows = readFileSync(process.argv[2], 'utf8').split('\n').filter(Boolean)
  .map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);

const TOK = /[a-z][a-z0-9_./-]{5,}/g;
const firstSeen = new Map(), lastSeen = new Map();
for (let i = 0; i < rows.length; i++) {
  for (const t of (JSON.stringify(rows[i].message ?? rows[i]).toLowerCase().match(TOK) ?? [])) {
    if (!firstSeen.has(t)) firstSeen.set(t, i);
    lastSeen.set(t, i);
  }
}
const calls = [], byId = new Map();
for (const [i, r] of rows.entries()) {
  const m = r.message; if (!m) continue;
  if (m.role === 'toolResult') {
    const txt = (m.content ?? []).map(p => p?.text ?? '').join('\n');
    const hit = byId.get(m.toolCallId);
    if (hit) { hit.result = txt; hit.resultIdx = i; }
    continue;
  }
  for (const c of (m.content ?? [])) if (c?.type === 'toolCall') {
    const rec = { idx: i, id: c.id, name: c.name, result: null, resultIdx: i };
    calls.push(rec); byId.set(c.id, rec);
  }
}
const scored = calls.filter(c => c.result);
const STOP = new Set('the a an and or of to in is it for with on at by from this that not you your we as be are was'.split(' '));

// reuse STRENGTH, not a boolean: how many distinct novel tokens actually came back
const strength = scored.map(c => {
  const toks = [...new Set((c.result.toLowerCase().match(TOK) ?? []))].filter(t => !STOP.has(t));
  const novel = toks.filter(t => (firstSeen.get(t) ?? 0) >= c.idx);
  return (novel.length ? novel : toks).filter(t => (lastSeen.get(t) ?? -1) > c.resultIdx).length;
});
const substantive = strength.map(s => s >= MIN_TOKENS);
const bytes = scored.map(c => c.result.length);
const totalBytes = bytes.reduce((a, b) => a + b, 0);
const totalReuse = substantive.filter(Boolean).length;

const evaluate = (name, drop) => {
  const saved = bytes.reduce((a, b, i) => a + (drop[i] ? b : 0), 0);
  const lost = substantive.filter((s, i) => s && drop[i]).length;
  const savePct = saved / totalBytes, lossPct = totalReuse ? lost / totalReuse : 0;
  const verdict = (savePct >= SAVE_BAR && lossPct <= LOSS_BAR) ? 'ADOPT' : 'REJECT';
  console.log(`${name.padEnd(14)} saved=${(savePct * 100).toFixed(1).padStart(5)}%  reuse-lost=${(lossPct * 100).toFixed(1).padStart(5)}%  ${verdict}`);
  return verdict;
};

console.log(`\n${process.argv[2].split('/').pop()}  results=${scored.length}  bytes=${totalBytes}  substantive-reuse-events=${totalReuse} (MIN_TOKENS=${MIN_TOKENS})`);
console.log(`WIN CONDITION (preregistered): save >= ${SAVE_BAR * 100}% of bytes AND lose <= ${LOSS_BAR * 100}% of substantive reuse\n`);
evaluate('keepAll', scored.map(() => false));
evaluate('dropAll', scored.map(() => true));
// Can ANY policy clear the bar? The oracle of last resort: a perfect judge that drops exactly the
// results never substantively reused. If even THIS returns REJECT, the oracle is still rigged.
evaluate('perfect', substantive.map(s => !s));
// A cheap deterministic policy nobody has tried: drop only results larger than N bytes that were
// never substantively reused is cheating (uses the future), so instead drop the LARGEST results.
const order = bytes.map((b, i) => [b, i]).sort((a, b) => b[0] - a[0]).slice(0, Math.ceil(scored.length * 0.3)).map(x => x[1]);
evaluate('drop-largest', scored.map((_, i) => order.includes(i)));
