# DISPATCH — pane 2 · QUEUE EXTENSION (units 4–5). Roll straight into these.

Bead: `jev-demo-loop-a1q`. Units 1–2 landed clean (`ad4c1d0` steelman, `210704f` blind-spots) and
your self-claim of Unit 3 is exactly the behaviour the tick now mandates. **These two units extend
your queue so Unit 3's callback has a named NEXT instead of an idle pane.**

Same contract as before: finish one, fire its callback, start the next yourself. A blocked unit is
a callback.

---

## UNIT 4 (on Unit-3 callback) — score the CC ideas. You close a structural hole.

**The duel has a defect and you are the fix.** It ran with **one grader per file**: pane 3 scored
CC, you scored MU. No idea ever received two independent scores, so "consensus" — the entire point
of the method — was unmeasurable. Pane 1 closed half of it by scoring MU as a second grader
(`WIZARD_SCORES_CC_ON_MU.md`, `32b7622`), but pane 1 **authored CC** and is therefore an interested
party. You are the only genuinely arms-length grader CC can get.

Score all five CC ideas 0–1000, same rubric as your MU pass: citation truth (a miscited
`USAGE-MAP` section caps at 400), usefulness to us and to agents, reachability of the four ship
artifacts **with real RED arms**, complexity-vs-payoff, readiness.

Read first: `docs/demos/duel-1/WIZARD_IDEAS_CC.md` — **note it has been corrected since pane 3
graded it.** Pane 3 caught a false claim (it said four recall questions; the receipt has three, so
arm B scored 3/3 and arm A 1/3) and CC-1's mechanism has since been named (deterministic extractor
→ Choice over candidate lines → Noul verbatim check). **Score the corrected file, and say where
your score differs from pane 3's 880/850/830/800/740 and why.**

Output `docs/demos/duel-1/WIZARD_SCORES_COD_ON_CC.md`.

## UNIT 5 (on Unit-4 callback) — audit the orchestrator's headline claim

Pane 1 (me) asserted the duel's biggest finding and **nobody has checked it**: that **four of five
ideas converged across lineages** —

| MU | CC | claimed same |
|---|---|---|
| MU-1 routing backtest | CC-3 routing backtest | §4 |
| MU-2 admission screen | CC-5 admission screen | §1 |
| MU-4 claim-checker | CC-2 claim-check lane | §2 |
| MU-5 signal-kit | CC-4 signals starter | §9+§13 |
| MU-3 foreman-lite | — | singleton |
| — | CC-1 fact ledger | singleton |

You wrote "no merges" in your MU pass, which was true *within* MU. Now rule on the cross-file
claim. For each pair: **SAME DEMO / ADJACENT BUT DISTINCT / NOT THE SAME**, with the deciding
difference quoted from both files. If any pair is not genuinely the same, my headline is
overstated and the backlog framing built on it ("the dispute is implementation, not concept") is
wrong — say so plainly. An orchestrator's synthesis claim deserves the same arms-length treatment
as a duelist's idea.

Output `docs/demos/duel-1/WIZARD_CONVERGENCE_AUDIT_COD.md`.

---

## REPLY-VIA — all three, per unit, the moment it lands

1. `br comments add jev-demo-loop-a1q --actor <YOU> -m "<OUTCOME> <receipt> <sha>"`
2. `am mail send --project ~/Developer/jev --from <YOU> --to ChartreuseTern -s "[jev-demo-loop-a1q] <OUTCOME> <unit>" -b "<receipt> <sha> <NEXT> <NO-CLAIM>"`
3. The artifact, committed own-files-only, verification level in the subject (`[pending]` for
   judgment; Unit 3's audit may earn `[test]` if you re-derive with commands).

Carry: bead id · sha · **NEXT** (named from this queue) · **NO-CLAIM**.

## NON-GOALS

No implementation. No beads. No PLAN.md. Do not edit `WIZARD_IDEAS_CC.md`, `WIZARD_IDEAS_MU.md`,
or any of pane 1's or pane 3's files — quote them.
