#!/usr/bin/env node
import {appendFile, readFile} from "node:fs/promises";
import {askJev} from "../../kit/src/client.ts";
import {SCIFACT_CRITERIA, SCIFACT_INSTRUCTIONS} from "../../kit/src/verify.ts";

const ROOT = new URL("../..", import.meta.url);
const STATES = new URL("var/agent-tmp/jev-oioo/states.jsonl", ROOT);
const ITEMS = new URL("work/jev-oioo/items.jsonl", ROOT);
const OUT = new URL(process.env.JEV_OIOO_OUT ?? "var/agent-tmp/jev-oioo/live-results.jsonl", ROOT);
const OPENROUTER_MODEL = "dots-studio/dots-3-note-preview:free";
const parseJsonl = async (url) => (await readFile(url, "utf8")).split("\n").filter(Boolean).map(JSON.parse);
const states = await parseJsonl(STATES);
const items = Object.fromEntries((await parseJsonl(ITEMS)).map((row) => [row.id, row]));
const seen = new Set((await (async () => { try { return await parseJsonl(OUT); } catch { return []; } })()).map((row) => row.id));
const question = {type: "noul", instructions: SCIFACT_INSTRUCTIONS, criteria: SCIFACT_CRITERIA};
const openRouterKey = process.env.OPENROUTER_API_KEY;
if (!openRouterKey) throw new Error("OPENROUTER_API_KEY is not configured");

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
  if (!response.ok) return {status: "refused", reason: `http-${response.status}`, latencyMs, raw: body.slice(0, 500)};
  try {
    const parsed = JSON.parse(body);
    const text = parsed.choices?.[0]?.message?.content;
    const answer = JSON.parse(text);
    if (typeof answer.supported !== "boolean" || typeof answer.confidence !== "number" || !Number.isFinite(answer.confidence) || answer.confidence < 0 || answer.confidence > 1) {
      return {status: "refused", reason: "invalid-answer", latencyMs};
    }
    return {status: "scored", supported: answer.supported, confidence: answer.confidence, latencyMs, usage: parsed.usage ?? null};
  } catch {
    return {status: "refused", reason: "non-json", latencyMs};
  }
}

for (const row of states.filter((item) => !seen.has(item.id))) {
  const started = Date.now();
  const state = row.state;
  const jev = await askJev({state, questions: {value: question}, model: "jev-1.13.0", timeoutMs: 10000, retry: {maxRetries: 0}});
  const jevAnswer = jev.ok
    ? {status: "scored", supported: jev.scores.value >= 0.5, noul: jev.scores.value, latencyMs: jev.latencyMs, usage: jev.usage ?? null, model: jev.model}
    : {status: "refused", reason: jev.reason, error: jev.error, latencyMs: jev.latencyMs, model: jev.model};
  const free = await comparator(state);
  await appendFile(OUT, JSON.stringify({id: row.id, gold: items[row.id].label, jev: jevAnswer, comparator: free, wallMs: Date.now() - started}) + "\n");
}
const done = await parseJsonl(OUT);
console.log(JSON.stringify({rows: done.length, jevRefused: done.filter((x) => x.jev.status !== "scored").length, comparatorRefused: done.filter((x) => x.comparator.status !== "scored").length, comparatorModel: OPENROUTER_MODEL}));
