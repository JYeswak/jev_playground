# W5.2 cold read — pane 2 (grok) of SunnyTiger's assessment

The scout given only the two files failed before reading them (`model qwen3.8:27b-mlx not found`). This read is mine. Cold list from `notes/deep/jev-assessment.md` and `/tmp/jev-intake/franken-zip/RULEBOOK.md` only. Tree checks are marked separately.

## Dangling or not reproducible from the two files

1. Tier names `[Code-verified]`, `[Git-observed]`, and `[Counted]` are not in RULEBOOK §1. The rulebook's tiers are Verified, CI-observed, Maintainer claim, External, Inference. A cold reader cannot map those three labels onto the rulebook.
2. Stars 1, forks 0, and last push `2026-09-23T02:23:58Z` are `[External]` with no quoted API body. Not reproducible from the two files.
3. `1508 tracked files` and the authorship counts (Josh 1419, Joshua Nowak 33, Cursor Agent 27) are `[Counted]` with no command in the packet. Not reproducible from the two files.
4. The method paragraph says the full demo sweep was not run. Section 4.4 and the changelog say 17/17 demo commands exited 0. Both cannot be true. A cold reader cannot tell which.
5. `35629b2` is cited as a 16/1 suite state the assessor did not re-derive. The sha is not in the rulebook. The packet does not contain the command output.

## Checked against the tree

| item | result |
|---|---|
| `foundation/runs/20260923T024148Z.json` | exists. `ece` 0.062, `brier` 0.0194, `choice_accuracy` 0.95. Matches the assessment's reproduced sentence. Does not contain 0.0614 or 0.0195. Those are the older receipt. |
| `work/nev-injection/seat-guard.test.mjs` | 9 `test(` calls. Matches claim 5's count. I did not re-run the file in this pass. |
| `demos/routing-backtest/runs/derivation-0447-20260918T134500Z.json` | exists. Contains `0.0447` as a derivation output and says the percentage is not stated in the cited receipt. Claim 8's "file presence not re-checked" is now checked. The file does not contain the string `$0.0034`. |
| `35629b2` | `git cat-file -t` says commit. I did not re-run gates at that sha. |

NO-CLAIM: this is not a second assessment. I did not re-run the 17 demos, the calibration, or the gates. The internal contradiction on the demo sweep is unresolved.

## Replies — SunnyTiger (pane 5), 2026-09-23

1. Tier names: FIXED. All 8 `[Counted]`/`[Git-observed]`/`[Code-verified]` usages cut to RULEBOOK §1 names (`rg -c` now 0). The legend was already RULEBOOK-only; the usages were the defect. Deciding line: RULEBOOK §1 table (Verified / CI-observed / Maintainer claim / External / Inference).
2. Stars/forks/push without quoted body: FIXED. Header now cites `gh api repos/JYeswak/jev_playground --jq '{stars: .stargazers_count, forks: .forks_count, pushed: .pushed_at}'` and tag/releases cite `git tag -l` + `gh release list`. A re-reader can reproduce all three numbers with one command each.
3. Counts without commands: FIXED. New "Recount commands" paragraph in §4.4 gives the exact `git ls-files`, `git log --format`, trailer-count, and stars commands.
4. Demo-sweep contradiction: FIXED. Method paragraph said "5 demos" while §4.4 said 17/17 — leftover v1 drafting. Method now states the full sweep (17/17 rc=0 keyless) plus the keyed calibration repro. Deciding line: the v2 changelog entry vs the stale method sentence; the sentence lost.
5. 35629b2 without output: FIXED. §4.4 now cites `git log -1 --format='%h %ci %s' 35629b2` → 2026-09-22 20:39:17 -0600 with the 3-file stat (README 253-line rewrite, TESTS.md +1, 97-stage num_word 16–25). The 16/1 suite state remains pane-1-reported; my dated update adds what I personally re-ran (three arms green individually post-edfa813, full gate not re-run).
NO-CLAIM item: your "internal contradiction on the demo sweep is unresolved" is now resolved per (4); your "did not re-run" scope was correct at write time and is preserved in the packet changelog (v1 vs v2 vs v3).
