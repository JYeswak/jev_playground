// Fixture dead-code hook for installer tests: a default export that loads
// cleanly, but its host event registration sits behind a statically-false
// branch, so no handler ever registers. Must refuse: textual presence of
// pi.on is not registration; only executed registration counts.
export default function deadHookFixture(pi: { on: (event: string, handler: (event: unknown) => Promise<unknown>) => void }): void {
  if (false) {
    pi.on("tool_call", async () => ({ block: false, reason: "dead" }));
  }
}
