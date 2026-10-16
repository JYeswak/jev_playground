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

import { mkdir, readdir, readFile, realpath, stat, writeFile } from "node:fs/promises";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { createRequire, registerHooks, stripTypeScriptTypes } from "node:module";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { EXIT_CODES } from "../families/registry.js";
import { validateContract, type DecisionContract } from "../contracts.js";
import { isSafeProfileName, profileAgentDir } from "./omp-paths.js";
import { decide } from "../conformance.js";
import { mergeExtensions } from "./omp-config-merge.js";


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

type ExtensionRecord = { config: string; entry: string; pin: string };

async function readShimMarker(agentDir: string): Promise<{ marker: Record<string, ShimRecord>; extensions: Record<string, ExtensionRecord>; raw: Buffer | undefined; path: string }> {
  const path = join(agentDir, "jev-shims.json");
  let raw: Buffer | undefined;
  try {
    raw = await readFile(path);
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return { marker: {}, extensions: {}, raw: undefined, path };
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
  const extensions: Record<string, ExtensionRecord> = {};
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
  if (parsed && typeof parsed === "object" && "extensions" in parsed && parsed.extensions !== null && typeof parsed.extensions === "object") {
    for (const [key, value] of Object.entries(parsed.extensions)) {
      if (
        value !== null &&
        typeof value === "object" &&
        "config" in value && typeof value.config === "string" &&
        "entry" in value && typeof value.entry === "string" &&
        "pin" in value && typeof value.pin === "string"
      ) {
        extensions[key] = { config: value.config, entry: value.entry, pin: value.pin };
      }
    }
  }
  return { marker, extensions, raw, path };
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

async function resolveFamilyPackage(family: TargetFamily): Promise<{ safeSideTests: Record<string, unknown>; importedPath: string; packageDir: string }> {
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
  return { safeSideTests, importedPath, packageDir: actualPackageRoot };
}


function shimSource(family: TargetFamily, profile: string, offSwitch: { path: string; polarity: string }, safeSide: string, importSpecifier: string): string {
  // export * re-exports named bindings only; the native default factory is
  // forwarded explicitly so the installed entry exposes the host contract.
  return (
    `${SHIM_MARKER_PREFIX} family=${family.id} profile=${profile} pin=${family.pin}\n` +
    `// off-switch: ${offSwitch.path} (${offSwitch.polarity})\n` +
    `// safe-side: ${safeSide} (test ${family.manifest.safeSideTestId})\n` +
    "export * from " + JSON.stringify(importSpecifier) + ";\n" +
    "export { default } from " + JSON.stringify(importSpecifier) + ";\n"
  );
}

const CANONICAL_SAFE_SIDE_PROOFS: Record<string, string> = {
  "command-gate:refuse": "gateNetworkUnreachableRefuses",
  "result-screen:pass": "screenNetworkUnreachablePasses",
  "advisory:pass": "hintAdvisoryUnreachablePasses",
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

type NativeMechanism = { kind: "hook"; hooksDir: "pre" | "post"; event: string } | { kind: "extension" };

// Declared surface -> native installation mechanism. A command gate must
// intercept before execution (pre tool_call hook); a result screen triages
// completed results (post tool_result hook); an advisory registers by path
// (config.yml extensions). Surfaces outside this table refuse rather than
// fake-install.
const NATIVE_SURFACE_MECHANISMS: Record<string, NativeMechanism> = {
  "command-gate": { kind: "hook", hooksDir: "pre", event: "tool_call" },
  "result-screen": { kind: "hook", hooksDir: "post", event: "tool_result" },
  "advisory": { kind: "extension" },
};

// A package entry is native-compatible for its declared surface when it
// loads, exposes a default function export, and — for hook mechanisms —
// registers its declared host event when invoked with a stub pi. The check
// runs by execution in both cases: directly, or — for exactly one Node
// limitation (type stripping is banned for files under node_modules, while
// the host loader accepts them there) — through a scoped builtin-TS load
// hook covering only the locked package root, deregistered in finally.
// The hook uses Node's own stripping engine, so entries load exactly as
// Node would load them outside node_modules; relative structure, bare
// dependencies and import.meta resolve in place, and unresolvable ones
// fail closed at import. Pure library modules without a default export,
// and factories that never register, are refused before any write. The
// host session start remains the final load authority.
function registerPackageTsHook(packageDir: string, familyId: string): () => void {
  if (typeof registerHooks !== "function") {
    throw new Error("native TypeScript verification needs a Node load-hook runtime: " + familyId);
  }
  const rootUrl = pathToFileURL(packageDir).href;
  const prefix = rootUrl.endsWith("/") ? rootUrl : rootUrl + "/";
  const handle = registerHooks({
    load(url, context, next) {
      if (url.startsWith(prefix) && (url.endsWith(".ts") || url.endsWith(".mts") || url.endsWith(".cts") || url.endsWith(".tsx"))) {
        return {
          format: "module",
          source: stripTypeScriptTypes(readFileSync(fileURLToPath(url), "utf8")),
          shortCircuit: true,
        };
      }
      return next(url, context);
    },
  });
  return () => handle.deregister();
}


async function checkLoadedModule(loaded: unknown, familyId: string, expectedEvent: string | undefined): Promise<void> {
  if (!isRecord(loaded) || !("default" in loaded) || typeof loaded.default !== "function") {
    throw new Error("native entry has no default function export: " + familyId);
  }
  // Every entry factory runs against a closed-world stub mirroring the
  // observed host surface (on, registerTool, flat zod builders). Unknown
  // host methods are absent, so calling one throws exactly as the real
  // host would — nothing is fabricated. A factory that throws is
  // incompatible, whatever it declares. Deep chained host APIs fail
  // closed; the stub is a boundary probe, not an emulator.
  const calls: Array<{ method: string; args: unknown[] }> = [];
  const stubPi = {
    on: (event: string, handler: unknown) => {
      calls.push({ method: "on", args: [event, handler] });
    },
    registerTool: (tool: unknown) => {
      calls.push({ method: "registerTool", args: [tool] });
    },
    zod: {
      object: (shape: unknown) => { calls.push({ method: "zod.object", args: [shape] }); return {}; },
      string: () => { calls.push({ method: "zod.string", args: [] }); return {}; },
      array: (of: unknown) => { calls.push({ method: "zod.array", args: [of] }); return {}; },
    },
  };
  // The typeof check above proves callability; name the factory shape once
  // for the invocation below.
  const factory: (pi: unknown) => unknown = loaded.default as (pi: unknown) => unknown;
  try {
    await factory(stubPi);
  } catch (error) {
    throw new Error("native entry factory throws: " + familyId + ": " + (error instanceof Error ? error.message : String(error)));
  }
  if (expectedEvent === undefined) {
    // Advisory contract, derived from the in-repo extension exemplar: the
    // entry must register at least one tool. Clean completion alone is not
    // registration.
    const toolsRegistered = calls.some((call) => call.method === "registerTool");
    if (!toolsRegistered) {
      throw new Error("native entry registers no tool: " + familyId);
    }
    return;
  }
  // Hook contract: the declared event must be registered with a callable
  // handler. pi.on(name, null) does not count.
  const registered = calls.some((call) => call.method === "on" && call.args.length >= 2 && call.args[0] === expectedEvent && typeof call.args[1] === "function");
  if (!registered) {
    throw new Error("native entry does not register " + expectedEvent + ": " + familyId);
  }
}

async function loadNativeEntry(importedPath: string, packageDir: string, familyId: string, expectedEvent: string | undefined): Promise<void> {
  const typeScriptEntry = importedPath.endsWith(".ts") || importedPath.endsWith(".mts") || importedPath.endsWith(".cts") || importedPath.endsWith(".tsx");
  if (!typeScriptEntry) {
    let loaded: unknown;
    try {
      // Dynamic import: the specifier is computed at runtime from the validated
      // locked package path, so no static import can name this module.
      loaded = await import(pathToFileURL(importedPath).href);
    } catch (error) {
      throw new Error("native entry does not load: " + familyId + ": " + (error instanceof Error ? error.message : String(error)));
    }
    await checkLoadedModule(loaded, familyId, expectedEvent);
    return;
  }
  // TypeScript entries always go through the scoped hook FIRST: on some
  // runtimes (observed Node 22.18) a failed direct import poisons the URL,
  // so a direct attempt must never precede the hooked one. Exactly one
  // import attempt per URL keeps failure caching deterministic.
  const deregister = registerPackageTsHook(packageDir, familyId);
  let loaded: unknown;
  try {
    loaded = await import(pathToFileURL(importedPath).href);
  } catch (error) {
    deregister();
    throw new Error("native entry does not load: " + familyId + ": " + (error instanceof Error ? error.message : String(error)));
  }
  try {
    await checkLoadedModule(loaded, familyId, expectedEvent);
  } finally {
    deregister();
  }
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
    let extensions = markerState.extensions;
    let markerDirty = false;
    let extensionsDirty = false;
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
      let importedPath: string;
      let mechanism: NativeMechanism;
      try {
        const resolved = await resolveFamilyPackage(family);
        importedPath = resolved.importedPath;
        gate = await checkBlastRadius(family, input.switchRegistry, input.maxHandlerLatencyMs, resolved.safeSideTests);
        const found = NATIVE_SURFACE_MECHANISMS[family.surfaceType];
        if (found === undefined) {
          throw new Error("unsupported native surface: " + family.id);
        }
        mechanism = found;
        await loadNativeEntry(importedPath, resolved.packageDir, family.id, mechanism.kind === "hook" ? mechanism.event : undefined);
      } catch (error) {
        families.push({ family: family.id, profile, status: "refused", reason: error instanceof Error ? error.message : String(error) });
        refused = true;
        continue;
      }
      if (mechanism.kind === "extension") {
        const entryAbs = importedPath;
        let merge;
        try {
          merge = await mergeExtensions({ configPath: join(agentDir, "config.yml"), profileDir: agentDir, addExtensions: [entryAbs] });
        } catch (error) {
          families.push({ family: family.id, profile, status: "refused", reason: error instanceof Error ? error.message : String(error) });
          refused = true;
          continue;
        }
        writes.push(...merge.writes);
        if (merge.status === "merged" || merge.status === "already") {
          const known = extensions[family.id];
          if (merge.status === "merged" || known === undefined || known.entry !== entryAbs || known.pin !== family.pin) {
            extensions = { ...extensions, [family.id]: { config: "config.yml", entry: entryAbs, pin: family.pin } };
            extensionsDirty = true;
          }
          families.push({ family: family.id, profile, status: merge.status === "merged" ? "installed" : "already" });
        } else {
          families.push({ family: family.id, profile, status: "refused", reason: "extension config " + merge.status + ": " + family.id });
          refused = true;
        }
        continue;
      }
      const dest = join(agentDir, "hooks", mechanism.hooksDir, `jev-${family.id}.ts`);
      const shimRelative = relative(dirname(dest), importedPath);
      const importSpecifier = shimRelative.startsWith(".") ? shimRelative : "./" + shimRelative;
      const source = shimSource(family, profile, gate.offSwitch, gate.safeSide, importSpecifier);
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
      marker = { ...marker, [family.id]: { path: `hooks/${mechanism.hooksDir}/jev-${family.id}.ts`, sha256: digestOf(Buffer.from(source, "utf8")), pin: family.pin } };
      markerDirty = true;
      families.push({ family: family.id, profile, status: "installed" });
    }
    if (markerDirty || extensionsDirty) {
      const text = JSON.stringify({ shims: marker, extensions }, null, 2) + "\n";
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
