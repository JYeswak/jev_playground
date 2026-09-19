# Integrations — proven vs WIP OMP/Jev seams

This is the user-facing scoreboard for what we have actually wired into OMP, and at which claim level. It is not a roadmap.

**0 promoted.** Re-derive from `docs/demos/STATUS.tsv` (column 4 = `verdict`; rung 5 in the header is `promoted`). No row in that file is `PROMOTED`. The one promotion awarded was retracted the same day when real data arrived (`README.md` Status; `NEGATIVE_EVIDENCE.md` R31). Receipts live under `docs/demos/` and `docs/demos/upstream-repro/`.

Do not read a later rung than the evidence named below. **BUILT ≠ WIRED; WIRED ≠ VALIDATED.**

### How citations work here

If this page mentions `fh`, it is as a *ranker*, not as a citation. `fh doctor` may report STALE
or degraded SCHEDULING (a 1/8 schedule-declaration miss does not retract shipped doctrine).
Corpus citations already in this repo were opened at file:line from the pinned Dicklesworthstone
mirror after `fh` ranked them — `asupersync` `eprocess.rs:224-238`, `franken_ocr`
`RATCHET.md:33-51`, `franken_engine` `promotion_gate_runner.rs:266-328`, `frankensearch`
`perf_ratchet.rs:732-740`. Pattern: **fh ranked, we opened.** A ranking alone is not a citation.

## Proven: `jev-compact` — L3 measurement instrument

| | |
|---|---|
| **What it is** | A `session_before_compact` hook that asks Jev keep/drop questions about the prefix omp has already decided to summarize, then **logs the verdict**. |
| **What it is not** | A pruner. It does not shrink the session. omp's own summarizer keeps the job. |
| **Claim level** | **L3** — the seam fires in a real omp session, and a known-bad envelope makes it refuse. **L4 is not reached and is not reachable on this seam** as Jev-pruning. |
| **Install** | `compaction/install-jev-compact.sh` |
| **Skill** | `.omp/skills/jev-compact/SKILL.md` |

### The load-bearing facts, with file:line

- The handler **only ever returns `undefined`**. A compact verdict is logged as `would-compact` and yielded; omp's summarizer does the actual compact. See `compaction/src/omp-hook.ts:217-222` and `compaction/src/omp-binding.ts:173-182`.
- The installer itself says what it verifies and what it never claims: placement plus dependency resolution, **not** firing (`compaction/install-jev-compact.sh:16-17`).
- The deployed entry is the same three-line wrapper: `compaction/deploy/hook-entry.ts:7-9`.
- Fail-open / fail-safe direction: every path yields. A missing key registers **nothing** (`compaction/src/omp-binding.ts:226-231`). A Jev outage, a malformed envelope, or a below-minimum reduction costs a missed optimisation, never context (`compaction/src/omp-hook.ts:93-97`).
- **Never claim a session was shrunk by this hook.** Stated in the skill (`.omp/skills/jev-compact/SKILL.md:19-21`) and in the live receipt (`docs/demos/omp-seam-live-20260918.md:104-108`). Replay-harness reductions (library over a transcript) are a different claim from a live `/compact`.
- Why L4-as-Jev-pruning is refused: omp consumes a fromHook result as `{summary, firstKeptEntryId, ...}`, not a pruned-message list. Jev judges; it does not write the required `summary` string. `NEGATIVE_EVIDENCE.md` R21 (`:780-783`) and `docs/demos/omp-seam-fqo-20260919.md:42-43`.

### How to see that it fired

```bash
./compaction/install-jev-compact.sh /path/to/your/repo
# restart that repo's omp session WITH TYPESAFE_API_KEY
# run /compact, then:
tail ~/.jev-compact.log
```

`refused` / `passthrough` / `would-compact` are decisions. No new line means the hook did not run — not a silent success.

## WIP: observe-and-log / dogfood logger — UNRUN, shippable after checks

The append-only decision/outcome logger lives at `work/dogfood-logger/`. Its schema, join, concurrent appends, and rotation are tested locally (`work/dogfood-logger/test/logger.test.mjs`; receipt `docs/demos/upstream-repro/dogfood-logger-20260919.md`).

**State today: UNRUN.** No live omp profile has this registered. That is a measured fact (`docs/demos/upstream-repro/dogfood-logger-20260919.md:57-58`), not a standing ban on live omp and not a quiet-window gate. Joshua did not take live omp off the table.

**Stop-before-register is the engineering gate, not a deferral.** A `tool_call` observer on `bash` would fire on every bash in every session, so the act has preconditions. They are:

1. **Offline proof first** — writer tests green; a synthetic `tool_call` proves the handler returns `undefined` on success, error, and timeout.
2. **Fail-open** — logger/observer failures return `false` / `undefined` and never throw into the host (`work/dogfood-logger/src/logger.mjs`; `compaction/src/omp-binding.ts:226-231`).
3. **`0 block:true`** — observe only. Never return omp's `{block: true, reason}` shape.
4. **jsm preconditions before the act** — the installed file must be self-contained. `9e6c88d` imported `../../dogfood-logger/src/logger.mjs`, a parent path that does not exist after a copy into `~/.omp`. `348894e` inlined the record builder so the extension no longer depends on a repo-relative parent. That defect is why stop-before-register earned its keep as a *check*.

Once those pass, observe-and-log is shippable to live omp. The path that earns a later fire is the improvement loop: carve the cases regex cannot express, tighten criteria, re-measure against the dcg prior — not an indefinite DEFER.

There is no dogfood or observer file under `.omp/hooks/` on this tip. The only pre-hook in this tree is `jev-compact`. This page does not give a register-now command.

**Where a probabilistic judge belongs.** Only on what regex cannot express. The receipt that states the prior — `docs/demos/upstream-repro/dcg-block-rate-prior-20260919.md` — landed on `origin/main` (`9e6c88d`) after this branch forked (`d6b52ea`). **It is not on this tip.** Numbers from that file will be linked on the next tip sync rather than restated here.

## Scoreboard

| Surface | State | Claim | Promoted? |
|---|---|---|---|
| `jev-compact` / `install-jev-compact.sh` | ships; fires in real `/compact` | L3 measurement; does **not** prune | no |
| dogfood / observe-and-log logger | library + tests; **UNRUN** | shippable after the four checks above | no |
| STATUS ledger (`docs/demos/STATUS.tsv`) | 0 `PROMOTED` rows | rulings, not products | **0** |

Further receipts: `docs/demos/omp-seam-live-20260918.md`, `docs/demos/omp-seam-fqo-20260919.md`, `docs/demos/upstream-repro/dogfood-logger-20260919.md`, `docs/demos/STATUS.tsv`, `NEGATIVE_EVIDENCE.md` R21 / R31. dcg prior: pending next tip sync (`dcg-block-rate-prior-20260919.md` on `origin/main`, not this tip).
