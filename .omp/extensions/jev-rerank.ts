/**
 * Project extension. omp does not scan `.omp/tools`. It does scan
 * `<cwd>/.omp/extensions` (omp://extension-loading.md). This wraps the existing
 * tool factory. It does not rewrite the tool.
 */
import toolFactory from "../tools/jev-rerank.ts";

type ZodLike = { object: (shape: Record<string, unknown>) => unknown };
type Host = { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevRerankExtension(pi: Host) {
  pi.registerTool(toolFactory(pi as never));
  pi.registerTool({
    name: "jev_rerank_ext_probe",
    label: "Jev rerank ext probe",
    description: "Load probe. Not a product tool.",
    parameters: pi.zod.object({}),
    async execute() {
      return { content: [{ type: "text", text: "ext-probe-ok" }], details: {} };
    },
  });
}
