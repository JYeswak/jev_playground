// Global duel entry (bead jev-n4eu): machine-wide composed web-result screen
// outside the jev repo. No-ops inside /Users/josh/Developer/jev (project
// hooks cover it). inj ENFORCES annotate-only (never withholds: annotate keeps
// content, so class=advisory, fail-open); web stays shadow. Flipped 2026-10-02
// on the j0er bar (0/100 false organic + fpkw availability + bqv0 L3).
import { makeDuelHandler } from "/Users/josh/Developer/jev/.omp/hooks/post/jev-web-duel.ts";
import { isJevRepoPath } from "/Users/josh/Developer/jev/work/jev-j0er/repo-scope.ts";
import { useInfisicalKey } from "/Users/josh/Developer/jev/work/jev-client/src/use-infisical-key.ts";

const REPO = "/Users/josh/Developer/jev";

const screen = makeDuelHandler({ web: { enforce: false }, inj: { enforce: true, mode: "annotate" } });

export default function jevWebscreenGlobalHook(pi: { on: (event: string, handler: (event: unknown, ctx?: { cwd?: unknown }) => Promise<unknown>) => void }): void {
  useInfisicalKey();
  pi.on("tool_result", (event, ctx) => {
    if (isJevRepoPath(ctx?.cwd, REPO)) return Promise.resolve(undefined);
    return screen(event);
  });
}
