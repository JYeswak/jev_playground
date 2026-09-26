# Draft upstream issue — validate the Jev promotion rubric against held-out outcomes

**Status: draft only; not filed.** Joshua decides whether to post this to `Asymptote-Labs/agent-beacon`.

## Title

Validate the three-Noul learning promotion rubric against held-out session outcomes

## Body

The learning evaluator currently promotes a completed evaluation when `task_success >= 0.50` and the mean of the three rubric probabilities is `>= 0.60` (`cli/beacon/internal/learning/candidate.go:11-22,36-55`). The evaluator asks:

- `task_success`: Did the trace complete the user's engineering task successfully?
- `reusable_correction`: Does the trace contain a correction or debugging pattern that future agents should reuse?
- `evidence_supported`: Is the reusable lesson supported by concrete events in the trace?

I ran a preregistered, live validation of that exact rubric at `jev-1.13.0` on 70 committed session-outcome rows from our own false-close census. The corpus and labels were frozen before the first API call:

- Source corpus: `notes/deep/false-close-census.tsv`, source commit `62355af7`, SHA-256 `7b6cd56b0f02d2830c1faf9c2970383656db062afe0488d2df67488529072edb`
- Ground truth: 40 `OK` and 30 `REPAIRABLE`, from the committed B13 rule; no Jev output was used to label rows
- Preregistration: commit `cdcc2445`, `work/agent-beacon-jev/prereg-20260926.md`
- Beacon source: `c8d56ada361eb7cb4d1eae1fe7b0e2fe69f36558`
- Rubric hash: `sha256:a1e00fed9327beffc443b833eeda73f8fa6021e37d7399cb4ed29f989b5fe1d9`

### Result

Primary metric: AUROC for predicting `OK` versus `REPAIRABLE`.

| Score | AUROC |
|---|---:|
| Majority constant | 0.5000 |
| `close_reason_len` baseline | 0.6921 |
| `task_success` | 0.6054 |
| `reusable_correction` | 0.7821 |
| `evidence_supported` | 0.6888 |
| Mean of all three Beacon questions | 0.7475 |

The preregistered bar was AUROC `>= 0.70` and at least `+0.10` over the length baseline (`>= 0.7921`). The mean score reached the absolute floor but not the baseline-improvement margin: gain `+0.0554`; `bar_met=false`.

The weakest discriminator was `task_success` (AUROC `0.6054`), while `reusable_correction` was strongest (`0.7821`). This matters because `task_success` is also a hard promotion precondition: a score below `0.50` blocks promotion regardless of the mean. The run does not claim that the `0.50` pointwise threshold is miscalibrated; it identifies task-success separation as the weakest component of the current promotion rubric.

### Reproduction evidence

- Live receipt: `work/agent-beacon-jev/receipt-20260926.json`
- Per-row validated answers: `work/agent-beacon-jev/live-rows-20260926.jsonl`
- EVAL entry and commit: `72293bcc41d9c9f6e64a7f603046d1714fbf59e5`
- 70 calls, model `jev-1.13.0`
- 46,655 input tokens, 4,270 output tokens
- Spend: `$0.001960` at `$0.042/M` input tokens; output free

### Limitations

This is a retrospective census of bead outcomes, not a random sample of all agent sessions. `OK`/`REPAIRABLE` is an outcome-derived label, not a human trace-quality annotation. The run did not exercise Beacon's production promotion side effect, persistence layer, or an omp seam.

Would you consider adding a held-out validation of the three questions and documenting whether the `task_success` precondition is intended as a calibrated decision threshold or only a conservative safety gate?
