// Does the "needed later" oracle DISCRIMINATE, or does it call everything needed?
// Planted negative: replace each result with noise that cannot possibly be reused.
import { readFileSync } from 'node:fs';
const rows = readFileSync(process.argv[2],'utf8').split('\n').filter(Boolean).map(l=>{try{return JSON.parse(l)}catch{return null}}).filter(Boolean);
const TOK=/[a-z][a-z0-9_./-]{5,}/g;
const firstSeen=new Map(), lastSeen=new Map();
for(let i=0;i<rows.length;i++){const s=JSON.stringify(rows[i].message??rows[i]).toLowerCase();for(const t of (s.match(TOK)??[])){if(!firstSeen.has(t))firstSeen.set(t,i);lastSeen.set(t,i);}}
const STOP=new Set('the a an and or of to in is it for with on at by from this that not you your we as be are was'.split(' '));
const judge=(text,idx,ridx)=>{const toks=[...new Set((text.toLowerCase().match(TOK)??[]))].filter(t=>!STOP.has(t));if(!toks.length)return false;const novel=toks.filter(t=>(firstSeen.get(t)??0)>=idx);const probe=(novel.length?novel:toks).slice(0,60);return probe.some(t=>(lastSeen.get(t)??-1)>ridx);};
const calls=[];const byId=new Map();
for(const [i,r] of rows.entries()){const m=r.message;if(!m)continue;
 if(m.role==='toolResult'){const txt=(m.content??[]).map(p=>p?.text??'').join('\n');const h=byId.get(m.toolCallId);if(h){h.result=txt.slice(0,4000);h.resultIdx=i;}continue;}
 for(const c of (m.content??[])) if(c?.type==='toolCall'){const rec={idx:i,id:c.id,result:null,resultIdx:i};calls.push(rec);byId.set(c.id,rec);} }
const s=calls.filter(c=>c.result).slice(0,200);
const real=s.filter(c=>judge(c.result,c.idx,c.resultIdx)).length;
const noise=s.filter(c=>judge(Array.from({length:40},()=>'zq'+Math.random().toString(36).slice(2,10)).join(' '),c.idx,c.resultIdx)).length;
// second control: a result copied from the LAST message (cannot be reused after the end)
const tail=s.filter(c=>judge(c.result,c.idx,rows.length-1)).length;
console.log(`n=${s.length}  real_needed=${real} (${(100*real/s.length).toFixed(1)}%)  NOISE_needed=${noise} (should be ~0)  scored_at_end=${tail} (should be ~0)`);
