# omp-compact-replay

Offline replay harness: omp session transcripts through `fast-jev-compaction`,
verifying the library contract on omp-shaped traffic.

## Layout

- `src/omp-adapter.ts` — `omp -p --mode json` event stream → `Message[]`.
  Reads `message_end` rows only (streaming `message_update` partials ignored).
  Assistant `thinking` blocks are dropped and counted (the library has no
  thinking channel; carrying them as text would corrupt its verbatim contract).
  Standalone `toolResult` messages attach to the message immediately FOLLOWING
  the call's message (any role; the library pairs by id, role-free).
  Call-adjacent placement keeps each result in its call's own pin window.
  A result whose call is in the final message lands on one trailing empty user
  message and is counted — never silently dropped.
- `test/adapter.test.ts` — deterministic mapping tests + known-bad
  (trailing result must be kept).
- `fixtures/` — real captured transcripts. `omp-session-20260917.jsonl` is a
  6-call session (fits the pin window; adapter-only proof). The `-big-`
  capture has 11 tool calls so middle calls become Jev candidates.
- `runs/` — live replay receipts (manual, like calibration runs).

## Use

```sh
npm install
npm test                      # 4 deterministic adapter tests
npm run replay -- <t.jsonl> [--out runs/r.json]
../../foundation/gates.d/40-omp-compact-replay.sh   # gate (hermetic)
```

- Thinking content is dropped (counted in receipt). If a future task needs
  reasoning preserved, the adapter must grow a channel for it — currently none.
- Single-turn `-p` sessions put every result after the only user turn; the
  call-adjacent rule still places each result next to its call.
- The `-big-` fixture keeps full raw rows including opaque `thinkingSignature`
  blobs (provider metadata, never model content).
