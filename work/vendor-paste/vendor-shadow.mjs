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
 */
import { appendFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
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

export function isScoredPath(path) {
  if (typeof path !== "string" || !path) return false;
  if (SKIP_DIRS.some((d) => path === d || path.startsWith(d))) return false;
  if (path.split("/").some((s) => SKIP_SEGS.has(s))) return false;
  const low = path.toLowerCase();
  if (low.includes("fork") || low.includes("/sdk/") || low.includes("p2-compaction")) return false;
  return true;
}

/** Added-line blocks per file from a unified diff (added lines only, <=60). */
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
  return blocks.filter((b) => isScoredPath(b.file))
    .sort((a, b) => b.added.length - a.added.length)
    .slice(0, VENDOR_MAX_HUNKS);
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

export async function scoreCommit({ commit, diff, ask, log, count }) {
  const day = new Date().toISOString().slice(0, 10);
  const blocks = addedBlocks(diff);
  if (blocks.length === 0) {
    await log({ ts: new Date().toISOString(), day, commit, status: "skipped", reason: "no-scorable-hunks", model: VENDOR_MODEL });
    return { scored: 0, skipped: "no-scorable-hunks" };
  }
  if ((await count()) >= VENDOR_CAP_PER_DAY) {
    await log({ ts: new Date().toISOString(), day, commit, status: "fail_open", reason: "cap", model: VENDOR_MODEL });
    return { scored: 0, skipped: "cap" };
  }
  let scored = 0;
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
      await log({ ...base, status: "scored", noul: n, would_flag: decideVendor(n), latencyMs: Date.now() - started, ...(res.usage ? { usage: res.usage } : {}) });
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

export async function main(argv = process.argv.slice(2)) {
  useInfisicalKey();
  const ask = (o) => askJev(o);
  try {
    const commit = git(["rev-parse", "HEAD"]);
    const parent = (() => { try { return git(["rev-parse", "HEAD^"]); } catch { return null; } })();
    if (!parent) {
      console.error("VENDOR_SHADOW_SKIPPED reason=root-commit");
      return 0;
    }
    const diff = git(["show", "--format=", "--unified=0", "HEAD"]);
    await scoreCommit({ commit, diff, ask, log: appendRow, count: () => todayCount() });
  } catch (err) {
    console.error(`VENDOR_SHADOW_SKIPPED reason=git-failed err=${String(err).slice(0, 80)}`);
  }
  return 0;
}

if (process.argv[1]?.endsWith("vendor-shadow.mjs")) await main();
