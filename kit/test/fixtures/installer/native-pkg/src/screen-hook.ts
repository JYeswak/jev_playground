// Fixture native hook entry for the result-screen surface (installer tests).
// Same real hook ABI as gate-hook.ts, registered on the tool_result event.
// Declared OFF in fixtures, so it never installs; present so the declared
// surface has a real module shape. Pure, no I/O.
export type FixturePi = {
  on: (event: string, handler: (event: unknown) => Promise<unknown>) => void;
};

async function onToolResult(event: unknown): Promise<unknown> {
  const command = (event as { command?: unknown } | null)?.command;
  if (typeof command === "string" && command.includes("rm -rf")) {
    return { block: true, reason: "fixture-risk" };
  }
  return { block: false, reason: "fixture-allow" };
}

export default function screenHookFixture(pi: FixturePi): void {
  pi.on("tool_result", onToolResult);
}
