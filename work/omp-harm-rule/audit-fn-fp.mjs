import { readRow } from '../jev-client/src/index.ts';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
const files=[]; (function w(d){ for (const e of readdirSync(d,{withFileTypes:true})) { const p=join(d,e.name);
  if (e.isDirectory()) w(p); else if (e.name.endsWith('.jsonl')) files.push(p); } })('/Users/josh/.omp/profiles');
// independent danger heuristic, deliberately BROADER than the shipped rule
const DANGER = /(rm\s+-rf|\bmkfs\b|dd\s+.*of=\/dev|chmod\s+-R|chown\s+-R|>\s*\/etc\/|curl[^|]*\|\s*(ba)?sh|git\s+push\s+--force|launchctl\s+(un)?load|openssl\s+enc|\bsudo\b|killall|pkill\s+-9|truncate\s+-s\s*0|\bshred\b|\bsecurity\s+(delete|dump)|--no-verify|history\s+-c)/i;
const uniq=new Map();
for (const f of files) { let t; try{t=readFileSync(f,'utf8');}catch{continue;}
  if(!t.includes('omp-harm-rule'))continue;
  for (const line of t.split('\n')) { if(!line.includes('omp-harm-rule')||!line.includes('decision'))continue;
    const r=readRow(line); if(!r||!r.type.includes('harm-rule.decision'))continue;
    const c=r.data.command; if(typeof c!=='string')continue;
    const key=r.data.kind+'|'+c; if(!uniq.has(key)) uniq.set(key,{kind:r.data.kind,c}); } }
const rowsU=[...uniq.values()];
const fnCandidates=rowsU.filter(r=>r.kind==='harm_pass'&&DANGER.test(r.c));
const fpCandidates=rowsU.filter(r=>r.kind==='harm_fire'&&!DANGER.test(r.c));
console.log('distinct (kind,command) pairs:',rowsU.length);
console.log('FALSE-NEGATIVE candidates (passed, but a broader heuristic calls dangerous):',fnCandidates.length);
for (const r of fnCandidates) console.log('   FN?', r.c);
console.log('FALSE-POSITIVE candidates (fired, broader heuristic sees nothing):',fpCandidates.length);
for (const r of fpCandidates) console.log('   FP?', r.c);
