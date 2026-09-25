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
  committed keyless floor receipt and are not sent to Jev.

Each state contains the compact `traj.jsonl` action records and a bounded `runtime.log` tail for
all eight frozen candidate archives, plus the public task instruction. `result.txt` is used only by
the offline scorer and task-label join; it is not in any live state, prompt, question, or arm
output. Candidate archive names are stripped from the live state before serialization. Candidate
IDs remain positional `c0` through `c7`; the prompt forbids treating IDs as correctness evidence.

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
No arm carries `result.txt`, grader output, official reward, or a success label.

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

## Held-out selection rule

Before any held-out call, score all four dev arms using the primary metric. An arm is eligible to
carry forward only if its dev mean reward is strictly above `original`; ties do not count. If no
arm is eligible, run `original` on the held-out set and report that no variable earned selection.
If exactly one arm is eligible, run that arm. If multiple arms are eligible, combine their winning
variables: add the public instruction if `goal` is eligible, use neutral criteria if `neutral` is
eligible, and use per-candidate Nouls if `noul` is eligible. This combination is the sole
pre-registered multi-variable held-out design; no prompt or threshold changes after seeing results.

The held-out task set is the deterministic complement of the 60 dev tasks in the committed
`floor_receipt.json` failure-class union (`correct_none`, `false_none`, `wrong_pick`), sorted by
task key. Its state is rebuilt from the same pinned public task files and allowed trajectory and
runtime members, with a different task set and the same fixed evidence window. The held-out arm is
scored with the same original bar above.

## Boundary

This preregistration does not claim that any arm is better before live results. It does not measure
MiniWoB, a chat-model comparator, terminal-status H5, a different step budget, or a deployment
policy. A TypeSafe API failure stops that arm with an explicit failure receipt; it is not converted
to a local answer.
