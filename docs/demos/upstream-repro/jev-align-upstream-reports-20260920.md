# Two defect reports for `sutro-sh/jev-align`, plus one UX gap

Report text, written to be handed upstream. **Nothing here has been posted to GitHub.** The
deliverable is this file.

Both defects were re-opened at source and re-reproduced for this document; neither claim below
rests on the earlier session's memory. Where a number comes from the previous receipt rather than
from a run made for this file, it says so.

## Environment

| | |
|---|---|
| Package | `jev-align` **0.1.2** (PyPI wheel) |
| Source read | `github.com/sutro-sh/jev-align` at **`49753df924d30c0d3642b58e0b9b1e89921dc102`** ("updates", 2026-09-19) |
| Resolved dependency | `gepa` **0.1.4** |
| Python | 3.11.15 in a throwaway `uv venv`, `uv pip install "jev-align==0.1.2"` |
| Host | macOS 25.5.0, arm64 |
| Evaluation backend (live runs only) | `typesafe/jev-1.13.0` |
| Reflection model (live runs only) | `anthropic/claude-haiku-4-5-20251001` |

The wheel and the clone are the same release: `pyproject.toml` at that commit is also
`version = "0.1.2"`. The clone was read, never edited.

Reproduction 1 needs **no API keys, no network and no dataset** — the backend and the reflection
LM are local stubs, so it is deterministic and free. Reproduction 2 needs `TYPESAFE_API_KEY` (11
backend calls) and any reflection key, and uses the `support-tickets.csv` that ships inside the
wheel.

---

## Defect 1 — the GEPA objective is flat: a strictly more correct candidate is rejected at F1 = 0

### The code

`src/jev_align/optimizer.py`, `F1BatchEvaluator.__call__`. A single batch-level score is computed
per candidate (binary branch shown; the multilabel, score and multiclass branches at 170, 178 and
183 have the same shape):

```python
185:                predicted = [_binary_label(prediction) for prediction in predictions]
186:                expected = [bool(example["label"]) for example in examples]
187:                metrics = binary_metrics(expected, predicted)
188:                score = metrics.f1
```

Fourteen lines later the loop computes a genuine **per-row** score and then does not return it:

```python
190:            for index, example, prediction, got, want in zip(
191:                indices, examples, predictions, predicted, expected, strict=True
192:            ):
...
201:                elif got == want:
202:                    row_score = 1.0
203:                    error_type = "correct"
...
213:                else:
214:                    row_score = 0.0
215:                    error_type = "false_negative"
216:                results[index] = (
217:                    score,
218:                    {
...
244:                        "scores": {"correct": row_score},
245:                    },
246:                )
```

`results[index]` — the score GEPA optimizes for row `index` — is `score`, the batch aggregate.
`row_score`, the row's own correctness, is carried only inside the feedback dictionary at line
244, which becomes reflection prose.

That matters because the configured acceptance criterion sums the per-row scores.
`optimizer.py:369` selects it:

```python
369:            acceptance_criterion="strict_improvement",
```

and `gepa/strategies/acceptance.py:44-53` is:

```python
44: class StrictImprovementAcceptance:
45:     """Accept only if the sum of new subsample scores is strictly greater than the old sum.
...
50:     def should_accept(self, proposal: CandidateProposal, state: GEPAState) -> bool:
51:         old_sum = sum(proposal.subsample_scores_before or [])
52:         new_sum = sum(proposal.subsample_scores_after or [])
53:         return new_sum > old_sum
```

Because every element of both lists is the same batch F1, `sum(...)` is `batch_size × F1` and
acceptance reduces to "did batch F1 rise". Per-row information never reaches selection, so the
per-instance Pareto machinery (`candidate_selection_strategy="pareto"`, `optimizer.py:367`) has no
per-instance signal to work with either.

**Observed consequence, stated narrowly.** At batch F1 = 0 (no true positives), a child candidate
that fixes rows the parent got wrong is rejected unless it also manufactures a true positive — no
matter how many rows it corrects. A candidate that removes every false positive, going from 0/6
rows correct to 4/6, still scores F1 = 0 and is discarded as no improvement. This is the regime a
badly-aimed seed question lands in, which is the regime the optimizer exists to rescue.

(The looser claim "GEPA can never improve at F1 = 0" is not what we measured and is not made here:
a child that produces a true positive does raise F1 and would be accepted.)

### Reproduction — deterministic, offline, no keys

```sh
python3 -m venv /tmp/jeva && /tmp/jeva/bin/pip install "jev-align==0.1.2"
/tmp/jeva/bin/python flat-objective-repro.py     # our copy: work/jev-align-probe/flat-objective-repro.py
```

Six rows, two of them positive. A stub backend answers: the seed candidate predicts True on the
four negatives and False on the two positives (tp=0 fp=4 fn=2, F1 = 0, **0/6 rows correct**); any
mutated candidate predicts False everywhere (tp=0 fp=0 fn=2, F1 = 0, **4/6 rows correct**). The
mutation is better on four rows and worse on none. A stub reflection LM returns a fixed proposal,
so the run is free and repeatable.

Actual output, run 2026-09-19:

```text
==========================================================================
PART 1  What the evaluator returns per row
==========================================================================

seed:
  batch F1                       = 0.000
  rows actually correct          = [0, 0, 0, 0, 0, 0]  (0/6)
  per-row scores GEPA receives   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  per-row correctness, feedback  = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]   <- computed, then discarded

child:
  batch F1                       = 0.000
  rows actually correct          = [0, 0, 1, 1, 1, 1]  (4/6)
  per-row scores GEPA receives   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  per-row correctness, feedback  = [0.0, 0.0, 1.0, 1.0, 1.0, 1.0]   <- computed, then discarded

==========================================================================
PART 2  What GEPA's acceptance criterion does with them
==========================================================================
  as shipped (batch F1 per row): 0.0 -> 0.0   accept=False
  with true per-row correctness: 0.0 -> 4.0   accept=True

==========================================================================
PART 3  End to end through jev_align.optimizer.optimize_candidate
==========================================================================
  metric calls spent   : 131
  backend batches      : 11
  candidates kept      : 1
  best score           : 0.0
  question changed?    : NO - byte-identical to the seed

REPRODUCED
rc=0
```

Line 244's `row_score` is visibly the information that would decide the comparison, and visibly not
the number that does.

### Corroboration on a live run

Same defect with the real TypeSafe backend and a reflection model proven live in the same session
(zero LiteLLM error banners in the transcript, so every reflection call succeeded):

```sh
jeva optimize <wheel>/jev_align/sample_data/support-tickets.csv \
  --question "Is this ticket about billing?" --column instruction \
  --pool-size 11 --batch-size 6 --max-metric-calls 40 --seed 0 \
  --reflection-model anthropic/claude-haiku-4-5-20251001
# labels supplied by a regex oracle that labels "reach a human" tickets True —
# deliberately disjoint from the seed question, so training F1 is 0.
```

```text
│ Training F1 │ 0.000 · P 0.000 · R 0.000 │ 0.000 · P 0.000 · R 0.000 │ +0.000 │
GEPA metric calls: 56 actual / 40 configured
AI Function diff: No textual change.
```

`.jev-align/runs/<run>/gepa-runs/round-0001/run_log.json` — every mutation attempt, before and
after:

```text
iter 0 n_tasks 4 subsample_scores [0.0, 0.0, 0.0, 0.0, 0.0] -> new [0.0, 0.0, 0.0, 0.0, 0.0]
iter 1 n_tasks 4 subsample_scores [0.0, 0.0, 0.0, 0.0, 0.0] -> new [0.0, 0.0, 0.0, 0.0, 0.0]
total mutation attempts: 8
candidates kept: 1
```

Eight real reflection-produced children, every per-row score 0.0 on both sides of every
comparison, one candidate at the end: the seed. `gepa-result.json` shows
`val_aggregate_scores: [0.0]` and a single entry in `candidates`.

A larger instance of the same shape — 320 metric calls, 6 iterations × 4 tasks = 24 mutation
attempts, zero accepted — is in [`jev-align-20260919.md`](jev-align-20260919.md); those numbers are
from that session, not re-run here.

### Expected

A child candidate that is correct on strictly more rows than its parent, and worse on none, should
be visible to selection as an improvement.

### Suggested direction

One line: the per-row correctness already computed at `optimizer.py:195-214` is the natural value
for `results[index]`'s score slot, with the batch metric kept where it is useful — in
`batch_confusion` and in the reflection feedback. How to keep macro-F1 honest under that change
(the comment at `optimizer.py:372-375` shows the authors have already thought hard about batch
composition) is a design call for the maintainers, not ours.

---

## Defect 2 — "The unlabeled pool is exhausted." is printed while rows have never been offered

### The code

`src/jev_align/cli.py`, the labeling loop:

```python
2476:        while True:
2477:            remaining = session.unlabeled_stories()
2478:            if not remaining or (
2479:                session.capture_pool is None and len(remaining) < state.batch_size
2480:            ):
2481:                # A shutdown after the last label must not strand an otherwise
2482:                # complete round when the resumed acquisition pool is empty.
2483:                if session.ready_to_optimize() and any(
...
2492:                console.print(
2493:                    "The captured sample is exhausted. Resume learning to sample more calls."
2494:                    if session.capture_pool is not None
2495:                    else "The unlabeled pool is exhausted."
2496:                )
2497:                return
```

`len(remaining) < state.batch_size` is a remainder condition, not an exhaustion condition. The
guard looks deliberate — a short final batch would make batch-level F1 incomparable across rounds,
which is the same concern the `ClassAwareBatchSampler` docstring raises at `optimizer.py:47-52`.
The sentence at line 2495 is the part that is false.

The CLI *does* guard the whole-run case: `--pool-size 5 --batch-size 6` is refused up front with
`dataset has 5 rows, fewer than the requested batch size of 6` (and `--pool-size 3` with
`not in the range x>=5`). The remainder case has no equivalent.

### Reproduction

```sh
# prerequisites: pip install "jev-align==0.1.2"; TYPESAFE_API_KEY set (11 backend calls);
# any reflection key set. Dataset ships inside the wheel.
./false-exhaustion-repro.sh          # our copy: work/jev-align-probe/false-exhaustion-repro.sh
```

which runs, in a fresh temp directory:

```sh
jeva optimize <wheel>/jev_align/sample_data/support-tickets.csv \
  --question "Is this ticket about billing?" --column instruction \
  --pool-size 11 --batch-size 6 --max-metric-calls 20 --seed 0
```

with blank lines on stdin. jev-align falls back to line-oriented input when stdin is not a TTY
(`cli.py:1449`) and an empty line accepts the highlighted default, so the six labels are whatever
the model already predicted and no human is needed.

Actual output, run 2026-09-19 (head, tail and the accounting; the six label cards are elided):

```text
workdir: /var/folders/.../tmp.HlJPXWU6jU
dataset: /tmp/jeva-repro-venv-a/lib/python3.11/site-packages/jev_align/sample_data/support-tickets.csv

Run created at .../.jev-align/runs/20260920-003115-274218-is-this-ticket-about-billing

Round 1: 11 inputs in the full original pool (11 unlabeled), using typesafe/jev-1.13.0...
...
GEPA stopped early: perfect training score · 6/20 metric calls
AI Function diff: No textual change.
AI Function decision (Accept/Reject/Quit): The unlabeled pool is exhausted.
jeva rc=0

--- accounting -------------------------------------------------------
pool size            : 11
rows ever offered    : 6
rows NEVER offered   : 5
REPRODUCED: printed "exhausted" with 5 rows never offered
```

`labels.jsonl` from that run holds exactly six rows — `row-000009`, `row-000007`, `row-000011`,
`row-000003`, `row-000006`, `row-000002`. The pool was the first eleven rows of the CSV, so
`row-000001`, `row-000004`, `row-000005`, `row-000008` and `row-000010` — **5 of 11, 45% of the
pool** — were never shown to the labeler, and the process exited 0 saying the pool was used up.

### Observed vs expected

- **Observed:** `The unlabeled pool is exhausted.` with 5 of 11 rows never offered, exit 0.
- **Expected:** either the remaining rows are offered, or the message says what is true — that a
  partial batch is being withheld and how many rows that leaves.

### Suggested direction

One line: the message is the defect, not the guard — a stranger cannot distinguish "you labeled
everything" from "5 rows were withheld because they do not fill a batch", and only one of those
asks them to do something.

---

## Separate, softer: a present-but-invalid reflection key is not a crash, it is a clean-looking report

**This is a UX and verification gap, not a defect that breaks a run.** No exception escapes, no
exit code changes, no data is corrupted. We are filing it alongside the two defects because the
failure it hides looks exactly like success.

jev-align refuses to start without a reflection provider key — that check works, and it is good:

```text
no reflection key -> rc=2  "no reflection provider key detected; set OPENAI_API_KEY,
                            ANTHROPIC_API_KEY (or CLAUDE_API_KEY), GEMINI_API_KEY, or
                            pass --reflection-model"
```

It verifies the key is **present**. It does not verify the key **works**.

Reproduced 2026-09-19 by running with a deliberately invalid `OPENAI_API_KEY` and
`--reflection-model openai/gpt-4.1-mini`. That the key really is rejected was confirmed separately
against LiteLLM:

```text
AuthenticationError: litellm.AuthenticationError: AuthenticationError: OpenAIException -
Incorrect API key provided: sk-delib**************************robe.
```

Inside `jeva optimize`, every reflection call failed. The transcript carries **288** copies of:

```text
Give Feedback / Get Help: https://github.com/BerriAI/litellm/issues/new
LiteLLM.Info: If you need to debug this error, use `litellm._turn_on_debug()'.
```

— a banner that does not name authentication, the provider, or the model. The exception text
itself never reaches the console. What the user is then shown is a complete, ordinary report:

```text
                               AI Function scores
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Score       ┃                   Current ┃                  Proposed ┃ Change ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Training F1 │ 0.000 · P 0.000 · R 0.000 │ 0.000 · P 0.000 · R 0.000 │ +0.000 │
└─────────────┴───────────────────────────┴───────────────────────────┴────────┘
... full-pool ambiguity table, replay-set ambiguity table, certainty-by-iteration table ...
GEPA metric calls: 21 actual / 20 configured
╭─ AI Function diff ─╮
│ No textual change. │
╰────────────────────╯
AI Function decision (Accept/Reject/Quit):
```

Exit 0. A total failure of the optimizer is presented as a considered `+0.000` and an Accept
prompt. Three distinct causes print nearly this same screen — budget starvation, a dead reflection
provider, and the flat objective of Defect 1 — and only the legitimate case
(`GEPA stopped early: perfect training score`) announces itself.

**What we did not measure:** how often reflection keys are invalid in practice. Our own
`OPENAI_API_KEY` happened to be dead in this project on 2026-09-19, which is how we found it. That
is one environment on one day; it is not a base rate, and nothing here says invalid keys are
common.

**Suggested direction.** One line: if a run ends with zero successful reflection calls, that is
worth one sentence on the console before the scores table, because the table cannot distinguish it
from a good question.

---

## No-claim

- Defect 1's reproduction uses a stub backend and a stub reflection LM. That is what makes it free
  and deterministic; it also means it exercises `F1BatchEvaluator`, `optimize_candidate` and GEPA's
  real acceptance code, but not a real model's behaviour. The live corroboration above is one seed,
  one dataset, 56 metric calls.
- We did not measure whether returning per-row scores would make GEPA improve a wrong question. We
  measured that the current shape cannot see a strictly better child at F1 = 0. Those are different
  claims and only the second is made.
- No label in either reproduction is a human label. jev-align is designed around human judgment and
  that design was bypassed to make the runs reproducible; nothing here evaluates the human loop.
- `--holdout`, `jeva functions`, resume, capture/continual-learning, and the Vercel and Cloudflare
  backends were not exercised.
- Nothing in this file has been posted to GitHub, and no issue has been opened.
