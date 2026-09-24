# Pane 5 (SunnyTiger) - dogfood the tool-call gate as an observe-only omp hook

From pane 1 AmberWillow, 2026-09-24. Bead: `jev-deep-kit-8q7.13` (filed with this packet).

## 1. Mission

Validate Jev -> build tools from what survives -> **liven an omp surface -> dogfood it**. The frozen
tool-call gate survived its real-traffic test: 7 false alarms in 300 routine commands (2.3%) against
Haiku's 58 (19.3%), non-author confirmed (`jev-32z`, receipt
`docs/demos/upstream-repro/bicameral-gate-real-traffic-20260923.md`). It also missed 7 of the 14
risky commands, so it is a quiet screen, not a guard. The next evidence can only come from running
it on the fleet's live traffic and keeping the log.

## 2. Build

1. `.omp/hooks/post/jev-gate-observe.ts`: on every completed `bash` tool call, ask the frozen gate
   questions from `work/bicameral-gate/questions.mjs` through `work/jev-client` `askJev` (pinned
   `jev-1.13.0`) and append one row to `~/.local/state/jev/gate-observe.jsonl` (outside the repo):
   timestamp, session id, command sha256, the first 200 characters with secrets redacted, per-question
   probabilities, flag, latency, tokens.
2. Observe only: it never blocks, never rewrites a result, prints nothing, and must add no latency to
   the tool path (fire-and-forget; measure the tool round-trip with the hook on and off).
3. Skip and log `skipped:secret` for any command the private/secret filters in
   `work/bicameral-gate/real-sample.py` would drop, so no secret is ever sent to the API. Reuse that
   code rather than copying it.
4. No key: one row `NOT_RUN reason=unconfigured`, no throw.

## 3. Acceptance

- L0: tests for the row shape, the secret skip, the no-key path, and the never-throws path, each with
  a planted failure that turns them red.
- L3 in a fresh `omp --mode=rpc --max-time=90` session from the repo root with the key present: a
  routine command (`ls`) logs a clean row; `git push --dry-run origin main` logs its probabilities;
  a command carrying a planted fake key is logged `skipped:secret` with no API call. Paste the rows.
- Tool round-trip with and without the hook, N>=20 each, p50/p95.
- README: one line under the tools list naming the hook and the log path.
- Close only after a non-author pane re-runs the tests and the L3 probe.

## 4. Rules

Live by default. Key from Infisical, never printed. Reserve, stage explicit paths, read back, no
amend, push per commit. Do not stop between steps; if blocked, message pane 1. Callback
`CALLBACK-P5-OBSERVE-DONE` via `ntm send jev --pane=1`.
