/**
 * omp-jev-route — observe-only routing ADVICE for omp (never routes anything).
 *
 * WHY THIS ONE CALLS JEV. Per-turn model routing's SAVINGS claim inverts on
 * our sessions (do not re-litigate it here), but the surviving signal was the
 * blockedBy histogram: a judgment about which turns are HARD. Hardness has no
 * cheap regex — no literal distinguishes "rename this variable" from "redesign
 * this boundary". A judge earns its seat exactly where a rule cannot be written.
 *
 * NEVER routes, NEVER blocks, NEVER throws into the host. Returns undefined on
 * every path. A failed call records `route_error`, never a scored pass.
 * The WIRE SHAPE lives in work/jev-client and nowhere else (askJev).
 */

const DECISION = "com.zeststream.omp-jev-route.decision.v1";
const DIAG = "com.zeststream.omp-jev-route.diagnostic.v1";

const MAX_PROMPT = 4000;
import { askJev } from "../../jev-client/src/index.ts";
import { appendProcessDecision } from "./process.mjs";
import { recording } from "../../jev-score-register/register.mjs";

/**
 * Export what this extension already computes. Every Jev score it produces is
 * appended to the register instead of being discarded when the run ends.
 * The register stores a sha256 of the input and NEVER the input itself, and it is
 * not a cache: it records that a question was answered, it never answers one.
 */
const REGISTER = process.env.JEV_SCORE_REGISTER ?? "work/jev-score-register/scores.jsonl";
const ask = recording(askJev, { path: REGISTER, extension: "omp-jev-route", model: "jev-1.13.0" });

/**
 * Frozen questions. Routing advice only; the scores predict nothing until a
 * later unit measures them against outcomes, and this file says so.
 */
export const QUESTIONS = {
  needs_heavyweight:
    "Does this turn require multi-step reasoning, unfamiliar code, or careful judgment (as opposed to a mechanical edit)?",
  mechanical:
    "Is this turn a mechanical edit: a rename, format, move, config tweak, or other routine change?",
};

/** Advice mapping, stated not tuned: heavyweight wins ties toward caution. */
export function suggestTier(probabilities) {
  const heavy = probabilities.needs_heavyweight ?? 0;
  const mech = probabilities.mechanical ?? 0;
  if (heavy >= 0.5 && heavy >= mech) return "heavy";
  if (mech >= 0.5) return "light";
  return "default";
}

function promptText(event) {
  if (!event || typeof event !== "object") return undefined;
  // turn_start carries only {type, turnIndex, timestamp} — measured live,
  // so this subscribes to context, whose messages[] holds the user text.
  const direct = [event.prompt, event.message, event.text, event.input];
  for (const c of direct) {
    if (typeof c === "string" && c.trim().length > 0) return c.slice(0, MAX_PROMPT);
  }
  const messages = Array.isArray(event.messages) ? event.messages : [];
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    if (!m || typeof m !== "object" || m.role !== "user") continue;
    if (typeof m.content === "string" && m.content.trim().length > 0) {
      return m.content.slice(0, MAX_PROMPT);
    }
    if (Array.isArray(m.content)) {
      const text = m.content
        .filter((p) => p && typeof p === "object" && p.type === "text" && typeof p.text === "string")
        .map((p) => p.text)
        .join("\n");
      if (text.trim().length > 0) return text.slice(0, MAX_PROMPT);
    }
  }
  return undefined;
}

export default function ompJevRoute(pi) {
  pi.on("context", async (event) => {
    try {
      if (process.env.OMP_JEV_ROUTE_DEBUG === "1") {
        try {
          await pi.appendEntry(DIAG, {
            kind: "turn_event_keys",
            eventKeys: event && typeof event === "object" ? Object.keys(event) : typeof event,
            timestamp: new Date().toISOString(),
          });
        } catch { /* never break the session */ }
      }
      const prompt = promptText(event);
      const toolCallId = typeof event?.toolCallId === "string" ? event.toolCallId : null;
      await appendProcessDecision(pi.appendEntry.bind(pi), event);
      if (prompt === undefined) return undefined;
      const r = await ask({ state: { prompt }, questions: QUESTIONS });
      if (!r.ok) {
        try {
          await pi.appendEntry(DECISION, {
            kind: "route_error", toolCallId, reason: r.reason,
            error: r.error, latencyMs: r.latencyMs,
            timestamp: new Date().toISOString(),
          });
        } catch { /* never break the session */ }
        return undefined;
      }
      const tier = suggestTier(r.scores);
      try {
        await pi.appendEntry(DECISION, {
          kind: "route_scored", toolCallId, prompt: prompt.slice(0, 500),
          probabilities: r.scores, suggested_tier: tier,
          latencyMs: r.latencyMs, model: r.model,
          timestamp: new Date().toISOString(),
        });
      } catch { /* never break the session */ }
      return undefined;
    } catch {
      return undefined;
    }
  });
}
