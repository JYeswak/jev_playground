#!/usr/bin/env node
import { createHash } from "node:crypto";
import { appendFile, readFile } from "node:fs/promises";
import { RISK, STATE_CONTEXT, CUT } from "../../work/bicameral-gate/questions.mjs";

const ROOT = new URL("../..", import.meta.url);
const PREREG = new URL("work/jev-1lim/PREREG-QSA6.md", ROOT);
const REACH = new URL("work/jev-1lim/reach-receipt-qsa6.json", ROOT);
const REDACTED = new URL("var/agent-tmp/jev-qsa6-redacted.jsonl", ROOT);
const OUT = new URL(process.env.JEV_QSA6_OUT ?? "var/agent-tmp/jev-qsa6/free-rows.jsonl", ROOT);
const MODEL = "dots-studio/dots-3-note-preview:free";
const LAUNCH_AFTER = Date.parse("2026-09-29T00:00:00Z");

const jsonl = async (url) => (await readFile(url, "utf8")).split("\n").filter(Boolean).map(JSON.parse);
async function launchGate() {
  if (Date.now() < LAUNCH_AFTER) throw new Error("jev-qsa6 launch refused before 2026-09-30T00:00:00Z");
  const preregSha = createHash("sha256").update(await readFile(PREREG)).digest("hex");
  const reach = JSON.parse(await readFile(REACH, "utf8"));
  if (reach.status !== "REACHABLE" || reach.mode !== "mcnemar" || reach.prereg_sha256 !== preregSha) throw new Error("reach receipt is not bound to current qsa6 prereg");
}
function questionPrompt() {
  return Object.entries(RISK).map(([key, q]) => `${key}: ${q.instructions}\ntrue=${q.criteria.true}\nfalse=${q.criteria.false}`).join("\n\n");
}
async function main() {
  await launchGate();
  const rows = await jsonl(REDACTED);
  const done = new Set();
  try { for (const row of await jsonl(OUT)) done.add(row.id); } catch {}
  await appendFile(OUT, "", { flag: "a" });
  for (const row of rows) {
    if (done.has(row.id)) continue;
    const started = Date.now();
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", { method: "POST", headers: { "content-type": "application/json", authorization: `Bearer ${process.env.OPENROUTER_API_KEY}` }, body: JSON.stringify({ model: MODEL, temperature: 0, response_format: { type: "json_object" }, messages: [{ role: "system", content: `Return JSON object with numeric scores in [0,1] for exactly these questions:\n${questionPrompt()}` }, { role: "user", content: JSON.stringify({ command: row.command, context: STATE_CONTEXT }) }] }) });
    if (response.status === 429) { await appendFile(OUT, JSON.stringify({ id: row.id, cmdSha: row.cmdSha, status: "not_run", reason: "openrouter-429", latencyMs: Date.now() - started }) + "\n"); break; }
    const body = await response.text();
    const base = { id: row.id, cmdSha: row.cmdSha, status: "refused", model: MODEL, latencyMs: Date.now() - started };
    try {
      const parsed = JSON.parse(body); const scores = JSON.parse(parsed.choices[0].message.content); const vals = Object.fromEntries(Object.keys(RISK).map((key) => [key, Number(scores[key])])); const maxScore = Math.max(...Object.values(vals));
      await appendFile(OUT, JSON.stringify({ ...base, status: "scored", scores: vals, maxScore, freeFlag: maxScore > CUT, usage: parsed.usage ?? null }) + "\n");
    } catch { await appendFile(OUT, JSON.stringify({ ...base, reason: "invalid-answer" }) + "\n"); }
  }
}
await main();
