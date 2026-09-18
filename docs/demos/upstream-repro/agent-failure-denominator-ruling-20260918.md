# What a 6,257-trace benchmark says about 17-candidate verdicts

## Upstream control

`jev-agent-failure-benchmark` reports 6,257 Who&When Pro text traces, confidence intervals,
and calibrated per-axis results:

| Axis | Jev | 95% interval |
|---|---:|---:|
| Who | 73.4 | 70.5–76.2 |
| When | 76.4 | 74.3–78.4 |
| What | 23.7 | 22.4–24.9 |
| All | 31.3 | 29.5–33.0 |

The repository's saved result file contains 6,257 unique trace IDs and zero error records. Its
own caveat matters: Who and When favor Jev because it chooses from enumerated options while the
paper baselines free-generate; What is the like-for-like axis.

Upstream tests pass with the development extras: **20/20**. A bare `uv run pytest` first failed
collection because the pinned `whowhen_eval` dependency was not installed; `uv run --extra dev
pytest` resolved it and passed.

## Ruling on our 17-candidate verdicts

A `CLEARED` row in `docs/demos/STATUS.tsv` does **not** mean the idea has benchmark-level
confidence, generalization, or production efficacy. It means the candidate passed its current
rung's acceptance condition. That is a different measurement object from a 6,257-trace benchmark:

- our denominator is **17 candidate ideas**, not repeated examples of one task;
- our evidence is heterogeneous: receipts, tests, demand checks, and falsification conditions;
- a CLEARED row is not a PROMOTED row and does not claim an effect size;
- the current process can still over-trust single-run evidence when a row's wording sounds like a
  performance conclusion.

The honest boundary is therefore:

> `CLEARED` = current rung passed under the cited evidence. It is not evidence that the underlying
> capability would survive a 6,257-example evaluation.

For any candidate that claims accuracy, lift, calibration, or generalization, a later promotion
needs an appropriate held-out denominator, uncertainty interval, and an explicit leakage/control
check. A candidate whose rung only asks for a runnable mechanism or a named demand signal does not
need 6,257 examples merely to pass that rung, but it must not be narrated as if it did.

## Decision

The benchmark does not invalidate the 17-row gauntlet. It **narrows the claim class** of its
verdicts. `CLEARED` is a process-state result; `PROMOTED` must carry benchmark-grade evidence when
its product claim is empirical. The benchmark's n=6,257 is an external warning against upgrading
our single-run rows into confidence claims, not a denominator to mechanically copy into every idea.
