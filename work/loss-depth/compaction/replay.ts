// Compaction keep replay loop (bead jev-9gtw.6), LOSS DEPTH step 3. Builds every request in THIS
// wrapper; the vendored fast-jev-compaction clone (6e1da50) is imported, never edited. Preregistered
// in docs/demos/upstream-repro/compaction-replay-20260925.md.
//
//   node --experimental-strip-types work/loss-depth/compaction/replay.ts check          # keyless: A0 body == the library's body, every arm's size
//   node --experimental-strip-types work/loss-depth/compaction/replay.ts tokens --live  # A0 + C2 on jev-jec6's 4 sessions vs its recorded 72,649 input tokens
//   node --experimental-strip-types work/loss-depth/compaction/replay.ts dev --live     # A0, H1, H2, H3 on the 7-session dev slice
//
// Live modes run under `infisical run --silent --projectId=... --` and refuse without TYPESAFE_API_KEY.
// Written files hold ids, numbers and hashes only, never session text.
import { createHash, timingSafeEqual } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  batchCalls,
  buildJevRequest,
  collectToolCalls,
  compactMessages,
  estimateTokens,
  fitState,
  parseJevResponse,
  questionsFor,
  resolveOptions,
  STATE_CONTEXT,
} from "../../../fast-jev-compaction/dist/index.js";
import type { CompactionState, HistoryEntry, JevQuestions, Message, ToolCall } from "../../../fast-jev-compaction/dist/index.js";
import { cut, load, OPTIONS, untilde } from "../../compaction-need/need.ts";
import { needQuestions } from "../../compaction-keep/keep.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..", "..");
const STUDIES = { x86y: join(ROOT, "work/compaction-need"), jec6: join(ROOT, "work/compaction-keep") };
export const ARMS = ["A0", "H1", "H2", "H3"] as const;
type Arm = (typeof ARMS)[number];
const MAX_REQUEST_TOKENS = resolveOptions(OPTIONS).maxRequestTokens;
const PRICE_PER_M = 0.042;

// H1: the state's re-run premise goes, and one single-condition Noul replaces the two library ones.
const RERUN_SENTENCE = " Whatever is not kept is deleted permanently, but the assistant can always re-run a tool or re-read a file.";
const H1_CONTEXT = STATE_CONTEXT.replace(RERUN_SENTENCE, " Whatever is not kept is deleted permanently.");
export function useQuestions(batch: readonly ToolCall[]): JevQuestions {
  return Object.fromEntries(
    batch.map((call) => [
      `use_${call.id}`,
      {
        type: "noul",
        instructions: `A later step of the assistant will read, cite or act on a value, line, path, error or finding that appears in the output of tool call ${call.id} (${call.tool}, ${call.resultChars} chars).`,
      },
    ]),
  );
}

// H2: every call's `result` shows the output's first HEAD characters instead of "(omitted)".
const HEAD = 500;
const OMITTED_PHRASE = "tool outputs are replaced by a short `result` note";
const H2_CONTEXT = STATE_CONTEXT.replace(OMITTED_PHRASE, `each tool output is cut to its first ${HEAD} characters in \`result\``);

// H3: the goal is the last three user prompts unclipped (a prompt carrying a tool result counts),
// plus the full output of each prefix call that fetched a file or bead those prompts name.
const BODY_CAP = 10_000;

if (!STATE_CONTEXT.includes(RERUN_SENTENCE) || !STATE_CONTEXT.includes(OMITTED_PHRASE)) {
  throw new Error("REFUSED: STATE_CONTEXT is not the 6e1da50 text this wrapper edits");
}

type Session = { study: keyof typeof STUDIES; id: string; path: string; sha256: string };
type Req = { arm: Arm; batch: number; state: CompactionState; questions: JevQuestions; calls: ToolCall[]; stage: string };

/** A study's sessions minus every one the autopsy skipped (A1, or the rider screen): those are never read. */
function sessionsOf(study: keyof typeof STUDIES): Session[] {
  const skipped = new Set(
    JSON.parse(readFileSync(join(HERE, "sessions.json"), "utf8"))
      .filter((s: { skipped?: string }) => s.skipped)
      .map((s: { session: string }) => s.session),
  );
  return JSON.parse(readFileSync(join(STUDIES[study], "sessions.json"), "utf8"))
    .sessions.filter((s: { id: string }) => !skipped.has(s.id))
    .map((s: Omit<Session, "study">) => ({ ...s, study }));
}

/** The 7 stub-free sessions of the committed autopsy (features.jsonl), never a held-out set. */
function devSlice(): Session[] {
  const feats = readFileSync(join(HERE, "features.jsonl"), "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const stub = new Set(feats.filter((f) => f.result_shaken).map((f) => f.session));
  const ids = new Set(feats.map((f) => f.session).filter((s) => !stub.has(s)));
  return [...sessionsOf("x86y"), ...sessionsOf("jec6")].filter((s) => ids.has(s.id));
}

function prefixOf(s: Session): Message[] {
  const bytes = readFileSync(untilde(s.path));
  if (!timingSafeEqual(createHash("sha256").update(bytes).digest(), Buffer.from(s.sha256, "hex"))) {
    throw new Error(`REFUSED: ${s.path} changed since it was sampled`);
  }
  return cut(load(untilde(s.path)))!.prefix;
}

/** The goal H3 sends: unclipped prompts, then the bodies they point at. */
export function h3Goal(prefix: readonly Message[], calls: readonly ToolCall[]): { goal: string; bodies: string[] } {
  const prompts = prefix.filter((m) => m.role === "user" && (m.text ?? "").trim().length > 0).slice(-3).map((m) => m.text);
  const said = prompts.join("\n");
  const output = new Map<string, string>();
  for (const m of prefix) for (const r of m.toolResults ?? []) output.set(r.tool_use_id, r.text ?? "");
  const beads = new Set([...said.matchAll(/\bjev-[0-9a-z]+(?:\.[0-9]+)*\b/g)].map((m) => m[0]));
  // One body per target: the longest fetch of it (a `br show` cut short beats nothing, a full read beats both).
  const best = new Map<string, { call: ToolCall; text: string }>();
  for (const call of calls) {
    if (call.isError) continue;
    // br's tracing lines (`2026-...Z  INFO ...`) are log noise around the bead, not its body.
    const text = (output.get(call.tool_use_id) ?? "").split("\n").filter((l) => !/^\S+Z\s+INFO\s/.test(l)).join("\n");
    const path = typeof call.input.path === "string" ? call.input.path.replace(`${ROOT}/`, "").replace(/:[\d,+-]+$/, "") : "";
    const command = typeof call.input.command === "string" ? call.input.command : "";
    const shown = /\bbr show\s+([\w.-]+)/.exec(command)?.[1];
    // A file the prompts name as a whole path (a read of it, not of a directory or a longer path),
    // or a bead they name, fetched by `br show` or read back as its JSON.
    const escaped = path.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const named = call.tool === "read" && /[./]/.test(path) && !path.startsWith("artifact://") && new RegExp(`(^|[^\\w.-])${escaped}(?![\\w/-]|\\.\\w)`).test(said);
    const bead = shown && beads.has(shown) ? shown : [...beads].find((b) => text.startsWith(`[{"id":"${b}"`));
    const target = named ? path : bead;
    if (!target || (best.get(target)?.text.length ?? -1) >= text.length) continue;
    best.set(target, { call, text });
  }
  const chosen = [...best.entries()].sort((a, b) => a[1].call.callIndex - b[1].call.callIndex);
  for (const [target, { call, text }] of chosen) {
    const body = text.length > BODY_CAP ? `${text.slice(0, BODY_CAP)}\n[... ${text.length - BODY_CAP} more chars]` : text;
    prompts.push(`=== ${target} (output of tool call ${call.id}) ===\n${body}`);
  }
  return { goal: prompts.join("\n"), bodies: chosen.map(([target, { call }]) => `${call.id} ${target}`) };
}

/** Every request an arm sends for one prefix, built exactly as compact() builds the library's. */
export function requests(arm: Arm, prefix: readonly Message[]): Req[] {
  const resolved = resolveOptions(OPTIONS);
  const calls = collectToolCalls(prefix, resolved.preserveRecentMessages);
  const candidates = calls.filter((c) => !c.pinned);
  if (candidates.length === 0) return [];
  const fitted = arm === "H3" ? fitState(prefix, calls, { ...resolved, goal: h3Goal(prefix, calls).goal }) : fitState(prefix, calls, resolved);
  let state: CompactionState = fitted.state;
  if (arm === "H1") state = { ...state, context: H1_CONTEXT };
  if (arm === "H2") {
    const output = new Map<string, string>();
    for (const m of prefix) for (const r of m.toolResults ?? []) output.set(r.tool_use_id, r.text ?? "");
    const byId = new Map(calls.map((c) => [c.id, c]));
    const history: HistoryEntry[] = state.history.map((e) => {
      if (!e.tool_calls || typeof e.tool_calls[0] === "string") return e;
      return {
        ...e,
        tool_calls: (e.tool_calls as Exclude<HistoryEntry["tool_calls"], string[] | undefined>).map((tc) => {
          const call = byId.get(tc.id)!;
          const text = output.get(call.tool_use_id) ?? "";
          const more = text.length > HEAD ? ` …[${text.length - HEAD} more chars]` : "";
          return { ...tc, result: `${call.isError ? "error" : "ok"}, ${call.resultChars} chars: ${text.slice(0, HEAD)}${more}` };
        }),
      };
    });
    state = { ...state, context: H2_CONTEXT, history };
  }
  // The library batches on fitState's own estimate; only H2 changes the state after fitting.
  const tokens = arm === "H2" ? estimateTokens(JSON.stringify(state)) : fitted.tokens;
  return batchCalls(candidates, tokens, resolved).map((batch, k) => ({
    arm,
    batch: k,
    state,
    questions: arm === "H1" ? useQuestions(batch) : Object.assign({}, ...batch.map(questionsFor)),
    calls: batch,
    stage: fitted.stage,
  }));
}

const bodyOf = (state: CompactionState, questions: JevQuestions) => buildJevRequest({ apiKey: "-", model: OPTIONS.model }, state, questions).body;

/** Keyless: the A0 wrapper body equals, byte for byte, the body compactMessages sends; and every arm fits. */
async function check() {
  const rows = [];
  for (const s of [...sessionsOf("x86y"), ...sessionsOf("jec6")]) {
    const prefix = prefixOf(s);
    const sent: string[] = [];
    const fake: typeof fetch = async (_u, init) => {
      sent.push(String(init?.body));
      const qs = JSON.parse(String(init?.body)).questions;
      return new Response(JSON.stringify({ answers: Object.fromEntries(Object.keys(qs).map((k) => [k, { noul: 0 }])) }), { status: 200 });
    };
    await compactMessages(prefix, { ...OPTIONS, apiKey: "-", fetch: fake });
    const mine = requests("A0", prefix).map((r) => bodyOf(r.state, r.questions));
    const same = mine.length === sent.length && mine.every((b, k) => b === sent[k]);
    const sizes = Object.fromEntries(ARMS.map((a) => [a, requests(a, prefix).map((r) => estimateTokens(bodyOf(r.state, r.questions)))]));
    rows.push({ study: s.study, session: s.id, a0_bytes_identical: same, library_requests: sent.length, est_request_tokens: sizes, h3_bodies: h3Goal(prefix, collectToolCalls(prefix, 6)).bodies });
    if (!same) throw new Error(`REFUSED: ${s.id}: the A0 body differs from the library's`);
  }
  for (const r of rows) console.log(JSON.stringify(r));
  const over = rows.flatMap((r) => Object.entries(r.est_request_tokens).flatMap(([a, xs]) => (xs as number[]).filter((x) => x > MAX_REQUEST_TOKENS).map(() => `${r.session} ${a}`)));
  console.log(over.length ? `WARN: over ${MAX_REQUEST_TOKENS} est tokens: ${over.join(", ")}` : `all arms within ${MAX_REQUEST_TOKENS} estimated request tokens`);
  return 0;
}

async function ask(key: string, state: CompactionState, questions: JevQuestions) {
  const req = buildJevRequest({ apiKey: key, model: OPTIONS.model }, state, questions);
  const res = await fetch(req.url, { method: req.method, headers: req.headers, body: req.body });
  const text = await res.text();
  const parsed = parseJevResponse(res.status, res.ok, text) as { answers: Record<string, { noul?: number }>; usage?: { input_tokens?: number } };
  return { answers: parsed.answers, inputTokens: Number(parsed.usage?.input_tokens ?? 0), bodySha: createHash("sha256").update(req.body).digest("hex").slice(0, 16) };
}

function liveKey(): string | null {
  if (!process.argv.includes("--live")) {
    console.log("NOT_RUN: live Jev calls; rerun with --live under `infisical run` after the prereg is committed");
    return null;
  }
  const key = process.env.TYPESAFE_API_KEY;
  if (!key) {
    console.log("NOT_RUN reason=unconfigured: TYPESAFE_API_KEY is not in the environment");
    return null;
  }
  return key;
}

/** A0 plus jev-jec6's C2 request on its 4 sessions: input tokens must equal the 72,649 it recorded. */
async function tokens() {
  const key = liveKey();
  if (!key) return 2;
  const recorded = JSON.parse(readFileSync(join(STUDIES.jec6, "decisions-pass.json"), "utf8"));
  let measured = 0;
  let n = 0;
  const per = [];
  for (const s of sessionsOf("jec6")) {
    const prefix = prefixOf(s);
    for (const r of requests("A0", prefix)) {
      const a = await ask(key, r.state, r.questions);
      const c2 = await ask(key, r.state, needQuestions(r.calls));
      measured += a.inputTokens + c2.inputTokens;
      n += 2;
      per.push({ session: s.id, a0: a.inputTokens, c2: c2.inputTokens });
    }
  }
  const out = { recorded_requests: recorded.requests, recorded_input_tokens: recorded.input_tokens, requests: n, input_tokens: measured, equal: measured === recorded.input_tokens, per, spend_usd: +((measured * PRICE_PER_M) / 1e6).toFixed(6), at: new Date().toISOString(), model: OPTIONS.model };
  writeFileSync(join(HERE, "tokens-check.json"), JSON.stringify(out, null, 2) + "\n");
  console.log(JSON.stringify(out));
  return out.equal ? 0 : 1;
}

async function dev() {
  const key = liveKey();
  if (!key) return 2;
  if (existsSync(join(HERE, "dev-answers.jsonl"))) {
    console.log("REFUSED: dev-answers.jsonl exists; the dev pass has run");
    return 1;
  }
  const answers = [];
  const reqs = [];
  let input = 0;
  for (const s of devSlice()) {
    const prefix = prefixOf(s);
    const resolved = resolveOptions(OPTIONS);
    const all = collectToolCalls(prefix, resolved.preserveRecentMessages);
    for (const arm of ARMS) {
      const scores = new Map<string, Record<string, number>>();
      for (const r of requests(arm, prefix)) {
        const a = await ask(key, r.state, r.questions);
        input += a.inputTokens;
        reqs.push({ arm, study: s.study, session: s.id, batch: r.batch, stage: r.stage, calls: r.calls.length, input_tokens: a.inputTokens, body_sha256_16: a.bodySha });
        for (const call of r.calls) {
          const got = (k: string) => Number(a.answers[k]?.noul);
          scores.set(call.id, arm === "H1" ? { use: got(`use_${call.id}`) } : { keepCall: got(`call_${call.id}`), keepResult: got(`result_${call.id}`) });
        }
      }
      for (const call of all) answers.push({ arm, study: s.study, session: s.id, tool_use_id: call.tool_use_id, id: call.id, pinned: call.pinned, ...(scores.get(call.id) ?? {}) });
      console.error(`${s.id} ${arm}: ${scores.size} candidates scored`);
    }
  }
  writeFileSync(join(HERE, "dev-answers.jsonl"), answers.map((r) => JSON.stringify(r)).join("\n") + "\n");
  writeFileSync(join(HERE, "dev-requests.jsonl"), reqs.map((r) => JSON.stringify(r)).join("\n") + "\n");
  const pass = { lane: "live", model: OPTIONS.model, at: new Date().toISOString(), requests: reqs.length, input_tokens: input, spend_usd: +((input * PRICE_PER_M) / 1e6).toFixed(6) };
  writeFileSync(join(HERE, "dev-pass.json"), JSON.stringify(pass, null, 2) + "\n");
  console.log(JSON.stringify(pass));
  return 0;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const mode = process.argv[2];
  const code = mode === "check" ? await check() : mode === "tokens" ? await tokens() : mode === "dev" ? await dev() : (console.log("usage: replay.ts check|tokens --live|dev --live"), 64);
  process.exit(code);
}
