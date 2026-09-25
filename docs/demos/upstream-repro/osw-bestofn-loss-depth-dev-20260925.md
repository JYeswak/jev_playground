# OSWorld Best-of-N loss-depth dev preregistration

Bead: `jev-9gtw.2` (R104)
Pattern: confidence-gated routing / candidate selection with a fixed Choice or Noul fan-out.
Lane: **live TypeSafe only** for the dev arms; no comparator, no result text in any arm state.
Model: `jev-1.13.0`, pinned before the first call.

## Question

Does adding the public OSWorld task instruction, neutralizing candidate labels, or replacing one
multi-way Choice with per-candidate Nouls improve selection of the candidate whose official reward
is highest, without changing the candidate evidence or the fixed task slice?

The original failure is that `state.task` is only the domain/task-key path component. The baseline
therefore has no task instruction. The goal arm adds the task's public instruction; it never reads
`result.txt` or the grader.

## Frozen source and task list

- Source repository: `xlang-ai/OSWorld`.
- Pinned source SHA: `b138d348256078fa634fc3b73567a7337c793e6b`.
- Public instruction path for task `domain/id`: `evaluation_examples/examples/<domain>/<id>.json`.
- Committed task manifest: `work/osw-bestofn/dev_slice.json`.
- Manifest SHA-256: `154482ff5f277999c1a76331dee6e6c9819a0010904b9b6b6ba7841fdbd8898e`.
- Slice: 60 tasks, 20 `correct_none`, 20 `false_none`, 20 `wrong_pick`; labels are from the
  committed `live_receipt.json` choices joined with the committed keyless floor rewards and are
  not sent to Jev.

Each state contains the compact `traj.jsonl` action records and a bounded `runtime.log` tail for
all eight frozen candidate archives, plus the public task instruction. `result.txt` contents are
used only by the offline scorer and task-label join; no official result value, grader output, or
success label is in any live state, prompt, question, or arm output. An action string may mention a
file named `result.txt` as part of the candidate's recorded trajectory; that is not the official
result content. Candidate archive names are stripped from the live state before serialization.
Candidate IDs remain positional `c0` through `c7`; the prompt forbids treating IDs as correctness
evidence.

## Pre-registered arms

Every arm uses the same 60 tasks, candidate evidence, model, timeout, retry setting, and state
serializer. Each arm differs from `original` by exactly one variable:

| Arm | One variable relative to `original` |
|---|---|
| `original` | Baseline: no public task instruction; one Choice question; positional labels only. |
| `goal` | Add only `task_instruction` from the pinned public JSON task file. |
| `neutral` | Change only Choice criteria from positional labels to evidence-only descriptions. |
| `noul` | Replace only the multi-way Choice with one Noul per candidate, each with the fixed true/false criteria below. |

Choice criteria: select `c0`–`c7` or `none`; `none` means the supplied evidence is insufficient.
The Noul criteria are fixed: true means the supplied evidence establishes successful completion
of the stated task; false means it does not. The validator rejects missing or non-finite answers.
No arm carries `result.txt` contents, grader output, official reward, or a success label.

H5 is **not run in this four-arm dev batch**. If a terminal-status field is added in a later arm,
it must be built only from the final parseable `traj.jsonl` record's terminal fields and the final
`runtime.log` tail; no `result.txt` or grader-derived field may be used. The later prereg must name
the exact JSON keys and log lines before that arm is run.

## Calls and accounting

Each arm makes exactly 60 sequential requests, one request per task, with `maxRetries: 0` and a
20-second timeout. The receipt records each call's task key, `resolvedModel`, input/output usage,
latency, validation result, and the arm total. Spend is computed only as
`input_tokens * 0.042 / 1_000_000`; output is free. A non-empty resolved model is required for a
successful row; a failed row is retained rather than retried or replaced by a chat fallback.

## Primary metric and bar

Primary metric: mean official reward of the selected candidate, scored offline after the live
receipt against the committed floor receipt. Secondary metrics: exact completion (`reward >= 1`),
paired McNemar exact p-value versus the best single archive, and gap closed toward the keyless
oracle. The original bar is retained unchanged: at least **+0.03 mean reward** versus the best
single, exact-completion McNemar `p < 0.05`, and at least **30% of the mean-reward gap to oracle@8**;
all three are required. No arm is declared a win from confidence, response count, or a single row.

## Dev result before held-out selection

The four live arms completed with 60/60 valid rows and `resolvedModel = jev-1.13.0` on every
successful call. The pre-registered strict-improvement rule selected no variable:

| Arm | Mean official reward | Exact tasks | Input tokens | Spend |
|---|---:|---:|---:|---:|
| `original` | 0.0166667 | 1/60 | 477,436 | $0.020052312 |
| `goal` | 0.0166667 | 1/60 | 480,164 | $0.020166888 |
| `neutral` | 0.0000000 | 0/60 | 481,756 | $0.020233752 |
| `noul` | 0.0000000 | 0/60 | 511,156 | $0.021468552 |

The four-arm total was 1,950,512 input tokens and $0.081921504. Per-call resolved models and usage
are retained in `work/osw-bestofn/dev_live_receipt.json`. `goal` recovered one baseline failure but
regressed one baseline success, so its mean tied `original`; neutral and Noul recovered zero. No arm
was eligible under the locked strict-improvement rule.

## Held-out selection rule

Before any held-out call, score all four dev arms using the primary metric. An arm is eligible to
carry forward only if its dev mean reward is strictly above `original`; ties do not count. If no
arm is eligible, run `original` on the held-out set and report that no variable earned selection.
If exactly one arm is eligible, run that arm. If multiple arms are eligible, combine their winning
variables: add the public instruction if `goal` is eligible, use neutral criteria if `neutral` is
eligible, and use per-candidate Nouls if `noul` is eligible. This combination is the sole
pre-registered multi-variable held-out design; no prompt or threshold changes after seeing results.

The exact manifest is `work/osw-bestofn/heldout_slice.json` (SHA-256
`9fa3f207783795bac4dd160bcfbcddf91652a5ddc54eea633b8fde18da2c7521`, N=57). **Correction:** this
set is the sorted complement of the 60 dev tasks inside the original 361-task failure-class union,
reconstructed from committed prior `live_receipt.json` choices joined with `floor_receipt.json`
rewards. Because the set was selected using the prior outcome, it is not an independent held-out
retest and its result is NOT-SCORED. A valid retest must use all tasks in a different fixed run set
or step budget, with the selection committed before any outcomes are read.

## Held-out arm — NOT-SCORED

The selected `original` arm completed 57/57 calls with no validation failures; every successful row
resolved to `jev-1.13.0`. It used 456,282 input tokens and cost $0.019163844. The run is retained
only for accounting and audit of the flawed selection; it is not evidence for the preregistered
bar. Its descriptive reward calculation (`0.0093946` vs `0.3015857` best single) is not a held-out
score and must not be reported as a retest result.

The sanitized live accounting receipt is `work/osw-bestofn/dev_live_receipt.json`; it records each
call's task, choice, resolved model, token usage, latency, and validation status without raw state,
trajectory text, official result values, response probabilities, grader output, or secrets.

## Boundary

The live results are limited to this pinned OSWorld failure-class slice and do not claim that any
other task distribution or workflow will behave the same. The experiment does not measure MiniWoB,
a chat-model comparator, terminal-status H5, a different step budget, or a deployment policy.

## Valid held-out retest preregistration — PREPARED-NOT-MEASURED (2026-09-25)

This section answers R106's correction. It is committed before any retest call and after reading
`/Users/josh/.claude/skills/experimental-design/SKILL.md` (randomization, replication at the
unit of analysis, and no outcome-dependent selection) and
`/Users/josh/.claude/skills/statistical-power/SKILL.md` (SESOI, sensitivity analysis, and
reporting the detectable effect). The previous complement is permanently excluded: it was chosen
from Jev's prior failures and remains `NOT-SCORED`.

### Released run sets and fixed task list

The retest candidate pool is the pair of released, pinned Ouroboros OSWorld-Verified evidence
packages below. Both are complete 361-task `test_nogdrive` runs with screenshot-only observation,
one rollout, and a 100-policy-turn budget. This deliberately changes both the released run set and
step budget from R104's eight 15-step archives; the choice is based on public provenance and
matching task coverage, not per-task scores:

- `razzant/ouroboros-osworld-verified-sonnet46` at snapshot
  `0e8ad516a4eeaa586607ead400429885814e7633`, candidate `c0`, Apache-2.0.
- `razzant/ouroboros-osworld-verified-opus5` at snapshot
  `f52ebf2248ce0ce0c496db18f5e6edce631304fa`, candidate `c1`, Apache-2.0.

The fixed task manifest is `work/osw-bestofn/heldout_valid_slice.json` (file SHA-256
`7aa586ed485d48d8f35dde4bac9e6cea0d64705a49f5f041d31d715be897aea8`). Its 361 domain/task IDs
are lexicographically ordered; the separate digest below is the SHA-256 of the newline-joined ID
list, not of the JSON file:
`aafabe6fd1f06b7dcb2a3d57397722871ce909295ae3ce3556d5fdcf2e7586c3`. Before freezing it, the
Hugging Face tree API was read only for path metadata: each snapshot exposed 361 task-ID
directories, the two ID sets were equal, and no `result.txt`, `task_outcome.json`,
`results_summary.json`, reward, success, or status field was read. The call order is a fixed
seeded permutation of this manifest (`seed=20250925`); no task is added, removed, stratified,
or reordered after a response.

The state adapter will use only each candidate's published acting evidence
(`ouroboros_task_final.json`, restricted to action/tool/text records) and the bounded public
task key. It excludes `result.txt`, `task_outcome.json`, `results_summary.json`,
`feasibility_gate.json`, `reset_verification.json`, `task_run_manifest.json`, evaluator data,
and every score/status/reward/success field. Candidate archive names are replaced by positional
IDs `c0` and `c1`.

### One-variable arm

Only the `goal` arm runs. Relative to the already-defined `original` state, its sole change is
adding the public OSWorld task instruction from `xlang-ai/OSWorld@b138d348256078fa634fc3b73567a7337c793e6b`,
path `evaluation_examples/examples/<domain>/<id>.json`, the already-pinned task source used by R104.
Candidate evidence, positional IDs, serializer, task order, Jev model, timeout, retry policy,
question, and validator are unchanged. The instruction is never obtained from the candidate
trajectory, result, grader, or task outcome.

### Frozen bar and analysis

The R104 bar is unchanged:

1. Jev's mean official reward must exceed the best single candidate's mean by at least `0.03`
   reward units (three points);
2. exact-completion McNemar's exact two-sided `p < 0.05` versus that best single candidate; and
3. Jev must close at least 30% of the per-task `oracle@2 - best_single` mean-reward gap.

All three are required. `best_single` and `oracle@2` are computed only from the two frozen
candidate packages after the calls. No confidence threshold, question wording, tie-break, or bar
may change after the first retest response.

The task unit is one task, so `N=361` is the complete released task universe; no pseudoreplication
is claimed. A keyless sensitivity calculation using R104's committed per-task reward-delta SD
`0.485121` gives an approximate 80%-power two-sided paired-mean MDE of `0.07172` reward units
(7.17 points) at `alpha=.05` (`statsmodels 0.15.0`, SciPy 1.18.1). Using R104's discordance
rate `84/361`, the corresponding normal McNemar planning MDE is approximately 7.11 percentage
points. Thus this fixed full-universe retest can reliably detect effects around seven points,
not the three-point bar; the limitation is reported rather than hidden.

### Cost, failure, and stop rules

The four-arm dev run measured `480,164 / 60 = 8,002.733` input tokens per `goal` call. The
361-call retest estimate is `2,888,987` input tokens and `$0.1213374428` at `$0.042/M` input
tokens; output is free. `maxRetries=0`, no comparator, and no chat fallback.

HTTP `401` or `402` is a hard stop: preserve the partial receipt, mark the run `NOT-SCORED`,
make no retry, and do not report a bar result. A task-level validation failure is retained as a
failed row and does not trigger a replacement call. The run also stops before any call if either
source snapshot, task-set digest, allowed-member list, or state-leak guard differs from this
preregistration.

Boundary: this is `PREPARED-NOT-MEASURED`; no retest call, score, bar verdict, or omp wiring is
claimed here. The external run packages are attributed to Razzhigaev/Ouroboros and OSWorld; their
published aggregates are not used as Jev outcomes.
