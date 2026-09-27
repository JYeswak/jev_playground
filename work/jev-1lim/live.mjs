#!/usr/bin/env node
import {appendFile, readFile} from "node:fs/promises";
import {createHash} from "node:crypto";
import {askJevBundle} from "../../kit/src/client.ts";
import {RISK, STATE_CONTEXT, CUT} from "../bicameral-gate/questions.mjs";

const ROOT = new URL("../..", import.meta.url);
const RAW = new URL("var/agent-tmp/jev-1lim/commands-A.jsonl", ROOT);
const MANIFEST = new URL("work/jev-1lim/manifest.jsonl", ROOT);
const LABEL_A = new URL("work/jev-1lim/labels-A.jsonl", ROOT);
const LABEL_B = new URL("work/jev-1lim/labels-B.jsonl", ROOT);
const ADJUDICATED = new URL("work/jev-1lim/adjudicated.jsonl", ROOT);
const OUT = new URL(process.env.JEV_1LIM_OUT ?? "var/agent-tmp/jev-1lim/live-rows.jsonl", ROOT);

const PREREG = new URL("work/jev-1lim/PREREG-QSA6.md", ROOT);
const REACH = new URL("work/jev-1lim/reach-receipt-qsa6.json", ROOT);
const LAUNCH_AFTER = Date.parse("2026-09-30T00:00:00Z");
async function assertLaunchReady() {
  if (Date.now() < LAUNCH_AFTER) throw new Error("jev-qsa6 launch refused before 2026-09-30T00:00:00Z");
  const preregText = await readFile(PREREG, "utf8");
  const preregSha = createHash("sha256").update(preregText).digest("hex");
  const reach = JSON.parse(await readFile(REACH, "utf8"));
  if (reach.status !== "REACHABLE" || reach.mode !== "mcnemar" || reach.prereg_sha256 !== preregSha) throw new Error("jev-qsa6 reach receipt is not bound to the current prereg");
}
await assertLaunchReady();
const parseJsonl = async (url) => (await readFile(url, "utf8")).split("\n").filter(Boolean).map(JSON.parse);
const raw = await parseJsonl(RAW);
const manifest = await parseJsonl(MANIFEST);
const a = Object.fromEntries((await parseJsonl(LABEL_A)).map((row) => [row.id, row.label]));
const b = Object.fromEntries((await parseJsonl(LABEL_B)).map((row) => [row.id, row.label]));
const adjudicated = Object.fromEntries((await parseJsonl(ADJUDICATED)).map((row) => [row.id, row.final_label]));
const finalLabel = (id) => a[id] === b[id] ? a[id] : adjudicated[id];
const commands = Object.fromEntries(raw.map((row) => [row.id, row.command]));
const rows = manifest
  .map((row) => ({...row, label: finalLabel(row.id), command: commands[row.id]}))
  .filter((row) => row.label === "no-harm" || row.label.startsWith("harm:"));
const seen = new Set((await (async () => { try { return await parseJsonl(OUT); } catch { return []; } })()).map((row) => row.id));
const pending = rows.filter((row) => !seen.has(row.id));
const now = () => new Date().toISOString();

for (const row of pending) {
  const started = Date.now();
  const result = await askJevBundle({
    state: {command: row.command, context: STATE_CONTEXT},
    questions: RISK,
    model: "jev-1.13.0",
    timeoutMs: 10000,
    retry: {maxRetries: 0},
  });
  const base = {id: row.id, cmdSha: row.cmdSha, existingFlag: row.existing_flag, label: row.label, sampleSource: row.sample_source, model: "jev-1.13.0", recordedAt: now()};
  if (!result.ok) {
    await appendFile(OUT, JSON.stringify({...base, status: "refused", reason: result.reason, error: result.error, latencyMs: result.latencyMs}) + "\n");
    continue;
  }
  const scores = Object.fromEntries(Object.entries(result.answers).map(([key, answer]) => [key, answer.noul]));
  const maxScore = Math.max(...Object.values(scores));
  await appendFile(OUT, JSON.stringify({...base, status: "scored", jevFlag: maxScore > CUT, maxScore, scores, resolvedModel: result.resolvedModel, latencyMs: result.latencyMs, usage: result.usage ?? null, wallMs: Date.now() - started}) + "\n");
}
const rowsOut = await parseJsonl(OUT);
const refused = rowsOut.filter((row) => row.status !== "scored").length;
console.log(JSON.stringify({model: "jev-1.13.0", requested: rows.length, completed: rowsOut.length, scored: rowsOut.length - refused, refused}));
