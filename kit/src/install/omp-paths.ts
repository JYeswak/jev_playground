// OMP profile/agent-dir resolution (T6): a port of DCG resolve_omp_agent_dir.
// Precedence, measured against `omp config path` in disposable HOMEs:
// - OMP_PROFILE set (even "") wins; "" means the default profile explicitly and
//   shadows the whole PI chain (a naive PI_PROFILE fallback fails that case).
// - OMP_PROFILE unset: a custom absolute PI_CODING_AGENT_DIR wins; a
//   legacy-derived one (exactly the default or profile-derived agent dir) is
//   ignored and resolution falls through to PI_PROFILE, then default.
// - PI_CONFIG_DIR overrides the config file path only when absolute.
// Reserved/traversal profile names and relative overrides are refused (USAGE)
// before any filesystem touch. This module reads no process environment and
// touches no filesystem: callers pass explicit values.

import { isAbsolute, join, normalize } from "node:path";

export type OmpPathError = Error & { code: "USAGE" };

function pathError(message: string): OmpPathError {
  return Object.assign(new Error(message), { code: "USAGE" as const });
}

const WINDOWS_RESERVED: Record<string, true> = {
  con: true,
  prn: true,
  aux: true,
  nul: true,
  com1: true,
  com2: true,
  com3: true,
  com4: true,
  com5: true,
  com6: true,
  com7: true,
  com8: true,
  com9: true,
  lpt1: true,
  lpt2: true,
  lpt3: true,
  lpt4: true,
  lpt5: true,
  lpt6: true,
  lpt7: true,
  lpt8: true,
  lpt9: true,
};

export function isSafeProfileName(name: string): boolean {
  if (typeof name !== "string" || name.length === 0) return false;
  if (name === "." || name === "..") return false;
  if (name.includes("/") || name.includes("\\") || name.includes("\0")) return false;
  const stem = name.includes(".") ? name.slice(0, name.indexOf(".")) : name;
  if (WINDOWS_RESERVED[name.toLowerCase()]) return false;
  if (WINDOWS_RESERVED[stem.toLowerCase()]) return false;
  return true;
}

export function ompHomeDir(home: string): string {
  return join(home, ".omp");
}

export function defaultAgentDir(home: string): string {
  return join(ompHomeDir(home), "agent");
}

export function profileAgentDir(ompHome: string, profile: string): string {
  if (profile === "default") return join(ompHome, "agent");
  if (!isSafeProfileName(profile)) {
    throw pathError(`refusing unsafe profile name: ${profile}`);
  }
  return join(ompHome, "profiles", profile, "agent");
}

export type OmpEnvInput = {
  home: string;
  ompProfile?: string;
  piProfile?: string;
  piCodingAgentDir?: string;
  piConfigDir?: string;
};

export function resolveAgentDir(input: OmpEnvInput): string {
  const ompHome = ompHomeDir(input.home);
  if (input.ompProfile !== undefined) {
    if (input.ompProfile === "") return join(ompHome, "agent");
    return profileAgentDir(ompHome, input.ompProfile);
  }
  const override = input.piCodingAgentDir;
  if (override !== undefined && override !== "") {
    if (!isAbsolute(override)) {
      throw pathError("PI_CODING_AGENT_DIR must be an absolute path");
    }
    const candidate = normalize(override);
    const legacyDefault = normalize(defaultAgentDir(input.home));
    const legacyProfile =
      input.piProfile !== undefined && input.piProfile !== ""
        ? normalize(profileAgentDir(ompHome, input.piProfile))
        : undefined;
    if (candidate !== legacyDefault && candidate !== legacyProfile) {
      return candidate;
    }
  }
  if (input.piProfile !== undefined && input.piProfile !== "") {
    return profileAgentDir(ompHome, input.piProfile);
  }
  return join(ompHome, "agent");
}

export function resolveConfigPath(input: OmpEnvInput): string {
  if (input.piConfigDir !== undefined && input.piConfigDir !== "") {
    if (!isAbsolute(input.piConfigDir)) {
      throw pathError("PI_CONFIG_DIR must be an absolute path");
    }
    return normalize(input.piConfigDir);
  }
  return join(resolveAgentDir(input), "config.yml");
}

