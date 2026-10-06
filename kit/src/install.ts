import { createHash, randomUUID } from "node:crypto";
import { access, lstat, mkdir, readFile, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join, relative, resolve } from "node:path";
import { isProtectedMutationPath, mutate } from "./doctor/mutate.js";

export const INSTALL_FILES = {
  "tools/jev-rerank.ts": "omp/tools/jev-rerank.ts",
  "tools/jev-claim-check.ts": "omp/tools/jev-claim-check.ts",
  "tools/jev-screen.ts": "omp/tools/jev-screen.ts",
  "tools/jev-flag.ts": "omp/tools/jev-flag.ts",
  "tools/jev-gate.ts": "omp/tools/jev-gate.ts",
  "hooks/post/jev-gate-observe.ts": "omp/hooks/post/jev-gate-observe.ts",
  "extensions/jev-rerank.ts": "omp/extensions/jev-rerank.ts",
  "extensions/jev-claim-check.ts": "omp/extensions/jev-claim-check.ts",
  "extensions/jev-screen.ts": "omp/extensions/jev-screen.ts",
  "extensions/jev-flag.ts": "omp/extensions/jev-flag.ts",
  "extensions/jev-classify.ts": "omp/extensions/jev-classify.ts",
  "jev-kit/client.ts": "jev-kit/client.ts",
  "jev-kit/validate.ts": "jev-kit/validate.ts",
  "jev-kit/preflight.ts": "jev-kit/preflight.ts",
  "jev-kit/fake.ts": "jev-kit/fake.ts",
  "jev-kit/use-infisical-key.ts": "jev-kit/use-infisical-key.ts",
  "jev-kit/infisical-key.ts": "jev-kit/infisical-key.ts",
  "jev-kit/questions.mjs": "jev-kit/questions.mjs",
  "jev-kit/coding-agent-seat.mjs": "omp/jev-kit/coding-agent-seat.mjs",
  "jev-kit/nev-rerank/rank.ts": "jev-kit/nev-rerank/rank.ts",
  "jev-kit/nev-rerank/live.ts": "jev-kit/nev-rerank/live.ts",
  "jev-kit/nev-injection/live-flag.ts": "jev-kit/nev-injection/live-flag.ts",
  "tools/jev-classify.ts": "omp/tools/jev-classify.ts",
  "jev-kit/rerank.ts": "../src/rerank.ts",
  "jev-kit/verify.ts": "../src/verify.ts",
  "jev-kit/classify.ts": "../src/classify.ts",
  "jev-kit/gate.ts": "../src/gate.ts",
};

const MANIFEST_PATH = ".omp/jev-kit-manifest.json";
type Manifest = { version: 1; files: Record<string, string> };
type ManifestSnapshot = { manifest: Manifest; bytes: Buffer; mode: number };
export type InstallResult = { status: "READY" | "DRY_RUN"; repo: string; files: string[]; extensionActivation: "MANUAL_REQUIRED" };
async function exists(path: string): Promise<boolean> { try { await access(path); return true; } catch { return false; } }
function sha256(content: string | Uint8Array): string {
  const hash = createHash("sha256");
  return (typeof content === "string" ? hash.update(content, "utf8") : hash.update(content)).digest("hex");
}
async function readManifestSnapshot(path: string): Promise<ManifestSnapshot | undefined> {
  let metadata;
  try { metadata = await lstat(path); }
  catch (cause) {
    if (cause && typeof cause === "object" && "code" in cause && cause.code === "ENOENT") return undefined;
    throw cause;
  }
  if (!metadata.isFile() || metadata.isSymbolicLink()) throw new Error(`refusing to read unsafe installer manifest: ${relative(process.cwd(), path)}`);
  const bytes = await readFile(path);
  let parsed: unknown;
  try { parsed = JSON.parse(bytes.toString("utf8")); } catch { throw new Error(`refusing to overwrite invalid installer manifest: ${relative(process.cwd(), path)}`); }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error(`refusing to overwrite invalid installer manifest: ${relative(process.cwd(), path)}`);
  const candidate = parsed as { version?: unknown; files?: unknown };
  if (candidate.version !== 1 || !candidate.files || typeof candidate.files !== "object" || Array.isArray(candidate.files) ||
    Object.values(candidate.files).some((value) => typeof value !== "string")) {
    throw new Error(`refusing to overwrite invalid installer manifest: ${relative(process.cwd(), path)}`);
  }
  return { manifest: parsed as Manifest, bytes, mode: metadata.mode & 0o777 };
}
export async function installOmp(repoDir: string, dryRun = false): Promise<InstallResult> {
  const repo = resolve(repoDir);
  const templateRoot = new URL("../templates/", import.meta.url);
  const files = Object.keys(INSTALL_FILES).map((path) => relative(repo, join(repo, ".omp", path)));
  const manifestPath = join(repo, MANIFEST_PATH);
  const manifestSnapshot = await readManifestSnapshot(manifestPath);
  const manifest = manifestSnapshot?.manifest;
  const templates = new Map<string, string>();
  if (manifest?.files["config.yml"]) {
    throw new Error("existing installer-managed .omp/config.yml requires owner review; preserve and merge host extensions before a new install");
  }
  for (const [destination, template] of Object.entries(INSTALL_FILES)) {
    templates.set(destination, await readFile(new URL(template, templateRoot), "utf8"));
  }

  const edited: string[] = [];
  const unmanaged: string[] = [];
  const writes = new Set<string>();
  for (const [destination, content] of templates) {
    const absolute = join(repo, ".omp", destination);
    if (!(await exists(absolute))) {
      writes.add(destination);
      continue;
    }
    if (!manifest) {
      unmanaged.push(relative(repo, absolute));
      continue;
    }
    const existing = await readFile(absolute, "utf8");
    const expected = manifest.files[destination];
    if (!expected || sha256(existing) !== expected) {
      edited.push(relative(repo, absolute));
      continue;
    }
    if (existing !== content) writes.add(destination);
  }
  if (edited.length > 0) throw new Error(`refusing to overwrite user-edited files: ${edited.join(", ")}`);
  if (unmanaged.length > 0) throw new Error(`refusing to overwrite existing files without installer manifest: ${unmanaged.join(", ")}`);

  const outputFiles = [...files, relative(repo, manifestPath)];
  if (!dryRun) {
    for (const destination of writes) await mkdir(resolve(join(repo, ".omp", destination), ".."), { recursive: true });
    const hashes: Record<string, string> = {};
    for (const [destination, content] of templates) hashes[destination] = sha256(content);
    for (const destination of writes) {
      const content = templates.get(destination);
      if (content === undefined) throw new Error(`installer plan references an unknown template: ${destination}`);
      await writeFile(join(repo, ".omp", destination), content, { mode: 0o644 });
    }
    const manifestContent = `${JSON.stringify({ version: 1, files: hashes }, null, 2)}\n`;
    if (!(await exists(manifestPath)) || await readFile(manifestPath, "utf8") !== manifestContent) {
      await writeFile(manifestPath, manifestContent, { mode: 0o644 });
    }
  }
  return { status: dryRun ? "DRY_RUN" : "READY", repo, files: outputFiles, extensionActivation: "MANUAL_REQUIRED" };
}

export type UninstallResult = { status: "DRY_RUN" | "REMOVED"; repo: string; files: string[]; kept: string[]; missing: string[] };
export async function uninstallOmp(repoDir: string, dryRun = true): Promise<UninstallResult> {
  const repo = resolve(repoDir);
  const manifestPath = join(repo, MANIFEST_PATH);
  const manifestSnapshot = await readManifestSnapshot(manifestPath);
  const manifest = manifestSnapshot?.manifest;
  if (!manifestSnapshot || !manifest) throw new Error(`no installer manifest: ${relative(process.cwd(), manifestPath)}`);
  const ompRoot = join(repo, ".omp");
  const remove: string[] = [];
  const kept: string[] = [];
  const missing: string[] = [];
  const expected = new Map<string, { sha256: string; mode: number }>();
  for (const [destination, expectedHash] of Object.entries(manifest.files)) {
    const absolute = resolve(ompRoot, destination);
    if (absolute === ompRoot || !absolute.startsWith(ompRoot + "/")) {
      throw new Error(`manifest entry escapes .omp, refusing: ${destination}`);
    }
    const rel = relative(repo, absolute);
    let metadata;
    try { metadata = await lstat(absolute); }
    catch (cause) {
      if (cause && typeof cause === "object" && "code" in cause && (cause.code === "ENOENT" || cause.code === "ENOTDIR")) {
        missing.push(rel);
        continue;
      }
      throw cause;
    }
    if (isProtectedMutationPath(rel) || !metadata.isFile() || metadata.isSymbolicLink()) {
      kept.push(rel);
      continue;
    }
    const bytes = await readFile(absolute);
    if (sha256(bytes) !== expectedHash) {
      kept.push(rel);
      continue;
    }
    expected.set(rel, { sha256: sha256(bytes), mode: metadata.mode & 0o777 });
    remove.push(rel);
  }
  const manifestRelative = relative(repo, manifestPath);
  expected.set(manifestRelative, { sha256: sha256(manifestSnapshot.bytes), mode: manifestSnapshot.mode });
  remove.push(manifestRelative);
  if (!dryRun) {
    const doctorDir = resolve(process.env.JEV_DOCTOR_DIR || join(homedir(), ".local", "state", "classifier", "doctor"));
    const runId = `${new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-')}.${randomUUID()}`;
    for (const rel of remove) {
      const before = expected.get(rel)!;
      await mutate({
        root: repo,
        doctorDir,
        target: rel,
        writeScopes: [rel],
        operation: "quarantine",
        runId,
        expectedBeforeSha256: before.sha256,
        expectedBeforeMode: before.mode,
        actionKind: "uninstall",
      });
    }
  }
  return { status: dryRun ? "DRY_RUN" : "REMOVED", repo, files: remove, kept, missing };
}
export async function ompDiscovery(repoDir: string): Promise<Record<string, unknown>> {
  const repo = resolve(repoDir); const tools = Object.keys(INSTALL_FILES).filter((path) => path.startsWith("tools/")).map((path) => ({ path: `.omp/${path}`, present: true })); const hooks = [{ path: ".omp/hooks/post/jev-gate-observe.ts", present: true }];
  for (const row of [...tools, ...hooks]) row.present = await exists(join(repo, row.path));
  const extensions = Object.keys(INSTALL_FILES).filter((path) => path.startsWith("extensions/")).map((path) => ({ path: `.omp/${path}`, present: true })); for (const row of extensions) row.present = await exists(join(repo, row.path));
  return { repo, tools, hooks, extensions, manifest: await exists(join(repo, MANIFEST_PATH)) };
}
