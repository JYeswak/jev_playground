# Honesty window classification: b801c10 back through c3adddf

## Ruling

The strict classification is correct:

- **USER: 4** — `bc3d32c`, `cadc655`, `37b1783`, `6fca097` — public README changes a stranger can consume.
- **ENABLER: 1** — `b801c10` — fail-closed hook behavior that protects future work.
- **PROCESS: 0 under the refined rubric** — no commit in this exact window is only an internal audit/ruling once upstream evidence is split out.
- **UPSTREAM_EVIDENCE: 7** — `4d30338`, `43a1db7`, `4c14d25`, `7df1c46`, `d1c24b2`, `ce44f9d`, `c3adddf`.

The previous three-bucket result `USER 4 / ENABLER 1 / PROCESS 7` was directionally
honest but collapsed external research into internal process.

## Why upstream evidence is a fourth bucket

An upstream receipt answers a different consumer question from a process receipt:

- **PROCESS**: did this lane coordinate, audit, gate, or classify its own work?
- **UPSTREAM_EVIDENCE**: what does an external repository or published benchmark actually
  reproduce, and where does its claim break?
- **USER**: can a stranger use the shipped tool or public explanation directly?
- **ENABLER**: does the mechanism make a USER artifact safer or more reproducible without
  itself being the user-facing answer?

The seven upstream commits are not mere internal process. They measure other people's
software and are valuable evidence. They are not automatically USER work, either: a receipt
or reproduction report becomes USER only when it is promoted into a stranger-consumable
surface with a clear consumer path, not merely because an outsider could read its JSON.

The two strongest candidates for promotion are `ce44f9d` (jev-benchmark limit) and `7df1c46`
(criteria inversion). Their current artifacts remain upstream evidence; a linked public guide,
decision surface, or executable reproduction would be the promotion event.

## Count outcome

USER is **not** a plurality. The window does not satisfy the first USER-plurality condition;
DRIFTING remains. The next block should produce a product artifact, not another receipt-only
research unit.

## Misclassification

No commit is misfiled under the strict four-bucket rule. The error was the missing bucket:
counting all seven upstream receipts as PROCESS made the classification less informative; counting
them as USER would overstate product shipping.
