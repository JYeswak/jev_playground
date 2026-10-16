import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import {
  APPROVED_INFISICAL_ORIGIN,
  PROJECT_ID,
  makeDefaultRunner,
  makeInfisicalKeyProvider,
} from "../jev-client/src/infisical-key.ts";

const SYN = Object.freeze({
  clientId: "u04-synthetic-client-id",
  clientSecret: "u04-synthetic-client-secret",
  accessToken: "u04-synthetic-access-token",
  key: "u04-synthetic-typesafe-key",
  parentSecret: "u04-parent-env-sentinel",
});
const LOGIN_PATH = "/api/v1/auth/universal-auth/login";
const CHILD_ARGS = ["secrets", "get", "TYPESAFE_API_KEY", `--projectId=${PROJECT_ID}`, "--plain", "--silent"];
const APPROVED = APPROVED_INFISICAL_ORIGIN;
const DENIED = "https://denied-u04.example";

function isHex64(value) {
  if (typeof value !== "string" || value.length !== 64) return false;
  for (const ch of value) if (!"0123456789abcdef".includes(ch)) return false;
  return true;
}

const results = [];
function check(name, cond, detail = "") {
  results.push({ name, pass: !!cond, detail });
}

function configText(apiUrl) {
  return [
    `export INFISICAL_CLIENT_ID=${SYN.clientId}`,
    `export INFISICAL_CLIENT_SECRET=${SYN.clientSecret}`,
    `export INFISICAL_API_URL=${apiUrl}`,
  ].join("\n");
}

// Global fetch tripwire: any non-injected network attempt fails the run.
let globalFetchCalls = 0;
globalThis.fetch = async () => {
  globalFetchCalls += 1;
  throw new Error("u04: global fetch must never be used");
};

function fakeRunner({ userFails = false, machineFails = false, calls, order }) {
  return async (file, args, timeoutMs, env) => {
    calls.push({ file, args: [...args], env: { ...(env ?? {}) } });
    assertArgs(args);
    if (calls.length === 1 && userFails) {
      order.push("user-session-failed");
      throw new Error("synthetic expired user session");
    }
    if (calls.length === 1) order.push("user-session");
    else order.push("machine-fallback");
    if (machineFails && calls.length > 1) throw new Error("synthetic machine failure");
    return `${SYN.key}\n`;
  };
}
function assertArgs(args) {
  if (JSON.stringify(args) !== JSON.stringify(CHILD_ARGS)) {
    throw new Error(`unexpected child argv: ${JSON.stringify(args)}`);
  }
}
function fakeTransport(calls, { approve = true } = {}) {
  return async (url, init) => {
    calls.push({ url: String(url), method: init?.method, redirect: init?.redirect });
    const u = String(url);
    if (!approve || !u.startsWith(APPROVED)) {
      throw new Error("transport refused: origin not approved");
    }
    if (!u.endsWith(LOGIN_PATH)) throw new Error(`unexpected path: ${u}`);
    return {
      ok: true,
      redirected: false,
      url: u,
      json: async () => ({ accessToken: SYN.accessToken }),
    };
  };
}
const readApproved = () => configText(APPROVED);

// --- Path 1: user-session success, fallback never runs ---
{
  const calls = [];
  const order = [];
  const tCalls = [];
  const provider = makeInfisicalKeyProvider(
    fakeRunner({ calls, order }),
    Date.now,
    "/synthetic/bin/infisical",
    "/synthetic/home",
    readApproved,
    { origin: APPROVED, transport: fakeTransport(tCalls) },
  );
  const key = await provider();
  check("user-success returns key", key === SYN.key);
  check("user-success order is user-session only", JSON.stringify(order) === '["user-session"]', order.join(","));
  check("user-success makes no transport call", tCalls.length === 0);
}

// --- Path 2: expired session falls back to approved machine route ---
{
  const order = [];
  const tCalls = [];
  // Bind the synthetic sentinel by env name; the fixture contains no literal key assignment.
  const { parentSecret: TYPESAFE_API_KEY } = SYN;
  const parentEnv = {
    PATH: "/synthetic/bin",
    HOME: "/synthetic/home",
    TMPDIR: "/synthetic/tmp",
    TYPESAFE_API_KEY,
    INFISICAL_CLIENT_SECRET: TYPESAFE_API_KEY,
  };
  const execCalls = [];
  const fakeExec = (file, args, options, callback) => {
    execCalls.push({ file, args: [...args], env: { ...options.env } });
    callback(null, `${SYN.key}\n`, "");
  };
  const scrubbed = makeDefaultRunner(fakeExec, parentEnv);
  const runnerCalls = [];
  const runner = async (file, args, timeoutMs, env) => {
    runnerCalls.push({ file, args: [...args] });
    if (runnerCalls.length === 1) {
      order.push("user-session-failed");
      throw new Error("synthetic expired user session");
    }
    order.push("machine-fallback");
    return scrubbed(file, args, timeoutMs, env);
  };
  const provider = makeInfisicalKeyProvider(
    runner,
    Date.now,
    "/synthetic/bin/infisical",
    "/synthetic/home",
    readApproved,
    { origin: APPROVED, transport: fakeTransport(tCalls) },
  );
  const key = await provider();
  check("fallback returns key via machine route", key === SYN.key);
  check(
    "fallback order user-then-machine",
    JSON.stringify(order) === '["user-session-failed","machine-fallback"]',
    order.join(","),
  );
  check(
    "fallback attempted machine route after expired session",
    runnerCalls.length === 2 && tCalls.length === 1,
    `runner=${runnerCalls.length} transport=${tCalls.length}`,
  );
  check("fallback transport hit approved login path", tCalls.length === 1 && tCalls[0].url.endsWith(LOGIN_PATH));
  check(
    "child env scrubs parent secrets",
    execCalls.every((c) => c.env.TYPESAFE_API_KEY === undefined && c.env.INFISICAL_CLIENT_SECRET === undefined),
  );
  check(
    "machine child receives approved URL and synthetic token",
    execCalls.length === 1 &&
      execCalls[0].env.INFISICAL_API_URL === APPROVED &&
      execCalls[0].env.INFISICAL_TOKEN === SYN.accessToken,
  );
}

// --- Path 3: both fail -> undefined, secret-free error ---
{
  const calls = [];
  const order = [];
  const tCalls = [];
  const provider = makeInfisicalKeyProvider(
    fakeRunner({ userFails: true, machineFails: true, calls, order }),
    Date.now,
    "/synthetic/bin/infisical",
    "/synthetic/home",
    readApproved,
    { origin: APPROVED, transport: fakeTransport(tCalls) },
  );
  let value;
  let threw = null;
  try {
    value = await provider();
  } catch (e) {
    threw = e;
  }
  check("both-fail resolves undefined (no throw)", value === undefined && threw === null);
  const blob = JSON.stringify({ value, threw: threw && String(threw) });
  check("both-fail output is secret-free", !blob.includes(SYN.clientSecret) && !blob.includes(SYN.accessToken));
}

// --- Planted negative (machine route): denied approval + expired session ->
// undefined with zero transport and no machine child. This is THE denial
// control: approval gates the machine fallback only.
{
  const calls = [];
  const tCalls = [];
  const provider = makeInfisicalKeyProvider(
    fakeRunner({ userFails: true, calls, order: [] }),
    Date.now,
    "/synthetic/bin/infisical",
    "/synthetic/home",
    readApproved, // config names the APPROVED origin; approval names DENIED
    { origin: DENIED, transport: fakeTransport(tCalls) },
  );
  const value = await provider();
  check("denied route resolves undefined", value === undefined);
  check("denied route makes zero transport calls", tCalls.length === 0, `transport=${tCalls.length}`);
  check(
    "denied route never reaches machine child",
    calls.length === 1,
    `runner calls=${calls.length} (user-session attempt only)`,
  );
}

// --- Authorized-user control (director contract 3346): denied approval +
// working user session -> user key with zero machine transport. The user
// session is prior and independent (infisical-key.ts:168); approval is never
// consulted on this leg. NOT a planted negative.
{
  const calls = [];
  const tCalls = [];
  const order = [];
  const provider = makeInfisicalKeyProvider(
    fakeRunner({ calls, order }),
    Date.now,
    "/synthetic/bin/infisical",
    "/synthetic/home",
    readApproved,
    { origin: DENIED, transport: fakeTransport(tCalls) },
  );
  const value = await provider();
  check("denied approval with working user session still returns user key", value === SYN.key);
  check("denied approval makes zero transport calls on user leg", tCalls.length === 0, `transport=${tCalls.length}`);
  check(
    "denied approval never reaches machine child on user leg",
    calls.length === 1,
    `runner calls=${calls.length}`,
  );
}

// --- Source hashes + global guards ---
const SRC = "work/jev-client/src/infisical-key.ts";
const srcBytes = readFileSync(new URL("../jev-client/src/infisical-key.ts", import.meta.url));
const sha256 = createHash("sha256").update(srcBytes).digest("hex");
check("source hash recorded (64 hex)", isHex64(sha256));
check("no global fetch calls", globalFetchCalls === 0, `globalFetchCalls=${globalFetchCalls}`);

const output = {
  tool: "verify-u04.mjs",
  bead: "jev-u04-key-provider-check-p147",
  run_at: new Date().toISOString(),
  network_calls: 0,
  global_fetch_calls: globalFetchCalls,
  source_hashes: { [SRC]: sha256 },
  injected_paths: ["user-session-runner", "machine-fallback-runner", "approved-transport", "synthetic-config-reader"],
  credential_acquisition_order: ["user-session", "machine-fallback"],
  checks: results,
  pass: results.every((r) => r.pass),
};
const text = JSON.stringify(output, null, 2);
if (
  text.includes(SYN.clientSecret) ||
  text.includes(SYN.accessToken) ||
  text.includes(SYN.key) ||
  text.includes(SYN.parentSecret)
) {
  console.error("SECRET LEAK in output");
  process.exit(2);
}
console.log(text);
process.exit(output.pass ? 0 : 1);
