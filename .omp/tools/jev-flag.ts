/**
 * Model-callable injection flag. Advisory ONLY: annotates, never vetoes.
 *
 * The caller passes text; the asker returns a Noul probability that the text
 * subverts the assistant. FLAG at p>=0.80, NOTE at 0.50-0.80, SILENT below.
 * Keyless/unconfigured asker returns ordered=false reason=unconfigured and
 * does not throw. Never prints a key.
 */
import { liveAsker } from "../../work/nev-injection/src/live-flag.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";
import { ASSISTANT, QUESTION } from "../../work/jev-a9fv/seat.mjs";
export function annotate(probability) {
  if (typeof probability !== "number" || !Number.isFinite(probability)) {
    return { level: "unknown", text: "" };
  }
  if (probability >= 0.8) {
    return { level: "flag", text: `FLAG: likely prompt injection (p=${probability.toFixed(2)}). Human glance advised; not a verdict.` };
  }
  if (probability >= 0.5) {
    return { level: "note", text: `Note: uncertain injection signal (p=${probability.toFixed(2)}).` };
  }
  return { level: "silent", text: "" };
}

export default function jevFlagTool(pi, asker) {
  if (!asker) useInfisicalKey();
  const ask = asker || liveAsker;
  return {
    name: "jev_flag",
    label: "Jev injection flag",
    description:
      "Score text for prompt-injection risk and return an advisory annotation. Flag-only: never blocks, never vetoes. Without a key returns unconfigured and says NOT_RUN.",
    parameters: pi.zod.object({
      text: pi.zod.string().min(1),
    }),
    async execute(_id, params) {
      try {
        const result = await ask({ assistant: ASSISTANT, userMessage: params.text, question: QUESTION });
        if (!result.ok) {
          return {
            content: [{ type: "text", text: `ordered=false reason=${result.reason} NOT_RUN` }],
            details: { level: "unknown", reason: result.reason, calledModel: result.calledModel === true, probability: null },
          };
        }
        const a = annotate(result.probability);
        const head = a.level === "silent" ? "ordered=true silent" : `ordered=true level=${a.level}`;
        return {
          content: [{ type: "text", text: a.text ? `${head}\n${a.text}` : head }],
          details: { level: a.level, reason: null, calledModel: true, probability: result.probability },
        };
      } catch (err) {
        const reason = err instanceof Error ? err.message : "throw";
        return {
          content: [{ type: "text", text: `ordered=false reason=throw NOT_RUN\n${reason}` }],
          details: { level: "unknown", reason: "throw", calledModel: false, probability: null },
        };
      }
    },
  };
}
