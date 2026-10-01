#!/usr/bin/env node
/** jev-wb7j Step 2 (live, bounded): one Noul per sampled pair.
 * Budget: max 110 HTTP POSTs total (100 + up to 10 retries).
 * Retry: 429/500/502/503/504 only, max 2 per id. Abort on 401/402/403.
 * Invalid answers recorded as errors (KEEP side), never retried.
 * Key: TYPESAFE_API_KEY from env only; missing key throws. Never logged.
 */
import { readFileSync, existsSync, appendFileSync } from 'node:fs';

const MODEL = 'jev-1.13.0';
const URL = 'https://api.typesafe.ai/v1/systemone';
import path from 'node:path';
const DIR = path.dirname(process.argv[1]) + '/';
const ROWS = "work/jev-wb7j-lossdepth/heldout-rows.jsonl";
const CALL_CAP = 110;
const RETRYABLE = new Set([429, 500, 502, 503, 504]);

const key = process.env.TYPESAFE_API_KEY;
if (!key) throw new Error('TYPESAFE_API_KEY missing; refusing to run');

const sample = readFileSync('work/jev-wb7j-lossdepth/heldout-sample.jsonl', 'utf8').trim().split('\n').map(JSON.parse);
const done = new Set();
if (existsSync(ROWS)) {
  for (const line of readFileSync(ROWS, 'utf8').trim().split('\n')) {
    if (line.trim()) done.add(JSON.parse(line).id);
  }
}
let calls = 0;
let aborted = false;

async function post(state) {
  const t0 = Date.now();
  const res = await fetch(URL, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: MODEL,
      state,
      questions: {
        rel: {
          type: 'noul',
          instructions: 'Memory: `memory`. Current request: `prompt`. Is this memory relevant to the current request?',
        },
      },
    }),
  });
  const latencyMs = Date.now() - t0;
  return { res, latencyMs };
}

for (const row of sample) {
  if (aborted) break;
  if (done.has(row.id)) continue;
  const state = { prompt: row.prompt, memory: row.memory };
  let attempt = 0, recorded = false;
  while (!recorded && attempt <= 2) {
    if (calls >= CALL_CAP) { aborted = true; break; }
    calls++;
    attempt++;
    let out;
    try {
      out = await post(state);
    } catch (e) {
      out = { transportError: String(e && e.message || e), latencyMs: -1 };
    }
    if (out.transportError) {
      if (attempt <= 2) { await new Promise(r => setTimeout(r, 1000 * attempt)); continue; }
      appendFileSync(ROWS, JSON.stringify({ id: row.id, model: MODEL, status: 'transport-error', http: null, noul: null, input_tokens: 0, latency_ms: out.latencyMs }) + '\n');
      recorded = true;
      continue;
    }
    const { res, latencyMs } = out;
    if (res.status === 401 || res.status === 402 || res.status === 403) {
      appendFileSync(ROWS, JSON.stringify({ id: row.id, model: MODEL, status: 'auth-stop', http: res.status, noul: null, input_tokens: 0, latency_ms: latencyMs }) + '\n');
      console.log('STOP on http ' + res.status + ' after ' + calls + ' calls');
      aborted = true; recorded = true;
      break;
    }
    if (RETRYABLE.has(res.status)) {
      if (attempt <= 2) { await new Promise(r => setTimeout(r, 1000 * attempt)); continue; }
      appendFileSync(ROWS, JSON.stringify({ id: row.id, model: MODEL, status: 'retry-exhausted', http: res.status, noul: null, input_tokens: 0, latency_ms: latencyMs }) + '\n');
      recorded = true;
      continue;
    }
    let body = null;
    try { body = await res.json(); } catch { /* fall through */ }
    const ans = body && body.answers && body.answers.rel;
    const usage = (body && body.usage) || {};
    const ok = ans && typeof ans.noul === 'number' && Number.isFinite(ans.noul) && ans.noul >= 0 && ans.noul <= 1;
    appendFileSync(ROWS, JSON.stringify({
      id: row.id, model: MODEL,
      status: res.ok && ok ? 'ok' : (res.ok ? 'invalid-answer' : 'http-error'),
      http: res.status, noul: ok ? ans.noul : null,
      input_tokens: usage.input_tokens || 0, latency_ms: latencyMs,
    }) + '\n');
    recorded = true;
  }
}
console.log('calls=' + calls + ' done_ids=' + (done.size) + ' aborted=' + aborted);
