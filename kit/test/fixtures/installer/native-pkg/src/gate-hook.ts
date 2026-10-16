// Fixture native hook entry for installer profile-target tests.
// Mirrors the real native hook ABI (see .omp/hooks/post/session-stop.ts):
// a default factory receiving pi and registering handlers via pi.on.
// Pure and deterministic, no I/O, never loaded outside owned test homes,
// except the probe-gated load marker below.
//
// Load marker (wiring proof, throwaway-only): when JEV_HOOK_PROBE_DIR is set,
// registration appends {nonce, family, ts} to hook-loads.jsonl there, so a
// host run proves genuine consumption. Unset (production, installer default)
// means fully silent: no file touches.
import { appendFileSync } from "node:fs";
import { join } from "node:path";

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
  const probeDir = process.env["JEV_HOOK_PROBE_DIR"];
  const nonce = process.env["JEV_HOOK_PROBE_NONCE"];
  if (probeDir !== undefined && probeDir !== "" && nonce !== undefined && nonce !== "") {
    appendFileSync(join(probeDir, "hook-loads.jsonl"), JSON.stringify({ nonce, family: "gate", ts: Date.now() }) + "\n");
  }
}
