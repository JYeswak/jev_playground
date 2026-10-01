#!/usr/bin/env node
/** jev-wb7j loss-depth dev replay: ONE variable changed vs score_live.mjs.
 * variant=word: instructions gain the quote-or-act criterion (state identical).
 * variant=statemin: state memory truncated to first 120 chars (wording identical).
 * Same budget/stop rules as score_live.mjs. Usage: node replay_live.mjs <variant> <out.jsonl>
 */
import { readFileSync, appendFileSync } from 'node:fs';

const MODEL = 'jev-1.13.0';
const URL = 'https://api.typesafe.ai/v1/systemone';
const CALL_CAP = 110;
const RETRYABLE = new Set([429, 500, 502, 503, 504]);

const BASE_INSTR = 'Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?';
const WORD_INSTR = 'Memory: `memory`. Current request: `prompt`. Would you quote or act on this memory while doing the current request? Answer for direct usability in the demanded response, not topical overlap.';

const variant = process.argv[2];
const OUT = process.argv[3];
if ((variant !== 'word' && variant !== 'statemin') || !OUT) {
  console.error('usage: node replay_live.mjs <word|statemin> <out.jsonl>');
  process.exit(2);
}

const key = process.env.TYPESAFE_API_KEY;
if (!key) throw new Error('TYPESAFE_API_KEY missing; refusing to run');

const sample = readFileSync('work/jev-wb7j/sample.jsonl', 'utf8').trim().split('\n').map(JSON.parse);
let calls = 0;
let aborted = false;

async function post(state, instructions) {
  const t0 = Date.now();
  const res = await fetch(URL, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: MODEL, state,
      questions: { rel: { type: 'noul', instructions } },
    }),
  });
  return { res, latencyMs: Date.now() - t0 };
}

for (const row of sample) {
  if (aborted) break;
  const state = variant === 'statemin'
    ? { prompt: row.prompt, memory: row.memory.slice(0, 120) }
    : { prompt: row.prompt, memory: row.memory };
  const instructions = variant === 'word' ? WORD_INSTR : BASE_INSTR;
  let attempt = 0, recorded = false;
  while (!recorded && attempt <= 2) {
    if (calls >= CALL_CAP) { aborted = true; break; }
    calls++;
    attempt++;
    let out;
    try {
      out = await post(state, instructions);
    } catch (e) {
      out = { transportError: String((e && e.message) || e), latencyMs: -1 };
    }
    if (out.transportError) {
      if (attempt <= 2) { await new Promise(r => setTimeout(r, 1000 * attempt)); continue; }
      appendFileSync(OUT, JSON.stringify({ id: row.id, model: MODEL, variant, status: 'transport-error', http: null, noul: null, input_tokens: 0, latency_ms: out.latencyMs }) + '\n');
      recorded = true;
      continue;
    }
    const { res, latencyMs } = out;
    if (res.status === 401 || res.status === 402 || res.status === 403) {
      appendFileSync(OUT, JSON.stringify({ id: row.id, model: MODEL, variant, status: 'auth-stop', http: res.status, noul: null, input_tokens: 0, latency_ms: latencyMs }) + '\n');
      console.log('STOP on http ' + res.status + ' after ' + calls + ' calls');
      aborted = true; recorded = true;
      break;
    }
    if (RETRYABLE.has(res.status)) {
      if (attempt <= 2) { await new Promise(r => setTimeout(r, 1000 * attempt)); continue; }
      appendFileSync(OUT, JSON.stringify({ id: row.id, model: MODEL, variant, status: 'retry-exhausted', http: res.status, noul: null, input_tokens: 0, latency_ms: latencyMs }) + '\n');
      recorded = true;
      continue;
    }
    let body = null;
    try { body = await res.json(); } catch { /* fall through */ }
    const ans = body && body.answers && body.answers.rel;
    const usage = (body && body.usage) || {};
    const ok = ans && typeof ans.noul === 'number' && Number.isFinite(ans.noul) && ans.noul >= 0 && ans.noul <= 1;
    appendFileSync(OUT, JSON.stringify({
      id: row.id, model: MODEL, variant,
      status: res.ok && ok ? 'ok' : (res.ok ? 'invalid-answer' : 'http-error'),
      http: res.status, noul: ok ? ans.noul : null,
      input_tokens: usage.input_tokens || 0, latency_ms: latencyMs,
    }) + '\n');
    recorded = true;
  }
}
console.log('variant=' + variant + ' calls=' + calls + ' aborted=' + aborted);
