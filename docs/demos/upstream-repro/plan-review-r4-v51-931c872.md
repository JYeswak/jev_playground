# PLAN REVIEW R4 (final) — v5.1 @ `931c872`

Target: `docs/PLAN-EVIDENCE-MATRIX.md` (508 lines on disk). Grok. Round 4 of 4–5. **No beads. No plan edit.**

Diff base: `29038ab` (v4.1) → `931c872` (v5.1): +103 / −32 on that file. Structural: bars out of the working row; `bar-unset` / `bar-equals-observed`; T6b `Depends: T6a only` and `T4 → T6b` dropped from the edge list; T6a costed from measurement; §6 kill wording; T1 P1/P2 conventions.

---

## Verdict

**NOT-YET.**

The six R2 defects are mostly *named*. Three of them still have a live copy-site. T2 is unimplementable until those three are one sentence each. That is the blocker, not taste.

---

## (1) Re-verify the six R2 fixes. Hunt copy-site.

| R2 defect | Intended fix | Live copy-site at 931c872 |
|---|---|---|
| §4.2 header `p̂ ≤ 0.30` (vacuous dual) | `p̂ ≤ bar_point` | **Partial.** `:254-255` still hardcodes `upper ≤ 0.30` and bind `lower ≥ 0.20` beside a variable `bar_point`. Defaults in the copy site. |
| `bar_point = 0.20` = 4/20 | unset; record the error | **Landed in §4.1.** Undone in §4.2 `:272-277`: *"Both legs now bite… evidence the corrected bars are real"* using the 0.20 it just refused. |
| k-drift honesty | closes transcription, not labelling / R71 | **Did not land.** `:129` still *"why that is not a hole."* No "transcription" / "labeller" sentence exists. `:157` still `unpersisted-rate` **R70/R71 exactly**. Overclaim. Schema points at **§4.1(6)** (`:115`) — **there is no item 6.** |
| §6 accepts 0/25 vs table refuses | refuse = kill | **Landed** (`:431-436`). Residual: "five right, three wrong" and "eight decisions" (`:280`, `:435`) vs **7 table rows**. |
| T6b `Depends: T4` | T6a only | **Landed** in Depends (`:405`) **and** the edge list (`:301-302`). The instance you feared is gone. |
| T2 six/eight vs planted count | one list | **Not landed.** T2 = eight codes (`:340-344`). §6 = **fifteen** plants (`:429-430`). `bar-unset` / `bar-equals-observed` / `no-mutation-twin` are not in T2's eight. |

**Copy-site class (this round, not the T4→T6b instance):**

1. **Title.** Line 1 `PLAN v4`, line 3 `post-review-round-1`. File is v5.1 after four review rounds. A fresh agent starts in the wrong year of the document.
2. **`uncertified-pass` = both bars clear** (`:158`) while `bar_point` is required-unset (`:217-219`). T2 cannot be written.
3. **`status` enum** (`:122`) is `{planned, executed, passed, failed}`. Runtime needs `retired`, `scope-unverified`, `point-leg-unset`.
4. **always_quiet "without any labelling"** (`:237-238`) — refused R1 and R2, still here.
5. **`non_claims` example** (`:117-119`) — still the phrase bypass.
6. **Joshua holds the second key** (`:140-142`) — still theatre next to "bars set before data."

The T4→T6b edge was the example of the class. The class is: **the predicate in the table/header/Depends line that an implementer will copy.** Remaining predicates: `:158` both-bars, `:157` R71 exactly, `:272` dual-is-real, `:129` not-a-hole.

---

## (2) k-drift honesty

You said it now states transcription ≠ labelling. **It does not.** §3 is the v4.1 paragraph. R71 is still claimed by `unpersisted-rate`.

Honest enough *if you add two sentences and delete "exactly" on R71*:

- sha256 + recompute `k` stops editing the numerator on frozen bytes.
- It does not stop the labeller (R71). Gold schema is still unspecified (FP vs TP field).

Until those sentences exist, the plan still implies coverage it lacks.

---

## (3) Point leg UNSET — rigor or evasion

Not cowardice to refuse a number you cannot justify. That was the right move.

**Evasion is keeping the dual-bar story while one leg is off.**

- Interval 0.30 still gates ships. The program can be an **interval-bar program**. Say that.
- `point-leg-unset` in non-claims is a sticker on a phrase list we already know is gameable.
- §4.2 then *uses* 0.20 illustratively to prove "both legs bite different rows… bars are real rather than cosmetic." That paragraph should have been deleted when 0.20 was refused. It is the 4.2-header defect: the demonstration outlived the bar.

`bar-equals-observed` is a real check and only fires when a bar is *set*. Fine. `bar-unset` on a rate row is real. Fine.

**Rule:** `status=passed` requires the **interval** leg only, until Joshua sets `bar_point` in authority *without seeing `k/n`*. Dual is a future. Not a present with a disabled limb.

That is rigor. Dual-plus-unset-plus-illustrative-0.20 is evasion.

---

## (4) Steady state — BEADS-READY?

Skill: ≥4 rounds, then beads, only if self-contained and the last round is marginal.

v4.1→v5.1 is still **structural**: ontology of bars, T6a cost 4h, two conventions, kill wording, two new codes. Not typo-level.

**NOT-YET.** Blocker, one sentence:

> T2 cannot be implemented: `uncertified-pass` demands both bars clear (`:158`) while `bar_point` must be absent (`:217`), T2's code list is eight (`:340`) and §6 plants fifteen (`:429`), and `k` has no gold field.

Secondary, not the blocker: title v4; §4.1(6) missing; 7≠8 rows; T8 still ceremony.

I will accept a v5.2 that only (a) defines `passed` as interval-leg given `point-leg-unset`, (b) puts `bar-unset` / `bar-equals-observed` in T2's list and makes §6's plant count equal that list, (c) replaces §3's "not a hole" with transcription≠R71 and names the gold field. Then beads. Not before.

---

## (5) Question seven — third time, answered as a list

**Adopting on authority** = taken because Jeffrey has it, or because it *looks like* his dual/eval-policy, without a named F1–F6 it closes *here*.

| Item | Fits our F-list? | Adopt? |
|---|---|---|
| Two files + bound-field byte equality | F3 silent widen | **Yes.** Mechanism is the files, not Joshua. |
| Joshua as second key | F3 was same party; he is that party | **No.** Time-freeze bars; steward ≠ scorer. |
| Resolve evidence refs | F1 phantom | **Yes.** |
| `planned/executed/passed/failed` | F1/F6 | **Yes**, once `retired` / `scope-unverified` exist. |
| "Declaration ≠ acceptance" | habitual "verified" | **Yes.** |
| Fixed diagnostic codes | session text in logs | **Yes.** |
| In-tree validators, no CI | our lane | **Yes.** |
| Orphan source→matrix | F6 | **Yes.** T6a cost is now measured. |
| Dual bar 0.90/0.80 *shape* | NEED #6 is the *interval* | **Interval 0.30: yes (ours, preregistered). Point bar: no number. Do not call it dual until a point bar exists.** |
| Method name = his family-iid string | our fires overlap | **No.** `iid_claimed: bool`. |
| ≥3 phrase `non_claims` | does not catch F1/F3; example is the bypass | **No.** Typed fields. |
| `always_quiet` without a 0/1/2 loss | "without labelling" is false | **No** until a loss table. |
| Mutation twins | dead RED arms, empty-scan-set | **Yes.** |
| `label_rows_sha256` + recompute k | F1 tamper | **Yes as checksum. No as R71.** |
| `bar-unset` / `bar-equals-observed` | the 0.20=4/20 we just did | **Yes.** Ours. |
| T1 P1/P2 conventions (headers, `.expect` strings) | none of F1–F6 | **Optional.** Pane 3 completeness, not F-list. Cheap; do not let them block beads. |
| Jev seat | Axis C / R69 | **Already refused. Keep refused.** |

The vacuous dual, then 0.20=4/20, then dual-with-unset plus an illustrative 0.20 table, is one failure: **adopting the shape of a two-legged bar without a second justified number.** That is Q7. It happened three times in this document. Interval-only until Joshua sets a point bar blind to `k/n` is the adoption that fits NEED #6.

---

## Diffs for v5.2 (only what blocks beads)

```diff
-# PLAN v4 … Status: v4, post-review-round-1
+# PLAN v5.1 … Status: post-R4, NOT beads-ready until uncertified-pass matches unset point leg

-Why k is not in that list, and why that is not a hole.
+k-drift closes transcription of k on frozen bytes. It does not catch R71
+(labeller). k = count of gold==FP. unpersisted-rate is R70 (file exists), not R71.

-status = passed ⇒ both bars clear
+status = passed ⇒ interval leg clear. If bar_point absent: require
+point-leg-unset and do not evaluate a point leg. bar-unset if rate exists
+and authority lacks bar_interval.

-Both legs now bite, and they bite different rows — which is the evidence
-the corrected bars are real rather than cosmetic.
+Delete this paragraph. 0.20 is not adopted. The table is historical, interval-leg only.

-eight rate-bearing decisions … five … three
+seven rows. Three ships reversed; two kills refused-as-retired; two relabels refuse.

-T2 implements these eight structural codes
+T2 implements: … + bar-unset + bar-equals-observed.
+§6 plant count = len(T2 list) + T3 remainder, listed once.

-Scope: §4.1(6)
+delete, or write item 6: checksum ≠ labelling oracle
```

Then beads. Not a fifth review round unless v5.2 reintroduces a copy-site in a *predicate*.

---

## Boundary

- Reviewed `931c872` as requested. Workspace `HEAD` is `4215345` (other files); plan log tip is `931c872`.
- Did not re-run Wilson; R2 table still matches.
- Did not edit the plan.
