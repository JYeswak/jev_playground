# PLAN v4 — the evidence matrix: make a coverage claim a thing a validator can refuse

**Status:** v4, post-review-round-1. Grounded in Axes A/B/C/D (all committed). Reviewed
adversarially by pane 4 (Grok, cross-model) and validated for implementability by pane 3;
both review artifacts are cited inline where they changed a decision. Per
`skill://planning-workflow`, this document is self-contained — a fresh agent who has never seen
this lane can implement from it without asking.

**What round 1 changed, because two of these were errors and not preferences:**

- **The dual bar was vacuous.** v2/v3 set `bar_point = bar_interval = 0.30`. If `upper ≤ 0.30`
  then `p̂ ≤ 0.30` follows automatically, so the point leg never binds — pane 4: *"POINT refuses
  none."* His bars are **distinct** (point 0.90, interval-lower 0.80) precisely so both bite.
  Rewritten in §4.1.
- **§4 cited the wrong event.** It quoted 0.381 and 0.605, which are the **n=77 relabel**
  numbers — measured *after* the ships. Ship-time evidence was 4/20. §4.2 was correct; the prose
  was not. Fixed.
- **`k` was unbound** — the reward hack pane 4 named. Fixed in §3.
- **`scope-disagreement` was fatal as a commit-time check** (environment-dependent). Demoted to a
  runtime check in §4.
- **T6 wrongly depended on T4**, and the ASCII picture disagreed with the `Depends:` lines. Both
  reviewers flagged it independently; split into T6a/T6b in §5.

---

## 1. Why — the measured failure this exists to prevent

On 2026-09-20 this lane shipped eight rules system-wide and **disabled all eight by day's end**,
each on its own statistics. That is not the failure. These are:

| # | failure | evidence |
|---|---|---|
| F1 | **Ships had no auditable evidence.** Kill decisions persisted row identities; ship decisions persisted none. | R70 |
| F2 | **A 3.6× labelling error we cannot diagnose.** `structural-def` FP 4/20 → 55/77; P(original given replacement) = 2.7×10⁻⁶. Cause undeterminable because the original rows do not exist. | R71 |
| F3 | **Bars were set and measured by the same party.** I preregistered thresholds; my own panes scored against them. No second key. | NEED #6 |
| F4 | **A documented trap recurred.** The `repeatMode: once` probe ambiguity was written in ARC.md in the morning and repeated in a different pane in the afternoon. | ARC.md row 7 |
| F5 | **"Disabled" was reported for rules that were still live**, twice, because verification used a probe instead of enumeration, and because `omp config set` on an array is not read-modify-write safe across panes. | this session |
| F6 | **No inventory of what is live.** Rule counts drifted 33→34→35 with no authority to check against. | this session |

**The common shape:** every claim this lane makes lives in prose — a commit subject, an `EVAL.md`
row, a ledger entry. Prose cannot be refused by a machine. Jeffrey's answer, measured in
`docs/demos/upstream-repro/axis-d-contract-matrix-20260921.md`, is to make the coverage claim a
**data structure with a second key**, and to let a validator refuse it.

**Rule 12 governs:** when Jeffrey does it, the default is ADOPT. §7 states what we refuse and pays
the required cost/defect/loss for each.

---

## 2. What we are adopting, and the one thing we are adding

**Adopting (grounded in `skillranker@77f302b`):**

- **A two-key declaration.** `tests/contract_matrix.toml` (92 boundaries) validated against
  `tests/contract_authority.toml` (79). `validate_contract_matrix.py:342` requires set equality;
  `:348` requires byte-equality on nine bound fields. **A coverage claim cannot be widened
  without review.** → fixes F3.
- **Evidence references that resolve.** `unit_property_tests = ["tests/x.rs::fn_name"]`, resolved
  with AST strictness — path traversal rejected, exactly one match, no rebinding
  (`reference_exists:189+`). → fixes F1.
- **Status that distinguishes declared from executed.** `{planned, executed, passed, failed}`,
  with the matrix header stating *"P0 rows for future product tests are planned, never fake
  passed results."* → fixes F1, F6.
- **Epistemics in code, not README.** *"Declaration validation is never a test-execution or
  product acceptance receipt"* (`:3-5`). → fixes our habitual "verified".
- **Fixed diagnostic codes.** `InvalidMatrix` emits `boundary-coverage`, `authority-phase`,
  `unknown-assertion` — never a content dump. Matters here because our artifacts touch session
  transcripts.
- **Runnable validators, not CI.** There is **no** `.github/workflows` in his tree; rigor is 11
  Python scripts run in-tree. This is what makes it portable to a lane that is not a package.

**Adding — the reverse check his tree lacks.** Axis A (`:143-144`): *"no orphan check found —
nothing verifies every `#[test]` IS registered in the matrix (matrix→source only)."* We port the
registry **with** source→matrix enforcement. Cheap: walk every selftest case and require
registration. Without it the matrix measures only what we remembered to declare — phantom
coverage, which is F6 again in a new costume.

**Explicitly NOT adopting the seat.** Axis C proved his 2,529 lines of Jev tests *"certify the
wire, not the judge"* — schema and numeric invariants only, **no accuracy assertion**, and **no
Jev-versus-baseline comparison executed anywhere**; his eval README says these are not benchmark
results and his own reality-check row 20 is UNPROVEN. **R69 stands and is stronger than anything
upstream.** We adopt his plumbing and keep our judgment.

---

## 3. The artifact — `evidence/matrix.toml` + `evidence/authority.toml`

A **boundary** is any claim this lane makes that a future agent would otherwise have to trust.
Four kinds, all already present: a **rule**, an **instrument** (script), a **refutation**
(R-number), and an **omp seam**.

```toml
[[boundaries]]
id = "rule_bash_glob_silenced"
kind = "rule"                          # rule | instrument | refutation | seam
owner_bead = "jev-xxxx"
title = "Silenced glob in bash is flagged once per session"

# EVIDENCE — every entry must resolve to a real declaration
selftest_cases = ["scripts/selftest-ttsr-rules.sh::glob_silenced_fires",
                  "scripts/selftest-ttsr-rules.sh::glob_silenced_quiet_on_clean"]
red_arm = "scripts/selftest-ttsr-rules.sh::glob_silenced_fires"   # REQUIRED, see §4
label_rows = "work/skills-vein/glob-labels-20260921.json"          # REQUIRED for any rate

# THE CLAIM, with its scope, its assumptions, and its control.
# Assumptions are TYPED FIELDS, not a magic method string — see §4.1(2).
rate = { kind = "fp", k = 4, n = 77,
         estimator = "wilson", sides = 2, conf = 0.95,
         iid_claimed = false }         # our fires overlap sessions; say so in a checkable field
#        bar_interval <- authority.toml, frozen BEFORE data exists (see §4.1)
#        bar_point    <- ABSENT. No justified value. Rows carry point_leg = "unset".
label_rows = "work/skills-vein/glob-labels-20260921.json"
label_rows_sha256 = "9f2c…"            # checksum: detects drift, does NOT prevent mislabelling
k_gold = 4                             # the AUTHORITY's count for these rows; k above must equal
                                       # the value recomputed from label_rows. See `k-drift`.
labeller_count = 1                     # typed, not prose. Was a NO-CLAIM we never enforced.
rows_independent = false               # typed. Was a NO-CLAIM we never enforced.
live_measurement = false               # typed.
scopes = ["project", "global"]
rung = "L3"                            # L0..L4 from AGENTS.md
status = "planned"                     # planned | executed | passed | failed | retired
point_leg = "unset"                    # unset | <bar>  — visible, never implied
```

`authority.toml` holds the same rows with the **bound fields** frozen: `owner_bead, kind, title,
red_arm, rate.estimator, rate.sides, rate.conf, rate.iid_claimed, rate.bar_interval, rate.n,
k_gold, label_rows_sha256, scopes, rung`.

**The control is a time-freeze, not a person.** v5 said *"Joshua holds the second key."* Pane 4's
round 4 refused that: **F3 was the same party setting and scoring, and he is that party** — he
directs this lane. Naming a person as the control re-creates the defect with a longer loop.
**The mechanism is the files plus the ordering: a bar is valid only if it was written before the
measurement existed, and `bar-equals-observed` catches the degenerate case mechanically.**
Steward ≠ scorer is a property of *when*, not of *who*.

**`k` and what the hash actually buys.** `k` is a measurement outcome, so freezing it in the
authority would make the reviewer set the result. Instead the authority carries **`k_gold`** and
the validator recomputes `k` from `label_rows`; disagreement is `k-drift`.
**What this does NOT do, stated plainly because v5 implied otherwise:** the hash detects
*transcription* drift — someone editing a number — and is **powerless against mislabelling.**
**R71's 3.6× discrepancy was a labeller failure, and none of this would have caught it.** The
only thing that closes that gap is a second labeller with measured agreement, which this program
does not include. `labeller_count = 1` exists so the weakness is visible in every row.

---

## 4. The validator — `scripts/validate-evidence-matrix.py`

Fail-closed, fixed diagnostic codes, no content in logs.

| check | code | prevents |
|---|---|---|
| matrix id set == authority id set | `boundary-coverage` | silent widening (F3) |
| byte-equality on every bound field | `authority-<field>` | bar drift (F3) |
| every `selftest_cases` ref resolves to a real, unique case | `unresolved-evidence` | phantom coverage (F1) |
| **every selftest case in the tree is registered** | `orphan-case` | **the reverse check he lacks** |
| `red_arm` present and is one of `selftest_cases` | `missing-red-arm` | untested gates |
| any `rate` present ⇒ `label_rows` exists and has ≥ n keys | `unpersisted-rate` | **R70/R71 exactly** |
| `status = passed` ⇒ the **interval** leg clears; point leg only if `point_leg ≠ "unset"` | `uncertified-pass` | NEED #6 |
| `bar_interval` absent from `authority.toml` | `bar-unset` | an unbarred claim |
| a bar exactly equals the `k/n` it scores | `bar-equals-observed` | **setting the bar to your data** |
| `iid_claimed = true` while rows share a session | `iid-unsupported` | silent independence assumption |
| `labeller_count`, `rows_independent`, `live_measurement` all present and typed | `missing-typed-caveat` | prose caveats nobody enforces |
| `negative_control` present ⇒ a **loss table** exists and the control loses under it | `control-not-beaten` | a rule that beats nothing |
| every semantic field has a corrupt-it-must-fail twin | `no-mutation-twin` | untested validator |
| `k` recomputed from `label_rows` matches declared `k` | `k-drift` | **moving the numerator** |
| `kind = rule` ⇒ enumeration in every declared scope agrees with `status` | `scope-disagreement` | F5 — *runtime only* |
| every non-epic `jev-*` bead is covered by ≥1 boundary | `uncovered-bead` | untracked work |
| platform-dependent claim + simulated evidence | `simulated-platform` | certifying a cross-build as native |

**Sixteen codes.** This count is the single source of truth: T2 implements the **thirteen**
deterministic ones, T6a adds `orphan-case`, and `scope-disagreement` plus `simulated-platform`
are **runtime** checks that report `…-unverified` rather than pass when their environment is
absent. v5 said "eight" in T2 and "fifteen" in §6 — pane 4's blocker — and both were guesses.

`uncertified-pass` is the rule that makes this pay for itself: **a boundary cannot say `passed`
while either leg of its bar fails.** Scored at **ship time** — 4/20 for all three, the evidence
we actually had on 2026-09-20 — every one of them is refused by the interval leg: Wilson upper
**0.416** (Clopper-Pearson 0.437) against a 0.30 bar. All three shipped anyway.

*(v2 wrongly cited 0.381 and 0.605 here. Those are the **n=77 relabel** results, measured after
the ships — pane 4's review caught the wrong-event error. §4.2 always had it right.)*

**`scope-disagreement` is a runtime check, not a commit gate.** It must shell out to
`omp ttsr list`, which makes it environment-dependent and non-deterministic in a clean checkout
— pane 4 called it *"fatal as a commit check"* and is right. It therefore runs in
`foundation/gates.sh` where an omp is present, and is **skipped-with-a-named-reason**, never
silently, when `omp` is absent. A skip is reported as `scope-unverified`, which is a distinct
state from pass — the absent-key lesson from AGENTS.md's offline/live split.

### 4.1 The dual bar, the stated assumption, and the control — adopted from his eval policy

Axis B (`docs/demos/upstream-repro/axis-b-validators-20260921.md` §2) found that
`validate_eval_policy.py` already solves NEED #6, and more stringently than I proposed. Four
mechanisms, adopted:

**1. A dual bar with DISTINCT thresholds.** His top-one precision requires rate ≥ 0.90 **AND**
Wilson lower ≥ 0.80 (`:263`). The two numbers differ *on purpose*: the point bar is strict, the
interval bar is looser, and each can bite where the other does not.

v2/v3 of this plan set `bar_point = bar_interval = 0.30` and called it a dual bar. **It was
not.** For an upper-bounded FP rate, `upper ≤ 0.30` implies `p̂ ≤ 0.30`, so the point leg could
never fire — pane 4's review: *"Dual 0.30/0.30 is NEED 6 renamed… POINT refuses none."* Correct,
and the error is instructive: I adopted the *shape* of his mechanism without the property that
made it work, which is exactly the failure mode Rule 12 invites if adoption is uncritical.

**The corrected bars are NOT stated in this plan, and that is the point.** v4.1 proposed
`bar_point = 0.20, bar_interval = 0.30` and justified 0.20 as *"two-thirds of the interval bar
by the same reasoning he uses (0.80 is ~89% of 0.90)"*. Pane 4's round 2 demolished that in one
line: **`2/3 ≠ 8/9`**, so the analogy is false; and **0.20 is exactly 4/20**, the observed rate
the bar was meant to judge.

**I picked a threshold equal to my own data and then justified it by a ratio that does not
match.** That is the named failure this whole document exists to prevent, committed by its
author, in the section describing the prevention. It is left in the record rather than quietly
corrected.

**The rule that follows, and it is stronger than any number I could have chosen:** *the party
being measured does not set the bar, and a bar derived from the measurement is not a bar.*
Both `bar_point` and `bar_interval` are **authority-only fields with no default**, set by the
key-holder before data exists. The validator emits `bar-unset` if a boundary carries a `rate`
whose bars are absent from `authority.toml`, and `bar-equals-observed` if a bar exactly equals
the `k/n` it scores — a cheap, mechanical check for the exact thing I just did.

`bar_interval = 0.30` has standing as the pre-existing preregistered TTSR FP bar and carries in
unchanged. `bar_point` has **no justified value yet** and is therefore **unset**: the program
can be built, and boundaries registered, with the point leg disabled and every such row marked
`point-leg-unset` in its non-claims. A disabled leg that is visible beats an invented threshold
that is not.

**2. The method name carries its assumption.**
`two_sided_95_wilson_with_one_primary_case_per_independent_family` (`:247-249`) — the
independence assumption is in the identifier, so it cannot be forgotten at read time. Our rows
labelled 20 fires drawn from overlapping sessions and silently treated them as independent.
`unstated-assumption` requires the method name to say what it assumes.

**3. Non-claims are load-bearing, validated fields.** His policy `status` must literally equal
`frozen_contract_not_evidence` (`:195`), and ≥4 non-claims must contain the phrases *"not an
evaluator"*, *"not a 300-family"*, *"synthetic"*, *"no live"* (`:197-200`). **The fixture cannot
silently become a claim.** Our `missing-non-claims` requires ≥3, naming labeller count and
independence — the two NO-CLAIMs we kept writing in prose and never enforced.

**4. A frozen negative control that must be proven to lose.** `always_abstain` plus six
baselines (`:250-253`), and the expected-values fixture must **prove always-abstain loses**
(`:429`). Our analogue is `always_quiet`: a rule must beat doing nothing, demonstrated, not
assumed. **v4 claimed this would have killed the FP-0.714 rule "without any labelling at all." That is
false** — pane 4, round 4. Ranking a rule against `always_quiet` requires a loss function, and
we have none; he pairs his control with an exact 0/1/2 loss table (Axis B `:231-244`). Without
one, "beats doing nothing" is an intuition, not a computation. `control-not-beaten` therefore
requires a **declared loss table**, and until one exists the control field is not usable.

**5. Mutation twins.** `test_eval_policy.py` is 43 mutation tests: corrupt one semantic field,
require `SystemExit` (Axis B §1). Named failure modes include *false abstention scored correct*,
*coverage ≠ recall*, *averages hiding loss*, *unstarted cases disappearing*. `no-mutation-twin`
requires every semantic field of our matrix to have one. This is the discipline that makes the
validator itself trustworthy rather than merely present.

**What this costs us in credibility, stated plainly:** four of the five mechanisms above are
things this lane argued for in prose today and failed to enforce. He enforces them in 521 lines
of stdlib Python with 43 mutation tests. That gap is the honest measure of the distance.

---

### 4.2 The replay — computed, not asserted

Every rate-bearing decision of 2026-09-20, scored by the dual bar (FP must satisfy
`p̂ ≤ bar_point` **and** `upper ≤ 0.30`; bind must satisfy `p̂ ≥ bar_point` **and** `lower ≥ 0.20`).
Rows below are scored with the **illustrative** `bar_point = 0.20` that §4.1 now refuses to
adopt — they show what a point leg *would* do, and are not a certification. Pane 4 caught this
header still carrying the vacuous `p̂ ≤ 0.30` after the bars were corrected: **the copy site
outlived the fix**, which is why §4.1's rule is that bars live in exactly one file.
Wilson two-sided 95%, computed by pane 1.

| boundary | p̂ | 95% CI | point | interval | verdict | what we did |
|---|---:|---|:--:|:--:|---|---|
| `absence-from-one-probe` n=20 *(ship-time)* | 0.200 | [0.081, 0.416] | ok | **NO** | REFUSE | **shipped** |
| `absence-from-one-probe` n=77 *(relabel)* | 0.273 | [0.186, 0.381] | **NO** | **NO** | REFUSE | retired |
| `bash-structural-def-search` n=20 *(ship-time)* | 0.200 | [0.081, 0.416] | ok | **NO** | REFUSE | **shipped** |
| `bash-structural-def-search` n=77 *(relabel)* | 0.714 | [0.605, 0.803] | **NO** | **NO** | REFUSE | retired |
| `bash-callsite-grep-exclusion` n=20 *(ship-time)* | 0.300 | [0.145, 0.519] | **NO** | **NO** | REFUSE | **shipped** |
| `ft-rs` / `ft-md` bind | 0.000 | [0.000, 0.133] | **NO** | **NO** | REFUSE | killed ✓ |
| `ft-sh` bind | 0.040 | [0.007, 0.195] | **NO** | **NO** | REFUSE | killed ✓ |

**Both legs now bite, and they bite different rows — which is the evidence the corrected bars
are real rather than cosmetic.** At ship time `absence` and `structural-def` (p̂ = 0.200) clear
the 0.20 point bar and are caught *only* by the interval leg; `callsite` (p̂ = 0.300) fails
**both**. At the n=77 relabel, `absence` (p̂ = 0.273) now fails the **point** leg too — under
v3's vacuous 0.30/0.30 it would have been caught only by its interval, and under a naive
single point bar of 0.30 it would have **passed outright**.

For the `bind` rows, REFUSE is the desired verdict: the validator agrees with every kill we made.
Across eight rate-bearing decisions the matrix reproduces our five correct outcomes and reverses
our three wrong ones, **a day earlier and without a relabel.**

Method note, and it is the best illustration of why `rate.method` exists. Pane 3 flagged that
0.137 for 0/25 *"matches neither Wilson nor CP"*. It matches CP exactly — as the **two-sided**
95% Clopper-Pearson upper, which for k=0 has the closed form `1 − α^(1/n)`:
`1 − 0.025^(1/25) = 0.1372`. Wilson two-sided gives **0.1332**; CP **one-sided** gives
**0.1129**. Three genuinely different numbers for one sample. The flag was right to fire and
the number was not wrong — it was **underspecified**, which is precisely the defect
`unstated-assumption` exists to catch.

---

## 5. Tasks and dependency graph

**Edges are normative; there is deliberately no ASCII picture.** Pane 3's validation found the
v2 drawing disagreed with the `Depends:` lines — it merged T5 into the T2→T4 edge and T3 into
T4→T6, so an agent following the picture builds the wrong order. A single representation
removes the contradiction.

```
T1 → T2      T1 → T5      T2 → T3      T2 → T4      T2 → T6a
T5 → T2*     T3 → T7      T6a → T6b    T6b → T7     T7 → T8
```

`T5 → T2*` is a **runtime** dependency, not a build order: T2's checks read `authority.toml`, so
T5 must *exist* before T2 can run green, though T2 can be written first. Pane 3 found T5
graph-orphaned in v2 — *"runtime-required but order-invisible"* — which would have let a
scheduler build T2 before the file it reads existed. Marked, not hidden.

Parallelizable after T1: **{T2, T5}**, then **{T3, T4, T6a}**.

**T1 — Define the schema.** `evidence/SCHEMA.md` + a commented empty `matrix.toml`. Encodes §3.
*Blocks:* everything. *Acceptance:* a fresh agent writes a valid boundary from the doc alone.
*Rationale:* his matrix header carries its own rules; ours must too, or the first contributor
invents a second dialect.

**T1 also carries two shapes that were dropped by accident.** Pane 3's round-3 completeness
audit found that their own Axis A recommended **three** portable shapes and the plan adopted
only the third. The other two were lost between artifact and plan — not refused, not scoped
out, simply missing, which is the silent-debt failure Rule 12 exists to prevent. Restored here
because they cost almost nothing and both are conventions the schema doc is the right place to
state:

- **P1 — required-behavior header + numbered scenarios.** Every test file opens with its
  boundary id and the behaviors under proof; multi-case tests number their scenarios
  (`// 1. … // 2. …`), as `context_contract.rs:163,243,286,330,454,485` does. Cost ~30 lines of
  convention plus minutes per new file. Deficit: it organizes, it does not verify. Lose by
  refusing: spec drift — tests that no longer prove anything stated.
- **P2 — contract-phrased assertions.** `.expect("absent first file must succeed as
  prompt_only")` rather than a bare comparison; `panic!("expected IneligibleAlternative, got
  {other:?}")`. Cost: a reviewer checklist line and one pass over existing suites (~2h).
  Deficit: wrong-but-well-described behavior. Lose by refusing: unactionable failures.

Both are conventions rather than checks, so neither gets a validator code — and saying that
explicitly is what stops them being dropped a second time.

**T2 — Validator core.** `scripts/validate-evidence-matrix.py`, stdlib only. **Interpreter:
`python3.12`** — verified present at `/opt/homebrew/bin/python3.12` (3.12.13); system `python3`
is 3.9.6 with **no `tomllib`**, so the pin is load-bearing, exactly as he pins
`nightly-2026-08-31`. Implements the **thirteen deterministic codes** of §4 (the sixteen minus `orphan-case`,
which is T6a, and the two runtime checks): `boundary-coverage`,
`authority-<field>`, `unresolved-evidence`, `missing-red-arm`, `unpersisted-rate`,
`uncertified-pass`, `k-drift`, `uncovered-bead`. The remaining five — `orphan-case` (T6a),
`scope-disagreement` (runtime), `unstated-assumption`, `missing-non-claims`, `control-not-beaten`
— land in T6a and T3. *Depends:* T1; needs T5's file present to run green.
*Acceptance:* each of the eight fires on a planted violation.
*Rationale:* zero-dependency mirrors his choice and keeps the validator runnable in any pane.

**T3 — RED arm per code.** Every check ships a planted-violation fixture.
*Depends:* T2. *Acceptance:* `--selftest` exits nonzero if any RED arm stops firing.
*Rationale:* AGENTS.md — "a stage that has only ever gone green is unproven." Today's callsite RED
arm went inert the moment I disabled the rule it used; arms must not depend on live state.

**T4 — Backfill the 2026-09-20 boundaries.** All eight disabled rules, five instruments, R63–R71,
and the live omp seams. Rates carry `label_rows` or are marked `unpersisted` and **may not claim
`passed`**. *Depends:* T2. *Acceptance:* validator green; the three uncertified rules appear as
`retired`, not `passed`.
*Rationale:* backfill is what converts the matrix from a proposal into an inventory — and F6 says
we currently cannot answer "what is live".

**T5 — Authority file + review protocol.** `evidence/authority.toml` + the one-paragraph rule in
AGENTS.md that bars, n, scopes, and rungs move only by Joshua's edit.
*Depends:* T1. *Acceptance:* a matrix edit that moves a bar fails `authority-rate.bar`.
*Rationale:* this is the second key. Without it we have a nicer spreadsheet, not a control.

**T6a — Case identity and the walker.** Both reviewers hit the same wall: *"walk every
`selftest-*.sh` case — what is a case?"* Our selftests emit `ok <label>` / `FAIL <label>` to
stdout and **no case IDs exist anywhere**, so the task as written in v2 was unimplementable.

**Define it first, then walk it.** A *case* is a labelled assertion a selftest can enumerate
without executing: each in-scope file gains a `--list-cases` mode printing one stable
`<script-basename>::<case-id>` per line.

**v4.1 claimed "identity is the label, so no renaming is required." That was an unverified
assertion about our own codebase, and measurement refutes it on three counts** (pane 1,
2026-09-21, across all 14 `scripts/selftest-*.sh`):

| assumed | measured |
|---|---|
| every selftest shares one idiom | **9 of 14** use `note ok "…"`; **5 have no idiom at all** — `selftest-{lane-status-integrity,lane-status-pipe,other-reasons,reason-numerals,score-lineage}.sh` |
| labels are static strings | **16 of 46** ok-labels contain `$interpolation` — not stable identities |
| labels are unique per file | `selftest-ttsr-rules.sh` has **5 duplicate labels** — identity collisions |

Worse, pass and fail branches carry *different* strings and the FAIL one interpolates
(`note ok "ee-preflight exits 1 (refusal)"` vs `note FAIL "ee-preflight exit=$rc1, want 1"`),
so "the label" was never a single thing.

**Corrected design and corrected cost.** Case identity is an **explicit static id**, not a
scraped label: `note ok` gains a leading id argument, and `--list-cases` prints the ids. Work
the plan previously assumed away: normalize **5** files to the idiom, assign explicit ids to
**46** cases of which **16** currently interpolate, and disambiguate **5** collisions. Estimate
revised from "walk the labels" to **~4h**, and it is now the largest single task in the program.

**Scope, named explicitly:** `scripts/selftest-*.sh` plus `*.test.mjs` under `work/*/test/` —
and *only* those two; other trees are out of scope until a boundary claims them.
*Depends:* T1, T2 — **not** T4. Runs parallel with backfill.
*Acceptance:* `--list-cases` on every in-scope file yields a **unique** id set, and the union
contains no `$`.
*Rationale:* Axis A `:143-144` — his validator resolves matrix→source but nothing checks the
reverse. This is the cheapest place we exceed upstream, and it cannot be built until "case"
means something. **The measurement above is why the plan is worth writing:** the task looked
free and is four hours.

**T6b — Enforce registration.** Every enumerated case must appear in some boundary.
*Depends:* **T6a only.** v4.1 kept `T4` on this task; pane 4's round 2 caught that it is still
false — the acceptance runs against a `mktemp -d` fixture matrix, so it needs **no real
backfill at all**. The edge survived a round of being questioned because I weakened it instead
of removing it, which is its own lesson about fix rounds.
*Acceptance:* against a **temporary fixture matrix in `mktemp -d`**, removing a row whose case
still exists exits `orphan-case`. Pane 3 flagged v2's acceptance as destructive — it directed a
fresh agent to delete a live boundary row with no restore instruction. No test in this program
mutates the real matrix.

**T7 — Wire into `foundation/gates.sh`.** New stage, per AGENTS.md gate thrift: extend `80` rather
than add a stage if it fits. *Depends:* T3, T6b. *Acceptance:* `gates.sh --selftest` green;
matrix violation turns the gate red.
*Rationale:* an unwired validator is an unconsumed instrument (R68) — the phase boundary forbids
adding another.

**T8 — Regenerate ARC.md figures from the matrix.** *Depends:* T7. *Acceptance:* the freshness
guard fails when a figure and the matrix disagree.
*Rationale:* P3's freshness proposal; closes the loop from claim to published number.

---

## 6. Acceptance for the whole program

- `python3.12 scripts/validate-evidence-matrix.py` exits 0 on a clean tree, and exits nonzero
  with the correct code for each of the **sixteen** planted violations in §4 — one per code,
  no more and no fewer, so the count cannot drift from the table again.
- Replaying 2026-09-20 through it **refuses all three ships**, and **refuses the three
  `ft-*` bind rows too — which is the correct outcome, because for a bind rate REFUSE *is* the
  kill.** v4.1's wording said the program "accepts the 0/25 kills", which reads as PASS and
  contradicts the §4.2 table; pane 4 caught the contradiction. The single consistent statement:
  **the validator reproduces all five decisions we got right and reverses the three we got
  wrong.**
- Every rate in the tree either points at persisted rows or is explicitly `unpersisted` and
  cannot be `passed`.
- `evidence/authority.toml` differs from `matrix.toml` only in ways the validator permits.
- The orphan check finds zero unregistered cases, or the matrix grows to cover them.

---

## 7. What we refuse, with the Rule 12 cost/defect/loss stated

*Round-3 completeness audit (pane 3, `0b0e225`) surfaced four unpaid debts — items the axis
evidence documented that this plan neither adopted nor refused. Drafts at
`docs/PLAN-DEBTS-DRAFT-20260921.md`, all four ruled ADOPT-as-drafted by pane 1. Three are
adoptions (§2/T6a); the refusal below is the fourth.*

**Full platform-boundary matrix** (real Darwin + Linux build matrix with probe crates per
target). *Cost:* days, plus build hosts we do not have — local builds are denied here and the
workers are Linux-only. *Defect class it would not catch:* **none of F1–F6** — every one is a
declaration or provenance failure, not a platform failure. *What we lose:* nothing today.
**Retry when a boundary needs a platform to prove.** This is scope creep, not rigor.

*But the cheap half is adopted, not refused.* **Refusal-of-simulation** (§2): a check that
refuses to *certify* platform-dependent behavior from simulated evidence — ambient
`RUSTFLAGS`/cross flags present, or the running host mismatching the claimed target, fails
loudly rather than passing quietly. ~1h, deterministic, no builds. It cannot catch broken
platform behavior; **it refuses to judge, which is the point.** Directly relevant: today's `sr`
repro was cross-built on Linux and executed on macOS, and the comment that went public did not
say where it ran until I asked. This check is that omission made mechanical.

**Real-process e2e harness** (his `scripts/e2e`, SQLite + spawned processes). *Cost:* a
spawn-and-reap harness we do not have; `hub` processes are the analogue and are unproven for it —
est. 2–3 days. *Defect class it would not catch:* none of F1–F6; all six are declaration and
provenance failures, not integration failures. *What we lose:* genuine end-to-end coverage of
multi-process behaviour — real, and the reason this is DEFERRED rather than rejected. Retry when a
boundary needs a spawned process to prove.

**Newtype-heavy inline builders.** *Cost:* low in Rust, high in shell/JS where our instruments
live. *Defect class:* none of F1–F6. *What we lose:* fixture ergonomics. The pattern ports, the
ergonomics do not (Axis A `:178-181`).

**A hosted CI pipeline.** *Cost:* moderate. *Defect class:* none of F1–F6. *What we lose:*
enforcement on push. **He does not have one either** — rigor is in-tree validators, which is the
portable form.

---

## 8. Boundary — what this plan does not claim

**Scope, stated once so it is not re-raised as debt.** The matrix program covers evidence
*about* rules, instruments, refutations, and seams. It does **not** cover Jev-client plumbing —
consent-before-key, live-ignore discipline, retry classification, injected transport, named
negative controls — which Axis C found upstream carries in 2,529 lines. That track ships its
own gates, measured separately. **Silence here is scope, stated once, not debt.** (Pane 3's D4:
leaving it silent costs a re-raise at the next completeness audit, which is churn with no
information.)

**Two further adoptions from the round-3 audit, recorded here because they change §2 and T6a
rather than this section.** *Docs-consistency validator* — port his `validate_public_contracts.py`
shape (heading anchors, link resolution, embedded JSON/TOML re-parsed strictly: duplicate keys
rejected, non-finite floats rejected) **with the adversarial test file his tree lacks**; ~5h,
1 script + 1 test. Axis B found docs-consistency is one of two things in *his* tree with no
adversarial test, so this is the second place we exceed upstream. *Trusted evidence
entrypoints* — his `TRUSTED_CHECK_ENTRYPOINTS` frozenset, with the reason *"any other plain
function is a helper, not test evidence"*; folded into T6a as one predicate on the walker
output, ~1h. Without it a passing suite can be composed of helpers that assert nothing.

Axis B **landed** (`f6c5a0a`) and its eval-policy findings are folded into §4.1; the v1 text
here said it was "in flight" and survived four revisions — **a fourth instance of the copy site
outliving the fix**, found by re-reading rather than by a reviewer. `cargo test` was never run
against skillranker, so nothing here claims his suite passes. The 2026-09-20 replay in §6 is
computed from recorded intervals, not re-measured. No claim is made that a matrix improves rule
quality — it constrains what may be *claimed* about a rule, which is a different and smaller
thing.
