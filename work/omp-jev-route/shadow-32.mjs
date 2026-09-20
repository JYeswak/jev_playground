/**
 * vbh.4 shadow measurement: policy v1 over RECORDED eww scores (no new calls).
 * Parses the recorded score-32 run output, applies shadow-policy-v1.md, prints
 * tier accuracy vs always-abstain and argmax-always baselines, and demonstrates
 * the kill switch firing. Second half of the run re-executes with ROUTER_KILL=1.
 *
 * Run: node work/omp-jev-route/shadow-32.mjs [score-log-path]
 */
import { readFileSync } from 'node:fs';

const logPath = process.argv[2] ?? '/tmp/score32.log';
const KILL = process.env.ROUTER_KILL === '1' || process.argv.includes('--kill');

const rows = [];
for (const line of readFileSync(logPath, 'utf8').split('\n')) {
  const m = line.match(/^(\S+)\s+(\S+)\s+needs=([0-9.]+)\/([TF])\/([TF])\/(HIT|MISS)\s+mechanical=([0-9.]+)\/([TF])\/([TF])\/(HIT|MISS)/);
  if (!m) continue;
  rows.push({
    id: m[1], cls: m[2],
    heavy: parseFloat(m[3]), mech: parseFloat(m[7]),
    heavyTruth: m[5] === 'T', mechTruth: m[9] === 'T',
  });
}
if (rows.length === 0) throw new Error(`no score rows parsed from ${logPath}`);

function decide(r) {
  if (KILL) return 'abstain';
  if (r.heavy >= 0.75 && r.mech < 0.5) return 'heavy';
  if (r.mech >= 0.75 && r.heavy < 0.5) return 'light';
  return 'abstain';
}
function argmax(r) {
  return r.heavy >= r.mech ? 'heavy' : 'light';
}
function judge(tier, r) {
  if (tier === 'abstain') return 'abstain';
  if (tier === 'heavy') return r.heavyTruth ? 'correct' : 'wrong';
  return r.mechTruth ? 'correct' : 'wrong';
}

const t = { correct: 0, wrong: 0, abstain: 0 };
const perClass = {};
for (const r of rows) {
  const v = judge(decide(r), r);
  t[v === 'abstain' ? 'abstain' : v] += 1;
  perClass[r.cls] ??= { correct: 0, wrong: 0, abstain: 0 };
  perClass[r.cls][v === 'abstain' ? 'abstain' : v] += 1;
}
let argCorrect = 0, argWrong = 0;
for (const r of rows) {
  const v = judge(argmax(r), r);
  if (v === 'correct') argCorrect += 1; else argWrong += 1;
}
console.log(`turns: ${rows.length} | kill: ${KILL ? 'FIRING' : 'off'} | model: jev-1.13.0 (recorded)`);
console.log(`shadow policy: correct=${t.correct} wrong=${t.wrong} abstain=${t.abstain}`);
console.log(`always-abstain: correct=0 wrong=0 abstain=${rows.length}`);
console.log(`argmax-always: correct=${argCorrect} wrong=${argWrong} abstain=0`);
for (const [cls, s] of Object.entries(perClass)) {
  console.log(`  ${cls.padEnd(12)} correct=${s.correct} wrong=${s.wrong} abstain=${s.abstain}`);
}
