# Bar provenance audit — 2026-09-25

Bead: `jev-le8u`
Lane: keyless audit; no Jev calls; no source bar changed.

This audit covers the six live-prereg surfaces named by the bead. The three filenames in the
original dispatch that said `20250925` are the current `20260925` files in the tree.

## Source classes

- **EXTERNAL** — a benchmark's own scorer or a published human/SOTA rate, with a URL.
- **INCUMBENT** — a paired comparison to the current implementation on the same rows.
- **ARITHMETIC** — computed from a recorded corpus, formula, or committed calculation.
- **DOCS** — a vendor/API document in this tree; the local citation is the authority.
- **UNSOURCED** — typed by this lane without one of the four sources above. The final column is
  the cheapest derivation that could replace the typed value; it is not a recommendation to
  change the preregistration in this audit.

A row may contain several related numbers when they form one pass rule. Denominators and fixed
protocol settings that are not themselves pass/fail gates are included when they bound a run or
can prevent a run from being scored.

## Inventory

### MiniWoB v3

Source: `docs/demos/upstream-repro/miniwob-jev-v3-prereg-20260925.md`.

| file:line | numeric bar / cap | what it gates | source | cheapest derivation if unsourced |
|---|---|---|---|---|
| `:40-42` | seeds `400..404`, `125` tasks, `10` steps, `0.5`-second wait | held-out denominator and per-episode protocol | UNSOURCED | Freeze the task manifest and derive the step/wait budget from the benchmark's published task protocol and a keyless timeout/coverage audit. |
| `:51-52` | exact paired McNemar `p < 0.05`; v3-only successes `>` v1-only successes | combined held-out PASS | UNSOURCED | Before the next run, choose family-wise alpha and the minimum discordance needed for power from the five-seed paired design; retain the strict direction as a separate estimand. |
| `:65-68` | quoted `N=16`: PASS `>=14/16`; FAIL `<=8/16`; `9..13` dev-only | quoted-span dev arm | UNSOURCED | Join these exact episodes to MiniWoB's published per-task human/SOTA rates, then choose a threshold that clears the external floor with a pre-run binomial/power calculation. |
| `:89-92` | date/time `N=10`: PASS `>=8/10`; FAIL `<=2/10`; `3..7` dev-only | date/time dev arm | UNSOURCED | Same task-level human/SOTA derivation, with a minimum detectable improvement chosen before reading the arm result. |
| `:107-110` | page text `N=35`: PASS `>=20/35`; `find-word <=2/5`; no regression on successful controls; FAIL `<=12/35` | page-text dev arm | UNSOURCED | Use the official per-task success rates for the 35-row slice and a paired non-regression power calculation for the already-successful controls. |
| `:150-153` | color `N=12`: PASS `>=8/12`; FAIL `<=3/12` | color dev arm | UNSOURCED | Use the published color/shape task rates and predeclare a binomial threshold with a stated effect size; the current file supplies neither. |
| `:170-173` | drag `N=87`: PASS `>=50/87`; FAIL `<=20/87`; no empty-action rows | drag dev arm | UNSOURCED | The file explicitly says this bar is proposed; derive it from task-level human/SOTA performance and an empty-action safety rate on a separate development slice. |
| `:265-268` | none `N=11`: PASS `>=6/11`; FAIL `<=2/11`; no empty-action rows | none-guard dev arm | UNSOURCED | Derive from the benchmark's task scorer plus a predeclared safety constraint for empty action sets; do not infer a bar from this slice's outcome. |

**MiniWoB result:** 8 inventory rows; 8 UNSOURCED, 0 EXTERNAL. The prereg names the autopsy
slices and task count, but does not cite a benchmark human/SOTA rate for any numeric dev bar.
The drag arm is the only one that labels its missing numeric source explicitly; the same gap
applies to the other arm bars.

### Emerald macro Choice

Source: `work/pokeagent-emerald/PREREG.md`.

| file:line | numeric bar / cap | what it gates | source | cheapest derivation if unsourced |
|---|---|---|---|---|
| `:59` | `1,200` requests/minute | TypeSafe request-rate ceiling | DOCS — `docs-mirror/typesafe/models.md:11-19` | — |
| `:59` | `20` requests/second | arithmetic conversion of the vendor ceiling | ARITHMETIC — `1,200 / 60` | — |
| `:60` | `N=80`; up to `40,000` requests (`80 * 500`) | planned live segment and spend ceiling | UNSOURCED | Run `work/pokeagent-emerald/power_mwu.py` over the frozen random rows for a preregistered MDE, then select the smallest N that reaches the target power while respecting a stated wall-time/cost ceiling. |
| `:60` | `130` ms assumed request latency; `225` ms macro cadence | timing feasibility assumption | UNSOURCED for `130` ms; ARITHMETIC for `225` ms (`18 / 80` seconds) | Replace the latency assumption with a recorded p95 from a measured Jev pilot and compare it with the computed cadence. |
| `:68`, `:72` | `500` macros after the fixed start | per-seed action cap and failure value | UNSOURCED | Derive the cap from the frozen baseline completion-vs-step curve and a declared maximum wall time; do not use the cap merely because seven random rows hit it. |
| `:74` | one-sided Mann–Whitney, `alpha=0.05`, `p<0.05` | primary treatment-vs-random decision | UNSOURCED | Freeze alpha after counting the decision family and use the committed power script to show detectable shifts and type-I-error behavior before any live calls. |
| `:74` | `75`- and `100`-macro shifts; power `0.637` and `0.810`; primary MDE about `100` macros | detectable-effect claim behind `N=80` | ARITHMETIC — `power_mwu.py` calculation recorded in the prereg | — |
| `:78` | fewer than `5` random goal-reaching runs ⇒ NO-CLAIM | prevents a distribution comparison with a vanishing control success cell | UNSOURCED | Derive the minimum from the intended median/quantile or success-rate confidence interval and freeze it before the next segment. |

**Emerald result:** 8 inventory rows; 5 UNSOURCED, 2 ARITHMETIC, 1 DOCS, 0 EXTERNAL and
0 INCUMBENT. The rule “success rate not below random” is an incumbent comparison but has no
additional numeric value; it is recorded in the row at `:74` rather than silently counted as a
source for the `p<0.05` bar.

### OSWorld Best-of-N

Source: `docs/demos/upstream-repro/osw-bestofn-loss-depth-dev-20260925.md`.

| file:line | numeric bar / cap | what it gates | source | cheapest derivation if unsourced |
|---|---|---|---|---|
| `:62-66` | exactly `60` calls per arm; `maxRetries=0`; `20`-second timeout | arm completeness and paid-call failure behavior | UNSOURCED | Freeze the call count from the task manifest and derive the timeout from a measured SDK/client p95 plus a hard stop for paid retries. |
| `:64-65`, `:224-226` | `$0.042/M` input tokens; output free | spend accounting | DOCS — `docs-mirror/typesafe/models.md:11-19` | — |
| `:71-72` | exact completion is `reward >= 1` | secondary binary metric | UNSOURCED | Resolve the threshold from the pinned OSWorld scorer's official reward semantics, with a URL or source-file citation, before using it as a pass metric. |
| `:73-74`, `:204-207` | mean reward `+0.03`; exact McNemar `p<0.05`; close at least `30%` of the oracle gap | primary win bar; all three required | UNSOURCED — inherited internal R104 bar, not an external benchmark bar | Set the SESOI from an operationally meaningful reward change, size paired power on an independent task set, and freeze the gap fraction from a stated decision utility. |
| `:96-102` | strict improvement `>` `original`; ties do not qualify | dev-arm selection | INCUMBENT — comparison to the original arm on the same tasks | — |
| `:104-110`, `:114-118` | `N=57` complement is outcome-selected and NOT-SCORED; original dev set is `60` within a `361`-task union | blocks a false held-out claim | UNSOURCED | Release a new task/run set independently of prior rewards, commit its digest before scoring, and use the full eligible set rather than an outcome-selected complement. |
| `:142-144` | `361` tasks, one rollout, `100` policy turns | valid-retest task and step budget | UNSOURCED | Cite the released package's run contract and derive the turn cap from coverage/cost requirements independent of per-task outcomes. |
| `:183-186` | scan `360`, exclude `23`, retain `337` | input-only exclusion and effective universe | ARITHMETIC — preflight receipt (`360 - 23 = 337`) | — |
| `:213-218` | effective `N=337`; `80%` power; MDE `0.07404` at `alpha=.05`; McNemar MDE `7.36` percentage points | sensitivity and detectable-effect disclosure | ARITHMETIC — formula and pinned `statsmodels`/SciPy calculation stated in the prereg | — |
| `:224-226` | estimated `337` calls, `2,696,921` input tokens, `$0.113270688` | retest budget estimate | ARITHMETIC — `337 * 8,002.733` tokens and the documented input price | — |
| `:229-233` | HTTP `401` or `402` is a hard stop; no retry or replacement row | paid-run stop rule | UNSOURCED | Derive from the paid API's authentication/billing failure contract and freeze the no-retry safety policy before the run. |

**OSWorld result:** 11 inventory rows; 6 UNSOURCED, 3 ARITHMETIC, 1 DOCS, 1 INCUMBENT,
0 EXTERNAL. The `+0.03` and `30%` values are not made external merely by being retained from
R104.

### Usage router

Source: `docs/demos/upstream-repro/usage-router-trial-choice-prereg-20260925.md`.

| file:line | numeric bar / cap | what it gates | source | cheapest derivation if unsourced |
|---|---|---|---|---|
| `:11` | `confidence >= 0.55`; otherwise `bypass` | router action gate | UNSOURCED | Use the non-authored labelled traffic corpus to choose a utility/coverage point, then freeze the confidence floor before a fresh replay. |
| `:17-18`, `:29` | discard goals longer than `4,000` characters; short-cell cutoff `<200` characters | corpus construction and subgroup definition | UNSOURCED | Run an inclusion-boundary sensitivity audit for label leakage, privacy, and routing prevalence; choose the cutoff before reading Jev outcomes. |
| `:34-36` | `94+94=188` goals; `3` repeats; `564` requests; seed `20260925` | fixed stratified trial denominator | ARITHMETIC for the counts; UNSOURCED for the seed choice | — for the counts; derive the seed from a committed reproducibility policy and record it before sampling. |
| `:40-41`, `:83` | incoherent/off-label answers accepted at `0` | response-validity acceptance | UNSOURCED | Use the SDK response contract to define malformed-answer refusal, then set a reliability SLO from historical transport/schema failure data rather than from this run. |
| `:46-47`, `:64` | prevalence `p = 94/2,307 = 0.0407` | converts stratified off-local precision to corpus prevalence | ARITHMETIC — recorded corpus counts | — |
| `:52-54`, `:89-90` | short non-local cell: `5 of 6 = 0.833` | reversal threshold for honouring the shadow action | UNSOURCED | Choose the threshold from a paired decision-utility analysis and a binomial confidence/power calculation on the 19-row short cell. |
| `:56-57` | `3` consecutive `401`/`402` answers stop the run | paid-key stop rule | UNSOURCED | Derive the stop count from the key-status contract and a no-retry billing safety policy, then freeze it before the next run. |

**Usage-router result:** 7 inventory rows; 5 UNSOURCED, 2 ARITHMETIC, 0 EXTERNAL, 0 DOCS
and 0 INCUMBENT. The trial has no preregistered numeric recall, precision, or false-route bar;
those are reported measurements, not pass rules.

### omp-jev-review advisory

Source: `docs/demos/upstream-repro/omp-jev-review-advisory-20260925.md`.

| file:line | numeric bar / cap | what it gates | source | cheapest derivation if unsourced |
|---|---|---|---|---|
| `:16-18`, `:36-37` | boundary `>=0.9` fires; `0.89` stays silent | advisory-line threshold and adjacent negative control | UNSOURCED for the threshold; the `0.89` case is a test boundary | Freeze an operator nuisance budget (for example, maximum advisory fire rate) on a development draw, choose the threshold there, and validate it on a separate diff holdout. |
| `:20-21` | on `125` diffs, `>=0.9` fired `3/125=2.4%`; `>=0.7` fired `13/125=10.4%`; “one in ten” is called a nag | threshold rationale, not an accuracy bar | ARITHMETIC for observed rates; UNSOURCED for the nuisance ceiling | — for the observed rates; derive the tolerated fire rate from recorded operator decisions or a preregistered alert budget. |
| `:23-26` | prior Score dimension AUC `0.625` under its `0.75` bar | rejected third dimension; not a bar for this extension | UNSOURCED — inherited internal prior | Re-run the 22 real-diff paired-label study with a preregistered AUC lower bound and independent holdout; do not transfer the old bar by prose. |
| `:43-65` | `N=12` live commits, `10` scored; p50 about `190` ms | live stability/latency disclosure | ARITHMETIC / observed, not a pass bar | — |

**omp-jev-review result:** 4 inventory rows; 3 UNSOURCED, 1 ARITHMETIC, 0 EXTERNAL, 0
DOCS and 0 INCUMBENT. The `0.9` value is explained by observed fire rate but is not itself
derived from a frozen alert budget.

### Gate-question gap

Source: `docs/demos/upstream-repro/gate-question-gap-20260924.md`, with executable constants in
`work/gate-question-gap/readout5.py` and `work/gate-question-gap/live-pass-5.mjs`.

| file:line | numeric bar / cap | what it gates | source | cheapest derivation if unsourced |
|---|---|---|---|---|
| `gate-question-gap-20260924.md:16,19`; `readout5.py:58`; `live-pass-5.mjs:8-10` | score cut `0.5`; candidate max is above `0.5` | current and candidate flags | UNSOURCED | Use a blind harm/no-harm ROC and an explicit false-alarm cost to choose the cut on development rows, then lock it before the paired comparison. |
| `gate-question-gap-20260924.md:56-57`; `readout5.py:59,123-128` | minimum `1,200` fresh rows | extract readiness; fewer rows refuse | UNSOURCED | Estimate target-harm prevalence from a label-free census and solve for the row count needed to detect the preregistered recall/false-alarm difference with paired power. |
| `gate-question-gap-20260924.md:91-94`; `readout5.py:60,160-164,232-236` | at least `10` target-harm rows | power gate before any live call | UNSOURCED | Derive the minimum from exact paired recall and false-alarm power at the smallest effect worth acting on; the current file supplies no effect-size calculation. |
| `gate-question-gap-20260924.md:113-116`; `readout5.py:311-318` | candidate target-harm recall `>=70%` and at least `5` more target-harm rows than current | improvement leg | UNSOURCED | Use blinded non-author labels to set a SESOI, then preregister exact paired power for both the percentage and absolute-count legs. |
| `gate-question-gap-20260924.md:117-118`; `readout5.py:312,320` | candidate false-alarm rate at most current `+2.0` percentage points | nuisance/non-inferiority leg | UNSOURCED | Derive the allowed increase from the operational false-alarm budget and size the Newcombe/McNemar comparison before labels are read. |
| `gate-question-gap-20260924.md:119`; `readout5.py:313,321` | candidate recall on all harm rows `>=` current recall | comparison to incumbent wording | INCUMBENT — current wording is the paired incumbent on the same rows | — |
| `live-pass-5.mjs:28` | `$0.042/M` input tokens | live receipt spend calculation | DOCS — `docs-mirror/typesafe/models.md:11-19` | — |

**Gate-question result:** 7 inventory rows; 5 UNSOURCED, 1 INCUMBENT, 1 DOCS, 0
ARITHMETIC and 0 EXTERNAL. The `14/934` false-alarm figure in the prereg's disclosure
(`gate-question-gap-20260924.md:39-41`) is an observed prior result, not a source for the new
`2.0`-point bar.

## Count and findings

Across the inventory there are **45 numeric gate/cap/pass rows**. A mixed row is counted by the
source class of the gate-bearing value; for example, the omp `125`-diff rates are arithmetic
observations, but that row is UNSOURCED because its `one in ten` nuisance ceiling is the operative
design choice.

| source class | rows |
|---|---:|
| EXTERNAL | 0 |
| INCUMBENT | 2 |
| ARITHMETIC | 8 |
| DOCS | 3 |
| **UNSOURCED** | **32** |

The dominant gap is not missing arithmetic. It is the absence of an external benchmark rate,
incumbent effect-size justification, or pre-run power/utility derivation for the typed thresholds.
The MiniWoB file explicitly marks the drag threshold as proposed, but its other five arm bars have
the same provenance shape. The OSWorld `+0.03` and `30%` values are inherited internal bars, not
external evidence. The omp `0.9` line is selected from observed fire rates without a frozen
nuisance budget.

No bar is changed by this audit. Cheapest next derivations are named per row above; they belong in
new preregistration amendments, not retroactive edits to this inventory.

## Boundary

- Keyless only. No TypeSafe request, comparator request, or external model call was made.
- This is a provenance audit, not a verdict on any arm and not evidence that an UNSOURCED bar is
  wrong; it identifies what would be needed to justify it.
- Observed result counts, latency, spend, seeds, and hashes are retained in the source files but
  are not silently promoted to bar provenance.
