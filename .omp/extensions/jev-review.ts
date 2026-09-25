/**
 * Project extension: the advisory diff review scorer (work/omp-jev-review, bead jev-k9z.2).
 * On `git diff` / `git show` of our own code it scores the diff with Jev and, when the boundary
 * score is at least 0.9, appends one advisory line to that git output. It never blocks.
 *
 * The key comes from Infisical into this process's memory (use-infisical-key.ts); panes run
 * without TYPESAFE_API_KEY in their environment. Rolled out to every pane by Joshua,
 * 2026-09-25: "yeah lets roll out all features to every pane".
 */
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";
import ompJevReview from "../../work/omp-jev-review/src/index.ts";

type ZodLike = { object: (shape: Record<string, unknown>) => unknown };
type Host = Parameters<typeof ompJevReview>[0] & { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevReviewExtension(pi: Host) {
  useInfisicalKey();
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
