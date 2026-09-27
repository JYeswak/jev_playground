# Private facts packet: omp #13303 and #13316

Prepared for Josh; no upstream write performed.

## Source and dedup

- Repository: `can1357/oh-my-pi`
- Skill read first: `/Users/josh/.claude/skills/zeststream-pr/SKILL.md`.
- Read-only commands run: `gh issue view 13303`, `gh issue view 13316`, `gh pr list --state all --search "13303 OR 13316" --limit 100`, `gh release list --limit 10`, `gh pr view` for each PR, and the comments API for each PR.
- Dedup result: both issue numbers are open PRs, not separate issue-only work. `gh pr list` returned exactly 2 matching PRs; the release list was not capped (10 requested, 9 returned).
- Latest release observed: `v18.3.2`, published 2026-09-26T00:00:25Z.

## #13303 — AST-conditioned TTSR before tool execution

- URL: https://github.com/can1357/oh-my-pi/pull/13303
- State: OPEN, non-draft.
- Head: `JYeswak:fix/astcondition-before-tool-execution`, commit `876af5084f1bdfc11410c2ad4426a0e5cab0ac20`; base `main`.
- Mergeability: `CONFLICTING`; merge state `DIRTY`.
- Review/check status: no required checks were returned by the API; `reviewDecision` is empty. The only PR comment is the Codex bot's rate-limit notice: code review credits are exhausted.
- Changed files: 6. Production: `packages/coding-agent/src/session/agent-session.ts` (+2/0), `packages/coding-agent/src/session/ttsr-coordinator.ts` (+19/-11). Tests: `agent-session-concurrent.test.ts` (+100/-1), `ttsr-coordinator-buffer.test.ts` (0/-51). Docs/changelog: `docs/ttsr-injection-lifecycle.md`, `packages/coding-agent/CHANGELOG.md`.
- What it changes: moves AST-conditioned TTSR evaluation onto finalized, validated tool arguments in the pre-execution hook, so interrupting matches block `write`/`edit` before disk execution. It removes the racy listener-side AST check and its obsolete location-pinning test while preserving the existing injection/retry path and non-interrupting `never` reminders.
- Why: the streaming event emitter does not await asynchronous listeners; the old listener-side check could let a violating write/edit hit disk before the interrupt.

## #13316 — TTSR on eval-bridged tool calls

- URL: https://github.com/can1357/oh-my-pi/pull/13316
- State: OPEN, non-draft.
- Head: `JYeswak:fix/ttsr-eval-bridged-tool-calls`, commit `51cf4bbe936f49e7d67a9d6aea5f2dc7226ad673`; base `main`.
- Dependency: the PR body says it builds on #13303; its commit list contains #13303's `876af508` followed by `51cf4bbe`.
- Mergeability: `CONFLICTING`; merge state `DIRTY`.
- Review/check status: no required checks were returned by the API; `reviewDecision` is empty. The only PR comment is the same Codex bot rate-limit notice.
- Changed files: 12. Production: `packages/coding-agent/src/export/ttsr.ts` (+11/0), `packages/coding-agent/src/extensibility/extensions/runner.ts` (+61/0), `packages/coding-agent/src/extensibility/extensions/wrapper.ts` (+35/-1), `packages/coding-agent/src/session/agent-session.ts` (+27/-9), `packages/coding-agent/src/session/ttsr-coordinator.ts` (+79/-17). Tests: `agent-session-concurrent.test.ts` (+300/-1), `extensions-runner.test.ts` (+56/0), `ttsr-coordinator-buffer.test.ts` (0/-51), `ttsr-eval-bridge.test.ts` (+155/0), `ttsr-eval-near-miss.test.ts` (+139/0). Docs/changelog: `docs/ttsr-injection-lifecycle.md`, `packages/coding-agent/CHANGELOG.md`.
- What it changes: applies the finalized inner `AgentTool` call at the eval wrapper boundary, covering `tool.write`, `tool.edit`, and related eval-bridge calls that previously went directly to `tool.execute()` and skipped tool-scoped TTSR regex/AST rules.
- Why: eval-bridge writes could bypass the TTSR rule path. The patch claims to preserve direct dispatch, nested `xd://` behavior, approval ordering, extension-hook ordering, and prelude semantics.

## Relationship and current action

#13303 is the base behavioral fix; #13316 is the dependent eval-bridge coverage. Both are currently dirty/conflicting, so neither is merge-ready from the observed GitHub state. #13316 should be reconciled after #13303's base is resolved, not independently nudged as if it were standalone.

The Codex review bot has not produced a code review because its credits are exhausted. That is a status fact, not a merge blocker classification from a maintainer.

## Nudge facts for 2026-10-02 or later

- Both PRs were last updated on 2026-09-25 (13303 at 13:35:37Z; 13316 at 16:22:28Z). The seven-day minimum therefore first permits a nudge on **2026-10-02**, UTC, not before.
- A compliant nudge must not ask for an ETA. Re-run `gh pr view` and the same dedup/status commands on or after that date; report any new maintainer review, CI, mergeability, or release change first.
- If a nudge is still warranted, handle #13303 before #13316 because #13316 is explicitly stacked on it. Josh owns the public words and approval; this packet is facts only.
- No issue comment, PR comment, push, merge, or other upstream write was performed while preparing this packet.
