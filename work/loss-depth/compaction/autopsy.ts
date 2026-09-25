// Loss-depth autopsy of the two compaction keep studies (bead jev-9gtw.5). KEYLESS: no Jev call.
// Rebuilds, for every prefix call, the exact request fast-jev-compaction sent (fitState state,
// batchCalls batch, questionsFor text; pinned SHA 6e1da50) from the sha-checked session files, and
// measures what that request showed about the call and what the horizon later used from it.
//
//   node --experimental-strip-types work/loss-depth/compaction/autopsy.ts features   # features.jsonl: numbers, flags and ids only
//   node --experimental-strip-types work/loss-depth/compaction/autopsy.ts dossier    # /tmp/loss-depth-compaction/*.md, session text, never committed
//
// autopsy.py runs `features` and classifies. Sessions: jev-x86y minus its A1 exclusion, jev-jec6's
// four, and any session whose prefix or horizon trips work/compaction-keep's RIDER_PATH is skipped
// before its text is read beyond that screen (jev-x86y's 01a0c530 does, with 0 needed unpinned calls).
import { createHash, timingSafeEqual } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { batchCalls, collectToolCalls, estimateTokens, fitState, goalFromMessages, questionsFor, resolveOptions } from "../../../fast-jev-compaction/dist/index.js";
import type { HistoryEntry, Message, ToolCall } from "../../../fast-jev-compaction/dist/index.js";
import { cut, load, OPTIONS, untilde } from "../../compaction-need/need.ts";
import { needQuestions, riderHits } from "../../compaction-keep/keep.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..", "..");
export const SETS = [
  { name: "x86y", dir: join(ROOT, "work/compaction-need"), excluded: join(ROOT, "work/compaction-need/excluded.json") },
  { name: "jec6", dir: join(ROOT, "work/compaction-keep"), excluded: null },
];
const DOSSIER = "/tmp/loss-depth-compaction";
const SHAKEN = /^\[shaken ~\d+ tokens/;
// A distinctive token: 8+ path/identifier characters, or a measured number (a percentage, a
// fraction like 17/24, a thousands-grouped count). Used to locate, inside a result, the part a
// horizon message used (the earliest offset of a token both contain).
const TOKEN = /[A-Za-z0-9_./:@#-]{8,}|\d+(?:\.\d+)?%|\b\d+\/\d+\b|\b\d{1,3}(?:,\d{3})+\b/g;

type Row = Record<string, unknown>;

function readJsonl(path: string): Row[] {
  return readFileSync(path, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
}

/** Final label and the horizon index a labeller named for it (adjudicated, else an agreeing labeller). */
function finalLabels(dir: string) {
  const [one, two, adj] = ["labels-1.jsonl", "labels-2.jsonl", "labels-adjudicated.jsonl"].map((f) =>
    new Map(readJsonl(join(dir, f)).map((r) => [`${r.session} ${r.tool_use_id}`, r])),
  );
  const out = new Map<string, { label: string; horizon: number | null; split: boolean }>();
  for (const [k, a] of one) {
    const b = two.get(k)!;
    const split = a.label !== b.label;
    const fin = split ? adj.get(k) : a;
    if (!fin) continue; // only jev-x86y's A1-excluded session has splits nobody adjudicated
    const hs = [fin, a, b].filter((r) => r && r.label === fin.label && typeof r.horizon === "number").map((r) => r.horizon as number);
    out.set(k, { label: fin.label as string, horizon: hs.length ? Math.min(...hs) : null, split });
  }
  return out;
}

const isUserPrompt = (m: Message) => m.role === "user" && (m.text ?? "").trim().length > 0;

/** Tokens a use message shares with a result, with each token's first offset in the result. */
function shared(result: string, use: string) {
  const got = new Map<string, number>();
  for (const [t] of use.matchAll(TOKEN)) {
    if (got.has(t)) continue;
    const at = result.indexOf(t);
    if (at >= 0) got.set(t, at);
  }
  return got;
}

/** Files a write (its `path`) or a hashline edit (its `[path#TAG]` anchors) targets. */
function editTargets(call: ToolCall): string[] {
  if (call.tool === "write") return [String(call.input.path ?? "")];
  if (call.tool !== "edit") return [];
  return [...JSON.stringify(call.input).matchAll(/\[([^\]#\s"]+)#[0-9A-F]{4}\]/g)].map((m) => m[1]);
}

/** Where the call sits in the fitted state, and how much of it that state shows. */
function stateView(history: readonly HistoryEntry[], call: ToolCall) {
  for (const e of history) {
    const tc = e.tool_calls;
    if (!tc) continue;
    for (const x of tc) {
      if (typeof x === "string") {
        if (x.startsWith(`${call.id} `)) return { form: "one-line", input_shown: x.length, entry_text_chars: e.text.length, line: x };
      } else if (x.id === call.id) {
        return { form: "structured", input_shown: x.input.length, entry_text_chars: e.text.length, line: JSON.stringify(x) };
      }
    }
  }
  return { form: "absent", input_shown: 0, entry_text_chars: 0, line: "" };
}

function verified(path: string, sha: string): Message[] {
  const bytes = readFileSync(untilde(path));
  if (!timingSafeEqual(createHash("sha256").update(bytes).digest(), Buffer.from(sha, "hex"))) {
    throw new Error(`REFUSED: ${path} changed since it was sampled`);
  }
  return load(untilde(path));
}

export function analyse(withText: boolean) {
  const rows: Row[] = [];
  const sessionsOut: Row[] = [];
  const dossiers: Record<string, string[]> = {};
  const resolved = resolveOptions(OPTIONS);
  for (const set of SETS) {
    const labels = finalLabels(set.dir);
    const decisions = new Map(readJsonl(join(set.dir, "decisions.jsonl")).map((d) => [`${d.session} ${d.tool_use_id}`, d]));
    const excluded: Record<string, string> = set.excluded ? JSON.parse(readFileSync(set.excluded, "utf8")) : {};
    for (const s of JSON.parse(readFileSync(join(set.dir, "sessions.json"), "utf8")).sessions) {
      if (s.id in excluded) {
        sessionsOut.push({ study: set.name, session: s.id, skipped: "jev-x86y amendment A1 (rider), never read" });
        continue;
      }
      const c = cut(verified(s.path, s.sha256))!;
      const rider = riderHits(c.prefix, c.horizon);
      if (rider > 0) {
        sessionsOut.push({ study: set.name, session: s.id, skipped: `rider screen: ${rider} tool inputs point into a rider-covered repo` });
        continue;
      }
      // The exact request compactMessages built (compact.ts compact()): same calls, state, batches.
      const calls = collectToolCalls(c.prefix, resolved.preserveRecentMessages);
      const candidates = calls.filter((x) => !x.pinned);
      const fitted = fitState(c.prefix, calls, resolved);
      const batches = batchCalls(candidates, fitted.tokens, resolved);
      const stateJson = JSON.stringify(fitted.state);
      const batchOf = new Map<string, number>();
      batches.forEach((b, k) => b.forEach((x) => batchOf.set(x.id, k)));
      const libQuestionTokens = candidates.reduce((a, x) => a + estimateTokens(JSON.stringify(questionsFor(x))), 0);
      const needQuestionTokens = candidates.reduce((a, x) => a + estimateTokens(JSON.stringify(needQuestions([x]))), 0);
      const goal = goalFromMessages(c.prefix);
      const prompts = c.prefix.map((m, i) => [m, i] as const).filter(([m]) => isUserPrompt(m));
      const [lastUser, lastUserIdx] = prompts.at(-1) ?? [null, -1];
      const lastUserInGoal = lastUser ? goal.includes((lastUser.text ?? "").slice(0, 400)) : false;
      const lastEntry = fitted.state.history.find((e) => e.i === lastUserIdx);
      sessionsOut.push({
        study: set.name,
        session: s.id,
        prefix_messages: c.prefix.length,
        horizon_messages: c.horizon.length,
        calls: calls.length,
        candidates: candidates.length,
        state_stage: fitted.stage,
        state_tokens_est: fitted.tokens,
        batches: batches.length,
        lib_question_tokens_est: libQuestionTokens,
        need_question_tokens_est: needQuestionTokens,
        goal_chars: goal.length,
        user_prompts_in_prefix: prompts.length,
        last_user_chars: lastUser ? lastUser.text.length : 0,
        last_user_has_results: lastUser ? (lastUser.toolResults ?? []).length > 0 : false,
        last_user_in_goal: lastUserInGoal,
        last_user_in_history: lastEntry ? (lastEntry.text === lastUser!.text ? "verbatim" : "abridged") : "absent",
        last_user_messages_before_cut: lastUserIdx >= 0 ? c.prefix.length - 1 - lastUserIdx : null,
      });
      if (withText) dossiers[s.id] = [`# ${set.name} ${s.id} stage=${fitted.stage} tokens~${fitted.tokens} batches=${batches.length}`, "", "## GOAL", goal, ""];

      const resultOf = new Map<string, string>();
      for (const m of c.prefix) for (const r of m.toolResults ?? []) resultOf.set(r.tool_use_id, r.text ?? "");
      for (const call of calls) {
        const key = `${s.id} ${call.tool_use_id}`;
        const lab = labels.get(key)!;
        const dec = decisions.get(key)!;
        const result = resultOf.get(call.tool_use_id) ?? "";
        const view = stateView(fitted.state.history, call);
        const k = lab.horizon;
        const used = k !== null ? c.horizon[k] : undefined;
        // The use is what the assistant wrote or passed to a tool there, not the results it received.
        const use = used ? [used.text ?? "", ...(used.toolUses ?? []).map((u) => JSON.stringify(u.input))].join("\n") : "";
        const hit = shared(result, use);
        const offsets = [...hit.values()];
        // Of the result tokens the use message cites, how many the assistant already restated in a
        // later PREFIX message's own text (which compaction keeps verbatim)?
        const laterText = c.prefix.slice(call.resultIndex + 1).map((m) => m.text ?? "").join("\n");
        const restated = [...hit.keys()].filter((t) => laterText.includes(t)).length;
        const firstUserInHorizon = c.horizon.findIndex(isUserPrompt);
        const inputJson = JSON.stringify(call.input);
        const inInput = [...new Set([...use.matchAll(TOKEN)].map(([t]) => t))].filter((t) => inputJson.includes(t) && !hit.has(t)).length;
        // Does the goal (last three user prompts, as sent) name this call's file as the thing to read?
        const path = typeof call.input.path === "string" ? call.input.path.replace(`${ROOT}/`, "").replace(/:[\d,+-]+$/, "") : "";
        const goalNamesTarget = path.length > 0 && goal.includes(path);
        // Did a later prefix write (its `path`) or edit (its `[path#TAG]` anchors) target the same file?
        // Then a re-read no longer returns this output.
        const writtenLater = path.length > 0 && calls.some((x) => x.callIndex > call.callIndex && editTargets(x).some((t) => t.endsWith(path)));
        rows.push({
          study: set.name,
          session: s.id,
          tool_use_id: call.tool_use_id,
          id: call.id,
          tool: call.tool,
          pinned: call.pinned,
          label: lab.label,
          label_split: lab.split,
          use_horizon: k,
          keepCall: dec.keepCall,
          keepResult: dec.keepResult,
          need: dec.need ?? null,
          action: dec.action ?? null,
          batch: batchOf.get(call.id) ?? null,
          result_chars: result.length,
          result_shaken: SHAKEN.test(result),
          result_is_error: call.isError,
          // Is any of the output in the request? Its first 40 characters, JSON-escaped as the state holds text.
          result_in_state: result.length >= 40 ? stateJson.includes(JSON.stringify(result.slice(0, 40)).slice(1, -1)) : null,
          input_chars: JSON.stringify(call.input).length,
          state_form: view.form,
          state_input_shown: view.input_shown,
          messages_before_cut: c.prefix.length - 1 - call.resultIndex,
          user_prompt_after_call: prompts.some(([, i]) => i > call.resultIndex),
          user_prompt_in_horizon_before_use: k !== null && firstUserInHorizon >= 0 && firstUserInHorizon <= k,
          use_tokens: hit.size,
          use_min_offset: offsets.length ? Math.min(...offsets) : null,
          use_max_offset: offsets.length ? Math.max(...offsets) : null,
          use_tokens_restated_in_prefix_text: restated,
          use_tokens_in_input_only: inInput,
          goal_names_target: goalNamesTarget,
          written_later_in_prefix: writtenLater,
        });
        if (withText && lab.label === "needed" && !call.pinned) {
          const d = dossiers[s.id];
          d.push(
            `\n---\n### ${call.id} ${call.tool} ${call.tool_use_id}`,
            `scores keepCall=${dec.keepCall} keepResult=${dec.keepResult} need=${dec.need ?? "-"} action=${dec.action ?? "-"} split=${lab.split} horizon=${k}`,
            `result ${result.length} chars shaken=${SHAKEN.test(result)} error=${call.isError}; messages before cut ${c.prefix.length - 1 - call.resultIndex}; user prompt after call ${prompts.some(([, i]) => i > call.resultIndex)}`,
            `STATE VIEW (${view.form}): ${view.line.slice(0, 600)}`,
            `INPUT: ${JSON.stringify(call.input).slice(0, 600)}`,
            `RESULT HEAD: ${result.slice(0, 900)}`,
            `USE TOKENS (${hit.size}; restated in later prefix text ${restated}; in input only ${inInput}; goal names target ${goalNamesTarget}): ${[...hit.entries()].slice(0, 12).map(([t, o]) => `${t}@${o}`).join(" ")}`,
            `PREFIX TEXT AFTER (next 2 msgs with text): ${c.prefix.slice(call.resultIndex).filter((m) => m.text?.trim()).slice(0, 2).map((m) => `[${m.role}] ${m.text.slice(0, 400)}`).join(" || ")}`,
            `USE MESSAGE h${k}: ${used ? `[${used.role}] ${use.slice(0, 1200)}` : "(none named)"}`,
          );
        }
      }
      if (withText) {
        const last = lastUser ? lastUser.text.slice(0, 1500) : "";
        dossiers[s.id].splice(4, 0, "## LAST USER PROMPT IN PREFIX", last, "");
      }
    }
  }
  return { rows, sessions: sessionsOut, dossiers };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const mode = process.argv[2];
  if (mode === "features") {
    const { rows, sessions } = analyse(false);
    writeFileSync(join(HERE, "features.jsonl"), rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
    writeFileSync(join(HERE, "sessions.json"), JSON.stringify(sessions, null, 2) + "\n");
    console.log(JSON.stringify({ calls: rows.length, sessions: sessions.length }));
  } else if (mode === "dossier") {
    const { dossiers } = analyse(true);
    mkdirSync(DOSSIER, { recursive: true });
    for (const [id, lines] of Object.entries(dossiers)) writeFileSync(join(DOSSIER, `${id}.md`), lines.join("\n"));
    console.log(JSON.stringify({ dossier: DOSSIER, sessions: Object.keys(dossiers) }));
  } else {
    console.log("usage: autopsy.ts features|dossier");
    process.exit(64);
  }
}
