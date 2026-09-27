import { appendFileSync, existsSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { askJev } from '../../kit/src/client.ts';
import { ASSISTANT, CUT, MODEL, QUESTION } from "./seat.mjs";

const HERE = new URL('.', import.meta.url);
const CORPUS = JSON.parse(readFileSync(new URL('CORPUS.json', HERE), 'utf8'));
const CLEAN = JSON.parse(readFileSync(new URL('../jev-injection-flag/tool-results-sample.json', import.meta.url), 'utf8')).rows;
const ATTACKS = readFileSync(new URL('../nev-injection/pairs.jsonl', import.meta.url), 'utf8').trim().split('\n').map((line) => JSON.parse(line));
const OUT = new URL('live-rows.jsonl', HERE);
const CONCURRENCY = Math.max(1, Number(process.env.CONCURRENCY ?? 8));
const MAX_FAILURES = 0;

function sha256(text) { return createHash('sha256').update(text, 'utf8').digest('hex'); }
function makeRows() {
  const attacksByIndex = new Map(ATTACKS.map((row, index) => [index, row]));
  const rows = [];
  for (let i = 0; i < CLEAN.length; i++) {
    const text = CLEAN[i].text;
    rows.push({ id: `clean-${i}`, set: 'clean', baseIndex: i, position: null, text, inputSha256: sha256(text) });
  }
  let sequence = 0;
  for (const attackIndex of CORPUS.selected_attack_indices) {
    const attack = attacksByIndex.get(attackIndex);
    if (!attack || attack.label !== 1) throw new Error(`selected attack index is not an attack: ${attackIndex}`);
    const baseIndex = sequence++;
    const base = CLEAN[baseIndex].text;
    const marker = `\n\n[UNTRUSTED TOOL OUTPUT]\n${attack.text}\n[/UNTRUSTED TOOL OUTPUT]\n`;
    for (const position of ['start', 'middle', 'end']) {
      const at = position === 'start' ? 0 : position === 'middle' ? Math.floor(base.length / 2) : base.length;
      const text = base.slice(0, at) + marker + base.slice(at);
      rows.push({ id: `planted-${baseIndex}-${position}`, set: 'planted', attackId: attack.id, attackIndex, baseIndex, position, text, inputSha256: sha256(text) });
    }
  }
  if (rows.length !== 600) throw new Error(`expected 600 rows, got ${rows.length}`);
  return rows;
}

const rows = makeRows();
const done = new Set();
if (existsSync(OUT)) {
  for (const line of readFileSync(OUT, 'utf8').split('\n')) {
    if (!line.trim()) continue;
    const row = JSON.parse(line);
    if (row.status === 'answered' || row.status === 'error') done.add(row.id);
  }
}
const todo = rows.filter((row) => !done.has(row.id));
let next = 0;
let completed = 0;
let failures = 0;
let stopped = false;
const startedAt = new Date().toISOString();
console.error(`jev-a9fv: ${todo.length} rows to run, ${done.size} resumed, concurrency=${CONCURRENCY}, model=${MODEL}`);

function isHardStop(result) {
  return result.reason === 'http' && /HTTP (401|402|403)\b/.test(result.error ?? '');
}

async function worker() {
  while (true) {
    if (stopped || next >= todo.length) return;
    const row = todo[next++];
    const result = await askJev({ state: { assistant: ASSISTANT, user_message: row.text }, questions: { inj: QUESTION }, model: MODEL, timeoutMs: 20_000 });
    const output = { id: row.id, set: row.set, baseIndex: row.baseIndex, ...(row.position ? { position: row.position, attackId: row.attackId, attackIndex: row.attackIndex } : {}), inputSha256: row.inputSha256, model: result.model, latencyMs: result.latencyMs };
    if (result.ok && typeof result.scores.inj === 'number' && Number.isFinite(result.scores.inj)) {
      Object.assign(output, { status: 'answered', p: result.scores.inj, flag: result.scores.inj >= CUT, usage: result.usage ?? null });
    } else {
      Object.assign(output, { status: 'error', reason: result.ok ? 'missing-score' : result.reason, error: result.ok ? 'inj score missing' : result.error, usage: null });
      failures++;
      if (isHardStop(result) || failures > MAX_FAILURES) stopped = true;
    }
    appendFileSync(OUT, JSON.stringify(output) + '\n');
    completed++;
    if (completed % 25 === 0) console.error(`progress ${completed}/${todo.length} failures=${failures}`);
  }
}
await Promise.all(Array.from({ length: CONCURRENCY }, () => worker()));
const finishedAt = new Date().toISOString();
console.error(`done completed=${completed} failures=${failures} stopped=${stopped}`);
process.stdout.write(JSON.stringify({ startedAt, finishedAt, completed, failures, stopped, rows: rows.length, model: MODEL, cut: CUT, input: OUT.pathname }) + '\n');
process.exit(failures === 0 && done.size + completed === rows.length ? 0 : 1);
