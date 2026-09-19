# Hook exit-code-on-missing sweep

**Bead:** `jev-4vz`
**Scope:** Jev `githooks/` plus active `.git/hooks/` copies.
**Scratch only:** `/tmp/jev-hook-sweep-20260919`. Live hooks and Foundry hooks were not edited.

| Hook/case | Missing component | Observed result |
|---|---|---|
| `githooks/commit-msg` | sibling `commit-msg-verification-level.sh` removed | `rc=1`, `verification-level REFUSE reason=impl-missing` |
| `githooks/pre-commit` | staged-deletion implementation removed | `rc=1`, `STAGED_DELETION_REFUSED reason=impl-missing` |
| `githooks/pre-commit` | optional Foundry autofix missing, no override | `rc=1`, `AUTOFIX_REFUSED reason=impl-missing` |
| `githooks/pre-commit` | optional Foundry autofix missing, explicit `JEV_ALLOW_MISSING_AUTOFIX=1` | `rc=0`, but named `AUTOFIX_LANE_SKIPPED ... allowed by ...` |
| `.git/hooks/commit-msg` | sibling verification implementation removed | `rc=1`, `verification-level REFUSE reason=impl-missing` |

The active `.git/hooks/commit-msg-verification-level.sh` matched `githooks/` byte-for-byte. The
active wrapper is equivalent and differs only in its Foundry remediation-path text.

## Ruling

No silent default pass remains in the exercised hook paths. The only `rc=0` missing-checker case
requires an explicit risk override and prints a named skip. That is an intentional escape hatch,
not an unqualified PASS.

## No-claim

- `.git/hooks` contained only the two commit-msg files in this checkout; no active pre-commit copy
  was present there.
- Foundry hooks were not edited or exercised, per the bead rule.
- The live hooks were not renamed or removed; every destructive condition was tested only in the
  scratch copy.
