// L3 for the numeric-scope refusal (bead jev-5cz). One fresh `omp --mode=rpc` session from the
// repo root with NO --profile flag, key from the environment. The model reads a receipt and calls
// jev_claim_check twice with its full text as evidence: once on a numeric claim, which must be
// refused (numeric-out-of-scope, calledModel=false, no verdict), and once on a qualitative claim,
// which must be answered (calledModel=true, a verdict).
// Hard cap: SIGKILL after 4 jev_claim_check executions. Writes l3-scope-frames.jsonl.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//        node work/jev-claim-check/l3-scope-drive.mjs
// Exit 0 when both directions hold, 1 otherwise, 2 without a key.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const FRAMES = new URL("l3-scope-frames.jsonl", import.meta.url);
const RECEIPT = "docs/demos/upstream-repro/typesafe-sdk-js-w70-20260923.md";
const NUMERIC = "Its own suite passes 189 tests and still exits 1 on unhandled aborts.";
const QUALITATIVE = "The clone was left untouched, and every probe and defect lived in /tmp.";
const CAP = 4;

if (!process.env.TYPESAFE_API_KEY) {
  console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No session started.");
  process.exit(2);
}

const prompt = [
  `Read the file ${RECEIPT} in full.`,
  "Then call the jev_claim_check tool exactly twice, using that file's full text as `evidence` both times:",
  `first with claim: "${NUMERIC}"`,
  `then with claim: "${QUALITATIVE}"`,
  "Do not call any other tool after that. Reply with ONLY the text jev_claim_check returned each time, in order.",
].join("\n");

const isCheck = (f) => f.type === "tool_execution_end" && JSON.stringify(f).includes("jev_claim_check") && !JSON.stringify(f).includes("# jev_claim_check");
const frames = [];
const child = spawn("omp", ["--mode=rpc", "--max-time=420"], { cwd: ROOT, env: { ...process.env } });
let buf = "";
child.stdout.on("data", (d) => {
  buf += d.toString();
  let idx;
  while ((idx = buf.indexOf("\n")) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    let f;
    try { f = JSON.parse(line); } catch { f = { _raw: line.slice(0, 200) }; }
    frames.push(f);
    if (frames.filter(isCheck).length > CAP) { try { child.kill("SIGKILL"); } catch {} }
    if (f.type === "agent_end" && f.isTerminal !== false && frames.some((x) => x.type === "agent_start")) child.stdin.end();
  }
});
child.stderr.on("data", () => {});
const timer = setTimeout(() => { try { child.kill("SIGKILL"); } catch {} }, 440000);
child.stdin.write(JSON.stringify({ id: "p1", type: "negotiate_protocol", protocolVersion: 2 }) + "\n");
child.stdin.write(JSON.stringify({ id: "s1", type: "prompt", message: prompt }) + "\n");
await new Promise((resolve) => child.on("close", resolve));
clearTimeout(timer);
writeFileSync(FRAMES, frames.map((f) => JSON.stringify(f)).join("\n") + "\n");

const checks = frames.filter(isCheck).map((f) => {
  const d = f.result?.details ?? {};
  const inner = d.xdev?.inner ?? d;
  const args = d.xdev?.args ?? {};
  return { claim: args.claim ?? null, text: f.result?.content?.[0]?.text ?? "", verdict: inner.verdict, reason: inner.reason, calledModel: inner.calledModel, probability: inner.probability };
});
for (const c of checks) console.log(JSON.stringify(c));
const n = checks.find((c) => c.claim === NUMERIC);
const q = checks.find((c) => c.claim === QUALITATIVE);
const refusedOk = n?.verdict === "refused" && n?.reason === "numeric-out-of-scope" && n?.calledModel === false;
const answeredOk = q?.calledModel === true && ["supported", "unsupported", "unsure"].includes(q?.verdict);
console.log(`frames=${frames.length} checks=${checks.length} numeric=${n?.verdict ?? "absent"}/${n?.reason ?? "-"} qualitative=${q?.verdict ?? "absent"} -> ${refusedOk && answeredOk ? "L3 BAR MET" : "L3 BAR MISSED"}`);
process.exit(refusedOk && answeredOk ? 0 : 1);
