/**
 * Project extension registering the measured Banking77 classifier tool.
 */
import toolFactory from "../tools/jev-classify.ts";

type ZodLike = {
  object: (shape: Record<string, unknown>) => unknown;
  string: () => { min: (n: number) => unknown };
  array: (item: unknown) => { min: (n: number) => { max: (n: number) => unknown } };
};
type Host = { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevClassifyExtension(pi: Host) {
  pi.registerTool(toolFactory(pi));
}
