/**
 * omp-guard-rule — observe-only epistemic-correctness scorer for bash tool calls.
 *
 * Four classes, copied VERBATIM from work/guardpack/install-guardpack.sh's tier-1
 * hook (the `case "$cmd" in` patterns). Verify: the class predicates below must
 * match the hook's globs — any drift between hook and extension is a defect.
 *
 * AXIS, stated so it is never merged: harm-rule asks "will this break the
 * machine?" (destructive shape). This asks "will this make you believe
 * something false?" (epistemic correctness). Folding them would destroy the
 * distinction (measurement-premortem-20260920.md, NARROW verdict).
 *
 * OBSERVE-ONLY, NEVER BLOCKS. Every path returns undefined (including errors).
 * A diagnostic row fires on EVERY tool_call so "loaded but no match" is
 * distinguishable from "never fired". guard_error exists from day one:
 * harm-rule shipped without it and a crash scored as pass.
 */
const DECISION_TYPE = 'com.zeststream.omp-guard-rule.decision.v1';
const DIAG_TYPE = 'com.zeststream.omp-guard-rule.diagnostic.v1';

export function classify(command) {
  // pipe-exit DROPPED under R51 (55.2% fire rate is wallpaper; detects the
  // precondition, not the defect). Do not re-add by pattern-matching.
  if (command.includes('git add -A') || command.includes('git add .')) return { cls: 'stage-all' };
  if (command.includes('git commit') && command.includes('-m') && command.includes('`')) return { cls: 'commit-backtick' };
  if (command.includes('grep -c') || command.includes('grep -q')) return { cls: 'grep-as-proof' };
  return { cls: null };
}

export default function guardRule(pi, deps = {}) {
  // Testability seam ONLY: production always uses the frozen classify above.
  const classifyFn = deps.classify ?? classify;
  pi.on('tool_call', async (event, ctx) => {
    try {
      const toolName = event?.toolName ?? event?.name;
      const command = event?.input?.command ?? event?.command ?? event?.input?.cmd;
      try {
        await pi.appendEntry(DIAG_TYPE, {
          kind: 'tool_call_observed',
          toolName: String(toolName),
          toolCallId: event?.toolCallId ?? null,
          timestamp: new Date().toISOString(),
        });
      } catch { /* observability must never break the session */ }
      if (toolName !== 'bash' || typeof command !== 'string' || command.length === 0) {
        return undefined;
      }
      let cls = null;
      let error = null;
      try {
        cls = classifyFn(command).cls;
      } catch (err) {
        error = String(err);
      }
      // A failed classification is not a pass: the row carries guard_error,
      // which no pass/fire count absorbs.
      const record = error
        ? { kind: 'guard_error' }
        : cls
          ? { kind: 'guard_fire', class: cls }
          : { kind: 'guard_pass' };
      try {
        await pi.appendEntry(DECISION_TYPE, {
          ...record,
          command: command.slice(0, 2000),
          toolCallId: event?.toolCallId ?? null,
          error,
          model: 'none-deterministic-regex-guard-v1',
          timestamp: new Date().toISOString(),
        });
      } catch { /* observability must never break the session */ }
      return undefined;
    } catch {
      return undefined;
    }
  });
}
