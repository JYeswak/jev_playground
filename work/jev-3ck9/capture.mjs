import { createHash, randomBytes } from "node:crypto";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { createReadStream, lstatSync, openSync, closeSync, writeFileSync } from "node:fs";
import { access, lstat, mkdir, readFile, readdir, realpath, writeFile } from "node:fs/promises";
import { createServer, createConnection } from "node:net";
import { dirname, isAbsolute, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const REPO = resolve(import.meta.dirname, "../..");
const MODE = "CAPTURE_ONLY";
const MODEL = "capture-only";
const PROVIDER = "native-capture";
const FIXTURE_FILES = ["native-find-contract.txt", "replay-corpus-metadata.txt"];
const sha256 = value => createHash("sha256").update(value).digest("hex");
const fail = code => Object.assign(new Error(code), { code });
const record = value => value !== null && typeof value === "object" && !Array.isArray(value);
const digits = value => typeof value === "string" && value.length > 0 && Array.from(value).every(char => char >= "0" && char <= "9");

function localUrl(value) {
  let url;
  try { url = new URL(value); } catch { throw fail("INVALID_LOCAL_URL"); }
  if (url.protocol !== "http:" || !["127.0.0.1", "[::1]"].includes(url.hostname) || !url.port || url.username || url.password || url.search || url.hash || url.pathname !== "/v1/systemone" || url.href !== value) throw fail("INVALID_LOCAL_URL");
  return url;
}

// Native System One wire: pi-ai/src/judgment/systemone.ts:21-42;
// find only emits Noul questions (pi-coding-agent/src/tools/jfind/questions.ts).
export function createCaptureFetch({ allowedUrl, sidecarDir, maxRequests = 128, maxBodyBytes = 524288, maxTotalBytes = 8388608 }) {
  localUrl(allowedUrl);
  const dir = lstatSync(sidecarDir);
  if (!dir.isDirectory() || dir.isSymbolicLink() || (dir.mode & 0o777) !== 0o700 || dir.uid !== process.getuid()) throw fail("UNSAFE_SIDECAR");
  if (![maxRequests, maxBodyBytes, maxTotalBytes].every(n => Number.isSafeInteger(n) && n > 0)) throw fail("CAPTURE_LIMIT");
  let accepted = 0;
  let rejected = 0;
  let bytes = 0;
  return {
    summary: () => ({ mode: MODE, accepted, rejected, bytes }),
    fetch: async (input, init) => {
      try {
        const target = typeof input === "string" ? input : input instanceof URL ? input.href : input?.url;
        if (target !== allowedUrl) throw fail("REFUSED_URL");
        if (init?.method !== "POST" || typeof init.body !== "string") throw fail("INVALID_NATIVE_REQUEST");
        const body = init.body;
        const size = Buffer.byteLength(body);
        if (size > maxBodyBytes || accepted >= maxRequests || bytes + size > maxTotalBytes) throw fail("CAPTURE_LIMIT");
        let request;
        try { request = JSON.parse(body); } catch { throw fail("INVALID_NATIVE_REQUEST"); }
        if (!record(request) || request.model !== MODEL || !(typeof request.state === "string" || (request.state !== null && typeof request.state === "object")) || !record(request.questions)) throw fail("INVALID_NATIVE_REQUEST");
        const entries = Object.entries(request.questions);
        if (!entries.length || entries.some(([, q]) => !record(q) || q.type !== "noul" || typeof q.instructions !== "string")) throw fail("INVALID_NATIVE_REQUEST");
        const answers = Object.fromEntries(entries.map(([key]) => [key, { type: "noul", noul: 0.9 }]));
        const path = join(sidecarDir, `${String(accepted + 1).padStart(6, "0")}.request.json`);
        const fd = openSync(path, "wx", 0o600);
        try { writeFileSync(fd, body); } finally { closeSync(fd); }
        accepted++;
        bytes += size;
        return new Response(JSON.stringify({ mode: MODE, model: MODEL, answers, usage: { input_tokens: 0, output_tokens: 0 } }), {
          status: 200, headers: { "content-type": "application/json", "x-jev-capture-mode": MODE },
        });
      } catch (error) { rejected++; throw error; }
    },
  };
}

export function isolatedEnvironment(root) {
  return {
    HOME: join(root, "home"), PATH: "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
    TMPDIR: join(root, "tmp"), OMP_PROFILE: "", PI_PROFILE: "",
    PI_CODING_AGENT_DIR: join(root, "agent"), PI_CONFIG_FILES: join(root, "capture-overlay.yml"),
    OMP_JUDGMENT_CACHE_DB: join(root, "cache", "judgment.db"),
    XDG_CONFIG_HOME: join(root, "xdg-config"), XDG_STATE_HOME: join(root, "xdg-state"),
    XDG_CACHE_HOME: join(root, "cache"), XDG_DATA_HOME: join(root, "xdg-data"),
  };
}

export function sandboxProfile(root) {
  if (!isAbsolute(root) || Array.from(root).some(char => char.charCodeAt(0) < 32)) throw fail("UNSAFE_SCOPE");
  const rules = ["(version 1)", "(allow default)", "(deny network*)",
    `(deny file-write* (require-not (require-any (subpath ${JSON.stringify(root)}) (literal "/dev/null"))))`];
  // A clean git root bounds project discovery; these rules additionally prevent
  // ancestor configuration reads if a different executable walks past that root.
  for (let dir = dirname(root); ; dir = dirname(dir)) {
    for (const name of [".omp", ".pi", ".claude", ".agents", ".codex", ".gemini", ".opencode", ".env"]) rules.push(`(deny file-read* (subpath ${JSON.stringify(join(dir, name))}))`);
    if (dirname(dir) === dir) break;
  }
  return rules.join("\n");
}

export async function assertFixtureScope(root, scope = join(root, "fixture")) {
  const owner = await lstat(root);
  if (resolve(scope) !== join(resolve(root), "fixture") || await realpath(scope) !== scope || !owner.isDirectory() || owner.isSymbolicLink() || owner.uid !== process.getuid() || (owner.mode & 0o777) !== 0o700) throw fail("UNSAFE_SCOPE");
  const entries = (await readdir(scope)).sort();
  if (JSON.stringify(entries) !== JSON.stringify([".git", ".omp", ...FIXTURE_FILES].sort())) throw fail("UNSAFE_SCOPE");
  for (const name of entries) {
    const info = await lstat(join(scope, name));
    if (info.isSymbolicLink() || info.uid !== process.getuid() || (name.startsWith(".") ? !info.isDirectory() : !info.isFile() || info.nlink !== 1)) throw fail("UNSAFE_SCOPE");
  }
  if ((await readdir(join(scope, ".omp"))).length || await readFile(join(scope, ".git", "HEAD"), "utf8") !== "ref: refs/heads/main\n") throw fail("UNSAFE_SCOPE");
}

async function bounded(command, args, { cwd, env, timeoutMs, signal, maxBytes = 2097152 }) {
  if (signal?.aborted) throw fail("INTERRUPTED");
  return new Promise(resolveRun => {
    const child = spawn(command, args, { cwd, env, stdio: ["ignore", "pipe", "pipe"], detached: true });
    const output = [[], []];
    const sizes = [0, 0];
    let failure;
    let spawnError;
    let escalation;
    const kill = sig => { if (child.pid) { try { process.kill(-child.pid, sig); } catch {} } };
    const stop = code => {
      if (failure) return;
      failure = code;
      kill("SIGTERM");
      escalation = setTimeout(() => kill("SIGKILL"), 250);
    };
    const timer = setTimeout(() => stop("DEADLINE"), timeoutMs);
    const abort = () => stop("INTERRUPTED");
    signal?.addEventListener("abort", abort, { once: true });
    [child.stdout, child.stderr].forEach((stream, index) => stream.on("data", data => {
      sizes[index] += data.length;
      if (sizes[index] > maxBytes) stop("OUTPUT_LIMIT");
      else output[index].push(data);
    }));
    child.once("error", error => { failure = "SPAWN_FAILED"; spawnError = error.code; });
    child.once("close", (code, exitSignal) => {
      clearTimeout(timer);
      clearTimeout(escalation);
      signal?.removeEventListener("abort", abort);
      resolveRun({
        code, signal: exitSignal, failure: failure ?? null, spawnError: spawnError ?? null,
        stdout: Buffer.concat(output[0]), stderr: Buffer.concat(output[1]),
      });
    });
  });
}

async function containmentProbe(run, root, outsidePath) {
  let accepts = 0;
  const sockets = new Set();
  const server = createServer(socket => { accepts++; sockets.add(socket); socket.once("close", () => sockets.delete(socket)); socket.end(); });
  let baseline;
  try {
    server.listen(0, "127.0.0.1");
    await once(server, "listening");
    const port = server.address().port;
    baseline = createConnection({ host: "127.0.0.1", port });
    baseline.setTimeout(1000, () => baseline.destroy(fail("SANDBOX_UNPROVEN")));
    await once(baseline, "close");
    if (accepts !== 1) throw fail("SANDBOX_UNPROVEN");
    await writeFile(outsidePath, "owner-control", { mode: 0o600, flag: "wx" });
    const code = `const fs=require('node:fs'),net=require('node:net');
      let outsideDenied=false; try{const fd=fs.openSync(process.argv[3],'r+');fs.writeSync(fd,'changed');fs.closeSync(fd)}catch(e){outsideDenied=['EPERM','EACCES'].includes(e.code)}
      fs.writeFileSync(process.argv[2], 'owned-write', {mode:384});
      const s=net.createConnection({host:'127.0.0.1',port:Number(process.argv[1])});
      s.setTimeout(1000,()=>{s.destroy();process.exit(2)});
      s.on('connect',()=>{s.destroy();process.exit(3)});
      s.on('error',e=>{const networkDenied=['EPERM','EACCES'].includes(e.code);console.log(JSON.stringify({networkDenied,outsideDenied}));process.exit(networkDenied&&outsideDenied?0:4)});`;
    const probe = await run(process.execPath, ["-e", code, String(port), join(root, "containment-write.txt"), outsidePath], 5000);
    let result;
    try { result = JSON.parse(probe.stdout.toString()); } catch { throw fail("SANDBOX_UNPROVEN"); }
    if (probe.code !== 0 || result.networkDenied !== true || result.outsideDenied !== true || accepts !== 1
      || await readFile(join(root, "containment-write.txt"), "utf8") !== "owned-write"
      || await readFile(outsidePath, "utf8") !== "owner-control") throw fail("SANDBOX_UNPROVEN");
    return { healthyLoopbackConnections: 1, sandboxLoopbackConnections: accepts - 1, networkDenied: true, outsideWritesDenied: true };
  } finally {
    baseline?.destroy();
    for (const socket of sockets) socket.destroy();
    await new Promise(resolveClose => server.close(resolveClose));
  }
}

export async function runCapture({ binary, allowedUrl = "http://127.0.0.1:11300/v1/systemone", timeoutMs = 45000, expectedVersion = "18.11.0" } = {}) {
  if (typeof binary !== "string" || !isAbsolute(binary)) throw fail("INVALID_BINARY");
  localUrl(allowedUrl);
  if (process.platform !== "darwin") throw fail("UNSUPPORTED_SANDBOX");
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 5000 || timeoutMs > 60000 || typeof expectedVersion !== "string" || expectedVersion.split(".").length !== 3 || !expectedVersion.split(".").every(digits)) throw fail("INVALID_OPTIONS");
  const executable = await realpath(binary);
  await access(executable, 1);
  await access("/usr/bin/sandbox-exec", 1);
  const parent = join(REPO, "var", "agent-tmp");
  await mkdir(parent, { recursive: true });
  const label = `3ck9-native-capture-${randomBytes(4).toString("hex")}`;
  const directory = join(parent, `${label}.${process.pid}`);
  await mkdir(directory, { mode: 0o700 });
  const ownerRoot = await realpath(directory);
  const root = join(ownerRoot, "capture");
  await mkdir(root, { mode: 0o700 });
  if (((await lstat(root)).mode & 0o777) !== 0o700) throw fail("UNSAFE_SCOPE");
  const controller = new AbortController();
  const interrupt = () => controller.abort();
  process.once("SIGINT", interrupt);
  process.once("SIGTERM", interrupt);
  const deadline = Date.now() + timeoutMs;
  const env = isolatedEnvironment(root);
  const fixture = join(root, "fixture");
  let commandIndex = 0;
  const run = async (command, args, cap) => {
    const remaining = Math.min(cap, deadline - Date.now());
    if (remaining <= 0) throw fail("DEADLINE");
    const result = await bounded("/usr/bin/sandbox-exec", ["-p", sandboxProfile(root), command, ...args], { cwd: fixture, env, timeoutMs: remaining, signal: controller.signal });
    const prefix = `command-${++commandIndex}`;
    await save(`${prefix}.stdout`, result.stdout);
    await save(`${prefix}.stderr`, result.stderr);
    await save(`${prefix}.json`, JSON.stringify({
      command, argumentSha256: sha256(JSON.stringify(args)), code: result.code,
      signal: result.signal, failure: result.failure, spawnError: result.spawnError,
    }));
    if (result.failure) throw fail(result.failure);
    return result;
  };
  const save = (name, data) => writeFile(join(root, name), data, { mode: 0o600, flag: "wx" });
  try {
    await writeFile(join(ownerRoot, ".owner"), JSON.stringify({
      pid: process.pid, label, repo: REPO, created: new Date().toISOString(), mode: MODE,
    }) + "\n", { mode: 0o600, flag: "wx" });
    for (const dir of ["home", "agent", "tmp", "cache", "xdg-config", "xdg-state", "xdg-data", "requests", "fixture", "fixture/.omp"]) await mkdir(join(root, dir), { mode: 0o700 });
    const boundary = await containmentProbe(run, root, join(ownerRoot, "outside-write-control.txt"));
    const developer = await run("/usr/bin/xcode-select", ["--print-path"], 5000);
    const developerDirectory = developer.stdout.toString().trim();
    if (developer.code !== 0 || !isAbsolute(developerDirectory)) throw fail("UNSUPPORTED_NATIVE_GIT");
    const gitBinary = await realpath(join(developerDirectory, "usr", "bin", "git"));
    await access(gitBinary, 1);
    env.PATH = `${dirname(gitBinary)}:${env.PATH}`;
    const git = await run(gitBinary, ["-c", "core.hooksPath=/dev/null", "init", "--template=", "--initial-branch=main", fixture], 5000);
    if (git.code !== 0) throw fail("UNSAFE_SCOPE");
    // New public metadata fixtures, never copied source or historical payloads.
    await writeFile(join(fixture, FIXTURE_FILES[0]), "Native semantic find sends a structured state and a questions map. Filename, sketch, and passage phases ask Noul questions. The System One response preserves question keys and supplies a Noul probability.\n", { mode: 0o600, flag: "wx" });
    await writeFile(join(fixture, FIXTURE_FILES[1]), "Saved native judge replay rows describe smart-stop and auto-thinking decisions. They are not a historical find corpus. Agreement with a hosted model is not opened-next accuracy.\n", { mode: 0o600, flag: "wx" });
    await assertFixtureScope(root);
    const models = { providers: { [PROVIDER]: { api: "typesafe", baseUrl: allowedUrl.slice(0, -"/v1/systemone".length), auth: "none", models: [{ id: MODEL, name: MODE, kind: "judge", contextWindow: 32768, maxTokens: 1024, input: ["text"], reasoning: false, cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 } }] } } };
    await writeFile(join(root, "agent", "models.yml"), JSON.stringify(models), { mode: 0o600, flag: "wx" });
    const extensionPath = join(root, "capture-extension.mjs");
    const readyPath = join(root, "capture-ready.json");
    const extension = `import {createCaptureFetch} from ${JSON.stringify(import.meta.url)};\nimport {writeFileSync} from 'node:fs';\nexport default function(){\nconst c=createCaptureFetch(${JSON.stringify({ allowedUrl, sidecarDir: join(root, "requests") })});\nglobalThis.fetch=c.fetch;\nwriteFileSync(${JSON.stringify(readyPath)},JSON.stringify({mode:'CAPTURE_ONLY',agentDir:process.env.PI_CODING_AGENT_DIR,home:process.env.HOME,profile:process.env.OMP_PROFILE||process.env.PI_PROFILE||''}),{mode:384,flag:'wx'});\n}\n`;
    await save("capture-extension.mjs", extension);
    // Standalone find has no --no-extensions flag. Empty fixture config roots
    // plus the private explicit extension replace neither flags nor shared state.
    await save("capture-overlay.yml", JSON.stringify({ modelRoles: { judge: `${PROVIDER}/${MODEL}` }, retry: { fallbackChains: { judge: [] } }, extensions: [extensionPath] }));
    const version = await run(executable, ["--version"], 5000);
    if (version.code !== 0 || version.stdout.toString().trim() !== `omp/${expectedVersion}`) throw fail("UNSUPPORTED_EXECUTABLE");
    const native = await run(executable, ["find", "native find request state questions metadata", fixture, "--json", "-q"], 30000);
    await save("native-result.json", native.stdout);
    await save("native-stderr.txt", native.stderr);
    if (native.code !== 0) throw fail("NATIVE_CAPTURE_FAILED");
    let ready;
    let result;
    try { ready = JSON.parse(await readFile(readyPath, "utf8")); result = JSON.parse(native.stdout); } catch { throw fail("NATIVE_CAPTURE_UNPROVEN"); }
    if (ready.mode !== MODE || ready.agentDir !== env.PI_CODING_AGENT_DIR || ready.home !== env.HOME || ready.profile !== "" || result.root !== fixture || !Array.isArray(result.hits) || !result.hits.length || !record(result.stats) || result.stats.errors !== 0) throw fail("NATIVE_CAPTURE_UNPROVEN");
    const names = (await readdir(join(root, "requests"))).filter(name => name.length === 19 && name.endsWith(".request.json") && digits(name.slice(0, 6))).sort();
    if (!names.length || result.stats.requests !== names.length) throw fail("NATIVE_CAPTURE_UNPROVEN");
    const requests = [];
    for (const name of names) {
      const data = await readFile(join(root, "requests", name));
      const body = JSON.parse(data);
      if (body.model !== MODEL || (await lstat(join(root, "requests", name))).mode & 0o077) throw fail("NATIVE_CAPTURE_UNPROVEN");
      requests.push({ sha256: sha256(data), bytes: data.length, questions: Object.keys(body.questions).length });
    }
    const executableHash = createHash("sha256");
    for await (const chunk of createReadStream(executable)) executableHash.update(chunk);
    const receipt = { mode: MODE, purpose: "native capture plumbing only", historicalEpisodes: 0, parityClaim: false, adaptiveCascade: true, sourceExecutableEquivalence: "UNVERIFIED: inspected package source 18.10.3; executable version checked separately", executableVersion: expectedVersion, executableSha256: executableHash.digest("hex"), artifactDirectory: root, boundary, requestCount: requests.length, requests, returnedHitCount: result.hits.length, resultSha256: sha256(native.stdout), stderrSha256: sha256(native.stderr) };
    await save("receipt.json", JSON.stringify(receipt, null, 2) + "\n");
    return receipt;
  } catch (error) {
    error.artifactDirectory = root;
    throw error;
  } finally {
    process.removeListener("SIGINT", interrupt);
    process.removeListener("SIGTERM", interrupt);
  }
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  if (process.argv.length === 3 && process.argv[2] === "--help") {
    console.log("Usage: node capture.mjs --omp ABSOLUTE_BINARY [--expected-version 18.11.0] [--timeout-ms 45000]");
    console.log("Capture-only native plumbing on a fresh owned metadata fixture; never historical parity or model scoring.");
    console.log("macOS containment denies networking and ordinary writes outside the owned capture directory; /dev/null is allowed for process I/O.");
    console.log("Raw requests stay in private 0600 sidecars. No shared config, original project scope, or live provider transport.");
    process.exit(0);
  }
  const options = {};
  let invalid = false;
  for (let i = 2; i < process.argv.length; i += 2) {
    const key = { "--omp": "binary", "--url": "allowedUrl", "--timeout-ms": "timeoutMs", "--expected-version": "expectedVersion" }[process.argv[i]];
    if (!key || process.argv[i + 1] === undefined || Object.hasOwn(options, key)) { invalid = true; break; }
    options[key] = key === "timeoutMs" ? Number(process.argv[i + 1]) : process.argv[i + 1];
  }
  try {
    if (invalid) throw fail("INVALID_OPTIONS");
    console.log(JSON.stringify(await runCapture(options)));
  } catch (error) {
    const code = typeof error.code === "string" && error.code.length < 64 && Array.from(error.code).every(char => (char >= "A" && char <= "Z") || char === "_") ? error.code : "CAPTURE_FAILED";
    console.error(JSON.stringify({ mode: MODE, ok: false, code, ...(error.artifactDirectory ? { artifactDirectory: error.artifactDirectory } : {}), parityClaim: false }));
    process.exitCode = 1;
  }
}
