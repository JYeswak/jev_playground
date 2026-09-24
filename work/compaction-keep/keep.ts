// Compaction keep rule (bead jev-jec6): does a lower cut or a reworded keep question keep the tool
// results a later turn needs? Rules are preregistered in docs/demos/upstream-repro/compaction-keep-20260924.md.
//
//   node --experimental-strip-types work/compaction-keep/keep.ts select    # seeded sample + rider screen -> sessions.json
//   node --experimental-strip-types work/compaction-keep/keep.ts packets   # /tmp/jec6-packets (never committed) + calls.json (ids)
//   node --experimental-strip-types work/compaction-keep/keep.ts replay --live   # after labels are final
//
// Same cut as jev-x86y (need.ts cut(): prefix through the 40th paired call's result, 40-message
// horizon). The replay asks, per session, (A) the library's own compaction questions, whose
// keepResult gives the current rule C0 (cut 0.5) and the lower-cut rule C1 (cut 0.15), and (B) the
// reworded NEED question below on the same fitted state and batches, which gives rule C2 (cut 0.5).
import { spawnSync } from "node:child_process";
import { createHash, timingSafeEqual } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { batchCalls, collectToolCalls, compactMessages, fitState, JevClient, resolveOptions } from "../../fast-jev-compaction/dist/index.js";
import type { Message, ToolCall } from "../../fast-jev-compaction/dist/index.js";
import { clip, cut, EXCLUDE, load, MIN_CALLS, OPTIONS, render, rng, SIZE, sessionFiles, untilde } from "../compaction-need/need.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const HOME = homedir();
const SESSIONS = join(HERE, "sessions.json");
const CALLS = join(HERE, "calls.json");
const PACKETS = "/tmp/jec6-packets";
export const CUTOFF = "2026-09-24T17:45:00Z";
export const SEED = 20260925;
export const SAMPLE = 6;
// A tool call whose input points into a rider-covered checkout reads its content (AGENTS.md
// "Rider-Covered Repos"): the session is screened out before any labeller sees its packet.
// Also `git -C <repo>` and `cd <repo>`, which run commands inside the checkout (conservative: a
// name-only `git -C skillranker rev-parse` screens a session out too).
export const RIDER_PATH =
  /(?:(?:^|[\s"'`=:(])(?:[\w.~-]*\/)*(?:skillranker(?:-tip)?|dicklesworthstone-mirror|franken[\w-]*|asupersync)\/|(?:-C|\bcd)\s+["']?(?:[\w.~-]*\/)*(?:skillranker(?:-tip)?|dicklesworthstone-mirror|franken[\w-]*|asupersync)\b)/i;

/** The reworded keep question for rule C2, one noul per candidate call. */
export function needQuestions(batch: readonly ToolCall[]) {
  return Object.fromEntries(
    batch.map((call) => [
      `need_${call.id}`,
      {
        type: "noul",
        instructions: `The output of tool call ${call.id} (${call.tool}, ${call.resultChars} chars) holds information the assistant will read, cite or act on in its next steps, and no later call in the history gives that information again.`,
        criteria: {
          true: "A next step would use a value, line, path, error or finding that appears in this output and in no later call's input or output.",
          false: "The output was exploration the assistant has moved past, or a later call re-read, re-ran or restated what it held.",
        },
      },
    ]),
  );
}

function usedSessions(): Set<string> {
  const x86y = JSON.parse(readFileSync(join(ROOT, "work/compaction-need/sessions.json"), "utf8"));
  return new Set([...EXCLUDE, ...x86y.sessions.map((s: { id: string }) => s.id)]);
}

function riderHits(prefix: readonly Message[], horizon: readonly Message[]): number {
  let hits = 0;
  for (const m of [...prefix, ...horizon]) for (const u of m.toolUses ?? []) if (RIDER_PATH.test(JSON.stringify(u.input))) hits += 1;
  return hits;
}

function select() {
  if (existsSync(SESSIONS)) {
    console.log("REFUSED: sessions.json exists; the sample is fixed");
    return 1;
  }
  const used = usedSessions();
  const eligible: { path: string; id: string; bytes: number; calls: number; sha256: string }[] = [];
  const skipped: Record<string, number> = {};
  const skip = (why: string) => (skipped[why] = (skipped[why] ?? 0) + 1);
  for (const f of sessionFiles()) {
    const st = statSync(f);
    const id = basename(f).split("_")[1]?.slice(0, 8) ?? "";
    if (used.has(id)) { skip("used in jev-x86y or jev-0c6"); continue; }
    if (st.mtime.toISOString() >= CUTOFF) { skip("written after CUTOFF"); continue; }
    if (st.size < SIZE[0] || st.size > SIZE[1]) { skip("size outside 200KB-3MB"); continue; }
    const calls = collectToolCalls(load(f), 0).length;
    if (calls < MIN_CALLS) { skip(`fewer than ${MIN_CALLS} paired tool calls`); continue; }
    eligible.push({ path: f.replace(HOME, "~"), id, bytes: st.size, calls, sha256: createHash("sha256").update(readFileSync(f)).digest("hex") });
  }
  // Seeded order over the eligible list; take sessions in that order until SAMPLE pass the rider screen.
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
  writeFileSync(SESSIONS, JSON.stringify({ seed: SEED, cutoff: CUTOFF, eligible: eligible.length, skipped, screened_out_rider: screened, sessions: picked }, null, 2) + "\n");
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
  if (existsSync(CALLS)) {
    console.log("REFUSED: calls.json exists; the call set is fixed (labels refer to it)");
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
  const ready = spawnSync("python3", [join(HERE, "keep.py"), "ready"], { encoding: "utf8" });
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
    const a = await compactMessages(c.prefix, { ...OPTIONS, apiKey, fetch: recording });
    const resolved = resolveOptions(OPTIONS);
    const calls = collectToolCalls(c.prefix, resolved.preserveRecentMessages);
    const candidates = calls.filter((x: ToolCall) => !x.pinned);
    const fitted = fitState(c.prefix, calls, resolved);
    const client = new JevClient({ apiKey, model: OPTIONS.model, fetch: recording });
    const need = new Map<string, number>();
    for (const batch of batchCalls(candidates, fitted.tokens, resolved)) {
      const { answers } = await client.ask(fitted.state, needQuestions(batch));
      for (const call of batch) need.set(call.id, Number(answers[`need_${call.id}`]?.noul));
    }
    const byId = new Map(calls.map((x: ToolCall) => [x.id, x]));
    for (const d of a.decisions) {
      const call = byId.get(d.id)!;
      out.push({ session: s.id, tool_use_id: call.tool_use_id, pinned: call.pinned, keepCall: d.keepCall, keepResult: d.keepResult, need: need.get(d.id) ?? null });
    }
    console.error(`${s.id}: ${calls.length} calls, ${candidates.length} candidates`);
  }
  const input = inputTokens.reduce((x, y) => x + y, 0);
  const requests = inputTokens.length;
  writeFileSync(join(HERE, "decisions.jsonl"), out.map((r) => JSON.stringify(r)).join("\n") + "\n");
  writeFileSync(join(HERE, "decisions-pass.json"), JSON.stringify({ lane: "live", model: OPTIONS.model, at: new Date().toISOString(), requests, input_tokens: input, spend_usd: +(input * 0.042 / 1e6).toFixed(6) }, null, 2) + "\n");
  console.log(JSON.stringify({ decisions: out.length, requests, receipt: join(HERE, "decisions-pass.json") }));
  return 0;
}

const mode = process.argv[2];
const code = mode === "select" ? select() : mode === "packets" ? packets() : mode === "replay" ? await replay() : (console.log("usage: keep.ts select|packets|replay --live"), 64);
process.exit(code);
