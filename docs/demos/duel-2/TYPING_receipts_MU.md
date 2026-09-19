# Q68 — Receipt typing for all 17 STATUS.tsv rows (opened, not filename-guessed)

**Discriminator rule (applied uniformly):** type by the receipt's PRIMARY speech act —
measurement emits numbers against thresholds; score emits grades; verdict rules on standing;
hold-resolution disposes a hold; anything else (design, mapping) is `other`.
Where a receipt carries two (grades + kill language, numbers + verdict field), the discriminator
names which dominates content and why. Ambiguous → `other` with reason; three landed there.

| # | Candidate | Receipt (col 6) | Type | Discriminator |
|---|---|---|---|---|
| 1 | demo-1 | `demos/routing-backtest/runs/backtest-real-excerpt.json` | measurement | emits totals/turns/priceTable only; no actor, verdict, or grade keys anywhere in the object |
| 2 | demo-2 | `HELD_demo2_demand_COD.md` | hold-resolution | status line is a hold disposition (RECOVERED from hold); score explicitly UNCHANGED (700 stated, not set) — the filename matches score patterns for the wrong reason, as briefed |
| 3 | demo-3 | `BASELINE_claimcheck_vs_jev_COD.md` | other (design) | status line: "comparison design, not implementation or benchmark result"; zero measurements, grades, or rulings inside |
| 4 | demo-4 | `SUPERSESSION_MU_argues_COD-H1.md` | verdict | concludes with a standing ruling (own pick yields slot to COD-H1), against interest; score discussion is evidence for the ruling, not the act |
| 5 | demo-5 | `RUNG2_JEV_SHAPE_COD.md` | verdict | emits per-candidate rung-2 gate verdicts (CLEARED table); structural reasoning is the brief for those verdicts |
| 6 | demo-6 | `HELD_demo6_incumbent_COD.md` | hold-resolution | status "HELD, not ruled out" + incumbent-search disposition; states what would move it, rules nothing out |
| 7 | demo-7 | `demo7-weights-20260918T041352Z.json` | measurement | status MEASURED; verdict field (MULTI) answers the pre-registered weight rule — a measured readout, not a gate ruling; numbers dominate content. Boundary call, stated. |
| 8 | demo-8 | `DEMAND_SCORES_COD_ON_MU.md` | score | emits numeric grades per candidate (120/150→100 table); "100 and kill" rides on the grades. Boundary call vs verdict: grades dominate content. |
| 9 | demo-9 | `HELD_demo9_build_or_skip_COD.md` | hold-resolution | status SKIP/HOLD; build-or-skip decision with the condition that would lift it |
| 10 | COD-H1 | `codh41-labelfree-20260918T054800Z.json` | measurement | reports executed label-free halves (file counts, transcript shapes) against pre-registered thresholds; UNASKABLEs are measurement outcomes, not rulings; no verdict keys in object |
| 11 | COD-H2 | `label-id-mapping-20260918T073641Z.json` | other (mapping) | relates two label sets under canonical keys with verification counts; asserts no score, hold, verdict, or new measurement |
| 12 | COD-H3 | `RUNG2_COD-H3_resolved_MU.md` | verdict | decisive RULED_OUT ruling with retry tracks; decomposition is the brief |
| 13 | COD-H4 | same file as 10 | measurement | same object, same discriminator (shared receipt, one typing) |
| 14 | COD-H5 | `RUNG2_COD-H5_owned_MU.md` | verdict | rules distinctness (DIFFERENT PRODUCTS, tester-to-subject); source comparison is the brief; no numbers measured |
| 15 | MU-H1 | `muh1-marker-census-20260918T034820Z.json` | measurement | census counts (17/283786 KLOC) primary; DENOMINATOR_TOO_THIN is a threshold outcome, not a standing ruling (the ruling lives in PLAN §3l). Boundary call, stated. |
| 16 | MU-H2 | `BASELINE_MU-H2_vs_incumbents_COD.md` | other (design) | status: "baseline design. No implementation or benchmark was run"; same discriminator as 3 |
| 17 | MU-H3 | `RUNG2_MU-H3_entropy_COD.md` | measurement | deterministic sentinel run reporting threshold-table numbers; "no Jev call, no key, no real secret" |

**Distribution:** measurement 6 · hold-resolution 3 · verdict 4 · score 1 · **other 3**.

**What `other` says about the enum (finding, not failure):** 3/17 (18%) — two designs and one
mapping. The vocabulary has no design/proposal type and no derivation/mapping type, so exactly the
artifacts that *set up* future measurements fall outside it. If `other` grows past this, the enum
needs a `design` value; at 3, the honest reading is that falsification pipelines produce
scaffolding the verdict-centric enum never named. Pane 2 owns the enum; the gap is tabled with
evidence either way.
