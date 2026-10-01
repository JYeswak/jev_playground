/**
 * TypeSafe key from Infisical, for omp sessions only.
 * User-session lookup comes first. Machine-identity fallback goes only to the owner-approved
 * HTTPS origin (APPROVED_INFISICAL_ORIGIN); any other origin fails closed before the credential POST.
 * Secrets and tokens stay in memory and are never printed, stored in process.env, or included in errors.
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
type MachineApproval = { origin: string; transport?: typeof fetch };
type ApprovedMachine = { baseUrl: URL; transport: typeof fetch };

export function makeDefaultRunner(
  execute: typeof execFile = execFile,
  parentEnv: NodeJS.ProcessEnv = process.env,
): Runner {
  const commonEnv: NodeJS.ProcessEnv = {
    PATH: parentEnv.PATH,
    HOME: parentEnv.HOME,
    TMPDIR: parentEnv.TMPDIR,
  };
  return (file, args, timeoutMs, env) => {
    const childEnv: NodeJS.ProcessEnv = env ? { ...commonEnv } : commonEnv;
    if (env?.INFISICAL_API_URL) childEnv.INFISICAL_API_URL = env.INFISICAL_API_URL;
    if (env?.INFISICAL_TOKEN) childEnv.INFISICAL_TOKEN = env.INFISICAL_TOKEN;
    const { promise, resolve, reject } = Promise.withResolvers<string>();
    execute(file, args, { timeout: timeoutMs, maxBuffer: 64 * 1024, env: childEnv }, (error, stdout) => {
      if (error) reject(new Error("infisical lookup failed"));
      else resolve(String(stdout));
    });
    return promise;
  };
}

const defaultRunner = makeDefaultRunner();

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

function approvedMachine(approval?: MachineApproval): ApprovedMachine | undefined {
  if (!approval) return undefined;
  try {
    const baseUrl = new URL(approval.origin);
    return baseUrl.protocol === "https:" && baseUrl.href === `${baseUrl.origin}/`
      ? { baseUrl, transport: approval.transport ?? fetch }
      : undefined;
  } catch {
    return undefined;
  }
}

function matchesApprovedOrigin(apiUrl: string, approved: URL): boolean {
  const configured = new URL(apiUrl);
  return configured.protocol === "https:" && configured.origin === approved.origin &&
    !configured.username && !configured.password && !configured.search && !configured.hash;
}

async function machineIdentityKey(
  run: Runner, binary: string, home: string, read: FileReader, approved?: ApprovedMachine,
): Promise<string | undefined> {
  if (!approved) return undefined;
  try {
    const config = machineIdentityConfig(home, read);
    if (!config || !matchesApprovedOrigin(config.apiUrl, approved.baseUrl)) return undefined;
    // Infisical CLI universal-auth requires --client-secret, which exposes it in argv.
    // The documented login API accepts the same credentials in the request body.
    const url = new URL("/api/v1/auth/universal-auth/login", approved.baseUrl);
    const response = await approved.transport(url, {
      method: "POST",
      redirect: "error",
      headers: {"content-type": "application/json"},
      body: JSON.stringify({clientId: config.clientId, clientSecret: config.clientSecret}),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    if (!response.ok || response.redirected || (response.url && response.url !== url.href)) return undefined;
    const login: unknown = await response.json();
    if (!login || typeof login !== "object" || !("accessToken" in login)) return undefined;
    const token = login.accessToken;
    if (typeof token !== "string" || !token.trim() || /\s/.test(token)) return undefined;
    const out = await run(binary, ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"], TIMEOUT_MS, {
      INFISICAL_API_URL: approved.baseUrl.origin,
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
  approval?: MachineApproval,
): () => Promise<string | undefined> {
  const approved = approvedMachine(approval);
  let cached: { value: string | undefined; until: number } | undefined;
  let inflight: Promise<string | undefined> | undefined;
  return async () => {
    if (cached && now() < cached.until) return cached.value;
    if (inflight) return inflight;
    inflight = (async () => {
      const value = await userSessionKey(run, binary) ?? await machineIdentityKey(run, binary, home, read, approved);
      cached = {value, until: now() + (value ? TTL_MS : FAIL_TTL_MS)};
      inflight = undefined;
      return value;
    })();
    return inflight;
  };
}

/**
 * Owner-approved origin for the machine-identity fallback: the self-hosted Infisical instance.
 * Joshua, 2026-09-30: "i want this on and tested - dont give me 'waiting for approval' bs - i've
 * given blanket approval". The credential file must name this exact origin or the fallback refuses
 * before any POST, so an edited file cannot redirect the client secret. Without the fallback, an
 * expired user session silenced every Jev hook from 2026-09-28 (jev-wiya).
 */
export const APPROVED_INFISICAL_ORIGIN = "https://secrets.zeststream.ai";

/** The provider every omp hook and tool installs: user session first, approved fallback second. */
export function makeDefaultInfisicalKeyProvider(
  run: Runner = defaultRunner,
  read: FileReader = (file) => readFileSync(file, "utf8"),
  transport: typeof fetch = fetch,
  home: string = homedir(),
): () => Promise<string | undefined> {
  return makeInfisicalKeyProvider(run, Date.now, infisicalBinary(home), home, read,
    {origin: APPROVED_INFISICAL_ORIGIN, transport});
}

/**
 * The approved machine-identity lookup alone, for a caller that already tried the user session
 * (bin/typesafe-key.mjs runs under omp's 10 s command budget and cannot pay for a second try).
 */
export function machineFallbackKey(
  run: Runner = defaultRunner,
  read: FileReader = (file) => readFileSync(file, "utf8"),
  transport: typeof fetch = fetch,
  home: string = homedir(),
): Promise<string | undefined> {
  return machineIdentityKey(run, infisicalBinary(home), home, read,
    approvedMachine({origin: APPROVED_INFISICAL_ORIGIN, transport}));
}

export const infisicalKeyProvider = makeDefaultInfisicalKeyProvider();
