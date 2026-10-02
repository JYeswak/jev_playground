// SUPERSEDED by the duel (bead jev-n4eu): jev-webscreen-global.ts in this
// directory now runs both evaluators as one orchestrated handler. This file
// is a permanent no-op so no event is screened twice; it stays loaded (same
// basename keeps hook discovery and inventory drift keys stable) pending
// delete permission, then the five profile links go with it.
export default function jevInjectionGlobalRetiredHook(pi: { on: (event: string, handler: (event: unknown) => Promise<unknown>) => void }): void {
  pi.on("tool_result", () => Promise.resolve(undefined));
}
