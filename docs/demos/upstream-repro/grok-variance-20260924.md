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

**Where the bar landed.** The bar went into `5dbfa23` (2026-09-24 03:51:34Z). That is a sibling's
commit titled "[test] ratify ae01091…". It swept my staged bar files in with its own; I did not make
it and did not amend it. The three bar files in it (this receipt down to "Pending the reruns",
`grok_variance.py`, `run.py`) are byte-identical to what I staged. No grok rerun call was made
before it. The first rerun started after 03:51:34Z.

Live, 2026-09-24, `[live]`. There were eight reruns: two per set, run in sequence. That was 4,100
grok calls, all answered: 0 failed rows, 0 resume passes, 0 transient retries, 0 rows needing more
than one attempt. Every finish reason was `stop`, and every row's provider model was
`grok-4.20-0309-non-reasoning`. Each rerun's input tokens equal run 1's exactly (SST-5 295,333,
CLINC 558,472, SciFact 336,369, Banking77 272,639 per run), so the prompts were byte-identical.
Rows (sha256 prefix…suffix): `rows-sst5-grok-run2` `a8de2670…f39cc9`, `-run3`
`059c36dd…f9a211`; `rows-clinc150-grok-run2` `122b604e…a4595d`, `-run3` `f7f2a809…903326`;
`rows-scifact-grok-run2` `402b32ae…3ef153`, `-run3` `e75859a5…461052`; `rows-banking77-grok-run2`
`da50a0d5…e9fb1d`, `-run3` `aea434bd…5f4ca7`. Re-score with no key, about a minute:
`python3 work/second-incumbent/grok_variance.py`. It prints every pairing's cells.

**Grok across its three runs.**

| Set | Run 1 | Run 2 | Run 3 | Answer flips between runs (1v2, 1v3, 2v3) | Zero-mass rows per run |
|---|---|---|---|---|---|
| SST-5 (exact, MAE) | 227, 0.624 | 229, 0.626 | 235, 0.620 | 76, 66, 60 levels | 0, 0, 0 |
| CLINC150 (overall, handled at 0.60) | 668, 657 | 671, 661 | 669, 662 | 46, 35, 48 choices | 0, 0, 0 |
| SciFact (correct, AUC, Brier, ECE) | 330, 0.875, 0.1443, 0.1363 | 328, 0.866, 0.1504, 0.1404 | 323, 0.836, 0.1671, 0.1593 | 18, 23, 17 decisions | n/a |
| Banking77 (correct) | 366 | 368 | 359 | 20, 20, 21 choices | 22, 21, 27 |

Grok's flips exceed several headrooms: SST-5 has 60 to 76 against 17, and CLINC 35 to 48 against
11. So R1, the all-pairings rule, decided every claim, not the headroom.

**All pairings, verdicts under the bar** (the full grid is in the scorer's output):

| Set | Claim [reading] | Committed | Pairings meeting it | Range across pairings | Under the bar |
|---|---|---|---:|---|---|
| SST-5 | MAE sign test [all rows] | WIN | 9/9 | 156–169 vs 93–104, p 1.9e-5 to 4.3e-4 | **STANDS** |
| SST-5 | MAE [zero-mass dropped: 0 rows] | WIN | 9/9 | same | **STANDS** |
| SST-5 | accuracy McNemar [both readings] | WIN | 9/9 | 128–144 vs 89–99, p 0.0035 to 0.027 | **STANDS** |
| SST-5 | PASS [both readings] | PASS | 9/9 | | **STANDS** |
| CLINC150 | handled at 0.60 [unit rule; zero-mass dropped: 0 rows] | WIN | 9/9 | 34–45 vs 12–18, p 3.9e-4 to 0.0055 | **STANDS** |
| CLINC150 | overall [both readings] | WIN | 9/9 | 29–35 vs 10–15, p 0.0022 to 0.014 | **STANDS** |
| CLINC150 | PASS [both readings] | PASS | 9/9 | | **STANDS** |
| SciFact | accuracy | WIN | 12/12 | 45–55 vs 14–17, p ≤ 1.4e-4 | **STANDS** |
| SciFact | AUC / Brier / ECE | WIN | 12/12 each | every interval excludes 0 (closest: ECE upper −0.0469) | **STANDS** |
| SciFact | PASS | PASS | 12/12 | | **STANDS** |
| Banking77 | McNemar [as returned] | WIN | 9/9 | 21–30 vs 3–7, p ≤ 0.0025 | **STANDS** |
| Banking77 | McNemar [zero-mass dropped] | NON-INFERIOR | 9/9 | 8/9 NON-INFERIOR (p 0.065 to 0.61), 1/9 WIN (11v2, p 0.023) | **STANDS** |
| Banking77 | PASS [both readings] | PASS | 9/9 | | **STANDS** |

**Verdict under the bar at `5dbfa23`: every claim STANDS.** Across 39 pairings (9 + 9 + 12 + 9),
every published Jev-vs-grok verdict meets its committed label in every pairing. This includes
SciFact's AUC and ECE, the two that Haiku's variance retracted (R89). Against grok they are WINs
in 12/12, because grok's calibration is far worse than Haiku's and varies (ECE 0.136 to 0.159).
No retraction, so no `NEGATIVE_EVIDENCE.md` row.

**The one qualifier that carries over unchanged: Banking77.** Grok returns zero-mass maps on every
run: 22, 21 and 27 of 400 rows, which the adapter ships as `activate_my_card` at confidence 0. The
as-returned WIN (9/9) rests on those rows. With them dropped, Jev and grok are NON-INFERIOR in 8
of 9 pairings (one WIN). The fair one-liner from `jev-dsu` still holds across grok's reruns:
"Jev never abstains by accident; on the rows grok answers, it ties grok."

**For the README (ReadmeStrangerRun told):** each grok comparison now has the 3-run check the Haiku
ones got, and none moves. The following can be stated with grok named beside Haiku:
- the SST-5 MAE WIN;
- the CLINC150 gated WIN;
- SciFact PASS, with accuracy, AUC, Brier and ECE all WINs against grok;
- Banking77 WIN as returned, with the zero-mass qualifier.

**Spend.** 4,100 grok calls: 2,925,626 input / 267,424 output tokens (adapter totals). xAI list
prices are not read here. No Jev or Haiku calls.

**Boundary / NO-CLAIM.** Three grok runs per set: the two reruns within about 10 minutes on 2026-09-24,
run sequentially, plus run 1 earlier that night. One grok model id (non-reasoning), one adapter version
(`adffc2e`). Jev's runs are the committed ones from other times. A STANDS says the verdict is
robust to grok's sampling on these rows. It does not cover other grok versions, reasoning mode, or
other sets. A non-author spot-check is still pending before close.

## Non-author verification (BillingUnits, 2026-09-24, zero model calls)

Oracle: committed rows, re-scored without a key in a clean clone. Clone: `git clone --local` →
`/tmp/bu-wu6v-clone` @ `5f382c3`.

- **Bar before calls.** The bar landed inside `5dbfa23`, a sweep commit whose author and committer
  times are both 21:51:34 -0600. That commit also adds the `run2|run3` tag to `run.py`, so the
  committed runner could not write rerun files before it. The rerun files were created on disk
  (`stat -f %SB`, main worktree) from 21:52:06 (`rows-sst5-grok-run2.jsonl`, the earliest) to
  22:00:14 (`rows-banking77-grok-run3.jsonl`). Every one was created after the bar commit. The
  earliest was created 32 s after it, and a file is created only when its first answer is appended.
  I found no evidence of a grok rerun call before `5dbfa23`. `[INFERENCE]` An uncommitted runner
  could in principle have called earlier without writing these files; nothing on disk suggests it.
- **Scorer and runner unchanged** between `5dbfa23` and `8374fd4` (`git diff --stat` is empty for
  `run.py` and `grok_variance.py`).
- **Re-score.** `env -u TYPESAFE_API_KEY -u XAI_API_KEY -u ANTHROPIC_API_KEY python3
  work/second-incumbent/grok_variance.py` exits 0. All 21 verdict lines read STANDS: SST-5 9/9,
  CLINC150 9/9, SciFact 12/12 on accuracy, AUC, Brier and ECE, and Banking77 9/9, with and without
  zero-mass rows as the bar specifies.
- **Rows.** All 8 rerun files hold one row per id (500 / 750 / 400 / 400 per set), 0 error rows,
  and one model, `xai/grok-4.20-0309-non-reasoning`.
- **Independent recount, SST-5 MAE** (my own script: level = floor(score + 0.5), exact sign test,
  over the committed `work/score-sst5/rows-jev{,-run2,-run3}.jsonl` and the three grok files). All 9
  pairings are WIN. The splits run from 156/99 to 169/103, and the (1,1) split of 168/101,
  p 5.27e-05, matches the scorer's table line. CLINC150, SciFact and Banking77 were checked through
  the scorer only.

**Verdict:** reproduced. No retraction is due.
