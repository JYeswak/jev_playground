import test from "node:test";
import assert from "node:assert/strict";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { randomBytes } from "node:crypto";
import { spawnSync } from "node:child_process";
import { createCaptureFetch, isolatedEnvironment, assertFixtureScope, runCapture } from "./capture.mjs";

const URL = "http://127.0.0.1:11300/v1/systemone";
const ROOT = resolve(import.meta.dirname, "../../var/agent-tmp");
const originalFetch = globalThis.fetch;
test.beforeEach(() => { globalThis.fetch = () => { throw new Error("offline suite forbids transport"); }; });
test.afterEach(() => { globalThis.fetch = originalFetch; });
async function owned() {
  await mkdir(ROOT, { recursive: true });
  const label = `3ck9-capture-test-${randomBytes(4).toString("hex")}`;
  const path = join(ROOT, `${label}.${process.pid}`);
  await mkdir(path, { mode: 0o700 });
  await writeFile(join(path, ".owner"), JSON.stringify({
    pid: process.pid, label, repo: resolve(ROOT, "../.."), created: new Date().toISOString(),
  }), { mode: 0o600 });
  return path;
}

// Shape/template: installed pi-coding-agent/src/tools/jfind/questions.ts:102-115
// and src/prompts/judge/find.json:5-6; public metadata, not a historical episode.
function request() {
  return JSON.stringify({
    state: {
      criteria: { true: "Explains native request metadata", false: "Unrelated metadata" },
      files: { f0: "native-find-contract.txt" },
      passages: { p00: ["f0", "Native find sends state and questions."], p01: ["f0", "A Noul answer is a probability."] },
      search: "native find request metadata",
    },
    model: "capture-only",
    questions: {
      p00: { type: "noul", instructions: "Could passage p00 implement a requested step of search? Apply criteria." },
      p01: { type: "noul", instructions: "Could passage p01 implement a requested step of search? Apply criteria." },
    },
  });
}

test("capture preserves full raw request, all native keys, fixed Noul values, and private modes", async () => {
  const dir = await owned();
  const capture = createCaptureFetch({ allowedUrl: URL, sidecarDir: dir });
  const body = request();
  const response = await capture.fetch(URL, { method: "POST", body });
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("x-jev-capture-mode"), "CAPTURE_ONLY");
  const result = await response.json();
  assert.deepEqual(Object.keys(result.answers).sort(), ["p00", "p01"]);
  for (const answer of Object.values(result.answers)) {
    assert.equal(answer.type, "noul");
    assert.ok(Number.isFinite(answer.noul) && answer.noul >= 0 && answer.noul <= 1);
  }
  assert.deepEqual(result.usage, { input_tokens: 0, output_tokens: 0 });
  assert.equal(result.model, "capture-only");
  assert.equal(await readFile(join(dir, "000001.request.json"), "utf8"), body);
  assert.equal((await stat(join(dir, "000001.request.json"))).mode & 0o777, 0o600);
  assert.equal((await stat(dir)).mode & 0o777, 0o700);
  assert.equal(capture.summary().accepted, 1);
  assert.equal(capture.summary().bytes, Buffer.byteLength(body));
});

test("planted nonlocal URL is rejected before body access, recording, or original transport", async () => {
  const dir = await owned();
  const previous = globalThis.fetch;
  let transports = 0;
  globalThis.fetch = () => { transports++; throw new Error("must never reach transport"); };
  try {
    const capture = createCaptureFetch({ allowedUrl: URL, sidecarDir: dir });
    const options = { method: "POST", get body() { throw new Error("body was accessed before URL rejection"); } };
    await assert.rejects(capture.fetch("https://api.typesafe.ai/v1/systemone", options), { code: "REFUSED_URL" });
    assert.equal(transports, 0);
    assert.equal(capture.summary().accepted, 0);
    assert.equal(capture.summary().rejected, 1);
    assert.deepEqual((await readdir(dir)).sort(), [".owner"]);
  } finally { globalThis.fetch = previous; }
});

test("local lookalikes and alternate ports/paths do not widen the exact allowlist", async () => {
  const capture = createCaptureFetch({ allowedUrl: URL, sidecarDir: await owned() });
  for (const url of ["http://localhost:11300/v1/systemone", "http://127.0.0.1:11301/v1/systemone", `${URL}?redirect=1`, `${URL}/`, "http://127.0.0.1.example.com:11300/v1/systemone"]) {
    await assert.rejects(capture.fetch(url, { method: "POST", body: request() }), { code: "REFUSED_URL" });
  }
  assert.equal(capture.summary().accepted, 0);
  assert.equal(capture.summary().rejected, 5);
  assert.throws(() => createCaptureFetch({ allowedUrl: "https://api.typesafe.ai/v1/systemone", sidecarDir: "/unused" }), { code: "INVALID_LOCAL_URL" });
});

test("unsupported model/questions and malformed requests produce no saved payload", async () => {
  const dir = await owned();
  const capture = createCaptureFetch({ allowedUrl: URL, sidecarDir: dir });
  const body = JSON.parse(request());
  for (const invalid of ["{", JSON.stringify({ ...body, model: "jev-latest" }), JSON.stringify({ ...body, questions: {} }), JSON.stringify({ ...body, questions: { q: { type: "choice", instructions: "pick" } } }), JSON.stringify({ ...body, state: null })]) {
    await assert.rejects(capture.fetch(URL, { method: "POST", body: invalid }), { code: "INVALID_NATIVE_REQUEST" });
  }
  await assert.rejects(capture.fetch(URL, { method: "GET", body: request() }), { code: "INVALID_NATIVE_REQUEST" });
  assert.deepEqual((await readdir(dir)).sort(), [".owner"]);
});

test("capture limits fail closed, without recording the refused request", async () => {
  const dir = await owned();
  const capture = createCaptureFetch({ allowedUrl: URL, sidecarDir: dir, maxRequests: 1, maxBodyBytes: 4096, maxTotalBytes: 4096 });
  await capture.fetch(URL, { method: "POST", body: request() });
  await assert.rejects(capture.fetch(URL, { method: "POST", body: request() }), { code: "CAPTURE_LIMIT" });
  assert.equal((await readdir(dir)).filter(name => name.endsWith(".request.json")).length, 1);
  const small = createCaptureFetch({ allowedUrl: URL, sidecarDir: await owned(), maxBodyBytes: 8 });
  await assert.rejects(small.fetch(URL, { method: "POST", body: request() }), { code: "CAPTURE_LIMIT" });
});

test("child environment excludes planted credentials, profiles, proxies and preload settings", () => {
  const keys = ["TYPESAFE_API_KEY", "HTTP_PROXY", "OMP_PROFILE", "PI_PROFILE", "NODE_OPTIONS", "BUN_OPTIONS"];
  const original = keys.map(key => [key, process.env[key]]);
  try {
    for (const key of keys) process.env[key] = "CAPTURE_ENV_PLANT";
    const root = "/owned/capture";
    const child = spawnSync(process.execPath, ["-e", `console.log(JSON.stringify({
      apiKey: Object.hasOwn(process.env, 'TYPESAFE_API_KEY'),
      proxy: Object.hasOwn(process.env, 'HTTP_PROXY'),
      nodePreload: Object.hasOwn(process.env, 'NODE_OPTIONS'),
      bunPreload: Object.hasOwn(process.env, 'BUN_OPTIONS'),
      profiles: [process.env.OMP_PROFILE, process.env.PI_PROFILE],
      home: process.env.HOME, agent: process.env.PI_CODING_AGENT_DIR,
      overlay: process.env.PI_CONFIG_FILES, cache: process.env.OMP_JUDGMENT_CACHE_DB
    }))`], { env: isolatedEnvironment(root), encoding: "utf8" });
    assert.equal(child.status, 0, child.stderr);
    const observed = JSON.parse(child.stdout);
    assert.deepEqual([observed.apiKey, observed.proxy, observed.nodePreload, observed.bunPreload], [false, false, false, false]);
    assert.deepEqual(observed.profiles, ["", ""]);
    assert.equal(observed.home, `${root}/home`);
    assert.equal(observed.agent, `${root}/agent`);
    assert.equal(observed.overlay, `${root}/capture-overlay.yml`);
    assert.equal(observed.cache, `${root}/cache/judgment.db`);
  } finally {
    for (const [key, value] of original) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
});

test("scope preflight accepts only owned metadata fixture and refuses ambient configuration", async () => {
  const root = await owned();
  const fixture = join(root, "fixture");
  await mkdir(fixture);
  await mkdir(join(fixture, ".git"));
  await writeFile(join(fixture, ".git", "HEAD"), "ref: refs/heads/main\n");
  await mkdir(join(fixture, ".omp"));
  await writeFile(join(fixture, "native-find-contract.txt"), "Native find sends state and questions.\n");
  await writeFile(join(fixture, "replay-corpus-metadata.txt"), "Saved replay rows are not a find corpus.\n");
  await assertFixtureScope(root);
  await writeFile(join(fixture, ".omp", "config.yml"), "extensions: [outside]\n");
  await assert.rejects(assertFixtureScope(root), { code: "UNSAFE_SCOPE" });
  await assert.rejects(assertFixtureScope(root, resolve(import.meta.dirname, "../..")), { code: "UNSAFE_SCOPE" });
});

test("runner refuses a relative binary before starting native capture", async () => {
  await assert.rejects(runCapture({ binary: "omp" }), { code: "INVALID_BINARY" });
});
