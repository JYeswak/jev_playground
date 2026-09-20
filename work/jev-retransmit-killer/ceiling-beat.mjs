/**
 * Section 21 — re-beat the CEILING arm on fresh real sessions, with no Jev call.
 *
 * THE POINT, and why this needs no API key. The decisive question for compaction is
 * not "is Jev's keep-probability well calibrated" — that is already measured twice,
 * AUC 0.522 / 0.348 / 0.648, straddling chance. The decisive question is whether ANY
 * policy could clear the preregistered bar, and that is answered by the `perfect`
 * arm: an omniscient judge that drops exactly the results never substantively reused.
 * No real policy can beat an omniscient one. If `perfect` fails the bar, the ceiling
 * is below the bar and the model is irrelevant to the decision.
 *
 * The bar is NOT set here. It is preregistered at work/compaction-proof/fair-oracle.mjs:22
 * and predates this section: save >= 50% of tool-result bytes AND lose <= 10% of
 * substantive reuse.
 *
 * THE FALSIFIER IS COMMITTED AT work/jev-retransmit-killer/FALSIFIER.md (8e43ccb),
 * before this file ran: if `perfect` returns ADOPT the claim is FALSE and the section
 * reopens. Its second clause is enforced in code below — a session with too few scored
 * results, or zero substantive reuse events, reports INSUFFICIENT and never a verdict.
 * A confident verdict on a thin session is the NaN% failure in another costume.
 *
 * Does NOT re-implement the oracle. It drives work/compaction-proof/fair-oracle.mjs,
 * which already carries the bars and the two planted-negative self-checks.
 *
 * Run: node work/jev-retransmit-killer/ceiling-beat.mjs [nSessions]
 */
import { execFileSync } from 'node:child_process';
import { statSync } from 'node:fs';

const WANT = Number(process.argv[2] ?? 12);
const MIN_RESULTS = 40; // preregistered in FALSIFIER.md
const ORACLE = 'work/compaction-proof/fair-oracle.mjs';

const found = execFileSync(
  'find',
  [`${process.env.HOME}/.omp/profiles`, '-path', '*agent/sessions*', '-name', '*.jsonl', '-size', '+400k'],
  { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 },
)
  .split('\n')
  .filter(Boolean);

// Largest first: a ceiling argument is strongest on the sessions with the most to save.
const sessions = found
  .map((p) => ({ p, size: statSync(p).size }))
  .sort((a, b) => b.size - a.size)
  .slice(0, WANT);

console.log(`candidate sessions >400k: ${found.length}; beating the ${sessions.length} largest`);
console.log(`bar (preregistered, ${ORACLE}): save >= 50% AND reuse-lost <= 10%`);
console.log(`insufficiency guard (preregistered, FALSIFIER.md): >= ${MIN_RESULTS} scored results AND > 0 reuse events\n`);

const parse = (text) => {
  const head = /results=(\d+)\s+bytes=(\d+)\s+substantive-reuse-events=(\d+)/.exec(text);
  const rows = {};
  for (const m of text.matchAll(/^(\w[\w-]*)\s+saved=\s*([\d.]+)%\s+reuse-lost=\s*([\d.]+)%\s+(ADOPT|REJECT)/gm)) {
    rows[m[1]] = { saved: Number(m[2]), lost: Number(m[3]), verdict: m[4] };
  }
  return head ? { results: +head[1], bytes: +head[2], reuse: +head[3], rows } : null;
};

let usable = 0;
let perfectAdopts = 0;
let dropLargestAdopts = 0;
const table = [];

for (const { p, size } of sessions) {
  let out;
  try {
    out = execFileSync('node', [ORACLE, p], { encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
  } catch (error) {
    table.push({ name: p.split('/').pop().slice(0, 28), note: `ORACLE ERROR: ${String(error.message).slice(0, 60)}` });
    continue;
  }
  const r = parse(out);
  if (!r) {
    table.push({ name: p.split('/').pop().slice(0, 28), note: 'UNPARSEABLE ORACLE OUTPUT' });
    continue;
  }
  const insufficient = r.results < MIN_RESULTS || r.reuse === 0;
  if (insufficient) {
    table.push({
      name: p.split('/').pop().slice(0, 28),
      kb: Math.round(size / 1024),
      results: r.results,
      reuse: r.reuse,
      note: `INSUFFICIENT (results=${r.results}, reuse=${r.reuse}) — no verdict taken`,
    });
    continue;
  }
  usable += 1;
  if (r.rows.perfect?.verdict === 'ADOPT') perfectAdopts += 1;
  if (r.rows['drop-largest']?.verdict === 'ADOPT') dropLargestAdopts += 1;
  table.push({
    name: p.split('/').pop().slice(0, 28),
    kb: Math.round(size / 1024),
    results: r.results,
    reuse: r.reuse,
    perfect: r.rows.perfect,
    dropLargest: r.rows['drop-largest'],
  });
}

console.log('session                        KB  results reuse | perfect saved/lost verdict | drop-largest');
for (const t of table) {
  if (t.note) {
    console.log(`${t.name.padEnd(30)} ${String(t.kb ?? '').padStart(5)} ${String(t.results ?? '').padStart(7)} ${String(t.reuse ?? '').padStart(5)} | ${t.note}`);
    continue;
  }
  console.log(
    `${t.name.padEnd(30)} ${String(t.kb).padStart(5)} ${String(t.results).padStart(7)} ${String(t.reuse).padStart(5)} | ` +
      `${String(t.perfect.saved).padStart(5)}% ${String(t.perfect.lost).padStart(5)}% ${t.perfect.verdict.padEnd(7)} | ` +
      `${String(t.dropLargest.saved).padStart(5)}% ${String(t.dropLargest.lost).padStart(5)}% ${t.dropLargest.verdict}`,
  );
}

console.log(`\nusable sessions (passed the insufficiency guard): ${usable} of ${sessions.length}`);
if (usable === 0) {
  console.log('VERDICT: NONE. Every session was too thin to rule on. This is not evidence for the claim.');
  process.exit(3);
}
console.log(`perfect (omniscient ceiling) ADOPTED on: ${perfectAdopts}/${usable}`);
console.log(`drop-largest ADOPTED on:                 ${dropLargestAdopts}/${usable}`);
console.log('');
if (perfectAdopts > 0) {
  console.log('FALSIFIER FIRED: the omniscient ceiling cleared the preregistered bar on at least one');
  console.log('real session. The claim "compaction cannot be adopted here" is FALSE as stated, and');
  console.log('the question becomes which policy reaches the ceiling. SECTION REOPENS.');
  process.exit(1);
}
console.log('CLAIM HOLDS on these sessions: even an omniscient judge cannot clear the bar, so no');
console.log('real policy can, and the keep-probability is irrelevant to the adopt decision.');
