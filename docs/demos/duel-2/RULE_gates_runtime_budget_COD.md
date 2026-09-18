# Q93 Rule: Foundation Gate Runtime Budget

## Measurements

Three normal and three selftest runs were requested from `foundation/gates.sh`.

### Normal mode

- run 1: `9.99s`, stage 80 `5s`;
- run 2: `9.16s`, stage 80 `4s`;
- run 3: **UNMEASURED** — the shared `foundation/gates.sh` changed during the run and produced a shell syntax error after stage 80. This is a shared-worktree mutation, not a valid runtime sample.

Stable normal totals: `9.16–9.99s`.

### Selftest mode

- run 1: `12.38s`, stage 80 `5s`;
- run 2: `12.47s`, stage 80 `6s`;
- run 3: `11.86s`, stage 80 `5s`.

Stable selftest totals: `11.86–12.47s`.

### Stage share

Stage 80 (`80-lane-instrument-selftests.sh`) consumed approximately:

- normal: `4–5s`, approximately `44–50%` of total;
- selftest: `5–6s`, approximately `40–48%` of total.

It is the slowest stage and the dominant local cost, but the aggregate is well below the proposed 30-second ceiling.

## Decision

The Q91 condition holds **today**:

- keep the stage in the default foundation run while stable total runtime remains below `30s`;
- keep stage 80 in the default run while its stable runtime remains below `10s` and does not exceed approximately half of total runtime for two consecutive stable samples;
- split stage 80 out of the default run rather than deleting coverage when either budget is exceeded.

The 30-second bound is meaningful because it is the operator's wait budget for a routine suite run, not a decorative performance number. The stage-specific bound catches glob-driven growth before the aggregate reaches 30 seconds.

A run that mutates its own script or another shared input during measurement is **UNMEASURED**, not a slow or fast sample. Record the changed path and repeat from a stable tree; do not average the syntax-error run into the budget.

## Re-examination condition

Re-examine this rule when:

- three consecutive stable normal runs have a p95/maximum above `30s`;
- stage 80 exceeds `10s` in two consecutive stable runs;
- stage 80 exceeds half of total runtime in two consecutive stable runs;
- a new selftest is added through the glob and changes the stage's cost materially;
- operators stop running the default suite because the wait is operationally painful;
- the suite gains parallel execution or a snapshot boundary that changes what the timing measures.

The measurement receipt must always report per-stage duration, total duration, mode, stable/unstable status, and the exact stage glob. A green result without those fields is not a budget observation.

## Scope

Current evidence supports keeping the default run: stable normal totals are about 9–10 seconds and stable selftests about 12 seconds. This is a runtime guard, not permission to wire the suite to the commit hook or to ignore shared-worktree mutation.
