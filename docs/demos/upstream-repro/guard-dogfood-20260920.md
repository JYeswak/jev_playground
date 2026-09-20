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

---

## CORRECTION appended 2026-09-20 (reconciliation lane, non-author)

**The claim stands. The witness does not. The build it came from no longer
exists anywhere.**

The row quoted above is real and is not retracted. But `class: "pipe-exit"`
was produced by guard-rule at `d26727a0`, and the `pipe-exit` class was
dropped under `NEGATIVE_EVIDENCE.md` R51 and removed from the classifier at
`e26b10f`. All 9 installed copies now hash `f10f7e16`. At the time this
receipt was written, jev-lab still carried the pre-drop build; it no longer
does. So this is a true record of a build that is gone.

What that does and does not cost:

- **LOADING PROVEN — still CONFIRMED.** The claim is that the extension
  loads and its handler runs on `tool_call`. Any decision row proves that;
  the class it carried is incidental. The `hooks/pre/` discovery and
  resolved-agentDir conclusions are untouched, because a wrong-path install
  could not have written a row of any kind.
- **The witness is no longer replayable.** Verified against the installed
  build, not inferred:

  ```
  cp ~/.omp/profiles/jev-lab/agent/hooks/pre/guard-rule.ts /tmp/gr-installed.mjs
  node -e 'import("/tmp/gr-installed.mjs").then(m=>console.log(m.classify("echo probe-ok | head -1").cls))'
  → null
  ```

  Re-running this receipt's procedure today yields `guard_pass`, not
  `guard_fire`. A reader who replays it and sees no fire has reproduced the
  correct current behavior, not a broken hook.
- **Replacement recipe for a fresh loading proof.** Probe with a string
  that still classifies — `grep -c …` → `grep-as-proof`, or a
  `git add -A`-shaped string → `stage-all`. If neither is convenient,
  `guard_pass` plus the `…diagnostic.v1` row (which fires on every
  `tool_call` regardless of tool or match) is sufficient evidence of load;
  that diagnostic exists precisely so "loaded but no match" is
  distinguishable from "never fired".

The per-tool denominator table (3 bash events, 1 decision) is unaffected in
shape but would now read 3 events / 1 `guard_pass` on the same prompt.

Not rewritten on purpose: this row is the only surviving evidence that the
R51 drop actually changed installed behavior rather than only source.
Deleting it would destroy that. Full reconciliation of the three
contradicting rulings on this class:
`pipe-exit-reconciliation-20260920.md`.
