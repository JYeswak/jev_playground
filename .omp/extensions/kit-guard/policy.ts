/**
 * kit-guard policy: pure functions, no omp imports, so they can be unit-tested.
 *
 * W1.4 config-driven rebuild (plan docs/PLAN-DEEP-KIT-20260922.md:198):
 * the protected set is this repo's real gate set, read from
 * `.omp/kit-guard.json`. The hardcoded lists are gone; every matcher below
 * takes the loaded config. Missing or malformed config fails closed
 * (block and say why, never allow).
 *
 * Turns three FrankenSuite-kit rules that the 44-repo synthesis found were
 * enforced only by "agent obedience" (execution-readiness.md, Gate 18) into
 * hard blocks at the tool boundary:
 *   - B5 / pattern 1: never bypass or re-point the pre-commit honesty gate
 *   - B7 / pattern 1: never edit a gate to land a change (gate files are read-only
 *     to agents unless a human launched the session with KIT_GATE_EDIT=1)
 *   - A9: the 12 forbidden patterns stay verbatim in AGENTS.md
 */

import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";

export type Verdict = { block: true; reason: string } | null;

export const CONFIG_REL_PATH = ".omp/kit-guard.json";

export type GuardConfig = {
  hookDir: string;
  gatePaths: string[];
  requiredPatterns: string[];
  reanchorFiles: string[];
  readOnlyBashAllow: string[];
};

/** The 12 pattern names, as they appear in the kit's AGENTS.md (CHECKLIST.md appendix). */
export const FORBIDDEN_PATTERNS = [
  "gate self-weakening",
  "proof-class inflation",
  "golden regeneration reflex",
  "commit-stream pumping",
  "tautological tests",
  "easy-lever cherry-picking",
  "close-pump abuse",
  "scope-splitting",
  "spec-editing as progress",
  "conformance metastasis",
  "dependency smuggling",
  "bench-path hardcoding",
] as const;

/** Throw unless the unknown JSON value is a usable guard config. */
export function validateGuardConfig(obj: unknown): GuardConfig {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) {
    throw new Error(`kit-guard: invalid ${CONFIG_REL_PATH}: root must be an object`);
  }
  const c = obj as Record<string, unknown>;
  if (typeof c.hookDir !== "string" || c.hookDir.length === 0) {
    throw new Error(`kit-guard: invalid ${CONFIG_REL_PATH}: hookDir must be a non-empty string`);
  }
  if (!Array.isArray(c.gatePaths) || c.gatePaths.length === 0 || !c.gatePaths.every(p => typeof p === "string" && (p as string).length > 0)) {
    throw new Error(`kit-guard: invalid ${CONFIG_REL_PATH}: gatePaths must be a non-empty string array`);
  }
  const gates = c.gatePaths as string[];
  if (!gates.some(p => p === CONFIG_REL_PATH || p.endsWith("/kit-guard.json") || p === "kit-guard.json")) {
    throw new Error(
      `kit-guard: invalid ${CONFIG_REL_PATH}: gatePaths must list its own path (${CONFIG_REL_PATH}); otherwise an agent can widen its own allowlist`,
    );
  }
  if (!Array.isArray(c.requiredPatterns) || c.requiredPatterns.length === 0) {
    throw new Error(`kit-guard: invalid ${CONFIG_REL_PATH}: requiredPatterns must be a non-empty string array`);
  }
  const required = c.requiredPatterns as string[];
  const missing = (FORBIDDEN_PATTERNS as readonly string[]).filter(p => !required.includes(p));
  if (missing.length > 0) {
    throw new Error(
      `kit-guard: invalid ${CONFIG_REL_PATH}: requiredPatterns must contain all 12 forbidden patterns; missing: ${missing.join(", ")}`,
    );
  }
  if (!Array.isArray(c.reanchorFiles) || c.reanchorFiles.length === 0) {
    throw new Error(`kit-guard: invalid ${CONFIG_REL_PATH}: reanchorFiles must be a non-empty string array`);
  }
  if (!Array.isArray(c.readOnlyBashAllow) || c.readOnlyBashAllow.length === 0) {
    throw new Error(`kit-guard: invalid ${CONFIG_REL_PATH}: readOnlyBashAllow must be a non-empty string array`);
  }
  return {
    hookDir: c.hookDir as string,
    gatePaths: gates.slice(),
    requiredPatterns: (c.requiredPatterns as string[]).slice(),
    reanchorFiles: (c.reanchorFiles as string[]).slice(),
    readOnlyBashAllow: (c.readOnlyBashAllow as string[]).slice(),
  };
}

/** Walk up from startDir until .omp/kit-guard.json is found; read, parse, validate. */
export function loadGuardConfig(startDir: string = process.cwd()): GuardConfig {
  let dir = startDir;
  for (;;) {
    const candidate = join(dir, CONFIG_REL_PATH);
    if (existsSync(candidate)) {
      let raw: string;
      try {
        raw = readFileSync(candidate, "utf8");
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        throw new Error(`kit-guard: cannot read ${candidate}: ${msg}`);
      }
      let parsed: unknown;
      try {
        parsed = JSON.parse(raw);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        throw new Error(`kit-guard: malformed ${candidate}: ${msg}`);
      }
      try {
        return validateGuardConfig(parsed);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        throw new Error(`kit-guard: malformed ${candidate}: ${msg}`);
      }
    }
    const up = dirname(dir);
    if (up === dir) throw new Error(`kit-guard: missing ${CONFIG_REL_PATH} (searched up from ${startDir})`);
    dir = up;
  }
}

/** Resolve an optional config argument; throw when there is nothing usable. */
function mustConfig(cfg?: GuardConfig | unknown): GuardConfig {
  if (cfg !== undefined && cfg !== null) return validateGuardConfig(cfg);
  return loadGuardConfig();
}

/** Fail-closed wrapper: a missing or malformed config blocks with the reason. */
function configOrBlock(cfg?: GuardConfig | unknown): { ok: true; cfg: GuardConfig } | { ok: false; reason: string } {
  try {
    return { ok: true, cfg: mustConfig(cfg) };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return { ok: false, reason: `${msg}. Refusing to allow (fail-closed). A human with KIT_GATE_EDIT=1 must restore it.` };
  }
}

function normalizePath(p: string): string {
  let s = p.replace(/\\/g, "/").trim();
  s = s.replace(/^\.\/+/, "");
  s = s.replace(/^\/+/, "");
  s = s.replace(/^["']+|["';,]+$/g, "");
  return s;
}

function escapeRegExp(s: string): string {
  return s.replace(/[+?^${}()|[\]\\.:]/g, "\\$&");
}

/** Convert one gate glob (`*` = one level, trailing `/*` = any depth) to a regex. */
function globToRegExp(glob: string): RegExp {
  const n = normalizePath(glob);
  if (n.endsWith("/*")) {
    const prefix = escapeRegExp(n.slice(0, -2)).replace(/\\\*/g, "[^/]*");
    return new RegExp(`(^|/)${prefix}/.*$`);
  }
  let body = "";
  for (let i = 0; i < n.length; i++) {
    const ch = n[i];
    if (ch === "*") {
      if (n[i + 1] === "*") {
        body += ".*";
        i++;
      } else {
        body += "[^/]*";
      }
    } else if ("+?^${}()|[]\\.".includes(ch)) {
      body += `\\${ch}`;
    } else {
      body += ch;
    }
  }
  return new RegExp(`(^|/)${body}$`);
}

/** True when the tool-call path targets a gate file under the loaded config. */
export function gatePathMatches(path: string, cfg: GuardConfig): boolean {
  const n = normalizePath(path);
  if (!n) return false;
  return cfg.gatePaths.some(pat => {
    try {
      return globToRegExp(pat).test(n);
    } catch {
      return false;
    }
  });
}

/** Remove single- and double-quoted spans so flags inside `-m "…"` do not match. */
export function stripQuotes(s: string): string {
  return s.replace(/"([^"\\]|\\.)*"/g, " ").replace(/'([^'\\]|\\.)*'/g, " ");
}

/** True when the command actually re-points the hook pointer (not a read). */
function isHookPointerWrite(command: string): boolean {
  if (/-c\s*core\.hooksPath/.test(command)) return true;
  const segments = command.split(/[\n;&|]+/);
  for (const seg of segments) {
    if (!/\bgit\s+config\b/.test(seg) || !/core\.hooksPath/.test(seg)) continue;
    if (/(^|[\s=])--(get|list|get-all|get-regexp)\b/.test(seg)) continue;
    return true;
  }
  return false;
}

/**
 * True when the command mentions the hook pointer only as an allowlisted read
 * (e.g. `git config --get` / `--list`). A write segment never qualifies.
 */
export function isReadOnlyBash(command: string, cfg: GuardConfig): boolean {
  if (!/hooksPath/.test(command)) return false;
  if (isHookPointerWrite(command)) return false;
  return cfg.readOnlyBashAllow.some(a => command.includes(a));
}

function hookDirAlternatives(hookDir: string): string {
  const h = escapeRegExp(normalizePath(hookDir)).replace(/\\\*/g, "[^/]*");
  return `(\\.git\\/hooks\\/|\\.githooks\\/|${h}\\/)`;
}

export function bashVerdict(command: string, cfg?: GuardConfig | unknown): Verdict {
  const r = configOrBlock(cfg);
  if (!r.ok) return { block: true, reason: r.reason };
  const stripped = stripQuotes(command);

  if (/\bgit\s+commit\b/.test(stripped) && /(^|\s)--no-verify\b/.test(stripped)) {
    return {
      block: true,
      reason:
        "kit-guard B5: `git commit --no-verify` bypasses the pre-commit honesty gate. Read the hook's stderr, fix the cause, and commit normally.",
    };
  }
  if (/\bgit\s+commit\b/.test(stripped) && /\s-[a-zA-Z]*n[a-zA-Z]*\b/.test(stripped)) {
    // The -n short flag, outside quotes (stripQuotes already removed -m "…").
    // `git push -n` is a dry run and stays allowed; only commit -n bypasses the hook.
    return {
      block: true,
      reason:
        "kit-guard B5: `git commit -n` bypasses the pre-commit honesty gate. Read the hook's stderr, fix the cause, and commit normally.",
    };
  }
  if (/\bgit\s+push\b/.test(stripped) && /(^|\s)--no-verify\b/.test(stripped)) {
    return { block: true, reason: "kit-guard B5: `git push --no-verify` bypasses the gates. Push normally." };
  }

  if (isHookPointerWrite(command)) {
    return {
      block: true,
      reason: "kit-guard B5: re-pointing core.hooksPath disables the honesty gate. Hook paths are owned by the repo checkout.",
    };
  }

  const hookAlt = hookDirAlternatives(r.cfg.hookDir);
  if (new RegExp(`\\b(rm|mv|chmod|truncate|unlink)\\b[^\\n;&|]*${hookAlt}`).test(command)) {
    return { block: true, reason: "kit-guard B5: removing, moving, or chmod-ing the hook disables the honesty gate." };
  }

  if (/(^|[\s;&|])(>|>>|\btee\b)\s*[^\n;&|]*/.test(command)) {
    // Extract redirection / tee targets and test each against the gate set.
    const targets: string[] = [];
    const re1 = />\s*([^\s;&|]+)/g;
    const re2 = /\btee\b\s*((?:-[a-zA-Z]+\s+)*)([^\s;&|]+)/g;
    let m: RegExpExecArray | null;
    while ((m = re1.exec(command)) !== null) targets.push(m[1]);
    while ((m = re2.exec(command)) !== null) targets.push(m[2]);
    for (const t of targets) {
      if (gatePathMatches(t, r.cfg) || new RegExp(`(^|/)${hookAlt}`).test(normalizePath(t))) {
        return {
          block: true,
          reason: "kit-guard B7: shell redirection into a gate file is a gate edit. Gate changes need a human and two-direction evidence.",
        };
      }
    }
  }

  return null;
}

export function pathVerdict(path: string, allowGateEdit: boolean, cfg?: GuardConfig | unknown): Verdict {
  const r = configOrBlock(cfg);
  if (!r.ok) return { block: true, reason: r.reason };
  if (allowGateEdit) return null;
  if (gatePathMatches(path, r.cfg)) {
    return {
      block: true,
      reason:
        `kit-guard B7: ${path} is a gate or reference file. Agents never weaken a gate to land a change. ` +
        "If the gate is wrong, file a bead with the false rejection (command + output) and a case that must stay rejected; a human re-launches with KIT_GATE_EDIT=1 to change it.",
    };
  }
  return null;
}

export function missingPatterns(agentsMd: string, cfg?: GuardConfig | unknown): string[] {
  let required: readonly string[] = FORBIDDEN_PATTERNS;
  try {
    required = mustConfig(cfg).requiredPatterns;
  } catch {
    required = FORBIDDEN_PATTERNS;
  }
  const lower = agentsMd.toLowerCase();
  return (required as readonly string[]).filter(p => !lower.includes(p.toLowerCase()));
}

/** Paths an edit/write tool call targets. Handles `path` and multi-edit `edits[].path`. */
export function targetPaths(input: Record<string, unknown>): string[] {
  const out: string[] = [];
  if (typeof input.path === "string") out.push(input.path);
  if (Array.isArray(input.edits)) {
    for (const e of input.edits) {
      if (e && typeof e === "object" && "path" in e && typeof e.path === "string") out.push(e.path);
    }
  }
  return out;
}

export function buildReanchorMessage(cfg: GuardConfig): string {
  return (
    "kit-guard: context was just compacted. The summary is not evidence. Before your next action: " +
    `(1) re-read ${cfg.reanchorFiles.join(", ")} with the read tool; ` +
    "(2) re-read your current bead (br show <id>, or its line in .beads/issues.jsonl) and its acceptance criteria; " +
    "(3) re-run the gates you last relied on instead of trusting remembered results."
  );
}

export const REANCHOR_AFTER_COMPACTION =
  "kit-guard: context was just compacted. The summary is not evidence. Before your next action: " +
  "(1) re-read AGENTS.md, GATES.md, .beads/issues.jsonl with the read tool; " +
  "(2) re-read your current bead (br show <id>, or its line in .beads/issues.jsonl) and its acceptance criteria; " +
  "(3) re-run the gates you last relied on instead of trusting remembered results.";

export function agentsChangedMessage(mtimeIso: string): string {
  return (
    `kit-guard: AGENTS.md changed on disk at ${mtimeIso}, after this session loaded it. ` +
    "Your system prompt holds the old copy. Read AGENTS.md with the read tool now and follow the new version."
  );
}
