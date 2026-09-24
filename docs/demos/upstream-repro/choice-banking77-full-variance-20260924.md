# Does the full Banking77 77-intent WIN hold on three runs of each arm? (bead `jev-384m`)

MaintFixes (background agent of pane 1), 2026-09-24. Live lane, model pinned `jev-1.13.0`, incumbent
Claude Haiku 4.5 through `system-one-adapter-python` at `adffc2e` in prompted-JSON mode.

## Preregistered (committed before the first rerun call)

**Why.** `jev-4jf` (`choice-banking77-full-20260924.md`) found a WIN on all 3,080 Banking77 test
queries across 77 intents: Jev 2,467 against Haiku-prompted 2,267, McNemar 326 vs 126,
p = 1.7e-21, PASS. That came from one run per arm. `R88` (Yelp) showed that one run of each arm
can mislead: there, 3 of 9 pairings were WIN. The README states this win, so it gets the same
3 x 3 check as the other published wins (`jev-qbc`, `jev-x5k`, `jev-hg8`, `jev-91u`). The margin
is large, so the expected outcome is HOLDS. That expectation does not change the rule.

**What runs.** Everything is unchanged from `jev-4jf`: the same 3,080 rows (`full.jsonl`), the
same single 77-option Choice (state, question and labels built by `run.py`), and the same settings.
Only the output paths are new, and no committed row file is touched.
- **Jev, runs 2 and 3:** `run.py --set full --out work/choice-banking77/rows-full-jev-run{2,3}.jsonl jev`
  (official `typesafe_sdk`, `jev-1.13.0`).
- **Haiku, runs 2 and 3:** `run_prompted.py --out work/choice-banking77/rows-full-haiku-prompted-run{2,3}.jsonl`.
  This is `jev-4jf`'s declared second-preregistration fallback, with `structured_outputs=False`,
  one corrective retry for malformed JSON, `llm_answer_mode="probabilities"` and normalized
  probabilities. The only code change in this commit is the `--out` flag on `run_prompted.py`
  (the same shape `jev-qbc` gave `run.py` in `8851fcd`). The default path is unchanged.
- **Concurrency:** the four runs go at once, as four processes, each at the runners' own
  `CONCURRENCY = 8`, the same as `jev-4jf`. Latency is client wall clock under that load and is
  descriptive.
- **Resumes:** each runner resumes ids that lack an answer. A run with more than 1% failed rows
  (30, `jev-4jf`'s limit) after resuming is NOT-SCORED.

**Scorer, keyless:** `python3 work/choice-banking77/variance_full.py`. It imports this unit's
`score.py` (`arm_stats`, `mcnemar_exact`, `is_flat`, and the `FEASIBLE`, `MARGIN_PP` and `ALPHA`
constants) and applies `jev-4jf`'s verdict rule unchanged: feasibility floor 50%, the constant
40/3,080, a 3.0 pp margin and McNemar exact. It exits 1 unless run 1 x run 1 first reproduces the
committed numbers. Run before any rerun call, it printed: `run 1 x run 1 reproduces jev-4jf: yes
(Jev 2467, Haiku 2267, McNemar 326 / 126, p = 1.7e-21, WIN)`.

**Headroom from the committed run** (`--bar`). The WIN ends after **151** Haiku answer changes
(4.9% of 3,080), each turning a Jev-only row into both-correct or a both-wrong row into
Haiku-only. The WIN ends when b <= c or McNemar p >= 0.05. A LOSE needs Haiku to gain 293
correct answers, to above 2,559.

**R1, decides: all 9 pairings** (Jev run j against Haiku run h, j and h in 1..3), each scored by
`jev-4jf`'s rule:
- **HOLDS:** WIN in 9/9 pairings. The README sentence stands, and a "held on three runs of each
  arm, 9/9 pairings" clause may be added.
- **DOWNGRADED:** WIN in 5 to 8 of 9, with no LOSE and no NOT-SCORED. The headline becomes "Jev
  routes more correctly in direction, and significantly in a majority of pairings, not all". PASS
  is kept.
- **RETRACTED to NON-INFERIOR:** WIN in fewer than 5 of 9, with no LOSE and no NOT-SCORED. PASS is
  kept.
- **PASS RETRACTED:** any pairing is LOSE or NOT-SCORED.
- Any outcome other than HOLDS gets a `NEGATIVE_EVIDENCE.md` row with a retry condition. No
  wording, option list, margin or threshold changes after an answer is seen.

**R2, describes: flips.** For each pair of runs of the same arm, count the rows whose chosen intent
differs, and compare it with the 151-row headroom.

**Also reported, descriptive.** Per run: answered, failed, correct, accuracy, p50/p95 latency,
input/output tokens, and flat (uniform) Haiku rows. Per pairing, as in `jev-4jf`: McNemar with
Haiku's flat rows dropped, and with them credited to Haiku.

**Stated before running:** 6,160 Jev calls and 6,160 Haiku calls (12,320), plus resumes of failed
rows only. Spend is not capped (AGENTS.md, Live Call Budget Gate) and is reported.
[INFERENCE] At `jev-4jf`'s token counts, the two Haiku runs cost about $43 at list price and the
two Jev runs about $0.25.

**NO-CLAIM.** Three runs per arm within one evening, with one Jev version, one Haiku version, one
adapter version, one wording and undescribed options. The Haiku arm is the prompted-JSON fallback,
not native structured output, which Anthropic rejects for this grammar. HOLDS would show the win is
stable across these runs, not that it transfers to other prompts or models.

## Results

Pending the live runs.
