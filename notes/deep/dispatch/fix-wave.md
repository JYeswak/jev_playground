# Fix wave — Joshua, 2026-09-22: "yeah get it fixed, you have 3 muse agents idle and grok"

From pane 1 AmberWillow. Depth directive and W7.0 standard still bind. Gate every commit on the
index readback. Callback `CALLBACK-P<N>-FIX-DONE` (pane 2, 3) or your W7.0 group callback (4, 5, 6).

## Cause (established by pane 1; evidence in bead `jev-pkd`)

`/dev/null` on contabo-2, -3, -4 is a 0644 regular file. contabo-4's was created at
2026-09-19T16:56:36Z, 0.18 s after UDS's transport probe ran there as root:
`printf 'fn main() {}' | rustc --crate-name uds_rch_probe --emit=metadata -o /dev/null -`
(`~/Developer/uds/crates/uds/src/main.rs:2185`, callers `main.rs:3115`, `rch_bundle.rs:742,942,1296`).
rustc >= 1.64 writes `-o` output via a temp dir beside the path and moves it into place
(rust-lang/rust#111157); as root in `/dev` that replaces the device. Consequence measured tonight:
trybuild compile-fail tests false-pass on those workers (s1-rs, 4/4), and every job reading
`/dev/null` gets stale bytes. Pane 1 is repairing the three workers now.

## Pane 2 — RedMaple (grok): fix the probe at its source, in `~/Developer/uds`

- Read `~/Developer/uds/AGENTS.md` first and follow that repo's rules (its commit, test and RCH
  conventions, not jev's). This is a cross-repo fix Joshua authorized; touch nothing else there.
- Change `transport_probe` so rustc never writes to `/dev/null`: emit into a fresh temp dir on the
  worker (for example `d=$(mktemp -d) && printf 'fn main() {}' | rustc --crate-name uds_rch_probe
  --emit=metadata --out-dir "$d" - && rm -r "$d"`), keeping the `REMOTE_COMMAND_FINISHED_SUCCESS`
  contract and its failure semantics exactly. Grep the whole uds tree (and `control-plane`,
  `omp-orchestrator`) for any other `-o /dev/null` given to rustc or cargo and fix those the same way.
- Test through RCH only, and only AFTER pane 1 reports all workers repaired: prove on a worker
  that `/dev/null` is still `character special file` after the probe runs (stat before and after).
- Add a regression test in uds that fails if the probe command string contains `-o /dev/null`.
- Receipt `docs/demos/upstream-repro/uds-devnull-probe-fix-20260923.md` in jev (what changed, the
  uds commit sha, before/after stat on a worker). Then draft (do not file) an upstream note for
  rust-lang/rust#111157 in the receipt: the root-in-`/dev` consequence, with our reproduction.

## Pane 3 — TopazRaven (Muse): fix `work/jev-client` T9 (your finding)

Your W7.0 receipt `jev-client-w70-20260923.md`: a timed-out request kills a Node host ~1/3 of runs
(SDK leak at `dist/index.mjs:636`); Bun passed 2/2. Fix it in `work/jev-client/src/index.ts`
without editing the vendored SDK: own the abort (pass our own `AbortSignal`, or attach a handler
to the SDK's internal rejection), keep the discriminated `JevFailure` contract. Prove with your own
T9 harness: Node N>=30 timed-out requests, 0 host kills; Bun N>=30, 0; plus the existing suites
(`node --test work/jev-client/test/*.test.mjs`) green. Add the Node timeout case as a regression
test that fails on the current code. Update `TESTS.md`. Then resume W7.0 if anything remains.

## Panes 4, 5, 6 — start your W7.0 groups now

Per `notes/deep/dispatch/W7-fresh-runs.md`. Pane 4: jev-sec-bench, jev-phishing-bench,
jev-spam-eval, foreman. Pane 5: jev-rerank-bench, jev-benchmark, jev-agent-failure-benchmark,
typesafe-ai-benchmark, awesome-typesafe (+ jevcal, Janus). Pane 6: jev-align, commit-miner,
skillranker, bicameral, jev-ultrafast. **RCH note:** until pane 1 reports the workers repaired,
any Rust verdict from contabo-2/3/4 that involves a negative test is suspect; rerun it after the
repair. commit-miner's `tests.rs:799` failure on c3 AND c4 may be this bug (git reads config from
`/dev/null`); re-run it after repair before calling it the clone's fault.
