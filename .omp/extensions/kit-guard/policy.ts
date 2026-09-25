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
import { basename, dirname, join } from "node:path";

export type Verdict = { block: true; reason: string } | null;

export const CONFIG_REL_PATH = ".omp/kit-guard.json";

export type GuardConfig = {
  hookDir: string;
  gatePaths: string[];
  requiredPatterns: string[];
  reanchorFiles: string[];
  /** Retained config contract; read operations are now recognized structurally. */
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

type ShellWord = { value: string; operator: boolean; quoted: boolean; heredoc?: string };
type ShellCommand = { tokens: ShellWord[]; depth: number };
type ShellAnalysis =
  | { ok: true; commands: ShellCommand[] }
  | { ok: false; verdict: NonNullable<Verdict> };
const MAX_ANALYSIS_DEPTH = 64;

/**
 * Lex literal shell words, not substrings of documentation. Quoting removes syntax,
 * not argument values. Substitutions execute even in double quotes. Quoted heredocs
 * are data to the parent, but can be executable stdin for a child shell. This is not
 * an evaluator: aliases, variable-built commands and arbitrary interpreters are out of scope.
 */
function shellCommands(source: string, initialDepth: number): ShellAnalysis {
  const commands: ShellCommand[] = [];
  let i = 0;
  let depth = initialDepth;
  let exhausted = false;

  function substitution(): boolean {
    if (source.startsWith("$(", i) || source.startsWith("<(", i) || source.startsWith(">(", i)) {
      i += 2;
      depth++;
      scan(")");
      depth--;
      return true;
    }
    if (source[i] === "`") {
      i++;
      depth++;
      scan("`");
      depth--;
      return true;
    }
    return false;
  }

  function word(end?: string): ShellWord {
    let value = "";
    let quoted = false;
    let quote = "";
    while (i < source.length) {
      const ch = source[i];
      if (!quote && end && ch === end) break;
      if (quote === "'") {
        i++;
        if (ch === "'") quote = "";
        else value += ch;
        continue;
      }
      if (ch === "\\" && (!quote || /[$`"\\\n]/.test(source[i + 1] ?? ""))) {
        quoted = true;
        i++;
        if (source[i] !== "\n") value += source[i] ?? "";
        i++;
        continue;
      }
      if (ch === quote) {
        quote = "";
        i++;
        continue;
      }
      if (!quote && (ch === "'" || ch === '"')) {
        quote = ch;
        quoted = true;
        i++;
        continue;
      }
      // Process substitution is syntax only outside quotes.
      if ((ch === "$" || ch === "`" || (!quote && (ch === "<" || ch === ">"))) && substitution()) {
        value += "\0"; // output is unknown; never pretend it is a literal argv value
        continue;
      }
      if (!quote && /[\s;&|()<>{}]/.test(ch)) break;
      value += ch;
      i++;
    }
    return { value, quoted, operator: false };
  }

  function scan(end?: string) {
    // One depth budget covers substitutions and the shell -c bodies they invoke.
    if (depth >= MAX_ANALYSIS_DEPTH) {
      exhausted = true;
      i = source.length;
      return;
    }
    let current: ShellWord[] = [];
    const heredocs: { delimiter: string; quoted: boolean; tabs: boolean; target: ShellWord }[] = [];
    const flush = () => {
      if (current.length) commands.push({ tokens: current, depth });
      current = [];
    };
    while (i < source.length) {
      const ch = source[i];
      if (end && ch === end) {
        i++;
        flush();
        return;
      }
      if (ch === "#" && (i === 0 || /[\s;&|()]/.test(source[i - 1]))) {
        while (i < source.length && source[i] !== "\n") i++;
        continue;
      }
      if (ch === "\n") {
        i++;
        flush();
        for (const doc of heredocs.splice(0)) {
          let body = "";
          while (i < source.length) {
            const stop = source.indexOf("\n", i);
            const lineEnd = stop === -1 ? source.length : stop;
            const line = source.slice(i, lineEnd);
            if ((doc.tabs ? line.replace(/^\t+/, "") : line) === doc.delimiter) {
              i = Math.min(lineEnd + 1, source.length);
              break;
            }
            if (doc.tabs) while (source[i] === "\t") i++;
            if (doc.quoted) {
              body += source.slice(i, lineEnd);
              i = lineEnd;
            } else {
              while (i < lineEnd) {
                if (source[i] === "\\" && /[$`\\\n]/.test(source[i + 1] ?? "")) {
                  if (source[i + 1] !== "\n") body += source[i + 1];
                  i += 2;
                } else if ((source[i] === "$" || source[i] === "`") && substitution()) {
                  body += "\0"; // parent expansion output is not a known literal
                } else body += source[i++];
              }
            }
            if (source[i] === "\n") { body += "\n"; i++; }
          }
          doc.target.heredoc = body;
        }
        continue;
      }
      if (/\s/.test(ch)) { i++; continue; }
      if (";&|(){}".includes(ch)) { i++; flush(); continue; }
      if ((ch === "<" || ch === ">") && source[i + 1] !== "(") {
        const op = /^(?:<<<|<<-|<<|>>|<>|>&|<&|>\||[<>])/.exec(source.slice(i))![0];
        current.push({ value: op, operator: true, quoted: false });
        i += op.length;
        while (source[i] === " " || source[i] === "\t") i++;
        if (i < source.length && !/[\n;&|]/.test(source[i])) {
          const target = word(end);
          current.push(target);
          if (op === "<<" || op === "<<-") {
            heredocs.push({ delimiter: target.value, quoted: target.quoted, tabs: op === "<<-", target });
          }
        }
        continue;
      }
      current.push(word(end));
    }
    flush();
  }

  scan();
  return exhausted
    ? { ok: false, verdict: { block: true, reason: "kit-guard: shell analysis nesting limit exceeded. Refusing to allow (fail-closed)." } }
    : { ok: true, commands };
}

const assignment = /^[A-Za-z_][A-Za-z0-9_]*=/;
const hookKey = /^core\.hookspath(?:=|$)/i;

/** Unwrap common direct-execution prefixes without treating arbitrary arguments as code. */
function executable(words: string[]): { args: string[]; environment: string[] } {
  let i = 0;
  const environment: string[] = [];
  while (i < words.length) {
    if (assignment.test(words[i])) { environment.push(words[i++]); continue; }
    const name = basename(words[i]);
    if (["if", "then", "elif", "else", "do", "!", "command", "exec", "builtin"].includes(name)) {
      i++;
      if (words[i] === "--") i++;
      continue;
    }
    if (name === "env") {
      i++;
      while (i < words.length) {
        if (assignment.test(words[i])) environment.push(words[i++]);
        else if (words[i] === "-u" || words[i] === "--unset" || words[i] === "-C" || words[i] === "--chdir") i += 2;
        else if (words[i].startsWith("-")) i++;
        else break;
      }
      continue;
    }
    break;
  }
  return { args: words.slice(i), environment };
}

function bypassFlag(args: string[], commit: boolean): boolean {
  const longValues = ["--message", "--file", "--reuse-message", "--reedit-message", "--template",
    "--author", "--date", "--fixup", "--squash", "--trailer", "--cleanup", "--pathspec-from-file",
    "--repo", "--receive-pack", "--exec", "--push-option"];
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--") break;
    if (arg.startsWith("--no-v") && "--no-verify".startsWith(arg)) return true;
    if (longValues.includes(arg)) { i++; continue; }
    if (arg.startsWith("--")) continue;
    if (arg.startsWith("-")) {
      for (let j = 1; j < arg.length; j++) {
        if (commit && arg[j] === "n") return true;
        if ((commit ? "mFCct" : "o").includes(arg[j])) {
          if (j === arg.length - 1) i++;
          break;
        }
      }
    }
  }
  return false;
}

function gitHookMutation(args: string[], environment: string[]): boolean {
  if (environment.some(v => /^GIT_CONFIG_KEY_\d+=core\.hookspath$/i.test(v))) return true;
  let i = 1;
  while (i < args.length && args[i].startsWith("-")) {
    const arg = args[i++];
    if (arg === "-c" || arg === "--config-env") {
      if (hookKey.test(args[i] ?? "")) return true;
      i++;
    } else if (arg.startsWith("-c") && hookKey.test(arg.slice(2))) return true;
    else if (arg.startsWith("--config-env=") && hookKey.test(arg.slice(13))) return true;
    else if (["-C", "--git-dir", "--work-tree", "--namespace"].includes(arg)) i++;
  }
  const subcommand = args[i++];
  const rest = args.slice(i);
  if ((subcommand === "commit" || subcommand === "push") && bypassFlag(rest, subcommand === "commit")) return true;
  if (subcommand !== "config") return false;
  const positional: string[] = [];
  let read = false;
  let write = false;
  for (let j = 0; j < rest.length; j++) {
    const arg = rest[j];
    if (["--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "--show-origin", "--show-scope"].includes(arg)) {
      if (arg !== "--show-origin" && arg !== "--show-scope") read = true;
    } else if (["--unset", "--unset-all", "--add", "--replace-all", "--rename-section", "--remove-section"].includes(arg)) write = true;
    else if (["--file", "-f", "--type", "-t", "--default"].includes(arg)) j++;
    else if (!arg.startsWith("-")) positional.push(arg);
  }
  if (["get", "list"].includes(positional[0])) read = true;
  if (["set", "unset", "rename-section", "remove-section"].includes(positional[0])) write = true;
  if (!positional.some(v => hookKey.test(v))) return false;
  return write || (!read && positional.length > 1);
}

function protectedSetting(id: string): boolean {
  const parts = id.toLowerCase().replace(/^cfg:\/\//, "").split(/[/.]/);
  if (parts.at(-1) === "save") parts.pop();
  return ["ttsr", "disabledproviders", "enabledproviders", "discovery", "extensions", "disabledextensions"].includes(parts[0]);
}

// Global config.yml remains outside this path-only guard: blocking whole YAML files
// would also block unrelated model-role edits. cfg:// provides the actual setting id.

function hookPath(path: string, cfg: GuardConfig): boolean {
  const n = normalizePath(path);
  return [".git/hooks", ".githooks", normalizePath(cfg.hookDir)].some(dir =>
    n === dir || n.endsWith(`/${dir}`) || n.startsWith(`${dir}/`) || n.includes(`/${dir}/`));
}

/** A script filename or -c consumes code elsewhere; -s explicitly selects stdin. */
function shellReadsStdin(args: string[]): boolean {
  let stdin = false;
  let noExec = false;
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--") return !noExec && (stdin || i === args.length - 1);
    if (["-o", "+o", "-O", "+O"].includes(arg)) {
      if (args[i + 1] === "noexec") noExec = arg.startsWith("-");
      i++;
    } else if (/^[-+][a-zA-Z]+$/.test(arg)) {
      if (arg.includes("n")) noExec = arg.startsWith("-");
      if (arg.startsWith("-") && arg.includes("s")) stdin = true;
    } else if (!arg.startsWith("-")) return !noExec && stdin;
  }
  return !noExec;
}

/** Third parameter is process-owned B7 authorization; B5 never consults it. */
export function bashVerdict(command: string, cfg?: GuardConfig | unknown, allowGateEdit = false): Verdict {
  const r = configOrBlock(cfg);
  if (!r.ok) return { block: true, reason: r.reason };
  return analyzeShell(command, r.cfg, allowGateEdit, 0);
}

function analyzeShell(command: string, cfg: GuardConfig, allowGateEdit: boolean, depth: number): Verdict {
  const analysis = shellCommands(command, depth);
  if (!analysis.ok) return analysis.verdict;
  for (const { tokens, depth: commandDepth } of analysis.commands) {
    const words: string[] = [];
    const outputs: string[] = [];
    let stdinScript: string | undefined;
    for (let i = 0; i < tokens.length; i++) {
      if (tokens[i].operator) {
        if (tokens[i].value.includes(">") && tokens[i + 1]) outputs.push(tokens[i + 1].value);
        if (tokens[i].value.startsWith("<")) stdinScript = tokens[i + 1]?.heredoc;
        i++; // a redirection target is not argv
      } else words.push(tokens[i].value);
    }
    const { args, environment } = executable(words);
    const name = basename(args[0] ?? "");
    if (name === "git" && gitHookMutation(args, environment)) {
      return { block: true, reason: "kit-guard B5: bypassing hooks or re-pointing core.hooksPath disables the honesty gate. Fix the hook's reported cause and run git normally." };
    }
    if (["rm", "mv", "chmod", "truncate", "unlink"].includes(name) && args.slice(1).some(p => hookPath(p, cfg))) {
      return { block: true, reason: "kit-guard B5: removing, moving, or chmod-ing the hook disables the honesty gate." };
    }
    if (["bash", "sh", "zsh", "dash", "ksh"].includes(name)) {
      const flag = args.findIndex((v, i) => i > 0 && /^-[a-z]*c[a-z]*$/.test(v));
      if (flag !== -1 && args[flag + 1]) {
        const verdict = analyzeShell(args[flag + 1], cfg, allowGateEdit, commandDepth + 1);
        if (verdict) return verdict;
      } else if (stdinScript !== undefined && shellReadsStdin(args)) {
        const verdict = analyzeShell(stdinScript, cfg, allowGateEdit, commandDepth + 1);
        if (verdict) return verdict;
      }
    }
    if (!allowGateEdit && name === "omp") {
      let i = 1;
      while (i < args.length && args[i].startsWith("-")) {
        if (args[i] === "--profile") i += 2;
        else i++;
      }
      if (args[i] === "config" && ["set", "reset", "unset"].includes(args[i + 1]) && protectedSetting(args[i + 2] ?? "")) {
        // HOME prefixes alone prove neither the effective profile nor filesystem isolation.
        return { block: true, reason: "kit-guard B7: changing rule-engine, discovery, or extension settings can disable the guards. A human must authorize this session with KIT_GATE_EDIT=1." };
      }
    }
    if (name === "tee") outputs.push(...args.slice(1).filter(v => !v.startsWith("-")));
    for (const path of outputs) {
      const verdict = pathVerdict(path, allowGateEdit, cfg);
      if (verdict) return verdict;
      if (!allowGateEdit && hookPath(path, cfg)) {
        return { block: true, reason: "kit-guard B7: shell redirection into a hook file requires a human-authorized gate-edit session." };
      }
    }
  }
  return null;
}

export function pathVerdict(path: string, allowGateEdit: boolean, cfg?: GuardConfig | unknown): Verdict {
  const r = configOrBlock(cfg);
  if (!r.ok) return { block: true, reason: r.reason };
  if (allowGateEdit) return null;
  if (gatePathMatches(path, r.cfg) || (/^cfg:\/\//i.test(path) && protectedSetting(path))) {
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
