#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { createWriteStream } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { once } from 'node:events';
import { dirname } from 'node:path';
import { inputHashes, readUsageFiles } from '../src/reader.mjs';
import { REDUCTIONS, aggregate, measureTurn, shares } from '../src/whatif-core.mjs';

function usage(message) { if (message) console.error(`ERROR ${message}`); console.error('usage: npm run whatif -- <session.jsonl|dir>... --out runs/whatif.json'); process.exit(2); }
function parseArgs(argv) { const inputs=[]; let out=null; for(let i=0;i<argv.length;i+=1){const arg=argv[i]; if(arg==='--out') out=argv[++i]; else if(arg.startsWith('--')) usage(`unknown option: ${arg}`); else inputs.push(arg);} if(!inputs.length) usage('input required'); if(!out) usage('--out required'); return {inputs,out}; }
function leverTable(values) { const keys=['cacheRead','cacheWrite','input','output','unreconciled']; const total=values.total ?? keys.reduce((sum,key)=>sum+(values[key]??0),0); return keys.map((lever)=>({lever,tokens:values[lever]??0,share:total?(values[lever]??0)/total:null})).sort((a,b)=>b.tokens-a.tokens||a.lever.localeCompare(b.lever)); }
async function writeLine(stream, value) { if (!stream.write(`${JSON.stringify(value)}\n`)) await once(stream, 'drain'); }
const {inputs,out}=parseArgs(process.argv.slice(2));
try {
  const parsed=await readUsageFiles(inputs);
  const hashes=await inputHashes(parsed.files);
  const turnsOut=`${out}.turns.ndjson`;
  await mkdir(dirname(out),{recursive:true});
  const stream=createWriteStream(turnsOut,{encoding:'utf8'});
  const perSession=[];
  const aggregateTotals={cacheRead:0,cacheWrite:0,input:0,output:0,unreconciled:0,total:0};
  const observedModels=new Set();
  for(const session of parsed.sessions){
    const total=aggregate(session.turns);
    for(const k of Object.keys(aggregateTotals)) aggregateTotals[k]+=total[k];
    for(const turn of session.turns) observedModels.add(turn.model);
    let sessionTurns=0;
    for(const turn of session.turns){
      const record={source:session.source,sessionId:session.sessionId,line:turn.line,model:turn.model,base:measureTurn(turn),shares:shares(measureTurn(turn)),whatIf:Object.fromEntries(REDUCTIONS.map(reduction=>[`${reduction*100}%`,measureTurn(turn,reduction)]))};
      sessionTurns+=1;
      await writeLine(stream,record);
    }
    perSession.push({source:session.source,sessionId:session.sessionId,turns:sessionTurns,levers:leverTable(total)});
  }
  await new Promise((resolve,reject)=>{stream.end(resolve);stream.on('error',reject);});
  const receipt={schema:'jev.retransmit-whatif.receipt.v1',generated_at:new Date().toISOString(),inputs:hashes,denominator:parsed.denominator,observedModels:[...observedModels].sort(),accounting:{unit:'tokens',billedTotal:'input + cacheRead + cacheWrite + output',assumption:'a reduction removes cacheRead * reduction from each usage-bearing turn; all other fields, turns, model behavior, retrieval quality, and tool behavior remain unchanged',notModeled:['quality preservation','retrieval recall','top_k effects','turn elimination overhead']},levers:{aggregate:leverTable(aggregateTotals),perSession,turnsFile:turnsOut},failures:parsed.failures};
  await writeFile(out,JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({output:out,turnsFile:turnsOut,denominator:receipt.denominator,failures:receipt.failures.length}));
  process.exitCode=receipt.failures.length?1:0;
} catch(error){console.error(JSON.stringify({schema:'jev.retransmit-whatif.receipt.v1',failures:[{code:error.code??'WHATIF_ERROR',message:error.message}]}));process.exitCode=1;}
