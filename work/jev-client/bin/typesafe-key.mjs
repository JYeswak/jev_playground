#!/usr/bin/env node
/**
 * Prints the TypeSafe key for omp's command-resolved `apiKey` in the profiles' models.yml.
 *
 * 1. The Infisical user session, the same command the profiles ran before; no jev code loads.
 * 2. Only if that fails (the 2026-09-28 outage: an expired user session silenced every new omp
 *    session's judge), the tested machine-identity lookup at the owner-approved origin
 *    (src/infisical-key.ts machineFallbackKey, APPROVED_INFISICAL_ORIGIN).
 *
 * omp gives the command 10 s: the user-session try is capped at 4 s (measured 1.3-1.7 s under
 * load on 2026-10-01). stdout carries only the key. Exit 1 means no key; omp retries after 30 s.
 */
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const PROJECT_ID = "42b194c3-89d7-4ebb-895f-dd77ddf005ba";
const local = path.join(homedir(), ".local", "bin", "infisical");
const binary = existsSync(local) ? local : "infisical";

function usable(value) {
  const key = String(value ?? "").trim();
  return key && !/\s/.test(key) ? key : undefined;
}

let key;
try {
  key = usable(execFileSync(binary, ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"],
    { timeout: 4000, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }));
} catch {
  key = undefined;
}
if (!key) {
  const { machineFallbackKey } = await import("../src/infisical-key.ts");
  key = usable(await machineFallbackKey());
}
if (!key) process.exit(1);
process.stdout.write(key);
