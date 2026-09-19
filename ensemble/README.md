# Should you average two scorers, or just use the better one?

A 120-line module that answers this before you build the ensemble, plus the evidence that it is
worth asking. **No API key, no training, no network** — but it does need upstream's committed
scores, which this repo does not redistribute (5.7 MB of someone else's data). One clone:

```bash
mkdir -p upstream/bitnovus
git clone https://github.com/bitnovus/jev-spam-eval upstream/bitnovus/jev-spam-eval
```

Without it the script exits 2 and prints those commands. Verified against a fresh clone of this
repository on 2026-09-19 — the earlier wording claimed the data was already here, and it is not.

```bash
python3 ensemble/run_all.py          # four pairs, real data, ~1 second
```

## The short version

Averaging two scorers is folk wisdom: "ensembles help." Sometimes they do not, and you can tell
which case you are in *before* building anything, from two numbers you already have.

| pair | phi (error correlation) | accuracy gap | averaging gained |
|---|---|---|---|
| plain question + logistic regression | +0.035 | 0.0 pp | **+1.25 pp** |
| Jev + TF-IDF (phishing, n=5,733) | +0.107 | 4.2 pp | **+0.38 pp** |
| with-context + without-context (n=662) | +0.343 | 6.8 pp | **-0.60 pp** |
| logistic regression + naive Bayes | **+0.526** | 0.8 pp | **-0.14 pp** |

**Two conditions, not one.** Averaging paid only when the two scorers *failed on different items*
(low phi) **and** were *close in accuracy*. Row 3 is the one that matters: phi well under 0.5, and
it still lost, because no amount of decorrelation at 9% disagreement overcomes a 6.8-point
accuracy gap.

## Using it on your own scorers

```python
# from the ensemble/ directory, or add it to sys.path
from decorrelation import analyze

report = analyze(scores_a, scores_b, truth, a_name="model", b_name="heuristic")
print(report.phi, report.gain_over_best_input, report.verdict)
```

`analyze` returns each scorer's error **shape** (false negatives vs false positives, which is the
mechanism — one scorer protecting recall while the other protects precision is what makes an
average pay), the phi coefficient between their error vectors, the disagreement rate, and the gain
over the better input. It refuses mismatched lengths and empty input rather than scoring them.

Rule of thumb from the four pairs: **average when phi is near zero and the accuracy gap is small;
otherwise take the better scorer.**

## Why you should not over-trust the table

Four points do not locate a boundary. The 0.5 figure in the verdict function is a stated
convention with one sign change near it — that is weak support, not calibration. All four pairs
come from three upstream projects and a handful of datasets, and one of them (row 3) is a context
ablation of a single model rather than two independent methods. **If you need to know where the
boundary is for your data, measure your data.** This tells you what to measure.

## Tests

```bash
cd ensemble && python3 -m unittest test_decorrelation      # 5 tests
```

The load-bearing one averages a scorer **with itself**: perfect correlation must buy exactly zero
and report `AVERAGE_DID_NOT_PAY`. A measurement showing a gain there would be measuring
arithmetic, not decorrelation — and every number above would look identical.

Full history, including the rule's first form being wrong: `../RECIPES.md` recipe 4.
