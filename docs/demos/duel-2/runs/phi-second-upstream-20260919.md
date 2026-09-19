# Phi replay on a second upstream clone

**Bead:** `jev-4uy`
**Method:** offline only; no API key; `python3 ensemble/run_all.py` existing suite plus a
second-clone replay through `ensemble/decorrelation.py`.

## Second clone

`jev-benchmark` contains two committed per-item scorer files with the same 60 task IDs:

- `results/jev-jev-latest.jsonl`
- `results/jev-jev-preview.jsonl`

For each class, the replay used that class's probability as the scorer value and the task label as
truth. This yields two valid one-vs-class analyses from the same scorer pair:

| Pair | n | phi | Jev latest | Jev preview | average | gain over best | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| `readonly` | 60 | 1.0000 | 0.9500 | 0.9500 | 0.9500 | 0.0000 | `AVERAGE_DID_NOT_PAY` |
| `destructive` | 60 | 1.0000 | 0.9833 | 0.9833 | 0.9833 | 0.0000 | `AVERAGE_DID_NOT_PAY` |

The result is a negative control: identical choices and perfectly correlated error vectors do not
benefit from averaging.

## Clone census and limitations

- `jev-benchmark`: usable paired per-item outputs; two one-vs-class analyses above.
- `jev-phishing-bench`: aggregate metrics only in `results/metrics.json` and `report.md`; no
  per-item paired scorer output, so it cannot supply a valid phi/gain pair.
- `jev-agent-failure-benchmark`: saved Jev outputs and aggregate paper baselines, but no paired
  per-item second scorer output.
- Other checked result trees did not expose a second compatible per-item scorer pair.

This does **not** claim two independent scorer pairs: both analyses use the same
`jev-benchmark` latest/preview scorer pair, split by one-vs-class target. It is a valid second-clone
negative control, not a broad calibration sample.

## No-claim

- No new Jev answers were generated.
- No API key was used.
- `RECIPES.md` was not edited because the requested two independent new scorer pairs were not found;
  this receipt records the strongest honest result available from the second clone.
