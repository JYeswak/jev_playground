# Unit 3: REFUSAL — the commit-msg hook is not built (2026-09-19)

Trigger, per the creation gate: Unit 2 (`docs/demos/upstream-repro/commit-judge-31-20260919.md`,
31 real commits, live) returned DEGENERATE / WEAK / WEAK — no question beats its own
constant, and the judge missed the one real omission (48eecdf: describes 0.78,
omits 0.49) while firing fourteen overstates false positives on accurate messages.
A warn-on-every-commit gate with a 14/31 FP rate on our own traffic is nagware, and
nagware gets uninstalled — a worse outcome than no gate.

What would reverse this refusal: a question set that (a) beats its own constant on
real commits, (b) catches 48eecdf-class omissions above threshold, and (c) fires
overstates below a 10% FP rate on receipt traffic. Re-run Unit 2's scorer; if all
three hold, build the warn-only hook then. Until that run exists, this refusal stands
and Unit 3 must not be re-proposed as "wire it anyway, observe-only".
