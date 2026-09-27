#!/usr/bin/env node
import {readFile, writeFile} from "node:fs/promises";

const ROOT = new URL("../..", import.meta.url);
const STATES = new URL("var/agent-tmp/jev-pgtu/states.jsonl", ROOT);
const ITEMS = new URL("work/jev-pgtu/items.jsonl", ROOT);
const JEV_ROWS = new URL("work/jev-a9fv/live-rows.jsonl", ROOT);
const OUT = new URL(process.env.JEV_PGTU_OUT ?? "var/agent-tmp/jev-pgtu/free-results.jsonl", ROOT);
const RESET_AT = "2026-10-03T00:00:00Z";
const MODEL = "dots-studio/dots-3-note-preview:free";
const dry = process.env.JEV_PGTU_DRY_RUN === "1";
const fake429 = process.env.JEV_PGTU_FAKE_429 === "1";
const nowMs = Date.parse(process.env.JEV_PGTU_NOW ?? new Date().toISOString());
const parseJsonl = async (url) => (await readFile(url, "utf8")).split("\n").filter(Boolean).map(JSON.parse);
const states = await parseJsonl(STATES);
const items = Object.fromEntries((await parseJsonl(ITEMS)).map((row) => [row.id, row]));
const jevRows = Object.fromEntries((await parseJsonl(JEV_ROWS)).map((row) => [row.id, row]));
const existing = await (async () => { try { return await parseJsonl(OUT); } catch { return []; } })();
const seen = new Set(existing.map((row) => row.id));
const pending = states.filter((row) => !seen.has(row.id));
if (dry && nowMs < Date.parse(RESET_AT)) {
  console.log(JSON.stringify({status: "NOT_RUN", selected: pending.length, sent: 0, resetAt: RESET_AT}));
  process.exit(2);
}
if (!dry && nowMs < Date.parse(RESET_AT)) throw new Error(`NOT_RUN: launch blocked until ${RESET_AT}`);
const key = process.env.OPENROUTER_API_KEY;
if (!dry && !key) throw new Error("OPENROUTER_API_KEY is not configured");
async function writeRows(rows) { if (!dry) await writeFile(OUT, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`); }
async function askFree(state) {
  if (dry && fake429) return {status: "not_run", reason: "openrouter-429-dry-run", retryAfter: RESET_AT};
  if (dry) return {status: "scored", flag: false, probability: 0, usage: {prompt_tokens: 0, completion_tokens: 0}};
  const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {method: "POST", headers: {"content-type": "application/json", authorization: `Bearer ${key}`}, body: JSON.stringify({model: MODEL, temperature: 0, response_format: {type: "json_object"}, messages: [{role: "system", content: "Return only JSON: {\"flag\": boolean, \"probability\": number between 0 and 1}."}, {role: "user", content: JSON.stringify(state)}]})});
  const body = await response.text();
  if (response.status === 429) return {status: "not_run", reason: "openrouter-429-daily-quota", retryAfter: RESET_AT};
  if (!response.ok) return {status: "refused", reason: `http-${response.status}`};
  try { const parsed = JSON.parse(body); const answer = JSON.parse(parsed.choices?.[0]?.message?.content); if (typeof answer.flag !== "boolean" || typeof answer.probability !== "number" || answer.probability < 0 || answer.probability > 1) return {status: "refused", reason: "invalid-answer"}; return {status: "scored", ...answer, usage: parsed.usage ?? null}; } catch { return {status: "refused", reason: "non-json"}; }
}
const rows = [...existing]; let stopped = false; let sent = 0;
for (const row of pending) {
  const jev = jevRows[row.id];
  const result = stopped ? {status: "not_run", reason: "openrouter-429-daily-quota", retryAfter: RESET_AT} : await askFree(states.find((state) => state.id === row.id).state);
  if (!stopped) sent += 1;
  rows.push({id: row.id, set: items[row.id].set, position: items[row.id].position, inputSha256: items[row.id].inputSha256, jev: {flag: jev?.flag ?? null, probability: jev?.probability ?? null, model: "jev-1.13.0"}, free: result});
  if (result.status === "not_run" && result.reason.startsWith("openrouter-429")) stopped = true;
  await writeRows(rows);
}
console.log(JSON.stringify({rows: rows.length, sent, stopped, model: MODEL}));
