# x7-gate-rules receipt

**Verdict: LOSES.** The combined deterministic rules do not make recorded Jev redundant on this paired sample. User's rule-out condition fails: weighted harm catch is 7/47 (14.89%) for DCG + pre-rule versus 47/47 (100%) for Jev, and weighted no-harm false-alarm rate is 242.44/1,637 (14.81%) versus 22.88/1,637 (1.40%). The result does not generalize beyond the captured command view or establish that Jev should be deployed elsewhere.

## Inputs and join

- `work/jev-1lim/labels-A.jsonl` and `labels-B.jsonl`: 396 rows each; `adjudicated.jsonl`: 29 rows. Reconstructed labels use the existing `live.mjs` rule (agreement label, else adjudicated label). No duplicate IDs, missing adjudications, or final-label mismatches against recorded rows.
- `work/jev-1lim/live-results.jsonl`: all 396 rows are `scored`, model `jev-1.13.0`. `work/jev-1lim/manifest.jsonl` agrees with the recorded live metadata for all IDs. `var/agent-tmp/jev-1lim/commands-A.jsonl` joins all 396 IDs.
- The supplied command view is at most 200 characters. Its SHA-256 matches recorded `cmdSha` on 100/396 rows and differs on 296/396; the suffix/full command is not available here. `work/jev-1lim/live.mjs:21-24,29-38` passes this same command-view string to Jev, so this comparison is paired on the recorded projection only. No claim about full original commands.
- Reconstructed labels in `row-scores.jsonl:1-396`: 47 `harm:*`, 349 `no-harm`; 29 A/B disagreements were adjudicated. By stratum: flagged 47 harm / 149 no-harm (196 rows); random-unflagged 0 harm / 200 no-harm. Weighting follows `work/jev-1lim/prereg.md:10-20`: 1.0 per flagged row, 7.44 per random-unflagged row; weighted denominators are 47 harm and 1,637 no-harm.

## Method

- DCG 0.15.2 evaluated each command view with `nice -n 10 dcg test --stdin --format json --robot --dialect posix --agent omp`. Only `decision=deny` counts as a deterministic trigger; allow/warn do not. 396/396 returned parseable decisions; 82 deny, 314 allow, zero warnings/errors. Decision sources: 78 `legacy_pattern`, 3 `pack`, 1 `heredoc_ast`; the 78 legacy-pattern denials did not expose individual rule IDs. Source: `row-scores.jsonl:1-396`.
- The gate-cascade destructive pre-rule was run through the existing `matchPrerule` implementation in `.omp/hooks/post/jev-gate-observe.ts:451-555`; it matched 0/396 views. This pre-rule routes matches to paid Jev; it is not itself an execution block. Source: `row-scores.jsonl:1-396`.
- DCG test output confirms OMP as the explicit agent and the current configured override (control `git stash drop` returned deny / `config_override`). `dcg packs` listed 24 enabled packs, including `core.filesystem`, `core.git`, `zeststream.shared_worktree`, and `zeststream.upstream_issues`; `strict_git` is disabled. No shell command from the dataset was executed.
- Combined trigger is `DCG deny OR pre-rule match`; because the pre-rule had no matches, its result equals DCG. Per-row labels and predictions, without command text, are in `row-scores.jsonl`.
- Post-write verification over persisted `row-scores.jsonl`: 396 rows, 396 unique IDs, all rows conform to the closed score schema, and no command field/text can be emitted. Recomputed Jev (47 TP, 10 FP) and combined-rule (7 TP, 75 FP) counts and weighted FP totals match the receipt. `dag-input.jsonl` is empty.

## Scores

| Arm | TP / harm | FP / no-harm | Sample catch | Sample false-alarm rate | Weighted catch | Weighted false-alarm rate |
|---|---:|---:|---:|---:|---:|---:|
| Recorded Jev | 47/47 | 10/349 | 100.00% | 2.87% | 100.00% | 1.40% |
| DCG | 7/47 | 75/349 | 14.89% | 21.49% | 14.89% | 14.81% |
| Cascade pre-rule alone | 0/47 | 0/349 | 0.00% | 0.00% | 0.00% | 0.00% |
| DCG + pre-rule | 7/47 | 75/349 | 14.89% | 21.49% | 14.89% | 14.81% |

Stratum detail: Jev false alarms are 8 flagged + 2 random-unflagged; DCG false alarms are 49 flagged + 26 random-unflagged. Weighted FP numerators are therefore 8 + 2×7.44 = 22.88 for Jev and 49 + 26×7.44 = 242.44 for DCG. The pre-rule-only arm is the lowest-cost in-process deterministic baseline in this comparison and matches the majority constant on this set.

## Baselines, calls, latency, spend

- Majority constant (`no-harm`): 349/396 sample accuracy (88.13%), 0/47 catch, 0/349 false alarms; weighted accuracy 1,637/1,684 (97.21%). Source rows and weights: `row-scores.jsonl:1-396`, `work/jev-1lim/prereg.md:10-20`.
- Cheapest in-scope deterministic component (pre-rule only): 0/396 matches; same scores as the no-harm constant. It was not tuned or selected by performance.
- The Jev comparison reuses `live-results.jsonl`; no Jev or other model call was made and new experiment spend is **$0.00**. Recorded Jev rows contain 318,056 input tokens; at the documented $0.042/M input rate this is an estimated prior-run spend of $0.01336, not spend from this experiment. Source: `live-results.jsonl:1-396` and the model pricing in `AGENTS.md`.
- Existing Jev latency from `live-results.jsonl:1-396`: n=396, median 151 ms, nearest-rank p95 354 ms, mean 180.97 ms, range 111–476 ms. No new API latency was incurred. DCG replay wall latency was not instrumented.
- DCG processing was sequential at `nice -n 10`, with one-minute load checked every 20 rows and a hard stop above 80. No stop was triggered.

## Integrity and boundary

- Selected sections of `work/jev-1lim/final-receipt.json` and the last three rows of `live-results.jsonl` were read before the analysis plan, exposing aggregate and row-level outcome information. The comparison is not blind to all outcomes. The user-fixed criterion was not changed. No source/test/bead/switch was edited; the already-committed test file was not touched by this experiment. No files outside `var/agent-tmp/dogfood/x7-gate-rules/` were written by this experiment.

**DAG consequence:** none. This comparison does not authorize an implementation task or scope change; conductor owns DAG actions.
