import { createHash } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";

const sessionPath = process.argv[2];
if (!sessionPath) throw new Error("usage: node work/omp-l3/recover.mjs PROFILE_SESSION.jsonl");
const framesPath = new URL("./frames.jsonl", import.meta.url);
const receiptPath = new URL("./receipt.json", import.meta.url);
const targetTools = new Set(["jev_rerank", "jev_claim_check", "jev_classify"]);
const records = readFileSync(sessionPath, "utf8").split("\n").filter(Boolean).flatMap((line) => {
  try {
    return [JSON.parse(line)];
  } catch {
    return [];
  }
});
const session = records.find((record) => Object.prototype.hasOwnProperty.call(record, "cwd") && Object.prototype.hasOwnProperty.call(record, "version"));
const calls = [];
const filtered = [];

for (const record of records) {
  if (record.type === "session") filtered.push({ type: "session", id: record.id, cwd: record.cwd, timestamp: record.timestamp });
  if (record.type !== "message" || record.message?.role !== "toolResult") continue;
  const xdev = record.message?.details?.xdev;
  const tool = xdev?.tool;
  if (!targetTools.has(tool)) continue;
  const inner = xdev.inner ?? null;
  const content = record.message.content ?? [];
  const text = content.map((item) => item?.text ?? "").join("\n");
  const usage = inner?.usage && Number.isFinite(Number(inner.usage.input_tokens)) && Number.isFinite(Number(inner.usage.output_tokens))
    ? { input_tokens: Number(inner.usage.input_tokens), output_tokens: Number(inner.usage.output_tokens) }
    : null;
  const sequence = calls.length + 1;
  const phase = sequence <= 3 ? "healthy" : "refusal";
  const result = {
    type: "tool_execution_end",
    recovered: true,
    sequence,
    phase,
    toolName: tool,
    result: { content, details: xdev },
  };
  filtered.push(result);
  calls.push({
    sequence,
    phase,
    tool,
    isError: false,
    verdict: inner?.verdict ?? (phase === "refusal" ? "refused-by-schema" : null),
    top1: inner?.top1 ?? null,
    label: inner?.label ?? null,
    choice: inner?.choice ?? null,
    selectedIndex: inner?.selectedIndex ?? null,
    model: inner?.model ?? null,
    threshold: inner?.threshold ?? null,
    reason: inner?.reason ?? (phase === "refusal" ? text.split("\n")[0] : null),
    value: inner?.value ?? null,
    latencyMs: inner?.latencyMs ?? null,
    usage,
    calledModel: usage !== null,
    text,
  });
}

const inputTokens = calls.reduce((sum, call) => sum + (call.usage?.input_tokens ?? 0), 0);
const outputTokens = calls.reduce((sum, call) => sum + (call.usage?.output_tokens ?? 0), 0);
const frames = filtered.map((frame) => JSON.stringify(frame)).join("\n") + "\n";
writeFileSync(framesPath, frames);
const receipt = {
  schema: "jev-omp-l3/v1",
  preregistration: "work/omp-l3/PREREG.md",
  recoveredFromSession: sessionPath,
  sessionId: session?.id ?? null,
  calls,
  totals: {
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    estimated_input_spend_usd: inputTokens * 0.042 / 1_000_000,
    output_spend_usd: 0,
  },
  frames_sha256: createHash("sha256").update(frames, "utf8").digest("hex"),
  notes: [
    "The RPC session's custom-tool surface is represented as write->xd://... in OMP transcript records; xdev.tool is the authoritative tool name.",
    "The three refusal inputs were rejected by OMP schema validation before tool execute, so they have no inner details or Jev usage; receipt verdict is refused-by-schema.",
  ],
};
writeFileSync(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`);
for (const call of calls) process.stdout.write(JSON.stringify(call) + "\n");
process.stdout.write(JSON.stringify({ calls: calls.length, input_tokens: inputTokens, output_tokens: outputTokens, estimated_input_spend_usd: receipt.totals.estimated_input_spend_usd }) + "\n");
if (calls.length !== 6 || calls.slice(0, 3).some((call) => !call.calledModel) || calls.slice(3).some((call) => call.calledModel)) process.exit(1);
