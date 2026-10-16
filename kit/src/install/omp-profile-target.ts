// OMP profile target (T8): install measured-profile shims for declared-ON
// families behind blast-radius checks. Every family install requires: the
// surface present in the shared switch registry with a non-null off switch
// the manifest names exactly; a positive-integer latency at or under the
// handler limit; a declared-safe-side test id bound to a canonical executable
// proof; and a contract that passes validateContract (which itself refuses
// contradictions). Declared-OFF families never install; extension families
// outside their supported profiles are unsupported. Predecessors that are not
// our shims conflict (exit 4) unless migrate backs them up; repo-path
// predecessors are refused untouched. All paths derive from explicit inputs;
// nothing reads process.env.

import { mkdir, readFile, realpath, stat, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { EXIT_CODES } from "../families/registry.js";
import { validateContract, type DecisionContract } from "../contracts.js";
import { isSafeProfileName, profileAgentDir } from "./omp-paths.js";
import { decide } from "../conformance.js";

export const SHIM_MARKER_PREFIX = "// classifier-shim-v2";
export type TargetFamily = {
  id: string;
  surfaceType: string;
  kind: "gate" | "screen" | "extension";
  declared: "ON" | "OFF";
  supportedProfiles?: string[];
  contract: unknown;
  manifest: {
    latencyBudgetMs: number;
    safeSideTestId: string;
    offSwitchPath: string;
  };
  packageSpecifier: string;
  packageRoot: string;
  packageLockPath: string;
  pin: string;
};

export type SwitchRegistrySurface = {
  id: string;
  off_switch: { path: string; polarity: string } | null;
};

export type SwitchRegistry = {
  surfaces: SwitchRegistrySurface[];
};

export type ProfileInstallInput = {
  ompHome: string;
  profiles: string[];
  families: TargetFamily[];
  switchRegistry: SwitchRegistry;
  maxHandlerLatencyMs: number;
  migrate?: boolean;
};

export type FamilyInstallStatus = {
  family: string;
  profile: string;
  status: "installed" | "already" | "skipped-off" | "unsupported" | "conflict" | "refused";
  reason?: string;
};

export type ProfileInstallResult = {
  exit: number;
  writes: string[];
  families: FamilyInstallStatus[];
};

function digestOf(bytes: Uint8Array): string {
  return createHash("sha256").update(bytes).digest("hex");
}

type ShimRecord = { path: string; sha256: string; pin: string };

async function readShimMarker(agentDir: string): Promise<{ marker: Record<string, ShimRecord>; raw: Buffer | undefined; path: string }> {
  const path = join(agentDir, "jev-shims.json");
  let raw: Buffer | undefined;
  try {
    raw = await readFile(path);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return { marker: {}, raw: undefined, path };
    }
    throw new Error(`cannot read ${path}: ${error instanceof Error ? error.message : String(error)}`);
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw.toString("utf8"));
  } catch {
    throw new Error(`cannot parse shim marker: ${path}`);
  }
  const marker: Record<string, ShimRecord> = {};
  if (parsed && typeof parsed === "object" && "shims" in parsed && parsed.shims !== null && typeof parsed.shims === "object") {
    for (const [key, value] of Object.entries(parsed.shims)) {
      if (
        value !== null &&
        typeof value === "object" &&
        "path" in value && typeof value.path === "string" &&
        "sha256" in value && typeof value.sha256 === "string" &&
        "pin" in value && typeof value.pin === "string"
      ) {
        marker[key] = { path: value.path, sha256: value.sha256, pin: value.pin };
      }
    }
  }
  return { marker, raw, path };
}
function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isGitCommit(value: unknown): value is string {
  if (typeof value !== "string" || value.length !== 40) return false;
  for (const character of value) {
    const code = character.charCodeAt(0);
    if (!((code >= 48 && code <= 57) || (code >= 97 && code <= 102))) return false;
  }
  return true;
}

function packageNameFromSpecifier(specifier: string): string {
  if (!specifier || specifier.startsWith("/") || specifier.includes("\\") || specifier.includes("\0")) {
    throw new Error("invalid packaged import specifier");
  }
  const segments = specifier.split("/");
  if (segments.some((segment) => segment === "" || segment === "." || segment === "..")) {
    throw new Error("invalid packaged import path");
  }
  if (segments[0].startsWith("@")) {
    if (segments.length < 2 || segments[0].length < 2) throw new Error("invalid scoped package import");
    return segments[0] + "/" + segments[1];
  }
  return segments[0];
}

async function resolveFamilyPackage(family: TargetFamily): Promise<Record<string, unknown>> {
  const packageName = packageNameFromSpecifier(family.packageSpecifier);
  const packageRoot = resolve(family.packageRoot);
  const packageLockPath = resolve(family.packageLockPath);
  const lockRoot = dirname(packageLockPath);
  let packageValue: unknown;
  let consumerValue: unknown;
  let lockValue: unknown;
  try {
    packageValue = JSON.parse(await readFile(join(packageRoot, "package.json"), "utf8")) as unknown;
    consumerValue = JSON.parse(await readFile(join(lockRoot, "package.json"), "utf8")) as unknown;
    lockValue = JSON.parse(await readFile(packageLockPath, "utf8")) as unknown;
  } catch (error) {
    throw new Error("package manifest or lockfile cannot be read: " + family.id + ": " + (error instanceof Error ? error.message : String(error)));
  }
  if (!isRecord(packageValue) || packageValue.name !== packageName || typeof packageValue.version !== "string") {
    throw new Error("package manifest does not identify imported package: " + family.id);
  }
  if (!isRecord(consumerValue) || !isRecord(consumerValue.dependencies) || !isRecord(lockValue) ||
      (lockValue.lockfileVersion !== 2 && lockValue.lockfileVersion !== 3) || !isRecord(lockValue.packages)) {
    throw new Error("package manifest or lockfile is invalid: " + family.id);
  }
  const lockRootEntry = lockValue.packages[""];
  const packageEntry = lockValue.packages["node_modules/" + packageName];
  if (!isRecord(lockRootEntry) || !isRecord(lockRootEntry.dependencies) || !isRecord(packageEntry)) {
    throw new Error("package lock does not contain imported package: " + family.id);
  }
  const declared = consumerValue.dependencies[packageName];
  const lockedRoot = lockRootEntry.dependencies[packageName];
  const resolved = packageEntry.resolved;
  if (typeof declared !== "string" || typeof lockedRoot !== "string" || typeof resolved !== "string" ||
      declared !== lockedRoot || declared !== resolved || packageEntry.version !== packageValue.version || !isGitCommit(family.pin)) {
    throw new Error("package manifest and lock do not agree: " + family.id);
  }
  const hashOffset = resolved.lastIndexOf("#");
  const resolvedCommit = hashOffset < 0 ? "" : resolved.slice(hashOffset + 1);
  if (!resolved.startsWith("git+https://") || !isGitCommit(resolvedCommit) || resolvedCommit !== family.pin) {
    throw new Error("package lock does not pin the declared commit: " + family.id);
  }
  const installedPackageRoot = await realpath(join(lockRoot, "node_modules", ...packageName.split("/")));
  const actualPackageRoot = await realpath(packageRoot);
  if (installedPackageRoot !== actualPackageRoot) throw new Error("package root differs from locked install: " + family.id);
  const requireFromConsumer = createRequire(join(lockRoot, "package.json"));
  const importedPath = await realpath(requireFromConsumer.resolve(family.packageSpecifier));
  const importRelative = relative(actualPackageRoot, importedPath);
  if (importRelative === ".." || importRelative.startsWith(".." + sep) || isAbsolute(importRelative) || !(await stat(importedPath)).isFile()) {
    throw new Error("package import does not resolve inside the locked package: " + family.id);
  }
  const jevMetadata = packageValue.jev;
  const safeSideTests = isRecord(jevMetadata) ? jevMetadata.safe_side_tests : undefined;
  if (!isRecord(safeSideTests)) throw new Error("package manifest has no safe-side test registry: " + family.id);
  return safeSideTests;
}


function shimSource(family: TargetFamily, profile: string, offSwitch: { path: string; polarity: string }, safeSide: string): string {
  return (
    `${SHIM_MARKER_PREFIX} family=${family.id} profile=${profile} pin=${family.pin}\n` +
    `// off-switch: ${offSwitch.path} (${offSwitch.polarity})\n` +
    `// safe-side: ${safeSide} (test ${family.manifest.safeSideTestId})\n` +
    "export * from " + JSON.stringify(family.packageSpecifier) + ";\n"
  );
}

const CANONICAL_SAFE_SIDE_PROOFS: Record<string, string> = {
  "command-gate:refuse": "gateNetworkUnreachableRefuses",
  "result-screen:pass": "screenNetworkUnreachablePasses",
};

async function proveSafeSideUnreachable(contract: DecisionContract): Promise<string> {
  const state = Object.fromEntries(contract.state.fields.map((field) => [field, "fixture"]));
  const outcome = await decide({
    contract,
    state,
    result: { fixture: "unchanged" },
    adapter: {
      id: "offline-unreachable",
      modelId: "offline-unreachable",
      probabilities: "required",
      evaluate: async (request, transport) => transport(request),
    },
    transport: async () => {
      throw new Error("network unreachable");
    },
  });
  if (outcome.status !== "transport-error" || outcome.reason !== "transport") {
    throw new Error("safe-side proof did not reach the unreachable transport");
  }
  return outcome.action;
}

async function checkBlastRadius(
  family: TargetFamily,
  registry: SwitchRegistry,
  maxHandlerLatencyMs: number,
  safeSideTests: Record<string, unknown>,
): Promise<{ offSwitch: { path: string; polarity: string }; safeSide: string }> {
  const surface = registry.surfaces.find((entry) => entry.id === family.id);
  if (surface === undefined) throw new Error("unknown surface: " + family.id);
  if (surface.off_switch === null || surface.off_switch === undefined) throw new Error("surface has no off switch: " + family.id);
  if (family.manifest.offSwitchPath !== surface.off_switch.path) throw new Error("manifest off switch does not match registry: " + family.id);
  const latency = family.manifest.latencyBudgetMs;
  if (!Number.isSafeInteger(latency) || (latency as number) < 1 || (latency as number) > maxHandlerLatencyMs) {
    throw new Error("latency budget outside the handler limit: " + family.id);
  }
  if (typeof family.manifest.safeSideTestId !== "string" || family.manifest.safeSideTestId.trim() === "") {
    throw new Error("manifest names no declared-safe-side test: " + family.id);
  }
  let contract: DecisionContract & { safe_side_test_id?: string };
  try {
    contract = validateContract(family.contract);
  } catch (error) {
    throw new Error("contract refused: " + (error instanceof Error ? error.message : String(error)));
  }
  const testId = contract.safe_side_test_id;
  if (typeof testId !== "string" || testId.trim() === "" || family.manifest.safeSideTestId !== testId) {
    throw new Error("manifest safe-side test ID does not match contract: " + family.id);
  }
  if (family.surfaceType !== contract.surface_type) throw new Error("family surface type does not match contract: " + family.id);
  const registration = safeSideTests[testId];
  if (!isRecord(registration) || registration.surface_type !== contract.surface_type ||
      registration.safe_side !== contract.safe_side || typeof registration.test !== "string" || registration.test.trim() === "") {
    throw new Error("contract safe-side test ID is not registered for this surface/action: " + family.id);
  }
  const canonicalProof = CANONICAL_SAFE_SIDE_PROOFS[contract.surface_type + ":" + contract.safe_side];
  if (canonicalProof === undefined || registration.test !== canonicalProof) {
    throw new Error("contract safe-side test is not a known executable proof: " + family.id);
  }
  const provenAction = await proveSafeSideUnreachable(contract);
  if (provenAction !== contract.safe_side) {
    throw new Error("safe-side proof did not produce the contracted action: " + family.id);
  }
  return { offSwitch: surface.off_switch, safeSide: contract.safe_side };
}

export async function installProfileTargets(input: ProfileInstallInput): Promise<ProfileInstallResult> {
  const writes: string[] = [];
  const families: FamilyInstallStatus[] = [];
  let refused = false;
  for (const profile of input.profiles) {
    let agentDir: string;
    try {
      agentDir = profileAgentDir(input.ompHome, profile);
    } catch {
      families.push(...input.families.map((family) => ({ family: family.id, profile, status: "refused" as const, reason: "bad-profile" })));
      refused = true;
      continue;
    }
    const markerState = await readShimMarker(agentDir);
    let marker = markerState.marker;
    let markerDirty = false;
    for (const family of input.families) {
      if (family.declared !== "ON") {
        families.push({ family: family.id, profile, status: "skipped-off" });
        continue;
      }
      if (family.kind === "extension" && family.supportedProfiles !== undefined && !family.supportedProfiles.includes(profile)) {
        families.push({ family: family.id, profile, status: "unsupported" });
        continue;
      }
      if (!isSafeProfileName(family.id)) {
        families.push({ family: family.id, profile, status: "refused", reason: "bad-family-id" });
        refused = true;
        continue;
      }
      if (family.packageSpecifier.startsWith("/") || family.packageSpecifier.includes("/Users/") || family.packageSpecifier.includes("Developer/jev")) {
        throw new Error(`packaged import must not be a repo path: ${family.id}`);
      }
      let gate: { offSwitch: { path: string; polarity: string }; safeSide: string };
      try {
        const safeSideTests = await resolveFamilyPackage(family);
        gate = await checkBlastRadius(family, input.switchRegistry, input.maxHandlerLatencyMs, safeSideTests);
      } catch (error) {
        families.push({ family: family.id, profile, status: "refused", reason: error instanceof Error ? error.message : String(error) });
        refused = true;
        continue;
      }
      const dest = join(agentDir, "shims", `jev-${family.id}.ts`);
      const source = shimSource(family, profile, gate.offSwitch, gate.safeSide);
      if (source.includes("/Users/") || source.includes("Developer/jev")) {
        throw new Error(`generated shim leaks a repo path: ${family.id}`);
      }
      let existing: Buffer | undefined;
      try {
        existing = await readFile(dest);
      } catch (error) {
        if (!error || typeof error !== "object" || !("code" in error) || error.code !== "ENOENT") {
          throw new Error(`cannot read ${dest}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
      const record = marker[family.id];
      if (existing !== undefined && record !== undefined && record.pin === family.pin && record.sha256 === digestOf(existing) && existing.toString("utf8") === source) {
        families.push({ family: family.id, profile, status: "already" });
        continue;
      }
      if (existing !== undefined) {
        const text = existing.toString("utf8");
        const ours = text.includes(`${SHIM_MARKER_PREFIX} family=${family.id} `);
        if (!ours) {
          if (text.includes("/Users/") || text.includes("Developer/jev")) {
            families.push({ family: family.id, profile, status: "refused", reason: "repo-path-predecessor" });
            refused = true;
            continue;
          }
          if (input.migrate !== true) {
            families.push({ family: family.id, profile, status: "conflict", reason: "unmarked-predecessor" });
            refused = true;
            continue;
          }
          const backup = `${dest}.migrate-bak`;
          await mkdir(dirname(backup), { recursive: true });
          await writeFile(backup, existing);
          writes.push(backup);
        }
      }
      await mkdir(dirname(dest), { recursive: true });
      const before = existing === undefined ? undefined : existing;
      if (before === undefined || digestOf(before) !== digestOf(Buffer.from(source, "utf8"))) {
        await writeFile(dest, source);
        writes.push(dest);
      }
      marker = { ...marker, [family.id]: { path: `shims/jev-${family.id}.ts`, sha256: digestOf(Buffer.from(source, "utf8")), pin: family.pin } };
      markerDirty = true;
      families.push({ family: family.id, profile, status: "installed" });
    }
    if (markerDirty) {
      const text = JSON.stringify({ shims: marker }, null, 2) + "\n";
      const current = markerState.raw === undefined ? undefined : markerState.raw.toString("utf8");
      if (current !== text) {
        await mkdir(agentDir, { recursive: true });
        await writeFile(markerState.path, text);
        writes.push(markerState.path);
      }
    }
  }
  return { exit: refused ? EXIT_CODES.REFUSED_UNSAFE : EXIT_CODES.OK, writes, families };
}
