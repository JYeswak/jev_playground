# Guard-rule live fire: LOADING PROVEN `[receipt]`

Session `2026-09-20T17-49-12-422Z_01a0bfef` (jev-lab, gemini-2.5-flash via
infisical — Codex quota exhausted, exact error kept in prior callback).
Prompt ran one piped bash command; agent ran 3 bash calls total.

## Proof (session JSONL, not install state)

```json
{"kind": "guard_fire", "class": "pipe-exit",
 "command": "echo probe-ok | head -1",
 "toolCallId": "bash_1789926557285_1",
 "model": "none-deterministic-regex-guard-v1"}
```

Row type `com.zeststream.omp-guard-rule.decision.v1`. The fire is
quotable (command carried). Installed is firing; the receipt was not the
row, and the correct path WAS a loaded module — hooks/pre/ discovery
confirmed live, which also confirms the installed path IS the resolved
agentDir scan path for jev-lab (a wrong-path install could not have
produced this row).

## Per-tool denominator, this session (third refinement)

| | |
|---|---:|
| tool events observed (guard diagnostics by toolName) | bash ×3, others 0 |
| decision rows | route 2, harm 1, preaction 1, guard 1, dcg-bridge 1, rch-lane-bind 1 |
| guard decisions vs bash events | 1 decision / 3 events (2 events carried no command string — observed, unscored, same as harm shape) |

First honest per-surface count: in this session, every tool call was bash
(3/3 observed). No "every tool call" claim beyond this session.

## Path notes for the record

- `-p` one-shot DOES persist sessions (this file exists); the earlier
  no-session finding was a wrong-directory look, plus a quota-dead run
  that never reached tool execution. Both failure modes recorded, neither
  was hook silence.
- Unblock was infisical keys (conductor), not a new design.

## NO-CLAIM

One session, one profile, 3 bash calls. FP-rate and goldens still open
(steps 4–5). No model. `[receipt]` used.
