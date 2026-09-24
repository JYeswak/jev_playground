/**
 * Model-callable claim check: does this evidence support this claim?
 * Advisory only. It never blocks anything; the caller reads the verdict.
 *
 * THE QUESTION. One Noul over state {claim, evidence}. The wording is the one
 * that beat Claude Haiku 4.5 on 400 SciFact claim/abstract pairs (bead jev-9er,
 * docs/demos/upstream-repro/noul-scifact-20260924.md, work/noul-scifact/run.py
 * QUESTION), with "abstract" renamed "evidence". The rename is ours; the SciFact
 * numbers were measured on the abstract wording, so they do not transfer by
 * assertion. This tool's own measurement is
 * docs/demos/upstream-repro/jev-claim-check-20260924.md.
 *
 * THE CUTS, fixed in that receipt's bar before any call: supported at p>=0.8,
 * unsupported at p<=0.2, unsure between. On the committed SciFact Jev rows those
 * cuts give supported 119/132 true and unsupported 212/216 false, 52/400 unsure.
 *
 * CONFIDENCE is derived, max(p, 1-p): a Noul answer carries no confidence field
 * (work/sdk/.../index.d.mts NoulResponse is {type, noul}).
 *
 * FAILURE. No key, missing SDK, transport or HTTP failure, or a throw: verdict
 * not_run, NOT_RUN in the text, no probability. A malformed answer (not a finite
 * number in [0, 1]) or an empty claim/evidence: verdict refused. Neither ever
 * returns supported/unsupported/unsure. Never prints a key.
 *
 * SCOPE. A claim that contains a number is refused before any call, with reason
 * numeric-out-of-scope and no verdict. Three designs for checking numbers failed
 * their preregistered bars (NEGATIVE_EVIDENCE.md R83: jev-10t, jev-2mp/jev-h8s,
 * jev-25r), so the tool says so instead of guessing. "Contains a number" is
 * numberTokens() below (the exact tokenizer of jev-h8s, unit-tested in
 * work/jev-claim-check/numeric-v2.test.mjs) over the claim with dates and times
 * blanked. Versions (1.13.0), names (SST-5, top-1) and 8+ digit runs do not count.
 */
import { askJev } from "../../work/jev-client/src/index.ts";

export const MODEL = "jev-1.13.0";
export const SUPPORTED_AT = 0.8;
export const UNSUPPORTED_AT = 0.2;
export const TIMEOUT_MS = 20000;
export const NUMERIC_REFUSAL = "numeric claims are out of scope (R83: 3 designs failed)";

const NUM = String.raw`\d[\d,.]*(?:[eE][-+]?\d+)?`;
const CHUNK = new RegExp(String.raw`(?<![A-Za-z0-9_.])(?<![A-Za-z]-)${NUM}(?:-${NUM})?(?:\/${NUM})*%?`, "g");
const THOUSANDS = /^\d{1,3}(?:,\d{3})+(?:\.\d+)?(?:[eE][-+]?\d+)?%?$/;
const DATE_TIME = /\d{4}-\d{2}-\d{2}(T[\d:.]+Z?)?|\b\d{1,2}:\d{2}(:\d{2})?Z?/g;

/** Exact number tokens: 2.6e-13, 0.0614, 75/219, 1,145, 96.0%, 1.1-4.7% whole; lists split at commas. */
export function numberTokens(blanked: string): Array<{ text: string; at: number }> {
  const out: Array<{ text: string; at: number }> = [];
  for (const m of blanked.matchAll(CHUNK)) {
    const text = m[0].replace(/[.,]+$/, "");
    const at = m.index ?? 0;
    const after = blanked[at + text.length] ?? "";
    if (/[A-Za-z0-9_]/.test(after)) continue;
    if (/^\d+\.\d+\.\d+/.test(text) && !text.includes("/")) continue;
    const parts = text.split(/\/|-(?=\d)/);
    if (parts.every((p) => !p.includes(",") || THOUSANDS.test(p))) {
      out.push({ text, at });
      continue;
    }
    let offset = 0;
    for (const piece of text.split(",")) {
      if (/\d/.test(piece)) out.push({ text: piece, at: at + offset });
      offset += piece.length + 1;
    }
  }
  return out.filter((t) => !/\d{8,}/.test(t.text));
}

/** The numbers a claim asserts, dates and times excluded. Any at all puts the claim out of scope. */
export function claimNumbers(claim: string): string[] {
  return numberTokens(claim.replace(DATE_TIME, (s) => " ".repeat(s.length))).map((t) => t.text);
}

export const QUESTION = {
  instructions: "Does the evidence support the claim?",
  criteria: {
    true: "The evidence states the claim or directly implies that it is true",
    false: "The evidence contradicts the claim, or does not address what the claim asserts",
  },
};

export type Verdict = "supported" | "unsupported" | "unsure";
export type AskerResult =
  | { ok: true; probability: unknown; latencyMs?: number; usage?: { input_tokens: number; output_tokens: number } }
  | { ok: false; reason: string };
export type Asker = (input: { claim: string; evidence: string }) => Promise<AskerResult>;

/** Pure policy. Returns null for anything that is not a probability. */
export function classify(probability: unknown): { verdict: Verdict; confidence: number } | null {
  if (typeof probability !== "number" || !Number.isFinite(probability) || probability < 0 || probability > 1) {
    return null;
  }
  const confidence = Math.max(probability, 1 - probability);
  if (probability >= SUPPORTED_AT) return { verdict: "supported", confidence };
  if (probability <= UNSUPPORTED_AT) return { verdict: "unsupported", confidence };
  return { verdict: "unsure", confidence };
}

export const liveAsker: Asker = async ({ claim, evidence }) => {
  const posted = await askJev({
    state: { claim, evidence },
    questions: { supports: QUESTION },
    model: MODEL,
    timeoutMs: TIMEOUT_MS,
  });
  if (!posted.ok) return { ok: false, reason: posted.reason };
  return { ok: true, probability: posted.scores["supports"], latencyMs: posted.latencyMs, usage: posted.usage };
};

type ToolHost = {
  zod: { object: (shape: Record<string, unknown>) => unknown; string: () => { min: (n: number) => unknown } };
};

function notRun(reason: string, detail?: string) {
  return {
    content: [{ type: "text", text: `calledModel=false verdict=not_run reason=${reason} NOT_RUN${detail ? `\n${detail}` : ""}` }],
    details: { verdict: "not_run", reason, calledModel: false, probability: null, confidence: null, latencyMs: null, usage: null },
  };
}

function refused(reason: string, calledModel: boolean, why = "The answer or input was not usable; nothing was checked.") {
  return {
    content: [{ type: "text", text: `calledModel=${calledModel} verdict=refused reason=${reason}\nREFUSED: no verdict. ${why}` }],
    details: { verdict: "refused", reason, calledModel, probability: null, confidence: null, latencyMs: null, usage: null },
  };
}

export default function jevClaimCheckTool(pi: ToolHost, asker?: Asker) {
  const ask = asker ?? liveAsker;
  return {
    name: "jev_claim_check",
    label: "Jev claim check",
    description:
      "Ask whether a piece of evidence supports a qualitative claim. Returns Jev's probability, a derived confidence, and a verdict: supported (p>=0.8), unsupported (p<=0.2), or unsure. Advisory only. Pass the claim sentence and the evidence text itself, not a file path. OUT OF SCOPE: a claim containing any number (count, score, fraction, percent, p-value) is refused with no verdict, because numeric checking failed three preregistered designs (R83); compare numbers against their source directly. Without a key returns not_run and says NOT_RUN.",
    parameters: pi.zod.object({
      claim: pi.zod.string().min(1),
      evidence: pi.zod.string().min(1),
    }),
    async execute(_id: string, params: { claim: string; evidence: string }) {
      const claim = typeof params?.claim === "string" ? params.claim.trim() : "";
      const evidence = typeof params?.evidence === "string" ? params.evidence.trim() : "";
      if (!claim) return refused("empty-input", false);
      const numbers = claimNumbers(claim);
      if (numbers.length) return refused("numeric-out-of-scope", false, `${NUMERIC_REFUSAL}. Numbers in the claim: ${numbers.join(", ")}. Compare each against its source directly.`);
      if (!evidence) return refused("empty-input", false);
      let result: AskerResult;
      try {
        result = await ask({ claim, evidence });
      } catch (err) {
        return notRun("throw", err instanceof Error ? err.message : String(err));
      }
      if (!result || result.ok !== true) {
        return notRun(result && "reason" in result && typeof result.reason === "string" ? result.reason : "unknown");
      }
      const c = classify(result.probability);
      if (!c) return refused("malformed", true);
      const p = result.probability as number;
      return {
        content: [{
          type: "text",
          text: `calledModel=true verdict=${c.verdict} p=${p.toFixed(3)} confidence=${c.confidence.toFixed(3)} cuts=${SUPPORTED_AT}/${UNSUPPORTED_AT} model=${MODEL}`,
        }],
        details: {
          verdict: c.verdict,
          reason: null,
          calledModel: true,
          probability: p,
          confidence: c.confidence,
          latencyMs: typeof result.latencyMs === "number" ? result.latencyMs : null,
          usage: result.usage ?? null,
        },
      };
    },
  };
}
