// Held-out test of keep rule C3 (bead jev-5720): keep a tool result when Jev's keepCall >= T_C3,
// with T_C3 fixed on the development sets (jev-x86y, jev-jec6). Rules are preregistered in
// docs/demos/upstream-repro/compaction-c3-20260924.md.
//
//   node --experimental-strip-types work/compaction-c3/c3.ts select    # seeded sample + rider screen -> sessions.json
//   node --experimental-strip-types work/compaction-c3/c3.ts packets   # /tmp/c3-packets (never committed) + calls.json (ids)
//   node --experimental-strip-types work/compaction-c3/c3.ts replay --live   # after labels are final
//
// Same cut and label as jev-x86y (need.ts cut()); one library compactMessages call per session, whose
// per-call keepResult gives C0 and C1 and whose keepCall gives C3.
import { spawnSync } from "node:child_process";
import { createHash, timingSafeEqual } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { collectToolCalls, compactMessages } from "../../fast-jev-compaction/dist/index.js";
import type { ToolCall } from "../../fast-jev-compaction/dist/index.js";
import { riderHits } from "../compaction-keep/keep.ts";
import { clip, cut, EXCLUDE, load, MIN_CALLS, OPTIONS, render, rng, sessionFiles, untilde } from "../compaction-need/need.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const HOME = homedir();
const SESSIONS = join(HERE, "sessions.json");
const CALLS = join(HERE, "calls.json");
const PACKETS = "/tmp/c3-packets";
export const CUTOFF = "2026-09-24T18:00:00Z";
export const SEED = 20260926;
export const SAMPLE = 8;
// The 200KB-3MB jev pool is exhausted by jev-x86y and jev-jec6; the upper bound is raised to 12 MB.
export const SIZE = [200_000, 12_000_000];

function committed(path: string): boolean {
  const rel = path.slice(ROOT.length + 1);
  const logged = spawnSync("git", ["-C", ROOT, "log", "-1", "--format=%h", "--", rel], { encoding: "utf8" }).stdout.trim();
  return Boolean(logged) && spawnSync("git", ["-C", ROOT, "diff", "--quiet", "HEAD", "--", rel]).status === 0;
}

/** Every session id a development set sampled, screened or saw, plus jev-0c6's files A and B. */
function usedSessions(): Set<string> {
  const used = new Set<string>(EXCLUDE);
  for (const rel of ["work/compaction-need/sessions.json", "work/compaction-keep/sessions.json"]) {
    const s = JSON.parse(readFileSync(join(ROOT, rel), "utf8"));
    for (const x of s.sessions) used.add(x.id);
    for (const x of s.screened_out_rider ?? []) used.add(x.id);
  }
  return used;
}

function select() {
  if (existsSync(SESSIONS) && committed(SESSIONS)) {
    console.log("REFUSED: sessions.json is committed; the sample is fixed");
    return 1;
  }
  const used = usedSessions();
  const eligible: { path: string; id: string; bytes: number; calls: number; sha256: string }[] = [];
  const skipped: Record<string, number> = {};
  const skip = (why: string) => (skipped[why] = (skipped[why] ?? 0) + 1);
  for (const f of sessionFiles()) {
    const st = statSync(f);
    // 13 characters (two uuid groups): the 8-character form jev-x86y and jev-jec6 used collides here
    // (three sessions started within 8 s share 01a0c742). The development sets' ids are 8 characters.
    const id = basename(f).split("_")[1]?.slice(0, 13) ?? "";
    if (used.has(id.slice(0, 8))) { skip("used by a development set or jev-0c6"); continue; }
    if (st.mtime.toISOString() >= CUTOFF) { skip("written after CUTOFF"); continue; }
    if (st.size < SIZE[0] || st.size > SIZE[1]) { skip("size outside 200KB-12MB"); continue; }
    const calls = collectToolCalls(load(f), 0).length;
    if (calls < MIN_CALLS) { skip(`fewer than ${MIN_CALLS} paired tool calls`); continue; }
    eligible.push({ path: f.replace(HOME, "~"), id, bytes: st.size, calls, sha256: createHash("sha256").update(readFileSync(f)).digest("hex") });
  }
  const ids = eligible.map((e) => e.id);
  if (new Set(ids).size !== ids.length) {
    console.log(`REFUSED: two eligible sessions share an id: ${ids.filter((x, i) => ids.indexOf(x) !== i)}`);
    return 1;
  }
  const draw = rng(SEED);
  const pool = [...eligible];
  const order = [];
  while (pool.length) order.push(pool.splice(Math.floor(draw() * pool.length), 1)[0]);
  const picked = [];
  const screened = [];
  for (const s of order) {
    if (picked.length >= SAMPLE) break;
    const c = cut(load(untilde(s.path)))!;
    const hits = riderHits(c.prefix, c.horizon);
    if (hits > 0) screened.push({ id: s.id, rider_path_calls: hits });
    else picked.push(s);
  }
  picked.sort((a, b) => a.path.localeCompare(b.path));
  writeFileSync(SESSIONS, JSON.stringify({ seed: SEED, cutoff: CUTOFF, size: SIZE, eligible: eligible.length, skipped, screened_out_rider: screened, sessions: picked }, null, 2) + "\n");
  console.log(JSON.stringify({ eligible: eligible.length, picked: picked.map((p) => `${p.id} ${p.calls}`), screened_out_rider: screened, skipped }));
  return 0;
}

function sessions() {
  const s = JSON.parse(readFileSync(SESSIONS, "utf8"));
  for (const x of s.sessions) {
    const got = createHash("sha256").update(readFileSync(untilde(x.path))).digest();
    if (!timingSafeEqual(got, Buffer.from(x.sha256, "hex"))) throw new Error(`REFUSED: ${x.path} changed since it was sampled`);
  }
  return s.sessions;
}

function packets() {
  if (existsSync(CALLS) && committed(CALLS)) {
    console.log("REFUSED: calls.json is committed; the call set is fixed (labels refer to it)");
    return 1;
  }
  mkdirSync(PACKETS, { recursive: true });
  const index = [];
  for (const s of sessions()) {
    const c = cut(load(untilde(s.path)))!;
    if (riderHits(c.prefix, c.horizon) > 0) throw new Error(`REFUSED: ${s.id} fails the rider screen`);
    const results = new Map<string, string>();
    for (const m of c.prefix) for (const r of m.toolResults ?? []) results.set(r.tool_use_id, r.text ?? "");
    const lines = [`# Session ${s.id}: ${c.prefixCalls.length} prefix tool calls to label, horizon of ${c.horizon.length} messages`, "", "## Prefix tool calls (label each one)"];
    for (const call of c.prefixCalls) {
      lines.push(`\n#### ${call.tool_use_id} (${call.tool})`, `INPUT: ${clip(JSON.stringify(call.input), 1500)}`, `RESULT: ${clip(results.get(call.tool_use_id) ?? "", 3000)}`);
    }
    lines.push("", "## Horizon: the messages after the cut", "");
    c.horizon.forEach((m, k) => lines.push(`<!-- horizon ${k} -->`, render(m), ""));
    const file = join(PACKETS, `${s.id}.md`);
    writeFileSync(file, lines.join("\n"));
    index.push({ session: s.id, packet: file, horizon_messages: c.horizon.length, calls: c.prefixCalls.map((x: ToolCall) => ({ tool_use_id: x.tool_use_id, tool: x.tool, pinned: x.pinned })) });
  }
  writeFileSync(join(PACKETS, "index.json"), JSON.stringify(index, null, 2) + "\n");
  writeFileSync(CALLS, JSON.stringify(index.map(({ packet, ...rest }) => rest), null, 2) + "\n");
  console.log(JSON.stringify({ packets: PACKETS, sessions: index.map((i) => `${i.session}: ${i.calls.length} calls`) }));
  return 0;
}

async function replay() {
  if (!process.argv.includes("--live")) {
    console.log("NOT_RUN: the replay makes live Jev calls; rerun with --live under `infisical run` once labels are final");
    return 2;
  }
  const ready = spawnSync("python3", [join(HERE, "c3.py"), "ready"], { encoding: "utf8" });
  if (ready.status !== 0) {
    console.log(`REFUSED: ${(ready.stdout || ready.stderr).trim()}`);
    return 1;
  }
  const apiKey = process.env.TYPESAFE_API_KEY;
  if (!apiKey) {
    console.log("NOT_RUN reason=unconfigured: TYPESAFE_API_KEY is not in the environment");
    return 2;
  }
  const inputTokens: number[] = [];
  const recording: typeof fetch = async (u, init) => {
    const res = await fetch(u, init);
    const body: unknown = await res.clone().json().catch(() => null);
    const usage = body && typeof body === "object" && "usage" in body ? body.usage : null;
    const tokens = usage && typeof usage === "object" && "input_tokens" in usage ? Number(usage.input_tokens) : 0;
    inputTokens.push(Number.isFinite(tokens) ? tokens : 0);
    return res;
  };
  const out = [];
  for (const s of sessions()) {
    const c = cut(load(untilde(s.path)))!;
    const result = await compactMessages(c.prefix, { ...OPTIONS, apiKey, fetch: recording });
    const byId = new Map(c.prefixCalls.map((x: ToolCall) => [x.id, x]));
    for (const d of result.decisions) {
      const call = byId.get(d.id)!;
      out.push({ session: s.id, tool_use_id: call.tool_use_id, pinned: call.pinned, action: d.action, keepCall: d.keepCall, keepResult: d.keepResult });
    }
    console.error(`${s.id}: ${result.stats.calls} calls, ${result.stats.requests} requests`);
  }
  const input = inputTokens.reduce((x, y) => x + y, 0);
  const requests = inputTokens.length;
  writeFileSync(join(HERE, "decisions.jsonl"), out.map((r) => JSON.stringify(r)).join("\n") + "\n");
  writeFileSync(join(HERE, "decisions-pass.json"), JSON.stringify({ lane: "live", model: OPTIONS.model, at: new Date().toISOString(), requests, input_tokens: input, spend_usd: +(input * 0.042 / 1e6).toFixed(6) }, null, 2) + "\n");
  console.log(JSON.stringify({ decisions: out.length, requests, receipt: join(HERE, "decisions-pass.json") }));
  return 0;
}

const mode = process.argv[2];
const code = mode === "select" ? select() : mode === "packets" ? packets() : mode === "replay" ? await replay() : (console.log("usage: c3.ts select|packets|replay --live"), 64);
process.exit(code);
