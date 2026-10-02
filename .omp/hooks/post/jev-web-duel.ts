// Duel orchestrator (bead jev-n4eu): one composed web-result screen path over the
// frozen webscreen + injection-shadow evaluators. Captures the event bytes once,
// runs both Jev requests concurrently, returns a single merged transformation:
// webscreen unit-level replacement wins when it withholds, else the injection
// NOTICE, else undefined. Thresholds, questions, caps and log destinations are
// the makers' own (pass-through deps); enforce:false forces shadow on both.
// Project hook files are untouched; the j0er global wrappers delegate here.
import { makeWebscreenHandler } from "./jev-webscreen.ts";
import { makeInjectionShadowHandler } from "./jev-injection-shadow.ts";
import { useInfisicalKey } from "../../../work/jev-client/src/use-infisical-key.ts";

type WebDeps = Parameters<typeof makeWebscreenHandler>[0];
type InjDeps = Parameters<typeof makeInjectionShadowHandler>[0];

export type DuelDeps = {
  web?: WebDeps;
  inj?: InjDeps;
  /** When defined, forces both evaluators into shadow (false) or enforce (true). */
  enforce?: boolean;
};

function withEnforce(
  deps: Record<string, unknown> | undefined,
  enforce: boolean | undefined,
): Record<string, unknown> | undefined {
  if (enforce === undefined) return deps;
  return { ...deps, enforce };
}

export function makeDuelHandler(deps: DuelDeps = {}) {
  const web = makeWebscreenHandler(
    (withEnforce(
      deps.web as Record<string, unknown> | undefined,
      deps.enforce,
    ) ?? {}) as WebDeps,
  );
  const inj = makeInjectionShadowHandler(
    (withEnforce(
      deps.inj as Record<string, unknown> | undefined,
      deps.enforce,
    ) ?? {}) as InjDeps,
  );
  return async (event: unknown): Promise<unknown> => {
    const [w, i] = await Promise.all([
      web(event as never),
      inj(event as never),
    ]);
    if (w !== undefined) return w;
    return i ?? undefined;
  };
}

export default function jevWebDuelHook(
  pi: {
    on: (event: string, handler: (event: unknown) => Promise<unknown>) => void;
  },
  deps: DuelDeps = {},
): void {
  if (!deps.web?.ask && !deps.inj?.ask) useInfisicalKey();
  pi.on("tool_result", makeDuelHandler(deps));
}
