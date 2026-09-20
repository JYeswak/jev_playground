# Wave plan — sections and passes

Named path from the 2026-09-19 dispatch. This file was not on `origin/main` at
`e6d7a03`; this section is the process-mirror pass.

## Pass: skillranker PROCESS mirror (2026-09-20)

| | |
|---|---|
| **Mission stage** | Validate Jev → **build a tool from what survived** → liven an omp surface |
| **Upstream** | `Dicklesworthstone/skillranker` `6a74cca` public main |
| **Not this pass** | Re-measure their corpus (already 8/10 under their gate) |
| **Copied** | `__none__` abstention, structured JSON decision, 0/1/2 eval gate, always-abstain control, fail-open |
| **Refused** | Quill 254-wide, two-stage Jev, Claude hook protocol, SQLite ledger, TUI, cass, 300-family cohort |
| **Landed in** | `work/omp-jev-route/` (extend, not rename) |
| **Receipt** | [`skillranker-process-mirror-20260919.md`](skillranker-process-mirror-20260919.md) |
| **ACCEPTANCE** | `node work/omp-jev-route/src/cli.mjs decide --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl` |
| | `node work/omp-jev-route/src/cli.mjs gate --fixture work/omp-jev-route/fixtures/process-cases.v1.jsonl` |
| | `node --test work/omp-jev-route/test/process.test.mjs work/omp-jev-route/test/gate.test.mjs` |
| **Promotion** | **0**. `diagnostic_synthetic` cannot promote. No working-dogfood claim. |

### Next lever (computed, not escalated)

Wire a real omp `context` event that carries `roster` from the session's visible skills,
still observe-only, still `binding: log-only`. Do not register a working profile until
the handler writes a process row next to a known-firing neighbour.
