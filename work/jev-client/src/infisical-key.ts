/**
 * TypeSafe key from Infisical, for omp sessions only.
 * User-session lookup falls back to universal-auth machine identity credentials
 * from ~/.config/infisical/zeststream.env. Secrets and tokens stay in memory and
 * are never printed, stored in process.env, or included in errors.
 */
import { execFile } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

export const PROJECT_ID = "42b194c3-89d7-4ebb-895f-dd77ddf005ba";
export const TTL_MS = 10 * 60 * 1000;
export const FAIL_TTL_MS = 60 * 1000;
const TIMEOUT_MS = 15_000;

export type Runner = (file: string, args: string[], timeoutMs: number, env?: Record<string, string>) => Promise<string>;
export type FileReader = (file: string) => string;

type MachineConfig = { clientId: string; clientSecret: string; apiUrl: string; projectId?: string; projectIds?: string; environment?: string; loaded?: string };

const defaultRunner: Runner = (file, args, timeoutMs, env) => {
  const { promise, resolve, reject } = Promise.withResolvers<string>();
  execFile(file, args, { timeout: timeoutMs, maxBuffer: 64 * 1024, env: {...process.env, ...env} }, (error, stdout) => {
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

function parseExport(text: string, name: string): string | undefined {
  const line = text.split(/\r?\n/).find((value) => new RegExp(`^\\s*export\\s+${name}=`).test(value));
  if (!line) return undefined;
  const raw = line.slice(line.indexOf("=") + 1).trim();
  if ((raw.startsWith("\"") && raw.endsWith("\"")) || (raw.startsWith("'") && raw.endsWith("'"))) return raw.slice(1, -1);
  return raw.split(" #", 1)[0].trim() || undefined;
}

export function machineIdentityConfig(home: string = homedir(), read: FileReader = (file) => readFileSync(file, "utf8")): MachineConfig | undefined {
  try {
    const text = read(path.join(home, ".config", "infisical", "zeststream.env"));
    const clientId = parseExport(text, "INFISICAL_CLIENT_ID");
    const clientSecret = parseExport(text, "INFISICAL_CLIENT_SECRET");
    const apiUrl = parseExport(text, "INFISICAL_API_URL");
    const projectId = parseExport(text, "INFISICAL_PROJECT_ID");
    const projectIds = parseExport(text, "INFISICAL_PROJECT_IDS");
    const environment = parseExport(text, "INFISICAL_ENV");
    const loaded = parseExport(text, "INFISICAL_LOADED");
    return clientId && clientSecret && apiUrl ? {clientId, clientSecret, apiUrl, projectId, projectIds, environment, loaded} : undefined;
  } catch {
    return undefined;
  }
}

async function userSessionKey(run: Runner, binary: string): Promise<string | undefined> {
  try {
    const out = await run(binary, ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"], TIMEOUT_MS);
    const key = out.trim();
    return key && !/\s/.test(key) ? key : undefined;
  } catch {
    return undefined;
  }
}

async function machineIdentityKey(run: Runner, binary: string, home: string, read: FileReader): Promise<string | undefined> {
  const config = machineIdentityConfig(home, read);
  if (!config) return undefined;
  try {
    const tokenOutput = await run(binary, ["login", "--method", "universal-auth", "--client-id", config.clientId, "--client-secret", config.clientSecret, "--domain", config.apiUrl, "--plain", "--silent"], TIMEOUT_MS, {
      INFISICAL_CLIENT_ID: config.clientId,
      INFISICAL_CLIENT_SECRET: config.clientSecret,
      INFISICAL_API_URL: config.apiUrl,
      ...(config.projectId ? {INFISICAL_PROJECT_ID: config.projectId} : {}),
      ...(config.projectIds ? {INFISICAL_PROJECT_IDS: config.projectIds} : {}),
      ...(config.environment ? {INFISICAL_ENV: config.environment} : {}),
      ...(config.loaded ? {INFISICAL_LOADED: config.loaded} : {}),
    });
    const token = tokenOutput.trim();
    if (!token || /\s/.test(token)) return undefined;
    const out = await run(binary, ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"], TIMEOUT_MS, {
      INFISICAL_API_URL: config.apiUrl,
      INFISICAL_TOKEN: token,
    });
    const key = out.trim();
    return key && !/\s/.test(key) ? key : undefined;
  } catch {
    return undefined;
  }
}

export function makeInfisicalKeyProvider(
  run: Runner = defaultRunner,
  now: () => number = Date.now,
  binary: string = infisicalBinary(),
  home: string = homedir(),
  read: FileReader = (file) => readFileSync(file, "utf8"),
): () => Promise<string | undefined> {
  let cached: { value: string | undefined; until: number } | undefined;
  let inflight: Promise<string | undefined> | undefined;
  return async () => {
    if (cached && now() < cached.until) return cached.value;
    if (inflight) return inflight;
    inflight = (async () => {
      const value = await userSessionKey(run, binary) ?? await machineIdentityKey(run, binary, home, read);
      cached = {value, until: now() + (value ? TTL_MS : FAIL_TTL_MS)};
      inflight = undefined;
      return value;
    })();
    return inflight;
  };
}

export const infisicalKeyProvider = makeInfisicalKeyProvider();
