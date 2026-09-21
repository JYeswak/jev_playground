# PLAN REVIEW R5 — confirming v7 @ `b34d3f8`

Grok. Round 5. **NOT-YET.** Diffs got smaller. The count is still wrong. No beads. No plan edit.

Three R4 blockers were: (1) `uncertified-pass` vs unset point, (2) plant count = table, (3) gold field in authority.

---

## (a) Three blockers — closed or reworded

**1. `uncertified-pass` interval-only — table cell closed; copy-sites not.**

`:159` is the real check: `status=passed` ⇒ interval leg; point only if `point_leg ≠ "unset"`. That is implementable.

Then `:176-177` still says *"cannot say passed while **either leg** of its bar fails."* That is both-legs. `:266-271` still scores an illustrative `bar_point=0.20`. `:284-289` still *"Both legs now bite… evidence the corrected bars are real."* R4 asked that paragraph deleted. It survived.

T2 can be written from `:159`. An agent who copies `:176` or §4.2 will not. **Predicate copy-site. Not closed.**

**2. Sixteen as single source of truth — false.**

I counted the §4 table (`:153-169`): **17 codes.**

```
boundary-coverage, authority-<field>, unresolved-evidence, orphan-case,
missing-red-arm, unpersisted-rate, uncertified-pass, bar-unset,
bar-equals-observed, iid-unsupported, missing-typed-caveat, control-not-beaten,
no-mutation-twin, k-drift, scope-disagreement, uncovered-bead, simulated-platform
```

Arithmetic they published (`:171-174`): 13 T2 + 1 orphan + 2 runtime = 16. 17 − 1 − 2 = **14** T2-class, not 13.

T2 (`:352-358`) then **names eight** codes and a "remaining five" that still includes `unstated-assumption` and `missing-non-claims` — **neither is in the table**. T2 acceptance still *"each of the **eight** fires."*

§6 (`:440-442`) plants **sixteen**. Table has **seventeen**. The SSoT they declared is not the table. **Not closed.** This is the same blocker as R4, with a new wrong integer.

**3. `k_gold` in authority — landed, residual on recompute.**

Bound set (`:125-127`) includes `k_gold`. Schema (`:114-115`) says authority count; matrix `k` must match recompute. Honesty (`:136-143`) now states transcription ≠ R71. That paragraph **did** land this time.

Still unspecified: **which field** on a label row is gold (FP vs TP). Without it T2 `k-drift` is a guess. Residual, not the blocker. Blocker 3 is close enough to call closed if 2 weren't open.

---

## (b) Silent-loss sweep v5 → v7 (copy-site as deletion)

Table codes, `git show` each rev:

| rev | n | lost vs prior |
|---|---:|---|
| v5 `c53e71b` | 14 | — |
| v5.1 `931c872` | 14 | none |
| v6 `2ef6bf3` | 14 | none |
| v7 `b34d3f8` | **17** | **`unstated-assumption`, `missing-non-claims`** (replaced, not restored under old names) |

`scope-disagreement` and `uncovered-bead` are in **every** table v5–v7. They were not silently dropped from the table. If they vanished, it was from a T2 *list*, which v7 still treats as an eight-code implementer surface.

**Fifth form, this round:** v7 *added* five table codes (`bar-unset`, `bar-equals-observed`, `iid-unsupported`, `missing-typed-caveat`, `simulated-platform`) and **did not add them to T2**. The T2 name-list is v6's eight + v6's remaining five (dead names). New codes exist only in the table. An agent implementing T2 from the T2 paragraph never writes `bar-equals-observed`. Deletion by omission of the *new* set.

Other leftovers of refused text (not table-drops):

- Title `:1-3` still `PLAN v4` / `post-review-round-1`.
- T5 `:373-376` still *"bars… move only by Joshua's edit"* after `:129-134` refused Joshua-as-key.
- `unpersisted-rate` `:158` still **R70/R71 exactly** after `:141` says R71 would not have been caught.
- Duplicate `label_rows` in the schema example (`:103` and `:112`).
- `:301` still cites `unstated-assumption` (deleted from table).
- §4.1(2)–(3) still describe the phrase-method and phrase-non-claims that §3 replaced.

---

## (c) BEADS-READY?

**NOT-YET.**

Not because the diff is large. Because the claimed machine count is 16 and the table is 17, and T2's named list is 8. A fresh agent cannot implement T2. That was the R4 blocker. It is still the blocker.

v7.1 that I would accept without another review round:

1. Count the table in the file. Put that integer in `:171` and in §6. No other integer for codes.
2. T2's name-list = table minus `orphan-case` minus the two runtime codes. Delete `unstated-assumption` / `missing-non-claims` from T2. Acceptance plant count = that list's length.
3. Delete `:176-177` "either leg" and `:284-289` "both legs bite… bars are real." `uncertified-pass` has one sentence: `:159`.
4. `unpersisted-rate` prevents R70 only. T5 "Joshua's edit" → time-freeze as in `:132`.

I will not grant BEADS-READY because the dual-bar story is tired and the remaining issues look small. The count is a load-bearing claim. It is wrong.

---

## Boundary

- Counted table rows on `b34d3f8` working tree (= HEAD).
- Did not re-derive Wilson.
- Did not edit the plan.
