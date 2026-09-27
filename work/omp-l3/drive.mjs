import { createHash } from "node:crypto";
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const OUT = fileURLToPath(new URL("./frames.jsonl", import.meta.url));
const RECEIPT = fileURLToPath(new URL("./receipt.json", import.meta.url));
const TARGETS = new Set(["jev_rerank", "jev_claim_check", "jev_classify"]);
const CAP = 6;
const MAX_OBSERVED = 12;

const prompt = [
  "You are running a bounded L3 acceptance harness. Read only the public files named below; do not edit files.",
  "Call each requested tool exactly once in the order listed. After each call, continue to the next call.",
  "Healthy calls:",
  "1. jev_rerank: query exactly `Tax implications of holding EWU (or other such UK ETFs) as a US citizen?`; passages exactly the JSON array in kit/examples/rerank-candidates.json.",
  "2. jev_claim_check: claim exactly `A low percentage of hematopoietic progenitor cells are susceptible to HIV-1 infection ex vivo.`; evidence must be the complete text of kit/examples/scifact-evidence.txt.",
  "3. jev_classify: text and expected label from kit/examples/banking77-example.json; labels must be the complete array in kit/examples/banking77-labels.json.",
  "Refusal calls:",
  "4. jev_rerank: query `q`; passages must be 21 distinct non-empty strings, so the measured <=20 preflight refuses it.",
  "5. jev_claim_check: claim `A qualitative claim`; evidence must be the empty string, so input validation refuses it before Jev.",
  "6. jev_classify: text `late card`; labels must be exactly [`card arrival`], so the fewer-than-two-label preflight refuses it before Jev.",
  "Do not call any other custom tool. After the sixth target-tool result, stop and reply with only a short completion message.",
].join("\n");

function toolNameOf(frame) {
  if ((frame?.type === "tool_execution_start" || frame?.type === "tool_execution_end") && TARGETS.has(frame.toolName)) return frame.toolName;
  const xdev = frame?.message?.details?.xdev;
  if (xdev && TARGETS.has(xdev.tool)) return xdev.tool;
  if (frame?.type === "custom" && frame.data?.kind === "tool_call_observed" && TARGETS.has(frame.data.toolName)) return frame.data.toolName;
  return null;
}

function isTargetResult(frame) {
  return frame?.type === "tool_execution_end" && toolNameOf(frame) !== null
    || frame?.type === "message" && frame.message?.role === "toolResult" && toolNameOf(frame) !== null;
}

function targetFrame(frame) {
  return toolNameOf(frame) !== null;
}

function writeFilteredFrame(frame) {
  if (targetFrame(frame)) return true;
  if (frame?.type === "ready" || frame?.type === "agent_start" || frame?.type === "agent_end") return true;
  if (frame?.type === "response" && ["negotiate_protocol", "prompt"].includes(frame.command)) return true;
  return false;
}

function detailsOf(frame) {
  const details = frame?.result?.details ?? frame?.message?.details ?? {};
  return details?.xdev?.inner ?? details?.inner ?? details;
}

function textOf(frame) {
  return frame?.result?.content?.[0]?.text ?? frame?.message?.content?.[0]?.text ?? "";
}

function usageOf(details) {
  const usage = details?.usage;
  if (!usage || typeof usage !== "object") return null;
  const input = Number(usage.input_tokens);
  const output = Number(usage.output_tokens);
  if (!Number.isFinite(input) || !Number.isFinite(output)) return null;
  return { input_tokens: input, output_tokens: output };
}

const PROFILE = process.env.OMP_L3_PROFILE ?? "muse";
const child = spawn("omp", [`--profile=${PROFILE}`, "--cwd", ROOT, "--mode=rpc", "--max-time=420"], {
  cwd: ROOT,
  env: { ...process.env },
});
const frames = [];
let buffer = "";
let targetEnds = 0;
let killReason = null;
const startedAt = new Date().toISOString();

function consume(chunk) {
  buffer += chunk.toString();
  let newline;
  while ((newline = buffer.indexOf("\n")) >= 0) {
    const line = buffer.slice(0, newline).trim();
    buffer = buffer.slice(newline + 1);
    if (!line) continue;
    let frame;
    try {
      frame = JSON.parse(line);
    } catch {
      continue;
    }
    if (isTargetResult(frame)) {
      targetEnds += 1;
      if (targetEnds > MAX_OBSERVED && !killReason) {
        killReason = "target-cap-exceeded";
        child.kill("SIGKILL");
      }
    }
    if (writeFilteredFrame(frame)) frames.push(frame);
    if (targetEnds >= CAP && !killReason) {
      killReason = "six-target-results-observed";
      child.stdin.end();
    }
  }
}

child.stdout.on("data", consume);
child.stderr.on("data", () => {});
child.stdin.write(JSON.stringify({ id: "p1", type: "negotiate_protocol", protocolVersion: 2 }) + "\n");
child.stdin.write(JSON.stringify({ id: "s1", type: "prompt", message: prompt }) + "\n");
try {
  await new Promise((resolve) => child.on("close", resolve));
} catch (error) {
  killReason ??= error instanceof Error ? error.message : String(error);
}
if (buffer.trim()) consume("\n");

const calls = frames
  .filter((frame) => isTargetResult(frame))
  .map((frame, index) => {
    const details = detailsOf(frame);
    const usage = usageOf(details);
    return {
      sequence: index + 1,
      tool: toolNameOf(frame),
      isError: frame.isError === true,
      verdict: details.verdict ?? (index >= 3 ? "refused-by-schema" : null),
      top1: details.top1 ?? null,
      label: details.label ?? null,
      choice: details.choice ?? null,
      selectedIndex: details.selectedIndex ?? null,
      model: details.model ?? null,
      threshold: details.threshold ?? null,
      reason: details.reason ?? null,
      value: details.value ?? null,
      latencyMs: details.latencyMs ?? null,
      usage,
      calledModel: usage !== null,
      text: textOf(frame),
    };
  });

const inputTokens = calls.reduce((sum, call) => sum + (call.usage?.input_tokens ?? 0), 0);
const outputTokens = calls.reduce((sum, call) => sum + (call.usage?.output_tokens ?? 0), 0);
const filtered = frames.map((frame) => JSON.stringify(frame)).join("\n") + "\n";
writeFileSync(OUT, filtered);
const receipt = {
  schema: "jev-omp-l3/v1",
  preregistration: "work/omp-l3/PREREG.md",
  startedAt,
  finishedAt: new Date().toISOString(),
  sessionId: null,
  processExit: child.exitCode,
  stopReason: killReason,
  targetResults: targetEnds,
  calls,
  totals: {
    input_tokens: inputTokens,
    output_tokens: outputTokens,
    estimated_input_spend_usd: inputTokens * 0.042 / 1_000_000,
    output_spend_usd: 0,
  },
  frames_sha256: createHash("sha256").update(filtered, "utf8").digest("hex"),
};
writeFileSync(RECEIPT, `${JSON.stringify(receipt, null, 2)}\n`);

for (const call of calls) process.stdout.write(JSON.stringify(call) + "\n");
process.stdout.write(JSON.stringify({ targetResults: targetEnds, stopReason: killReason, input_tokens: inputTokens, output_tokens: outputTokens, estimated_input_spend_usd: receipt.totals.estimated_input_spend_usd }) + "\n");
const healthy = calls.filter((call) => call.calledModel && !call.isError);
const refused = calls.filter((call) => !call.calledModel && ["not_run", "refused-by-schema"].includes(call.verdict));
process.exit(healthy.length >= 3 && refused.length >= 3 ? 0 : 1);
