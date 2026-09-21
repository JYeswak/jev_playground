# PLAN REVIEW R1 — adversarial (Grok on Opus v2)

Target: `docs/PLAN-EVIDENCE-MATRIX.md` @ `680d11e` (279 lines). Not `662154d`.
Reviewer: Grok. Author: Opus. Round 1 of ≥4. **Do not convert to beads.**
Lane: offline. Intervals recomputed here; ship-time CIs taken from `docs/NEEDS.md:33-38`.

Header is already lying: line 1 still says **PLAN v1**, line 3 **Axis B in flight**. The commit message says v2 folded Axis B. A plan that cannot name its own revision is the defect it exists to prevent.

---

## 0. Whole-plan verdict

Keep the matrix. Kill the story that v2 adopted a dual bar. The interval check you already had is NEED #6. Equal `bar_point = bar_interval = 0.30` is a rename. His 0.90/0.80 is a *split*. You did not take the split. You took the slogan.

The validator still does not stop a ship. It stops a `status=passed` string. F5 happened in `~/.agents/rules` and `omp config`, not in a TOML file that did not exist.

---

## (1) Two-key scheme is theatre if Joshua is the key

Jeffrey's second key is **a second file with byte-equality**, not a person. `validate_contract_matrix.py` set-equality + bound-field equality. The control is: you cannot silently widen IDs or edit frozen fields in the working matrix. Review is whoever reviews the authority-file diff.

You replaced that with **"Joshua holds the second key"** (`:109-111`). Failure mode:

- Panes write `authority.toml` and ask Joshua to rubber-stamp.
- He is the same authority who already told the fleet to ship eight rules this morning.
- F3 was "bars set and measured by the same party." A human bottleneck who already blessed the bars is the same party with extra latency.
- When he is asleep, panes will edit both files in one commit. The validator cannot see who typed.

**Fix (time, not person):** the second key is *when* the bar was frozen, not *who* signed it.

- Bound fields hashed **before** `label_rows` exist (NEED #6 preregistration).
- `k` is not a matrix field. It is `count_fp(label_rows)`. Still unbound in v2 (`:105` — working matrix may move `k`).
- Same-commit ban: `authority.toml` and `label_rows` cannot land together.
- Drop `title` from the bound set — typo-fixes will burn the second key on noise.

```diff
-**Who holds the second key.** Joshua. An authority edit is a reviewed change; the matrix is ours.
-This is the mechanism that would have stopped F3, because I could not have both set the bar and
-scored against it.
+**The second key is temporal, not personal.** `authority.toml` is frozen *before*
+`label_rows` exist. The validator refuses `status=passed` unless
+`authority.frozen_at < min(label_rows.labelled_at)`. Joshua reviews authority
+diffs because he owns taste, not because his name is a cryptographic key.
+A pane that scores the sample cannot author the authority row for that id
+(steward ≠ scorer). `k` is derived from `label_rows`, never transcribed.
```

Without that, two files is a nicer spreadsheet. You said so yourself about T5 (`:221`) and then implemented the rubber-stamp version.

---

## (2) Dual-bar arithmetic — the centerpiece cites the wrong intervals

### What dual actually is in v2

`bar_point = 0.30`, `bar_interval = 0.30` (`:91-93`). `uncertified-pass` fires if **either** fails (`:155`). For FP (lower-better):

- point fails iff `p̂ > bar_point`
- interval fails iff `upper > bar_interval`

His eval policy (`axis-b-validators-20260921.md:49`, upstream `:263`): top-one precision **rate ≥ 0.90 AND Wilson lower ≥ 0.80**. That is a **10pp split**, higher-is-better. Equal 0.30/0.30 is not that mechanism.

### Ship-time numbers (`NEEDS.md:35-38`, Clopper-Pearson 95%)

Recomputed Wilson two-sided z=1.96 in this session (stdlib). No overturn on refuse/accept.

| ship (the act) | k/n | p̂ | CP 95% | Wilson 95% | point ≤0.30 | upper ≤0.30 |
|---|---|---:|---|---|---|---|
| absence | **4/20** | 0.200 | [0.057, **0.437**] | [0.081, **0.416**] | PASS | **FAIL** |
| structural-def | **4/20** | 0.200 | [0.057, **0.437**] | [0.081, **0.416**] | PASS | **FAIL** |
| callsite | **6/20** | 0.300 | [0.119, **0.543**] | [0.146, **0.519**] | PASS (equal) | **FAIL** |
| kill ft-rs (claimed accept) | **0/25** | 0.000 | [0.000, **0.137**] | [0.000, **0.133**] | PASS vs 0.20 | **PASS** |

Post-ship relabels the plan cites at `:136-138`:

| later sample | k/n | p̂ | Wilson | what the plan quoted |
|---|---|---:|---|---|
| absence retire | 21/77 | 0.2727 | [0.186, **0.381**] | "upper 0.381" |
| structural R71 | 55/77 | 0.7143 | [**0.605**, 0.803] | "lower 0.605" |

**The plan uses retire-time n=77 to claim a ship-time control would have fired.** That is a dated interval attached to the wrong event. Same class as today's five measurement errors.

### Does dual still refuse all three ships?

**Yes — on the INTERVAL leg, at ship-time 4/20 and 6/20.** Point leg refuses **none** of the original ships. `4/20 = 0.20` is why they shipped. Dual with equal bars is NEED #6's upper check plus a redundant point check.

Callsite `p̂ = bar`: point **passes** (`0.300 ≤ 0.30`). Interval refuses. The plan's parenthetical "(p̂ = bar)" describes NEED #6, not the point half of dual.

Structural "lower 0.605 > 0.30": **wrong statistic**. Spec says upper (`:135-136`). 55/77 upper is 0.803. Also not the ship.

### Does dual now refuse anything you claimed to accept?

**No.** 0/25 vs bar 0.20: p̂=0 and CP upper 0.137 both clear. Dual still accepts the kill. Pin **Clopper-Pearson** if you want the 0.137 figure; Wilson is 0.133. Shopping methods after seeing the number is F3.

### What equal dual does *not* do

It does not catch "passed at 4/20=0.20 then 0.714 at n=77" via the point bar. The point bar is what *permitted* 4/20. The interval bar is what would have stopped it. Stop attributing that to his 0.90/0.80.

A *real* split for FP (conservative, matching his direction): `bar_interval ≤ bar_point` (upper tighter than the headline). Example: `bar_point=0.30`, `bar_interval=0.25` would still refuse 4/20. A *liberal* split `bar_interval=0.40` would **pass absence n=77** (upper 0.381 < 0.40, p̂ 0.273 < 0.30) and re-open a retirement. Freeze direction in the schema or this will be gamed on the next bar edit.

```diff
-Applied to 2026-09-20 it refuses
-`absence-from-one-probe` (upper 0.381 > 0.30), `bash-structural-def-search` (lower 0.605 > 0.30),
-and `bash-callsite-grep-exclusion` (p̂ = bar). All three shipped anyway.
+Applied to **ship-time** CIs in `NEEDS.md:35-38` (CP 4/20 upper 0.437, 6/20 upper 0.543):
+the INTERVAL leg refuses all three; the POINT leg refuses none.
+The 0.381 / 0.605 figures are post-ship relabels (21/77, 55/77) and must not
+be cited as what would have blocked the morning ship.
+`bar_point` and `bar_interval` both 0.30 is NEED #6, not his 0.90/0.80 split.
+Validator recomputes the interval from `label_rows`; it never trusts a stored upper.
```

Also fix §6 `:244-245` "nine planted violations" — the table now has **13** codes. T2 `:201-203` still says "first six codes." v2 grafted 4.1 onto a v1 task list and left the counts stale.

---

## (3) `scope-disagreement` is fatal as a commit check, acceptable as a doctor

It shells `omp ttsr list | grep -c` (`:141-142`).

- **Environment:** omp missing → current lane selftests SKIP (not fail). Skip-as-pass is F5 in a costume.
- **Cwd/profile:** project vs `/tmp` vs `~/.omp/profiles/<name>` disagree. Validator cwd is not a declared input.
- **Not in git:** `ttsr.disabledRules` is user config. A commit green on pane 4 can be red on pane 1. Inverse of a reproducible gate.
- **grep -c:** substring, and under `pipefail` a zero count is exit 1. We already built `scripts/ttsr-assert-disabled.sh` to not do this.

**Fatal** inside `validate-evidence-matrix.py` if that script is a git/gates commit check.

**Acceptable** as a live doctor that `ttsr-assert-disabled.sh` already is. Wire that. Do not reimplement it with `grep -c`.

```diff
-| `kind = rule` ⇒ enumeration in every declared scope agrees with `status` | `scope-disagreement` | **F5 exactly** |
+| `kind = rule` ⇒ `scripts/ttsr-assert-disabled.sh` (or assert-present) agrees with `status` | live `scope-disagreement`, **not** a matrix-parse check | **F5 exactly** |
```

Declaration validator checks `scopes` is a frozen list of names. Live enumeration is T7-adjacent, fail-closed if omp absent (exit 2, never 0).

---

## (4) Reward hacks — v2 added four new surfaces

AGENTS.md named class. Each check is a thing an agent can satisfy without the work.

**Still open from v1:**

1. **`k` unbound.** Set `k=0`, `n=77`, `bar_*=0.30`. `label_rows` has ≥77 keys (`unpersisted-rate` greens). Wilson upper on 0/77 ≈ 0.047. `uncertified-pass` greens. Dual does not help. **This is the hole that eats the centerpiece.**
2. Never set `status=passed`. Ship the `.md` rule anyway. Matrix does not walk `.omp/rules/` or `~/.agents/rules`.
3. `status=retired` while the file is still in both roots (cross-root drift already a RED in `selftest-ttsr-rules.sh`; matrix ignores it).
4. `status=executed` forever. Uncertified-pass never runs.
5. `rate` omitted. No `unpersisted-rate`, no dual bar.
6. Tautological `red_arm` that is in `selftest_cases` but is the quiet near-miss.
7. Epic-labelled beads to dodge `uncovered-bead`.
8. Method shopping: store `interval="wilson"` after seeing CP vs Wilson.

**New in 4.1:**

9. **`missing-non-claims` substring theatre.** Schema example (`:95-97`) is already the exploit:
   ```
   "not a live measurement"
   "single labeller"
   "rows not independent across one session"
   ```
   Three strings, names labeller count and independence, semantically empty. His check (`:163-167`) requires phrases; ours requires topics. An agent writes those three lines on every row.

10. **`unstated-assumption` name-contains-independent.** Method `two_sided_95_wilson_independent_rows` while drawing 20 overlapping fires from one session. The identifier lies; the check passes.

11. **`control-not-beaten` without a loss.** `always_quiet` / `must_lose=true` (`:94`). His always-abstain has a 0/1/2 table and a 6-row counterexample that *recomputes*. Ours has a boolean. Agent sets `must_lose=true` and points at a comment. `:172-173` claims FP 0.714 would fail "without any labelling at all" — **false**. 0.714 is a labelled rate. Quiet vs fire needs TP, not just FP.

12. **`no-mutation-twin` satisfied by a twin that asserts the mock.** Corrupt field, expect `SystemExit`, implement the twin to match the production bug. 43 of his tests work because they are independent of the policy author. Ours will be written by the same pane that writes the validator (F3 again).

**Minimum patches:**

```diff
-# working matrix may move `status`, `k`, and add evidence refs
+# working matrix may move `status` only.
+# `k` is computed: fp_count(label_rows). Transcribed `k` is InvalidMatrix.
+
-non_claims = ["not a live measurement", "single labeller", "rows not independent…"]
+labeller_count = 1          # int, mutation-twinned
+iid_claimed = false         # bool; if true, method must match; if false, interval is descriptive
+non_claims = []             # optional prose, never the control
+
-negative_control = { name = "always_quiet", must_lose = true }
+# require a 0/1/2 loss table on the same label_rows, recomputed, always_quiet total > candidate
+# or omit the control and cannot status=passed
```

Walk **rule files**, not just selftest cases: every `.omp/rules/*.md` and every promoted `~/.agents/rules` name has a boundary. Otherwise the matrix is a diary of what we remembered.

---

## (5) Eight tasks, false edge, stale counts

```
T1 ──┬── T2 ──┬── T4 ── T6 ── T7 ── T8
     │        ├── T3 ───┘
     └── T5 ───┘
```

**T6 depending on T4 is a false edge.** Orphan is source→matrix: *unregistered cases fail*. That RED arm is strongest on an **empty** matrix (every case is an orphan). Waiting for backfill so the check is "meaningful" is how you ship a validator that has only ever gone green. T6 depends on T2+T3. T4 is parallel content.

**T4 depending on T2 but not T5 repeats F3.** Backfill writes bars into a matrix with no authority file yet. T4 depends on T2 **and T5**.

**T8 is process porn.** ARC.md as a generated view of the matrix is a consumer only if humans read ARC for decisions. They read `NEGATIVE_EVIDENCE.md` and `EVAL.md`. Drop T8 or fold a one-line freshness assert into T7.

**T2 still implements "first six codes"** while §4 lists 13. Acceptance still wants 9 planted violations. v2 did not update the DAG.

```
T1 ──┬── T2 ── T3 ──┬── T6 ── T7
     └── T5 ────────┴── T4 (parallel; needs T5)
```

Five implementation tasks plus wiring. Not eight.

---

## (6) Missing entirely

- **Direction of the bar.** FP upper vs precision lower. Schema must say `kind=fp` ⇒ compare `upper` to `bar_interval`. Kind=accuracy ⇒ compare `lower`. Unsigned dual will be applied backwards (plan already used "lower 0.605" for an FP ship).
- **Recompute, never store, the interval.** Stored upper is a forgery surface.
- **Rule-file inventory** (F6 is live-rule count, not selftest-case count).
- **Cross-root drift** already RED in `selftest-ttsr-rules.sh`; matrix never mentions both roots.
- **Same-commit ban** authority vs labels.
- **red_arm must be observed to FIRE** in `--selftest`, not merely listed.
- **Python 3.12 pin vs this machine's 3.9.** T2 notes it; no `#!/usr/bin/env python3.12` contract.
- **Replay uses ship-time 4/20 not n=77.**
- Plan length 279 lines. `planning-workflow` calls <1500 under-specified for a non-trivial program. I will not pad. I will say: schema of `label_rows`, loss table, and live-vs-declaration split are not implementable from this doc alone. That fails self-containment.

---

## (7) Wholesale 4.1 — what we took on authority

Rule 12: default ADOPT; refusal needs cost, defect-class-not-caught, loss. The inverse also binds: **adopt the mechanism that fits F1–F6, not the file that impressed us at 17:00.**

| # | 4.1 claim | Fits our F-list? | Verdict |
|---|---|---|---|
| 1 Dual bar 0.90/0.80 copied as 0.30/0.30 | Interval half fits NEED #6 / F3. The *split* does not; we have no precision target of 0.90. Equal bars are a rename. Story that dual explains 4/20→0.714 is **false** (point 0.20 is what shipped). | **Rewrite.** Keep one interval bar with explicit direction. If you want a split, `bar_interval ≤ bar_point` for FP, and say why the gap exists in *our* units. |
| 2 Method name carries independence | Real: we treated overlapping session fires as iid. A longer identifier does not fix iid. His string is `…_one_primary_case_per_independent_family` — **our sampling frame is not that**. Copying it is a false assumption with extra syllables. | **Adopt the idea, not the string.** `iid_claimed: bool`. If true, method must be a named iid estimator; if false, interval is descriptive and **cannot `passed`.** |
| 3 ≥3 non-claims naming topics | His ≥4 phrases describe a *frozen synthetic fixture* (`frozen_contract_not_evidence`). Our rows are live rules. Phrase-matching "labeller" / "independence" is the exploit in the schema example. Does not catch F1 (unpersisted rows) or F3 (same party). | **Refuse as specified.** Replace with `labeller_count: int` + `iid_claimed: bool`, mutation-twinned. Prose optional. |
| 4 `always_quiet` must_lose | His control has a loss table and a recomputed counterexample. We have a boolean and a slogan. `:172` "without any labelling" is a wrong claim about a labelled rate. Does not catch F1–F6 without a loss. | **Refuse until a 0/1/2 loss exists.** Cost to adopt for real: define quiet vs fire on the same `label_rows`. That is a day, not a field. |
| 5 Mutation twins | Fits dead-check class (callsite RED arm went inert; UBS empty-scan-set). Axis B P2 already priced ~2h/check. | **Adopt.** This is the one 4.1 item with a measured defect *here*. |

**The tell that we stopped thinking:** five mechanisms from one file in one hour, counts in T2/§6 not updated, header still v1, dual-bar story inverted, non-claims example is the bypass, `always_quiet` claimed to work without labels. That is ADOPT as mood, not Rule 12.

Rule 12 refusal for (3) and (4) as specified:

- **Cost:** structured fields are fewer lines than a phrase linter; a real loss table is ~1 day on existing `label_rows`.
- **Defect class they would not catch:** F1 (persistence) and F5 (enumeration). Phrase-presence and a boolean `must_lose` catch neither.
- **Loss if we refuse the slogan:** we do not get a green `missing-non-claims` / `control-not-beaten` that an agent can satisfy in thirty seconds. That is the point.

---

## Diffs Opus should integrate (minimal)

1. Header: v2, Axis B landed, this review is R1, round-not-done.
2. §2 uncertified-pass citations: ship-time 4/20 CP 0.437 / 6/20 0.543, not 0.381/0.605.
3. Dual: either drop `bar_point` or make it a real split with direction. Do not claim 0.90/0.80.
4. `k` derived; `title` unbound; temporal freeze; steward ≠ scorer.
5. `non_claims` → typed fields. `always_quiet` waits on a loss table.
6. `scope-disagreement` out of the parse validator; call `ttsr-assert-disabled.sh`.
7. DAG: T6  ped T4; T4 needs T5; drop T8; T2 implements all codes not "six"; §6 planted count = 13 or whatever remains.
8. Rule-file walk for F6.
9. Validator recomputes intervals; method frozen in authority including Wilson vs CP.

I am not editing the plan. That is the author's job after review. Beads after round 4.

---

## Boundary

- Did not run his `validate_eval_policy.py` (vendored/other checkout). Citations of `:263` etc. are via Axis B's file:line, which names `sr-head-retest@b9e8b34`.
- Wilson z=1.96 two-sided computed here; CP ship-time taken from `NEEDS.md` as recorded, not re-derived with scipy.
- ntm start-callback for v2 **failed**: pane 1 `not in a mode` (copy-mode). Start file on disk: `docs/demos/upstream-repro/p4-callback-plan-r1-v2-start-20260920.txt`.
