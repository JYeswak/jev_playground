// Compaction need measurement (bead jev-x86y): does Jev-driven compaction drop a tool call a later
// turn needed? Rules are preregistered in docs/demos/upstream-repro/compaction-need-20260924.md.
//
//   node --experimental-strip-types work/compaction-need/need.ts select    # writes sessions.json (sampled, sha-pinned)
//   node --experimental-strip-types work/compaction-need/need.ts packets   # labelling packets under /tmp, no Jev
//   node --experimental-strip-types work/compaction-need/need.ts replay --live   # after labels are committed
//
// For each sampled session: the omp file -> adaptOmpTranscript -> the PREFIX ends at the message that
// holds the result of the CUT_CALLS-th paired tool call; the HORIZON is the next HORIZON_MESSAGES
// messages. Labellers judge each prefix call against the horizon. The replay compacts the prefix
// with the library (the same options as compaction/src/replay.ts, model pinned) and records each
// call's decision, joined to labels by tool_use_id. No text from any session is written into the repo.
import { spawnSync } from "node:child_process";
import { createHash, timingSafeEqual } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { adaptOmpTranscript } from "../../compaction/src/omp-adapter.ts";
import { collectToolCalls, compactMessages } from "../../fast-jev-compaction/dist/index.js";
import type { Message, ToolCall } from "../../fast-jev-compaction/dist/index.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const HOME = homedir();
const SESSIONS = join(HERE, "sessions.json");
const PACKETS = "/tmp/x86y-packets";
const LABELS = [join(HERE, "labels-1.jsonl"), join(HERE, "labels-2.jsonl"), join(HERE, "labels-adjudicated.jsonl")];
export const CUT_CALLS = 40;
export const HORIZON_MESSAGES = 40;
export const MIN_CALLS = 50;
export const SIZE = [200_000, 3_000_000];
export const SAMPLE = 6;
export const SEED = 20260924;
// File B of jev-0c6 (its outcome was seen), and file A (too small; its outcome was seen).
export const EXCLUDE = ["01a0d3a7", "01a0b735"];
export const OPTIONS = { keepThreshold: 0.5, maxStateTokens: 20000, truncateHeadChars: 500, preserveRecentMessages: 6, model: "jev-1.13.0" };
export const CUTOFF = "2026-09-24T17:00:00Z"; // only files last written before this are eligible (a still-open session is not)

const untilde = (p: string) => p.replace(/^~/, HOME);

function sessionFiles(): string[] {
  const roots = [join(HOME, ".omp/agent/sessions/-Developer-jev")];
  const profiles = join(HOME, ".omp/profiles");
  if (existsSync(profiles)) {
    for (const p of readdirSync(profiles)) roots.push(join(profiles, p, "agent/sessions/-Developer-jev"));
  }
  const out: string[] = [];
  for (const r of roots) {
    if (!existsSync(r)) continue;
    for (const f of readdirSync(r)) if (f.endsWith(".jsonl")) out.push(join(r, f));
  }
  return out.sort();
}

function load(file: string) {
  const events = readFileSync(file, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
  return adaptOmpTranscript(events).messages;
}

/** The prefix (through the message holding the CUT_CALLS-th paired result) and the horizon after it. */
export function cut(messages: readonly Message[]) {
  const calls = collectToolCalls(messages, 0);
  if (calls.length < MIN_CALLS) return null;
  const end = calls[CUT_CALLS - 1].resultIndex;
  const prefix = messages.slice(0, end + 1);
  const horizon = messages.slice(end + 1, end + 1 + HORIZON_MESSAGES);
  return { prefix, horizon, prefixCalls: collectToolCalls(prefix, OPTIONS.preserveRecentMessages) };
}

// A small seeded generator (mulberry32) so the sample can be re-drawn from the committed seed.
function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function select() {
  if (existsSync(SESSIONS)) {
    console.log("REFUSED: sessions.json exists; the sample is fixed");
    return 1;
  }
  const eligible: { path: string; id: string; bytes: number; calls: number; sha256: string }[] = [];
  const skipped: Record<string, number> = {};
  const skip = (why: string) => (skipped[why] = (skipped[why] ?? 0) + 1);
  for (const f of sessionFiles()) {
    const st = statSync(f);
    const id = basename(f).split("_")[1]?.slice(0, 8) ?? "";
    if (EXCLUDE.includes(id)) { skip("excluded id"); continue; }
    if (st.mtime.toISOString() >= CUTOFF) { skip("written after CUTOFF"); continue; }
    if (st.size < SIZE[0] || st.size > SIZE[1]) { skip("size outside 200KB-3MB"); continue; }
    const messages = load(f);
    const calls = collectToolCalls(messages, 0).length;
    if (calls < MIN_CALLS) { skip(`fewer than ${MIN_CALLS} paired tool calls`); continue; }
    eligible.push({ path: f.replace(HOME, "~"), id, bytes: st.size, calls, sha256: createHash("sha256").update(readFileSync(f)).digest("hex") });
  }
  const draw = rng(SEED);
  const pool = [...eligible];
  const picked = [];
  while (picked.length < SAMPLE && pool.length) picked.push(pool.splice(Math.floor(draw() * pool.length), 1)[0]);
  picked.sort((a, b) => a.path.localeCompare(b.path));
  writeFileSync(SESSIONS, JSON.stringify({ seed: SEED, cutoff: CUTOFF, eligible: eligible.length, skipped, sessions: picked }, null, 2) + "\n");
  console.log(JSON.stringify({ sessions: SESSIONS, eligible: eligible.length, picked: picked.map((p) => `${p.id} ${p.calls}`), skipped }));
  return 0;
}

/** The sampled sessions minus excluded.json's (amendment A1); an excluded file is never read. */
function sessions() {
  const s = JSON.parse(readFileSync(SESSIONS, "utf8"));
  const excludedFile = join(HERE, "excluded.json");
  const excluded: Record<string, string> = existsSync(excludedFile) ? JSON.parse(readFileSync(excludedFile, "utf8")) : {};
  const kept = s.sessions.filter((x: { id: string }) => !(x.id in excluded));
  for (const x of kept) {
    const bytes = readFileSync(untilde(x.path));
    const got = createHash("sha256").update(bytes).digest();
    if (!timingSafeEqual(got, Buffer.from(x.sha256, "hex"))) throw new Error(`REFUSED: ${x.path} changed since it was sampled`);
  }
  return kept;
}

const clip = (s: string, n: number) => (s.length > n ? `${s.slice(0, n)} …[${s.length - n} more chars]` : s);

function render(m: Message): string {
  const parts = [`### ${m.role}`];
  if (m.text) parts.push(clip(m.text, 2000));
  for (const u of m.toolUses ?? []) parts.push(`TOOL CALL ${u.tool_use_id} ${u.tool}: ${clip(JSON.stringify(u.input), 800)}`);
  for (const r of m.toolResults ?? []) parts.push(`TOOL RESULT ${r.tool_use_id}: ${clip(r.text ?? "", 1500)}`);
  return parts.join("\n");
}

function packets() {
  if (existsSync(join(HERE, "calls.json"))) {
    console.log("REFUSED: calls.json exists; the call set is fixed (labels refer to it)");
    return 1;
  }
  mkdirSync(PACKETS, { recursive: true });
  const index = [];
  for (const s of sessions()) {
    const c = cut(load(untilde(s.path)));
    if (!c) throw new Error(`${s.id}: fewer than ${MIN_CALLS} calls`);
    const results = new Map<string, string>();
    for (const m of c.prefix) for (const r of m.toolResults ?? []) results.set(r.tool_use_id, r.text ?? "");
    const lines = [
      `# Session ${s.id}: ${c.prefixCalls.length} prefix tool calls to label, horizon of ${c.horizon.length} messages`,
      "",
      "## Prefix tool calls (label each one)",
    ];
    for (const call of c.prefixCalls) {
      lines.push(`\n#### ${call.tool_use_id} (${call.tool})`, `INPUT: ${clip(JSON.stringify(call.input), 1500)}`, `RESULT: ${clip(results.get(call.tool_use_id) ?? "", 3000)}`);
    }
    lines.push("", "## Horizon: the messages after the cut", "");
    c.horizon.forEach((m, k) => lines.push(`<!-- horizon ${k} -->`, render(m), ""));
    const file = join(PACKETS, `${s.id}.md`);
    writeFileSync(file, lines.join("\n"));
    index.push({
      session: s.id,
      packet: file,
      horizon_messages: c.horizon.length,
      calls: c.prefixCalls.map((x: ToolCall) => ({ tool_use_id: x.tool_use_id, tool: x.tool, pinned: x.pinned })),
    });
  }
  writeFileSync(join(PACKETS, "index.json"), JSON.stringify(index, null, 2) + "\n");
  // Ids, tool names and the pinned flag only: the set need.py checks labels against. No session text.
  writeFileSync(join(HERE, "calls.json"), JSON.stringify(index.map(({ packet, ...rest }) => rest), null, 2) + "\n");
  console.log(JSON.stringify({ packets: PACKETS, sessions: index.map((i) => `${i.session}: ${i.calls.length} calls`) }));
  return 0;
}

function labelsCommitted() {
  const need = LABELS.slice(0, 2);
  for (const f of need) {
    if (!existsSync(f)) return `${basename(f)} does not exist`;
    const rel = f.slice(ROOT.length + 1);
    const logged = spawnSync("git", ["-C", ROOT, "log", "-1", "--format=%h", "--", rel], { encoding: "utf8" }).stdout.trim();
    const clean = spawnSync("git", ["-C", ROOT, "diff", "--quiet", "HEAD", "--", rel]).status === 0;
    if (!logged || !clean) return `${basename(f)} is not committed and clean`;
  }
  const ready = spawnSync("python3", [join(HERE, "need.py"), "ready"], { encoding: "utf8" });
  if (ready.status !== 0) return (ready.stdout || ready.stderr).trim();
  return null;
}

async function replay() {
  if (!process.argv.includes("--live")) {
    console.log("NOT_RUN: the replay makes live Jev calls; rerun with --live under `infisical run` once labels are committed");
    return 2;
  }
  const blocked = labelsCommitted();
  if (blocked) {
    console.log(`REFUSED: ${blocked}`);
    return 1;
  }
  const apiKey = process.env.TYPESAFE_API_KEY;
  if (!apiKey) {
    console.log("NOT_RUN reason=unconfigured: TYPESAFE_API_KEY is not in the environment");
    return 2;
  }
  const out = [];
  let input = 0;
  let requests = 0;
  for (const s of sessions()) {
    const c = cut(load(untilde(s.path)))!;
    const inputTokens: number[] = [];
    const recording: typeof fetch = async (u, init) => {
      const res = await fetch(u, init);
      const body: unknown = await res.clone().json().catch(() => null);
      const usage = body && typeof body === "object" && "usage" in body ? body.usage : null;
      const tokens = usage && typeof usage === "object" && "input_tokens" in usage ? Number(usage.input_tokens) : 0;
      inputTokens.push(Number.isFinite(tokens) ? tokens : 0);
      return res;
    };
    const result = await compactMessages(c.prefix, { ...OPTIONS, apiKey, fetch: recording });
    const byId = new Map(c.prefixCalls.map((x: ToolCall) => [x.id, x.tool_use_id]));
    for (const d of result.decisions) {
      out.push({ session: s.id, tool_use_id: byId.get(d.id), action: d.action, reason: d.reason, keepCall: d.keepCall, keepResult: d.keepResult });
    }
    requests += result.stats.requests;
    input += inputTokens.reduce((a, t) => a + t, 0);
    console.error(`${s.id}: ${result.stats.calls} calls, ${result.stats.kept} kept, ${result.stats.resultsDropped} results dropped, ${result.stats.callsDropped} calls dropped, ${result.stats.pinned} pinned, ${result.stats.requests} requests`);
  }
  writeFileSync(join(HERE, "decisions.jsonl"), out.map((r) => JSON.stringify(r)).join("\n") + "\n");
  writeFileSync(join(HERE, "decisions-pass.json"), JSON.stringify({ lane: "live", model: OPTIONS.model, at: new Date().toISOString(), requests, input_tokens: input, spend_usd: +(input * 0.042 / 1e6).toFixed(6) }, null, 2) + "\n");
  console.log(JSON.stringify({ decisions: out.length, requests, receipt: join(HERE, "decisions-pass.json") }));
  return 0;
}

const mode = process.argv[2];
const code = mode === "select" ? select() : mode === "packets" ? packets() : mode === "replay" ? await replay() : (console.log("usage: need.ts select|packets|replay --live"), 64);
process.exit(code);
