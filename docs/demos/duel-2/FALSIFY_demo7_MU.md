# Q7 falsifier — demo-7 signals starter: decompose the delta, then gate transfer

Status: falsification design with the label-free half EXECUTED HERE
($0, read-only, committed aggregates only). The labelled half is
specified for the next corpus. Thesis under test: the 32.5-point gap
(verdict-only 62.6% → five signals + fitted head 95.1%) transfers to a
user's own data, justifying a template product.

## Half 1 (label-free): provenance + decomposition — EXECUTED, no kill

**Provenance: VERIFIED PRESENT.** All three headline numbers re-derive
from the vendored pinned source (`jev-phishing-bench@1d56e8c`, remote
`github.com/anisselbd/jev-phishing-bench`): verdict accuracy 0.626 on
N=2000 (`results/metrics.json`, seed 20260916, CIs throughout); fitted
95.1% [94.1%, 96.0%] by 5-fold CV *plus* a stratified A/B split
replication (fit on A, measure on B, split seed 20260917); model pinned
`jev-1.13.0` served behind `jev-latest` with 0/2000 API errors
(`results/report.md:3`). This half of the falsifier did not fire: the
evidence base exists, is pinned, and shows split discipline. The
"unverifiable transcription" failure mode does not apply here.

**Decomposition: the delta is 89% dataset knowledge, measured from
committed aggregates.** The source ships its own no-AI control
(`bench/heuristics.py`, Control 1, `report.md:113-119`): two regex
features, no fitting, no labels — **91.6% [90.4%, 92.8%]**, FPR 0.2%.
Stacked:

```text
verdict-only ............ 62.6%          (the problem)
+ dataset knowledge ...... 91.6%  (+29.0) (regex floor, no AI)
+ Jev signals + fitting . 95.1%  (+3.5)  (the method)
```

CIs disjoint at each step ([90.4,92.8] vs [94.1,96.0]), so the 3.5pts
are real — but the advertised 32.5-point "don't trust verdicts" delta
is overwhelmingly the gap between *knowing the dataset* and not
knowing it, not between verdicts and signals. The source says so
itself (`report.md:162-165`): the five questions were written after
reading the dataset's URL-evasion taxonomy and "target the way this
dataset was built." A template selling the full 32.5 as transferable
method gain is selling 29 points of local knowledge with 3.5 points
of method attached.

This does not kill demo-7 (3.5 real points + calibration machinery
retain value), but it reprices it: the transferable claim is ~3pts
plus ECE/AUROC discipline, not a 32-point miracle. Any corpus where
the regex floor already reaches the fitted model kills the Jev
machinery on the spot — which is exactly the failure rule below.

## Half 2 (labelled): the transfer gate for the next corpus

On any new labelled corpus, run three arms — verdict-only, regex
floor expressing the corpus builder's own knowledge, fitted
signals+head — and compute:

```text
method_gain = acc_fitted − acc_regexfloor
```

**Failure rule (predeclared):** `method_gain < 0.05` (with overlapping
95% CIs, or either arm under N=200 labelled items → UNASKABLE, not a
pass) → the template's Jev machinery adds nothing beyond writing
down what the builder knows as regex → **HELD**: ship the regex and
the calibration report format, not the template. The corpus that
fails this way is the common case by the base rate of the current
evidence (one corpus in, dataset-knowledge dominant).

**Non-failure outcomes:** method_gain ≥0.05 with disjoint CIs →
falsifier did not fire; proceed to calibration measurement (ECE/AUROC
on held-out, flip rates). Corpus too small or single-class →
UNASKABLE/HELD. Regex floor unbuildable because the builder claims no
domain knowledge → UNASKABLE (the comparison the rule needs does not
exist; do not grade the template against a missing baseline).

**Exact command (design target):**

```sh
signals-falsify transfer \
  --corpus fixtures/user-corpus.jsonl \
  --regex-floor fixtures/corpus-regex.json \
  --out runs/signals-transfer.json
```

Behavior contract: fit verdict-only, regex floor, and signals+head
under identical splits (stratified, fixed seed); report all three
accuracies with Wilson CIs, method_gain, and the failure comparison;
write corpus sha, seed, split policy, and per-arm counts. No Jev call
beyond what the arms require (budgeted, model version recorded).

## Why this ordering is cheapest

Provenance ($0, done above) precedes everything: had the numbers been
unpinned transcription, no further work would be justified. The
decomposition ($0, done above) reframes the transfer question from
"does 32.5 transfer" (it cannot — 29 of it is local knowledge by the
source's own account) to "does ~3.5 + calibration transfer," a
smaller, honest, testable claim. Only then do labels enter, and only
on a corpus where someone already paid for them. At no point does
anyone fit a model to justify fitting models.

## Secondary falsifiers considered

**Calibration-without-discrimination.** If the fitted head reaches
95% by riding one dominant signal (here: free-hosting weight +9.27,
generic-sender +12.24 per the committed full-fit weights,
`report.md:107`), the "five signals" story is one signal plus
decoration. Check committed weights first ($0); if one weight
dominates, the template's K-question machinery is oversold for that
corpus — HELD for scope-narrowing, not a kill.

**Published-grid non-reproduction.** The source documents its own
failed reproduction of the published grid (id/label mismatch,
`report.md:183-185`) and stands on its own numbers instead. Any
falsifier run must do the same: our numbers stand on our corpus;
published numbers are context only. Citing upstream tables as
baselines without re-deriving them repeats the error this lane just
self-corrected (85415e0).

## NO-CLAIM

Half 1 executed read-only ($0, no labels, no Jev calls) with the
committed numbers above; Half 2 is specified, not run. No new corpus
was fitted, no regex was written for new data, no transfer result
exists. Demo-7's thesis survives narrowed (method gain ~3.5pts +
calibration discipline, not 32.5), and the transfer gate above is
the instrument that decides each future corpus.
