# MiniWoB Jev v3 receipt

Bead: `jev-9gtw.4`
State: **BLOCKED — no held-out run**.
No v3 held-out bar was scored.

## Design and isolation

The v3 prereg and exact autopsy slice IDs are committed in
`docs/demos/upstream-repro/miniwob-jev-v3-prereg-20260925.md`. The v3 code is behind
`MINIWOB_V3=1`; `MINIWOB_V3_ARM` isolates quoted, date/time, page-text, color, drag, and none arms.
The default (`MINIWOB_V3` unset) preserves v1 behavior. The contaminated rows below were generated
before arm isolation and are retained as evidence, not counted as one-variable dev results.

| Feature arm | Isolated mechanism | Contaminated smoke status |
|---|---|---|
| quoted | quoted terminal punctuation | 1/16 before mechanism fix; 16/16 after quote-normalizer fix; earlier combined-feature rows retained |
| date/time | date/time typability and formatter | initial 5/10; formatter attempts 5/10 and 0/10 when other feature state polluted the arm |
| page-text | visible page/value text options | smoke only; no isolated exact result |
| color | serialized element color | smoke only; no isolated exact result |
| drag | source/target pairs and mouse sequence | smoke only; no isolated exact result |
| none | after-page-change none guard | not scored |

Every contaminated smoke row records resolved model `jev-1.13.0` and remains under
`work/miniwob-jev/rows/miniwob-jev-v3-contaminated-smoke-*.jsonl`. None is used for the combined
held-out bar.

## Harness-bug rows — NOT-SCORED

The following six row files are **NOT-SCORED**. Commit `c7651c4` (`05:35:41Z`) dropped the
`type_spans[r] = ...` assignment in `build_candidates`, so no `type [` candidate was offered.
Commit `afd8a5b` (`07:25:58Z`) restored the assignment. Every run in that window typed 0 times;
these rows are excluded from every arm score and are not evidence about Jev's action selection.

- `miniwob-jev-v3-dev-quoted-isolated-rerun.s0.jsonl`
- `miniwob-jev-v3-dev-quoted-isolated-correct.s0.jsonl`
- `miniwob-jev-v3-dev-date-time-isolated-rerun.s0.jsonl`
- `miniwob-jev-v3-dev-date-time-isolated-correct.s0.jsonl`
- `miniwob-jev-v3-dev-date-time-isolated-rerun2.s0.jsonl`
- `miniwob-jev-v3-dev-date-time-exact-rerun3.s0.jsonl`

The 11 untracked `miniwob-jev-v3-dev-*.jsonl` row copies remain in place as evidence; none was
deleted.

## Security boundary

No further v3 live calls are permitted from this session after an environment propagation check
accidentally emitted the injected TypeSafe API key into captured tool stdout/log. The key value is
not repeated here. An urgent Agent Mail security report requested revocation/rotation. The bead
remains blocked pending that remediation. No held-out seeds 400–404 were run.

## No-claim boundary

The v3 dev data is not a clean six-arm experiment: the initial rows enabled all v3 features, and
later isolated attempts exposed additional harness/model-selection failures. The combined bar is
therefore **NOT SCORED**, not failed. No negative-evidence ruling is added for v3. Retry requires
credential rotation, clean isolated dev re-runs, and a fresh preregistered held-out run.
