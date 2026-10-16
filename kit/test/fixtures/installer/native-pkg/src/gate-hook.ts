// Fixture native hook entry for installer profile-target tests.
// Mirrors the real native hook ABI (see .omp/hooks/post/session-stop.ts):
// a default factory receiving pi and registering handlers via pi.on.
// Pure and deterministic, no I/O, never loaded outside owned test homes.
export type FixturePi = {
  on: (event: string, handler: (event: unknown) => Promise<unknown>) => void;
};

export type FixtureHookVerdict = {
  block: boolean;
  reason: string;
};

async function onToolCall(event: unknown): Promise<unknown> {
  const command = (event as { command?: unknown } | null)?.command;
  if (typeof command === "string" && command.includes("rm -rf")) {
    return { block: true, reason: "fixture-risk" };
  }
  return { block: false, reason: "fixture-allow" };
}

export default function gateHookFixture(pi: FixturePi): void {
  pi.on("tool_call", onToolCall);
}
