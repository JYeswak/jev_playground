import { readRow } from '../jev-client/src/index.ts';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
const roots = [];
function walk(d){ for (const e of readdirSync(d,{withFileTypes:true})) { const p=join(d,e.name);
  if (e.isDirectory()) walk(p); else if (e.name.endsWith('.jsonl')) roots.push(p); } }
walk('/Users/josh/.omp/profiles');
const kinds={}, cmds=[]; let rows=0, unparsed=0;
for (const f of roots) {
  let txt; try { txt = readFileSync(f,'utf8'); } catch { continue; }
  if (!txt.includes('omp-harm-rule')) continue;
  for (const line of txt.split('\n')) {
    if (!line.includes('omp-harm-rule') || !line.includes('decision')) continue;
    const r = readRow(line);
    if (!r) { unparsed++; continue; }
    if (!r.type.includes('harm-rule.decision')) continue;
    rows++;
    const k = String(r.data.kind ?? 'MISSING'); kinds[k]=(kinds[k]??0)+1;
    if (typeof r.data.command === 'string') cmds.push([k, r.data.command.slice(0,90)]);
  }
}
console.log('harm-rule decision rows:', rows, '| unparsed by readRow:', unparsed);
console.log('kinds:', JSON.stringify(kinds));
console.log('rows carrying a command:', cmds.length, `(${rows? (100*cmds.length/rows).toFixed(0):0}%)`);
console.log('\nevery fire, verbatim:');
for (const [k,c] of cmds) if (k==='harm_fire') console.log('  FIRE:', c);
const passes = cmds.filter(([k])=>k==='harm_pass');
console.log(`\npasses (${passes.length}), first 12 verbatim — these are the false-negative candidates:`);
for (const [,c] of passes.slice(0,12)) console.log('  pass:', c);
