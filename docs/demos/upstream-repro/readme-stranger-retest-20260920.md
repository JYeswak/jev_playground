# README.md, run as a stranger would — every fenced command, 2026-09-20

**One verdict: README.md was NOT true as written this morning.** Twenty-six fenced commands ran.
Twenty-one are honest. Five were not: one command points at a directory that does not exist on the
machine it was measured on, one needs an API key the page twice promises you will not need, two
print something other than the figures the prose beneath them cites, and one table on this page was
corrected in one of the three places it appears. All five are fixed in this commit. A sixth finding
is not a README defect and is not fixed here: **a guard added on 2026-09-20 to stop published
counts drifting turned `foundation/gates.sh` RED on a fresh clone**, and the README's fresh-clone
table blames the wrong stage.

Tip under test: `1c2b4f0` → `8d34f11` (siblings were committing throughout; counts re-derived
immediately before the edit). Fresh clone: `6eee6ab`, the public tip, into a `mktemp -d`.
Every exit code below was taken **unpiped**.

## The four numbers corrected today, re-checked including the corrections

| claim | derivation (re-runnable) | result | verdict |
|---|---|---|---|
| 40 verdict rows (8 cleared, 17 held, 15 ruled out, 0 promoted) | `grep -vc '^#\|^candidate\|^$' docs/demos/STATUS.tsv`; `awk -F'\t' '$4=="CLEARED"' … \| grep -c .` per status | `40`, `8`, `17`, `15`, `0`; 8+17+15 = 40 | **CONFIRMED** — and independently by `./scripts/lane-status.sh`: `OK: 40 candidates. 40 receipt(s) exist` |
| 13 gate stages | `find foundation/gates.d -name '*.sh' \| grep -c .` | `13`; `bash foundation/gates.sh` printed 13 `PASS` rows matching the pasted transcript name-for-name | **CONFIRMED** |
| 55 dead-end ledger entries | `grep -cE '^## R[0-9]+' NEGATIVE_EVIDENCE.md` | `55` at `1c2b4f0`, **`56`** at `8d34f11` | **OVERTURNED as written.** The correction commit `13badbc` is titled "50 ledger entries is now 55" and changed **one of three sites**. L827 and L870 still said `50` — in the local tree *and in the public repo*. Both fixed to the derived count; a re-derivation command now sits beside the first one. |
| `omp-jev-observer` 89 live rows | `for p in ~/.omp/profiles/*/agent/sessions ~/.omp/agent/sessions; do [ -d "$p" ] \|\| continue; rg -oIN '"customType"\s*:\s*"(com\.zeststream\.[a-zA-Z0-9._-]+)"' -r '$1' "$p"; done \| sort \| uniq -c \| sort -rn` | `59` `…omp-jev-observer.diagnostic.v1` + `30` `…omp-jev-observer.decision.v1` = **89** | **CONFIRMED to the row.** 3,339/89 = 37.5, so the "37× overstatement" wording holds. **The public repo still carries the 3,339 sentence** — the correction is local and unpushed. |

Same census corroborates three other README cells with no work: `omp-jev-review` 3 decision + 3
diagnostic (page says 3 + 3), `omp-jev-failure` 2 decision (page says 2), `omp-jev-rerank` absent
entirely (page says 0 live rows).

## Every fenced command

`RUNS` = exits as documented **and** prints what the prose beside it claims. `RUNS-BUT-DOES-NOT-
DEMONSTRATE` = exits fine, does not produce the cited figures. `BROKEN` = cannot do its job here.

| # | README | command | rc | verdict | fresh-clone | settling line |
|---|---|---|---|---|---|---|
| 1 | L314 | `install-harm-rule.sh --check default` | 1 | RUNS (rc 1 is documented) | yes, rc 1 | `RED: not installed (or not listed)` |
| 2 | L315 | `install-harm-rule.sh default` | 1 | **RUNS-BUT-DOES-NOT-DEMONSTRATE** | n/a | `RED: no such profile: /Users/josh/.omp/profiles/default/agent` — there is **no `default` profile** on the machine this page is measured on; the 12 profiles are `claude codex glm grok jev-lab muse omp-1..3 omp-test1..3` |
| 3 | L335 | `node work/omp-harm-rule/verify-claim.mjs` | 0 | RUNS | **yes** | `shipped rule recall: 12/12` / `false positives: 0/38` |
| 4 | L358 | the observe-only `grep -qE` proof | 0 | RUNS | **yes** | `observe-only: no block path` |
| 5 | L382 | `grep -rho '"kind":"harm_[a-z]*"' ~/.omp/profiles/default/agent/sessions/ \| sort \| uniq -c` | pipeline 0, grep **2** | **BROKEN** | no | `grep: /Users/josh/.omp/profiles/default/agent/sessions/: No such file or directory (os error 2)` — and `$?` after the pipe is `uniq`'s **0**. The page's own dominant defect class, in the page's own proof command. Fixed to loop every profile with the rc taken before the pipe. |
| 6 | L407 | `python3 ensemble/run_all.py` | 0 | **RUNS-BUT-DOES-NOT-DEMONSTRATE** | **no**, rc 2 | prints **three** pairs; the table above it has **four** and the prose singles out the missing one ("Row three is the one that cost us a published rule"). The script's own docstring says "three pairs". Row 3 is `jev-sec-bench`'s n=662 ablation, computed in a different repo. Fixed by labelling which rows the command prints. |
| 7 | L456 | `npm --prefix compaction run replay -- …` | **2** keyless / **0** keyed | **BROKEN as documented** | no, rc 2 | `TYPESAFE_API_KEY is not set.` Root page said "No API key" (L279) and "none to run any tool above" (L551). `compaction/README.md:29` has said `NEEDS TYPESAFE_API_KEY; exits 2 without one` all along. Also `~/.omp/**/…` needs `shopt -s globstar`, which bash does not set (`shopt -u globstar` measured). Both fixed. Run **with** a key through the fixed command it is rc 0 on a real jev-lab transcript: `"messagesBefore": 48, "messagesAfter": 8, "charsBefore": 277779, "charsAfter": 35706, "requests": 1, "ms": 1269` — 87.1% chars saved, so the tool works and only its documentation was wrong. |
| 8 | L467 | `node demos/usage-shape/bin/shape.mjs ~/.claude/projects` | 0 | RUNS; dated figures no longer reproduce | yes (on any dir) | `4512 sessions, 488021 billed turns, 4519 files read` / `mean … 341907` vs the page's 4,619 / 488,724 / 4,626 / 341,496. The corpus **shrank** — Claude Code prunes its own logs. The L474 statement is dated 2026-09-18 and stays; the undated present-tense restatement at L663 was stale and is now dated with both runs. |
| 9 | L500 | `cd demos/routing-backtest && npm run backtest -- fixtures/real-excerpt-t1-t6.jsonl --out runs/try.json` | 0 | **RUNS-BUT-DOES-NOT-DEMONSTRATE** | yes | `{"denominator":{"sessions":1,"turns":6,"classifiableTurns":6,…}}` — **6** turns, no savings figure. The next sentence cites "30 classifiable turns … 0.0447%", which comes from `runs/derivation-0447-20260918T134500Z.json` (2 sessions). Fixed by naming the other run. |
| 10 | L525 | `git clone https://github.com/JYeswak/jev_playground.git` | 0 | RUNS | yes | resolves; public tip `6eee6ab` |
| 11 | L528 | `./scripts/sync-docs.sh` | — | **NOT RUN, declared** | — | maintainer-only network refresh that rewrites tracked mirror bytes; four sibling agents were committing into this worktree. `--check` was run in both trees instead. |
| 12 | L529 | `./scripts/sync-docs.sh --check` | 0 local / **1** clone | RUNS | no (by design) | local `CHECK PASS  114 mirrored files match MANIFEST.tsv (24 repo clones pinned)`; clone `CHECK FAIL  137 of 114 mirrored files missing or drifted` — **"137 of 114"** is a nonsensical fraction, a real display defect in `sync-docs.sh`, reported not fixed |
| 13 | L559 | `./scripts/quickstart.sh` | 0 | RUNS | **yes** | `5 of 5 questions answered.` Every figure in the pasted transcript matches live output: 16.4%, 7/7, 98.878%, 488,724/4,619/4,626, 80.1% of 1,013,018 over 18 turns, 0.78/0.15/0.05/0.02. The paste is truncated and its first line reads `quickstart:` where the tool prints `quickstart —`; gate 97 deliberately does not check transcripts. |
| 14 | L560, L682 | `bash foundation/gates.sh` | **0** local / **1** clone | RUNS locally; **fresh clone RED** | **no** | local: 13 `PASS`, `gates: ALL GREEN`, 32 s. Clone: `RED  80-lane-instrument-selftests (exit=1, 27s)`, `scripts/selftest-denominator-sweep.sh: 2 ok, 1 failed`. See the causal finding below. |
| 15 | L566 | `./scripts/bootstrap-compaction.sh` | 0 | RUNS | yes | `bootstrap-compaction: already ready` |
| 16 | L632 | `./scripts/quickstart.sh --mine` | 0 | RUNS | yes | `NO ANSWER, and the demo refused rather than guessed: EMPTY_CLASSIFIABLE_SET` — the L641 claim reproduces |
| 17 | L649 | `adapt-claude.mjs --print-price-template > prices.json` | 0 | RUNS | yes | emits `"source": "REQUIRED: …"` placeholders |
| 18 | L651 | `JEV_PRICES=prices.json ./scripts/quickstart.sh --mine` | 0 | RUNS | yes | with placeholders: `price file's source is missing or still the template placeholder` — the L669 refusal claim reproduces. Filled in: `converted 47428 of 55794 assistant turns; 8366 refused` and `NO_CHEAP_CANDIDATES: no turn qualifies for the cheap scenario` — **both exact to the digit**. The paste shows 3 of the 5 refused-model lines. |
| 19 | L740 | `infisical run --projectId=… -- node scripts/jev-probe.mjs` | 0 | RUNS (live) | n/a | live call returned `"noul": 0.36`, `"choice": "fewer_turns"`, `input_tokens: 629` |
| 20 | L746 | `bash foundation/gates.sh --selftest` | 0 | RUNS | yes | 13 `PASS`, `gates: ALL GREEN`, 55 s |
| 21 | L747 | `bash scripts/verify-frozen.sh` | 1 | RUNS (rc 1 documented) | — | `FAIL  foundation/gates.sh … require an imported Beads database`; 5 suites PASS; `cmp … 0 differ` |
| 22 | L748 | `cd demos/routing-backtest && npm run mutate` | 0 | RUNS | **yes** | `mutations: 7/7 caught` / `files restored byte-identical: yes` |
| 23 | L202 | `for d in */; do [ -d "$d/.git" ] && echo $d; done` | 0 | RUNS | n/a | `24` — matches "twenty-four" |
| 24 | L130 | `bash scripts/selftest-vgrep.sh` and the three siblings | 0,0,0,0 local | RUNS locally | **no** | `selftest-vgrep 8 ok`, `selftest-pinned-denominator 11 ok`, `selftest-pin-liveness 8 ok`, `selftest-denominator-sweep 3 ok` locally; **`selftest-denominator-sweep` is `2 ok, 1 failed` from a clone** |
| 25 | L731 | `cd demos/routing-backtest && npm test` | 0 | RUNS | **yes** | `# pass 29 / # fail 0` — matches "29 tests" |
| 26 | L733/734 | `node scripts/jev-probe.mjs --replay` / without a key | 0 / 2 | RUNS | yes | `"input_tokens": 523, "output_tokens": 82` matches Q5; keyless run prints `ERROR no key in env` — troubleshooting row correct |

## The finding worth more than the fixes: a fix broke the fresh clone

`foundation/gates.sh` is the third of the three Quick-start commands and the README's fresh-clone
table attributes its rc 1 to one cause: a missing Beads database, fixable with
`br sync --import-only`. On a real clone of `6eee6ab` on 2026-09-20 **stage 50-house-gates PASSED**
— that hole is closed — and the RED is somewhere else:

```
RED  80-lane-instrument-selftests (exit=1, 27s):
  RED  scripts/selftest-denominator-sweep.sh   scripts/selftest-denominator-sweep.sh: 2 ok, 1 failed
```

```
ERROR locked-dig-138 (rc=2) — the check itself is broken, NOT a drift finding
```

Cause, settled: `scripts/denominator-sweep.sh:50` is
`check "locked-dig-138" 138 grep -c . work/cass-mail-mines/exports/cass-dig-rows.jsonl`, and
`git check-ignore -v` returns `.gitignore:95:work/cass-mail-mines/exports/*.jsonl`. The file is
20 KB of mined mail rows that the repo deliberately does not publish, so the check can never run
from a clone.

Ordering is not a guess: `git merge-base --is-ancestor b194b55 06a1e1d` is true. `b194b55`
(2026-09-19) published the fresh-clone table; `06a1e1d` (2026-09-20) added the sweep. **The guard
built to stop published counts from drifting silently is the thing that now fails a stranger's
`gates.sh`.**

Not fixed here, and deliberately not fixed by committing the fixture — it is somebody's mined mail
corpus and gitignored on purpose. **Smallest honest fixture:** commit
`work/cass-mail-mines/exports/cass-dig-rows.count` — one integer plus the generating command and
the source SHA — and point `locked-dig-138` at that, so the pin travels while the data does not.
Failing that, `denominator-sweep.sh` must distinguish *source absent from this checkout* (skip,
with the reason named, and never counted as ok) from *check broken*, which its header already
argues for: "An empty scan set is never a pass."

## Second broken remedy: bootstrap does not fix the compaction check

The same table says `compaction/install-jev-compact.sh --check` rc 1 is fixed by
`./scripts/bootstrap-compaction.sh`. Measured on the fresh clone: rc 1 **before** the bootstrap,
bootstrap prints `bootstrap-compaction: already ready` (rc 0), rc 1 **after**. They do different
jobs. `--check` verifies a hook installed into a *target repo*; the real remedy is
`compaction/install-jev-compact.sh <target>`, after which `--check <target>` is rc 0 with
`PASS: jev-compact installed at …`. Verified against a clean `mktemp -d` target: install rc 0,
check rc 0.

**Installer defect found on the way (reported, not fixed):** `install-jev-compact.sh .` run inside
jev_playground itself exits **1** with `RED: copy of skill failed`, because source and destination
are the same path and `cp` refuses — `cp: … are identical (not copied)`. The subsequent `--check`
then says `PASS`. An installer that reports RED after succeeding is the same defect class as
`harm_error` reading as `harm_pass`. Only reachable when the target is the repo itself, which is
what the README's argument-less form defaults to.

## Claims checked that are not fenced commands

- **Framing flip** (`scripts/measure-framing-flip.mjs`, 10 paired calls, re-run live 2026-09-20
  19:20 UTC): WITH-shape `min 0.34 median 0.38 max 0.41`, `top_lever {"fewer_turns":10}`;
  WITHOUT `min 0.69 median 0.7 max 0.71`, `{"cheaper_model":10}`. **The load-bearing claims hold
  exactly** — distributions do not overlap, the lever flips 10/10, `0/10` with-arm calls reach
  0.21 and `10/10` without-arm calls clear 0.59. The three quoted decimals per arm moved within
  hours of being published (0.32/0.37/0.41 → 0.34/0.38/0.41). That is the bullet's own lesson
  landing on the bullet. **CONFIRMED**, no edit.
- **Latency** (10 consecutive live probes through the documented command): `min 255 median 468
  max 878 ms` against the page's re-measured `min 484 median 1,034 max 2,291`. The load-bearing
  claim — 0 of 10 inside the published `743 to 773 ms` — **still holds** (today: 673 and 796
  straddle it). The published triple does not reproduce four hours later, on a page whose next
  clause is "budget for the tail, not the median". **CONFIRMED in direction, not in digits.** No
  edit: it is dated and explicitly a single run.
- **`harm_error`**: the page says "You will see three kinds". Across all 12 profiles:
  `116 harm_pass`, `14 harm_fire`, **`0 harm_error`** — consistent with the page's own "It had
  never fired in production" fifteen lines later, and inconsistent with the sentence introducing
  the table. Fixed.
- **`n=16` live fires**: the corrected command counts **14**. Monotonic growth cannot explain a
  decrease, and the original derivation was not recorded. Replaced with the number the published
  command prints, with the disagreement stated rather than hidden.
- **Eleven taste packages**: all eleven named directories exist. But `ls -d work/omp-jev-*` returns
  **20**, and four — `omp-jev-commit`, `omp-jev-dispatch`, `omp-jev-foreman`, `omp-jev-route` — are
  in neither the six-row table nor the eleven. `omp-jev-route` has **147 live decision rows**, more
  than every table row except `omp-harm-rule`. `grep -c` for each of the four in README.md returns
  `0`. Not false, but the page reads as a complete inventory and is not one. **Reported, not
  fixed** — deciding what those four are is a product call, not a typo.
- **Markdown**: the Troubleshooting table had **no delimiter row** and a blank line after its
  header, so it rendered as seven lines of literal pipes, and `## Troubleshooting` had no blank
  line before it. Fixed; two rows added for the two new failure modes above.

## What changed in README.md

`55/50/50` → derived count in all three places, with the derivation command beside the first ·
harm-kind command loops every profile and takes the rc before the pipe; "three kinds" → the two
you will actually see, with the 2026-09-20 counts · ensemble block states that the command prints
three of the four rows and where the fourth comes from · replay block carries the key requirement,
the `infisical` wrapper and `shopt -s globstar` · both blanket "no API key" sentences name their
two exceptions · routing-backtest block separates the 6-turn fixture from the 30-turn 0.0447%
derivation · `--mine` figures dated with both runs · fresh-clone table gains a dated 2026-09-20
retest correcting three rows rather than rewriting the 2026-09-19 measurement · Troubleshooting
table markup repaired, two rows added · `TYPESAFE_API_KEY` scoped to two commands · runtimes
re-measured under load.

Stages 95, 96 and 97 re-run after the edit: all `PASS`.

## NO-CLAIM

- One machine (M3 Ultra, macOS 25.5.0, node v22.22.0, python 3.9.6), one network, one afternoon,
  with four sibling agents committing into the same worktree. Runtimes are contended.
- `./scripts/sync-docs.sh` (full fetch) was **not run**; only `--check`.
- `foundation/gates.sh --selftest` was run and is rc 0, but its output is byte-identical in shape
  to the normal run, so **this receipt does not independently verify that each stage went red**;
  the exit code is the whole evidence.
- The fresh-clone column is measured at `6eee6ab` (public tip), which does **not** contain the
  local observer/89 correction. A clone taken after this commit lands may behave differently.
- Live-row counts (89, 147, 14, 116) are monotonic against a growing session store: they are
  as-of 2026-09-20 and will not reproduce as equalities later.
- The `omp-jev-route` 147-row figure is a `customType` count only. **No claim** about what that
  package is, whether it is promoted, or whether it should be in the table.
- The compaction replay **was** run with a key (rc 0, one live request, 48 messages to 8). **No
  claim** beyond that single transcript: one session, one call, no invariant re-check beyond the
  harness's own `"failures": []`.
- **No claim** that the fixes in this commit are complete: five defects were fixed, four more
  (the `137 of 114` fraction, the self-install RED, the gitignored sweep pin, the four undisclosed
  packages) are reported and left to their owners.

---

# Addendum — second pass, 2026-09-20: a stranger's `gates.sh` is green, and two of my own claims were wrong

## Retraction first: "the beads hole is gone" was false

The first pass reported `foundation/gates.sh` rc 1 on a clone with "stage **50-house-gates
PASSED** — the beads hole is gone", and blamed stage 80 alone. **Wrong.** That clone had already
been handed a `.beads/beads.db` by an earlier command in the same sweep — `.br-db-openers-*.lock`,
`.br-db-write-*.lock` and `.br-jsonl-write-*.lock` were sitting in its `.beads/` — because
`lane-status.sh`, `sync-docs.sh --check` and the quickstart all ran before `gates.sh` did.

Measured on a clone with **nothing run in it**, first command after `cd`:

```
RED  foundation gates require an imported Beads database under …/.beads/*.db
     Fresh clone fix: run 'br sync --import-only' from the repository root, then rerun …
```

It does not reach stage 10. The 2026-09-19 table row was right; my retraction of it was not. A
clone you have run anything else in is not a fresh clone, and this is the second time that exact
error has been made on this page today.

## The Quick start was a three-command list that could not complete

`br sync --import-only` was never in it. Every stranger hit a RED as their third command. README
now lists four steps with the import's real output, and `br` is named in *What you'll need*.

## A stranger's gates.sh is GREEN — measured in an untouched clone, in order

Clone of `work/cass-dig-vs-invent` at `2344ab0` into a fresh `mktemp -d`. Proof of untouched,
taken before anything ran: `.beads/` held only `config.yaml issues.jsonl metadata.json` — **no
`*.db`** — and `compaction/node_modules` did not exist. Then, in order, only the four documented
commands:

| step | command | rc | evidence |
|---|---|---|---|
| 1 | `git clone --branch work/cass-dig-vs-invent … && cd` | 0 | `2344ab0` |
| 2 | `./scripts/quickstart.sh` | **0** | `5 of 5 questions answered.`; `.beads/*.db` still absent afterwards |
| 3 | `br sync --import-only` | **0** | `Imported from JSONL (via automatic recovery): Created: 50 issues` |
| 4 | `bash foundation/gates.sh` | **0** | 13 `PASS`, **`gates: ALL GREEN`**, 55 s |

This is the first run in which a stranger's `gates.sh` has been green from a clone that had
nothing else done to it. It took `190668d` (absent ≠ broken), `2e76a29` (the selftest arm that was
green locally and RED for every stranger) and the Quick-start step above.

**Arm 1, not arm 4, was the second blocker.** After the beads import at `190668d`, stage 80 was
still RED: `selftest-denominator-sweep.sh: 3 ok, 1 failed`, the failure being
`FAIL sweep did not agree: rc=0` at `selftest-denominator-sweep.sh:21`, which required the literal
string `ALL-AGREE` while the honest clone verdict is `AGREE-WITH-1-SKIPPED`. The new SKIP branch
(arm 4) passed. The seam is why it hid: `JEV_SWEEP_FORCE_ABSENT=1` drives arm 4 only, while arm 1
runs the real sweep, whose absent-source state is the **default on a clone and never the case
locally**. A test seam that covers the new branch can leave the old branch environment-dependent,
and no local run can see it.

## The other seven sweep checks, audited (Main's question)

**None depends on installed demos.** All seven report `ok` in a clone where
`demos/routing-backtest`, `demos/usage-shape` and `work/jev-score-register` have **no
`node_modules` at all** (verified by `ls -d …/node_modules` → absent for each, immediately before
running the sweep). The two file-backed sources are tracked and present:
`work/jev-score-register/fixtures/scores-pinned-20260920.jsonl` and
`work/p3-calibration/toolcall-corpus-frozen.jsonl` — `git ls-files --error-unmatch` succeeds and
`git check-ignore` returns nothing for both. `locked-dig-138` was the only absent-source check.

**Without `node`, the three node-backed checks fail loudly and correctly.** With a `node` shim
that exits 127 on PATH:

```
ERROR pinned-replay-55 (rc=2) — the check itself is broken, NOT a drift finding
ERROR pinned-replay-api0 (rc=2) — the check itself is broken, NOT a drift finding
ERROR backtest-29 (rc=2) — the check itself is broken, NOT a drift finding
```

Not silent, not misclassified as DRIFT. That shape is right.

**But two of the seven are live-monotonic, which the sweep's own header forbids.**
`census-packages-21` is `ls -d work/omp-jev-* work/omp-harm-rule | wc -l` and `export-yes-19`
counts qualifying packages the same way. The header says: *"Do NOT add live-monotonic claims here
— a moving target wired as an agree-check REDs forever (the nag class R46/R47 refused)."* Proven,
not argued — in the clone, creating one `work/omp-jev-zzprobe/src/` directory:

```
  DRIFT census-packages-21
scripts/denominator-sweep.sh: DRIFT-FOUND      (rc=1, taken unpiped)
```

which REDs stage 80 and therefore `gates.sh` for everyone. This repo ships eleven unpromoted taste
packages under `work/` and is still adding them, so this fires on the next one. **Reported, not
fixed** — it is the sweep's owner's call whether the count is pinned, derived, or dropped.

## My own fix taught the defect it fixed

The first pass replaced the `~/.omp/profiles/default/…` census with a loop whose comment read
`# rc UNPIPED: a bad path here exits 2`. That is false: `done | sort | uniq -c` still reports
`uniq`'s status. Measured both arms — dead path with the guard and dead path without it — and
`rc_after_pipeline=0` in **both**. The `-d` guard, not an exit-code read, was doing the work. The
block now says exactly that and emits a `scanned <dir>` line per directory to stderr, so zero rows
with zero scanned lines cannot be read as "read everything, found none" (good arm: 13 scanned,
`116 harm_pass` / `14 harm_fire`; dead arm: 0 scanned, empty). A page that gets the rc discipline
wrong inside its own proof command has no standing to teach it.

`awk` over every fenced `bash` block in README.md now returns three `|` lines: the two in this
corrected census, and the `&&`/`||` observe-only proof, which consumes `grep -q`'s status directly
and never pipes it. **No remaining fenced command in README.md reads an exit code through a pipe.**

## Still shipping wrong to the public (unresolved, owner action)

`git ls-remote --symref origin HEAD` → `refs/heads/main`, `6eee6ab`. `main` is **60 commits**
behind the working branch and `git merge-base --is-ancestor origin/main HEAD` succeeds, so
publishing is a fast-forward; there is no open PR for `work/cass-dig-vs-invent`. Until it merges,
a reader of the public page today gets: the observer row saying **3,339 rows** "not attributable
to this package alone" instead of 89; **"50 entries"** twice for a ledger holding 56; the dead
`~/.omp/profiles/default/` census; `npm run replay` presented as keyless; the three-command Quick
start that cannot complete; and a `gates.sh` that REDs on `locked-dig-138`. **Not actioned here:**
merging 60 commits to a public default branch is a repository-owner decision, not a subagent's.

## NO-CLAIM, addendum

- The green `gates.sh` is **one** clone, on **one** machine, at `2344ab0`. It is not a claim about
  a machine without `br`, without `node`, or without network for stage 40's bootstrap.
- The `node`-absent result used a shim exiting 127, not a machine genuinely lacking node.
- The live-monotonic hazard was proven by creating one directory in a throwaway clone. **No claim**
  about which of the two checks should change, or whether the count should exist at all.
- **No claim** that the public page is fixed. It is not. Nothing in this addendum touches `main`.
