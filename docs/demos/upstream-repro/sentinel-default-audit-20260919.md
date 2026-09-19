# Sentinel-default audit

**Unit:** P2-32
**Scope:** `work/`, `compaction/`, `scripts/`, `foundation/`; source extensions `mjs/js/ts`.
**Commands:** both required `rg` patterns plus explicit `none`/`n/a` and `|| unknown` controls.

The required `unknown` search found two hits. The numeric/default search found 25 source hits in
15 files. The `none`/`n/a` and `|| unknown` searches returned zero matches (`producer_rc=1`, no
matches). Total audited hits: 27. No code was changed.

| Hit | Classification | Reason |
|---|---|---|
| `work/p2-compaction/live-probe.mjs:30` `p.name ?? 'unknown'` | STORED | fallback enters normalized `toolUses` objects emitted by the probe |
| `compaction/src/omp-adapter.ts:94` `c.name ?? 'unknown'` | STORED | fallback enters normalized adapter message/tool-use data |
| `work/p2-localjev/scripts/eval/report.ts:86` `row.error ?? "unknown"` | STORED | fallback becomes a terminal-error label in the generated report |
| `work/omp-jev-observer/src/observer.mjs:40` `result.costUsd ?? 0` | STORED | missing classifier cost is written into the decision record as zero |
| `work/p2-compaction/live-probe.mjs:60-61` usage-token fallbacks | STORED | missing usage values enter probe counters/output metrics |
| `work/p2-compaction/live-probe.mjs:70` tool-result count fallback | FINE | debug-only diagnostic count; no truth-bearing artifact |
| `work/router-spec/oracle.mjs:80` distribution values `?? 0` | CONTROL | missing probability values feed a rank calculation only |
| `work/dogfood-logger/src/replay.mjs:38,40` probability `?? 0` | CONTROL | replay scorer fallback; it is not written back to decision records |
| `compaction/src/replay.ts:70,73,76` map counts `?? 0` | CONTROL | internal replay accounting for absent map entries |
| `work/compaction-proof/fair-oracle.mjs:54` first-seen `?? 0` | CONTROL | oracle comparison boundary, not persisted output |
| `work/compaction-proof/oracle.mjs:60` first-seen `?? 0` | CONTROL | oracle comparison boundary, not persisted output |
| `work/compaction-proof/oracle-selftest.mjs:9` first-seen `?? 0` | CONTROL | self-test oracle boundary, not persisted output |
| `work/p2-compaction/hooks/fast-jev.ts:296` context percent `?? 0` | FINE | optional runtime progress value used for a threshold branch |
| `work/p2-compaction/src/state.ts:228,283` per-entry token `?? 0` | FINE | internal state arithmetic for absent optional entries |
| `work/p2-compaction/types/claude-code.d.ts:2337,2669` `?? 0` | FINE | declaration-file examples/comments, not runtime data |
| `work/p2-localjev/scripts/eval/metrics.ts:29` label count `?? 0` | FINE | empty-input metric initialization |
| `work/p2-localjev/src/engine.ts:309,315` probability `?? 0` | CONTROL | normalized choice scoring and argmax comparison |
| `work/p2-localjev/src/engine.ts:459-460` token usage `?? 0` | FINE | provider usage accounting when fields are absent |

## Result

Stored sentinel count: **6 hit locations**. This is not an automatic defect verdict: each stored
location needs its own schema/consumer review. The audit found no additional `none`, `n/a`, or
`|| unknown` source hits. The observer's gate-path sentinel cleanup is not repeated here.

## NO-CLAIM

This is a one-off source audit, not a new checker, gate, or CI instrument. It does not claim the
six stored defaults are all harmful, only that they cross a persistence/report boundary and deserve
separate review. No directories outside `work/`, `compaction/`, `scripts/`, and `foundation/` were
covered.
