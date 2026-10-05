/** 30hi post-commit shadow (bead jev-m94x): score HEAD's added hunks, never block.
 *
 * Class: advisory-observer (never denies; post-commit cannot block by git
 * construction) -> fail-open CORRECT BY DESIGN (rust-hook-pattern ladder).
 * Every path exits 0. Skips print a named reason; only an unwritable log is
 * silent. Rows carry hashes, never diff text.
 *
 * Key tradeoff, stated: the scorer resolves TYPESAFE_API_KEY through the
 * fleet-standard Infisical provider (spawns the infisical CLI, 15 s timeout,
 * 10-min TTL). That is a subprocess in the hook's path, against the
 * close-check shape; the alternative is a seam that never scores (post-commit
 * env almost never carries the key). Bounded: hunk cap 5/commit, 20 s per
 * call, daily row cap, fail_open row on any key/transport failure.
 * The optional local leg is disabled unless JEV_VENDOR_LOCAL_URL is set; when
 * enabled, one shared 2 s deadline covers all local scores for the commit.
 */
import { appendFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { execFileSync, spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { askJev } from "../../kit/src/client.ts";
import { useInfisicalKey } from "../../work/jev-client/src/use-infisical-key.ts";

export const VENDOR_MODEL = "jev-1.13.0";
export const VENDOR_CUT = 0.35;
const decideVendor = (noul) => Number.isFinite(noul) && noul >= VENDOR_CUT;
export const VENDOR_TIMEOUT_MS = 20000;
export const VENDOR_CAP_PER_DAY = 100;
export const VENDOR_MAX_HUNKS = 5;
export const VENDOR_QUESTION =
  "This pasted code is vendored third-party code, not code written for this repository. Judge only the code text, not any file path.";

const LOG_FILE = process.env.VENDOR_SHADOW_LOG ??
  join(homedir(), ".local", "state", "jev", "vendor-shadow.jsonl");

const SKIP_DIRS = ["upstream/", "docs-mirror/"];
const SKIP_SEGS = new Set(["node_modules", ".venv"]);
const SOURCE_EXTS = new Set(["ts", "js", "mjs", "cjs", "jsx", "tsx", "py", "rs", "go", "sh", "bash", "c", "h", "cpp", "hpp", "cc", "cxx", "java", "rb", "php", "swift", "kt", "kts", "cs", "scala", "hs", "ml", "mli", "ex", "exs", "erl", "clj", "cljs", "zig", "nim", "lua", "pl", "pm", "r", "jl", "dart", "vue", "svelte"]);
const LOCKFILES = new Set(["package-lock.json", "yarn.lock", "bun.lock", "bun.lockb", "cargo.lock", "gemfile.lock", "poetry.lock", "pdm.lock", "pnpm-lock.yaml", "podfile.lock", "composer.lock", "pipfile.lock", "packages.lock.json", "pubspec.lock", "go.sum"]);

export function isScoredPath(path) {
  return skipReason(path) === null;
}

/** null = score it; otherwise the skipped:<reason> suffix (no call made). */
export function skipReason(path) {
  if (typeof path !== "string" || !path) return "bad-path";
  if (SKIP_DIRS.some((d) => path === d || path.startsWith(d))) return "excluded-path";
  if (path.split("/").some((s) => SKIP_SEGS.has(s))) return "excluded-path";
  const low = path.toLowerCase();
  if (low.includes("fork") || low.includes("/sdk/") || low.includes("p2-compaction")) return "excluded-path";
  const base = path.split("/").pop() ?? path;
  if (base.startsWith(".")) return "dotfile";
  if (LOCKFILES.has(base.toLowerCase())) return "lockfile";
  const dot = base.lastIndexOf(".");
  if (dot < 0 || !SOURCE_EXTS.has(base.slice(dot + 1).toLowerCase())) return "non-source-extension";
  return null;
}

/** Added-line blocks per file (added lines only, <=60). Returns scored
 * candidates plus per-file skip reasons; skips make no calls. */
export function addedBlocks(diff) {
  const blocks = [];
  let file = null;
  let cur = [];
  const flush = () => {
    const added = cur.filter((l) => l.startsWith("+") && !l.startsWith("+++")).map((l) => l.slice(1));
    if (file && added.length >= 3) blocks.push({ file, added: added.slice(0, 60).join("\n") });
    cur = [];
  };
  for (const line of diff.split("\n")) {
    if (line.startsWith("+++ b/")) {
      flush();
      file = line.slice(6);
      cur = [];
    } else if (line.startsWith("@@")) {
      cur.push(line);
    } else if (file) {
      cur.push(line);
    }
  }
  flush();
  const scored = blocks.filter((b) => skipReason(b.file) === null)
    .sort((a, b) => b.added.length - a.added.length)
    .slice(0, VENDOR_MAX_HUNKS);
  const skipped = blocks.filter((b) => skipReason(b.file) !== null)
    .map((b) => ({ file: b.file, reason: skipReason(b.file) }));
  return { scored, skipped };
}

const sha = (s) => createHash("sha256").update(s, "utf8").digest("hex").slice(0, 12);

export async function todayCount(logFile = LOG_FILE) {
  try {
    const { readFile } = await import("node:fs/promises");
    const text = await readFile(logFile, "utf8");
    const day = new Date().toISOString().slice(0, 10);
    let n = 0;
    for (const line of text.split("\n")) if (line.includes(`"day":"${day}"`)) n += 1;
    return n;
  } catch {
    return 0;
  }
}

// jev-517o: a second, local verdict (Clef-flash + Platt map fitted on vendor dev, jev-576e) logged
// beside Jev's. Log only; NOT_RUN when the local server is absent; never blocks the commit.
export const LOCAL_URL = process.env.JEV_VENDOR_LOCAL_URL;
export const LOCAL_PLATT = { a: 1.239, b: 2.926 };
export const LOCAL_TIMEOUT_MS = 2000;
const LOCAL_GUARD_TIMEOUT_MS = 750;
const LOCAL_GUARD_SCRIPT = fileURLToPath(new URL("../../scripts/local-model-guard.sh", import.meta.url));

export function plattMap(p, { a, b } = LOCAL_PLATT) {
  const q = Math.min(Math.max(p, 1e-4), 1 - 1e-4);
  return 1 / (1 + Math.exp(-(a * Math.log(q / (1 - q)) + b)));
}

function runLocalModelGuard(timeoutMs = LOCAL_GUARD_TIMEOUT_MS) {
  return new Promise((resolve) => {
    let settled = false;
    let timer;
    const finish = (result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve(result);
    };
    let child;
    try {
      child = spawn("/bin/bash", [LOCAL_GUARD_SCRIPT, "--once"], { detached: true, stdio: "ignore" });
    } catch {
      finish({ available: false, reason: "guard-error" });
      return;
    }
    child.once("error", () => finish({ available: false, reason: "guard-error" }));
    child.once("close", (code) => finish(code === 0
      ? { available: true }
      : { available: false, reason: "guard-unavailable" }));
    timer = setTimeout(() => {
      if (child.pid !== undefined) {
        try {
          process.kill(-child.pid, "SIGKILL");
        } catch {}
      }
      finish({ available: false, reason: "guard-timeout" });
    }, timeoutMs);
  });
}

export async function askLocal(code, url = process.env.JEV_VENDOR_LOCAL_URL, fetchImpl = fetch, guard = runLocalModelGuard, deadlineAt = Date.now() + LOCAL_TIMEOUT_MS) {
  const configuredUrl = process.env.JEV_VENDOR_LOCAL_URL;
  if (!configuredUrl) return { local_status: "NOT_RUN", local_reason: "disabled" };
  const endpoint = url ?? configuredUrl;
  const remainingMs = deadlineAt - Date.now();
  if (remainingMs <= 0) return { local_status: "NOT_RUN", local_reason: "deadline" };
  const started = Date.now();
  try {
    const status = await guard(Math.min(LOCAL_GUARD_TIMEOUT_MS, remainingMs));
    if (!status?.available) return { local_status: "NOT_RUN", local_reason: status?.reason ?? "local-guard" };
    const timeoutMs = deadlineAt - Date.now();
    if (timeoutMs <= 0) return { local_status: "NOT_RUN", local_reason: "deadline" };
    const res = await fetchImpl(endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ model: "clef-flash", state: { code }, questions: { vendored: { type: "noul", instructions: VENDOR_QUESTION } } }),
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (!res.ok) return { local_status: "NOT_RUN", local_reason: `http-${res.status}` };
    const raw = (await res.json())?.answers?.vendored;
    const n = typeof raw === "number" ? raw : raw?.noul;
    if (typeof n !== "number" || !Number.isFinite(n)) return { local_status: "NOT_RUN", local_reason: "invalid-noul" };
    const p = plattMap(n);
    return { local_status: "scored", local_raw: n, local_noul: p, local_would_flag: p >= 0.5, local_ms: Date.now() - started };
  } catch (err) {
    return { local_status: "NOT_RUN", local_reason: String(err?.name ?? err).slice(0, 40) };
  }
}

export async function scoreCommit({ commit, diff, ask, log, count, local = (code, deadlineAt) => askLocal(code, undefined, fetch, runLocalModelGuard, deadlineAt) }) {
  const day = new Date().toISOString().slice(0, 10);
  const { scored: blocks, skipped } = addedBlocks(diff);
  for (const s of skipped) {
    await log({ ts: new Date().toISOString(), day, commit, file: s.file, status: "skipped", reason: s.reason, model: VENDOR_MODEL });
  }
  if (blocks.length === 0) {
    if (skipped.length === 0) {
      await log({ ts: new Date().toISOString(), day, commit, status: "skipped", reason: "no-scorable-hunks", model: VENDOR_MODEL });
    }
    return { scored: 0, skipped: skipped.length };
  }
  if ((await count()) >= VENDOR_CAP_PER_DAY) {
    await log({ ts: new Date().toISOString(), day, commit, status: "fail_open", reason: "cap", model: VENDOR_MODEL });
    return { scored: 0, skipped: skipped.length };
  }
  let scored = 0;
  let localDeadlineAt;
  for (const b of blocks) {
    const started = Date.now();
    const base = { ts: new Date().toISOString(), day, commit, file: b.file, hunk_sha: sha(b.added), model: VENDOR_MODEL };
    try {
      const res = await ask({ model: VENDOR_MODEL, state: { code: b.added.slice(0, 4000) }, questions: { vendored: VENDOR_QUESTION }, timeoutMs: VENDOR_TIMEOUT_MS });
      if (!res.ok) {
        await log({ ...base, status: "fail_open", reason: res.reason ?? "error", latencyMs: Date.now() - started });
        continue;
      }
      const n = res.scores?.vendored;
      if (typeof n !== "number" || !Number.isFinite(n)) {
        await log({ ...base, status: "fail_open", reason: "invalid-noul", latencyMs: Date.now() - started });
        continue;
      }
      localDeadlineAt ??= Date.now() + LOCAL_TIMEOUT_MS;
      const second = await local(b.added.slice(0, 4000), localDeadlineAt);
      await log({ ...base, status: "scored", noul: n, would_flag: decideVendor(n), latencyMs: Date.now() - started, ...(res.usage ? { usage: res.usage } : {}), ...second });
      scored += 1;
    } catch (err) {
      await log({ ...base, status: "fail_open", reason: `throw:${String(err).slice(0, 60)}`, latencyMs: Date.now() - started });
    }
  }
  return { scored, skipped: null };
}

async function appendRow(row) {
  try {
    await mkdir(join(homedir(), ".local", "state", "jev"), { recursive: true });
    await appendFile(LOG_FILE, JSON.stringify(row) + "\n", { mode: 0o600 });
  } catch {
    // Logging never disturbs the commit.
  }
}

function git(args) {
  return execFileSync("git", args, { encoding: "utf8", timeout: 15000 }).trim();
}

export async function main(argv = process.argv.slice(2), dependencies = {}) {
  const ask = dependencies.ask ?? ((o) => askJev(o));
  if (!dependencies.ask) useInfisicalKey();
  const gitCommand = dependencies.git ?? git;
  try {
    const commit = gitCommand(["rev-parse", "HEAD"]);
    const parent = (() => { try { return gitCommand(["rev-parse", "HEAD^"]); } catch { return null; } })();
    if (!parent) {
      console.error("VENDOR_SHADOW_SKIPPED reason=root-commit");
      return 0;
    }
    const diff = gitCommand(["show", "--format=", "--unified=0", "HEAD"]);
    await scoreCommit({
      commit,
      diff,
      ask,
      log: dependencies.log ?? appendRow,
      count: dependencies.count ?? (() => todayCount()),
      local: dependencies.local ?? ((code, deadlineAt) => askLocal(code, undefined, fetch, runLocalModelGuard, deadlineAt)),
    });
  } catch (err) {
    console.error(`VENDOR_SHADOW_SKIPPED reason=git-failed err=${String(err).slice(0, 80)}`);
  }
  return 0;
}

if (process.argv[1]?.endsWith("vendor-shadow.mjs")) await main();
