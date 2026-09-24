# QuixBugs code-Score, run-to-run variance: does the pair-ordering WIN hold on 3x3 runs? (bead `jev-kz50`)

ClaimCheckTool (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`.

## Preregistered (committed before the first rerun call)

**Headline under test** (`jev-2wc`, [`score-quixbugs-20260924.md`](score-quixbugs-20260924.md), bar
`6ee168c`, rows `a2bee8b`). Over the 40 QuixBugs Python program pairs, correct vs buggy, the
jev-curate `code_quality` Score (five levels, sent as an ordered list):
- **Jev separates:** W/L/T 38/2/0, sign p = 1.5e-09, AUC 0.739 [0.683, 0.812].
- **Haiku 4.5** via `system-one-adapter`: 28/10/2, AUC 0.668.
- **Pair ordering, Jev vs Haiku:** Jev-only 12, Haiku-only 2, McNemar p = 0.013, **WIN**.
- **AUC difference:** +0.070 [−0.003, +0.156], **TIE**.
- **Pass rule:** PASS.

**Headroom, from the committed run before any rerun** (`python3 work/score-quixbugs/variance.py
--bar`): **1 pair.** Moving one pair from Jev-only to Haiku-only gives 11 vs 3, p = 0.057, a TIE.
Losing Jev-only pairs without Haiku gaining any: 11 vs 2 p = 0.023, 10 vs 2 p = 0.039, 9 vs 2
p = 0.065. So 3 lost pairs end the WIN. This is the thinnest margin of any surviving Jev win.

**Runs.** Two more runs of each arm on the same 80 programs, same code path, pin, question and
state (`{"text": canon}`). Each run goes to a new file; no committed row file or receipt of
`jev-2wc` is edited.
- Jev: `run.py jev work/score-quixbugs/rows-jev-run{2,3}.jsonl`
- Haiku: `run.py haiku work/score-quixbugs/rows-haiku-run{2,3}.jsonl`. The adapter's
  `probability_errors` / `original_probabilities` are recorded as in run 1.
- The only change to `run.py` since `jev-2wc` is an optional output path (second argument). The
  call path, `QUESTION`, clients and settings are unchanged.
- Sequential order: Jev 2, Jev 3, Haiku 2, Haiku 3, each at 8 concurrent. Each run gets at most one
  resume pass for failed rows. A pair still unanswered is scored by `jev-2wc`'s rule (T, AUC at 2.0).
- Only `jev` and `haiku`, the primary arms, are re-run. `jev-flat` and `jev-asis` were descriptive
  and are not re-run.

**Scorer.** `python3 work/score-quixbugs/variance.py` (stdlib, no key). It imports `score.py`'s rules
unchanged: outcomes, sign test, AUC and bootstrap, McNemar, the paired AUC bootstrap, the pass rule
and the zero-mass drop. It exits 1 unless run 1 x run 1 reproduces every published `jev-2wc`
verdict. At the bar commit it does: 38/2/0, 28/10/2, 12 vs 2 WIN, AUC TIE, PASS.

**Rules, fixed now** (the all-pairings rule of `jev-x5k` / `jev-hg8` / `jev-91u`):
- **R1, decides: all 9 pairings** (Jev run j vs Haiku run h, j, h in 1..3). Each pairing gets
  `jev-2wc`'s full pass rule on all 40 pairs **and** with that Haiku run's zero-mass pairs dropped.
  - **HOLDS:** pair ordering WIN in 9/9 pairings, both ways.
  - **DOWNGRADED:** WIN in 5 to 8 of 9, both ways, and no LOSE. The headline becomes "Jev orders
    more pairs correctly in direction, significant in a majority of pairings, not all". PASS is kept.
  - **RETRACTED to TIE:** WIN in fewer than 5 of 9, and no LOSE. PASS is kept.
  - **PASS RETRACTED:** any pairing fails the pass rule. That happens if a Jev run fails to separate
    (W>L, sign p < 0.05, AUC CI above 0.5) or either comparison is a LOSE.
  - A `NEGATIVE_EVIDENCE.md` row with a retry condition follows any outcome other than HOLDS.
- **The published AUC TIE** is re-checked in all 9 pairings. It is not upgraded here even if every
  pairing shows WIN, because this bar only tests the published verdicts.
- **R2, describes: flips.** For each pair of runs of the same arm: pair outcomes (W/L/T) that change,
  and program scores whose rounded level changes. Compare these with the 1-pair headroom.

**Spend, planned.** 160 Jev + 160 Haiku calls, plus resume calls.

**NO-CLAIM.** Three runs per arm on one small public set (40 pairs), one question wording, one Jev
version, one Haiku configuration, all within one hour. This measures sampling variance of the served
models, not drift across days or versions.

## Result

Bar at `431a2fc`, committed before the first rerun call. Live, 2026-09-24, `[live]`. Four reruns in
sequence: 320 calls, 320 answered, 0 failed, 0 resume passes. Every Jev row reports `jev-1.13.0`;
every Haiku row reports `anthropic/claude-haiku-4-5`. Adapter debug was recorded on all 160 rerun
Haiku rows: 0 had `probability_errors` set, 0 were zero-mass. Row files (sha256 prefixes):
`rows-jev-run2.jsonl` `d9daeb65f467c059`, `rows-jev-run3.jsonl` `1e2b9c17e2dfc7dc`,
`rows-haiku-run2.jsonl` `86b546749023a105`, `rows-haiku-run3.jsonl` `aa88356924029930`. Re-score with
no key: `python3 work/score-quixbugs/variance.py`.

| Arm | Run | W / L / T | Sign p | AUC | Tokens in / out |
|---|---:|---|---:|---:|---|
| Jev | 1 (`jev-2wc`) | 38 / 2 / 0 | 1.5e-09 | 0.739 | 35,623 / 1,440 |
| Jev | 2 | 38 / 2 / 0 | 1.5e-09 | 0.724 | 35,623 / 1,440 |
| Jev | 3 | 37 / 1 / 2 | 2.8e-10 | 0.731 | 35,623 / 1,440 |
| Haiku | 1 (`jev-2wc`) | 28 / 10 / 2 | 0.0051 | 0.668 | 65,796 / 3,812 |
| Haiku | 2 | 25 / 13 / 2 | 0.073 | 0.634 | 65,796 / 3,786 |
| Haiku | 3 | 31 / 8 / 1 | 0.00029 | 0.683 | 65,796 / 3,749 |

**R1, all 9 pairings.** Each pairing was scored on all pairs and with that Haiku run's zero-mass pairs
dropped. There were none, so both columns agree.

| Jev run | Haiku run | Pair ordering: Jev-only / Haiku-only, McNemar p | Ordering | AUC diff [95%] | AUC | Pass |
|---:|---:|---|---|---|---|---|
| 1 | 1 | 12 / 2, 0.013 | **WIN** | +0.070 [−0.003, +0.156] | TIE | PASS |
| 1 | 2 | 14 / 1, 0.00098 | **WIN** | +0.105 [+0.023, +0.201] | WIN | PASS |
| 1 | 3 | 8 / 1, 0.039 | **WIN** | +0.056 [−0.032, +0.159] | TIE | PASS |
| 2 | 1 | 12 / 2, 0.013 | **WIN** | +0.056 [−0.018, +0.141] | TIE | PASS |
| 2 | 2 | 13 / 0, 0.00024 | **WIN** | +0.090 [+0.013, +0.177] | WIN | PASS |
| 2 | 3 | 8 / 1, 0.039 | **WIN** | +0.042 [−0.044, +0.140] | TIE | PASS |
| 3 | 1 | 11 / 2, 0.023 | **WIN** | +0.063 [−0.008, +0.146] | TIE | PASS |
| 3 | 2 | 13 / 1, 0.0018 | **WIN** | +0.097 [+0.021, +0.184] | WIN | PASS |
| 3 | 3 | 8 / 2, 0.109 | TIE | +0.048 [−0.036, +0.145] | TIE | PASS |

**Verdicts, per published metric:**
- **Pair ordering WIN: DOWNGRADED.** WIN in 8 of 9 pairings, TIE in 1 (Jev run 3 vs Haiku run 3,
  8 vs 2, p = 0.109), no LOSE. The headline becomes: Jev orders more QuixBugs pairs correctly than
  Haiku in every pairing, significantly in 8 of 9. `NEGATIVE_EVIDENCE.md` R91.
- **AUC TIE: stands.** WIN in 3 of 9 pairings (all three against Haiku run 2, Haiku's weakest), TIE
  in 6, no LOSE. The direction favours Jev in all 9 (+0.042 to +0.105).
- **PASS: holds, 9/9.** Every Jev run separates correct from buggy (37/1/2 to 38/2/0, AUC 0.724 to
  0.739, every AUC CI above 0.5), and no pairing is a LOSE.

**R2, flips.** Jev changes 2 to 4 pair outcomes and 1 to 4 rounded levels between runs. Haiku
changes 13 to 15 pair outcomes and 20 to 24 rounded levels. In pair outcomes, Haiku's run-to-run
spread is 3 to 7 times Jev's, and against a 1-pair headroom it decides the result alone: Haiku's
separation ranges from 25/13 (p = 0.073, not significant on its own) to 31/8.

**Spend.** 320 calls: Jev 160 (71,246 input / 2,880 output tokens), Haiku 160 (131,592 input / 7,535
output). [INFERENCE] The Haiku arm is about $0.17 at list price.

**Boundary.** Three runs per arm within minutes, 40 pairs, one wording, one Jev version, one Haiku
configuration. The one TIE pairing is the pairing of both arms' third runs, so this is a sampling
result, not a trend. A non-author spot-check is needed before the bead closes.

**Keyless fresh-clone re-score** (`[oracle]`, author-run). A `git clone` of `505701b` into
`/tmp/claimcheck-qb-clone`, with `TYPESAFE_API_KEY` and `ANTHROPIC_API_KEY` unset.
`python3 work/score-quixbugs/variance.py` exits 0 and prints the verdicts above (DOWNGRADED 8/9, AUC
TIE stands, PASS 9/9). `score.py` still prints `jev-2wc`'s committed run-1 result (12 vs 2 WIN, PASS).

## Non-author verification — Verifier3

Verifier3 (background agent of pane 1, Anthropic model), 2026-09-24. Not the author. Everything ran
in a fresh `git clone --local` of `71edf02` under `/tmp`. No call was made.

| Check | Command | Result |
|---|---|---|
| Bar precedes rows | `git show --stat 431a2fc 505701b`; `stat -f %SB` on the live worktree's rerun files | bar, scorer and the `run.py` change are at `431a2fc` (21:41:25 −0600). The four rerun files were born 21:41:46 to 21:42:20, all after it, and committed at `505701b` (21:43:50). The `run.py` diff only threads an output path through `answered()`, `main()` and the append. `QUESTION`, the clients and the call are untouched. |
| Bar text unedited | `git diff 431a2fc 505701b -- <receipt>`; `git diff 431a2fc HEAD --stat -- run.py variance.py score.py` | receipt additions only, with no line removed from the bar. The scripts are unchanged after the bar. |
| Re-score reproduces | `python3 work/score-quixbugs/variance.py` (rc 0, 17 s, no key) | run 1 × run 1 reproduces `jev-2wc` (38/2/0, 28/10/2, 12 vs 2 WIN, AUC TIE, PASS). Every number in both Result tables matches: per-run W/L/T, sign p and AUC, all 9 pairings' discordant counts, p, AUC intervals and pass, and the R2 flips. The verdicts are **pair ordering DOWNGRADED (8/9, the J3 × H3 pairing TIE at 8 vs 2, p = 0.109), AUC TIE stands (3/9 WIN, 0 LOSE), PASS 9/9**. |
| Input tokens per rerun | own script, per row | input tokens are identical to run 1 on 80/80 rows for Jev runs 2 and 3 and for Haiku runs 2 and 3, and every row reports the pinned model. |
| Independent recompute | own script, W/L/T per run from the stored scores | J1–J3 38/2/0, 38/2/0, 37/1/2; H1–H3 28/10/2, 25/13/2, 31/8/1. J3 × H3 is Jev-only 8, Haiku-only 2. All identical. |
| 10 seeded pairs by hand | `random.Random(24)` over the 40 names: find_first_in_sorted, get_factors, hanoi, is_valid_parenthesization, kheapsort, knapsack, pascal, possible_change, sqrt, to_base | Jev ranks correct above buggy on all 10 in all three runs, and its scores move by at most 0.05. Haiku's order flips across runs on knapsack (2.57>2.22, then 2.10<2.63, then 2.18>2.04), pascal (2.10>2.03, 2.95>2.06, then 1.95<2.28), sqrt (1.93<2.05, 1.96<2.01, then 2.31>1.35) and is_valid_parenthesization (1.92<1.93, 2.16>2.05, then a 2.05 tie). This agrees with R2: Haiku's variance, not Jev's, decides the TIE pairing. |
| Zero-mass handling | row fields | adapter debug recorded on 80/80 rows of each Haiku rerun, 0 set. The "without zero-mass" column correctly equals the main one. |
| NO-CLAIM vs what ran | receipt vs rows | 3 runs per arm, 40 pairs, one wording, one pin and one Haiku configuration. Only the primary arms were re-run, as stated. `NEGATIVE_EVIDENCE.md` R91 exists with a retry condition. |

**Verdict: CONFIRMED** (clean-clone keyless re-score, `[oracle]`): DOWNGRADED 8/9, AUC TIE stands,
PASS 9/9. Scratch left at `/tmp/v3-kz50.q27Z` (not deleted).
