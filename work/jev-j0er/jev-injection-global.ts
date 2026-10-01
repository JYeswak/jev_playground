// Global shadow install (bead jev-j0er): machine-wide would-withhold logging for
// tool results outside the jev repo. No-ops inside /Users/josh/Developer/jev
// (project hooks cover it); enforces nothing anywhere (enforce: false) and
// never touches process.env: shadow mode travels as a factory option.
import { makeInjectionShadowHandler } from "/Users/josh/Developer/jev/.omp/hooks/post/jev-injection-shadow.ts";
import { useInfisicalKey } from "/Users/josh/Developer/jev/work/jev-client/src/use-infisical-key.ts";

const REPO = "/Users/josh/Developer/jev";

const screen = makeInjectionShadowHandler({ enforce: false });

export default function jevInjectionGlobalHook(pi: { on: (event: string, handler: (event: unknown, ctx?: { cwd?: unknown }) => Promise<unknown>) => void }): void {
  useInfisicalKey();
  pi.on("tool_result", (event, ctx) => {
    const cwd = String(ctx?.cwd ?? "");
    if (cwd === REPO || cwd.startsWith(REPO + "/")) return Promise.resolve(undefined);
    return screen(event as never);
  });
}
