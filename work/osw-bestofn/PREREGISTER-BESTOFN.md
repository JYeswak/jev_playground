# Best-of-N OSWorld-Verified selection — preregistration

Bead: `jev-jy7t.1.2`
Status: preregistered before any Jev call.
Model under test: `jev-1.13.0` through the official TypeSafe SDK.
Comparator models: none.

## Corpus and pool-selection rule

Source: Hugging Face dataset `xlangai/ubuntu_osworld_verified_trajs`, repository root at the
measurement date. The archive universe is fixed to root files whose names contain `15step` or
`15steps`, end in `.zip`, and are not `results_only` artifacts. This is the common 15-step
OSWorld-Verified setting; no 50/100/300-step archive is eligible.

The pool is fixed by an ordered allowlist before any result, trajectory, or runtime member is read.
The selector tests these root archives in exactly this order and takes the first eight with one
official result row for each of the 361 OSWorld-Verified tasks:

```text
autoglm_15steps.zip
claude-3-7-sonnet-20250219-15steps.zip
claude-4-sonnet-20250514-15steps.zip
claude-sonnet-4-5-20250929_15steps.zip
jedi-7b-o3-15steps.zip
opencua_agent-opencua_qwen2_7b-cot_l2-action_history-3image-Ubuntu-15step.zip
qwen2.5-vl-32b-instruct_15step.zip
qwen2.5-vl-72b-instruct_15step.zip
```

Each candidate must have exactly 361 result rows; an invalid candidate is recorded as excluded and
the next preregistered candidate is used. If fewer than eight are valid, the experiment aborts.
No score, model label, trajectory content, or runtime text selects among valid candidates. The
selected eight filenames and result counts are frozen in the keyless oracle receipt before any
trajectory or runtime member is read.

Each official `result.txt` row is a finite reward in `[0,1]`, not necessarily an integer. The
reported rate is the mean reward multiplied by 100 (percentage points). For paired McNemar, an
exact completion is `result >= 1.0`; partial rewards remain in the mean-rate metric but are not
counted as exact completions.

This fixed-allowlist rule supersedes the earlier score-ranked draft in commit `7f908b7`; the
superseding amendment is committed before the keyless floors and before any live call. It is a
selection-over-public-runs experiment, not an unbiased estimate of a new agent's single-run
performance. The official `result.txt` is the only ground truth.

## State and privacy boundary

For each selected archive and task, later live state construction may range-read only:

- that task's `traj.jsonl` member, compacted to action type/name and bounded text fields;
- that task's `runtime.log` member, truncated to the fixed tail window;
- that task's `result.txt` row.

Screenshots and every other ZIP member are forbidden. Receipts contain archive IDs, task IDs,
result booleans/counts, selected candidate IDs, probabilities, latency, token usage and spend only.
No trajectory text, screenshot, raw runtime log, key, or response body is committed.

## Keyless floors and oracle

From the frozen pool's official `result.txt` rows:

- `oracle@8`: a task is successful if any of the eight selected runs succeeds;
- `best_single`: the highest-success selected run;
- `random`: deterministic seeded uniform candidate selection, seed fixed in the receipt;
- `shortest`: candidate with the fewest `traj.jsonl` actions, lexical candidate-ID tie-break;
- `claims_success`: candidate whose bounded final runtime text claims success, lexical tie-break.

Each floor is computed without Jev, before live calls. The oracle and floors are not claims about
Jev; they establish the task-level prevalence and the attainable ceiling in this released pool.

## Live bar — fixed before the first live call
**PASS:** Jev's selected candidates have a mean official reward at least 3 percentage points higher
than `best_single`, with paired McNemar p < 0.05 on exact completions, and close at least 30% of
the mean-reward gap between `best_single` and `oracle@8`:

```text
jev_mean_reward - best_single_mean_reward >= 0.03
mcnemar_exact_p < 0.05  # exact completion means result.txt reward >= 1.0
(jev_mean_reward - best_single_mean_reward) / (oracle_mean_reward - best_single_mean_reward) >= 0.30
```

If `oracle_mean_reward == best_single_mean_reward`, the gap-closure term is vacuous but the
three-point and McNemar requirements remain mandatory.

**KILL:** Jev is no better than `best_single`, or any required live state cannot be constructed
from the permitted members, or the official result row cannot be joined unambiguously.

No threshold, question wording, candidate ordering, tie-break, or bar may change after the first
live call. Spend is reported from returned `usage.input_tokens` at the documented Jev price
($0.042/M input tokens; output free).

## Frozen floor tie-breaks

For `shortest`, the action count is the number of JSONL records in that candidate's `traj.jsonl`; ties break by candidate archive name. For `claims_success`, inspect only the final 12,000 characters of that candidate's `runtime.log` and mark a claim when the case-insensitive regex `(?:task\s+)?(?:completed|succeeded|success(?:ful|fully)?)` matches; multiple matches tie by archive name, and no-match tasks tie to the first archive name. The floor's success value still comes only from the selected candidate's official `result.txt` row.
