/**
 * Project extension: registers the injection-flag tool plus a load probe.
 * Mirrors .omp/extensions/jev-rerank.ts (the proven shape).
 *
 * NOTE on arg order (latent defect, inert today): extension ToolDefinition
 * execute is (id, params, signal, onUpdate, ctx); custom-tool execute is
 * (id, params, onUpdate, ctx, signal). This wrapper reads only (id, params),
 * so the difference cannot bite here. Any future use of signal must pick the
 * extension order deliberately.
 */
import toolFactory from "../tools/jev-flag.ts";

type ZodLike = {
  object: (shape: Record<string, unknown>) => unknown;
  string: () => { min: (n: number) => unknown };
};
type Host = { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevFlagExtension(pi: Host) {
  pi.registerTool(toolFactory(pi as never));
  pi.registerTool({
    name: "jev_flag_ext_probe",
    label: "Jev flag ext probe",
    description: "Load probe. Not a product tool.",
    parameters: pi.zod.object({}),
    async execute() {
      return { content: [{ type: "text", text: "ext-probe-ok" }], details: {} };
    },
  });
}
