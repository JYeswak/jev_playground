// Global duel entry (bead jev-n4eu): machine-wide composed web-result screen
// outside the jev repo. No-ops inside /Users/josh/Developer/jev (project
// hooks cover it); enforces nothing anywhere (enforce:false -> shadow only,
// logs would-withhold to the standard shadow logs); never touches
// process.env: shadow mode travels as a factory option into both evaluators.
import { makeDuelHandler } from "/Users/josh/Developer/jev/.omp/hooks/post/jev-web-duel.ts";
import { useInfisicalKey } from "/Users/josh/Developer/jev/work/jev-client/src/use-infisical-key.ts";

const REPO = "/Users/josh/Developer/jev";

const screen = makeDuelHandler({ enforce: false });

export default function jevWebscreenGlobalHook(pi: { on: (event: string, handler: (event: unknown, ctx?: { cwd?: unknown }) => Promise<unknown>) => void }): void {
  useInfisicalKey();
  pi.on("tool_result", (event, ctx) => {
    const cwd = String(ctx?.cwd ?? "");
    if (cwd === REPO || cwd.startsWith(REPO + "/")) return Promise.resolve(undefined);
    return screen(event);
  });
}
