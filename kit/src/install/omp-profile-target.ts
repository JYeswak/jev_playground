// OMP profile target (T8): install measured-profile shims for declared-ON
// families behind blast-radius checks. Every family install requires: the
// surface present in the shared switch registry with a non-null off switch
// the manifest names exactly; a positive-integer latency at or under the
// handler limit; a non-empty declared-safe-side test id; and a contract that
// passes validateContract (which itself refuses safe-side/surface-type
// contradictions). Declared-OFF families never install; extension families
// outside their supported profiles are unsupported. Predecessors that are not
// our shims conflict (exit 4) unless migrate backs them up; repo-path
// predecessors are refused untouched. All paths derive from explicit inputs;
// nothing reads process.env.

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { EXIT_CODES } from "../families/registry.js";
import { validateContract } from "../contracts.js";
import { isSafeProfileName, profileAgentDir } from "./omp-paths.js";

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

function shimSource(family: TargetFamily, profile: string, offSwitch: { path: string; polarity: string }, safeSide: string): string {
  return (
    `${SHIM_MARKER_PREFIX} family=${family.id} profile=${profile} pin=${family.pin}\n` +
    `// off-switch: ${offSwitch.path} (${offSwitch.polarity})\n` +
    `// safe-side: ${safeSide} (test ${family.manifest.safeSideTestId})\n` +
    `export * from '${family.packageSpecifier}';\n`
  );
}

function checkBlastRadius(
  family: TargetFamily,
  registry: SwitchRegistry,
  maxHandlerLatencyMs: number,
): { offSwitch: { path: string; polarity: string }; safeSide: string } {
  const surface = registry.surfaces.find((entry) => entry.id === family.id);
  if (surface === undefined) {
    throw new Error(`unknown surface: ${family.id}`);
  }
  if (surface.off_switch === null || surface.off_switch === undefined) {
    throw new Error(`surface has no off switch: ${family.id}`);
  }
  if (family.manifest.offSwitchPath !== surface.off_switch.path) {
    throw new Error(`manifest off switch does not match registry: ${family.id}`);
  }
  const latency = family.manifest.latencyBudgetMs;
  if (!Number.isSafeInteger(latency) || (latency as number) < 1 || (latency as number) > maxHandlerLatencyMs) {
    throw new Error(`latency budget outside the handler limit: ${family.id}`);
  }
  if (typeof family.manifest.safeSideTestId !== "string" || family.manifest.safeSideTestId.trim() === "") {
    throw new Error(`manifest names no declared-safe-side test: ${family.id}`);
  }
  let contract: { safe_side: string };
  try {
    contract = validateContract(family.contract);
  } catch (error) {
    throw new Error(`contract refused: ${error instanceof Error ? error.message : String(error)}`);
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
        gate = checkBlastRadius(family, input.switchRegistry, input.maxHandlerLatencyMs);
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
