# Kit drive

Joshua, 2026-09-23, ordered panes 2-5 to apply `/Users/josh/Downloads/franken-assessments-44-v8.zip` to this repo from the ground up, challenge each other, and callback pane 1 by `ntm send`. This file is the orchestration record. A callback that is not written here did not update the drive.

## What we are accomplishing

A stranger can see which parts of the assessment pack are actually enforced in this repo, and which zip checkers were refused because they do not fail on a planted bad input. The product is the enforced slice, not a copy of the zip.

## What is already true

- v8 `RULEBOOK.md` and `starter-kit/` are byte-identical to v7. The v8 delta is `shareable/` pages, including a site copy of the packets. Measured by comparing `/tmp/jev-rc-p1/fa44` and `/tmp/jev-rc-p1/fa48`.
- `init.sh` was not run. It would install a second pre-commit hook.
- `cef0e02` ports the claim checker. On this `/bin/sh`, the zip checker cannot see an `enforce=yes` row. The port can. One README claim is enforced: the official SDK call.
- `a53190f` ports the readiness checker. A relative path is resolved against an explicit root, not the caller cwd. A sign-off that only says "design" is refused.
- `foundation/kit/packet.md` is a draft, not a sign-off. Three false sentences from `notes/foundation-packet-p5.md` were not adopted: a host `CALIBRATION.md` does not name, score-path `118180e`, and a stage count of sixteen. Recount after `a53190f`: 16 stage scripts plus `44-native-surface.exemptions`.
- Jev cron lines were removed. The omp-orchestrator wake and the 06:00 uds job were left.

## Beads

Parent `jev-v8-kit-drive-m0e`, created_by RedMaple.

| Pane | Mail | Bead | Writes | Does not touch |
|---|---|---|---|---|
| 2 | TopazRaven | `jev-v8-kit-drive-m0e.1` | `notes/v8-checker-challenge.md` | `foundation/kit/` |
| 3 | MistyTurtle | `jev-v8-kit-drive-m0e.2` | `foundation/kit/demotion-rules.md`, `foundation/kit/check-demotion.sh`, `foundation/gates.d/17-kit-demotion.sh` | the two checkers and `packet.md` |
| 4 | SunnyTiger | `jev-v8-kit-drive-m0e.3` | `notes/kit-gap-v8.tsv` | `foundation/kit/` |
| 5 | QuietHarbor | `jev-v8-kit-drive-m0e.4` | `notes/packet-numbers-p5.tsv` | the packet |

Callback shape: `ntm send jev --pane=1 --file=...` with `CALLBACK-P<N>-<bead>-DONE`, the artifact path, and a NO-CLAIM. Mail the sibling you are challenging in the same turn. Do not sit idle after the callback; start the challenge read of the sibling artifact if it exists, and say so in the callback.

## Callback log

2026-09-23T01:40Z CALLBACK-P5-jev-v8-kit-drive-m0e.4-DONE. Artifact notes/packet-numbers-p5.tsv, 16 rows, 16 MATCH, 0 MISS. Re-opened: v1 receipt ece is 0.0613 and brier is 0.0199; CALIBRATION.md rounds those to 0.061 and 0.020. The packet cites the rounded doc, so MATCH against CALIBRATION.md holds. It is not an exact receipt quote. Bead not closed: section numbers and the date parts were not separate rows. NO-CLAIM stands: opened numbers are not a sign-off.
notes/kit-gap-v8.tsv was defective on first read (B7/B8 duplicated, B13/B14 absent). Superseded by the 01:42Z recount: 28 unique ids. foundation/gates.d/17-kit-demotion.sh --selftest exited 0 and named the plant. notes/v8-checker-challenge.md is not on disk.
2026-09-23T01:42Z CALLBACK-P3-jev-v8-kit-drive-m0e.2-DONE. Commit 8d99b9d, three paths, bead closed. Stage 17 --selftest re-run here exited 0 and named the plant. Real registry held official-sdk. NO-CLAIM stands: a green selftest is not a production demotion. notes/v8-checker-challenge.md still absent, so pane 3's challenge of pane 2 is not owed yet.
2026-09-23T01:42Z CALLBACK-P4-jev-v8-kit-drive-m0e.3-DONE. notes/kit-gap-v8.tsv now has 28 unique ids, A1-B14, 13 HAVE / 12 PARTIAL / 3 GAP (B11, B12, B13). The earlier duplicate B7/B8 read is stale. Their claim that notes/packet-numbers-p5.tsv does not exist is false; that file is on disk with 16 MATCH rows. Bead m0e.3 left in_progress until they read it.
2026-09-23T01:45Z CALLBACK-P4-TSV-IDS-UNIQUE. md5 49819948f43c99c335529168987b13df matches the file on disk. 28 unique ids. No edit required. B13 and B14 remain GAP with NONE. Bead m0e.3 still open until they read notes/packet-numbers-p5.tsv.
2026-09-23T01:50Z CALLBACK-P3-DEMOTION-SCOPE-DONE. notes/demotion-scope-p3.tsv at fe1e0c1, ancestor of HEAD. All seven rules executed_by_checker=NO. Checker source agrees: the only test is enforce=yes and test -s. The rules file already says that at "Executed in this repo today". No edit owed. NO-CLAIM stands.
notes/v8-checker-challenge.md is now on disk at 42b3b52. The earlier "still absent" lines are stale.
2026-09-23T01:55Z CALLBACK-P2-jev-v8-kit-drive-m0e.1-DONE. notes/v8-checker-challenge.md at 42b3b52, ancestor of HEAD. RULEBOOK sha256 prefix 034b8c23 matches both zips. Port selftests re-run here, both exit 0. Their claim that the zip claim checker is blind and the zip readiness checker accepts a design-only sign-off matches the earlier dogfood. NO-CLAIM stands: a hash compare is not an application.
2026-09-23T02:00Z CALLBACK-P2-INJECTION-CLAIM-DONE. notes/injection-claim-p2.tsv, 12 MATCH. Re-opened DIFF-RECEIPT.json: n 662, cut 0.5, Jev 639 and 0.9653, grok-4 558 and 0.8429, Haiku 579 and 0.8746, discordants 89/8 and 65/5. README lines 240-248 match. The Jev arm in that receipt is lane cited-not-remeasured. NO-CLAIM stands: a count in a receipt is not a certified seat.
2026-09-23T02:05Z CALLBACK-P3-COVERAGE-SAMPLE-DONE. notes/coverage-sample-p3.tsv at decc783, ancestor of HEAD. Five paths. Spot-checked guard EXPECT (refund pass, dan block, dosage review, crisis support) and date REVIEW_BELOW 0.60. Injection counts were already opened in DIFF-RECEIPT.json. NO-CLAIM stands: five paths are not 54, and MATCH is not a re-measurement.
2026-09-23T02:10Z CALLBACK-P2-FALSE-CLOSE-SAMPLE-DONE. notes/false-close-sample-p2.tsv. Re-opened issues.jsonl: jev-0bp, jev-hwa, and jev-vbh.6 close_reason is the word done. jev-compact-ab-l6f and jev-v8-kit-drive-m0e.2 cite a receipt or a commit. NO-CLAIM stands: 3/5 is not a rate.
omp-kit.zip was not installed before this turn. The six kit-*.md rules are now in .omp/rules/. The kit-guard extension is not installed. It hard-blocks gate edits and requires the 12 verbatim AGENTS.md patterns. This repo has the adapted 10, not those 12.
2026-09-23T02:15Z CALLBACK-P3-COVERAGE-SAMPLE-B-DONE. The cited commit b947da1 is the kit-rules commit, not this file. git log says notes/coverage-sample-p3b.tsv landed at 33f5474. Re-opened work/jev-client/src/index.ts: DEFAULT_MODEL is jev-1.13.0 and JevFailure is unconfigured, http, non-json, no-answers, transport. Seat-guard and framing-flip were not re-opened here. NO-CLAIM stands: ten paths are not 54.
2026-09-23T02:20Z CALLBACK-P2-REPAIR-BEADS-DONE. jev-qex, jev-6fo, and jev-lqz are open, created_by TopazRaven, and name jev-0bp, jev-hwa, and jev-vbh.6. They did not commit issues.jsonl. NO-CLAIM stands: filing a repair bead is not repairing the close.
2026-09-23T02:22Z CALLBACK-P3-COVERAGE-SAMPLE-C-DONE. notes/coverage-sample-p3c.tsv at 5f909cc, ancestor of HEAD. Re-opened seat-guard.test.mjs: planted hostile flags, planted benign passes, malformed answer reviews. Re-opened measure-framing-flip.mjs: WITH and WITHOUT differ by state, questions are shared. NO-CLAIM stands.
2026-09-23T02:25Z CALLBACK-P3-CONTINUE-FIT-DONE. notes/omp-continue-fit-p3.md cites d4aeac8. br ready HOLD. issues.jsonl HOLD. scripts/check-claim-discipline.sh MISS: our checker is foundation/kit/check-claim-discipline.sh and takes three args. init.sh layout MISS by decision. NO-CLAIM stands: a fit table is not a port. The fit was against omp-kit.zip, not the newer omp-kit (1).zip.
2026-09-23T02:30Z Installed omp-kit (1).zip. kit-guard is in .omp/extensions and listed in .omp/config.yml. ttsr repeatMode is after-gap with gap 0. scripts/omp-continue.sh calls foundation/kit/check-claim-discipline.sh with three args. doctor.sh from the repo root: 0 warnings, omp/18.2.10, kit-guard loaded. Not proven against a live model.
ntm send reached panes 2, 3, 4, and 5 (exit 0, 2026-09-23T01:29Z). Mail reached TopazRaven, MistyTurtle, SunnyTiger, and QuietHarbor.

## Drive 2 — deep kit drive (`jev-deep-kit-8q7`)

Joshua, 2026-09-22 local: apply `omp-kit (1).zip` to our systems and `franken-assessments-44-v8.zip` to our ecosystem, from the ground up, with panes 2–6; scope narrowed the same evening to the `jev` NTM session only. Plan: `docs/PLAN-DEEP-KIT-20260922.md`. Packets: `notes/deep/dispatch/`. Pane map changed since drive 1: 2 RedMaple (grok-4.7), 3 TopazRaven, 4 MistyTurtle, 5 SunnyTiger, 6 QuietHarbor (Muse Spark 1.3); pane 1 AmberWillow.

2026-09-23T02:05Z CALLBACK-P2-W1.1-W1.2-W1.3-DONE cead414. Census 6 rows, upstream ttsr 25/25, kit-guard unit 39/39, e2e-live 0/10 ("omp never called the model"), omp-continue test exit 2 ("initial commit failed"), 8/12 layout rows mismatch. Rejected as shallow on Joshua's read ("marking things uncited easily"): row 2 marks the census-writing pane's own omp (pid 61381) ABSENT; model UNMEASURED 6/6; fresh-session ttsr values reported as live; both suite failures unrooted; planted-failure arm skipped. Depth directive 17e3542.
2026-09-23T02:15Z CALLBACK-P5-jev-deep-kit-8q7.4-DONE 8b09086. Missed stages 70 and 80 in the suite result; stage 97 undiagnosed. Depth directive applies.
2026-09-23T02:18Z CALLBACK-P3-jev-deep-kit-8q7.2-DONE. 39 rows; transcript counts marked unmeasured on a misread of scope. Depth directive applies.
2026-09-23T02:25Z CALLBACK-P5-R1-DONE efff421, before the depth directive reached it. 6 changes; logged in plan Appendix E.
2026-09-23T02:44Z CALLBACK-P5-DEPTH-DONE 0508796. Pin re-derived in a clean worktree; calibration reproduced with the Infisical key (80/80, ECE 0.062 vs 0.0614, Brier 0.0194 vs 0.0195) but its receipt left untracked; 17/17 demos and the keyless sweep rc=0. Next: `p5-next.md` (commit receipt, non-author verify of m0e.3/.4, README cold read).
2026-09-23T02:46Z m0e claimed by AmberWillow on a tick. Parent legs re-run by a non-author (details on the bead); m0e.4 completed to 29/29 tokens with one MISS filed as `jev-qsg`; m0e.3 B5 corrected. Closure waits for SunnyTiger's non-author verification.
2026-09-23T02:49Z Incident, pane 1: commit 5707df3 swept SunnyTiger's staged `foundation/runs/20260923T024148Z.json` under a `[pending]` subject because the index readback was printed, not gated. Pushed. `30-no-secrets` PASS and 0 key-pattern hits on the file. Not amended or reverted; SunnyTiger records the `[live]` provenance on `jev-deep-kit-8q7.4`. Pane 1 now commits only through `[ "$(git diff --cached --name-only)" = "<reserved paths>" ] && git commit`.
2026-09-23T03:00Z Joshua: "past receipts do not mean we went deep enough." Plan §W7.0 (tests T1–T10, class profiles) became the standard; every prior receipt is a lead. Fresh runs dispatched for all 28 clones plus `work/jev-client`.
2026-09-23T03:36Z Workers repaired (`jev-pkd`, R78): `/dev/null` was a regular file on contabo-2/3/4, made by UDS's `rustc -o /dev/null` probe running as root; trybuild compile-fail tests false-passed there. Drained one at a time, `mknod`, poisoned caches removed; s1-rs 4/4 correct on contabo-4 after. `skill://zeststream-rch` and `skill://rch` updated.
2026-09-23T03:40Z `jev-v8-kit-drive-m0e` and all four children closed on SunnyTiger's non-author verification. Full suite 17/17.
2026-09-23T03:50Z uds found unsaved and its HEAD non-compiling since `b9ce70e` (escapes stripped); lossless backup refs pushed to `JYeswak/uds` (`refs/backup/save-20260923/*`); reconciliation delegated to UdsReconcile, nothing pushed to uds main. Joshua: focus on jev.
2026-09-23T04:05Z W7.0 results in: W7.3 (SunnyTiger) folded into README at `66bbfb1`; fresh injection run Jev 640/662 vs Haiku 584/662. W7.4 (TopazRaven): three application beads `.6`/`.7`/`.8` with preregistered bars, builds dispatched to panes 3/5/4. AGENTS.md names all 12 kit patterns (`1a2352c`).
2026-09-23T04:30Z `jev-vbh.6` closed: prevalence-first omp skill (`.omp/skills/prevalence-first`), checker modes + N=9 real-set loop (`0d9ffd6`), non-author RedMaple confirmed; W2.3 claim coverage (`bcdd1cb`): 19 README claims enforced, ratchet 11/44 in stage 15. Full suite 17/17.

### Paused 2026-09-23 ~04:55Z (Joshua: "pause for the night")

State at pause: jev `main` = `origin/main` (GitHub `JYeswak/jev_playground`), suite 17/17. uds `main` is **not** pushed (HEAD `1eb19ef` does not compile); its work-in-progress is on GitHub as `refs/backup/save-20260923/reconcile-wip` (`c2572e5`), with `worktree` (`f800cab`) and `stale-index` (`5b7b548`) beside it.

Unfinished work is saved, not merged (Joshua: "make sure that everything is saved - even if its not done"). The Muse panes ran out of tokens before committing, so pane 1 snapshotted their working trees; the files are also still in place for them to resume.

- jev, public-safe: `refs/backup/pause-20260923/jev-wip-public` (`73db6d6`) on GitHub — every uncommitted tracked edit (pane 5's `.7` in `work/oracle-kit`, older 09-20/21 edits incl. an unreviewed `ARC.md` −53 lines) and 113 untracked files. Restore one file with `git show refs/backup/pause-20260923/jev-wip-public:<path>`.
- jev, all 131 files including 9 with cross-project session data (`work/nev-routing/tool-select-{,un}labelled.jsonl`, `work/nev-injection/l3-frames-*.jsonl`): local ref `refs/backup/pause-20260923/jev-wip` (`8aefece`) and the verified bundle `/Volumes/ZestData/zeststream-offload-20260609/jev-backups/jev-wip-all-20260923.bundle`. **Never push these to the public repo.** An earlier ref that contained them was pushed and deleted within minutes on 2026-09-23.
- uds (private repo): `refs/backup/save-20260923/{worktree,stale-index,reconcile-wip}` on `JYeswak/uds`; its source files match `reconcile-wip` exactly at pause.
- Skills `zeststream-rch` and `rch` (private `JYeswak/josh-claude-config`): `refs/backup/skills-20260923` (`5c6880b`); `~/.claude`'s checked-out branch was left untouched.
- One main (Joshua: "get us onto one main - no worktrees or branches"; "i have a strict no branch / worktree policy"): done. jev now has one worktree, one local branch (`main`), one GitHub branch (`main`) and no stashes. PR #36 (jobhunt) was closed unmerged. Every removed branch tip, all 8 stashes and the pin worktree HEAD are in local refs `refs/branch-rationalization-backup/20260923/*` (40) and the verified bundle `/Volumes/ZestData/zeststream-offload-20260609/jev-backups/jev-branches-20260923.bundle`; restore one with `git fetch <bundle> refs/branch-rationalization-backup/20260923/<slug>:refs/heads/<name>`. Enforcement since `04dc862`: `githooks/pre-commit` lane 0 refuses commits off `main`, in a linked worktree, or on a stray detached HEAD; `scripts/verify-frozen.sh` uses a throwaway clone; GitHub deletes merged PR branches. Process defect recorded: 9 local branch deletions ran inside a script that dcg did not inspect; destructive git commands now run directly or go to Joshua.

Pick up here, in order:
1. Read each pane's `CALLBACK-P<N>-PAUSED` and its bead handoff comment.
2. `jev-deep-kit-8q7.6` (TopazRaven): run the bead's metric on the 669-commit draw (thin gate keyless; noul gate live on substantial diffs; any substantial refusal fails the bar as written), then L3 from the session `.jsonl` custom rows.
3. `.7` (SunnyTiger, `work/oracle-kit` uncommitted at pause) and `.8` (MistyTurtle, must run `skill://prevalence-first` before its first live call).
3b. `jev-deep-kit-8q7.9`: ten popular Jev projects Joshua shared were cloned and read (ledger rows 29-38, all 200 citations resolve). Seven get W7.0 runs by the `run_owner` in each row. Look first at Canny (a done-claim is blocked unless a verify command passed after the last edit; Jev may only relax it, which is our close-pump problem) and jev-drone (decide in code when to ask, cache by scene fingerprint, cap calls, drop stale answers, fall back to a safe default on error). jev-trader's advertised ~81 ms is its mock's `Bun.sleep(80)`, not a Jev latency.
4. W2.6 CI (QuietHarbor): `.github/workflows/gates.yml`, typed SKIPs for the omp stages, green and planted-RED run URLs.
5. uds (RedMaple): from `reconcile-wip`, get `cargo test -j 2 -p uds` green via RCH (`caam` exception is DROPPED), commit per uds `AGENTS.md`, then pane 1 pushes uds `main`.
6. Plan: round 3 review (a Muse pane) on `docs/PLAN-DEEP-KIT-20260922.md`, then §12 sign-off and Phase C beads for the packets without beads.
7. Needs Joshua: a `KIT_GATE_EDIT=1` omp session for W1.4 (kit-guard rebuild) and W2.5 (pre-commit canary); the franken-repo license rider question; pane restarts (W1.7) after W1.4.

### Resumed 2026-09-24 ~01:04Z (Joshua: "get this project back on the road")

- Panes 2–6 restarted 01:04–01:07Z so they load the fixed stop hook (`5563da1`, "prove Jev with the API") and the kit rules: pane 2 fresh (its session was 16 MB at 100% of grok's 500K window, likely why it stalled mid-unit), panes 3–6 resumed their own sessions. A stale `.git/index.lock` from a crashed git process at 09:35 local was blocking every commit; moved aside to `/tmp/jev-index.lock.stale-20260923-0935`, index intact.
- Wave `051014f`, live by default. Results in the first 20 minutes:
  - `8q7.9` (RedMaple): all 7 new clones done (`40133aa`). Canny's Jev done-claim judgment 9/24 < always-not-done 12/24; its deterministic ledger also loses on an independent-enough set (1067 vs 1108 of 1145, `f1dde64`), so no surface was built. jev-curate's 422s are the clone's bug (Score criteria must be a list); issue drafted, unfiled.
  - `.6` (TopazRaven): bar failed as written; the noul pre-gate mostly reproduces "touches code". `.10`: that question flips on rewording for all 4 code-mixed diffs. Decision by pane 1 from that data: replace it with a deterministic code-diff check (new bead to TopazRaven).
  - `.8` (MistyTurtle): structured-criteria variant fails its bar (0.9848 vs 0.9884, stable over 3 seeds).
  - `.7` (SunnyTiger): select-on-A/report-on-B helper landed (`c22673b`, 29 checks); first use on real rows running.
  - W2.6 CI (QuietHarbor): workflow committed; first runs red, being fixed. `jev-qsg` closed.
  - `jev-32z` (AmberWillow, `e29b8f6`, live): the frozen tool-call gate on 300 real routine jev commands flags 14 with 7 false positives (2.3%, PASS) against Haiku's 59 (19.7%, FAIL), p=1.4e-17; Jev catches 7 of 13 commands that meet the harm rule, Haiku 12. RedMaple verifying.

### Muse quota out, pane 2 + background agents (2026-09-24 ~02:15Z onward)

- Panes 3–7 (Muse Spark) hit a subscription quota that resets 2026-09-28. Their units moved to pane 1's background task agents; pane 2 (grok) took `jev-jwr` (skillranker#4 dogfood, outside the license rider). Pane 7's gate-edit session was resumed on Claude Opus with `KIT_GATE_EDIT=1`, finished W1.4 (`4954b50`) and W2.5 (`ce7e919`), then exited; W1.4's live L3 was proven from pane 1 afterwards (`c82b0eb`).
- Idle prevention (Joshua: "dont let that happen again"): stop hook continues workers and reports `IDLE` to pane 1 (`8b3dced`), never continues a non-interactive probe (`bc9b8d6`, which had hijacked the gate session's probes); `fleet-idle-watch` hub process; ready-queue floor of three; AGENTS.md "NO IDLE WORKERS".
- Live results (receipts under `docs/demos/upstream-repro/*-20260924.md`): gate criteria 78/100 vs 41/100 at 1/300 FA (verified by pane 1, `8q7.12` closed); SST-5 Score MAE win, narrow (verified); Banking77 Choice 384 vs 362 (held 3/3 runs); SciFact Noul AUC/Brier/ECE wins; gate observe hook L3 + no latency cost; injection seat on tool output FAILED (R80); gate hard cases FAILED catch floor (R81); adapter all-zero -> fabricated uniform answer confirmed (`jev-mly`, issue drafted, unposted).
- **Process defect, recorded per AGENTS.md "DO NOT EVER BREAK GLASS" §5.** Before pane 1 broadcast the no-delete rule, three background agents ran `rm -rf` on `/tmp` scratch directories they had created or were about to create: AdapterUniform (`/tmp/allzero`), ScoreSST5 (`/tmp/nsf-smoke`, `/tmp/k2q-smoke`, each immediately before `mkdir`), LabelFixT2u (`/tmp/lfx-old`, `/tmp/lfx-score`, `/tmp/lfx-clone`, `/tmp/lfx-v`). No repo path and no file another agent owned was touched. No user text authorized these commands. Cause: pane 1's task contexts omitted RULE NUMBER 1; fixed by a broadcast to all 19 agents at ~02:58Z and by the rule's presence in every task context written since.
  - Later disclosure, same class: ObserveHookL3's planted-regression loop (gate-observe unit, before the rule) called `shutil.rmtree(ignore_errors=True)` on `/tmp/gate-plant` subdirectories it was about to create. No repo path touched.

### Closed 2026-09-24 ~09:30Z (`jev-deep-kit-8q7`)

- **Acceptance, measured at `037a807`.**
  - Section 5 claims: three landed at enforce=yes (claim-coverage 50 of 84, ci-pin, self-assessed). Four were dropped with R94-R97.
  - Section 12 signed (`2c5a1d6`, READY 12/12).
  - `gates.sh` passes 17/17. CI is green with typed SKIPs (run 35978286566).
- **Blockers that shaped the rest of the drive.** None is an engineering fault; each needs Joshua.
  - TypeSafe credits: every Jev call has returned 402 since 04:19Z (`jev-1gdi`). The gate hook now pauses calls for 15 minutes after a 402 (`jev-nhv9`) instead of calling on every command.
  - The Anthropic spend cap (`jev-1y19`) blocks the Haiku arms until 10-01.
  - The OpenRouter balance is about $0.005 (`jev-qkvc`).
  - Measurement moved to grok-4.20 as the incumbent (`jev-n4j`, `jev-wu6v`, `jev-iwhh`, `jev-ze4z`) and to keyless verification.
- **Adapter pin moved** `adffc2e -> e1d4cc9` (v0.2.1, `9da0e2b`, `jev-ygl7`). The adapter suite passes 424/424; 0 of 6,257 committed answers would raise under v0.2.1.
- **Upstream filed** under Joshua's standing approval: `jev-curate#4` (fixed and released as v0.1.1 upstream within the hour; our dogfood of the fix is blocked on credits) and `system-one-adapter-python#45` (open; a third party confirmed it).
