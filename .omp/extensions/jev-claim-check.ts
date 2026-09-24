/**
 * Project extension: registers jev_claim_check plus a load probe.
 * Mirrors .omp/extensions/jev-screen.ts (the proven shape).
 *
 * Extension execute is (id, params, signal, onUpdate, ctx); custom-tool execute
 * is (id, params, onUpdate, ctx, signal). The tool reads only (id, params), so
 * the difference cannot bite here.
 */
import toolFactory from "../tools/jev-claim-check.ts";

type ZodLike = {
  object: (shape: Record<string, unknown>) => unknown;
  string: () => { min: (n: number) => unknown };
};
type Host = { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevClaimCheckExtension(pi: Host) {
  pi.registerTool(toolFactory(pi));
  pi.registerTool({
    name: "jev_claim_check_ext_probe",
    label: "Jev claim check ext probe",
    description: "Load probe. Not a product tool.",
    parameters: pi.zod.object({}),
    async execute() {
      return { content: [{ type: "text", text: "ext-probe-ok" }], details: {} };
    },
  });
}
