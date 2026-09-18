# DISPATCH — pane 2 · three demo contracts at measured depth · 3 units

Demo-1 is **shipped** on your work: clean clone → `install.sh` → documented fixture command →
1 session / 6 turns / **6 classifiable** (matching the manifest's claim exactly, after you defined
"turn" once as a marker pair) / 0 skipped, 5 cheap candidates, **no verdict string**, and **both**
RED arms passing — floor and missing-price. Gates ALL GREEN. All four PLAN.md artifacts exist and a
non-author clean-clone run confirms the install.

**New direction from Joshua: mirror the depth and lengths Jeff actually uses.** We measured his
plan→bead transformation today and the numbers changed what "a bead" means here:

```
his plan  COMPREHENSIVE_PLAN_TO_DESIGN_SKILLRANKER.md ...  191,829 bytes  1,367 lines
his bead text TOTAL ................................... 1,725,754 bytes  195 beads
                                                          = 6.34x the plans
plan sentences appearing VERBATIM inside beads ........ 1,125 / 1,138 = 98.9%
mean number of beads each plan sentence appears in .... 5.35   (max 17)
```

He does **not** partition the plan across beads. He copies each requirement, word for word, into
**every bead that touches it** — mean 5.35 copies. That redundancy is the whole point: an
implementer reading one bead has the complete contract and never opens the plan.

**Read first, in full:**
- `/Users/josh/Developer/jev/docs/demos/BEAD-TEMPLATE.md` — his five sections with per-section
  adoption across all 195 beads, the derived depth targets, and six anti-patterns measured here.
- `/Users/josh/Developer/jev/docs/demos/PLAN.md` — §0 is the guardrail block you embed **verbatim**;
  §5.5, §5.7 and §5.9 are the epic-scale contracts you are expanding.
- `/Users/josh/Developer/jev/docs/demos/contracts/demo-2-admission-screen.md` (14,868 chars) as a
  worked example of the target shape — pane 3 wrote three of these at 13–15 KB each.

**Target: ≥7,000 chars each**, his median. Write markdown files, **not beads** — emission is gated
on plan steady-state because a bead graph inherits every structural error in its source.

---

## UNIT 1 — `docs/demos/contracts/demo-5-fact-ledger.md` (≥7,000 chars)

Source: `PLAN.md` §5.5. Mean 792.5, and it has the **widest grader spread in the duel** (740 → 845).

Facts the contract must carry, all measured:
- **Its premise got STRONGER from the evidence that refuted its comparison.** Arm A (Jev-prune)
  scored **1/3 in all three runs across two corpora**. Pruning robustly drops answer-bearing facts.
  That is the problem this demo exists to solve and it is the lane's one supported compaction
  finding.
- **Mechanism, stage by stage, because the first version hid a stage:** deterministic extractor →
  **Choice** over candidate lines → **Noul** verbatim verification. *A Noul judges; it does not
  extract.* A paraphrase in a fact ledger is the failure mode, so shipping one must be
  structurally impossible — specify the byte-identity assertion against `sourceMessageId` spans.
- **Threshold is 3/3 ABSOLUTE.** Never "beat arm B": arm B scores **3, 1, 3** on a byte-identical
  fixture, so a demo pinned to it could pass by standing still on a bad roll. A stochastic baseline
  is not a threshold (R11).
- **The 105-point spread is explained, not noise.** 740 was scored *before* the mechanism was
  named, 845 *after*; grader means differ by only 6 points, so the gap is the repair.

RED arms: answer-bearing line present but omitted from the ledger ⇒ recall question fails and the
harness reports the miss; a ledger `quote` not byte-identical to its source span ⇒ **refuse**.

## UNIT 2 — `docs/demos/contracts/demo-7-signals-starter.md` (≥7,000 chars)

Source: `PLAN.md` §5.7. Mean 712.5, 4 graders — lowest of the converged demos.

Facts the contract must carry:
- It packages the lane's central lesson: verdict-only **62.6%** vs five signal questions +
  logistic regression **95.1%** on `jev-phishing-bench@1d56e8c` — a **32.5-point** delta. Quote both
  endpoints, never the rounded difference; the delta *is* the claim.
- Ships a **fixed-rule floor** (best single rule alone) and a **verdict-only baseline that must
  lose**, so the thesis is falsifiable and the template checks itself.
- **ITS ORIGINAL GATE IS INVALIDATED AND YOU ARE REWRITING IT.** The proposal said "apply only once
  A/B receipts accumulate past N≥50 — today N=4". R11 then showed arm B is nondeterministic, so 50
  receipts of a coin-flip arm would fit a model on noise and call it calibration. **The gate must
  become a property: N≥50 from a pinned generator (fixed model, fixed temperature, fixed seed if
  exposed), or a published distribution with spread.** A sample-count threshold over an unpinned
  generator is the same error class as pinning a threshold to a stochastic baseline. Put that
  reasoning in the contract — it is the most transferable thing in the demo.
- Calibration output: accuracy, AUROC, ECE with bins, flip rates between passes. Our existing
  baseline is ECE 0.061 / Brier 0.020 from `foundation/runs/20260917T224444Z.json`.

RED arms: shuffled labels ⇒ "no signal found", nonzero exit, **never** a fitted model; empty corpus
⇒ ERROR; the shipped synthetic example reproduces its committed report within tolerance.

## UNIT 3 — `docs/demos/contracts/demo-9-review-signal.md` (≥7,000 chars)

Source: `PLAN.md` §5.9. **UNSCORED** — admitted by ruling, not by rank.

Facts the contract must carry:
- **You found this**, in `WIZARD_BLINDSPOTS_COD.md` (`210704f`): usage map §5,
  `jev-review@57690af`, a continuous review signal alongside `ubs` — the thing neither duelist
  proposed. I read it, acknowledged it in chat, and **failed to carry it into the plan**; a later
  audit caught the omission. Record that provenance in the contract.
- **It is distinct from demos 3 and 6.** They check *claims against cited artifacts*; this scores
  *code* on dimensions a linter structurally cannot see. Different input, different oracle.
- **The surface exists and has a measured baseline**: your own R6 pass ran `ubs` over the four
  first-party TS files — 1 critical / 6 warnings / 27 info, every finding classified non-defect,
  with an `eval()` positive control proving the scanner fires. That baseline is what a complementary
  signal must be judged against: **it fails if its findings are a subset of what `ubs` already
  reports.**
- **Advisory, never blocking**, until a false-positive rate is published — same constraint as
  demo-2, and `GATES.md` rule 3 binds it (silent on the healthy path).
- **It has ZERO grader scores.** Its position behind demo-3 is a conductor judgment, not a measured
  rank. State that it must be scored by two non-authors before it is built — and you cannot be one
  of them, because you proposed it.

---

## REPLY-VIA — FOUR legs, leg 1 first, per unit

1. **`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-DONE: <full path> <sha>. chars=<N>. NEXT <unit>. NO-CLAIM <limit>."`** — include the **character count**; depth is the acceptance.
2. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
3. `am mail send --project ~/Developer/jev --from <YOU> --to CyanFalcon -s "[jev-demo-loop-a1q] <OUTCOME>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
4. Committed file, own files only, `[pending]` in the subject — these are specifications, nothing is run.

## NON-GOALS

Do not create beads. Do not edit `PLAN.md`, `BEAD-TEMPLATE.md`, or a contract file assigned to
pane 3 (`demo-2`, `demo-3`, `demo-4`). Do not pad: a 7 KB contract that repeats itself is worse
than a 3 KB one that is complete. Reach depth by answering every question an implementer would
otherwise have to ask a human.
