# Hardening census: wired vs prose-only — 2026-09-20 `[pending]`

Re-derived from `commit-learnings-20260919.md` after both new guards
landed (`scripts/vgrep.sh` + selftest, `scripts/pinned-denominator.sh` +
selftest, both discovered by stage 80's `scripts/selftest-*.sh` glob —
no new stage added).

## Wired (a command fails loudly)

| class | recurrence | guard |
|---|---:|---|
| selector / silent-zero read as clean | 26 | vgrep (exit 3 on zero matches) |
| denominator drift under a fixed sentence | 8 | pinned-denominator (exit 3 on disagreement) |
| TESTS.md registry drift | 1 | stage 70 |
| stale numerals in verdicts | 0 live fires | stage 95 ratchet |
| readme counts | 3 caught | stage 97 |
| staged-deletion drop by path-limited commit | causal | stage 60 + pre-commit hook |

## Prose-only, ranked by recurrence

| rank | class | recurrence | evidence |
|---:|---|---:|---|
| 1 | staged-file exposure (uncommitted work lost / clobbered on branch-switch) | 4 | 16b THIRD, 18b FOURTH, "lost twice today" (§16b/18b + dispatch) |
| 2 | reproducibility: live numbers quoted without pinned inputs | 5 | ledger §"What the program established" #4; 15c fourth defect; partial source fix (replay.mjs sha) covers one surface |
| 3 | callback/receipt sha omission (packet contract) | 4 | 9b three consecutive + 18b receipt/sha landing split |
| 4 | residual mention-vs-use beyond silent-zero (judgment shape: quoted prompts, test strings, doc prose scored as fires) | 17 total, minus vgrep-covered selector subset | ledger #3; harm-rule organic 0/28 |
| 5 | placeholder prose in shipped surfaces | 2–3 | §24/24b (+ intentional teaching literals in essays — a guard here false-positives by construction) |

Rank 1 vs 2 note: reproducibility counts 5 but one surface already fixed
at source and the denominator half is now wired; staged-exposure counts 4
with zero wiring and live loss (files actually lost). Rank by unguarded
remainder: staged-exposure first.

## NO-CLAIM

Counts re-derived by grep over the ledger tonight, not an independent
audit. "Wired" means a command exits nonzero on the defect shape, not
that the class cannot recur in a new shape (vgrep header states its 1-of-3
boundary). No third guard built in this unit, per instruction.
