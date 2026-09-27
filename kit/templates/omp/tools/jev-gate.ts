/**
 * Model-callable RISK gate over a shell command.
 * Uses kit/src/gate.ts's frozen five-Noul design; it never executes the command.
 * Without Jev it returns NOT_RUN rather than making a local decision.
 */
import { gateCommand, type GateResult } from "../jev-kit/gate.ts";
import { useInfisicalKey } from "../jev-kit/use-infisical-key.ts";

type ToolHost = {
  zod: { object: (shape: Record<string, unknown>) => unknown; string: () => { min: (n: number) => unknown } };
};
type GateAsker = (options: Parameters<typeof gateCommand>[0]) => Promise<GateResult>;

export default function jevGateTool(pi: ToolHost, asker?: GateAsker) {
  if (!asker) useInfisicalKey();
  return {
    name: "jev_gate",
    label: "Jev command safety gate",
    description:
      "Assess whether a shell command risks exfiltration, destruction, privilege escalation, irreversible publishing, or secret staging using the measured five-Noul RISK gate (cut 0.5). Returns a flag only; never executes or blocks the command. Without Jev returns NOT_RUN.",
    parameters: pi.zod.object({ command: pi.zod.string().min(1) }),
    async execute(_id: string, params: { command: string }) {
      try {
        const result = await gateCommand({ command: params.command, ...(asker ? { ask: asker } : {}) });
        if (!result.ok) {
          return {
            content: [{ type: "text", text: `verdict=not_run reason=${result.reason} NOT_RUN` }],
            details: { verdict: "not_run", reason: result.reason, flag: null, scores: null, model: result.model },
          };
        }
        return {
          content: [{ type: "text", text: `flag=${result.flag} maxScore=${result.maxScore.toFixed(3)} cut=0.5 model=${result.model}` }],
          details: { verdict: result.flag ? "flag" : "allow", flag: result.flag, maxScore: result.maxScore, scores: result.scores, cut: 0.5, model: result.model, latencyMs: result.latencyMs, usage: result.usage ?? null },
        };
      } catch (error) {
        const reason = error instanceof Error ? error.message : String(error);
        return {
          content: [{ type: "text", text: `verdict=not_run reason=${reason} NOT_RUN` }],
          details: { verdict: "not_run", reason, flag: null, scores: null, model: null },
        };
      }
    },
  };
}
