# PREREG — outcome census on 4 remaining classes (no bead, conductor order)

Frozen 2026-10-02 before any label. Census top-3 (destructive/instruction/
failed_ignored) already have programs; double_read stays out per order. For
each class below: random 50 instances, blind-label HARMFUL OUTCOME (wasted
tokens/time or a wrong action — NOT mere occurrence), report harmful/week
with Wilson CI on the harmful fraction scaled by the census class count.
Only classes with real harm go forward.

## HARMFUL rules (fixed pre-label, judgment disclosed)

- skill_abandoned: HARMFUL iff the loaded skill body >= 2KB AND no reference
  to it in the next 5 turns (material tokens burned for nothing). Else NOT.
- long_unref: HARMFUL iff result >= 20KB AND probe unreferenced (material
  context bloat). 10-20KB unreferenced = NOT (below materiality).
- test_rerun: HARMFUL iff a FULL-suite rerun (no -k/filter/single-target) with
  no code change between runs. Targeted reruns = NOT (cheap, often necessary).
- memory: HARMFUL iff memory block >= 3KB present with zero lexical use in the
  next 3 turns. Else NOT.
## Math

harmful/week = (k/50) x N_class, N from the committed census rerun
(destructive 133/instruction 468/failed 3606/test 790/memory 619/long 892/
double 530/skill 213 over 139,143 turns). CI = Wilson(k, 50) endpoints x N.
Seed 20261005. No live calls (keyless); scorer + instances + labels committed.
