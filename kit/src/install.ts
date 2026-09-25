import { createHash } from "node:crypto";
import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { join, relative, resolve } from "node:path";

export const INSTALL_FILES = {
  "tools/jev-rerank.ts": "omp/tools/jev-rerank.ts",
  "tools/jev-claim-check.ts": "omp/tools/jev-claim-check.ts",
  "tools/jev-screen.ts": "omp/tools/jev-screen.ts",
  "tools/jev-flag.ts": "omp/tools/jev-flag.ts",
  "hooks/post/jev-gate-observe.ts": "omp/hooks/post/jev-gate-observe.ts",
  "config.yml": "omp/config.yml",
  "extensions/jev-rerank.ts": "omp/extensions/jev-rerank.ts",
  "extensions/jev-claim-check.ts": "omp/extensions/jev-claim-check.ts",
  "extensions/jev-screen.ts": "omp/extensions/jev-screen.ts",
  "extensions/jev-flag.ts": "omp/extensions/jev-flag.ts",
  "jev-kit/client.ts": "jev-kit/client.ts",
  "jev-kit/validate.ts": "jev-kit/validate.ts",
  "jev-kit/preflight.ts": "jev-kit/preflight.ts",
  "jev-kit/fake.ts": "jev-kit/fake.ts",
  "jev-kit/use-infisical-key.ts": "jev-kit/use-infisical-key.ts",
  "jev-kit/infisical-key.ts": "jev-kit/infisical-key.ts",
  "jev-kit/questions.mjs": "jev-kit/questions.mjs",
  "jev-kit/nev-rerank/rank.ts": "jev-kit/nev-rerank/rank.ts",
  "jev-kit/nev-rerank/live.ts": "jev-kit/nev-rerank/live.ts",
  "jev-kit/nev-injection/live-flag.ts": "jev-kit/nev-injection/live-flag.ts",
};

const MANIFEST_PATH = ".omp/jev-kit-manifest.json";

type Manifest = { version: 1; files: Record<string, string> };

export type InstallResult = {
  status: "READY" | "DRY_RUN";
  repo: string;
  files: string[];
};

async function exists(path: string): Promise<boolean> {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

function sha256(content: string): string {
  return createHash("sha256").update(content, "utf8").digest("hex");
}

async function readManifest(path: string): Promise<Manifest | undefined> {
  if (!(await exists(path))) return undefined;
  let parsed: unknown;
  try {
    parsed = JSON.parse(await readFile(path, "utf8"));
  } catch {
    throw new Error(`refusing to overwrite invalid installer manifest: ${relative(process.cwd(), path)}`);
  }
  if (!parsed || typeof parsed !== "object" || (parsed as Manifest).version !== 1 || typeof (parsed as Manifest).files !== "object") {
    throw new Error(`refusing to overwrite invalid installer manifest: ${relative(process.cwd(), path)}`);
  }
  return parsed as Manifest;
}

export async function installOmp(repoDir: string, dryRun = false): Promise<InstallResult> {
  const repo = resolve(repoDir);
  const templateRoot = new URL("../templates/", import.meta.url);
  const files = Object.keys(INSTALL_FILES).map((path) => relative(repo, join(repo, ".omp", path)));
  const destinations = Object.keys(INSTALL_FILES).map((path) => join(repo, ".omp", path));
  const manifestPath = join(repo, MANIFEST_PATH);
  const manifest = await readManifest(manifestPath);
  const templates = new Map<string, string>();
  for (const [destination, template] of Object.entries(INSTALL_FILES)) {
    templates.set(destination, await readFile(new URL(template, templateRoot), "utf8"));
  }
  const edited = [];
  const unmanaged = [];
  for (const [destination] of templates) {
    const absolute = join(repo, ".omp", destination);
    if (!(await exists(absolute))) continue;
    if (!manifest) {
      unmanaged.push(relative(repo, absolute));
      continue;
    }
    const expected = manifest.files[destination];
    const actual = sha256(await readFile(absolute, "utf8"));
    if (!expected || actual !== expected) edited.push(relative(repo, absolute));
  }
  if (edited.length > 0) throw new Error(`refusing to overwrite user-edited files: ${edited.join(", ")}`);
  if (unmanaged.length > 0) throw new Error(`refusing to overwrite existing files without installer manifest: ${unmanaged.join(", ")}`);
  const outputFiles = [...files, relative(repo, manifestPath)];
  if (!dryRun) {
    for (const destination of destinations) await mkdir(resolve(destination, ".."), { recursive: true });
    const hashes: Record<string, string> = {};
    for (const [destination, content] of templates) {
      await writeFile(join(repo, ".omp", destination), content, { mode: 0o644 });
      hashes[destination] = sha256(content);
    }
    await writeFile(manifestPath, `${JSON.stringify({ version: 1, files: hashes }, null, 2)}\n`, { mode: 0o644 });
  }
  return { status: dryRun ? "DRY_RUN" : "READY", repo, files: outputFiles };
}

export async function ompDiscovery(repoDir: string): Promise<Record<string, unknown>> {
  const repo = resolve(repoDir);
  const tools = Object.keys(INSTALL_FILES)
    .filter((path) => path.startsWith("tools/"))
    .map((path) => ({ path: `.omp/${path}`, present: true }));
  const hooks = [{ path: ".omp/hooks/post/jev-gate-observe.ts", present: true }];
  for (const row of [...tools, ...hooks]) row.present = await exists(join(repo, row.path));
  const extensions = Object.keys(INSTALL_FILES)
    .filter((path) => path.startsWith("extensions/"))
    .map((path) => ({ path: `.omp/${path}`, present: true }));
  for (const row of extensions) row.present = await exists(join(repo, row.path));
  return { repo, tools, hooks, extensions, manifest: await exists(join(repo, MANIFEST_PATH)) };
}
