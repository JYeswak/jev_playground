/**
 * TypeSafe key from Infisical, for omp sessions only.
 *
 * Panes are launched without TYPESAFE_API_KEY, so every Jev tool and extension in them answered
 * NOT_RUN / unconfigured (measured 2026-09-25: no pane process had the key in its environment).
 * This runs the same command the omp profiles' models.yml already use for the typesafe provider
 * (bead jev-m1e9) and keeps the result in this process's memory. It never sets process.env, so
 * commands a pane runs never see the key, and it never logs the value or stderr.
 *
 * The cache lives TTL_MS so a rotated key is picked up without restarting the pane. A failed
 * lookup is cached for FAIL_TTL_MS so a missing Infisical does not add seconds to every call.
 */
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

export const PROJECT_ID = "42b194c3-89d7-4ebb-895f-dd77ddf005ba";
export const TTL_MS = 10 * 60 * 1000;
export const FAIL_TTL_MS = 60 * 1000;
const TIMEOUT_MS = 15_000;

export type Runner = (file: string, args: string[], timeoutMs: number) => Promise<string>;

const defaultRunner: Runner = (file, args, timeoutMs) => {
  const { promise, resolve, reject } = Promise.withResolvers<string>();
  execFile(file, args, { timeout: timeoutMs, maxBuffer: 64 * 1024 }, (error, stdout) => {
    if (error) reject(new Error("infisical lookup failed"));
    else resolve(String(stdout));
  });
  return promise;
};

/** ~/.local/bin/infisical first: brew's newer build speaks an API our instance does not serve. */
export function infisicalBinary(home: string = homedir(), exists: (p: string) => boolean = existsSync): string {
  const local = path.join(home, ".local", "bin", "infisical");
  return exists(local) ? local : "infisical";
}

export function makeInfisicalKeyProvider(
  run: Runner = defaultRunner,
  now: () => number = Date.now,
  binary: string = infisicalBinary(),
): () => Promise<string | undefined> {
  let cached: { value: string | undefined; until: number } | undefined;
  let inflight: Promise<string | undefined> | undefined;
  return async () => {
    if (cached && now() < cached.until) return cached.value;
    if (inflight) return inflight;
    inflight = (async () => {
      let value: string | undefined;
      try {
        const out = await run(
          binary,
          ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"],
          TIMEOUT_MS,
        );
        const key = out.trim();
        value = key && !/\s/.test(key) ? key : undefined;
      } catch {
        value = undefined;
      }
      cached = { value, until: now() + (value ? TTL_MS : FAIL_TTL_MS) };
      inflight = undefined;
      return value;
    })();
    return inflight;
  };
}

export const infisicalKeyProvider = makeInfisicalKeyProvider();
