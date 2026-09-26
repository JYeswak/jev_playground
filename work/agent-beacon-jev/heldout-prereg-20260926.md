# Held-out Beacon question comparison preregistration

- Bead: `jev-b4jj`
- Frozen before live calls: 2026-09-26
- Prior sample excluded: all 70 IDs in `notes/deep/false-close-census.tsv` at SHA-256 `7b6cd56b0f02d2830c1faf9c2970383656db062afe0488d2df67488529072edb`, including every row used by `jev-6o2a`.
- Held-out source: `.beads/issues.jsonl` at SHA-256 `1377c868d9496883615a4779bc5aa0f39b1b105b02819e0d9ea6439157c7a10b`; closed rows with `closed_at >= 2026-09-25`, excluding the 70 census IDs. Frozen rows: `work/agent-beacon-jev/heldout-rows-20260926.jsonl`.
- Held-out size: 73 rows; labels derived before live calls by the committed B13 rule: 70 `OK`, 3 `REPAIRABLE`.

## Label derivation

The ground truth is not a Jev answer. For each closed row, `OK` iff `len(close_reason) >= 20` and at least one of `names_command`, a resolving commit SHA, or an existing referenced path is present. Otherwise `REPAIRABLE` when the row is supported by the committed outcome ledger. The derivation records only the row's title, close reason, close timestamp, and final label; the label is excluded from every live state.

## Frozen live arm

One request per held-out row, Beacon's exact three Nouls and exact state shape from `agent-beacon/cli/beacon/internal/learning/evaluator.go`:

- `task_success`: Did the trace complete the user's engineering task successfully?
- `reusable_correction`: Does the trace contain a correction or debugging pattern that future agents should reuse?
- `evidence_supported`: Is the reusable lesson supported by concrete events in the trace?

The state contains the trace ID, title, harness `bead-census`, one close event with title and close reason, `rubric_version`, and Beacon's pinned rubric hash. It excludes the ground-truth label and census-only fields. Model is pinned `jev-1.13.0`.

## Hypothesis and bar

Primary comparison: AUROC of `reusable_correction` alone versus AUROC of the mean of all three probabilities on this held-out set. The preregistered hypothesis passes only if:

1. `reusable_correction AUROC >= mean-of-three AUROC + 0.05`; and
2. `reusable_correction AUROC >= 0.70`.

AUROC uses the exact pairwise rule: OK score above REPAIRABLE scores 1, ties 0.5, below 0. The mean-of-three is Beacon's `evaluationScore` arithmetic mean. No question, threshold, label, or row may be changed after live answers.

Receipt must include per-row model IDs, three probabilities, both scores, source hashes, exact AUROCs, paired discordance counts/p-value, input/output tokens, and spend at `$0.042/M` input tokens (output free). No automatic approval or memory write is part of this test.

Boundary: these are our newly closed bead outcomes, not a random sample of all agent sessions and not the original 70-row sample. This measures question separation against this held-out outcome proxy, not Beacon production promotion quality.
