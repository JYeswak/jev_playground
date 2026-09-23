/**
 * kit-guard policy: pure functions, no omp imports, so they can be unit-tested.
 *
 * Turns three FrankenSuite-kit rules that the 44-repo synthesis found were
 * enforced only by "agent obedience" (execution-readiness.md, Gate 18) into
 * hard blocks at the tool boundary:
 *   - B5 / pattern 1: never bypass or re-point the pre-commit honesty gate
 *   - B7 / pattern 1: never edit a gate to land a change (gate files are read-only
 *     to agents unless a human launched the session with KIT_GATE_EDIT=1)
 *   - A9: the 12 forbidden patterns stay verbatim in AGENTS.md
 */

export type Verdict = { block: true; reason: string } | null;

const BASH_RULES: { re: RegExp; reason: string }[] = [
  {
    re: /\bgit\s+commit\b[^\n;&|]*(--no-verify|\s-[a-zA-Z]*n[a-zA-Z]*\b)/,
    reason:
      "kit-guard B5: `git commit --no-verify`/`-n` bypasses the pre-commit honesty gate. Read the hook's stderr, fix the cause, and commit normally.",
  },
  {
    re: /\bgit\s+push\b[^\n;&|]*--no-verify/,
    reason: "kit-guard B5: `git push --no-verify` bypasses the gates. Push normally.",
  },
  {
    re: /core\.hooksPath/,
    reason: "kit-guard B5: re-pointing core.hooksPath disables the honesty gate. Hook paths are owned by scripts/init.sh.",
  },
  {
    re: /\b(rm|mv|chmod|truncate|unlink)\b[^\n;&|]*(\.git\/hooks\/|\.githooks\/)/,
    reason: "kit-guard B5: removing, moving, or chmod-ing the hook disables the honesty gate.",
  },
  {
    re: /(>|>>|\btee\b)\s*[^\n;&|]*(\.git\/hooks\/|\.githooks\/|scripts\/check-[\w.-]+\.sh|kit-gates\.yml)/,
    reason: "kit-guard B7: shell redirection into a gate file is a gate edit. Gate changes need a human and two-direction evidence.",
  },
];

export function bashVerdict(command: string): Verdict {
  for (const r of BASH_RULES) if (r.re.test(command)) return { block: true, reason: r.reason };
  return null;
}

const GATE_PATHS: RegExp[] = [
  /(^|\/)scripts\/check-[\w.-]+\.sh$/,
  /(^|\/)\.githooks\//,
  /(^|\/)\.git\/hooks\//,
  /(^|\/)\.github\/workflows\/kit-gates\.yml$/,
  /(^|\/)templates\//, // read-only reference copies (kit README: "edit the installed copies, never these")
  // This repo's gates are not under scripts/check-*.sh. Without these, the
  // guard would lock the kit's paths and leave the live checkers writable.
  /(^|\/)foundation\/kit\/check-[\w.-]+\.sh$/,
  /(^|\/)foundation\/gates\.d\/[0-9].*\.sh$/,
];

export function pathVerdict(path: string, allowGateEdit: boolean): Verdict {
  const p = path.replace(/\\/g, "/");
  if (allowGateEdit) return null;
  if (GATE_PATHS.some(re => re.test(p))) {
    return {
      block: true,
      reason:
        `kit-guard B7: ${path} is a gate or reference file. Agents never weaken a gate to land a change. ` +
        "If the gate is wrong, file a bead with the false rejection (command + output) and a case that must stay rejected; a human re-launches with KIT_GATE_EDIT=1 to change it.",
    };
  }
  return null;
}

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

export function missingPatterns(agentsMd: string): string[] {
  const lower = agentsMd.toLowerCase();
  return FORBIDDEN_PATTERNS.filter(p => !lower.includes(p));
}

/** Paths an edit/write tool call targets. Handles `path` and multi-edit `edits[].path`. */
export function targetPaths(input: Record<string, unknown>): string[] {
  const out: string[] = [];
  if (typeof input.path === "string") out.push(input.path);
  if (Array.isArray(input.edits))
    for (const e of input.edits) if (e && typeof (e as { path?: unknown }).path === "string") out.push((e as { path: string }).path);
  return out;
}

export const REANCHOR_AFTER_COMPACTION =
  "kit-guard: context was just compacted. The summary is not evidence. Before your next action: " +
  "(1) re-read AGENTS.md and docs/definition-of-done.md with the read tool; " +
  "(2) re-read your current bead (br show <id>, or its line in .beads/issues.jsonl) and its acceptance criteria; " +
  "(3) re-run the gates you last relied on instead of trusting remembered results.";

export function agentsChangedMessage(mtimeIso: string): string {
  return (
    `kit-guard: AGENTS.md changed on disk at ${mtimeIso}, after this session loaded it. ` +
    "Your system prompt holds the old copy. Read AGENTS.md with the read tool now and follow the new version."
  );
}
