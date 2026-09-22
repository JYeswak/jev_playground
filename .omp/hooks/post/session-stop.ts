/**
 * Project session_stop hook. Discovered from .omp/hooks/post/.
 *
 * Contract (omp SessionStopEvent / SessionStopEventResult):
 *   continue + additionalContext, or decision block + reason,
 *   requests one model-visible continuation. First non-empty wins.
 *
 * This hook never blocks and never calls Jev. If a cookbook demo is
 * missing and this stop is not already a continuation, it asks for one
 * more turn. stop_hook_active returns nothing, so it cannot loop.
 */
import { existsSync } from "node:fs";
import { resolve } from "node:path";

export const MISSING_DEMOS = [
  "demos/consistency/demo.mjs",
  "demos/preparsed/demo.mjs",
];

export function decideStop(
  event: { stop_hook_active?: boolean; signal?: { aborted?: boolean } },
  exists: (path: string) => boolean,
): { continue: true; additionalContext: string } | undefined {
  if (event.stop_hook_active || event.signal?.aborted) return undefined;
  const missing = MISSING_DEMOS.find((path) => !exists(path));
  if (!missing) return undefined;
  return {
    continue: true,
    additionalContext:
      `session_stop: ${missing} is not on disk. Build that keyless demo from the matching cookbook, ` +
      `name the command in README.md, and do not spend a key. Then stop.`,
  };
}

export default function sessionStopHook(pi: {
  on: (event: string, handler: (event: unknown) => Promise<unknown>) => void;
}): void {
  pi.on("session_stop", async (event) => {
    try {
      const typed = event as { stop_hook_active?: boolean; signal?: { aborted?: boolean } };
      return decideStop(typed, (path) => existsSync(resolve(path)));
    } catch {
      return undefined;
    }
  });
}
