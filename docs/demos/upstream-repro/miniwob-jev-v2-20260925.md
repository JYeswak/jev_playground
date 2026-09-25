# MiniWoB Jev v2 held-out receipt

Bead: `jev-jy7t.1.7`
State: **BLOCKED / NOT SCORED**. The live v2 arm halted on an official TypeSafe 400 before the
held-out set completed. No v2-vs-v1 bar is scored.

## Preregistration and keyless work

The bar and held-out seeds were committed before the first live call in
`miniwob-jev-v2-prereg-20260925.md`: all 125 tasks x seeds `100,101,102,103,104` (625 episodes per
arm), exact paired McNemar p < 0.05 and v2-only successes > v1-only successes. v1 and v2 differ
only in the preregistered `none` availability rule.

The 23 `/tmp/miniwob-floors-v2*.jsonl` sources were merged by the committed precedence rule:
`.p*.jsonl` > `.retry.s0.jsonl` > `.s0.jsonl` > base, keyed by `(task, seed, rep, policy)`.
The canonical tracked floor is `work/miniwob-jev/rows/miniwob-floors-v2.heldout.jsonl`:
1,250 rows exactly: 625 random and 625 scripted.

Keyless gates passed:

```text
/tmp/jev-miniwob-jev/venv/bin/python work/miniwob-jev/jev_arm.py selftest
/tmp/jev-miniwob-jev/venv/bin/python work/miniwob-jev/jev_arm.py dev --fake greedy --tasks click-button --seeds 9000-9001
```

The selftest and dev arm used no Jev calls.

## Live rows completed before the halt

All calls used `jev-1.13.0` through the official SDK, with the resolved model recorded per row.
No comparator model ran. No 402 occurred in this run.

| Arm | Raw rows committed | Unique episode rows | Successes on latest unique row | Calls | Input tokens | Output tokens | Spend at $0.042/M input |
|---|---:|---:|---:|---:|---:|---:|---:|
| v1 `none_policy=always` | 1,022 | 625/625 | 321 | 4,587 | 12,192,804 | 4,597,050 | $0.512097768 |
| v2 `none_policy=after-page-change` | 365 | 365/625 | 183 | 1,573 | 5,208,134 | 2,301,644 | $0.218741628 |

The v1 raw count exceeds 625 because the first single-shard run was resumed through 20 shards;
rows are preserved unchanged, and the latest row for each `(task, seed, rep)` is the only row that
would be used for a keyless score. The actual spend includes every live call, including resumed
duplicates. The v1 output rows are committed in `miniwob-jev-v1-heldout.s*.jsonl`; v2 rows are
committed in `miniwob-jev-v2.s*.jsonl`.

The v2 process stopped at `drag-items-grid`, seed 100, after three consecutive validator failures:

```text
TypeSafeBadRequestError: 400 Choice question must have at least one choice: action
```

The episode row was not written, and no further v2 live calls were made. The v2 `none` policy can
remove every candidate when the page fingerprint is unchanged; this is an implementation failure
that prevents scoring the preregistered rule. The missing v2 episodes are not imputed and the
partial 183/365 success count is not compared to v1.

The v1 output's 7 recorded per-row validator failures were non-HTTP failures; the resolved model
remained `jev-1.13.0`. No API key, raw browser state, screenshot, or response body was committed.

## Boundary and next action

- **No bar verdict:** the held-out v2 set is incomplete, so McNemar is intentionally uncomputed.
- **No claim about Jev:** this run tests neither the none rule nor v2 success because the harness
  generated an invalid empty Choice question.
- Retry requires a new preregistration that preserves the original none-rule comparison but adds an
  explicit nonempty-action guard, then reruns the full held-out set. Do not reuse this partial set
  as a held-out bar.
