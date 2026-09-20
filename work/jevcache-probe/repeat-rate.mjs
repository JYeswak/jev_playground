import { readRow } from '../jev-client/src/index.ts';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
const files=[]; (function w(d){ for (const e of readdirSync(d,{withFileTypes:true})) { const p=join(d,e.name);
  if (e.isDirectory()) w(p); else if (e.name.endsWith('.jsonl')) files.push(p); } })('/Users/josh/.omp/profiles');
const byExt={};
for (const f of files) { let t; try{t=readFileSync(f,'utf8');}catch{continue;}
  if(!t.includes('com.zeststream.omp-jev')&&!t.includes('omp-harm-rule'))continue;
  for (const line of t.split('\n')) {
    if(!line.includes('decision'))continue;
    const r=readRow(line); if(!r)continue;
    const m=/com\.zeststream\.(omp-jev-[a-z-]+)\.decision/.exec(r.type); if(!m)continue;
    const ext=m[1];
    if(ext==='omp-jev-observer'&&typeof r.data.command!=='string')continue; // no state field stored
    // the state a cache would key on: the scored input
    const st=r.data.command ?? r.data.subject ?? r.data.intent ?? r.data.failure ?? r.data.prompt;  // NO fallback: a row without a state field is not countable
    if(typeof st!=='string'||!st) continue;
    const k=createHash('sha256').update(ext+'|'+st).digest('hex');
    byExt[ext] ??= {total:0, seen:new Map()};
    byExt[ext].total++;
    byExt[ext].seen.set(k,(byExt[ext].seen.get(k)??0)+1);
  }}
let T=0,D=0;
console.log('extension'.padEnd(20),'calls'.padStart(6),'distinct'.padStart(9),'repeat%'.padStart(8),'  cache would save');
for (const [ext,v] of Object.entries(byExt).sort((a,b)=>b[1].total-a[1].total)) {
  const d=v.seen.size, rep=v.total-d; T+=v.total; D+=d;
  console.log(ext.padEnd(20), String(v.total).padStart(6), String(d).padStart(9),
    ((100*rep/v.total)||0).toFixed(0).padStart(7)+'%', '  ', rep, 'calls');
}
console.log('\nTOTAL', T, 'model-scored rows |', D, 'distinct |', T-D, 'repeats =', ((100*(T-D)/T)||0).toFixed(1)+'%');
console.log('Only model-CALLING extensions with a stored state field. Rows lacking one are excluded, not guessed.');
