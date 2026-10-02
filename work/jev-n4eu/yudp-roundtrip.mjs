import { spawnSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const ROOT = "/Users/josh/Developer/jev";
const repo = mkdtempSync(join(tmpdir(), "yudp-roundtrip-"));
const cli = [process.execPath, join(ROOT, "kit/bin/jev.mjs")];
const run = (args) => spawnSync(process.execPath, [...cli.slice(1), ...args], { cwd: ROOT, encoding: "utf8" });

let r = run(["omp", "install", "--dir", repo, "--robot"]);
if (r.status !== 0) throw new Error("install failed: " + r.stdout + r.stderr);
const manifest = JSON.parse(readFileSync(join(repo, ".omp/jev-kit-manifest.json"), "utf8"));
const n = Object.keys(manifest.files).length;
r = run(["omp", "uninstall", "--dir", repo, "--robot"]);
if (r.status !== 0) throw new Error("dry run failed");
if (JSON.parse(r.stdout).status !== "DRY_RUN") throw new Error("not a dry run");
r = run(["omp", "uninstall", "--dir", repo, "--apply", "--robot"]);
if (r.status !== 0) throw new Error("apply failed: " + r.stdout + r.stderr);
const out = JSON.parse(r.stdout);
if (out.status !== "REMOVED") throw new Error("not removed");
const leftovers = [];
const walk = (d) => {
  for (const e of readdirSync(d, { withFileTypes: true })) {
    const p = join(d, e.name);
    if (e.isDirectory()) walk(p);
    else leftovers.push(p);
  }
};
try {
  walk(join(repo, ".omp"));
} catch {
  /* .omp gone entirely is also clean */
}
console.log(JSON.stringify({ manifestFiles: n, removed: out.files.length, leftovers }));
if (leftovers.length > 0) throw new Error("files behind: " + leftovers.join(","));
console.log("ROUND TRIP CLEAN");
