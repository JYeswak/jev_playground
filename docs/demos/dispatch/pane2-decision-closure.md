# P2 — build the ruling closure. Queue of 3.

Read `docs/demos/upstream-repro/alignment-operating-model-20260920.md` first. Short version:
`franken_alignment`'s core primitive is the **`DecisionClosure`** — *one* object that is
simultaneously the authorization, the tamper-evident record, the replayable baseline, the
calibration sample, and the regression test.

**We produce all five per ruling, as five hand-maintained artifacts.** That is why `STATUS.tsv`
fell behind three separate times tonight, why a digest pointed at a live file and took the lane
RED, and why the README counts went stale twice. **Every one of those is a consistency failure
between parts of what should be one object.**

## Unit 1 — `work/ruling-closure/emit.mjs`

One JSON per ruling, written at ruling time, carrying:

- `candidate`, `rung`, `verdict`, `author`
- `receipt` path **and** its computed content digest (reuse the `lane-status.sh` normalisation —
  do not invent a second hashing rule)
- `falsifier`: its path, its commit sha, and **whether it fired**
- `inputs`: pinned file(s) + sha, and an `as_of` timestamp for any live-monotonic source
- `guards`: recorded exit codes of `pin-liveness`, `pinned-denominator` where applicable

**Creation Gate, answered in the header, or it does not get built.** The observed defect is the
three same-turn-update failures plus the RED — cite them. Retirement: when `STATUS.tsv` is
generated rather than edited.

## Unit 2 — make `STATUS.tsv` a projection, not a parallel file

`work/ruling-closure/project.mjs` renders the TSV from the closure set. **Do not delete or
rewrite the existing rows** — generate and `diff` against the committed file, and report the
delta. If the projection cannot reproduce the 40 existing rows exactly, **say which rows it
cannot reproduce and why**; that is a finding about our history, not a bug to paper over.

Ship a `scripts/selftest-ruling-closure.sh` (stage 80 discovers it by glob — **no new stage**)
whose arms plant: a closure whose digest disagrees with its receipt, a closure citing a
live-monotonic input with no `as_of`, and a projection that drops a row. Each must FIRE.

## Unit 3 — rung demotion

Today a rung-4 claim stays rung-4 while its inputs rot. The as-of audit proved `78,455` is
unrecoverable and **nothing demoted the claim citing it.** Add the rule: a claim whose cited
input is live-monotonic and whose `as_of` predates its last use is **automatically demoted one
rung** with the reason recorded.

**Measure before wiring**, as with every guard tonight: how many of the 40 current rows would
demote? If it is most of them the rule is too aggressive and you should narrow it or refuse with
R49 and a trigger.

## Explicitly out of scope

Conserved rights, effect gates, one-shot permits, ATP, Z-sets, dominator trees. **We authorize
documents, not irreversible effects** — importing that machinery would be exactly the ceremony
this lane refuses. Do not.

`[receipt]` for result commits. Exit codes unpiped. `scripts/vgrep.sh` for proof-greps. Commit
on create. Finish one, fire its callback, start the next yourself.

`ntm --robot-send=jev --panes=1 --msg="CALLBACK-P2-<UNIT>-<DONE|BLOCKED|REFUSE>: <receipt path> <sha>. NEXT <unit>. NO-CLAIM <limit>."`
