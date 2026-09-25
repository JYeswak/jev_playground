/**
 * Project extension: registers the seat-faithful screen tool plus a load probe.
 * Mirrors .omp/extensions/jev-flag.ts (the proven shape).
 *
 * Same latent arg-order note as the flag wrapper: extension ToolDefinition
 * execute is (id, params, signal, onUpdate, ctx); custom-tool execute is
 * (id, params, onUpdate, ctx, signal). This wrapper reads only (id, params),
 * so the difference cannot bite here.
 */
import toolFactory from "../tools/jev-screen.ts";

type ZodLike = {
  object: (shape: Record<string, unknown>) => unknown;
  string: () => { min: (n: number) => unknown };
};
type Host = { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevScreenExtension(pi: Host) {
  pi.registerTool(toolFactory(pi as never));
  pi.registerTool({
    name: "jev_screen_ext_probe",
    label: "Jev screen ext probe",
    description: "Load probe. Not a product tool.",
    parameters: pi.zod.object({}),
    async execute() {
      return { content: [{ type: "text", text: "ext-probe-ok" }], details: {} };
    },
  });
}
