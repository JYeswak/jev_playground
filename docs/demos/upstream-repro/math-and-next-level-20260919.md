# Math we already use, math sitting unused, next-level Jev ticks

**Date:** 2026-09-20 · **Level:** `[oracle]` — every numeral below is quoted from a committed
receipt or from a public upstream file fetched this turn. No live Jev calls.

**This is not another CLI inventory.** The inventory already exists:
[`franken-crate-alpha-20260919.md`](franken-crate-alpha-20260919.md) ranks `promotion_gate_runner`,
`franken_decision`, and `universal_dominance_ratchet` as unused *process*. This file does the
math those crates encode, against the numbers this lane has already measured.

**Upstream pins (public `gh api`, 2026-09-20):**

| repo | HEAD | files opened |
|---|---|---|
| `Dicklesworthstone/asupersync` | `c80b20609` | `franken_decision/src/lib.rs`, `src/lab/oracle/eprocess.rs`, `docs/raptorq_expected_loss_decision_contract.md` |
| `Dicklesworthstone/franken_engine` | `fc37f2dec` | `promotion_gate_runner.rs`, `universal_dominance_ratchet.rs`, `runtime_decision_theory.rs` |
| `Dicklesworthstone/skillranker` | `bb52b8f25` | `tests/eval/evaluation_policy.v1.json`, `expected_values.v1.json` |

**Local receipts opened first:**
`skillranker-corpus-measured-20260919.md`, `prevalence-retrofit-20260919.md`,
`random-judge-substitution-20260919.md`, `RULING-authored-vs-real-20260919.md`,
`franken-crate-alpha-20260919.md`, `docs/demos/SDK-SURFACE.md`,
`work/skillranker-eval/oracle.mjs`, `foundation/CALIBRATION.md`,
`foundation/runs/20260917T224444Z.json`, `docs/demos/STATUS.tsv`.

---

## 1. Math we already use

### 1.1 Skillranker 0/1/2 loss + always-abstain control

Their frozen contract (`tests/eval/evaluation_policy.v1.json:58–72`, status
`frozen_contract_not_evidence`) is a proper scoring rule for an *advisory* surface: it charges
missed help, not only wrong help, so always-abstain cannot win by silence.

| outcome | loss \(L\) |
|---|---:|
| correct recommendation on positive | 0 |
| correct no-match abstention | 0 |
| **false abstention on a positive** | **1** |
| incorrect recommendation on a positive | 2 |
| needless recommendation on no-match | 2 |
| operationally unavailable after attempt | 2 |

Normalized: \(y = L/2\) (`evaluation_policy.v1.json:67`). Their rationale, quoted: *“A loss that
charges only wrong emitted suggestions is invalid because always abstaining would minimize it
without helping positive cases.”*

On their 12-case diagnostic corpus (10 positives / 2 no-match, prevalence \(10/12 = 0.833\)):

\[
\bar L_{\text{always-abstain}} = \frac{10\cdot 1 + 2\cdot 0}{12} = \frac{10}{12} = 0.833
\]

That identity is why `oracle.mjs` hard-codes `ABSTAIN_CONTROL = 0.833`. The coin-flip baseline
**1.011** (5,000 trials, `oracle.mjs:16–18`) is *worse than doing nothing* — the corpus is
discriminative. Oracle is 0 by construction.

**Live Jev on that corpus** (`skillranker-corpus-measured-20260919.md`, `jev-latest` → one run):

| metric | value | formula |
|---|---|---|
| mean loss | **0.167** | \(2/12\): two false abstentions, zero wrong picks |
| top-1 precision on positives | **0.800** | \(8/10\) |
| their promotion gate | **0.90** | `top_one_precision.minimum_rate` (`evaluation_policy.v1.json:150–153`) plus Wilson lower endpoint ≥ 0.80 |

Both misses are the *cheap* error (\(L=1\), not \(L=2\)). Mean loss is \(0.833/0.167 = 5\times\)
better than always-abstain and still **fails their gate by one case**. The contract itself forbids
treating `split: diagnostic_synthetic` as holdout (`evaluation_policy.v1.json:53–56`).

**Harness defect, same file:** an invented `helpful` noul ≥ 0.5 gate moved mean loss
**0.750 → 0.167**. The choice was already confident (`topP` 0.74–1.00); the extra noul never
cleared 0.50. That is a selector bug, not a model result — see §4(d).

### 1.2 Prevalence retrofit — AUC without a base rate is not a deployability number

Bayes on a detector. Let \(\pi = P(Y{=}1)\), TPR at a threshold, FPR at that threshold.
Expected false alarms per true catch:

\[
\frac{\text{FP}}{\text{TP}} \approx \frac{(1-\pi)\,\text{FPR}}{\pi\,\text{TPR}}
\]

Measured (`prevalence-retrofit-20260919.md`, `RULING-authored-vs-real-20260919.md`):

| surface | sample \(\pi\) | population \(\pi\) | at operating point |
|---|---|---|---|
| foreman stuck-window | 10/20 constructed | **30 / 186,449 = 0.016%** | 80% recall → **~24 TP vs ~55,791 FP ≈ 1:2300** |
| bicameral tool-call gate | dangerous 20/40 | routine danger **<0.1% (est.)** | 15% FP on ~100% of traffic |
| fast-jev-compaction | needed 84–92/96 (~90%) | same sessions ~90% reuse | dropping 98% of a 90%-needed population ≈ **9:1 wrong:right on drops** |
| skillranker | 10/12 (83%) | UNKNOWN (synthetic; repo forbids holdout) | precision 0.80 would fall if \(\pi\) falls |
| router-tier | 25/25 by design | hard turns ~253/278 ≈ 91% | prevalence *helps*; AUC 0.56–0.63 still < 0.70 |

**No verdict inverted.** Every `RULED_OUT` already died on cost, signal-below-bar, or gate miss.
The retrofit's job was to stop publishing an AUC as if it were a ship number.

Foreman is the clean identity. At \(\pi = 30/186449\), even a strong separator cannot reach
parity of TP:FP without a threshold that zeros recall. The useful move is **change the base
rate** (trigger only in already-suspicious contexts), not “tune 0.80.”

### 1.3 Proper scores we already compute — ECE / Brier

`foundation/run_calibration.py:146–147` (receipt `foundation/runs/20260917T224444Z.json`,
`jev-latest` → `jev-1.13.0`, n=60 noul, 0 errors):

\[
\text{ECE} = \sum_{b=1}^{10} \frac{n_b}{n}\,\lvert \widehat{\mathrm{acc}}_b - \bar p_b \rvert = 0.0613
\]

\[
\text{Brier} = \frac{1}{n}\sum_i (p_i - y_i)^2 = 0.0199
\]

Threshold sweep on the same receipt (`:1241–1271`): at \(t \ge 0.75\), accuracy **1.0** at
coverage 0.95; at \(t=0.90\), accuracy 1.0 at coverage 0.90. `CALIBRATION.md` states the
limit: easy hand-written items; n=60 → wide per-bin Wilson CIs; no Choice-confidence
calibration.

`work/oracle-kit/index.mjs:68–84` implements the same ECE and **flags a constant score**
(`auc().constant`) because a missing SDK field produced AUC **exactly 0.500** on three
router runs (`SDK-SURFACE.md`). Mann–Whitney:

\[
\mathrm{AUC} = \frac{\#\{a>b\} + \tfrac12\#\{a=b\}}{n_+ n_-},\qquad
\text{ties count half, both classes required}
\]

Brier is the unique proper score (up to affine transform) that is also a calibration +
refinement decomposition. We compute it. We do **not** put it on a `STATUS.tsv` row, and we
do not have a withhold-aware Brier (skillranker names `fit_brier` in the contract and never
runs it).

### 1.4 Random-judge survival — most suites do not score judgment

`random-judge-substitution-20260919.md`:

| | |
|---|---|
| executable tests | 305 |
| still green under a well-formed random judge | **254 (83%)** |
| broke for a tautological reason (pinned the mock's own literal) | 35 of the 51 failures |
| class-C (label the judge did not supply) | **17, all in one file** (`system-one-adapter-python`) |
| tests that score **Jev itself** against an independent label | **1** |

Coin-flip on skillranker's unused corpus: mean loss **1.011 ± 0.210**, uniform-pick top-1
**0.484** against a 0.90 gate. The corpus can kill a random judge. `src/` never reads it.

### 1.5 Cost-benefit kill vs capability kill

`docs/INTEGRATIONS.md` and `RULING-authored-vs-real-20260919.md` (second axis): five surfaces
where a cheap deterministic baseline beat Jev. The load-bearing distinction:

| kind | what died | example |
|---|---|---|
| **capability kill** | the score does not rank the thing | compaction `keep_p` AUC **0.348–0.648**; positive control **0.941** — the harness sees signal; Jev does not rank future need |
| **cost-benefit kill** | the score is fine and still not worth calling | harm-rule: regex **12/12** recall, FP **0/38**; live Jev **11/12**, historical FP 0/40. Jev is *good*. The regex is free and strictly dominates. **Ledger stays 0 promoted.** |

Capability kill ⇒ do not ship that question. Cost-benefit kill ⇒ keep the measurement, drop
the paid call. Confusing them produces either false despair (“Jev is bad”) or false ceremony
(“we should still wire it because 11/12”).

dcg prior, same surface (`dcg-block-rate-prior-20260919.md`): **488 / (49,661+488) = 0.97%**
block rate. Jev gate v2 fired at **15%** (3/20) on held-out daily commands — ~15× noisier than
the regex it would sit next to.

### 1.6 Authored → real collapse (the measurement law, not a moral)

Three candidates measured both ways, all fell
(`RULING-authored-vs-real-20260919.md`):

| candidate | authored | real |
|---|---|---|
| tool-call gate | 0/20 FP | **3/20 FP**, AUC 0.865 |
| foreman | AUC **1.000** | **0.750** on 186k windows |
| jev-review pair order | **12/12** | AUC **0.625** on 22 real diffs |

One promotion awarded and **retracted by its author** the same day. `promoted = 0` is the
honest state, not a badge.

---

## 2. Math sitting unused in Franken (`file:line` at the pins above)

`franken-crate-alpha-20260919.md:142–153` already said these are unused. The formulas:

### 2.1 Bayesian loss matrix / Decision Contract

`asupersync/franken_decision/src/lib.rs:9–12, 348–404`.

A contract is a finite state space \(S\), action set \(A\), and a non-negative loss matrix
\(L(s,a)\). Posterior \(\pi_t\) over \(S\). Bayes action:

\[
a^\star(\pi) = \arg\min_{a\in A}\; \mathbb{E}_{s\sim\pi}\bigl[L(s,a)\bigr]
= \arg\min_a \sum_s \pi(s)\, L(s,a)
\]

Ties broken by lowest index (`:396–404`). Expected loss is fail-loud if
\(\lvert\pi\rvert \ne \lvert S\rvert\) (`:362–369`) — a dimension mismatch returns a
plausible-but-wrong number otherwise. That is the same defect class as reading
`.distribution` instead of `.probabilities`.

Worked 2×2 in the crate docs (`lib.rs:59–64`):

| \(L\) | continue | stop |
|---|---:|---:|
| good | 0.0 | 0.3 |
| bad | 0.8 | 0.1 |

At \(\pi=(\text{good }0.8,\;\text{bad }0.2)\):
\(\mathbb{E}[\text{continue}]=0.16\), \(\mathbb{E}[\text{stop}]=0.26\) → continue.
At \(\pi=(0.2, 0.8)\): \(0.64\) vs \(0.14\) → stop.

**FallbackPolicy** (`lib.rs:537–618`), default `:616–618`:

\[
\text{fallback if }\;
\text{calibration} < 0.7
\;\lor\;
e_t > 20
\;\lor\;
\text{CI width} > 0.5
\]

RaptorQ's production contract (`docs/raptorq_expected_loss_decision_contract.md:15–43`) makes
the same shape operational: states `{healthy, degraded, regression, unknown}`, actions
`{continue, canary_hold, rollback, fallback}`, **asymmetric** \(L\) so `continue` is cheap
when healthy and expensive when unknown/regression. Required emission per decision:
`state_posterior`, `expected_loss_terms`, `chosen_action`, `confidence_score`,
`uncertainty_score`, `deterministic_fallback_trigger`, `replay_ref`.

**Jev equivalent we do not have:** a STATUS row does not name \(S\), \(A\), \(L\), \(\pi\),
or a withhold action's loss. Verdicts are process labels (`CLEARED`/`HELD`/`RULED_OUT`), not
Bayes actions.

### 2.2 Four-gate promotion (AND, not a scalar)

`franken_engine/.../promotion_gate_runner.rs:1–8, 31–63, 200–353`. Four *mandatory* gates;
empty evidence **fails** (performance `:271–278`, adversarial `:335–342`).

| gate | predicate | default strictness (`:94–128`) |
|---|---|---|
| **Equivalence** | semantic divergences ≤ `max_divergences` (0 = bitwise/behavior identity) | required, 0 divergences |
| **Capability preservation** | requested caps ⊆ authority envelope | required |
| **Performance** | every measurement ≥ min throughput AND ≤ max latency | 0.5 ops/s, 100 ms |
| **Adversarial survival** | pass rate ≥ threshold | **95%** (`950_000 / 1_000_000`) |

Parser-correctness specialization (`docs/PARSER_CORRECTNESS_PROMOTION_GATE.md:23–29`):
`promote` iff no unresolved high-severity drift **and** all evidence lanes green; else
`hold`. Boundary test cited in our own harvest: `delta == threshold` produces `"promote"`
(`docs/demos/ORACLE-PROGRAM.md:50–51`).

**Jev equivalent we do not have:** `STATUS.tsv` has one `score` (100–940) and one `verdict`.
A row can `CLEAR` on demand (rung 2) with no equivalence, no capability envelope, no
adversarial survival. Rung 5 is `promoted`. Zero rows are there.

### 2.3 Dominance ratchet / frontier gap

`universal_dominance_ratchet.rs:7–10, 247–255`:

\[
\text{dominance fraction} = \frac{\#\{\text{cells in Proven}\}}{\#\{\text{cells}\}}
\quad\text{(fixed-point millionths)}
\]

Once a cell is `Proven` it cannot regress. Unclaimed dimensions are **frontier gaps**
(states: registered / closed-by-proof / out-of-scope / subsumed / not-meaningful —
`:436–446`). Aggregate improvement cannot hide a per-cell drop. This is the same idea as
`franken_ocr`'s monotone per-category ratchet (`oracle-design-from-corpus-20260919.md:29–37`).

**Jev equivalent we do not have:** `STATUS.tsv` is a flat list. A `CLEARED` row can become
`HELD` in prose without a digest-level ratchet. `promoted=0` is currently enforced by
honesty, not by a board that refuses the write.

### 2.4 Planted-negative as a hypothesis test

Franken's differential oracle pins mixed pos/neg case identity *before* measurement
(`oracle-design-from-corpus-20260919.md:59–68`). Our smallest form is already in
`work/oracle-kit/test.mjs:9–25`:

| \(H_0\) (the defect) | planted observation | reject \(H_0\) when |
|---|---|---|
| constant score is a real null | `auc([0,0,0,0], [T,T,F,F])` | `constant === true` (value is 0.5 **and flagged**) |
| one-class label is measurable | all-true labels | throws, does not return NaN |
| missing SDK field scores silence | `field({noul}, 'probabilities')` | throws naming the field |

This is a one-sided test that the *harness* is not blind. Feasibility
(`oracle-kit/index.mjs:61–65`) is the dual: an arm that *ought* to pass must clear
`auc ≥ 0.8` and `!constant`, else the instrument is broken and **no verdict issues**.
Compaction's positive control AUC **0.941** is why the `keep_p` null is real
(`compaction-retention-oracle-20260919.md:72–80`).

### 2.5 Conformal / CVaR / e-process (present upstream, unused as a Jev gate)

**e-process** (we *copied the update*, we do not gate STATUS on it).
`asupersync/src/lab/oracle/eprocess.rs:224–229` and `oracle-kit/index.mjs:92–98`:

\[
e_t = e_{t-1}\cdot \max\bigl(10^{-15},\; 1 + \lambda(x_t - p_0)\bigr),\qquad
\text{reject if } e_t \ge 1/\alpha
\]

Ville's inequality: Type I is controlled under *optional stopping*. Default in the kit:
\(\lambda=0.5\), \(p_0=0.5\), \(\alpha=0.05\) ⇒ reject at \(e \ge 20\), which is exactly
Franken's default `e_process_breach_threshold: 20.0`. Kit self-test: 8 unanimous
observations do **not** reject; 40 do (`test.mjs:50–54`).

**Conformal calibrator** (`runtime_decision_theory.rs:41–42, 442–569`). Target
miscoverage \(\alpha = 0.10\) (100,000 millionths). Fail-closed tri-state:
`InsufficientData` / `Calibrated` / `OutOfTolerance` — `is_calibrated()` is false unless
`Calibrated`. Anytime-valid e-value under \(H_0\): coverage \(\ge 1-\alpha\); a miss
multiplies by \((1-\alpha)/\alpha = 9\) at \(\alpha=0.10\). Min 50 observations before
enforcement; 5 consecutive violations flag. **We have no conformal set around a Jev
noul.** A 0.75 threshold with ECE 0.061 is a point estimate, not a coverage guarantee.

**CVaR tail-risk** (`runtime_decision_theory.rs:15, 39–40`): default \(\alpha=0.95\).
Mean improvement must not hide a p99 regression. Compaction's keep-everything win is
exactly a CVaR-shaped fact (the *tail* of “needed later” is long-horizon; class D
ceiling ≤ 0.083 inside 80 messages — `RULING` sharpening). We narrated it. We did not
encode it as a gate.

Skillranker's unused inferential gates, for completeness
(`evaluation_policy.v1.json:133–182`): n ≥ 300 primary families, top-1 ≥ 0.90 with
Wilson lower ≥ 0.80, needless-suggestion ≤ 0.05 (Wilson upper ≤ 0.10), harm: 0 events
in 150 families, one-sided 95% Clopper–Pearson upper ≤ 0.02. Their own calculator
(`expected_values.v1.json:112–128`):

\[
\text{zero of } n \text{, one-sided 95% upper} = 1 - 0.05^{1/n}
\]

0/100 → 0.029513 (fails 2% gate); 0/150 → 0.019773 (passes). **Do not copy the 300-case
bar.** Copy the refusal to promote on a diagnostic split.

---

## 3. Gaps between `STATUS.tsv` and a Decision Contract

`scripts/lane-status.sh` reads **10 columns** (`EXPECTED_COLS=10`, `:188`):
`candidate, rung, score, verdict, author, receipt, blocked_on, kill_concurrence, digest, receipt_type`.
The header line in the file still names 7. Census this tip (column 4):

| verdict | n |
|---|---:|
| CLEARED | 7 |
| HELD | 10 |
| RULED_OUT | 8 |
| PROMOTED | **0** |

A Decision Contract (`franken_decision` + RaptorQ emission list) wants fields STATUS
cannot even store:

| contract field | what it decides | STATUS today |
|---|---|---|
| **state space \(S\)** | what the world can be (needed / not; stuck / healthy; harm / benign) | absent — implied in receipts, not in the row |
| **action set \(A\)** | allow / block / withhold / escalate / compact / keep | absent — `verdict` is a *process* label, not an action |
| **loss matrix \(L(s,a)\)** | relative cost of each mistake | absent — skillranker 0/1/2 lives in one oracle, not the ledger |
| **withhold cost** \(L(\cdot,\text{abstain})\) | is silence cheap or expensive? | absent — we discovered it is cheap on skillranker (\(1\) vs \(2\)) and expensive on compaction (keep-everything wins) |
| **action utilities** (or \(L\) as negative utility) | Bayes argmin | absent — `score` is a 0–1000 pane grade, not \(\mathbb{E}[L]\) |
| **prevalence prior \(\pi\)** | deployability | absent — retrofit lives in a markdown file; two rows are `PREVALENCE-UNKNOWN` |
| **posterior snapshot** | what we believed at decision time | absent |
| **expected_loss_terms** | why that action won | `blocked_on` is prose |
| **fallback trigger** (cal / \(e_t\) / CI width) | when to stop trusting the judge | absent |
| **conformal coverage / CVaR** | does the interval cover? does the tail regress? | ECE/Brier exist in `foundation/runs/`, not joined |
| **four promotion gates** | AND of equivalence, capability, perf, adversarial | one `rung` + one `score` |
| **frontier cell + digest ratchet** | proven cells cannot silently drop | `digest` pins a receipt's bytes; it does not pin a *cell state* |

What STATUS *does* well, and must keep: receipt path, digest, author-is-not-scorer,
`receipt_type` enum, kill-concurrence, **0 promoted**. Filling the contract by adding
fifteen columns to a shared TSV is how you get ceremony. The gap is not “STATUS is
wrong.” The gap is: **a CLEARED row cannot name the loss of the action it is proposing
to take.**

---

## 4. Next-level approaches, ranked for Jev (product ticks)

Each tick: math in one paragraph, smallest experiment **on this repo**, `ACCEPTANCE` = a
live command, `NO-CLAIM`. Ranked by (ground truth already on disk) × (prevalence known) ×
(cost = zero-API) × (decision leverage), per the autonomous-loop selection rule.

### (a) Proper scoring + abstention loss — **do this first**

**Math.** A scoring rule is *proper* if reporting the true distribution uniquely minimizes
expected score. Brier is proper for probabilities. Skillranker's 0/1/2 table is a proper
*decision* score for \(\{recommend, abstain\}\) once you include \(L(\text{false abstain})=1\):
always-abstain has \(\bar L = \pi\), so a policy that never helps cannot beat the control
unless \(\pi=0\). Without that cell, the optimum is silence. We already paid for this on
n=12 and then left the table inside one script.

**Smallest experiment.** Lift `LOSS` from `work/skillranker-eval/oracle.mjs:30–36` into
`work/oracle-kit/index.mjs` as `decisionLoss({yNonEmpty, abstained, pickInY})`, with the
always-abstain identity `meanLoss = nPos/n` as a planted check. Re-score any existing
receipt that already distinguishes false-abstain from wrong-pick (skillranker 12, harm-rule
12, compaction keep/drop). Do not call Jev.

**ACCEPTANCE.**

```bash
node work/oracle-kit/test.mjs
# must print a new check:
#   always-abstain mean loss equals nPos/n on the skillranker 10/12 identity (0.833)
#   false abstention costs 1; wrong pick costs 2; needless costs 2
# planted negative: a table that omits false_abstention_on_positive makes always-abstain win
```

**NO-CLAIM.** Does not promote skillranker. Does not claim 0.167 transfers off the
diagnostic split. Does not replace Brier — it scores *actions*, Brier scores *probabilities*.

### (b) Prevalence-conditioned thresholds

**Math.** For a binary act/pass decision with losses \(L_{\mathrm{FP}}, L_{\mathrm{FN}}\)
and prior \(\pi\), the Bayes threshold on posterior \(p = P(Y{=}1\mid x)\) is

\[
t^\star(\pi) = \frac{L_{\mathrm{FP}}(1-\pi)}{L_{\mathrm{FP}}(1-\pi)+L_{\mathrm{FN}}\pi}.
\]

With an abstain action of cost \(c_A\), act only when
\(\min(\mathbb{E}[L\mid\mathrm{act}], \mathbb{E}[L\mid\mathrm{pass}]) < c_A\). At
\(\pi = 30/186449\) and \(L_{\mathrm{FP}}=L_{\mathrm{FN}}\), \(t^\star \approx 1 - \pi
\approx 0.99984\). That is the 1:2300 identity in closed form: a 0.80 threshold is the
*authored-corpus* threshold, not the population one. For dcg-adjacent harm,
\(\pi_{\mathrm{block}} = 0.0097\) and a 15% fire rate is already above \(t^\star\) unless
\(L_{\mathrm{FN}} \gg L_{\mathrm{FP}}\).

**Smallest experiment.** A stdlib script that reads
`work/p3-calibration/toolcall-corpus-frozen.jsonl` (or the committed 30/186449 counts) and
prints \(t^\star(\pi)\) for a *declared* \((L_{\mathrm{FP}}, L_{\mathrm{FN}}, c_A)\).
Preregister the three losses **in the file** before printing. Show that the shipped 0.80
(foreman) and 0.50 (compaction) are not Bayes for any loss triple we would actually sign.

**ACCEPTANCE.**

```bash
python3 work/oracle-kit/prevalence_threshold.py   # or the path you land it at
# prints t*(pi) for:
#   foreman pi=30/186449, L_FP=L_FN=1, c_A=0.5
#   dcg    pi=488/50149,  L_FP=1, L_FN in {1,10,100}
# planted: pi=0.5 recovers t*= L_FP/(L_FP+L_FN)
# planted: pi=0 throws or refuses (no Bayes threshold)
```

**NO-CLAIM.** Does not invent a population \(\pi\) for jev-review or skillranker (those
stay `PREVALENCE-UNKNOWN`). Does not retune a live hook.

### (c) Promotion as four AND-gates, not one metric

**Math.** Let \(G_1,\dots,G_4\) be the Franken gates (equivalence, capability, performance,
adversarial). Promotion is \(\bigwedge_i G_i\), with \(G_i=\mathrm{false}\) on empty
evidence. A single AUC, a single `score`, or a single precision cannot substitute: each
gate's Type I error is a *different* mistake (behavior drift, authority widening, tail
latency, known-bad survival). Skillranker independently AND-gates relevance / harm /
operational cohorts and forbids conflating them (`expected_values.v1.json:130–135`).

**Smallest experiment.** Do **not** add columns to `STATUS.tsv` this tick (shared file,
ceremony risk). Write a reader that, for one named candidate with existing receipts,
emits four bits from evidence that is *already on disk*:

| gate | Jev meaning | existing oracle |
|---|---|---|
| equivalence | same decision as a frozen deterministic baseline on the same cases | harm-rule vs regex 12/12 vs 11/12 |
| capability | the hook cannot return `{block:true}` if the design is observe-only | `harm-rule.ts` / compaction `undefined` |
| performance | p99 latency or $ / session vs the cheap baseline | compaction keep-everything is free; Jev is not |
| adversarial | planted-bad / random-judge / known-bad still refuse | `oracle-kit` planted negatives; compaction 0/200 noise |

Promote only if all four are `pass`. Today every CLEARED row fails at least one (usually
equivalence against the cheap thing, or adversarial on authored data).

**ACCEPTANCE.**

```bash
python3 scripts/promotion-four-gates.py UP-R5-jev-toolcall-gate
# exits 0 only if all four bits are pass; otherwise prints which gate is empty/fail
# planted: a candidate with no adversarial receipt must FAIL (empty ≠ pass)
# STATUS.tsv is not written
```

**NO-CLAIM.** Does not promote anyone. Does not change `lane-status.sh`. The four bits are
a *view* over receipts, not a new score.

### (d) selector ≡ claim (measurement integrity)

**Math.** A statistic \(T = f(\mathbf{X})\) is only a measurement of \(X\) if \(f\) reads
the coordinate it claims to read. If \(f\) reads a missing field and silently defaults,
\(T\) is a function of the default, and \(\mathrm{AUC}(T,Y)=1/2\) whenever \(T\) is
constant — indistinguishable from a true null. Eight times this lane published an absence
that was a wrong selector (`oracle-kit/index.mjs:100–115`; `SDK-SURFACE.md`). The
mechanical rule: **you may not assert a field is missing without dumping the keys that
are present**; you may not score a field the SDK does not declare.

**Smallest experiment.** Already mostly built (`field`, `requireKey`, `inspectKey`). Close
the remaining hole: a receipt-time check that every cited answer path is in
`docs/demos/SDK-SURFACE.md` (`noul` / `choice` / `confidence` / `probabilities` / `score`
/ `legend`). Fail if a receipt mentions `.probability` or `.distribution`.

**ACCEPTANCE.**

```bash
node work/oracle-kit/test.mjs          # existing planted negatives stay green
rg -n '\\.distribution|\\.probability\\b' work docs/demos --glob '!**/node_modules/**'
# planted: a fixture answer {noul:0.9} scored as probabilities must throw
```

**NO-CLAIM.** Does not prove past receipts used the right field — only that new scorers
cannot silently default.

### (e) Sharper instruments, only where (a)–(d) have a consumer

#### Expected regret vs keep-everything / always-abstain

\[
R(a) = \mathbb{E}\bigl[L(a,Y) - L(a^\star,Y)\bigr]
\]

On compaction, \(a^\star\) is keep-everything (12 / 4 / 13 mistakes vs Jev 82 / 91 / 81).
Regret is ~7–23× the oracle, already measured. On skillranker, \(a^\star\) is not
always-abstain (\(R=0.167-0=0.167\) vs control \(0.833\)). **The next useful regret
number** is: regret of *Jev-at-0.5* versus *Bayes \(t^\star(\pi)\)* on a corpus that has
both labels and a known \(\pi\). That is (a)+(b) composed, not a new crate.

#### Neyman–Pearson (fix Type I, maximize power)

Maximize TPR subject to \(\mathrm{FPR} \le \alpha\). This lane already named
\(\alpha = 0.001\) as a kill line (`INTEGRATIONS.md` toolcall corpus: 3.95% `isError` is
40× that line, so the *surface* is not killed). On harm-rule both regex and Jev posted
**0 FP** on their corpora, so NP does not separate them — cost-benefit does. **Use NP
only on a surface with nonzero measured FPR** (bicameral 3/20, foreman real 0/10 at 0.80
but AUC 0.750). Smallest command: given a frozen `(score, label)` jsonl, print the
highest TPR at FPR ≤ 0.05 / 0.01 / 0.001. Empty FPR-bin ⇒ `InsufficientData`, not 1.0.

#### Information value of a Jev call

Let \(a_0 = \arg\min_a \mathbb{E}[L(a,Y)]\) under the prior (usually the regex, or
keep-everything, or always-abstain). After observing Jev's answer \(Z\),
\(a(Z)=\arg\min_a \mathbb{E}[L(a,Y)\mid Z]\).

\[
\mathrm{VOI}(Z) = \mathbb{E}\bigl[L(a_0,Y)\bigr] - \mathbb{E}\bigl[L(a(Z),Y)\bigr] - c_{\text{call}}
\]

If \(a(Z)=a_0\) almost surely, \(\mathrm{VOI} \le -c_{\text{call}}\). That is the
cost-benefit kill in one line. On harm-rule the regex *is* \(a_0\) and \(a(Z)\) is
weaker (11/12 < 12/12), so \(\mathrm{VOI}<0\) before counting the key. On skillranker,
\(a_0\) is always-abstain and \(\mathrm{VOI}\approx 0.833-0.167 = 0.666\) loss-units
per case — *on a diagnostic split, one run, no \(c_{\text{call}}\) priced*.

**Smallest experiment for VOI:** reuse the harm-rule frozen corpus and
`node work/omp-harm-rule/verify-claim.mjs` (already exits 0). Add a table:

```
E[L|regex], E[L|jev], E[L|regex then jev-on-regex-allow], c_call
```

with \(L\) declared (e.g. miss=1, FP=10, call=0.01). If `regex then jev` does not beat
`regex`, VOI of the paid call on that surface is negative. **NO-CLAIM:** 12 planted
harms, not incidents; FP denominators are not like-for-like (R34).

#### Sequential e-process instead of fixed-n p-values

We already have the update. The unused move: **stop a live budget when \(e_t \ge 20\)**
rather than “run N=20 because the brief said 20.” Kit test already shows n=8 is not
enough under the default \(\lambda,p_0,\alpha\). Consumer: any future live probe that
currently picks N in advance (foreman was 30 live requests on real windows). Until a
live probe is budgeted, do not wrap STATUS in e-values — that is theater.

---

## 5. What NOT to copy

**Math theater.** A 15-column Decision Contract TSV that no scorer reads. Importing
`franken_decision` as a Cargo dep to score 12 JSONL rows. A conformal wrapper around
noul that has never seen 50 calibration points. Re-litigating `promoted=0` by defining
a weaker `PROMOTED-DOC` rung. Copying skillranker's n=300 / n=150 / n=500 promotion
floors onto a lane whose real corpora are n=12, n=20, n=96. Ranking crates again
(`franken-crate-alpha` already did; `franken-tooling-gaps` already did).

**Ceremony this file refuses.** No new `foundation/gates.sh` stage. No STATUS rewrite.
No live Jev spend. No claim that citing Franken formulas is adoption — adoption is a
consumer that fails on a planted negative (`franken-crate-alpha-20260919.md:210–216`:
copy the contract, don't link the engine).

**Honesty that stays.** `promoted = 0`. Authored data inflates. AUC without \(\pi\) is
not deployable. A cost-benefit kill is a success. Empty evidence fails the gate; it
does not pass as `CLEARED`. Selector bugs fabricate 0.500. Always-abstain must lose
on purpose, or the loss table is wrong.

---

## NO-CLAIM

- No new measurement. n=12 / n=60 / n=96 / 30/186449 / 254/305 / 12/12 are **other
  receipts'** numbers, re-derived only where the algebra is an identity (10/12=0.833,
  2/12=0.167, 30/186449).
- `franken_decision` / `promotion_gate_runner` / `universal_dominance_ratchet` line
  numbers are from public HEAD `c80b20609` / `fc37f2dec` on 2026-09-20, not from a
  Studio mirror and not from a live `ripwire --exemplar`.
- Conformal “anytime-valid” in `runtime_decision_theory.rs:16` is the crate's own
  hedge: *“formal anytime-validity guarantees not proven.”* We do not upgrade that.
- This document does not promote a candidate, add a STATUS column, or spend a key.
- `franken-crate-alpha-20260919.md` remains the crate/process map. If the two disagree,
  the alpha receipt wins on inventory; this file wins on formulas.

**Next concrete lever:** land §4(a) — `decisionLoss` in `oracle-kit` with the
always-abstain planted negative — then §4(b) on the frozen 30/186449 and 488/50,149
priors. Those two ticks turn unused Franken math into a scorer this repo already runs.
