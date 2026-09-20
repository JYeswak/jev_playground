# P3 — Can anything ever promote? Adversarial test of the promotion contract

`promoted = 0` across **38 rulings**. I have been reporting that number all night as evidence of
honesty. It has an equally consistent alternative reading: **the bar is impossible, and the gate
is theatre that can never fire.** I authored `foundation/gates.d/85-promotion-contract.sh`, so I
am the wrong person to settle this.

An unfalsifiable gate and a strict gate produce identical logs. Only a **planted deserving
candidate** tells them apart.

## The unit

1. **Read the contract.** `foundation/gates.d/85-promotion-contract.sh` (4 gates, 3 planted
   arms) plus the promotion criteria in `docs/demos/PLAN.md` and the `STATUS.tsv` schema.
   Write down, in your own words, **the exact conjunction a candidate must satisfy to promote.**

2. **Construct the strongest possible deserving candidate** — a synthetic row plus whatever
   receipt it requires. Not a real ruling; a fabricated best case. Give it everything: a
   large effect, a named subset that does not collapse, a non-author concurrence, a committed
   falsifier, an existing integrity-checked receipt.

3. **Run the gate on it.** Does it promote?
   - **If YES** → the gate is strict but satisfiable. Record exactly what it took. That list is
     the lane's actual promotion recipe and we have never written it down.
   - **If NO** → find which clause blocks it and decide: is that clause *right* (our candidates
     genuinely fall short) or *unsatisfiable by construction* (e.g. it requires a field nothing
     can produce, or two clauses contradict)? **An unsatisfiable clause is a defect and I want
     it named.**

4. **Then the honest half:** take the **closest real candidate** we actually have — my read is
   `UP-R14-route-multiturn-labels` (HELD: beats its constant, fails the trap subset) or the
   score-register work — and compute **precisely how far short it falls**. One clause? Three?
   That distance is the answer to "is promoted=0 honest or vacuous".

## Do not

- Do not weaken the gate to make something pass. If the bar is right and nothing meets it, the
  finding is *"the bar is right and nothing meets it"* and that is a good outcome.
- Do not promote a real candidate. This is a test on synthetic input; `STATUS.tsv` is untouched.
- Do not add a gate arm — instruments are frozen. You may add a **planted-candidate fixture**
  under `foundation/gates.d/fixtures/` only if the gate already reads that directory.

## ACCEPTANCE

A receipt at `docs/demos/upstream-repro/promotion-satisfiability-20260920.md` containing: the
conjunction in plain words; the synthetic candidate; the gate's verdict on it with quoted output;
and one ruling — **SATISFIABLE** (with the recipe) or **UNSATISFIABLE** (with the blocking clause
and whether it is a defect). Plus the distance measurement for the closest real candidate.

Exit codes unpiped. Commit on create. Test file and `TESTS.md` entry in the same commit if you
add one.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-PROMOTE-<SATISFIABLE|UNSATISFIABLE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
