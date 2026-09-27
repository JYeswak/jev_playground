#!/usr/bin/env node
import {appendFile, readFile, writeFile} from "node:fs/promises";
import {askJev} from "../../kit/src/client.ts";
import {SCIFACT_CRITERIA, SCIFACT_INSTRUCTIONS} from "../../kit/src/verify.ts";

const ROOT = new URL("../..", import.meta.url);
const STATES = new URL("var/agent-tmp/jev-oioo/states.jsonl", ROOT);
const ITEMS = new URL("work/jev-oioo/items.jsonl", ROOT);
const OUT = new URL(process.env.JEV_OIOO_OUT ?? "var/agent-tmp/jev-oioo/live-results.jsonl", ROOT);
const OPENROUTER_MODEL = "dots-studio/dots-3-note-preview:free";
const RESET_AT = "2026-09-28T00:00:00Z";
const comparatorOnly = process.env.JEV_OIOO_COMPARATOR_ONLY === "1";

const parseJsonl = async (url) => (await readFile(url, "utf8")).split("\n").filter(Boolean).map(JSON.parse);
const states = await parseJsonl(STATES);
const stateById = Object.fromEntries(states.map((row) => [row.id, row.state]));
const items = Object.fromEntries((await parseJsonl(ITEMS)).map((row) => [row.id, row]));
const existing = await (async () => { try { return await parseJsonl(OUT); } catch { return []; } })();
const byId = new Map(existing.map((row) => [row.id, row]));
const question = {type: "noul", instructions: SCIFACT_INSTRUCTIONS, criteria: SCIFACT_CRITERIA};
const openRouterKey = process.env.OPENROUTER_API_KEY;
if (!openRouterKey) throw new Error("OPENROUTER_API_KEY is not configured");

async function writeRows() {
  await writeFile(OUT, `${[...byId.values()].map((row) => JSON.stringify(row)).join("\n")}\n`);
}

async function comparator(state) {
  const started = Date.now();
  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
    method: "POST",
    headers: {"content-type": "application/json", authorization: `Bearer ${openRouterKey}`},
    body: JSON.stringify({
      model: OPENROUTER_MODEL,
      temperature: 0,
      response_format: {type: "json_object"},
      messages: [
        {role: "system", content: "Decide whether the evidence supports the claim. Return only JSON: {\"supported\": true|false, \"confidence\": number between 0 and 1}."},
        {role: "user", content: JSON.stringify(state)},
      ],
    }),
  });
  const latencyMs = Date.now() - started;
  const body = await response.text();
  if (response.status === 429) return {status: "not_run", reason: "openrouter-429-daily-quota", retryAfter: RESET_AT, latencyMs};
  if (!response.ok) return {status: "refused", reason: `http-${response.status}`, latencyMs, raw: body.slice(0, 500)};
  try {
    const parsed = JSON.parse(body);
    const text = parsed.choices?.[0]?.message?.content;
    const answer = JSON.parse(text);
    if (typeof answer.supported !== "boolean" || typeof answer.confidence !== "number" || !Number.isFinite(answer.confidence) || answer.confidence < 0 || answer.confidence > 1) return {status: "refused", reason: "invalid-answer", latencyMs};
    return {status: "scored", supported: answer.supported, confidence: answer.confidence, latencyMs, usage: parsed.usage ?? null};
  } catch { return {status: "refused", reason: "non-json", latencyMs}; }
}

const baseFor = (id) => ({id, gold: items[id].label});
const pending = comparatorOnly
  ? existing.filter((row) => row.comparator.status === "refused" || row.comparator.status === "not_run")
  : states.filter((row) => !byId.has(row.id)).map((row) => ({id: row.id}));
let stopped = false;
for (const pendingRow of pending) {
  const id = pendingRow.id;
  const state = stateById[id];
  let row = byId.get(id);
  if (!comparatorOnly) {
    const started = Date.now();
    const jev = await askJev({state, questions: {value: question}, model: "jev-1.13.0", timeoutMs: 10000, retry: {maxRetries: 0}});
    const jevAnswer = jev.ok
      ? {status: "scored", supported: jev.scores.value >= 0.5, noul: jev.scores.value, latencyMs: jev.latencyMs, usage: jev.usage ?? null, model: jev.model}
      : {status: "refused", reason: jev.reason, error: jev.error, latencyMs: jev.latencyMs, model: jev.model};
    row = {...baseFor(id), jev: jevAnswer, comparator: {status: "not_run", reason: "pending", retryAfter: RESET_AT}, wallMs: Date.now() - started};
  }
  if (stopped) { row.comparator = {status: "not_run", reason: "openrouter-429-daily-quota", retryAfter: RESET_AT}; byId.set(id, row); continue; }
  const free = await comparator(state);
  row.comparator = free;
  byId.set(id, row);
  await writeRows();
  if (free.status === "not_run" && free.reason === "openrouter-429-daily-quota") stopped = true;
}
if (stopped) {
  for (const pendingRow of pending) {
    const row = byId.get(pendingRow.id);
    if (row && row.comparator.status === "pending") { row.comparator = {status: "not_run", reason: "openrouter-429-daily-quota", retryAfter: RESET_AT}; byId.set(row.id, row); }
  }
  await writeRows();
}
const done = [...byId.values()];
console.log(JSON.stringify({rows: done.length, comparatorOnly, jevRefused: done.filter((x) => x.jev.status !== "scored").length, comparatorRefused: done.filter((x) => x.comparator.status !== "scored").length, comparatorNotRun: done.filter((x) => x.comparator.status === "not_run").length, comparatorModel: OPENROUTER_MODEL}));
