# W7.2 fresh runs — every clone, under the W7.0 standard

From pane 1 AmberWillow. Joshua, 2026-09-22: "past receipts do not mean we went deep enough - we
proved nothing with past receipts except that we didn't know how to test this system properly."

**The standard is plan §4 W7.0** (`docs/PLAN-DEEP-KIT-20260922.md`), tests T1–T10 with class profiles.
Read it before your first clone. Prior receipts and the W7.1 ledger (`notes/deep/clone-ledger.tsv`)
are **leads**: read them to know where to look, never cite them as a pass. The depth directive
binds (`notes/deep/dispatch/DEPTH-DIRECTIVE.md`): an unrun test carries command, verbatim output,
`file:line` cause, two routes. Use subagents of your own, one per clone. You verify each subagent's
decisive command before it enters a receipt.

Rules that bind every run:
- Live Jev is allowed and expected where T4/T6 apply (cost gate lifted). Key: `infisical run
  --projectId=42b194c3-89d7-4ebb-895f-dd77ddf005ba -- <cmd>`. LLM keys for the incumbent arm: find
  them the same way `work/nev-differential/` found them; never print a key.
- Write the T4 bar into the receipt **before** the first live call, and commit that preregistration
  first (`[pending]`), so the bar provably predates the data.
- Rust builds and tests run only on Contabo via RCH (`skill://zeststream-rch`). Record the worker.
  `contabo-4` returned a pass-shaped result for compile-fail tests tonight: when a Rust result
  matters, confirm it on a second worker.
- Clones stay untouched. Work in `/tmp` copies when you plant a defect (T2) or need a scratch file.
- One receipt per clone: `docs/demos/upstream-repro/<clone>-w70-<date>.md`, a table with one row per
  test id (status: PASS / FAIL / NOT-APPLICABLE with reason / NOT-RUN with the four fields), then
  the verdict (T10) and `Boundary`. Append one EVAL.md section per clone (reserve EVAL.md first).
- Gate every commit on the index readback.

## Assignments

| pane | model | group | clones (class) | starts |
|---|---|---|---|---|
| 3 TopazRaven | Muse | SDK / transport | `upstream/typesafe-ai/typesafe-sdk-js`, `upstream/typesafe-ai/typesafe-sdk-python`, `upstream/typesafe-ai/system-one-adapter-python` (and confirm the root `system-one-adapter-python` copy is a stale duplicate, then say so), `s1-rs`, and **our own `work/jev-client`** (T9: does a timed-out request through our client still leak the SDK's `AbortError`, and does that kill a Node host and a Bun host? old lead: `docs/demos/upstream-repro/sdk-js-timeout-crash-20260919.md`) | now |
| 4 MistyTurtle | Muse | seat / benchmark | `jev-sec-bench`, `jev-phishing-bench`, `jev-spam-eval`, `foreman` | after W3.1 depth |
| 5 SunnyTiger | Muse | seat / benchmark + catalogue | `jev-rerank-bench`, `jev-benchmark`, `jev-agent-failure-benchmark`, `typesafe-ai-benchmark`, `awesome-typesafe` (clone `jevcal` and `Janus` at pinned SHAs first; run them under W7.0 as new clones) | after `p5-next` |
| 6 QuietHarbor | Muse | seat / benchmark | `jev-align`, `commit-miner`, `skillranker`, `bicameral`, `jev-ultrafast` | after W2.1 depth |
| 2 RedMaple | grok | tool / integration + catalogue | `jev-mcp`, `jev-review`, `jev-router`, `jev-codex-router`, `fast-jev-compaction`, `pi-subagents`, `awesome-jev`, `awesome-jev-by-typesafe`, `upstream/typesafe-ai/skills` | after `p2-next` |

Callback per clone is not required; callback per group: `CALLBACK-P<N>-W70-<group>-DONE` with one
line per clone (test ids PASS/FAIL/NA/NOT-RUN and the result class), the receipt paths, and the
commit shas.
