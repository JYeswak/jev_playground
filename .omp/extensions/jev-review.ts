/**
 * Project extension: observe git diff/show calls without sending data or re-running git.
 * The scorer remains disabled until recipient and local execution are separately authorized.
 */
import ompJevReview from "../../work/omp-jev-review/src/index.ts";

type ZodLike = { object: (shape: Record<string, unknown>) => unknown };
type Host = Parameters<typeof ompJevReview>[0] & { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevReviewExtension(pi: Host) {
  ompJevReview(pi);
  pi.registerTool({
    name: "jev_review_ext_probe",
    label: "Jev review ext probe",
    description: "Load probe. Not a product tool.",
    parameters: pi.zod.object({}),
    async execute() {
      return { content: [{ type: "text", text: "ext-probe-ok" }], details: {} };
    },
  });
}
