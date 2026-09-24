// L3 driver for jev_claim_check (bead jev-sp5). One fresh `omp --mode=rpc` session from the repo
// root, key from the environment (run under infisical). The model reads a receipt and calls the
// tool twice: the README sentence that receipt proves, and a planted false twin.
// Bar: docs/demos/upstream-repro/jev-claim-check-20260924.md (L3 paragraph), committed first.
// Hard cap: SIGKILL after 4 jev_claim_check executions. Writes l3-frames.jsonl.
// Run: infisical run --silent --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- \
//        node work/jev-claim-check/l3-drive.mjs
// Exit 0 when true -> supported and false -> unsupported, 1 otherwise, 2 without a key.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../../", import.meta.url));
const FRAMES = new URL("l3-frames.jsonl", import.meta.url);
const RECEIPT = "docs/demos/upstream-repro/typesafe-sdk-js-w70-20260923.md";
const TRUE_CLAIM = "Its own suite passes 189 tests and still exits 1 on unhandled aborts.";
const FALSE_CLAIM = "Its own suite passes 189 tests and exits 0 with no unhandled aborts.";
const CAP = 4;

if (!process.env.TYPESAFE_API_KEY) {
  console.error("TYPESAFE_API_KEY unset: run under infisical run (see header). No session started.");
  process.exit(2);
}

const prompt = [
  `Read the file ${RECEIPT} in full.`,
  "Then call the jev_claim_check tool exactly twice, using that file's full text as `evidence` both times:",
  `first with claim: "${TRUE_CLAIM}"`,
  `then with claim: "${FALSE_CLAIM}"`,
  "Do not call any other tool after that. Reply with ONLY the two lines jev_claim_check returned, in order.",
].join("\n");

const isCheck = (f) => f.type === "tool_execution_end" && JSON.stringify(f).includes("jev_claim_check") && !JSON.stringify(f).includes("# jev_claim_check");
const frames = [];
const child = spawn("omp", ["--profile=muse", "--mode=rpc", "--max-time=420"], { cwd: ROOT, env: { ...process.env } });
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
  return { claim: args.claim ?? null, evidenceChars: typeof args.evidence === "string" ? args.evidence.length : null, text: f.result?.content?.[0]?.text ?? "", verdict: inner.verdict, probability: inner.probability, isError: f.isError };
});
for (const c of checks) console.log(JSON.stringify(c));
const t = checks.find((c) => c.claim === TRUE_CLAIM);
const n = checks.find((c) => c.claim === FALSE_CLAIM);
const ok = t?.verdict === "supported" && n?.verdict === "unsupported";
console.log(`frames=${frames.length} checks=${checks.length} true=${t?.verdict ?? "absent"} false=${n?.verdict ?? "absent"} -> ${ok ? "L3 BAR MET" : "L3 BAR MISSED"}`);
process.exit(ok ? 0 : 1);
