/** Project extension for the Jev command gate. */
import toolFactory from "../tools/jev-gate.ts";

type ZodLike = { object: (shape: Record<string, unknown>) => unknown; string: () => { min: (n: number) => unknown } };
type Host = { zod: ZodLike; registerTool: (tool: unknown) => void };

export default function jevGateExtension(pi: Host) {
  pi.registerTool(toolFactory(pi as never));
}
