# Fresh-clone re-run: one wrong fix line, one drift, everything else holds

Pane 3 (muse), 2026-09-19. Public HEAD 48ddb1e cloned to /tmp/fresh-jev (NOT
this worktree). Every rc below UNPIPED. Zero API calls except none — fully
offline except the clone itself.

| Command | rc | Verdict |
|---|---|---|
| `./scripts/quickstart.sh` | 0 | holds, BUT content stale: prints "17 candidate ideas" (STATUS now 25 rows) |
| `bash foundation/gates.sh` | 1→0 | RED names missing .db but prescribes nonexistent `br import` — see finding |
| `bash foundation/gates.sh --selftest` | 0 | 12 stages prove RED arms |
| `bash scripts/verify-frozen.sh` | 1 | fails on gates stage, same wrong fix line; 4 suites PASS in frozen clone |
| `./scripts/lane-status.sh` | 4 | names drifted UP-R8 receipt + "re-pin or explain" — actionable |
| `node demos/usage-shape/bin/shape.mjs --help` | 2 | prints usage (no --help flag exists); acceptable, reported |
| routing-backtest `npm test` + `npm run mutate` | 0/0 | via frozen run |
| `node scripts/jev-probe.mjs --replay` | 0 | — |
| `./scripts/quickstart.sh --mine /tmp` | 0 | "holds no .jsonl session files", clean refusal-as-answer |
| observe-only grep (full `-q` form) | 0 | "observe-only: no block path" (bare form rc=1 is grep semantics, documented) |
| `node work/omp-harm-rule/verify-claim.mjs` | 0 | 12/12 + 0/38 REPRODUCIBLE |
| `sync-docs.sh --check` | — | NOT RUN (downloads ~5MB mirror; state honestly, not skipped silently) |

## Planted negative (followed a fix line to green)

`br import` does not exist (`unrecognized subcommand`); the gate's fix line
is wrong. The real command `br sync --import-only` (Created: 32 issues,
rebuilt cache) takes the same gates run to **ALL GREEN — 12/12 stages on a
fresh clone**, including stage 40 (the fresh-clone caveat in README about
`compaction/node_modules` did not fire here). So the finding is precise: the
gate detects correctly and its remediation pointer is stale, in `gates.sh`
output AND in `verify-frozen.sh` output (same string, two surfaces).

## Other findings (reported, not fixed)

- UP-R8 receipt drift (lane-status exit 4): bytes vs pinned digest differ —
  needs deliberate re-pin or explanation, not silent acceptance.
- quickstart's "17 candidates" is stale (25 rows). Content rot in a passing
  script — the R37 class (numbers written into prose).

## NO-CLAIM

Live-key commands (`jev-probe` without `--replay`, keyed suites) not run;
`sync-docs.sh` not run; mine-mode only on an empty dir; one machine, one run.

## Second re-run after 850ea73 (new temp clone, public HEAD incl. the fix)

End-to-end arm, exactly as printed: clone fresh -> gates rc=1 naming
`br sync --import-only` -> run it verbatim (Created: 32 issues, rc=0) ->
rerun gates: **ALL GREEN, 12/12 including stage 40**. The corrected fix line
is now proven from a cold start, not just from a developed tree. This closes
the loop the first re-run opened.

| Command | rc | Verdict |
|---|---|---|
| quickstart | 0 | tail fixed: no count, points at lane-status.sh; reads correctly |
| gates --selftest | 0 | 12 stages prove RED arms |
| verify-frozen | 1 | FAILs on gates (missing .db in frozen clone); 4 suites PASS inside |
| lane-status | 4 | same UP-R8 drift, named + actionable (re-pin or explain) |
| jev-probe --replay | 0 | — |
| quickstart --mine /tmp | 0 | clean empty-dir message |
| observe-only grep (`-q` form) | 0 | "observe-only: no block path" |
| verify-claim.mjs | 0 | 12/12 + 0/38 REPRODUCIBLE |

sync-docs --check and live-key commands not run (stated, as before). No R37
regression: every row behaves or fails with its fix attached.
