/** Project-installed Jev RISK gate; delegates to the kit implementation. */
import { gateCommand, type GateAsk, type GateResult } from "../../kit/src/gate.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

type ToolHost = { zod: { object: (shape: Record<string, unknown>) => unknown; string: () => { min: (n: number) => unknown } } };

export default function jevGateTool(pi: ToolHost, asker?: GateAsk) {
  if (!asker) useInfisicalKey();
  return {
    name: "jev_gate",
    label: "Jev command safety gate",
    description: "Assess shell-command risk with the measured five-Noul RISK gate (cut 0.5). Returns refusal for flagged commands and never executes them. Without Jev returns NOT_RUN.",
    parameters: pi.zod.object({ command: pi.zod.string().min(1) }),
    async execute(_id: string, params: { command: string }) {
      try {
        const result: GateResult = await gateCommand({ command: params.command, ...(asker ? { ask: asker } : {}) });
        if (!result.ok) return { content: [{ type: "text", text: `verdict=not_run reason=${result.reason} NOT_RUN` }], details: { verdict: "not_run", reason: result.reason, flag: null, scores: null, model: result.model } };
        const verdict = result.flag ? "refuse" : "allow";
        return { content: [{ type: "text", text: `verdict=${verdict} flag=${result.flag} maxScore=${result.maxScore.toFixed(3)} cut=0.5 model=${result.model}` }], details: { verdict, flag: result.flag, maxScore: result.maxScore, scores: result.scores, cut: 0.5, model: result.model, latencyMs: result.latencyMs, usage: result.usage ?? null } };
      } catch (error) {
        const reason = error instanceof Error ? error.message : String(error);
        return { content: [{ type: "text", text: `verdict=not_run reason=${reason} NOT_RUN` }], details: { verdict: "not_run", reason, flag: null, scores: null, model: null } };
      }
    },
  };
}
