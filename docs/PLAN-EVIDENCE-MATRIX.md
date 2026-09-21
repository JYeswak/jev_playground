# PLAN v1 — the evidence matrix: make a coverage claim a thing a validator can refuse

**Status:** v1, pre-review. Written by pane 1 from grounded evidence (Axes A, C, D committed;
Axis B in flight). Per `skill://planning-workflow`, this document is self-contained — a fresh
agent who has never seen this lane can implement from it without asking.

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

# THE CLAIM, with its scope, its assumptions, and its control
# Method name carries its assumption, per his eval policy (:247-249):
#   two_sided_95_wilson_with_one_primary_case_per_independent_family
rate = { kind = "fp", k = 4, n = 77,
         method = "two_sided_95_wilson_independent_rows",
         bar_point = 0.30, bar_interval = 0.30 }   # DUAL bar, see §4.1
negative_control = { name = "always_quiet", must_lose = true }
non_claims = ["not a live measurement",
              "single labeller",
              "rows not independent across one session"]
scopes = ["project", "global"]
rung = "L3"                            # L0..L4 from AGENTS.md
status = "planned"                     # planned | executed | passed | failed | retired
```

`authority.toml` holds the same rows with the **bound fields** frozen. Bound set for this lane:
`owner_bead, kind, title, red_arm, rate.method, rate.bar_point, rate.bar_interval, rate.n,
negative_control, scopes, rung`. The working matrix may move `status`, `k`, and add evidence
refs; **it may not move a bar, a method, an n, a control, a scope, or a rung without an authority
edit.**

**Who holds the second key.** Joshua. An authority edit is a reviewed change; the matrix is ours.
This is the mechanism that would have stopped F3, because I could not have both set the bar and
scored against it.

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
| `status = passed` ⇒ **both** bars clear (see §4.1) | `uncertified-pass` | NEED #6 exactly |
| `kind = rule` ⇒ enumeration in every declared scope agrees with `status` | `scope-disagreement` | **F5 exactly** |
| every non-epic `jev-*` bead is covered by ≥1 boundary | `uncovered-bead` | untracked work |
| `rate.method` names its independence assumption | `unstated-assumption` | silent iid assumption |
| ≥3 `non_claims`, and they name labeller count and independence | `missing-non-claims` | a fixture quietly becoming a claim |
| `negative_control.must_lose` ⇒ evidence that it loses | `control-not-beaten` | a rule that beats nothing |
| every semantic field has a corrupt-it-must-fail twin | `no-mutation-twin` | untested validator |

`uncertified-pass` is the rule that makes this pay for itself: **a boundary cannot say `passed`
while its own interval admits a value above its bar.** Applied to 2026-09-20 it refuses
`absence-from-one-probe` (upper 0.381 > 0.30), `bash-structural-def-search` (lower 0.605 > 0.30),
and `bash-callsite-grep-exclusion` (p̂ = bar). All three shipped anyway. **The validator would
have refused all three before they went system-wide.**

`scope-disagreement` is the F5 fix: the matrix declares scopes, the validator *enumerates* them
(`omp ttsr list | grep -c`) rather than probing, so "reported disabled but still live" becomes
impossible to commit.

### 4.1 The dual bar, the stated assumption, and the control — adopted from his eval policy

Axis B (`docs/demos/upstream-repro/axis-b-validators-20260921.md` §2) found that
`validate_eval_policy.py` already solves NEED #6, and more stringently than I proposed. Four
mechanisms, adopted:

**1. A dual bar, not a single one.** His top-one precision requires rate ≥ 0.90 **AND** Wilson
lower ≥ 0.80 (`:263`). A point estimate and an interval bound are different claims and he makes
both mandatory. Today we used only one, which is how `structural-def` passed at 4/20 = 0.20 and
then measured 0.714 at n=77. Our matrix therefore carries `bar_point` and `bar_interval`, and
`uncertified-pass` fires if **either** fails.

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
assumed. Note what this does to our own history — a rule with FP 0.714 does *not* beat
`always_quiet`, and this check would have said so without any labelling at all.

**5. Mutation twins.** `test_eval_policy.py` is 43 mutation tests: corrupt one semantic field,
require `SystemExit` (Axis B §1). Named failure modes include *false abstention scored correct*,
*coverage ≠ recall*, *averages hiding loss*, *unstarted cases disappearing*. `no-mutation-twin`
requires every semantic field of our matrix to have one. This is the discipline that makes the
validator itself trustworthy rather than merely present.

**What this costs us in credibility, stated plainly:** four of the five mechanisms above are
things this lane argued for in prose today and failed to enforce. He enforces them in 521 lines
of stdlib Python with 43 mutation tests. That gap is the honest measure of the distance.

---

## 5. Tasks and dependency graph

```
T1 schema ──┬── T2 validator core ──┬── T4 backfill ── T6 orphan ── T7 gate ── T8 arc
            │                       ├── T3 red arms ───┘
            └── T5 authority ───────┘
```

**T1 — Define the schema.** `evidence/SCHEMA.md` + a commented empty `matrix.toml`. Encodes §3.
*Blocks:* everything. *Acceptance:* a fresh agent writes a valid boundary from the doc alone.
*Rationale:* his matrix header carries its own rules; ours must too, or the first contributor
invents a second dialect.

**T2 — Validator core.** `scripts/validate-evidence-matrix.py`, stdlib only (`tomllib`, py≥3.11 —
note `python3` here is older; pin `python3.12` as he pins his toolchain). Implements the first six
codes in §4. *Depends:* T1. *Acceptance:* each code fires on a planted violation; `selftest-*`
covers all six.
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

**T6 — Orphan check.** Walk every `selftest-*.sh` case and `*.test.mjs` and require registration.
*Depends:* T4 (needs a populated matrix to be meaningful). *Acceptance:* deleting a boundary row
whose case still exists fails `orphan-case`.
*Rationale:* the gap Axis A found in his tree; the cheapest place we can exceed upstream.

**T7 — Wire into `foundation/gates.sh`.** New stage, per AGENTS.md gate thrift: extend `80` rather
than add a stage if it fits. *Depends:* T3, T6. *Acceptance:* `gates.sh --selftest` green;
matrix violation turns the gate red.
*Rationale:* an unwired validator is an unconsumed instrument (R68) — the phase boundary forbids
adding another.

**T8 — Regenerate ARC.md figures from the matrix.** *Depends:* T7. *Acceptance:* the freshness
guard fails when a figure and the matrix disagree.
*Rationale:* P3's freshness proposal; closes the loop from claim to published number.

---

## 6. Acceptance for the whole program

- `python3.12 scripts/validate-evidence-matrix.py` exits 0, and exits nonzero with the right code
  for each of the nine planted violations.
- Replaying 2026-09-20 through it **refuses all three uncertified ships** and **accepts the
  0/25 kills** (CI upper 0.137 < 0.20 bar).
- Every rate in the tree either points at persisted rows or is explicitly `unpersisted` and
  cannot be `passed`.
- `evidence/authority.toml` differs from `matrix.toml` only in ways the validator permits.
- The orphan check finds zero unregistered cases, or the matrix grows to cover them.

---

## 7. What we refuse, with the Rule 12 cost/defect/loss stated

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

Axis B (the other ten validators, `validate_eval_policy.py`, the p3/p4 gate internals, the no-CI
run order) is **in flight**; §4's check list may grow when it lands. `cargo test` was never run
against skillranker, so nothing here claims his suite passes. The 2026-09-20 replay in §6 is
computed from recorded intervals, not re-measured. No claim is made that a matrix improves rule
quality — it constrains what may be *claimed* about a rule, which is a different and smaller
thing.
