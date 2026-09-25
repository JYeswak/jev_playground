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

The eligible pool is selected mechanically after reading only each candidate archive's official
`result.txt` member through HTTP Range reads:

1. Keep an archive only if `result.txt` contains one official scored row for each of the 361
   OSWorld-Verified tasks. A missing, duplicate, malformed, or non-361 archive is excluded and the
   exclusion is recorded by filename and reason.
2. Compute each archive's official success count from its `result.txt` rows only. A row is success
   exactly when the official result field is the success value used by that file; no trajectory
   text, screenshots, runtime logs, task metadata, or model names influence the score.
3. Sort eligible archives by descending official success count, then ascending filename as the
   deterministic tie-break. Select the first **N=8** archives.
4. Freeze the selected filenames and their result counts in the keyless oracle receipt before any
   trajectory or runtime member is read. No archive can enter because its trajectory looks good.

The pool rule is intentionally score-ranked, as the bead permits “top 8 by published score at one
step budget.” It is a selection-over-public-runs experiment, not an unbiased estimate of a new
agent's single-run performance. The official `result.txt` is the only ground truth.

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

One Jev Choice per task over the eight candidate IDs plus `none`, with compact text-only state.
The official evaluator's success row for the selected candidate is the outcome. No comparator model
runs.

**PASS:** Jev's selected candidate succeeds on at least 3 percentage points more tasks than
`best_single`, with paired McNemar p < 0.05, and closes at least 30% of the gap between
`best_single` and `oracle@8`:

```text
jev_rate - best_single_rate >= 0.03
mcnemar_exact_p < 0.05
(jev_rate - best_single_rate) / (oracle_rate - best_single_rate) >= 0.30
```

If `oracle_rate == best_single_rate`, the gap-closure term is vacuous but the +3-point and
McNemar requirements remain mandatory.

**KILL:** Jev is no better than `best_single`, or any required live state cannot be constructed
from the permitted members, or the official result row cannot be joined unambiguously.

No threshold, question wording, candidate ordering, tie-break, or bar may change after the first
live call. Spend is reported from returned `usage.input_tokens` at the documented Jev price
($0.042/M input tokens; output free).

## Frozen floor tie-breaks

For `shortest`, the action count is the number of JSONL records in that candidate's `traj.jsonl`; ties break by candidate archive name. For `claims_success`, inspect only the final 12,000 characters of that candidate's `runtime.log` and mark a claim when the case-insensitive regex `(?:task\s+)?(?:completed|succeeded|success(?:ful|fully)?)` matches; multiple matches tie by archive name, and no-match tasks tie to the first archive name. The floor's success value still comes only from the selected candidate's official `result.txt` row.
