#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const DATA = resolve(ROOT, 'var/agent-tmp/xfji');
const ROWS_PATH = resolve(dirname(fileURLToPath(import.meta.url)), 'xfji-rows.json');
const RATE_USD_PER_MILLION_INPUT = 0.042;
const NONINFERIORITY_MARGIN = 1 / 6;

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8'));
}

function readJsonLines(path) {
  return readFileSync(path, 'utf8').split('\n').filter(Boolean).map(JSON.parse);
}

function hash(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function collectTaskSpecs() {
  const tasks = new Map();
  for (const [prefix, name] of [['N', 'n30-tasks.json'], ['M', 'n60-tasks.json']]) {
    const file = resolve(ROOT, `work/jev-i20b/${name}`);
    for (const task of readJson(file).tasks) {
      if (typeof task.id !== 'string' || !Array.isArray(task.key) || task.key.length === 0 ||
          task.key.some((key) => typeof key !== 'string' || key.length === 0)) {
        throw new Error(`Invalid task label schema in ${name}`);
      }
      if (!task.id.startsWith(prefix) || tasks.has(task.id)) {
        throw new Error(`Unexpected or duplicate task id: ${task.id}`);
      }
      tasks.set(task.id, task);
    }
  }
  if (tasks.size !== 60) throw new Error(`Expected 60 preregistered tasks, found ${tasks.size}`);
  return tasks;
}

function collectRankManifest() {
  const rows = new Map();
  const files = readdirSync(DATA).filter((name) => /^manifest-g[1-6]\.jsonl$/.test(name)).sort();
  if (files.length !== 6) throw new Error(`Expected 6 rank manifests, found ${files.length}`);
  for (const file of files) {
    for (const row of readJsonLines(resolve(DATA, file))) {
      if (typeof row.task !== 'string' || rows.has(row.task)) throw new Error(`Duplicate or invalid manifest task: ${row.task}`);
      for (const field of ['a_top3', 'b_top3']) {
        if (!Array.isArray(row[field]) || row[field].length !== 3 || new Set(row[field]).size !== 3) {
          throw new Error(`${row.task} ${field} must contain three distinct candidate ids`);
        }
      }
      if (!Number.isSafeInteger(row.b_inputTokens) || row.b_inputTokens <= 0 || row.trunc !== 1000 || row.decontaminated !== true) {
        throw new Error(`Invalid frozen Choice receipt for ${row.task}`);
      }
      rows.set(row.task, row);
    }
  }
  if (rows.size !== 60) throw new Error(`Expected 60 rank receipts, found ${rows.size}`);
  return rows;
}

function collectArm(task, arm) {
  const logPath = resolve(DATA, `logs/xfji-${arm}-${task}.log`);
  const bytes = readFileSync(logPath);
  const lines = bytes.toString('utf8').split('\n');
  const events = [];
  for (const line of lines) {
    if (!line || line.startsWith('Failed to load extension ')) continue;
    try {
      events.push(JSON.parse(line));
    } catch (error) {
      throw new Error(`Invalid JSON in ${logPath}: ${error.message}`);
    }
  }
  const promptResults = events.filter((event) => event.type === 'prompt_result');
  if (promptResults.length !== 1 || promptResults[0].status !== 'completed') {
    throw new Error(`${arm}-${task} did not complete exactly one successful prompt`);
  }
  const assistantMessages = events
    .filter((event) => event.type === 'message_end' && event.message?.role === 'assistant')
    .map((event) => event.message);
  if (assistantMessages.length !== 1) throw new Error(`${arm}-${task} expected one final assistant message`);
  const message = assistantMessages[0];
  const answer = message.content
    .filter((block) => block.type === 'text' && typeof block.text === 'string')
    .map((block) => block.text)
    .join('\n');
  if (!answer.trim()) throw new Error(`${arm}-${task} final answer is empty`);
  const usage = message.usage ?? {};
  const modelId = typeof message.model === 'string' ? message.model : message.model?.id ?? message.model?.name ?? null;
  const promptPath = resolve(DATA, `prompts-${arm}-${task}.txt`);
  return {
    correct: null,
    answer_chars: answer.length,
    answer_sha256: hash(Buffer.from(answer, 'utf8')),
    prompt_sha256: hash(readFileSync(promptPath)),
    transcript_sha256: hash(bytes),
    model_id: modelId,
    input_tokens: Number.isFinite(usage.input) ? usage.input : null,
    model_cost_usd: Number.isFinite(usage.cost?.total) ? usage.cost.total : null,
    answer,
  };
}

function collectRows() {
  const tasks = collectTaskSpecs();
  const rankRows = collectRankManifest();
  const rows = [];
  for (const taskId of [...tasks.keys()].sort()) {
    const spec = tasks.get(taskId);
    const rank = rankRows.get(taskId);
    if (!rank) throw new Error(`Missing rank receipt for ${taskId}`);
    const a = collectArm(taskId, 'A');
    const b = collectArm(taskId, 'B');
    const matches = (answer) => spec.key.some((key) => answer.toLowerCase().includes(key.toLowerCase()));
    a.correct = matches(a.answer);
    b.correct = matches(b.answer);
    delete a.answer;
    delete b.answer;
    rows.push({
      task: taskId,
      key_count: spec.key.length,
      rank_trunc_chars: rank.trunc,
      a_top3: rank.a_top3,
      b_top3: rank.b_top3,
      choice_input_tokens: rank.b_inputTokens,
      a,
      b,
    });
  }
  return rows;
}

function binomialCdfAt(k, n) {
  if (n === 0) return 1;
  let probability = 2 ** -n;
  let sum = probability;
  for (let i = 0; i < k; i += 1) {
    probability *= (n - i) / (i + 1);
    sum += probability;
  }
  return sum;
}

function summarize(rows) {
  const n = rows.length;
  const aPass = rows.filter((row) => row.a.correct).length;
  const bPass = rows.filter((row) => row.b.correct).length;
  const bOnly = rows.filter((row) => row.b.correct && !row.a.correct).length;
  const aOnly = rows.filter((row) => row.a.correct && !row.b.correct).length;
  const discordant = bOnly + aOnly;
  const difference = (bPass - aPass) / n;
  const variance = n > 1 ? Math.max(0, (discordant / n - difference ** 2) / (n - 1)) : 0;
  const standardError = Math.sqrt(variance);
  const lower = difference - 1.96 * standardError;
  const upper = difference + 1.96 * standardError;
  const exactMcNemarP = discordant === 0 ? 1 : Math.min(1, 2 * binomialCdfAt(Math.min(aOnly, bOnly), discordant));
  const jevInputTokens = rows.reduce((sum, row) => sum + row.choice_input_tokens, 0);
  const modelCost = (arm) => rows.every((row) => Number.isFinite(row[arm].model_cost_usd))
    ? Number(rows.reduce((sum, row) => sum + row[arm].model_cost_usd, 0).toFixed(8))
    : null;
  return {
    n,
    rubric: 'case-insensitive literal substring match against each task key; no semantic adjudication',
    rank_context: 'first 1000 characters per candidate; selected top-3 passages appended in full to both arms',
    design_deviation: 'dev-fit.json froze full-text ranking, but all six recorded manifests specify trunc=1000; results apply to the measured 1000-character ranking variant only',
    a_pass: aPass,
    b_pass: bPass,
    b_minus_a: Number(difference.toFixed(6)),
    paired_difference_ci95: [Number(lower.toFixed(6)), Number(upper.toFixed(6))],
    discordant: { b_only: bOnly, a_only: aOnly },
    mcnemar_exact_two_sided_p: Number(exactMcNemarP.toFixed(6)),
    noninferiority_margin: Number(NONINFERIORITY_MARGIN.toFixed(6)),
    lower_ci_above_minus_margin: lower > -NONINFERIORITY_MARGIN,
    b_wins_preregistered_bar: difference >= 0 && lower > -NONINFERIORITY_MARGIN,
    jev_choice_requests: n,
    jev_choice_input_tokens: jevInputTokens,
    jev_choice_estimated_cost_usd: Number((jevInputTokens * RATE_USD_PER_MILLION_INPUT / 1_000_000).toFixed(8)),
    model_session_input_tokens: {
      a: rows.every((row) => Number.isSafeInteger(row.a.input_tokens)) ? rows.reduce((sum, row) => sum + row.a.input_tokens, 0) : null,
      b: rows.every((row) => Number.isSafeInteger(row.b.input_tokens)) ? rows.reduce((sum, row) => sum + row.b.input_tokens, 0) : null,
    },
    model_session_cost_usd: { a: modelCost('a'), b: modelCost('b') },
    model_ids: [...new Set(rows.flatMap((row) => [row.a.model_id, row.b.model_id]).filter(Boolean))].sort(),
  };
}

const mode = process.argv[2] ?? '--collect';
if (mode === '--collect') {
  const rows = collectRows();
  const output = { schema: 'jev-xfji-rows.v1', summary: summarize(rows), rows };
  writeFileSync(ROWS_PATH, `${JSON.stringify(output, null, 2)}\n`);
  console.log(JSON.stringify(output.summary));
} else if (mode === '--verify') {
  const output = readJson(ROWS_PATH);
  if (output.schema !== 'jev-xfji-rows.v1' || output.rows.length !== 60) throw new Error('Invalid committed XFJI rows');
  const calculated = summarize(output.rows);
  if (JSON.stringify(calculated) !== JSON.stringify(output.summary)) throw new Error('Committed XFJI summary does not match its rows');
  console.log(JSON.stringify(calculated));
} else {
  throw new Error(`Unknown mode ${mode}; use --collect or --verify`);
}
