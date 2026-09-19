# Reproduction: bicameral System-1/System-2 split, run here

Pane 3 (muse), 2026-09-18. Vendored clone `upstream/AbdelStark/bicameral` at
pinned SHA — read and executed only, never edited (worktree verified clean).

## What was run

```bash
pnpm install                 # deps only; lockfile untouched
pnpm test                    # 13 files, 41 tests, ALL PASS, zero key, zero network
```

Backend test (`typesafe-backend.test.ts`) injects a stub fetch — the suite never
touches the live API. No keyed path was exercised (nothing in the suite needs one).

## Is their split the one our lane assumes?

Top level, yes: System 2 (the pi coding agent) writes code; System 1 judges;
deterministic policy maps to actions (`decideGate` in
`packages/s1-runtime/src/decisions/gate.ts` is pure policy over pre-computed
Jev Nouls/Scores → allow/confirm/block). Our USAGE-MAP §11 summary of it is fair.

Two load-bearing differences underneath:

1. **Judgment is an interface, not a model.** Backends are pluggable
   (`backends/fake.ts`, `llm.ts`, `typesafe.ts`); the gate consumes answers,
   not Jev. Our demos hardwire Jev into the scoring step — theirs would keep
   working (degraded) with the model unplugged, ours would not run at all.
2. **Degraded path fails toward patterns, not passthrough.** On backend
   timeout/error, high-risk commands (network, push, recursive delete,
   out-of-project paths) match a local regex and confirm/block, while low-risk
   allows (`degraded.low_risk`). Our hook adapters fail toward full passthrough
   (allow-all). Their shape distinguishes; ours does not. Concrete import for
   our next hook revision.
3. **Bonus — speculation:** a `Speculator` prefetches judgments ahead of need.
   Our lane has no equivalent; every one of our hook judgments is on the
   critical path.

## s1-rs status (context, not this unit)

`examples/triage.rs` + `examples/moderation.rs` (FakeClient, offline) remain
unrun: RCH recovered only for trivial commands (`cargo --version` passes
through) and refuses compilation with `critical_pressure=3,
insufficient_slots=1`, local fallback disabled. Transient — retry when workers
recover. Cheapest unrun Jev surface in the tree, still waiting.
