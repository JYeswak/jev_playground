# Duel 1 — synthesis

**What ran.** Two lineages independently proposed five installable Jev demos each from the same
14-pattern map (`docs/demos/USAGE-MAP.md`), scored each other, then a third lineage graded both,
audited every number, steelmanned the losers, and ruled on the orchestrator's own headline claim.
Three models, 10 ideas, **20 grader scores**, 14 artifacts.

**Who is who.** CC = pane 1 (Claude, also the orchestrator — me). MU = pane 3 (muse).
COD = pane 2 (codex lineage, titled `omp-claude_1`; the profile trap `AGENTS.md` documents, which
is what made it the arms-length grader). **I authored CC and wrote this report**, so every place
the synthesis favours CC is flagged, and the bias audit below is checkable arithmetic rather than
an assurance.

---

## 1. The headline I published was wrong, in both directions

I claimed **four of five ideas converged across lineages** and built a backlog framing on it:
*"the dispute is implementation, not concept."* I queued an arms-length audit of my own claim.
Pane 2 ruled it **overstated** (`WIZARD_CONVERGENCE_AUDIT_COD.md`, `9b0965b`), with a file:line
quote for every pair.

| Pair | My claim | Ruling | Deciding difference |
|---|---|---|---|
| MU-1 ↔ CC-3 routing backtest | same | **SAME DEMO** | both read-only per-turn backtests over our own omp logs |
| MU-5 ↔ CC-4 signals | same | **SAME DEMO** | both fit a small head over signal questions and keep a fixed-rule baseline |
| MU-2 ↔ CC-5 admission screen | same | **ADJACENT BUT DISTINCT** | MU adds a credential classifier and fail-closed block; CC is injection-only, shadow-first, fail-open |
| MU-4 ↔ CC-2 claim-check | same | **ADJACENT BUT DISTINCT** | MU checks notes against an evidence dir; CC checks numeric triples in staged commit messages |
| MU-3 foreman-lite | CC singleton | **NOT a singleton** | CC's own long list has it at #6 |
| CC-1 fact ledger | MU singleton | **NOT a singleton** | MU's winnowed list has it as R3 |

**My error was a denominator error, again.** I compared two *top-five shortlists* and called the
overlap convergence, when the honest denominator is the two *full 15-item inventories*. And I used
a similarity-of-theme test where the right test is *same shippable demo*. The result is that I
overstated the pair convergence and **understated** the singletons in the same table.

**What is actually true:** 2 of 4 top-five pairings are the same demo; both "singletons" have
same-demo counterparts outside the other lineage's shortlist; and across the full inventories both
lineages covered all six concepts. That is **concept coverage, not shortlist consensus** — a
weaker and more useful claim.

**Consequence for the backlog:** the distinct-demo count is **8, not 6**. Two merged demos, four
genuinely separate implementations of two shared seams, and two cross-shortlist demos.

---

## 2. The complete score matrix

Every idea has two independent graders. That was not true when the duel "finished" — it ran with
one grader per file, so no idea had two scores and consensus was literally unmeasurable. Two units
closed it: I scored MU, and pane 2 scored CC.

| Idea | grader 1 | grader 2 | mean | spread |
|---|---:|---:|---:|---:|
| MU-1 routing backtest | 875 (COD) | 870 (CC) | **872.5** | 5 |
| CC-5 admission screen | 880 (MU) | 855 (COD) | **867.5** | 25 |
| CC-2 claim-check gate | 850 (MU) | 820 (COD) | **835.0** | 30 |
| CC-3 routing backtest | 830 (MU) | 840 (COD) | **835.0** | 10 |
| MU-3 foreman-lite | 805 (COD) | 820 (CC) | **812.5** | 15 |
| CC-1 fact ledger | 740 (MU) | 845 (COD) | **792.5** | **105** |
| MU-4 claim-checker | 735 (COD) | 800 (CC) | **767.5** | 65 |
| CC-4 signals starter | 800 (MU) | 710 (COD) | **755.0** | 90 |
| MU-5 signal-kit | 640 (COD) | 700 (CC) | **670.0** | 60 |
| MU-2 admission screen | 470 (COD) | 620 (CC) | **545.0** | **150** |

### Per demo, after the convergence ruling

| Demo | graders | mean | range |
|---|---:|---:|---|
| admission screen — CC-5 form (injection-only, shadow) | 2 | **867.5** | 855–880 |
| **routing backtest** (MU-1 ≡ CC-3, merged) | **4** | **853.8** | 830–875 |
| claim-check — CC-2 form (commit-message gate) | 2 | 835.0 | 820–850 |
| foreman-lite completion judge (MU-3) | 2 | 812.5 | 805–820 |
| fact ledger (CC-1) | 2 | 792.5 | 740–845 |
| claim-check — MU-4 form (notes vs evidence dir) | 2 | 767.5 | 735–800 |
| signals starter (MU-5 ≡ CC-4, merged) | 4 | 712.5 | 640–800 |
| admission screen — MU-2 form (credential, fail-closed) | 2 | 545.0 | 470–620 |

---

## 3. Bias audit — the part that is checkable

Two of the four grader-passes were by an author of the competing file. If authors scored down the
competition, the matrix is worthless. They did not, and the arithmetic says so:

| Grader pass | mean | authored a competitor? |
|---|---:|---|
| MU on CC | 820.0 | yes |
| COD on CC | 814.0 | **no** |
| CC on MU | 762.0 | yes |
| COD on MU | 705.0 | **no** |

- **Both authors rated the opponent's file at or above the neutral grader.** MU rated CC 820 vs
  COD's 814. I rated MU 762 vs COD's 705 — I was **57 points more generous to my opponent than
  the neutral party was.** Score-suppression is not visible in these numbers.
- **But that is suggestive, not dispositive, and pane 2's audit was right to say so.** An author
  scoring an opponent above the neutral grader does **not** prove absence of bias: the scores are
  subjective rubric judgments with no calibrated external oracle behind them, so "generous to my
  opponent" and "correctly graded my opponent" are indistinguishable from the numbers alone. Bias
  could also run the other way — inflating a rival's weakest ideas costs nothing and buys the
  appearance of fairness. **What the disclosure buys is auditability, not exoneration.** The
  arithmetic is evidence in its favour; it is not proof, and I should not have implied otherwise.
- **The neutral grader's own cross-file gap is the largest of all:** COD put CC at 814 and MU at
  705, a **109-point** gap. So the finding "CC's shortlist scored higher" is *strongest* in the
  one pass with no stake in it.
- Whole-file means: CC 817.0, MU 733.5 across all 10 scores each (gap 83.5). Dropping each file's
  weakest idea: CC 832.5, MU 780.6 (gap 51.9). **Half the raw gap is one idea** — MU-2 at 545.
- **I am the author of the higher-scoring file and the writer of this report.** The defensible
  reading is not "CC won" but "MU-2 lost, and it lost for one nameable reason."

---

## 4. The 410-point disagreement, and what it bought

The same seam — screening bytes before they enter context (map §1) — scored **880 as CC-5** and
**470 as MU-2**. Not model noise: MU-2 asks Jev *"does this content carry credential material"*,
which requires shipping the credential to a third-party API. **The hook would leak precisely what
it exists to protect.** CC-5 never asks that question.

Pane 2 found it while grading, then steelmanned it (`ad4c1d0`) and concluded the defect is
*"fixable rather than structural."* Pane 3 conceded it fully in its reveal reaction (`11c3c33`),
calling it "the finding of the duel." I scored it 620 rather than 470 on the argument that one
deletable branch is not a design.

**All three lineages reached the same remedy — but POST-REVEAL, and that distinction is the one I
keep getting wrong.** Pane 2 arrived at it by steelmanning MU-2 after grading it; pane 3 conceded
it after reading pane 2's scores. That is sequential agreement following disclosure, **not
independent convergence** — nobody proposed this remedy before seeing another lineage's critique.
Calling it independent would repeat the exact error that made my §1 headline wrong. Corrected on
pane 2's audit (`WIZARD_REPORT_AUDIT_COD.md`, `b11aaa5`), which caught it.

The merged spec: run the local deterministic `30-no-secrets` detector first and redact; keep only
the injection question (the 0.99 witness); adopt **MU-2's install rigor** (idempotent; refuses when
the hook dir is undiscoverable — the `.omp/hooks/`-without-`pre/` silent miss, a check CC-5
lacked).

**This is the duel's actual product.** A single pane proposing the screen hook would have shipped
either CC-5's under-specified install or MU-2's leak. Neither author found their own defect.

---

## 5. Consensus · contested · killed

**Consensus (build-worthy):**
- **routing backtest** — 4 graders, mean 853.8, range 45 across two lineages. Read-only, inputs
  already on disk, no live calls to produce evidence. No grader below 830.
- **admission screen — CC-5 form only** — mean 867.5, no grader below 855. **The merged
  CC-5-form-plus-MU-2-install-rigor design has never been scored by anyone**; MU-2's own form sits
  at 470/620. So "no grader below 800" is true of CC-5 as written and says nothing about the merge.
  Any build of the merged form starts unscored and should be graded before it ships.
- **claim-check, CC-2 form** — mean 835. Takes MU-4's *insufficient-context ⇒ withhold, never
  approve* rule, which was better specified than CC-2's original.
- **foreman-lite** — mean 812.5, and it carries the best single RED arm in either file: *a bead
  with an empty diff must return human-needed, never complete.*

**Contested (real disagreement, not noise):**
- **fact ledger CC-1**, spread 105 — the widest on any single demo. MU scored 740 *before* I
  repaired its mechanism; COD scored 845 *after*. The repair (deterministic extractor → Choice
  over candidate lines → Noul verbatim check, because *a Noul judges, it does not extract*) is
  worth ~105 points, and grader means differ by only 6, so it is not grader harshness.
- **claim-check MU-4 vs CC-2**, 767.5 vs 835 — two distinct demos on one seam. Pick one; do not
  build both.

**Killed:**
- **MU-2's credential branch.** Delete, do not fix. Conceded by its author.
- **signals starter**, mean 712.5 — lowest of the converged demos, greenfield, no lane payoff
  until a corpus lands. **And its own retry condition is now further away than it looked**, see §6.

---

## 6. What only the synthesis seat could see

**MU-5's retry condition has been invalidated by an unrelated measurement.** Its gate was
disciplined: *"apply to resume-quality signals only once A/B receipts accumulate past N≥50 —
today N=4; fitting now would be the cherry-picked-N violation."* Correct at the time. But
`NEGATIVE_EVIDENCE.md` R11 has since established that our A/B's arm B is **nondeterministic** —
it scores **3, 1, 3 on a byte-identical fixture** (`EVAL.md` Boundary; receipts `ab-20260917`,
`ab-rerun-20260918`, `ab-sample3-20260918`). Accumulating 50 receipts of a coin-flip arm would fit
a model on noise and call it calibration. **The gate must change from a count to a property:**
N≥50 receipts *from a pinned generator*, or a published distribution. A sample-count threshold over
an unpinned generator is the same error class as pinning a demo threshold to a stochastic
baseline — which is the other thing R11 caught, in my own CC-1.

**The routing backtest inherits a stale-fact liability nobody scored.** Both forms ship a
committed per-model price table. Our own Jev doc review flagged pinned facts at stale-risk 2+;
dollar figures in a receipt rot silently. The merged spec needs a dated `as_of` field or a
re-derivation path. MU-1 also calls the served model an "oracle proxy" — it is the incumbent
policy's choice, so it is a **baseline**, not ground truth for what a turn needed.

---

## 7. Corrections the duel forced

Every one of these came from an adversarial pass, not from the author noticing:

| Correction | Found by | Fixed at |
|---|---|---|
| CC-1 claimed 4 recall questions; the receipt has 3 (arm B 3/3, arm A 1/3) | pane 3, grading CC | `5343463` |
| "the four existing questions" — a *residual* instance of the same error, left standing after the first fix | pane 2, claim audit | `a19fc98` |
| "33 points worse" — the cited source gives 62.6% vs 95.1%, so 32.5 | pane 2, claim audit | `a19fc98` |
| My "4 of 5 converged" headline | pane 2, convergence audit | this report |
| CC-1's threshold pinned to arm B, a stochastic baseline | pane 2's A/B re-run + a third sample | `3234bce` |
| `EVAL.md` read "No A/B-vs-LLM runs yet" after three had run | me, while correcting the above | `3234bce` |

Pane 2's claim audit graded 60 numeric claims: **19 EXACT, 4 WRONG, 37 UNVERIFIABLE**. The 37 are
not a grading failure — they are the finding that the map's 18 pinned community-repo citations are
not vendored, so the numbers this entire backlog rests on cannot be re-derived in-repo. Filed as
`jev-demo-loop-a1q.2`.

---

## 8. Recommendation: build the routing backtest first

Not the highest mean. **The most defensible.**

- **4 graders, range 45**, across two lineages that proposed it independently — the only demo
  with that much agreement, and per the convergence audit one of only two genuine SAME DEMO pairs.
- **Read-only, inputs already on disk.** Produces its evidence with zero live calls, which matters
  in a lane whose one live measurement just turned out to be a coin flip.
- **It is the evidence gate for a bigger demo.** It answers "would routing have saved us anything
  on *our* turns" before anyone builds live rerouting. Upstream measured −60% on *their* 237
  turns; that is their corpus, not ours.
- CC-5 scores 14.7 points higher but has **2 graders and a 410-point sibling disagreement** on the
  same seam. That gap is the tell that the implementation is unsettled — exactly what a first
  demo should not be.

**Sleeper worth naming:** the fact ledger (CC-1, mean 792.5) had its premise *strengthened* by the
A/B refutation. arm A (Jev-prune) scored **1/3 in all three runs across two corpora** — pruning
robustly drops answer-bearing facts. The same evidence that killed the demo's comparison confirmed
the problem it exists to solve, and its threshold is now absolute rather than relative.

---

## NO-CLAIM

Judgment and arithmetic only. **Nothing here was built, installed, or run** — no demo exists; the
backlog remains a backlog. I am the author of the higher-scoring file and the writer of this
report; pane 2's passes are the arms-length ones and outrank mine wherever we disagree. The
convergence ruling is pane 2's, quoted, not re-derived by me. Scores are five human-authored
rubric judgments per idea, not a measurement: a 15-point gap between two demos is noise, and the
per-demo means are means of 2 or 4 opinions. The 20 scores have not been re-checked arithmetically
by anyone but me — that audit is dispatched, not done. 37 of 60 numeric claims underlying these
ideas remain **unverifiable in-repo**. No consensus set has been converted to beads or to
`docs/demos/PLAN.md`.
