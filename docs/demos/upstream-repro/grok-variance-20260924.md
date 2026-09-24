# Do the Jev-vs-grok verdicts survive grok's re-runs? All pairings on four sets (bead `jev-wu6v`)

ConfidenceCascade (background agent of pane 1), 2026-09-24. Live lane: grok calls only. Jev rows are
the committed runs.

## Preregistered (committed before any rerun call)

**Question.** Grok is a published comparator on four sets. Each rests on one grok run:
`jev-n4j` ([receipt](grok-incumbent-sst5-clinc-20260924.md)) for SST-5 and CLINC150, and `jev-dsu`
([receipt](second-incumbent-20260924.md)) for SciFact and Banking77 10-intent. Haiku's run-to-run
variance flipped published verdicts twice (R88 Yelp, R89 SciFact AUC/ECE). Before the README names
grok beside Haiku, does every Jev-vs-grok verdict hold across two more grok runs, paired with every
committed Jev run?

**Runs.** Two more runs of `grok-4.20-0309-non-reasoning` on each set, through the same path as the
committed runs: `work/second-incumbent/run.py <set> run2|run3`, which writes
`rows-<set>-grok-run{2,3}.jsonl`. It uses `system-one-adapter-python` at `adffc2e`,
`AsyncOpenAIProvider(base_url="https://api.x.ai/v1")`, structured outputs, probabilities mode,
normalized, `RetryPolicy()`, 8 concurrent, 90 s. Inputs are read with `git show` from the same
pinned commits as grok run 1. The only runner change is the optional run tag, which changes the
output path; the call is unchanged. `XAI_API_KEY` comes from the lane's Infisical project, and only
its presence was checked. Runs are sequential within a set, each with one resume pass for failed
rows. 4,100 grok calls are planned: 2 x (500 + 750 + 400 + 400).
Unaffected by the Anthropic spend cap Main announced: no Haiku or Jev call is made.

**Every committed Jev run, pinned (read with `git show`):**

| Set | Jev runs | Pairings |
|---|---|---:|
| SST-5 (500) | `rows-jev` @ `576e60e`, `-run2`/`-run3` @ `510e804` (`jev-qbc`) | 3 x 3 = 9 |
| CLINC150 (750) | `rows-jev` @ `2842340`, `-run2`/`-run3` @ `0516464` (`jev-kvw`) | 9 |
| SciFact (400) | `rows-jev` @ `83a7295`, `rows-jev-rerun` @ `6ac0092`, `-run2`/`-run3` @ `3c006e2` (`jev-hg8`) | 4 x 3 = 12 |
| Banking77 10-intent (400) | `rows-jev` @ `3709ee6`, `-run2`/`-run3` @ `510e804` (`jev-qbc`) | 9 |

Grok run 1 is `rows-sst5-grok` and `rows-clinc150-grok` @ `492d8d6`, and `rows-scifact-grok` and
`rows-banking77-grok` @ `a8cbf6e`.

**Scorer.** `python3 work/second-incumbent/grok_variance.py` (keyless). Each set uses its own
unit's metric code and verdict rule, at the commit its receipt scored: SST-5 `score.py` @
`576e60e`; CLINC `score.py` @ `2842340`; SciFact `score.py` @ `15b0371`, scored as `jev-dsu` did;
Banking77 `score.py` @ `3709ee6`, the `jev-dsu` k3k rule. It exits 1 unless the pairing (Jev run 1,
grok run 1) reproduces every committed verdict below, and **it does, now**: SST-5 MAE 168/101 WIN,
accuracy 142/96 WIN; CLINC handled 44v16 WIN, overall 35v15 WIN; SciFact accuracy 46/15, AUC,
Brier and ECE WIN; Banking77 24v6 WIN as returned and 8v5 NON-INFERIOR with zero-mass rows dropped;
PASS on all four. **Disclosed:** while testing the scorer I also printed the Jev run 2/3 (and
SciFact rerun) x grok run 1 pairings. Every one of those 9 meets every claim. No grok rerun exists
yet.

**Claims under test**, each against its own reading:

| Set | Claim (committed label) | Readings |
|---|---|---|
| SST-5 | MAE sign test WIN; accuracy McNemar WIN; pass rule PASS | all rows; zero-mass grok rows dropped |
| CLINC150 | handled at peak >= 0.60 WIN; overall WIN; pass rule PASS | unit rule (worse of as shipped / zero-mass = none); zero-mass dropped |
| SciFact | accuracy WIN; AUC WIN; Brier WIN; ECE WIN; PASS (no grok win on any) | all rows (a Noul answer cannot be zero-mass) |
| Banking77 | McNemar WIN as returned; NON-INFERIOR with zero-mass dropped; PASS both ways | as returned; zero-mass dropped |

**The rule, fixed now** (the all-pairings rule of `jev-x5k`, `jev-hg8` and `jev-kvw`). A claim
**STANDS** only if every pairing meets its committed label. For a WIN, that means WIN in all
pairings. For NON-INFERIOR it means NON-INFERIOR or better, and for PASS it means PASS. Otherwise the
claim is **RETRACTED**, and the count of pairings that met it is reported either way. Each
retraction gets a `NEGATIVE_EVIDENCE.md` row with a retry condition. ReadmeStrangerRun is told the
verdicts either way. A set whose grok run has more than 1% unanswered rows after the resume pass is
reported as incomplete, not scored (the scorer prints INCOMPLETE for any missing run).

**Headroom from the committed grok run against Jev run 1** (`grok_variance.py --bar`). This is the
fewest grok answer changes, placed adversarially, that end the WIN. It is a lower bound.

| Claim | Run 1 | Headroom (grok rows) |
|---|---|---:|
| SST-5 MAE sign WIN | 168 vs 101 | 17 |
| SST-5 accuracy WIN | 142 vs 96 | 14 |
| CLINC150 handled at 0.60 WIN | 44 vs 16 | 11 |
| CLINC150 overall WIN | 35 vs 15 | 5 |
| SciFact accuracy WIN | 46 vs 15 | 14 |
| Banking77 as-returned WIN | 24 vs 6 | 6 |

SciFact's AUC, Brier and ECE are bootstrap intervals and have no row headroom. Of all these claims,
AUC and ECE were the ones Haiku's variance retracted.

**NO-CLAIM.** Three grok runs per set, within about an hour, one model id (non-reasoning), and one
adapter version. Jev's runs are the committed ones, and their timing differs from grok's. A STANDS
here covers these sets and this grok model only.

## Result

Pending the reruns.
