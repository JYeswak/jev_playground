# R112 retry — size-gated Best-of-N over the frozen eight-archive OSWorld pool

Bead: `jev-jjwt`
Status: **PREPARED-NOT-MEASURED**; no Jev call has been made for this retry.
Model under test: `jev-1.13.0`, official TypeSafe SDK/client.
Comparator: none.

## Question

Can a single Jev Choice over eight released OSWorld trajectories select a candidate whose
official reward beats the best single archive on a task split that R112 did not call?

This retry exists because R112's 337-task, two-archive run selected below its best single
archive (`work/osw-bestofn/live_receipt_r3.json`: 0.8796197 vs 0.9002621 mean reward), and
12 input-limit refusals accounted for 71% of that run's measured loss. The frozen eight-archive
floor has headroom (`work/osw-bestofn/floor_receipt.json`: oracle mean 0.6749819 vs best single
mean 0.4625750 over 361 tasks).

## Frozen candidate pool

The candidate pool is exactly `work/osw-bestofn/pool.json`, selected by the committed fixed
allowlist in `work/osw-bestofn/select_pool.py`. It contains eight archives, each with 361
official `result.txt` rows. Pool membership is not chosen by score, trajectory content, or Jev.
The pool is pinned by the receipt already committed in `pool.json`.

Allowed state members per archive:

- `traj.jsonl`, compacted to step, action name/type/input/command;
- the final `runtime.log` tail, fixed at **240 UTF-8 characters**;
- `result.txt` is used only by the offline scorer and feasibility receipt, never in a live state.

Screenshots, archive names, grader output, outcome files, and raw result values are excluded
from every live state. Candidate IDs are positional `c0` through `c7`; the question explicitly
forbids treating IDs as correctness evidence.

## Frozen held-out split

R112 called the 337 task IDs in `work/osw-bestofn/live_rows_r3.jsonl`, whose sorted task-ID
digest is:

`c2f320a71b86a6b35ae66dbdb4d2fb9d368aee181b21787f149b48516440aaf2`

The retry split is the sorted set difference between the 361 task IDs in
`work/osw-bestofn/heldout_valid_slice.json` and those 337 R112 task IDs. It contains **24**
tasks and has newline-joined task-ID SHA-256:

`97a8053f93b5c19681dd735fd4c23609d687c3d770c92f57165c68ae8157fa7c`

The manifest SHA-256 is:

`7aa586ed485d48d8f35dde4bac9e6cea0d64705a49f5f041d31d715be897aea8`

Selection uses task IDs only, not scores, rewards, prior choices, or trajectory contents. The
24 IDs are reconstructed keylessly before any retry call by the following committed-data rule:

```text
heldout = manifest.tasks - {row.task for row in live_rows_r3.jsonl}
heldout = sorted(heldout)
```

A missing state, missing candidate, or ambiguous result join aborts the retry; no replacement
task or outcome-derived split is permitted.

## Frozen Jev request

For each held-out task, the state is:

```json
{
  "task": "<domain>/<uuid>",
  "candidates": [
    {"id":"c0", "actions":[...], "runtime_tail":"..."},
    {"id":"c1", "actions":[...], "runtime_tail":"..."},
    "... c2 through c7 ..."
  ]
}
```

The one Choice question is:

```json
{
  "choice": {
    "type": "choice",
    "instructions": "Which candidate trajectory completed the stated OSWorld task? Compare the candidate action histories and final runtime evidence. Choose none when the evidence is insufficient. Do not use candidate IDs, archive names, or any result field as a proxy for correctness; judge completion of the stated task from the supplied evidence.",
    "criteria": {
      "c0": "Candidate 1",
      "c1": "Candidate 2",
      "c2": "Candidate 3",
      "c3": "Candidate 4",
      "c4": "Candidate 5",
      "c5": "Candidate 6",
      "c6": "Candidate 7",
      "c7": "Candidate 8",
      "none": "No candidate has enough evidence of completing the stated task; abstain."
    }
  }
}
```

The size preflight uses a fixed **1,886-byte question budget** and the documented 32,768-token
state limit. Only `FITS` states may be sent. Any `NEAR` or `OVER` item aborts before the first
Jev call; therefore the live receipt must show zero `OVER` and zero `NEAR` items sent.

## Keyless feasibility bar

Before any Jev call:

1. Build states from the eight frozen archives with `build_states.py --runtime-tail 240`.
2. Sanitize archive names from the state and retain exactly eight candidate IDs for every one
   of the 24 held-out tasks.
3. Run `scripts/jev-state-size.py` with `--question-bytes 1886`; the receipt must show no
   `NEAR` or `OVER` items accepted for sending.
4. Independently verify from the frozen official floor receipt that the per-task oracle winner
   is among the eight offered candidate IDs for all 24 tasks. This check may read official
   rewards only in the keyless feasibility/scoring receipt; it must never copy them into state
   or question bytes.
5. Record state count, candidate count, held-out digest, size classification counts, and the
   winning-archive-offered count in `work/osw-bestofn/r112_retry_preflight.json`.

This feasibility arm proves only that the proposed requests can represent the frozen candidate
pool and fit the documented limit. It does not measure Jev.

## Keyless feasibility result (before any live call)

Receipt: `work/osw-bestofn/r112_retry_preflight.json`.

| Check | Result |
|---|---:|
| Held-out states | 24 |
| Candidates per state | 8 |
| Actual question bytes | 621 |
| Question-byte budget | 1,886 |
| FITS | 24 |
| NEAR | 0 |
| OVER | 0 |
| Oracle winner offered | 24/24 |

The sanitized state file SHA-256 is `83480c50df5b86d4b0b4f9fe11d1428340b6c4927d4e061270519de371ee60ea`.
No Jev call has been made; this receipt is feasibility evidence only.

## Outcome: UNDERPOWERED before live measurement

The keyless floor receipt shows the incumbent best single archive, `autoglm_15steps.zip`,
exact-completes 22 of the 24 held-out tasks. Jev can therefore create at most two exact
completion wins over the incumbent, so the McNemar discordant count satisfies `b <= 2`.
The most favorable possible exact McNemar result is `b=2, c=0`, with two-sided exact
`p=0.5`; the locked `p < 0.05` requirement is unreachable for every possible Jev output.

**Outcome:** NOT MEASURED; UNDERPOWERED. Do not make a live call or report a Jev result for
this 24-task retry. Retry only on a new task universe with measured discordant headroom giving
at least 0.8 power for the locked McNemar bar. This is a feasibility stop, not a model ruling.

## Live bar, fixed before the first retry call

Score Jev's choices against the official `result.txt` rows after the live receipt is complete.
The incumbent is the best single archive on these same 24 held-out task IDs. PASS requires all
three conditions:

```text
jev_mean_reward - best_single_mean_reward >= 0.03
paired exact-completion McNemar p < 0.05
(jev_mean_reward - best_single_mean_reward)
  / (oracle@8_mean_reward - best_single_mean_reward) >= 0.30
```

Exact completion means official reward `>= 1.0`. If the oracle and best-single means tie, the
gap-closure term is vacuous but the three-point and McNemar requirements remain mandatory.
Jev is killed if it is no better than the best single archive, if any required state cannot be
constructed, or if any official result join is ambiguous.

No question wording, candidate order, runtime-tail length, size rule, retry policy, or bar may
change after the first live call. The live model is pinned to `jev-1.13.0`; spend is reported as
`input_tokens * $0.042 / 1,000,000`, with output free. No comparator model is run.

## Boundary

This is a preregistration and feasibility artifact, not a Jev result. It does not claim live
accuracy, calibration, omp wiring, a comparator result, or general OSWorld performance. Another
pane must verify this preregistration and its keyless feasibility receipt before any live retry.
