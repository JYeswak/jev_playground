# Fresh-clone README command audit

**Unit:** P2-29 Unit 1
**Clone:** `https://github.com/JYeswak/jev_playground.git`
**Fresh HEAD:** `fb137d271f2aa66fe1441d41f6d4d5322ba2a18c`
**Clone directory:** `/tmp/jev-p2-29.zYUcrk`

Commands were run in the fresh clone, separately, with each producer exit code captured without a
pipeline. README bash blocks were extracted first; placeholder/key-dependent commands were not
pretended to be runnable.

| Command | rc | Matches README implication? | Finding |
|---|---:|---|---|
| `work/omp-harm-rule/install-harm-rule.sh --check default` | 1 | NO | Fresh clone has no default profile/config or installed extension; check correctly reports RED, not a clean verification. |
| `node work/omp-harm-rule/verify-claim.mjs` | 0 | YES | Prints 12/12 and 0/38 committed-corpus result. |
| Published harm-rule grep | 1 | NO | Exact published grep prints `0`, but grep's no-match exit is 1; the README presents `# 0` without explaining this shell status. |
| `bash foundation/gates.sh` | 1 | NO | Fresh clone lacks `.beads/*.db`; stage 50 refuses DAG validation. Content gates otherwise run. |
| `bash compaction/install-jev-compact.sh --check` | 1 | NO | `.omp/lib/jev-compact` files and upstream clone are absent; check reports incomplete install. |
| `node demos/usage-shape/bin/shape.mjs /Users/josh/.claude/projects` | 0 | YES | Produces a real local-log token census; output is machine-specific as the README caveat says. |
| routing backtest fixture command | 0 | YES | Denominator 1 session / 6 turns / 0 failures; writes `runs/try-p2-29.json` in the disposable clone. |
| `scripts/sync-docs.sh --check` | 1 | NO | 137 mirrored files and 24 pinned clones are missing in the fresh clone. |
| `./scripts/quickstart.sh` | 0 | YES | All five offline questions answered. |
| `./scripts/bootstrap-compaction.sh` | 0 | YES | Reports already ready. |
| `bash foundation/gates.sh --selftest` | 0 | YES | All selftest stages pass in the fresh clone. |
| `bash scripts/verify-frozen.sh` | 1 | NO | Frozen verification fails because its frozen clone has no `.beads/*.db`; other suites and mutation arms pass. |
| routing mutation command | 0 | YES | 7/7 mutations caught and files restored byte-identical. |

Additional README blocks requiring unavailable inputs were not claimed as executed:
`infisical run` needs a project id/credentials; commands using `/path/to/logs` are placeholders;
`git clone`/`cd` setup blocks are instructions rather than repo-state assertions. The exact
compaction check was run separately because it is a required public installation surface.

## NO-CLAIM

This audit does not claim a clean fresh-clone install, missing mirror data recovery, a default
profile installation, or live Jev behavior. It records the public commands' actual fresh-clone
behavior. The mismatch findings are left unfixed; no command or README implication was tuned to
make the audit green.
